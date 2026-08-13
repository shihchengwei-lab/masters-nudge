#!/usr/bin/env python3
"""Analyze Stage 1 control/positive-control task sensitivity."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


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
        and any(item.get("name") == "target_resolution" for item in components)
        and all(isinstance(item.get("passed"), bool) for item in components)
    )


def condition_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if grader_valid(row)]
    return {
        "runs": len(rows),
        "agent_valid": sum(agent_valid(row) for row in rows),
        "grader_valid": len(valid),
        "safe_target_successes": sum(bool(row["grader"].get("safe_target_resolution")) for row in valid),
        "full_task_passes": sum(bool(row["grader"].get("passed")) for row in valid),
        "total_cost_usd": round(sum(float((row.get("agent") or {}).get("total_cost_usd") or 0) for row in rows), 6),
        "mean_turns": round(sum(int((row.get("agent") or {}).get("num_turns") or 0) for row in rows) / len(rows), 2) if rows else 0,
        "mean_wall_ms": round(sum(int(row.get("wall_ms") or 0) for row in rows) / len(rows)) if rows else 0,
    }


def summarize(rows: list[dict[str, Any]], expected_keys: set[tuple[str, int, str]]) -> dict[str, Any]:
    actual_keys = {(row["task_id"], int(row["repeat"]), row["condition"]) for row in rows}
    duplicate_keys = len(actual_keys) != len(rows)
    by_key = {(row["task_id"], int(row["repeat"]), row["condition"]): row for row in rows}
    task_pairs: dict[str, list[dict[str, Any]]] = defaultdict(list)
    wins = losses = both_success = both_fail = 0
    for task_id, repeat, condition in sorted(actual_keys):
        if condition != "positive_control":
            continue
        positive = by_key[(task_id, repeat, "positive_control")]
        control = by_key.get((task_id, repeat, "control"))
        if control is None:
            continue
        positive_pass = bool((positive.get("grader") or {}).get("safe_target_resolution"))
        control_pass = bool((control.get("grader") or {}).get("safe_target_resolution"))
        if positive_pass and not control_pass:
            outcome = "win"
            wins += 1
        elif control_pass and not positive_pass:
            outcome = "loss"
            losses += 1
        elif positive_pass:
            outcome = "both_success"
            both_success += 1
        else:
            outcome = "both_fail"
            both_fail += 1
        task_pairs[task_id].append({"repeat": repeat, "outcome": outcome})

    by_task = {}
    for task_id in sorted({row["task_id"] for row in rows}):
        selected = [row for row in rows if row["task_id"] == task_id]
        control_rows = [row for row in selected if row["condition"] == "control"]
        positive_rows = [row for row in selected if row["condition"] == "positive_control"]
        control_success = sum(bool((row.get("grader") or {}).get("safe_target_resolution")) for row in control_rows)
        positive_success = sum(bool((row.get("grader") or {}).get("safe_target_resolution")) for row in positive_rows)
        task_wins = sum(item["outcome"] == "win" for item in task_pairs[task_id])
        task_losses = sum(item["outcome"] == "loss" for item in task_pairs[task_id])
        accepted = bool(
            control_success in {1, 2}
            and positive_success >= 2
            and task_wins - task_losses >= 1
        )
        by_task[task_id] = {
            "control_safe_target": control_success,
            "positive_control_safe_target": positive_success,
            "paired_wins": task_wins,
            "paired_losses": task_losses,
            "accepted": accepted,
            "pairs": sorted(task_pairs[task_id], key=lambda item: item["repeat"]),
        }

    integrity = bool(
        len(rows) == 36
        and not duplicate_keys
        and actual_keys == expected_keys
        and sum(agent_valid(row) for row in rows) >= 35
        and sum(grader_valid(row) for row in rows) == 36
    )
    accepted_tasks = sum(item["accepted"] for item in by_task.values())
    conditions = {
        condition: condition_stats([row for row in rows if row["condition"] == condition])
        for condition in ("control", "positive_control")
    }
    return {
        "rows": len(rows),
        "conditions": conditions,
        "paired": {
            "pairs": wins + losses + both_success + both_fail,
            "wins": wins,
            "losses": losses,
            "both_success": both_success,
            "both_fail": both_fail,
            "net": wins - losses,
        },
        "by_task": by_task,
        "gates": {
            "run_integrity": {
                "passed": integrity,
                "measured": f"rows {len(rows)}/36; agent-valid {sum(agent_valid(row) for row in rows)}/36; grader-valid {sum(grader_valid(row) for row in rows)}/36",
            },
            "all_six_patterns_accepted": {
                "passed": accepted_tasks == 6,
                "measured": f"accepted tasks {accepted_tasks}/6",
            },
            "synthetic_fixture_viability_floor": {
                "passed": accepted_tasks >= 4,
                "measured": f"accepted tasks {accepted_tasks}/6; stop if fewer than 4",
            },
        },
        "stage1_passed": bool(integrity and accepted_tasks == 6),
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
    summary = summarize(load_rows(args.runs), expected_keys)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"stage 1 passed: {summary['stage1_passed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
