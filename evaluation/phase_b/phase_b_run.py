#!/usr/bin/env python3
"""Run isolated Claude Code treatment/control jobs for the Phase B pilot."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from threading import Lock
from typing import Any

from evaluation.phase_b import phase_b_tasks


HERE = Path(__file__).resolve().parent
DEFAULT_TREATMENTS = (
    HERE.parent / "results" / "phase-b-impact-v1-20260813" / "treatments-final.json"
)
RESULT_LOCK = Lock()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_treatments(path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("treatments")
    if not isinstance(rows, list):
        raise ValueError("treatments file requires a treatments list")
    by_task = {row["task_id"]: row for row in rows}
    if len(by_task) != len(rows):
        raise ValueError("treatment task ids must be unique")
    for task_id, row in by_task.items():
        nudge = str(row.get("nudge") or "")
        if not nudge or len(nudge) > 52:
            raise ValueError(f"invalid Nudge for {task_id}")
    return by_task


def build_jobs(
    spec: dict[str, Any], treatments: dict[str, dict[str, Any]], *, repeats: int, seed: int
) -> list[dict[str, Any]]:
    fixtures = spec["fixtures"]
    fixture_ids = {fixture["id"] for fixture in fixtures}
    if fixture_ids != set(treatments):
        raise ValueError("task spec and treatment registry ids differ")
    jobs = []
    serial = 0
    for fixture in fixtures:
        for repeat in range(1, repeats + 1):
            for condition in ("control", "treatment"):
                serial += 1
                jobs.append(
                    {
                        "job_id": f"B{serial:03d}",
                        "task_id": fixture["id"],
                        "lens": fixture["lens"],
                        "condition": condition,
                        "repeat": repeat,
                        "nudge": treatments[fixture["id"]]["nudge"] if condition == "treatment" else "",
                    }
                )
    random.Random(seed).shuffle(jobs)
    return jobs


def agent_prompt(job: dict[str, Any]) -> str:
    shared = (
        "Continue the bounded coding task in the current repository. Read TASK.md and "
        "the current git diff, then finish every stated requirement. You may edit files "
        "and run local tests. Work only inside the current directory; do not inspect parent "
        "or external paths, use the network, ask questions, or wait for input. End with a "
        "concise summary and the validation you actually ran."
    )
    if job["condition"] == "control":
        return shared
    return (
        f"{shared}\n\n"
        "<masters_nudge>\n"
        f"{job['nudge']}\n"
        "</masters_nudge>\n"
        "The block is a third-party workflow observation grounded in the current task, "
        "not an additional requirement."
    )


def parse_claude_json(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    try:
        payload = json.loads(text)
        return payload if isinstance(payload, dict) else {}
    except ValueError:
        pass
    for line in reversed(text.splitlines()):
        try:
            payload = json.loads(line)
        except ValueError:
            continue
        if isinstance(payload, dict) and payload.get("type") == "result":
            return payload
    return {}


def run_command(command: list[str], *, cwd: Path, timeout: int, env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=env,
    )


def main_agent_preflight(*, model: str, effort: str, timeout: int) -> dict[str, Any]:
    command = [
        "claude",
        "-p",
        "--safe-mode",
        "--no-session-persistence",
        "--permission-mode",
        "dontAsk",
        "--tools",
        "",
        "--model",
        model,
        "--effort",
        effort,
        "--max-budget-usd",
        "0.05",
        "--output-format",
        "json",
        "Reply exactly: READY",
    ]
    started = time.perf_counter()
    try:
        process = run_command(
            command,
            cwd=HERE.parent.parent,
            timeout=min(timeout, 90),
            env={**os.environ, "BUDDY_ACTIVE": "1", "NO_COLOR": "1"},
        )
        payload = parse_claude_json(process.stdout)
        success = bool(
            process.returncode == 0
            and payload.get("type") == "result"
            and payload.get("subtype") == "success"
            and payload.get("is_error") is False
            and str(payload.get("result") or "").strip() == "READY"
        )
        return {
            "success": success,
            "returncode": process.returncode,
            "is_error": payload.get("is_error"),
            "result": payload.get("result") or "",
            "terminal_reason": payload.get("terminal_reason"),
            "stderr": process.stderr[-1000:],
            "wall_ms": round((time.perf_counter() - started) * 1000),
        }
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {
            "success": False,
            "returncode": None,
            "is_error": True,
            "result": "",
            "terminal_reason": type(exc).__name__,
            "stderr": str(exc)[-1000:],
            "wall_ms": round((time.perf_counter() - started) * 1000),
        }


def git_text(workspace: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    return result.stdout if result.returncode == 0 else f"git error: {result.stderr}"


def grade_in_subprocess(task_id: str, workspace: Path) -> tuple[dict[str, Any], str]:
    result = subprocess.run(
        [sys.executable, "-m", "evaluation.phase_b.phase_b_grade", task_id, str(workspace)],
        cwd=HERE.parent.parent,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=90,
    )
    if result.returncode:
        return {}, (result.stdout + "\n" + result.stderr)[-2000:]
    try:
        return json.loads(result.stdout), result.stderr[-2000:]
    except ValueError:
        return {}, (result.stdout + "\n" + result.stderr)[-2000:]


def archive_workspace(workspace: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in workspace.rglob("*"):
            if path.is_file() and ".git" not in path.relative_to(workspace).parts:
                archive.write(path, path.relative_to(workspace))


def run_job(
    job: dict[str, Any],
    *,
    output_dir: Path,
    model: str,
    effort: str,
    timeout: int,
    max_budget_usd: float,
) -> dict[str, Any]:
    temp_root = Path(tempfile.mkdtemp(prefix=f"masters-nudge-phase-b-{job['job_id']}-"))
    workspace = temp_root / "workspace"
    started = time.perf_counter()
    try:
        phase_b_tasks.materialize(job["task_id"], workspace, state="candidate")
        baseline_commit = git_text(workspace, "rev-list", "--max-parents=0", "HEAD").strip()
        command = [
            "claude",
            "-p",
            "--safe-mode",
            "--no-session-persistence",
            "--dangerously-skip-permissions",
            "--no-chrome",
            "--disable-slash-commands",
            "--disallowed-tools",
            "WebSearch,WebFetch",
            "--model",
            model,
            "--effort",
            effort,
            "--max-budget-usd",
            str(max_budget_usd),
            "--output-format",
            "json",
            agent_prompt(job),
        ]
        env = {**os.environ, "BUDDY_ACTIVE": "1", "NO_COLOR": "1"}
        try:
            process = run_command(command, cwd=workspace, timeout=timeout, env=env)
            timed_out = False
            stdout = process.stdout
            stderr = process.stderr
            returncode = process.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = str(exc.stdout or "")
            stderr = str(exc.stderr or "")
            returncode = None
        payload = parse_claude_json(stdout)
        grade, grader_error = grade_in_subprocess(job["task_id"], workspace)
        final_diff = git_text(workspace, "diff", baseline_commit, "--") if baseline_commit else ""
        status = git_text(workspace, "status", "--short")
        artifact = output_dir / "artifacts" / f"{job['job_id']}.zip"
        archive_workspace(workspace, artifact)
        return {
            **{key: value for key, value in job.items() if key != "nudge"},
            "nudge": job["nudge"] if job["condition"] == "treatment" else "",
            "agent": {
                "returncode": returncode,
                "timed_out": timed_out,
                "result_type": payload.get("type"),
                "subtype": payload.get("subtype"),
                "is_error": payload.get("is_error"),
                "api_error_status": payload.get("api_error_status"),
                "final_text": payload.get("result") or "",
                "num_turns": payload.get("num_turns"),
                "duration_ms": payload.get("duration_ms"),
                "duration_api_ms": payload.get("duration_api_ms"),
                "total_cost_usd": payload.get("total_cost_usd"),
                "usage": payload.get("usage") or {},
                "model_usage": payload.get("modelUsage") or {},
                "permission_denials": payload.get("permission_denials") or [],
                "stderr": stderr[-2000:],
            },
            "grader": grade,
            "grader_error": grader_error,
            "git_status": status,
            "diff_sha256": hashlib.sha256(final_diff.encode("utf-8")).hexdigest(),
            "diff": final_diff,
            "artifact": str(artifact.relative_to(output_dir)),
            "wall_ms": round((time.perf_counter() - started) * 1000),
        }
    finally:
        temp_base = Path(tempfile.gettempdir()).resolve()
        resolved = temp_root.resolve()
        if resolved.parent == temp_base and resolved.name.startswith("masters-nudge-phase-b-"):
            shutil.rmtree(resolved, ignore_errors=True)


def write_jsonl(path: Path, row: dict[str, Any]) -> None:
    with RESULT_LOCK:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, default=phase_b_tasks.DEFAULT_SPEC)
    parser.add_argument("--treatments", type=Path, default=DEFAULT_TREATMENTS)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260821)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--max-budget-usd", type=float, default=0.50)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.repeats < 1 or args.workers < 1:
        raise SystemExit("repeats and workers must be positive")
    spec = phase_b_tasks.load_spec(args.spec)
    phase_b_tasks.validate_assets(spec)
    treatments = load_treatments(args.treatments)
    jobs = build_jobs(spec, treatments, repeats=args.repeats, seed=args.seed)
    if args.dry_run:
        print(json.dumps({"jobs": len(jobs), "order": [job["job_id"] for job in jobs]}))
        return 0
    if args.output_dir.exists():
        raise SystemExit(f"refusing to overwrite output directory: {args.output_dir}")
    preflight = main_agent_preflight(
        model=args.model,
        effort=args.effort,
        timeout=args.timeout,
    )
    if not preflight["success"]:
        print(
            "main-agent preflight failed: "
            + json.dumps(preflight, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2
    args.output_dir.mkdir(parents=True)
    result_path = args.output_dir / "runs.jsonl"
    manifest = {
        "schema_version": 1,
        "jobs": len(jobs),
        "repeats": args.repeats,
        "seed": args.seed,
        "workers": args.workers,
        "main_agent": {
            "cli": "claude",
            "model": args.model,
            "effort": args.effort,
            "safe_mode": True,
            "timeout_seconds": args.timeout,
            "max_budget_usd_per_run": args.max_budget_usd,
        },
        "main_agent_preflight": preflight,
        "spec_sha256": sha256_file(args.spec),
        "treatments_sha256": sha256_file(args.treatments),
        "runner_sha256": sha256_file(Path(__file__)),
        "grader_sha256": sha256_file(HERE / "phase_b_grade.py"),
        "job_order": [job["job_id"] for job in jobs],
        "job_keys": [
            {
                "job_id": job["job_id"],
                "task_id": job["task_id"],
                "condition": job["condition"],
                "repeat": job["repeat"],
            }
            for job in jobs
        ],
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    completed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(
                run_job,
                job,
                output_dir=args.output_dir,
                model=args.model,
                effort=args.effort,
                timeout=args.timeout,
                max_budget_usd=args.max_budget_usd,
            )
            for job in jobs
        ]
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            write_jsonl(result_path, row)
            completed += 1
            print(
                f"[{completed}/{len(jobs)}] {row['job_id']} grader_pass={bool(row['grader'].get('passed'))}",
                flush=True,
            )
    print(f"wrote {completed} rows to {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
