#!/usr/bin/env python3
"""Masters' Nudge — Stop hook worker.

Reads the transcript path from the Stop-hook JSON on stdin, gathers the recent
turns, dispatches to the configured provider's CLI (Anthropic by default for
this Claude host; explicitly overridable), and appends the reaction to the
host-namespaced local data log.

Never raises out of main() — hook must not block on our errors.
"""

import json
import hashlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import source_context
import review_telemetry
import persona_config
import lens_router
from masters_nudge.contracts import EvidenceBundle, ReviewRequest, SessionRef, find_git_root
from masters_nudge.core import ReviewCore
from masters_nudge import providers as shared_providers
from masters_nudge import prompting as shared_prompting
from masters_nudge.runtime import (
    DEFAULT_MODELS,
    RuntimePaths,
    RuntimeSettings,
    active_guard,
)

SCRIPT_DIR = Path(__file__).resolve().parent
_RUNTIME = RuntimeSettings.from_env(SCRIPT_DIR, host="claude_code")
CLAUDE_DIR = _RUNTIME.paths.legacy_data_dir.parent
PROMPT_FILE = SCRIPT_DIR / "buddy-prompt.txt"
OUTPUT_SCHEMA_FILE = SCRIPT_DIR / "reaction-schema.json"
PERSONA_DIR = SCRIPT_DIR / "personas"
BUDDY_DIR = _RUNTIME.paths.data_dir
ERROR_LOG = _RUNTIME.paths.error_log
MAX_REACTION_CHARS = shared_prompting.MAX_REACTION_CHARS

PERSONAS = persona_config.LENS_PERSONAS

PROVIDER = _RUNTIME.provider
_DEFAULT_MODELS = DEFAULT_MODELS
MODEL = _RUNTIME.model
TIMEOUT_SEC = _RUNTIME.timeout_sec
OLLAMA_URL = _RUNTIME.ollama_url

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


def build_system_prompt(route: lens_router.ReviewRoute | None = None) -> str:
    """Backward-compatible entry point backed by the shared prompt contract."""
    return shared_prompting.build_system_prompt(
        prompt_file=PROMPT_FILE,
        persona_dir=PERSONA_DIR,
        data_dir=BUDDY_DIR,
        route=route,
        log_error=log_error,
    )


def load_output_schema_json() -> str:
    """Backward-compatible entry point backed by the shared schema loader."""
    return shared_providers.load_output_schema_json(OUTPUT_SCHEMA_FILE, log_error)


def parse_reaction_result(stdout: str) -> dict:
    """Backward-compatible entry point backed by the shared output parser."""
    return shared_providers.parse_reaction_result(stdout)


def parse_reaction(stdout: str) -> str:
    """Backward-compatible finding-only wrapper."""
    return str(parse_reaction_result(stdout)["finding"])


def parse_usage(stdout: str) -> dict[str, int]:
    """Backward-compatible entry point backed by shared usage parsing."""
    return shared_providers.parse_usage(stdout)


def call_claude_result(
    system_prompt: str,
    transcript_text: str,
    model: str,
    *,
    capture_raw: bool = False,
) -> dict:
    """Backward-compatible entry point backed by the shared Claude client."""
    return shared_providers.call_claude_result(
        system_prompt,
        transcript_text,
        model,
        schema_path=OUTPUT_SCHEMA_FILE,
        timeout_sec=TIMEOUT_SEC,
        capture_raw=capture_raw,
        log_error=log_error,
    )


def call_claude(system_prompt: str, transcript_text: str, model: str) -> str:
    """Backward-compatible finding-only wrapper."""
    return str(call_claude_result(system_prompt, transcript_text, model)["finding"])


def _resolve_codex_bin() -> str | None:
    """Backward-compatible entry point backed by shared executable discovery."""
    return shared_providers.resolve_codex_bin()


def call_codex_result(
    system_prompt: str,
    transcript_text: str,
    model: str,
    *,
    capture_raw: bool = False,
) -> dict:
    """Backward-compatible entry point backed by the shared Codex client."""
    return shared_providers.call_codex_result(
        system_prompt,
        transcript_text,
        model,
        schema_path=OUTPUT_SCHEMA_FILE,
        timeout_sec=TIMEOUT_SEC,
        capture_raw=capture_raw,
        log_error=log_error,
        codex_bin_resolver=_resolve_codex_bin,
    )


def call_codex(system_prompt: str, transcript_text: str, model: str) -> str:
    """Backward-compatible finding-only wrapper."""
    return str(call_codex_result(system_prompt, transcript_text, model)["finding"])


def sanitize_reaction(raw: str) -> str:
    """Backward-compatible entry point backed by shared output sanitation."""
    return shared_prompting.sanitize_reaction(raw)


def dispatch_call(system_prompt: str, transcript_text: str) -> str:
    """Route to the configured reviewer provider."""
    return str(dispatch_call_result(system_prompt, transcript_text)["finding"])


def dispatch_call_result(system_prompt: str, transcript_text: str) -> dict:
    """Compatibility wrapper around the host-neutral provider boundary."""
    return shared_providers.dispatch_call_result(
        PROVIDER,
        system_prompt,
        transcript_text,
        MODEL,
        schema_path=OUTPUT_SCHEMA_FILE,
        timeout_sec=TIMEOUT_SEC,
        ollama_url=OLLAMA_URL,
        log_error=log_error,
    )


def append_buddy_log(
    session_id: str,
    provider: str,
    model: str,
    reaction: str,
    route: lens_router.ReviewRoute | None = None,
) -> None:
    if not reaction.strip():
        return
    BUDDY_DIR.mkdir(parents=True, exist_ok=True)
    log_path = BUDDY_DIR / f"{session_id}.log"
    route = route or lens_router.resolve_review_route(BUDDY_DIR)
    entry = {
        "ts": datetime.now().isoformat(),
        "session_id": session_id,
        "kind": "review",
        "provider": provider,
        "model": model,
        "persona": _selected_persona(route),
        **route_metadata(route),
        "reaction": reaction,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _selected_persona(route: lens_router.ReviewRoute | None = None) -> str:
    persona = (route or lens_router.resolve_review_route(BUDDY_DIR)).effective_lens
    return persona if persona in PERSONAS else "general"


def route_metadata(route: lens_router.ReviewRoute) -> dict[str, str]:
    """Backward-compatible entry point backed by shared route metadata."""
    return shared_prompting.route_metadata(route)


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
    route: lens_router.ReviewRoute | None = None,
) -> None:
    """Record content-free local metadata; telemetry failure never blocks hooks."""
    try:
        route = route or lens_router.resolve_review_route(BUDDY_DIR)
        review_telemetry.record_review(
            BUDDY_DIR,
            {
                "session_id": session_id,
                "kind": kind,
                "reason": reason,
                "provider": PROVIDER,
                "model": MODEL,
                "persona": _selected_persona(route),
                **route_metadata(route),
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
    if active_guard():
        return
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

    candidates = review_telemetry.stop_shadow_candidates(
        tool_evidence=str(source["tool_evidence"]),
        agentcam_evidence=str(source["agentcam_evidence"]),
        checkpoint_overlap=bool(source["checkpoint_overlap"]),
    )
    session = SessionRef(
        "claude_code",
        str(session_id),
        cwd=str(cwd),
        repo_root=find_git_root(str(cwd)),
    )
    request = ReviewRequest(
        schema_version=1,
        kind="stop",
        reason="stop",
        session=session,
        evidence=EvidenceBundle(
            task_anchor=str(
                source_context.load_source_state(BUDDY_DIR, str(session_id)).get(
                    "task_anchor"
                )
                or ""
            ),
            assistant_claim=str(hook.get("last_assistant_message") or ""),
            tool_evidence=str(source["tool_evidence"]),
            agentcam_evidence=str(source["agentcam_evidence"]),
        ),
        source_packet=source_packet,
        source_fingerprint=hashlib.sha256(
            source_packet.encode("utf-8", errors="replace")
        ).hexdigest()[:24],
        shadow_candidates=tuple(candidates),
    )

    settings = RuntimeSettings(
        provider=PROVIDER,
        model=MODEL,
        timeout_sec=TIMEOUT_SEC,
        checkpoint_timeout_sec=_RUNTIME.checkpoint_timeout_sec,
        paths=RuntimePaths(
            runtime_dir=SCRIPT_DIR,
            data_dir=BUDDY_DIR,
            legacy_data_dir=CLAUDE_DIR / "buddy",
            error_log=ERROR_LOG,
        ),
        ollama_url=_RUNTIME.ollama_url,
        configuration_source=_RUNTIME.configuration_source,
        configuration_error=_RUNTIME.configuration_error,
    )

    ReviewCore(settings, log_error=log_error).review(
        request, persist_reaction=True
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
