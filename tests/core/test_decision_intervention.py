"""A Provider can return one observation without gaining workspace access."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from masters_nudge.core import NudgeCore
from masters_nudge.providers import call_codex_result
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


ROOT = Path(__file__).resolve().parents[2]


class ProviderBoundaryTests(unittest.TestCase):
    def test_core_sends_only_prompt_and_observation(self):
        with tempfile.TemporaryDirectory() as raw:
            captured = {}
            settings = RuntimeSettings(
                "openai",
                "test-model",
                RuntimePaths(ROOT, Path(raw), Path(raw), Path(raw) / "error.log"),
            )

            def dispatch(*args, **kwargs):
                captured["args"] = args
                captured["kwargs"] = kwargs
                return {
                    "nudge": {
                        "message": "同一事實有兩個 owner。",
                        "evidence": ["+parallel_owner = True"],
                    }
                }

            nudge = NudgeCore(settings, dispatch=dispatch).nudge_once(
                "[task]\nKeep one owner\n[end task]\n\n"
                "[change]\n+parallel_owner = True\n[end change]"
            )

        self.assertEqual(nudge.message, "同一事實有兩個 owner。")
        self.assertEqual(nudge.evidence, ("+parallel_owner = True",))
        self.assertEqual(len(captured["args"]), 4)
        self.assertNotIn("workspace_root", captured["kwargs"])

    def test_codex_provider_runs_without_actor_workspace_or_repo_tools(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            schema = root / "schema.json"
            schema.write_text('{"type":"object"}', encoding="utf-8")

            def fake_run(command, **kwargs):
                Path(command[command.index("-o") + 1]).write_text(
                    '{"nudge":null}', encoding="utf-8"
                )
                self.assertNotEqual(kwargs["cwd"], str(root))
                self.assertEqual(
                    [path.name for path in Path(kwargs["cwd"]).iterdir()],
                    ["output.json"],
                )
                return subprocess.CompletedProcess([], 0, "", "")

            with mock.patch(
                "masters_nudge.providers._run_cli_process", side_effect=fake_run
            ) as run:
                result = call_codex_result(
                    "prompt",
                    "observation",
                    "model",
                    schema_path=schema,
                    timeout_sec=10,
                    codex_bin_resolver=lambda: "codex.exe",
                )

        self.assertIsNone(result["nudge"])
        command = run.call_args.args[0]
        self.assertIn("features.shell_tool=false", command)
        self.assertIn("project_doc_max_bytes=0", command)
        self.assertFalse(any("readrepo" in part for part in command))

    def test_codex_provider_recovers_complete_json_event(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            schema = root / "schema.json"
            schema.write_text('{"type":"object"}', encoding="utf-8")
            clean = {
                "nudge": {
                    "message": "同一事實有兩個 owner。",
                    "evidence": ["+parallel_owner = True"],
                }
            }
            event = json.dumps(
                {
                    "type": "item.completed",
                    "item": {
                        "type": "agent_message",
                        "text": json.dumps(clean, ensure_ascii=False),
                    },
                },
                ensure_ascii=False,
            )

            def fake_run(command, **kwargs):
                Path(command[command.index("-o") + 1]).write_text(
                    '{"nudge":null}', encoding="utf-8"
                )
                return subprocess.CompletedProcess([], 0, event + "\n", "")

            with mock.patch(
                "masters_nudge.providers._run_cli_process", side_effect=fake_run
            ):
                result = call_codex_result(
                    "prompt",
                    "observation",
                    "model",
                    schema_path=schema,
                    timeout_sec=10,
                    codex_bin_resolver=lambda: "codex.exe",
                )

        self.assertEqual(result["nudge"], clean["nudge"])


if __name__ == "__main__":
    unittest.main()
