"""One evidence packet receives one Provider judgment."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from masters_nudge.core import NudgeCore
from masters_nudge.provider_contract import parse_nudge_result
from masters_nudge import prompting
from masters_nudge.prompting import delivery_text
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


ROOT = Path(__file__).resolve().parents[2]


class SingleProviderTests(unittest.TestCase):
    def settings(self, data_dir: Path) -> RuntimeSettings:
        return RuntimeSettings(
            "openai",
            "test-model",
            RuntimePaths(ROOT, data_dir, data_dir, data_dir / "error.log"),
        )

    def test_one_packet_causes_one_provider_call(self):
        with tempfile.TemporaryDirectory() as raw:
            calls = []

            def dispatch(_provider, prompt, packet, _model, **kwargs):
                calls.append((prompt, packet, kwargs["timeout_sec"]))
                return {
                    "status": "finding",
                    "principle": "causality",
                    "anchor": "batch owner",
                    "relationship": "讓批次只有一個擁有者，避免重試重複移除。",
                }

            outcome = NudgeCore(
                self.settings(Path(raw)), dispatch=dispatch
            ).nudge_once("EVIDENCE-PACKET")

        self.assertEqual(outcome.status, "finding")
        self.assertEqual(outcome.principle, "causality")
        self.assertEqual(outcome.anchor, "batch owner")
        self.assertEqual(
            outcome.relationship,
            "讓批次只有一個擁有者，避免重試重複移除。",
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], "EVIDENCE-PACKET")
        self.assertEqual(calls[0][2], 90)

    def test_no_finding_hint_comes_from_the_local_example_library(self):
        expected = (
            "資料結構能排除不可能的狀態，就不必讓每條路徑重複防守。",
            "旗標組合越多，資料模型容許的矛盾狀態通常也越多。",
            "事件是已發生的事實；狀態應沿單一方向由事件推導。",
            "許多時序問題源自缺少唯一的因果順序，而非缺少重試。",
            "好的抽象讓人能局部推理，不必在腦中執行整個系統。",
            "依賴與副作用越隱晦，所謂彈性越容易變成不可預測。",
        )
        first = prompting.no_finding_hint("same evidence packet")
        second = prompting.no_finding_hint("same evidence packet")

        self.assertEqual(prompting.CODE_TASTE_HINTS, expected)
        self.assertEqual(first, second)
        self.assertIn(first.removeprefix("hint: "), prompting.CODE_TASTE_HINTS)
        self.assertTrue(first.startswith("hint: "))

    def test_provider_prompt_carries_only_the_three_structural_principles(self):
        with tempfile.TemporaryDirectory() as raw:
            prompts = []

            def dispatch(_provider, prompt, _packet, _model, **_kwargs):
                prompts.append(prompt)
                return {
                    "status": "no_finding",
                    "principle": "none",
                    "anchor": "",
                    "relationship": "",
                }

            outcome = NudgeCore(
                self.settings(Path(raw)), dispatch=dispatch
            ).nudge_once("packet")

        self.assertEqual(outcome.status, "no_finding")
        self.assertEqual(len(prompts), 1)
        normalized = " ".join(prompts[0].split())
        self.assertIn("every constructible value satisfies the required invariants", normalized)
        self.assertIn("one explicit direction and owner", normalized)
        self.assertIn("local reasoning", normalized)
        self.assertNotIn("Epistemic correctness and feedback distance", normalized)
        self.assertNotIn("Measured execution cost", normalized)
        self.assertNotIn("Knowledge ownership and change locality", normalized)
        self.assertNotIn("SELECTED LENS", normalized)

    def test_prompt_maps_each_principle_to_one_word_and_fixes_warning(self):
        with tempfile.TemporaryDirectory() as raw:
            prompts = []

            def dispatch(_provider, prompt, _packet, _model, **_kwargs):
                prompts.append(prompt)
                return {
                    "status": "no_finding",
                    "principle": "none",
                    "anchor": "",
                    "relationship": "",
                }

            NudgeCore(self.settings(Path(raw)), dispatch=dispatch).nudge_once("packet")

        self.assertIn("validity", prompts[0])
        self.assertIn("causality", prompts[0])
        self.assertIn("predictability", prompts[0])
        self.assertIn("`principle warning: anchor — relationship`", prompts[0])
        self.assertNotIn("attention cue: `alert`", prompts[0])
        self.assertNotIn("attention cue: `risk`", prompts[0])
        self.assertIn("required invariants", prompts[0])
        self.assertIn("required ordering and completion", prompts[0])
        self.assertIn("predictability", prompts[0])

    def test_provider_grounds_inference_in_the_visible_boundaries(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")
        normalized = " ".join(prompt.split())

        self.assertIn("Ground every observation in these visible boundaries", normalized)
        self.assertIn("Use inference to connect visible facts", normalized)

    def test_provider_inspects_the_current_decision_from_clean_boundaries(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")
        normalized = " ".join(prompt.split())

        self.assertIn("task beginning", normalized)
        self.assertIn("ordered observable tool-result batch", normalized)
        self.assertIn("bounded decision evidence", normalized)
        self.assertIn("related_source", normalized)
        self.assertIn("source-link records for direct calls and multi-hop owners", normalized)
        self.assertIn("unresolved and omitted references remain explicit", normalized)
        self.assertIn("Inspect the concrete engineering decision", normalized)
        self.assertIn("task's behavioral requirements", normalized)
        self.assertIn("Identify the implementation choice", normalized)

    def test_provider_deduplicates_only_the_same_engineering_relationship(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")
        normalized = " ".join(prompt.split()).lower()

        self.assertIn("deduplication references", normalized)
        self.assertIn("same engineering relationship", normalized)
        self.assertIn("different dependency or downstream consequence remains eligible", normalized)

    def test_prompt_uses_positive_operational_instructions(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")

        for defensive_phrase in (
            "not a reviewer",
            "outside your role",
            "Do not",
            "Never",
            "not a submission to grade",
            "strongest non-obvious",
        ):
            with self.subTest(defensive_phrase=defensive_phrase):
                self.assertNotIn(defensive_phrase, prompt)

    def test_finding_rejects_an_unknown_principle(self):
        with tempfile.TemporaryDirectory() as raw:
            def dispatch(_provider, _prompt, _packet, _model, **_kwargs):
                return {
                    "status": "finding",
                    "principle": "reliability",
                    "anchor": "batch owner",
                    "relationship": "讓批次只有一個擁有者，避免重試重複移除。",
                }

            outcome = NudgeCore(
                self.settings(Path(raw)), dispatch=dispatch
            ).nudge_once("packet")

        self.assertEqual(outcome.status, "error")

    def test_delivery_uses_principle_plus_fixed_warning(self):
        self.assertEqual(
            delivery_text("validity", "flags", "布林旗標可形成矛盾狀態。"),
            "validity warning: flags — 布林旗標可形成矛盾狀態。",
        )
        self.assertNotIn(
            "獨立第二意見",
            delivery_text("predictability", "side effect", "副作用不明確。"),
        )

    def test_anchor_and_relationship_have_distinct_ownership(self):
        relationship = (
            "舊回呼清空新計時器狀態，使取消控制失去唯一擁有者；"
            "後續排程再依錯誤狀態決定是否送出，讓事件結果取決於回呼先後。"
        )
        self.assertGreater(len(relationship), 52)
        with tempfile.TemporaryDirectory() as raw:
            def dispatch(_provider, _prompt, _packet, _model, **_kwargs):
                return {
                    "status": "finding",
                    "principle": "predictability",
                    "anchor": "_autoFlushTimer",
                    "relationship": relationship,
                }

            outcome = NudgeCore(
                self.settings(Path(raw)), dispatch=dispatch
            ).nudge_once("packet")

        self.assertEqual(outcome.status, "finding")
        self.assertEqual(outcome.anchor, "_autoFlushTimer")
        self.assertEqual(outcome.relationship, relationship)
        self.assertEqual(
            delivery_text(
                outcome.principle,
                outcome.anchor,
                outcome.relationship,
            ),
            f"predictability warning: _autoFlushTimer — {relationship}",
        )

    def test_provider_contract_rejects_a_rendered_prefix_inside_the_relationship(self):
        result = parse_nudge_result(
            json.dumps(
                {
                    "status": "finding",
                    "principle": "causality",
                    "anchor": "batch owner",
                    "relationship": "causality warning: 重複前綴",
                }
            )
        )

        self.assertEqual(result["status"], "error")

    def test_prompt_and_schema_require_one_grounded_open_gap(self):
        with tempfile.TemporaryDirectory() as raw:
            prompts = []

            def dispatch(_provider, prompt, _packet, _model, **_kwargs):
                prompts.append(prompt)
                return {
                    "status": "no_finding",
                    "principle": "none",
                    "anchor": "",
                    "relationship": "",
                }

            NudgeCore(self.settings(Path(raw)), dispatch=dispatch).nudge_once("packet")

        normalized = " ".join(prompts[0].split())
        self.assertIn("Before answering, follow this sequence", normalized)
        self.assertIn("Every finding names one still-open structural gap", normalized)
        self.assertIn(
            "Observed implementation choice → unmet runtime dependency → task-breaking behavior",
            normalized,
        )
        self.assertIn(
            "Findings describe runtime gaps in code, data, responsibility, or control flow",
            normalized,
        )
        self.assertIn(
            "A successful verification-only batch returns `no_finding`",
            normalized,
        )
        self.assertIn("Trace changed state transitions and effects in execution order", normalized)
        self.assertIn(
            "Track each returned promise or callback into the next action that depends on its completion",
            normalized,
        )
        self.assertIn(
            "An unconsumed completion signal marks an open causality gap",
            normalized,
        )
        self.assertIn("completion, ownership, and ordering", normalized)
        self.assertIn("covers only the behavior it exercised", normalized)
        self.assertIn("could change the next engineering decision", normalized)

        schema = json.loads((ROOT / "nudge-schema.json").read_text(encoding="utf-8"))
        anchor_description = schema["properties"]["anchor"]["description"]
        description = schema["properties"]["relationship"]["description"]
        self.assertIn("still-open, packet-grounded", description)
        self.assertIn("task-breaking runtime behavior", description)
        self.assertIn("engineering edge", description)
        self.assertIn("smallest exact implementation location", anchor_description.lower())
        self.assertNotIn("maxLength", schema["properties"]["anchor"])
        self.assertNotIn("maxLength", schema["properties"]["relationship"])
        self.assertIn("smallest exact implementation location", prompts[0])
        self.assertIn("one short Traditional Chinese declarative sentence", prompts[0])
        self.assertIn("one engineering edge", normalized)
        self.assertNotIn("characters", prompts[0])
        self.assertEqual(
            schema["properties"]["principle"]["enum"],
            ["validity", "causality", "predictability", "none"],
        )
        self.assertEqual(
            schema["required"],
            ["status", "principle", "anchor", "relationship"],
        )


if __name__ == "__main__":
    unittest.main()
