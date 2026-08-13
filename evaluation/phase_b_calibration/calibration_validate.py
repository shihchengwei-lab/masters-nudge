#!/usr/bin/env python3
"""Validate calibration candidates, acceptable solutions, and near misses."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from evaluation.phase_b_calibration import calibration_grade, calibration_tasks


def component_pass(result: dict, name: str) -> bool:
    return bool(next(item for item in result["components"] if item["name"] == name)["passed"])


def validate_fixture(task_id: str, root: Path) -> dict:
    states = {}
    for state in calibration_tasks.ALL_STATES:
        workspace = root / f"{task_id}-{state}"
        calibration_tasks.materialize(task_id, workspace, state=state)
        states[state] = calibration_grade.grade(task_id, workspace)

    candidate = states["candidate"]
    reference = states["reference"]
    alternative = states["alternative"]
    near_misses = [states["near_miss_1"], states["near_miss_2"]]
    checks = {
        "candidate_public_green": component_pass(candidate, "public_tests"),
        "candidate_target_red": not component_pass(candidate, "target_resolution"),
        "reference_green": bool(reference["passed"]),
        "alternative_green": bool(alternative["passed"]),
        "near_misses_public_green": all(component_pass(row, "public_tests") for row in near_misses),
        "near_misses_target_red": all(not component_pass(row, "target_resolution") for row in near_misses),
    }
    return {
        "task_id": task_id,
        "valid": all(checks.values()),
        "checks": checks,
        "states": {
            state: {
                "passed": result["passed"],
                "safe_target_resolution": result["safe_target_resolution"],
                "components": {
                    item["name"]: {"passed": item["passed"], "detail": item["detail"]}
                    for item in result["components"]
                },
            }
            for state, result in states.items()
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, default=calibration_tasks.DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec = calibration_tasks.load_spec(args.spec)
    calibration_tasks.validate_assets(spec)
    with tempfile.TemporaryDirectory(prefix="masters-nudge-calibration-validate-") as temp:
        root = Path(temp)
        tasks = [validate_fixture(item["id"], root) for item in spec["fixtures"]]
    payload = {
        "schema_version": 1,
        "task_set": spec["task_set"],
        "all_valid": all(item["valid"] for item in tasks),
        "tasks": tasks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"all valid: {payload['all_valid']}")
    return 0 if payload["all_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
