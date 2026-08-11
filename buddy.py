#!/usr/bin/env python3
"""Masters' Nudge — Stop hook worker.

Reads the transcript path from the Stop-hook JSON on stdin, gathers the recent
turns, dispatches to the configured provider's CLI (OpenAI Codex by default,
or Anthropic Claude via BUDDY_PROVIDER=anthropic) with the Masters' Nudge prompt
prompt, and appends the reaction to the per-session log at
~/.claude/buddy/<session_id>.log.

Never raises out of main() — hook must not block on our errors.
"""

import json
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import source_context
import review_telemetry

CLAUDE_DIR = Path(os.environ.get("BUDDY_CLAUDE_DIR", os.path.expanduser("~/.claude")))
SCRIPT_DIR = Path(__file__).resolve().parent
PROMPT_FILE = SCRIPT_DIR / "buddy-prompt.txt"
OUTPUT_SCHEMA_FILE = SCRIPT_DIR / "reaction-schema.json"
PERSONA_DIR = SCRIPT_DIR / "personas"
BUDDY_DIR = CLAUDE_DIR / "buddy"
ERROR_LOG = CLAUDE_DIR / "buddy-error.log"
MAX_REACTION_CHARS = 52

PERSONAS = {
    "jeff": "Jeff Dean",
    "linus": "Linus Torvalds",
    "fowler": "Martin Fowler",
    "beck": "Kent Beck",
    "lamport": "Leslie Lamport",
    "carmack": "John Carmack",
}

PROVIDER = os.environ.get("BUDDY_PROVIDER", "openai").lower()
# BUDDY_MODEL meaning depends on provider:
#   anthropic: sonnet (default), opus, haiku
#   openai/codex: gpt-5.6-sol (default), other model names codex CLI accepts
_DEFAULT_MODELS = {
    "anthropic": "sonnet",
    "openai": "gpt-5.6-sol",
    "codex": "gpt-5.6-sol",
}
MODEL = os.environ.get("BUDDY_MODEL", _DEFAULT_MODELS.get(PROVIDER, "sonnet"))
TIMEOUT_SEC = int(os.environ.get("BUDDY_TIMEOUT", "60"))

# Transcript shaping: fill a char budget walking backwards from the newest
# user/assistant entry. Each entry kept in full unless it exceeds the per-
# message cap (then tail-truncated with a "…" prefix). The oldest entry
# included may itself be tail-truncated when only partial budget remains.
# tool_result content from the SAME selected window is collected into one
# trailing block tail-truncated to TOOL_OUTPUT_TAIL_CHARS.
#
# Sizing rationale:
# - Prior PER_MESSAGE_MAX_CHARS=1500 regularly truncated long Claude
#   responses mid-sentence — the reviewer then surfaced "content looks incomplete"
#   findings that were actually budget artifacts, not real delivery gaps.
#   5000 lets a typical 2000-4000-char Claude response survive whole.
# - TRANSCRIPT_CHAR_BUDGET capped at 6000 because read_recent_reactions
#   only carries forward the last 3 reactions — letting the transcript window
#   walk farther back than ~3 turns means the reviewer sees old
#   Claude content without knowing what it itself said about it, which
#   degrades into hallucinated or repeated findings.
# - TRANSCRIPT + TOOL_OUTPUT held at 8000 total (user-set ceiling).
TRANSCRIPT_CHAR_BUDGET = 6000
PER_MESSAGE_MAX_CHARS = 5000
MIN_REMAINING_TO_INCLUDE = 400
TOOL_OUTPUT_TAIL_CHARS = 2000


MAX_ERROR_LOG_BYTES = 256 * 1024  # 256 KB


def _rotate_error_log() -> None:
    """If error log exceeds MAX_ERROR_LOG_BYTES, keep only the last half."""
    try:
        if not ERROR_LOG.exists():
            return
        size = ERROR_LOG.stat().st_size
        if size <= MAX_ERROR_LOG_BYTES:
            return
        keep = size // 2
        with ERROR_LOG.open("rb") as f:
            f.seek(size - keep)
            f.readline()  # skip partial line
            tail = f.read()
        with ERROR_LOG.open("wb") as f:
            f.write(tail)
    except Exception:
        pass


def log_error(msg: str) -> None:
    try:
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        _rotate_error_log()
        with ERROR_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] buddy: {msg}\n")
    except Exception:
        pass


def read_hook_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except Exception as e:
        log_error(f"hook input parse failed: {e}")
        return {}


def parse_transcript_entry(obj: dict) -> tuple[str, str, list[str]] | None:
    """Pull (prefix, text, tool_results) from one transcript JSONL entry.

    - prefix: "user" or "claude"
    - text: concatenated text-block content (no truncation here — the
      per-message head-cap is applied by read_recent_transcript)
    - tool_results: raw tool_result content strings, in encounter order
    Returns None for non-user/assistant entries. tool_use blocks are dropped.
    """
    typ = obj.get("type")
    if typ not in ("user", "assistant"):
        return None

    prefix = "user" if typ == "user" else "claude"
    msg = obj.get("message", {}) or {}
    content = msg.get("content", "")

    text_parts: list[str] = []
    tool_results: list[str] = []

    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                text_parts.append(block.get("text", ""))
            elif btype == "tool_result":
                raw = block.get("content", "")
                if isinstance(raw, list):
                    inner = []
                    for item in raw:
                        if isinstance(item, dict) and item.get("type") == "text":
                            inner.append(item.get("text", ""))
                    tool_results.append("\n".join(inner))
                else:
                    tool_results.append(str(raw))
            # tool_use blocks are dropped entirely (Cinder-style)
    else:
        text_parts.append(str(content))

    text = "\n".join(p for p in text_parts if p).strip()
    return prefix, text, tool_results


def _read_transcript_entries(
    transcript_path: str, start_offset: int | None = None
) -> list[tuple[str, str, list[str]]]:
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    try:
        tail_bytes = 65536
        size = os.path.getsize(transcript_path)
        with open(transcript_path, "rb") as handle:
            if start_offset is not None and 0 < start_offset <= size:
                handle.seek(start_offset)
            elif size > tail_bytes:
                handle.seek(size - tail_bytes)
                handle.readline()  # drop the partial first JSONL line
            data = handle.read()
        lines = data.decode("utf-8", errors="replace").splitlines()
    except Exception as e:
        log_error(f"transcript read failed: {e}")
        return []

    entries: list[tuple[str, str, list[str]]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        parsed = parse_transcript_entry(obj)
        if parsed is not None:
            entries.append(parsed)
    return entries


def read_recent_transcript(transcript_path: str) -> str:
    """Build the legacy transcript fallback using a character budget.

    Walk backwards from the newest user/assistant entry, including each one
    in full until the TRANSCRIPT_CHAR_BUDGET is consumed. Entries longer
    than PER_MESSAGE_MAX_CHARS are tail-truncated (with a "…" prefix) before
    the budget check. The oldest included entry may itself be tail-truncated
    to fit the remaining budget — provided at least MIN_REMAINING_TO_INCLUDE
    chars remain (otherwise it is dropped). tool_result content from the
    same selected window flows into a separate trailing block, tail-cropped
    to TOOL_OUTPUT_TAIL_CHARS.

    Output shape (sections are explicitly delimited so the reviewer can tell where
    the conversation ends and tool output begins):

        [transcript — 從最新往回填，總長 ≤ TRANSCRIPT_CHAR_BUDGET 字；
         單則超過 PER_MESSAGE_MAX_CHARS 字者以…起頭]
        user: <text>
        claude: <text>
        ...
        [end transcript]
        [tool output — 工具回傳合併後尾部 TOOL_OUTPUT_TAIL_CHARS 字；非對話本身]
        <last TOOL_OUTPUT_TAIL_CHARS chars of selected tool_result content>
        [end tool output]

    The tool output block appears only if any selected entry contained
    tool_result data. The transcript block appears only if any selected
    entry had user/claude text (a tool-result-only window suppresses the
    transcript framing but keeps the tool output framing).
    """
    entries = _read_transcript_entries(transcript_path)

    # Walk newest → oldest, filling the char budget. tool_result-only
    # entries cost nothing against the transcript budget (they have no
    # text), but their tool_results are still collected in encounter order
    # so the [tool output] block matches the [transcript] window.
    selected: list[tuple[str, str, list[str]]] = []
    remaining = TRANSCRIPT_CHAR_BUDGET
    for prefix, text, tool_results in reversed(entries):
        if not text:
            selected.append((prefix, "", tool_results))
            continue

        # Hard cap on any single message — tail-bias keeps the end.
        if len(text) > PER_MESSAGE_MAX_CHARS:
            snippet = "…" + text[-PER_MESSAGE_MAX_CHARS:]
        else:
            snippet = text

        cost = len(snippet)
        if cost <= remaining:
            selected.append((prefix, snippet, tool_results))
            remaining -= cost
            continue

        # Snippet won't fit. If there's still meaningful space, truncate
        # this one entry to fit; otherwise stop walking back.
        if remaining >= MIN_REMAINING_TO_INCLUDE:
            # Reserve 1 char for the "…" marker.
            tail = text[-(remaining - 1):]
            selected.append((prefix, "…" + tail, tool_results))
            remaining = 0
        break

    selected.reverse()

    transcript_lines: list[str] = []
    tool_buffer: list[str] = []
    for prefix, snippet, tool_results in selected:
        if snippet:
            transcript_lines.append(f"{prefix}: {snippet}")
        tool_buffer.extend(tool_results)

    out_lines: list[str] = []
    if transcript_lines:
        out_lines.append(
            "[transcript — 從最新往回填，總長 ≤ "
            f"{TRANSCRIPT_CHAR_BUDGET} 字；單則超過 "
            f"{PER_MESSAGE_MAX_CHARS} 字者以…起頭]"
        )
        out_lines.extend(transcript_lines)
        out_lines.append("[end transcript]")

    if tool_buffer:
        joined = "\n".join(tool_buffer)
        out_lines.append(
            "[tool output — 工具回傳合併後尾部 "
            f"{TOOL_OUTPUT_TAIL_CHARS} 字；非對話本身]"
        )
        out_lines.append(joined[-TOOL_OUTPUT_TAIL_CHARS:])
        out_lines.append("[end tool output]")

    return "\n".join(out_lines)


def read_recent_tool_evidence(transcript_path: str, start_offset: int = 0) -> str:
    offset = start_offset if start_offset > 0 else None
    entries = _read_transcript_entries(transcript_path, offset)
    tool_results: list[str] = []
    for _, _, results in entries:
        tool_results.extend(result for result in results if result)
    return "\n".join(tool_results)


def read_latest_assistant_text(transcript_path: str, start_offset: int = 0) -> str:
    offset = start_offset if start_offset > 0 else None
    for prefix, text, _ in reversed(_read_transcript_entries(transcript_path, offset)):
        if prefix == "claude" and text:
            return text
    return ""



def read_recent_reactions(session_id: str, max_count: int = 3, max_chars: int = 200) -> list[str]:
    """Read the last N Masters' Nudge reactions from this session's log."""
    log_path = BUDDY_DIR / f"{session_id}.log"
    if not log_path.exists():
        return []
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    reactions = []
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            if entry.get("kind") == "evaluation_notice":
                continue
            r = entry.get("reaction", "").strip()
            if r:
                reactions.append(r[:max_chars])
        except Exception:
            continue
        if len(reactions) >= max_count:
            break
    reactions.reverse()
    return reactions


# ── agentcam report integration ───────────────────────────────────────
# Masters' Nudge can read AGENT_RUN_REPORT.md generated by `cr` / `agentcam run` and
# include it in the payload sent to the second-opinion model. Dedup is per
# session_id keyed on report file mtime.

AGENTCAM_REPORT_READ_CHARS = 65536


def _find_git_root(start: str) -> str | None:
    """Walk up from `start` until a .git entry is found. Returns repo root or None."""
    try:
        p = Path(start).resolve()
    except Exception:
        return None
    while True:
        if (p / ".git").exists():
            return str(p)
        if p.parent == p:
            return None
        p = p.parent


def read_latest_agentcam_report(cwd: str) -> dict | None:
    """Find the most recent AGENT_RUN_REPORT.md under <git_root>/.git/agentcam/runs/.

    Returns {"path": str, "content": str, "mtime": float} or None.
    Content keeps both ends within AGENTCAM_REPORT_READ_CHARS. The provider
    receives only selected evidence sections, capped separately.
    """
    git_root = _find_git_root(cwd)
    if not git_root:
        return None
    runs_dir = Path(git_root) / ".git" / "agentcam" / "runs"
    if not runs_dir.is_dir():
        return None
    try:
        candidates = list(runs_dir.glob("*/AGENT_RUN_REPORT.md"))
    except Exception:
        return None
    if not candidates:
        return None
    # Pick newest by mtime
    newest = max(candidates, key=lambda p: p.stat().st_mtime)
    try:
        content = newest.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        log_error(f"agentcam report read failed: {e}")
        return None
    content = source_context.head_tail(content, AGENTCAM_REPORT_READ_CHARS)
    return {
        "path": str(newest),
        "content": content,
        "mtime": newest.stat().st_mtime,
    }


def _agentcam_state_path(session_id: str) -> Path:
    return BUDDY_DIR / f"{session_id}.agentcam.state.json"


def load_agentcam_last_mtime(session_id: str) -> float:
    p = _agentcam_state_path(session_id)
    if not p.exists():
        return 0.0
    try:
        return float(json.loads(p.read_text(encoding="utf-8")).get("last_mtime", 0.0))
    except Exception:
        return 0.0


def save_agentcam_last_mtime(session_id: str, mtime: float) -> None:
    try:
        BUDDY_DIR.mkdir(parents=True, exist_ok=True)
        _agentcam_state_path(session_id).write_text(
            json.dumps({"last_mtime": mtime}), encoding="utf-8"
        )
    except Exception as e:
        log_error(f"agentcam state save failed: {e}")


def build_system_prompt() -> str:
    if not PROMPT_FILE.exists():
        log_error(f"prompt file missing: {PROMPT_FILE}")
        return ""
    try:
        base_prompt = PROMPT_FILE.read_text(encoding="utf-8")
    except Exception as e:
        log_error(f"prompt file read failed: {e}")
        return ""

    persona = os.environ.get("BUDDY_PERSONA", "").strip().lower()
    if not persona:
        return base_prompt
    if persona not in PERSONAS:
        supported = ", ".join(PERSONAS)
        log_error(f"unknown persona: {persona!r}; supported: {supported}")
        return ""

    persona_file = PERSONA_DIR / f"{persona}.txt"
    try:
        overlay = persona_file.read_text(encoding="utf-8").strip()
    except Exception as e:
        log_error(f"persona prompt read failed ({persona}): {e}")
        return ""

    persona_header = (
        "# 工程觀察鏡頭\n\n"
        f"這一輪以 {PERSONAS[persona]} 常見的工程判斷作為注意力索引。\n"
        "只套用下方的選題框架；身份與語氣維持 Masters’ Nudge "
        "的中性、證據優先風格。\n"
        "上方 Masters’ Nudge 的證據、旁觀者角色、單一 finding 與字數規則仍然優先。"
    )
    return f"{base_prompt.rstrip()}\n\n{persona_header}\n\n{overlay}\n"


def load_output_schema_json() -> str:
    """Return the shared output schema as compact JSON, or fail closed."""
    try:
        schema = json.loads(OUTPUT_SCHEMA_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        log_error(f"reaction schema unavailable: {exc}")
        return ""
    if not isinstance(schema, dict):
        log_error("reaction schema root must be an object")
        return ""
    return json.dumps(schema, ensure_ascii=False, separators=(",", ":"))


def parse_reaction_result(stdout: str) -> dict:
    """Extract and validate one finding from structured CLI output.

    Both direct schema objects (Codex) and Claude's JSON result envelope are
    accepted. Anything outside the shared two-field contract fails closed.
    """
    stdout = stdout.strip()
    if not stdout:
        return {"status": "error", "finding": ""}
    try:
        obj = json.loads(stdout)
    except (TypeError, ValueError):
        return {"status": "error", "finding": ""}
    if isinstance(obj, dict) and "structured_output" in obj:
        obj = obj.get("structured_output")
    if not isinstance(obj, dict) or set(obj) != {"status", "finding"}:
        return {"status": "error", "finding": ""}
    status = obj.get("status")
    finding = obj.get("finding")
    if not isinstance(finding, str):
        return {"status": "error", "finding": ""}
    if status == "no_finding":
        return {"status": "no_finding", "finding": ""}
    if status != "finding":
        return {"status": "error", "finding": ""}
    finding = finding.strip()
    if not finding or len(finding) > MAX_REACTION_CHARS:
        return {"status": "error", "finding": ""}
    return {"status": "finding", "finding": finding}


def parse_reaction(stdout: str) -> str:
    """Backward-compatible finding-only wrapper."""
    return str(parse_reaction_result(stdout)["finding"])


def parse_usage(stdout: str) -> dict[str, int]:
    """Best-effort extraction of token counters from CLI JSON/JSONL output."""
    usage_fields = {
        "input_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
        "total_tokens",
    }
    best: dict[str, int] = {}

    def visit(value) -> None:
        nonlocal best
        if isinstance(value, dict):
            candidate = {
                key: int(item)
                for key, item in value.items()
                if key in usage_fields and isinstance(item, (int, float))
            }
            if len(candidate) > len(best):
                best = candidate
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    for line in str(stdout or "").splitlines():
        try:
            visit(json.loads(line))
        except (TypeError, ValueError):
            continue
    return best


def _call_result(status: str = "error", finding: str = "", **extra) -> dict:
    return {"status": status, "finding": finding, "usage": {}, **extra}


def call_claude_result(system_prompt: str, transcript_text: str, model: str) -> dict:
    user_prompt = "請對 stdin 提供的對話片段寫一句簡短的旁觀者反應。"
    schema_json = load_output_schema_json()
    if not schema_json:
        return _call_result()

    fd = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    fd.write(system_prompt)
    fd.close()

    env = {**os.environ, "BUDDY_ACTIVE": "1"}
    try:
        r = subprocess.run(
            [
                "claude", "-p", user_prompt,
                "--model", model,
                "--append-system-prompt-file", fd.name,
                "--output-format", "json",
                "--json-schema", schema_json,
            ],
            input=transcript_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            timeout=TIMEOUT_SEC,
        )
        if r.returncode != 0:
            log_error(f"claude CLI exit {r.returncode}: {r.stderr[:500]}")
            return _call_result()
        result = parse_reaction_result(r.stdout)
        result["usage"] = parse_usage(r.stdout)
        return result
    except subprocess.TimeoutExpired:
        log_error("claude CLI timeout")
        return _call_result()
    except FileNotFoundError:
        log_error("claude CLI not found in PATH")
        return _call_result()
    finally:
        try:
            os.unlink(fd.name)
        except OSError:
            pass


def call_claude(system_prompt: str, transcript_text: str, model: str) -> str:
    """Backward-compatible finding-only wrapper."""
    return str(call_claude_result(system_prompt, transcript_text, model)["finding"])


def _resolve_codex_bin() -> str | None:
    """Find codex executable. PATH lookup may miss it (e.g. npm on Windows
    isn't in the env Python sees), so probe known install locations too."""
    direct = shutil.which("codex")
    if direct and os.path.exists(direct):
        return direct
    candidates = [
        os.path.expanduser(r"~\AppData\Roaming\npm\codex.cmd"),
        os.path.expanduser(r"~\AppData\Roaming\npm\codex.exe"),
        os.path.expanduser(r"~\AppData\Roaming\npm\codex"),
        os.path.expanduser("~/.codex/bin/codex"),
        "/usr/local/bin/codex",
        "/usr/bin/codex",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def call_codex_result(system_prompt: str, transcript_text: str, model: str) -> dict:
    """Invoke codex exec and return structured status plus best-effort usage."""
    codex_bin = _resolve_codex_bin()
    if not codex_bin:
        log_error("codex CLI not found (checked PATH + common npm paths)")
        return _call_result()
    if not load_output_schema_json():
        return _call_result()

    # codex has no separate system-prompt slot — bundle everything into one prompt.
    user_prompt = "請對下方 [transcript] 區塊裡的對話片段寫一句簡短的旁觀者反應。"
    combined = (
        f"{system_prompt}\n\n"
        f"---\n\n"
        f"{user_prompt}\n\n"
        f"[transcript]\n{transcript_text}\n[end transcript]"
    )

    output_fd = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    output_fd.close()

    env = {**os.environ, "BUDDY_ACTIVE": "1"}
    # On Windows, .cmd files need shell=True or cmd /c. Detect by extension.
    use_shell = codex_bin.lower().endswith((".cmd", ".bat"))
    try:
        cmd = [
            codex_bin, "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--ignore-user-config",
            "--json",
            "-s", "read-only",
            "-m", model,
            "--output-schema", str(OUTPUT_SCHEMA_FILE),
            "-o", output_fd.name,
            "-",  # read prompt from stdin
        ]
        if use_shell:
            # Quote args properly for cmd shell
            cmd_str = " ".join(f'"{a}"' if " " in a else a for a in cmd)
            r = subprocess.run(
                cmd_str,
                input=combined,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=TIMEOUT_SEC,
                shell=True,
            )
        else:
            r = subprocess.run(
                cmd,
                input=combined,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=TIMEOUT_SEC,
            )
        if r.returncode != 0:
            log_error(f"codex exit {r.returncode}: {r.stderr[:500]}")
            return _call_result(usage=parse_usage(r.stdout))
        try:
            with open(output_fd.name, "r", encoding="utf-8") as f:
                result = parse_reaction_result(f.read())
                result["usage"] = parse_usage(r.stdout)
                return result
        except Exception as e:
            log_error(f"codex output read failed: {e}")
            return _call_result(usage=parse_usage(r.stdout))
    except subprocess.TimeoutExpired:
        log_error("codex timeout")
        return _call_result()
    except FileNotFoundError:
        log_error(f"codex CLI not executable: {codex_bin}")
        return _call_result()
    finally:
        try:
            os.unlink(output_fd.name)
        except OSError:
            pass


def call_codex(system_prompt: str, transcript_text: str, model: str) -> str:
    """Backward-compatible finding-only wrapper."""
    return str(call_codex_result(system_prompt, transcript_text, model)["finding"])


_WRAPPER_RE = re.compile(
    r"\[(?:end )?(?:Buddy|Masters[’'] Nudge)[^\]]*\]"
)
_CODEBLOCK_RE = re.compile(r"```[\s\S]*?```")
_INLINE_CODE_RE = re.compile(r"`([^`]*)`")
_MD_BOLD_RE = re.compile(r"\*{1,3}([^*]+)\*{1,3}")
_MD_HEADER_RE = re.compile(r"^#{1,6}\s*", re.MULTILINE)
_BOILERPLATE_PREFIX_RES = (
    re.compile(r"^(?:作為|身為)[^，,：:。！？!?]{1,40}[，,：:]\s*"),
    re.compile(
        r"^(?:整體來說|總體而言|總的來說|簡單來說|先說結論|"
        r"值得注意的是|需要注意的是|我認為|在我看來|以下是我的觀察)"
        r"[，,:：。.!！\s]*"
    ),
    re.compile(
        r"^(?:做得很好|整體做得不錯|這個方向很好|方向很清楚|"
        r"這是一個很好的(?:做法|方向|實作))"
        r"[，,:：。.!！\s]*"
    ),
)
_BOILERPLATE_SUFFIX_RE = re.compile(
    r"(?:希望(?:這|以上)?(?:對你)?有幫助|希望能幫到你|供參考|"
    r"以上(?:是我的觀察)?|謝謝(?:閱讀)?)"
    r"[。.!！\s]*$"
)
def _strip_boilerplate(text: str) -> str:
    """Remove anchored social filler without rewriting finding content."""
    previous = None
    while text and text != previous:
        previous = text
        for pattern in _BOILERPLATE_PREFIX_RES:
            text = pattern.sub("", text, count=1).lstrip()
        text = _BOILERPLATE_SUFFIX_RE.sub("", text, count=1).rstrip()
    return text


def sanitize_reaction(raw: str) -> str:
    """Clean model output before logging.

    - Strip code blocks and markdown formatting
    - Remove current and legacy wrapper collision markers
    - Collapse whitespace
    - Remove common leading/trailing social filler
    - Hard truncate to MAX_REACTION_CHARS
    """
    text = raw.strip()
    if not text:
        return ""
    text = _CODEBLOCK_RE.sub("", text)
    text = _INLINE_CODE_RE.sub(r"\1", text)
    text = _MD_BOLD_RE.sub(r"\1", text)
    text = _MD_HEADER_RE.sub("", text)
    text = _WRAPPER_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = _strip_boilerplate(text)
    if len(text) > MAX_REACTION_CHARS:
        text = text[:MAX_REACTION_CHARS]
    return text


def dispatch_call(system_prompt: str, transcript_text: str) -> str:
    """Route to the right provider based on BUDDY_PROVIDER."""
    return str(dispatch_call_result(system_prompt, transcript_text)["finding"])


def dispatch_call_result(system_prompt: str, transcript_text: str) -> dict:
    """Route to a provider while preserving outcome and usage metadata."""
    if PROVIDER in ("openai", "codex"):
        return call_codex_result(system_prompt, transcript_text, MODEL)
    return call_claude_result(system_prompt, transcript_text, MODEL)


def append_buddy_log(session_id: str, provider: str, model: str, reaction: str) -> None:
    if not reaction.strip():
        return
    BUDDY_DIR.mkdir(parents=True, exist_ok=True)
    log_path = BUDDY_DIR / f"{session_id}.log"
    persona = os.environ.get("BUDDY_PERSONA", "").strip().lower()
    if persona not in PERSONAS:
        persona = "general"
    entry = {
        "ts": datetime.now().isoformat(),
        "session_id": session_id,
        "kind": "review",
        "provider": provider,
        "model": model,
        "persona": persona,
        "reaction": reaction,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _selected_persona() -> str:
    persona = os.environ.get("BUDDY_PERSONA", "").strip().lower()
    return persona if persona in PERSONAS else "general"


def _checkpoint_delivery_path(session_id: str) -> Path:
    safe_session = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)[:120]
    return BUDDY_DIR / f"{safe_session}.checkpoint-delivery.json"


def mark_checkpoint_delivery(
    session_id: str,
    *,
    prompt_offset: int,
    transcript_path: str,
    reason: str,
) -> None:
    """Remember a delivered checkpoint without retaining its text."""
    try:
        transcript_offset = Path(transcript_path).stat().st_size if transcript_path else 0
        BUDDY_DIR.mkdir(parents=True, exist_ok=True)
        _checkpoint_delivery_path(session_id).write_text(
            json.dumps(
                {
                    "prompt_offset": max(0, int(prompt_offset)),
                    "transcript_offset": max(0, int(transcript_offset)),
                    "reason": reason,
                }
            ),
            encoding="utf-8",
        )
    except (OSError, TypeError, ValueError) as exc:
        log_error(f"checkpoint delivery state failed: {exc}")


def checkpoint_stop_overlap(
    session_id: str, *, prompt_offset: int, transcript_path: str
) -> bool:
    """True when no new tool evidence followed a same-turn checkpoint."""
    try:
        state = json.loads(
            _checkpoint_delivery_path(session_id).read_text(encoding="utf-8")
        )
        if int(state.get("prompt_offset") or 0) != max(0, int(prompt_offset)):
            return False
        checkpoint_offset = int(state.get("transcript_offset") or 0)
    except (OSError, TypeError, ValueError):
        return False
    return not bool(read_recent_tool_evidence(transcript_path, checkpoint_offset).strip())


def record_review_telemetry(
    *,
    session_id: str,
    kind: str,
    reason: str,
    status: str,
    input_chars: int,
    latency_ms: int,
    source_fingerprint: str,
    shadow_candidates: list[str],
    usage: dict | None = None,
) -> None:
    """Record content-free local metadata; telemetry failure never blocks hooks."""
    try:
        review_telemetry.record_review(
            BUDDY_DIR,
            {
                "session_id": session_id,
                "kind": kind,
                "reason": reason,
                "provider": PROVIDER,
                "model": MODEL,
                "persona": _selected_persona(),
                "status": status,
                "input_chars": input_chars,
                "latency_ms": latency_ms,
                "source_fingerprint": source_fingerprint,
                "shadow_candidates": shadow_candidates,
                "usage": usage or {},
            },
        )
    except Exception as exc:
        log_error(f"review telemetry failed: {exc}")


def build_stop_source_context(hook: dict, agentcam_content: str = "") -> dict:
    session_id = str(hook.get("session_id") or "unknown")
    transcript_path = str(hook.get("transcript_path") or "")
    state = source_context.load_source_state(BUDDY_DIR, session_id)
    offset = int(state.get("transcript_offset") or 0)
    last_assistant = str(hook.get("last_assistant_message") or "")
    if not last_assistant:
        last_assistant = read_latest_assistant_text(transcript_path, offset)
    tool_evidence = read_recent_tool_evidence(transcript_path, offset)
    agentcam_evidence = source_context.extract_agentcam_evidence(agentcam_content)

    if not any((last_assistant, tool_evidence, agentcam_evidence)):
        packet = read_recent_transcript(transcript_path)
    else:
        packet = source_context.build_stop_packet(
            task_anchor=str(state.get("task_anchor") or ""),
            last_assistant_message=last_assistant,
            tool_evidence=tool_evidence,
            agentcam_evidence=agentcam_evidence,
        )
    overlap = checkpoint_stop_overlap(
        session_id,
        prompt_offset=offset,
        transcript_path=transcript_path,
    )
    return {
        "packet": packet,
        "tool_evidence": tool_evidence,
        "agentcam_evidence": agentcam_evidence,
        "checkpoint_overlap": overlap,
    }


def build_stop_source_packet(hook: dict, agentcam_content: str = "") -> str:
    """Backward-compatible packet-only wrapper."""
    return str(build_stop_source_context(hook, agentcam_content)["packet"])


def main() -> None:
    hook = read_hook_input()
    session_id = hook.get("session_id", "unknown")
    cwd = hook.get("cwd") or os.getcwd()

    report = read_latest_agentcam_report(cwd)
    report_content = ""
    if report and report["mtime"] > load_agentcam_last_mtime(session_id):
        report_content = report["content"]
        save_agentcam_last_mtime(session_id, report["mtime"])

    source = build_stop_source_context(hook, report_content)
    source_packet = str(source["packet"])
    if not source_packet:
        log_error("empty source packet, skipping")
        return

    system_prompt = build_system_prompt()
    if not system_prompt:
        return

    # --- recent reactions context ---
    recent = read_recent_reactions(session_id)

    context_parts = []
    if recent:
        context_parts.append("[你最近說過]")
        for r in recent:
            context_parts.append(f"- {r}")
        context_parts.append("[避免重複上面的話，可以接著講]")
    context_parts.append("")
    context_parts.append(source_packet)

    enriched_text = "\n".join(context_parts)

    candidates = review_telemetry.stop_shadow_candidates(
        tool_evidence=str(source["tool_evidence"]),
        agentcam_evidence=str(source["agentcam_evidence"]),
        checkpoint_overlap=bool(source["checkpoint_overlap"]),
    )
    fingerprint = hashlib.sha256(
        f"{system_prompt}\0{enriched_text}".encode("utf-8", errors="replace")
    ).hexdigest()[:24]
    started = time.perf_counter()
    call_result = dispatch_call_result(system_prompt, enriched_text)
    latency_ms = round((time.perf_counter() - started) * 1000)
    raw_reaction = str(call_result.get("finding") or "")
    reaction = sanitize_reaction(raw_reaction)
    if reaction:
        append_buddy_log(session_id, PROVIDER, MODEL, reaction)
    else:
        log_error("empty reaction, not logged")
    status = str(call_result.get("status") or "error")
    if status == "finding" and not reaction:
        status = "error"
    record_review_telemetry(
        session_id=str(session_id),
        kind="stop",
        reason="stop",
        status=status,
        input_chars=len(system_prompt) + len(enriched_text),
        latency_ms=latency_ms,
        source_fingerprint=fingerprint,
        shadow_candidates=candidates,
        usage=call_result.get("usage") if isinstance(call_result, dict) else {},
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
