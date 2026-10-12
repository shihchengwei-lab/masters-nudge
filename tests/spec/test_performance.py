"""Offline contract tests for the opt-in performance checkpoint.

All measurements below are synthetic fixtures and every Provider is a stub. These
assert prompt/transport/lifecycle contracts, not model quality or real bottlenecks.
"""
import copy
import hashlib
import json
import re
import subprocess
import tempfile
import threading
import time
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.contracts import (
    FEEDBACK_FIELD_LIMITS, FEEDBACK_MAX_CHARS, MATERIAL_MAX_CHARS,
    ProviderRun, SessionRef, ToolFault,
)
from masters_nudge.core import NudgeCore
from masters_nudge.diagnostics import (
    DiagnosticBatch, MAX_EVIDENCE_RESULTS, MAX_INPUT_BYTES, build_diagnostic_packet,
)
from masters_nudge.prompting import delivery_text, load_system_prompt
from masters_nudge.provider_contract import parse_feedback
from masters_nudge.runtime import RuntimePaths, RuntimeSettings
from masters_nudge.storage import FINALIZATION_RESERVE_SEC

ROOT = Path(__file__).resolve().parents[2]
# Recorded from main fa092ba, not computed from the implementation under test.
LINUS_PROMPT_SHA256 = "6c058c7110caac5cf86f96a457821d60feb481ef8fbf25ca52b39e7b6e6109a3"
SCHEMA_SHA256 = "ce3c0e0a74fd63dd5b01bf0d88c798c223f27bb9110dc7b34137f7cb1ddac0e0"
MEASUREMENT_FEEDBACK = {
    "required": "確認延遲限制且保持正確",
    "observed": "sample RAM=90%; pressure unknown",
    "why": "容量不等於壓力",
    "structure": "compare p95 latency with page-fault windows",
}
PATCH = "*** Begin Patch\n*** Update File: job.py\n@@\n-old\n+new\n*** End Patch"


def evidence(identity="read-1", output=None, tool_input=None, tool="exec_command"):
    return {
        "tool_use_id": identity,
        "tool_name": tool,
        "tool_input": {"cmd": "read scoped measurement"} if tool_input is None else tool_input,
        "tool_response": {"exit_code": 0, "stdout": "RAM=90%; p95 unknown"} if output is None else output,
    }


def payload(cwd="/synthetic/evidence", **changes):
    value = {
        "cwd": cwd,
        "task_request": "確認延遲瓶頸，保持正確性與穩定性",
        "batch_id": "batch-A",
        "reason": "Need one distinguishing measurement before choosing an action",
        "progress": "No changes; only scoped read-only results collected",
        "evidence": [evidence()],
    }
    value.update(changes)
    return value


class PerformanceProfileTests(unittest.TestCase):
    def test_default_profile_and_linus_prompt_are_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = RuntimeSettings.from_env(ROOT, environ={"HOME": directory})
        self.assertEqual(settings.profile, "software-engineering")
        self.assertEqual(settings.prompt_file, ROOT / "buddy-prompt.txt")
        self.assertEqual(hashlib.sha256(settings.prompt_file.read_bytes()).hexdigest(), LINUS_PROMPT_SHA256)
        self.assertEqual(load_system_prompt(prompt_file=settings.prompt_file), settings.prompt_file.read_text().strip())

    def test_opt_in_isolates_journal_but_preserves_provider_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            base = {"HOME": directory, "MASTERS_NUDGE_DATA_DIR": str(Path(directory) / "settings")}
            Path(base["MASTERS_NUDGE_DATA_DIR"]).mkdir()
            config = Path(base["MASTERS_NUDGE_DATA_DIR"]) / "config.json"
            config.write_text('{"provider":"openai","model":"already-selected-model"}')
            before = config.read_bytes()
            regular = RuntimeSettings.from_env(ROOT, environ=base)
            perf = RuntimeSettings.from_env(ROOT, environ={**base, "MASTERS_NUDGE_PROFILE": "performance"})
            self.assertEqual(perf.paths.settings_dir, regular.paths.settings_dir)
            self.assertEqual(perf.paths.data_dir, regular.paths.data_dir / "performance")
            self.assertEqual(perf.paths.error_log, perf.paths.data_dir / "error.log")
            self.assertEqual(perf.model, regular.model)
            self.assertEqual(perf.model, "already-selected-model")
            self.assertEqual(perf.provider, regular.provider)
            self.assertEqual(config.read_bytes(), before)
            self.assertEqual(perf.prompt_file, ROOT / "performance-prompt.txt")

    def test_default_home_path_is_also_profile_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            regular = RuntimePaths.resolve(ROOT, environ={"HOME": directory})
            perf = RuntimePaths.resolve(ROOT, environ={"HOME": directory, "MASTERS_NUDGE_PROFILE": "performance"})
            self.assertEqual(perf.data_dir, regular.data_dir / "performance")
            self.assertEqual(perf.settings_dir, regular.settings_dir)

    def test_unknown_profile_is_configuration_error(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = RuntimeSettings.from_env(ROOT, environ={"HOME": directory, "MASTERS_NUDGE_PROFILE": "perfomance"})
        self.assertTrue(settings.configuration_error)

    def test_performance_has_exactly_five_principles_and_only_carmack_anchor(self):
        prompt = (ROOT / "performance-prompt.txt").read_text()
        numbered = re.findall(r"^([0-9]+)\. (.+)$", prompt, re.MULTILINE)
        self.assertEqual([number for number, _ in numbered], ["1", "2", "3", "4", "5"])
        expected = ["Measure, don't guess.", "Remove work before optimizing work.", "Follow the data.",
                    "Optimize the bottleneck, not the metric.", "Prove the improvement end-to-end."]
        for (_, actual), prefix in zip(numbered, expected):
            self.assertTrue(actual.startswith(prefix), actual)
        self.assertEqual(prompt.count("John Carmack"), 1)
        self.assertNotRegex(prompt, r"(?i)Linus|Torvalds")
        self.assertIn("focusing anchor only", prompt)
        self.assertIn("do not imitate", prompt)
        self.assertIn("return silence", prompt)
        self.assertIn("at most one consequential measurement", prompt)
        self.assertIn("not verified host telemetry", prompt)

    def test_original_schema_and_shared_field_limits_are_unchanged(self):
        self.assertEqual(hashlib.sha256((ROOT / "nudge-schema.json").read_bytes()).hexdigest(), SCHEMA_SHA256)
        self.assertEqual(FEEDBACK_FIELD_LIMITS, {"observed": 40, "why": 25, "structure": 61, "required": 35})
        self.assertEqual(FEEDBACK_MAX_CHARS, 200)
        schema = json.loads((ROOT / "nudge-schema.json").read_text())
        fields = schema["properties"]["feedback"]["anyOf"][1]
        self.assertEqual(set(fields["properties"]), set(FEEDBACK_FIELD_LIMITS))
        self.assertFalse(fields["additionalProperties"])
        for name, limit in FEEDBACK_FIELD_LIMITS.items():
            self.assertEqual(fields["properties"][name]["maxLength"], limit)

    def test_delivery_preserves_same_fields_without_requiring_changes(self):
        feedback = parse_feedback(json.dumps({"feedback": MEASUREMENT_FEEDBACK}))
        default = delivery_text(feedback)
        perf = delivery_text(feedback, profile="performance")
        self.assertIn(feedback.message, default)
        self.assertIn(feedback.message, perf)
        self.assertIn("decide whether further measurement or a change is warranted", perf)
        self.assertIn("stop when no actionable problem is supported", perf)
        self.assertNotIn("John Carmack", perf)
        self.assertNotEqual(perf, default)


class DiagnosticInputTests(unittest.TestCase):
    def test_exact_top_level_contract(self):
        valid = payload()
        for key in valid:
            with self.subTest(missing=key):
                value = copy.deepcopy(valid)
                del value[key]
                with self.assertRaises(ToolFault):
                    DiagnosticBatch.parse(value)
        for value in (None, [], "text", {**valid, "session_id": "guess"}, {**valid, "extra": True}):
            with self.subTest(value=value):
                with self.assertRaises(ToolFault):
                    DiagnosticBatch.parse(value)

    def test_exact_evidence_contract(self):
        for key in evidence():
            with self.subTest(missing=key):
                item = evidence()
                del item[key]
                with self.assertRaises(ToolFault):
                    DiagnosticBatch.parse(payload(evidence=[item]))
        for item in (None, [], "result", {**evidence(), "exit_code": 0}):
            with self.subTest(item=item):
                with self.assertRaises(ToolFault):
                    DiagnosticBatch.parse(payload(evidence=[item]))

    def test_text_fields_reject_empty_wrong_type_and_over_limit(self):
        limits = {"cwd": 4096, "task_request": MATERIAL_MAX_CHARS,
                  "batch_id": 128, "reason": 1000, "progress": 2000}
        for name, limit in limits.items():
            for value in (None, 1, True, [], "", " \n\t", "x" * (limit + 1)):
                with self.subTest(name=name, value_type=type(value).__name__, length=len(value) if isinstance(value, str) else None):
                    with self.assertRaises(ToolFault):
                        DiagnosticBatch.parse(payload(**{name: value}))
            with self.subTest(boundary=name):
                self.assertEqual(getattr(DiagnosticBatch.parse(payload(**{name: "x" * limit})), name), "x" * limit)

    def test_tool_identity_and_name_limits(self):
        for name in ("tool_use_id", "tool_name"):
            for value in (None, 7, "", " \n", "x" * 129):
                with self.subTest(name=name, value=value):
                    with self.assertRaises(ToolFault):
                        DiagnosticBatch.parse(payload(evidence=[{**evidence(), name: value}]))
            batch = DiagnosticBatch.parse(payload(evidence=[{**evidence(), name: "x" * 128}]))
            self.assertEqual(getattr(batch.events[0], name), "x" * 128)

    def test_one_to_eight_evidence_results(self):
        self.assertEqual(MAX_EVIDENCE_RESULTS, 8)
        for count in (1, 8):
            self.assertEqual(len(DiagnosticBatch.parse(payload(evidence=[evidence(str(i)) for i in range(count)])).events), count)
        for values in ([], [evidence(str(i)) for i in range(9)], {}, "one", None):
            with self.subTest(values=values):
                with self.assertRaises(ToolFault):
                    DiagnosticBatch.parse(payload(evidence=values))

    def test_result_ids_must_be_unique_within_a_batch(self):
        with self.assertRaisesRegex(ToolFault, "tool_use_id"):
            DiagnosticBatch.parse(payload(evidence=[evidence(), evidence(output="different")]))

    def test_result_outputs_must_be_nonempty_supported_json(self):
        for value in (None, "", " \n", {}, [], 0, 1, False, True):
            with self.subTest(value=value):
                with self.assertRaises(ToolFault):
                    DiagnosticBatch.parse(payload(evidence=[{**evidence(), "tool_response": value}]))
        for value in ("0", {"exit_code": 0}, [0], [None], "no observation"):
            with self.subTest(accepted=value):
                self.assertEqual(DiagnosticBatch.parse(payload(evidence=[evidence(output=value)])).events[0].tool_response, value)

    def test_nan_infinity_and_non_json_values_are_faults(self):
        for value in (float("nan"), float("inf"), float("-inf"), object(), {1, 2}):
            with self.subTest(value=repr(value)):
                with self.assertRaises(ToolFault):
                    DiagnosticBatch.parse(payload(evidence=[evidence(tool_input={"value": value})]))

    def test_input_size_is_utf8_bytes_not_character_count(self):
        value = payload(evidence=[evidence(output="量" * 23000)])
        self.assertLess(len(json.dumps(value, ensure_ascii=False)), MAX_INPUT_BYTES)
        with self.assertRaises(ToolFault) as caught:
            DiagnosticBatch.parse(value)
        self.assertEqual(caught.exception.kind, "input_size")

    def test_canonical_byte_limit_accepts_exact_boundary_then_rejects_one_more(self):
        value = payload(evidence=[evidence(output="x")])
        size = len(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
        value["evidence"][0]["tool_response"] += "x" * (MAX_INPUT_BYTES - size)
        DiagnosticBatch.parse(value)
        value["evidence"][0]["tool_response"] += "x"
        with self.assertRaises(ToolFault) as caught:
            DiagnosticBatch.parse(value)
        self.assertEqual(caught.exception.kind, "input_size")

    def test_fingerprint_ignores_wrapping_ids_order_and_object_key_order(self):
        first = payload(evidence=[evidence("first", output={"a": 1, "b": 2}), evidence("second", output="latency=60")])
        other = copy.deepcopy(first)
        other.update(batch_id="renamed", reason="different rationale", progress="different progress")
        other["evidence"].reverse()
        other["evidence"][0]["tool_use_id"] = "id-B"
        other["evidence"][1]["tool_use_id"] = "id-A"
        other["evidence"][1]["tool_response"] = {"b": 2, "a": 1}
        self.assertEqual(DiagnosticBatch.parse(first).fingerprint, DiagnosticBatch.parse(other).fingerprint)
        other["evidence"][0]["tool_response"] = "latency=61; window=next"
        self.assertNotEqual(DiagnosticBatch.parse(first).fingerprint, DiagnosticBatch.parse(other).fingerprint)

    def test_repeating_identical_result_with_fresh_id_does_not_change_evidence(self):
        first = DiagnosticBatch.parse(payload())
        second = DiagnosticBatch.parse(payload(evidence=[evidence("original"), evidence("duplicate")]))
        self.assertEqual(first.fingerprint, second.fingerprint)


class PerformanceIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        paths = RuntimePaths(ROOT, self.root / "data" / "performance", self.root / "settings", self.root / "error.log")
        self.settings = RuntimeSettings("openai", "offline-model", paths, profile="performance")
        self.calls = []
        self.reply = {"feedback": None}
        self.core = self.new_core()
        self.session = SessionRef("session-1", "turn-1", str(self.repo))
        self.request = payload()["task_request"]
        self.core.start_round(self.session, self.request)

    def new_core(self):
        return NudgeCore(self.settings, dispatch=self.dispatch)

    def dispatch(self, **kwargs):
        self.calls.append(kwargs)
        if isinstance(self.reply, Exception):
            raise self.reply
        return ProviderRun(self.reply if isinstance(self.reply, str) else json.dumps(self.reply, ensure_ascii=False),
                           usage={"fixture": True}, trace=({"event": "stub-only"},))

    def checkpoint(self, **changes):
        return payload(**{"cwd": str(self.repo), **changes})

    def packet(self):
        return json.loads(self.calls[-1]["nudge_input"])

    def submit(self, **changes):
        return self.core.process_diagnostic(self.checkpoint(**changes))

    def assert_fault(self, value, kind, core=None):
        with self.assertRaises(ToolFault) as caught:
            (core or self.core).process_diagnostic(value)
        self.assertEqual(caught.exception.kind, kind)
        return caught.exception

    def test_stub_insufficient_evidence_may_silence_without_changes(self):
        # The stub chooses silence. This deliberately does not claim semantic accuracy.
        self.assertIsNone(self.submit())
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.core.journal.recent()[0]["outcome"], "silence")
        self.assertEqual(self.packet()["batch_change"], [])
        self.assertIn("p95 unknown", str(self.packet()["tool_result"]))

    def test_stub_can_return_one_key_measurement_without_code_patch(self):
        self.reply = {"feedback": MEASUREMENT_FEEDBACK}
        attempt, result = self.submit()
        self.assertEqual(result.structure, MEASUREMENT_FEEDBACK["structure"])
        self.assertEqual(result.required, MEASUREMENT_FEEDBACK["required"])
        self.assertEqual(self.packet()["batch_change"], [])
        row = self.core.journal.recent()[0]
        self.assertEqual(row["id"], attempt)
        self.assertEqual(row["outcome"], "feedback")
        self.assertEqual(row["delivered"], 0)

    def test_performance_uses_shared_dispatch_schema_and_model(self):
        self.submit()
        call = self.calls[0]
        self.assertEqual(call["system_prompt"], (ROOT / "performance-prompt.txt").read_text().strip())
        self.assertEqual(call["schema_path"], ROOT / "nudge-schema.json")
        self.assertEqual(call["model"], self.settings.model)
        self.assertEqual(call["workspace_root"], str(self.repo.resolve()))
        self.assertGreater(call["timeout_sec"], 0)
        self.assertLessEqual(call["remaining_chars"], MATERIAL_MAX_CHARS)
        row = self.core.journal.recent()[0]
        self.assertEqual(row["detail"]["usage"], {"fixture": True})
        self.assertEqual(row["detail"]["trace"], [{"event": "stub-only"}])
        trigger = row["detail"]["trigger"]
        self.assertEqual(trigger["kind"], "explicit_diagnostic_checkpoint")
        self.assertEqual(trigger["profile"], "performance")
        self.assertEqual(trigger["evidence_origin"], "actor_supplied")
        self.assertEqual(trigger["reason"], self.checkpoint()["reason"])
        self.assertEqual(trigger["progress"], self.checkpoint()["progress"])
        self.assertEqual(trigger["evidence_sha256"], DiagnosticBatch.parse(self.checkpoint()).fingerprint)
        self.assertGreaterEqual(row["detail"]["elapsed_seconds"], 0)

    def test_nonpatch_tool_inputs_never_become_batch_change(self):
        self.reply = {"feedback": MEASUREMENT_FEEDBACK}
        items = [
            evidence("content", tool_input={"path": "profile.txt", "content": "sample data"}),
            evidence("patch", tool_input={"patch": PATCH}),
            evidence("diff", tool_input={"diff": "not an edit"}),
            evidence("wrapped", tool_input={"command": PATCH}),
            evidence("raw", tool_input=PATCH),
            evidence("edit-shaped", tool_input={"file_path": "job.py", "old_string": "x", "new_string": "y"}),
        ]
        self.submit(evidence=items)
        packet = self.packet()
        self.assertEqual(packet["batch_change"], [])
        self.assertEqual(packet["file_origin"], [])
        self.assertEqual(packet["current_structure"], [])
        self.assertIn("sample data", str(packet["tool_result"]))
        self.assertIn("*** Begin Patch", str(packet["tool_result"]))

    def test_explicit_apply_patch_keeps_original_input_and_change(self):
        self.submit(evidence=[evidence(tool="apply_patch", tool_input=PATCH, output="Success. Updated job.py")])
        self.assertIn("*** Begin Patch", str(self.packet()["batch_change"]))
        self.assertIn("*** Begin Patch", str(self.packet()["tool_result"]))

    def test_successful_exit_preserves_full_stdout_stderr_and_measurement_fields(self):
        raw = {"exit_code": 0, "stdout": "BEGIN\nRAM=90%\nlatency_p95=200ms\nEND",
               "stderr": "warning: one synthetic sample", "sample_window": {"begin": 11, "end": 22}}
        self.submit(evidence=[evidence(output=raw)])
        records = {item["path"]: item["lines"] for item in self.packet()["tool_result"]}
        self.assertEqual(records["tool/read-1/output/stdout"], raw["stdout"].splitlines())
        self.assertEqual(records["tool/read-1/output/stderr"], [raw["stderr"]])
        self.assertEqual(json.loads(records["tool/read-1/output/sample_window"][0]), raw["sample_window"])
        self.assertNotIn("output_omitted", self.calls[-1]["nudge_input"])
        self.assertNotIn("tool/read-1/output/summary", records)

    def test_complete_packet_over_limit_faults_instead_of_truncating_exit_zero(self):
        value = self.checkpoint(evidence=[evidence(output={"exit_code": 0, "stdout": "head" + "x" * 20500 + "tail"})])
        DiagnosticBatch.parse(value)  # Raw input is legal; assembled complete packet is too large.
        self.assert_fault(value, "input_size")
        self.assertEqual(self.calls, [])
        rows = self.core.journal.recent()
        self.assertEqual([row["outcome"] for row in rows], ["fault"])
        self.assertEqual(rows[0]["detail"]["fault"]["kind"], "input_size")
        self.assertEqual(self.core.journal.unresolved(), [])
        self.assert_fault(value, "input_size", self.new_core())
        self.assertEqual(len(self.core.journal.recent()), 1)

    def test_packet_exact_size_boundary_is_complete_and_leaves_zero_repo_budget(self):
        value = self.checkpoint(evidence=[evidence(output="x")])
        with self.core.journal.connect() as db:
            task = dict(db.execute("SELECT * FROM rounds").fetchone())
        packet = build_diagnostic_packet(self.session, task, DiagnosticBatch.parse(value))
        value["evidence"][0]["tool_response"] += "x" * (MATERIAL_MAX_CHARS - packet.material_chars)
        exact = build_diagnostic_packet(self.session, task, DiagnosticBatch.parse(value))
        self.assertEqual(exact.material_chars, MATERIAL_MAX_CHARS)
        self.core.process_diagnostic(value)
        self.assertEqual(self.calls[0]["remaining_chars"], 0)
        output = next(item for item in self.packet()["tool_result"] if item["path"] == "tool/read-1/output")
        self.assertEqual(output["lines"], [value["evidence"][0]["tool_response"]])
        value["evidence"][0]["tool_response"] += "x"
        with self.assertRaises(ToolFault) as caught:
            build_diagnostic_packet(self.session, task, DiagnosticBatch.parse(value))
        self.assertEqual(caught.exception.kind, "input_size")

    def test_unrelated_shell_hooks_still_do_not_trigger(self):
        adapter = CodexAdapter(self.core)
        with patch("masters_nudge.codex_adapter.active_guard", return_value=False):
            for command in ("ls", "profile CPU RAM performance", "python -m unittest", "echo benchmark"):
                with self.subTest(command=command):
                    result = adapter.process({"hook_event_name": "PostToolUse", "session_id": self.session.session_id,
                        "turn_id": self.session.turn_id, "cwd": str(self.repo), "tool_name": "exec_command",
                        "tool_use_id": "shell", "tool_input": {"cmd": command}, "tool_response": {"exit_code": 0}})
                    self.assertIsNone(result)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.core.journal.recent(), [])
        hooks = json.loads((ROOT / "plugins/masters-nudge/hooks/hooks.json").read_text())
        self.assertEqual([item["matcher"] for item in hooks["hooks"]["PostToolUse"]], ["^apply_patch$"])

    def test_performance_patch_hook_uses_same_profile_and_feedback_form(self):
        self.reply = {"feedback": MEASUREMENT_FEEDBACK}
        with patch("masters_nudge.codex_adapter.active_guard", return_value=False):
            output = CodexAdapter(self.core).process({"hook_event_name": "PostToolUse", "session_id": self.session.session_id,
                "turn_id": self.session.turn_id, "cwd": str(self.repo), "tool_name": "apply_patch",
                "tool_use_id": "patch", "tool_input": PATCH, "tool_response": "Success. Updated job.py"})
        feedback = parse_feedback(json.dumps(self.reply))
        self.assertEqual(output["hookSpecificOutput"]["additionalContext"], delivery_text(feedback, profile="performance"))
        self.assertEqual(self.calls[0]["system_prompt"], (ROOT / "performance-prompt.txt").read_text().strip())

    def test_software_engineering_profile_rejects_explicit_diagnostics(self):
        regular = NudgeCore(replace(self.settings, profile="software-engineering"), dispatch=self.dispatch)
        self.assert_fault(self.checkpoint(), "configuration", regular)
        self.assertEqual(self.calls, [])

    def test_shared_parser_rejects_malformed_and_oversized_output_in_both_profiles(self):
        invalid = ["not JSON", "null", '{"feedback":{},"extra":1}', json.dumps({"feedback": {**MEASUREMENT_FEEDBACK, "extra": "x"}})]
        for name, limit in FEEDBACK_FIELD_LIMITS.items():
            invalid.extend(json.dumps({"feedback": {**MEASUREMENT_FEEDBACK, name: value}})
                           for value in ("", " ", "x" * (limit + 1), 5))
        for profile in ("software-engineering", "performance"):
            for index, raw in enumerate(invalid):
                with self.subTest(profile=profile, case=index):
                    self.core.settings = replace(self.settings, profile=profile)
                    self.core.start_round(self.session, self.request)
                    self.reply = raw
                    if profile == "performance":
                        # Distinct real evidence for each case, avoiding intentional content dedup.
                        self.assert_fault(self.checkpoint(batch_id=f"invalid-{index}", evidence=[evidence(output=f"sample={index}")]), "output")
                    else:
                        from masters_nudge.contracts import ToolCompleted
                        with self.assertRaises(ToolFault) as caught:
                            self.core.process_event(self.session, ToolCompleted(f"p-{index}", "apply_patch", PATCH, "Success"))
                        self.assertEqual(caught.exception.kind, "output")
                    self.assertEqual(self.core.journal.recent()[0]["outcome"], "fault")

    def test_shared_parser_accepts_exact_four_field_boundaries(self):
        item = {name: "x" * limit for name, limit in FEEDBACK_FIELD_LIMITS.items()}
        result = parse_feedback(json.dumps({"feedback": item}))
        self.assertEqual(len(result.message), FEEDBACK_MAX_CHARS)
        self.assertIsNone(parse_feedback('{"feedback":null}'))

    def test_provider_fault_is_durable_and_never_counted_as_silence_or_recalled(self):
        self.reply = ToolFault("timeout", "synthetic Provider did not complete")
        first = self.assert_fault(self.checkpoint(), "timeout")
        self.assertEqual(len(self.calls), 1)
        for value in (self.checkpoint(), self.checkpoint(batch_id="new-alias"),
                      self.checkpoint(batch_id="new-evidence", evidence=[evidence(output="changed measurement")])):
            with self.subTest(value=value["batch_id"]):
                repeated = self.assert_fault(value, "timeout", self.new_core())
                self.assertEqual(str(first), str(repeated))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual([row["outcome"] for row in self.core.journal.recent()], ["fault"])
        self.assertEqual(self.core.journal.unresolved(), [])

    def test_internal_dispatch_exception_is_observable_fault(self):
        self.reply = RuntimeError("synthetic transport failure")
        self.assert_fault(self.checkpoint(), "internal")
        self.assertEqual(self.core.journal.recent()[0]["outcome"], "fault")
        self.assert_fault(self.checkpoint(), "internal", self.new_core())
        self.assertEqual(len(self.calls), 1)

    def test_persistent_dedup_ignores_ids_order_reason_progress(self):
        self.reply = {"feedback": MEASUREMENT_FEEDBACK}
        first = self.checkpoint(evidence=[evidence("a", output="window=1"), evidence("b", output="window=2")])
        self.core.process_diagnostic(first)
        again = copy.deepcopy(first)
        again.update(batch_id="alias-B", reason="new narrative", progress="reviewing prior nudge")
        again["evidence"].reverse()
        for i, item in enumerate(again["evidence"]):
            item["tool_use_id"] = f"renamed-{i}"
        self.assertIsNone(self.new_core().process_diagnostic(again))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(len(self.core.journal.recent()), 1)
        with self.core.journal.connect() as db:
            aliases = db.execute("SELECT evidence_id,batch_id FROM diagnostic_batches ORDER BY evidence_id").fetchall()
        self.assertEqual({row["evidence_id"] for row in aliases}, {"batch-A", "alias-B"})
        self.assertEqual(len({row["batch_id"] for row in aliases}), 1)

    def test_dedup_persists_across_same_task_new_turn_and_reset_quota(self):
        self.submit()
        next_session = replace(self.session, turn_id="turn-2")
        self.core.start_round(next_session, "繼續；先確認瓶頸")
        self.assertIsNone(self.new_core().process_diagnostic(self.checkpoint(task_request="繼續；先確認瓶頸", batch_id="fresh-wrapper")))
        self.assertEqual(len(self.calls), 1)
        self.core.process_diagnostic(self.checkpoint(task_request="繼續；先確認瓶頸", batch_id="fresh-window",
                                                     evidence=[evidence(output="window=2; p95=30")]))
        self.assertEqual(len(self.calls), 2)

    def test_same_batch_id_cannot_change_evidence_even_via_prior_alias(self):
        self.submit()
        self.assertIsNone(self.submit(batch_id="B"))
        self.assert_fault(self.checkpoint(batch_id="B", evidence=[evidence(output="F")]), "input")
        self.assertEqual(len(self.calls), 1)

    def test_alias_conflict_remains_fault_after_silence_quota(self):
        self.submit()
        self.submit(batch_id="second", evidence=[evidence(output="second actual measurement window")])
        self.assertEqual(len(self.calls), 2)
        self.assertIsNone(self.submit(batch_id="B"))  # Register B/E despite exhausted budget.
        self.assert_fault(self.checkpoint(batch_id="B", evidence=[evidence(output="F")]), "input", self.new_core())
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(len(self.core.journal.recent()), 2)

    def test_three_feedback_and_two_silence_limits_apply_to_explicit_batches(self):
        for outcome, limit in ((None, 2), (MEASUREMENT_FEEDBACK, 3)):
            with self.subTest(outcome=outcome):
                self.core.start_round(self.session, self.request, goal=f"separate goal {limit}")
                self.reply = {"feedback": outcome}
                before = len(self.calls)
                for i in range(limit + 2):
                    self.submit(batch_id=f"q-{limit}-{i}", evidence=[evidence(output=f"window={limit}-{i}")])
                self.assertEqual(len(self.calls) - before, limit)
                self.assertEqual(self.core.journal.unresolved(), [])

    def test_previous_delivered_nudge_and_actor_progress_reach_next_packet(self):
        self.reply = {"feedback": MEASUREMENT_FEEDBACK}
        attempt, _ = self.submit()
        self.core.journal.delivered(attempt)
        self.submit(batch_id="next", progress="Collected page-fault windows after prior suggestion",
                    evidence=[evidence(output="window=2; page_faults=0")])
        self.assertEqual(self.packet()["previous_nudges"], [MEASUREMENT_FEEDBACK])
        self.assertIn("Collected page-fault windows", str(self.packet()["tool_result"]))

    def test_concurrent_identical_batches_reserve_provider_once(self):
        entered = threading.Event()
        release = threading.Event()
        completed = threading.Event()
        gate = threading.Barrier(3)
        results, errors = [], []
        lock = threading.Lock()

        def dispatch(**kwargs):
            with lock:
                self.calls.append(kwargs)
            entered.set()
            if not release.wait(5):
                raise RuntimeError("test dispatch was not released")
            return ProviderRun(json.dumps({"feedback": MEASUREMENT_FEEDBACK}))

        cores = [NudgeCore(self.settings, dispatch=dispatch) for _ in range(2)]

        def submit(core, alias):
            try:
                gate.wait(3)
                result = core.process_diagnostic(self.checkpoint(batch_id=alias))
                with lock:
                    results.append(result)
                if result is None:
                    completed.set()
            except BaseException as exc:
                errors.append(exc)

        workers = [threading.Thread(target=submit, args=(core, f"race-{i}")) for i, core in enumerate(cores)]
        try:
            for worker in workers:
                worker.start()
            gate.wait(3)
            self.assertTrue(entered.wait(3))
            self.assertTrue(completed.wait(3), "duplicate must not launch or wait for another Provider")
            self.assertEqual(len(self.calls), 1)
        finally:
            release.set()
            for worker in workers:
                worker.join(5)
        self.assertFalse(any(worker.is_alive() for worker in workers))
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 2)
        self.assertEqual(sum(result is not None for result in results), 1)
        self.assertEqual(len(self.core.journal.recent()), 1)
        self.assertEqual(self.core.journal.unresolved(), [])

    def test_never_started_checkpoint_can_retry_after_round_supersedes_queue(self):
        # Reserve a synthetic active patch and block the diagnostic behind it.
        # No Provider is run for that fixture reservation.
        self.reply = {"feedback": MEASUREMENT_FEEDBACK}
        for turn in ("turn-1", "replacement-turn"):
            with self.subTest(replacement_turn=turn):
                self.core.start_round(self.session, self.request, goal=f"queue-case-{turn}")
                old_attempt, old_task = self.core.journal.begin(self.session, [{"tool_use_id": "active-patch"}])
                first = self.checkpoint(batch_id=f"A-{turn}")
                alias = self.checkpoint(batch_id=f"B-{turn}")
                outcomes, errors = [], []

                def queued_checkpoint():
                    try:
                        outcomes.append(self.core.process_diagnostic(first))
                    except BaseException as exc:
                        errors.append(exc)

                worker = threading.Thread(target=queued_checkpoint)
                worker.start()
                queued_batch = None
                try:
                    deadline = time.monotonic() + 3
                    while time.monotonic() < deadline:
                        with self.core.journal.connect() as db:
                            registered = db.execute("SELECT batch_id FROM diagnostic_batches WHERE evidence_id=?",
                                                    (first["batch_id"],)).fetchone()
                        if registered:
                            queued_batch = registered["batch_id"]
                            break
                        time.sleep(0.01)
                    self.assertIsNotNone(queued_batch, "diagnostic was not queued behind active patch")
                    self.assertIsNone(self.core.process_diagnostic(alias))
                finally:
                    next_session = replace(self.session, turn_id=turn)
                    self.core.start_round(next_session, "new exact request")
                    worker.join(5)
                self.assertFalse(worker.is_alive())
                self.assertEqual(errors, [])
                self.assertEqual(outcomes, [None])
                before = len(self.calls)
                retried = self.new_core().process_diagnostic({**alias, "task_request": "new exact request"})
                self.assertIsNotNone(retried)
                self.assertEqual(len(self.calls), before + 1)
                self.assertIsNone(self.new_core().process_diagnostic({**first, "task_request": "new exact request"}))
                self.assertEqual(len(self.calls), before + 1)
                self.assert_fault({**alias, "task_request": "new exact request", "evidence": [evidence(output="different") ]}, "input")
                with self.core.journal.connect() as db:
                    aliases = db.execute("SELECT batch_id FROM diagnostic_batches WHERE evidence_id IN (?,?)",
                                         (first["batch_id"], alias["batch_id"])).fetchall()
                    old_events = self.core.journal._fold_events(db.execute(
                        "SELECT * FROM judgment_events WHERE batch_id=? ORDER BY seq", (queued_batch,)))
                self.assertEqual(len({row["batch_id"] for row in aliases}), 1)
                self.assertNotEqual(aliases[0]["batch_id"], queued_batch)
                self.assertIsNone(old_events[0]["started"])
                self.assertEqual(old_events[0]["outcome"], "skipped")
                self.assertFalse(self.core.journal.finish(self.session, old_attempt, old_task, "silence", {"raw_output": '{"feedback":null}'}))
                self.assertEqual(self.core.journal.unresolved(), [])

    def test_unclaimed_old_round_reservation_rebinds_without_retrying_a_started_call(self):
        # Simulate process death after queue reservation and before provider claim.
        batch = DiagnosticBatch.parse(self.checkpoint())
        _, round_id = self.core.journal.diagnostic_session(batch.cwd, batch.task_request)
        attempt, task = self.core.journal.begin(self.session, {"fixture": "unclaimed"},
                                               diagnostic=batch, expected_round_id=round_id)
        with self.core.journal.connect() as db:
            db.execute("DELETE FROM judgment_events WHERE attempt=? AND kind='started'", (attempt,))
        self.assertIsNone(self.submit(batch_id="B"))
        self.core.start_round(self.session, "replacement request")
        self.reply = {"feedback": MEASUREMENT_FEEDBACK}
        result = self.submit(batch_id="B", task_request="replacement request")
        self.assertIsNotNone(result)
        self.assertEqual(len(self.calls), 1)
        self.assertIsNone(self.submit(task_request="replacement request"))
        self.assert_fault(self.checkpoint(batch_id="B", task_request="replacement request",
                                          evidence=[evidence(output="changed content")]), "input")
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.core.journal.unresolved(), [])
        with self.core.journal.connect() as db:
            old = self.core.journal._fold_events(db.execute(
                "SELECT * FROM judgment_events WHERE attempt=? ORDER BY seq", (attempt,)))[0]
        self.assertIsNone(old["started"])
        self.assertEqual(old["outcome"], "skipped")
        self.assertFalse(self.core.journal.finish(self.session, attempt, task, "silence", {}))

    def test_missing_cwd_or_request_registration_is_fault_without_provider(self):
        for changes in ({"cwd": str(self.root)}, {"task_request": self.request + " "}, {"task_request": "not registered"}):
            with self.subTest(changes=changes):
                self.assert_fault(self.checkpoint(**changes), "input")
        self.assertEqual(self.calls, [])
        self.assertEqual(self.core.journal.recent(), [])

    def test_ambiguous_cwd_and_exact_request_is_fault_without_guessing_session(self):
        other = replace(self.session, session_id="different-host-session")
        self.core.start_round(other, self.request)
        self.assert_fault(self.checkpoint(), "input")
        self.assertEqual(self.calls, [])

    def test_stale_request_does_not_match_latest_registered_round(self):
        self.core.start_round(self.session, "new exact task request")
        self.assert_fault(self.checkpoint(), "input")
        self.assertEqual(self.calls, [])

    def test_same_turn_round_replacement_between_resolution_and_reservation_is_fault(self):
        original = self.core.journal.diagnostic_session

        def resolve_then_replace(cwd, request):
            result = original(cwd, request)
            self.core.start_round(self.session, "replacement request")
            return result

        with patch.object(self.core.journal, "diagnostic_session", side_effect=resolve_then_replace):
            self.assert_fault(self.checkpoint(), "input")
        self.assertEqual(self.calls, [])
        self.assertEqual(self.core.journal.unresolved(), [])

    def test_new_turn_round_replacement_between_resolution_and_reservation_is_fault(self):
        original = self.core.journal.diagnostic_session

        def resolve_then_replace(cwd, request):
            result = original(cwd, request)
            self.core.start_round(replace(self.session, turn_id="new-turn"), "replacement request")
            return result

        with patch.object(self.core.journal, "diagnostic_session", side_effect=resolve_then_replace):
            self.assert_fault(self.checkpoint(), "input")
        self.assertEqual(self.calls, [])

    def test_same_turn_replacement_during_provider_keeps_old_result_historical(self):
        def dispatch(**kwargs):
            self.calls.append(kwargs)
            self.core.start_round(self.session, "latest request in same host turn")
            return ProviderRun(json.dumps({"feedback": MEASUREMENT_FEEDBACK}))

        self.core.dispatch = dispatch
        self.assertIsNone(self.submit())
        old = self.core.journal.recent()[0]
        self.assertEqual(old["outcome"], "feedback")
        self.assertEqual(old["delivered"], 0)
        self.core.dispatch = self.dispatch
        self.assertIsNone(self.submit(task_request="latest request in same host turn", batch_id="fresh-alias"))
        self.assertEqual(len(self.calls), 1)
        self.submit(task_request="latest request in same host turn", batch_id="new-evidence", evidence=[evidence(output="window=2")])
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.packet()["previous_nudges"], [])

    def test_non_git_workspace_faults_before_provider(self):
        plain = self.root / "plain"
        plain.mkdir()
        self.core.start_round(replace(self.session, cwd=str(plain)), self.request)
        self.assert_fault(self.checkpoint(cwd=str(plain)), "workspace")
        self.assertEqual(self.calls, [])
        self.assertEqual(self.core.journal.recent()[0]["outcome"], "fault")

    def _reserve_interrupted(self, *, started):
        batch = DiagnosticBatch.parse(self.checkpoint())
        _, round_id = self.core.journal.diagnostic_session(batch.cwd, batch.task_request)
        attempt, task = self.core.journal.begin(self.session, {"fixture": "interrupted-reservation"},
                                               diagnostic=batch, expected_round_id=round_id)
        with self.core.journal.connect() as db:
            if not started:
                db.execute("DELETE FROM judgment_events WHERE attempt=? AND kind='started'", (attempt,))
            timeout = (self.core.journal.provider_timeout_sec + FINALIZATION_RESERVE_SEC
                       if started else self.core.journal.hook_timeout_sec)
            db.execute("UPDATE judgment_events SET happened=? WHERE attempt=? AND kind IN ('queued','started')",
                       (time.time() - timeout - 10, attempt))
        return attempt, task

    def test_expired_started_reservation_is_durable_fault_on_duplicate_retry(self):
        attempt, task = self._reserve_interrupted(started=True)
        self.assert_fault(self.checkpoint(), "timeout", self.new_core())
        row = self.core.journal.recent()[0]
        self.assertEqual(row["id"], attempt)
        self.assertEqual(row["outcome"], "fault")
        self.assertEqual(self.core.journal.unresolved(), [])
        self.assertFalse(self.core.journal.finish(self.session, attempt, task, "silence", {}))
        self.assert_fault(self.checkpoint(batch_id="new", evidence=[evidence(output="window=2")]), "timeout", self.new_core())
        self.assertEqual(self.calls, [])
        self.assertEqual(len(self.core.journal.recent()), 1)

    def test_orphaned_queued_reservation_is_fault_on_duplicate_retry(self):
        attempt, _ = self._reserve_interrupted(started=False)
        self.assert_fault(self.checkpoint(batch_id="alias-after-crash"), "timeout", self.new_core())
        row = self.core.journal.recent()[0]
        self.assertEqual(row["id"], attempt)
        self.assertEqual(row["outcome"], "fault")
        self.assertEqual(self.core.journal.unresolved(), [])
        self.assert_fault(self.checkpoint(), "timeout", self.new_core())
        self.assertEqual(self.calls, [])
        self.assertEqual(len(self.core.journal.recent()), 1)



if __name__ == "__main__":
    unittest.main()
