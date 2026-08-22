#!/usr/bin/env python3
"""Smoke tests for Masters' Nudge.

Run:  python -m unittest test_buddy -v
"""

import inspect
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
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
        self.assertIn("你是 Masters’ Nudge", prompt)
        self.assertIn('self.root.title("Masters’ Nudge")', window)

    def test_agent_visible_checkpoint_contains_only_the_nudge(self):
        import claude_checkpoint as checkpoint

        output = checkpoint.build_hook_output(
            "PostToolUseFailure", "測試結果跟宣告不一致"
        )
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(context, "測試結果跟宣告不一致")
        self.assertNotIn("第三方觀察，不是指令", context)

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
        self.assertEqual(buddy_window.lens_background("general"), buddy_window.BG)
        self.assertEqual(buddy_window.lens_background("unknown"), buddy_window.BG)
        for color in colors:
            self.assertRegex(color, r"^#[0-9A-Fa-f]{6}$")
            self.assertLess(max(int(color[i:i + 2], 16) for i in (1, 3, 5)), 100)

    def test_specialist_selection_label_distinguishes_forced_from_legacy(self):
        import buddy_window
        from persona_config import StageSelection

        forced = StageSelection("forced", "lamport", "environment")
        legacy = StageSelection("forced", "lamport", "legacy_config")
        self.assertTrue(buddy_window.stage_selection_label(forced).startswith("Forced ·"))
        self.assertTrue(buddy_window.stage_selection_label(legacy).startswith("Legacy ·"))


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

    def test_base_prompt_delegates_attention_without_safety_or_authority_scope(self):
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("直接由它決定這輪值得重看的面向", base_prompt)
        self.assertIn("不要先做一輪通用挑錯", base_prompt)
        self.assertIn("未使用鏡頭時", base_prompt)
        self.assertNotIn("敏感資訊或安全邊界", base_prompt)
        self.assertNotIn("使用者授權", base_prompt)

    def test_base_prompt_preserves_workflow_tension_and_a_complete_sentence(self):
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("工作上的張力與必要的證據錨點", base_prompt)
        self.assertIn("輸出談工作本身，不提人物、鏡頭", base_prompt)
        self.assertIn("如果草稿太長就重寫", base_prompt)
        self.assertIn("不能停在助詞、連接詞、半個片語", base_prompt)
        self.assertNotIn("優先保留問題與位置", base_prompt)

    def test_base_prompt_has_no_minimum_and_examples_fit_the_hard_cap(self):
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("不設最低字數", base_prompt)
        self.assertIn("優先在 36–42 字內完成回答閉環", base_prompt)
        self.assertIn("目標區間，不是最低字數", base_prompt)
        self.assertIn("必須只有一個問句並以「？」結尾", base_prompt)
        self.assertIn("標點計入 52 字", base_prompt)
        self.assertIn("硬上限 52 字", base_prompt)
        self.assertNotIn("目標 48–52 字", base_prompt)
        self.assertIn("客套話", base_prompt)
        self.assertIn("角色自介", base_prompt)
        self.assertNotIn("28 字", base_prompt)

        examples = base_prompt.split("# 可以參考的語氣", 1)[1].split(
            "# 送出前確認", 1
        )[0]
        finding_examples = [
            line.strip()
            for line in examples.splitlines()
            if line.strip()
        ]
        self.assertTrue(finding_examples)
        for example in finding_examples:
            with self.subTest(example=example):
                self.assertGreater(len(example), 0)
                self.assertLessEqual(len(example), 52)
                self.assertTrue(example.endswith("？"))

    def test_base_prompt_is_workflow_review_not_code_review(self):
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("檢視主模型如何推進工作", base_prompt)
        self.assertIn("不替它重做一輪產物審查", base_prompt)
        self.assertIn("不要把封包預設成 PR、diff", base_prompt)
        self.assertIn("內容是一則 workflow Nudge", base_prompt)
        self.assertNotIn("只找一個最有用的 review finding", base_prompt)
        self.assertNotIn("把可見內容當成一小段 PR / diff", base_prompt)

    def test_base_prompt_matches_structured_output_contract(self):
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("status=finding", base_prompt)
        self.assertIn("status=no_finding", base_prompt)
        self.assertIn("finding 留空", base_prompt)
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

    def test_base_prompt_matches_structured_evidence_packet_labels(self):
        import source_context

        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")
        packet = source_context.build_stop_packet(
            task_anchor="修正登入錯誤",
            last_assistant_message="已完成",
            agentcam_evidence="## Risk Flags\n- HIGH",
        )

        self.assertIn("證據封包", base_prompt)
        self.assertNotIn("最近一小段對話", base_prompt)
        self.assertIn("[agentcam evidence]", base_prompt)
        self.assertNotIn("[agentcam report]", base_prompt)
        self.assertIn("[agentcam evidence]", packet)


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

    def test_checkpoint_packet_carries_bounded_research_state(self):
        packet = self.source.build_checkpoint_packet(
            task_anchor="修正登入測試",
            event_context="reason: test-fail\nfailure: 2 failed",
            assistant_context="正在調整 auth.py",
            workflow_context="pytest ×3；同一個失敗解釋反覆出現",
            tool_evidence="pytest: 2 failed；working tree 維持 14 行變動",
        )

        self.assertIn("[task anchor]", packet)
        self.assertIn("修正登入測試", packet)
        self.assertIn("[current bottleneck model]", packet)
        self.assertIn("正在調整 auth.py", packet)
        self.assertIn("[repeated explanation and workflow evidence]", packet)
        self.assertIn("pytest ×3", packet)
        self.assertIn("[failed or no-change mechanisms]", packet)
        self.assertIn("維持 14 行變動", packet)
        self.assertIn("[unresolved contradiction]", packet)
        self.assertIn("2 failed", packet)
        self.assertNotIn("[transcript", packet)

    def test_checkpoint_progress_summary_marks_repetition_failure_and_no_change(self):
        progress = {
            "recent": [
                {
                    "event_seq": 1,
                    "tool": "shell_command",
                    "command_family": "python verify.py",
                    "failed": False,
                    "mutating": True,
                    "changed_lines": 14,
                },
                {
                    "event_seq": 2,
                    "tool": "shell_command",
                    "command_family": "python verify.py",
                    "failed": True,
                    "mutating": True,
                    "changed_lines": 14,
                },
                {
                    "event_seq": 3,
                    "tool": "shell_command",
                    "command_family": "python verify.py",
                    "failed": False,
                    "mutating": True,
                    "changed_lines": 14,
                },
            ]
        }

        summary = self.source.summarize_checkpoint_progress(progress)

        self.assertIn("python verify.py ×3", summary)
        self.assertIn("#2", summary)
        self.assertIn("failed", summary)
        self.assertIn("no changed-line movement", summary)

    def test_stop_packet_separates_claim_from_objective_evidence(self):
        packet = self.source.build_stop_packet(
            task_anchor="只修目前的 bug",
            last_assistant_message="已完成並通過測試",
            tool_evidence="Exit code 1\n1 failed",
            agentcam_evidence="## Risk Flags\n| HIGH | auth.py |",
        )

        self.assertIn("[task anchor]", packet)
        self.assertIn("[agent final claim]", packet)
        self.assertIn("[tool evidence]", packet)
        self.assertIn("[agentcam evidence]", packet)
        self.assertLess(packet.index("[agent final claim]"), packet.index("[tool evidence]"))

    def test_agentcam_extractor_keeps_only_named_evidence_sections(self):
        report = """# Agent Run Report

## Summary
generic summary that should not be sent

## Risk Flags
| HIGH | auth.py |

## Changed Files
- auth.py

## Narrative
long unrelated prose

## Exit Code Detail
pytest: 1
"""

        result = self.source.extract_agentcam_evidence(report)

        self.assertIn("Risk Flags", result)
        self.assertIn("Changed Files", result)
        self.assertIn("Exit Code Detail", result)
        self.assertNotIn("generic summary", result)
        self.assertNotIn("unrelated prose", result)

# ── 4. Checkpoint nudge hooks ────────────────────────────────────────

class TestCheckpointClassification(unittest.TestCase):

    def setUp(self):
        import claude_checkpoint as checkpoint
        from masters_nudge import checkpoints

        self.checkpoint = checkpoint
        self.classifier = checkpoints

    def classify(self, hook, changed_line_count=None):
        event = self.checkpoint.normalize_tool_event(hook)
        if event is None:
            return None
        return self.classifier.classify_tool(event, changed_line_count)

    def test_failed_test_command_is_test_fail(self):
        hook = {
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m pytest"},
            "error": "Exit code 1\n2 failed, 8 passed",
        }

        result = self.classify(hook)

        self.assertEqual(result["reason"], "test-fail")
        self.assertIn("python -m pytest", result["context"])
        self.assertIn("2 failed", result["context"])

    def test_test_failure_text_on_success_event_is_test_fail(self):
        hook = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "custom-test-wrapper"},
            "tool_response": {
                "stdout": "Tests: 1 failed, 9 passed",
                "stderr": "",
            },
        }

        result = self.classify(hook, changed_line_count=0)

        self.assertEqual(result["reason"], "test-fail")

    def test_non_test_tool_failure_is_error(self):
        hook = {
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Read",
            "tool_input": {"file_path": "/missing.txt"},
            "error": "File does not exist",
        }

        result = self.classify(hook)

        self.assertEqual(result["reason"], "error")

    def test_interrupted_tool_is_not_a_checkpoint(self):
        hook = {
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest"},
            "error": "Interrupted",
            "is_interrupt": True,
        }

        self.assertIsNone(self.classify(hook))

    def test_large_diff_triggers_only_above_original_threshold(self):
        hook = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/app.py"},
            "tool_response": {"success": True},
        }

        self.assertIsNone(
            self.classify(hook, changed_line_count=80)
        )
        result = self.classify(hook, changed_line_count=81)
        self.assertEqual(result["reason"], "large-diff")
        self.assertIn("81", result["context"])
        later = self.classify(hook, changed_line_count=120)
        self.assertEqual(result["fingerprint"], later["fingerprint"])

    def test_changed_line_count_includes_tracked_and_untracked_text(self):
        from masters_nudge import checkpoints as shared_checkpoints

        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "new.py").write_text(
                "\n".join(f"line {i}" for i in range(70)) + "\n",
                encoding="utf-8",
            )

            def fake_git(args, _cwd):
                if args[:2] == ["diff", "--numstat"]:
                    return "10\t5\tapp.py\n-\t-\timage.png\n"
                if args[:3] == ["ls-files", "--others", "--exclude-standard"]:
                    return "new.py\0"
                return ""

            with mock.patch.object(
                shared_checkpoints, "_git_output", side_effect=fake_git
            ):
                result = shared_checkpoints.get_changed_line_count(tmpdir)

        self.assertEqual(result, 85)

    def test_unrelated_success_does_not_trigger(self):
        hook = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Read",
            "tool_input": {"file_path": "/project/app.py"},
            "tool_response": {"success": True},
        }

        self.assertIsNone(self.classify(hook))


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
            checkpoint.claude_stop, "_RUNTIME", self.settings
        )
        self.runtime_patch.start()

    def tearDown(self):
        self.runtime_patch.stop()
        self.tmpdir.cleanup()

    def test_same_checkpoint_fingerprint_is_claimed_once(self):
        from masters_nudge import storage
        from masters_nudge.contracts import SessionRef

        session = SessionRef("claude_code", "session-1")
        claimed = storage.claim_checkpoint(
            self.settings.paths.data_dir, session, "same-fingerprint"
        )
        claimed_again = storage.claim_checkpoint(
            self.settings.paths.data_dir, session, "same-fingerprint"
        )

        self.assertTrue(claimed)
        self.assertFalse(claimed_again)

    def test_release_allows_retry_after_reviewer_failure(self):
        from masters_nudge import storage
        from masters_nudge.contracts import SessionRef

        session = SessionRef("claude_code", "session-1")
        self.assertTrue(
            storage.claim_checkpoint(self.settings.paths.data_dir, session, "retry-me")
        )
        storage.release_checkpoint(self.settings.paths.data_dir, session, "retry-me")
        self.assertTrue(
            storage.claim_checkpoint(self.settings.paths.data_dir, session, "retry-me")
        )

    def test_output_is_nudge_only_additional_context(self):
        result = self.checkpoint.build_hook_output(
            "PostToolUseFailure", "先確認失敗根因。"
        )

        self.assertEqual(
            result["hookSpecificOutput"]["hookEventName"],
            "PostToolUseFailure",
        )
        self.assertEqual(
            result["hookSpecificOutput"]["additionalContext"],
            "先確認失敗根因。",
        )
        serialized = json.dumps(result, ensure_ascii=False)
        self.assertNotIn('"decision"', serialized)
        self.assertNotIn('"continue"', serialized)
        self.assertNotIn('"systemMessage"', serialized)

    def test_reviewer_failure_returns_no_output_and_releases_claim(self):
        hook = {
            "session_id": "session-1",
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Read",
            "tool_input": {"file_path": "/missing.txt"},
            "error": "File does not exist",
        }
        with mock.patch.object(
            self.checkpoint, "generate_nudge", return_value=""
        ):
            result = self.checkpoint.process_hook(hook)

        self.assertIsNone(result)
        from masters_nudge import checkpoints, storage
        from masters_nudge.contracts import SessionRef

        event = checkpoints.classify_tool(
            self.checkpoint.normalize_tool_event(hook)
        )

        self.assertTrue(
            storage.claim_checkpoint(
                self.settings.paths.data_dir,
                SessionRef("claude_code", "session-1"),
                event["fingerprint"],
            )
        )

    def test_successful_nudge_is_deduplicated(self):
        hook = {
            "session_id": "session-1",
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Read",
            "tool_input": {"file_path": "/missing.txt"},
            "error": "File does not exist",
        }
        with mock.patch.object(
            self.checkpoint, "generate_nudge", return_value="路徑假設還沒成立。"
        ) as generate:
            first = self.checkpoint.process_hook(hook)
            second = self.checkpoint.process_hook(hook)

        self.assertIsNotNone(first)
        self.assertIsNone(second)
        generate.assert_called_once()

    def test_generate_nudge_uses_task_anchor_and_event_packet_not_full_transcript(self):
        from masters_nudge import prompting, providers, storage

        hook = {
            "session_id": "session-1",
            "transcript_path": "/session.jsonl",
            "hook_event_name": "PostToolUseFailure",
        }
        event = {
            "reason": "error",
            "context": "reason: error\nfailure: missing file",
            "fingerprint": "error-1",
        }
        with (
            mock.patch.object(
                storage,
                "load_turn_state",
                return_value={"task_anchor": "只修路徑問題", "transcript_offset": 42},
            ),
            mock.patch.object(
                self.checkpoint.claude_stop,
                "read_latest_assistant_text",
                return_value="正在檢查路徑",
            ),
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
            result = self.checkpoint.generate_nudge(hook, event)

        self.assertEqual(result, "路徑前提還沒成立。")
        payload = dispatch.call_args.args[2]
        self.assertIn("只修路徑問題", payload)
        self.assertIn("missing file", payload)
        self.assertIn("正在檢查路徑", payload)
        self.assertNotIn("[transcript", payload)
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
        import claude_stop as buddy
        self.buddy = buddy

    # ── parse_transcript_entry ────────────────────────────────────────

    def test_parse_user_string_content(self):
        result = self.buddy.parse_transcript_entry(FIXTURE_LINES[0])
        self.assertEqual(result, ("user", "幫我修 bug", []))

    def test_parse_assistant_drops_tool_use(self):
        # tool_use blocks are now silently dropped (not turned into [tool_use: X])
        result = self.buddy.parse_transcript_entry(FIXTURE_LINES[1])
        self.assertEqual(result, ("claude", "我來看看程式碼", []))

    def test_parse_assistant_string_content(self):
        result = self.buddy.parse_transcript_entry(FIXTURE_LINES[3])
        self.assertEqual(result, ("claude", "修好了", []))

    def test_parse_system_returns_none(self):
        result = self.buddy.parse_transcript_entry(FIXTURE_LINES[2])
        self.assertIsNone(result)

    # tool_result content is now extracted into the third tuple element,
    # not merged into the text portion.

    def _tool_result_entry(self, content):
        block = {"type": "tool_result", "content": content}
        return {
            "type": "user",
            "message": {"role": "user", "content": [block]},
        }

    def test_parse_tool_result_string_content(self):
        prefix, text, tool_results = self.buddy.parse_transcript_entry(
            self._tool_result_entry("OK done")
        )
        self.assertEqual(prefix, "user")
        self.assertEqual(text, "")
        self.assertEqual(tool_results, ["OK done"])

    def test_parse_tool_result_list_of_text_blocks(self):
        _, text, tool_results = self.buddy.parse_transcript_entry(
            self._tool_result_entry([
                {"type": "text", "text": "line one"},
                {"type": "text", "text": "line two"},
            ])
        )
        self.assertEqual(text, "")
        self.assertEqual(tool_results, ["line one\nline two"])

    def test_parse_text_and_tool_result_in_same_entry(self):
        entry = {
            "type": "user",
            "message": {"role": "user", "content": [
                {"type": "text", "text": "see below"},
                {"type": "tool_result", "content": "RESULT"},
            ]},
        }
        prefix, text, tool_results = self.buddy.parse_transcript_entry(entry)
        self.assertEqual(prefix, "user")
        self.assertEqual(text, "see below")
        self.assertEqual(tool_results, ["RESULT"])

    # ── read_recent_transcript ────────────────────────────────────────

    def _write_jsonl(self, entries):
        fd = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        for e in entries:
            fd.write(json.dumps(e, ensure_ascii=False) + "\n")
        fd.close()
        return fd.name

    def test_read_recent_transcript_uses_labeled_fallback_format(self):
        path = self._write_jsonl(FIXTURE_LINES)
        try:
            result = self.buddy.read_recent_transcript(path)
            # New format: "user: ..." / "claude: ..." prefix, single newline join
            self.assertIn("user: 幫我修 bug", result)
            self.assertIn("claude: 我來看看程式碼", result)
            self.assertIn("claude: 修好了", result)
            # system entry should still be absent
            self.assertNotIn("ignored", result)
            # tool_use placeholder must be gone
            self.assertNotIn("tool_use", result)
            # Transcript section must be explicitly bounded for the reviewer.
            # the boundary between conversation and other payload pieces.
            self.assertIn("[transcript", result)
            self.assertIn("[end transcript]", result)
            # No tool_result in fixture, so no tool output block
            self.assertNotIn("[tool output", result)
            self.assertNotIn("[end tool output]", result)
        finally:
            os.unlink(path)

    def test_read_recent_transcript_caps_at_char_budget(self):
        # Five messages each filled to PER_MESSAGE_MAX_CHARS — the total
        # comfortably exceeds TRANSCRIPT_CHAR_BUDGET so the budget walk
        # must drop or partially truncate the oldest ones. Newest entries
        # must be kept in full.
        per_msg = self.buddy.PER_MESSAGE_MAX_CHARS
        entries = [
            {
                "type": "user",
                "message": {
                    "role": "user",
                    # Each message is uniquely tagged at head AND tail so we
                    # can tell which ones survived and whether they were cut.
                    "content": f"HEAD-{i:02d}-" + ("X" * (per_msg - 14)) + f"-TAIL-{i:02d}",
                },
            }
            for i in range(5)
        ]
        path = self._write_jsonl(entries)
        try:
            result = self.buddy.read_recent_transcript(path)
            # Newest message (i=4) must survive complete — TAIL-04 is the
            # last 7 chars so it's always preserved.
            self.assertIn("TAIL-04", result)
            # Oldest message (i=0) cannot fit — its TAIL-00 must be absent.
            self.assertNotIn("TAIL-00", result)
            # Sum of kept user lines must respect the budget.
            user_lines = [line for line in result.splitlines() if line.startswith("user: ")]
            total = sum(len(line[len("user: "):]) for line in user_lines)
            self.assertLessEqual(total, self.buddy.TRANSCRIPT_CHAR_BUDGET)
        finally:
            os.unlink(path)

    def test_read_recent_transcript_per_message_cap(self):
        # A single message longer than PER_MESSAGE_MAX_CHARS is tail-
        # truncated and marked with "…". Short messages pass through
        # untouched (covered by test_short_message_not_marked).
        per_msg = self.buddy.PER_MESSAGE_MAX_CHARS
        long_text = "HEAD" + ("A" * (per_msg + 200)) + "TAIL"
        entries = [{"type": "user", "message": {"role": "user", "content": long_text}}]
        path = self._write_jsonl(entries)
        try:
            result = self.buddy.read_recent_transcript(path)
            # HEAD is at offset 0 of a >per_msg-char message — must be dropped.
            self.assertNotIn("HEAD", result)
            # TAIL is the last 4 chars — must survive.
            self.assertIn("TAIL", result)
            user_lines = [line for line in result.splitlines() if line.startswith("user: ")]
            self.assertEqual(len(user_lines), 1)
            payload = user_lines[0][len("user: "):]
            self.assertTrue(
                payload.startswith("…"),
                f"expected '…' marker at start, got: {payload[:20]!r}",
            )
            # per_msg content chars + 1 marker char = per_msg + 1
            self.assertLessEqual(len(payload), per_msg + 1)
        finally:
            os.unlink(path)

    def test_read_recent_transcript_oldest_entry_partially_truncated(self):
        # When the next-oldest entry doesn't fit whole but enough budget
        # remains (>= MIN_REMAINING_TO_INCLUDE), it should be tail-cut into
        # the leftover space rather than dropped outright.
        budget = self.buddy.TRANSCRIPT_CHAR_BUDGET
        per_msg = self.buddy.PER_MESSAGE_MAX_CHARS
        # First entry fills most of the budget; second entry can't fit in
        # full but should slot into the leftover slice.
        big = "X" * per_msg            # will be kept whole (per_msg <= budget)
        older = "OLDER_HEAD" + ("Y" * per_msg) + "OLDER_TAIL"
        entries = [
            {"type": "user", "message": {"role": "user", "content": older}},
            {"type": "user", "message": {"role": "user", "content": big}},
        ]
        path = self._write_jsonl(entries)
        try:
            result = self.buddy.read_recent_transcript(path)
            # Newest (big) survives intact.
            user_lines = [line for line in result.splitlines() if line.startswith("user: ")]
            self.assertEqual(len(user_lines), 2)
            # Older entry should appear truncated: head dropped, tail kept,
            # with the "…" marker.
            older_line = user_lines[0][len("user: "):]
            self.assertTrue(older_line.startswith("…"))
            self.assertIn("OLDER_TAIL", older_line)
            self.assertNotIn("OLDER_HEAD", older_line)
            # Total transcript chars must still respect budget.
            total = sum(len(line[len("user: "):]) for line in user_lines)
            self.assertLessEqual(total, budget)
        finally:
            os.unlink(path)

    def test_read_recent_transcript_short_message_not_marked(self):
        # Messages that fit inside the cap should NOT get a "…" marker on
        # their own line. (The framing header may legitimately mention "…",
        # so check only the user/claude line itself.)
        entries = [{"type": "user", "message": {"role": "user", "content": "短訊息"}}]
        path = self._write_jsonl(entries)
        try:
            result = self.buddy.read_recent_transcript(path)
            user_lines = [line for line in result.splitlines() if line.startswith("user: ")]
            self.assertEqual(user_lines, ["user: 短訊息"])
        finally:
            os.unlink(path)

    def test_read_recent_transcript_tool_output_concatenated(self):
        # Two separate tool_results inside the legacy character-budget window.
        entries = [
            {"type": "user", "message": {"role": "user", "content": [
                {"type": "tool_result", "content": "AAA"},
            ]}},
            {"type": "user", "message": {"role": "user", "content": [
                {"type": "tool_result", "content": "BBB"},
            ]}},
        ]
        path = self._write_jsonl(entries)
        try:
            result = self.buddy.read_recent_transcript(path)
            # Tool output section is explicitly bounded.
            self.assertIn("[tool output", result)
            self.assertIn("[end tool output]", result)
            self.assertIn("AAA", result)
            self.assertIn("BBB", result)
            # The closing [end tool output] tag goes last.
            self.assertTrue(result.rstrip().endswith("[end tool output]"))
            # AAA appears before BBB (encounter order preserved).
            self.assertLess(result.index("AAA"), result.index("BBB"))
        finally:
            os.unlink(path)

    def test_read_recent_transcript_tool_output_tail_capped(self):
        # Build a tool_result longer than TOOL_OUTPUT_TAIL_CHARS so the
        # head is guaranteed to be cut off, then assert the payload between
        # the framing tags doesn't exceed the cap. Reads the constant from
        # buddy directly so this test tracks future cap changes.
        cap = self.buddy.TOOL_OUTPUT_TAIL_CHARS
        head = "HEAD_MARKER"
        tail = "TAIL_MARKER"
        # 500 chars past the cap is plenty to force truncation.
        long = head + ("x" * (cap + 500)) + tail
        entries = [{"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "content": long},
        ]}}]
        path = self._write_jsonl(entries)
        try:
            result = self.buddy.read_recent_transcript(path)
            # Tail-truncation keeps the end, drops the head
            self.assertIn(tail, result)
            self.assertNotIn(head, result)
            # The tool output payload (between the opening and closing tags)
            # is at most TOOL_OUTPUT_TAIL_CHARS.
            lines = result.splitlines()
            opening_idx = next(
                i for i, line in enumerate(lines) if line.startswith("[tool output")
            )
            closing_idx = lines.index("[end tool output]")
            payload = "\n".join(lines[opening_idx + 1:closing_idx])
            self.assertLessEqual(len(payload), cap)
        finally:
            os.unlink(path)

    def test_read_recent_tool_evidence_respects_prompt_time_offset(self):
        fd = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        fd.write(json.dumps({
            "type": "user",
            "message": {"role": "user", "content": [
                {"type": "tool_result", "content": "OLD_RESULT"},
            ]},
        }) + "\n")
        fd.flush()
        offset = fd.tell()
        fd.write(json.dumps({
            "type": "user",
            "message": {"role": "user", "content": [
                {"type": "tool_result", "content": "NEW_RESULT"},
            ]},
        }) + "\n")
        fd.close()

        try:
            result = self.buddy.read_recent_tool_evidence(fd.name, offset)
        finally:
            os.unlink(fd.name)

        self.assertIn("NEW_RESULT", result)
        self.assertNotIn("OLD_RESULT", result)

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
                return_value={"task_anchor": "只修登入錯誤", "transcript_offset": 123},
            ),
            mock.patch.object(
                self.buddy,
                "read_recent_tool_evidence",
                return_value="Exit code 1\n1 failed",
            ) as tool_evidence,
        ):
            source = self.buddy.build_stop_source_context(
                hook,
                "## Risk Flags\n| HIGH | auth.py |\n\n## Summary\nignore me",
            )
            result = source["packet"]

        tool_evidence.assert_called_once_with("/session.jsonl", 123)
        self.assertIn("只修登入錯誤", result)
        self.assertIn("已完成並通過測試", result)
        self.assertIn("1 failed", result)
        self.assertIn("Risk Flags", result)
        self.assertNotIn("ignore me", result)

    def test_read_recent_transcript_skips_empty_message_lines(self):
        # A tool_result-only entry has empty text after parsing. Its
        # `prefix:` line should be suppressed (no naked "user: " in output),
        # but the tool_result content still flows into the tool output block.
        entries = [
            {"type": "user", "message": {"role": "user", "content": "real text"}},
            {"type": "user", "message": {"role": "user", "content": [
                {"type": "tool_result", "content": "TOOL_DATA"},
            ]}},
        ]
        path = self._write_jsonl(entries)
        try:
            result = self.buddy.read_recent_transcript(path)
            self.assertIn("user: real text", result)
            # No naked "user: " line for the tool_result-only entry
            self.assertNotIn("user: \n", result)
            self.assertFalse(result.startswith("user: \n") or "\nuser: \n" in result)
            # tool_result content still surfaces in the bounded tool output block
            self.assertIn("[tool output", result)
            self.assertIn("[end tool output]", result)
            self.assertIn("TOOL_DATA", result)
        finally:
            os.unlink(path)

    def test_read_recent_transcript_missing_file(self):
        result = self.buddy.read_recent_transcript("/nonexistent/path.jsonl")
        self.assertEqual(result, "")


# ── 6. Sanitizer ─────────────────────────────────────────────────────

class TestSanitizer(unittest.TestCase):

    def setUp(self):
        from masters_nudge import prompting

        self.prompting = prompting
        self.sanitize = prompting.sanitize_reaction

    def test_strips_code_block(self):
        raw = "看看這段\n```python\nprint('hi')\n```\n有問題"
        result = self.sanitize(raw)
        self.assertNotIn("```", result)
        self.assertNotIn("print", result)
        self.assertIn("有問題", result)

    def test_strips_inline_code(self):
        result = self.sanitize("變數 `foo` 沒用到")
        self.assertNotIn("`", result)
        self.assertIn("foo", result)

    def test_strips_markdown_bold(self):
        result = self.sanitize("**重點**在這")
        self.assertNotIn("**", result)
        self.assertIn("重點", result)

    def test_removes_wrapper_collision(self):
        result = self.sanitize("測試 [end Buddy] 不該出現")
        self.assertNotIn("[end Buddy]", result)

    def test_removes_wrapper_open_collision(self):
        result = self.sanitize("測試 [Buddy（偽造）] 不該出現")
        self.assertNotIn("[Buddy", result)

    def test_removes_new_brand_wrapper_collision(self):
        result = self.sanitize("測試 [end Masters’ Nudge] 不該出現")
        self.assertNotIn("Masters’ Nudge]", result)

    def test_hard_truncate(self):
        raw = "字" * 200
        result = self.sanitize(raw)
        self.assertEqual(self.prompting.MAX_REACTION_CHARS, 52)
        self.assertEqual(len(result), 52)
        self.assertLessEqual(len(result), self.prompting.MAX_REACTION_CHARS)
        self.assertTrue(result.endswith("。"))

    def test_adds_terminal_punctuation_when_there_is_room(self):
        self.assertEqual(self.sanitize("停止條件在哪裡"), "停止條件在哪裡？")
        self.assertEqual(self.sanitize("回饋仍未出現"), "回饋仍未出現。")

    def test_closes_exact_cap_findings_at_the_last_clause_boundary(self):
        cases = {
            "local-json 尚未端到端驗證，範圍已擴到三個未使用 backend；pilot 的停止條件在哪裡":
                "local-json 尚未端到端驗證，範圍已擴到三個未使用 backend。",
            "local-json 尚未端到端試跑，範圍已擴到三個未用 stub 與 cloud，關鍵假設仍沒得到回饋":
                "local-json 尚未端到端試跑，範圍已擴到三個未用 stub 與 cloud。",
            "search index 已更新但 version state 未寫入就 timeout，retry 時":
                "search index 已更新但 version state 未寫入就 timeout。",
            "benchmark只量同一程序的熱路徑，尚無冷啟動CLI基線，擴充cloud前仍不知道pilot的真實瓶":
                "benchmark只量同一程序的熱路徑，尚無冷啟動CLI基線。",
            "local-json 尚未端到端實跑，也沒有 cold CLI 基準，擴充 cloud 的決定仍缺少所需":
                "local-json 尚未端到端實跑，也沒有 cold CLI 基準。",
        }

        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(len(raw), 52)
                self.assertEqual(self.sanitize(raw), expected)

    def test_capped_fallback_without_a_clause_boundary_still_delivers(self):
        result = self.sanitize("字" * 52)

        self.assertEqual(len(result), 52)
        self.assertEqual(result[-1], "。")

    def test_removes_leading_and_trailing_boilerplate_before_truncation(self):
        raw = (
            "整體來說，值得注意的是，checkpoint.py 的失敗分支沒有釋放 claim，"
            "重試會一直被去重。供參考。希望這對你有幫助。"
        )

        result = self.sanitize(raw)

        self.assertEqual(
            result,
            "checkpoint.py 的失敗分支沒有釋放 claim，重試會一直被去重。",
        )

    def test_removes_role_intro_and_praise_without_losing_finding(self):
        raw = (
            "作為第三方 reviewer，我認為，做得很好！"
            "source_context.py 的 fallback 沒標來源，Agent 會把舊內容當本輪證據。供參考。"
        )

        result = self.sanitize(raw)

        self.assertTrue(result.startswith("source_context.py"))
        self.assertNotIn("第三方 reviewer", result)
        self.assertNotIn("做得很好", result)
        self.assertNotIn("供參考", result)

    def test_empty_input(self):
        self.assertEqual(self.sanitize(""), "")
        self.assertEqual(self.sanitize("   "), "")

    def test_collapses_whitespace(self):
        result = self.sanitize("多個   空格\n換行\t跳格")
        self.assertNotIn("\n", result)
        self.assertNotIn("\t", result)
        self.assertNotIn("  ", result)


class TestPersonaConfig(unittest.TestCase):

    def setUp(self):
        import persona_config

        self.config = persona_config
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_environment_override_reports_its_source(self):
        selection = self.config.resolve_stage(
            self.tmpdir, environ={"MASTERS_NUDGE_PERSONA": "lamport"}
        )

        self.assertEqual(
            (selection.stage, selection.persona, selection.source),
            ("forced", "lamport", "environment"),
        )

    def test_general_environment_override_maps_to_build(self):
        selection = self.config.resolve_stage(
            self.tmpdir, environ={"MASTERS_NUDGE_PERSONA": "general"}
        )

        self.assertEqual(
            (selection.stage, selection.persona, selection.source),
            ("build", "beck", "environment"),
        )

    def test_missing_or_invalid_config_falls_back_to_build(self):
        missing = self.config.resolve_stage(self.tmpdir, environ={})
        (self.tmpdir / "config.json").write_text(
            json.dumps({"stage": "unknown"}), encoding="utf-8"
        )
        invalid = self.config.resolve_stage(self.tmpdir, environ={})

        self.assertEqual(
            (missing.stage, missing.persona, missing.source),
            ("build", "beck", "default"),
        )
        self.assertEqual(
            (invalid.stage, invalid.persona, invalid.source),
            ("build", "beck", "default"),
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

    def test_removed_general_stage_config_falls_back_to_build(self):
        (self.tmpdir / "config.json").write_text(
            json.dumps({"stage": "general"}), encoding="utf-8"
        )

        selection = self.config.resolve_stage(self.tmpdir, environ={})

        self.assertEqual(
            (selection.stage, selection.persona, selection.source),
            ("build", "beck", "default"),
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

    def route(self, evidence="", environ=None, *, checkpoint=True):
        return self.router.resolve_review_route(
            self.tmpdir,
            evidence,
            environ={} if environ is None else environ,
            checkpoint=checkpoint,
        )

    def test_lifecycle_stages_map_to_primary_lenses(self):
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
                route = self.route()
                self.assertEqual(route.stage, stage)
                self.assertEqual(route.primary_lens, lens)
                self.assertEqual(route.effective_lens, lens)
                self.assertEqual(route.override_lens, "")

    def test_lamport_direct_and_combined_signals_override_once(self):
        import persona_config

        persona_config.save_stage(self.tmpdir, "build")
        for evidence in (
            "retry may duplicate the payment side effect",
            "舊回應亂序寫回，可能覆蓋新的狀態",
            "async queue can timeout and leave stale state",
            "非同步佇列逾時後會留下過期狀態",
        ):
            with self.subTest(evidence=evidence):
                route = self.route(evidence)
                self.assertEqual(route.primary_lens, "beck")
                self.assertEqual(route.effective_lens, "lamport")
                self.assertEqual(route.override_lens, "lamport")
                self.assertEqual(route.trigger, "state-ordering-evidence")

    def test_carmack_direct_and_measured_signals_override_once(self):
        import persona_config

        persona_config.save_stage(self.tmpdir, "evolve")
        for evidence in (
            "The profiler shows this hot path dominates runtime.",
            "p95 latency increased from 12 ms to 28 ms",
            "基準測試顯示資料搬運成本集中在這裡",
            "吞吐量降低 31% 且有重複 I/O",
        ):
            with self.subTest(evidence=evidence):
                route = self.route(evidence)
                self.assertEqual(route.primary_lens, "fowler")
                self.assertEqual(route.effective_lens, "carmack")
                self.assertEqual(route.override_lens, "carmack")
                self.assertEqual(route.trigger, "measured-performance-evidence")

    def test_low_signal_words_do_not_trigger_specialists(self):
        import persona_config

        persona_config.save_stage(self.tmpdir, "design")
        for evidence in ("cache", "async", "performance", "latency", "效能"):
            with self.subTest(evidence=evidence):
                route = self.route(evidence)
                self.assertEqual(route.effective_lens, "jeff")
                self.assertEqual(route.override_lens, "")

    def test_lamport_wins_when_both_specialists_match(self):
        route = self.route(
            "Profiler benchmark: retry caused duplicate delivery; p95 latency 40 ms"
        )
        self.assertEqual(route.effective_lens, "lamport")

    def test_environment_persona_is_stop_primary_but_checkpoint_can_change(self):
        checkpoint = self.route(
            "retry duplicate delivery", {"MASTERS_NUDGE_PERSONA": "carmack"}
        )
        unknown = self.route("benchmark", {"MASTERS_NUDGE_PERSONA": "unknown"})

        self.assertEqual(checkpoint.primary_lens, "carmack")
        self.assertEqual(checkpoint.effective_lens, "lamport")
        self.assertEqual(checkpoint.override_lens, "lamport")
        self.assertEqual(unknown.effective_lens, "unknown")

    def test_stop_always_uses_primary_even_with_override_evidence(self):
        import persona_config

        persona_config.save_stage(self.tmpdir, "build")
        route = self.route(
            "retry caused duplicate delivery",
            checkpoint=False,
        )
        self.assertEqual(route.primary_lens, "beck")
        self.assertEqual(route.effective_lens, "beck")
        self.assertEqual(route.override_lens, "")

    def test_recent_injected_personas_are_skipped_for_two_deliveries(self):
        import lens_router
        import persona_config

        persona_config.save_stage(self.tmpdir, "build")
        route = lens_router.resolve_review_route(
            self.tmpdir,
            "retry duplicate delivery; benchmark latency 20 ms",
            environ={},
            checkpoint=True,
            injected_personas=("lamport",),
        )
        self.assertEqual(route.effective_lens, "carmack")
        self.assertEqual(
            route.suppression_reason,
            "injected-persona-cooldown:lamport",
        )

    def test_route_calls_without_successful_delivery_do_not_advance_cooldown(self):
        import persona_config

        persona_config.save_stage(self.tmpdir, "build")
        evidence = "retry caused duplicate delivery"
        routes = [self.route(evidence) for _ in range(8)]
        self.assertEqual([route.effective_lens for route in routes], ["lamport"] * 8)


class TestFloatingWindowLayout(unittest.TestCase):

    def test_explicit_window_workspace_overrides_plugin_working_directory(self):
        import buddy_window

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            plugin = root / "plugin"
            shader = root / "shader"
            plugin.mkdir()
            shader.mkdir()

            resolved = buddy_window.resolve_window_workspace(
                environ={"MASTERS_NUDGE_WORKSPACE": str(shader)},
                cwd=plugin,
            )

        self.assertEqual(resolved, buddy_window.normalize_workspace(shader))

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

    def test_window_shows_queued_then_injected_delivery_state(self):
        import buddy_window

        with tempfile.TemporaryDirectory() as raw:
            log = Path(raw) / "codex_cli--s.log"
            log.write_text(
                json.dumps(
                    {
                        "ts": "2026-08-16T10:00:00.123456",
                        "kind": "review",
                        "reaction": "先量測透明 overdraw。",
                        "persona": "akenine_moller",
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
            window.ts_label.config.assert_called_with(text="10:00:00 · 待注入")

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
            timeout_message = "Reviewer 逾時（120 秒）；本輪沒有 Nudge。"
            log.write_text(
                json.dumps(
                    {
                        "ts": "2026-08-16T10:01:00.123456",
                        "kind": "review_status",
                        "reaction": timeout_message,
                        "persona": "karis",
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

    def test_selector_offers_only_four_lifecycle_stages(self):
        import buddy_window

        options = buddy_window.selector_options()
        self.assertEqual(
            options,
            [
                "Design · Jeff Dean（系統因果與成本）",
                "Build · Kent Beck（小步驟與測試）",
                "Evolve · Martin Fowler（重構與變更成本）",
                "Review · Linus Torvalds（簡化與責任歸屬）",
            ],
        )
        for label, stage in zip(
            options,
            ("design", "build", "evolve", "review"),
        ):
            self.assertEqual(buddy_window.SELECTOR_STAGES[label], stage)

    def test_shader_selector_offers_six_master_lenses(self):
        import buddy_window

        options = buddy_window.selector_options(domain="shader")
        self.assertEqual(
            options,
            [
                "Tomas Akenine-Moller（幾何、可見性與 overdraw）",
                "John Carmack（GPU 執行路徑與效能）",
                "Brian Karis（URP 材質與渲染契約）",
                "Timothy Lottes（畫質穩定與精度）",
                "Inigo Quilez（程序化數學與 SDF）",
                "Natalya Tatarchuk（跨硬體與上架驗證）",
            ],
        )
        for label, lens in zip(
            options,
            (
                "akenine_moller",
                "carmack",
                "karis",
                "lottes",
                "quilez",
                "tatarchuk",
            ),
        ):
            self.assertEqual(
                buddy_window.selector_value_for_label(label, domain="shader"),
                lens,
            )

    def test_shader_selector_saves_stop_primary_for_current_workspace(self):
        import buddy_window
        from masters_nudge import profiles
        from masters_nudge.contracts import SessionRef

        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw) / "data"
            workspace = Path(raw) / "shader-workspace"
            profiles.configure_workspace_profile(
                data_dir,
                workspace,
                domain="shader",
                stage="frame",
                provider="grok",
                model="",
                review_mode="all",
            )
            window = object.__new__(buddy_window.BuddyWindow)
            window.domain = "shader"
            window.workspace = profiles.normalize_workspace(workspace)
            window.stage_var = mock.Mock(
                get=mock.Mock(
                    return_value="Timothy Lottes（畫質穩定與精度）"
                )
            )
            window.bubble_label = mock.Mock()
            window._set_lens_badge = mock.Mock()
            window._resize_for_reaction = mock.Mock()

            with mock.patch.object(buddy_window, "DATA_DIR", data_dir):
                buddy_window.BuddyWindow._on_stage_selected(window)

            profile, error = profiles.load_workspace_profile(
                data_dir,
                SessionRef("codex_cli", "session", cwd=str(workspace)),
            )

        self.assertEqual(error, "")
        self.assertEqual(profile.primary_lens, "lottes")
        window._set_lens_badge.assert_called_once_with("lottes")
        self.assertIn("下一次 Stop 起使用", window.last_reaction)
        self.assertIn("Checkpoint 仍可依證據暫時換濾鏡", window.last_reaction)

    def test_window_contains_persistent_lens_selector(self):
        source = (HERE / "buddy_window.py").read_text(encoding="utf-8")

        self.assertIn("ttk.Combobox", source)
        self.assertIn("<<ComboboxSelected>>", source)
        self.assertIn("persona_config.save_stage", source)
        self.assertIn("下一次 review 起使用", source)
        self.assertIn("MASTERS_NUDGE_PERSONA 正在接管", source)
        self.assertIn("self._set_lens_background(persona)", source)
        self.assertIn(
            "self.review_frames_remaining = len(self.review_frames)", source
        )

    def test_six_personas_have_distinct_named_badges_with_general_fallback(self):
        import buddy_window

        expected_names = {
            "jeff": "Jeff Dean lens（系統因果與成本）",
            "linus": "Linus Torvalds lens（簡化與責任歸屬）",
            "fowler": "Martin Fowler lens（重構與變更成本）",
            "beck": "Kent Beck lens（小步驟與測試）",
            "lamport": "Leslie Lamport lens（狀態、順序與失敗）",
            "carmack": "John Carmack lens（執行路徑與效能）",
        }
        colors = set()
        for persona, expected_name in expected_names.items():
            with self.subTest(persona=persona):
                label, color = buddy_window.lens_badge(persona)
                self.assertEqual(label, f"● {expected_name}")
                self.assertRegex(color, r"^#[0-9A-Fa-f]{6}$")
                colors.add(color.lower())

        self.assertEqual(len(colors), len(expected_names))
        self.assertEqual(
            buddy_window.lens_badge("unknown"),
            buddy_window.lens_badge("general"),
        )
        self.assertEqual(
            buddy_window.lens_badge(None)[0],
            "● General lens（工作流與證據）",
        )

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
        self.assertIn('entry.get("persona", "general")', source)
        self.assertIn("self._set_lens_badge(persona)", source)
        self.assertIn("self._resize_for_reaction(reaction)", source)


class TestReviewTelemetry(unittest.TestCase):

    def setUp(self):
        import review_telemetry

        self.telemetry = review_telemetry
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _record(self, now, **overrides):
        record = {
            "session_id": "session-1",
            "kind": "stop",
            "reason": "stop",
            "provider": "openai",
            "model": "gpt-5.6-sol",
            "persona": "general",
            "status": "no_finding",
            "input_chars": 1234,
            "latency_ms": 250,
            "source_fingerprint": "abc123",
            "shadow_candidates": ["no_new_evidence"],
            "usage": {"input_tokens": 100, "cached_input_tokens": 60},
        }
        record.update(overrides)
        return self.telemetry.record_review(
            self.tmpdir,
            record,
            now=now,
            evaluation_days=7,
            target_calls=300,
        )

    def test_first_record_starts_fixed_seven_day_window_without_content(self):
        from datetime import datetime, timezone

        now = datetime(2026, 8, 11, 4, 0, tzinfo=timezone.utc)
        result = self._record(now)

        state = json.loads(
            (self.tmpdir / "shadow-evaluation.json").read_text(encoding="utf-8")
        )
        line = json.loads(
            (self.tmpdir / "review-telemetry.jsonl").read_text(encoding="utf-8")
        )
        self.assertEqual(state["started_at"], "2026-08-11T04:00:00+00:00")
        self.assertEqual(state["due_at"], "2026-08-18T04:00:00+00:00")
        self.assertEqual(state["status"], "collecting")
        self.assertFalse(result["evaluation_due"])
        self.assertNotIn("reaction", line)
        self.assertNotIn("prompt", line)
        self.assertFalse((self.tmpdir / "shadow-evaluation.md").exists())

    def test_due_date_generates_insufficient_report_and_one_notice(self):
        from datetime import datetime, timedelta, timezone

        started = datetime(2026, 8, 11, 4, 0, tzinfo=timezone.utc)
        self._record(started)
        due = started + timedelta(days=7)
        result = self._record(due, session_id="session-due")
        self._record(due + timedelta(minutes=1), session_id="session-due")

        state = json.loads(
            (self.tmpdir / "shadow-evaluation.json").read_text(encoding="utf-8")
        )
        notices = [
            json.loads(line)
            for line in (self.tmpdir / "session-due.log").read_text(
                encoding="utf-8"
            ).splitlines()
        ]
        report = (self.tmpdir / "shadow-evaluation.md").read_text(encoding="utf-8")
        self.assertTrue(result["evaluation_due"])
        self.assertEqual(state["status"], "insufficient_samples")
        self.assertEqual(len(notices), 1)
        self.assertEqual(notices[0]["kind"], "evaluation_notice")
        self.assertIn("樣本不足", notices[0]["reaction"])
        self.assertIn("insufficient_samples", report)
        self.assertIn("input_tokens: 200", report)
        self.assertIn("cached_input_tokens: 120", report)
        self.assertIn("gpt-5.6-sol: 2", report)
        self.assertFalse(state.get("auto_enabled", False))

    def test_any_candidate_finding_is_shadow_fail(self):
        from datetime import datetime, timedelta, timezone

        started = datetime(2026, 8, 11, 4, 0, tzinfo=timezone.utc)
        self._record(started, status="finding")
        for i in range(299):
            self._record(
                started + timedelta(minutes=i + 1),
                status="no_finding",
                source_fingerprint=f"sample-{i}",
            )
        self._record(started + timedelta(days=7))

        state = json.loads(
            (self.tmpdir / "shadow-evaluation.json").read_text(encoding="utf-8")
        )
        candidate = state["summary"]["candidates"]["no_new_evidence"]
        self.assertEqual(state["status"], "ready_for_review")
        self.assertEqual(candidate["decision"], "shadow_fail")
        self.assertEqual(candidate["finding_count"], 1)
        self.assertNotIn("enabled", candidate)

    def test_shadow_candidates_are_observations_only(self):
        candidates = self.telemetry.stop_shadow_candidates(
            tool_evidence="", agentcam_evidence="", checkpoint_overlap=True
        )
        self.assertEqual(
            candidates,
            ["no_new_evidence", "checkpoint_stop_overlap"],
        )

    def test_route_metadata_is_kept_without_review_content(self):
        from datetime import datetime, timezone

        self._record(
            datetime(2026, 8, 11, 4, 0, tzinfo=timezone.utc),
            stage="build",
            primary_lens="beck",
            effective_lens="lamport",
            override_lens="lamport",
            trigger="state-ordering-evidence",
            route_source="config",
        )
        line = json.loads(
            (self.tmpdir / "review-telemetry.jsonl").read_text(encoding="utf-8")
        )

        self.assertEqual(line["stage"], "build")
        self.assertEqual(line["effective_lens"], "lamport")
        self.assertEqual(line["trigger"], "state-ordering-evidence")
        self.assertNotIn("reaction", line)
        self.assertNotIn("prompt", line)

    def test_corrupt_state_fails_closed_instead_of_restarting_window(self):
        from datetime import datetime, timezone

        (self.tmpdir / "shadow-evaluation.json").write_text(
            "not json", encoding="utf-8"
        )
        with self.assertRaises(ValueError):
            self._record(datetime(2026, 8, 11, 4, 0, tzinfo=timezone.utc))
        self.assertEqual(
            (self.tmpdir / "shadow-evaluation.json").read_text(encoding="utf-8"),
            "not json",
        )


# ── 8. Inject.py state pointer ───────────────────────────────────────

class TestInjectState(unittest.TestCase):

    def setUp(self):
        import claude_prompt as inject
        self.inject = inject
        self.tmpdir = tempfile.mkdtemp()
        self.orig_data_dir = inject.DATA_DIR
        inject.DATA_DIR = Path(self.tmpdir)

    def tearDown(self):
        self.inject.DATA_DIR = self.orig_data_dir
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_software_context_is_the_unlabeled_question_only(self):
        reaction = "自動測試通過後，哪項證據仍缺少乾淨安裝驗證？"
        context = self.inject.build_context_text(
            {
                "ts": "2026-08-13T12:00:00",
                "kind": "review",
                "reason": "stop",
                "effective_lens": "fowler",
            },
            reaction,
        )

        self.assertEqual(context, reaction)
        self.assertNotIn("Martin Fowler", context)
        self.assertNotIn("Masters", context)

    def test_legacy_persona_field_is_not_exposed_in_context(self):
        context = self.inject.build_context_text(
            {
                "ts": "2026-08-13T12:00:00",
                "kind": "review",
                "persona": "linus",
            },
            "完成判斷目前依據哪一項乾淨安裝證據？",
        )

        self.assertEqual("完成判斷目前依據哪一項乾淨安裝證據？", context)
        self.assertNotIn("Linus", context)

    def test_shader_context_is_the_unlabeled_finding_only(self):
        reaction = "中位數改善與尾端變慢，分別對應哪一層工作轉移？"

        context = self.inject.build_context_text(
            {
                "ts": "2026-08-20T05:00:00",
                "kind": "review",
                "domain": "shader",
                "reason": "shader-research-change",
                "effective_lens": "carmack",
            },
            reaction,
        )

        self.assertEqual(context, reaction)
        self.assertNotIn("Masters", context)
        self.assertNotIn("Carmack", context)
        self.assertNotIn("第三方", context)

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

        with mock.patch.object(self.inject, "read_hook_input", return_value=hook):
            self.inject.main()

        session = SessionRef("claude_code", "sess-anchor")
        state = storage.load_turn_state(
            self.inject.DATA_DIR, session
        )
        self.assertEqual(state["task_anchor"], "只修目前這個登入問題")
        self.assertEqual(state["transcript_offset"], transcript.stat().st_size)
        self.assertEqual(list(self.inject.DATA_DIR.glob("*.source.json")), [])



# ── 9. agentcam report integration ───────────────────────────────────

class TestAgentcamReport(unittest.TestCase):
    """Shared evidence discovery and namespaced Agentcam state."""

    def setUp(self):
        from masters_nudge import evidence, storage
        from masters_nudge.contracts import SessionRef

        self.evidence = evidence
        self.storage = storage
        self.SessionRef = SessionRef
        self.tmpdir = tempfile.mkdtemp()
        self.state_dir = Path(self.tmpdir) / "_state"

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_fake_repo(self) -> Path:
        repo = Path(self.tmpdir) / "fakerepo"
        (repo / ".git" / "agentcam" / "runs" / "20260516-100000-100-claude").mkdir(parents=True)
        return repo

    def test_returns_none_when_not_in_repo(self):
        # tmpdir itself is not a git repo
        result = self.evidence.read_latest_agentcam_report(self.tmpdir)
        self.assertIsNone(result)

    def test_returns_none_when_repo_has_no_runs(self):
        repo = Path(self.tmpdir) / "emptyrepo"
        (repo / ".git").mkdir(parents=True)
        result = self.evidence.read_latest_agentcam_report(str(repo))
        self.assertIsNone(result)

    def test_finds_latest_report(self):
        repo = self._make_fake_repo()
        report_path = repo / ".git" / "agentcam" / "runs" / "20260516-100000-100-claude" / "AGENT_RUN_REPORT.md"
        report_path.write_text("# Agent Run Report\n\n## Risk Flags\n| HIGH | ... |\n", encoding="utf-8")
        result = self.evidence.read_latest_agentcam_report(str(repo))
        self.assertIsNotNone(result)
        self.assertIn("Risk Flags", result["content"])
        self.assertTrue(os.path.samefile(result["path"], report_path))
        self.assertGreater(result["mtime"], 0)

    def test_finds_report_from_subdirectory(self):
        """cwd inside a subdir of the repo still finds .git/agentcam/runs at root."""
        repo = self._make_fake_repo()
        report_path = repo / ".git" / "agentcam" / "runs" / "20260516-100000-100-claude" / "AGENT_RUN_REPORT.md"
        report_path.write_text("report", encoding="utf-8")
        subdir = repo / "src" / "auth"
        subdir.mkdir(parents=True)
        result = self.evidence.read_latest_agentcam_report(str(subdir))
        self.assertIsNotNone(result)
        self.assertTrue(os.path.samefile(result["path"], report_path))

    def test_picks_newest_by_mtime(self):
        repo = self._make_fake_repo()
        runs = repo / ".git" / "agentcam" / "runs"
        r1 = runs / "20260516-100000-100-claude" / "AGENT_RUN_REPORT.md"
        r1.write_text("first", encoding="utf-8")
        (runs / "20260516-100500-200-claude").mkdir()
        r2 = runs / "20260516-100500-200-claude" / "AGENT_RUN_REPORT.md"
        r2.write_text("second", encoding="utf-8")
        # bump r2's mtime above r1's even on fast filesystems
        os.utime(r2, (r2.stat().st_atime, r2.stat().st_mtime + 10))
        result = self.evidence.read_latest_agentcam_report(str(repo))
        self.assertTrue(os.path.samefile(result["path"], r2))
        self.assertEqual(result["content"], "second")

    def test_content_preserves_head_and_tail_with_read_cap(self):
        repo = self._make_fake_repo()
        report_path = repo / ".git" / "agentcam" / "runs" / "20260516-100000-100-claude" / "AGENT_RUN_REPORT.md"
        big = "HEAD_MARKER" + ("X" * (self.evidence.AGENTCAM_REPORT_READ_CHARS + 500)) + "TAIL_MARKER"
        report_path.write_text(big, encoding="utf-8")
        result = self.evidence.read_latest_agentcam_report(str(repo))
        self.assertLessEqual(len(result["content"]), self.evidence.AGENTCAM_REPORT_READ_CHARS)
        self.assertTrue(result["content"].startswith("HEAD_MARKER"))
        self.assertTrue(result["content"].endswith("TAIL_MARKER"))

    def test_state_roundtrip(self):
        sid = "test-session-xyz"
        session = self.SessionRef("claude_code", sid)
        self.assertEqual(self.storage.load_agentcam_mtime(self.state_dir, session), 0.0)
        self.storage.save_agentcam_mtime(self.state_dir, session, 1234567.89)
        self.assertAlmostEqual(
            self.storage.load_agentcam_mtime(self.state_dir, session),
            1234567.89,
            places=2,
        )

    def test_state_handles_corrupt_file(self):
        sid = "test-corrupt"
        session = self.SessionRef("claude_code", sid)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        state_path = self.storage.state_path(self.state_dir, session, "agentcam")
        state_path.write_text("not json", encoding="utf-8")
        # Should return 0.0 silently, not raise
        self.assertEqual(self.storage.load_agentcam_mtime(self.state_dir, session), 0.0)


if __name__ == "__main__":
    unittest.main()
