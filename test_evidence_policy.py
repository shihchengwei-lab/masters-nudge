#!/usr/bin/env python3
"""Public evidence boundaries for the current long-task experiment."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
HISTORY_URL = (
    "https://github.com/shihchengwei-lab/masters-nudge/tree/"
    "evidence-archive-2026-08-22/experiment/riemann-domain"
)


class EvidencePolicyTests(unittest.TestCase):
    def test_riemann_benchmark_is_history_only(self):
        self.assertFalse((HERE / "experiment" / "riemann-domain").exists())
        evidence_index = (HERE / "evaluation" / "README.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(HISTORY_URL, evidence_index)
        self.assertIn("pre-question", evidence_index)
        self.assertIn("incomplete delivery receipts", evidence_index)

    def test_threejs_protocol_freezes_observation_without_an_effect_claim(self):
        protocol = (
            HERE / "evaluation" / "shader_long_tail" / "PROTOCOL_V2.md"
        ).read_text(encoding="utf-8")

        for required in (
            "dgreenheck/webgpu-black-hole",
            "cf2fca75a9e774449057cbebe2197129249d96b8",
            "不宣稱 Masters' Nudge 改善研究成果",
            "每則 finding 都必須是開放問句並以「？」收束",
            "generated",
            "delivered",
            "main_response",
            "A01–A50",
            "candidate-budget-and-saturation-gates",
        ):
            with self.subTest(required=required):
                self.assertIn(required, protocol)

    def test_threejs_manifest_freezes_fifty_candidates_and_saturation_gates(self):
        manifest_path = (
            HERE
            / "evaluation"
            / "shader_long_tail"
            / "run-manifest-v2.template.json"
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual("threejs-webgpu-black-hole-v2", manifest["run_id"])
        self.assertEqual(
            "cf2fca75a9e774449057cbebe2197129249d96b8",
            manifest["workspace"]["upstream_commit"],
        )
        self.assertEqual(
            "unconfirmed", manifest["domain_fit"]["decision"]
        )
        self.assertEqual(
            "selected-workload-not-threejs-general",
            manifest["domain_fit"]["scope"],
        )
        self.assertEqual(
            "baseline-profiler-shows-shader-gpu-dominant",
            manifest["domain_fit"]["confirmation_gate"],
        )
        self.assertIsNone(manifest["shader_profile"]["engine_adapter"])
        self.assertEqual(
            "pending-observed-runtime-failure",
            manifest["shader_profile"]["adapter_decision"],
        )
        self.assertEqual(50, manifest["search"]["candidate_budget"])
        self.assertEqual("A01-A50", manifest["search"]["candidate_id_range"])
        self.assertEqual(50, manifest["search"]["distinct_cell_limit"])
        self.assertIsNone(manifest["search"]["refinement_limit_per_cell"])
        self.assertEqual(
            "candidate-budget-and-saturation-gates",
            manifest["search"]["stop_condition"],
        )
        self.assertGreaterEqual(
            len(manifest["search"]["prefrozen_mechanism_inventory"]), 8
        )


if __name__ == "__main__":
    unittest.main()
