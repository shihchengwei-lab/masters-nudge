#!/usr/bin/env python3
"""Characterize the stage-only public surface."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import buddy_window
import lens_router
import persona_config
from masters_nudge.prompting import build_system_prompt


HERE = Path(__file__).resolve().parent
PERSON_NAMES = tuple(persona_config.LENS_PERSONAS.values())


class TestStageOnlyPublicSurface(unittest.TestCase):
    def test_selector_and_badges_describe_work_not_people(self):
        self.assertEqual(
            [
                "Design · 系統結構、因果與成本",
                "Build · 小步驟、測試與回饋",
                "Evolve · 重構與變更成本",
                "Review · 簡化與責任歸屬",
            ],
            buddy_window.selector_options(),
        )
        expected = {
            "jeff": "● Design · 系統結構、因果與成本",
            "beck": "● Build · 小步驟、測試與回饋",
            "fowler": "● Evolve · 重構與變更成本",
            "linus": "● Review · 簡化與責任歸屬",
            "lamport": "● Reliability · 狀態、順序與失敗",
            "carmack": "● Performance · 執行路徑與效能",
        }
        for persona, label in expected.items():
            with self.subTest(persona=persona):
                self.assertEqual(label, buddy_window.lens_badge(persona)[0])
                self.assertFalse(any(name in label for name in PERSON_NAMES))

    def test_stage_environment_is_the_only_public_override(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            selected = persona_config.resolve_stage(
                base, environ={"MASTERS_NUDGE_STAGE": "review"}
            )
            legacy = persona_config.resolve_stage(
                base, environ={"MASTERS_NUDGE_PERSONA": "linus"}
            )
            invalid = persona_config.resolve_stage(
                base, environ={"MASTERS_NUDGE_STAGE": "linus"}
            )

        self.assertEqual(("review", "linus", "environment"), (
            selected.stage, selected.persona, selected.source
        ))
        self.assertEqual(("build", "beck", "default"), (
            legacy.stage, legacy.persona, legacy.source
        ))
        self.assertEqual(("build", "beck", "invalid_environment"), (
            invalid.stage, invalid.persona, invalid.source
        ))

    def test_provider_prompt_keeps_person_name_as_private_attention_cue(self):
        route = lens_router.ReviewRoute(
            stage="review",
            primary_lens="linus",
            effective_lens="linus",
            override_lens="",
            trigger="configured-stage",
            source="config",
        )
        prompt = build_system_prompt(
            prompt_file=HERE / "buddy-prompt.txt",
            persona_dir=HERE / "personas",
            route=route,
        )

        self.assertIn("Linus Torvalds", prompt)

    def test_public_docs_expose_stage_not_persona_or_people(self):
        for name in ("README.md", "README.zh-TW.md", "docs/phase-c-architecture.md"):
            with self.subTest(name=name):
                text = (HERE / name).read_text(encoding="utf-8")
                self.assertIn("MASTERS_NUDGE_STAGE", text)
                self.assertNotIn("MASTERS_NUDGE_PERSONA", text)
                for person in PERSON_NAMES:
                    self.assertNotIn(person, text)


if __name__ == "__main__":
    unittest.main()
