"""Keep route state smaller than the reviewer decision it enables."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import lens_router
import persona_config


class RoutingSimplificationTests(unittest.TestCase):
    def test_automatic_neither_parses_evidence_nor_guesses_a_lens(self):
        with tempfile.TemporaryDirectory() as raw:
            route = lens_router.resolve_review_route(Path(raw), environ={})

        self.assertEqual(route.lens, "")
        self.assertEqual(route.stage, "automatic")

    def test_each_manual_stage_forces_its_existing_lens(self):
        for stage, lens in (
            ("design", "jeff"),
            ("build", "beck"),
            ("evolve", "fowler"),
            ("review", "linus"),
            ("reliability", "lamport"),
            ("performance", "carmack"),
        ):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                persona_config.save_stage(root, stage)
                route = lens_router.resolve_review_route(root, environ={})
                self.assertEqual(
                    (route.stage, route.lens, route.source),
                    (stage, lens, "config"),
                )

    def test_router_has_no_general_persona(self):
        self.assertNotIn("general", persona_config.PERSONA_NAMES)


if __name__ == "__main__":
    unittest.main()
