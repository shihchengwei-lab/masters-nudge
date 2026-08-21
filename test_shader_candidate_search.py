import unittest

from evaluation.shader_candidate_search import registry


def proposal(
    name: str,
    *,
    hypothesis: str = "register-pressure",
    mechanism: str = "shorten-live-ranges",
) -> dict:
    return {
        "name": name,
        "bottleneck_hypothesis": {
            "family": hypothesis,
            "statement": "長生命週期中間值限制 occupancy。",
            "evidence_refs": ["vtune:gpu-hotspots:occupancy"],
            "falsifiable_prediction": "live range 縮短時 active registers 應下降。",
        },
        "work_elimination_mechanism": {
            "family": mechanism,
            "eliminated_work": "跨迭代保留的中間向量。",
        },
    }


class ShaderCandidateSearchTests(unittest.TestCase):
    def setUp(self):
        self.state = registry.new_registry(
            max_candidate_cells=50,
            refinement_limit_per_cell=2,
        )

    def test_first_hypothesis_mechanism_cell_consumes_one_candidate_slot(self):
        result = registry.register_candidate(
            self.state,
            proposal("scalarize normal path"),
        )

        self.assertTrue(result["accepted"])
        self.assertEqual("candidate-001", result["candidate_id"])
        self.assertEqual(1, registry.coverage_report(self.state)["candidate_cells"])

    def test_near_neighbor_in_same_cell_is_redirected_without_using_a_slot(self):
        first = registry.register_candidate(
            self.state,
            proposal("normal precision live-range rewrite"),
        )
        result = registry.register_candidate(
            self.state,
            proposal("half precision live-range rewrite"),
        )

        self.assertFalse(result["accepted"])
        self.assertEqual("existing-search-cell", result["reason"])
        self.assertEqual(first["candidate_id"], result["record_as_refinement_of"])
        self.assertEqual(1, registry.coverage_report(self.state)["candidate_cells"])

    def test_different_hypothesis_or_mechanism_opens_a_new_candidate_cell(self):
        registry.register_candidate(self.state, proposal("normal"))
        changed_mechanism = registry.register_candidate(
            self.state,
            proposal("reciprocal", mechanism="remove-dependent-divide"),
        )
        changed_hypothesis = registry.register_candidate(
            self.state,
            proposal(
                "coverage cull",
                hypothesis="overdraw",
                mechanism="shorten-live-ranges",
            ),
        )

        self.assertTrue(changed_mechanism["accepted"])
        self.assertTrue(changed_hypothesis["accepted"])
        self.assertEqual(3, registry.coverage_report(self.state)["candidate_cells"])

    def test_refinements_are_nested_and_have_a_separate_explicit_budget(self):
        parent = registry.register_candidate(self.state, proposal("normal"))

        for name in ("half", "scalarized half"):
            result = registry.register_refinement(
                self.state,
                parent["candidate_id"],
                {
                    "name": name,
                    "changed_variable": "numeric representation",
                    "discriminator": "register count and frame-time distribution",
                },
            )
            self.assertTrue(result["accepted"])
        overflow = registry.register_refinement(
            self.state,
            parent["candidate_id"],
            {
                "name": "reciprocal half",
                "changed_variable": "instruction form",
                "discriminator": "dependent ALU latency",
            },
        )

        report = registry.coverage_report(self.state)
        self.assertFalse(overflow["accepted"])
        self.assertEqual("refinement-budget-exhausted", overflow["reason"])
        self.assertEqual(1, report["candidate_cells"])
        self.assertEqual(2, report["refinements"])

    def test_unsupported_hypothesis_does_not_consume_a_candidate_slot(self):
        invalid = proposal("guess")
        invalid["bottleneck_hypothesis"]["evidence_refs"] = []

        result = registry.register_candidate(self.state, invalid)

        self.assertFalse(result["accepted"])
        self.assertEqual("invalid-proposal", result["reason"])
        self.assertIn("evidence_refs", result["missing"])
        self.assertEqual(0, registry.coverage_report(self.state)["candidate_cells"])

    def test_candidate_budget_counts_distinct_cells_not_rejected_variants(self):
        state = registry.new_registry(
            max_candidate_cells=2,
            refinement_limit_per_cell=1,
        )
        registry.register_candidate(state, proposal("normal"))
        registry.register_candidate(state, proposal("half"))
        registry.register_candidate(
            state,
            proposal("divide", mechanism="remove-dependent-divide"),
        )
        overflow = registry.register_candidate(
            state,
            proposal("overdraw", hypothesis="overdraw", mechanism="early-reject"),
        )

        report = registry.coverage_report(state)
        self.assertFalse(overflow["accepted"])
        self.assertEqual("candidate-cell-budget-exhausted", overflow["reason"])
        self.assertEqual(2, report["candidate_cells"])
        self.assertEqual(1, report["existing_cell_rejections"])


if __name__ == "__main__":
    unittest.main()
