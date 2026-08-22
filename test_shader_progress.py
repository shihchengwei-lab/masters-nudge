#!/usr/bin/env python3
"""Shader research-source projection and semantic trigger tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import shader_progress
import shader_router
import source_context
from masters_nudge import profiles, storage
from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.contracts import ReviewOutcome, SessionRef
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


HERE = Path(__file__).resolve().parent
SHADER_FIXTURES = HERE / "tests" / "fixtures" / "shader"


def write_json(path: Path, payload: dict, *, indent: int | None = 2) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=indent), encoding="utf-8"
    )


def write_research_sources(root: Path, *, result_status: str = "running") -> None:
    write_json(
        root / "benchmark" / "architecture-contract.json",
        {
            "schema_version": 3,
            "status": "active",
            "claims_permitted": False,
            "research_question": "Find the reproducible Shader Pareto frontier.",
        },
    )
    write_json(
        root / "benchmark" / "architecture-experiments.json",
        {
            "schema_version": 2,
            "experiments": [
                {"id": "A26", "family": "vertex-fetch", "status": "measured"},
                {"id": "A27", "family": "normal-format", "status": "visual-rejected"},
                {"id": "A28", "family": "normal-format", "status": "planned"},
            ],
        },
    )
    write_json(
        root / "benchmark" / "architecture-result.json",
        {
            "schema_version": 2,
            "status": result_status,
            "current_frontier": ["A26"],
            "resolved_architecture_trials": 2,
            "unresolved_architecture_trials": 1,
            "claims_permitted": False,
        },
    )
    write_json(
        root / "benchmark" / "candidate-results.json",
        {
            "schema_version": 1,
            "protocol": "formal-long-tail-v1",
            "results": [],
        },
    )


def settings_for(root: Path) -> RuntimeSettings:
    return RuntimeSettings(
        "openai",
        "test-model",
        60,
        15,
        RuntimePaths(HERE, root / "data", root / "error.log"),
    )


class FakeCore:
    def __init__(self, settings: RuntimeSettings) -> None:
        self.settings = settings
        self.calls = []
        self.log_error = lambda _message: None

    def review(self, request, **_kwargs):  # pragma: no cover - detached in these tests
        self.calls.append(request)
        raise AssertionError("semantic strategy review should be detached")


class WorkerCore(FakeCore):
    def review(self, request, **_kwargs):
        self.calls.append(request)
        return ReviewOutcome("no_finding", effective_lens="carmack")


class ShaderResearchProjectionTests(unittest.TestCase):
    def test_observed_long_tail_failure_fixture_routes_by_mechanism_not_generic_metrics(self):
        fixture = json.loads(
            (SHADER_FIXTURES / "observed-long-tail-failure-v1.json").read_text(
                encoding="utf-8"
            )
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            for relative, payload in fixture["source_files"].items():
                write_json(root / relative, payload)

            snapshot = shader_progress.load_research_snapshot(root)

        self.assertIsNotNone(snapshot)
        assert snapshot is not None
        metadata = shader_progress.research_review_metadata(None, snapshot.state)
        self.assertEqual(
            fixture["expected_v2"]["primary_route_signal"],
            metadata["route_signals"][0],
        )
        self.assertEqual(fixture["expected_v2"]["gap_key"], metadata["gap_key"])
        self.assertEqual(
            {"akenine_moller": 32, "lottes": 38, "carmack": 0,
             "karis": 0, "quilez": 0, "tatarchuk": 0},
            fixture["source"]["observed_persona_findings"],
        )

    def test_completed_long_tail_schema_aliases_become_decision_material(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_json(
                root / "benchmark" / "architecture-contract.json",
                {
                    "status": "active",
                    "claims_permitted": False,
                    "product_contract_sha256": "contract-sha",
                    "research_question": "How far can the frontier move?",
                },
            )
            write_json(
                root / "benchmark" / "architecture-experiments.json",
                {
                    "experiments": [
                        {
                            "id": "LT021",
                            "stage": "combination",
                            "mechanism_family": "frontier-beam-object-normalization",
                            "hypothesis": "Remove redundant fragment normalization.",
                            "single_change": "Add the measured normalization removal.",
                            "status": "measured",
                            "source_sha256": "shader-sha",
                            "metrics": {"gallery_incremental_gpu_median_ms": 0.9408075},
                            "evidence_files": [
                                {"path": "Evidence/LT021/acceptance.json", "sha256": "a"},
                                {"path": "benchmark/results/LT021.json", "sha256": "b"},
                            ],
                            "decision": "eligible-frontier",
                        }
                    ]
                },
            )
            write_json(
                root / "benchmark" / "architecture-result.json",
                {
                    "status": "running",
                    "frontier": ["LT021"],
                    "resolved_candidate_cells": 21,
                    "unresolved_candidate_cells": 29,
                    "saturation_reached": False,
                    "claims_permitted": False,
                },
            )

            snapshot = shader_progress.load_research_snapshot(root)

            self.assertIsNotNone(snapshot)
            assert snapshot is not None
            candidate = snapshot.state["candidates"][0]
            self.assertEqual(
                "Add the measured normalization removal.",
                candidate["implementation_delta"],
            )
            self.assertEqual(
                ["Evidence/LT021/acceptance.json", "benchmark/results/LT021.json"],
                candidate["evidence_refs"],
            )
            self.assertEqual("shader-sha", candidate["source_fingerprint"])
            self.assertEqual("combination", candidate["trajectory"])
            self.assertEqual("contract-sha", candidate["contract_fingerprint"])
            self.assertIn("0.9408075", snapshot.projection)

    def test_v2_packet_preserves_decision_material_and_marks_missing_fields(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_json(
                root / "benchmark" / "architecture-contract.json",
                {
                    "status": "active",
                    "claims_permitted": False,
                    "research_question": "Find the long-tail frontier.",
                    "contract_fingerprint": "contract-v1",
                },
            )
            write_json(
                root / "benchmark" / "architecture-experiments.json",
                {
                    "experiments": [
                        {
                            "id": "LT011",
                            "mechanism_family": "compiler-work-elimination",
                            "status": "measured",
                            "parent_frontier_id": "LT009",
                            "falsifiable_statement": "The compiler removes one reciprocal.",
                            "expected_removed_work": "one fragment reciprocal",
                            "actual_removed_work": "compiler output still contains one reciprocal",
                            "implementation_delta": "replace divide with shared reciprocal",
                            "evidence_refs": ["benchmark/raw/LT011.json"],
                            "decision": "N",
                            "unresolved_question": "source rewrite or executed work removal",
                            "evidence_dimensions": ["execution"],
                            "metrics": {"gpu_median_ms": 0.94, "ci95_ms": [0.93, 0.95]},
                        }
                    ]
                },
            )
            write_json(
                root / "benchmark" / "architecture-result.json",
                {
                    "status": "running",
                    "frontier": ["LT009"],
                    "resolved_candidate_cells": 11,
                    "unresolved_candidate_cells": 39,
                    "saturation_reached": False,
                    "claims_permitted": False,
                },
            )

            snapshot = shader_progress.load_research_snapshot(root)

            self.assertIsNotNone(snapshot)
            assert snapshot is not None
            candidate = snapshot.state["candidates"][0]
            self.assertEqual("LT009", candidate["parent_frontier_id"])
            self.assertEqual("one fragment reciprocal", candidate["expected_removed_work"])
            self.assertEqual(["benchmark/raw/LT011.json"], candidate["evidence_refs"])
            self.assertEqual(["execution"], candidate["evidence_dimensions"])
            self.assertIn("parent frontier: LT009", snapshot.projection)
            self.assertIn("expected removed work: one fragment reciprocal", snapshot.projection)
            self.assertIn("direct evidence: compiler output still contains one reciprocal", snapshot.projection)
            self.assertIn("missing: source_fingerprint, trajectory, nudge_ids", snapshot.projection)

            metadata = shader_progress.research_review_metadata(None, snapshot.state)
            self.assertEqual(("carmack|executed-work-elimination",), metadata["route_signals"])
            self.assertEqual("carmack:executed-work-elimination", metadata["gap_key"])
            self.assertRegex(metadata["gap_evidence_fingerprint"], r"^[0-9a-f]{16}$")
            self.assertGreater(metadata["material_completeness"], 0.5)

            packet = source_context.build_shader_research_packet(
                "candidate LT011: planned -> measured",
                snapshot.projection,
                task_anchor="Pursue the long-tail frontier.",
                tool_evidence="GPU benchmark median 0.94 ms; compiler output retained reciprocal.",
            )
            self.assertIn("[candidate decision material]", packet)
            self.assertIn("[latest direct evidence]", packet)
            self.assertNotIn("[recent blind spots]", packet)

    def test_review_metadata_routes_six_explicit_evidence_dimensions_without_quotas(self):
        expected = {
            "execution": "carmack|executed-work-elimination",
            "visibility": "akenine_moller|visibility-work-elimination",
            "procedural": "quilez|procedural-representation",
            "material": "karis|render-contract-semantics",
            "temporal": "lottes|spatiotemporal-stability",
            "platform": "tatarchuk|platform-generality",
        }
        for dimension, signal in expected.items():
            with self.subTest(dimension=dimension):
                state = {
                    "contract": {},
                    "result": {"frontier": ["P0"]},
                    "candidates": [
                        {
                            "id": "C1",
                            "status": "measured",
                            "family": dimension,
                            "evidence_dimensions": [dimension],
                            "expected_removed_work": "bounded work",
                            "actual_removed_work": "measured evidence",
                        }
                    ],
                }
                metadata = shader_progress.research_review_metadata(None, state)
                self.assertEqual((signal,), metadata["route_signals"])

    def test_six_natural_material_classes_reach_the_expected_persona(self):
        fixture = json.loads(
            (SHADER_FIXTURES / "material-routing-v1.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(1, fixture["schema_version"])
        self.assertEqual(6, len(fixture["cases"]))
        for case in fixture["cases"]:
            with self.subTest(material=case["id"]):
                state = {
                    "contract": {},
                    "result": {"frontier": ["P0"]},
                    "candidates": [case["candidate"]],
                }
                metadata = shader_progress.research_review_metadata(None, state)
                route = shader_router.resolve_shader_route(
                    "optimize",
                    case["distractor_prompt"],
                    primary_lens=case["primary_lens"],
                    checkpoint=True,
                    route_signals=metadata["route_signals"],
                )

                self.assertEqual(
                    case["expected_signal"], metadata["route_signals"][0]
                )
                self.assertEqual(case["expected_lens"], route.effective_lens)
                self.assertEqual("shader_structured_evidence", route.source)

    def test_generic_quality_metrics_do_not_override_the_candidate_mechanism(self):
        state = {
            "contract": {},
            "result": {"frontier": ["LT042"]},
            "candidates": [
                {
                    "id": "LT050",
                    "status": "measured",
                    "family": "frontier-ring-beam-sweep-normalize-rsqrt",
                    "falsifiable_statement": "Explicit rsqrt may remove normalization cost.",
                    "implementation_delta": "Lower sweep normalization in the vertex path.",
                    "metrics": {
                        "overdraw_mean_layers": 0.24,
                        "shader_variants": 1,
                        "gpu_median_ms": 0.94,
                    },
                }
            ],
        }

        metadata = shader_progress.research_review_metadata(None, state)

        self.assertEqual(
            "quilez|procedural-representation", metadata["route_signals"][0]
        )
        self.assertNotIn(
            "akenine_moller|visibility-work-elimination",
            metadata["route_signals"],
        )
        self.assertNotIn(
            "karis|render-contract-semantics", metadata["route_signals"]
        )

    def test_v1_long_tail_schema_maps_frontier_coverage_and_mechanism_family(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_json(
                root / "benchmark" / "architecture-contract.json",
                {
                    "status": "active",
                    "claims_permitted": False,
                    "research_question": "Find the long-tail frontier.",
                },
            )
            write_json(
                root / "benchmark" / "architecture-experiments.json",
                {
                    "experiments": [
                        {
                            "id": "Cell001",
                            "mechanism_family": "interpolator-pressure",
                            "status": "planned",
                        }
                    ]
                },
            )
            write_json(
                root / "benchmark" / "architecture-result.json",
                {
                    "status": "baseline-established",
                    "frontier": ["BaselineV0"],
                    "resolved_candidate_cells": 0,
                    "unresolved_candidate_cells": 50,
                    "saturation_reached": False,
                    "claims_permitted": False,
                },
            )

            snapshot = shader_progress.load_research_snapshot(root)

            self.assertIsNotNone(snapshot)
            assert snapshot is not None
            self.assertEqual(["BaselineV0"], snapshot.state["result"]["frontier"])
            self.assertEqual(0, snapshot.state["result"]["resolved"])
            self.assertEqual(50, snapshot.state["result"]["unresolved"])
            self.assertFalse(snapshot.state["result"]["saturation_rule_met"])
            self.assertEqual(
                "interpolator-pressure", snapshot.state["candidates"][0]["family"]
            )
            self.assertIn("frontier: BaselineV0", snapshot.projection)
            self.assertIn("coverage: resolved=0; unresolved=50", snapshot.projection)

    def test_webgpu_black_hole_schema_preserves_candidates_and_search_coverage(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_json(
                root / "benchmark" / "architecture-contract.json",
                {
                    "status": "active",
                    "claims_permitted": False,
                    "research_question": "Find the WebGPU black-hole frontier.",
                    "search_contract": {
                        "candidate_budget": 4,
                        "candidate_id_range": "A01-A04",
                        "prefrozen_mechanism_inventory": [
                            "raymarch-budget-and-early-exit",
                            "blackbody-color-and-temperature-profile",
                            "starfield",
                        ],
                    },
                },
            )
            write_json(
                root / "benchmark" / "architecture-experiments.json",
                {
                    "candidate_budget": 4,
                    "candidate_id_range": "A01-A04",
                    "experiments": [
                        {
                            "candidate_id": "A01",
                            "parent_id": "A00",
                            "mechanism_id": "raymarch-budget-and-early-exit",
                            "status": "qualified",
                            "change": "Remove redundant loop state.",
                            "evidence_ref": "benchmark/evidence/A01-evaluation.json",
                            "evidence_dimensions": ["execution"],
                            "performance": {"paired_mean_improvement_percent": 0.5},
                            "visual": {"global_ssim": 1.0},
                        },
                        {
                            "candidate_id": "A02",
                            "parent_id": "A00",
                            "mechanism_id": "raymarch-budget-and-early-exit",
                            "status": "visual-rejected",
                            "change": "Reduce the raymarch ceiling.",
                        },
                        {
                            "candidate_id": "A03",
                            "parent_id": "A00",
                            "mechanism_id": "raymarch-budget-and-early-exit",
                            "status": "visual-rejected",
                            "change": "Reduce the raymarch ceiling again.",
                        },
                        {
                            "candidate_id": "A04",
                            "parent_id": "A00",
                            "mechanism_id": "blackbody-color-and-temperature-profile",
                            "status": "exhausted",
                            "change": "Change the blackbody lookup.",
                        },
                    ],
                },
            )
            write_json(
                root / "benchmark" / "architecture-result.json",
                {
                    "status": "phase-close-unsaturated",
                    "current_frontier": [
                        {"candidate_id": "A01", "status": "qualified"}
                    ],
                    "resolved_candidate_cells": 4,
                    "unresolved_candidate_cells": 0,
                    "saturation_reached": False,
                    "claims_permitted": False,
                    "evaluated_candidates": 4,
                },
            )

            snapshot = shader_progress.load_research_snapshot(root)

            self.assertIsNotNone(snapshot)
            assert snapshot is not None
            self.assertEqual(["A01"], snapshot.state["result"]["frontier"])
            self.assertEqual(
                ["A01", "A02", "A03", "A04"],
                [item["id"] for item in snapshot.state["candidates"]],
            )
            first = snapshot.state["candidates"][0]
            self.assertEqual(
                "raymarch-budget-and-early-exit", first["family"]
            )
            self.assertEqual("A00", first["parent_frontier_id"])
            self.assertEqual("Remove redundant loop state.", first["implementation_delta"])
            self.assertEqual(
                ["benchmark/evidence/A01-evaluation.json"],
                first["evidence_refs"],
            )
            self.assertEqual(
                {"paired_mean_improvement_percent": 0.5}, first["metrics"]
            )
            self.assertEqual({"global_ssim": 1.0}, first["quality"])
            self.assertEqual(
                {
                    "raymarch-budget-and-early-exit": 3,
                    "blackbody-color-and-temperature-profile": 1,
                },
                snapshot.state["search"]["family_distribution"],
            )
            self.assertEqual(3, snapshot.state["search"]["consecutive_failures"])
            self.assertEqual(4, snapshot.state["search"]["evaluated"])
            self.assertEqual(4, snapshot.state["search"]["budget"])
            self.assertEqual(0, snapshot.state["search"]["remaining"])
            self.assertEqual(
                ["starfield"], snapshot.state["search"]["unexplored_mechanisms"]
            )
            self.assertIn("search budget: evaluated=4/4; remaining=0", snapshot.projection)
            self.assertIn(
                "candidate families: raymarch-budget-and-early-exit=3; "
                "blackbody-color-and-temperature-profile=1",
                snapshot.projection,
            )
            self.assertIn("consecutive explicit failures: 3", snapshot.projection)
            self.assertIn(
                "unexplored prefrozen mechanisms: starfield", snapshot.projection
            )

    def test_known_research_files_are_the_only_authoritative_inputs(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root)

            snapshot = shader_progress.load_research_snapshot(root)

            self.assertIsNotNone(snapshot)
            assert snapshot is not None
            self.assertIn("frontier: A26", snapshot.projection)
            self.assertIn("active: A28 (planned)", snapshot.projection)
            self.assertIn("closed: A27 (visual-rejected)", snapshot.projection)
            self.assertEqual(
                set(snapshot.sources),
                {
                    "benchmark/architecture-contract.json",
                    "benchmark/architecture-experiments.json",
                    "benchmark/architecture-result.json",
                    "benchmark/candidate-results.json",
                },
            )

    def test_candidate_results_update_projection_and_fingerprint_before_result_rollup(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root)
            experiments_path = root / "benchmark" / "architecture-experiments.json"
            experiments = json.loads(experiments_path.read_text(encoding="utf-8"))
            experiments["experiments"].append(
                {"id": "H08", "family": "compiler-unroll-hint", "status": "planned"}
            )
            write_json(experiments_path, experiments)
            before = shader_progress.load_research_snapshot(root)
            write_json(
                root / "benchmark" / "candidate-results.json",
                {
                    "schema_version": 1,
                    "protocol": "formal-long-tail-v1",
                    "results": [
                        {
                            "candidate": "A28",
                            "status": "measured",
                            "valid_candidate_cell": True,
                            "source_sha256": "candidate-source",
                            "summary": {
                                "phases": {
                                    "gallery-24-shields": {
                                        "incremental_gpu_median_ms": 0.94,
                                        "incremental_gpu_p95_ms": 1.02,
                                    }
                                },
                                "visual_ssim": 0.9999,
                                "max_abs_channel_error": 0.003,
                            },
                            "contract_checks": {"visual_ssim": True},
                            "repeat_hashes_match": {"gallery-24-shields": True},
                            "evidence_files": {
                                "raw": "Evidence/A28/raw.json",
                                "visual": "Evidence/A28/visual.json",
                            },
                        }
                    ],
                },
            )

            after = shader_progress.load_research_snapshot(root)

            assert before is not None and after is not None
            self.assertNotEqual(before.fingerprint, after.fingerprint)
            candidate = next(
                item for item in after.state["candidates"] if item["id"] == "A28"
            )
            self.assertEqual("measured", candidate["status"])
            self.assertEqual("candidate-source", candidate["source_fingerprint"])
            self.assertEqual(
                ["Evidence/A28/raw.json", "Evidence/A28/visual.json"],
                candidate["evidence_refs"],
            )
            self.assertEqual(
                0.94,
                candidate["metrics"]["phases"]["gallery-24-shields"][
                    "incremental_gpu_median_ms"
                ],
            )
            self.assertEqual(0.9999, candidate["quality"]["visual_ssim"])
            self.assertIn("candidate: A28 (measured)", after.projection)
            self.assertIn("incremental_gpu_median_ms", after.projection)
            self.assertIn("candidate A28: planned -> measured", shader_progress.describe_change(before.state, after.state))

    def test_live_evidence_result_updates_projection_without_candidate_results_ledger(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root)
            (root / "benchmark" / "candidate-results.json").unlink()
            experiments_path = root / "benchmark" / "architecture-experiments.json"
            experiments = json.loads(experiments_path.read_text(encoding="utf-8"))
            experiments["experiments"].append(
                {
                    "id": "LTV2-I10",
                    "family": "hex-coordinate",
                    "status": "planned",
                }
            )
            write_json(experiments_path, experiments)
            before = shader_progress.load_research_snapshot(root)
            write_json(
                root / "Evidence" / "LongTail" / "LTV2-I10" / "result.json",
                {
                    "schema_version": 1,
                    "candidate": "LTV2-I10",
                    "family": "hex-coordinate",
                    "stage": "isolated",
                    "valid_candidate_cell": True,
                    "all_research_targets_pass": False,
                    "checks": {"visual_regression": True, "hero_gpu_budget": False},
                    "summary": {
                        "visual_ssim": 1.0,
                        "max_abs_channel_error": 0.0,
                        "phases": {
                            "gallery-24-shields": {
                                "incremental_gpu_median_ms": 1.3279
                            }
                        },
                    },
                    "raw_evidence": {
                        "input_manifest": {
                            "path": "Evidence/LongTail/LTV2-I10/input-manifest.json",
                            "sha256": "manifest-sha",
                        },
                        "benchmark": {
                            "path": "Evidence/LongTail/LTV2-I10/benchmark.json",
                            "sha256": "benchmark-sha",
                        },
                        "build_tree_sha256": "not-an-evidence-path",
                    },
                },
            )

            after = shader_progress.load_research_snapshot(root)

            assert before is not None and after is not None
            self.assertNotEqual(before.fingerprint, after.fingerprint)
            candidate = next(
                item for item in after.state["candidates"] if item["id"] == "LTV2-I10"
            )
            self.assertEqual("measured", candidate["status"])
            self.assertEqual("manifest-sha", candidate["source_fingerprint"])
            self.assertEqual(
                [
                    "Evidence/LongTail/LTV2-I10/result.json",
                    "Evidence/LongTail/LTV2-I10/input-manifest.json",
                    "Evidence/LongTail/LTV2-I10/benchmark.json",
                ],
                candidate["evidence_refs"],
            )
            self.assertEqual(
                {"observed": 1, "valid": 1, "failed": 0},
                after.state["evidence_progress"],
            )
            self.assertIn("live evidence: observed=1; valid=1; failed=0", after.projection)
            self.assertIn("candidate: LTV2-I10 (measured)", after.projection)
            self.assertIn(
                "Evidence/LongTail/LTV2-I10/result.json", after.sources
            )

    def test_formal_long_tail_result_schema_counts_valid_evidence_and_uses_live_status(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root, result_status="search-active")
            write_json(
                root / "benchmark" / "architecture-contract.json",
                {
                    "schema_version": 3,
                    "status": "baseline-pending",
                    "claims_permitted": False,
                    "research_question": "Find the reproducible Shader Pareto frontier.",
                },
            )
            write_json(
                root / "benchmark" / "architecture-result.json",
                {
                    "schema_version": 2,
                    "status": "search-active",
                    "current_frontier": ["C01_EARLY_RADIAL_REJECT"],
                    "resolved_candidate_cells": 1,
                    "unresolved_candidate_cells": 49,
                    "claims_permitted": False,
                },
            )
            write_json(
                root
                / "Evidence"
                / "LongTail"
                / "C01_EARLY_RADIAL_REJECT"
                / "result.json",
                {
                    "schema_version": 1,
                    "protocol": "formal-long-tail-v1",
                    "candidate_id": "C01_EARLY_RADIAL_REJECT",
                    "parent_frontier_id": "BaselineV0",
                    "mechanism_family": "geometric_culling",
                    "status": "resolved",
                    "decision": "inconclusive_not_frontier",
                    "improvement_percent": 1.33,
                    "visual": {
                        "repeat_hashes_match": True,
                        "ssim_minimum_observed": 1.0,
                        "max_abs_channel_error_observed": 0.0,
                        "pass": True,
                    },
                    "gpu_metric_ms": {
                        "metric_scope": "Unity Render:GPU Frame Time",
                        "mean_of_repetition_medians_ms": 2.65,
                        "ci95_ms": [2.64, 2.66],
                        "profiler_bottleneck": "CPU",
                    },
                    "raw_measurement_refs": [
                        "Evidence/LongTail/C01_EARLY_RADIAL_REJECT/run-01.json"
                    ],
                    "actual_evidence": {
                        "valid_repetitions": 5,
                        "raw_gpu_samples": 6000,
                        "graphics_device_names": ["Intel(R) UHD Graphics"],
                        "graphics_api": ["Direct3D11"],
                        "resolution": [1920, 1080],
                    },
                },
            )

            snapshot = shader_progress.load_research_snapshot(root)

            assert snapshot is not None
            self.assertEqual(
                {"observed": 1, "valid": 1, "failed": 0},
                snapshot.state["evidence_progress"],
            )
            self.assertEqual("search-active", snapshot.state["contract"]["status"])
            self.assertEqual(
                "baseline-pending", snapshot.state["contract"]["declared_status"]
            )
            candidate = next(
                item
                for item in snapshot.state["candidates"]
                if item["id"] == "C01_EARLY_RADIAL_REJECT"
            )
            self.assertEqual("resolved", candidate["status"])
            self.assertEqual("BaselineV0", candidate["parent_frontier_id"])
            self.assertEqual(2.65, candidate["metrics"]["mean_of_repetition_medians_ms"])
            self.assertEqual(5, candidate["quality"]["actual_evidence"]["valid_repetitions"])
            self.assertIn(
                "Evidence/LongTail/C01_EARLY_RADIAL_REJECT/run-01.json",
                candidate["evidence_refs"],
            )
            self.assertIn("contract: search-active", snapshot.projection)
            self.assertIn(
                "live evidence: observed=1; valid=1; failed=0", snapshot.projection
            )

    def test_formal_long_tail_baseline_is_observed_but_not_counted_as_a_candidate(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root, result_status="search-active")
            write_json(
                root / "Evidence" / "LongTail" / "BaselineV0" / "result.json",
                {
                    "schema_version": 1,
                    "protocol": "formal-long-tail-v1",
                    "candidate_id": "BaselineV0",
                    "status": "resolved",
                    "decision": "baseline_established",
                    "mechanism_family": "baseline",
                    "gpu_metric_ms": {
                        "mean_of_repetition_medians_ms": 2.67,
                    },
                    "actual_evidence": {
                        "valid_repetitions": 5,
                        "raw_gpu_samples": 6000,
                    },
                },
            )

            snapshot = shader_progress.load_research_snapshot(root)

            assert snapshot is not None
            self.assertEqual(
                {"observed": 1, "valid": 0, "failed": 0},
                snapshot.state["evidence_progress"],
            )

    def test_live_evidence_failure_is_visible_and_next_result_moves_focus(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root)
            (root / "benchmark" / "candidate-results.json").unlink()
            experiments_path = root / "benchmark" / "architecture-experiments.json"
            experiments = json.loads(experiments_path.read_text(encoding="utf-8"))
            experiments["experiments"].extend(
                [
                    {"id": "LTV2-I08", "family": "view-vector", "status": "planned"},
                    {"id": "LTV2-I10", "family": "hex-coordinate", "status": "planned"},
                ]
            )
            write_json(experiments_path, experiments)
            failure_path = (
                root / "Evidence" / "LongTail" / "LTV2-I08" / "failure.json"
            )
            write_json(
                failure_path,
                {"candidate": "LTV2-I08", "error": "Unity build failed"},
            )
            failed = shader_progress.load_research_snapshot(root)
            write_json(
                root / "Evidence" / "LongTail" / "LTV2-I10" / "result.json",
                {
                    "candidate": "LTV2-I10",
                    "valid_candidate_cell": True,
                    "summary": {"visual_ssim": 1.0},
                    "raw_evidence": {},
                },
            )

            measured = shader_progress.load_research_snapshot(root)

            assert failed is not None and measured is not None
            failure = next(
                item for item in measured.state["candidates"] if item["id"] == "LTV2-I08"
            )
            self.assertEqual("failed", failure["status"])
            self.assertEqual(
                ["Evidence/LongTail/LTV2-I08/failure.json"],
                failure["evidence_refs"],
            )
            self.assertIn("Unity build failed", failure["metrics"]["error"])
            self.assertNotEqual(failed.fingerprint, measured.fingerprint)
            self.assertIn("candidate: LTV2-I10 (measured)", measured.projection)

    def test_live_evidence_overrides_stale_ledger_fields_but_keeps_ledger_context(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root)
            write_json(
                root / "benchmark" / "candidate-results.json",
                {
                    "results": [
                        {
                            "candidate": "A28",
                            "status": "measuring",
                            "decision": "keep semantic context",
                            "source_sha256": "stale-ledger",
                            "summary": {"visual_ssim": 0.9},
                        }
                    ]
                },
            )
            write_json(
                root / "Evidence" / "LongTail" / "A28" / "result.json",
                {
                    "candidate": "A28",
                    "valid_candidate_cell": True,
                    "summary": {"visual_ssim": 1.0},
                    "raw_evidence": {
                        "input_manifest": {"sha256": "fresh-evidence"}
                    },
                },
            )

            snapshot = shader_progress.load_research_snapshot(root)

            assert snapshot is not None
            candidate = next(
                item for item in snapshot.state["candidates"] if item["id"] == "A28"
            )
            self.assertEqual("measured", candidate["status"])
            self.assertEqual(1.0, candidate["metrics"]["visual_ssim"])
            self.assertEqual("fresh-evidence", candidate["source_fingerprint"])
            self.assertEqual("keep semantic context", candidate["decision"])

    def test_fingerprint_depends_on_json_meaning_not_whitespace(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root)
            first = shader_progress.load_research_snapshot(root)
            result_path = root / "benchmark" / "architecture-result.json"
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            write_json(result_path, payload, indent=None)

            second = shader_progress.load_research_snapshot(root)

            assert first is not None and second is not None
            self.assertEqual(first.fingerprint, second.fingerprint)
            self.assertEqual(first.state, second.state)

    def test_missing_research_sources_do_not_invent_a_projection(self):
        with tempfile.TemporaryDirectory() as raw:
            self.assertIsNone(shader_progress.load_research_snapshot(Path(raw)))

    def test_change_mode_is_expand_deepen_or_live_guard_not_a_quota(self):
        previous = {
            "contract": {"claims_permitted": False},
            "result": {
                "claims_permitted": False,
                "frontier": ["A26"],
                "unresolved": 1,
                "saturation_rule_met": False,
            },
            "candidates": [{"id": "A26", "status": "measured"}],
        }
        expanded = json.loads(json.dumps(previous))
        expanded["candidates"].append({"id": "A28", "status": "planned"})
        deepened = json.loads(json.dumps(previous))
        deepened["candidates"][0]["status"] = "measured-inconclusive"
        guarded = json.loads(json.dumps(previous))
        guarded["result"]["claims_permitted"] = True

        self.assertEqual(shader_progress.classify_change(previous, expanded), "expand")
        self.assertEqual(shader_progress.classify_change(previous, deepened), "deepen")
        self.assertEqual(shader_progress.classify_change(previous, guarded), "guard")


class ShaderSemanticTriggerTests(unittest.TestCase):
    def test_live_evidence_result_schedules_semantic_review_without_ledger(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root)
            (root / "benchmark" / "candidate-results.json").unlink()
            settings = settings_for(root)
            profiles.configure_workspace_profile(
                settings.paths.data_dir,
                root,
                domain="shader",
                stage="optimize",
                provider="grok",
                model="",
                review_mode="all",
                reasoning_effort="medium",
            )
            scheduled = []
            adapter = CodexAdapter(
                FakeCore(settings),
                schedule_strategy=lambda work: scheduled.append(work) or True,
            )
            event = {
                "hook_event_name": "PostToolUse",
                "session_id": "shader-live-evidence",
                "turn_id": "turn",
                "cwd": str(root),
                "tool_name": "verify_candidate",
                "tool_input": {"candidate": "LTV2-I10"},
                "tool_response": {"success": True},
            }
            adapter.process(event)
            write_json(
                root / "Evidence" / "LongTail" / "LTV2-I10" / "result.json",
                {
                    "candidate": "LTV2-I10",
                    "family": "hex-coordinate",
                    "valid_candidate_cell": True,
                    "summary": {
                        "visual_ssim": 1.0,
                        "phases": {
                            "gallery-24-shields": {
                                "incremental_gpu_median_ms": 1.3279
                            }
                        },
                    },
                    "raw_evidence": {},
                },
            )

            adapter.process(event)

            self.assertEqual(1, len(scheduled))
            self.assertEqual(
                "shader-research-deepen", scheduled[0]["checkpoint"]["trigger"]
            )
            self.assertIn("candidate: LTV2-I10 (measured)", scheduled[0]["checkpoint"]["context"])
            self.assertIn("live evidence: observed=1; valid=1; failed=0", scheduled[0]["checkpoint"]["context"])

    def test_shader_workspace_keeps_generic_strategy_fallback_when_research_state_is_static(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root)
            settings = settings_for(root)
            profiles.configure_workspace_profile(
                settings.paths.data_dir,
                root,
                domain="shader",
                stage="optimize",
                provider="grok",
                model="",
                review_mode="all",
                reasoning_effort="medium",
            )
            scheduled = []
            adapter = CodexAdapter(
                FakeCore(settings),
                schedule_strategy=lambda work: scheduled.append(work) or True,
            )

            for index in range(8):
                adapter.process(
                    {
                        "hook_event_name": "PostToolUse",
                        "session_id": "shader-semantic",
                        "turn_id": "turn",
                        "cwd": str(root),
                        "tool_name": f"verify_step_{index}",
                        "tool_input": {"step": index},
                        "tool_response": {"success": True},
                    }
                )

            self.assertEqual(scheduled, [])

    def test_research_source_change_schedules_one_semantic_review(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            write_research_sources(root)
            settings = settings_for(root)
            profiles.configure_workspace_profile(
                settings.paths.data_dir,
                root,
                domain="shader",
                stage="optimize",
                provider="grok",
                model="",
                review_mode="all",
                reasoning_effort="medium",
            )
            scheduled = []
            adapter = CodexAdapter(
                FakeCore(settings),
                schedule_strategy=lambda work: scheduled.append(work) or True,
            )
            event = {
                "hook_event_name": "PostToolUse",
                "session_id": "shader-change",
                "turn_id": "turn",
                "cwd": str(root),
                "tool_name": "verify_step",
                "tool_input": {"step": 1},
                "tool_response": {"success": True},
            }
            adapter.process(event)  # Establish the rebuildable baseline.
            write_research_sources(root, result_status="candidate-resolved")

            adapter.process(event)
            adapter.process(event)

            self.assertEqual(len(scheduled), 1)
            self.assertEqual(
                scheduled[0]["checkpoint"]["trigger"], "shader-research-deepen"
            )
            self.assertIn("candidate-resolved", scheduled[0]["checkpoint"]["context"])
            self.assertIn(
                "[candidate decision material]",
                scheduled[0]["checkpoint"]["context"],
            )
            self.assertIn(
                "[latest direct evidence]",
                scheduled[0]["checkpoint"]["context"],
            )
            self.assertEqual(
                ["carmack|executed-work-elimination"],
                scheduled[0]["route_signals"],
            )
            self.assertEqual(
                "carmack:executed-work-elimination", scheduled[0]["gap_key"]
            )

            worker = CodexAdapter(WorkerCore(settings))
            worker._run_strategy_payload(scheduled[0])
            session = SessionRef(
                "codex_cli", "shader-change", "turn", str(root), str(root)
            )
            progress = json.loads(
                storage.state_path(
                    settings.paths.data_dir, session, "progress"
                ).read_text(encoding="utf-8")
            )
            self.assertEqual(
                progress["shader_research_fingerprint"],
                scheduled[0]["research_fingerprint"],
            )
            self.assertTrue(
                storage.claim_strategy_run(
                    settings.paths.data_dir, session, "after-worker"
                )
            )
            storage.release_strategy_run(
                settings.paths.data_dir, session, "after-worker"
            )

            write_research_sources(root, result_status="candidate-archived")
            adapter.process(event)
            progress = json.loads(
                storage.state_path(
                    settings.paths.data_dir, session, "progress"
                ).read_text(encoding="utf-8")
            )

            self.assertEqual(len(scheduled), 1)
            self.assertEqual(
                "unchanged-evidence-gap",
                progress["shader_research_suppressions"][-1]["reason"],
            )


if __name__ == "__main__":
    unittest.main()
