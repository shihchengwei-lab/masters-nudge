"""Transport tests for the supported read-only judgment providers."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from masters_nudge import local_ollama, providers


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "nudge-schema.json"
PASS_JSON = json.dumps(
    {
        "decision": "pass",
        "current_choice": "",
        "structural_cost": "",
        "direction": "",
        "evidence": [],
    }
)


class SupportedProviderTests(unittest.TestCase):
    def test_anthropic_receives_snapshot_unchanged(self):
        completed = subprocess.CompletedProcess(
            ["claude"], 0, json.dumps({"structured_output": json.loads(PASS_JSON)}), ""
        )
        with mock.patch.object(providers, "_run_cli_process", return_value=completed) as run:
            result = providers.call_claude_result(
                "system", "WORKSPACE-SNAPSHOT", "opus", schema_path=SCHEMA, timeout_sec=12
            )
        argv = run.call_args.args[0]
        self.assertEqual(argv[argv.index("-p") + 1], "WORKSPACE-SNAPSHOT")
        self.assertEqual(result["decision"], "pass")

    def test_openai_receives_prompt_once_and_uses_workspace_cwd(self):
        def run(_command, **kwargs):
            Path(_command[_command.index("-o") + 1]).write_text(PASS_JSON, encoding="utf-8")
            return subprocess.CompletedProcess(["codex"], 0, "", "")

        with mock.patch.object(providers, "_run_cli_process", side_effect=run) as call:
            result = providers.call_codex_result(
                "SYSTEM-Q7K9",
                "WORKSPACE-Q7K9",
                "gpt-test",
                schema_path=SCHEMA,
                timeout_sec=12,
                workspace_root=str(ROOT),
                codex_bin_resolver=lambda: "codex",
            )
        supplied = call.call_args.kwargs["input_text"]
        self.assertEqual(supplied.count("SYSTEM-Q7K9"), 1)
        self.assertEqual(supplied.count("WORKSPACE-Q7K9"), 1)
        self.assertEqual(call.call_args.kwargs["cwd"], str(ROOT))
        self.assertEqual(result["decision"], "pass")

    def test_dispatch_supports_ollama(self):
        expected = json.loads(PASS_JSON)
        with mock.patch.object(
            providers, "call_local_ollama_result", return_value=expected
        ) as local:
            actual = providers.dispatch_call_result(
                "ollama", "system", "snapshot", "qwen3", schema_path=SCHEMA, timeout_sec=12
            )
        self.assertEqual(actual, expected)
        local.assert_called_once()

    def test_ollama_rejects_non_loopback_endpoint(self):
        for url in ("https://example.com", "http://192.168.1.50:11434"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                local_ollama.normalize_loopback_url(url)

    def test_ollama_sends_snapshot_to_checked_local_endpoint(self):
        response = {"done": True, "message": {"content": PASS_JSON}}
        with (
            mock.patch.object(
                local_ollama,
                "inspect_local_ollama",
                return_value={"ready": True, "endpoint": "http://127.0.0.1:11434", "error": ""},
            ),
            mock.patch.object(local_ollama, "_request_json", return_value=response) as request,
        ):
            result = local_ollama.call_local_ollama_result(
                "SYSTEM",
                "WORKSPACE-SNAPSHOT",
                "qwen3",
                schema_path=SCHEMA,
                timeout_sec=12,
            )
        self.assertEqual(result["decision"], "pass")
        self.assertEqual(request.call_args.args[0], "http://127.0.0.1:11434")
        self.assertEqual(request.call_args.kwargs["payload"]["messages"][1]["content"], "WORKSPACE-SNAPSHOT")

    def test_cli_timeout_terminates_process_tree(self):
        process = mock.Mock(pid=4321)
        process.communicate.side_effect = subprocess.TimeoutExpired(cmd=["provider"], timeout=12)
        with (
            mock.patch.object(providers.subprocess, "Popen", return_value=process),
            mock.patch.object(
                providers, "_terminate_process_tree", return_value=("partial", "retry")
            ) as terminate,
        ):
            with self.assertRaises(subprocess.TimeoutExpired):
                providers._run_cli_process(
                    ["provider"], input_text="snapshot", environment={}, timeout_sec=12
                )
        terminate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
