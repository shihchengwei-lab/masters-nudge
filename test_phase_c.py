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
    EvidenceBundle,
    PromptSubmitted,
    ReviewOutcome,
    ReviewRequest,
    SessionRef,
    ToolCompleted,
)
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


HERE = Path(__file__).resolve().parent


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
        mark_delivered: bool = False,
        timeout_sec: int | None = None,
    ) -> ReviewOutcome:
        self.calls.append((request, persist_reaction, timeout_sec))
        return self.outcome


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
                route_metadata={"effective_lens": "general"},
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
                "last_assistant_message": "已完成指定流程",
            }
            with (
                mock.patch.object(buddy, "_RUNTIME", settings),
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
            ):
                buddy.main()
            self.assertTrue(
                (root / "data" / "claude_code--claude-session.log").exists()
            )
            self.assertFalse((root / "data" / "claude-session.log").exists())


class DetachedStopTests(unittest.TestCase):
    def test_detached_stop_spools_payload_and_starts_worker(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = settings_for(Path(tmpdir))
            with mock.patch.object(hook_entry.subprocess, "Popen") as popen:
                hook_entry._detach_stop(
                    settings,
                    {"hook_event_name": "Stop", "session_id": "s"},
                    self.fail,
                )
            popen.assert_called_once()
            command = popen.call_args.args[0]
            self.assertIn("--payload-file", command)
            payload_path = Path(command[command.index("--payload-file") + 1])
            self.assertTrue(payload_path.exists())
            self.assertEqual(
                json.loads(payload_path.read_text(encoding="utf-8"))["session_id"],
                "s",
            )

    def test_detached_strategy_uses_the_same_spool_launcher(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            settings = settings_for(Path(tmpdir))
            with mock.patch.object(hook_entry.subprocess, "Popen") as popen:
                launched = hook_entry._schedule_strategy(
                    settings,
                    {"hook_event_name": "PostToolUse", "session_id": "s"},
                    self.fail,
                )

            self.assertTrue(launched)
            popen.assert_called_once()
            command = popen.call_args.args[0]
            self.assertIn("--strategy-payload-file", command)
            payload_path = Path(
                command[command.index("--strategy-payload-file") + 1]
            )
            self.assertEqual(
                json.loads(payload_path.read_text(encoding="utf-8"))["session_id"],
                "s",
            )


class CodexAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.settings = settings_for(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_normal_nudge_additional_context_has_no_visible_wrapper(self):
        output = build_hook_output(
            "PostToolUse",
            "目前省下的工作，是否只是轉移到另一個 pass？",
        )

        self.assertEqual(
            output["hookSpecificOutput"]["additionalContext"],
            "目前省下的工作，是否只是轉移到另一個 pass？",
        )

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
                                    "<objective>\n改善黑洞特效的效能。\n</objective>\n"
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
                    "tool_input": {"file_path": "blackhole-shader.js"},
                    "tool_response": {"content": "shader"},
                }
            )

        session = SessionRef(
            "codex_cli", "goal-session", "goal-turn", str(self.root)
        )
        self.assertEqual(
            storage.load_turn_state(self.settings.paths.data_dir, session)[
                "task_anchor"
            ],
            "改善黑洞特效的效能。",
        )
        self.assertEqual(
            json.loads(
                storage.state_path(
                    self.settings.paths.data_dir, session, "progress"
                ).read_text(encoding="utf-8")
            )["goal_objective"],
            "改善黑洞特效的效能。",
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
                                    "<objective>\n改善黑洞特效的效能。\n</objective>\n"
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
                    "tool_input": {"file_path": "blackhole-shader.js"},
                    "tool_response": {"content": "shader"},
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
        self.assertEqual(turn["task_anchor"], "改善黑洞特效的效能。")
        self.assertGreater(turn["transcript_offset"], 0)
        self.assertEqual(progress["goal_objective"], "改善黑洞特效的效能。")

    def test_stop_review_uses_journal_not_transcript_contents(self):
        core = FakeCore(self.settings, ReviewOutcome("no_finding"))
        adapter = CodexAdapter(core)  # type: ignore[arg-type]
        with mock.patch.dict(os.environ, {}, clear=True):
            adapter.process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "s",
                    "turn_id": "t",
                    "cwd": str(self.root),
                    "prompt": "只修登入流程",
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
                    "tool_input": {"file_path": "auth.py"},
                    "tool_response": {"content": "token check"},
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
        self.assertIn("已完成登入修正", request.source_packet)
        self.assertNotIn("does-not-exist", request.source_packet)

    def test_failed_test_checkpoint_returns_immediate_additional_context(self):
        core = FakeCore(
            self.settings,
            ReviewOutcome("finding", "失敗已證明目前步驟的前提不成立。", "beck"),
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
                    "prompt": "讓登入流程通過完整驗收",
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
        self.assertIn("[current bottleneck model]", request.source_packet)
        self.assertIn("[repeated explanation and workflow evidence]", request.source_packet)
        self.assertIn("[failed or no-change mechanisms]", request.source_packet)
        self.assertIn("token check", request.source_packet)
        self.assertIn("1 failed", request.source_packet)
        self.assertIn("[unresolved contradiction]", request.source_packet)
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
        self.assertIsNotNone(
            storage.latest_pending(self.settings.paths.data_dir, session)
        )
        hook_entry._emit_output(output, self.settings, io.StringIO())
        self.assertIsNone(storage.latest_pending(self.settings.paths.data_dir, session))
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

    def test_stop_finding_is_delivered_once_on_next_prompt(self):
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
            hook_entry._emit_output(first, self.settings, io.StringIO())
            second = adapter.process(payload)
        self.assertEqual(
            first["hookSpecificOutput"]["additionalContext"],
            "先確認交付證據是否真的覆蓋聲稱範圍。",
        )
        self.assertIsNone(second)

    def test_duplicate_hook_dispatch_claims_pending_finding_once_before_stdout(self):
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

        self.assertIsNotNone(first)
        self.assertIsNone(duplicate)
        hook_entry._emit_output(first, self.settings, io.StringIO())
        receipts = [
            json.loads(line)
            for line in storage.reaction_log_path(
                self.settings.paths.data_dir, session
            ).read_text(encoding="utf-8").splitlines()
            if json.loads(line).get("kind") == "delivery_receipt"
        ]
        self.assertEqual(len(receipts), 1)

    def test_failed_hook_stdout_releases_delivery_claim_for_retry(self):
        class BrokenStream:
            def write(self, _text):
                raise OSError("closed pipe")

            def flush(self):
                pass

        session = SessionRef("codex_cli", "retry", "old-turn", str(self.root))
        storage.append_reaction(
            self.settings.paths.data_dir,
            session,
            provider="anthropic",
            model="opus",
            reaction="輸出失敗後必須能重試。",
            route_metadata={"effective_lens": "linus"},
        )
        adapter = CodexAdapter(FakeCore(self.settings, ReviewOutcome("no_finding")))
        payload = {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "retry",
            "turn_id": "new-turn",
            "cwd": str(self.root),
            "prompt": "繼續",
        }

        with mock.patch.dict(os.environ, {}, clear=True):
            first = adapter.process(payload)
            with self.assertRaises(OSError):
                hook_entry._emit_output(first, self.settings, BrokenStream())
            retry = adapter.process(payload)

        self.assertIsNotNone(retry)

    def test_stop_finding_is_delivered_on_next_tool_without_new_prompt(self):
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
        self.assertEqual(
            output["hookSpecificOutput"]["additionalContext"],
            "先檢查均方估計是否偷渡逐點控制。",
        )
        self.assertIsNotNone(
            storage.latest_pending(self.settings.paths.data_dir, session)
        )
        hook_entry._emit_output(output, self.settings, io.StringIO())
        self.assertIsNone(storage.latest_pending(self.settings.paths.data_dir, session))

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
            self.assertEqual(
                storage.load_delivery_state(
                    settings.paths.data_dir, session
                )["last_ts"],
                "2026-08-14T09:00:00",
            )

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
            self.assertEqual(
                storage.load_delivery_state(
                    settings.paths.data_dir, session
                )["last_ts"],
                "",
            )

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
                )["last_ts"],
                "",
            )


class SharedCoreTests(unittest.TestCase):
    def test_stop_timeout_is_logged_as_visible_non_injectable_status(self):
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

            def dispatch(*_args, **kwargs):
                calls.append(kwargs)
                return {
                    "status": "error",
                    "finding": "",
                    "usage": {},
                    "error_kind": "timeout",
                }

            session = SessionRef("codex_cli", "timeout", cwd=str(root))
            ReviewCore(settings, dispatch=dispatch).review(
                ReviewRequest(
                    1,
                    "stop",
                    "stop",
                    session,
                    EvidenceBundle(assistant_claim="已完成"),
                    "已完成",
                    "timeout",
                ),
                persist_reaction=True,
            )
            entries = storage.read_reaction_entries(
                settings.paths.data_dir, session
            )

        self.assertEqual(calls[0]["timeout_sec"], 120)
        self.assertEqual(entries[-1]["kind"], "review_status")
        self.assertEqual(
            entries[-1]["reaction"],
            "Reviewer 逾時（120 秒）；本輪沒有 Nudge。",
        )
        self.assertEqual(entries[-1]["delivery_status"], "")

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
                    1,
                    "stop",
                    "stop",
                    session,
                    EvidenceBundle(tool_evidence="retry caused duplicate delivery"),
                    "retry caused duplicate delivery",
                    "stop",
                ),
                persist_reaction=False,
            )
            core.review(
                ReviewRequest(
                    1,
                    "checkpoint",
                    "tool",
                    session,
                    EvidenceBundle(
                        task_anchor="retry caused duplicate delivery",
                        checkpoint_event="ordinary file edit",
                    ),
                    "retry caused duplicate delivery\nordinary file edit",
                    "quiet",
                ),
                persist_reaction=False,
            )
            core.review(
                ReviewRequest(
                    1,
                    "checkpoint",
                    "tool",
                    session,
                    EvidenceBundle(checkpoint_event="retry caused duplicate delivery"),
                    "retry caused duplicate delivery",
                    "new-event",
                ),
                persist_reaction=False,
            )

            self.assertIn("Kent Beck", prompts[0])
            self.assertIn("Kent Beck", prompts[1])
            self.assertIn("Leslie Lamport", prompts[2])

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
                evidence=EvidenceBundle(checkpoint_event="pytest: 1 failed"),
                source_packet="pytest: 1 failed",
                source_fingerprint="failure-1",
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
                mark_delivered=True,
            )

            entries = storage.read_reaction_entries(
                settings.paths.data_dir, session
            )
            self.assertEqual(entries[-1]["reaction"], "先確認失敗是否推翻目前使用的前提。")
            self.assertIsNone(storage.latest_pending(settings.paths.data_dir, session))

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
                        1,
                        "stop",
                        "stop",
                        SessionRef(host, f"{host}-session"),  # type: ignore[arg-type]
                        EvidenceBundle(task_anchor="同一任務"),
                        "[task anchor]\n同一任務\n[end task anchor]",
                        "same",
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


class PackagingTests(unittest.TestCase):
    def test_docs_describe_the_actual_host_core_boundary(self):
        architecture = " ".join(
            (HERE / "docs" / "phase-c-architecture.md")
            .read_text(encoding="utf-8")
            .split()
        )

        self.assertIn("Host entry and adapter", architecture)
        self.assertIn("Shared checkpoints and evidence", architecture)
        self.assertIn("ReviewCore", architecture)
        self.assertIn("claude_prompt.py", architecture)
        self.assertIn("claude_checkpoint.py", architecture)
        self.assertIn("claude_stop.py", architecture)
        self.assertIn("One `.turn.json` record", architecture)
        self.assertNotIn("compatibility delegate", architecture.lower())


if __name__ == "__main__":
    unittest.main()
