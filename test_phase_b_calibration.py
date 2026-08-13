import copy
import json
import tempfile
import unittest
from pathlib import Path

from evaluation.phase_b import phase_b_run
from evaluation.phase_b_calibration import calibration_analyze
from evaluation.phase_b_calibration import calibration_run
from evaluation.phase_b_calibration import calibration_tasks


HERE = Path(__file__).resolve().parent
ORACLE_VALIDATION = (
    HERE
    / "evaluation"
    / "results"
    / "phase-b-calibration-v1-20260813"
    / "oracle-validation.json"
)


def synthetic_rows() -> list[dict]:
    rows = []
    task_ids = [item["id"] for item in calibration_tasks.load_spec()["fixtures"]]
    for task_id in task_ids:
        for repeat in range(1, 4):
            for condition in ("control", "positive_control"):
                passed = condition == "positive_control" or repeat == 1
                rows.append(
                    {
                        "job_id": f"C{len(rows) + 1:03d}",
                        "task_id": task_id,
                        "condition": condition,
                        "repeat": repeat,
                        "agent": {
                            "returncode": 0,
                            "timed_out": False,
                            "result_type": "result",
                            "subtype": "success",
                            "is_error": False,
                        },
                        "grader": {
                            "passed": passed,
                            "safe_target_resolution": passed,
                            "components_total": 1,
                            "components": [
                                {"name": "target_resolution", "passed": passed}
                            ],
                        },
                        "wall_ms": 1,
                    }
                )
    return rows


class PhaseBCalibrationTests(unittest.TestCase):
    def test_spec_has_six_lenses_and_complete_state_assets(self):
        spec = calibration_tasks.load_spec()
        calibration_tasks.validate_assets(spec)
        fixtures = spec["fixtures"]
        self.assertEqual(6, len(fixtures))
        self.assertEqual(
            {"jeff", "beck", "fowler", "linus", "lamport", "carmack"},
            {fixture["lens"] for fixture in fixtures},
        )
        self.assertTrue(all(row["target_component"] == "target_resolution" for row in fixtures))

    def test_oracle_validation_covers_positive_and_negative_controls(self):
        payload = json.loads(ORACLE_VALIDATION.read_text(encoding="utf-8"))
        self.assertTrue(payload["all_valid"])
        self.assertEqual(6, len(payload["tasks"]))
        for task in payload["tasks"]:
            self.assertTrue(task["valid"])
            self.assertTrue(all(task["checks"].values()))

    def test_materialized_candidate_keeps_baseline_commit_and_candidate_diff(self):
        with tempfile.TemporaryDirectory(prefix="mn-calibration-test-") as raw:
            workspace = calibration_tasks.materialize(
                "setup-bottleneck-choice",
                Path(raw) / "candidate",
                state="candidate",
            )
            self.assertEqual(
                "1",
                phase_b_run.git_text(workspace, "rev-list", "--count", "HEAD").strip(),
            )
            self.assertIn("schedule_setup_followup", phase_b_run.git_text(workspace, "diff", "--"))

    def test_build_jobs_is_balanced_and_prompt_changes_only_by_control_block(self):
        spec = calibration_tasks.load_spec()
        jobs = calibration_run.build_jobs(spec, repeats=3, seed=20260822)
        self.assertEqual(36, len(jobs))
        self.assertEqual(18, sum(row["condition"] == "control" for row in jobs))
        self.assertEqual(18, sum(row["condition"] == "positive_control" for row in jobs))
        keys = {(row["task_id"], row["repeat"], row["condition"]) for row in jobs}
        self.assertEqual(36, len(keys))

        fixture = spec["fixtures"][0]
        control = {**fixture, "condition": "control", "positive_control": ""}
        positive = {**fixture, "condition": "positive_control"}
        control_prompt = calibration_run.agent_prompt(control)
        positive_prompt = calibration_run.agent_prompt(positive)
        self.assertTrue(positive_prompt.startswith(control_prompt))
        self.assertNotIn(fixture["positive_control"], control_prompt)
        self.assertIn(fixture["positive_control"], positive_prompt)

    def test_analyzer_accepts_discriminating_tasks_and_rejects_control_ceiling(self):
        rows = synthetic_rows()
        expected = {
            (row["task_id"], row["repeat"], row["condition"])
            for row in rows
        }
        summary = calibration_analyze.summarize(rows, expected)
        self.assertTrue(summary["stage1_passed"])
        self.assertEqual(6, sum(row["accepted"] for row in summary["by_task"].values()))
        self.assertEqual(12, summary["paired"]["wins"])

        ceiling = copy.deepcopy(rows)
        first_task = ceiling[0]["task_id"]
        for row in ceiling:
            if row["task_id"] == first_task and row["condition"] == "control":
                row["grader"]["passed"] = True
                row["grader"]["safe_target_resolution"] = True
                row["grader"]["components"][0]["passed"] = True
        rejected = calibration_analyze.summarize(ceiling, expected)
        self.assertFalse(rejected["stage1_passed"])
        self.assertFalse(rejected["by_task"][first_task]["accepted"])


if __name__ == "__main__":
    unittest.main()
