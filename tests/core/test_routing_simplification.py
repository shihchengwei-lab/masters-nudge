"""Characterization tests for evidence-owned software lens routing."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import lens_router
import persona_config


class RoutingSimplificationTests(unittest.TestCase):
    def test_cooldown_without_evidence_uses_general_instead_of_arbitrary_persona(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            persona_config.save_stage(data_dir, "build")

            route = lens_router.resolve_review_route(
                data_dir,
                "ordinary checkpoint with no specialist signal",
                checkpoint=True,
                injected_personas=("beck",),
            )

        self.assertEqual(route.stage, "build")
        self.assertEqual(route.primary_lens, "beck")
        self.assertEqual(route.effective_lens, "general")
        self.assertEqual(route.override_lens, "")
        self.assertEqual(route.source, "software_cooldown_general")

    def test_evidence_backed_specialist_still_overrides_the_stage(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            persona_config.save_stage(data_dir, "build")

            route = lens_router.resolve_review_route(
                data_dir,
                "benchmark shows latency 20 ms in the hot path",
                checkpoint=True,
                injected_personas=("beck",),
            )

        self.assertEqual(route.primary_lens, "beck")
        self.assertEqual(route.effective_lens, "carmack")
        self.assertEqual(route.trigger, "measured-performance-evidence")


if __name__ == "__main__":
    unittest.main()
