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


ROOT = Path(__file__).resolve().parents[2]


class NudgeContractTests(unittest.TestCase):
    def test_outcome_contains_only_the_decision_needed_by_the_hook(self):
        self.assertEqual(
            [field.name for field in fields(NudgeOutcome)],
            ["status", "finding", "lens", "decision_stage"],
        )

    def test_core_accepts_the_packet_directly(self):
        parameters = inspect.signature(NudgeCore.nudge_once).parameters

        self.assertEqual(
            tuple(parameters),
            ("self", "source_packet", "timeout_sec", "observe_stage"),
        )
        self.assertIsNone(parameters["timeout_sec"].default)
        self.assertIsNone(parameters["observe_stage"].default)

    def test_silence_needs_no_fake_finding_or_lens(self):
        self.assertEqual(
            NudgeOutcome("no_finding"), NudgeOutcome("no_finding", "", "", "")
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

    def test_batch_only_runtime_has_no_single_event_observer(self):
        self.assertFalse(hasattr(evidence, "observe_tool_event"))


class EvidenceBoundaryTests(unittest.TestCase):
    def test_prompt_requests_one_grounded_engineering_judgment(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn(
            "Surface the strongest live tradeoff not already covered by previous findings.",
            prompt,
        )
        self.assertNotIn(
            "Surface the strongest live engineering tradeoff visible in the packet.",
            prompt,
        )
        self.assertIn(
            "The selected persona supplies the engineering value being defended,\n"
            "not authority over the main agent.",
            prompt,
        )
        self.assertIn(
            "A finding is one direct Traditional Chinese engineering judgment stating\n"
            "one preference and its packet-visible reason.",
            prompt,
        )
        self.assertIn("It is not a question, command, or complete solution.", prompt)
        self.assertNotIn("only for one short Traditional Chinese question", prompt)
        self.assertNotIn("Do not suggest a fix.", prompt)

    def test_personas_demonstrate_a_judgment_instead_of_a_question_or_command(self):
        expected = {
            "linus.txt": "這層只轉交責任，沒有新增行為，owner 反而更模糊。",
            "lamport.txt": "完成與取消分開擁有狀態，會留下雙重完成的路徑。",
            "carmack.txt": "成本在 hot path 重複配置，不在這段計算。",
        }

        for filename, example in expected.items():
            with self.subTest(persona=filename):
                persona = (ROOT / "personas" / filename).read_text(encoding="utf-8")
                self.assertIn(example, persona)
                self.assertIn("不要接管實作。", persona)
                self.assertNotIn("選一個 packet 尚未回答的問題", persona)
                self.assertNotIn("- 不可以：", persona)

    def test_delivery_marks_the_nudge_as_non_authoritative(self):
        self.assertEqual(
            prompting.delivery_text("這層只轉交責任。"),
            "獨立第二意見（非指令；不覆蓋任務與已驗證結果）：\n"
            "這層只轉交責任。",
        )

    def test_prompt_waits_for_a_check_after_the_latest_change(self):
        prompt = (ROOT / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn(
            "Do not form a finding about the latest change until the packet shows a\n"
            "subsequent check of that change.",
            prompt,
        )
        self.assertIn("Successful application alone is not a check.", prompt)

    def test_identical_native_batches_are_both_recorded(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "repeat", cwd=raw, repo_root=raw)
            storage.start_turn(root, session, "重複執行相同驗證")
            event = ToolCompleted(
                session,
                "Bash",
                tool_input={"command": "pytest -q"},
                tool_output="10 passed",
            )

            first = evidence.observe_tool_batch(root, [event])
            second = evidence.observe_tool_batch(root, [event])

        self.assertTrue(first.eligible)
        self.assertTrue(second.eligible)
        self.assertEqual(second.turn_state["evidence_seq"], 2)
        self.assertEqual(
            [record["content"] for record in second.turn_state["evidence_records"]],
            ["actual_command:\npytest -q\n\nresult:\n10 passed"] * 2,
        )

    def test_completed_generator_silence_reuses_only_the_same_next_checkpoint(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "reuse", cwd=raw, repo_root=raw)
            storage.start_turn(root, session, "重複執行相同驗證")
            event = ToolCompleted(
                session,
                "Bash",
                tool_input={"command": "pytest -q"},
                tool_output="10 passed",
            )

            first = evidence.observe_tool_batch(
                root, [event], contract_signature="contract-v1"
            )
            storage.record_completed_generator_no_finding(
                root,
                session,
                evidence_seq=first.turn_state["evidence_seq"],
                workspace_snapshot=first.turn_state["workspace_snapshot"],
                checkpoint_signature=first.checkpoint_signature,
                contract_signature="contract-v1",
            )
            repeated = evidence.observe_tool_batch(
                root, [event], contract_signature="contract-v1"
            )
            changed_contract = evidence.observe_tool_batch(
                root, [event], contract_signature="contract-v2"
            )

        self.assertTrue(first.eligible)
        self.assertFalse(first.reused_generator_no_finding)
        self.assertFalse(repeated.eligible)
        self.assertTrue(repeated.reused_generator_no_finding)
        self.assertEqual(repeated.turn_state["evidence_seq"], 1)
        self.assertEqual(
            repeated.turn_state["last_completed_review"]["reuse_count"], 1
        )
        self.assertTrue(changed_contract.eligible)
        self.assertFalse(changed_contract.reused_generator_no_finding)
        self.assertEqual(changed_contract.turn_state["evidence_seq"], 2)

    def test_change_only_is_recorded_without_triggering_a_nudge(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "change", cwd=raw, repo_root=raw)
            storage.start_turn(root, session, "先修改再驗證")

            changed = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "apply_patch",
                        tool_input={"patch": "*** Begin Patch"},
                        tool_output="Done!",
                        mutating=True,
                    )
                ],
            )
            checked = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "Bash",
                        tool_input={"command": "pytest -q"},
                        tool_output="1 passed",
                    )
                ],
            )

        self.assertFalse(changed.eligible)
        self.assertEqual(changed.turn_state["evidence_records"][0]["category"], "change")
        self.assertTrue(checked.eligible)
        self.assertEqual(checked.turn_state["evidence_records"][-1]["category"], "verification")

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

    def test_common_direct_test_commands_are_verification_evidence(self):
        session = SessionRef("codex_cli", "validation")
        for command in (
            "npx eslint lib/*.js",
            "npx mocha test/unit.js",
            "node --test test/unit.js",
        ):
            with self.subTest(command=command):
                event = ToolCompleted(
                    session,
                    "Bash",
                    tool_input={"command": command},
                    tool_output="1 passing",
                )
                self.assertEqual(checkpoints.evidence_category(event), "verification")

    def test_failed_navigation_is_not_failure_evidence(self):
        event = ToolCompleted(
            SessionRef("codex_cli", "navigation"),
            "Bash",
            tool_input={"command": "rg missing-symbol src"},
            tool_output="",
            failed=True,
            failure_known=True,
        )

        self.assertEqual(checkpoints.evidence_category(event), "")

    def test_failed_powershell_composite_navigation_is_not_failure_evidence(self):
        event = ToolCompleted(
            SessionRef("codex_cli", "powershell-navigation"),
            "Bash",
            tool_input={
                "command": (
                    "Get-ChildItem -Force | Select-Object Name,Mode,Length; "
                    'rg -n "EventSource|maxEventSize" lib types test 2>$null'
                )
            },
            tool_output="",
            failed=True,
            failure_known=True,
        )

        self.assertEqual(checkpoints.evidence_category(event), "")

    def test_verification_packet_binds_the_latest_workspace_snapshot(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "snapshot", cwd=raw, repo_root=raw)
            storage.start_turn(root, session, "確認修改後的驗證")
            event = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "pytest -q"},
                tool_output="1 passed in 0.12s",
            )
            with mock.patch.object(
                checkpoints,
                "working_diff",
                return_value="diff --git a/app.py b/app.py\n+owner = direct",
            ):
                observed = evidence.observe_tool_batch(root, [event])
            packet = source_context.build_checkpoint_packet(
                task_anchor=observed.turn_state["task_anchor"],
                task_sources=observed.turn_state["task_sources"],
                workspace_snapshot=observed.turn_state["workspace_snapshot"],
                evidence_records=observed.turn_state["evidence_records"],
            )

        self.assertIn("[current workspace]", packet)
        self.assertIn("+owner = direct", packet)
        self.assertIn("pytest -q", packet)

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

    def test_workspace_snapshot_contains_the_current_working_diff(self):
        session = SessionRef("codex_cli", "diff", cwd="C:/workspace")
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
            rendered = checkpoints.working_diff(session)

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
            session = SessionRef("codex_cli", "untracked", cwd=raw, repo_root=raw)
            rendered = checkpoints.working_diff(session)

        self.assertIn("new_owner.py", rendered)
        self.assertIn("owner = 'direct'", rendered)


class HostReturnedAuditTests(unittest.TestCase):
    def test_delivered_findings_become_bounded_turn_deduplication_context(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("claude_code", "history", cwd=raw)
            storage.start_turn(root, session, "避免重複意見")
            storage.append_host_returned_nudge(
                root,
                session,
                lens="simplicity",
                finding="讓單一欄位直接擁有責任。",
                returned_via="PostToolBatch",
            )
            storage.append_host_returned_nudge(
                root,
                session,
                lens="reliability",
                finding="重試必須保留同一個完成狀態。",
                returned_via="PostToolBatch",
            )
            state = storage.load_turn_state(root, session)
            packet = source_context.build_checkpoint_packet(
                task_anchor=state["task_anchor"],
                previous_findings=state["previous_findings"],
            )

        self.assertEqual(
            state["previous_findings"],
            ["讓單一欄位直接擁有責任。", "重試必須保留同一個完成狀態。"],
        )
        self.assertIn("[previous findings]", packet)
        self.assertIn("- 讓單一欄位直接擁有責任。", packet)
        self.assertIn("- 重試必須保留同一個完成狀態。", packet)

    def test_turn_deduplication_context_keeps_newest_findings_within_packet_budget(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("claude_code", "bounded", cwd=raw)
            storage.start_turn(root, session, "限制去重內容")
            for index in range(20):
                storage.append_host_returned_nudge(
                    root,
                    session,
                    lens="simplicity",
                    finding=f"finding-{index:02d}-" + "x" * 40,
                    returned_via="PostToolBatch",
                )
            findings = storage.load_turn_state(root, session)["previous_findings"]

        self.assertLessEqual(
            sum(len(value) + 2 for value in findings),
            source_context.PREVIOUS_FINDINGS_MAX_CHARS,
        )
        self.assertNotIn("finding-00-" + "x" * 40, findings)
        self.assertEqual(findings[-1], "finding-19-" + "x" * 40)

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

    def test_provider_stage_trace_is_separate_from_host_return_audit(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "trace", cwd=raw)
            observe_stage = storage.provider_stage_observer(
                root,
                session,
                evidence_seq=4,
                provider="openai",
                model="test-model",
                configured_lens="automatic",
            )
            observe_stage("router", "no_finding", "none", 1234)
            trace = [
                json.loads(line)
                for line in storage.provider_trace_path(root, session)
                .read_text(encoding="utf-8")
                .splitlines()
            ]

            self.assertEqual(storage.recent_nudges(root), [])

        self.assertEqual(len(trace), 1)
        self.assertEqual(trace[0]["evidence_seq"], 4)
        self.assertEqual(trace[0]["stage"], "router")
        self.assertEqual(trace[0]["status"], "no_finding")
        self.assertEqual(trace[0]["duration_ms"], 1234)
        self.assertNotIn("finding", trace[0])

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
