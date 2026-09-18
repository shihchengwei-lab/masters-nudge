import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from masters_nudge import providers
from masters_nudge.contracts import ToolFault

ROOT = Path(__file__).resolve().parents[2]


class TransportTests(unittest.TestCase):
    def call(self):
        return providers.call_codex_result("SYSTEM-unique", "PACKET-unique", "model",
                   schema_path=ROOT / "nudge-schema.json", timeout_sec=5, workspace_root=str(ROOT),
                   remaining_chars=1500, codex_bin_resolver=lambda: "codex")

    def fake_process(self, command, **kwargs):
        output = Path(command[command.index("-o") + 1])
        output.write_text('{"feedback":null}', encoding="utf-8")
        args = json.loads(next(part.split("=", 1)[1] for part in command if part.startswith("mcp_servers.readrepo.args=")))
        Path(args[args.index("--audit") + 1]).write_text(json.dumps({"name": "initialize", "text": "", "fault": ""}) + "\n")
        return subprocess.CompletedProcess(command, 0, '{"type":"turn.completed","usage":{"input_tokens":123}}\n', "")

    def test_one_prompt_and_only_repository_tools(self):
        with mock.patch.object(providers, "_run_cli_process", side_effect=self.fake_process) as process:
            result = self.call()
        args = process.call_args.args[0]
        self.assertIn("--ignore-user-config", args)
        self.assertIn("features.shell_tool=false", args)
        self.assertIn("features.view_image=false", args)
        self.assertIn("features.plugins=false", args)
        self.assertIn("mcp_servers.readrepo.required=true", args)
        self.assertIn('mcp_servers.readrepo.enabled_tools=["search_repo","read_file"]', args)
        self.assertIn("read-only", args)
        self.assertEqual(process.call_args.kwargs["input_text"].count("SYSTEM-unique"), 1)
        self.assertEqual(process.call_args.kwargs["input_text"].count("PACKET-unique"), 1)
        self.assertEqual(result.usage["input_tokens"], 123)

    def test_mcp_process_explicitly_uses_utf8(self):
        with mock.patch.object(providers, "_run_cli_process", side_effect=self.fake_process) as process:
            self.call()
        self.assertIn('mcp_servers.readrepo.env={PYTHONIOENCODING="utf-8"}', process.call_args.args[0])

    def test_successful_null_without_mcp_startup_is_a_fault(self):
        def process(command, **kwargs):
            Path(command[command.index("-o") + 1]).write_text('{"feedback":null}')
            return subprocess.CompletedProcess(command, 0, "", "MCP failed")
        with mock.patch.object(providers, "_run_cli_process", side_effect=process), self.assertRaises(ToolFault) as fault:
            self.call()
        self.assertEqual(fault.exception.kind, "mcp_startup")

    def test_mcp_material_and_failures_survive_provider_transport(self):
        from masters_nudge.contracts import MaterialLine, json_text
        line = {"source": "current_structure", "path": "src/狀態.py", "line": 2,
                "text": '狀態 = "完成"'}
        cases = (
            (json_text({"lines": [line], "truncated": False}), "", None),
            (json_text({"error": "read denied"}), "read denied", "mcp"),
            ("x" * 1501, "", "mcp_budget"),
        )
        for text, fault, expected_fault in cases:
            with self.subTest(expected_fault=expected_fault):
                def process(command, **kwargs):
                    result = self.fake_process(command, **kwargs)
                    args = json.loads(next(part.split("=", 1)[1] for part in command
                                           if part.startswith("mcp_servers.readrepo.args=")))
                    audit = Path(args[args.index("--audit") + 1])
                    with audit.open("a", encoding="utf-8") as stream:
                        stream.write(json_text({"name": "read_file", "arguments": {"path": line["path"]},
                                                "text": text, "fault": fault}) + "\n")
                    return result  # Provider still returned feedback:null.
                with mock.patch.object(providers, "_run_cli_process", side_effect=process):
                    if expected_fault:
                        with self.assertRaises(ToolFault) as caught:
                            self.call()
                        self.assertEqual(caught.exception.kind, expected_fault)
                    else:
                        result = self.call()
                        self.assertEqual(result.materials, (MaterialLine(**line),))
                        self.assertEqual(result.trace[-1]["text"], text)

    def test_nonzero_and_timeout_never_recover_a_successful_looking_null(self):
        for problem in (subprocess.CompletedProcess([], 1, '{"feedback":null}', "failed"),
                        subprocess.TimeoutExpired("codex", 5, output='{"feedback":null}')):
            with self.subTest(problem=problem):
                behavior = {"side_effect": problem} if isinstance(problem, Exception) else {"return_value": problem}
                with mock.patch.object(providers, "_run_cli_process", **behavior), self.assertRaises(ToolFault):
                    self.call()

    def test_timeout_terminates_provider_process_tree(self):
        process = mock.Mock(pid=4321)
        process.communicate.side_effect = subprocess.TimeoutExpired("provider", 1)
        with mock.patch.object(providers.subprocess, "Popen", return_value=process), \
             mock.patch.object(providers, "_terminate_process_tree", return_value=("partial", "")) as terminate:
            with self.assertRaises(subprocess.TimeoutExpired):
                providers._run_cli_process(["provider"], input_text="data", environment={}, timeout_sec=1)
        terminate.assert_called_once_with(process, log_error=providers._noop)

    def test_real_stdio_mcp_initializes_reads_and_records(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "source.txt").write_text("single source\n", encoding="utf-8")
            audit = root / "audit.jsonl"
            messages = [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "read_file", "arguments": {"path": "source.txt"}}},
            ]
            result = subprocess.run([os.sys.executable, str(ROOT / "masters_nudge/read_only_repo_mcp.py"),
                                     "--root", str(root), "--budget", "1000", "--audit", str(audit)],
                                     input="\n".join(json.dumps(message) for message in messages) + "\n",
                                     text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            replies = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertEqual({tool["name"] for tool in replies[1]["result"]["tools"]}, {"search_repo", "read_file"})
            self.assertIn("single source", replies[2]["result"]["content"][0]["text"])
            self.assertEqual(len(audit.read_text().splitlines()), 2)
