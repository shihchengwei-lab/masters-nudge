import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

import claude_checkpoint
import claude_stop
import masters_nudge_cli
from masters_nudge.management import (
    configure_grok,
    configure_local,
    doctor,
    inspect_legacy_config,
    launch_window,
    migrate_legacy,
    migrate_legacy_config,
    reset_reviewer_config,
)
from masters_nudge.runtime import RuntimeSettings, reviewer_config_path
from tools import build_plugin


HERE = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = HERE / "plugins" / "masters-nudge"


class HostDefaultTests(unittest.TestCase):
    def test_each_host_defaults_to_its_own_reviewer(self):
        environment = {"HOME": "/tmp/masters-nudge-test"}
        claude = RuntimeSettings.from_env(environ=environment, host="claude_code")
        codex = RuntimeSettings.from_env(environ=environment, host="codex_cli")
        legacy = RuntimeSettings.from_env(environ=environment)

        self.assertEqual((claude.provider, claude.model), ("anthropic", "sonnet"))
        self.assertEqual((codex.provider, codex.model), ("openai", "gpt-5.6-sol"))
        self.assertEqual(legacy.provider, "openai")
        self.assertEqual(claude.timeout_sec, 120)
        self.assertEqual(codex.timeout_sec, 120)
        self.assertEqual(claude.checkpoint_timeout_sec, 90)
        self.assertEqual(codex.checkpoint_timeout_sec, 90)

    def test_grok_can_be_selected_without_changing_host_defaults(self):
        environment = {
            "HOME": "/tmp/masters-nudge-test",
            "MASTERS_NUDGE_PROVIDER": "grok",
        }
        settings = RuntimeSettings.from_env(environ=environment, host="codex_cli")
        self.assertEqual((settings.provider, settings.model), ("grok", ""))


class RuntimeConfigurationTests(unittest.TestCase):
    def test_configure_grok_persists_cli_default_model(self):
        with (
            tempfile.TemporaryDirectory() as raw,
            patch("masters_nudge.management._provider_cli", return_value="grok"),
        ):
            environment = {
                "HOME": raw,
                "USERPROFILE": raw,
                "MASTERS_NUDGE_DATA_DIR": str(Path(raw) / "data"),
            }
            result = configure_grok(environ=environment)
            settings = RuntimeSettings.from_env(environ=environment, host="codex_cli")
        self.assertTrue(result["saved"])
        self.assertEqual((settings.provider, settings.model), ("grok", ""))

    def test_explicit_provider_and_model_override_host_default(self):
        environment = {
            "HOME": "/tmp/masters-nudge-test",
            "MASTERS_NUDGE_PROVIDER": "openai",
            "MASTERS_NUDGE_MODEL": "custom-model",
        }
        settings = RuntimeSettings.from_env(environ=environment, host="claude_code")
        self.assertEqual(
            (settings.provider, settings.model), ("openai", "custom-model")
        )

    def test_provider_override_gets_that_providers_default_model(self):
        settings = RuntimeSettings.from_env(
            environ={
                "HOME": "/tmp/masters-nudge-test",
                "MASTERS_NUDGE_PROVIDER": "anthropic",
            },
            host="codex_cli",
        )

        self.assertEqual((settings.provider, settings.model), ("anthropic", "sonnet"))

    def test_python_entries_enforce_recursion_guard_without_shell_wrappers(self):
        with (
            patch.dict(os.environ, {"MASTERS_NUDGE_ACTIVE": "1"}),
            patch("claude_stop.read_hook_input") as buddy_input,
            patch("claude_checkpoint.sys.stdin.read") as checkpoint_input,
        ):
            claude_stop.main()
            claude_checkpoint.main()

        buddy_input.assert_not_called()
        checkpoint_input.assert_not_called()


class LocalConfigurationTests(unittest.TestCase):
    @staticmethod
    def _environment(root: str) -> dict[str, str]:
        return {
            "HOME": root,
            "USERPROFILE": root,
            "MASTERS_NUDGE_DATA_DIR": str(Path(root) / "data"),
        }

    @staticmethod
    def _ready(endpoint: str, _model: str, **_kwargs) -> dict:
        return {
            "ready": True,
            "endpoint": endpoint,
            "endpoint_loopback": True,
            "server_ready": True,
            "cloud_disabled": True,
            "model_ready": True,
            "model_local": True,
            "error": "",
        }

    def test_persistent_local_config_is_shared_by_both_hosts(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = self._environment(raw)
            path = reviewer_config_path(Path(environment["MASTERS_NUDGE_DATA_DIR"]))
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "provider": "ollama-local",
                        "model": "user-model",
                        "ollama_url": "http://localhost:11434",
                    }
                ),
                encoding="utf-8",
            )

            claude = RuntimeSettings.from_env(environ=environment, host="claude_code")
            codex = RuntimeSettings.from_env(environ=environment, host="codex_cli")

        for settings in (claude, codex):
            self.assertEqual(settings.provider, "ollama-local")
            self.assertEqual(settings.model, "user-model")
            self.assertEqual(settings.ollama_url, "http://localhost:11434")
            self.assertEqual(settings.configuration_source, "config")

    def test_environment_provider_does_not_reuse_stale_config_model(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = self._environment(raw)
            path = reviewer_config_path(Path(environment["MASTERS_NUDGE_DATA_DIR"]))
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "provider": "ollama-local",
                        "model": "local-model",
                        "ollama_url": "http://localhost:11434",
                    }
                ),
                encoding="utf-8",
            )
            environment["MASTERS_NUDGE_PROVIDER"] = "anthropic"
            settings = RuntimeSettings.from_env(environ=environment, host="codex_cli")

        self.assertEqual((settings.provider, settings.model), ("anthropic", "sonnet"))
        self.assertEqual(settings.configuration_source, "environment")

    def test_invalid_persistent_config_fails_closed_instead_of_using_cloud(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = self._environment(raw)
            path = reviewer_config_path(Path(environment["MASTERS_NUDGE_DATA_DIR"]))
            path.parent.mkdir(parents=True)
            path.write_text("{broken", encoding="utf-8")
            settings = RuntimeSettings.from_env(environ=environment, host="claude_code")

        self.assertEqual(settings.provider, "configuration-error")
        self.assertEqual(settings.model, "")
        self.assertTrue(settings.configuration_error)

    def test_unreadable_persistent_config_fails_closed(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = self._environment(raw)
            with patch.object(Path, "read_text", side_effect=PermissionError("denied")):
                settings = RuntimeSettings.from_env(
                    environ=environment, host="codex_cli"
                )

        self.assertEqual(settings.provider, "configuration-error")
        self.assertIn("denied", settings.configuration_error)

    def test_explicit_local_provider_requires_an_explicit_model(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = self._environment(raw)
            environment["MASTERS_NUDGE_PROVIDER"] = "ollama-local"
            settings = RuntimeSettings.from_env(environ=environment, host="claude_code")

        self.assertEqual(settings.provider, "ollama-local")
        self.assertEqual(settings.model, "")

    def test_legacy_environment_aliases_no_longer_configure_runtime(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = {
                **self._environment(raw),
                "BUDDY_PROVIDER": "ollama-local",
                "BUDDY_MODEL": "legacy-model",
                "BUDDY_OLLAMA_URL": "http://localhost:22434",
            }
            settings = RuntimeSettings.from_env(environ=environment, host="codex_cli")

        self.assertEqual(settings.provider, "openai")
        self.assertEqual(settings.model, "gpt-5.6-sol")
        self.assertEqual(settings.ollama_url, "http://127.0.0.1:11434")
        self.assertEqual(settings.configuration_source, "host_default")

    def test_configure_preflights_then_writes_atomically_and_reset_is_scoped(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = self._environment(raw)
            result = configure_local(
                "user-model",
                "http://localhost:11434/",
                environ=environment,
                inspector=self._ready,
            )
            path = Path(result["path"])
            payload = json.loads(path.read_text(encoding="utf-8"))
            unrelated = path.parent / "reactions.log"
            unrelated.write_text("keep", encoding="utf-8")
            reset = reset_reviewer_config(environ=environment)

            self.assertTrue(result["saved"])
            self.assertEqual(payload["provider"], "ollama-local")
            self.assertEqual(payload["model"], "user-model")
            self.assertEqual(payload["ollama_url"], "http://localhost:11434")
            self.assertTrue(reset["reset"])
            self.assertTrue(reset["removed"])
            self.assertFalse(path.exists())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")

    def test_failed_preflight_preserves_existing_config(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = self._environment(raw)
            path = reviewer_config_path(Path(environment["MASTERS_NUDGE_DATA_DIR"]))
            path.parent.mkdir(parents=True)
            original = {
                "provider": "ollama-local",
                "model": "old-model",
                "ollama_url": "http://127.0.0.1:11434",
            }
            path.write_text(json.dumps(original), encoding="utf-8")
            result = configure_local(
                "new-model",
                environ=environment,
                inspector=lambda *_args, **_kwargs: {
                    "ready": False,
                    "error": "cloud is enabled",
                },
            )

            self.assertFalse(result["saved"])
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)

    def test_invalid_preflight_result_does_not_replace_existing_config(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = self._environment(raw)
            path = reviewer_config_path(Path(environment["MASTERS_NUDGE_DATA_DIR"]))
            path.parent.mkdir(parents=True)
            original = {
                "provider": "ollama-local",
                "model": "old-model",
                "ollama_url": "http://127.0.0.1:11434",
            }
            path.write_text(json.dumps(original), encoding="utf-8")

            result = configure_local(
                "new-model",
                environ=environment,
                inspector=lambda *_args, **_kwargs: None,
            )

            self.assertFalse(result["saved"])
            self.assertIn("invalid result", result["error"])
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)

    @unittest.skipIf(os.name == "nt", "POSIX file modes are not stable on Windows")
    def test_new_local_config_is_private_on_posix(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = self._environment(raw)
            result = configure_local(
                "user-model",
                environ=environment,
                inspector=self._ready,
            )

            self.assertEqual(Path(result["path"]).stat().st_mode & 0o777, 0o600)


class LocalCliTests(unittest.TestCase):
    def test_local_configure_json_exit_status_matches_save_result(self):
        configured = {
            "saved": True,
            "path": "/tmp/reviewer.json",
            "provider": "ollama-local",
            "model": "chosen-model",
            "ollama_url": "http://127.0.0.1:11434",
            "diagnostic": {"ready": True},
            "error": "",
        }
        output = io.StringIO()
        with (
            patch.object(
                sys,
                "argv",
                [
                    "masters-nudge",
                    "local",
                    "configure",
                    "--model",
                    "chosen-model",
                    "--json",
                ],
            ),
            patch.object(
                masters_nudge_cli, "configure_local", return_value=configured
            ) as configure,
            redirect_stdout(output),
        ):
            status = masters_nudge_cli.main()

        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue())["model"], "chosen-model")
        configure.assert_called_once_with("chosen-model", "http://127.0.0.1:11434")

    def test_local_reset_warns_that_cloud_defaults_return(self):
        output = io.StringIO()
        with (
            patch.object(sys, "argv", ["masters-nudge", "local", "reset"]),
            patch.object(
                masters_nudge_cli,
                "reset_reviewer_config",
                return_value={
                    "reset": True,
                    "removed": True,
                    "path": "/tmp/reviewer.json",
                    "error": "",
                },
            ),
            redirect_stdout(output),
        ):
            status = masters_nudge_cli.main()

        self.assertEqual(status, 0)
        self.assertIn("cloud defaults", output.getvalue())

    def test_grok_reset_reports_a_removal_error(self):
        output = io.StringIO()
        with (
            patch.object(sys, "argv", ["masters-nudge", "grok", "reset"]),
            patch.object(
                masters_nudge_cli,
                "reset_reviewer_config",
                return_value={
                    "reset": False,
                    "removed": False,
                    "path": "/tmp/reviewer.json",
                    "error": "permission denied",
                },
            ),
            redirect_stdout(output),
        ):
            status = masters_nudge_cli.main()

        self.assertEqual(status, 1)
        self.assertIn("permission denied", output.getvalue())
        self.assertNotIn("No persistent reviewer config", output.getvalue())


class PluginPackagingTests(unittest.TestCase):
    def test_generated_runtime_matches_canonical_sources(self):
        self.assertEqual(build_plugin.check_plugin(), [])

    def test_manifests_and_marketplaces_share_name_and_prerelease(self):
        codex = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        claude = json.loads(
            (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        codex_marketplace = json.loads(
            (HERE / ".agents" / "plugins" / "marketplace.json").read_text(
                encoding="utf-8"
            )
        )
        claude_marketplace = json.loads(
            (HERE / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )

        self.assertEqual(codex["name"], "masters-nudge")
        self.assertEqual(codex["version"].split("+", 1)[0], claude["version"])
        self.assertIn("dev", claude["version"])
        self.assertTrue(codex["interface"]["privacyPolicyURL"].endswith("#privacy"))
        self.assertNotIn("hooks", codex)
        self.assertEqual(claude["hooks"], "./hooks/claude.json")
        self.assertEqual(claude["userConfig"]["python_command"]["default"], "python")
        self.assertEqual(codex_marketplace["name"], "masters-nudge")
        self.assertEqual(
            codex_marketplace["plugins"][0]["source"]["path"],
            "./plugins/masters-nudge",
        )
        self.assertEqual(claude_marketplace["plugins"][0]["version"], claude["version"])
        self.assertIn(
            "local Ollama",
            " ".join(codex["interface"]["defaultPrompt"]),
        )

    def test_inventory_rejects_unexpected_plugin_files(self):
        with tempfile.TemporaryDirectory() as raw:
            plugin_root = Path(raw) / "masters-nudge"
            import shutil

            shutil.copytree(PLUGIN_ROOT, plugin_root)
            (plugin_root / "leftover.py").write_text("pass\n", encoding="utf-8")

            with patch.object(build_plugin, "PLUGIN_ROOT", plugin_root):
                errors = build_plugin.check_plugin()

        self.assertIn("unexpected: plugins/masters-nudge/leftover.py", errors)

    def test_inventory_rejects_missing_static_plugin_file(self):
        with tempfile.TemporaryDirectory() as raw:
            plugin_root = Path(raw) / "masters-nudge"
            import shutil

            shutil.copytree(PLUGIN_ROOT, plugin_root)
            (plugin_root / "hooks" / "claude.json").unlink()

            with patch.object(build_plugin, "PLUGIN_ROOT", plugin_root):
                errors = build_plugin.check_plugin()

        self.assertIn("missing: plugins/masters-nudge/hooks/claude.json", errors)

    def test_claude_manifest_is_the_base_version_owner(self):
        with tempfile.TemporaryDirectory() as raw:
            import shutil

            root = Path(raw)
            plugin_root = root / "masters-nudge"
            marketplace = root / "marketplace.json"
            shutil.copytree(PLUGIN_ROOT, plugin_root)
            shutil.copy2(HERE / ".claude-plugin" / "marketplace.json", marketplace)
            claude_path = plugin_root / ".claude-plugin" / "plugin.json"
            claude = json.loads(claude_path.read_text(encoding="utf-8"))
            claude["version"] = "9.8.7-dev.6"
            claude_path.write_text(json.dumps(claude), encoding="utf-8")

            with (
                patch.object(build_plugin, "PLUGIN_ROOT", plugin_root),
                patch.object(build_plugin, "CLAUDE_MARKETPLACE", marketplace),
            ):
                build_plugin._sync_versions()

            codex = json.loads(
                (plugin_root / ".codex-plugin" / "plugin.json").read_text(
                    encoding="utf-8"
                )
            )
            marketplace_payload = json.loads(marketplace.read_text(encoding="utf-8"))

        self.assertEqual(codex["version"].split("+", 1)[0], "9.8.7-dev.6")
        self.assertEqual(marketplace_payload["plugins"][0]["version"], "9.8.7-dev.6")

    def test_host_hook_files_are_separate_and_reference_plugin_roots(self):
        codex_text = (PLUGIN_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8")
        claude_text = (PLUGIN_ROOT / "hooks" / "claude.json").read_text(
            encoding="utf-8"
        )
        codex = json.loads(codex_text)["hooks"]
        claude = json.loads(claude_text)["hooks"]

        self.assertEqual(set(codex), {"UserPromptSubmit", "PostToolUse", "Stop"})
        self.assertIn("PostToolUseFailure", claude)
        self.assertIn("${PLUGIN_ROOT}", codex_text)
        self.assertIn("$env:PLUGIN_ROOT", codex_text)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", claude_text)
        self.assertIn("${user_config.python_command}", claude_text)
        self.assertIn('"args"', claude_text)
        self.assertNotIn('"command": "bash ', claude_text)
        self.assertIn("claude_prompt.py", claude_text)
        self.assertIn("claude_checkpoint.py", claude_text)
        self.assertIn("claude_stop.py", claude_text)
        self.assertNotIn("${CLAUDE_PLUGIN_ROOT}/inject.py", claude_text)
        self.assertNotIn("${CLAUDE_PLUGIN_ROOT}/checkpoint.py", claude_text)
        self.assertNotIn("${CLAUDE_PLUGIN_ROOT}/buddy.py", claude_text)
        post_tool_hook = codex["PostToolUse"][0]["hooks"][0]
        self.assertNotIn("async", post_tool_hook)
        self.assertGreaterEqual(post_tool_hook["timeout"], 90)

    def test_codex_launchers_are_fail_open(self):
        windows = (PLUGIN_ROOT / "hooks" / "run_python.cmd").read_text(encoding="utf-8")
        posix = (PLUGIN_ROOT / "hooks" / "run_python.sh").read_text(encoding="utf-8")

        self.assertNotIn("exit /b %errorlevel%", windows)
        self.assertIn("PYTHONIOENCODING=utf-8", windows)
        self.assertGreaterEqual(windows.count("exit /b 0"), 4)
        self.assertIn("PYTHONIOENCODING=utf-8", posix)
        self.assertNotIn('exec "$candidate" "$@"', posix)

    def test_readmes_lead_with_native_plugin_install(self):
        for name in ("README.md", "README.zh-TW.md"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn("claude plugin install masters-nudge@masters-nudge ", text)
            self.assertIn("--config python_command=python", text)
            self.assertIn("codex plugin add masters-nudge@masters-nudge", text)
            self.assertIn(
                "0.1.0-dev.2",
                (HERE / "CHANGELOG.md").read_text(encoding="utf-8"),
            )
        self.assertTrue((PLUGIN_ROOT / "skills" / "setup-local" / "SKILL.md").exists())

    def test_ci_smokes_the_plugin_package_without_legacy_installers(self):
        workflow = (HERE / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )

        for entrypoint in (
            "claude_prompt.py",
            "claude_checkpoint.py",
            "claude_stop.py",
        ):
            self.assertIn(entrypoint, workflow)
        for removed in (
            " buddy.py",
            " checkpoint.py",
            " inject.py",
            " install.sh",
            "./install.ps1",
        ):
            self.assertNotIn(removed, workflow)
        self.assertIn("hooks/run_python.sh", workflow)
        self.assertIn("hooks\\run_python.cmd", workflow)
        self.assertIn("masters_nudge_cli.py\" doctor --host all --json", workflow)
        self.assertNotIn('assert data["core_ready"]', workflow)
        self.assertNotIn("-not $doctor.core_ready", workflow)
        self.assertIn('data["python"]["ready"]', workflow)
        self.assertIn('data["data"]["writable"]', workflow)
        self.assertIn("$doctor.python.ready", workflow)
        self.assertIn("$doctor.data.writable", workflow)
        self.assertIn("Expected two host-namespaced turn states", workflow)


class LegacyMigrationTests(unittest.TestCase):
    @staticmethod
    def _write(path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2), encoding="utf-8")

    def test_dry_run_then_apply_removes_only_known_handler_and_backs_up(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / ".claude" / "settings.json"
            known = {
                "type": "command",
                "command": "bash ~/.claude/scripts/buddy/buddy.sh",
                "timeout": 90,
                "async": True,
            }
            unrelated = {"type": "command", "command": "echo keep-me"}
            original = {
                "theme": "dark",
                "hooks": {"Stop": [{"hooks": [known, unrelated]}]},
            }
            self._write(path, original)

            dry_run = migrate_legacy_config(path, "claude")
            self.assertEqual(dry_run["exact"], 1)
            self.assertFalse(dry_run["applied"])
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)

            applied = migrate_legacy_config(path, "claude", apply=True)
            self.assertTrue(applied["applied"])
            self.assertEqual(applied["removed"], 1)
            self.assertTrue(Path(applied["backup"]).exists())
            updated = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(updated["theme"], "dark")
            self.assertEqual(updated["hooks"]["Stop"][0]["hooks"], [unrelated])
            self.assertEqual(
                json.loads(Path(applied["backup"]).read_text(encoding="utf-8")),
                original,
            )

            repeated = migrate_legacy_config(path, "claude", apply=True)
            self.assertFalse(repeated["applied"])
            self.assertEqual(repeated["exact"], 0)

    def test_modified_near_match_refuses_automatic_migration(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / ".claude" / "settings.json"
            original = {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "bash ~/.claude/scripts/buddy/custom.sh",
                                }
                            ]
                        }
                    ]
                }
            }
            self._write(path, original)

            result = migrate_legacy_config(path, "claude", apply=True)
            self.assertFalse(result["applied"])
            self.assertEqual(len(result["near"]), 1)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)
            self.assertEqual(list(path.parent.glob("*.bak")), [])

    def test_apply_refuses_when_source_changed_since_preflight(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "settings.json"
            original = {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "bash ~/.claude/scripts/buddy/buddy.sh",
                                }
                            ]
                        }
                    ]
                }
            }
            self._write(path, original)
            plan = inspect_legacy_config(path, "claude")
            changed = {**original, "unrelated": "changed after preflight"}
            self._write(path, changed)

            result = migrate_legacy_config(
                path,
                "claude",
                apply=True,
                expected_source_digest=plan["source_digest"],
            )

            self.assertFalse(result["applied"])
            self.assertIn("changed since preflight", result["error"])
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), changed)
            self.assertEqual(list(path.parent.glob("*.bak")), [])

    def test_all_hosts_preflight_before_changing_either_config(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            claude_path = root / ".claude" / "settings.json"
            codex_path = root / ".codex" / "hooks.json"
            claude = {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "bash ~/.claude/scripts/buddy/buddy.sh",
                                }
                            ]
                        }
                    ]
                }
            }
            codex = {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "python ~/.masters-nudge/runtime/hook_entry.py --host codex_cli --custom",
                                }
                            ]
                        }
                    ]
                }
            }
            self._write(claude_path, claude)
            self._write(codex_path, codex)

            result = migrate_legacy(
                "all",
                apply=True,
                environ={"HOME": raw, "USERPROFILE": raw},
            )

            self.assertTrue(result["unsafe"])
            self.assertEqual(
                json.loads(claude_path.read_text(encoding="utf-8")), claude
            )
            self.assertEqual(list(claude_path.parent.glob("*.bak")), [])

    def test_codex_handler_with_both_platform_commands_is_exact(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / ".codex" / "hooks.json"
            self._write(
                path,
                {
                    "hooks": {
                        "Stop": [
                            {
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "python3 ~/.masters-nudge/runtime/hook_entry.py --host codex_cli --detach-stop",
                                        "commandWindows": 'py -3 "%USERPROFILE%\\.masters-nudge\\runtime\\hook_entry.py" --host codex_cli --detach-stop',
                                    }
                                ]
                            }
                        ]
                    }
                },
            )
            inspection = inspect_legacy_config(path, "codex")
            self.assertEqual(inspection["exact"], 1)
            self.assertEqual(inspection["near"], [])

    def test_invalid_json_fails_closed(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "settings.json"
            path.write_text("{not-json", encoding="utf-8")
            result = migrate_legacy_config(path, "claude", apply=True)
            self.assertFalse(result["applied"])
            self.assertIn("cannot read JSON", result["error"])
            self.assertEqual(path.read_text(encoding="utf-8"), "{not-json")

    def test_write_failure_restores_original_and_reports_backup(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / ".claude" / "settings.json"
            original = {
                "hooks": {
                    "Stop": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "bash ~/.claude/scripts/buddy/buddy.sh",
                                }
                            ]
                        }
                    ]
                }
            }
            self._write(path, original)

            with patch(
                "masters_nudge.management._atomic_json_write",
                side_effect=OSError("write blocked"),
            ):
                result = migrate_legacy_config(path, "claude", apply=True)

            self.assertFalse(result["applied"])
            self.assertIn("write blocked", result["error"])
            self.assertTrue(Path(result["backup"]).exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)

    @unittest.skipIf(os.name == "nt", "POSIX file modes are not stable on Windows")
    def test_apply_preserves_original_file_mode(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / ".claude" / "settings.json"
            self._write(
                path,
                {
                    "hooks": {
                        "Stop": [
                            {
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "bash ~/.claude/scripts/buddy/buddy.sh",
                                    }
                                ]
                            }
                        ]
                    }
                },
            )
            path.chmod(0o600)

            migrate_legacy_config(path, "claude", apply=True)

            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_migrate_copies_general_stage_config_and_log_idempotently(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            legacy = root / ".claude" / "buddy"
            legacy.mkdir(parents=True)
            (legacy / "config.json").write_text(
                json.dumps({"persona": "general"}), encoding="utf-8"
            )
            legacy_log = legacy / "session-1.log"
            legacy_log.write_text(
                json.dumps({"ts": "2026-01-01", "reaction": "keep"}) + "\n",
                encoding="utf-8",
            )
            environment = {"HOME": raw, "USERPROFILE": raw}

            dry_run = migrate_legacy("claude", environ=environment)
            self.assertEqual(dry_run["lifecycle"]["status"], "would_migrate")
            self.assertEqual(dry_run["lifecycle"]["stage"], "build")
            self.assertEqual(dry_run["logs"]["items"][0]["status"], "would_copy")
            self.assertFalse((root / ".masters-nudge" / "data").exists())

            applied = migrate_legacy("claude", apply=True, environ=environment)
            data_dir = root / ".masters-nudge" / "data"
            self.assertEqual(applied["lifecycle"]["status"], "migrated")
            self.assertEqual(
                json.loads((data_dir / "config.json").read_text(encoding="utf-8")),
                {"stage": "build"},
            )
            copied = data_dir / "claude_code--session-1.log"
            self.assertEqual(copied.read_bytes(), legacy_log.read_bytes())
            self.assertTrue(legacy_log.exists())

            repeated = migrate_legacy("claude", apply=True, environ=environment)
            self.assertEqual(repeated["lifecycle"]["status"], "already_migrated")
            self.assertEqual(repeated["logs"]["items"][0]["status"], "already_copied")
            self.assertFalse(repeated["unsafe"])

    def test_migrate_requires_manual_choice_for_specialist_persona(self):
        for persona in ("lamport", "carmack"):
            with self.subTest(persona=persona), tempfile.TemporaryDirectory() as raw:
                legacy = Path(raw) / ".claude" / "buddy"
                legacy.mkdir(parents=True)
                (legacy / "config.json").write_text(
                    json.dumps({"persona": persona}), encoding="utf-8"
                )

                result = migrate_legacy(
                    "claude",
                    apply=True,
                    environ={"HOME": raw, "USERPROFILE": raw},
                )

                self.assertTrue(result["manual_required"])
                self.assertEqual(result["lifecycle"]["status"], "manual_required")
                self.assertFalse(
                    (Path(raw) / ".masters-nudge" / "data" / "config.json").exists()
                )

    def test_migrate_converts_in_place_legacy_config_with_backup(self):
        with tempfile.TemporaryDirectory() as raw:
            config = Path(raw) / ".masters-nudge" / "data" / "config.json"
            self._write(config, {"persona": "linus"})

            result = migrate_legacy(
                "claude",
                apply=True,
                environ={"HOME": raw, "USERPROFILE": raw},
            )

            self.assertEqual(result["lifecycle"]["status"], "migrated")
            self.assertEqual(
                json.loads(config.read_text(encoding="utf-8")), {"stage": "review"}
            )
            backup = Path(result["lifecycle"]["backup"])
            self.assertTrue(backup.exists())
            self.assertEqual(
                json.loads(backup.read_text(encoding="utf-8")),
                {"persona": "linus"},
            )

    def test_migrate_refuses_noncanonical_destination_config(self):
        with tempfile.TemporaryDirectory() as raw:
            config = Path(raw) / ".masters-nudge" / "data" / "config.json"
            self._write(config, {"stage": "build", "extra": True})

            result = migrate_legacy(
                "claude",
                apply=True,
                environ={"HOME": raw, "USERPROFILE": raw},
            )

            self.assertTrue(result["unsafe"])
            self.assertEqual(result["lifecycle"]["status"], "conflict")
            self.assertEqual(
                json.loads(config.read_text(encoding="utf-8")),
                {"stage": "build", "extra": True},
            )

    def test_migrate_refuses_invalid_or_conflicting_log_without_overwrite(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            legacy = root / ".claude" / "buddy"
            destination = root / ".masters-nudge" / "data"
            legacy.mkdir(parents=True)
            destination.mkdir(parents=True)
            (legacy / "bad.log").write_text("not-json\n", encoding="utf-8")
            (legacy / "same.log").write_text('{"reaction":"old"}\n', encoding="utf-8")
            conflict = destination / "claude_code--same.log"
            conflict.write_text('{"reaction":"new"}\n', encoding="utf-8")

            result = migrate_legacy(
                "claude",
                apply=True,
                environ={"HOME": raw, "USERPROFILE": raw},
            )

            statuses = {
                item["source_name"]: item["status"] for item in result["logs"]["items"]
            }
            self.assertEqual(statuses, {"bad.log": "invalid", "same.log": "conflict"})
            self.assertTrue(result["unsafe"])
            self.assertEqual(
                conflict.read_text(encoding="utf-8"), '{"reaction":"new"}\n'
            )

    def test_migrate_reports_environment_alias_mappings_without_writing_profiles(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = {
                "HOME": raw,
                "USERPROFILE": raw,
                "BUDDY_PROVIDER": "ollama-local",
                "BUDDY_MODEL": "model-a",
                "BUDDY_CLAUDE_DIR": str(Path(raw) / "legacy-claude"),
            }

            result = migrate_legacy("claude", apply=True, environ=environment)

            mappings = {
                item["legacy"]: item["replacement"] for item in result["environment"]
            }
            self.assertEqual(mappings["BUDDY_PROVIDER"], "MASTERS_NUDGE_PROVIDER")
            self.assertEqual(mappings["BUDDY_MODEL"], "MASTERS_NUDGE_MODEL")
            self.assertEqual(mappings["BUDDY_CLAUDE_DIR"], "MASTERS_NUDGE_DATA_DIR")
            self.assertTrue(result["manual_required"])
            self.assertFalse((Path(raw) / ".profile").exists())

    def test_migrate_requires_a_stage_choice_for_legacy_persona_environment(self):
        with tempfile.TemporaryDirectory() as raw:
            result = migrate_legacy(
                "claude",
                environ={
                    "HOME": raw,
                    "USERPROFILE": raw,
                    "BUDDY_PERSONA": "linus",
                },
            )

        [mapping] = result["environment"]
        self.assertEqual(mapping["legacy"], "BUDDY_PERSONA")
        self.assertEqual(mapping["replacement"], "MASTERS_NUDGE_STAGE")
        self.assertIn("design|build|evolve|review", mapping["note"])
        self.assertTrue(result["manual_required"])

    def test_migrate_reports_removed_masters_nudge_persona_override(self):
        with tempfile.TemporaryDirectory() as raw:
            result = migrate_legacy(
                "claude",
                environ={
                    "HOME": raw,
                    "USERPROFILE": raw,
                    "MASTERS_NUDGE_PERSONA": "linus",
                },
            )

        [mapping] = result["environment"]
        self.assertEqual(mapping["legacy"], "MASTERS_NUDGE_PERSONA")
        self.assertEqual(mapping["replacement"], "MASTERS_NUDGE_STAGE")
        self.assertIn("design|build|evolve|review", mapping["note"])
        self.assertTrue(result["manual_required"])


class DoctorTests(unittest.TestCase):
    def test_doctor_requires_complete_runtime_dependency_inventory(self):
        with tempfile.TemporaryDirectory() as raw:
            import shutil

            plugin_root = Path(raw) / "masters-nudge"
            shutil.copytree(PLUGIN_ROOT, plugin_root)
            missing = plugin_root / "masters_nudge" / "codex_adapter.py"
            missing.unlink()
            environment = {
                "HOME": raw,
                "USERPROFILE": raw,
                "PATH": "",
                "CLAUDE_PLUGIN_OPTION_PYTHON_COMMAND": sys.executable,
            }
            with patch(
                "masters_nudge.management._provider_cli", return_value="fake-cli"
            ):
                result = doctor(plugin_root, "claude", environ=environment)

        self.assertFalse(result["core_ready"])
        self.assertIn("masters_nudge/codex_adapter.py", result["runtime"]["missing"])

    def test_doctor_ignores_a_shrunken_self_reported_inventory(self):
        with tempfile.TemporaryDirectory() as raw:
            import shutil

            plugin_root = Path(raw) / "masters-nudge"
            shutil.copytree(PLUGIN_ROOT, plugin_root)
            (plugin_root / ".masters-nudge-inventory.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "files": [".masters-nudge-inventory.json"],
                        "runtime_files": [".masters-nudge-inventory.json"],
                    }
                ),
                encoding="utf-8",
            )
            (plugin_root / "masters_nudge" / "codex_adapter.py").unlink()
            environment = {
                "HOME": raw,
                "USERPROFILE": raw,
                "PATH": "",
                "CLAUDE_PLUGIN_OPTION_PYTHON_COMMAND": sys.executable,
            }
            with patch(
                "masters_nudge.management._provider_cli", return_value="fake-cli"
            ):
                result = doctor(plugin_root, "claude", environ=environment)

        self.assertFalse(result["core_ready"])
        self.assertIn("masters_nudge/codex_adapter.py", result["runtime"]["missing"])

    def test_doctor_reports_unauthenticated_grok_as_not_ready(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = {
                "HOME": raw,
                "USERPROFILE": raw,
                "PATH": "",
                "MASTERS_NUDGE_PROVIDER": "grok",
                "CLAUDE_PLUGIN_OPTION_PYTHON_COMMAND": sys.executable,
            }
            with patch("masters_nudge.management._provider_cli", return_value="grok"):
                result = doctor(
                    PLUGIN_ROOT,
                    "claude",
                    environ=environment,
                    grok_inspector=lambda *_args, **_kwargs: {
                        "ready": False,
                        "authenticated": False,
                        "error": "grok CLI is not authenticated",
                    },
                )

        self.assertFalse(result["core_ready"])
        self.assertFalse(result["hosts"][0]["provider_ready"])
        self.assertFalse(result["hosts"][0]["grok"]["authenticated"])

    def test_doctor_reports_host_default_and_keeps_ui_optional(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = {
                "HOME": raw,
                "USERPROFILE": raw,
                "PATH": "",
                "CLAUDE_PLUGIN_OPTION_PYTHON_COMMAND": sys.executable,
            }
            with (
                patch(
                    "masters_nudge.management._provider_cli", return_value="fake-cli"
                ),
                patch("masters_nudge.management.importlib.util.find_spec") as find_spec,
            ):
                find_spec.side_effect = lambda name: None if name == "PIL" else object()
                result = doctor(PLUGIN_ROOT, "claude", environ=environment)

            self.assertTrue(result["core_ready"])
            self.assertFalse(result["ui"]["ready"])
            self.assertEqual(result["hosts"][0]["provider"], "anthropic")
            self.assertEqual(result["hosts"][0]["model"], "sonnet")

    def test_doctor_rejects_unknown_provider(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = {
                "HOME": raw,
                "USERPROFILE": raw,
                "PATH": "",
                "MASTERS_NUDGE_PROVIDER": "unknown",
            }
            result = doctor(PLUGIN_ROOT, "claude", environ=environment)

            self.assertFalse(result["core_ready"])
            self.assertFalse(result["hosts"][0]["provider_ready"])

    def test_doctor_reports_local_metadata_without_generating(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = {
                **LocalConfigurationTests._environment(raw),
                "PATH": "",
                "CLAUDE_PLUGIN_OPTION_PYTHON_COMMAND": sys.executable,
            }
            path = reviewer_config_path(Path(environment["MASTERS_NUDGE_DATA_DIR"]))
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "provider": "ollama-local",
                        "model": "user-model",
                        "ollama_url": "http://127.0.0.1:11434",
                    }
                ),
                encoding="utf-8",
            )
            calls = []

            def inspect(endpoint, model, **kwargs):
                calls.append((endpoint, model, kwargs))
                return LocalConfigurationTests._ready(endpoint, model)

            result = doctor(
                HERE,
                "all",
                environ=environment,
                local_inspector=inspect,
            )

            self.assertTrue(result["core_ready"])
            self.assertEqual(len(calls), 2)
            self.assertTrue(all(item["local"]["ready"] for item in result["hosts"]))
            self.assertTrue(all(item["provider_cli"] == "" for item in result["hosts"]))

    def test_doctor_handles_invalid_local_inspection_result(self):
        with tempfile.TemporaryDirectory() as raw:
            environment = {
                **LocalConfigurationTests._environment(raw),
                "MASTERS_NUDGE_PROVIDER": "ollama-local",
                "MASTERS_NUDGE_MODEL": "user-model",
                "CLAUDE_PLUGIN_OPTION_PYTHON_COMMAND": sys.executable,
            }

            result = doctor(
                HERE,
                "claude",
                environ=environment,
                local_inspector=lambda *_args, **_kwargs: None,
            )

            self.assertFalse(result["core_ready"])
            self.assertIn("invalid result", result["hosts"][0]["local"]["error"])

    def test_window_launch_error_is_reported(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "buddy_window.py").write_text("pass\n", encoding="utf-8")
            with (
                patch(
                    "masters_nudge.management.importlib.util.find_spec",
                    return_value=object(),
                ),
                patch(
                    "masters_nudge.management.subprocess.Popen",
                    side_effect=OSError("launch blocked"),
                ),
            ):
                result = launch_window(root)

            self.assertFalse(result["launched"])
            self.assertIn("launch blocked", result["missing"][0])

    def test_window_launch_passes_explicit_workspace_to_child(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "plugin"
            workspace = Path(raw) / "software-workspace"
            root.mkdir()
            workspace.mkdir()
            (root / "buddy_window.py").write_text("pass\n", encoding="utf-8")
            process = Mock(pid=123)
            with (
                patch(
                    "masters_nudge.management.importlib.util.find_spec",
                    return_value=object(),
                ),
                patch(
                    "masters_nudge.management.subprocess.Popen",
                    return_value=process,
                ) as popen,
            ):
                result = launch_window(root, workspace=workspace)

        self.assertTrue(result["launched"])
        self.assertEqual(result["workspace"], str(workspace.resolve()))
        self.assertEqual(
            popen.call_args.kwargs["env"]["MASTERS_NUDGE_WORKSPACE"],
            str(workspace.resolve()),
        )
        self.assertEqual(popen.call_args.kwargs["cwd"], str(workspace.resolve()))

    def test_window_cli_forwards_explicit_workspace(self):
        workspace = r"E:\projects\software-review-app"
        with (
            patch.object(
                sys,
                "argv",
                ["masters-nudge", "window", "--workspace", workspace, "--json"],
            ),
            patch.object(
                masters_nudge_cli,
                "launch_window",
                return_value={
                    "launched": True,
                    "pid": 123,
                    "missing": [],
                    "workspace": workspace,
                },
            ) as launch,
            redirect_stdout(io.StringIO()),
        ):
            result = masters_nudge_cli.main()

        self.assertEqual(result, 0)
        launch.assert_called_once_with(
            masters_nudge_cli.PLUGIN_ROOT,
            workspace=workspace,
        )

if __name__ == "__main__":
    unittest.main()
