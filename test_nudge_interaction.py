import unittest
import tempfile
from pathlib import Path

from evaluation.nudge_interaction import analysis, dashboard
from masters_nudge import storage
from masters_nudge.contracts import SessionRef


SESSION_ID = "shader-session"


def telemetry(persona: str, status: str = "finding") -> dict:
    return {
        "domain": "shader",
        "session_id": SESSION_ID,
        "effective_lens": persona,
        "status": status,
    }


def research_telemetry(mode: str) -> dict:
    row = telemetry("carmack")
    row["review_trigger"] = f"shader-research-{mode}"
    return row


def review(ts: str, persona: str = "carmack") -> dict:
    return {
        "kind": "review",
        "session_id": SESSION_ID,
        "ts": ts,
        "persona": persona,
        "reaction": "一則觀察",
    }


def receipt(ts: str, status: str) -> dict:
    return {
        "kind": "delivery_receipt",
        "session_id": SESSION_ID,
        "reaction_ts": ts,
        "delivery_status": status,
    }


def annotation(
    ts: str,
    reaction_class: str,
    *,
    content_match: bool,
    behavior_change: bool = False,
    explicit_reference: bool = False,
    reframed: bool = False,
) -> dict:
    return {
        "reaction_ts": ts,
        "reaction_class": reaction_class,
        "evaluable": True,
        "content_match": content_match,
        "behavior_change": behavior_change,
        "explicit_reference": explicit_reference,
        "reframed": reframed,
        "delayed": False,
        "evidence": "固定快照中的後續行為證據。",
        "source": "heartbeat-observation",
    }


class NudgeInteractionAnalysisTests(unittest.TestCase):
    def test_same_gap_and_evidence_is_suppressed_but_new_evidence_reopens_it(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw)
            session = SessionRef("codex_cli", SESSION_ID, cwd=raw)

            storage.mark_shader_research_gap_reviewed(
                data_dir,
                session,
                gap_key="carmack:executed-work-elimination",
                evidence_fingerprint="evidence-a",
                source_fingerprint="source-a",
            )

            self.assertTrue(
                storage.shader_research_gap_is_unchanged(
                    data_dir,
                    session,
                    gap_key="carmack:executed-work-elimination",
                    evidence_fingerprint="evidence-a",
                )
            )
            self.assertFalse(
                storage.shader_research_gap_is_unchanged(
                    data_dir,
                    session,
                    gap_key="carmack:executed-work-elimination",
                    evidence_fingerprint="evidence-b",
                )
            )

    def test_funnel_uses_findings_then_injected_then_annotated_followups(self):
        telemetry_rows = [
            telemetry("carmack", "finding"),
            telemetry("lottes", "error"),
            telemetry("karis", "no_finding"),
        ]
        reaction_rows = [
            review("t1"),
            receipt("t1", "injected"),
            review("t2", "lottes"),
            receipt("t2", "expired"),
        ]
        annotations = {
            "schema_version": 1,
            "session_id": SESSION_ID,
            "cohort": {"name": "fixed cohort", "generated_count": 2},
            "annotations": [
                annotation(
                    "t1",
                    "possible_influence",
                    content_match=True,
                    behavior_change=True,
                )
            ],
        }

        metrics = analysis.analyze_session(
            telemetry_rows, reaction_rows, annotations, SESSION_ID
        )

        self.assertEqual(
            [2, 1, 1, 1],
            [stage["count"] for stage in metrics["delivery_funnel"]],
        )
        self.assertEqual(3, metrics["invocation_total"])
        self.assertEqual(1, metrics["annotation_coverage"]["evaluable"])

    def test_invocation_rate_includes_errors_no_findings_and_zero_personas(self):
        telemetry_rows = [
            telemetry("carmack", "finding"),
            telemetry("carmack", "error"),
            telemetry("lottes", "no_finding"),
        ]

        metrics = analysis.analyze_session(
            telemetry_rows,
            [],
            {
                "schema_version": 1,
                "session_id": SESSION_ID,
                "cohort": {"name": "empty", "generated_count": 0},
                "annotations": [],
            },
            SESSION_ID,
        )
        routes = {row["persona"]: row for row in metrics["invocations"]}

        self.assertEqual(6, len(routes))
        self.assertEqual(2, routes["carmack"]["count"])
        self.assertEqual(1, routes["carmack"]["statuses"]["error"])
        self.assertEqual(1, routes["lottes"]["statuses"]["no_finding"])
        self.assertEqual(0, routes["quilez"]["count"])
        self.assertAlmostEqual(66.7, routes["carmack"]["percent"])

    def test_research_mode_metric_checks_forward_opportunities_without_enforcing_a_quota(self):
        metrics = analysis.analyze_session(
            [
                research_telemetry("expand"),
                research_telemetry("deepen"),
                research_telemetry("guard"),
                telemetry("lottes"),
            ],
            [],
            {
                "schema_version": 1,
                "session_id": SESSION_ID,
                "cohort": {"name": "empty", "generated_count": 0},
                "annotations": [],
            },
            SESSION_ID,
        )

        self.assertEqual(
            metrics["research_modes"]["counts"],
            {"expand": 1, "deepen": 1, "guard": 1},
        )
        self.assertEqual(metrics["research_modes"]["forward_opportunities"], 2)
        self.assertTrue(metrics["research_modes"]["forward_exceeds_guard"])

    def test_possible_influence_requires_content_match_and_behavior_change(self):
        bad_annotations = {
            "schema_version": 1,
            "session_id": SESSION_ID,
            "cohort": {"name": "bad", "generated_count": 1},
            "annotations": [
                annotation(
                    "t1",
                    "possible_influence",
                    content_match=True,
                    behavior_change=False,
                )
            ],
        }

        with self.assertRaisesRegex(ValueError, "possible_influence"):
            analysis.analyze_session(
                [telemetry("carmack")],
                [review("t1"), receipt("t1", "injected")],
                bad_annotations,
                SESSION_ID,
            )

    def test_reaction_classes_are_mutually_exclusive_and_preserve_zeroes(self):
        rows = [review("t1"), receipt("t1", "injected")]
        annotations = {
            "schema_version": 1,
            "session_id": SESSION_ID,
            "cohort": {"name": "one", "generated_count": 1},
            "annotations": [
                annotation(
                    "t1", "temporal_only", content_match=True
                )
            ],
        }

        metrics = analysis.analyze_session(
            [telemetry("carmack")], rows, annotations, SESSION_ID
        )
        reactions = {row["key"]: row["count"] for row in metrics["reactions"]}

        self.assertEqual(1, reactions["temporal_only"])
        self.assertEqual(0, reactions["explicit_uptake"])
        self.assertEqual(0, reactions["reinterpretation"])
        self.assertEqual(0, reactions["possible_influence"])
        self.assertEqual(0, reactions["no_observable_response"])
        self.assertEqual(1, sum(reactions.values()))

    def test_annotation_must_reference_an_injected_finding(self):
        annotations = {
            "schema_version": 1,
            "session_id": SESSION_ID,
            "cohort": {"name": "expired", "generated_count": 1},
            "annotations": [
                annotation(
                    "t1", "no_observable_response", content_match=False
                )
            ],
        }

        with self.assertRaisesRegex(ValueError, "not injected"):
            analysis.analyze_session(
                [telemetry("carmack")],
                [review("t1"), receipt("t1", "expired")],
                annotations,
                SESSION_ID,
            )


class NudgeInteractionDashboardTests(unittest.TestCase):
    def test_dashboard_contains_exactly_three_requested_charts(self):
        metrics = analysis.analyze_session(
            [telemetry("carmack")],
            [review("t1"), receipt("t1", "injected")],
            {
                "schema_version": 1,
                "session_id": SESSION_ID,
                "cohort": {"name": "one", "generated_count": 1},
                "annotations": [
                    annotation(
                        "t1", "no_observable_response", content_match=False
                    )
                ],
            },
            SESSION_ID,
        )

        html = dashboard.render_dashboard(metrics)

        self.assertEqual(3, html.count('data-chart="'))
        self.assertIn('data-chart="delivery-funnel"', html)
        self.assertIn('data-chart="reaction-classes"', html)
        self.assertIn('data-chart="persona-invocations"', html)
        self.assertNotIn("延遲散點", html)
        self.assertNotIn("因果成功率", html)
        self.assertIn("不能證明因果", html)


if __name__ == "__main__":
    unittest.main()
