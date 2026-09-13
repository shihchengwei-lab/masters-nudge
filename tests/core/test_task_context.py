"""Long tasks retain their stated goal and explicitly named task source."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import source_context
from masters_nudge import checkpoints, evidence, storage
from types import SimpleNamespace

from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.contracts import SessionRef, ToolCompleted


class TaskContextTests(unittest.TestCase):
    def test_node_test_runners_are_verification_results(self):
        session = SessionRef("codex_cli", "node-validation", cwd="")

        for command in (
            "node --test test/interceptors/cache.js",
            "npx borp test/interceptors/cache.js",
        ):
            with self.subTest(command=command):
                event = ToolCompleted(
                    session,
                    "exec_command",
                    tool_input={"cmd": command},
                    tool_output={"exit_code": 0, "output": "tests passed"},
                    failed=False,
                    failure_known=True,
                )

                self.assertEqual(checkpoints.evidence_category(event), "verification")

    def test_command_paths_do_not_override_tool_semantics(self):
        session = SessionRef("codex_cli", "path-semantics", cwd="")
        cases = (
            (
                ToolCompleted(
                    session,
                    "apply_patch",
                    tool_input={
                        "patch": (
                            "*** Update File: E:/work/vitest/build/verify.py\n"
                            "@@\n-old_owner = True\n+new_owner = True\n"
                        )
                    },
                    tool_output="Done!",
                    mutating=True,
                ),
                "change",
            ),
            (
                ToolCompleted(
                    session,
                    "exec_command",
                    tool_input={"cmd": "Get-Content packages/vitest/src/index.ts"},
                    tool_output="source",
                ),
                "",
            ),
            (
                ToolCompleted(
                    session,
                    "exec_command",
                    tool_input={"cmd": "Get-Content missing/vitest/index.ts"},
                    tool_output="file not found",
                    failed=True,
                    failure_known=True,
                ),
                "",
            ),
            (
                ToolCompleted(
                    session,
                    "exec_command",
                    tool_input={"cmd": "git diff -- packages/vitest/src/index.ts"},
                    tool_output="diff",
                ),
                "",
            ),
            (
                ToolCompleted(
                    session,
                    "exec_command",
                    tool_input={"cmd": "pnpm --filter vitest build"},
                    tool_output="built",
                ),
                "verification",
            ),
        )

        for event, expected in cases:
            with self.subTest(command=event.tool_input):
                self.assertEqual(checkpoints.evidence_category(event), expected)

    def test_change_record_selects_related_source_from_the_changed_file(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            filler = "\n".join(f"unrelated_{index} = {index}" for index in range(700))
            (root / "engine.py").write_text(
                "\n".join(
                    (
                        "def decide(base, target):",
                        "    return resolve(base, target)",
                        filler,
                        "def choose_path(context, options):",
                        "    return decide(context.base, options.target)",
                    )
                ),
                encoding="utf-8",
            )
            (root / "unrelated.py").write_text(
                "SHOULD_NOT_LEAK = options.target\n",
                encoding="utf-8",
            )
            session = SessionRef("codex_cli", "related-source", cwd=raw)
            event = ToolCompleted(
                session,
                "apply_patch",
                tool_input={
                    "patch": """*** Update File: engine.py
@@
-    return old_path(options.target)
+    return decide(context.base, options.target)
"""
                },
                tool_output="changed",
                mutating=True,
            )

            rendered = checkpoints.render_evidence_record(event)

        self.assertIn("related_source:", rendered)
        self.assertIn("reference: decide", rendered)
        self.assertIn("resolution: resolved", rendered)
        self.assertIn("source: engine.py:", rendered)
        self.assertIn("def decide(base, target):", rendered)
        self.assertIn("return resolve(base, target)", rendered)
        self.assertNotIn("SHOULD_NOT_LEAK", rendered)

    def test_command_field_patch_selects_related_source(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "engine.py").write_text(
                """def decide(base, target):
    return resolve(base, target)

def choose_path(context, options):
    return old_path(options.target)
""",
                encoding="utf-8",
            )
            event = ToolCompleted(
                SessionRef("codex_cli", "command-patch", cwd=raw),
                "apply_patch",
                tool_input={
                    "command": """*** Update File: engine.py
@@
-    return old_path(options.target)
+    return decide(context.base, options.target)
"""
                },
                tool_output="changed",
                mutating=True,
            )

            rendered = checkpoints.render_evidence_record(event)

        self.assertIn("related_source:", rendered)
        self.assertIn("reference: decide", rendered)
        self.assertIn("def decide(base, target):", rendered)
        self.assertIn("return resolve(base, target)", rendered)

    def test_only_change_batches_are_normally_eligible_without_prior_read_carryover(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "eligible-results", cwd=raw)
            storage.start_turn(root, session, "只在有用時呼叫 Provider")

            first = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "read",
                        tool_input={"path": "first.py"},
                        tool_output="first source",
                    )
                ],
            )
            later_read = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "read",
                        tool_input={"path": "second.py"},
                        tool_output="second source",
                    )
                ],
            )
            changed = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "apply_patch",
                        tool_input={"patch": "change owner"},
                        tool_output="changed",
                        mutating=True,
                    )
                ],
            )
            verified = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "exec_command",
                        tool_input={"cmd": "pytest tests/test_owner.py"},
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
                        tool_input={"cmd": "python check_owner.py"},
                        tool_output="exit 1",
                        failed=True,
                        failure_known=True,
                    )
                ],
            )
            measured = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "exec_command",
                        tool_input={"cmd": "python benchmark.py"},
                        tool_output="12 ms",
                    )
                ],
            )

        self.assertFalse(first.eligible)
        self.assertFalse(later_read.eligible)
        self.assertTrue(changed.eligible)
        changed_content = "\n".join(
            record["content"] for record in changed.batch_records
        )
        self.assertNotIn("first source", changed_content)
        self.assertNotIn("second source", changed_content)
        self.assertIn("change owner", changed_content)
        self.assertFalse(verified.eligible)
        self.assertFalse(failed.eligible)
        self.assertFalse(measured.eligible)

    def test_turn_state_does_not_store_source_batch_history(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "no-source-history", cwd=raw)
            storage.start_turn(root, session, "inspect then change")
            evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "read",
                        tool_input={"path": "observed.py"},
                        tool_output="source must not enter turn state",
                    )
                ],
            )

            state = storage.load_turn_state(root, session)

        self.assertNotIn("last_source_context", state)
        self.assertNotIn("source must not enter turn state", json.dumps(state))

    def test_navigation_history_does_not_enter_a_later_change_record(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "source-survives-status", cwd=raw)
            storage.start_turn(root, session, "keep the source, ignore status")
            evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "read",
                        tool_input={"path": "owner.py"},
                        tool_output="owner source survives",
                    )
                ],
            )
            evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "exec_command",
                        tool_input={"cmd": "git status --short"},
                        tool_output="M owner.py",
                    )
                ],
            )
            changed = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "apply_patch",
                        tool_input={"patch": "change after status"},
                        tool_output="changed",
                        mutating=True,
                    )
                ],
            )

        content = "\n".join(record["content"] for record in changed.batch_records)
        self.assertNotIn("owner source survives", content)
        self.assertNotIn("git status --short", content)
        self.assertIn("change after status", content)

    def test_structured_edit_selects_related_source_without_prior_read_state(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            path = root / "packages" / "app" / "owner.ts"
            path.parent.mkdir(parents=True)
            path.write_text(
                """function decide(base, target) {
  return resolve(base, target)
}

function choosePath(context, options) {
  return decide(context.base, options.target)
}
""",
                encoding="utf-8",
            )
            session = SessionRef("claude_code", "structured-edit", cwd=raw)
            event = ToolCompleted(
                session,
                "Edit",
                tool_input={
                    "file_path": "packages/app/owner.ts",
                    "old_string": "return oldPath(options.target)",
                    "new_string": "return decide(context.base, options.target)",
                },
                tool_output="changed",
                mutating=True,
            )

            rendered = checkpoints.render_evidence_record(event)

        self.assertIn("related_source:", rendered)
        self.assertIn("reference: decide", rendered)
        self.assertIn("function decide(base, target)", rendered)
        self.assertIn("return resolve(base, target)", rendered)

    def test_related_source_covers_direct_dependencies_without_weak_member_noise(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "engine.ts").write_text(
                """function logOwner(owner) {
  return log(owner.root) // WEAK_OWNER_USE
}

// separation one
// separation two
// separation three
// separation four

function buildTarget(owner) {
  const targetRoot = owner.root // STRONG_OWNER
  return targetRoot
}

function queueBatches() {
  return "QUEUED"
}

function resetQueueCounts() {
  let normalQueue = 0
  for (const batch of batches) {
    normalQueue += batch.count
  }
  queueSize = normalQueue // RECOUNTED
}

function inspectFirst(options) {
  return options.target // WEAK_CONTEXT_ONE
}

function inspectSecond(options) {
  return options.target // WEAK_CONTEXT_TWO
}
""",
                encoding="utf-8",
            )
            selected = source_context.related_source_for_change(
                raw,
                {
                    "patch": """*** Update File: engine.ts
@@
-  return oldTarget(options.target)
+  queueBatches()
+  resetQueueCounts()
+  return decide(context.owner.root, options.target)
"""
                },
            )

        self.assertIn("STRONG_OWNER", selected)
        self.assertIn("reference: queueBatches", selected)
        self.assertIn('return "QUEUED"', selected)
        self.assertIn("reference: resetQueueCounts", selected)
        self.assertIn("queueSize = normalQueue // RECOUNTED", selected)
        self.assertNotIn("WEAK_OWNER_USE", selected)
        self.assertNotIn("WEAK_CONTEXT_ONE", selected)
        self.assertNotIn("WEAK_CONTEXT_TWO", selected)

    def test_related_source_marks_an_unresolved_direct_dependency(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "engine.ts").write_text(
                """function existingOwner() {
  return "existing"
}
""",
                encoding="utf-8",
            )

            selected = source_context.related_source_for_change(
                raw,
                {
                    "patch": """*** Update File: engine.ts
@@
-  return existingOwner()
+  return missingOwner()
"""
                },
            )

        self.assertIn("reference: missingOwner", selected)
        self.assertIn("resolution: unresolved", selected)

    def test_related_source_does_not_scan_unchanged_workspace_files(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "engine.ts").write_text(
                "export function run() { return decide('value') }\n",
                encoding="utf-8",
            )
            dependency = root / "dependency.ts"
            dependency.write_text(
                "export function decide(value) {\n"
                "  return normalize(value)\n"
                "}\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "add", "."], cwd=root, check=True)

            selected = source_context.related_source_for_change(
                raw,
                {
                    "patch": """*** Update File: engine.ts
@@
-  return oldDecision(value)
+  return decide(value)
"""
                },
            )

        self.assertIn("reference: decide", selected)
        self.assertIn("resolution: unresolved", selected)
        self.assertNotIn("source: dependency.ts:", selected)
        self.assertNotIn("return normalize(value)", selected)

    def test_related_source_reports_the_fixed_reference_limit(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "engine.ts").write_text("// unchanged\n", encoding="utf-8")
            added_calls = "\n".join(f"+  owner{index}()" for index in range(17))

            selected = source_context.related_source_for_change(
                raw,
                {
                    "patch": (
                        "*** Update File: engine.ts\n@@\n"
                        "-  oldOwner()\n"
                        f"{added_calls}\n"
                    )
                },
            )

        self.assertIn("coverage: references=16 omitted=1", selected)
        self.assertIn("reference: owner0", selected)
        self.assertIn("reference: owner15", selected)
        self.assertNotIn("reference: owner16", selected)

    def test_related_source_is_bounded_and_stays_inside_the_workspace(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "workspace"
            workspace.mkdir()
            inside = workspace / "engine.py"
            inside.write_text(
                "def decide(base, target):\n"
                "    "
                + ("x" * 6000)
                + "\n    return resolve(base, target)\n",
                encoding="utf-8",
            )
            outside = root / "outside.py"
            outside.write_text(
                "OUTSIDE_MUST_NOT_LEAK = resolve(context.base, options.target)\n",
                encoding="utf-8",
            )
            binary = workspace / "binary.py"
            binary.write_bytes(b"BINARY_MUST_NOT_LEAK\0options.target")
            patch = f"""*** Update File: engine.py
*** Update File: {outside}
*** Update File: binary.py
@@
-    return old_path(options.target)
+    return decide(context.base, options.target)
"""

            selected = source_context.related_source_for_change(
                str(workspace), {"patch": patch}
            )

        self.assertLessEqual(len(selected), source_context.RELATED_SOURCE_MAX_CHARS)
        self.assertIn("source: engine.py:", selected)
        self.assertNotIn("OUTSIDE_MUST_NOT_LEAK", selected)
        self.assertNotIn("BINARY_MUST_NOT_LEAK", selected)

    def test_exact_replay_is_not_eligible(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "duplicate-batch", cwd=raw)
            storage.start_turn(root, session, "忽略同一批重播")
            events = [
                ToolCompleted(
                    session,
                    "apply_patch",
                    tool_input={"patch": "same change"},
                    tool_output="changed",
                    mutating=True,
                )
            ]

            first = evidence.observe_tool_batch(root, events)
            duplicate = evidence.observe_tool_batch(root, events)

        self.assertTrue(first.eligible)
        self.assertFalse(duplicate.eligible)
        self.assertEqual(duplicate.batch_records, ())

    def test_packet_keeps_every_post_tool_batch_result_in_native_order(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "complete-batch", cwd=raw)
            storage.start_turn(root, session, "修正 ownership，不要逐一封堵特例")
            events = [
                ToolCompleted(
                    session,
                    "read",
                    tool_input={"path": "owner.py"},
                    tool_output="source-one: existing owner",
                    native_event_name="PostToolBatch",
                ),
                ToolCompleted(
                    session,
                    "apply_patch",
                    tool_input={"patch": "change-two: add guard"},
                    tool_output="result-two: changed",
                    mutating=True,
                    native_event_name="PostToolBatch",
                ),
                ToolCompleted(
                    session,
                    "exec_command",
                    tool_input={"cmd": "pytest owner_test.py"},
                    tool_output="result-three: edge still fails",
                    failed=True,
                    failure_known=True,
                    native_event_name="PostToolBatch",
                ),
                ToolCompleted(
                    session,
                    "apply_patch",
                    tool_input={"patch": "change-four: add fallback flag"},
                    tool_output="result-four: changed",
                    mutating=True,
                    native_event_name="PostToolBatch",
                ),
            ]

            observed = evidence.observe_tool_batch(root, events)
            packet = source_context.build_checkpoint_packet(
                task_anchor=observed.turn_state["task_anchor"],
                evidence_records=observed.batch_records,
            )

        self.assertIn("[task beginning]", packet)
        self.assertIn("[decision evidence]", packet)
        ordered_markers = [
            "[tool result seq=1 category=observation]",
            "owner.py",
            "source-one: existing owner",
            "[tool result seq=2 category=change]",
            "change-two: add guard",
            "[tool result seq=3 category=failure]",
            "result-three: edge still fails",
            "[tool result seq=4 category=change]",
            "change-four: add fallback flag",
        ]
        positions = [packet.index(marker) for marker in ordered_markers]
        self.assertEqual(positions, sorted(positions))

    def test_single_result_uses_packet_space_left_by_the_actual_task(self):
        middle = "RELATION_OWNER_MUST_SURVIVE"
        event = ToolCompleted(
            SessionRef("codex_cli", "dynamic-single", cwd=""),
            "read",
            tool_input={"path": "owner.py"},
            tool_output=("source-head\n" * 180) + middle + ("source-tail\n" * 180),
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            storage.start_turn(root, event.session, "檢查 owner")
            observed = evidence.observe_tool_batch(root, [event])
            packet = source_context.build_checkpoint_packet(
                task_anchor=observed.turn_state["task_anchor"],
                evidence_records=observed.batch_records,
            )

        self.assertIn(middle, packet)
        self.assertLessEqual(len(packet), source_context.PACKET_MAX_CHARS)

    def test_multiple_results_share_the_remaining_packet_space(self):
        first_middle = "FIRST_RELATION_MUST_SURVIVE"
        second_middle = "SECOND_RELATION_MUST_SURVIVE"
        records = [
            {
                "seq": 1,
                "category": "observation",
                "content": ("a" * 1700) + first_middle + ("b" * 1700),
            },
            {
                "seq": 2,
                "category": "change",
                "content": ("c" * 1700) + second_middle + ("d" * 1700),
            },
        ]

        packet = source_context.build_checkpoint_packet(
            task_anchor="檢查資料與控制流程的關係",
            evidence_records=records,
        )

        self.assertIn(first_middle, packet)
        self.assertIn(second_middle, packet)
        self.assertLessEqual(len(packet), source_context.PACKET_MAX_CHARS)

    def test_large_task_and_batch_still_obey_the_one_packet_limit(self):
        records = [
            {"seq": index, "category": "observation", "content": "x" * 10000}
            for index in range(1, 5)
        ]

        packet = source_context.build_checkpoint_packet(
            task_anchor="task " * 1000,
            task_sources={"TASK.md": "source " * 2000},
            evidence_records=records,
        )

        self.assertLessEqual(len(packet), source_context.PACKET_MAX_CHARS)
        for index in range(1, 5):
            self.assertIn(f"[tool result seq={index} category=observation]", packet)

    def test_packet_uses_the_current_batch_without_prior_batch_history(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "clean-boundaries", cwd=raw)
            storage.start_turn(root, session, "保留乾淨的開頭與結尾")
            evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "read",
                        tool_input={"path": "old.py"},
                        tool_output="prior-batch-result",
                    )
                ],
            )
            current = evidence.observe_tool_batch(
                root,
                [
                    ToolCompleted(
                        session,
                        "read",
                        tool_input={"path": "current.py"},
                        tool_output="current-batch-result",
                    )
                ],
            )

            packet = source_context.build_checkpoint_packet(
                task_anchor=current.turn_state["task_anchor"],
                evidence_records=current.batch_records,
            )

        self.assertIn("current-batch-result", packet)
        self.assertNotIn("prior-batch-result", packet)

    def test_task_source_is_read_once_when_the_turn_starts(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            task_file = root / "TASK.md"
            task_file.write_text("原始驗收：只保留必要責任。", encoding="utf-8")
            session = SessionRef("codex_cli", "task-source", cwd=raw, repo_root=raw)

            storage.start_turn(root / "data", session, "依照 `TASK.md` 執行")
            task_file.write_text("工作途中被改寫的內容", encoding="utf-8")
            state = storage.load_turn_state(root / "data", session)

        self.assertEqual(
            state["task_sources"],
            {"TASK.md": "原始驗收：只保留必要責任。"},
        )

    def test_plain_explicit_task_path_is_read_without_markdown_punctuation(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "TASK.md").write_text(
                "白話路徑也必須成為任務證據。", encoding="utf-8"
            )
            session = SessionRef("codex_cli", "plain-task", cwd=raw, repo_root=raw)

            storage.start_turn(root / "data", session, "請依照 TASK.md 執行")
            state = storage.load_turn_state(root / "data", session)

        self.assertEqual(
            state["task_sources"],
            {"TASK.md": "白話路徑也必須成為任務證據。"},
        )

    def test_codex_recovers_an_explicit_goal_from_the_transcript(self):
        with tempfile.TemporaryDirectory() as raw:
            transcript = Path(raw) / "session.jsonl"
            transcript.write_text(
                json.dumps(
                    {
                        "payload": {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_text",
                                    "text": (
                                        '<codex_internal_context source="goal">'
                                        "<objective>持續刪除不承重機制</objective>"
                                        "</codex_internal_context>"
                                    ),
                                }
                            ],
                        }
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            data = Path(raw) / "data"
            core = SimpleNamespace(
                settings=SimpleNamespace(paths=SimpleNamespace(data_dir=data)),
                log_error=lambda _message: None,
            )
            CodexAdapter(core).process(
                {
                    "hook_event_name": "UserPromptSubmit",
                    "session_id": "long-goal",
                    "cwd": raw,
                    "prompt": "",
                    "transcript_path": str(transcript),
                }
            )
            state = storage.load_turn_state(
                data,
                SessionRef("codex_cli", "long-goal", cwd=raw),
            )

        self.assertEqual(state["task_anchor"], "持續刪除不承重機制")


if __name__ == "__main__":
    unittest.main()
