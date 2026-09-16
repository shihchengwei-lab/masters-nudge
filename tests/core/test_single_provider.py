"""One completed change receives at most one Provider Nudge."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from masters_nudge.core import NudgeCore
from masters_nudge.prompting import delivery_text
from masters_nudge.provider_contract import parse_nudge_result
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


ROOT = Path(__file__).resolve().parents[2]


class SingleProviderTests(unittest.TestCase):
    def settings(self, data_dir: Path) -> RuntimeSettings:
        return RuntimeSettings(
            "openai",
            "test-model",
            RuntimePaths(ROOT, data_dir, data_dir, data_dir / "error.log"),
        )

    def test_one_observation_causes_one_provider_call(self):
        with tempfile.TemporaryDirectory() as raw:
            calls = []

            def dispatch(_provider, prompt, observation, _model, **kwargs):
                calls.append((prompt, observation, kwargs))
                return {
                    "nudge": {
                        "message": "兩個欄位表示同一個傳送狀態。",
                        "evidence": ["isSent", "isMarkedAsSent"],
                    }
                }

            nudge = NudgeCore(
                self.settings(Path(raw)), dispatch=dispatch
            ).nudge_once("TASK-AND-CHANGE")

        self.assertEqual(nudge.message, "兩個欄位表示同一個傳送狀態。")
        self.assertEqual(nudge.evidence, ("isSent", "isMarkedAsSent"))
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], "TASK-AND-CHANGE")
        self.assertNotIn("workspace_root", calls[0][2])

    def test_null_is_no_runtime_nudge(self):
        with tempfile.TemporaryDirectory() as raw:
            core = NudgeCore(
                self.settings(Path(raw)),
                dispatch=lambda *_args, **_kwargs: {"nudge": None},
            )
            self.assertIsNone(core.nudge_once("TASK-AND-CHANGE"))

        parsed = parse_nudge_result(json.dumps({"nudge": None}))
        self.assertIsNone(parsed["nudge"])

    def test_delivery_is_one_observation_not_an_instruction(self):
        rendered = delivery_text(
            "兩個欄位表示同一個傳送狀態。",
            ("isSent", "isMarkedAsSent"),
        )
        self.assertIn("Nudge：", rendered)
        self.assertIn("證據：", rendered)
        self.assertIn("Actor 自行決定、實作與驗證", rendered)
        self.assertNotIn("reframe", rendered.lower())
        self.assertNotIn("invariant", rendered.lower())

    def test_prompt_and_schema_expose_only_optional_nudge(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")
        normalized = " ".join(prompt.split())
        self.assertIn("the user's task", normalized)
        self.assertIn("the completed change that just happened", normalized)
        self.assertIn("Actor has just changed the program", normalized)
        self.assertIn("still owns every implementation decision", normalized)
        self.assertNotIn("workspace state", normalized.lower())
        self.assertNotIn("read-only tools", normalized.lower())
        self.assertNotIn("# REASONING MODELS", prompt)

        schema = json.loads((ROOT / "nudge-schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["required"], ["nudge"])
        self.assertEqual(set(schema["properties"]), {"nudge"})


if __name__ == "__main__":
    unittest.main()
