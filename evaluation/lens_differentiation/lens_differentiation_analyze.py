#!/usr/bin/env python3
"""Summarize six-lens output validity, variation, and preregistered term alignment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.lens_differentiation.lens_differentiation_run import LENSES, load_fixture


PERSON_NAMES = ("Jeff", "Dean", "Beck", "Fowler", "Linus", "Torvalds", "Lamport", "Carmack")


def provider_valid(row: dict[str, Any]) -> bool:
    return bool(
        row.get("status") in {"finding", "no_finding"}
        and row.get("raw_schema_valid") is True
        and isinstance(row.get("finding"), str)
        and len(row["finding"]) <= 52
    )


def theme_hits(finding: str, terms: list[str]) -> list[str]:
    folded = finding.casefold()
    return [term for term in terms if term.casefold() in folded]


def analyze(fixture: dict[str, Any], rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    expected = {(lens, repeat) for lens in LENSES for repeat in range(1, 4)}
    actual = {(row["lens"], int(row["repeat"])) for row in rows}
    by_lens = {}
    selections = []
    for lens in LENSES:
        selected = sorted((row for row in rows if row["lens"] == lens), key=lambda row: row["repeat"])
        expectation = fixture["lens_expectations"][lens]
        finding_rows = [row for row in selected if provider_valid(row) and row["status"] == "finding"]
        hero = finding_rows[0] if finding_rows else selected[0]
        selections.append(
            {
                "lens": lens,
                "repeat": hero["repeat"],
                "finding": hero["finding"],
                "selection_rule": "lowest repeat with a valid finding",
            }
        )
        alignments = [theme_hits(row["finding"], expectation["terms"]) for row in selected]
        by_lens[lens] = {
            "label": expectation["label"],
            "provider_valid": sum(provider_valid(row) for row in selected),
            "findings": len(finding_rows),
            "distinct_findings": len({row["finding"] for row in finding_rows}),
            "theme_term_aligned": sum(bool(hits) for hits in alignments),
            "theme_hits": alignments,
            "mean_characters": round(sum(row["characters"] for row in selected) / len(selected), 1),
        }
    hero_findings = [row["finding"] for row in selections]
    forbidden_names = {
        name: [finding for finding in hero_findings if name.casefold() in finding.casefold()]
        for name in PERSON_NAMES
    }
    forbidden_names = {name: values for name, values in forbidden_names.items() if values}
    gates = {
        "integrity": len(rows) == 18 and len(actual) == 18 and actual == expected,
        "valid_findings": all(item["provider_valid"] == 3 and item["findings"] >= 2 for item in by_lens.values()),
        "six_unique_hero_lines": len(set(hero_findings)) == 6 and all(hero_findings),
        "theme_term_signal": all(item["theme_term_aligned"] >= 2 for item in by_lens.values()),
        "no_person_imitation": not forbidden_names,
        "hard_cap": all(int(row["characters"]) <= 52 for row in rows),
    }
    summary = {
        "schema_version": 1,
        "fixture_id": fixture["id"],
        "rows": len(rows),
        "by_lens": by_lens,
        "hero_exact_unique": len(set(hero_findings)),
        "forbidden_person_names": forbidden_names,
        "gates": gates,
        "automated_passed": all(gates.values()),
        "claim_boundary": "Semantic lens differentiation still requires human review; term matching is diagnostic only.",
    }
    selection_payload = {
        "schema_version": 1,
        "fixture_id": fixture["id"],
        "selection_rule": "lowest repeat with a valid finding; no wording edits",
        "selections": selections,
    }
    return summary, selection_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixture = load_fixture(args.fixture)
    rows = json.loads(args.runs.read_text(encoding="utf-8"))["runs"]
    summary, selections = analyze(fixture, rows)
    args.analysis.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.selection.write_text(json.dumps(selections, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"automated passed: {summary['automated_passed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
