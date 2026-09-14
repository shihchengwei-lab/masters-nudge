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

    def test_prompt_uses_results_as_scoped_behavioral_evidence(self):
        for prompt_path in (ROOT / "buddy-prompt.txt", PLUGIN / "buddy-prompt.txt"):
            with self.subTest(prompt_path=prompt_path):
                prompt = prompt_path.read_text(encoding="utf-8")
                normalized = " ".join(prompt.split())
                self.assertIn(
                    "structural relationships in code, data, responsibility, and control flow",
                    normalized,
                )
                self.assertIn(
                    "Each build, test, lint, and verification result covers only the "
                    "behavior it exercised.",
                    normalized,
                )

    def test_prompt_runs_an_operational_decision_trace(self):
        for prompt_path in (ROOT / "buddy-prompt.txt", PLUGIN / "buddy-prompt.txt"):
            with self.subTest(prompt_path=prompt_path):
                prompt = prompt_path.read_text(encoding="utf-8")
                normalized = " ".join(prompt.split())
                self.assertIn(
                    "Inspect the concrete engineering decision revealed by the bounded decision evidence",
                    normalized,
                )
                self.assertIn("current ordered observable tool-result batch", normalized)
                self.assertIn(
                    "native tool input and observable result",
                    normalized,
                )
                self.assertNotIn("related_source", normalized)
                self.assertNotIn("declaration candidates", normalized)
                self.assertIn(
                    "Trace changed state transitions and effects in execution order",
                    normalized,
                )
                self.assertIn(
                    "Track each returned promise or callback into the next action that depends on its completion",
                    normalized,
                )
                self.assertIn(
                    "An unconsumed completion signal marks an open causality gap",
                    normalized,
                )
                self.assertIn(
                    "Every finding surfaces one still-open structural decision",
                    normalized,
                )
                self.assertIn(
                    "Observed implementation choice → unmet runtime dependency → task-breaking behavior",
                    normalized,
                )
                self.assertIn(
                    "structural decision in code, data, responsibility, or control flow",
                    normalized,
                )
                self.assertIn(
                    "Use an observation when the visible evidence establishes every edge in that relationship",
                    normalized,
                )
                self.assertIn(
                    "Use a question when the visible evidence establishes an exact decision fork",
                    normalized,
                )
                self.assertIn("visible tool-result record", normalized)
                self.assertIn("completion, ownership, and ordering", normalized)
                self.assertIn(
                    "Recent returned Nudges are exclusions, not evidence",
                    normalized,
                )
                self.assertIn(
                    "Ground the choice and every claimed consequence in the current packet",
                    normalized,
                )
                self.assertIn(
                    "When multiple current-packet consequences depend on one visible state, owner, or control path",
                    normalized,
                )
                self.assertIn(
                    "A visible name, call, literal, or branch establishes only what happens after entry",
                    normalized,
                )
                self.assertIn(
                    "Reachability requires a visible producer or caller and path to the anchor",
                    normalized,
                )
                self.assertIn(
                    "The current packet must establish every edge in this relationship",
                    normalized,
                )
                self.assertIn(
                    "When the relevant caller or path is absent, ask whether the task-relevant value can reach the anchor",
                    normalized,
                )
                self.assertIn(
                    "Keep every question premise to visible facts",
                    normalized,
                )
                self.assertIn("the Actor owns the remedy", normalized)
                self.assertNotIn(
                    "different dependency or downstream consequence remains eligible",
                    normalized,
                )

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
