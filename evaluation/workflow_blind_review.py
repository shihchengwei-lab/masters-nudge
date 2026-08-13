#!/usr/bin/env python3
"""Create a condition-blind review packet and keep the identity map separate."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from evaluation import quality_eval


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def raw_finding_length(raw_output: str) -> int:
    payload = quality_eval._structured_raw(raw_output)
    finding = payload.get("finding") if payload else ""
    return len(finding) if isinstance(finding, str) else 0


def build_blind_records(
    fixtures: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    *,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fixture_map = {fixture["id"]: fixture for fixture in fixtures}
    candidates = list(rows)
    random.Random(seed).shuffle(candidates)

    review: list[dict[str, Any]] = []
    identity_map: list[dict[str, Any]] = []
    for index, row in enumerate(candidates, 1):
        fixture = fixture_map[row["fixture_id"]]
        blind_id = f"W{index:03d}"
        oracle = fixture["oracle"]
        review.append(
            {
                "blind_id": blind_id,
                "expected_status": oracle["expected_status"],
                "intended_lens": fixture["expected_effective_lens"],
                "workflow_target": oracle["issue_id"],
                "support_facts": oracle["support_facts"],
                "packet": quality_eval.build_packet(fixture),
                "observed_status": row["status"],
                "nudge": row["finding"],
                "chars": len(row["finding"]),
                "raw_chars": raw_finding_length(str(row.get("raw_output") or "")),
                "judgment": {
                    "grounded": None,
                    "workflow_level": None,
                    "target_relevant": None,
                    "lens_aligned": None,
                    "complete": None,
                    "note": ""
                },
            }
        )
        identity_map.append(
            {
                "blind_id": blind_id,
                "fixture_id": row["fixture_id"],
                "condition": row["condition"],
                "repeat": row["repeat"],
            }
        )
    return review, identity_map


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--review-output", type=Path, required=True)
    parser.add_argument("--map-output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260817)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixtures = quality_eval.load_fixtures(args.fixtures)
    rows = load_rows(args.results)
    review, identity_map = build_blind_records(fixtures, rows, seed=args.seed)
    args.review_output.parent.mkdir(parents=True, exist_ok=True)
    args.map_output.parent.mkdir(parents=True, exist_ok=True)
    args.review_output.write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.map_output.write_text(
        json.dumps(identity_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(review)} blinded rows", flush=True)
    print(f"review packet: {args.review_output}", flush=True)
    print(f"identity map: {args.map_output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
