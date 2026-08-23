#!/usr/bin/env python3
"""Keep lifecycle-stage metadata owned by one canonical specification."""

from __future__ import annotations

import unittest

import buddy_window
import persona_config


class TestStageSpec(unittest.TestCase):
    def test_stage_specs_are_the_single_source_for_public_stage_data(self):
        expected = {
            "design": ("Design", "系統結構、因果與成本", "jeff"),
            "build": ("Build", "小步驟、測試與回饋", "beck"),
            "evolve": ("Evolve", "重構與變更成本", "fowler"),
            "review": ("Review", "簡化與責任歸屬", "linus"),
        }

        self.assertEqual(expected, {
            stage: (spec.name, spec.focus, spec.persona)
            for stage, spec in persona_config.STAGE_SPECS.items()
        })
        self.assertEqual(
            {
                spec.persona: f"{spec.name} · {spec.focus}"
                for spec in persona_config.STAGE_SPECS.values()
            },
            {
                persona: persona_config.PERSONA_PUBLIC_LABELS[persona]
                for persona in (spec.persona for spec in persona_config.STAGE_SPECS.values())
            },
        )

    def test_window_selector_iterates_the_canonical_stage_order(self):
        self.assertFalse(hasattr(buddy_window, "stage_selection_label"))
        self.assertEqual(
            list(persona_config.STAGE_SPECS),
            list(buddy_window.SELECTOR_STAGES.values()),
        )
        self.assertEqual(
            [spec.label for spec in persona_config.STAGE_SPECS.values()],
            buddy_window.selector_options(),
        )


if __name__ == "__main__":
    unittest.main()
