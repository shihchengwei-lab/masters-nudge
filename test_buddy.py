#!/usr/bin/env python3
"""Smoke tests for Buddy_similar.

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


# ── 2. Transcript parser ─────────────────────────────────────────────

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

    def test_format_user_entry(self):
        result = self.buddy.format_transcript_entry(FIXTURE_LINES[0])
        self.assertEqual(result, "[user]\n幫我修 bug")

    def test_format_assistant_with_blocks(self):
        result = self.buddy.format_transcript_entry(FIXTURE_LINES[1])
        self.assertIn("[tool_use: Read]", result)
        self.assertIn("我來看看程式碼", result)

    def test_format_system_ignored(self):
        result = self.buddy.format_transcript_entry(FIXTURE_LINES[2])
        self.assertEqual(result, "")

    def test_format_truncates_long_content(self):
        long_entry = {
            "type": "user",
            "message": {"role": "user", "content": "x" * 2000},
        }
        result = self.buddy.format_transcript_entry(long_entry)
        self.assertIn("...[truncated]", result)
        # The text portion should be capped at 1500 + truncation marker
        text_part = result.split("\n", 1)[1]
        self.assertLessEqual(len(text_part), 1520)

    def test_read_recent_transcript_from_fixture(self):
        fd = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        for line in FIXTURE_LINES:
            fd.write(json.dumps(line, ensure_ascii=False) + "\n")
        fd.close()
        try:
            result = self.buddy.read_recent_transcript(fd.name, 5000)
            self.assertIn("幫我修 bug", result)
            self.assertIn("修好了", result)
            # system entry should be absent
            self.assertNotIn("ignored", result)
        finally:
            os.unlink(fd.name)

    def test_read_recent_transcript_respects_char_budget(self):
        fd = tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        for i in range(50):
            line = {"type": "user", "message": {"role": "user", "content": f"msg {i} " + "a" * 100}}
            fd.write(json.dumps(line, ensure_ascii=False) + "\n")
        fd.close()
        try:
            result = self.buddy.read_recent_transcript(fd.name, 500)
            self.assertLessEqual(len(result), 600)  # some overhead from joining
        finally:
            os.unlink(fd.name)

    def test_read_recent_transcript_missing_file(self):
        result = self.buddy.read_recent_transcript("/nonexistent/path.jsonl", 5000)
        self.assertEqual(result, "")


# ── 3. Sanitizer ─────────────────────────────────────────────────────

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

    def test_hard_truncate(self):
        import buddy
        raw = "字" * 200
        result = self.sanitize(raw)
        self.assertLessEqual(len(result), buddy.MAX_REACTION_CHARS)

    def test_empty_input(self):
        self.assertEqual(self.sanitize(""), "")
        self.assertEqual(self.sanitize("   "), "")

    def test_collapses_whitespace(self):
        result = self.sanitize("多個   空格\n換行\t跳格")
        self.assertNotIn("\n", result)
        self.assertNotIn("\t", result)
        self.assertNotIn("  ", result)


# ── 4. Mock CLI calls ────────────────────────────────────────────────

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
        original_run = mock_run.side_effect

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


# ── 5. Inject.py state pointer ───────────────────────────────────────

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



if __name__ == "__main__":
    unittest.main()
