"""Tests for the smallest product behavior that must survive the refactor."""

from __future__ import annotations

import inspect
import json
import os
import subprocess
import tempfile
import time
import unittest
from dataclasses import fields
from pathlib import Path
from subprocess import CompletedProcess
from unittest import mock

import source_context
from masters_nudge import (
    checkpoints,
    contracts,
    evidence,
    plugin_inventory,
    prompting,
    storage,
)
from masters_nudge.contracts import NudgeOutcome, SessionRef, ToolCompleted
from masters_nudge.core import NudgeCore


class NudgeContractTests(unittest.TestCase):
    def test_outcome_contains_only_the_decision_needed_by_the_hook(self):
        self.assertEqual(
            [field.name for field in fields(NudgeOutcome)],
            ["status", "principle", "anchor", "relationship"],
        )

    def test_core_accepts_the_packet_directly(self):
        parameters = inspect.signature(NudgeCore.nudge_once).parameters

        self.assertEqual(tuple(parameters), ("self", "source_packet", "timeout_sec"))
        self.assertIsNone(parameters["timeout_sec"].default)

    def test_silence_needs_no_fake_finding(self):
        self.assertEqual(
            NudgeOutcome("no_finding"),
            NudgeOutcome("no_finding", "none", "", ""),
        )

    def test_contracts_do_not_keep_unconsumed_event_fields_or_types(self):
        with self.subTest(contract="PromptSubmitted"):
            self.assertFalse(hasattr(contracts, "PromptSubmitted"))
        with self.subTest(contract="SessionRef"):
            self.assertEqual(
                [field.name for field in fields(SessionRef)],
                ["host", "session_id", "cwd", "repo_root"],
            )
        with self.subTest(contract="ToolCompleted"):
            self.assertEqual(
                [field.name for field in fields(ToolCompleted)],
                [
                    "session",
                    "tool_name",
                    "tool_input",
                    "tool_output",
                    "failed",
                    "failure_known",
                    "mutating",
                    "native_event_name",
                ],
            )

    def test_runtime_inventory_has_no_ignored_installation_parameter(self):
        self.assertEqual(
            tuple(inspect.signature(plugin_inventory.runtime_files).parameters),
            (),
        )


class EvidenceBoundaryTests(unittest.TestCase):
    def test_recent_nudges_are_a_separate_exclusion_set(self):
        review_input = prompting.build_review_input(
            "CURRENT-PACKET",
            ("old-nudge-1", "old-nudge-2", "old-nudge-3"),
        )

        self.assertIn(
            "[recent returned nudges — exclusions, not evidence]", review_input
        )
        self.assertLess(
            review_input.index("old-nudge-3"), review_input.index("CURRENT-PACKET")
        )
        self.assertEqual(
            prompting.build_review_input("CURRENT-PACKET", ()), "CURRENT-PACKET"
        )

    def test_exact_native_event_replay_is_the_only_duplicate_guard(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "replay")

            self.assertEqual(storage.record_event(root, session, "event-123"), "first")
            self.assertEqual(
                storage.record_event(root, session, "event-123"), "duplicate"
            )
            self.assertEqual(storage.record_event(root, session, "event-456"), "new")

    def test_returned_nudge_defers_the_latest_change_until_an_actor_result(self):
        boundaries = {
            "verification": ToolCompleted(
                SessionRef("codex_cli", "placeholder"),
                "exec_command",
                tool_input={"cmd": "pytest -q"},
                tool_output="1 passed in 0.10s",
            ),
            "failure": ToolCompleted(
                SessionRef("codex_cli", "placeholder"),
                "exec_command",
                tool_input={"cmd": "python app.py"},
                tool_output="Traceback (most recent call last): RuntimeError: broken",
                failed=True,
                failure_known=True,
            ),
            "measurement": ToolCompleted(
                SessionRef("codex_cli", "placeholder"),
                "exec_command",
                tool_input={"cmd": "python benchmark.py"},
                tool_output="median: 12 ms",
            ),
        }
        for category, template in boundaries.items():
            with self.subTest(category=category), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                session = SessionRef("codex_cli", category, cwd=raw)
                storage.start_turn(root, session, "讓 Actor 決定如何處理 Nudge")
                evidence.observe_tool_batch(
                    root,
                    [
                        ToolCompleted(
                            session,
                            "read",
                            tool_input={"path": "owner.py"},
                            tool_output="owner = direct",
                        )
                    ],
                )
                storage.append_host_returned_nudge(
                    root,
                    session,
                    principle="causality",
                    anchor="owner",
                    relationship="目前的責任可能分散。",
                    returned_via="PostToolBatch",
                )

                blocked = evidence.observe_tool_batch(
                    root,
                    [
                        ToolCompleted(
                            session,
                            "apply_patch",
                            tool_input={"patch": "change after Nudge"},
                            tool_output={"status": "completed"},
                            mutating=True,
                        )
                    ],
                )
                still_blocked = evidence.observe_tool_batch(
                    root,
                    [
                        ToolCompleted(
                            session,
                            "apply_patch",
                            tool_input={"patch": "second change before a result"},
                            tool_output={"status": "completed"},
                            mutating=True,
                        )
                    ],
                )
                latest_blocked = evidence.observe_tool_batch(
                    root,
                    [
                        ToolCompleted(
                            session,
                            "apply_patch",
                            tool_input={"patch": "third and latest change"},
                            tool_output={"status": "completed"},
                            mutating=True,
                        )
                    ],
                )
                boundary = evidence.observe_tool_batch(
                    root,
                    [
                        ToolCompleted(
                            session,
                            template.tool_name,
                            tool_input=template.tool_input,
                            tool_output=template.tool_output,
                            failed=template.failed,
                            failure_known=template.failure_known,
                        )
                    ],
                )
                resumed = evidence.observe_tool_batch(
                    root,
                    [
                        ToolCompleted(
                            session,
                            "apply_patch",
                            tool_input={"patch": "later independent change"},
                            tool_output={"status": "completed"},
                            mutating=True,
                        )
                    ],
                )

                self.assertFalse(blocked.eligible)
                self.assertTrue(blocked.turn_state["nudge_pending_validation"])
                self.assertFalse(still_blocked.eligible)
                self.assertTrue(
                    still_blocked.turn_state["nudge_pending_validation"]
                )
                self.assertFalse(latest_blocked.eligible)
                self.assertTrue(
                    latest_blocked.turn_state["nudge_pending_validation"]
                )
                self.assertTrue(boundary.eligible)
                self.assertFalse(boundary.turn_state["nudge_pending_validation"])
                self.assertIsNone(boundary.turn_state["pending_change"])
                self.assertEqual(
                    [record["category"] for record in boundary.batch_records],
                    ["change", category],
                )
                packet_content = "\n".join(
                    record["content"] for record in boundary.batch_records
                )
                self.assertNotIn("owner = direct", packet_content)
                self.assertNotIn("change after Nudge", packet_content)
                self.assertNotIn("second change before a result", packet_content)
                self.assertIn("third and latest change", packet_content)
                self.assertIn(str(template.tool_output), packet_content)
                self.assertTrue(resumed.eligible)

    def test_returned_nudge_without_a_followup_change_ignores_actor_results(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "unchanged-after-nudge", cwd=raw)
            storage.start_turn(root, session, "只在採用 Nudge 後重新檢查")
            storage.append_host_returned_nudge(
                root,
                session,
                principle="causality",
                anchor="owner",
                relationship="目前的責任可能分散。",
                returned_via="PostToolBatch",
            )

            verified = evidence.observe_tool_batch(
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
            failed = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "exec_command",
                        tool_input={"cmd": "python app.py"},
                        tool_output="missing dependency",
                        failed=True,
                        failure_known=True,
                    )
                ],
            )

        self.assertFalse(verified.eligible)
        self.assertFalse(failed.eligible)
        self.assertTrue(failed.turn_state["nudge_pending_validation"])
        self.assertIsNone(failed.turn_state["pending_change"])

    def test_new_turn_clears_a_pending_nudge(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "new-turn", cwd=raw)
            storage.start_turn(root, session, "first task")
            storage.append_host_returned_nudge(
                root,
                session,
                principle="causality",
                anchor="owner",
                relationship="目前的責任可能分散。",
                returned_via="PostToolBatch",
            )
            evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "apply_patch",
                        tool_input={"patch": "change from first task"},
                        tool_output={"status": "completed"},
                        mutating=True,
                    )
                ],
            )
            self.assertTrue(
                storage.load_turn_state(root, session)["nudge_pending_validation"]
            )
            self.assertIsNotNone(
                storage.load_turn_state(root, session)["pending_change"]
            )

            storage.start_turn(root, session, "next task")

            self.assertFalse(
                storage.load_turn_state(root, session)["nudge_pending_validation"]
            )
            self.assertIsNone(
                storage.load_turn_state(root, session)["pending_change"]
            )

    def test_packet_contains_the_actual_command_and_result(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "command", cwd=raw, repo_root=raw)
            storage.start_turn(root, session, "確認實際執行的驗證")
            event = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "pytest tests/test_owner.py -q"},
                tool_output="1 passed in 0.12s",
            )
            observed = evidence.observe_tool_batch(root, [event])
            packet = source_context.build_checkpoint_packet(
                task_anchor=observed.turn_state["task_anchor"],
                task_sources=observed.turn_state["task_sources"],
                evidence_records=observed.batch_records,
            )

        self.assertIn("pytest tests/test_owner.py -q", packet)
        self.assertIn("1 passed in 0.12s", packet)

    def test_turn_state_keeps_no_cross_batch_evidence_history(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "single-evidence-owner")
            storage.start_turn(root, session, "只保留最近來源批次")
            state = storage.load_turn_state(root, session)

        self.assertNotIn("last_source_context", state)
        self.assertNotIn("evidence_seq", state)
        self.assertNotIn("evidence_records", state)
        self.assertFalse(hasattr(storage, "record_evidence"))

    def test_change_evidence_contains_the_current_working_diff(self):
        event = ToolCompleted(
            SessionRef("codex_cli", "diff", cwd="C:/workspace"),
            "apply_patch",
            tool_input={"patch": "*** Update File: app.py"},
            tool_output={"status": "completed"},
            mutating=True,
        )
        with mock.patch.object(
            checkpoints.subprocess,
            "run",
            return_value=CompletedProcess(
                ["git", "diff"],
                0,
                "diff --git a/app.py b/app.py\n+owner = direct\n",
                "",
            ),
        ):
            rendered = checkpoints.render_evidence_record(event)

        self.assertIn("current_diff:", rendered)
        self.assertIn("+owner = direct", rendered)

    def test_change_evidence_contains_an_untracked_new_file(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "tests@example.invalid"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Masters Nudge Tests"],
                cwd=root,
                check=True,
            )
            (root / "anchor.txt").write_text("anchor\n", encoding="utf-8")
            subprocess.run(["git", "add", "anchor.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "anchor"], cwd=root, check=True)
            (root / "new_owner.py").write_text(
                "owner = 'direct'\n", encoding="utf-8"
            )
            event = ToolCompleted(
                SessionRef("codex_cli", "untracked", cwd=raw, repo_root=raw),
                "file_change",
                tool_input={"path": "new_owner.py"},
                tool_output={"status": "completed"},
                mutating=True,
            )

            rendered = checkpoints.render_evidence_record(event)

        self.assertIn("new_owner.py", rendered)
        self.assertIn("owner = 'direct'", rendered)


class HostReturnedAuditTests(unittest.TestCase):
    def test_latest_three_returned_nudges_feed_deduplication_in_order(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "dedup", cwd=raw)
            for index in range(4):
                storage.append_host_returned_nudge(
                    root,
                    session,
                    principle="causality",
                    anchor=f"owner-{index}",
                    relationship=f"relationship-{index}",
                    returned_via="PostToolBatch",
                )

            recent = storage.read_recent_returned_nudges(root, session, limit=3)

        self.assertEqual(
            recent,
            (
                "causality warning: owner-1 — relationship-1",
                "causality warning: owner-2 — relationship-2",
                "causality warning: owner-3 — relationship-3",
            ),
        )

    def test_host_return_creates_one_plain_audit_entry(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("claude_code", "audit", cwd=raw)
            storage.append_host_returned_nudge(
                root,
                session,
                principle="causality",
                anchor="batch owner",
                relationship="讓單一欄位直接擁有責任。",
                returned_via="PostToolBatch",
            )
            entries = storage.recent_nudges(root, limit=10)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["principle"], "causality")
        self.assertEqual(entries[0]["anchor"], "batch owner")
        self.assertEqual(entries[0]["relationship"], "讓單一欄位直接擁有責任。")
        self.assertEqual(entries[0]["returned_via"], "PostToolBatch")
        self.assertIn("time", entries[0])
        self.assertIn("workspace", entries[0])
        for obsolete in (
            "queued",
            "emitted",
            "injected",
            "responded",
            "provider_output",
            "usage",
            "latency_ms",
        ):
            self.assertNotIn(obsolete, entries[0])

    def test_recent_nudges_keeps_a_legacy_finding_record(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "legacy", cwd=raw)
            path = storage.audit_path(root, session)
            path.write_text(
                json.dumps(
                    {
                        "time": "2026-09-01T00:00:00+00:00",
                        "finding": "舊格式 Nudge",
                        "returned_via": "PostToolUse",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            entries = storage.recent_nudges(root, limit=10)

        self.assertEqual(entries[0]["finding"], "舊格式 Nudge")

    def test_cleanup_removes_an_expired_session_but_keeps_global_settings(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "expired", cwd=raw)
            storage.start_turn(root, session, "舊任務")
            storage.append_host_returned_nudge(
                root,
                session,
                principle="causality",
                anchor="retry owner",
                relationship="讓重試保留同一個責任擁有者。",
                returned_via="PostToolUse",
            )
            settings = root / "config.json"
            settings.write_text(
                '{"provider":"","model":"","ollama_url":"http://127.0.0.1:11434"}\n',
                encoding="utf-8",
            )
            old = time.time() - 31 * 24 * 60 * 60
            for path in root.iterdir():
                if path != settings:
                    os.utime(path, (old, old))

            storage.cleanup_expired_sessions(root, max_age_days=30)

            self.assertTrue(settings.exists())
            self.assertEqual(storage.recent_nudges(root, limit=10), [])
            self.assertEqual(storage.load_turn_state(root, session)["task_anchor"], "")


if __name__ == "__main__":
    unittest.main()
