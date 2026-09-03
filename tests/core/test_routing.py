"""Each checkpoint uses exactly one selected attention Lens."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from masters_nudge import storage
from masters_nudge.contracts import SessionRef, ToolCompleted
from masters_nudge.core import NudgeCore
from masters_nudge.lenses import LENSES
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


ROOT = Path(__file__).resolve().parents[2]


class RoutingTests(unittest.TestCase):
    def settings(
        self, data_dir: Path, lens: str, *, runtime_dir: Path = ROOT
    ) -> RuntimeSettings:
        return RuntimeSettings(
            "openai",
            "test-model",
            RuntimePaths(runtime_dir, data_dir, data_dir, data_dir / "error.log"),
            lens=lens,
        )

    def test_only_three_manual_lenses_exist(self):
        self.assertEqual(
            {lens: spec.persona for lens, spec in LENSES.items()},
            {
                "simplicity": "linus",
                "reliability": "lamport",
                "performance": "carmack",
            },
        )

    def test_review_flow_uses_one_candidate_and_one_failure_opportunity(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "budget", cwd=raw)
            storage.start_turn(root, session, "檢查驗證結果")
            calls = []

            def dispatch(_provider, _prompt, packet, _model, **_kwargs):
                calls.append(packet)
                return {"status": "no_finding", "lens": "none", "finding": ""}

            core = NudgeCore(self.settings(root, "simplicity"), dispatch=dispatch)
            first_check = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest"},
                tool_output="FIRST_CHECKPOINT passed",
            )
            second_check = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest"},
                tool_output="SECOND_CHECKPOINT passed",
            )
            third_check = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest"},
                tool_output="THIRD_CHECKPOINT passed",
            )
            change = lambda name: ToolCompleted(
                session,
                "apply_patch",
                tool_input={"patch": name},
                tool_output="Done!",
                mutating=True,
            )
            failure = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest"},
                tool_output="1 failed",
                failed=True,
                failure_known=True,
            )

            baseline = core.review_tool_batch([first_check])
            core.review_tool_batch([change("edit-1")])
            candidate = core.review_tool_batch([second_check])
            repeated_candidate = core.review_tool_batch([third_check])
            recovery = core.review_tool_batch([failure])
            repeated_failure = core.review_tool_batch([failure])
            final_state = storage.load_turn_state(root, session)

        self.assertIsNone(baseline)
        self.assertEqual(candidate.status, "no_finding")
        self.assertIsNone(repeated_candidate)
        self.assertEqual(recovery.status, "no_finding")
        self.assertIsNone(repeated_failure)
        self.assertEqual(len(calls), 2)
        self.assertIn("SECOND_CHECKPOINT", calls[0])
        self.assertIn("1 failed", calls[1])
        self.assertNotIn("SECOND_CHECKPOINT", calls[1])
        self.assertTrue(
            any(
                "FIRST_CHECKPOINT" in record["content"]
                for record in final_state["evidence_records"]
            )
        )
        self.assertTrue(final_state["candidate_review_used"])
        self.assertTrue(final_state["failure_review_used"])

    def test_a_distinct_completed_check_without_new_change_does_not_call(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "richer-review", cwd=raw)
            storage.start_turn(root, session, "檢查驗證結果")
            storage.record_evidence(root, session, category="change", content="edit")
            calls = []

            def dispatch(*_args, **_kwargs):
                calls.append("generator")
                return {"status": "no_finding", "lens": "none", "finding": ""}

            core = NudgeCore(self.settings(root, "simplicity"), dispatch=dispatch)
            focused = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest tests.focused"},
                tool_output="Process exited with code 0",
            )
            complete = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest discover"},
                tool_output="Process exited with code 0; 83 tests passed",
            )

            first = core.review_tool_batch([focused])
            second = core.review_tool_batch([complete])

        self.assertEqual(first.status, "no_finding")
        self.assertIsNone(second)
        self.assertEqual(calls, ["generator"])

    def test_provider_error_consumes_the_candidate_opportunity(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "retry", cwd=raw)
            storage.start_turn(root, session, "檢查驗證結果")
            storage.record_evidence(root, session, category="change", content="edit")
            calls = []

            def dispatch(*_args, **_kwargs):
                calls.append("generator")
                return {"status": "error"}

            core = NudgeCore(self.settings(root, "simplicity"), dispatch=dispatch)
            event = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest"},
                tool_output="Process exited with code 0",
            )

            first = core.review_tool_batch([event])
            second = core.review_tool_batch([event])

        self.assertEqual(first.status, "error")
        self.assertIsNone(second)
        self.assertEqual(calls, ["generator"])

    def test_finding_consumes_the_candidate_opportunity(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "finding", cwd=raw)
            storage.start_turn(root, session, "檢查驗證結果")
            storage.record_evidence(root, session, category="change", content="edit")
            calls = []

            def dispatch(*_args, **_kwargs):
                calls.append("generator")
                return {
                    "status": "finding",
                    "lens": "simplicity",
                    "finding": "保留真正承重的邊界。",
                }

            core = NudgeCore(self.settings(root, "simplicity"), dispatch=dispatch)
            event = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest"},
                tool_output="Process exited with code 0",
            )

            first = core.review_tool_batch([event])
            repeated = core.review_tool_batch([event])

        self.assertEqual(first.status, "finding")
        self.assertIsNone(repeated)
        self.assertEqual(calls, ["generator"])

    def test_an_identical_multi_class_batch_uses_one_candidate_opportunity(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "multi-class", cwd=raw)
            storage.start_turn(root, session, "檢查驗證與量測")
            calls = []

            def dispatch(*_args, **_kwargs):
                calls.append("generator")
                return {"status": "no_finding", "lens": "none", "finding": ""}

            core = NudgeCore(self.settings(root, "simplicity"), dispatch=dispatch)
            core.review_tool_batch(
                [
                    ToolCompleted(
                        session,
                        "apply_patch",
                        tool_input={"patch": "edit"},
                        tool_output="Done!",
                        mutating=True,
                    )
                ]
            )
            verification = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest"},
                tool_output="Process exited with code 0",
            )
            measurement = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python benchmark.py"},
                tool_output="median: 10 ms",
            )

            first = core.review_tool_batch([verification, measurement])
            repeated = core.review_tool_batch([verification, measurement])
            state = storage.load_turn_state(root, session)

        self.assertEqual(first.status, "no_finding")
        self.assertIsNone(repeated)
        self.assertEqual(calls, ["generator"])
        self.assertTrue(state["candidate_review_used"])
        self.assertFalse(state["failure_review_used"])

    def test_each_lens_calls_one_generator_with_its_persona(self):
        persona_markers = {
            "simplicity": "# Linus Torvalds",
            "reliability": "# Leslie Lamport",
            "performance": "# John Carmack",
        }
        for lens, marker in persona_markers.items():
            with self.subTest(lens=lens), tempfile.TemporaryDirectory() as raw:
                calls = []

                def dispatch(_provider, prompt, packet, _model, **kwargs):
                    calls.append((prompt, packet, kwargs["timeout_sec"]))
                    return {"status": "no_finding", "lens": "none", "finding": ""}

                outcome = NudgeCore(
                    self.settings(Path(raw), lens), dispatch=dispatch
                ).nudge_once("EVIDENCE-PACKET")

                self.assertEqual(outcome.status, "no_finding")
                self.assertEqual(len(calls), 1)
                self.assertIn(f"# LENS CONTEXT: {lens}", calls[0][0])
                self.assertIn(marker, calls[0][0])
                self.assertEqual(calls[0][1], "EVIDENCE-PACKET")
                self.assertEqual(calls[0][2], 90)


if __name__ == "__main__":
    unittest.main()
