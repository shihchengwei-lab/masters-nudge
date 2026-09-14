"""The event pipeline preserves facts instead of inferring tool semantics."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import source_context
from masters_nudge import checkpoints, contracts, evidence, provider_contract, storage
from masters_nudge.codex_adapter import normalize_tool_batch
from masters_nudge.contracts import SessionRef, ToolCompleted


class ExplicitMutationEvidenceTests(unittest.TestCase):
    def test_only_structured_mutation_payloads_create_mutation_evidence(self):
        cases = (
            ({"patch": "*** Update File: app.py"}, "patch"),
            ({"diff": "diff --git a/app.py b/app.py"}, "diff"),
            (
                {"path": "app.py", "old_string": "same", "new_string": "same"},
                "replacement",
            ),
            ({"file_path": "empty.txt", "content": ""}, "content"),
            ({"command": "echo build"}, None),
            ({"text": "preview only"}, None),
            ({"path": "app.py"}, None),
            ({"patch": ""}, None),
            ({"diff": 7}, None),
            ({"path": "", "content": ""}, None),
            ({"path": "app.py", "old_string": 1, "new_string": "next"}, None),
            ({"payload": {"path": "app.py", "content": "hidden"}}, None),
        )

        for payload, expected in cases:
            with self.subTest(payload=payload):
                mutation = contracts.mutation_evidence_from_input(payload)
                self.assertEqual(
                    None if mutation is None else mutation.kind,
                    expected,
                )

    def test_codex_adapter_does_not_infer_mutation_from_tool_name(self):
        events = normalize_tool_batch(
            {
                "hook_event_name": "PostToolBatch",
                "session_id": "explicit-mutation",
                "cwd": "",
                "tool_calls": [
                    {
                        "tool_name": "write_file_preview",
                        "tool_input": {"text": "proposed only"},
                        "tool_response": {"success": True},
                    },
                    {
                        "tool_name": "mcp__docs__edit_document",
                        "tool_input": {"path": "doc.md", "content": ""},
                        "tool_response": {"success": True},
                    },
                ],
            }
        )

        self.assertIsNotNone(events)
        self.assertIsNone(events[0].mutation)
        self.assertEqual(events[1].mutation.kind, "content")

    def test_codex_apply_patch_command_is_explicit_mutation(self):
        events = normalize_tool_batch(
            {
                "hook_event_name": "PostToolBatch",
                "session_id": "codex-apply-patch-command",
                "cwd": "",
                "tool_calls": [
                    {
                        "tool_name": "apply_patch",
                        "tool_input": {
                            "command": (
                                "*** Begin Patch\n"
                                "*** Update File: app.py\n"
                                "@@\n"
                                "-old\n"
                                "+new\n"
                                "*** End Patch"
                            )
                        },
                        "tool_response": "Success. Updated app.py",
                    }
                ],
            }
        )

        self.assertIsNotNone(events)
        self.assertEqual(events[0].mutation.kind, "patch")

    def test_codex_command_fallback_rejects_non_patch_and_other_tools(self):
        events = normalize_tool_batch(
            {
                "hook_event_name": "PostToolBatch",
                "session_id": "codex-command-controls",
                "cwd": "",
                "tool_calls": [
                    {
                        "tool_name": "apply_patch",
                        "tool_input": {"command": "Write app.py"},
                        "tool_response": "done",
                    },
                    {
                        "tool_name": "exec",
                        "tool_input": (
                            'const patch = "*** Begin Patch\\n'
                            '*** Update File: app.py\\n*** End Patch"; '
                            "await tools.apply_patch(patch);"
                        ),
                        "tool_response": "done",
                    },
                    {
                        "tool_name": "exec_command",
                        "tool_input": {
                            "command": (
                                "*** Begin Patch\n"
                                "*** Delete File: app.py\n"
                                "*** End Patch"
                            )
                        },
                        "tool_response": "done",
                    },
                ],
            }
        )

        self.assertIsNotNone(events)
        self.assertTrue(all(event.mutation is None for event in events))

    def test_raw_input_is_not_rewritten_or_dropped(self):
        event = ToolCompleted(
            SessionRef("codex_cli", "raw"),
            "host_tool",
            tool_input={
                "command": "wrapper --mode apply",
                "patch": "*** Update File: app.py\n@@\n-old\n+new",
            },
            tool_output={"success": True},
            mutation=contracts.MutationEvidence("patch"),
        )

        rendered = checkpoints.render_evidence_record(event)

        self.assertIn('"command": "wrapper --mode apply"', rendered)
        self.assertIn('"patch": "*** Update File: app.py', rendered)
        self.assertNotIn("actual_command:", rendered)


class FactualControlFlowTests(unittest.TestCase):
    def test_nudge_does_not_create_a_cross_batch_pairing_state(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "no-pairing", cwd=raw)
            storage.start_turn(root, session, "inspect each mutation batch")
            storage.append_host_returned_nudge(
                root,
                session,
                evidence_seq=1,
                principle="causality",
                anchor="owner",
                relationship="gap",
                returned_via="PostToolBatch",
            )
            mutation_input = {"patch": "change after Nudge"}
            changed = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "unknown_tool_name",
                        tool_input=mutation_input,
                        tool_output={"success": True},
                        mutation=contracts.mutation_evidence_from_input(mutation_input),
                    )
                ],
            )
            later_command = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "exec_command",
                        tool_input={"cmd": "echo build"},
                        tool_output={"exit_code": 0, "output": "build"},
                    )
                ],
            )
            state = storage.load_turn_state(root, session)

        self.assertTrue(changed.eligible)
        self.assertFalse(later_command.eligible)
        self.assertNotIn("nudge_pending_validation", state)
        self.assertNotIn("pending_change", state)

    def test_records_have_no_inferred_engineering_category(self):
        mutation_input = {"diff": "diff --git a/a.py b/a.py"}
        event = ToolCompleted(
            SessionRef("codex_cli", "no-category"),
            "anything",
            tool_input=mutation_input,
            tool_output="done",
            mutation=contracts.mutation_evidence_from_input(mutation_input),
        )
        with tempfile.TemporaryDirectory() as raw:
            observed = evidence.observe_tool_batch(Path(raw), [event])
            packet = source_context.build_checkpoint_packet(
                task_anchor="task",
                evidence_records=observed.batch_records,
            )

        self.assertEqual(observed.batch_records[0].keys(), {"seq", "content"})
        self.assertIn("[tool result seq=1]", packet)
        self.assertNotIn("category=", packet)
        self.assertFalse(hasattr(checkpoints, "evidence_category"))

    def test_task_path_mentions_do_not_cause_implicit_file_reads(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "secret.txt").write_text("must not enter packet", encoding="utf-8")
            session = SessionRef("codex_cli", "no-task-scan", cwd=raw, repo_root=raw)

            storage.start_turn(
                root / "data",
                session,
                "不要讀 secret.txt，只修改 app.py",
            )
            state = storage.load_turn_state(root / "data", session)

        self.assertNotIn("task_sources", state)
        self.assertNotIn("must not enter packet", json.dumps(state, ensure_ascii=False))


class GroundedProviderContractTests(unittest.TestCase):
    def test_finding_identifies_the_visible_evidence_record(self):
        result = provider_contract.parse_nudge_result(
            json.dumps(
                {
                    "status": "finding",
                    "principle": "causality",
                    "evidence_seq": 2,
                    "anchor": "owner",
                    "relationship": "依賴沒有明確完成邊界。",
                },
                ensure_ascii=False,
            )
        )

        self.assertEqual(result["status"], "finding")
        self.assertEqual(result["evidence_seq"], 2)

    def test_finding_without_evidence_sequence_is_invalid(self):
        result = provider_contract.parse_nudge_result(
            json.dumps(
                {
                    "status": "finding",
                    "principle": "causality",
                    "anchor": "owner",
                    "relationship": "依賴沒有明確完成邊界。",
                },
                ensure_ascii=False,
            )
        )

        self.assertEqual(result["status"], "error")

    def test_no_finding_uses_zero_evidence_sequence(self):
        result = provider_contract.parse_nudge_result(
            json.dumps(
                {
                    "status": "no_finding",
                    "principle": "none",
                    "evidence_seq": 0,
                    "anchor": "",
                    "relationship": "",
                }
            )
        )

        self.assertEqual(result["status"], "no_finding")
        self.assertEqual(result["evidence_seq"], 0)


if __name__ == "__main__":
    unittest.main()
