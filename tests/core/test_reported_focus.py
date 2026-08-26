"""Contract tests for main-agent-reported review focus."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import claude_prompt
import lens_router
import persona_config
from masters_nudge import codex_adapter


class ReportedFocusTests(unittest.TestCase):
    def test_reported_focus_selects_one_private_lens(self):
        with tempfile.TemporaryDirectory() as raw:
            route = lens_router.resolve_review_route(
                Path(raw),
                reported_focus="reliability",
            )

        self.assertEqual(route.stage, "reliability")
        self.assertEqual(route.effective_lens, "lamport")
        self.assertEqual(route.source, "main_model_report")

    def test_packet_words_do_not_change_the_reported_focus(self):
        with tempfile.TemporaryDirectory() as raw:
            route = lens_router.resolve_review_route(
                Path(raw),
                reported_focus="evolve",
            )

        self.assertEqual(route.effective_lens, "fowler")
        self.assertFalse(hasattr(lens_router, "LAMPORT_STRONG_RE"))
        self.assertFalse(hasattr(lens_router, "CARMACK_DIRECT_RE"))

    def test_explicit_stage_override_wins_over_main_model_report(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona_config.save_stage(root, "design")
            route = lens_router.resolve_review_route(
                root,
                reported_focus="performance",
            )

        self.assertEqual(route.stage, "design")
        self.assertEqual(route.effective_lens, "jeff")
        self.assertEqual(route.source, "config")

    def test_missing_report_uses_bounded_fallbacks_without_suppressing_review(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            midturn = lens_router.resolve_review_route(root)
            stopping = lens_router.resolve_review_route(root, stopping=True)

        self.assertEqual(
            (midturn.stage, midturn.effective_lens, midturn.source),
            ("build", "beck", "default_fallback"),
        )
        self.assertEqual(
            (stopping.stage, stopping.effective_lens, stopping.source),
            ("review", "linus", "stop_fallback"),
        )

    def test_hidden_marker_reports_focus_without_entering_visible_text(self):
        text = (
            "已完成重現，正在縮小失敗範圍。\n"
            "<!-- masters-nudge-focus:reliability -->"
        )

        self.assertEqual(persona_config.reported_focus(text), "reliability")
        self.assertEqual(
            persona_config.strip_focus_markers(text),
            "已完成重現，正在縮小失敗範圍。",
        )

    def test_prompt_instruction_only_requests_progress_reporting(self):
        instruction = persona_config.FOCUS_REPORT_INSTRUCTION

        self.assertIn("masters-nudge-focus", instruction)
        self.assertIn("hooks decide when reviews run", instruction)
        self.assertNotIn("call the reviewer", instruction.lower())
        self.assertLessEqual(len(instruction), 256)

    def test_codex_reader_uses_latest_current_turn_assistant_report(self):
        with tempfile.TemporaryDirectory() as raw:
            transcript = Path(raw) / "rollout.jsonl"
            transcript.write_text(
                json.dumps(
                    {
                        "type": "event_msg",
                        "payload": {
                            "type": "agent_message",
                            "message": "先前進度 <!-- masters-nudge-focus:build -->",
                        },
                    }
                )
                + "\n"
                + json.dumps(
                    {
                        "type": "event_msg",
                        "payload": {
                            "type": "agent_message",
                            "message": (
                                "正在驗證亂序狀態 "
                                "<!-- masters-nudge-focus:reliability -->"
                            ),
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            latest = codex_adapter._latest_assistant_text(str(transcript))

        self.assertEqual(persona_config.reported_focus(latest), "reliability")

    def test_claude_prompt_hook_parses_input_and_injects_only_report_contract(self):
        payload = {"session_id": "s", "prompt": "修正登入問題"}
        with mock.patch.object(
            claude_prompt.sys,
            "stdin",
            io.StringIO(json.dumps(payload)),
        ):
            parsed = claude_prompt.read_hook_input()

        output = claude_prompt.build_hook_output()
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(parsed, payload)
        self.assertIn("masters-nudge-focus:build", context)
        self.assertNotIn("Provider", context)


if __name__ == "__main__":
    unittest.main()
