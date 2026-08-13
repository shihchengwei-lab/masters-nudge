import json
import unittest
from pathlib import Path
from unittest import mock

from evaluation import quality_eval
from evaluation import workflow_blind_review
from evaluation import workflow_unblind
from evaluation.phase_b import phase_b_prepare


HERE = Path(__file__).resolve().parent


class QualityEvaluationTests(unittest.TestCase):
    def test_all_fixtures_build_and_route_as_declared(self):
        fixtures = quality_eval.load_fixtures(HERE / "evaluation" / "fixtures.json")
        self.assertEqual(12, len(fixtures))
        for fixture in fixtures:
            packet = quality_eval.build_packet(fixture)
            self.assertTrue(packet)
            routes = quality_eval.fixture_routes(fixture, packet)
            self.assertEqual("general", routes["baseline"].effective_lens)
            self.assertEqual(
                fixture["expected_effective_lens"],
                routes["effective"].effective_lens,
            )

    def test_raw_schema_validation_keeps_no_finding_strict(self):
        self.assertTrue(
            quality_eval.raw_schema_valid(
                json.dumps({"status": "no_finding", "finding": ""})
            )
        )
        self.assertFalse(
            quality_eval.raw_schema_valid(
                json.dumps({"status": "no_finding", "finding": "hidden text"})
            )
        )
        self.assertTrue(
            quality_eval.raw_schema_valid(
                json.dumps({"status": "finding", "finding": "具體問題"})
            )
        )

    def test_issue_match_requires_one_term_from_every_group(self):
        groups = [["舊回應", "Search A"], ["覆寫"], ["新結果", "Search B"]]
        self.assertTrue(quality_eval.issue_matches("舊回應會覆寫 Search B 的結果", groups))
        self.assertFalse(quality_eval.issue_matches("舊回應會延遲畫面", groups))

    def test_score_payload_queues_unpunctuated_findings_for_review(self):
        fixture = quality_eval.load_fixtures(
            HERE / "evaluation" / "fixtures.json"
        )[0]
        finding = "accounts.status 與 status_copy 都可寫，可能造成狀態不一致"
        raw = json.dumps({"status": "finding", "finding": finding})
        scores = quality_eval.score_payload(fixture, "finding", finding, raw)
        self.assertTrue(scores["issue_match"])
        self.assertFalse(scores["sentence_terminated"])

    def test_job_count_adds_primary_condition_for_specialists(self):
        fixtures = quality_eval.load_fixtures(HERE / "evaluation" / "fixtures.json")
        jobs = quality_eval.build_jobs(fixtures, repeats=1, seed=1)
        self.assertEqual(28, len(jobs))

    def test_holdout_v1_is_frozen_to_declared_shape_and_routes(self):
        fixtures = quality_eval.load_fixtures(
            HERE / "evaluation" / "holdout-fixtures-v1.json"
        )
        self.assertEqual(16, len(fixtures))
        self.assertEqual(
            {"finding": 10, "no_finding": 6},
            {
                status: sum(
                    fixture["oracle"]["expected_status"] == status
                    for fixture in fixtures
                )
                for status in ("finding", "no_finding")
            },
        )
        jobs = quality_eval.build_jobs(fixtures, repeats=2, seed=20260815)
        self.assertEqual(72, len(jobs))

    def test_workflow_holdout_v2_has_balanced_lenses_and_declared_jobs(self):
        fixtures = quality_eval.load_fixtures(
            HERE / "evaluation" / "workflow-holdout-v2.json"
        )
        self.assertEqual(18, len(fixtures))
        self.assertEqual(
            {"finding": 12, "no_finding": 6},
            {
                status: sum(
                    fixture["oracle"]["expected_status"] == status
                    for fixture in fixtures
                )
                for status in ("finding", "no_finding")
            },
        )
        for lens in ("jeff", "beck", "fowler", "linus", "lamport", "carmack"):
            selected = [
                fixture
                for fixture in fixtures
                if fixture["expected_effective_lens"] == lens
            ]
            self.assertEqual(3, len(selected))
            self.assertEqual(
                ["finding", "finding", "no_finding"],
                sorted(
                    (fixture["oracle"]["expected_status"] for fixture in selected),
                    key=lambda status: status == "no_finding",
                ),
            )
        for fixture in fixtures:
            routes = quality_eval.fixture_routes(
                fixture, quality_eval.build_packet(fixture)
            )
            self.assertEqual(
                fixture["expected_effective_lens"],
                routes["effective"].effective_lens,
            )
        jobs = quality_eval.build_jobs(fixtures, repeats=2, seed=20260816)
        self.assertEqual(84, len(jobs))

    def test_blind_review_removes_condition_identity_from_review_packet(self):
        fixtures = quality_eval.load_fixtures(
            HERE / "evaluation" / "workflow-holdout-v2.json"
        )
        fixture = fixtures[0]
        rows = [
            {
                "fixture_id": fixture["id"],
                "condition": "effective",
                "repeat": 2,
                "status": "finding",
                "finding": "先選了技術，問題位置還沒被確認。",
                "raw_output": json.dumps(
                    {"status": "finding", "finding": "先選了技術，問題位置還沒被確認。"},
                    ensure_ascii=False,
                ),
            }
        ]
        review, identity_map = workflow_blind_review.build_blind_records(
            fixtures, rows, seed=1
        )
        self.assertEqual(1, len(review))
        self.assertNotIn("condition", review[0])
        self.assertNotIn("fixture_id", review[0])
        self.assertNotIn("repeat", review[0])
        self.assertEqual("effective", identity_map[0]["condition"])
        self.assertIsNone(review[0]["judgment"]["grounded"])

    def test_unblind_expands_categories_and_diagnostic_flags(self):
        payload = {
            "categories": {
                "valid": {
                    "ids": ["W001"],
                    "decision_valid": True,
                    "note": "ok",
                }
            },
            "diagnostic_flags": {
                "cap_hit_but_complete": {"ids": ["W001"], "note": "diagnostic"}
            },
        }
        expanded = workflow_unblind.expand_judgments(payload)
        self.assertTrue(expanded["W001"]["decision_valid"])
        self.assertEqual("valid", expanded["W001"]["category"])
        self.assertEqual(["cap_hit_but_complete"], expanded["W001"]["flags"])

    def test_unblind_paired_stats_count_validity_wins_and_losses(self):
        def row(condition, repeat, valid):
            return {
                "fixture_id": "fixture",
                "condition": condition,
                "repeat": repeat,
                "judgment": {"decision_valid": valid},
            }

        rows = [
            row("baseline", 1, False),
            row("effective", 1, True),
            row("baseline", 2, True),
            row("effective", 2, False),
        ]
        stats = workflow_unblind.paired_stats(rows, "effective", "baseline")
        self.assertEqual(2, stats["pairs"])
        self.assertEqual(1, stats["wins"])
        self.assertEqual(1, stats["losses"])
        self.assertEqual(0, stats["treatment_invalid_minus_control_invalid"])

    def test_phase_b_treatment_row_uses_real_route_fields(self):
        fixture = {
            "id": "task",
            "lens": "lamport",
        }
        route = quality_eval.lens_router.ReviewRoute(
            "evolve",
            "fowler",
            "lamport",
            "lamport",
            "state-ordering-evidence",
            "evaluation",
        )
        job = {
            "fixture": fixture,
            "packet": "packet",
            "route": route,
            "prompt": "prompt",
        }
        raw = json.dumps({"status": "finding", "finding": "順序尚未驗證。"}, ensure_ascii=False)
        with mock.patch.object(
            phase_b_prepare.quality_eval,
            "call_reviewer",
            return_value={
                "status": "finding",
                "finding": "順序尚未驗證。",
                "raw_output": raw,
                "usage": {},
            },
        ):
            row = phase_b_prepare.run_job(job)
        self.assertEqual("lamport", row["route"]["override_lens"])


if __name__ == "__main__":
    unittest.main()
