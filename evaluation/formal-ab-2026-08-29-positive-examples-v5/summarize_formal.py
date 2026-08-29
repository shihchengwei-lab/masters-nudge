from __future__ import annotations

import json
import os
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
WORK_ROOT = Path(os.environ.get(
    "MASTERS_NUDGE_FORMAL_AB_ROOT",
    r"C:\Users\kk789\AppData\Local\Temp\masters-nudge-formal-ab-20260829-positive-v5",
))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    safety = read_json(HERE / "results.json")
    taste = read_json(HERE / "taste-results.json")
    mechanism_totals: Counter[str] = Counter()
    lenses: Counter[str] = Counter()
    telemetry_status: Counter[str] = Counter()
    telemetry_stages: Counter[str] = Counter()
    error_kinds: Counter[str] = Counter()
    latencies: list[int] = []
    per_task = []
    arm_seconds = {"a": [], "b": []}
    arm_tokens = {"a": [], "b": []}
    taste_dimensions = ("choice_specificity", "load_bearing_principle", "trajectory_influence", "review_friction")
    taste_dimension_totals = {
        arm: {dimension: sum(verdict[arm][dimension] for verdict in taste["verdicts"]) for dimension in taste_dimensions}
        for arm in ("arm_a", "arm_b")
    }
    taste_confidence = Counter(verdict["confidence"] for verdict in taste["verdicts"])

    for task in safety["tasks"]:
        key = task["task_key"]
        nudge = task["arm_b"]["score"].get("nudge") or {}
        for name in ("findings", "injected", "response_observations"):
            mechanism_totals[name] += int(nudge.get(name, 0))
        mechanism_totals["nudges"] += len(nudge.get("nudges") or [])
        lenses.update(nudge.get("lenses") or [])

        nudge_root = WORK_ROOT / "tasks" / key / "runs" / "b" / "nudge-data"
        telemetry = []
        telemetry_path = nudge_root / "review-telemetry.jsonl"
        if telemetry_path.exists():
            telemetry = [json.loads(line) for line in telemetry_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        deviations = 0
        for event in telemetry:
            telemetry_status[str(event.get("status"))] += 1
            telemetry_stages[str(event.get("stage"))] += 1
            if event.get("error_kind"):
                error_kinds[str(event["error_kind"])] += 1
            deviations += len(event.get("contract_deviations") or [])
            if isinstance(event.get("latency_ms"), int):
                latencies.append(event["latency_ms"])
        mechanism_totals["contract_deviations"] += deviations
        attempts = len(list(nudge_root.glob("*.review-attempts/*.json")))
        mechanism_totals["review_attempts"] += attempts

        for arm in ("a", "b"):
            run = task[f"arm_{arm}"]["run"]
            arm_seconds[arm].append(float(run["wall_time_seconds"]))
            arm_tokens[arm].append(int((run.get("usage") or {}).get("output_tokens", 0)))

        per_task.append({
            "task_key": key,
            "safety_a": task["arm_a"]["score"]["passed"],
            "safety_b": task["arm_b"]["score"]["passed"],
            "nudge_findings": int(nudge.get("findings", 0)),
            "nudge_injected": int(nudge.get("injected", 0)),
            "response_observations": int(nudge.get("response_observations", 0)),
            "lenses": nudge.get("lenses") or [],
            "review_attempts": attempts,
            "telemetry_events": len(telemetry),
            "contract_deviations": deviations,
        })

    result = {
        "schema_version": 1,
        "safety": safety["counts"],
        "taste": {
            **taste["summary"],
            "dimension_totals": taste_dimension_totals,
            "confidence": dict(taste_confidence),
            "ceiling_effect": all(
                taste_dimension_totals[arm][dimension] == 20
                for arm in ("arm_a", "arm_b")
                for dimension in taste_dimensions[:3]
            ),
        },
        "mechanism": {
            **dict(mechanism_totals),
            "lenses": dict(lenses),
            "telemetry_status": dict(telemetry_status),
            "telemetry_stages": dict(telemetry_stages),
            "error_kinds": dict(error_kinds),
            "provider_latency_ms_median": statistics.median(latencies) if latencies else None,
            "provider_latency_ms_max": max(latencies) if latencies else None,
        },
        "operational": {
            "arm_a_wall_seconds_total": round(sum(arm_seconds["a"]), 3),
            "arm_b_wall_seconds_total": round(sum(arm_seconds["b"]), 3),
            "arm_a_wall_seconds_median": round(statistics.median(arm_seconds["a"]), 3),
            "arm_b_wall_seconds_median": round(statistics.median(arm_seconds["b"]), 3),
            "arm_a_output_tokens_total": sum(arm_tokens["a"]),
            "arm_b_output_tokens_total": sum(arm_tokens["b"]),
        },
        "per_task": per_task,
        "interpretation": {
            "confirmed": "B produced and injected seven dynamic findings, but the blinded primary taste rating found no material paired difference; safety was exactly tied.",
            "not_supported": "This ten-task run does not support a claim that Nudge injected observable engineering taste into the main model trajectory.",
            "not_a_claim": "The run is descriptive and too small for a causal effect estimate or a general no-effect conclusion."
        }
    }
    (HERE / "formal-summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
