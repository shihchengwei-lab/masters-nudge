#!/usr/bin/env python3
"""Smoke tests for Masters' Nudge.

Run:  python -m unittest test_buddy -v
"""

import json
import os
import py_compile
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


# ── 1. py_compile smoke ──────────────────────────────────────────────

class TestCompile(unittest.TestCase):
    """All .py files must at least compile."""

    def test_buddy_compiles(self):
        py_compile.compile(str(HERE / "buddy.py"), doraise=True)

    def test_inject_compiles(self):
        py_compile.compile(str(HERE / "inject.py"), doraise=True)

    def test_window_compiles(self):
        py_compile.compile(str(HERE / "buddy_window.py"), doraise=True)

    def test_checkpoint_compiles(self):
        py_compile.compile(str(HERE / "checkpoint.py"), doraise=True)

    def test_source_context_compiles(self):
        py_compile.compile(str(HERE / "source_context.py"), doraise=True)


# ── 2. Persona prompt selection ──────────────────────────────────────

class TestBranding(unittest.TestCase):
    """Public surfaces use the new name while legacy paths stay compatible."""

    def test_public_brand_name_is_masters_nudge(self):
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        readme_zh = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")
        prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")
        window = (HERE / "buddy_window.py").read_text(encoding="utf-8")
        installer = (HERE / "install.sh").read_text(encoding="utf-8")

        self.assertTrue(readme.startswith("# Masters’ Nudge"))
        self.assertTrue(readme_zh.startswith("# Masters’ Nudge"))
        self.assertIn("你是 Masters’ Nudge", prompt)
        self.assertIn('self.root.title("Masters’ Nudge")', window)
        self.assertIn('echo "Masters’ Nudge — install"', installer)

    def test_readmes_explain_six_master_lenses_and_compatibility_layer(self):
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        readme_zh = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")

        self.assertIn("### Six master lenses", readme)
        self.assertIn("### 六種 master lenses", readme_zh)
        self.assertNotIn("### Engineering persona lenses", readme)
        self.assertNotIn("### 工程 persona 鏡頭", readme_zh)
        self.assertIn("BUDDY_*", readme)
        self.assertIn("compatibility", readme.lower())
        self.assertIn("BUDDY_*", readme_zh)
        self.assertIn("相容", readme_zh)
        self.assertIn("two short selection examples", readme)
        self.assertIn("兩個極短選題例", readme_zh)

    def test_readmes_include_windows_powershell_env_examples(self):
        readme = (HERE / "README.md").read_text(encoding="utf-8")
        readme_zh = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")

        for document in (readme, readme_zh):
            self.assertIn("$env:BUDDY_SPRITE_PATH", document)
            self.assertIn("$env:BUDDY_PERSONA", document)

    def test_new_brand_is_used_in_agent_visible_checkpoint_wrapper(self):
        import checkpoint

        output = checkpoint.build_hook_output(
            "PostToolUseFailure", "測試結果跟宣告不一致", "test-fail"
        )
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Masters’ Nudge", context)
        self.assertNotIn("[Buddy", context)

    def test_legacy_runtime_paths_remain_for_existing_installations(self):
        installer = (HERE / "install.sh").read_text(encoding="utf-8")
        settings = (HERE / "settings-snippet.json").read_text(encoding="utf-8")

        self.assertIn("~/.claude/scripts/buddy", installer)
        self.assertIn("~/.claude/scripts/buddy", settings)
        self.assertIn("BUDDY_PROVIDER", (HERE / "buddy.py").read_text(encoding="utf-8"))

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


class TestPersonaPromptSelection(unittest.TestCase):
    PERSONAS = {
        "jeff": "Jeff Dean",
        "linus": "Linus Torvalds",
        "fowler": "Martin Fowler",
        "beck": "Kent Beck",
        "lamport": "Leslie Lamport",
        "carmack": "John Carmack",
    }

    def setUp(self):
        import buddy
        self.buddy = buddy

    def test_default_prompt_uses_evidence_first_review_without_lens_overlay(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            result = self.buddy.build_system_prompt()

        self.assertIn("你是 Masters’ Nudge", result)
        self.assertNotIn("# 工程觀察鏡頭", result)

    def test_each_supported_persona_appends_its_overlay(self):
        for persona, display_name in self.PERSONAS.items():
            with self.subTest(persona=persona):
                with mock.patch.dict(os.environ, {"BUDDY_PERSONA": persona}, clear=True):
                    result = self.buddy.build_system_prompt()

                self.assertIn("你是 Masters’ Nudge", result)
                self.assertIn("# 工程觀察鏡頭", result)
                self.assertIn(display_name, result)
                self.assertIn("作為注意力索引", result)
                self.assertIn("身份與語氣維持 Masters’ Nudge", result)
                self.assertNotIn("不要假裝自己是這位人物", result)
                self.assertNotIn("模仿口吻、迷因", result)
                overlay = (HERE / "personas" / f"{persona}.txt").read_text(
                    encoding="utf-8"
                ).strip()
                self.assertTrue(overlay)
                self.assertTrue(result.endswith(f"{overlay}\n"))

    def test_each_persona_has_exactly_two_short_selection_examples(self):
        marker = "選題例（只示範先檢查哪裡，不示範輸出字數或固定措辭）："

        for persona in self.PERSONAS:
            with self.subTest(persona=persona):
                overlay = (HERE / "personas" / f"{persona}.txt").read_text(
                    encoding="utf-8"
                )
                self.assertEqual(overlay.count(marker), 1)
                example_block = overlay.split(marker, 1)[1].split("\n\n", 1)[0]
                examples = [
                    line.removeprefix("- ").strip()
                    for line in example_block.splitlines()
                    if line.startswith("- ")
                ]
                self.assertEqual(len(examples), 2)
                for example in examples:
                    self.assertIn("→", example)
                    self.assertLessEqual(len(example), 46)

    def test_persona_directory_contains_exactly_the_supported_overlays(self):
        files = {path.stem for path in (HERE / "personas").glob("*.txt")}
        self.assertEqual(files, set(self.PERSONAS))

    def test_unknown_persona_stops_instead_of_silently_using_default(self):
        with mock.patch.dict(os.environ, {"BUDDY_PERSONA": "unknown"}, clear=True):
            with mock.patch.object(self.buddy, "log_error") as log_error:
                result = self.buddy.build_system_prompt()

        self.assertEqual(result, "")
        log_error.assert_called_once()
        self.assertIn("unknown persona", log_error.call_args.args[0])

    def test_installer_copies_persona_overlays(self):
        installer = (HERE / "install.sh").read_text(encoding="utf-8")
        self.assertIn('cp -R "$SRC_DIR/personas" "$TARGET_DIR/"', installer)

    def test_base_prompt_delegates_attention_after_high_risk_screen(self):
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("先做高風險篩選", base_prompt)
        self.assertIn("由該鏡頭決定先檢查哪類工程問題", base_prompt)
        self.assertIn("未使用工程觀察鏡頭時", base_prompt)
        self.assertNotIn("其他問題只有非常明確時才提", base_prompt)

    def test_base_prompt_preserves_problem_and_location_inside_length_cap(self):
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("優先保留問題與位置", base_prompt)
        self.assertIn("不犧牲前兩者", base_prompt)

    def test_base_prompt_targets_48_to_52_useful_characters_without_filler(self):
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("目標 48–52 字", base_prompt)
        self.assertIn("硬上限 52 字", base_prompt)
        self.assertIn("客套話", base_prompt)
        self.assertIn("角色自介", base_prompt)
        self.assertNotIn("28 字", base_prompt)

        examples = base_prompt.split("# 可以參考的語氣", 1)[1].split(
            "# 送出前只問一件事", 1
        )[0]
        finding_examples = [
            line.strip()
            for line in examples.splitlines()
            if line.strip() and line.strip() != "這輪沒看到明顯問題。"
        ]
        self.assertTrue(finding_examples)
        for example in finding_examples:
            with self.subTest(example=example):
                self.assertGreaterEqual(len(example), 48)
                self.assertLessEqual(len(example), 52)

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
        base_prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")
        packet = self.buddy.source_context.build_stop_packet(
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

    def test_source_state_saves_bounded_task_anchor_and_transcript_offset(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            transcript = Path(tmpdir) / "session.jsonl"
            transcript.write_text("existing transcript\n", encoding="utf-8")
            expected_offset = transcript.stat().st_size
            prompt = "PROMPT_HEAD" + ("p" * 3000) + "PROMPT_TAIL"

            self.source.save_source_state(
                Path(tmpdir), "session/unsafe", prompt, str(transcript)
            )
            state = self.source.load_source_state(Path(tmpdir), "session/unsafe")

        self.assertLessEqual(
            len(state["task_anchor"]), self.source.TASK_ANCHOR_MAX_CHARS
        )
        self.assertIn("PROMPT_HEAD", state["task_anchor"])
        self.assertIn("PROMPT_TAIL", state["task_anchor"])
        self.assertEqual(state["transcript_offset"], expected_offset)

    def test_source_state_invalid_offset_falls_back_without_losing_anchor(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = self.source.source_state_path(Path(tmpdir), "session-1")
            path.write_text(
                json.dumps({"task_anchor": "保留這個要求", "transcript_offset": "bad"}),
                encoding="utf-8",
            )

            state = self.source.load_source_state(Path(tmpdir), "session-1")

        self.assertEqual(state["task_anchor"], "保留這個要求")
        self.assertEqual(state["transcript_offset"], 0)

    def test_checkpoint_packet_is_event_centered_and_source_labeled(self):
        packet = self.source.build_checkpoint_packet(
            task_anchor="修正登入測試",
            event_context="reason: test-fail\nfailure: 2 failed",
            assistant_context="正在調整 auth.py",
        )

        self.assertIn("[task anchor]", packet)
        self.assertIn("修正登入測試", packet)
        self.assertIn("[checkpoint evidence]", packet)
        self.assertIn("2 failed", packet)
        self.assertIn("[recent agent context]", packet)
        self.assertNotIn("[transcript", packet)

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

    def test_installer_copies_source_context(self):
        installer = (HERE / "install.sh").read_text(encoding="utf-8")
        self.assertIn('cp "$SRC_DIR/source_context.py" "$TARGET_DIR/"', installer)


# ── 4. Checkpoint nudge hooks ────────────────────────────────────────

class TestCheckpointClassification(unittest.TestCase):

    def setUp(self):
        import checkpoint
        self.checkpoint = checkpoint

    def test_failed_test_command_is_test_fail(self):
        hook = {
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "tool_input": {"command": "python -m pytest"},
            "error": "Exit code 1\n2 failed, 8 passed",
        }

        result = self.checkpoint.classify_checkpoint(hook)

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

        result = self.checkpoint.classify_checkpoint(hook, changed_line_count=0)

        self.assertEqual(result["reason"], "test-fail")

    def test_non_test_tool_failure_is_error(self):
        hook = {
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Read",
            "tool_input": {"file_path": "/missing.txt"},
            "error": "File does not exist",
        }

        result = self.checkpoint.classify_checkpoint(hook)

        self.assertEqual(result["reason"], "error")

    def test_interrupted_tool_is_not_a_checkpoint(self):
        hook = {
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Bash",
            "tool_input": {"command": "pytest"},
            "error": "Interrupted",
            "is_interrupt": True,
        }

        self.assertIsNone(self.checkpoint.classify_checkpoint(hook))

    def test_large_diff_triggers_only_above_original_threshold(self):
        hook = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "tool_input": {"file_path": "/project/app.py"},
            "tool_response": {"success": True},
        }

        self.assertIsNone(
            self.checkpoint.classify_checkpoint(hook, changed_line_count=80)
        )
        result = self.checkpoint.classify_checkpoint(hook, changed_line_count=81)
        self.assertEqual(result["reason"], "large-diff")
        self.assertIn("81", result["context"])
        later = self.checkpoint.classify_checkpoint(hook, changed_line_count=120)
        self.assertEqual(result["fingerprint"], later["fingerprint"])

    def test_changed_line_count_includes_tracked_and_untracked_text(self):
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
                self.checkpoint, "_git_output", side_effect=fake_git
            ):
                result = self.checkpoint.get_changed_line_count(tmpdir)

        self.assertEqual(result, 85)

    def test_unrelated_success_does_not_trigger(self):
        hook = {
            "hook_event_name": "PostToolUse",
            "tool_name": "Read",
            "tool_input": {"file_path": "/project/app.py"},
            "tool_response": {"success": True},
        }

        self.assertIsNone(self.checkpoint.classify_checkpoint(hook))


class TestCheckpointDelivery(unittest.TestCase):

    def setUp(self):
        import checkpoint
        self.checkpoint = checkpoint
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_patch = mock.patch.object(
            checkpoint, "CHECKPOINT_STATE_DIR", Path(self.tmpdir.name)
        )
        self.state_patch.start()

    def tearDown(self):
        self.state_patch.stop()
        self.tmpdir.cleanup()

    def test_same_checkpoint_fingerprint_is_claimed_once(self):
        claimed = self.checkpoint.claim_checkpoint("session-1", "same-fingerprint")
        claimed_again = self.checkpoint.claim_checkpoint(
            "session-1", "same-fingerprint"
        )

        self.assertTrue(claimed)
        self.assertFalse(claimed_again)

    def test_release_allows_retry_after_reviewer_failure(self):
        self.assertTrue(self.checkpoint.claim_checkpoint("session-1", "retry-me"))
        self.checkpoint.release_checkpoint("session-1", "retry-me")
        self.assertTrue(self.checkpoint.claim_checkpoint("session-1", "retry-me"))

    def test_output_is_nudge_only_additional_context(self):
        result = self.checkpoint.build_hook_output(
            "PostToolUseFailure", "先確認失敗根因。", "error"
        )

        self.assertEqual(
            result["hookSpecificOutput"]["hookEventName"],
            "PostToolUseFailure",
        )
        self.assertIn(
            "先確認失敗根因。",
            result["hookSpecificOutput"]["additionalContext"],
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
        event = self.checkpoint.classify_checkpoint(hook)
        self.assertTrue(
            self.checkpoint.claim_checkpoint("session-1", event["fingerprint"])
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

    def test_settings_register_checkpoint_hooks_without_async(self):
        settings = json.loads(
            (HERE / "settings-snippet.json").read_text(encoding="utf-8")
        )

        self.assertIn("PostToolUse", settings["hooks"])
        self.assertIn("PostToolUseFailure", settings["hooks"])
        for event_name in ("PostToolUse", "PostToolUseFailure"):
            handlers = settings["hooks"][event_name]
            command_hooks = [
                hook
                for group in handlers
                for hook in group["hooks"]
            ]
            self.assertTrue(
                any("checkpoint.sh" in hook["command"] for hook in command_hooks)
            )
            self.assertTrue(all(not hook.get("async") for hook in command_hooks))

    def test_installer_copies_checkpoint_files(self):
        installer = (HERE / "install.sh").read_text(encoding="utf-8")
        self.assertIn('cp "$SRC_DIR/checkpoint.py" "$TARGET_DIR/"', installer)
        self.assertIn('cp "$SRC_DIR/checkpoint.sh" "$TARGET_DIR/"', installer)

    def test_generate_nudge_uses_task_anchor_and_event_packet_not_full_transcript(self):
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
                self.checkpoint.source_context,
                "load_source_state",
                return_value={"task_anchor": "只修路徑問題", "transcript_offset": 42},
            ),
            mock.patch.object(
                self.checkpoint.buddy,
                "read_latest_assistant_text",
                return_value="正在檢查路徑",
            ),
            mock.patch.object(
                self.checkpoint.buddy, "build_system_prompt", return_value="system"
            ),
            mock.patch.object(
                self.checkpoint.buddy, "read_recent_reactions", return_value=[]
            ),
            mock.patch.object(
                self.checkpoint.buddy,
                "dispatch_call",
                return_value="路徑前提還沒成立。",
            ) as dispatch,
        ):
            result = self.checkpoint.generate_nudge(hook, event)

        self.assertEqual(result, "路徑前提還沒成立。")
        payload = dispatch.call_args.args[1]
        self.assertIn("只修路徑問題", payload)
        self.assertIn("missing file", payload)
        self.assertIn("正在檢查路徑", payload)
        self.assertNotIn("[transcript", payload)


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
        import buddy
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
        hook = {
            "session_id": "session-1",
            "transcript_path": "/session.jsonl",
            "last_assistant_message": "已完成並通過測試",
        }
        with (
            mock.patch.object(
                self.buddy.source_context,
                "load_source_state",
                return_value={"task_anchor": "只修登入錯誤", "transcript_offset": 123},
            ),
            mock.patch.object(
                self.buddy,
                "read_recent_tool_evidence",
                return_value="Exit code 1\n1 failed",
            ) as tool_evidence,
        ):
            result = self.buddy.build_stop_source_packet(
                hook,
                "## Risk Flags\n| HIGH | auth.py |\n\n## Summary\nignore me",
            )

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
        import buddy
        self.sanitize = buddy.sanitize_reaction

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
        import buddy
        raw = "字" * 200
        result = self.sanitize(raw)
        self.assertEqual(buddy.MAX_REACTION_CHARS, 52)
        self.assertEqual(len(result), 52)
        self.assertLessEqual(len(result), buddy.MAX_REACTION_CHARS)

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


class TestFloatingWindowLayout(unittest.TestCase):

    def test_window_grows_for_a_52_character_reaction(self):
        import buddy_window

        short_height = buddy_window.window_height_for_reaction("短提醒。")
        long_height = buddy_window.window_height_for_reaction("字" * 52)

        self.assertEqual(short_height, buddy_window.WINDOW_MIN_HEIGHT)
        self.assertGreater(long_height, short_height)
        self.assertLessEqual(long_height, buddy_window.WINDOW_MAX_HEIGHT)

    def test_window_wrap_width_and_resize_hook_cover_long_reactions(self):
        import buddy_window

        source = (HERE / "buddy_window.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(buddy_window.BUBBLE_WRAP_LENGTH, 300)
        self.assertIn("self._resize_for_reaction(reaction)", source)


# ── 7. Mock CLI calls ────────────────────────────────────────────────

class TestCallClaude(unittest.TestCase):

    def setUp(self):
        import buddy
        self.buddy = buddy

    @mock.patch("subprocess.run")
    def test_call_claude_returns_reaction(self, mock_run):
        mock_run.return_value = mock.Mock(returncode=0, stdout="這次乾淨", stderr="")
        result = self.buddy.call_claude("system prompt", "transcript", "sonnet")
        self.assertEqual(result, "這次乾淨")
        mock_run.assert_called_once()
        args = mock_run.call_args
        cmd = args[0][0]
        self.assertIn("claude", cmd[0])
        self.assertIn("--model", cmd)

    @mock.patch("subprocess.run")
    def test_call_claude_nonzero_exit(self, mock_run):
        mock_run.return_value = mock.Mock(returncode=1, stdout="", stderr="error")
        result = self.buddy.call_claude("sp", "tx", "sonnet")
        self.assertEqual(result, "")

    @mock.patch("subprocess.run")
    def test_call_claude_timeout(self, mock_run):
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=60)
        result = self.buddy.call_claude("sp", "tx", "sonnet")
        self.assertEqual(result, "")

    @mock.patch("subprocess.run")
    def test_call_claude_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        result = self.buddy.call_claude("sp", "tx", "sonnet")
        self.assertEqual(result, "")


class TestCallCodex(unittest.TestCase):

    def setUp(self):
        import buddy
        self.buddy = buddy

    @mock.patch("buddy._resolve_codex_bin", return_value=None)
    def test_codex_not_found(self, _):
        result = self.buddy.call_codex("sp", "tx", "gpt-5.5")
        self.assertEqual(result, "")

    @mock.patch("subprocess.run")
    @mock.patch("buddy._resolve_codex_bin", return_value="/usr/bin/codex")
    def test_call_codex_reads_output_file(self, _, mock_run):
        mock_run.return_value = mock.Mock(returncode=0, stdout="", stderr="")
        # call_codex writes to a temp file then reads it — we need to
        # intercept the output file path and write to it during the mock
        def fake_run(cmd, **kwargs):
            # Find the -o flag and write reaction to that file
            cmd_list = cmd if isinstance(cmd, list) else cmd.split()
            for i, arg in enumerate(cmd_list):
                if arg == "-o" and i + 1 < len(cmd_list):
                    Path(cmd_list[i + 1]).write_text("危險，別推", encoding="utf-8")
                    break
            return mock.Mock(returncode=0, stdout="", stderr="")

        mock_run.side_effect = fake_run
        result = self.buddy.call_codex("sp", "tx", "gpt-5.5")
        self.assertEqual(result, "危險，別推")


class TestParseReaction(unittest.TestCase):

    def setUp(self):
        import buddy
        self.parse = buddy.parse_reaction

    def test_plain_text(self):
        self.assertEqual(self.parse("這次乾淨"), "這次乾淨")

    def test_json_envelope_result(self):
        obj = json.dumps({"result": "反應文字"})
        self.assertEqual(self.parse(obj), "反應文字")

    def test_json_envelope_content(self):
        obj = json.dumps({"content": "反應"})
        self.assertEqual(self.parse(obj), "反應")

    def test_empty(self):
        self.assertEqual(self.parse(""), "")
        self.assertEqual(self.parse("  "), "")


# ── 8. Inject.py state pointer ───────────────────────────────────────

class TestInjectState(unittest.TestCase):

    def setUp(self):
        import inject
        self.inject = inject
        self.tmpdir = tempfile.mkdtemp()
        self.orig_buddy_dir = inject.BUDDY_DIR
        inject.BUDDY_DIR = Path(self.tmpdir)

    def tearDown(self):
        self.inject.BUDDY_DIR = self.orig_buddy_dir
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_load_state_missing_file(self):
        state = self.inject.load_state("no-such-session")
        self.assertEqual(state, {"last_ts": ""})

    def test_save_and_load_state(self):
        self.inject.save_state("sess1", {"last_ts": "2026-05-09T10:00:00"})
        state = self.inject.load_state("sess1")
        self.assertEqual(state["last_ts"], "2026-05-09T10:00:00")

    def test_read_pending_empty_log(self):
        pending = self.inject.read_pending("sess1", "")
        self.assertEqual(pending, [])

    def test_read_pending_filters_by_ts(self):
        log_path = Path(self.tmpdir) / "sess1.log"
        entries = [
            {"ts": "2026-05-09T10:00:00", "reaction": "舊的"},
            {"ts": "2026-05-09T10:01:00", "reaction": "新的"},
            {"ts": "2026-05-09T10:02:00", "reaction": "最新"},
        ]
        with log_path.open("w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")

        # Only entries after 10:00:30 should appear
        pending = self.inject.read_pending("sess1", "2026-05-09T10:00:30")
        self.assertEqual(len(pending), 2)
        self.assertEqual(pending[0]["reaction"], "新的")
        self.assertEqual(pending[1]["reaction"], "最新")

    def test_read_pending_returns_all_when_no_last_ts(self):
        log_path = Path(self.tmpdir) / "sess2.log"
        entries = [
            {"ts": "2026-05-09T10:00:00", "reaction": "a"},
            {"ts": "2026-05-09T10:01:00", "reaction": "b"},
        ]
        with log_path.open("w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")

        pending = self.inject.read_pending("sess2", "")
        self.assertEqual(len(pending), 2)

    def test_main_saves_task_anchor_even_when_no_buddy_reaction_is_pending(self):
        transcript = Path(self.tmpdir) / "session.jsonl"
        transcript.write_text("existing\n", encoding="utf-8")
        hook = {
            "session_id": "sess-anchor",
            "prompt": "只修目前這個登入問題",
            "transcript_path": str(transcript),
        }

        with mock.patch.object(self.inject, "read_hook_input", return_value=hook):
            self.inject.main()

        import source_context
        state = source_context.load_source_state(
            self.inject.BUDDY_DIR, "sess-anchor"
        )
        self.assertEqual(state["task_anchor"], "只修目前這個登入問題")
        self.assertEqual(state["transcript_offset"], transcript.stat().st_size)



# ── 9. agentcam report integration ───────────────────────────────────

class TestAgentcamReport(unittest.TestCase):
    """buddy.read_latest_agentcam_report walks up to git root and finds
    the newest AGENT_RUN_REPORT.md under .git/agentcam/runs/.
    Dedup state functions round-trip the last seen mtime per session."""

    def setUp(self):
        if "buddy" not in sys.modules:
            import buddy  # noqa: F401
        self.buddy = sys.modules["buddy"]
        self.tmpdir = tempfile.mkdtemp()
        # patch BUDDY_DIR so state writes don't touch the real ~/.claude
        self._orig_buddy_dir = self.buddy.BUDDY_DIR
        self.buddy.BUDDY_DIR = Path(self.tmpdir) / "_state"

    def tearDown(self):
        self.buddy.BUDDY_DIR = self._orig_buddy_dir
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_fake_repo(self) -> Path:
        repo = Path(self.tmpdir) / "fakerepo"
        (repo / ".git" / "agentcam" / "runs" / "20260516-100000-100-claude").mkdir(parents=True)
        return repo

    def test_returns_none_when_not_in_repo(self):
        # tmpdir itself is not a git repo
        result = self.buddy.read_latest_agentcam_report(self.tmpdir)
        self.assertIsNone(result)

    def test_returns_none_when_repo_has_no_runs(self):
        repo = Path(self.tmpdir) / "emptyrepo"
        (repo / ".git").mkdir(parents=True)
        result = self.buddy.read_latest_agentcam_report(str(repo))
        self.assertIsNone(result)

    def test_finds_latest_report(self):
        repo = self._make_fake_repo()
        report_path = repo / ".git" / "agentcam" / "runs" / "20260516-100000-100-claude" / "AGENT_RUN_REPORT.md"
        report_path.write_text("# Agent Run Report\n\n## Risk Flags\n| HIGH | ... |\n", encoding="utf-8")
        result = self.buddy.read_latest_agentcam_report(str(repo))
        self.assertIsNotNone(result)
        self.assertIn("Risk Flags", result["content"])
        self.assertEqual(result["path"], str(report_path))
        self.assertGreater(result["mtime"], 0)

    def test_finds_report_from_subdirectory(self):
        """cwd inside a subdir of the repo still finds .git/agentcam/runs at root."""
        repo = self._make_fake_repo()
        report_path = repo / ".git" / "agentcam" / "runs" / "20260516-100000-100-claude" / "AGENT_RUN_REPORT.md"
        report_path.write_text("report", encoding="utf-8")
        subdir = repo / "src" / "auth"
        subdir.mkdir(parents=True)
        result = self.buddy.read_latest_agentcam_report(str(subdir))
        self.assertIsNotNone(result)
        self.assertEqual(result["path"], str(report_path))

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
        result = self.buddy.read_latest_agentcam_report(str(repo))
        self.assertEqual(result["path"], str(r2))
        self.assertEqual(result["content"], "second")

    def test_content_preserves_head_and_tail_with_read_cap(self):
        repo = self._make_fake_repo()
        report_path = repo / ".git" / "agentcam" / "runs" / "20260516-100000-100-claude" / "AGENT_RUN_REPORT.md"
        big = "HEAD_MARKER" + ("X" * (self.buddy.AGENTCAM_REPORT_READ_CHARS + 500)) + "TAIL_MARKER"
        report_path.write_text(big, encoding="utf-8")
        result = self.buddy.read_latest_agentcam_report(str(repo))
        self.assertLessEqual(len(result["content"]), self.buddy.AGENTCAM_REPORT_READ_CHARS)
        self.assertTrue(result["content"].startswith("HEAD_MARKER"))
        self.assertTrue(result["content"].endswith("TAIL_MARKER"))

    def test_state_roundtrip(self):
        sid = "test-session-xyz"
        self.assertEqual(self.buddy.load_agentcam_last_mtime(sid), 0.0)
        self.buddy.save_agentcam_last_mtime(sid, 1234567.89)
        self.assertAlmostEqual(self.buddy.load_agentcam_last_mtime(sid), 1234567.89, places=2)

    def test_state_handles_corrupt_file(self):
        sid = "test-corrupt"
        self.buddy.BUDDY_DIR.mkdir(parents=True, exist_ok=True)
        state_path = self.buddy.BUDDY_DIR / f"{sid}.agentcam.state.json"
        state_path.write_text("not json", encoding="utf-8")
        # Should return 0.0 silently, not raise
        self.assertEqual(self.buddy.load_agentcam_last_mtime(sid), 0.0)


if __name__ == "__main__":
    unittest.main()
