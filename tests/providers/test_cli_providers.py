from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest import mock

from masters_nudge import providers


HERE = Path(__file__).resolve().parents[2]
SCHEMA = HERE / "reaction-schema.json"


class ReviewerProcessTests(unittest.TestCase):
    def test_cleanup_does_not_skip_descendants_when_parent_just_exited(self):
        process = mock.Mock(pid=4321)
        process.poll.return_value = 1
        process.communicate.return_value = ("", "")

        with (
            mock.patch.object(providers.os, "name", "nt"),
            mock.patch.object(providers.subprocess, "run") as run,
        ):
            providers._terminate_process_tree(process)

        run.assert_called_once()

    def test_timeout_terminates_the_process_tree_for_every_cli(self):
        process = mock.Mock(pid=4321)
        process.communicate.side_effect = subprocess.TimeoutExpired(
            cmd=["reviewer"], timeout=12
        )

        with (
            mock.patch.object(providers.subprocess, "Popen", return_value=process),
            mock.patch.object(providers, "_terminate_process_tree") as terminate,
        ):
            with self.assertRaises(subprocess.TimeoutExpired):
                providers._run_cli_process(
                    ["reviewer"],
                    input_text="packet",
                    environment={},
                    timeout_sec=12,
                )

        terminate.assert_called_once_with(process, log_error=providers._noop)

    def test_posix_cli_starts_an_isolated_process_group(self):
        process = mock.Mock(returncode=0)
        process.communicate.return_value = ("out", "err")

        with (
            mock.patch.object(providers.os, "name", "posix"),
            mock.patch.object(providers.subprocess, "Popen", return_value=process) as popen,
        ):
            providers._run_cli_process(
                ["reviewer"],
                input_text="packet",
                environment={},
                timeout_sec=12,
            )

        self.assertTrue(popen.call_args.kwargs["start_new_session"])


class ProviderErrorContractTests(unittest.TestCase):
    def test_claude_places_evidence_in_the_positional_prompt(self):
        completed = subprocess.CompletedProcess(
            ["claude"],
            0,
            '{"structured_output":{"status":"no_finding","finding":""}}',
            "",
        )
        with mock.patch.object(
            providers, "_run_cli_process", return_value=completed
        ) as run:
            providers.call_claude_result(
                "system",
                "EVIDENCE-Q7K9",
                "opus",
                schema_path=SCHEMA,
                timeout_sec=12,
            )

        argv = run.call_args.args[0]
        prompt = argv[argv.index("-p") + 1]
        self.assertIn("EVIDENCE-Q7K9", prompt)
        self.assertIsNone(run.call_args.kwargs["input_text"])

    def test_claude_nonzero_and_invalid_output_are_distinct(self):
        with mock.patch.object(
            providers,
            "_run_cli_process",
            return_value=subprocess.CompletedProcess(
                ["claude"], 2, "", "bad command"
            ),
        ):
            nonzero = providers.call_claude_result(
                "system",
                "packet",
                "opus",
                schema_path=SCHEMA,
                timeout_sec=12,
            )
        self.assertEqual(nonzero["error_kind"], "nonzero_exit")

        with mock.patch.object(
            providers,
            "_run_cli_process",
            return_value=subprocess.CompletedProcess(["claude"], 0, "not json", ""),
        ):
            invalid = providers.call_claude_result(
                "system",
                "packet",
                "opus",
                schema_path=SCHEMA,
                timeout_sec=12,
            )
        self.assertEqual(invalid["error_kind"], "invalid_output")

    def test_codex_timeout_and_not_found_are_machine_readable(self):
        with mock.patch.object(
            providers,
            "_run_cli_process",
            side_effect=subprocess.TimeoutExpired(cmd=["codex"], timeout=12),
        ):
            timed_out = providers.call_codex_result(
                "system",
                "packet",
                "model",
                schema_path=SCHEMA,
                timeout_sec=12,
                codex_bin_resolver=lambda: "codex",
            )
        self.assertEqual(timed_out["error_kind"], "timeout")

        missing = providers.call_codex_result(
            "system",
            "packet",
            "model",
            schema_path=SCHEMA,
            timeout_sec=12,
            codex_bin_resolver=lambda: None,
        )
        self.assertEqual(missing["error_kind"], "not_found")

    def test_grok_nonzero_without_valid_payload_is_classified(self):
        completed = subprocess.CompletedProcess(["grok"], 1, "not json", "failed")
        with mock.patch.object(providers, "_run_cli_process", return_value=completed):
            result = providers.call_grok_result(
                "system",
                "packet",
                "model",
                schema_path=SCHEMA,
                timeout_sec=12,
                grok_bin_resolver=lambda: "grok",
            )
        self.assertEqual(result["error_kind"], "nonzero_exit")


if __name__ == "__main__":
    unittest.main()
