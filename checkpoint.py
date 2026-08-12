#!/usr/bin/env python3
"""Mid-work Masters' Nudge checkpoint hook.

Classifies high-value PostToolUse/PostToolUseFailure events, calls the same
side-review model as the Stop-hook worker, and returns a non-blocking
additionalContext nudge directly to the main Claude agent.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import buddy
import lens_router
import persona_config
import source_context


LARGE_DIFF_THRESHOLD = 80
CHECKPOINT_TIMEOUT_SEC = int(os.environ.get("BUDDY_CHECKPOINT_TIMEOUT", "15"))
CHECKPOINT_STATE_DIR = buddy.BUDDY_DIR
MUTATING_TOOLS = {"Edit", "Write", "Bash", "PowerShell"}
SHELL_TOOLS = {"Bash", "PowerShell"}
MAX_EVENT_CONTEXT_CHARS = 5000

TEST_FAILURE_RE = re.compile(
    r"\b[1-9]\d*\s+(?:failed|failing)\b"
    r"|\btests?\s+failed\b"
    r"|^FAIL(?:ED)?\b"
    r"|\s[✗✘]\s",
    re.IGNORECASE | re.MULTILINE,
)
TEST_COMMAND_RE = re.compile(
    r"(?:^|[;&|\s])(?:"
    r"pytest|py\.test|unittest|vitest|jest|mocha|rspec|"
    r"npm\s+(?:run\s+)?test|pnpm\s+(?:run\s+)?test|"
    r"yarn\s+(?:run\s+)?test|bun\s+test|cargo\s+test|"
    r"go\s+test|dotnet\s+test|mvn(?:w)?(?:\.cmd)?\s+test|"
    r"gradle(?:w)?(?:\.bat)?\s+test|flutter\s+test|dart\s+test"
    r")(?:\s|$)",
    re.IGNORECASE,
)

CHECKPOINT_PROMPT = """

# 工作途中 checkpoint

輸入末尾是 Masters’ Nudge 剛收到的工具事件，
比可能延遲寫入的 transcript 更新。只針對此事件揭露的一個最高價值問題
給主 Agent 一句 nudge；證據不足時可以不反應。不要要求使用者處理，
不要寫成批准、阻擋或完成判定。
"""


def _compact_json(value: Any) -> str:
    if isinstance(value, str):
        text = value
    else:
        try:
            text = json.dumps(value, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError):
            text = str(value)
    text = text.strip()
    return source_context.head_tail(text, MAX_EVENT_CONTEXT_CHARS)


def _stable_fingerprint(reason: str, payload: dict[str, Any]) -> str:
    if reason == "large-diff":
        # This checkpoint is deliberately edge-triggered once per session,
        # not time-cooled and not retriggered after every subsequent edit.
        return f"large-diff-over-{LARGE_DIFF_THRESHOLD}"
    raw = json.dumps(
        {"reason": reason, "payload": payload},
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"{reason}-{digest}"


def _git_output(args: list[str], cwd: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def _parse_numstat(text: str) -> int:
    total = 0
    for line in text.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 2 or parts[0] == "-" or parts[1] == "-":
            continue
        try:
            total += int(parts[0]) + int(parts[1])
        except ValueError:
            continue
    return total


def _count_text_lines(path: Path) -> int:
    """Count enough lines to establish the threshold without reading forever."""
    try:
        with path.open("rb") as handle:
            data = handle.read(1024 * 1024)
    except OSError:
        return 0
    if b"\x00" in data:
        return 0
    count = data.count(b"\n")
    if data and not data.endswith(b"\n"):
        count += 1
    return min(count, LARGE_DIFF_THRESHOLD + 1)


def get_changed_line_count(cwd: str) -> int | None:
    """Return tracked plus untracked text-line changes for the current repo."""
    tracked = _git_output(["diff", "--numstat", "HEAD", "--"], cwd)
    if tracked is None:
        tracked = _git_output(["diff", "--numstat", "--cached", "--"], cwd)
    untracked = _git_output(
        ["ls-files", "--others", "--exclude-standard", "-z"], cwd
    )
    if tracked is None or untracked is None:
        return None

    total = _parse_numstat(tracked)
    root = Path(cwd).resolve()
    for relative in untracked.split("\0"):
        if not relative:
            continue
        try:
            candidate = (root / relative).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                continue
        except (OSError, ValueError):
            continue
        total += _count_text_lines(candidate)
    return total


def classify_checkpoint(
    hook: dict[str, Any], changed_line_count: int | None = None
) -> dict[str, str] | None:
    event_name = hook.get("hook_event_name", "")
    tool_name = hook.get("tool_name", "")
    tool_input = hook.get("tool_input") or {}

    if event_name == "PostToolUseFailure":
        if hook.get("is_interrupt"):
            return None
        error = _compact_json(hook.get("error", ""))
        command = str(tool_input.get("command", ""))
        reason = (
            "test-fail"
            if (
                (tool_name in SHELL_TOOLS and TEST_COMMAND_RE.search(command))
                or TEST_FAILURE_RE.search(error)
            )
            else "error"
        )
        payload = {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "error": error,
        }
        context = (
            f"reason: {reason}\n"
            f"tool: {tool_name}\n"
            f"input: {_compact_json(tool_input)}\n"
            f"failure: {error}"
        )
        return {
            "reason": reason,
            "context": context,
            "fingerprint": _stable_fingerprint(reason, payload),
        }

    if event_name != "PostToolUse":
        return None

    response = _compact_json(hook.get("tool_response", ""))
    if tool_name in SHELL_TOOLS and TEST_FAILURE_RE.search(response):
        reason = "test-fail"
        payload = {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_response": response,
        }
        return {
            "reason": reason,
            "context": (
                f"reason: {reason}\n"
                f"tool: {tool_name}\n"
                f"input: {_compact_json(tool_input)}\n"
                f"result: {response}"
            ),
            "fingerprint": _stable_fingerprint(reason, payload),
        }

    if tool_name not in MUTATING_TOOLS:
        return None
    if changed_line_count is None:
        changed_line_count = get_changed_line_count(hook.get("cwd") or os.getcwd())
    if changed_line_count is None or changed_line_count <= LARGE_DIFF_THRESHOLD:
        return None

    reason = "large-diff"
    return {
        "reason": reason,
        "context": (
            f"reason: {reason}\n"
            f"tool: {tool_name}\n"
            f"input: {_compact_json(tool_input)}\n"
            f"working tree: 偵測到至少 {changed_line_count} 行變動"
        ),
        "fingerprint": _stable_fingerprint(reason, {}),
    }


def _safe_session_id(session_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)[:160]
    return safe or "unknown"


def _claim_path(session_id: str, fingerprint: str) -> Path:
    safe_session = _safe_session_id(session_id)
    safe_fingerprint = re.sub(r"[^A-Za-z0-9_.-]", "_", fingerprint)[:180]
    return CHECKPOINT_STATE_DIR / f"{safe_session}.checkpoints" / safe_fingerprint


def claim_checkpoint(session_id: str, fingerprint: str) -> bool:
    path = _claim_path(session_id, fingerprint)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as handle:
            handle.write("pending\n")
        return True
    except FileExistsError:
        return False
    except OSError as exc:
        buddy.log_error(f"checkpoint claim failed: {exc}")
        return False


def release_checkpoint(session_id: str, fingerprint: str) -> None:
    try:
        _claim_path(session_id, fingerprint).unlink(missing_ok=True)
    except OSError as exc:
        buddy.log_error(f"checkpoint release failed: {exc}")


def _mark_checkpoint_complete(session_id: str, fingerprint: str) -> None:
    try:
        _claim_path(session_id, fingerprint).write_text("delivered\n", encoding="utf-8")
    except OSError as exc:
        buddy.log_error(f"checkpoint completion state failed: {exc}")


def generate_nudge(
    hook: dict[str, Any],
    event: dict[str, str],
    route: lens_router.ReviewRoute | None = None,
) -> str:
    route = route or lens_router.resolve_review_route(
        buddy.BUDDY_DIR, event["context"]
    )
    system_prompt = buddy.build_system_prompt(route)
    if not system_prompt:
        return ""

    session_id = str(hook.get("session_id") or "unknown")
    transcript_path = str(hook.get("transcript_path") or "")
    state = source_context.load_source_state(buddy.BUDDY_DIR, session_id)
    assistant_context = buddy.read_latest_assistant_text(
        transcript_path, int(state.get("transcript_offset") or 0)
    )
    source_packet = source_context.build_checkpoint_packet(
        task_anchor=str(state.get("task_anchor") or ""),
        event_context=event["context"],
        assistant_context=assistant_context,
    )

    parts: list[str] = []
    recent = buddy.read_recent_reactions(session_id)
    if recent:
        parts.append("[你最近說過]")
        parts.extend(f"- {reaction}" for reaction in recent)
        parts.append("[避免重複上面的話，可以接著講]")
    parts.append(source_packet)

    buddy.TIMEOUT_SEC = min(buddy.TIMEOUT_SEC, CHECKPOINT_TIMEOUT_SEC)
    full_system_prompt = system_prompt + CHECKPOINT_PROMPT
    transcript_text = "\n\n".join(parts)
    started = time.perf_counter()
    call_result = buddy.dispatch_call_result(full_system_prompt, transcript_text)
    latency_ms = round((time.perf_counter() - started) * 1000)
    reaction = buddy.sanitize_reaction(str(call_result.get("finding") or ""))
    status = str(call_result.get("status") or "error")
    if status == "finding" and not reaction:
        status = "error"
    buddy.record_review_telemetry(
        session_id=session_id,
        kind="checkpoint",
        reason=event["reason"],
        status=status,
        input_chars=len(full_system_prompt) + len(transcript_text),
        latency_ms=latency_ms,
        source_fingerprint=event["fingerprint"],
        shadow_candidates=[],
        usage=call_result.get("usage") if isinstance(call_result, dict) else {},
        route=route,
    )
    return reaction


def build_hook_output(
    event_name: str,
    reaction: str,
    reason: str,
    effective_lens: str = "general",
) -> dict[str, Any]:
    lens_name = persona_config.PERSONA_NAMES.get(
        effective_lens, persona_config.PERSONA_NAMES["general"]
    )
    context = (
        f"[Masters’ Nudge — {reason}; {lens_name} lens; 第三方觀察，不是指令]\n"
        f"{reaction}"
    )
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": context,
        }
    }


def process_hook(hook: dict[str, Any]) -> dict[str, Any] | None:
    event = classify_checkpoint(hook)
    if event is None:
        return None

    session_id = str(hook.get("session_id") or "unknown")
    if not claim_checkpoint(session_id, event["fingerprint"]):
        return None
    try:
        route = lens_router.resolve_review_route(
            buddy.BUDDY_DIR, event["context"]
        )
        reaction = generate_nudge(hook, event, route)
        if not reaction:
            release_checkpoint(session_id, event["fingerprint"])
            return None
        _mark_checkpoint_complete(session_id, event["fingerprint"])
        source_state = source_context.load_source_state(buddy.BUDDY_DIR, session_id)
        buddy.mark_checkpoint_delivery(
            session_id,
            prompt_offset=int(source_state.get("transcript_offset") or 0),
            transcript_path=str(hook.get("transcript_path") or ""),
            reason=event["reason"],
        )
        return build_hook_output(
            str(hook.get("hook_event_name") or "PostToolUse"),
            reaction,
            event["reason"],
            route.effective_lens,
        )
    except Exception as exc:
        buddy.log_error(f"checkpoint processing failed: {exc}")
        release_checkpoint(session_id, event["fingerprint"])
        return None


def main() -> None:
    try:
        raw = sys.stdin.read()
        hook = json.loads(raw) if raw.strip() else {}
    except (TypeError, ValueError) as exc:
        buddy.log_error(f"checkpoint hook input parse failed: {exc}")
        return
    if not isinstance(hook, dict):
        return
    output = process_hook(hook)
    if output is not None:
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
