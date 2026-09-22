#!/usr/bin/env python3
"""Windows-native calibration for the next balanced benchmark candidates."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE_PATH = REPO / "benchmark" / "formal-v2" / "calibrate_harder.py"
SPEC = importlib.util.spec_from_file_location("formal_v2_calibration", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("formal-v2 calibration module is unavailable")
base = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(base)

base.ROOT = Path(r"D:\masters-nudge-benchmark\round-5-calibration")
base.DATASET = REPO.parent / "_external" / "multi-swe-bench-flash.jsonl"
AXIOS_DATASET = Path.home() / "AppData" / "Local" / "Temp" / "masters-nudge-candidates-20260922" / "axios.jsonl"
TOKIO_DATASET = AXIOS_DATASET.with_name("tokio.jsonl")
VUE_DATASET = AXIOS_DATASET.with_name("vue.jsonl")

base.CASES = {
    "clap-rs__clap-5075": {
        "install": None,
        "verify": ["cargo", "test", "--test", "builder", "unknown_argument"],
    },
    "BurntSushi__ripgrep-1980": {
        "install": None,
        "verify": ["cargo", "test", "--test", "integration", "feature::f1791_multiple_smart_case_exprs"],
    },
    "vuejs__core-10101": {
        "install": ["corepack.cmd", "pnpm", "install", "--frozen-lockfile"],
        "verify": [
            "corepack.cmd", "pnpm", "run", "test-unit", "--no-watch", "--reporter=verbose",
            "packages/reactivity/__tests__/computed.spec.ts",
            "packages/reactivity/__tests__/effect.spec.ts",
        ],
    },
    "vuejs__core-11517": {
        "install": ["corepack.cmd", "pnpm", "install", "--frozen-lockfile"],
        "verify": [
            "corepack.cmd", "pnpm", "run", "test-unit", "--no-watch", "--reporter=verbose",
            "packages/runtime-dom/__tests__/customElement.spec.ts",
        ],
    },
    "axios__axios-5919": {
        "install": ["npm.cmd", "install"],
        "verify": [
            "node", "node_modules/mocha/bin/mocha.js", "test/unit/adapters/adapters.js",
            "--timeout", "30000", "--exit",
        ],
    },
    "anuraghazra__github-readme-stats-1314": {
        "install": ["npm.cmd", "install"],
        "verify": [
            "npm.cmd", "test", "--", "--runInBand",
            "tests/flexLayout.test.js", "tests/renderRepoCard.test.js", "tests/utils.test.js",
        ],
    },
}


def rows() -> dict[str, dict]:
    wanted = set(base.CASES)
    found: dict[str, dict] = {}
    for dataset in (base.DATASET, AXIOS_DATASET, TOKIO_DATASET, VUE_DATASET):
        with dataset.open(encoding="utf-8") as source:
            for line in source:
                row = json.loads(line)
                if row["instance_id"] in wanted:
                    found[row["instance_id"]] = row
    if found.keys() != wanted:
        raise RuntimeError(f"missing dataset rows: {sorted(wanted - found.keys())}")
    return found


base.rows = rows
_task_text = base.task_text
base.task_text = lambda row: "請高品味的完成任務。\n\n" + _task_text(row)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in {"prepare", "preflight", "actors"}:
        raise SystemExit("usage: calibrate.py prepare|preflight|actors [case ...]")
    {"prepare": base.prepare, "preflight": base.preflight, "actors": base.calibrate_actors}[sys.argv[1]]()
