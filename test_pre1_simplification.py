from __future__ import annotations

import ast
import inspect
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import review_telemetry
from masters_nudge import plugin_inventory
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


class PreOneSimplificationTests(unittest.TestCase):
    def settings(self, root: Path) -> RuntimeSettings:
        paths = RuntimePaths(
            runtime_dir=root / "runtime",
            data_dir=root / "data",
            error_log=root / "data" / "error.log",
        )
        return RuntimeSettings("openai", "current-model", 120, 90, paths)

    def test_core_never_routes_active_reads_to_legacy_data(self):
        from masters_nudge.core import ReviewCore

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            settings = self.settings(root)
            legacy_data_dir = root / ".claude" / "buddy"
            legacy_data_dir.mkdir(parents=True)
            (legacy_data_dir / "config.json").write_text(
                '{"persona": "linus"}\n', encoding="utf-8"
            )

            self.assertEqual(settings.paths.data_dir, ReviewCore(settings)._route_dir())

    def test_runtime_ignores_buddy_reviewer_aliases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            environment = {
                "MASTERS_NUDGE_DATA_DIR": str(root / "data"),
                "BUDDY_PROVIDER": "grok",
                "BUDDY_MODEL": "legacy",
            }
            settings = RuntimeSettings.from_env(root / "runtime", environ=environment)

            self.assertEqual("openai", settings.provider)
            self.assertNotEqual("legacy", settings.model)
            self.assertEqual("host_default", settings.configuration_source)

    def test_shadow_thresholds_ignore_buddy_aliases(self):
        with mock.patch.dict(
            review_telemetry.os.environ,
            {
                "BUDDY_SHADOW_EVALUATION_DAYS": "99",
                "BUDDY_SHADOW_TARGET_CALLS": "999",
            },
            clear=True,
        ):
            self.assertEqual(
                review_telemetry.DEFAULT_EVALUATION_DAYS,
                review_telemetry.configured_evaluation_days(),
            )
            self.assertEqual(
                review_telemetry.DEFAULT_TARGET_CALLS,
                review_telemetry.configured_target_calls(),
            )

    def test_window_workspace_ignores_buddy_alias(self):
        import buddy_window

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            current = root / "current"
            legacy = root / "legacy"
            current.mkdir()
            legacy.mkdir()

            self.assertEqual(
                buddy_window.normalize_workspace(current),
                buddy_window.resolve_window_workspace(
                    environ={"BUDDY_WORKSPACE": str(legacy)}, cwd=current
                ),
            )

    def test_codex_entry_uses_shared_error_logger(self):
        import hook_entry

        with tempfile.TemporaryDirectory() as temp_dir:
            settings = self.settings(Path(temp_dir))
            with mock.patch.object(hook_entry.storage, "append_error") as append:
                hook_entry._log_error(settings, "failed")

            append.assert_called_once_with(
                settings.paths.error_log, "codex-hook", "failed"
            )

    def test_plugin_inventory_contains_only_the_software_runtime(self):
        inventory = set(plugin_inventory.SOURCE_RUNTIME_FILES)

        self.assertNotIn("shader_progress.py", inventory)
        self.assertNotIn("shader_router.py", inventory)
        self.assertNotIn("masters_nudge/profiles.py", inventory)
        self.assertFalse(
            any(path.startswith("domains/shader/") for path in inventory),
            sorted(path for path in inventory if path.startswith("domains/shader/")),
        )

    def test_cli_help_does_not_offer_a_shader_command(self):
        import masters_nudge_cli

        output = io.StringIO()
        with (
            mock.patch.object(sys, "argv", ["masters-nudge", "--help"]),
            redirect_stdout(output),
            self.assertRaises(SystemExit) as stopped,
        ):
            masters_nudge_cli.main()

        self.assertEqual(0, stopped.exception.code)
        self.assertNotIn("shader", output.getvalue().lower())

    def test_window_selector_is_software_lifecycle_only(self):
        import buddy_window

        self.assertEqual(
            [
                "Design · Jeff Dean（系統因果與成本）",
                "Build · Kent Beck（小步驟與測試）",
                "Evolve · Martin Fowler（重構與變更成本）",
                "Review · Linus Torvalds（簡化與責任歸屬）",
            ],
            buddy_window.selector_options(),
        )
        self.assertNotIn(
            "domain", inspect.signature(buddy_window.selector_options).parameters
        )
        self.assertFalse(hasattr(buddy_window, "SHADER_SELECTOR_LENSES"))

    def test_active_runtime_does_not_import_shader_modules(self):
        root = Path(__file__).resolve().parent
        runtime_paths = [
            root / "buddy_window.py",
            root / "masters_nudge_cli.py",
            root / "source_context.py",
            *sorted((root / "masters_nudge").glob("*.py")),
        ]
        forbidden: list[str] = []
        for path in runtime_paths:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                if any(
                    name.split(".", 1)[0] in {"shader_progress", "shader_router"}
                    for name in names
                ):
                    forbidden.append(str(path.relative_to(root)))

        self.assertEqual([], sorted(set(forbidden)))


if __name__ == "__main__":
    unittest.main()
