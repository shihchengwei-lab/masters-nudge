"""Routing chooses one of the three retained attention lenses."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import lens_router
from masters_nudge import storage
from masters_nudge.contracts import SessionRef, ToolCompleted
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

    def test_review_contract_signature_changes_with_provider_configuration(self):
        with tempfile.TemporaryDirectory() as raw:
            first = NudgeCore(
                self.settings(Path(raw), "automatic")
            ).review_contract_signature()
            changed = RuntimeSettings(
                "openai",
                "another-model",
                RuntimePaths(ROOT, Path(raw), Path(raw), Path(raw) / "error.log"),
                lens="automatic",
            )
            second = NudgeCore(changed).review_contract_signature()

        self.assertEqual(len(first), 64)
        self.assertNotEqual(first, second)

    def test_review_tool_batch_owns_completed_generator_silence(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "core-review", cwd=raw)
            storage.start_turn(root, session, "檢查驗證結果")
            calls = []

            def dispatch(*_args, **_kwargs):
                calls.append("generator")
                return {"status": "no_finding", "lens": "none", "finding": ""}

            core = NudgeCore(
                self.settings(root, "simplicity"),
                dispatch=dispatch,
            )
            event = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest"},
                tool_output="Process exited with code 0",
                failed=False,
                failure_known=True,
            )

            first = core.review_tool_batch([event])
            repeated = core.review_tool_batch([event])
            state = storage.load_turn_state(root, session)

        self.assertEqual(first.decision_stage, "generator")
        self.assertIsNone(repeated)
        self.assertEqual(calls, ["generator"])
        self.assertEqual(state["evidence_seq"], 1)
        self.assertEqual(state["last_completed_review"]["reuse_count"], 1)

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
        self.assertEqual(outcome.decision_stage, "generator")
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
                self.assertEqual(outcome.decision_stage, "generator")
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
        self.assertEqual(outcome.decision_stage, "router")
        self.assertEqual(len(calls), 1)

    def test_stage_observer_reports_each_provider_call_without_changing_outcome(self):
        with tempfile.TemporaryDirectory() as raw:
            calls = []
            observed = []

            def dispatch(*_args, **_kwargs):
                calls.append(1)
                if len(calls) == 1:
                    return {"status": "finding", "lens": "reliability"}
                return {
                    "status": "finding",
                    "lens": "reliability",
                    "finding": "讓失敗狀態只有一個權威來源。",
                }

            outcome = NudgeCore(
                self.settings(Path(raw), "automatic"), dispatch=dispatch
            ).nudge_once(
                "packet",
                observe_stage=lambda stage, status, lens, duration_ms: observed.append(
                    (stage, status, lens, duration_ms)
                ),
            )

        self.assertEqual(outcome.status, "finding")
        self.assertEqual(
            [(stage, status, lens) for stage, status, lens, _duration in observed],
            [
                ("router", "finding", "reliability"),
                ("generator", "finding", "reliability"),
            ],
        )
        self.assertTrue(all(duration >= 0 for *_prefix, duration in observed))

    def test_broken_stage_observer_does_not_change_provider_outcome(self):
        with tempfile.TemporaryDirectory() as raw:
            def dispatch(*_args, **_kwargs):
                return {"status": "no_finding", "lens": "none"}

            def broken_observer(*_args):
                raise OSError("diagnostic storage unavailable")

            outcome = NudgeCore(
                self.settings(Path(raw), "automatic"), dispatch=dispatch
            ).nudge_once("packet", observe_stage=broken_observer)

        self.assertEqual(outcome.status, "no_finding")
        self.assertEqual(outcome.decision_stage, "router")

    def test_stage_observer_reports_a_provider_timeout_as_an_error(self):
        with tempfile.TemporaryDirectory() as raw:
            observed = []

            def dispatch(*_args, **_kwargs):
                raise TimeoutError("provider timed out")

            with self.assertRaises(TimeoutError):
                NudgeCore(
                    self.settings(Path(raw), "automatic"), dispatch=dispatch
                ).nudge_once(
                    "packet",
                    observe_stage=lambda stage, status, lens, duration_ms: observed.append(
                        (stage, status, lens, duration_ms)
                    ),
                )

        self.assertEqual(
            [(stage, status, lens) for stage, status, lens, _duration in observed],
            [("router", "error", "")],
        )


if __name__ == "__main__":
    unittest.main()
