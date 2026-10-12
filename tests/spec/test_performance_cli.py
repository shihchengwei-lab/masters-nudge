import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

import diagnostic_checkpoint
from masters_nudge.contracts import ProviderRun, SessionRef
from masters_nudge.core import NudgeCore
from masters_nudge.runtime import RuntimeSettings

ROOT = Path(__file__).resolve().parents[2]


class DiagnosticCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.environment = {"MASTERS_NUDGE_PROFILE": "performance",
                            "MASTERS_NUDGE_DATA_DIR": str(self.root / "data"),
                            "MASTERS_NUDGE_RUNTIME_DIR": str(ROOT), "MASTERS_NUDGE_ACTIVE": "0"}
        self.settings = RuntimeSettings.from_env(ROOT, environ=self.environment)
        self.request = "Diagnose idle RAM 78% without presuming pressure"
        NudgeCore(self.settings).start_round(SessionRef("s", "t", str(self.repo)), self.request)
        self.payload = {"cwd": str(self.repo), "task_request": self.request,
                        "batch_id": "first", "reason": "Before concluding pressure", "progress": "Initial sample",
                        "evidence": [{"tool_use_id": "measure-1", "tool_name": "supplied_fixture",
                                      "tool_input": {"synthetic": True},
                                      "tool_response": {"ram_used_percent": 78}}]}

    def run_cli(self, data, dispatch):
        output, errors = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, self.environment), \
                patch.object(sys, "stdin", Mock(buffer=io.BytesIO(data))), \
                patch("masters_nudge.providers.call_codex_result", dispatch), \
                redirect_stdout(output), redirect_stderr(errors):
            code = diagnostic_checkpoint.main()
        return code, output.getvalue(), errors.getvalue()

    def test_cli_feedback_is_delivered_once_and_retry_does_not_call_provider(self):
        dispatch = Mock(return_value=ProviderRun(json.dumps({"feedback": {
            "required": "Distinguish use from pressure", "observed": "RAM=78%; pressure unmeasured",
            "why": "Utilization is not pressure", "structure": "pressure <- available + paging + latency"}})))
        # Respect the exact 25-character WHY cap.
        dispatch.return_value = ProviderRun(dispatch.return_value.raw_output.replace(
            "Utilization is not pressure", "Pressure is unmeasured"))
        code, output, errors = self.run_cli(json.dumps(self.payload).encode(), dispatch)
        self.assertEqual((code, errors), (0, ""))
        result = json.loads(output)
        self.assertEqual(result["status"], "feedback")
        self.assertNotIn("Carmack", result["additionalContext"])
        self.assertIn("measurement distinction", result["additionalContext"])
        row = NudgeCore(self.settings).journal.recent()[0]
        self.assertEqual((row["outcome"], row["delivered"]), ("feedback", 1))
        code, output, _ = self.run_cli(json.dumps(self.payload).encode(), dispatch)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["status"], "no_feedback")
        self.assertEqual(dispatch.call_count, 1)

    def test_invalid_or_oversized_stdin_is_a_fault_without_provider_call(self):
        for data in (b"{", b"\xff", b"x" * 65537, b'{"evidence":[]}'):
            with self.subTest(length=len(data)):
                dispatch = Mock()
                code, output, errors = self.run_cli(data, dispatch)
                self.assertEqual((code, output), (1, ""))
                self.assertEqual(json.loads(errors)["status"], "fault")
                dispatch.assert_not_called()

    def test_reentry_guard_does_not_consume_input_or_invoke_provider(self):
        with patch.dict(os.environ, {"MASTERS_NUDGE_ACTIVE": "1"}), \
                patch.object(sys, "stdin", Mock()) as stream, \
                patch("masters_nudge.providers.call_codex_result") as dispatch:
            self.assertEqual(diagnostic_checkpoint.main(), 0)
            stream.buffer.read.assert_not_called()
            dispatch.assert_not_called()

    def test_packaged_entrypoint_rejects_default_profile_without_provider(self):
        package = ROOT / "plugins/masters-nudge"
        command = [sys.executable, str(package / "diagnostic_checkpoint.py")]
        env = {**os.environ, **self.environment, "MASTERS_NUDGE_PROFILE": "software-engineering",
               "MASTERS_NUDGE_RUNTIME_DIR": str(package)}
        result = subprocess.run(command, input=json.dumps(self.payload), text=True,
                                capture_output=True, env=env, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr)["kind"], "configuration")


if __name__ == "__main__":
    unittest.main()
