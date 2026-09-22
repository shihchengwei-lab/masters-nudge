#!/usr/bin/env python3
"""Windows-native calibration for round-six non-ceiling candidates."""

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

base.ROOT = Path(r"D:\masters-nudge-benchmark\round-6-calibration")
base.DATASET = REPO.parent / "_external" / "multi-swe-bench-flash.jsonl"
EXTRA_DATASETS = tuple(
    Path.home() / "AppData" / "Local" / "Temp" / "masters-nudge-candidates-20260922" / name
    for name in (
        "axios.jsonl", "darkreader.jsonl", "dayjs.jsonl", "ripgrep.jsonl",
        "serde.jsonl", "tokio.jsonl", "vue.jsonl",
    )
)

base.CASES = {
    "tokio-rs__tokio-6205": {
        "install": None,
        "verify": ["cargo", "test", "-p", "tokio", "--features", "full", "--test", "sync_mpsc"],
    },
    "sharkdp__fd-658": {
        "install": None,
        "verify": ["cargo", "test", "--test", "tests", "test_prune"],
    },
    "serde-rs__serde-2798": {
        "install": None,
        "verify": ["cargo", "test", "-p", "serde_test_suite", "--test", "test_gen"],
    },
    "vuejs__core-8402": {
        "install": ["corepack.cmd", "pnpm", "install", "--frozen-lockfile"],
        "verify": [
            "corepack.cmd", "pnpm", "run", "test-unit", "--no-watch", "--reporter=verbose",
            "packages/runtime-core/__tests__/apiCreateApp.spec.ts",
            "packages/shared/__tests__/toDisplayString.spec.ts",
        ],
    },
    "iamkun__dayjs-569": {
        "install": ["npm.cmd", "install"],
        "verify": ["node", "node_modules/jest/bin/jest.js", "test/plugin/weekday.test.js", "--runInBand"],
    },
    "axios__axios-5338": {
        "install": ["npm.cmd", "install"],
        "verify": ["npm.cmd", "test"],
    },
    "clap-rs__clap-5080": {
        "install": None,
        "verify": ["cargo", "test", "--test", "builder", "unknown_argument"],
    },
    "anuraghazra__github-readme-stats-2844": {
        "install": ["npm.cmd", "install"],
        "verify": ["npm.cmd", "test", "--", "--runInBand", "tests/renderStatsCard.test.js"],
    },
    "BurntSushi__ripgrep-2610": {
        "install": None,
        "verify": ["cargo", "test", "--test", "integration", "hyperlink"],
    },
    "tokio-rs__tokio-6742": {
        "install": None,
        "verify": [
            "cargo", "--config", "build.rustflags=['--cfg','tokio_unstable']", "test",
            "-p", "tokio", "--features", "full", "--test", "task_hooks",
        ],
    },
    "vuejs__core-9507": {
        "install": ["corepack.cmd", "pnpm", "install", "--frozen-lockfile"],
        "verify": [
            "corepack.cmd", "pnpm", "run", "test-unit", "--no-watch", "--reporter=verbose",
            "packages/compiler-sfc/__tests__/compileScript/defineModel.spec.ts",
            "packages/compiler-sfc/__tests__/compileScript/defineProps.spec.ts",
            "packages/compiler-sfc/__tests__/compileScript/definePropsDestructure.spec.ts",
        ],
    },
    "expressjs__express-3695": {
        "install": ["npm.cmd", "install"],
        "verify": ["npm.cmd", "test", "--", "--grep", "Route errors"],
    },
    "darkreader__darkreader-6747": {
        "install": ["npm.cmd", "install"],
        "verify": ["npm.cmd", "test", "--", "tests/generators/utils/parse.tests.ts"],
    },
    "axios__axios-5085": {
        "install": ["npm.cmd", "install"],
        "verify": [
            "node", "node_modules/mocha/bin/mocha.js", "test/unit/core/AxiosHeaders.js",
            "test/unit/regression/bugs.js", "--timeout", "30000", "--exit",
        ],
    },
    "anuraghazra__github-readme-stats-2099": {
        "install": ["npm.cmd", "install"],
        "verify": ["npm.cmd", "test", "--", "--runInBand", "tests/renderTopLanguages.test.js"],
    },
    "clap-rs__clap-5298": {
        "install": None,
        "verify": ["cargo", "test", "--test", "builder", "conflicts"],
    },
    "BurntSushi__ripgrep-2626": {
        "install": None,
        "verify": ["cargo", "test", "-p", "ripgrep", "--test", "integration", "quiet"],
    },
    "vuejs__core-8511": {
        "install": ["corepack.cmd", "pnpm", "install", "--frozen-lockfile"],
        "verify": [
            "corepack.cmd", "pnpm", "run", "test-unit", "--no-watch", "--reporter=verbose",
            "packages/compiler-sfc/__tests__/compileScript/resolveType.spec.ts",
        ],
    },
    "vuejs__core-8535": {
        "install": ["corepack.cmd", "pnpm", "install", "--frozen-lockfile", "--offline"],
        "verify": [
            "corepack.cmd", "pnpm", "run", "test-unit", "--no-watch", "--reporter=verbose",
            "packages/compiler-sfc/__tests__/compileScript.spec.ts",
            "packages/compiler-sfc/__tests__/compileScript/defineEmits.spec.ts",
            "packages/compiler-sfc/__tests__/compileScript/defineProps.spec.ts",
            "packages/compiler-sfc/__tests__/compileScript/definePropsDestructure.spec.ts",
        ],
    },
    "anuraghazra__github-readme-stats-105": {
        "install": ["npm.cmd", "install"],
        "verify": [
            "npm.cmd", "test", "--", "--runInBand", "tests/renderRepoCard.test.js",
            "tests/renderStatsCard.test.js", "tests/utils.test.js",
        ],
    },
    "tokio-rs__tokio-5200": {
        "install": None,
        "verify": [
            "cargo", "--config", "build.rustflags=['--cfg','tokio_unstable']", "test",
            "-p", "tokio", "--features", "full,test-util", "--test", "time_no_auto_advance",
        ],
    },
    "sharkdp__bat-1276": {
        "install": None,
        "verify": ["cargo", "test", "--test", "snapshot_tests"],
    },
}

SELECTED_CASES = (
    "tokio-rs__tokio-6742",
    "clap-rs__clap-5298",
    "vuejs__core-8511",
    "anuraghazra__github-readme-stats-105",
    "sharkdp__bat-1276",
    "darkreader__darkreader-6747",
)


def requested_cases() -> list[str]:
    requested = sys.argv[2:] or list(SELECTED_CASES)
    unknown = set(requested) - set(base.CASES)
    if unknown:
        raise RuntimeError(f"unknown cases: {sorted(unknown)}")
    return requested


base.requested_cases = requested_cases


def rows() -> dict[str, dict]:
    wanted = set(base.CASES)
    found: dict[str, dict] = {}
    for dataset in (base.DATASET, *EXTRA_DATASETS):
        if not dataset.is_file():
            continue
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
