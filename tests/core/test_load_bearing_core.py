"""Tests for the smallest product behavior that must survive the refactor."""

from __future__ import annotations

import inspect
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
from masters_nudge import checkpoints, contracts, evidence, plugin_inventory, storage
from masters_nudge.contracts import NudgeOutcome, SessionRef, ToolCompleted
from masters_nudge.core import NudgeCore


ROOT = Path(__file__).resolve().parents[2]


class NudgeContractTests(unittest.TestCase):
    def test_outcome_contains_only_the_decision_needed_by_the_hook(self):
        self.assertEqual(
            [field.name for field in fields(NudgeOutcome)],
            ["status", "finding", "lens"],
        )

    def test_core_accepts_the_packet_directly(self):
        parameters = inspect.signature(NudgeCore.nudge_once).parameters

        self.assertEqual(tuple(parameters), ("self", "source_packet", "timeout_sec"))
        self.assertIsNone(parameters["timeout_sec"].default)

    def test_silence_needs_no_fake_finding_or_lens(self):
        self.assertEqual(NudgeOutcome("no_finding"), NudgeOutcome("no_finding", "", ""))

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

    def test_batch_only_runtime_has_no_single_event_observer(self):
        self.assertFalse(hasattr(evidence, "observe_tool_event"))


class EvidenceBoundaryTests(unittest.TestCase):
    def test_prompt_waits_for_a_check_after_the_latest_change(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn(
            "Do not form a finding about the latest change until the packet shows a\n"
            "subsequent check of that change.",
            prompt,
        )
        self.assertIn("Successful application alone is not a check.", prompt)

    def test_exact_native_event_replay_is_the_only_duplicate_guard(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "replay")

            self.assertTrue(storage.record_event(root, session, "event-123"))
            self.assertFalse(storage.record_event(root, session, "event-123"))
            self.assertTrue(storage.record_event(root, session, "event-456"))

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
            storage.record_evidence(
                root,
                session,
                category=checkpoints.evidence_category(event),
                content=checkpoints.render_evidence_record(event),
            )
            state = storage.load_turn_state(root, session)
            packet = source_context.build_checkpoint_packet(
                task_anchor=state["task_anchor"],
                task_sources=state["task_sources"],
                evidence_records=state["evidence_records"],
            )

        self.assertIn("pytest tests/test_owner.py -q", packet)
        self.assertIn("1 passed in 0.12s", packet)

    def test_only_a_small_number_of_recent_results_is_retained(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "bounded")
            storage.start_turn(root, session, "保持證據聚焦")
            for index in range(12):
                storage.record_evidence(
                    root,
                    session,
                    category="verification",
                    content=f"verification-{index}",
                )
            records = storage.load_turn_state(root, session)["evidence_records"]

        verification = [
            item for item in records if item.get("category") == "verification"
        ]
        self.assertLessEqual(len(verification), 3)
        self.assertEqual(verification[-1]["content"], "verification-11")

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
    def test_host_return_creates_one_plain_audit_entry(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("claude_code", "audit", cwd=raw)
            storage.append_host_returned_nudge(
                root,
                session,
                lens="simplicity",
                finding="讓單一欄位直接擁有責任。",
                returned_via="PostToolBatch",
            )
            entries = storage.recent_nudges(root, limit=10)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["lens"], "simplicity")
        self.assertEqual(entries[0]["finding"], "讓單一欄位直接擁有責任。")
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

    def test_cleanup_removes_an_expired_session_but_keeps_global_settings(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "expired", cwd=raw)
            storage.start_turn(root, session, "舊任務")
            storage.append_host_returned_nudge(
                root,
                session,
                lens="reliability",
                finding="讓重試保留同一個責任擁有者。",
                returned_via="PostToolBatch",
            )
            settings = root / "config.json"
            settings.write_text('{"lens":"automatic"}\n', encoding="utf-8")
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
