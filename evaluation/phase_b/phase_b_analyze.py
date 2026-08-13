#!/usr/bin/env python3
"""Aggregate objective Phase B task outcomes after all identities are known."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def agent_valid(row: dict[str, Any]) -> bool:
    agent = row.get("agent") or {}
    return bool(
        agent.get("returncode") == 0
        and not agent.get("timed_out")
        and agent.get("result_type") == "result"
        and agent.get("subtype") == "success"
        and agent.get("is_error") is False
    )


def grader_valid(row: dict[str, Any]) -> bool:
    grader = row.get("grader") or {}
    components = grader.get("components")
    return bool(
        isinstance(components, list)
        and components
        and grader.get("components_total") == len(components)
        and all(isinstance(item.get("passed"), bool) for item in components)
    )


def condition_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid_grades = [row for row in rows if grader_valid(row)]
    return {
        "runs": len(rows),
        "agent_valid": sum(agent_valid(row) for row in rows),
        "grader_valid": len(valid_grades),
        "task_passes": sum(bool(row["grader"].get("passed")) for row in valid_grades),
        "components_passed": sum(int(row["grader"].get("components_passed") or 0) for row in valid_grades),
        "components_total": sum(int(row["grader"].get("components_total") or 0) for row in valid_grades),
        "total_cost_usd": round(
            sum(float((row.get("agent") or {}).get("total_cost_usd") or 0) for row in rows), 6
        ),
        "mean_turns": round(
            sum(int((row.get("agent") or {}).get("num_turns") or 0) for row in rows) / len(rows),
            2,
        ) if rows else 0,
        "mean_wall_ms": round(sum(int(row.get("wall_ms") or 0) for row in rows) / len(rows)) if rows else 0,
    }


def exact_one_sided_p(wins: int, losses: int) -> float | None:
    discordant = wins + losses
    if not discordant:
        return None
    probability = sum(
        math.comb(discordant, k) for k in range(wins, discordant + 1)
    ) / (2**discordant)
    return round(probability, 6)


def summarize(
    rows: list[dict[str, Any]],
    expected_keys: set[tuple[str, int, str]] | None = None,
) -> dict[str, Any]:
    if expected_keys is None:
        expected_keys = {
            (task_id, repeat, condition)
            for task_id in {row["task_id"] for row in rows}
            for repeat in {row["repeat"] for row in rows}
            for condition in ("control", "treatment")
        }
    actual_keys = {(row["task_id"], row["repeat"], row["condition"]) for row in rows}
    duplicate_keys = len(actual_keys) != len(rows)
    by_key = {(row["task_id"], row["repeat"], row["condition"]): row for row in rows}

    wins = losses = both_pass = both_fail = 0
    component_delta = 0
    task_net: dict[str, int] = defaultdict(int)
    pairs = []
    for task_id, repeat, condition in sorted(actual_keys):
        if condition != "treatment":
            continue
        treatment = by_key[(task_id, repeat, "treatment")]
        control = by_key.get((task_id, repeat, "control"))
        if control is None:
            continue
        treatment_pass = bool((treatment.get("grader") or {}).get("passed"))
        control_pass = bool((control.get("grader") or {}).get("passed"))
        if treatment_pass and not control_pass:
            outcome = "win"
            wins += 1
            task_net[task_id] += 1
        elif control_pass and not treatment_pass:
            outcome = "loss"
            losses += 1
            task_net[task_id] -= 1
        elif treatment_pass:
            outcome = "both_pass"
            both_pass += 1
        else:
            outcome = "both_fail"
            both_fail += 1
        treatment_components = int((treatment.get("grader") or {}).get("components_passed") or 0)
        control_components = int((control.get("grader") or {}).get("components_passed") or 0)
        delta = treatment_components - control_components
        component_delta += delta
        pairs.append(
            {
                "task_id": task_id,
                "repeat": repeat,
                "outcome": outcome,
                "component_delta": delta,
            }
        )

    conditions = {
        condition: condition_stats([row for row in rows if row["condition"] == condition])
        for condition in ("control", "treatment")
    }
    by_task = {}
    for task_id in sorted({row["task_id"] for row in rows}):
        selected = [row for row in rows if row["task_id"] == task_id]
        by_task[task_id] = {
            condition: condition_stats([row for row in selected if row["condition"] == condition])
            for condition in ("control", "treatment")
        }
        by_task[task_id]["net_paired_wins"] = task_net[task_id]

    treatment_passes = conditions["treatment"]["task_passes"]
    control_passes = conditions["control"]["task_passes"]
    integrity_ok = (
        len(rows) == 36
        and not duplicate_keys
        and actual_keys == expected_keys
        and sum(agent_valid(row) for row in rows) >= 35
        and sum(grader_valid(row) for row in rows) == 36
    )
    gates = {
        "run_integrity": {
            "passed": integrity_ok,
            "measured": f"rows {len(rows)}/36; agent-valid {sum(agent_valid(row) for row in rows)}/36; grader-valid {sum(grader_valid(row) for row in rows)}/36",
        },
        "treatment_not_lower_full_task_success": {
            "passed": treatment_passes >= control_passes,
            "measured": f"treatment {treatment_passes}/18; control {control_passes}/18",
        },
        "paired_net_benefit": {
            "passed": wins - losses >= 3,
            "measured": f"wins {wins}; losses {losses}; net {wins - losses}",
        },
        "benefit_spans_tasks": {
            "passed": sum(net > 0 for net in task_net.values()) >= 2,
            "measured": f"tasks with net benefit {sum(net > 0 for net in task_net.values())}/6",
        },
        "no_task_majority_harm": {
            "passed": all(net > -2 for net in task_net.values()),
            "measured": json.dumps(dict(sorted(task_net.items())), ensure_ascii=False),
        },
    }
    return {
        "rows": len(rows),
        "conditions": conditions,
        "paired": {
            "pairs": len(pairs),
            "wins": wins,
            "losses": losses,
            "both_pass": both_pass,
            "both_fail": both_fail,
            "component_pass_delta": component_delta,
            "exact_one_sided_p": exact_one_sided_p(wins, losses),
            "details": pairs,
        },
        "by_task": by_task,
        "gates": gates,
        "positive_pilot_signal": all(item["passed"] for item in gates.values()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    expected_keys = {
        (row["task_id"], int(row["repeat"]), row["condition"])
        for row in manifest["job_keys"]
    }
    summary = summarize(load_rows(args.runs), expected_keys=expected_keys)
    args.output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"positive pilot signal: {summary['positive_pilot_signal']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
