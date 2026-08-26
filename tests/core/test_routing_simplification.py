"""Characterization tests for explicit work-focus routing."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import lens_router
import persona_config
class RoutingSimplificationTests(unittest.TestCase):
    def test_reported_focus_routes_without_reparsing_evidence(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            route = lens_router.resolve_review_route(
                data_dir,
                environ={},
                reported_focus="reliability",
            )

        self.assertEqual(route.stage, "reliability")
        self.assertEqual(route.effective_lens, "lamport")
        self.assertEqual(route.source, "main_model_report")

    def test_router_accepts_no_evidence_or_structured_concern_arguments(self):
        parameters = lens_router.resolve_review_route.__annotations__
        self.assertNotIn("evidence", parameters)
        self.assertNotIn("routing_concern", parameters)

    def test_explicit_manual_stage_wins(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            persona_config.save_stage(data_dir, "build")
            route = lens_router.resolve_review_route(
                data_dir,
                environ={},
                reported_focus="performance",
            )

        self.assertEqual(route.stage, "build")
        self.assertEqual(route.effective_lens, "beck")
        self.assertEqual(route.source, "config")

    def test_automatic_stage_uses_report_or_phase_fallback(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            persona_config.save_stage(data_dir, "automatic")
            reported = lens_router.resolve_review_route(
                data_dir, environ={}, reported_focus="performance"
            )
            stopping = lens_router.resolve_review_route(
                data_dir, environ={}, stopping=True
            )

        self.assertEqual(reported.effective_lens, "carmack")
        self.assertEqual(stopping.effective_lens, "linus")
        self.assertNotIn("general", persona_config.PERSONA_NAMES)


if __name__ == "__main__":
    unittest.main()
