"""Each checkpoint uses exactly one selected attention Lens."""

from __future__ import annotations

import shutil
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

    def test_review_contract_signature_tracks_only_the_effective_contract(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            runtime = root / "runtime"
            (runtime / "personas").mkdir(parents=True)
            shutil.copy(ROOT / "buddy-prompt.txt", runtime / "buddy-prompt.txt")
            shutil.copy(ROOT / "nudge-schema.json", runtime / "nudge-schema.json")
            for persona in ("linus", "lamport", "carmack"):
                shutil.copy(
                    ROOT / "personas" / f"{persona}.txt",
                    runtime / "personas" / f"{persona}.txt",
                )
            core = NudgeCore(self.settings(root, "simplicity", runtime_dir=runtime))
            first = core.review_contract_signature()
            (runtime / "personas" / "lamport.txt").write_text(
                "unselected persona changed\n", encoding="utf-8"
            )
            unrelated = core.review_contract_signature()
            (runtime / "personas" / "linus.txt").write_text(
                "selected persona changed\n", encoding="utf-8"
            )
            selected = core.review_contract_signature()
            changed_model = NudgeCore(
                RuntimeSettings(
                    "openai",
                    "another-model",
                    RuntimePaths(runtime, root, root, root / "error.log"),
                    lens="simplicity",
                )
            ).review_contract_signature()

        self.assertEqual(len(first), 64)
        self.assertEqual(first, unrelated)
        self.assertNotEqual(first, selected)
        self.assertNotEqual(selected, changed_model)

    def test_review_tool_batch_completes_one_decision_per_evidence_class(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "core-review", cwd=raw)
            storage.start_turn(root, session, "檢查驗證結果")
            calls = []

            def dispatch(*_args, **_kwargs):
                calls.append("generator")
                return {"status": "no_finding", "lens": "none", "finding": ""}

            core = NudgeCore(self.settings(root, "simplicity"), dispatch=dispatch)
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
            repeated_state = storage.load_turn_state(root, session)

            changed_event = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "python -m unittest"},
                tool_output="Process exited with code 1",
                failed=True,
                failure_known=True,
            )
            changed_evidence = core.review_tool_batch([changed_event])
            changed_settings = RuntimeSettings(
                "openai",
                "changed-model",
                RuntimePaths(ROOT, root, root, root / "error.log"),
                lens="simplicity",
            )
            changed_contract = NudgeCore(
                changed_settings, dispatch=dispatch
            ).review_tool_batch([changed_event])
            final_state = storage.load_turn_state(root, session)

        self.assertEqual(first.status, "no_finding")
        self.assertIsNone(repeated)
        self.assertEqual(repeated_state["evidence_seq"], 2)
        self.assertEqual(
            repeated_state["review_admission"]["completed_evidence_classes"],
            ["verification"],
        )
        self.assertEqual(changed_evidence.status, "no_finding")
        self.assertEqual(changed_contract.status, "no_finding")
        self.assertEqual(calls, ["generator", "generator", "generator"])
        self.assertEqual(final_state["evidence_seq"], 4)
        self.assertEqual(
            final_state["review_admission"]["completed_evidence_classes"],
            ["failure"],
        )

    def test_provider_error_leaves_the_decision_open_for_retry(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "retry", cwd=raw)
            storage.start_turn(root, session, "檢查驗證結果")
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
        self.assertEqual(second.status, "error")
        self.assertEqual(calls, ["generator", "generator"])

    def test_finding_also_completes_the_decision(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "finding", cwd=raw)
            storage.start_turn(root, session, "檢查驗證結果")
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

    def test_one_batch_completes_every_evidence_class_it_reviewed(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "multi-class", cwd=raw)
            storage.start_turn(root, session, "檢查驗證與量測")
            calls = []

            def dispatch(*_args, **_kwargs):
                calls.append("generator")
                return {"status": "no_finding", "lens": "none", "finding": ""}

            core = NudgeCore(self.settings(root, "simplicity"), dispatch=dispatch)
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
            repeated_verification = core.review_tool_batch([verification])
            repeated_measurement = core.review_tool_batch([measurement])
            state = storage.load_turn_state(root, session)

        self.assertEqual(first.status, "no_finding")
        self.assertIsNone(repeated_verification)
        self.assertIsNone(repeated_measurement)
        self.assertEqual(calls, ["generator"])
        self.assertEqual(
            state["review_admission"]["completed_evidence_classes"],
            ["verification", "measurement"],
        )

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
