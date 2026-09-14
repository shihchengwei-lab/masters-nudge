"""Tests for the smallest product behavior that must survive refactors."""

from __future__ import annotations

import inspect
import json
import os
import tempfile
import time
import unittest
from dataclasses import fields
from pathlib import Path

import source_context
from masters_nudge import contracts, evidence, plugin_inventory, prompting, storage
from masters_nudge.contracts import NudgeOutcome, SessionRef, ToolCompleted
from masters_nudge.core import NudgeCore


class NudgeContractTests(unittest.TestCase):
    def test_outcome_contains_only_the_grounded_decision_needed_by_the_hook(self):
        self.assertEqual(
            [field.name for field in fields(NudgeOutcome)],
            ["status", "principle", "anchor", "relationship", "evidence_seq"],
        )

    def test_core_accepts_the_packet_directly(self):
        parameters = inspect.signature(NudgeCore.nudge_once).parameters
        self.assertEqual(tuple(parameters), ("self", "source_packet", "timeout_sec"))
        self.assertIsNone(parameters["timeout_sec"].default)

    def test_silence_needs_no_fake_finding_or_evidence(self):
        self.assertEqual(
            NudgeOutcome("no_finding"),
            NudgeOutcome("no_finding", "none", "", "", 0),
        )

    def test_tool_event_keeps_only_native_facts_and_explicit_mutation(self):
        names = [field.name for field in fields(ToolCompleted)]
        self.assertEqual(
            names,
            [
                "session",
                "tool_name",
                "tool_input",
                "tool_output",
                "mutation",
                "native_event_name",
            ],
        )
        for obsolete in ("failed", "failure_known", "mutating"):
            self.assertNotIn(obsolete, names)

    def test_runtime_inventory_has_no_ignored_installation_parameter(self):
        self.assertEqual(tuple(inspect.signature(plugin_inventory.runtime_files).parameters), ())


class EvidenceBoundaryTests(unittest.TestCase):
    def test_recent_nudges_are_a_separate_exclusion_set(self):
        review_input = prompting.build_review_input(
            "CURRENT-PACKET", ("old-nudge-1", "old-nudge-2", "old-nudge-3")
        )
        self.assertIn("[recent returned nudges — exclusions, not evidence]", review_input)
        self.assertLess(review_input.index("old-nudge-3"), review_input.index("CURRENT-PACKET"))
        self.assertEqual(prompting.build_review_input("CURRENT-PACKET", ()), "CURRENT-PACKET")

    def test_exact_native_event_replay_is_the_only_duplicate_guard(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "replay")
            self.assertEqual(storage.record_event(root, session, "event-123"), "first")
            self.assertEqual(storage.record_event(root, session, "event-123"), "duplicate")
            self.assertEqual(storage.record_event(root, session, "event-456"), "new")

    def test_mutation_batch_is_independent_after_a_returned_nudge(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "independent", cwd=raw)
            storage.start_turn(root, session, "檢查每個明確修改批次")
            storage.append_host_returned_nudge(
                root,
                session,
                evidence_seq=1,
                principle="causality",
                anchor="owner",
                relationship="目前的責任可能分散。",
                returned_via="PostToolBatch",
            )
            mutation_input = {"patch": "*** Update File: owner.py\n@@\n-old\n+new"}
            changed = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "unknown",
                        tool_input=mutation_input,
                        tool_output={"status": "anything"},
                        mutation=contracts.mutation_evidence_from_input(mutation_input),
                    )
                ],
            )
            command = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "exec_command",
                        tool_input={"cmd": "pytest -q"},
                        tool_output="1 passed",
                    )
                ],
            )
            state = storage.load_turn_state(root, session)

        self.assertTrue(changed.eligible)
        self.assertFalse(command.eligible)
        self.assertEqual(set(changed.batch_records[0]), {"seq", "content"})
        self.assertNotIn("pending_change", state)
        self.assertNotIn("nudge_pending_validation", state)

    def test_packet_preserves_actual_native_input_and_result(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "raw", cwd=raw)
            storage.start_turn(root, session, "確認原生證據")
            mutation_input = {
                "command": "wrapper --apply",
                "patch": "*** Update File: app.py\n@@\n-old\n+new",
            }
            observed = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "host_tool",
                        tool_input=mutation_input,
                        tool_output={"success": True},
                        mutation=contracts.mutation_evidence_from_input(mutation_input),
                    )
                ],
            )
            packet = source_context.build_checkpoint_packet(
                task_anchor=observed.turn_state["task_anchor"],
                evidence_records=observed.batch_records,
            )

        self.assertIn('"command": "wrapper --apply"', packet)
        self.assertIn('"patch": "*** Update File: app.py', packet)
        self.assertIn('"success": true', packet)
        self.assertNotIn("actual_command:", packet)
        self.assertNotIn("category=", packet)

    def test_turn_state_keeps_no_cross_batch_tool_or_source_history(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "state")
            storage.start_turn(root, session, "不要讀 secret.txt")
            state = storage.load_turn_state(root, session)

        for obsolete in (
            "last_source_context",
            "evidence_seq",
            "evidence_records",
            "pending_change",
            "nudge_pending_validation",
        ):
            self.assertNotIn(obsolete, state)

    def test_source_context_has_no_change_inference_or_related_source_scan_api(self):
        for obsolete in (
            "changed_paths_for_change",
            "related_source_for_change",
            "has_attributable_change",
        ):
            self.assertFalse(hasattr(source_context, obsolete))


class HostReturnedAuditTests(unittest.TestCase):
    def test_latest_three_returned_nudges_feed_deduplication_in_order(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "dedup", cwd=raw)
            for index in range(4):
                storage.append_host_returned_nudge(
                    root,
                    session,
                    evidence_seq=index + 1,
                    principle="causality",
                    anchor=f"owner-{index}",
                    relationship=f"relationship-{index}",
                    returned_via="PostToolBatch",
                )
            recent = storage.read_recent_returned_nudges(root, session, limit=3)

        self.assertEqual(
            recent,
            (
                "causality nudge: owner-1 — relationship-1",
                "causality nudge: owner-2 — relationship-2",
                "causality nudge: owner-3 — relationship-3",
            ),
        )

    def test_host_return_audit_keeps_grounding_sequence(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("claude_code", "audit", cwd=raw)
            storage.append_host_returned_nudge(
                root,
                session,
                evidence_seq=2,
                principle="causality",
                anchor="batch owner",
                relationship="讓單一欄位直接擁有責任。",
                returned_via="PostToolBatch",
            )
            entries = storage.recent_nudges(root, limit=10)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["evidence_seq"], 2)
        self.assertEqual(entries[0]["relationship"], "讓單一欄位直接擁有責任。")

    def test_cleanup_removes_expired_session_data_but_keeps_settings(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "expired", cwd=raw)
            storage.start_turn(root, session, "舊任務")
            storage.append_host_returned_nudge(
                root,
                session,
                evidence_seq=1,
                principle="causality",
                anchor="retry owner",
                relationship="讓重試保留同一個責任擁有者。",
                returned_via="PostToolBatch",
            )
            settings = root / "config.json"
            settings.write_text("{}\n", encoding="utf-8")
            old = time.time() - 31 * 24 * 60 * 60
            for path in root.iterdir():
                if path != settings:
                    os.utime(path, (old, old))

            storage.cleanup_expired_sessions(root, max_age_days=30)

            self.assertTrue(settings.exists())
            self.assertEqual(storage.recent_nudges(root, limit=10), [])
            self.assertEqual(storage.load_turn_state(root, session)["task_anchor"], "")

    def test_recent_nudges_keeps_a_legacy_finding_record(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "legacy", cwd=raw)
            storage.audit_path(root, session).write_text(
                json.dumps({"finding": "舊格式 Nudge"}, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self.assertEqual(storage.recent_nudges(root, limit=10)[0]["finding"], "舊格式 Nudge")


if __name__ == "__main__":
    unittest.main()
