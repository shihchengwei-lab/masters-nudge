from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import masters_nudge_cli
from masters_nudge import management
from masters_nudge.runtime import PROVIDER_TIMEOUT_SEC, RuntimePaths, RuntimeSettings
from masters_nudge.settings import (
    DEFAULT_OLLAMA_URL,
    load_user_settings,
    save_provider,
)


class SettingsTests(unittest.TestCase):
    def test_default_config_lives_outside_expiring_session_data(self):
        with tempfile.TemporaryDirectory() as raw:
            home = Path(raw)
            paths = RuntimePaths.resolve(environ={"USERPROFILE": raw})

            self.assertEqual(paths.data_dir, home / ".masters-nudge" / "data")
            self.assertEqual(paths.settings_dir, home / ".masters-nudge")
            save_provider(paths.settings_dir, "openai", model="gpt-test")
            self.assertTrue((home / ".masters-nudge" / "config.json").is_file())
            self.assertFalse((paths.data_dir / "config.json").exists())

    def test_config_contains_only_provider_settings(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            save_provider(root, "openai", model="gpt-test")

            stored = json.loads((root / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(
                stored,
                {
                    "provider": "openai",
                    "model": "gpt-test",
                    "ollama_url": DEFAULT_OLLAMA_URL,
                },
            )

    def test_legacy_lens_key_is_ignored_and_removed_on_next_save(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "config.json").write_text(
                json.dumps(
                    {
                        "lens": "reliability",
                        "provider": "openai",
                        "model": "gpt-old",
                        "ollama_url": DEFAULT_OLLAMA_URL,
                    }
                ),
                encoding="utf-8",
            )

            loaded = load_user_settings(root)
            self.assertEqual((loaded.provider, loaded.model, loaded.error), ("openai", "gpt-old", ""))
            save_provider(root, "anthropic", model="sonnet")

            stored = json.loads((root / "config.json").read_text(encoding="utf-8"))
            self.assertNotIn("lens", stored)
            self.assertEqual(stored["provider"], "anthropic")

    def test_runtime_ignores_manual_environment_overrides(self):
        with tempfile.TemporaryDirectory() as raw:
            data = Path(raw)
            save_provider(data, "anthropic", model="chosen-model")
            settings = RuntimeSettings.from_env(
                environ={
                    "MASTERS_NUDGE_DATA_DIR": str(data),
                    "MASTERS_NUDGE_STAGE": "performance",
                    "MASTERS_NUDGE_PROVIDER": "openai",
                    "MASTERS_NUDGE_MODEL": "ignored-model",
                    "MASTERS_NUDGE_TIMEOUT": "1",
                    "MASTERS_NUDGE_CHECKPOINT_TIMEOUT": "2",
                },
                host="codex_cli",
            )

            self.assertEqual((settings.provider, settings.model), ("anthropic", "chosen-model"))
            self.assertEqual(PROVIDER_TIMEOUT_SEC, 90)
            self.assertFalse(hasattr(settings, "timeout_sec"))
            self.assertFalse(hasattr(settings, "lens"))

    def test_provider_reset_returns_to_host_default(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = {"MASTERS_NUDGE_DATA_DIR": raw}
            save_provider(Path(raw), "ollama", model="qwen3", ollama_url=DEFAULT_OLLAMA_URL)

            result = management.reset_provider_config(environ=environment)
            settings = RuntimeSettings.from_env(environ=environment, host="claude_code")

            self.assertTrue(result["reset"])
            self.assertEqual(settings.provider, "anthropic")


class JsonCliTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> tuple[int, dict]:
        output = io.StringIO()
        with patch.object(sys, "argv", ["masters-nudge", *arguments]):
            with redirect_stdout(output):
                code = masters_nudge_cli.main()
        return code, json.loads(output.getvalue())

    def test_lens_command_is_not_part_of_the_cli(self):
        stderr = io.StringIO()
        with patch.object(sys, "argv", ["masters-nudge", "lens"]):
            with self.assertRaises(SystemExit), redirect_stdout(io.StringIO()), patch(
                "sys.stderr", stderr
            ):
                masters_nudge_cli.main()

        self.assertIn("invalid choice", stderr.getvalue())

    def test_provider_cloud_configuration_and_reset(self):
        with tempfile.TemporaryDirectory() as raw:
            with patch.dict("os.environ", {"MASTERS_NUDGE_DATA_DIR": raw}, clear=True):
                code, result = self.run_cli(
                    "provider", "set", "openai", "--model", "gpt-test"
                )
                self.assertEqual(code, 0)
                self.assertTrue(result["saved"])
                code, result = self.run_cli("provider", "get")
                self.assertEqual(result["provider"], "openai")
                self.assertEqual(result["model"], "gpt-test")
                code, result = self.run_cli("provider", "reset")
                self.assertEqual(code, 0)
                self.assertTrue(result["reset"])

    def test_provider_get_resolves_the_host_default_after_reset(self):
        with tempfile.TemporaryDirectory() as raw:
            with patch.dict("os.environ", {"MASTERS_NUDGE_DATA_DIR": raw}, clear=True):
                code, result = self.run_cli("provider", "reset")
                self.assertEqual(code, 0)
                self.assertTrue(result["reset"])
                code, result = self.run_cli(
                    "provider", "get", "--host", "claude"
                )
                self.assertEqual(code, 0)
                self.assertEqual(result["provider"], "anthropic")
                self.assertEqual(result["model"], "sonnet")
                self.assertEqual(result["source"], "host_default")

    def test_recent_nudges_has_a_stable_empty_interface(self):
        with tempfile.TemporaryDirectory() as raw:
            with patch.dict("os.environ", {"MASTERS_NUDGE_DATA_DIR": raw}, clear=True):
                code, result = self.run_cli("recent-nudges", "--limit", "5")
                self.assertEqual(code, 0)
                self.assertEqual(result, {"nudges": [], "limit": 5, "error": ""})


if __name__ == "__main__":
    unittest.main()
