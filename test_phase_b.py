import json
import tempfile
import unittest
from pathlib import Path

from evaluation import quality_eval
from evaluation.phase_b import phase_b_analyze
from evaluation.phase_b import phase_b_run
from evaluation.phase_b import phase_b_tasks


HERE = Path(__file__).resolve().parent
TREATMENTS = (
    HERE
    / "evaluation"
    / "results"
    / "phase-b-impact-v1-20260813"
    / "treatments-final.json"
)


class PhaseBTests(unittest.TestCase):
    def test_task_set_has_six_balanced_lenses_and_routes(self):
        spec = phase_b_tasks.load_spec()
        phase_b_tasks.validate_assets(spec)
        fixtures = spec["fixtures"]
        self.assertEqual(6, len(fixtures))
        self.assertEqual(
            {"jeff", "beck", "fowler", "linus", "lamport", "carmack"},
            {fixture["lens"] for fixture in fixtures},
        )
        for fixture in fixtures:
            routed = {**fixture, "expected_effective_lens": fixture["lens"]}
            packet = quality_eval.build_packet(routed)
            route = quality_eval.fixture_routes(routed, packet)["effective"]
            self.assertEqual(fixture["lens"], route.effective_lens)

    def test_final_treatments_cover_tasks_and_are_complete_under_cap(self):
        spec = phase_b_tasks.load_spec()
        treatments = phase_b_run.load_treatments(TREATMENTS)
        self.assertEqual(
            {fixture["id"] for fixture in spec["fixtures"]},
            set(treatments),
        )
        incomplete_endings = ("讓『任", "跑在驗", "哪個已確認")
        for row in treatments.values():
            nudge = row["nudge"]
            self.assertGreater(len(nudge), 0)
            self.assertLessEqual(len(nudge), 52)
            self.assertFalse(nudge.endswith(incomplete_endings))

    def test_build_jobs_creates_three_matched_repeats(self):
        spec = phase_b_tasks.load_spec()
        treatments = phase_b_run.load_treatments(TREATMENTS)
        jobs = phase_b_run.build_jobs(spec, treatments, repeats=3, seed=20260821)
        self.assertEqual(36, len(jobs))
        keys = {(job["task_id"], job["repeat"], job["condition"]) for job in jobs}
        self.assertEqual(36, len(keys))
        for fixture in spec["fixtures"]:
            for repeat in range(1, 4):
                self.assertIn((fixture["id"], repeat, "control"), keys)
                self.assertIn((fixture["id"], repeat, "treatment"), keys)

    def test_materialized_candidate_diff_includes_tracked_jeff_candidate(self):
        with tempfile.TemporaryDirectory(prefix="mn-phase-b-test-") as raw:
            workspace = phase_b_tasks.materialize(
                "onboarding-problem-location",
                Path(raw) / "candidate",
                state="candidate",
            )
            diff = phase_b_run.git_text(workspace, "diff", "--")
            self.assertIn("ReminderQueue", diff)

    def test_analyzer_counts_paired_win_and_requires_three_net_wins(self):
        rows = []
        for index in range(1, 4):
            for condition in ("control", "treatment"):
                passed = condition == "treatment"
                rows.append(
                    {
                        "job_id": f"B{len(rows) + 1:03d}",
                        "task_id": "task",
                        "condition": condition,
                        "repeat": index,
                        "agent": {
                            "returncode": 0,
                            "timed_out": False,
                            "result_type": "result",
                            "subtype": "success",
                            "is_error": False,
                        },
                        "grader": {
                            "passed": passed,
                            "components_passed": 1 if passed else 0,
                            "components_total": 1,
                            "components": [{"name": "check", "passed": passed}],
                        },
                        "wall_ms": 1,
                    }
                )
        summary = phase_b_analyze.summarize(rows)
        self.assertEqual(3, summary["paired"]["wins"])
        self.assertEqual(0, summary["paired"]["losses"])
        self.assertTrue(summary["gates"]["paired_net_benefit"]["passed"])


if __name__ == "__main__":
    unittest.main()
