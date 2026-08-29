"""Routing chooses one of the three retained attention lenses."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import lens_router
from masters_nudge.core import NudgeCore
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


ROOT = Path(__file__).resolve().parents[2]


class RoutingTests(unittest.TestCase):
    def settings(self, data_dir: Path, lens: str) -> RuntimeSettings:
        return RuntimeSettings(
            "openai",
            "test-model",
            RuntimePaths(ROOT, data_dir, data_dir, data_dir / "error.log"),
            lens=lens,
        )

    def test_only_three_manual_lenses_exist(self):
        self.assertEqual(
            lens_router.LENS_PERSONAS,
            {
                "simplicity": "linus",
                "reliability": "lamport",
                "performance": "carmack",
            },
        )

    def test_automatic_route_then_generator_share_one_deadline(self):
        with tempfile.TemporaryDirectory() as raw:
            calls = []

            def dispatch(_provider, prompt, packet, _model, **kwargs):
                calls.append((prompt, packet, kwargs["timeout_sec"]))
                if len(calls) == 1:
                    return {"status": "finding", "lens": "simplicity"}
                return {
                    "status": "finding",
                    "lens": "simplicity",
                    "finding": "讓單一欄位直接擁有責任。",
                }

            outcome = NudgeCore(
                self.settings(Path(raw), "automatic"), dispatch=dispatch
            ).nudge_once("EVIDENCE-PACKET")

        self.assertEqual(outcome.status, "finding")
        self.assertEqual(outcome.lens, "simplicity")
        self.assertEqual(len(calls), 2)
        self.assertEqual([call[1] for call in calls], ["EVIDENCE-PACKET"] * 2)
        self.assertGreaterEqual(calls[0][2], calls[1][2])

    def test_each_manual_lens_skips_the_router(self):
        for lens in lens_router.LENS_PERSONAS:
            with self.subTest(lens=lens), tempfile.TemporaryDirectory() as raw:
                calls = []

                def dispatch(_provider, prompt, packet, _model, **_kwargs):
                    calls.append((prompt, packet))
                    return {
                        "status": "no_finding",
                        "lens": "none",
                        "finding": "",
                    }

                outcome = NudgeCore(
                    self.settings(Path(raw), lens), dispatch=dispatch
                ).nudge_once("EVIDENCE-PACKET")

                self.assertEqual(outcome.status, "no_finding")
                self.assertEqual(len(calls), 1)
                self.assertIn(f"# LENS CONTEXT: {lens}", calls[0][0])
                self.assertEqual(calls[0][1], "EVIDENCE-PACKET")

    def test_router_silence_does_not_call_the_generator(self):
        with tempfile.TemporaryDirectory() as raw:
            calls = []

            def dispatch(*_args, **_kwargs):
                calls.append(1)
                return {"status": "no_finding", "lens": "none"}

            outcome = NudgeCore(
                self.settings(Path(raw), "automatic"), dispatch=dispatch
            ).nudge_once("packet")

        self.assertEqual(outcome.status, "no_finding")
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
