#!/usr/bin/env python3
"""Buddy_similar — Stop hook worker.

Reads the transcript path from the Stop-hook JSON on stdin, gathers the recent
turns, dispatches to the configured provider's CLI (OpenAI Codex by default,
or Anthropic Claude via BUDDY_PROVIDER=anthropic) with the Buddy personality
prompt, and appends the reaction to the per-session log at
~/.claude/buddy/<session_id>.log.

Never raises out of main() — hook must not block on our errors.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

CLAUDE_DIR = Path(os.environ.get("BUDDY_CLAUDE_DIR", os.path.expanduser("~/.claude")))
SCRIPT_DIR = Path(__file__).resolve().parent
PROMPT_FILE = SCRIPT_DIR / "buddy-prompt.txt"
BUDDY_DIR = CLAUDE_DIR / "buddy"
ERROR_LOG = CLAUDE_DIR / "buddy-error.log"

PROVIDER = os.environ.get("BUDDY_PROVIDER", "openai").lower()
# BUDDY_MODEL meaning depends on provider:
#   anthropic: sonnet (default), opus, haiku
#   openai/codex: gpt-5.5 (default), other model names codex CLI accepts
_DEFAULT_MODELS = {"anthropic": "sonnet", "openai": "gpt-5.5", "codex": "gpt-5.5"}
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
#   responses mid-sentence — Buddy then surfaced "content looks incomplete"
#   findings that were actually budget artifacts, not real delivery gaps.
#   5000 lets a typical 2000-4000-char Claude response survive whole.
# - TRANSCRIPT_CHAR_BUDGET capped at 6000 because read_recent_reactions
#   only carries forward the last 3 of Buddy's own reactions — letting the
#   transcript window walk farther back than ~3 turns means Buddy sees old
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


def read_recent_transcript(transcript_path: str) -> str:
    """Build the transcript snippet for Buddy's prompt using a char budget.

    Walk backwards from the newest user/assistant entry, including each one
    in full until the TRANSCRIPT_CHAR_BUDGET is consumed. Entries longer
    than PER_MESSAGE_MAX_CHARS are tail-truncated (with a "…" prefix) before
    the budget check. The oldest included entry may itself be tail-truncated
    to fit the remaining budget — provided at least MIN_REMAINING_TO_INCLUDE
    chars remain (otherwise it is dropped). tool_result content from the
    same selected window flows into a separate trailing block, tail-cropped
    to TOOL_OUTPUT_TAIL_CHARS.

    Output shape (sections are explicitly delimited so Buddy can tell where
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
    if not transcript_path or not os.path.exists(transcript_path):
        return ""
    try:
        # Read only the tail of the JSONL file. Long sessions can produce
        # many-MB transcripts; we only need the last few turns. 64 KB tail
        # comfortably covers TRANSCRIPT_CHAR_BUDGET plus the tool-output
        # tail even when entries arrive as wide JSON envelopes.
        TAIL_BYTES = 65536
        size = os.path.getsize(transcript_path)
        with open(transcript_path, "rb") as f:
            if size > TAIL_BYTES:
                f.seek(size - TAIL_BYTES)
                # Drop the (likely partial) first line from the seek point
                # so JSON parsing below doesn't choke on a half-line.
                f.readline()
            data = f.read()
        lines = data.decode("utf-8", errors="replace").splitlines()
    except Exception as e:
        log_error(f"transcript read failed: {e}")
        return ""

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
        if parsed is None:
            continue
        entries.append(parsed)

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



def read_recent_reactions(session_id: str, max_count: int = 3, max_chars: int = 200) -> list[str]:
    """Read last N Buddy reactions from this session's log."""
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
# Buddy can read AGENT_RUN_REPORT.md generated by `cr` / `agentcam run` and
# include it in the payload sent to the second-opinion model. Dedup is per
# session_id keyed on report file mtime.

AGENTCAM_REPORT_TAIL_CHARS = 2000  # cap inclusion size to keep token cost sane


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
    Content is tail-truncated to AGENTCAM_REPORT_TAIL_CHARS.
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
    if len(content) > AGENTCAM_REPORT_TAIL_CHARS:
        content = content[-AGENTCAM_REPORT_TAIL_CHARS:]
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
        return PROMPT_FILE.read_text(encoding="utf-8")
    except Exception as e:
        log_error(f"prompt file read failed: {e}")
        return ""


def parse_reaction(stdout: str) -> str:
    """Robustly extract Buddy's text from claude CLI stdout.

    Handles both raw-text output and JSON-envelope output.
    """
    stdout = stdout.strip()
    if not stdout:
        return ""
    if stdout.startswith("{"):
        try:
            obj = json.loads(stdout)
            if isinstance(obj, dict):
                for k in ("result", "content", "text"):
                    v = obj.get(k)
                    if isinstance(v, str) and v.strip():
                        return v.strip()
        except Exception:
            pass
    return stdout


def call_claude(system_prompt: str, transcript_text: str, model: str) -> str:
    user_prompt = "請對 stdin 提供的對話片段寫一句簡短的旁觀者反應。"

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
            return ""
        return parse_reaction(r.stdout)
    except subprocess.TimeoutExpired:
        log_error("claude CLI timeout")
        return ""
    except FileNotFoundError:
        log_error("claude CLI not found in PATH")
        return ""
    finally:
        try:
            os.unlink(fd.name)
        except OSError:
            pass


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


def call_codex(system_prompt: str, transcript_text: str, model: str) -> str:
    """Invoke codex exec for OpenAI-side critique. Returns last assistant message."""
    codex_bin = _resolve_codex_bin()
    if not codex_bin:
        log_error("codex CLI not found (checked PATH + common npm paths)")
        return ""

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
            "-s", "read-only",
            "-m", model,
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
            return ""
        try:
            with open(output_fd.name, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            log_error(f"codex output read failed: {e}")
            return ""
    except subprocess.TimeoutExpired:
        log_error("codex timeout")
        return ""
    except FileNotFoundError:
        log_error(f"codex CLI not executable: {codex_bin}")
        return ""
    finally:
        try:
            os.unlink(output_fd.name)
        except OSError:
            pass


_WRAPPER_RE = re.compile(r"\[(?:end )?Buddy[^\]]*\]")
_CODEBLOCK_RE = re.compile(r"```[\s\S]*?```")
_INLINE_CODE_RE = re.compile(r"`([^`]*)`")
_MD_BOLD_RE = re.compile(r"\*{1,3}([^*]+)\*{1,3}")
_MD_HEADER_RE = re.compile(r"^#{1,6}\s*", re.MULTILINE)
MAX_REACTION_CHARS = 28


def sanitize_reaction(raw: str) -> str:
    """Clean model output before logging.

    - Strip code blocks and markdown formatting
    - Remove wrapper collision markers ([end Buddy], [Buddy ...])
    - Collapse whitespace
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
    if len(text) > MAX_REACTION_CHARS:
        text = text[:MAX_REACTION_CHARS]
    return text


def dispatch_call(system_prompt: str, transcript_text: str) -> str:
    """Route to the right provider based on BUDDY_PROVIDER."""
    if PROVIDER in ("openai", "codex"):
        return call_codex(system_prompt, transcript_text, MODEL)
    return call_claude(system_prompt, transcript_text, MODEL)


def append_buddy_log(session_id: str, provider: str, model: str, reaction: str) -> None:
    if not reaction.strip():
        return
    BUDDY_DIR.mkdir(parents=True, exist_ok=True)
    log_path = BUDDY_DIR / f"{session_id}.log"
    entry = {
        "ts": datetime.now().isoformat(),
        "session_id": session_id,
        "provider": provider,
        "model": model,
        "reaction": reaction,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> None:
    hook = read_hook_input()
    transcript_path = hook.get("transcript_path", "")
    session_id = hook.get("session_id", "unknown")
    cwd = hook.get("cwd") or os.getcwd()

    transcript_text = read_recent_transcript(transcript_path)
    if not transcript_text:
        log_error("empty transcript, skipping")
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
    context_parts.append(transcript_text)

    # --- agentcam report (only if a *new* report has appeared this session) ---
    report = read_latest_agentcam_report(cwd)
    if report and report["mtime"] > load_agentcam_last_mtime(session_id):
        context_parts.append("")
        context_parts.append("[agentcam report — 此 run 的 git/檔案/風險旗 authoritative 來源]")
        context_parts.append(report["content"])
        context_parts.append("[end agentcam report]")
        save_agentcam_last_mtime(session_id, report["mtime"])

    enriched_text = "\n".join(context_parts)

    raw_reaction = dispatch_call(system_prompt, enriched_text)
    reaction = sanitize_reaction(raw_reaction)
    if reaction:
        append_buddy_log(session_id, PROVIDER, MODEL, reaction)
    else:
        log_error("empty reaction, not logged")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
