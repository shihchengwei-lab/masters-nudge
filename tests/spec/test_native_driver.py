import tempfile
import json
import unittest
from unittest.mock import patch
from pathlib import Path

from tools.verify_spec_actor import runtime_helpers, trial_invalid_reason, packaged_hook_overrides, prepare_case, capture_sources, actor_workspace, arm_hook_arguments


class NativeDriverTests(unittest.TestCase):
    def test_actor_workspace_has_a_separate_lifetime_and_never_replaces_existing_files(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "result.txt").write_text("evidence")
            with actor_workspace(root) as workspace:
                self.assertEqual(workspace, root / "workspace")
                (workspace / "source.py").write_text("x=1")
            self.assertFalse(workspace.exists())
            self.assertEqual((root / "result.txt").read_text(), "evidence")
            workspace.mkdir()
            (workspace / "user.txt").write_text("keep")
            with self.assertRaises(FileExistsError):
                with actor_workspace(root):
                    pass
            self.assertEqual((workspace / "user.txt").read_text(), "keep")

    def test_source_read_failure_retains_other_files_and_reports_incomplete_evidence(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "source.py").write_text("x = 1\n")
            (root / "test_source.py").touch()
            read = Path.read_text
            def read_text(path, *args, **kwargs):
                if path.name == "test_source.py":
                    raise PermissionError("read denied")
                return read(path, *args, **kwargs)
            with patch.object(Path, "read_text", read_text):
                files, errors = capture_sources(root)
            self.assertEqual(files, {"source.py": "x = 1\n"})
            self.assertEqual(errors, {"test_source.py": "PermissionError: read denied"})

    def test_custom_case_uses_its_own_files_task_and_verification(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "workspace"
            workspace.mkdir()
            fixture = root / "case.json"
            files = {"state.py": "done = False\n", "view.py": "from state import done\n"}
            fixture.write_text(json.dumps({"files": files, "task": "新增 render", "verify": "assert True"}), encoding="utf-8")
            initial, task, verify = prepare_case(workspace, fixture=fixture)
            self.assertEqual(initial, files)
            self.assertEqual(task, "新增 render")
            self.assertEqual(verify, "assert True")
            self.assertEqual((workspace / "view.py").read_text(), files["view.py"])
            self.assertFalse((workspace / "job.py").exists())
            fixture.write_text(json.dumps({"files": {"../outside.py": "x"}, "task": "task", "verify": "pass"}))
            with self.assertRaises(ValueError):
                prepare_case(workspace, fixture=fixture)
            self.assertFalse((root / "outside.py").exists())

    def test_uses_packaged_hook_commands_including_launcher(self):
        package = Path(__file__).resolve().parents[2] / "plugins/masters-nudge"
        overrides = packaged_hook_overrides(package)
        self.assertEqual(len(overrides), 6)
        self.assertIn("mcp_servers.masters_nudge=", overrides[1])
        self.assertIn("mcp_entry.py", overrides[1])
        self.assertNotIn("PLUGIN_ROOT", overrides[1])
        self.assertIn("hooks.PostToolUse=", overrides[3])
        self.assertIn('"type"="mcp_tool"', overrides[3])
        self.assertIn("hooks.UserPromptSubmit=", overrides[5])

    def test_direct_arm_has_no_hook_arguments_and_nudge_arm_uses_the_package(self):
        package = Path(__file__).resolve().parents[2] / "plugins/masters-nudge"
        self.assertEqual(arm_hook_arguments(package, "direct"), [])
        self.assertEqual(arm_hook_arguments(package, "nudge"), packaged_hook_overrides(package))

    def test_missing_windows_runner_is_rejected_before_actor(self):
        with tempfile.TemporaryDirectory() as raw:
            binary = Path(raw) / "codex.exe"
            binary.touch()
            with self.assertRaisesRegex(ValueError, "codex-command-runner"):
                runtime_helpers(binary, windows=True)
            (binary.parent / "codex-command-runner.exe").write_bytes(b"runner")
            self.assertIn("codex-command-runner.exe", runtime_helpers(binary, windows=True))

    def test_fault_and_missing_events_are_invalid_not_success(self):
        self.assertEqual(trial_invalid_reason("provider timeout", 0, [], []), "provider timeout")
        self.assertTrue(trial_invalid_reason("", 0, [], []))
        self.assertTrue(trial_invalid_reason("", 0, [{"event": "read"}], []))
        self.assertTrue(trial_invalid_reason("", 1, [{}], [{"outcome": "silence"}]))
        self.assertEqual(trial_invalid_reason("", 0, [{}], [{"outcome": "silence"}]), "")
        self.assertEqual(trial_invalid_reason("", 0, [], [], require_attempts=False), "")
        self.assertTrue(trial_invalid_reason("", 0, [{}], [{"outcome": "fault"}]))
        self.assertTrue(trial_invalid_reason("", 0, [{}], [{"outcome": None}]))
