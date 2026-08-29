"""Contracts for the first-principles Masters' Nudge redesign."""

from __future__ import annotations

import inspect
import json
import tempfile
import unittest
from pathlib import Path

import lens_router
import persona_config
from masters_nudge import checkpoints, evidence, prompting, storage
from masters_nudge.contracts import SessionRef, ToolCompleted
from masters_nudge.provider_contract import parse_reaction_result


HERE = Path(__file__).resolve().parents[2]
RETAINED_LENSES = {"linus", "lamport", "carmack"}


class PromptContractTests(unittest.TestCase):
    def test_base_prompt_only_owns_identity_view_and_output(self):
        prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")
        normalized = " ".join(prompt.split()).lower()

        self.assertIn("# role", normalized)
        self.assertIn("# view", normalized)
        self.assertIn("# output", normalized)
        self.assertNotIn("# evidence", normalized)
        self.assertNotIn("# nudge", normalized)
        self.assertNotIn("change what the main agent should decide", normalized)
        self.assertNotIn("underexplored", normalized)
        for lens in RETAINED_LENSES:
            self.assertNotIn(lens, normalized)

    def test_generator_builder_has_no_router_hypothesis_or_timing_input(self):
        parameters = inspect.signature(prompting.build_system_prompt).parameters

        self.assertNotIn("route_decision", parameters)
        self.assertNotIn("timing_prompt", parameters)

    def test_runtime_input_is_only_the_source_packet(self):
        self.assertEqual(prompting.build_review_input("packet"), "packet")
        self.assertEqual(
            tuple(inspect.signature(prompting.build_review_input).parameters),
            ("source_packet",),
        )


class LensSurfaceTests(unittest.TestCase):
    def test_only_three_lenses_are_registered_and_packaged(self):
        self.assertEqual(set(persona_config.LENS_PERSONAS), RETAINED_LENSES)
        self.assertEqual(
            {path.stem for path in (HERE / "personas").glob("*.txt")},
            RETAINED_LENSES,
        )

    def test_only_three_manual_stages_remain(self):
        self.assertEqual(
            {
                "review": "linus",
                "reliability": "lamport",
                "performance": "carmack",
            },
            {
                stage: spec.persona
                for stage, spec in persona_config.STAGE_SPECS.items()
            },
        )

    def test_retired_stage_is_visible_as_retired_automatic_fallback(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "config.json").write_text(
                '{"stage":"build"}\n', encoding="utf-8"
            )
            config = persona_config.resolve_stage(root, environ={})
            environment = persona_config.resolve_stage(
                root, environ={"MASTERS_NUDGE_STAGE": "design"}
            )

        self.assertEqual(
            ("automatic", "", "retired_config"),
            (config.stage, config.persona, config.source),
        )
        self.assertEqual(
            ("automatic", "", "retired_environment"),
            (environment.stage, environment.persona, environment.source),
        )

    def test_router_only_names_retained_lenses(self):
        prompt = prompting.build_router_prompt().lower()

        for lens in RETAINED_LENSES:
            self.assertIn(lens, prompt)
        for retired in ("jeff", "beck", "fowler"):
            self.assertNotIn(retired, prompt)


class StructuralOutputTests(unittest.TestCase):
    def test_semantic_wording_is_not_mechanically_rejected(self):
        parsed = parse_reaction_result(
            '{"status":"finding","effective_lens":"linus",'
            '"finding":"讓欄位直接擁有責任。"}'
        )

        self.assertEqual(parsed["status"], "finding")
        self.assertNotIn("contract_deviations", parsed)

    def test_over_length_finding_is_structurally_rejected(self):
        finding = "甲" * 53
        parsed = parse_reaction_result(
            json.dumps(
                {
                    "status": "finding",
                    "effective_lens": "linus",
                    "finding": finding,
                },
                ensure_ascii=False,
            )
        )

        self.assertEqual(parsed["status"], "error")

    def test_output_schemas_only_accept_retained_lenses(self):
        expected = ["linus", "lamport", "carmack", "none"]
        for name in ("reaction-schema.json", "route-schema.json"):
            with self.subTest(name=name):
                schema = json.loads((HERE / name).read_text(encoding="utf-8"))
                self.assertEqual(
                    schema["properties"]["effective_lens"]["enum"], expected
                )


class EvidenceOwnershipTests(unittest.TestCase):
    def test_checkpoints_has_no_lens_or_strategy_classifier(self):
        self.assertFalse(hasattr(checkpoints, "classify_strategy"))
        self.assertFalse(hasattr(checkpoints, "failure_family"))
        self.assertFalse(hasattr(checkpoints, "semantic_cycle_after"))

    def test_each_new_semantic_result_opens_one_evidence_window(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "evidence-window")
            storage.start_turn(root, session, "修正責任邊界")
            change = ToolCompleted(
                session,
                "apply_patch",
                tool_input={"cmd": "*** Begin Patch\n+value = 1\n*** End Patch"},
                tool_output={"status": "completed"},
                mutating=True,
            )
            first = evidence.observe_tool_event(root, change)
            replay = evidence.observe_tool_event(root, change)
            verification = evidence.observe_tool_event(
                root,
                ToolCompleted(
                    session,
                    "exec_command",
                    tool_input={"cmd": "pytest tests/test_owner.py"},
                    tool_output="1 passed",
                ),
            )

        self.assertEqual(first.checkpoint["trigger"], "evidence-ready")
        self.assertIsNone(replay.checkpoint)
        self.assertEqual(verification.checkpoint["trigger"], "evidence-ready")

    def test_navigation_is_recorded_without_opening_a_window(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "navigation")
            storage.start_turn(root, session, "閱讀檔案")
            observed = evidence.observe_tool_event(
                root,
                ToolCompleted(
                    session,
                    "exec_command",
                    tool_input={"cmd": "rg owner masters_nudge"},
                    tool_output="masters_nudge/core.py:1:owner",
                ),
            )
            progress = storage.load_progress_state(root, session)

        self.assertIsNone(observed.checkpoint)
        self.assertNotIn("last_strategy_event_seq", progress)
        self.assertNotIn("midturn_review_attempts", progress)
        self.assertNotIn("recent", progress)
        self.assertTrue(progress["last_event_fingerprint"])

    def test_exact_injected_finding_is_detected_without_provider_context(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "exact-dedup", "turn-1")
            reaction = storage.append_reaction(
                root,
                session,
                provider="anthropic",
                model="opus",
                reaction="讓欄位直接擁有責任。",
                route_metadata={"effective_lens": "linus"},
            )
            storage.mark_emitted(
                root,
                session,
                reaction["ts"],
                event_seq=1,
                delivered_via="PostToolUse",
            )
            storage.observe_injected_response(
                root,
                session,
                event_seq=2,
                observation_kind="semantic-event",
                observation={"evidence_category": "change"},
            )

            self.assertTrue(
                storage.was_finding_injected(
                    root, session, "讓欄位直接擁有責任。"
                )
            )
            self.assertFalse(
                storage.was_finding_injected(root, session, "另一項取捨。")
            )


class ClaudeBatchCheckpointTests(unittest.TestCase):
    def test_manifest_uses_post_tool_batch_only_for_tool_checkpoints(self):
        manifest = json.loads(
            (HERE / "plugins" / "masters-nudge" / "hooks" / "claude.json").read_text(
                encoding="utf-8"
            )
        )
        hooks = manifest["hooks"]

        self.assertIn("PostToolBatch", hooks)
        self.assertNotIn("PostToolUse", hooks)
        self.assertNotIn("PostToolUseFailure", hooks)
        self.assertNotIn("matcher", hooks["PostToolBatch"][0])

    def test_claude_batch_normalization_preserves_tool_order_and_payloads(self):
        import claude_checkpoint

        events = claude_checkpoint.normalize_tool_batch(
            {
                "hook_event_name": "PostToolBatch",
                "session_id": "batch-order",
                "tool_calls": [
                    {
                        "tool_name": "Edit",
                        "tool_input": {"file_path": "app.py"},
                        "tool_response": "updated",
                    },
                    {
                        "tool_name": "Bash",
                        "tool_input": {"command": "pytest -q"},
                        "tool_response": "Exit code 1\n1 failed",
                    },
                ],
            }
        )

        self.assertEqual([event.tool_name for event in events], ["Edit", "Bash"])
        self.assertEqual(events[0].tool_input, {"file_path": "app.py"})
        self.assertEqual(events[1].tool_output, "Exit code 1\n1 failed")
        self.assertTrue(events[1].failed)
        self.assertTrue(events[1].failure_known)

    def test_one_native_batch_opens_at_most_one_review_window(self):
        import claude_checkpoint

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            events = claude_checkpoint.normalize_tool_batch(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "one-window",
                    "cwd": str(root),
                    "tool_calls": [
                        {
                            "tool_name": "Edit",
                            "tool_input": {"file_path": "a.py"},
                            "tool_response": "updated",
                        },
                        {
                            "tool_name": "Bash",
                            "tool_input": {"command": "pytest -q"},
                            "tool_response": "1 passed",
                        },
                    ],
                }
            )
            storage.start_turn(root, events[0].session, "完成批次變更")
            observed = evidence.observe_tool_batch(root, events)
            replay = evidence.observe_tool_batch(root, events)

        self.assertEqual(observed.checkpoint["trigger"], "evidence-ready")
        self.assertEqual(observed.event_seq, 1)
        self.assertIsNone(replay.checkpoint)

    def test_claude_batch_output_targets_post_tool_batch(self):
        import claude_checkpoint

        output = claude_checkpoint.build_hook_output(
            "PostToolBatch", "把狀態責任放回唯一擁有者。"
        )

        self.assertEqual(
            output["hookSpecificOutput"]["hookEventName"], "PostToolBatch"
        )


if __name__ == "__main__":
    unittest.main()
