"""One workspace snapshot receives one bounded Provider judgment."""

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
            "openai", "test-model", RuntimePaths(ROOT, data_dir, data_dir, data_dir / "error.log")
        )

    def test_one_snapshot_causes_one_provider_call(self):
        with tempfile.TemporaryDirectory() as raw:
            calls = []

            def dispatch(_provider, prompt, snapshot, _model, **kwargs):
                calls.append((prompt, snapshot, kwargs))
                return {
                    "decision": "intervene",
                    "current_choice": "新增第二個 owner",
                    "structural_cost": "責任可能分歧",
                    "direction": "沿用既有 owner",
                    "evidence": ["src/state.ts:owner"],
                }

            outcome = NudgeCore(
                self.settings(Path(raw)), dispatch=dispatch
            ).nudge_once("WORKSPACE-SNAPSHOT", workspace_root=raw)

        self.assertEqual(outcome.decision, "intervene")
        self.assertEqual(outcome.direction, "沿用既有 owner")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], "WORKSPACE-SNAPSHOT")
        self.assertEqual(calls[0][2]["workspace_root"], raw)

    def test_pass_is_silent_data(self):
        parsed = parse_nudge_result(
            json.dumps(
                {
                    "decision": "pass",
                    "current_choice": "",
                    "structural_cost": "",
                    "direction": "",
                    "evidence": [],
                }
            )
        )
        self.assertEqual(parsed["decision"], "pass")

    def test_delivery_keeps_provider_advisory_and_actor_ownership(self):
        rendered = delivery_text(
            "新增第二個 owner",
            "責任可能分歧",
            "沿用既有 owner",
            ("src/state.ts:owner",),
        )
        self.assertIn("供參考", rendered)
        self.assertIn("方向：沿用既有 owner", rendered)
        self.assertIn("Actor 負責驗證與實作", rendered)

    def test_prompt_uses_workspace_facts_and_allows_direction(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")
        normalized = " ".join(prompt.split())
        self.assertIn("workspace state at task start", normalized)
        self.assertIn("current cumulative workspace state", normalized)
        self.assertIn("Actor's prose, proposed remedy, and confidence are not evidence", normalized)
        self.assertIn("propose a better responsibility boundary or existing seam", normalized)
        self.assertIn("Actor alone owns implementation and verification", normalized)
        self.assertNotIn("visible responsibility overlap", normalized.lower())
        self.assertNotIn("contract_warning", normalized)
        self.assertNotIn("taste_nudge", normalized)

    def test_schema_is_only_pass_or_intervene(self):
        schema = json.loads((ROOT / "nudge-schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["decision"]["enum"], ["intervene", "pass"])
        self.assertEqual(
            schema["required"],
            ["decision", "current_choice", "structural_cost", "direction", "evidence"],
        )


if __name__ == "__main__":
    unittest.main()
