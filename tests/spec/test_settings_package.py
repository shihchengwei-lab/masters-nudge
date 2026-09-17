import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sqlite3
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

import masters_nudge_cli
from masters_nudge.runtime import RuntimePaths, RuntimeSettings
from masters_nudge.settings import load_user_settings, save_provider
from tools.build_plugin import check_plugin

ROOT = Path(__file__).resolve().parents[2]


class SettingsPackageTests(unittest.TestCase):
    def test_delivery_receipt_failure_does_not_emit_a_second_response(self):
        import hook_entry
        from unittest.mock import Mock
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for strict in (False, True):
                settings = RuntimeSettings("openai", "model", RuntimePaths(ROOT, root, root, root / "error.log"), strict=strict)
                core = Mock()
                core.journal.delivered.side_effect = sqlite3.OperationalError("disk I/O error")
                response = {"hookSpecificOutput": {"hookEventName": "PostToolBatch", "additionalContext": "feedback"},
                            "_masters_nudge": "attempt-1"}
                output = io.StringIO()
                with patch.object(sys, "argv", ["hook_entry.py"]), \
                     patch.object(sys, "stdin", Mock(buffer=io.BytesIO(b"{}"))), \
                     patch.object(hook_entry, "active_guard", return_value=False), \
                     patch.object(hook_entry.RuntimeSettings, "from_env", return_value=settings), \
                     patch.object(hook_entry, "NudgeCore", return_value=core), \
                     patch.object(hook_entry.CodexAdapter, "process", return_value=response), redirect_stdout(output):
                    code = hook_entry.main()
                self.assertEqual(code, int(strict))
                self.assertEqual(len(output.getvalue().splitlines()), 1)
                self.assertEqual(json.loads(output.getvalue())["hookSpecificOutput"]["additionalContext"], "feedback")
                self.assertNotIn("systemMessage", json.loads(output.getvalue()))
                self.assertIn("disk I/O error", settings.paths.error_log.read_text(encoding="utf-8"))

    def test_unwritable_journal_still_returns_fault_status(self):
        with tempfile.TemporaryDirectory() as raw:
            data_path = Path(raw) / "not-a-directory"
            data_path.write_text("occupied", encoding="utf-8")
            event = {"hook_event_name": "UserPromptSubmit", "session_id": "s", "turn_id": "t",
                     "cwd": raw, "prompt": "task", "transcript_path": None}
            for strict in ("0", "1"):
                env = {**os.environ, "MASTERS_NUDGE_ACTIVE": "0", "MASTERS_NUDGE_TEST_MODE": strict,
                       "MASTERS_NUDGE_DATA_DIR": str(data_path), "MASTERS_NUDGE_RUNTIME_DIR": str(ROOT)}
                result = subprocess.run([sys.executable, str(ROOT / "hook_entry.py")], input=json.dumps(event),
                                        capture_output=True, text=True, env=env, timeout=10)
                self.assertEqual(result.returncode, int(strict), result.stderr)
                response = json.loads(result.stdout)
                self.assertEqual(response["systemMessage"], "本輪反饋未執行")
                self.assertNotIn("hookSpecificOutput", response)
                self.assertTrue(result.stderr)

    @unittest.skipUnless(os.name == "nt", "Windows launcher")
    def test_packaged_launcher_preserves_failure_and_reports_missing_python(self):
        launcher = ROOT / "plugins/masters-nudge/hooks/run_python.cmd"
        command = subprocess.list2cmdline([str(launcher), "-c", "import sys; sys.exit(7)"])
        result = subprocess.run(command, shell=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 7)
        env = {**os.environ, "PATH": str(Path(os.environ["SystemRoot"]) / "System32")}
        for strict in ("0", "1"):
            result = subprocess.run(command, shell=True, capture_output=True, text=True,
                                    env={**env, "MASTERS_NUDGE_TEST_MODE": strict}, timeout=15)
            self.assertIn("本輪反饋未執行", json.loads(result.stdout)["systemMessage"])
            self.assertEqual(result.returncode, int(strict))

    def test_settings_outside_data_and_only_supported_choice(self):
        with tempfile.TemporaryDirectory() as raw:
            paths = RuntimePaths.resolve(environ={"USERPROFILE": raw})
            self.assertNotEqual(paths.settings_dir, paths.data_dir)
            save_provider(paths.settings_dir, "openai", model="chosen")
            self.assertEqual(load_user_settings(paths.settings_dir).model, "chosen")
            self.assertEqual(set(json.loads((paths.settings_dir / "config.json").read_text())), {"provider", "model"})
            for provider in ("anthropic", "ollama"):
                with self.assertRaises(ValueError):
                    save_provider(paths.settings_dir, provider)

    def test_old_supported_setting_is_preserved_but_unsupported_never_falls_back(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "config.json"
            path.write_text(json.dumps({"provider": "openai", "model": "chosen", "ollama_url": "old", "lens": "old"}))
            settings = RuntimeSettings.from_env(environ={"MASTERS_NUDGE_DATA_DIR": raw,
                                 "MASTERS_NUDGE_MODEL": "ignored", "MASTERS_NUDGE_PROVIDER": "ignored"})
            self.assertEqual(settings.model, "chosen")
            self.assertFalse(settings.configuration_error)
            path.write_text('{"provider":"ollama","model":"chosen"}')
            self.assertTrue(RuntimeSettings.from_env(environ={"MASTERS_NUDGE_DATA_DIR": raw}).configuration_error)

    def test_cli_lists_only_openai_and_rejects_removed_commands(self):
        output = io.StringIO()
        with patch.object(sys, "argv", ["nudge", "provider", "list"]), redirect_stdout(output):
            self.assertEqual(masters_nudge_cli.main(), 0)
        self.assertEqual([p["id"] for p in json.loads(output.getvalue())["providers"]], ["openai"])
        for argv in (["nudge", "provider", "set", "ollama"], ["nudge", "lens"]):
            with patch.object(sys, "argv", argv), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                masters_nudge_cli.main()

    def test_generated_plugin_is_current(self):
        self.assertEqual(check_plugin(), [])
        self.assertFalse((ROOT / ".claude-plugin/marketplace.json").exists())
        hooks = json.loads((ROOT / "plugins/masters-nudge/hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
        self.assertEqual(set(hooks), {"UserPromptSubmit", "PostToolBatch"})

    def test_provider_aims_below_the_hard_feedback_limit(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")
        self.assertIn("Aim for at most 100 characters", prompt)

    def test_clean_package_starts_hook_and_reports_fault_without_actor_context(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            package = root / "package"
            shutil.copytree(ROOT / "plugins/masters-nudge", package, ignore=shutil.ignore_patterns("__pycache__"))
            env = {**os.environ, "MASTERS_NUDGE_DATA_DIR": str(root / "data"), "MASTERS_NUDGE_ACTIVE": "0",
                   "MASTERS_NUDGE_RUNTIME_DIR": str(package), "PYTHONPATH": ""}
            event = {"hook_event_name": "UserPromptSubmit", "session_id": "s", "turn_id": "t",
                     "cwd": str(root), "prompt": "task", "transcript_path": None}
            command = [sys.executable, str(package / "hook_entry.py")]
            result = subprocess.run(command, input=json.dumps(event), capture_output=True, text=True, env=env, cwd=root, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            bad = dict(event, hook_event_name="PostToolBatch")
            for strict in ("0", "1"):
                result = subprocess.run(command, input=json.dumps(bad), capture_output=True, text=True,
                                        env={**env, "MASTERS_NUDGE_TEST_MODE": strict}, cwd=root, timeout=10)
                output = json.loads(result.stdout)
                self.assertIn("本輪反饋未執行", output["systemMessage"])
                self.assertNotIn("hookSpecificOutput", output)
                self.assertEqual(result.returncode, int(strict))
