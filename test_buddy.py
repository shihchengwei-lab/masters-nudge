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

    def test_read_recent_transcript_uses_cinder_format(self):
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
            # No tool_result in fixture, so no tool output block
            self.assertNotIn("[tool output]", result)
        finally:
            os.unlink(path)

    def test_read_recent_transcript_caps_at_12_messages(self):
        entries = [
            {"type": "user", "message": {"role": "user", "content": f"msg-{i:02d}"}}
            for i in range(20)
        ]
        path = self._write_jsonl(entries)
        try:
            result = self.buddy.read_recent_transcript(path)
            # Last 12: msg-08 through msg-19
            self.assertNotIn("msg-07", result)
            self.assertIn("msg-08", result)
            self.assertIn("msg-19", result)
            # Exactly 12 lines (no tool output present)
            self.assertEqual(len(result.splitlines()), 12)
        finally:
            os.unlink(path)

    def test_read_recent_transcript_per_message_head_cap_300(self):
        long_text = "A" * 500
        entries = [{"type": "user", "message": {"role": "user", "content": long_text}}]
        path = self._write_jsonl(entries)
        try:
            result = self.buddy.read_recent_transcript(path)
            # Keeps the FIRST 300 (head-bias), drops the rest
            self.assertEqual(result, "user: " + ("A" * 300))
        finally:
            os.unlink(path)

    def test_read_recent_transcript_tool_output_concatenated(self):
        # Two separate tool_results inside the 12-message window.
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
            self.assertIn("[tool output]", result)
            self.assertIn("AAA", result)
            self.assertIn("BBB", result)
            # Tool output block goes last
            self.assertTrue(result.rstrip().endswith("BBB"))
        finally:
            os.unlink(path)

    def test_read_recent_transcript_tool_output_tail_1000(self):
        head = "HEAD_MARKER"
        tail = "TAIL_MARKER"
        long = head + ("x" * 1500) + tail   # 1521 chars total
        entries = [{"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "content": long},
        ]}}]
        path = self._write_jsonl(entries)
        try:
            result = self.buddy.read_recent_transcript(path)
            # Tail-truncation keeps the end, drops the head
            self.assertIn(tail, result)
            self.assertNotIn(head, result)
            # The tool output payload itself is at most 1000 chars
            payload = result.split("[tool output]\n", 1)[1]
            self.assertLessEqual(len(payload), 1000)
        finally:
            os.unlink(path)

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
            # tool_result content still surfaces
            self.assertIn("[tool output]", result)
            self.assertIn("TOOL_DATA", result)
        finally:
            os.unlink(path)

    def test_read_recent_transcript_missing_file(self):
        result = self.buddy.read_recent_transcript("/nonexistent/path.jsonl")
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



# ── 6. agentcam report integration ───────────────────────────────────

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

    def test_content_is_tail_truncated(self):
        repo = self._make_fake_repo()
        report_path = repo / ".git" / "agentcam" / "runs" / "20260516-100000-100-claude" / "AGENT_RUN_REPORT.md"
        # Make a report longer than AGENTCAM_REPORT_TAIL_CHARS
        big = "X" * (self.buddy.AGENTCAM_REPORT_TAIL_CHARS + 500) + "TAIL_MARKER"
        report_path.write_text(big, encoding="utf-8")
        result = self.buddy.read_latest_agentcam_report(str(repo))
        self.assertEqual(len(result["content"]), self.buddy.AGENTCAM_REPORT_TAIL_CHARS)
        # Tail should be preserved (truncation is from the front)
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
