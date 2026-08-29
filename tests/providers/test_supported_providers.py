"""Small transport tests for the three providers the product supports."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from masters_nudge import local_ollama, providers


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "nudge-schema.json"


class SupportedProviderTests(unittest.TestCase):
    def test_grok_transport_is_not_part_of_the_runtime(self):
        self.assertFalse(hasattr(providers, "call_grok_result"))
        self.assertNotIn('provider == "grok"', Path(providers.__file__).read_text(encoding="utf-8"))

    def test_anthropic_receives_the_evidence_packet_unchanged(self):
        completed = subprocess.CompletedProcess(
            ["claude"],
            0,
            '{"structured_output":{"status":"no_finding","lens":"none","finding":""}}',
            "",
        )
        with mock.patch.object(
            providers, "_run_cli_process", return_value=completed
        ) as run:
            providers.call_claude_result(
                "system",
                "COMMAND-AND-RESULT-Q7K9",
                "opus",
                schema_path=SCHEMA,
                timeout_sec=12,
            )

        argv = run.call_args.args[0]
        self.assertEqual(argv[argv.index("-p") + 1], "COMMAND-AND-RESULT-Q7K9")

    def test_openai_receives_system_prompt_and_evidence_once(self):
        completed = subprocess.CompletedProcess(["codex"], 0, "", "")

        def run(*args, **_kwargs):
            argv = args[0]
            Path(argv[argv.index("-o") + 1]).write_text(
                '{"status":"no_finding","lens":"none","finding":""}',
                encoding="utf-8",
            )
            return completed

        with mock.patch.object(providers, "_run_cli_process", side_effect=run) as call:
            providers.call_codex_result(
                "SYSTEM-Q7K9",
                "COMMAND-AND-RESULT-Q7K9",
                "gpt-test",
                schema_path=SCHEMA,
                timeout_sec=12,
                codex_bin_resolver=lambda: "codex",
            )

        supplied = call.call_args.kwargs["input_text"]
        self.assertEqual(supplied.count("SYSTEM-Q7K9"), 1)
        self.assertEqual(supplied.count("COMMAND-AND-RESULT-Q7K9"), 1)

    def test_dispatch_supports_ollama_under_its_public_name(self):
        expected = {
            "status": "no_finding",
            "lens": "none",
            "finding": "",
        }
        with mock.patch.object(
            providers, "call_local_ollama_result", return_value=expected
        ) as local:
            actual = providers.dispatch_call_result(
                "ollama",
                "system",
                "packet",
                "qwen3",
                schema_path=SCHEMA,
                timeout_sec=12,
            )

        self.assertEqual(actual, expected)
        local.assert_called_once()

    def test_ollama_rejects_a_non_loopback_endpoint(self):
        for url in ("https://example.com", "http://192.168.1.50:11434"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                local_ollama.normalize_loopback_url(url)

    def test_ollama_sends_the_packet_only_to_the_checked_local_endpoint(self):
        response = {
            "done": True,
            "message": {
                "content": '{"status":"no_finding","lens":"none","finding":""}'
            },
        }
        with (
            mock.patch.object(
                local_ollama,
                "inspect_local_ollama",
                return_value={
                    "ready": True,
                    "endpoint": "http://127.0.0.1:11434",
                    "error": "",
                },
            ),
            mock.patch.object(
                local_ollama, "_request_json", return_value=response
            ) as request,
        ):
            result = local_ollama.call_local_ollama_result(
                "SYSTEM",
                "COMMAND-AND-RESULT-Q7K9",
                "qwen3",
                schema_path=SCHEMA,
                timeout_sec=12,
                parse_result=lambda _raw: {
                    "status": "no_finding",
                    "lens": "none",
                    "finding": "",
                },
            )

        self.assertEqual(result["status"], "no_finding")
        self.assertEqual(request.call_args.args[0], "http://127.0.0.1:11434")
        payload = request.call_args.kwargs["payload"]
        self.assertEqual(payload["messages"][1]["content"], "COMMAND-AND-RESULT-Q7K9")
        self.assertFalse(payload["stream"])
        self.assertFalse(payload["think"])

    def test_cli_timeout_terminates_the_process_tree(self):
        process = mock.Mock(pid=4321)
        process.communicate.side_effect = subprocess.TimeoutExpired(
            cmd=["provider"], timeout=12
        )
        with (
            mock.patch.object(providers.subprocess, "Popen", return_value=process),
            mock.patch.object(
                providers,
                "_terminate_process_tree",
                return_value=("partial output", "backend retry"),
            ) as terminate,
        ):
            with self.assertRaises(subprocess.TimeoutExpired):
                providers._run_cli_process(
                    ["provider"],
                    input_text="packet",
                    environment={},
                    timeout_sec=12,
                )

        terminate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
