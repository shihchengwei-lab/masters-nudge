#!/usr/bin/env python3
"""Round-six benchmark reusing one calibrated A run per selected task."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


calibration = load("formal_v6_calibration", HERE / "calibrate.py")
benchmark = load("formal_v5_runner", REPO / "benchmark" / "formal-v5" / "run.py")

benchmark.HERE = HERE
benchmark.CALIBRATION_ROOT = Path(r"D:\masters-nudge-benchmark\round-6-calibration")
benchmark.ARTIFACT_ROOT = benchmark.CALIBRATION_ROOT / "formal-artifacts"
benchmark.ROUND_TITLE = "第六輪 Benchmark"
benchmark.CALIBRATION_EVIDENCE = "round-6 calibration actor reused as formal repeat-1 A"
benchmark.calibration = calibration
benchmark.CASE_IDS = list(calibration.SELECTED_CASES)
benchmark.ROWS = calibration.rows()
benchmark.runner.ROOT = benchmark.CALIBRATION_ROOT
benchmark.runner.ARTIFACT_ROOT = benchmark.ARTIFACT_ROOT
benchmark.runner.TMP = benchmark.CALIBRATION_ROOT / "tmp-formal"
benchmark.runner.PACKAGE = REPO / "plugins" / "masters-nudge"
benchmark.runner.CASES = {
    case_id: {
        "task": calibration._task_text(benchmark.ROWS[case_id]),
        "verify": calibration.base.CASES[case_id]["verify"],
    }
    for case_id in benchmark.CASE_IDS
}
benchmark.runner.TIMEOUT_SECONDS = 1800


if __name__ == "__main__":
    raise SystemExit(benchmark.main())
