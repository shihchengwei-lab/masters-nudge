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
            ["status", "finding", "lens"],
        )

    def test_core_accepts_the_packet_directly(self):
        parameters = inspect.signature(NudgeCore.nudge_once).parameters

        self.assertEqual(tuple(parameters), ("self", "source_packet", "timeout_sec"))
        self.assertIsNone(parameters["timeout_sec"].default)

    def test_silence_needs_no_fake_finding_or_lens(self):
        self.assertEqual(
            NudgeOutcome("no_finding"), NudgeOutcome("no_finding", "", "")
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
            "A finding identifies one concrete mechanism in the packet, the behavior\n"
            "that mechanism is meant to defend, and the preferred tradeoff.",
            prompt,
        )
        self.assertIn("Generic advice must return no_finding.", prompt)
        self.assertIn("It is not a question, command, or complete solution.", prompt)
        self.assertNotIn("only for one short Traditional Chinese question", prompt)
        self.assertNotIn("Do not suggest a fix.", prompt)

    def test_personas_do_not_anchor_the_provider_with_stock_examples(self):
        for filename in ("linus.txt", "lamport.txt", "carmack.txt"):
            with self.subTest(persona=filename):
                persona = (ROOT / "personas" / filename).read_text(encoding="utf-8")
                self.assertNotIn("- 範例：", persona)
                self.assertIn("不要接管實作。", persona)
                self.assertNotIn("選一個 packet 尚未回答的問題", persona)
                self.assertNotIn("- 不可以：", persona)

    def test_linus_scene_checks_what_each_mechanism_actually_defends(self):
        persona = (ROOT / "personas" / "linus.txt").read_text(encoding="utf-8")

        self.assertIn("沿著 packet 顯示的實際 control flow 往前走", persona)
        self.assertIn("拿掉這段，哪條路會失去保證？", persona)
        self.assertIn("若兩段守的是不同入口", persona)
        self.assertIn("又讓多少分支真正消失", persona)
        self.assertIn("拿掉這一層，哪個可見 caller 會失去行為？", persona)
        self.assertIn("這個新概念消滅的分支，比它新增的責任多嗎？", persona)

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

    def test_same_revision_and_evidence_class_is_admitted_only_once_but_recorded(self):
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

            with mock.patch.object(
                checkpoints,
                "workspace_state",
                return_value=checkpoints.WorkspaceState("", "revision-1"),
            ):
                first = evidence.observe_tool_batch(
                    root, [event], contract_signature="contract-v1"
                )
                storage.record_completed_review(
                    root,
                    session,
                    workspace_revision_signature=first.workspace_revision_signature,
                    contract_signature="contract-v1",
                    evidence_classes=first.evidence_classes,
                )
                second = evidence.observe_tool_batch(
                    root, [event], contract_signature="contract-v1"
                )

        self.assertTrue(first.eligible)
        self.assertFalse(second.eligible)
        self.assertEqual(second.turn_state["evidence_seq"], 2)
        self.assertEqual(
            [record["content"] for record in second.turn_state["evidence_records"]],
            ["actual_command:\npytest -q\n\nresult:\n10 passed"] * 2,
        )

    def test_new_evidence_class_contract_or_revision_starts_a_new_decision(self):
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

            with mock.patch.object(
                checkpoints,
                "workspace_state",
                return_value=checkpoints.WorkspaceState("", "revision-1"),
            ):
                first = evidence.observe_tool_batch(
                    root, [event], contract_signature="contract-v1"
                )
                storage.record_completed_review(
                    root,
                    session,
                    workspace_revision_signature=first.workspace_revision_signature,
                    contract_signature="contract-v1",
                    evidence_classes=first.evidence_classes,
                )
                repeated = evidence.observe_tool_batch(
                    root, [event], contract_signature="contract-v1"
                )
                failure = evidence.observe_tool_batch(
                    root,
                    [
                        ToolCompleted(
                            session,
                            "Bash",
                            tool_input={"command": "pytest -q"},
                            tool_output="1 failed",
                            failed=True,
                            failure_known=True,
                        )
                    ],
                    contract_signature="contract-v1",
                )
                changed_contract = evidence.observe_tool_batch(
                    root, [event], contract_signature="contract-v2"
                )
            with mock.patch.object(
                checkpoints,
                "workspace_state",
                return_value=checkpoints.WorkspaceState("", "revision-2"),
            ):
                changed_revision = evidence.observe_tool_batch(
                    root, [event], contract_signature="contract-v1"
                )

        self.assertTrue(first.eligible)
        self.assertFalse(repeated.eligible)
        self.assertTrue(failure.eligible)
        self.assertTrue(changed_contract.eligible)
        self.assertTrue(changed_revision.eligible)

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

    def test_non_git_change_starts_a_new_observed_generation(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "fallback", cwd=raw)
            storage.start_turn(root, session, "修改後重新驗證")
            check = ToolCompleted(
                session,
                "exec_command",
                tool_input={"cmd": "pytest -q"},
                tool_output="1 passed",
            )
            first = evidence.observe_tool_batch(
                root, [check], contract_signature="contract-v1"
            )
            storage.record_completed_review(
                root,
                session,
                workspace_revision_signature=first.workspace_revision_signature,
                contract_signature="contract-v1",
                evidence_classes=first.evidence_classes,
            )
            repeated = evidence.observe_tool_batch(
                root, [check], contract_signature="contract-v1"
            )
            evidence.observe_tool_batch(
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
                contract_signature="contract-v1",
            )
            after_change = evidence.observe_tool_batch(
                root, [check], contract_signature="contract-v1"
            )

        self.assertFalse(repeated.eligible)
        self.assertTrue(after_change.eligible)
        self.assertNotEqual(
            first.workspace_revision_signature,
            after_change.workspace_revision_signature,
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
                "workspace_state",
                return_value=checkpoints.WorkspaceState(
                    "diff --git a/app.py b/app.py\n+owner = direct",
                    "revision-1",
                ),
            ):
                observed = evidence.observe_tool_batch(root, [event])
            packet = source_context.build_checkpoint_packet(
                task_anchor=observed.turn_state["task_anchor"],
                task_sources=observed.turn_state["task_sources"],
                workspace_snapshot=observed.turn_state["workspace_snapshot"],
                evidence_records=observed.turn_state["evidence_records"],
            )

        self.assertIn("[current workspace — authoritative]", packet)
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

    def test_workspace_snapshot_gives_each_hunk_part_of_the_fixed_budget(self):
        noisy_lines = "\n".join(
            f"+unrelated_change_{index:04d} = True" for index in range(300)
        )
        raw_diff = (
            "diff --git a/noisy.py b/noisy.py\n"
            "--- a/noisy.py\n"
            "+++ b/noisy.py\n"
            "@@ -1,0 +1,300 @@\n"
            f"{noisy_lines}\n"
            "diff --git a/agent.js b/agent.js\n"
            "--- a/agent.js\n"
            "+++ b/agent.js\n"
            "@@ -10 +10 @@\n"
            "+dispatcherDefault = kStringMaxLength\n"
            "diff --git a/stream.js b/stream.js\n"
            "--- a/stream.js\n"
            "+++ b/stream.js\n"
            "@@ -20 +20 @@\n"
            "+streamDefault = kStringMaxLength\n"
        )

        rendered = checkpoints.render_workspace_diff(
            raw_diff, checkpoints.CHANGE_MAX_CHARS
        )

        self.assertLessEqual(len(rendered), checkpoints.CHANGE_MAX_CHARS)
        self.assertIn("unrelated_change_0000", rendered)
        self.assertIn("dispatcherDefault = kStringMaxLength", rendered)
        self.assertIn("streamDefault = kStringMaxLength", rendered)

    def test_untracked_files_share_the_workspace_budget(self):
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
            (root / "a.txt").write_text("a" * 4000, encoding="utf-8")
            (root / "b.txt").write_text("B_VISIBLE", encoding="utf-8")
            (root / "c.txt").write_text("C_VISIBLE", encoding="utf-8")

            rendered = checkpoints.working_diff(
                SessionRef("codex_cli", "untracked-budget", cwd=raw)
            )

        self.assertLessEqual(len(rendered), checkpoints.CHANGE_MAX_CHARS)
        self.assertIn("B_VISIBLE", rendered)
        self.assertIn("C_VISIBLE", rendered)

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

    def test_revision_signature_covers_untracked_files_hidden_from_the_packet(self):
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
            for name in ("a.txt", "b.txt", "c.txt"):
                (root / name).write_text(name, encoding="utf-8")
            hidden = root / "z.txt"
            hidden.write_text("first", encoding="utf-8")
            session = SessionRef("codex_cli", "full-revision", cwd=raw)

            first = checkpoints.workspace_state(session)
            hidden.write_text("second", encoding="utf-8")
            second = checkpoints.workspace_state(session)

        self.assertEqual(first.snapshot, second.snapshot)
        self.assertNotEqual(first.revision_signature, second.revision_signature)

    def test_current_workspace_owns_state_and_historical_patch_body_is_omitted(self):
        packet = source_context.build_checkpoint_packet(
            task_anchor="修正錯誤處理",
            workspace_snapshot=(
                "diff --git a/stream.js b/stream.js\n"
                "- error?.code === 'OLD_CODE'\n"
                "+ error instanceof EventSourceStreamError"
            ),
            evidence_records=[
                {
                    "seq": 1,
                    "category": "change",
                    "content": (
                        "actual_command:\n*** Begin Patch\n"
                        "- HISTORICAL_ONLY_BRANCH\n+ replacement"
                    ),
                },
                {
                    "seq": 2,
                    "category": "verification",
                    "content": "actual_command:\npytest -q\n\nresult:\n1 passed",
                },
            ],
        )

        self.assertIn("[current workspace — authoritative]", packet)
        self.assertIn("'-' means removed/not current", packet)
        self.assertIn("'+' means present/current", packet)
        self.assertIn("[tool history — ordered past events]", packet)
        self.assertIn("[evidence seq=1 category=change]", packet)
        self.assertIn("details omitted because current workspace", packet)
        self.assertNotIn("HISTORICAL_ONLY_BRANCH", packet)
        self.assertIn("pytest -q", packet)

    def test_non_git_packet_retains_change_body_when_current_state_is_unavailable(self):
        packet = source_context.build_checkpoint_packet(
            task_anchor="修正錯誤處理",
            evidence_records=[
                {
                    "seq": 1,
                    "category": "change",
                    "content": "actual_command:\n- old_branch\n+ replacement",
                }
            ],
        )

        self.assertIn("current workspace unavailable", packet)
        self.assertIn("- old_branch", packet)
        self.assertIn("+ replacement", packet)

    def test_packet_budget_preserves_the_authoritative_workspace_section(self):
        records = []
        for index, category in enumerate(
            ("verification", "verification", "failure", "failure", "measurement", "measurement"),
            start=1,
        ):
            records.append(
                {
                    "seq": index,
                    "category": category,
                    "content": f"{category}-{index}-" + "r" * 2000,
                }
            )
        packet = source_context.build_checkpoint_packet(
            task_anchor="t" * source_context.TASK_ANCHOR_MAX_CHARS,
            task_sources={"TASK.md": "s" * source_context.TASK_SOURCE_MAX_CHARS},
            workspace_snapshot=(
                "diff --git a/owner.py b/owner.py\n"
                "+AUTHORITATIVE_WORKSPACE_MUST_SURVIVE\n"
                "+" + "w" * 1900
            ),
            previous_findings=["p" * source_context.PREVIOUS_FINDINGS_MAX_CHARS],
            evidence_records=records,
        )

        self.assertLessEqual(len(packet), source_context.PACKET_MAX_CHARS)
        self.assertIn("AUTHORITATIVE_WORKSPACE_MUST_SURVIVE", packet)
        self.assertIn("[tool history — ordered past events]", packet)


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
            settings.write_text('{"lens":"simplicity"}\n', encoding="utf-8")
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
