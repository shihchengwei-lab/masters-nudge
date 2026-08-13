#!/usr/bin/env python3
"""Phase C compatibility and Codex CLI hook contract tests."""

from __future__ import annotations

import inspect
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import review_telemetry
import buddy
import hook_entry
from masters_nudge import prompting, providers, storage
from masters_nudge.codex_adapter import CodexAdapter, normalize_event
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
        RuntimePaths(HERE, root / "data", root / "legacy", root / "error.log"),
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


class RuntimeCompatibilityTests(unittest.TestCase):
    def test_default_paths_are_host_neutral_with_legacy_read_location(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = RuntimePaths.resolve(environ={"USERPROFILE": tmpdir})
            self.assertEqual(paths.data_dir, Path(tmpdir) / ".masters-nudge" / "data")
            self.assertEqual(paths.legacy_data_dir, Path(tmpdir) / ".claude" / "buddy")

    def test_legacy_path_override_preserves_existing_install_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            paths = RuntimePaths.resolve(environ={"BUDDY_CLAUDE_DIR": tmpdir})
            self.assertEqual(paths.data_dir, Path(tmpdir) / "buddy")
            self.assertEqual(paths.error_log, Path(tmpdir) / "buddy-error.log")

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
    def test_same_native_session_id_cannot_collide_between_hosts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            claude = SessionRef("claude_code", "same")
            codex = SessionRef("codex_cli", "same")
            self.assertNotEqual(
                storage.reaction_log_path(root, claude),
                storage.reaction_log_path(root, codex),
            )

    def test_legacy_log_is_read_but_new_reaction_is_namespaced(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            data = root / "data"
            legacy = root / "legacy"
            legacy.mkdir()
            session = SessionRef("claude_code", "s1")
            (legacy / "s1.log").write_text(
                json.dumps({"ts": "2026-01-01", "reaction": "舊提醒"}) + "\n",
                encoding="utf-8",
            )
            storage.append_reaction(
                data,
                session,
                provider="openai",
                model="m",
                reaction="新提醒",
                route_metadata={"effective_lens": "beck"},
            )
            self.assertEqual(
                storage.read_recent_reactions_compatible(data, legacy, session),
                ["舊提醒", "新提醒"],
            )
            self.assertTrue((data / "claude_code--s1.log").exists())
            self.assertFalse((data / "s1.log").exists())

    def test_codex_does_not_import_an_unscoped_legacy_claude_reaction(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            legacy = root / "legacy"
            legacy.mkdir()
            (legacy / "same.log").write_text(
                json.dumps({"ts": "2026-01-01", "reaction": "Claude 舊提醒"}) + "\n",
                encoding="utf-8",
            )
            reactions = storage.read_recent_reactions_compatible(
                root / "data", legacy, SessionRef("codex_cli", "same")
            )
            self.assertEqual(reactions, [])


class ClaudeCompatibilityTests(unittest.TestCase):
    def test_stop_adapter_writes_new_host_namespaced_log(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            hook = {
                "session_id": "claude-session",
                "cwd": str(root),
                "last_assistant_message": "已完成指定流程",
            }
            with (
                mock.patch.object(buddy, "BUDDY_DIR", root / "data"),
                mock.patch.object(buddy, "CLAUDE_DIR", root / ".claude"),
                mock.patch.object(buddy, "ERROR_LOG", root / "error.log"),
                mock.patch.object(buddy, "read_hook_input", return_value=hook),
                mock.patch.object(buddy, "read_latest_agentcam_report", return_value=None),
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


class CodexAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.settings = settings_for(self.root)

    def tearDown(self):
        self.temp.cleanup()

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
        self.assertFalse(persist)
        self.assertEqual(timeout, 15)

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
            second = adapter.process(payload)
        self.assertIn("先確認交付證據", first["hookSpecificOutput"]["additionalContext"])
        self.assertIsNone(second)

    def test_recursion_guard_is_fail_open(self):
        core = FakeCore(self.settings, ReviewOutcome("finding", "不應執行"))
        adapter = CodexAdapter(core)  # type: ignore[arg-type]
        with mock.patch.dict(os.environ, {"MASTERS_NUDGE_ACTIVE": "1"}, clear=True):
            output = adapter.process(
                {"hook_event_name": "Stop", "session_id": "s"}
            )
        self.assertIsNone(output)
        self.assertEqual(core.calls, [])


class SharedCoreTests(unittest.TestCase):
    def test_review_core_has_no_host_compatibility_callback_slots(self):
        parameters = inspect.signature(ReviewCore).parameters
        self.assertNotIn("prompt_builder", parameters)
        self.assertNotIn("telemetry_recorder", parameters)

    def test_legacy_prompt_api_delegates_to_the_shared_contract(self):
        with mock.patch.object(
            prompting, "build_system_prompt", return_value="shared prompt"
        ) as build:
            self.assertEqual(buddy.build_system_prompt(), "shared prompt")

        build.assert_called_once_with(
            prompt_file=buddy.PROMPT_FILE,
            persona_dir=buddy.PERSONA_DIR,
            data_dir=buddy.BUDDY_DIR,
            route=None,
            log_error=buddy.log_error,
        )
        self.assertEqual(buddy.MAX_REACTION_CHARS, prompting.MAX_REACTION_CHARS)

    def test_legacy_output_apis_delegate_to_the_shared_contract(self):
        with mock.patch.object(
            prompting, "sanitize_reaction", return_value="shared finding"
        ) as sanitize:
            self.assertEqual(buddy.sanitize_reaction("raw"), "shared finding")
        sanitize.assert_called_once_with("raw")

        expected = {"status": "no_finding", "finding": ""}
        with mock.patch.object(
            providers, "parse_reaction_result", return_value=expected
        ) as parse:
            self.assertIs(buddy.parse_reaction_result("raw json"), expected)
        parse.assert_called_once_with("raw json")

    def test_legacy_provider_apis_delegate_to_the_shared_clients(self):
        expected = {"status": "no_finding", "finding": "", "usage": {}}
        with mock.patch.object(
            providers, "call_claude_result", return_value=expected
        ) as call_claude:
            self.assertIs(
                buddy.call_claude_result("prompt", "packet", "model"), expected
            )
        call_claude.assert_called_once_with(
            "prompt",
            "packet",
            "model",
            schema_path=buddy.OUTPUT_SCHEMA_FILE,
            timeout_sec=buddy.TIMEOUT_SEC,
            capture_raw=False,
            log_error=buddy.log_error,
        )

        with mock.patch.object(
            providers, "call_codex_result", return_value=expected
        ) as call_codex:
            self.assertIs(
                buddy.call_codex_result("prompt", "packet", "model"), expected
            )
        call_codex.assert_called_once_with(
            "prompt",
            "packet",
            "model",
            schema_path=buddy.OUTPUT_SCHEMA_FILE,
            timeout_sec=buddy.TIMEOUT_SEC,
            capture_raw=False,
            log_error=buddy.log_error,
            codex_bin_resolver=buddy._resolve_codex_bin,
        )

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


class PackagingTests(unittest.TestCase):
    def test_codex_snippet_registers_three_supported_events(self):
        snippet = json.loads((HERE / "codex-hooks-snippet.json").read_text(encoding="utf-8"))
        hooks = snippet["hooks"]
        self.assertEqual(set(hooks), {"UserPromptSubmit", "PostToolUse", "Stop"})
        for event_name in hooks:
            commands = [hook for group in hooks[event_name] for hook in group["hooks"]]
            self.assertTrue(all("commandWindows" in hook for hook in commands))
            self.assertTrue(all("hook_entry.py" in hook["command"] for hook in commands))
        self.assertIn("--detach-stop", hooks["Stop"][0]["hooks"][0]["command"])
        self.assertNotIn("async", hooks["Stop"][0]["hooks"][0])
        self.assertNotIn("async", hooks["PostToolUse"][0]["hooks"][0])

    def test_installers_include_shared_runtime_and_both_host_choices(self):
        shell = (HERE / "install.sh").read_text(encoding="utf-8")
        powershell = (HERE / "install.ps1").read_text(encoding="utf-8")
        for text in (shell, powershell):
            self.assertIn("masters_nudge", text)
            self.assertIn("codex-hooks-snippet.json", text)
            self.assertIn("claude", text.lower())
            self.assertIn("codex", text.lower())


if __name__ == "__main__":
    unittest.main()
