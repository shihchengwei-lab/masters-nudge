from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import review_telemetry
import hook_entry
from masters_nudge.core import ReviewCore
from masters_nudge.profiles import WorkspaceProfile, resolve_reviewer
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
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            settings = self.settings(root)
            legacy_data_dir = root / ".claude" / "buddy"
            legacy_data_dir.mkdir(parents=True)
            (legacy_data_dir / "config.json").write_text(
                '{"persona": "linus"}\n', encoding="utf-8"
            )

            self.assertEqual(settings.paths.data_dir, ReviewCore(settings)._route_dir())

    def test_workspace_profile_ignores_buddy_reviewer_aliases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = self.settings(Path(temp_dir))
            profile = WorkspaceProfile(
                provider="anthropic",
                model="profile-model",
                workspace="C:/repo",
                source="workspace_profile",
            )

            self.assertEqual(
                ("anthropic", "profile-model", "workspace_profile"),
                resolve_reviewer(
                    settings,
                    profile,
                    environ={"BUDDY_PROVIDER": "grok", "BUDDY_MODEL": "legacy"},
                ),
            )

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
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = self.settings(Path(temp_dir))
            with mock.patch.object(hook_entry.storage, "append_error") as append:
                hook_entry._log_error(settings, "failed")

            append.assert_called_once_with(
                settings.paths.error_log, "codex-hook", "failed"
            )


if __name__ == "__main__":
    unittest.main()
