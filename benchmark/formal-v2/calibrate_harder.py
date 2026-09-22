#!/usr/bin/env python3
"""Minimal Windows-native calibration for harder public benchmark candidates."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
DATASET = REPO.parent / "_external" / "multi-swe-bench-flash.jsonl"
ROOT = Path(os.environ["LOCALAPPDATA"]) / "Temp" / "mn-formal-v3-hard-calibration"
ACTOR_MODEL = "gpt-5.6-sol"
CASES = {
    "anuraghazra__github-readme-stats-2099": {
        "install": ["npm.cmd", "install"],
        "verify": ["npm.cmd", "test", "--", "--runInBand", "tests/renderTopLanguages.test.js"],
    },
    "BurntSushi__ripgrep-1980": {
        "install": None,
        "verify": ["cargo", "test", "--test", "integration", "feature::f1791_multiple_smart_case_exprs"],
    },
    "BurntSushi__ripgrep-2610": {
        "install": None,
        "verify": ["cargo", "test", "--test", "integration", "regression::r428_color_context_path"],
    },
    "tokio-rs__bytes-547": {
        "install": None,
        "verify": ["cargo", "test", "--tests"],
    },
    "cli__cli-1642": {
        "install": None,
        "verify": ["go", "test", "./pkg/cmd/auth/login"],
    },
    "sharkdp__fd-1121": {
        "install": None,
        "verify": ["cargo", "test", "test_exec"],
    },
    "tokio-rs__tokio-6618": {
        "install": None,
        "verify": ["cargo", "test", "-p", "tokio-util", "--test", "sync_cancellation_token",
                   "run_until_cancelled_test"],
    },
    "vuejs__core-10101": {
        "install": ["corepack.cmd", "pnpm", "install", "--frozen-lockfile"],
        "verify": ["corepack.cmd", "pnpm", "run", "test-unit", "--no-watch", "--reporter=verbose",
                   "packages/reactivity/__tests__/computed.spec.ts",
                   "packages/reactivity/__tests__/effect.spec.ts"],
    },
    "vuejs__core-8535": {
        "install": ["corepack.cmd", "pnpm", "install", "--frozen-lockfile", "--offline"],
        "verify": ["corepack.cmd", "pnpm", "run", "test-unit", "--no-watch", "--reporter=verbose",
                   "packages/compiler-sfc/__tests__/compileScript.spec.ts",
                   "packages/compiler-sfc/__tests__/compileScript/defineEmits.spec.ts",
                   "packages/compiler-sfc/__tests__/compileScript/defineProps.spec.ts",
                   "packages/compiler-sfc/__tests__/compileScript/definePropsDestructure.spec.ts"],
    },
    "anuraghazra__github-readme-stats-3442": {
        "install": ["npm.cmd", "install"],
        "verify": ["npm.cmd", "test", "--", "--runInBand", "tests/fetchGist.test.js",
                   "tests/fetchRepo.test.js", "tests/fetchStats.test.js",
                   "tests/fetchTopLanguages.test.js", "tests/retryer.test.js"],
    },
}


def run(command: list[str], cwd: Path, timeout: int = 1800) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout,
    )


def rows() -> dict[str, dict]:
    found = {}
    with DATASET.open(encoding="utf-8") as source:
        for line in source:
            row = json.loads(line)
            if row["instance_id"] in CASES:
                found[row["instance_id"]] = row
    if found.keys() != CASES.keys():
        raise RuntimeError(f"missing dataset rows: {CASES.keys() - found.keys()}")
    return found


def git(cwd: Path, *args: str, check: bool = True) -> str:
    result = run(["git", *args], cwd)
    if check and result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


def apply(cwd: Path, text: str, name: str) -> None:
    patch = cwd.parent / name
    patch.write_text(text, encoding="utf-8", newline="\n")
    try:
        result = run(["git", "apply", "--whitespace=nowarn", str(patch)], cwd)
    finally:
        patch.unlink(missing_ok=True)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)


def write_process(path: Path, result: subprocess.CompletedProcess[str], elapsed: float) -> None:
    path.write_text(json.dumps({
        "command": result.args, "exit_code": result.returncode,
        "elapsed_seconds": round(elapsed, 3), "stdout": result.stdout, "stderr": result.stderr,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def execute(command: list[str], cwd: Path, output: Path, timeout: int = 1800) -> int:
    started = time.monotonic()
    result = run(command, cwd, timeout)
    write_process(output, result, time.monotonic() - started)
    return result.returncode


def requested_cases() -> list[str]:
    requested = sys.argv[2:] or list(CASES)
    unknown = set(requested) - set(CASES)
    if unknown:
        raise RuntimeError(f"unknown cases: {sorted(unknown)}")
    return requested


def prepare() -> None:
    selected = rows()
    (ROOT / "cases").mkdir(parents=True, exist_ok=True)
    for case_id in requested_cases():
        config = CASES[case_id]
        row = selected[case_id]
        case = ROOT / "cases" / case_id
        case.mkdir(exist_ok=False)
        for command in (
            ["git", "init"],
            ["git", "config", "core.autocrlf", "false"],
            ["git", "remote", "add", "origin", f"https://github.com/{row['org']}/{row['repo']}.git"],
            ["git", "fetch", "--depth", "1", "origin", row["base"]["sha"]],
            ["git", "checkout", "--detach", "FETCH_HEAD"],
        ):
            result = run(command, case)
            if result.returncode:
                raise RuntimeError(f"{case_id}: {' '.join(command)}\n{result.stderr or result.stdout}")
        if config["install"]:
            if execute(config["install"], case, case.parent / f"{case_id}-install.json"):
                raise RuntimeError(f"dependency install failed: {case_id}")
        print(json.dumps({"prepared": case_id}, ensure_ascii=False), flush=True)


def test_paths(patch: str) -> list[str]:
    return re.findall(r"^diff --git a/(\S+)", patch, re.MULTILINE)


def fingerprint(root: Path, paths: list[str]) -> str:
    digest = hashlib.sha256()
    for name in sorted(paths):
        path = root / name
        digest.update(name.encode())
        digest.update(path.read_bytes() if path.is_file() else b"<missing>")
    return digest.hexdigest()


def preflight() -> None:
    selected = rows()
    result_path = ROOT / "preflight.json"
    records = json.loads(result_path.read_text(encoding="utf-8")) if result_path.is_file() else []
    done = {record["case"] for record in records}
    for case_id in requested_cases():
        if case_id in done:
            continue
        config = CASES[case_id]
        row = selected[case_id]
        case = ROOT / "cases" / case_id
        git(case, "reset", "--hard", row["base"]["sha"])
        git(case, "clean", "-fd")
        apply(case, row["test_patch"], f"{case_id}-test.patch")
        baseline = execute(config["verify"], case, case.parent / f"{case_id}-baseline.json")
        apply(case, row["fix_patch"], f"{case_id}-fix.patch")
        oracle = execute(config["verify"], case, case.parent / f"{case_id}-oracle.json")
        record = {"case": case_id, "baseline_exit": baseline, "oracle_exit": oracle}
        records.append(record)
        (ROOT / "preflight.json").write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(record, ensure_ascii=False), flush=True)
        if baseline == 0 or oracle != 0:
            raise RuntimeError(f"invalid native contract: {case_id}")
        git(case, "reset", "--hard", row["base"]["sha"])
        git(case, "clean", "-fd")
        apply(case, row["test_patch"], f"{case_id}-seed-test.patch")
        git(case, "config", "user.name", "Masters Nudge Benchmark")
        git(case, "config", "user.email", "benchmark@local.invalid")
        git(case, "add", "-A")
        git(case, "commit", "--no-verify", "-m", "hard calibration seed")
        record["seed"] = git(case, "rev-parse", "HEAD").strip()
        record["test_paths"] = test_paths(row["test_patch"])
        record["tests_sha256"] = fingerprint(case, record["test_paths"])
        (ROOT / "preflight.json").write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


def task_text(row: dict) -> str:
    parts = [row["title"].strip(), row["body"].strip()]
    parts.extend(
        f"{issue['title']}\n\n{issue['body']}".strip()
        for issue in row.get("resolved_issues", [])
    )
    return "\n\n".join(part for part in parts if part).strip()


def actor_bin() -> str:
    from masters_nudge.providers import resolve_codex_bin
    binary = resolve_codex_bin()
    if not binary:
        raise RuntimeError("Codex executable unavailable")
    return binary


def actor_usage(events: str) -> dict:
    for line in reversed(events.splitlines()):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "turn.completed":
            return event.get("usage") or {}
    return {}


def calibrate_actors() -> None:
    selected = rows()
    records = json.loads((ROOT / "preflight.json").read_text(encoding="utf-8"))
    preflight_by_case = {record["case"]: record for record in records}
    summary_path = ROOT / "actor-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else []
    done = {record["case"] for record in summary}
    for case_id in requested_cases():
        if case_id in done:
            continue
        config = CASES[case_id]
        seed = preflight_by_case[case_id]
        case = ROOT / "cases" / case_id
        git(case, "reset", "--hard", seed["seed"])
        git(case, "clean", "-fd")
        artifact = ROOT / "actors" / case_id
        artifact.mkdir(parents=True, exist_ok=False)
        verify = subprocess.list2cmdline(config["verify"])
        prompt = (
            "Complete the repository task below. The checked-in tests are an immutable contract: "
            "do not edit, delete, or replace them. You own implementation and verification. Use "
            "apply_patch for edits. Do not commit, install packages, inspect Git history, use the "
            "network, delegate, or use subagents.\n\n"
            f"{task_text(selected[case_id])}\n\n"
            f"Run `{verify}`, inspect the final diff, and report the result.\n"
        )
        command = [
            actor_bin(), "-c", "project_doc_max_bytes=0", "-c", "features.multi_agent=false",
            "-c", 'model_reasoning_effort="medium"', "--disable", "hooks", "--disable", "plugins",
            "exec", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check", "--ephemeral",
            "--json", "-s", "danger-full-access", "-m", ACTOR_MODEL, "-C", str(case),
            "-o", str(artifact / "actor-final.txt"), "-",
        ]
        started = time.monotonic()
        actor = subprocess.run(
            command, cwd=case, input=prompt, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=1800,
        )
        elapsed = time.monotonic() - started
        (artifact / "actor-events.jsonl").write_text(actor.stdout, encoding="utf-8")
        (artifact / "actor-stderr.txt").write_text(actor.stderr, encoding="utf-8")
        (artifact / "final.patch").write_text(git(case, "diff", "--binary"), encoding="utf-8")
        verification = run(config["verify"], case, 900)
        (artifact / "verification.txt").write_text(
            verification.stdout + verification.stderr, encoding="utf-8"
        )
        unchanged = run(
            ["git", "diff", "--quiet", "HEAD", "--", *seed["test_paths"]], case
        ).returncode == 0
        row = {
            "case": case_id, "actor_exit": actor.returncode,
            "contract_exit": verification.returncode,
            "contract_passed": verification.returncode == 0 and unchanged,
            "tests_unchanged": unchanged, "elapsed_seconds": round(elapsed, 3),
            "usage": actor_usage(actor.stdout), "changed_files": git(case, "diff", "--name-only").splitlines(),
        }
        summary.append(row)
        (artifact / "result.json").write_text(
            json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(row, ensure_ascii=False), flush=True)
        if actor.returncode:
            raise RuntimeError(f"Actor fault: {case_id}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in {"prepare", "preflight", "actors"}:
        raise SystemExit("usage: calibrate_harder.py prepare|preflight|actors [case ...]")
    {"prepare": prepare, "preflight": preflight, "actors": calibrate_actors}[sys.argv[1]]()
