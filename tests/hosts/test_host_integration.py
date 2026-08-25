#!/usr/bin/env python3
"""Phase C compatibility and Codex CLI hook contract tests."""

from __future__ import annotations

import inspect
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import review_telemetry
import claude_stop as buddy
import hook_entry
import persona_config
from masters_nudge import providers, storage
from masters_nudge.codex_adapter import CodexAdapter, build_hook_output, normalize_event
from masters_nudge.contracts import (
    PromptSubmitted,
    ReviewOutcome,
    ReviewRequest,
    SessionRef,
    ToolCompleted,
)
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


HERE = Path(__file__).resolve().parents[2]


def settings_for(root: Path) -> RuntimeSettings:
    return RuntimeSettings(
        "openai",
        "test-model",
        60,
        15,
        RuntimePaths(HERE, root / "data", root / "error.log"),
    )


class FakeCore:
    def __init__(self, settings: RuntimeSettings, outcome: ReviewOutcome) -> None:
        self.settings = settings
        self.outcome = outcome
        self.calls: list[tuple[ReviewRequest, bool, int | None]] = []
        self.errors: list[str] = []
        self.log_error = self.errors.append

    def review(
        self,
        request: ReviewRequest,
        *,
        persist_reaction: bool,
        timeout_sec: int | None = None,
    ) -> ReviewOutcome:
        self.calls.append((request, persist_reaction, timeout_sec))
        return self.outcome

    def review_once(
        self,
        request: ReviewRequest,
        *,
        persist_reaction: bool = True,
        timeout_sec: int | None = None,
    ) -> ReviewOutcome:
        return self.review(
            request,
            persist_reaction=persist_reaction,
            timeout_sec=timeout_sec,
        )


class RuntimePathTests(unittest.TestCase):
    def test_default_paths_are_host_neutral_without_legacy_runtime_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = RuntimePaths.resolve(environ={"USERPROFILE": tmpdir})
            self.assertEqual(paths.data_dir, Path(tmpdir) / ".masters-nudge" / "data")
            self.assertFalse(hasattr(paths, "legacy_data_dir"))

    def test_legacy_path_override_does_not_redirect_active_runtime_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = RuntimePaths.resolve(
                environ={"USERPROFILE": tmpdir, "BUDDY_CLAUDE_DIR": "C:/legacy"}
            )
            self.assertEqual(paths.data_dir, Path(tmpdir) / ".masters-nudge" / "data")
            self.assertEqual(
                paths.error_log,
                Path(tmpdir) / ".masters-nudge" / "data" / "error.log",
            )

    def test_new_environment_names_take_precedence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            environment = {
                "USERPROFILE": tmpdir,
                "MASTERS_NUDGE_PROVIDER": "anthropic",
                "BUDDY_PROVIDER": "openai",
                "MASTERS_NUDGE_MODEL": "new-model",
                "BUDDY_MODEL": "old-model",
            }
            settings = RuntimeSettings.from_env(environ=environment)
            self.assertEqual((settings.provider, settings.model), ("anthropic", "new-model"))


class NamespacedStorageTests(unittest.TestCase):
    def test_atomic_state_write_retries_transient_windows_access_denial(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            real_replace = os.replace
            attempts = 0

            def transient_replace(source, destination):
                nonlocal attempts
                attempts += 1
                if attempts < 3:
                    raise PermissionError(13, "file is temporarily busy", destination)
                return real_replace(source, destination)

            with mock.patch(
                "masters_nudge.storage.os.replace", side_effect=transient_replace
            ), mock.patch("masters_nudge.storage.time.sleep") as sleep:
                storage._atomic_write(path, {"status": "queued"})

            self.assertEqual(attempts, 3)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"status": "queued"})
            self.assertEqual(sleep.call_count, 2)

    def test_same_native_session_id_cannot_collide_between_hosts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            claude = SessionRef("claude_code", "same")
            codex = SessionRef("codex_cli", "same")
            self.assertNotEqual(
                storage.reaction_log_path(root, claude),
                storage.reaction_log_path(root, codex),
            )

    def test_reaction_metadata_carries_normalized_workspace_identity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            session = SessionRef("codex_cli", "s", cwd=tmpdir)
            entry = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="m",
                reaction="提醒",
                route_metadata={"effective_lens": "beck"},
            )

            self.assertEqual(entry["workspace"], os.path.normcase(str(root.resolve())))

class ClaudeCompatibilityTests(unittest.TestCase):
    def test_stop_adapter_writes_new_host_namespaced_log(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            settings = settings_for(root)
            hook = {
                "session_id": "claude-session",
                "cwd": str(root),
                "hook_event_name": "Stop",
                "last_assistant_message": "已完成指定流程",
            }
            with (
                mock.patch.object(buddy.claude_adapter, "RUNTIME", settings),
                mock.patch.object(buddy, "read_hook_input", return_value=hook),
                mock.patch.object(
                    buddy.shared_evidence,
                    "read_latest_agentcam_report",
                    return_value=None,
                ),
                mock.patch.object(
                    providers,
                    "dispatch_call_result",
                    return_value={
                        "status": "finding",
                        "finding": "完成宣告仍缺少與需求相同邊界的驗證。",
                        "usage": {},
                    },
                ),
                mock.patch.object(buddy.sys, "stdout", io.StringIO()),
            ):
                buddy.main()
            self.assertTrue(
                (root / "data" / "claude_code--claude-session.log").exists()
            )
            self.assertFalse((root / "data" / "claude-session.log").exists())


class SynchronousHookTests(unittest.TestCase):
    def test_codex_entry_has_no_detached_review_path(self):
        self.assertFalse(hasattr(hook_entry, "_detach_stop"))
        self.assertFalse(hasattr(hook_entry, "_schedule_strategy"))
        source = inspect.getsource(hook_entry)
        self.assertNotIn("--detach-stop", source)
        self.assertNotIn("--strategy-payload-file", source)


class CodexAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.settings = settings_for(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_normal_nudge_additional_context_labels_the_independent_opinion(self):
        output = build_hook_output(
            "PostToolUse",
            "目前省下的工作，是否只是轉移到另一個 pass？",
        )

        self.assertEqual(
            output["hookSpecificOutput"]["additionalContext"],
            "獨立第二意見：\n目前省下的工作，是否只是轉移到另一個 pass？",
        )

    def test_stop_finding_continues_the_same_turn_and_is_reviewed_once(self):
        core = ReviewCore(
            self.settings,
            dispatch=lambda *_args, **_kwargs: {
                "status": "finding",
                "finding": "哪個完成條件仍缺少直接證據？",
                "usage": {},
            },
        )
        adapter = CodexAdapter(core)
        payload = {
            "hook_event_name": "Stop",
            "session_id": "sync-stop",
            "turn_id": "turn-1",
            "cwd": str(self.root),
            "last_assistant_message": "已完成。",
            "stop_hook_active": False,
        }
        storage.start_turn(
            self.settings.paths.data_dir,
            SessionRef("codex_cli", "sync-stop", "turn-1", str(self.root)),
            "完成可靠性修正",
        )

        first = adapter.process(payload)
        hook_entry._emit_output(first, self.settings, io.StringIO())
        second = adapter.process(
            {
                **payload,
                "last_assistant_message": "我會補上完成證據。",
                "stop_hook_active": True,
            }
        )

        self.assertEqual(
            {
                "decision": "block",
                "reason": "獨立第二意見：\n哪個完成條件仍缺少直接證據？",
            },
            {key: first[key] for key in ("decision", "reason")},
        )
        self.assertIsNone(second)
        attempts = storage.read_review_attempts(
            self.settings.paths.data_dir,
            SessionRef("codex_cli", "sync-stop", "turn-1", str(self.root)),
        )
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0]["status"], "finding")
        receipt = next(
            iter(
                storage.load_delivery_state(
                    self.settings.paths.data_dir,
                    SessionRef(
                        "codex_cli", "sync-stop", "turn-1", str(self.root)
                    ),
                )["receipts"].values()
            )
        )
        self.assertEqual(receipt["status"], "injected")

    def test_normalizes_documented_prompt_and_tool_fields(self):
        prompt = normalize_event(
            {
                "hook_event_name": "UserPromptSubmit",
                "session_id": "s",
                "turn_id": "t",
                "cwd": str(self.root),
                "prompt": "修正流程",
            }
        )
        self.assertIsInstance(prompt, PromptSubmitted)
        self.assertEqual(prompt.session.turn_id, "t")
        tool = normalize_event(
            {
                "hook_event_name": "PostToolUse",
                "session_id": "s",
                "tool_name": "shell_command",
                "tool_input": {"command": "pytest"},
                "tool_response": {"exit_code": 1, "output": "1 failed"},
            }
        )
        self.assertIsInstance(tool, ToolCompleted)
        self.assertTrue(tool.failure_known)
        self.assertTrue(tool.failed)

        failure = normalize_event(
            {
                "hook_event_name": "PostToolUseFailure",
                "session_id": "s",
                "tool_name": "Bash",
                "tool_input": {"command": "pytest"},
                "error": "1 failed",
            }
        )
        self.assertIsInstance(failure, ToolCompleted)
        self.assertTrue(failure.failed)

    def test_active_goal_context_populates_turn_anchor_and_progress_objective(self):
        transcript = self.root / "rollout.jsonl"
        transcript.write_text(
            json.dumps(
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    '<codex_internal_context source="goal">\n'
                                    "<objective>\n改善登入流程的可靠性。\n</objective>\n"
                                    "</codex_internal_context>"
                                ),
                            }
                        ],
                    },
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        core = FakeCore(self.settings, ReviewOutcome("no_finding"))
        adapter = CodexAdapter(core)  # type: ignore[arg-type]

        with mock.patch.dict(os.environ, {}, clear=True):
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "goal-session",
                    "turn_id": "goal-turn",
                    "cwd": str(self.root),
                    "prompt": "",
                    "transcript_path": str(transcript),
                }
            )
            adapter.process(
                {
                    "hook_event_name": "PostToolUse",
                    "session_id": "goal-session",
                    "turn_id": "goal-turn",
                    "cwd": str(self.root),
                    "tool_name": "Read",
                    "tool_input": {"file_path": "auth_service.py"},
                    "tool_response": {"content": "authentication service"},
                }
            )

        session = SessionRef(
            "codex_cli", "goal-session", "goal-turn", str(self.root)
        )
        self.assertEqual(
            storage.load_turn_state(self.settings.paths.data_dir, session)[
                "task_anchor"
            ],
            "改善登入流程的可靠性。",
        )
        self.assertEqual(
            json.loads(
                storage.state_path(
                    self.settings.paths.data_dir, session, "progress"
                ).read_text(encoding="utf-8")
            )["goal_objective"],
            "改善登入流程的可靠性。",
        )

    def test_first_tool_recovers_active_goal_when_prompt_hook_did_not_fire(self):
        transcript = self.root / "rollout-with-goal.jsonl"
        transcript.write_text(
            json.dumps(
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    '<codex_internal_context source="goal">\n'
                                    "<objective>\n改善登入流程的可靠性。\n</objective>\n"
                                    "</codex_internal_context>"
                                ),
                            }
                        ],
                    },
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        adapter = CodexAdapter(
            FakeCore(self.settings, ReviewOutcome("no_finding"))
        )

        with mock.patch.dict(os.environ, {}, clear=True):
            adapter.process(
                {
                    "hook_event_name": "PostToolUse",
                    "session_id": "goal-session-without-prompt",
                    "turn_id": "goal-turn",
                    "cwd": str(self.root),
                    "transcript_path": str(transcript),
                    "tool_name": "Read",
                    "tool_input": {"file_path": "auth_service.py"},
                    "tool_response": {"content": "authentication service"},
                }
            )

        session = SessionRef(
            "codex_cli", "goal-session-without-prompt", "goal-turn", str(self.root)
        )
        turn = storage.load_turn_state(self.settings.paths.data_dir, session)
        progress = json.loads(
            storage.state_path(
                self.settings.paths.data_dir, session, "progress"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(turn["task_anchor"], "改善登入流程的可靠性。")
        self.assertGreater(turn["transcript_offset"], 0)
        self.assertEqual(progress["goal_objective"], "改善登入流程的可靠性。")

    def test_stop_review_uses_layered_evidence_not_transcript_contents(self):
        core = FakeCore(self.settings, ReviewOutcome("no_finding"))
        adapter = CodexAdapter(core)  # type: ignore[arg-type]
        with mock.patch.dict(os.environ, {}, clear=True):
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "s",
                    "turn_id": "t",
                    "cwd": str(self.root),
                    "prompt": "讀取 `ISSUE.md`，只修登入流程",
                    "transcript_path": str(self.root / "does-not-exist.jsonl"),
                }
            )
            adapter.process(
                {
                    "hook_event_name": "PostToolUse",
                    "session_id": "s",
                    "turn_id": "t",
                    "cwd": str(self.root),
                    "tool_name": "Read",
                    "tool_input": {"file_path": "ISSUE.md"},
                    "tool_response": {"content": "逾時時必須保留 token check"},
                }
            )
            adapter.process(
                {
                    "hook_event_name": "PostToolUseFailure",
                    "session_id": "s",
                    "turn_id": "t",
                    "cwd": str(self.root),
                    "tool_name": "exec_command",
                    "tool_input": {"cmd": "pytest -q"},
                    "error": {"exit_code": 1, "output": "1 failed"},
                }
            )
            output = adapter.process(
                {
                    "hook_event_name": "Stop",
                    "session_id": "s",
                    "turn_id": "t",
                    "cwd": str(self.root),
                    "transcript_path": str(self.root / "does-not-exist.jsonl"),
                    "last_assistant_message": "已完成登入修正",
                }
            )
        self.assertIsNone(output)
        request, persist, _timeout = core.calls[-1]
        self.assertTrue(persist)
        self.assertIn("token check", request.source_packet)
        self.assertIn("referenced_sources:", request.source_packet)
        self.assertIn("active_failures:", request.source_packet)
        self.assertIn("已完成登入修正", request.source_packet)
        self.assertNotIn("does-not-exist", request.source_packet)

    def test_failed_test_checkpoint_returns_immediate_additional_context(self):
        core = FakeCore(
            self.settings,
            ReviewOutcome(
                "finding",
                "失敗已證明目前步驟的前提不成立。",
                "beck",
                reaction_ts="checkpoint-reaction",
            ),
        )
        adapter = CodexAdapter(core)  # type: ignore[arg-type]
        with mock.patch.dict(os.environ, {}, clear=True):
            output = adapter.process(
                {
                    "hook_event_name": "PostToolUse",
                    "session_id": "s",
                    "turn_id": "t",
                    "cwd": str(self.root),
                    "tool_name": "shell_command",
                    "tool_input": {"command": "pytest"},
                    "tool_response": {"exit_code": 1, "output": "1 failed"},
                }
            )
        self.assertEqual(
            output["hookSpecificOutput"]["hookEventName"], "PostToolUse"
        )
        self.assertIn("失敗已證明", output["hookSpecificOutput"]["additionalContext"])
        request, persist, timeout = core.calls[0]
        self.assertEqual(request.reason, "test-fail")
        self.assertIn("review_event:", request.source_packet)
        self.assertIn("active_failures:", request.source_packet)
        self.assertIn("1 failed", request.source_packet)
        self.assertTrue(persist)
        self.assertEqual(timeout, 15)

    def test_checkpoint_packet_includes_accumulated_research_state(self):
        core = FakeCore(self.settings, ReviewOutcome("no_finding"))
        adapter = CodexAdapter(core)  # type: ignore[arg-type]
        with mock.patch.dict(os.environ, {}, clear=True):
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "research-state",
                    "turn_id": "t",
                    "cwd": str(self.root),
                    "prompt": "讀取 `auth.py`，讓登入流程通過完整驗收",
                }
            )
            adapter.process(
                {
                    "hook_event_name": "PostToolUse",
                    "session_id": "research-state",
                    "turn_id": "t",
                    "cwd": str(self.root),
                    "tool_name": "Read",
                    "tool_input": {"file_path": "auth.py"},
                    "tool_response": {"content": "token check"},
                }
            )
            adapter.process(
                {
                    "hook_event_name": "PostToolUse",
                    "session_id": "research-state",
                    "turn_id": "t",
                    "cwd": str(self.root),
                    "tool_name": "shell_command",
                    "tool_input": {"command": "pytest"},
                    "tool_response": {"exit_code": 1, "output": "1 failed"},
                }
            )

        request, _persist, _timeout = core.calls[-1]
        self.assertIn("review_event:", request.source_packet)
        self.assertIn("referenced_sources:", request.source_packet)
        self.assertIn("token check", request.source_packet)
        self.assertIn("active_failures:", request.source_packet)
        self.assertIn("1 failed", request.source_packet)
        self.assertIn("讓登入流程通過完整驗收", request.source_packet)

    def test_checkpoint_is_marked_delivered_only_after_stdout_succeeds(self):
        core = ReviewCore(
            self.settings,
            dispatch=lambda *_args, **_kwargs: {
                "status": "finding",
                "finding": "B_N² 的界尚未閉合。",
                "usage": {},
            },
        )
        adapter = CodexAdapter(core)
        payload = {
            "hook_event_name": "PostToolUse",
            "session_id": "s",
            "turn_id": "t",
            "cwd": str(self.root),
            "tool_name": "shell_command",
            "tool_input": {"command": "pytest"},
            "tool_response": {"exit_code": 1, "output": "1 failed"},
        }
        with mock.patch.dict(os.environ, {}, clear=True):
            output = adapter.process(payload)
        session = SessionRef("codex_cli", "s", "t", str(self.root))
        self.assertEqual(
            {}, storage.load_delivery_state(self.settings.paths.data_dir, session)["receipts"]
        )
        hook_entry._emit_output(output, self.settings, io.StringIO())
        delivery = storage.load_delivery_state(self.settings.paths.data_dir, session)
        self.assertEqual("emitted", next(iter(delivery["receipts"].values()))["status"])
        followup_payload = dict(payload)
        followup_payload.update(
            {
                "tool_name": "Read",
                "tool_input": {"file_path": "benchmark/result.json"},
                "tool_response": {"content": "{}"},
            }
        )
        with mock.patch.dict(os.environ, {}, clear=True):
            adapter.process(followup_payload)
        delivery = storage.load_delivery_state(self.settings.paths.data_dir, session)
        receipt = next(iter(delivery["receipts"].values()))
        self.assertEqual(receipt["response_observation"]["kind"], "tool")
        self.assertEqual(
            receipt["response_observation"]["observation"]["tool"], "Read"
        )

    def test_queued_finding_is_not_delivered_on_later_prompt(self):
        session = SessionRef("codex_cli", "s", "old-turn", str(self.root))
        storage.append_reaction(
            self.settings.paths.data_dir,
            session,
            provider="openai",
            model="m",
            reaction="先確認交付證據是否真的覆蓋聲稱範圍。",
            route_metadata={"effective_lens": "fowler"},
        )
        core = FakeCore(self.settings, ReviewOutcome("no_finding"))
        adapter = CodexAdapter(core)  # type: ignore[arg-type]
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "s",
            "turn_id": "new-turn",
            "cwd": str(self.root),
            "prompt": "下一步",
        }
        with mock.patch.dict(os.environ, {}, clear=True):
            first = adapter.process(payload)
            second = adapter.process(payload)
        self.assertIsNone(first)
        self.assertIsNone(second)

    def test_later_tool_does_not_claim_an_unemitted_finding(self):
        session = SessionRef("codex_cli", "s", "old-turn", str(self.root))
        storage.append_reaction(
            self.settings.paths.data_dir,
            session,
            provider="anthropic",
            model="opus",
            reaction="同一則提醒只能注入一次。",
            route_metadata={"effective_lens": "linus"},
        )
        adapter = CodexAdapter(FakeCore(self.settings, ReviewOutcome("no_finding")))
        payload = {
            "hook_event_name": "PostToolUse",
            "session_id": "s",
            "turn_id": "new-turn",
            "cwd": str(self.root),
            "tool_name": "Read",
            "tool_input": {"file_path": "benchmark/result.json"},
            "tool_response": {"content": "{}"},
        }

        with mock.patch.dict(os.environ, {}, clear=True):
            first = adapter.process(payload)
            duplicate = adapter.process(payload)

        self.assertIsNone(first)
        self.assertIsNone(duplicate)
        receipts = [
            json.loads(line)
            for line in storage.reaction_log_path(
                self.settings.paths.data_dir, session
            ).read_text(encoding="utf-8").splitlines()
            if json.loads(line).get("kind") == "delivery_receipt"
        ]
        self.assertEqual(len(receipts), 0)

    def test_failed_hook_stdout_is_terminal_and_not_retried_later(self):
        class BrokenStream:
            def write(self, _text):
                raise OSError("closed pipe")

            def flush(self):
                pass

        session = SessionRef("codex_cli", "retry", "new-turn", str(self.root))
        core = ReviewCore(
            self.settings,
            dispatch=lambda *_args, **_kwargs: {
                "status": "finding",
                "finding": "輸出失敗後不可跨事件重送。",
                "usage": {},
            },
        )
        adapter = CodexAdapter(core)
        payload = {
            "hook_event_name": "PostToolUse",
            "session_id": "retry",
            "turn_id": "new-turn",
            "cwd": str(self.root),
            "tool_name": "shell_command",
            "tool_input": {"command": "pytest"},
            "tool_response": {"exit_code": 1, "output": "1 failed"},
        }

        with mock.patch.dict(os.environ, {}, clear=True):
            first = adapter.process(payload)
            with self.assertRaises(OSError):
                hook_entry._emit_output(first, self.settings, BrokenStream())
            later = adapter.process({
                **payload,
                "tool_name": "Read",
                "tool_input": {"file_path": "result.json"},
                "tool_response": {"content": "{}"},
            })

        self.assertIsNone(later)
        receipt = storage.load_delivery_state(
            self.settings.paths.data_dir, session
        )["receipts"][first["_masters_nudge_delivery"]["timestamp"]]
        self.assertEqual("failed", receipt["status"])

    def test_queued_finding_is_not_delivered_on_later_tool(self):
        session = SessionRef("codex_cli", "s", "old-turn", str(self.root))
        storage.append_reaction(
            self.settings.paths.data_dir,
            session,
            provider="anthropic",
            model="m",
            reaction="先檢查均方估計是否偷渡逐點控制。",
            route_metadata={"effective_lens": "lamport"},
            reason="stop",
        )
        adapter = CodexAdapter(
            FakeCore(self.settings, ReviewOutcome("no_finding"))
        )
        payload = {
            "hook_event_name": "PostToolUse",
            "session_id": "s",
            "turn_id": "next-turn",
            "cwd": str(self.root),
            "tool_name": "Read",
            "tool_input": {"file_path": "proof.md"},
            "tool_response": {"content": "draft"},
        }
        with mock.patch.dict(os.environ, {}, clear=True):
            output = adapter.process(payload)
        self.assertIsNone(output)

    def test_recursion_guard_is_fail_open(self):
        core = FakeCore(self.settings, ReviewOutcome("finding", "不應執行"))
        adapter = CodexAdapter(core)  # type: ignore[arg-type]
        with mock.patch.dict(os.environ, {"MASTERS_NUDGE_ACTIVE": "1"}, clear=True):
            output = adapter.process(
                {"hook_event_name": "Stop", "session_id": "s"}
            )
        self.assertIsNone(output)
        self.assertEqual(core.calls, [])


class HookOutputTests(unittest.TestCase):
    def test_cp950_stream_can_emit_unicode_nudge_as_ascii_safe_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = settings_for(Path(tmpdir))
            session = SessionRef("codex_cli", "s")
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": "B_N² 與 κ₃ 都要保留。",
                },
                "_masters_nudge_delivery": {
                    "session": session,
                    "timestamp": "2026-08-14T09:00:00",
                    "event_seq": 0,
                    "event_name": "PostToolUse",
                },
            }
            raw = io.BytesIO()
            stream = io.TextIOWrapper(raw, encoding="cp950", newline="")
            hook_entry._emit_output(output, settings, stream)
            stream.flush()
            payload = json.loads(raw.getvalue().decode("ascii"))
            self.assertIn(
                "B_N²", payload["hookSpecificOutput"]["additionalContext"]
            )
            receipt = storage.load_delivery_state(
                settings.paths.data_dir, session
            )["receipts"]["2026-08-14T09:00:00"]
            self.assertEqual("emitted", receipt["status"])

    def test_failed_stdout_does_not_mark_pending_finding_delivered(self):
        class BrokenStream:
            def write(self, _text):
                raise OSError("closed pipe")

            def flush(self):
                pass

        with tempfile.TemporaryDirectory() as tmpdir:
            settings = settings_for(Path(tmpdir))
            session = SessionRef("codex_cli", "s")
            output = {
                "hookSpecificOutput": {"hookEventName": "PostToolUse"},
                "_masters_nudge_delivery": {
                    "session": session,
                    "timestamp": "2026-08-14T09:00:00",
                    "event_seq": 0,
                    "event_name": "PostToolUse",
                },
            }
            with self.assertRaises(OSError):
                hook_entry._emit_output(output, settings, BrokenStream())
            receipt = storage.load_delivery_state(
                settings.paths.data_dir, session
            )["receipts"]["2026-08-14T09:00:00"]
            self.assertEqual("failed", receipt["status"])

    def test_tuple_delivery_marker_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = settings_for(Path(tmpdir))
            session = SessionRef("codex_cli", "s")
            output = {
                "hookSpecificOutput": {"hookEventName": "PostToolUse"},
                "_masters_nudge_delivery": (
                    session,
                    "2026-08-14T09:00:00",
                ),
            }

            hook_entry._emit_output(output, settings, io.StringIO())

            self.assertEqual(
                storage.load_delivery_state(
                    settings.paths.data_dir, session
                )["receipts"],
                {},
            )


class SharedCoreTests(unittest.TestCase):
    def test_every_timeout_subtype_is_visible_and_keeps_stop_scope(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            base = settings_for(root)
            settings = RuntimeSettings(
                base.provider,
                base.model,
                120,
                90,
                base.paths,
            )
            calls = []

            session = SessionRef("codex_cli", "timeout", cwd=str(root))
            telemetry = []
            for error_kind in (
                "timeout",
                "timeout_before_output",
                "timeout_after_partial_output",
            ):
                def dispatch(*_args, _error_kind=error_kind, **kwargs):
                    calls.append(kwargs)
                    return {
                        "status": "error",
                        "finding": "",
                        "usage": {},
                        "error_kind": _error_kind,
                    }

                with mock.patch(
                    "masters_nudge.core.review_telemetry.record_review",
                    side_effect=lambda _data_dir, record: telemetry.append(record),
                ):
                    ReviewCore(settings, dispatch=dispatch).review(
                        ReviewRequest(
                            schema_version=1,
                            kind="stop",
                            reason="stop",
                            session=session,
                            source_packet="已完成",
                            source_fingerprint=error_kind,
                        ),
                        persist_reaction=True,
                    )
            entries = storage.read_reaction_entries(
                settings.paths.data_dir, session
            )

        self.assertEqual([call["timeout_sec"] for call in calls], [90, 90, 90])
        self.assertTrue(all(entry["kind"] == "review_status" for entry in entries))
        self.assertTrue(all(
            entry["reaction"] == "Reviewer 逾時（90 秒）；本輪沒有 Nudge。"
            for entry in entries
        ))
        self.assertTrue(all(entry["finding_scope"] == "trajectory" for entry in entries))
        self.assertTrue(all(record["finding_scope"] == "trajectory" for record in telemetry))

    def test_stop_is_primary_and_checkpoint_routing_uses_only_new_event(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = settings_for(root)
            persona_config.save_stage(settings.paths.data_dir, "build")
            prompts: list[str] = []

            def dispatch(_provider, system_prompt, _review_input, _model, **_kwargs):
                prompts.append(system_prompt)
                return {"status": "no_finding", "finding": "", "usage": {}}

            core = ReviewCore(settings, dispatch=dispatch)
            session = SessionRef("codex_cli", "routing")
            core.review(
                ReviewRequest(
                    schema_version=1,
                    kind="stop",
                    reason="stop",
                    session=session,
                    source_packet="retry caused duplicate delivery",
                    source_fingerprint="stop",
                ),
                persist_reaction=False,
            )
            core.review(
                ReviewRequest(
                    schema_version=1,
                    kind="checkpoint",
                    reason="tool",
                    session=session,
                    source_packet="retry caused duplicate delivery\nordinary file edit",
                    source_fingerprint="quiet",
                    routing_evidence="ordinary file edit",
                ),
                persist_reaction=False,
            )
            core.review(
                ReviewRequest(
                    schema_version=1,
                    kind="checkpoint",
                    reason="tool",
                    session=session,
                    source_packet="retry caused duplicate delivery",
                    source_fingerprint="new-event",
                    routing_evidence="retry caused duplicate delivery",
                ),
                persist_reaction=False,
            )
            core.review(
                ReviewRequest(
                    schema_version=1,
                    kind="strategy",
                    reason="strategy-review",
                    session=session,
                    source_packet="ordinary workflow",
                    source_fingerprint="structured-route",
                    routing_evidence="ordinary workflow",
                    trigger="diff-growth",
                    routing_concern="knowledge-boundary",
                ),
                persist_reaction=False,
            )
            core.review(
                ReviewRequest(
                    schema_version=1,
                    kind="strategy",
                    reason="strategy-review",
                    session=session,
                    source_packet="ordinary workflow",
                    source_fingerprint="machine-text-only",
                    routing_evidence="ordinary workflow",
                    trigger="diff-growth",
                ),
                persist_reaction=False,
            )

            self.assertIn("# COMPLETION BOUNDARY", prompts[0])
            self.assertIn("Linus Torvalds", prompts[0])
            self.assertIn("Kent Beck", prompts[1])
            self.assertIn("Leslie Lamport", prompts[2])
            self.assertIn("Martin Fowler", prompts[3])
            self.assertIn("Kent Beck", prompts[4])

    def test_checkpoint_reaction_is_visible_but_not_redelivered_next_turn(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = settings_for(root)
            session = SessionRef("codex_cli", "s", "t", str(root))
            request = ReviewRequest(
                schema_version=1,
                kind="checkpoint",
                reason="test-fail",
                session=session,
                source_packet="pytest: 1 failed",
                source_fingerprint="failure-1",
                routing_evidence="pytest: 1 failed",
            )
            core = ReviewCore(
                settings,
                dispatch=lambda *_args, **_kwargs: {
                    "status": "finding",
                    "finding": "先確認失敗是否推翻目前使用的前提。",
                    "usage": {},
                },
            )

            core.review(
                request,
                persist_reaction=True,
            )

            reaction_ts = storage.read_reaction_entries(
                settings.paths.data_dir, session
            )[-1]["ts"]
            storage.mark_emitted(settings.paths.data_dir, session, reaction_ts)

            entries = storage.read_reaction_entries(
                settings.paths.data_dir, session
            )
            self.assertEqual(entries[-1]["reaction"], "先確認失敗是否推翻目前使用的前提。")
            self.assertEqual(
                "emitted",
                storage.load_delivery_state(settings.paths.data_dir, session)[
                    "receipts"
                ][reaction_ts]["status"],
            )

    def test_review_core_has_no_host_compatibility_callback_slots(self):
        parameters = inspect.signature(ReviewCore).parameters
        self.assertNotIn("prompt_builder", parameters)
        self.assertNotIn("telemetry_recorder", parameters)

    def test_both_hosts_feed_the_same_prompt_and_provider_boundary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = settings_for(Path(tmpdir))
            calls = []

            def dispatch(provider, system_prompt, review_input, model, **kwargs):
                calls.append((provider, system_prompt, review_input, model, kwargs))
                return {"status": "no_finding", "finding": "", "usage": {}}

            core = ReviewCore(settings, dispatch=dispatch)
            for host in ("claude_code", "codex_cli"):
                core.review(
                    ReviewRequest(
                        schema_version=1,
                        kind="stop",
                        reason="stop",
                        session=SessionRef(host, f"{host}-session"),  # type: ignore[arg-type]
                        source_packet="[task anchor]\n同一任務\n[end task anchor]",
                        source_fingerprint="same",
                    ),
                    persist_reaction=False,
                )
            self.assertEqual(calls[0][1], calls[1][1])
            self.assertEqual(calls[0][2], calls[1][2])
            self.assertEqual(calls[0][0:1] + calls[0][3:4], ("openai", "test-model"))
            self.assertEqual(calls[0][4]["ollama_url"], settings.ollama_url)

    def test_telemetry_keeps_host_and_turn_without_review_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            review_telemetry.record_review(
                root,
                {
                    "schema_version": 1,
                    "host": "codex_cli",
                    "session_id": "s",
                    "turn_id": "t",
                    "kind": "stop",
                    "reason": "stop",
                    "status": "no_finding",
                    "input_chars": 123,
                    "latency_ms": 4,
                    "source_packet": "must not be stored",
                    "usage": {},
                },
            )
            record = json.loads(
                (root / review_telemetry.TELEMETRY_FILE).read_text(encoding="utf-8")
            )
            self.assertEqual((record["host"], record["turn_id"]), ("codex_cli", "t"))
        self.assertNotIn("source_packet", record)


class GrokProviderTests(unittest.TestCase):
    def test_windows_cleanup_targets_the_exact_process_tree(self):
        process = mock.Mock(pid=4321)
        process.poll.return_value = None
        process.communicate.return_value = ("", "")
        completed = mock.Mock(returncode=0, stdout="", stderr="")

        with (
            mock.patch.object(providers.os, "name", "nt"),
            mock.patch(
                "masters_nudge.providers.subprocess.run",
                return_value=completed,
            ) as run,
        ):
            providers._terminate_process_tree(process)

        self.assertEqual(
            run.call_args.args[0],
            ["taskkill.exe", "/PID", "4321", "/T", "/F"],
        )
        process.communicate.assert_called_once_with(timeout=5)

    def test_grok_timeout_terminates_the_started_process_tree(self):
        process = mock.Mock(pid=4321)
        process.communicate.side_effect = subprocess.TimeoutExpired(
            cmd=["grok"], timeout=12
        )
        errors = []

        with (
            mock.patch(
                "masters_nudge.providers.subprocess.Popen",
                return_value=process,
            ),
            mock.patch(
                "masters_nudge.providers._terminate_process_tree"
            ) as terminate,
        ):
            result = providers.call_grok_result(
                "system",
                "evidence",
                "grok-4.6",
                schema_path=HERE / "reaction-schema.json",
                timeout_sec=12,
                grok_bin_resolver=lambda: "grok",
                log_error=errors.append,
            )

        self.assertEqual(result["error_kind"], "timeout")
        terminate.assert_called_once_with(process, log_error=errors.append)

    def test_grok_accepts_valid_schema_output_when_cli_hits_max_turns(self):
        payload = json.dumps(
            {
                "text": json.dumps(
                    {
                        "status": "finding",
                        "finding": "先固定 GPU baseline 再比較。",
                    },
                    ensure_ascii=False,
                ),
                "stopReason": "cancelled",
                "structuredOutput": None,
                "structuredOutputError": "model did not produce structured output",
                "usage": {"input_tokens": 10, "output_tokens": 3},
            },
            ensure_ascii=False,
        )
        completed = mock.Mock(
            returncode=1,
            stdout=payload,
            stderr="Error: max turns reached",
        )
        with mock.patch(
            "masters_nudge.providers._run_grok_process", return_value=completed
        ):
            result = providers.call_grok_result(
                "system",
                "evidence",
                "",
                schema_path=HERE / "reaction-schema.json",
                timeout_sec=12,
                grok_bin_resolver=lambda: "grok",
            )

        self.assertEqual(result["status"], "finding")
        self.assertEqual(result["finding"], "先固定 GPU baseline 再比較。")
        self.assertEqual(result["usage"]["input_tokens"], 10)

    def test_grok_runs_one_tool_free_schema_constrained_turn(self):
        payload = json.dumps(
            {"result": {"status": "finding", "finding": "先確認停止條件。"}},
            ensure_ascii=False,
            indent=2,
        )
        completed = mock.Mock(returncode=0, stdout=payload, stderr="")
        observed = {}

        def fake_run(command, **kwargs):
            observed["command"] = command
            observed["kwargs"] = kwargs
            reviewer_cwd = Path(kwargs["cwd"])
            self.assertTrue(reviewer_cwd.is_dir())
            self.assertEqual(list(reviewer_cwd.iterdir()), [])
            return completed

        with tempfile.TemporaryDirectory() as raw, mock.patch(
            "masters_nudge.providers._run_grok_process", side_effect=fake_run
        ):
            schema = Path(raw) / "schema.json"
            schema.write_text(
                (HERE / "reaction-schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            result = providers.call_grok_result(
                "system",
                "evidence",
                "grok-test",
                schema_path=schema,
                timeout_sec=12,
                grok_bin_resolver=lambda: "grok",
            )
        self.assertEqual(result["finding"], "先確認停止條件。")
        command = observed["command"]
        self.assertIn("--disable-web-search", command)
        self.assertNotIn("--tools", command)
        denied = set(command[command.index("--disallowed-tools") + 1].split(","))
        self.assertEqual(
            denied,
            {
                "run_terminal_cmd",
                "grep",
                "read_file",
                "search_replace",
                "list_dir",
                "web_search",
                "web_fetch",
                "todo_write",
                "task",
                "Agent",
            },
        )
        self.assertIn("--cwd", command)
        self.assertEqual(command[command.index("--cwd") + 1], observed["kwargs"]["cwd"])
        self.assertIn("--no-memory", command)
        self.assertIn("--no-subagents", command)
        self.assertEqual(command[command.index("--max-turns") + 1], "1")
        self.assertEqual(command[command.index("--model") + 1], "grok-test")

    def test_grok_uses_cli_default_model_when_model_is_empty(self):
        completed = mock.Mock(
            returncode=0,
            stdout=json.dumps({"status": "no_finding", "finding": ""}),
            stderr="",
        )
        with mock.patch(
            "masters_nudge.providers._run_grok_process", return_value=completed
        ) as run:
            providers.call_grok_result(
                "system",
                "evidence",
                "",
                schema_path=HERE / "reaction-schema.json",
                timeout_sec=12,
                grok_bin_resolver=lambda: "grok",
            )
        self.assertNotIn("--model", run.call_args.args[0])

    def test_grok_passes_explicit_reasoning_effort(self):
        completed = mock.Mock(
            returncode=0,
            stdout=json.dumps({"status": "no_finding", "finding": ""}),
            stderr="",
        )
        with mock.patch(
            "masters_nudge.providers._run_grok_process", return_value=completed
        ) as run:
            providers.call_grok_result(
                "system",
                "evidence",
                "grok-4.6",
                schema_path=HERE / "reaction-schema.json",
                timeout_sec=12,
                reasoning_effort="medium",
                grok_bin_resolver=lambda: "grok",
            )

        command = run.call_args.args[0]
        self.assertEqual(
            command[command.index("--reasoning-effort") + 1],
            "medium",
        )

    def test_provider_dispatch_forwards_reasoning_effort_to_grok(self):
        with mock.patch(
            "masters_nudge.providers.call_grok_result",
            return_value={"status": "no_finding", "finding": "", "usage": {}},
        ) as call:
            providers.dispatch_call_result(
                "grok",
                "system",
                "evidence",
                "",
                schema_path=HERE / "reaction-schema.json",
                timeout_sec=12,
                reasoning_effort="medium",
            )

        self.assertEqual(call.call_args.kwargs["reasoning_effort"], "medium")

    def test_grok_subscription_call_does_not_inherit_xai_api_key(self):
        completed = mock.Mock(
            returncode=0,
            stdout=json.dumps({"status": "no_finding", "finding": ""}),
            stderr="",
        )
        with mock.patch.dict(os.environ, {"XAI_API_KEY": "must-not-be-used"}), mock.patch(
            "masters_nudge.providers._run_grok_process", return_value=completed
        ) as run:
            providers.call_grok_result(
                "system",
                "evidence",
                "",
                schema_path=HERE / "reaction-schema.json",
                timeout_sec=12,
                grok_bin_resolver=lambda: "grok",
            )

        child_environment = run.call_args.kwargs["environment"]
        self.assertNotIn("XAI_API_KEY", child_environment)
        self.assertEqual(child_environment["MASTERS_NUDGE_ACTIVE"], "1")
        for vendor in ("CLAUDE", "CURSOR"):
            for source in ("SKILLS", "RULES", "AGENTS", "MCPS", "HOOKS", "SESSIONS"):
                self.assertEqual(
                    child_environment[f"GROK_{vendor}_{source}_ENABLED"], "false"
                )

    def test_grok_parses_real_cli_camel_case_envelope_and_usage(self):
        raw = json.dumps(
            {
                "text": json.dumps(
                    {"status": "finding", "finding": "先重現原始失敗。"},
                    ensure_ascii=False,
                ),
                "structuredOutput": {
                    "status": "finding",
                    "finding": "先重現原始失敗。",
                },
                "usage": {
                    "input_tokens": 10,
                    "cache_read_input_tokens": 2,
                    "output_tokens": 3,
                    "reasoning_tokens": 1,
                    "total_tokens": 13,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        result = providers.parse_grok_reaction_result(raw)
        usage = providers.parse_usage(raw)
        self.assertEqual(result["finding"], "先重現原始失敗。")
        self.assertEqual(usage["cached_input_tokens"], 2)
        self.assertEqual(usage["reasoning_output_tokens"], 1)

if __name__ == "__main__":
    unittest.main()
