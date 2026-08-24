"""Characterization tests for evidence-owned software lens routing."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import lens_router
import persona_config
from masters_nudge import checkpoints


class RoutingSimplificationTests(unittest.TestCase):
    def test_classifier_emits_structured_concerns_for_known_triggers(self):
        cases = {
            "repeated-command-family": "feedback-loop",
            "repeated-failure-family": "feedback-loop",
            "diff-growth": "knowledge-boundary",
            "goal-complete": "completion-boundary",
            "goal-blocked": "completion-boundary",
        }

        for trigger, expected in cases.items():
            with self.subTest(trigger=trigger):
                self.assertEqual(
                    checkpoints.routing_concern_for_trigger(trigger), expected
                )

    def test_structured_concern_routes_without_machine_trigger_text(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            persona_config.save_stage(data_dir, "build")

            route = lens_router.resolve_review_route(
                data_dir,
                "ordinary bounded workflow evidence",
                routing_concern="knowledge-boundary",
                checkpoint=True,
            )

        self.assertEqual(route.stage, "build")
        self.assertEqual(route.primary_lens, "beck")
        self.assertEqual(route.effective_lens, "fowler")
        self.assertEqual(route.trigger, "knowledge-boundary-evidence")

    def test_machine_trigger_words_are_not_reparsed_as_free_text(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            persona_config.save_stage(data_dir, "build")

            route = lens_router.resolve_review_route(
                data_dir,
                "trigger: diff-growth",
                checkpoint=True,
            )

        self.assertEqual(route.effective_lens, "beck")
        self.assertEqual(route.trigger, "")

    def test_route_keeps_the_stage_lens_without_specialist_evidence(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            persona_config.save_stage(data_dir, "build")

            route = lens_router.resolve_review_route(
                data_dir,
                "ordinary checkpoint with no specialist signal",
                checkpoint=True,
            )

        self.assertEqual(route.stage, "build")
        self.assertEqual(route.primary_lens, "beck")
        self.assertEqual(route.effective_lens, "beck")
        self.assertFalse(hasattr(route, "suppression_reason"))
        self.assertEqual(route.override_lens, "")
        self.assertNotIn("general", persona_config.PERSONA_NAMES)

    def test_evidence_backed_specialist_still_overrides_the_stage(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            persona_config.save_stage(data_dir, "build")

            route = lens_router.resolve_review_route(
                data_dir,
                "benchmark shows latency 20 ms in the hot path",
                checkpoint=True,
            )

        self.assertEqual(route.primary_lens, "beck")
        self.assertEqual(route.effective_lens, "carmack")
        self.assertEqual(route.trigger, "measured-performance-evidence")


if __name__ == "__main__":
    unittest.main()
