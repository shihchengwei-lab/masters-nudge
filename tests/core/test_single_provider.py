"""One evidence packet receives one Provider judgment."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from masters_nudge.core import NudgeCore
from masters_nudge.provider_contract import parse_nudge_result
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
                    "evidence_seq": 1,
                    "anchor": "batch owner",
                    "relationship": "讓批次只有一個擁有者，避免重試重複移除。",
                }

            outcome = NudgeCore(
                self.settings(Path(raw)), dispatch=dispatch
            ).nudge_once("EVIDENCE-PACKET")

        self.assertEqual(outcome.status, "finding")
        self.assertEqual(outcome.principle, "causality")
        self.assertEqual(outcome.evidence_seq, 1)
        self.assertEqual(outcome.anchor, "batch owner")
        self.assertEqual(
            outcome.relationship,
            "讓批次只有一個擁有者，避免重試重複移除。",
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], "EVIDENCE-PACKET")
        self.assertEqual(calls[0][2], 90)

    def test_provider_prompt_carries_only_the_three_structural_principles(self):
        with tempfile.TemporaryDirectory() as raw:
            prompts = []

            def dispatch(_provider, prompt, _packet, _model, **_kwargs):
                prompts.append(prompt)
                return {
                    "status": "no_finding",
                    "principle": "none",
                    "evidence_seq": 0,
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

    def test_prompt_maps_each_principle_to_one_word_and_fixes_neutral_nudge(self):
        with tempfile.TemporaryDirectory() as raw:
            prompts = []

            def dispatch(_provider, prompt, _packet, _model, **_kwargs):
                prompts.append(prompt)
                return {
                    "status": "no_finding",
                    "principle": "none",
                    "evidence_seq": 0,
                    "anchor": "",
                    "relationship": "",
                }

            NudgeCore(self.settings(Path(raw)), dispatch=dispatch).nudge_once("packet")

        self.assertIn("validity", prompts[0])
        self.assertIn("causality", prompts[0])
        self.assertIn("predictability", prompts[0])
        self.assertIn("`principle nudge: anchor — relationship`", prompts[0])
        self.assertNotIn("attention cue: `alert`", prompts[0])
        self.assertNotIn("attention cue: `risk`", prompts[0])
        self.assertIn("required invariants", prompts[0])
        self.assertIn("required ordering and completion", prompts[0])
        self.assertIn("predictability", prompts[0])

    def test_provider_grounds_inference_in_the_visible_boundaries(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")
        normalized = " ".join(prompt.split())

        self.assertIn("Ground every Nudge in these visible boundaries", normalized)
        self.assertIn("Use inference to connect visible facts", normalized)
        self.assertIn(
            "A visible name, call, literal, or branch establishes only what happens "
            "after entry",
            normalized,
        )
        self.assertIn(
            "Reachability requires a visible producer or caller and path to the anchor",
            normalized,
        )
        self.assertIn(
            "an internal branch that handles a value does not establish that any "
            "caller supplies it",
            normalized,
        )

    def test_provider_inspects_the_current_decision_from_clean_boundaries(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")
        normalized = " ".join(prompt.split())

        self.assertIn("task beginning", normalized)
        self.assertIn("explicitly referenced task sources", normalized)
        self.assertIn("ordered observable tool-result batch", normalized)
        self.assertIn("bounded decision evidence", normalized)
        self.assertIn("native tool input and observable result", normalized)
        self.assertIn("without assigning an engineering category", normalized)
        self.assertNotIn("related_source", normalized)
        self.assertNotIn("declaration candidates", normalized)
        self.assertIn("Inspect the concrete engineering decision", normalized)
        self.assertIn("task's behavioral requirements", normalized)
        self.assertIn("Identify the implementation choice", normalized)
        self.assertIn(
            "Treat an explicitly required behavior as satisfied", normalized
        )

    def test_provider_uses_recent_nudges_only_as_exclusions(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")
        normalized = " ".join(prompt.split()).lower()

        self.assertIn("recent returned nudges are exclusions, not evidence", normalized)
        self.assertIn(
            "use them only to recognize a repeated relationship or another obligation "
            "of the same visible implementation choice",
            normalized,
        )
        self.assertIn(
            "ground the choice and every claimed consequence in the current packet",
            normalized,
        )
        self.assertIn("different still-changeable engineering decision", normalized)
        self.assertNotIn("decision-lineage references", normalized)
        self.assertNotIn(
            "different dependency or downstream consequence remains eligible", normalized
        )

    def test_provider_surfaces_one_shared_choice_without_owning_the_remedy(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")
        normalized = " ".join(prompt.split())

        self.assertIn("the Actor owns the remedy", normalized)
        self.assertIn(
            "When multiple current-packet consequences depend on one visible state, "
            "owner, or control path",
            normalized,
        )
        self.assertIn(
            "use the shared implementation choice as the single candidate anchor",
            normalized,
        )
        self.assertIn("consequences as its runtime effects", normalized)

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
                    "evidence_seq": 1,
                    "anchor": "batch owner",
                    "relationship": "讓批次只有一個擁有者，避免重試重複移除。",
                }

            outcome = NudgeCore(
                self.settings(Path(raw)), dispatch=dispatch
            ).nudge_once("packet")

        self.assertEqual(outcome.status, "error")

    def test_delivery_uses_principle_plus_neutral_nudge(self):
        self.assertEqual(
            delivery_text("validity", "flags", "布林旗標可形成矛盾狀態。"),
            "validity nudge: flags — 布林旗標可形成矛盾狀態。",
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
                    "evidence_seq": 1,
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
            f"predictability nudge: _autoFlushTimer — {relationship}",
        )

    def test_provider_contract_rejects_rendered_prefixes_inside_the_relationship(self):
        for relationship in (
            "causality nudge: 重複前綴",
            "causality warning: 舊版重複前綴",
        ):
            with self.subTest(relationship=relationship):
                result = parse_nudge_result(
                    json.dumps(
                        {
                            "status": "finding",
                            "principle": "causality",
                            "evidence_seq": 1,
                            "anchor": "batch owner",
                            "relationship": relationship,
                        }
                    )
                )

                self.assertEqual(result["status"], "error")

    def test_prompt_and_schema_let_provider_choose_observation_question_or_silence(self):
        with tempfile.TemporaryDirectory() as raw:
            prompts = []

            def dispatch(_provider, prompt, _packet, _model, **_kwargs):
                prompts.append(prompt)
                return {
                    "status": "no_finding",
                    "principle": "none",
                    "evidence_seq": 0,
                    "anchor": "",
                    "relationship": "",
                }

            NudgeCore(self.settings(Path(raw)), dispatch=dispatch).nudge_once("packet")

        normalized = " ".join(prompts[0].split())
        self.assertIn("Before answering, follow this sequence", normalized)
        self.assertIn("Every finding surfaces one still-open structural decision", normalized)
        self.assertIn(
            "Observed implementation choice → unmet runtime dependency → task-breaking behavior",
            normalized,
        )
        self.assertIn(
            "Use an observation when the visible evidence establishes every edge "
            "in that relationship",
            normalized,
        )
        self.assertIn(
            "Use a question when the visible evidence establishes an exact decision fork",
            normalized,
        )
        self.assertIn(
            "the answer would change the next engineering decision",
            normalized,
        )
        self.assertIn("Otherwise return no_finding", normalized)
        self.assertIn(
            "The current packet must establish every edge in this relationship",
            normalized,
        )
        self.assertIn(
            "When the relevant caller or path is absent, ask whether the task-relevant "
            "value can reach the anchor",
            normalized,
        )
        self.assertIn("Keep every question premise to visible facts", normalized)
        self.assertIn(
            "Use an observation only when both local behavior and reachability are visible",
            normalized,
        )
        self.assertIn(
            "structural decision in code, data, responsibility, or control flow",
            normalized,
        )
        self.assertIn("visible tool-result record", normalized)
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
        self.assertIn("would change the next engineering decision", normalized)

        schema = json.loads((ROOT / "nudge-schema.json").read_text(encoding="utf-8"))
        anchor_description = schema["properties"]["anchor"]["description"]
        description = schema["properties"]["relationship"]["description"]
        self.assertIn("declarative observation or one precise question", description)
        self.assertIn("packet-grounded structural decision", description)
        self.assertIn("smallest exact implementation location", anchor_description.lower())
        self.assertNotIn("maxLength", schema["properties"]["anchor"])
        self.assertNotIn("maxLength", schema["properties"]["relationship"])
        self.assertIn("smallest exact implementation location", prompts[0])
        self.assertIn(
            "one short Traditional Chinese declarative observation or one precise question",
            normalized,
        )
        self.assertIn("one packet-grounded observation or question", normalized)
        self.assertNotIn("characters", prompts[0])
        self.assertEqual(
            schema["properties"]["principle"]["enum"],
            ["validity", "causality", "predictability", "none"],
        )
        self.assertEqual(
            schema["required"],
            ["status", "principle", "evidence_seq", "anchor", "relationship"],
        )


if __name__ == "__main__":
    unittest.main()
