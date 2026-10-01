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
        self.reply = {"feedback": {
            "observed": "tool/call-1/input:4 state := job.status", "why": "sources(job.status) = 2",
            "structure": "UI <- job.status", "required": "保留目前狀態顯示"}}

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
        self.assertIn("OBSERVED: tool/call-1/input:4 state := job.status", text)
        self.assertIn("WHY: sources(job.status) = 2", text)
        self.assertIn("STRUCTURE: UI <- job.status", text)
        self.assertIn("REQUIRED: 保留目前狀態顯示", text)
        self.assertIn("tool/call-1/input:4", text)
        self.assertNotIn("criterion", text)
        self.assertNotIn("evidence", text)

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

    def test_all_test_file_operations_skip_provider_and_leave_feedback_budget(self):
        self.prompt("必須保留 tests/required.spec.ts；Actor 負責測試")
        self.feedback()
        changes = [
            "*** Add File: tests/new.spec.ts\n+test()",
            "*** Update File: tests/new.spec.ts\n@@\n-test()\n+revised_test()",
            "*** Update File: tests/existing.py\n@@\n-assert old\n+assert new",
            "*** Delete File: tests/required.spec.ts",
            "*** Delete File: tests/__snapshots__/result.snap",
            "*** Update File: tests/old.rs\n*** Move to: tests/renamed.rs\n@@\n-old\n+new",
            "*** Add File: internal/cache/context_test.go\n+package cache",
            "*** Update File: internal/cache/context_test.go\n@@\n-old\n+new",
            "*** Delete File: internal/storage/cache/no_store_test.go",
            "*** Update File: internal/old_test.go\n*** Move to: internal/new_test.go\n@@\n-old\n+new",
        ]
        for i, change in enumerate(changes):
            with self.subTest(change=change):
                self.assertIsNone(self.batch(f"*** Begin Patch\n{change}\n*** End Patch", call=f"test-{i}"))
        self.assertEqual(self.calls, [])
        self.assertEqual(self.adapter.core.journal.recent(), [])
        self.assertEqual(self.adapter.core.journal.unresolved(), [])
        with self.adapter.core.journal.connect() as db:
            row = db.execute("SELECT skipped_test_patches FROM rounds").fetchone()
            self.assertEqual(row["skipped_test_patches"], len(changes))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM batches").fetchone()[0], len(changes))
        for i in range(4):
            self.batch(call=f"product-{i}")
        self.assertEqual(len(self.calls), 3)
        self.assertEqual([r["outcome"] for r in self.adapter.core.journal.recent()], ["feedback"] * 3)

    def test_test_only_changes_leave_silence_budget_for_product(self):
        self.prompt()
        removal = "*** Begin Patch\n*** Update File: tests/feature.rs\n@@\n-assert old\n+assert new\n*** End Patch"
        for i in range(3):
            self.assertIsNone(self.batch(removal, call=f"test-{i}"))
        self.assertEqual(self.calls, [])
        for i in range(3):
            self.batch(call=f"product-{i}")
        self.assertEqual(len(self.calls), 2)
        self.assertEqual([r["outcome"] for r in self.adapter.core.journal.recent()], ["silence"] * 2)

    def test_mixed_patch_keeps_product_feedback_without_test_history(self):
        self.prompt("Existing tests are immutable")
        self.batch("*** Begin Patch\n*** Add File: tests/new.spec.ts\n+test()\n*** End Patch", call="add-test")
        mixed = ("*** Begin Patch\n*** Update File: tests/new.spec.ts\n@@\n-test()\n+revised_test()\n"
                 "*** Delete File: tests/old.spec.ts\n"
                 "*** Update File: internal/cache/context_test.go\n@@\n-old\n+new\n"
                 "*** Update File: job.py\n@@\n+retry_state = job.status\n*** End Patch")
        self.feedback()
        self.assertIsNotNone(self.batch(mixed, call="mixed"))
        self.assertEqual(len(self.calls), 1)
        packet = json.loads(self.calls[0]["nudge_input"])
        self.assertIn("retry_state = job.status", str(packet["batch_change"]))
        self.assertEqual(packet["before_structure"], [])
        self.assertNotIn("new_test_paths", packet)
        self.assertNotIn("judgment_scope", packet)

    def test_file_origin_distinguishes_existing_untracked_and_later_staged_tests(self):
        tests = self.repo / "tests"
        tests.mkdir()
        (tests / "existing.spec.ts").write_text("original()", encoding="utf-8")
        self.prompt("Existing tests are immutable; new tests may be added")
        (tests / "new.spec.ts").write_text("test()", encoding="utf-8")
        self.batch("*** Begin Patch\n*** Add File: tests/new.spec.ts\n+test()\n*** End Patch", call="new-test")
        subprocess.run(["git", "-C", str(self.repo), "add", "tests/new.spec.ts"], check=True)
        # A new core/process and a follow-up request must not redefine a new test as existing.
        self.adapter = CodexAdapter(NudgeCore(self.settings, dispatch=self.dispatch))
        self.prompt("Continue the same task", turn="turn-2")
        patch = ("*** Begin Patch\n*** Update File: tests/new.spec.ts\n@@\n-test()\n+fixed_test()\n"
                 "*** Delete File: tests/existing.spec.ts\n"
                 "*** Update File: job.py\n@@\n+value = 1\n*** End Patch")
        self.batch(patch, turn="turn-2", call="mixed")
        packet = json.loads(self.calls[-1]["nudge_input"])
        origins = {row["path"]: json.loads(row["lines"][0]) for row in packet["file_origin"]}
        self.assertEqual(origins["tests/new.spec.ts"], {
            "existed_at_task_start": False, "baseline_turn_id": "turn-1",
        })
        self.assertEqual(origins["tests/existing.spec.ts"], {
            "existed_at_task_start": True, "baseline_turn_id": "turn-1",
        })
        self.assertEqual(len(self.calls), 1)  # Pure test patches still do not call Provider.
        self.assertNotIn("judgment_scope", packet)

    def test_explicit_new_goal_starts_a_new_file_baseline(self):
        self.adapter.core.start_round(self._session("turn-1"), "first", "goal one")
        (self.repo / "later.py").write_text("value = 1", encoding="utf-8")
        self.adapter.core.start_round(self._session("turn-2"), "second", "goal two")
        self.batch("*** Begin Patch\n*** Update File: later.py\n@@\n+value = 2\n*** End Patch",
                   turn="turn-2")
        origins = json.loads(self.calls[-1]["nudge_input"])["file_origin"]
        self.assertEqual(json.loads(origins[0]["lines"][0]), {
            "existed_at_task_start": True, "baseline_turn_id": "turn-2",
        })

    def _session(self, turn):
        from masters_nudge.contracts import SessionRef
        return SessionRef("session-1", turn, str(self.repo))

    def test_move_between_test_and_product_paths_keeps_provider(self):
        for i, (source, destination) in enumerate([
            ("tests/helper.py", "helper.py"),
            ("helper.py", "tests/helper.py"),
            ("internal/cache_test.go", "internal/cache.go"),
        ]):
            with self.subTest(source=source, destination=destination):
                turn = f"turn-{i}"
                self.prompt(turn=turn)
                change = f"*** Begin Patch\n*** Update File: {source}\n*** Move to: {destination}\n@@\n-old\n+new\n*** End Patch"
                self.batch(change, turn=turn, call=f"move-{i}")
        self.assertEqual(len(self.calls), 3)

    def test_uncertain_patch_and_non_test_file_keep_provider_review(self):
        self.prompt()
        self.batch("*** Begin Patch\n*** Add File: tests/README.md\n+notes\n*** End Patch", call="readme")
        self.batch("*** Begin Patch\n*** Add File: tests/new.spec.ts\n+test\n"
                   "*** Move to: tests/moved.spec.ts\n*** End Patch", call="invalid-move")
        self.assertEqual(len(self.calls), 2)

    def test_failed_test_patch_is_not_recorded_as_successfully_skipped(self):
        self.prompt()
        self.batch("*** Begin Patch\n*** Add File: tests/new.spec.ts\n+test\n*** End Patch",
                   output="Failed to write file", call="failed-add")
        self.assertEqual(len(self.calls), 1)
        with self.adapter.core.journal.connect() as db:
            self.assertEqual(db.execute("SELECT skipped_test_patches FROM rounds").fetchone()[0], 0)

    def test_native_exit_code_zero_add_skips_provider(self):
        self.prompt()
        output = "Exit code: 0\nWall time: 0 seconds\nOutput:\nSuccess. Updated the following files:\nA test/cacheKey.js"
        self.batch("*** Begin Patch\n*** Add File: test/cacheKey.js\n+test\n*** End Patch", output=output)
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
        self.reply["feedback"]["structure"] = "render <- job.status"
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

    def test_observed_location_is_not_a_literal_runtime_gate(self):
        self.prompt()
        self.feedback()
        self.reply["feedback"]["observed"] = "tool/call-1/input:5 state := job.status"
        result = self.batch()
        self.assertIn(
            self.reply["feedback"]["structure"],
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
