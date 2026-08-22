import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from evaluation.shader_prompt_replay import replay


LATENCY_FIXTURES = (
    Path(__file__).resolve().parent
    / "tests"
    / "fixtures"
    / "shader"
    / "prompt-replay-latency-v1"
)


class ShaderPromptReplayTests(unittest.TestCase):
    def test_text_sha256_is_stable_across_platform_line_endings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lf_path = Path(temp_dir) / "lf.json"
            crlf_path = Path(temp_dir) / "crlf.json"
            lf_path.write_bytes(b'{"value": 1}\n')
            crlf_path.write_bytes(b'{"value": 1}\r\n')

            self.assertEqual(
                replay.sha256_text_file(lf_path),
                replay.sha256_text_file(crlf_path),
            )

    def test_fixture_builds_one_checkpoint_packet_with_six_expectations(self):
        fixture = replay.load_fixture()
        packet = replay.build_packet(fixture)

        self.assertEqual("checkpoint", fixture["event_type"])
        self.assertEqual(set(replay.LENSES), set(fixture["lens_expectations"]))
        self.assertIn("[task anchor]", packet)
        self.assertIn("[current bottleneck model]", packet)
        self.assertIn("[unresolved contradiction]", packet)

    def test_three_repeats_create_eighteen_same_packet_jobs(self):
        fixture = replay.load_fixture()
        jobs = replay.build_jobs(fixture, repeats=3, seed=20260817)

        self.assertEqual(18, len(jobs))
        self.assertEqual(1, len({job["packet_sha256"] for job in jobs}))
        self.assertEqual(6, len({job["system_prompt"] for job in jobs}))
        self.assertEqual(
            {lens: 3 for lens in replay.LENSES},
            {
                lens: sum(job["lens"] == lens for job in jobs)
                for lens in replay.LENSES
            },
        )

    def test_focused_rerun_preserves_original_job_order_for_selected_lenses(self):
        fixture = replay.load_fixture()
        all_jobs = replay.build_jobs(fixture, repeats=3, seed=20260817)
        focused = replay.build_jobs(
            fixture,
            repeats=3,
            seed=20260817,
            lenses=("karis", "quilez"),
        )

        self.assertEqual(
            [
                job["job_id"]
                for job in all_jobs
                if job["lens"] in {"karis", "quilez"}
            ],
            [job["job_id"] for job in focused],
        )
        self.assertEqual(6, len(focused))

    def test_focused_analysis_uses_six_row_integrity_gate(self):
        fixture = replay.load_fixture()
        rows = []
        for lens in ("karis", "quilez"):
            for repeat in range(1, 4):
                rows.append(
                    replay.score_row(
                        lens=lens,
                        repeat=repeat,
                        result={"status": "finding", "finding": f"{lens} 的成本關係仍未被命名。"},
                        latency_ms=10,
                    )
                )

        analysis = replay.analyze(
            fixture,
            rows,
            lenses=("karis", "quilez"),
        )

        self.assertEqual(6, analysis["rows"])
        self.assertTrue(analysis["gates"]["integrity"])

    def test_job_scores_the_raw_finding_before_production_sanitation(self):
        fixture = replay.load_fixture()
        job = replay.build_jobs(fixture, repeats=1, seed=1)[0]
        raw_finding = "先重跑移動鏡頭，再確認畫面是否穩定"

        with mock.patch.object(
            replay,
            "call_grok",
            return_value={
                "status": "finding",
                "finding": raw_finding,
                "raw_output": "RAW",
                "usage": {},
            },
        ):
            row = replay.run_job(job, timeout_sec=90)

        self.assertEqual(raw_finding, row["raw_finding"])
        self.assertNotEqual("", row["production_finding"])
        self.assertTrue(row["imperative_flags"])
        self.assertEqual("RAW", row["raw_output"])

    def test_claude_job_uses_subscription_cli_and_records_latency(self):
        fixture = replay.load_fixture()
        job = replay.build_jobs(
            fixture,
            repeats=1,
            seed=1,
            lenses=("karis",),
        )[0]

        with (
            mock.patch.object(
                replay,
                "call_claude",
                return_value={
                    "status": "finding",
                    "finding": "材質契約仍有一段沒有被目前證據覆蓋。",
                    "raw_output": "RAW",
                    "usage": {},
                },
            ) as call_claude,
            mock.patch.object(replay, "call_grok") as call_grok,
        ):
            row = replay.run_job(job, timeout_sec=90, provider="claude")

        call_claude.assert_called_once_with(
            job["system_prompt"], job["packet"], 90
        )
        call_grok.assert_not_called()
        self.assertEqual("finding", row["status"])
        self.assertIsInstance(row["latency_ms"], int)
        self.assertGreaterEqual(row["latency_ms"], 0)

    def test_codex_job_uses_gpt_5_6_sol_and_records_latency(self):
        fixture = replay.load_fixture()
        job = replay.build_jobs(
            fixture,
            repeats=1,
            seed=1,
            lenses=("karis",),
        )[0]

        with (
            mock.patch.object(
                replay,
                "call_codex",
                return_value={
                    "status": "finding",
                    "finding": "完整管線仍有一段材質語意未被目前證據覆蓋。",
                    "raw_output": "RAW",
                    "usage": {},
                },
            ) as call_codex,
            mock.patch.object(replay, "call_grok") as call_grok,
            mock.patch.object(replay, "call_claude") as call_claude,
        ):
            row = replay.run_job(job, timeout_sec=90, provider="codex")

        call_codex.assert_called_once_with(
            job["system_prompt"], job["packet"], 90
        )
        call_grok.assert_not_called()
        call_claude.assert_not_called()
        self.assertEqual("finding", row["status"])
        self.assertIsInstance(row["latency_ms"], int)
        self.assertGreaterEqual(row["latency_ms"], 0)

    def test_unknown_provider_is_rejected_before_a_call(self):
        fixture = replay.load_fixture()
        job = replay.build_jobs(fixture, repeats=1, seed=1)[0]

        with self.assertRaisesRegex(ValueError, "unsupported replay provider"):
            replay.run_job(job, timeout_sec=90, provider="unknown")

    def test_grok_replay_forwards_explicit_reasoning_effort(self):
        fixture = replay.load_fixture()
        job = replay.build_jobs(
            fixture,
            repeats=1,
            seed=1,
            lenses=("quilez",),
        )[0]

        with mock.patch.object(
            replay,
            "call_grok",
            return_value={"status": "no_finding", "finding": ""},
        ) as call_grok:
            replay.run_job(
                job,
                timeout_sec=90,
                provider="grok",
                reasoning_effort="medium",
            )

        call_grok.assert_called_once_with(
            job["system_prompt"],
            job["packet"],
            90,
            reasoning_effort="medium",
        )

    def test_analysis_separates_timeout_from_prompt_quality_denominator(self):
        fixture = replay.load_fixture()
        rows = []
        for lens in replay.LENSES:
            rows.extend(
                [
                    replay.score_row(
                        lens=lens,
                        repeat=1,
                        result={"status": "finding", "finding": "成本沒有消失，只轉入另一條執行路徑。"},
                        latency_ms=10,
                    ),
                    replay.score_row(
                        lens=lens,
                        repeat=2,
                        result={"status": "error", "error_kind": "timeout"},
                        latency_ms=90000,
                    ),
                    replay.score_row(
                        lens=lens,
                        repeat=3,
                        result={"status": "finding", "finding": "先量測再決定。"},
                        latency_ms=11,
                    ),
                ]
            )

        analysis = replay.analyze(fixture, rows)

        self.assertEqual(18, analysis["rows"])
        self.assertEqual(6, analysis["timeouts"])
        self.assertEqual(12, analysis["prompt_quality_denominator"])
        self.assertEqual(0.5, analysis["rates"]["non_imperative"])
        self.assertEqual("nearest-rank", analysis["latency_ms"]["method"])
        self.assertEqual(18, analysis["latency_ms"]["attempts"]["samples"])
        self.assertEqual(90000, analysis["latency_ms"]["attempts"]["p95"])
        self.assertEqual(12, analysis["latency_ms"]["successful"]["samples"])
        self.assertEqual(11, analysis["latency_ms"]["successful"]["p95"])
        for lens in replay.LENSES:
            self.assertEqual(
                90000,
                analysis["by_lens"][lens]["latency_ms"]["attempts"]["p95"],
            )
            self.assertEqual(
                11,
                analysis["by_lens"][lens]["latency_ms"]["successful"]["p95"],
            )

    def test_latency_summary_keeps_timeout_attempts_but_excludes_them_from_success(self):
        rows = [
            {"status": "finding", "error_kind": "", "latency_ms": 100},
            {"status": "no_finding", "error_kind": "", "latency_ms": 200},
            {"status": "error", "error_kind": "schema", "latency_ms": 300},
            {"status": "error", "error_kind": "timeout", "latency_ms": 90000},
        ]

        summary = replay.latency_summary(rows)

        self.assertEqual(
            {
                "method": "nearest-rank",
                "attempts": {"samples": 4, "p95": 90000},
                "successful": {"samples": 2, "p95": 200},
            },
            summary,
        )

    def test_grok_medium_latency_artifact_matches_frozen_runs(self):
        runs_path = LATENCY_FIXTURES / "runs.json"
        rows = json.loads(runs_path.read_text(encoding="utf-8"))["runs"]
        artifact = json.loads(
            (LATENCY_FIXTURES / "latency-analysis.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(
            replay.sha256_text_file(runs_path),
            artifact["source_sha256"],
        )
        self.assertEqual(replay.latency_summary(rows), {
            "method": artifact["method"],
            "attempts": artifact["overall"]["attempts"],
            "successful": artifact["overall"]["successful"],
        })
        for lens in replay.LENSES:
            lens_rows = [row for row in rows if row["lens"] == lens]
            expected = replay.latency_summary(lens_rows)
            self.assertEqual(expected["attempts"], artifact["by_lens"][lens]["attempts"])
            self.assertEqual(
                expected["successful"],
                artifact["by_lens"][lens]["successful"],
            )


if __name__ == "__main__":
    unittest.main()
