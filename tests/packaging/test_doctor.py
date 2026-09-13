"""Doctor diagnoses only the product surface that remains supported."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from masters_nudge import management


ROOT = Path(__file__).resolve().parents[2]


class DoctorTests(unittest.TestCase):
    def test_openai_login_status_accepts_windows_cli_stderr(self):
        completed = __import__("subprocess").CompletedProcess(
            ["codex.cmd", "login", "status"],
            0,
            "",
            "Logged in using ChatGPT\n",
        )
        with mock.patch.object(management, "_run_cli", return_value=completed):
            ready = management._provider_authenticated(
                "openai", "codex.cmd", {"PATH": ""}
            )

        self.assertTrue(ready)

    def test_hook_status_rejects_an_installed_older_version(self):
        completed = __import__("subprocess").CompletedProcess(
            ["codex", "plugin", "list", "--json"],
            0,
            '{"installed":[{"name":"masters-nudge","enabled":true,"version":"old"}]}',
            "",
        )
        with (
            mock.patch.object(management.shutil, "which", return_value="codex"),
            mock.patch.object(management, "_run_cli", return_value=completed),
        ):
            status = management._hook_status("codex", {"PATH": ""}, "new")

        self.assertFalse(status["ready"])
        self.assertEqual(status["error"], "installed version differs")

    def test_doctor_reports_provider_hooks_and_data(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = {
                "MASTERS_NUDGE_DATA_DIR": str(Path(raw) / "data"),
                "PATH": "",
            }
            with (
                mock.patch.object(management, "runtime_files", return_value=()),
                mock.patch.object(management, "_provider_cli", return_value="provider-cli"),
                mock.patch.object(management, "_provider_authenticated", return_value=True),
                mock.patch.object(
                    management,
                    "_hook_status",
                    return_value={"ready": True, "version": "test", "error": ""},
                ),
                mock.patch.object(management, "_python_version", return_value=(3, 12, 0)),
            ):
                result = management.doctor(ROOT, "all", environ=environment)

        self.assertTrue(result["core_ready"])
        self.assertEqual(
            [item["control_point"]["event"] for item in result["hosts"]],
            ["PostToolBatch", "PostToolBatch"],
        )
        self.assertEqual(
            [item["control_point"]["precision"] for item in result["hosts"]],
            ["exact", "exact"],
        )
    def test_doctor_reports_a_missing_host_hook_as_not_ready(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / ".codex-plugin").mkdir()
            (root / ".codex-plugin" / "plugin.json").write_text(
                '{"name":"masters-nudge"}\n', encoding="utf-8"
            )
            environment = {
                "MASTERS_NUDGE_DATA_DIR": str(root / "data"),
                "PATH": "",
            }
            with (
                mock.patch.object(management, "runtime_files", return_value=()),
                mock.patch.object(management, "_provider_cli", return_value="provider-cli"),
                mock.patch.object(management, "_python_version", return_value=(3, 12, 0)),
            ):
                result = management.doctor(root, "codex", environ=environment)

        self.assertFalse(result["core_ready"])
        self.assertFalse(result["hosts"][0]["hook_ready"])


if __name__ == "__main__":
    unittest.main()
