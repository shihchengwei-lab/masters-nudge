"""Observable requirements of SPEC, using the actual hook adapter and core."""
import json
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.core import NudgeCore
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


ROOT = Path(__file__).resolve().parents[2]


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.calls = []
        self.reply = {"feedback": None}
        paths = RuntimePaths(ROOT, self.root / "data", self.root / "settings", self.root / "error.log")
        self.settings = RuntimeSettings("openai", "gpt-5.6-sol", paths)
        self.adapter = CodexAdapter(NudgeCore(self.settings, dispatch=self.dispatch))

    def dispatch(self, **kwargs):
        from masters_nudge.contracts import ProviderRun
        self.calls.append(kwargs)
        if isinstance(self.reply, Exception):
            raise self.reply
        return ProviderRun(json.dumps(self.reply, ensure_ascii=False))

    def prompt(self, text="保留畫面行為", turn="turn-1"):
        return self.adapter.process({"hook_event_name": "UserPromptSubmit", "session_id": "session-1",
                                     "turn_id": turn, "cwd": str(self.repo), "prompt": text,
                                     "transcript_path": None})

    def batch(self, tool_input=None, *, tool="apply_patch", turn="turn-1", output="Success", call="call-1"):
        if tool_input is None:
            tool_input = "*** Begin Patch\n*** Update File: job.py\n@@\n+retry_state = job.status\n*** End Patch"
        return self.adapter.process({"hook_event_name": "PostToolUse", "session_id": "session-1",
                                     "turn_id": turn, "cwd": str(self.repo), "transcript_path": None,
                                     "tool_name": tool, "tool_input": tool_input,
                                     "tool_response": output, "tool_use_id": call})

    def release(self, *, turn="turn-1", call="release-1", output="checked"):
        return self.batch({"cmd": "python -m unittest"}, tool="exec_command", turn=turn,
                          output=output, call=call)

    def feedback(self):
        self.reply = {"feedback": {"criterion": 4,
            "evidence": [{"source": "batch_change", "location": "tool/call-1/input:4",
                          "excerpt": "retry_state = job.status"}],
            "observed": "retry_state := job.status", "violates": "sources(job.status) = 2",
            "prefer": "UI <- job.status"}}

    def test_prompt_and_reads_do_not_call_provider(self):
        self.assertIsNone(self.prompt())
        self.assertIsNone(self.batch({"cmd": "Get-Content job.py"}, tool="exec_command"))
        self.assertEqual(self.calls, [])

    def test_apply_patch_calls_provider_immediately_after_success(self):
        self.prompt()

        self.batch(output="Success. Updated job.py", call="change-1")
        self.assertEqual(len(self.calls), 1)
        packet = json.loads(self.calls[0]["nudge_input"])
        self.assertIn("retry_state = job.status", str(packet["batch_change"]))
        self.assertIn("Success. Updated job.py", str(packet["tool_result"]))

    def test_required_material_over_target_still_calls_provider_without_repo_budget(self):
        self.prompt("t" * 12000)
        patch = "*** Begin Patch\n*** Update File: job.py\n@@\n+" + "x" * 9000 + "\n*** End Patch"
        self.batch(tool_input=patch)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0]["remaining_chars"], 0)
        packet = json.loads(self.calls[0]["nudge_input"])
        self.assertEqual(len(packet["task_contract"]), 1)

    def test_overlapping_patches_call_provider_in_one_sequence(self):
        from masters_nudge.contracts import ProviderRun
        first_entered = threading.Event()
        release_first = threading.Event()
        second_entered = threading.Event()
        errors = []

        def dispatch(**kwargs):
            self.calls.append(kwargs)
            if len(self.calls) == 1:
                first_entered.set()
                release_first.wait(2)
            else:
                second_entered.set()
            return ProviderRun('{"feedback":null}')

        def run_batch(call):
            try:
                self.batch(call=call)
            except Exception as exc:
                errors.append(exc)

        self.adapter.core.dispatch = dispatch
        self.prompt()
        first = threading.Thread(target=run_batch, args=("change-1",))
        second = threading.Thread(target=run_batch, args=("change-2",))
        first.start()
        self.assertTrue(first_entered.wait(1))
        second.start()
        self.assertFalse(second_entered.wait(0.1))
        release_first.set()
        first.join(2)
        second.join(2)
        self.assertFalse(first.is_alive() or second.is_alive())
        self.assertEqual(errors, [])
        self.assertTrue(second_entered.is_set())
        self.assertEqual(len(self.calls), 2)

    def test_non_apply_patch_post_tool_use_does_not_call_provider(self):
        self.prompt()
        self.batch({"cmd": "python -m unittest"}, tool="exec_command")
        self.assertEqual(self.calls, [])

    def test_tests_and_opaque_shell_writes_after_mutation_do_not_trigger(self):
        self.prompt()
        self.batch()
        self.batch({"cmd": "python -m unittest"}, tool="exec_command")
        self.batch({"cmd": "Set-Content job.py changed"}, tool="exec_command")
        self.assertEqual(len(self.calls), 1)

    def test_other_edit_tool_names_do_not_trigger(self):
        self.prompt()
        self.batch({"file_path": "job.py", "old_string": "x", "new_string": "y"}, tool="edit")
        self.batch({"path": "new.py", "content": ""}, tool="write")
        self.batch({"path": "third.py", "content": "x"}, tool="write")
        self.assertEqual(self.calls, [])

    def test_legacy_post_tool_batch_is_ignored(self):
        self.prompt()
        self.adapter.process({"hook_event_name": "PostToolBatch", "session_id": "session-1",
            "turn_id": "turn-1", "cwd": str(self.repo), "tool_calls": [
                {"tool_use_id": f"id-{n}", "tool_name": "write", "tool_input": {"path": f"{n}.py", "content": "x=1"},
                 "tool_response": "done"} for n in range(3)]})
        self.assertEqual(self.calls, [])

    def test_non_git_workspace_reports_fault(self):
        self.prompt()
        import shutil
        shutil.rmtree(self.repo / ".git")
        result = self.batch()
        self.assertIn("本輪反饋未執行", result["systemMessage"])
        self.assertEqual(self.calls, [])

    def test_strict_fault_stops_caller_and_journals_invalid_attempt(self):
        from dataclasses import replace
        from masters_nudge.contracts import ToolFault
        self.adapter.core.settings = replace(self.settings, strict=True)
        self.prompt()
        self.reply = ToolFault("timeout", "failed")
        with self.assertRaises(ToolFault):
            self.batch()
        self.assertEqual(self.adapter.core.journal.recent()[0]["outcome"], "fault")

    def test_native_freeform_patch_triggers_with_actual_tool_result(self):
        self.prompt()
        self.batch(output="Success. Updated job.py")
        self.assertEqual(len(self.calls), 1)
        packet = json.loads(self.calls[0]["nudge_input"])
        self.assertIn("Success. Updated job.py", str(packet["tool_result"]))
        for field in ("task_contract", "before_structure", "batch_change", "current_structure", "tool_result"):
            self.assertIn(field, packet)

    def test_native_command_wrapped_patch_triggers(self):
        # Captured from native-actor-4, not the model-facing freeform schema.
        patch = "*** Begin Patch\n*** Update File: job.py\n@@\n+retry_state = job.status\n*** End Patch"
        self.prompt()
        self.batch({"command": patch}, output={})
        self.assertEqual(len(self.calls), 1)
        packet = json.loads(self.calls[0]["nudge_input"])
        self.assertIn("+retry_state = job.status", str(packet["batch_change"]))
        self.assertIn("{}", str(packet["tool_result"]))
        self.batch({"command": "Write-Output '*** Begin Patch'"}, tool="Bash")
        self.assertEqual(len(self.calls), 1)

    def test_feedback_delivers_fixed_formal_fields(self):
        self.prompt()
        self.feedback()
        result = self.batch(output={"ok": True})
        self.assertNotIn("continue", result)
        self.assertNotIn("stopReason", result)
        specific = result["hookSpecificOutput"]
        self.assertEqual(specific["hookEventName"], "PostToolUse")
        text = specific["additionalContext"]
        self.assertTrue(text.startswith("Masters’ Nudge\n"))
        self.assertIn("OBSERVED: retry_state := job.status", text)
        self.assertIn("VIOLATES: sources(job.status) = 2", text)
        self.assertIn("PREFER: UI <- job.status", text)
        self.assertNotIn("tool/call-1", text)
        self.assertNotIn("criterion", text)

    def test_two_silences_stop_and_user_message_resets(self):
        self.prompt()
        for i in range(4):
            self.batch(call=f"call-{i}")
        self.assertEqual(len(self.calls), 2)
        self.prompt("現在改成只保留一份狀態", turn="turn-2")
        self.batch(turn="turn-2")
        self.assertEqual(len(self.calls), 3)
        packet = json.loads(self.calls[-1]["nudge_input"])
        self.assertIn("現在改成只保留一份狀態", str(packet["task_contract"]))

    def test_new_test_file_patches_leave_silence_budget_for_source_changes(self):
        self.prompt()
        added = "*** Begin Patch\n*** Add File: tests/new.spec.ts\n+x\n*** End Patch"
        updated = "*** Begin Patch\n*** Update File: tests/new.spec.ts\n@@\n+x\n*** End Patch"
        self.assertIsNone(self.batch(added, call="test-add"))
        self.assertIsNone(self.batch(updated, call="test-update"))
        self.assertEqual(len(self.calls), 0)
        with self.adapter.core.journal.connect() as db:
            row = db.execute("SELECT skipped_test_patches FROM rounds").fetchone()
        self.assertEqual(row["skipped_test_patches"], 2)
        for i in range(3):
            self.batch(call=f"source-{i}")
        self.assertEqual(len(self.calls), 2)

    def test_addition_to_existing_test_skips_but_mixed_patch_calls_provider(self):
        self.prompt()
        existing = "*** Begin Patch\n*** Update File: tests/existing.spec.ts\n@@\n+x\n*** End Patch"
        mixed = ("*** Begin Patch\n*** Add File: tests/new.spec.ts\n+x\n"
                 "*** Update File: job.py\n@@\n+x\n*** End Patch")
        self.batch(existing, call="existing")
        self.batch(mixed, call="mixed")
        self.assertEqual(len(self.calls), 1)
        packet = json.loads(self.calls[-1]["nudge_input"])
        self.assertEqual(packet["judgment_scope"], "implementation")
        self.assertEqual(packet["new_test_paths"], ["tests/new.spec.ts"])
        self.assertIn("*** Update File: job.py", str(packet["batch_change"]))
        self.batch("*** Begin Patch\n*** Update File: tests/new.spec.ts\n@@\n+x\n*** End Patch",
                   call="new-update")
        self.assertEqual(len(self.calls), 1)

    def test_test_removal_silences_do_not_exhaust_implementation_budget(self):
        self.prompt("保留既有產品行為，Actor 自行決定驗證方式")
        removal = ("*** Begin Patch\n*** Update File: tests/feature.rs\n@@\n"
                   "-assert_eq!(run(), expected);\n+assert_eq!(run(), updated);\n*** End Patch")
        for i in range(3):
            self.assertIsNone(self.batch(removal, call=f"test-{i}"))
        self.assertEqual(len(self.calls), 3)
        for call in self.calls:
            self.assertEqual(json.loads(call["nudge_input"])["judgment_scope"], "task_contract")
        self.assertEqual([item["outcome"] for item in self.adapter.core.journal.recent()],
                         ["silence"] * 3)
        self.assertTrue(all(item["detail"]["judgment_scope"] == "task_contract"
                            for item in self.adapter.core.journal.recent()))
        self.feedback()
        self.assertIsNotNone(self.batch(call="product-change"))
        self.assertEqual(json.loads(self.calls[-1]["nudge_input"])["judgment_scope"], "implementation")
        self.reply = {"feedback": None}
        for i in range(3):
            self.batch(call=f"product-silence-{i}")
        self.assertEqual(len(self.calls), 6)

    def test_contract_feedback_is_delivered_and_counts_towards_feedback_limit(self):
        self.prompt("必須保留 tests/required.spec.ts 的拒絕非法狀態測試")
        self.batch("*** Begin Patch\n*** Add File: tests/required.spec.ts\n+assert rejected\n*** End Patch",
                   call="add-required")
        removal = "*** Begin Patch\n*** Delete File: tests/required.spec.ts\n*** End Patch"
        self.reply = {"feedback": {"criterion": 1,
            "evidence": [{"source": "batch_change", "location": "tool/delete/input:2",
                          "excerpt": "*** Delete File: tests/required.spec.ts"}],
            "observed": "required.spec.ts 被刪除", "violates": "契約要求的驗證消失",
            "prefer": "保留契約要求的非法狀態測試"}}
        self.assertIsNotNone(self.batch(removal, call="delete"))
        self.assertEqual(json.loads(self.calls[0]["nudge_input"])["judgment_scope"], "task_contract")
        self.assertIn("add-required", str(json.loads(self.calls[0]["nudge_input"])["before_structure"]))
        self.feedback()
        for i in range(3):
            self.batch(call=f"product-{i}")
        self.assertEqual(len(self.calls), 3)

    def test_snapshot_deletion_asks_about_contract_without_inferring_file_origin(self):
        self.prompt()
        self.batch("*** Begin Patch\n*** Delete File: tests/__snapshots__/result.snap\n*** End Patch")
        self.assertEqual(len(self.calls), 1)
        packet = json.loads(self.calls[0]["nudge_input"])
        self.assertEqual(packet["judgment_scope"], "task_contract")
        self.assertEqual(packet["new_test_paths"], [])

    def test_mixed_patch_with_test_removal_keeps_implementation_scope(self):
        self.prompt()
        self.batch("*** Begin Patch\n*** Delete File: tests/old.spec.ts\n"
                   "*** Update File: job.py\n@@\n+retry_state = job.status\n*** End Patch")
        packet = json.loads(self.calls[0]["nudge_input"])
        self.assertEqual(packet["judgment_scope"], "implementation")
        self.assertIn("retry_state = job.status", str(packet["batch_change"]))

    def test_test_blank_line_cleanup_skips_provider(self):
        self.prompt()
        self.batch("*** Begin Patch\n*** Update File: tests/feature.rs\n@@\n-});\n-\n-  \n+});\n*** End Patch")
        self.assertEqual(self.calls, [])

    def test_identical_text_added_elsewhere_does_not_hide_test_removal(self):
        self.prompt()
        self.batch("*** Begin Patch\n*** Update File: tests/required.py\n@@\n-assert rejected\n"
                   "*** Update File: tests/other.py\n@@\n+assert rejected\n*** End Patch")
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(json.loads(self.calls[0]["nudge_input"])["judgment_scope"], "task_contract")

    def test_skipped_test_addition_is_available_when_actor_removes_its_own_case(self):
        self.prompt("Existing tests are immutable")
        addition = "*** Begin Patch\n*** Update File: tests/feature.rs\n@@\n+fn actor_case() {}\n*** End Patch"
        self.batch(addition, call="actor-added-case")
        self.batch("*** Begin Patch\n*** Add File: tests/unrelated.rs\n+fn other() {}\n*** End Patch",
                   call="unrelated")
        self.assertEqual(self.calls, [])
        removal = "*** Begin Patch\n*** Update File: tests/feature.rs\n@@\n-fn actor_case() {}\n*** End Patch"
        self.batch(removal, call="actor-removed-case")
        packet = json.loads(self.calls[0]["nudge_input"])
        self.assertEqual(packet["before_structure"], [
            {"path": "prior_tool/actor-added-case/input", "start": 1, "lines": addition.splitlines()},
            {"path": "prior_tool/actor-added-case/output", "start": 1, "lines": ["Success"]},
        ])
        self.assertEqual(self.adapter.core.journal.unresolved(), [])
        self.prompt("新的要求", turn="turn-2")
        self.batch(removal, turn="turn-2", call="new-round-removal")
        self.assertEqual(json.loads(self.calls[-1]["nudge_input"])["before_structure"], [])

    def test_mixed_followup_identifies_new_test_without_hiding_source_change(self):
        self.prompt("Checked-in tests are immutable")
        self.batch("*** Begin Patch\n*** Add File: tests/new.spec.ts\n+x\n*** End Patch", call="add-test")
        mixed = ("*** Begin Patch\n*** Update File: tests/new.spec.ts\n@@\n+y\n"
                 "*** Update File: job.py\n@@\n+value = 1\n*** End Patch")
        self.batch(mixed, call="mixed")
        self.assertEqual(len(self.calls), 1)
        packet = json.loads(self.calls[0]["nudge_input"])
        self.assertEqual(packet["new_test_paths"], ["tests/new.spec.ts"])
        self.assertIn("*** Update File: tests/new.spec.ts", str(packet["batch_change"]))
        self.assertIn("*** Update File: job.py", str(packet["batch_change"]))

    def test_new_round_forgets_new_test_file(self):
        self.prompt()
        self.batch("*** Begin Patch\n*** Add File: tests/new.spec.ts\n+x\n*** End Patch")
        self.prompt("另一輪", turn="turn-2")
        self.batch("*** Begin Patch\n*** Update File: tests/new.spec.ts\n@@\n-x\n+y\n*** End Patch",
                   turn="turn-2")
        self.assertEqual(len(self.calls), 1)
        packet = json.loads(self.calls[0]["nudge_input"])
        self.assertEqual(packet["new_test_paths"], [])

    def test_uncertain_patch_and_non_test_file_keep_provider_review(self):
        self.prompt()
        self.batch("*** Begin Patch\n*** Add File: tests/README.md\n+notes\n*** End Patch",
                   call="readme")
        self.batch("*** Begin Patch\n*** Add File: tests/new.spec.ts\n+test\n"
                   "*** Move to: tests/moved.spec.ts\n*** End Patch", call="move")
        self.assertEqual(len(self.calls), 2)

    def test_failed_add_does_not_establish_new_test_provenance(self):
        self.prompt()
        self.batch("*** Begin Patch\n*** Add File: tests/new.spec.ts\n+test\n*** End Patch",
                   output="Failed to write file", call="failed-add")
        self.batch("*** Begin Patch\n*** Update File: tests/new.spec.ts\n@@\n-test\n+replacement\n*** End Patch",
                   call="later-update")
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(json.loads(self.calls[-1]["nudge_input"])["new_test_paths"], [])
        self.assertIn("Failed to write file", str(json.loads(self.calls[-1]["nudge_input"])["before_structure"]))

    def test_native_exit_code_zero_add_skips_provider(self):
        self.prompt()
        output = "Exit code: 0\nWall time: 0 seconds\nOutput:\nSuccess. Updated the following files:\nA test/cacheKey.js"
        self.batch("*** Begin Patch\n*** Add File: test/cacheKey.js\n+test\n*** End Patch",
                   output=output)
        self.assertEqual(self.calls, [])

    def test_three_identical_feedbacks_count_without_cooldown(self):
        self.prompt()
        self.feedback()
        for _ in range(5):
            result = self.batch()
            if result:
                self.adapter.core.journal.delivered(result["_masters_nudge"])
        self.assertEqual(len(self.calls), 3)
        history = json.loads(self.calls[-1]["nudge_input"])["previous_nudges"]
        self.assertEqual(history, [self.reply["feedback"], self.reply["feedback"]])

    def test_all_delivered_nudges_are_sent_in_order_across_silence(self):
        self.prompt()
        self.feedback()
        first = json.loads(json.dumps(self.reply["feedback"]))
        result = self.batch(call="first-feedback")
        self.adapter.core.journal.delivered(result["_masters_nudge"])
        self.reply = {"feedback": None}
        self.batch(call="silence")
        self.feedback()
        self.reply["feedback"]["prefer"] = "render <- job.status"
        second = json.loads(json.dumps(self.reply["feedback"]))
        result = self.batch(call="second-feedback")
        self.adapter.core.journal.delivered(result["_masters_nudge"])
        self.batch(call="third-feedback")
        self.batch(call="over-limit")
        history = [json.loads(call["nudge_input"])["previous_nudges"] for call in self.calls]
        self.assertEqual(history, [[], [first], [first], [first, second]])

    def test_undelivered_and_previous_round_feedback_are_not_sent(self):
        self.prompt()
        self.feedback()
        self.batch(call="not-delivered")
        result = self.batch(call="delivered")
        self.adapter.core.journal.delivered(result["_masters_nudge"])
        self.prompt("新一輪要求")
        self.batch(call="new-round")
        self.assertEqual([json.loads(call["nudge_input"])["previous_nudges"] for call in self.calls],
                         [[], [], []])

    def test_new_user_message_resets_even_when_codex_reuses_turn_id(self):
        self.prompt()
        self.batch()
        self.batch()
        self.batch()
        self.prompt("改成只保留一份狀態")
        self.batch()
        self.assertEqual(len(self.calls), 3)

    def test_new_message_with_same_turn_id_withholds_in_flight_feedback(self):
        self.prompt()
        self.feedback()
        original = self.dispatch
        def dispatch(**kwargs):
            result = original(**kwargs)
            self.prompt("改做另一件事")
            return result
        self.adapter.core.dispatch = dispatch
        self.assertIsNone(self.batch())
        self.assertEqual(self.adapter.core.journal.recent()[0]["outcome"], "feedback")
        self.assertEqual(self.adapter.core.journal.recent()[0]["delivered"], 0)

    def test_evidence_line_offset_is_not_a_literal_runtime_gate(self):
        self.prompt()
        self.feedback()
        self.reply["feedback"]["evidence"][0]["location"] = "tool/call-1/input:5"
        result = self.batch()
        self.assertIn(
            self.reply["feedback"]["prefer"],
            result["hookSpecificOutput"]["additionalContext"],
        )

    def test_fault_ends_the_round_without_becoming_silence(self):
        from masters_nudge.contracts import ToolFault
        self.prompt()
        self.reply = ToolFault("timeout", "provider timed out")
        result = self.batch()
        self.assertIn("本輪反饋未執行", result["systemMessage"])
        self.reply = {"feedback": None}
        for _ in range(3):
            result = self.batch()
            self.assertIn("本輪反饋未執行", result["systemMessage"])
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.adapter.core.journal.unresolved(), [])

    def test_new_request_during_judgment_withholds_old_feedback(self):
        self.prompt()
        self.feedback()
        original = self.dispatch
        def dispatch(**kwargs):
            result = original(**kwargs)
            self.prompt("停止這件事", turn="turn-2")
            return result
        self.adapter.core.dispatch = dispatch
        self.assertIsNone(self.batch())


if __name__ == "__main__":
    unittest.main()
