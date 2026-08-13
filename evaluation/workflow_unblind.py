#!/usr/bin/env python3
"""Join frozen blind judgments to identities and compute workflow-eval gates."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def expand_judgments(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    expanded: dict[str, dict[str, Any]] = {}
    for category, values in payload["categories"].items():
        ids = values["ids"]
        judgment = {key: value for key, value in values.items() if key != "ids"}
        judgment["category"] = category
        for blind_id in ids:
            if blind_id in expanded:
                raise ValueError(f"duplicate judgment: {blind_id}")
            expanded[blind_id] = dict(judgment)

    flags: dict[str, list[str]] = defaultdict(list)
    for flag, values in payload.get("diagnostic_flags", {}).items():
        for blind_id in values["ids"]:
            flags[blind_id].append(flag)
    for blind_id, judgment in expanded.items():
        judgment["flags"] = sorted(flags.get(blind_id, []))
    return expanded


def join_rows(
    review: list[dict[str, Any]],
    identities: list[dict[str, Any]],
    raw_rows: list[dict[str, Any]],
    judgments: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    identity_by_id = {row["blind_id"]: row for row in identities}
    raw_by_key = {
        (row["fixture_id"], row["condition"], row["repeat"]): row
        for row in raw_rows
    }
    if len(identity_by_id) != len(identities) or len(raw_by_key) != len(raw_rows):
        raise ValueError("duplicate identity or raw-result key")
    if set(identity_by_id) != set(judgments):
        raise ValueError("identity and judgment IDs differ")

    joined: list[dict[str, Any]] = []
    for blinded in review:
        blind_id = blinded["blind_id"]
        identity = identity_by_id[blind_id]
        key = (identity["fixture_id"], identity["condition"], identity["repeat"])
        raw = raw_by_key[key]
        if raw["status"] != blinded["observed_status"] or raw["finding"] != blinded["nudge"]:
            raise ValueError(f"blind/raw mismatch: {blind_id}")
        joined.append(
            {
                "blind_id": blind_id,
                **identity,
                "expected_status": blinded["expected_status"],
                "intended_lens": blinded["intended_lens"],
                "workflow_target": blinded["workflow_target"],
                "observed_status": blinded["observed_status"],
                "nudge": blinded["nudge"],
                "chars": blinded["chars"],
                "raw_chars": blinded["raw_chars"],
                "provider_success": raw["provider_success"],
                "raw_schema_valid": raw["raw_schema_valid"],
                "latency_ms": raw["latency_ms"],
                "usage": raw.get("usage") or {},
                "judgment": judgments[blind_id],
            }
        )
    if len(joined) != len(raw_rows):
        raise ValueError("joined row count differs from raw results")
    return joined


def condition_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in rows if row["expected_status"] == "finding"]
    clean = [row for row in rows if row["expected_status"] == "no_finding"]
    findings = [row for row in rows if row["observed_status"] == "finding"]
    usage_keys = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")
    return {
        "calls": len(rows),
        "provider_success": sum(bool(row["provider_success"]) for row in rows),
        "raw_schema_valid": sum(bool(row["raw_schema_valid"]) for row in rows),
        "seeded_positive_calls": len(positives),
        "finding_recall": sum(row["observed_status"] == "finding" for row in positives),
        "seeded_clean_calls": len(clean),
        "correct_silence": sum(row["observed_status"] == "no_finding" for row in clean),
        "human_valid_positive": sum(bool(row["judgment"]["decision_valid"]) for row in positives),
        "workflow_level_positive": sum(
            row["observed_status"] == "finding" and row["judgment"]["workflow_level"] is True
            for row in positives
        ),
        "lens_aligned_positive": sum(
            row["observed_status"] == "finding" and row["judgment"]["lens_aligned"] is True
            for row in positives
        ),
        "complete_positive": sum(
            row["observed_status"] == "finding" and row["judgment"]["complete"] is True
            for row in positives
        ),
        "local_artifact_only_positive": sum(
            row["observed_status"] == "finding" and row["judgment"]["local_artifact_only"] is True
            for row in positives
        ),
        "human_valid_all": sum(bool(row["judgment"]["decision_valid"]) for row in rows),
        "findings": len(findings),
        "cap_hits": sum(row["raw_chars"] == 52 for row in findings),
        "incomplete_findings": sum(row["judgment"]["complete"] is False for row in findings),
        "mean_finding_chars": round(sum(row["chars"] for row in findings) / len(findings), 2) if findings else 0,
        "mean_latency_ms": round(sum(row["latency_ms"] for row in rows) / len(rows)) if rows else 0,
        "usage": {
            key: sum(int(row["usage"].get(key) or 0) for row in rows)
            for key in usage_keys
        },
    }


def paired_stats(rows: list[dict[str, Any]], treatment: str, control: str) -> dict[str, int]:
    by_key = {(row["fixture_id"], row["repeat"], row["condition"]): row for row in rows}
    wins = losses = both_valid = both_invalid = 0
    for fixture_id, repeat, condition in by_key:
        if condition != treatment:
            continue
        treated = by_key[(fixture_id, repeat, treatment)]
        controlled = by_key.get((fixture_id, repeat, control))
        if controlled is None:
            continue
        treatment_valid = bool(treated["judgment"]["decision_valid"])
        control_valid = bool(controlled["judgment"]["decision_valid"])
        if treatment_valid and not control_valid:
            wins += 1
        elif control_valid and not treatment_valid:
            losses += 1
        elif treatment_valid:
            both_valid += 1
        else:
            both_invalid += 1
    pairs = wins + losses + both_valid + both_invalid
    return {
        "pairs": pairs,
        "wins": wins,
        "losses": losses,
        "both_valid": both_valid,
        "both_invalid": both_invalid,
        "treatment_invalid_minus_control_invalid": losses - wins,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_condition = {
        condition: condition_stats([row for row in rows if row["condition"] == condition])
        for condition in sorted({row["condition"] for row in rows})
    }
    effective = by_condition["effective"]
    baseline_pair = paired_stats(rows, "effective", "baseline")
    primary_pair = paired_stats(rows, "effective", "primary")
    gates = {
        "transport_and_schema": {
            "passed": effective["provider_success"] >= 35 and effective["raw_schema_valid"] == 36,
            "measured": f"provider {effective['provider_success']}/36; schema {effective['raw_schema_valid']}/36",
        },
        "finding_recall": {
            "passed": effective["finding_recall"] >= 21,
            "measured": f"{effective['finding_recall']}/{effective['seeded_positive_calls']}",
        },
        "correct_silence": {
            "passed": effective["correct_silence"] >= 11,
            "measured": f"{effective['correct_silence']}/{effective['seeded_clean_calls']}",
        },
        "human_valid_workflow_warning": {
            "passed": effective["human_valid_positive"] >= 20,
            "measured": f"{effective['human_valid_positive']}/{effective['seeded_positive_calls']}",
        },
        "lens_alignment": {
            "passed": effective["lens_aligned_positive"] >= 20,
            "measured": f"{effective['lens_aligned_positive']}/{effective['seeded_positive_calls']}",
        },
        "not_local_artifact_only": {
            "passed": effective["local_artifact_only_positive"] <= 2,
            "measured": f"{effective['local_artifact_only_positive']}/{effective['seeded_positive_calls']} local-only",
        },
        "no_material_regression_vs_baseline": {
            "passed": baseline_pair["treatment_invalid_minus_control_invalid"] <= 2,
            "measured": f"invalid delta {baseline_pair['treatment_invalid_minus_control_invalid']}; losses {baseline_pair['losses']}",
        },
        "specialist_no_material_regression_vs_primary": {
            "passed": primary_pair["losses"] <= 1,
            "measured": f"losses {primary_pair['losses']}/{primary_pair['pairs']}",
        },
    }
    by_lens = {
        lens: condition_stats(
            [row for row in rows if row["condition"] == "effective" and row["intended_lens"] == lens]
        )
        for lens in sorted({row["intended_lens"] for row in rows})
    }
    return {
        "rows": len(rows),
        "conditions": by_condition,
        "paired": {
            "effective_vs_baseline": baseline_pair,
            "effective_vs_primary": primary_pair,
        },
        "effective_by_lens": by_lens,
        "gates": gates,
        "all_gates_passed": all(gate["passed"] for gate in gates.values()),
        "cap_hits": [
            {
                "blind_id": row["blind_id"],
                "fixture_id": row["fixture_id"],
                "condition": row["condition"],
                "repeat": row["repeat"],
                "complete": row["judgment"]["complete"],
                "nudge": row["nudge"],
            }
            for row in rows
            if row["observed_status"] == "finding" and row["raw_chars"] == 52
        ],
        "contaminated_clean_findings": [
            {
                "blind_id": row["blind_id"],
                "fixture_id": row["fixture_id"],
                "condition": row["condition"],
                "repeat": row["repeat"],
                "nudge": row["nudge"],
            }
            for row in rows
            if "seeded_clean_fixture_contamination" in row["judgment"]["flags"]
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--identity-map", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--judgments", type=Path, required=True)
    parser.add_argument("--adjudicated-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    review = load_json(args.review)
    identities = load_json(args.identity_map)
    raw_rows = load_jsonl(args.results)
    judgment_payload = load_json(args.judgments)
    judgments = expand_judgments(judgment_payload)
    joined = join_rows(review, identities, raw_rows, judgments)
    summary = summarize(joined)
    args.adjudicated_output.write_text(
        json.dumps(joined, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.summary_output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"unblinded {len(joined)} rows")
    print(f"all gates passed: {summary['all_gates_passed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
