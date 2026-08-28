"""The removed lifecycle focus protocol must not return through host hooks."""

from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path

import claude_prompt
import lens_router
import persona_config
from masters_nudge import codex_adapter


class AutomaticRouteTests(unittest.TestCase):
    def test_automatic_route_has_no_preselected_lens(self):
        with tempfile.TemporaryDirectory() as raw:
            route = lens_router.resolve_review_route(Path(raw), environ={})

        self.assertEqual(
            (route.stage, route.lens, route.source),
            ("automatic", "", "default"),
        )

    def test_manual_stage_remains_the_only_route_override(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona_config.save_stage(root, "performance")
            route = lens_router.resolve_review_route(root, environ={})

        self.assertEqual(
            (route.stage, route.lens, route.source),
            ("performance", "carmack", "config"),
        )

    def test_lifecycle_focus_protocol_is_absent(self):
        self.assertFalse(hasattr(persona_config, "FOCUS_REPORT_INSTRUCTION"))
        self.assertFalse(hasattr(persona_config, "reported_focus"))
        self.assertNotIn(
            "reported_focus",
            inspect.signature(lens_router.resolve_review_route).parameters,
        )
        self.assertFalse(hasattr(codex_adapter, "build_progress_instruction_output"))
        self.assertFalse(hasattr(claude_prompt, "build_hook_output"))


if __name__ == "__main__":
    unittest.main()
