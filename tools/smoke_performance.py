#!/usr/bin/env python3
"""Offline synthetic integration smoke; never launch an Actor or live Provider.

The fixed stub intentionally cannot demonstrate diagnostic/model quality.
All journal data stays in a fresh temporary directory. Only --output persists.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "experiments" / "carmack-performance" / "fixtures"
sys.path.insert(0, str(ROOT))

from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.contracts import ProviderRun, SessionRef
from masters_nudge.core import NudgeCore
from masters_nudge.prompting import delivery_text
from masters_nudge.provider_contract import parse_feedback
from masters_nudge.runtime import RuntimeSettings


def require(condition: bool, message: str):
    if not condition:
        raise RuntimeError(message)


def read_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def replace_paths(value, replacements):
    if isinstance(value, str):
        for source, replacement in replacements:
            value = value.replace(source, replacement)
        return value
    if isinstance(value, list):
        return [replace_paths(item, replacements) for item in value]
    if isinstance(value, tuple):
        return [replace_paths(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: replace_paths(item, replacements) for key, item in value.items()}
    return value


class ScriptedProvider:
    """Return fixed replies by call number; do not infer or select a diagnosis."""

    def __init__(self, replies):
        self.replies = replies
        self.calls = []

    def __call__(self, **kwargs):
        index = len(self.calls)
        require(index < len(self.replies), "Unexpected extra Provider dispatch")
        raw = json.dumps(self.replies[index], ensure_ascii=False)
        parse_feedback(raw)  # The real four-field parser enforces all limits.
        self.calls.append({
            "dispatch_index": index + 1,
            "kind": "SCRIPTED_STUB_NOT_A_MODEL_CALL",
            "system_prompt_sha256": sha256(kwargs["system_prompt"]),
            "nudge_input": kwargs["nudge_input"],
            "configured_model_not_executed": kwargs["model"],
            "schema_path": str(kwargs["schema_path"]),
            "workspace_root": kwargs["workspace_root"],
            "timeout_sec": kwargs["timeout_sec"],
            "remaining_chars": kwargs["remaining_chars"],
            "raw_output": raw,
            "actual_model_usage": None,
            "actual_model_latency_seconds": None,
            "actual_model_cost": None,
        })
        return ProviderRun(raw_output=raw, usage={}, trace=({
            "kind": "offline_scripted_stub",
            "dispatch_index": index + 1,
            "not_model_generated": True,
        },))


def run_smoke() -> dict:
    started_at = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    fixture_names = (
        "windows-ram-only.synthetic.json",
        "windows-pressure-window.synthetic.json",
        "provider-replies.scripted.json",
    )
    first, later, scripted = [read_fixture(name) for name in fixture_names]
    require(first["payload"]["task_request"] == later["payload"]["task_request"],
            "Fixtures must belong to the same exact task request")
    stub = ScriptedProvider(scripted["replies"])
    with tempfile.TemporaryDirectory(prefix="masters-nudge-synthetic-") as raw:
        temporary = Path(raw).resolve()
        workspace = temporary / "git-evidence-workspace"
        workspace.mkdir()
        subprocess.run(["git", "init", "--quiet", str(workspace)], check=True,
                       capture_output=True, text=True, timeout=10)
        (workspace / "SYNTHETIC.txt").write_text(
            "This temporary Git workspace contains no host diagnostic data.\n",
            encoding="utf-8")
        data = temporary / "isolated-data"
        settings = RuntimeSettings.from_env(ROOT, environ={
            "MASTERS_NUDGE_DATA_DIR": str(data),
            "MASTERS_NUDGE_PROFILE": "performance",
            "MASTERS_NUDGE_TEST_MODE": "1",
        })
        require(settings.profile == "performance", "Performance profile was not selected")
        require(settings.paths.data_dir == data / "performance", "Journal is not profile-isolated")
        core = NudgeCore(settings, dispatch=stub)
        adapter = CodexAdapter(core)
        session = SessionRef("synthetic-smoke-session", "synthetic-smoke-turn", str(workspace))
        task = first["payload"]["task_request"]
        checkpoints = []

        # The injected stub is the sole Provider route. Fail closed if a future
        # refactor ignores dependency injection and tries the default Provider.
        with patch("masters_nudge.providers.call_codex_result",
                   side_effect=RuntimeError("LIVE PROVIDER FORBIDDEN IN OFFLINE SMOKE")), \
             patch.dict("os.environ", {"MASTERS_NUDGE_ACTIVE": "0"}):
            adapter.process({"hook_event_name": "UserPromptSubmit",
                             "session_id": session.session_id, "turn_id": session.turn_id,
                             "cwd": session.cwd, "prompt": task})
            require(not stub.calls, "Starting a task must not call Provider")
            ignored = adapter.process({"hook_event_name": "PostToolUse",
                                       "session_id": session.session_id, "turn_id": session.turn_id,
                                       "cwd": session.cwd, "tool_name": "shell",
                                       "tool_use_id": "unrelated-shell",
                                       "tool_input": {"command": "echo fixture"},
                                       "tool_response": "fixture"})
            require(ignored is None and not stub.calls, "Ordinary shell event unexpectedly triggered")

            def checkpoint(name, payload, expected_calls, expected_feedback):
                payload = deepcopy(payload)
                payload["cwd"] = str(workspace)
                step_started = time.monotonic()
                result = core.process_diagnostic(payload)
                elapsed = time.monotonic() - step_started
                require(len(stub.calls) == expected_calls, f"{name}: wrong dispatch count")
                require((result is not None) == expected_feedback, f"{name}: wrong feedback result")
                feedback = asdict(result[1]) if result else None
                actor_text = delivery_text(result[1], profile=settings.profile) if result else None
                if result:
                    # Simulate acknowledgement after local rendering, not Host delivery.
                    core.journal.delivered(result[0])
                checkpoints.append({
                    "name": name,
                    "trigger": "explicit_diagnostic_checkpoint_in_process",
                    "reason": payload["reason"], "progress": payload["progress"],
                    "submitted_materials": payload,
                    "provider_dispatches_total": len(stub.calls),
                    "returned_attempt": result[0] if result else None,
                    "nudge": feedback, "rendered_actor_text": actor_text,
                    "outcome": "scripted_feedback" if result else
                               "deduplicated_no_dispatch" if "duplicate" in name else "scripted_silence",
                    "offline_plumbing_elapsed_seconds": elapsed,
                    "actual_model_tokens": None, "actual_model_latency_seconds": None,
                    "actual_model_cost": None,
                })

            checkpoint("ram_only", first["payload"], 1, True)
            duplicate = deepcopy(first["payload"])
            duplicate["batch_id"] = "renamed-batch-same-ram-evidence"
            duplicate["reason"] = "相同量測重新包裝，不應再次呼叫 Provider。"
            duplicate["progress"] = "僅更換 batch 與 tool call ID；没有新量測。"
            duplicate["evidence"][0]["tool_use_id"] = "renamed-tool-call"
            checkpoint("ram_only_duplicate_rewrapped", duplicate, 1, False)
            checkpoint("new_pressure_window", later["payload"], 2, False)
            reordered = deepcopy(later["payload"])
            reordered["batch_id"] = "renamed-batch-same-pressure-evidence"
            reordered["reason"] = "相同材料反轉順序並改 ID，不是新時間窗。"
            reordered["progress"] = "固定重複輸入測試。"
            reordered["evidence"].reverse()
            for number, item in enumerate(reordered["evidence"]):
                item["tool_use_id"] = f"reordered-renamed-call-{number}"
            checkpoint("pressure_window_duplicate_reordered", reordered, 2, False)

        attempts = core.journal.recent(20)
        require(len(attempts) == 2, "Exactly two judgments must be journaled")
        require(sorted(item["outcome"] for item in attempts) == ["feedback", "silence"],
                "The journal must contain one feedback and one silence")
        expected_batches = {item["payload"]["batch_id"]: item["payload"] for item in (first, later)}
        for attempt in attempts:
            detail = attempt["detail"]
            trigger = detail["trigger"]
            original = expected_batches[trigger["batch_id"]]
            require(trigger["kind"] == "explicit_diagnostic_checkpoint"
                    and trigger["profile"] == "performance"
                    and trigger["evidence_origin"] == "actor_supplied",
                    "The journal did not retain checkpoint provenance")
            require(trigger["reason"] == original["reason"]
                    and trigger["progress"] == original["progress"]
                    and len(trigger["evidence_sha256"]) == 64,
                    "The journal lost trigger reason, progress, or fingerprint")
            require(detail["usage"] == {} and detail["trace"][0]["not_model_generated"] is True,
                    "The journal must identify the stub and cannot invent model usage")
        require(not core.journal.unresolved(), "Smoke left an unresolved judgment")
        expected_prompt = settings.prompt_file.read_text(encoding="utf-8").strip()
        require(all(call["system_prompt_sha256"] == sha256(expected_prompt) for call in stub.calls),
                "The selected performance prompt did not reach the stub")
        require("reported_memory_percent" in stub.calls[0]["nudge_input"],
                "Evidence containing exit_code=0 was lost or summarized as generic success")
        require("available_mib" in stub.calls[1]["nudge_input"],
                "Follow-up pressure-window evidence was lost")
        with core.journal.connect() as db:
            events = [dict(row) for row in db.execute("SELECT * FROM judgment_events ORDER BY seq")]
            batches = [dict(row) for row in db.execute("SELECT * FROM batches ORDER BY received,id")]
        require(all("task_request" not in json.loads(item["payload"]) for item in batches),
                "The batch payload must not duplicate the task request")
        report = {
            "status": "PASS_OFFLINE_SYNTHETIC_SMOKE_ONLY",
            "started_at_utc": started_at,
            "execution_platform": platform.system(),
            "python_version": platform.python_version(),
            "provenance": {
                "evidence": "SYNTHETIC_NOT_WINDOWS_MEASUREMENTS",
                "provider_outputs": "PREWRITTEN_STUB_NOT_MODEL_GENERATED",
                "actor_followup": "PREWRITTEN_FIXTURE_NOT_MODEL_GENERATED",
                "host_hook_delivery": "NOT_RUN",
                "real_windows_diagnosis": "NOT_RUN",
                "live_actor_or_provider": "NOT_RUN",
                "matched_ab": "NOT_RUN",
                "system_configuration_changes": "NONE",
            },
            "profile": settings.profile,
            "fixture_sha256": {name: hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest()
                               for name in fixture_names},
            "checks": ["performance profile and isolated journal", "adapter task-start without Provider",
                       "ordinary shell event ignored", "four-field schema and character limits",
                       "RAM-only scripted feedback", "renamed IDs/reason/progress deduplicate",
                       "new evidence produces scripted silence", "reordered evidence deduplicates",
                       "successful diagnostic output is preserved", "performance prompt is selected",
                       "one feedback and one silence journaled", "journal preserves reason/progress/provenance/fingerprint",
                       "batch payload does not duplicate task request", "no unresolved judgment"],
            "checkpoints": checkpoints,
            "provider_stub_dispatches": stub.calls,
            "journal": {"path": str(core.journal.path), "attempts": attempts,
                        "batches": batches, "events": events},
            "actual_live_model_metrics": {"status": "NOT_RUN", "tokens": None,
                                          "elapsed_seconds": None, "cost": None},
            "offline_total_elapsed_seconds": time.monotonic() - started,
            "allowed_conclusion": "The tested offline profile/checkpoint/evidence/deduplication/schema/journal plumbing works with a fixed stub",
            "forbidden_conclusions": ["Carmack improved Actor diagnosis", "Carmack won an A/B test",
                                      "the user's Windows device has or lacks memory pressure",
                                      "a real model emitted these nudges or chose these measurements"],
        }
        replacements = [(str(temporary), "$SMOKE_TMP"), (str(ROOT), "$REPO")]
        # Journal packets are nested JSON strings, whose Windows slashes are escaped.
        replacements += [(source.replace("\\", "\\\\"), target) for source, target in replacements]
        return replace_paths(report, replacements)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write audit JSON to a NEW file; existing results are never overwritten")
    args = parser.parse_args()
    if args.output and args.output.exists():
        parser.error("output already exists; choose a new path to preserve the prior audit")
    result = run_smoke()
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(text)
        print(json.dumps({"status": result["status"], "output": str(args.output),
                          "stub_dispatches": len(result["provider_stub_dispatches"]),
                          "live_provider": "NOT_RUN", "ab": "NOT_RUN"}, ensure_ascii=False))
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
