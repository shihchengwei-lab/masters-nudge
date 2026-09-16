"""The checked-in plugin must be complete and start outside the source tree."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from masters_nudge.plugin_inventory import package_files
from tools.build_plugin import check_plugin


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugins" / "masters-nudge"


class PackageTests(unittest.TestCase):
    def test_readmes_describe_task_and_completed_change(self):
        for readme_path, expected in (
            (ROOT / "README.md", "task and the completed change"),
            (ROOT / "README.zh-TW.md", "任務與剛完成的修改"),
        ):
            with self.subTest(readme_path=readme_path):
                normalized = " ".join(
                    readme_path.read_text(encoding="utf-8").split()
                ).lower()
                self.assertIn(expected, normalized)
                self.assertNotIn("taste_nudge", normalized)
                self.assertNotIn("contract_warning", normalized)

    def test_inventory_matches_the_checked_in_plugin(self):
        declared = set(package_files())
        actual = {
            path.relative_to(PLUGIN).as_posix()
            for path in PLUGIN.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        }

        self.assertEqual(actual, declared)
        self.assertEqual(check_plugin(), [])

    def test_package_has_only_the_supported_surface(self):
        paths = set(package_files())
        forbidden = {
            "buddy_window.py",
            "spritesheet.webp",
            "claude_stop.py",
            "review_telemetry.py",
            "skills/migrate/SKILL.md",
            "skills/setup-local/SKILL.md",
            "skills/window/SKILL.md",
        }
        required = {
            "skills/doctor/SKILL.md",
            "skills/select-provider/SKILL.md",
            "skills/recent-nudges/SKILL.md",
        }
        removed = {
            "lens_router.py",
            "masters_nudge/lenses.py",
            "route-schema.json",
            "skills/select-lens/SKILL.md",
            "personas/linus.txt",
            "personas/lamport.txt",
            "personas/carmack.txt",
            "masters_nudge/read_only_repo_mcp.py",
        }

        self.assertFalse(paths & forbidden)
        self.assertFalse(paths & removed)
        self.assertTrue(required <= paths)
        self.assertFalse({path for path in paths if path.startswith("personas/")})

    def test_hook_manifests_have_no_stop_hook(self):
        claude = json.loads((PLUGIN / "hooks" / "claude.json").read_text(encoding="utf-8"))["hooks"]
        codex = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]

        self.assertEqual(set(claude), {"UserPromptSubmit", "PostToolBatch"})
        self.assertEqual(set(codex), {"UserPromptSubmit", "PostToolBatch"})

    def test_codex_manifest_exposes_no_lens_selection(self):
        manifest = json.loads(
            (PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        interface = manifest["interface"]
        visible_text = " ".join(
            [interface["longDescription"], *interface["defaultPrompt"]]
        ).lower()

        self.assertNotIn("lens", visible_text)

    def test_packaged_runtime_uses_nudge_not_review_contract_names(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in PLUGIN.rglob("*.py")
        )

        for obsolete in (
            "ReviewRequest",
            "ReviewOutcome",
            "ReviewCore",
            "review_once",
            "review_telemetry",
            "reviewer_config",
        ):
            self.assertNotIn(obsolete, text)

    def test_prompt_uses_only_task_and_completed_change(self):
        for prompt_path in (ROOT / "buddy-prompt.txt", PLUGIN / "buddy-prompt.txt"):
            with self.subTest(prompt_path=prompt_path):
                prompt = prompt_path.read_text(encoding="utf-8")
                normalized = " ".join(prompt.split())
                self.assertIn("the user's task", normalized)
                self.assertIn("the completed change that just happened", normalized)
                self.assertIn("Actor has just changed the program", normalized)
                self.assertIn("still owns every implementation decision", normalized)
                self.assertNotIn("workspace state", normalized.lower())
                self.assertNotIn("read-only tools", normalized.lower())
                self.assertNotIn("# REASONING MODELS", prompt)

    def test_clean_copy_starts_both_prompt_hooks(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            copied = root / "plugin"
            data = root / "data"
            shutil.copytree(PLUGIN, copied)
            environment = {
                **os.environ,
                "MASTERS_NUDGE_DATA_DIR": str(data),
                "PYTHONPATH": "",
            }
            cases = (
                (
                    copied / "hook_entry.py",
                    ["--host", "codex_cli"],
                    {
                        "hook_event_name": "UserPromptSubmit",
                        "session_id": "package-codex",
                        "cwd": raw,
                        "prompt": "record task",
                    },
                ),
                (
                    copied / "claude_prompt.py",
                    [],
                    {
                        "hook_event_name": "UserPromptSubmit",
                        "session_id": "package-claude",
                        "cwd": raw,
                        "prompt": "record task",
                    },
                ),
            )
            for script, arguments, payload in cases:
                with self.subTest(script=script.name):
                    completed = subprocess.run(
                        [sys.executable, str(script), *arguments],
                        input=json.dumps(payload),
                        text=True,
                        capture_output=True,
                        cwd=root,
                        env=environment,
                        timeout=20,
                        check=False,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)

            states = [
                json.loads(path.read_text(encoding="utf-8"))
                for path in data.glob("*.turn.json")
            ]
            self.assertEqual(
                {
                    (state["host"], state["session_id"], state["task_anchor"])
                    for state in states
                },
                {
                    ("codex_cli", "package-codex", "record task"),
                    ("claude_code", "package-claude", "record task"),
                },
            )


if __name__ == "__main__":
    unittest.main()
