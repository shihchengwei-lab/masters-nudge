#!/usr/bin/env python3
"""Analyze the non-terminal six-lens v2 run with the frozen shared rubric."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluation.lens_differentiation import lens_differentiation_analyze as base
from evaluation.lens_differentiation.lens_differentiation_run_v2 import load_fixture


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
    summary, selections = base.analyze(fixture, rows)
    args.analysis.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.selection.write_text(json.dumps(selections, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"automated passed: {summary['automated_passed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
