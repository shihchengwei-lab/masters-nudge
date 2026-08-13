#!/usr/bin/env python3
"""Verify that each candidate is public-green/hidden-red and each reference passes."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from evaluation import quality_eval
from evaluation.phase_b import phase_b_grade, phase_b_tasks


def validate(spec_path: Path) -> dict:
    spec = phase_b_tasks.load_spec(spec_path)
    phase_b_tasks.validate_assets(spec)
    rows = []
    for fixture in spec["fixtures"]:
        routed = {**fixture, "expected_effective_lens": fixture["lens"]}
        route = quality_eval.fixture_routes(
            routed, quality_eval.build_packet(routed)
        )["effective"]
        with tempfile.TemporaryDirectory(prefix="masters-nudge-phase-b-validate-") as raw:
            root = Path(raw)
            candidate_workspace = phase_b_tasks.materialize(
                fixture["id"], root / "candidate", state="candidate"
            )
            reference_workspace = phase_b_tasks.materialize(
                fixture["id"], root / "reference", state="reference"
            )
            candidate = phase_b_grade.grade(fixture["id"], candidate_workspace)
            reference = phase_b_grade.grade(fixture["id"], reference_workspace)
        public_green = bool(candidate["components"] and candidate["components"][0]["passed"])
        valid = bool(
            route.effective_lens == fixture["lens"]
            and public_green
            and not candidate["passed"]
            and reference["passed"]
        )
        rows.append(
            {
                "task_id": fixture["id"],
                "expected_lens": fixture["lens"],
                "actual_lens": route.effective_lens,
                "candidate_public_green": public_green,
                "candidate_hidden_passed": candidate["passed"],
                "candidate_components": f"{candidate['components_passed']}/{candidate['components_total']}",
                "candidate_failures": [
                    item["name"] for item in candidate["components"] if not item["passed"]
                ],
                "reference_hidden_passed": reference["passed"],
                "reference_components": f"{reference['components_passed']}/{reference['components_total']}",
                "valid": valid,
            }
        )
    return {
        "schema_version": 1,
        "tasks": rows,
        "all_valid": all(row["valid"] for row in rows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, default=phase_b_tasks.DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = validate(args.spec)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"all task oracles valid: {result['all_valid']}")
    return 0 if result["all_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
