#!/usr/bin/env python3
"""Masters' Nudge — Claude Stop hook worker.

Reads the transcript path from the Stop-hook JSON on stdin, gathers the recent
turns, dispatches to the configured provider's CLI (Anthropic by default for
this Claude host; explicitly overridable), and appends the reaction to the
host-namespaced local data log.

Never raises out of main() — hook must not block on our errors.
"""

import json
import hashlib
import os
import sys
from pathlib import Path

import source_context
import review_telemetry
from masters_nudge import evidence as shared_evidence, storage
from masters_nudge.contracts import EvidenceBundle, ReviewRequest, SessionRef, find_git_root
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import RuntimeSettings, active_guard

SCRIPT_DIR = Path(__file__).resolve().parent
_RUNTIME = RuntimeSettings.from_env(SCRIPT_DIR, host="claude_code")

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


def log_error(msg: str) -> None:
    storage.append_error(_RUNTIME.paths.error_log, "claude-stop", msg)


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



def build_stop_source_context(hook: dict, agentcam_content: str = "") -> dict:
    session_id = str(hook.get("session_id") or "unknown")
    cwd = str(hook.get("cwd") or "")
    session = SessionRef(
        "claude_code",
        session_id,
        turn_id=str(hook.get("turn_id") or ""),
        cwd=cwd,
        repo_root=find_git_root(cwd),
    )
    transcript_path = str(hook.get("transcript_path") or "")
    state = storage.load_turn_state(_RUNTIME.paths.data_dir, session)
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
    overlap = storage.checkpoint_stop_overlap(
        _RUNTIME.paths.data_dir,
        session,
        tool_evidence=tool_evidence,
    )
    return {
        "packet": packet,
        "task_anchor": str(state.get("task_anchor") or ""),
        "tool_evidence": tool_evidence,
        "agentcam_evidence": agentcam_evidence,
        "checkpoint_overlap": overlap,
    }
def main() -> None:
    if active_guard():
        return
    hook = read_hook_input()
    session_id = hook.get("session_id", "unknown")
    cwd = hook.get("cwd") or os.getcwd()
    session = SessionRef(
        "claude_code",
        str(session_id),
        turn_id=str(hook.get("turn_id") or ""),
        cwd=str(cwd),
        repo_root=find_git_root(str(cwd)),
    )

    report = shared_evidence.read_latest_agentcam_report(
        str(cwd), log_error=log_error
    )
    report_content = ""
    if report and float(report["mtime"]) > storage.load_agentcam_mtime(
        _RUNTIME.paths.data_dir, session
    ):
        report_content = report["content"]
        storage.save_agentcam_mtime(
            _RUNTIME.paths.data_dir, session, float(report["mtime"])
        )

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
    request = ReviewRequest(
        schema_version=1,
        kind="stop",
        reason="stop",
        session=session,
        evidence=EvidenceBundle(
            task_anchor=str(source["task_anchor"]),
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

    ReviewCore(_RUNTIME, log_error=log_error).review(
        request, persist_reaction=True
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
