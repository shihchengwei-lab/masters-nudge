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
            "skills/select-lens/SKILL.md",
            "skills/select-provider/SKILL.md",
            "skills/recent-nudges/SKILL.md",
        }

        self.assertFalse(paths & forbidden)
        self.assertTrue(required <= paths)
        self.assertEqual(
            {path for path in paths if path.startswith("personas/")},
            {
                "personas/linus.txt",
                "personas/lamport.txt",
                "personas/carmack.txt",
            },
        )

    def test_hook_manifests_have_no_stop_hook(self):
        claude = json.loads((PLUGIN / "hooks" / "claude.json").read_text(encoding="utf-8"))["hooks"]
        codex = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]

        self.assertEqual(set(claude), {"UserPromptSubmit", "PostToolBatch"})
        self.assertEqual(set(codex), {"UserPromptSubmit", "PostToolUse"})

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
