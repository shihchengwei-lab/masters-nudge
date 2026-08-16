#!/usr/bin/env python3
"""Export a path- and session-neutral snapshot of the Riemann reaction logs."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path


WORKSPACE = r"d:\riemann"
FIELDS = (
    "schema_version", "ts", "kind", "reason", "provider", "model", "persona",
    "domain", "stage", "primary_lens", "effective_lens", "override_lens",
    "trigger", "route_source", "review_trigger", "completion_basis", "reaction",
    "source_event_seq", "reaction_ts", "delivery_status", "delivery_event_seq",
    "delivered_at", "delivered_via",
)


def load_rows(data_dir: Path) -> list[dict]:
    grouped: list[tuple[str, list[dict]]] = []
    for path in sorted(data_dir.glob("*.log")):
        matches: list[dict] = []
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                row = json.loads(line)
            except (TypeError, ValueError):
                continue
            if str(row.get("workspace") or "").lower() == WORKSPACE:
                matches.append(row)
        if matches:
            grouped.append((min(str(row.get("ts") or "") for row in matches), matches))

    rows: list[dict] = []
    for index, (_, matches) in enumerate(sorted(grouped), start=1):
        run = f"run-{index}"
        for source in matches:
            row = {key: source[key] for key in FIELDS if key in source}
            row["run"] = run
            rows.append(row)
    return sorted(rows, key=lambda row: str(row.get("ts") or ""))


def counter(rows: list[dict], key: str) -> dict[str, int]:
    return dict(sorted(collections.Counter(str(row.get(key) or "") for row in rows).items()))


def summarize(rows: list[dict]) -> dict:
    reviews = [row for row in rows if row.get("kind") == "review"]
    statuses = [row for row in rows if row.get("kind") == "review_status"]
    receipts = [row for row in rows if row.get("kind") == "delivery_receipt"]
    return {
        "schema_version": 1,
        "scope": "observational Riemann-domain experiment; no control arm",
        "runs": len({row["run"] for row in rows}),
        "first_event": min(row["ts"] for row in rows),
        "last_event": max(row["ts"] for row in rows),
        "records": len(rows),
        "findings": len(reviews),
        "review_statuses": len(statuses),
        "delivery_receipts": len(receipts),
        "confirmed_injections": sum(
            row.get("delivery_status") == "injected" for row in receipts
        ),
        "generated_with_receipt_tracking": sum(
            row.get("delivery_status") == "queued" for row in reviews
        ),
        "finding_by_lens": counter(reviews, "effective_lens"),
        "finding_by_reason": counter(reviews, "reason"),
        "finding_by_trigger": counter(reviews, "trigger"),
        "status_messages": counter(statuses, "reaction"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent / "snapshot")
    args = parser.parse_args()
    rows = load_rows(args.data_dir)
    if not rows:
        raise SystemExit("no matching Riemann-domain reactions found")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    reactions = args.output_dir / "reactions.jsonl"
    reactions.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    (args.output_dir / "summary.json").write_text(
        json.dumps(summarize(rows), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"exported {len(rows)} records to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
