"""The event pipeline preserves facts instead of inferring tool semantics."""

from __future__ import annotations

import json
import tempfile
import unittest
from unittest import mock
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

    def test_mutation_target_keeps_callable_references_from_the_full_change(self):
        added_lines = [f"+  const marker{index} = {index};" for index in range(10)]
        patch = "\n".join(
            (
                "*** Begin Patch",
                "*** Update File: src/runtime.ts",
                "@@",
                *added_lines,
                "@@",
                "+  drainBatch(true, pending);",
                "*** End Patch",
            )
        )

        mutation = contracts.mutation_evidence_from_input({"patch": patch})

        self.assertIsNotNone(mutation)
        target = mutation.targets[0]
        self.assertEqual(len(target.anchors), 8)
        self.assertIn("drainBatch", target.references)


class FactualControlFlowTests(unittest.TestCase):
    def test_current_mutation_includes_bounded_post_change_source_context(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "src" / "runtime.ts"
            source.parent.mkdir()
            source.write_text(
                "\n".join(
                    (
                        "async function linkDependency(dependency) {",
                        "  const discoveredModules = new Set();",
                        "  const unlinkedModules = new Set();",
                        *(f"  step{index}();" for index in range(20)),
                        "  for (const dependency of unlinkedModules) {",
                        "  if (dependency.status === 'unlinked') {",
                        "    await linkDependency(dependency);",
                        "  }",
                        "}",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            events = normalize_tool_batch(
                {
                    "hook_event_name": "PostToolBatch",
                    "session_id": "post-change-source",
                    "cwd": raw,
                    "tool_calls": [
                        {
                            "tool_name": "apply_patch",
                            "tool_input": {
                                "command": (
                                    "*** Begin Patch\n"
                                    "*** Update File: src/runtime.ts\n"
                                    "@@\n"
                                    "+  const discoveredModules = new Set();\n"
                                    "+  const unlinkedModules = new Set();\n"
                                    "@@\n"
                                    "-  for (const dependency of modules) {\n"
                                    "+  for (const dependency of unlinkedModules) {\n"
                                    "*** End Patch"
                                )
                            },
                            "tool_response": {},
                        }
                    ],
                }
            )
            self.assertIn(
                "for (const dependency of unlinkedModules) {",
                events[0].mutation.targets[0].anchors,
            )
            observed = evidence.observe_tool_batch(root / "data", events)
            packet = source_context.build_checkpoint_packet(
                task_anchor="fix dependency linking",
                evidence_records=observed.batch_records,
            )

        self.assertIn("[post-change source context]", packet)
        self.assertLess(
            packet.index("[post-change source context]"),
            packet.index("actual_input:"),
        )
        self.assertIn("source: src/runtime.ts", packet)
        self.assertIn("const unlinkedModules = new Set", packet)
        self.assertIn("if (dependency.status === 'unlinked')", packet)

    def test_post_change_source_stays_at_changed_anchors(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "src" / "runtime.ts"
            source.parent.mkdir()
            source.write_text(
                "\n".join(
                    (
                        "let _transport: Transport;",
                        "function initDefaults() {",
                        "  _transport = new Transport();",
                        "}",
                        "initDefaults();",
                        "function submit(item) {",
                        "  if (item.urgent) {",
                        "    if (!_transport) {",
                        "      item.urgent = false;",
                        "    } else {",
                        "      return sendImmediately(item);",
                        "    }",
                        "  }",
                        "  enqueue(item);",
                        "}",
                        *(f"function unrelatedBefore{index}() {{}}" for index in range(24)),
                        "function drainBatch(isDeferred, shouldDrain) {",
                        *(f"  const marker{index} = {index};" for index in range(10)),
                        "  state.pending = shouldDrain && isDeferred;",
                        "}",
                        *(f"function unrelatedMiddle{index}() {{}}" for index in range(24)),
                        "function enqueue(item) {",
                        "  if (queueReachedLimit()) {",
                        "    drainBatch(!item.urgent, true);",
                        "  }",
                        "}",
                        *(f"function unrelatedAfter{index}() {{}}" for index in range(24)),
                        "function finishManualDrain(pending) {",
                        "  drainBatch(true, pending);",
                        "}",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            patch = "\n".join(
                (
                    "*** Begin Patch",
                    "*** Update File: src/runtime.ts",
                    "@@",
                    *(f"+  const marker{index} = {index};" for index in range(10)),
                    "@@",
                    "+  drainBatch(true, pending);",
                    "*** End Patch",
                )
            )
            mutation = contracts.mutation_evidence_from_input({"patch": patch})

            rendered = source_context.render_post_change_sources(
                SessionRef("codex_cli", "relationship-context", cwd=raw), mutation
            )

        self.assertLessEqual(
            len(rendered), source_context.POST_CHANGE_SOURCE_MAX_CHARS
        )
        self.assertIn("const marker9 = 9", rendered)
        self.assertNotIn("[same-file relationship context]", rendered)
        self.assertNotIn("[complete same-file lexical inventories]", rendered)
        self.assertNotIn("drainBatch(!item.urgent, true)", rendered)
        self.assertNotIn("if (item.urgent)", rendered)
        self.assertNotIn("_transport = new Transport()", rendered)

    def test_post_change_source_does_not_infer_a_distant_data_flow(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "runtime.ts"
            source.write_text(
                "\n".join(
                    (
                        "function submit(item) {",
                        "  if (item.urgent) {",
                        "    item.urgent = false;",
                        "  }",
                        "}",
                        *(f"const before{index} = {index};" for index in range(20)),
                        "changedAnchor();",
                        *(f"const after{index} = {index};" for index in range(7)),
                        *(f"helper{index}(Mode.Value{index});" for index in range(8)),
                        *(f"const gap{index} = {index};" for index in range(20)),
                        "drainBatch(!item.urgent, true);",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            mutation = contracts.MutationEvidence(
                "patch",
                (
                    contracts.MutationTarget(
                        "runtime.ts",
                        anchors=("changedAnchor();",),
                        references=tuple(
                            [*(f"helper{index}" for index in range(8)), "drainBatch"]
                        ),
                    ),
                ),
            )

            with mock.patch.object(
                source_context, "POST_CHANGE_SOURCE_MAX_CHARS", 1200
            ):
                rendered = source_context.render_post_change_sources(
                    SessionRef("codex_cli", "prioritized-relationship", cwd=raw),
                    mutation,
                )

        self.assertLessEqual(len(rendered), 1200)
        self.assertIn("changedAnchor();", rendered)
        self.assertNotIn("drainBatch(!item.urgent, true)", rendered)
        self.assertNotIn("if (item.urgent)", rendered)
        self.assertNotIn("item.urgent = false", rendered)

    def test_post_change_source_does_not_infer_a_distant_lifecycle(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "runtime.ts"
            source.write_text(
                "\n".join(
                    (
                        "let _retryTimer: Timer;",
                        "self.pause = () => {",
                        "  _clearMainTimer();",
                        "  paused = true;",
                        "};",
                        "function flush() {",
                        "  if (_retryTimer) {",
                        "    _retryTimer.cancel();",
                        "    _retryTimer = null;",
                        "  }",
                        "}",
                        *(f"function unrelated{index}() {{}}" for index in range(24)),
                        "function _clearMainTimer() {",
                        "  mainTimer?.cancel();",
                        "}",
                        *(f"const gap{index} = {index};" for index in range(24)),
                        "function scheduleRetry(doWork) {",
                        "  if (doWork && _retryTimer == null) {",
                        "    _clearMainTimer();",
                        "    _retryTimer = _createTimer(runRetry, 0);",
                        "  }",
                        "}",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            mutation = contracts.MutationEvidence(
                "patch",
                (
                    contracts.MutationTarget(
                        "runtime.ts",
                        anchors=("_retryTimer = _createTimer(runRetry, 0);",),
                        references=(
                            "_retryTimer.cancel",
                            "_createTimer",
                            "_clearMainTimer",
                        ),
                    ),
                ),
            )

            rendered = source_context.render_post_change_sources(
                SessionRef("codex_cli", "lifecycle-context", cwd=raw), mutation
            )

        self.assertIn("_retryTimer = _createTimer(runRetry, 0);", rendered)
        self.assertIn("function scheduleRetry(doWork)", rendered)
        self.assertNotIn("[same-file relationship context]", rendered)
        self.assertNotIn("_retryTimer.cancel();", rendered)
        self.assertNotIn("self.pause", rendered)

    def test_post_change_source_excludes_unrelated_value_focuses_under_budget(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            source = root / "runtime.ts"
            long_filler = "const filler = '" + "x" * 300 + "';"
            source.write_text(
                "\n".join(
                    (
                        "if (item.urgent) { // first-flow",
                        *(long_filler for _ in range(8)),
                        "item.urgent = false; // middle-flow",
                        *(long_filler for _ in range(8)),
                        "record(item.urgent); // last-flow",
                        *(f"const before{index} = {index};" for index in range(20)),
                        "changedAnchor();",
                        *(f"const after{index} = {index};" for index in range(20)),
                        "drainBatch(!item.urgent, true);",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            mutation = contracts.MutationEvidence(
                "patch",
                (
                    contracts.MutationTarget(
                        "runtime.ts",
                        anchors=("changedAnchor();",),
                        references=("drainBatch",),
                    ),
                ),
            )

            with mock.patch.object(
                source_context, "POST_CHANGE_SOURCE_MAX_CHARS", 1200
            ):
                rendered = source_context.render_post_change_sources(
                    SessionRef("codex_cli", "bounded-value-focuses", cwd=raw),
                    mutation,
                )

        self.assertIn("changedAnchor();", rendered)
        self.assertNotIn("if (item.urgent) { // first-flow", rendered)
        self.assertNotIn("item.urgent = false; // middle-flow", rendered)
        self.assertNotIn("record(item.urgent); // last-flow", rendered)

    def test_post_change_source_context_cannot_read_outside_workspace(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "workspace"
            workspace.mkdir()
            (root / "secret.txt").write_text(
                "must not enter mutation evidence", encoding="utf-8"
            )
            session = SessionRef(
                "codex_cli",
                "contained-source",
                cwd=str(workspace),
                repo_root=str(workspace),
            )
            mutation_input = {
                "path": "../secret.txt",
                "old_string": "old",
                "new_string": "must not enter mutation evidence",
            }
            observed = evidence.observe_tool_batch(
                root / "data",
                [
                    ToolCompleted(
                        session,
                        "edit",
                        tool_input=mutation_input,
                        tool_output={"success": True},
                        mutation=contracts.mutation_evidence_from_input(mutation_input),
                    )
                ],
            )

        rendered = observed.batch_records[0]["content"]
        self.assertNotIn("[post-change source context]", rendered)
        self.assertEqual(rendered.count("must not enter mutation evidence"), 1)

    def test_post_change_source_context_caps_long_source_lines(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target_line = "changed_" + "x" * 1000
            (root / "large.txt").write_text(
                "\n".join(
                    [*("filler_" + "y" * 1000 for _ in range(20)), target_line]
                ),
                encoding="utf-8",
            )
            mutation_input = {
                "path": "large.txt",
                "old_string": "old",
                "new_string": target_line,
            }
            mutation = contracts.mutation_evidence_from_input(mutation_input)
            rendered = source_context.render_post_change_sources(
                SessionRef("codex_cli", "bounded-lines", cwd=raw), mutation
            )

        self.assertLessEqual(
            len(rendered), source_context.POST_CHANGE_SOURCE_MAX_CHARS
        )
        self.assertIn("changed_", rendered)
        self.assertNotIn("x" * 300, rendered)

    def test_nudge_does_not_create_a_cross_batch_pairing_state(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "no-pairing", cwd=raw)
            storage.start_turn(root, session, "inspect each mutation batch")
            storage.append_host_returned_nudge(
                root,
                session,
                status="taste_nudge",
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
    def test_each_positive_status_identifies_the_visible_evidence_record(self):
        for status in ("contract_warning", "taste_nudge"):
            with self.subTest(status=status):
                result = provider_contract.parse_nudge_result(
                    json.dumps(
                        {
                            "status": status,
                            "principle": "causality",
                            "evidence_seq": 2,
                            "anchor": "owner",
                            "relationship": "依賴沒有明確完成邊界。",
                        },
                        ensure_ascii=False,
                    )
                )

                self.assertEqual(result["status"], status)
                self.assertEqual(result["evidence_seq"], 2)

    def test_finding_without_evidence_sequence_is_invalid(self):
        result = provider_contract.parse_nudge_result(
            json.dumps(
                {
                    "status": "contract_warning",
                    "principle": "causality",
                    "anchor": "owner",
                    "relationship": "依賴沒有明確完成邊界。",
                },
                ensure_ascii=False,
            )
        )

        self.assertEqual(result["status"], "error")

    def test_ambiguous_legacy_finding_status_is_invalid(self):
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
