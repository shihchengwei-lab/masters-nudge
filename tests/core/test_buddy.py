#!/usr/bin/env python3
"""Smoke tests for Masters' Nudge.

Run:  python -m unittest test_buddy -v
"""

import inspect
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))


# ── Persona prompt selection ─────────────────────────────────────────

class TestBranding(unittest.TestCase):
    """Public surfaces use the new name while legacy paths stay compatible."""

    def test_public_brand_name_is_masters_nudge(self):
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        readme_zh = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")
        prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")
        window = (HERE / "buddy_window.py").read_text(encoding="utf-8")

        self.assertTrue(readme.startswith("# Masters’ Nudge"))
        self.assertTrue(readme_zh.startswith("# Masters’ Nudge"))
        self.assertIn("You are Masters’ Nudge", prompt)
        self.assertIn('self.root.title("Masters’ Nudge")', window)

    def test_agent_visible_checkpoint_labels_the_independent_opinion(self):
        import claude_checkpoint as checkpoint

        output = checkpoint.build_hook_output(
            "PostToolUseFailure", "測試結果跟宣告不一致"
        )
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(context, "獨立第二意見：\n測試結果跟宣告不一致")

    def test_default_sprite_is_transparent_and_detectable(self):
        from PIL import Image
        import buddy_window

        with Image.open(HERE / "spritesheet.webp") as source:
            sprite = source.convert("RGBA")
        alpha = sprite.getchannel("A")
        rows = buddy_window.detect_frames(sprite)

        self.assertEqual(alpha.getextrema()[0], 0)
        self.assertGreater(alpha.getbbox()[2] - alpha.getbbox()[0], 0)
        self.assertEqual(len(rows), 2)
        self.assertEqual([len(row) for row in rows], [6, 6])

    def test_default_sprite_cells_have_transparent_edge_padding(self):
        from PIL import Image

        with Image.open(HERE / "spritesheet.webp") as source:
            sprite = source.convert("RGBA")
        cell_width = sprite.width // 6
        cell_height = sprite.height // 2
        self.assertEqual(sprite.size, (cell_width * 6, cell_height * 2))

        alpha = sprite.getchannel("A")
        for row in range(2):
            for column in range(6):
                left = column * cell_width
                top = row * cell_height
                cell = alpha.crop((left, top, left + cell_width, top + cell_height))
                self.assertFalse(cell.crop((0, 0, 2, cell_height)).getbbox())
                self.assertFalse(
                    cell.crop((cell_width - 2, 0, cell_width, cell_height)).getbbox()
                )

    def test_lens_backgrounds_are_distinct_dark_colors(self):
        import buddy_window

        colors = [
            buddy_window.lens_background(persona)
            for persona in ("jeff", "linus", "fowler", "beck", "lamport", "carmack")
        ]
        self.assertEqual(len(set(colors)), 6)
        self.assertEqual(buddy_window.lens_background("unknown"), buddy_window.BG)
        self.assertEqual(buddy_window.lens_background("unknown"), buddy_window.BG)
        for color in colors:
            self.assertRegex(color, r"^#[0-9A-Fa-f]{6}$")
            self.assertLess(max(int(color[i:i + 2], 16) for i in (1, 3, 5)), 100)

class TestPersonaPromptSelection(unittest.TestCase):
    PERSONAS = {
        "jeff": "Jeff Dean",
        "linus": "Linus Torvalds",
        "fowler": "Martin Fowler",
        "beck": "Kent Beck",
        "lamport": "Leslie Lamport",
        "carmack": "John Carmack",
    }

    def test_each_persona_defines_concepts_focus_and_two_internal_questions(self):
        for persona in self.PERSONAS:
            with self.subTest(persona=persona):
                overlay = (HERE / "personas" / f"{persona}.txt").read_text(
                    encoding="utf-8"
                )
                for heading in (
                    "### 核心概念",
                    "### 觀察場景",
                    "### 關注面向",
                    "### 內部追問",
                    "### 形成 Nudge",
                ):
                    self.assertEqual(overlay.count(heading), 1)
                question_block = overlay.split("### 內部追問", 1)[1].split(
                    "### 形成 Nudge", 1
                )[0]
                questions = [
                    line.removeprefix("- ").strip()
                    for line in question_block.splitlines()
                    if line.startswith("- ")
                ]
                self.assertEqual(len(questions), 2)
                for question in questions:
                    self.assertTrue(question.endswith("？"))

    def test_each_persona_has_a_distinct_workflow_thesis_and_grounding_rule(self):
        concept_anchors = {
            "jeff": "constraint、ownership 或 source of truth",
            "beck": "從假設到回饋的距離",
            "fowler": "某份知識可能沒有清楚的家",
            "linus": "把決定往後延",
            "lamport": "所有可能發生的事件順序",
            "carmack": "抽象描述不會讓成本消失",
        }
        scene_anchors = {
            "jeff": "換一支顏色的筆",
            "beck": "未來工作全部翻到背面",
            "fowler": "頁邊貼上一張小標籤",
            "linus": "用粗筆寫下「多了什麼？」",
            "lamport": "卡的邊緣仔細對齊",
            "carmack": "把架構圖推到一旁",
        }

        for persona, concept_anchor in concept_anchors.items():
            with self.subTest(persona=persona):
                overlay = (HERE / "personas" / f"{persona}.txt").read_text(
                    encoding="utf-8"
                )
                self.assertIn(concept_anchor, overlay)
                self.assertIn(scene_anchors[persona], overlay)
                self.assertIn("packet 必須", overlay)
                self.assertIn("提醒要", overlay)
                if persona == "fowler":
                    self.assertIn("優先完成這條變更擴散", overlay)
                    self.assertIn("回饋時機、範圍或系統邊界", overlay)

    def test_persona_directory_contains_exactly_the_supported_overlays(self):
        files = {path.stem for path in (HERE / "personas").glob("*.txt")}
        self.assertEqual(files, set(self.PERSONAS))

    def test_base_prompt_matches_structured_output_contract(self):
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn('{"status":"finding"', base_prompt)
        self.assertIn('{"status":"no_finding","finding":""}', base_prompt)
        self.assertNotIn("這輪沒看到明顯問題。", base_prompt)

    def test_base_prompt_examples_do_not_use_old_imperative_phrases(self):
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        conflicting_examples = (
            "回去對一下需求",
            "拆兩句各講一件事",
            "提一下保留前面的選項",
            "補個檢查步驟",
        )
        for phrase in conflicting_examples:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, base_prompt)

    def test_base_prompt_matches_minimal_evidence_packet_labels(self):
        import source_context

        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")
        packet = source_context.build_stop_packet(
            task_anchor="修正登入錯誤",
            last_assistant_message="已完成",
            task_sources="ISSUE.md\n登入逾時時不得遺失 session",
        )

        self.assertIn("Use only the supplied packet", base_prompt)
        self.assertIn("original task", base_prompt)
        self.assertIn("current observable result", base_prompt)
        self.assertIn("Recent injected Nudges", base_prompt)
        self.assertIn("a separate exclusion set", base_prompt)
        self.assertIn("[contract]", packet)
        self.assertIn("[current result]", packet)
        self.assertNotIn("runtime_output:", packet)
        self.assertNotIn("Decision frame", base_prompt)
        self.assertNotIn("current approach", base_prompt)


# ── 3. Source evidence packets ───────────────────────────────────────

class TestSourceContext(unittest.TestCase):

    def setUp(self):
        import source_context
        self.source = source_context

    def test_head_tail_keeps_both_ends_with_explicit_marker(self):
        text = "HEAD_MARKER" + ("x" * 500) + "TAIL_MARKER"

        result = self.source.head_tail(text, 120)

        self.assertLessEqual(len(result), 120)
        self.assertIn("HEAD_MARKER", result)
        self.assertIn("TAIL_MARKER", result)
        self.assertIn("中段已截斷", result)

    def test_head_tail_leaves_short_text_unchanged(self):
        self.assertEqual(self.source.head_tail("short", 100), "short")

    def test_turn_state_saves_bounded_task_anchor_and_transcript_offset(self):
        from masters_nudge import storage
        from masters_nudge.contracts import SessionRef

        with tempfile.TemporaryDirectory() as tmpdir:
            transcript = Path(tmpdir) / "session.jsonl"
            transcript.write_text("existing transcript\n", encoding="utf-8")
            expected_offset = transcript.stat().st_size
            prompt = "PROMPT_HEAD" + ("p" * 3000) + "PROMPT_TAIL"
            session = SessionRef("claude_code", "session/unsafe")

            storage.start_turn(
                Path(tmpdir), session, prompt, transcript_path=str(transcript)
            )
            state = storage.load_turn_state(Path(tmpdir), session)

        self.assertLessEqual(
            len(state["task_anchor"]), self.source.TASK_ANCHOR_MAX_CHARS
        )
        self.assertIn("PROMPT_HEAD", state["task_anchor"])
        self.assertIn("PROMPT_TAIL", state["task_anchor"])
        self.assertEqual(state["transcript_offset"], expected_offset)

    def test_turn_start_loads_an_explicit_referenced_contract_file(self):
        from masters_nudge import storage
        from masters_nudge.contracts import SessionRef

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace = root / "workspace"
            workspace.mkdir()
            (workspace / "ISSUE.md").write_text(
                "# Expected behavior\nUse the docstring instead of alias text.\n",
                encoding="utf-8",
            )
            session = SessionRef(
                "codex_cli",
                "contract-source",
                cwd=str(workspace),
                repo_root=str(workspace),
            )

            storage.start_turn(
                root / "data",
                session,
                "Read `ISSUE.md` and resolve it completely.",
            )
            state = storage.load_turn_state(root / "data", session)

        self.assertEqual(
            state["task_sources"],
            {
                "ISSUE.md": (
                    "# Expected behavior\n"
                    "Use the docstring instead of alias text."
                )
            },
        )

    def test_layered_evidence_uses_one_cross_section_chronology(self):
        from masters_nudge import storage
        from masters_nudge.contracts import SessionRef

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            session = SessionRef("codex_cli", "chronology")
            storage.start_turn(root, session, "修正目前失敗")
            storage.record_turn_evidence(
                root, session, category="failure", record="pytest: 1 failed"
            )
            storage.record_turn_evidence(
                root, session, category="change", record="auth.py changed"
            )
            state = storage.record_turn_evidence(
                root, session, category="verification", record="pytest: 8 passed"
            )

        self.assertEqual(state["evidence_seq"], 3)
        self.assertEqual(
            [
                {"seq": 1, "category": "failure", "scope": "", "content": "pytest: 1 failed"},
                {"seq": 2, "category": "change", "scope": "", "content": "auth.py changed"},
                {"seq": 3, "category": "verification", "scope": "", "content": "pytest: 8 passed"},
            ],
            state["evidence_records"],
        )
        self.assertNotIn("change_evidence", state)
        self.assertNotIn("verification_evidence", state)
        self.assertNotIn("failure_history", state)

    def test_packet_keeps_newest_evidence_records_with_bounded_excerpts(self):
        records = [
            {"seq": 1, "category": "change", "content": "OLD\n" + "a" * 2200},
            {"seq": 2, "category": "change", "content": "CORE\n" + "b" * 2200},
            {"seq": 3, "category": "verification", "content": "CHECKED\n" + "c" * 2200},
            {"seq": 4, "category": "change", "content": "LATEST\n" + "d" * 2200},
        ]

        packet = self.source.build_checkpoint_packet(
            task_anchor="修正行為",
            evidence_records=records,
        )

        self.assertNotIn("OLD", packet)
        self.assertIn("CORE", packet)
        self.assertIn("CHECKED", packet)
        self.assertIn("LATEST", packet)
        self.assertIn(self.source.TRUNCATION_MARKER, packet)

    def test_packet_uses_the_latest_results_without_failure_priority(self):
        records = [
            {"seq": 1, "category": "failure", "content": "OPEN_FAILURE"},
            {"seq": 2, "category": "verification", "content": "CHECK_2"},
            {"seq": 3, "category": "verification", "content": "CHECK_3"},
            {"seq": 4, "category": "change", "content": "LATEST_CHANGE"},
        ]

        packet = self.source.build_checkpoint_packet(
            task_anchor="修正行為",
            evidence_records=records,
        )

        self.assertNotIn("OPEN_FAILURE", packet)
        self.assertIn("CHECK_2", packet)
        self.assertIn("CHECK_3", packet)
        self.assertIn("LATEST_CHANGE", packet)

    def test_turn_state_rejects_generic_inspection_records(self):
        from masters_nudge.contracts import SessionRef
        from masters_nudge import storage

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "inspection")
            storage.start_turn(root, session, "修正公開行為")
            state = storage.record_turn_evidence(
                root,
                session,
                category="inspection",
                record="inspection:\nassert public_order == [C, A, B]",
            )

        self.assertEqual([], state["evidence_records"])

    def test_checkpoint_packet_carries_bounded_research_state(self):
        packet = self.source.build_checkpoint_packet(
            task_anchor="修正登入測試",
            task_sources="ISSUE.md\n逾時時仍應保留 session",
            evidence_records=[
                {"seq": 1, "category": "change", "content": "auth.py 修改 14 行"},
                {"seq": 2, "category": "verification", "content": "pytest: 8 passed"},
                {"seq": 3, "category": "failure", "content": "pytest: 2 failed"},
            ],
        )

        self.assertIn("[contract]", packet)
        self.assertIn("修正登入測試", packet)
        self.assertIn("逾時時仍應保留 session", packet)
        self.assertIn("[current result]", packet)
        self.assertIn("auth.py 修改 14 行", packet)
        self.assertIn("8 passed", packet)
        self.assertIn("2 failed", packet)
        self.assertNotIn("review_event:", packet)
        self.assertNotIn("正在調整 auth.py", packet)
        self.assertNotIn("[transcript", packet)

    def test_explicit_referenced_task_source_is_promoted_without_navigation_noise(self):
        captured = self.source.capture_referenced_task_source(
            "Read `ISSUE.md` and resolve it.",
            {"cmd": "sed -n '1,220p' ISSUE.md"},
            {"content": "# Issue\nPreserve the old positional API."},
        )
        ignored = self.source.capture_referenced_task_source(
            "Read `ISSUE.md` and resolve it.",
            {"cmd": "rg -n BaseConstraint django"},
            {"content": "django/core/constraints.py:10"},
        )
        poisoned_listing = self.source.capture_referenced_task_source(
            "Read `ISSUE.md` and resolve it.",
            {"cmd": "pwd; Get-ChildItem ISSUE.md"},
            {"content": "C:/repo\nISSUE.md"},
        )
        mixed_read_and_listing = self.source.capture_referenced_task_source(
            "Read `ISSUE.md` and resolve it.",
            {"cmd": "Get-Content ISSUE.md; Get-ChildItem -Recurse"},
            {"content": "# Issue\nPreserve the API.\n./src/app.py"},
        )
        similarly_named_file = self.source.capture_referenced_task_source(
            "Read `ISSUE.md` and resolve it.",
            {"cmd": "cat NOTISSUE.md"},
            {"content": "unrelated"},
        )
        direct_read = self.source.capture_referenced_task_source(
            "Read `ISSUE.md` and resolve it.",
            {"file_path": "C:/repo/ISSUE.md"},
            {"content": "# Issue\nPreserve the public contract."},
        )

        self.assertEqual(captured[0], "ISSUE.md")
        self.assertIn("Preserve the old positional API", captured[1])
        self.assertIsNone(ignored)
        self.assertIsNone(poisoned_listing)
        self.assertIsNone(mixed_read_and_listing)
        self.assertIsNone(similarly_named_file)
        self.assertEqual(direct_read[0], "ISSUE.md")
        self.assertIn("Preserve the public contract", direct_read[1])

    def test_stop_packet_separates_claim_from_objective_evidence(self):
        packet = self.source.build_stop_packet(
            task_anchor="只修目前的 bug",
            last_assistant_message="已完成並通過測試",
            task_sources="ISSUE.md\n舊呼叫方式必須維持",
            evidence_records=[
                {"seq": 1, "category": "change", "content": "新增 violation_error_code"},
                {"seq": 2, "category": "verification", "content": "128 tests passed"},
                {"seq": 3, "category": "failure", "content": "舊位置參數尚未驗證"},
            ],
        )

        self.assertIn("[contract]", packet)
        self.assertIn("[current result]", packet)
        self.assertIn("assistant_output:", packet)
        self.assertNotIn("runtime_output:", packet)
        self.assertNotIn("completion_claim_context:", packet)
        self.assertLess(
            packet.index("[contract]"),
            packet.index("[current result]"),
        )

# ── 4. Checkpoint nudge hooks ────────────────────────────────────────

class TestCheckpointDelivery(unittest.TestCase):

    def setUp(self):
        import claude_checkpoint as checkpoint
        from masters_nudge.runtime import RuntimePaths, RuntimeSettings

        self.checkpoint = checkpoint
        self.tmpdir = tempfile.TemporaryDirectory()
        root = Path(self.tmpdir.name)
        self.settings = RuntimeSettings(
            "anthropic",
            "test-model",
            60,
            15,
            RuntimePaths(HERE, root, root / "error.log"),
        )
        self.runtime_patch = mock.patch.object(
            checkpoint.claude_adapter, "RUNTIME", self.settings
        )
        self.runtime_patch.start()

    def tearDown(self):
        self.runtime_patch.stop()
        self.tmpdir.cleanup()

    def test_same_review_identity_is_claimed_once(self):
        from masters_nudge import storage
        from masters_nudge.contracts import SessionRef

        session = SessionRef("claude_code", "session-1")
        claimed = storage.claim_review_attempt(
            self.settings.paths.data_dir, session, "checkpoint", "same-fingerprint"
        )
        claimed_again = storage.claim_review_attempt(
            self.settings.paths.data_dir, session, "checkpoint", "same-fingerprint"
        )

        self.assertTrue(claimed)
        self.assertFalse(claimed_again)

    def test_terminal_reviewer_failure_does_not_retry_automatically(self):
        from masters_nudge import storage
        from masters_nudge.contracts import SessionRef

        session = SessionRef("claude_code", "session-1")
        token = storage.claim_review_attempt(
            self.settings.paths.data_dir, session, "checkpoint", "retry-me"
        )
        storage.finish_review_attempt(
            self.settings.paths.data_dir,
            session,
            "checkpoint",
            "retry-me",
            token,
            "error",
        )
        retry = storage.claim_review_attempt(
            self.settings.paths.data_dir, session, "checkpoint", "retry-me"
        )

        self.assertTrue(token)
        self.assertFalse(retry)

    def test_output_is_labeled_nudge_additional_context(self):
        result = self.checkpoint.build_hook_output(
            "PostToolUseFailure", "先確認失敗根因。"
        )

        self.assertEqual(
            result["hookSpecificOutput"]["hookEventName"],
            "PostToolUseFailure",
        )
        self.assertEqual(
            result["hookSpecificOutput"]["additionalContext"],
            "獨立第二意見：\n先確認失敗根因。",
        )
        serialized = json.dumps(result, ensure_ascii=False)
        self.assertNotIn('"decision"', serialized)
        self.assertNotIn('"continue"', serialized)
        self.assertNotIn('"systemMessage"', serialized)

    def test_reviewer_failure_returns_no_output_and_closes_attempt(self):
        hook = {
            "session_id": "session-1",
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest tests/test_path.py"},
            "error": "1 failed",
        }
        from masters_nudge.contracts import ReviewOutcome

        with mock.patch.object(
            self.checkpoint.ReviewCore,
            "_review_claimed",
            return_value=ReviewOutcome(status="error"),
        ):
            self.assertIsNone(self.checkpoint.prepare_hook(hook))
            result = self.checkpoint.prepare_hook({**hook, "error": "2 failed"})

        self.assertIsNone(result)
        from masters_nudge import storage
        from masters_nudge.contracts import SessionRef

        session = SessionRef("claude_code", "session-1")
        attempt_dir = (
            self.settings.paths.data_dir
            / f"{storage.session_stem(session)}.review-attempts"
        )
        attempts = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in attempt_dir.glob("*.json")
        ]
        self.assertEqual(1, len(attempts))
        self.assertEqual(attempts[0]["status"], "error")

    def test_successful_nudge_is_deduplicated(self):
        hook = {
            "session_id": "session-1",
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest tests/test_path.py"},
            "error": "1 failed",
        }
        from masters_nudge.contracts import ReviewOutcome

        with mock.patch.object(
            self.checkpoint.ReviewCore,
            "_review_claimed",
            return_value=ReviewOutcome(
                status="finding",
                finding="路徑假設還沒成立。",
                reaction_ts="reaction-1",
            ),
        ) as review:
            self.assertIsNone(self.checkpoint.prepare_hook(hook))
            first = self.checkpoint.prepare_hook({**hook, "error": "2 failed"})
            second = self.checkpoint.prepare_hook({**hook, "error": "2 failed"})

        self.assertIsNotNone(first)
        self.assertIsNone(second)
        review.assert_called_once()

    def test_claude_does_not_review_unverified_changes_alone(self):
        from masters_nudge import storage
        from masters_nudge.contracts import ReviewOutcome, SessionRef

        session = SessionRef("claude_code", "strategy", cwd=self.tmpdir.name)
        storage.start_turn(
            self.settings.paths.data_dir,
            session,
            "完成兩次變更後取得驗證回饋",
        )
        hook = {
            "session_id": "strategy",
            "cwd": self.tmpdir.name,
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "tool_input": {"file_path": "app.py"},
            "tool_response": {"success": True},
        }

        with mock.patch.object(
            self.checkpoint,
            "review_checkpoint",
            return_value=ReviewOutcome("no_finding"),
        ) as review:
            self.checkpoint.prepare_hook(hook)
            self.checkpoint.prepare_hook(
                {**hook, "tool_input": {"file_path": "second.py"}}
            )

        review.assert_not_called()
        progress = storage.load_progress_state(
            self.settings.paths.data_dir, session
        )
        self.assertEqual(2, progress["event_seq"])

    def test_generate_nudge_uses_task_anchor_and_event_packet_not_full_transcript(self):
        from masters_nudge import prompting, providers, storage

        hook = {
            "session_id": "session-1",
            "transcript_path": "/session.jsonl",
            "hook_event_name": "PostToolUseFailure",
        }
        event = {
            "reason": "error",
            "context": "reason: error",
            "fingerprint": "error-1",
        }
        with (
            mock.patch.object(
                storage,
                "load_turn_state",
                return_value={
                    "task_anchor": "只修路徑問題",
                    "transcript_offset": 42,
                    "evidence_records": [
                        {
                            "seq": 1,
                            "category": "failure",
                            "scope": "path-check",
                            "content": "failure:\nmissing file",
                        }
                    ],
                },
            ),
            mock.patch.object(
                self.checkpoint.claude_adapter,
                "read_latest_assistant_text",
                side_effect=AssertionError("assistant feedback must stay out of provider input"),
            ) as assistant_reader,
            mock.patch.object(
                prompting,
                "build_system_prompt",
                return_value="system",
            ),
            mock.patch.object(
                providers,
                "dispatch_call_result",
                return_value={
                    "status": "finding",
                    "finding": "路徑前提還沒成立。",
                    "usage": {"input_tokens": 100},
                },
            ) as dispatch,
            mock.patch("masters_nudge.core.review_telemetry.record_review") as telemetry,
        ):
            result = self.checkpoint.review_checkpoint(
                event,
                session=self.checkpoint.claude_adapter.session_from_hook(hook),
            )

        self.assertEqual(result.finding, "路徑前提還沒成立。")
        payload = dispatch.call_args.args[2]
        self.assertIn("只修路徑問題", payload)
        self.assertIn("missing file", payload)
        self.assertNotIn("正在檢查路徑", payload)
        self.assertNotIn("[transcript", payload)
        assistant_reader.assert_not_called()
        telemetry.assert_called_once()
        telemetry_record = telemetry.call_args.args[1]
        self.assertEqual(telemetry_record["kind"], "checkpoint")
        self.assertEqual(telemetry_record["reason"], "error")
        self.assertEqual(telemetry_record["effective_lens"], "beck")


# ── 5. Transcript parser ─────────────────────────────────────────────

FIXTURE_LINES = [
    {"type": "user", "message": {"role": "user", "content": "幫我修 bug"}},
    {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "text", "text": "我來看看程式碼"},
        {"type": "tool_use", "name": "Read"},
    ]}},
    {"type": "system", "message": {"role": "system", "content": "ignored"}},
    {"type": "assistant", "message": {"role": "assistant", "content": "修好了"}},
]


class TestTranscriptParser(unittest.TestCase):

    def setUp(self):
        from masters_nudge import claude_adapter as buddy
        self.buddy = buddy

    # ── parse_transcript_entry ────────────────────────────────────────

    def test_parse_user_string_content(self):
        result = self.buddy.parse_transcript_entry(FIXTURE_LINES[0])
        self.assertEqual(result, ("user", "幫我修 bug"))

    def test_parse_assistant_drops_tool_use(self):
        # tool_use blocks are now silently dropped (not turned into [tool_use: X])
        result = self.buddy.parse_transcript_entry(FIXTURE_LINES[1])
        self.assertEqual(result, ("claude", "我來看看程式碼"))

    def test_parse_assistant_string_content(self):
        result = self.buddy.parse_transcript_entry(FIXTURE_LINES[3])
        self.assertEqual(result, ("claude", "修好了"))

    def test_parse_system_returns_none(self):
        result = self.buddy.parse_transcript_entry(FIXTURE_LINES[2])
        self.assertIsNone(result)

    def test_stop_source_packet_uses_task_claim_and_current_turn_evidence(self):
        from masters_nudge import storage

        hook = {
            "session_id": "session-1",
            "transcript_path": "/session.jsonl",
            "last_assistant_message": "已完成並通過測試",
        }
        with (
            mock.patch.object(
                storage,
                "load_turn_state",
                return_value={
                    "task_anchor": "只修登入錯誤",
                    "transcript_offset": 123,
                    "task_sources": {"ISSUE.md": "逾時時必須保留 session"},
                    "evidence_records": [
                        {"seq": 1, "category": "change", "content": "auth.py changed"},
                        {"seq": 2, "category": "verification", "content": "8 passed"},
                        {
                            "seq": 3,
                            "category": "failure",
                            "content": "Exit code 1\n1 failed",
                        },
                    ],
                },
            ),
            mock.patch.object(
                self.buddy,
                "_read_transcript_entries",
                side_effect=AssertionError("tool transcript must stay out of packet"),
            ) as transcript_reader,
        ):
            source = self.buddy.build_stop_source_context(
                hook,
                session=self.buddy.session_from_hook(hook),
            )
            result = source

        transcript_reader.assert_not_called()
        self.assertIn("只修登入錯誤", result)
        self.assertIn("逾時時必須保留 session", result)
        self.assertIn("已完成並通過測試", result)
        self.assertIn("8 passed", result)
        self.assertIn("1 failed", result)
        self.assertNotIn("runtime_output:", result)

class TestPersonaConfig(unittest.TestCase):

    def setUp(self):
        import persona_config

        self.config = persona_config
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_stage_environment_override_reports_its_source(self):
        selection = self.config.resolve_stage(
            self.tmpdir, environ={"MASTERS_NUDGE_STAGE": "review"}
        )

        self.assertEqual(
            (selection.stage, selection.persona, selection.source),
            ("review", "linus", "environment"),
        )

    def test_invalid_stage_environment_falls_back_to_automatic(self):
        selection = self.config.resolve_stage(
            self.tmpdir, environ={"MASTERS_NUDGE_STAGE": "general"}
        )

        self.assertEqual(
            (selection.stage, selection.persona, selection.source),
            ("automatic", "", "invalid_environment"),
        )

    def test_missing_or_invalid_config_falls_back_to_automatic(self):
        missing = self.config.resolve_stage(self.tmpdir, environ={})
        (self.tmpdir / "config.json").write_text(
            json.dumps({"stage": "unknown"}), encoding="utf-8"
        )
        invalid = self.config.resolve_stage(self.tmpdir, environ={})

        self.assertEqual(
            (missing.stage, missing.persona, missing.source),
            ("automatic", "", "default"),
        )
        self.assertEqual(
            (invalid.stage, invalid.persona, invalid.source),
            ("automatic", "", "default"),
        )

    def test_save_and_load_new_stage_format(self):
        self.config.save_stage(self.tmpdir, "review")

        selection = self.config.resolve_stage(self.tmpdir, environ={})
        saved = json.loads(
            (self.tmpdir / "config.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            (selection.stage, selection.persona, selection.source),
            ("review", "linus", "config"),
        )
        self.assertEqual(saved, {"stage": "review"})

    def test_removed_general_stage_config_falls_back_to_automatic(self):
        (self.tmpdir / "config.json").write_text(
            json.dumps({"stage": "general"}), encoding="utf-8"
        )

        selection = self.config.resolve_stage(self.tmpdir, environ={})

        self.assertEqual(
            (selection.stage, selection.persona, selection.source),
            ("automatic", "", "default"),
        )

    def test_automatic_is_a_persisted_non_persona_selection(self):
        self.config.save_stage(self.tmpdir, "automatic")

        selection = self.config.resolve_stage(self.tmpdir, environ={})

        self.assertEqual(
            (selection.stage, selection.persona, selection.source),
            ("automatic", "", "config"),
        )

    def test_general_is_not_a_savable_stage(self):
        with self.assertRaises(ValueError):
            self.config.save_stage(self.tmpdir, "general")

    def test_invalid_stage_is_not_saved(self):
        with self.assertRaises(ValueError):
            self.config.save_stage(self.tmpdir, "unknown")
        self.assertFalse((self.tmpdir / "config.json").exists())


class TestLensRouter(unittest.TestCase):

    def setUp(self):
        import lens_router

        self.router = lens_router
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_route_contract_has_no_unused_session_key(self):
        self.assertNotIn(
            "session_key",
            inspect.signature(self.router.resolve_review_route).parameters,
        )

    def route(self, focus="", environ=None, *, stopping=False):
        return self.router.resolve_review_route(
            self.tmpdir,
            environ={} if environ is None else environ,
            reported_focus=focus,
            stopping=stopping,
        )

    def test_explicit_lifecycle_stages_override_reported_focus(self):
        import persona_config

        expected = {
            "design": "jeff",
            "build": "beck",
            "evolve": "fowler",
            "review": "linus",
        }
        for stage, lens in expected.items():
            with self.subTest(stage=stage):
                persona_config.save_stage(self.tmpdir, stage)
                route = self.route("performance")
                self.assertEqual(route.stage, stage)
                self.assertEqual(route.effective_lens, lens)
                self.assertEqual(route.source, "config")

    def test_reported_focus_selects_one_private_lens(self):
        expected = {
            "design": "jeff",
            "build": "beck",
            "evolve": "fowler",
            "review": "linus",
            "reliability": "lamport",
            "performance": "carmack",
        }
        for focus, lens in expected.items():
            with self.subTest(focus=focus):
                route = self.route(focus)
                self.assertEqual(route.stage, focus)
                self.assertEqual(route.effective_lens, lens)
                self.assertEqual(route.source, "main_model_report")

    def test_environment_override_wins_over_reported_focus(self):
        route = self.route(
            "performance", {"MASTERS_NUDGE_STAGE": "review"}
        )

        self.assertEqual(
            (route.stage, route.effective_lens, route.source),
            ("review", "linus", "environment"),
        )

    def test_missing_report_keeps_forced_review_with_phase_fallback(self):
        midturn = self.route()
        stopping = self.route(stopping=True)

        self.assertEqual(
            (midturn.stage, midturn.effective_lens, midturn.source),
            ("build", "beck", "default_fallback"),
        )
        self.assertEqual(
            (stopping.stage, stopping.effective_lens, stopping.source),
            ("review", "linus", "stop_fallback"),
        )


class TestFloatingWindowLayout(unittest.TestCase):

    def test_explicit_window_workspace_overrides_plugin_working_directory(self):
        import buddy_window

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            plugin = root / "plugin"
            workspace = root / "workspace"
            plugin.mkdir()
            workspace.mkdir()

            resolved = buddy_window.resolve_window_workspace(
                environ={"MASTERS_NUDGE_WORKSPACE": str(workspace)},
                cwd=plugin,
            )

        self.assertEqual(resolved, buddy_window.normalize_workspace(workspace))

    def test_window_skill_forwards_the_active_workspace(self):
        skill = (
            HERE / "plugins" / "masters-nudge" / "skills" / "window" / "SKILL.md"
        ).read_text(encoding="utf-8")

        normalized = " ".join(skill.split())
        self.assertIn("--workspace", normalized)
        self.assertIn("Do not change the working directory", normalized)

    def test_reaction_log_workspace_uses_newest_scoped_entry(self):
        import buddy_window

        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "session.log"
            path.write_text(
                json.dumps({"reaction": "old"}) + "\n"
                + json.dumps({"workspace": raw, "reaction": "new"}) + "\n",
                encoding="utf-8",
            )

            self.assertEqual(
                buddy_window.reaction_log_workspace(path),
                buddy_window.normalize_workspace(raw),
            )

    def test_window_ignores_logs_from_other_workspaces(self):
        import buddy_window

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            own = root / "own"
            other = root / "other"
            own.mkdir()
            other.mkdir()
            own_log = root / "own.log"
            other_log = root / "other.log"
            own_log.write_text(
                json.dumps({"workspace": str(own), "reaction": "own"}) + "\n",
                encoding="utf-8",
            )
            other_log.write_text(
                json.dumps({"workspace": str(other), "reaction": "other"}) + "\n",
                encoding="utf-8",
            )
            os.utime(other_log, (other_log.stat().st_atime, own_log.stat().st_mtime + 5))
            window = object.__new__(buddy_window.BuddyWindow)
            window.workspace = buddy_window.normalize_workspace(own)

            with mock.patch.object(buddy_window, "DATA_DIR", root):
                active = buddy_window.BuddyWindow._find_active_log(window)

            self.assertEqual(active, own_log)

    def test_switching_to_new_session_log_reads_its_first_reaction(self):
        import buddy_window

        window = object.__new__(buddy_window.BuddyWindow)
        window.current_log = Path("old.log")
        window.last_offset = 999
        window._find_active_log = mock.Mock(return_value=Path("new.log"))
        window._read_new = mock.Mock()
        window.root = mock.Mock()

        buddy_window.BuddyWindow._poll(window)

        self.assertEqual(window.current_log, Path("new.log"))
        self.assertEqual(window.last_offset, 0)
        window._read_new.assert_called_once_with()

    def test_window_shows_queued_emitted_then_injected_delivery_state(self):
        import buddy_window

        with tempfile.TemporaryDirectory() as raw:
            log = Path(raw) / "codex_cli--s.log"
            log.write_text(
                json.dumps(
                    {
                        "ts": "2026-08-16T10:00:00.123456",
                        "kind": "review",
                        "reaction": "先確認失敗測試是否覆蓋原始需求。",
                        "persona": "beck",
                        "delivery_status": "queued",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            window = object.__new__(buddy_window.BuddyWindow)
            window.current_log = log
            window.last_offset = 0
            window.last_reaction = ""
            window.last_reaction_ts = ""
            window.frame_idx = 0
            window.review_frames = []
            window.bubble_label = mock.Mock()
            window.ts_label = mock.Mock()
            window._set_lens_badge = mock.Mock()
            window._resize_for_reaction = mock.Mock()

            buddy_window.BuddyWindow._read_new(window)
            self.assertEqual(window.last_reaction_ts, "2026-08-16T10:00:00.123456")
            window.ts_label.config.assert_called_with(text="10:00:00 · 待送出")

            with log.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "ts": "2026-08-16T10:00:03.123456",
                            "kind": "delivery_receipt",
                            "reaction_ts": "2026-08-16T10:00:00.123456",
                            "delivery_status": "emitted",
                            "delivered_at": "2026-08-16T10:00:03.123456",
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

            buddy_window.BuddyWindow._read_new(window)
            window.ts_label.config.assert_called_with(
                text="10:00:03 · 已送出，待確認"
            )

            with log.open("a", encoding="utf-8") as handle:
                handle.write(
                    json.dumps(
                        {
                            "ts": "2026-08-16T10:00:05.123456",
                            "kind": "delivery_receipt",
                            "reaction_ts": "2026-08-16T10:00:00.123456",
                            "delivery_status": "injected",
                            "delivered_at": "2026-08-16T10:00:05.123456",
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

            buddy_window.BuddyWindow._read_new(window)

        window.ts_label.config.assert_called_with(text="10:00:05 · 已注入")

    def test_window_shows_timeout_message_without_pending_suffix(self):
        import buddy_window

        with tempfile.TemporaryDirectory() as raw:
            log = Path(raw) / "codex_cli--s.log"
            timeout_message = "Reviewer 逾時（90 秒）；本輪沒有 Nudge。"
            log.write_text(
                json.dumps(
                    {
                        "ts": "2026-08-16T10:01:00.123456",
                        "kind": "review_status",
                        "reaction": timeout_message,
                        "persona": "fowler",
                        "delivery_status": "queued",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            window = object.__new__(buddy_window.BuddyWindow)
            window.current_log = log
            window.last_offset = 0
            window.last_reaction = ""
            window.last_reaction_ts = ""
            window.frame_idx = 0
            window.review_frames = []
            window.bubble_label = mock.Mock()
            window.ts_label = mock.Mock()
            window._set_lens_badge = mock.Mock()
            window._resize_for_reaction = mock.Mock()

            buddy_window.BuddyWindow._read_new(window)

        window.bubble_label.config.assert_called_with(text=timeout_message)
        window.ts_label.config.assert_called_with(text="10:01:00")

    def test_selector_offers_automatic_then_four_manual_stages(self):
        import buddy_window

        options = buddy_window.selector_options()
        self.assertEqual(
            options,
            [
                "Automatic · coding agent 回報目前工作焦點",
                "Design · 系統結構、因果與成本",
                "Build · 小步驟、測試與回饋",
                "Evolve · 重構與變更成本",
                "Review · 簡化與責任歸屬",
            ],
        )
        for label, stage in zip(
            options,
            ("automatic", "design", "build", "evolve", "review"),
        ):
            self.assertEqual(buddy_window.SELECTOR_STAGES[label], stage)

    def test_window_contains_persistent_lens_selector(self):
        source = (HERE / "buddy_window.py").read_text(encoding="utf-8")

        self.assertIn("ttk.Combobox", source)
        self.assertIn("<<ComboboxSelected>>", source)
        self.assertIn("persona_config.save_stage", source)
        self.assertIn("下一次 review 起", source)
        self.assertIn("Hook 仍決定何時強制呼叫 Provider", source)
        self.assertIn("MASTERS_NUDGE_STAGE 正在接管", source)
        self.assertIn("self._set_lens_background(persona)", source)
        self.assertIn(
            "self.review_frames_remaining = len(self.review_frames)", source
        )

    def test_six_lenses_have_distinct_functional_badges_with_unknown_fallback(self):
        import buddy_window

        expected_names = {
            "jeff": "Design · 系統結構、因果與成本",
            "linus": "Review · 簡化與責任歸屬",
            "fowler": "Evolve · 重構與變更成本",
            "beck": "Build · 小步驟、測試與回饋",
            "lamport": "Reliability · 狀態、順序與失敗",
            "carmack": "Performance · 執行路徑與效能",
        }
        colors = set()
        for persona, expected_name in expected_names.items():
            with self.subTest(persona=persona):
                label, color = buddy_window.lens_badge(persona)
                self.assertEqual(label, f"● {expected_name}")
                self.assertRegex(color, r"^#[0-9A-Fa-f]{6}$")
                colors.add(color.lower())

        self.assertEqual(len(colors), len(expected_names))
        self.assertEqual(buddy_window.lens_badge("unknown")[0], "● 未記錄")
        self.assertEqual(buddy_window.lens_badge(None)[0], "● 未記錄")

    def test_window_grows_for_a_52_character_reaction(self):
        import buddy_window

        short_height = buddy_window.window_height_for_reaction("短提醒。")
        long_height = buddy_window.window_height_for_reaction("字" * 52)

        self.assertEqual(short_height, buddy_window.WINDOW_MIN_HEIGHT)
        self.assertGreater(long_height, short_height)
        self.assertLessEqual(long_height, buddy_window.WINDOW_MAX_HEIGHT)
        self.assertGreaterEqual(buddy_window.WINDOW_NON_TEXT_HEIGHT, 104)

    def test_window_wrap_width_and_resize_hook_cover_long_reactions(self):
        import buddy_window

        source = (HERE / "buddy_window.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(buddy_window.BUBBLE_WRAP_LENGTH, 300)
        self.assertIn('entry.get("effective_lens") or entry.get("persona", "")', source)
        self.assertIn("self._set_lens_badge(persona)", source)
        self.assertIn("self._resize_for_reaction(reaction)", source)


# ── 8. Inject.py state pointer ───────────────────────────────────────

class TestInjectState(unittest.TestCase):

    def setUp(self):
        import claude_prompt as inject
        from masters_nudge.runtime import RuntimePaths, RuntimeSettings

        self.inject = inject
        self.tmpdir = tempfile.mkdtemp()
        root = Path(self.tmpdir)
        self.runtime_patch = mock.patch.object(
            inject.claude_adapter,
            "RUNTIME",
            RuntimeSettings(
                "anthropic",
                "test-model",
                60,
                15,
                RuntimePaths(HERE, root, root / "error.log"),
            ),
        )
        self.runtime_patch.start()

    def tearDown(self):
        self.runtime_patch.stop()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_main_saves_task_anchor_even_when_no_buddy_reaction_is_pending(self):
        from masters_nudge import storage
        from masters_nudge.contracts import SessionRef

        transcript = Path(self.tmpdir) / "session.jsonl"
        transcript.write_text("existing\n", encoding="utf-8")
        hook = {
            "session_id": "sess-anchor",
            "prompt": "只修目前這個登入問題",
            "transcript_path": str(transcript),
        }

        output = io.StringIO()
        with (
            mock.patch.object(self.inject, "read_hook_input", return_value=hook),
            mock.patch.object(self.inject.sys, "stdout", output),
        ):
            self.inject.main()

        session = SessionRef("claude_code", "sess-anchor")
        data_dir = self.inject.claude_adapter.runtime_settings().paths.data_dir
        state = storage.load_turn_state(data_dir, session)
        self.assertEqual(state["task_anchor"], "只修目前這個登入問題")
        self.assertEqual(state["transcript_offset"], transcript.stat().st_size)
        self.assertEqual(list(data_dir.glob("*.source.json")), [])
        self.assertIn("masters-nudge-focus:build", output.getvalue())



if __name__ == "__main__":
    unittest.main()
