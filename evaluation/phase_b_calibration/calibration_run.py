#!/usr/bin/env python3
"""Run isolated control/positive-control task-sensitivity jobs."""

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
from pathlib import Path
from typing import Any

from evaluation.phase_b import phase_b_run
from evaluation.phase_b_calibration import calibration_tasks


HERE = Path(__file__).resolve().parent


def sha256_tree(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
        relative = item.relative_to(path)
        if "__pycache__" in relative.parts or item.suffix == ".pyc":
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_jobs(spec: dict[str, Any], *, repeats: int, seed: int) -> list[dict[str, Any]]:
    jobs = []
    serial = 0
    for fixture in spec["fixtures"]:
        for repeat in range(1, repeats + 1):
            for condition in ("control", "positive_control"):
                serial += 1
                jobs.append(
                    {
                        "job_id": f"C{serial:03d}",
                        "task_id": fixture["id"],
                        "lens": fixture["lens"],
                        "condition": condition,
                        "repeat": repeat,
                        "objective": fixture["objective"],
                        "prior_assistant": fixture["prior_assistant"],
                        "recent_evidence": fixture["recent_evidence"],
                        "positive_control": fixture["positive_control"] if condition == "positive_control" else "",
                    }
                )
    random.Random(seed).shuffle(jobs)
    return jobs


def agent_prompt(job: dict[str, Any]) -> str:
    shared = (
        "Continue the bounded coding task from this checkpoint. The repository is the "
        "complete working context. Read TASK.md and the current git diff, inspect other "
        "repository evidence when warranted, and decide what remains before finalizing. "
        "You may edit files and run local tests. Work only inside the current directory; "
        "do not inspect parent or external paths, use the network, ask questions, or wait "
        "for input. End with a concise summary and the validation you actually ran.\n\n"
        f"Original user objective: {job['objective']}\n"
        f"Prior assistant checkpoint: {job['prior_assistant']}\n"
        f"Recent tool evidence: {job['recent_evidence']}"
    )
    if job["condition"] == "control":
        return shared
    return (
        f"{shared}\n\n"
        "<calibration_positive_control>\n"
        f"{job['positive_control']}\n"
        "</calibration_positive_control>\n"
        "This direct hint is part of task-sensitivity calibration. Verify it against the "
        "repository before acting."
    )


def grade_in_subprocess(task_id: str, workspace: Path) -> tuple[dict[str, Any], str]:
    result = subprocess.run(
        [sys.executable, "-m", "evaluation.phase_b_calibration.calibration_grade", task_id, str(workspace)],
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


def run_job(
    job: dict[str, Any],
    *,
    output_dir: Path,
    model: str,
    effort: str,
    timeout: int,
    max_budget_usd: float,
) -> dict[str, Any]:
    temp_root = Path(tempfile.mkdtemp(prefix=f"masters-nudge-calibration-{job['job_id']}-"))
    workspace = temp_root / "workspace"
    started = time.perf_counter()
    try:
        calibration_tasks.materialize(job["task_id"], workspace, state="candidate")
        baseline_commit = phase_b_run.git_text(workspace, "rev-list", "--max-parents=0", "HEAD").strip()
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
            process = phase_b_run.run_command(command, cwd=workspace, timeout=timeout, env=env)
            timed_out = False
            stdout = process.stdout
            stderr = process.stderr
            returncode = process.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            stdout = str(exc.stdout or "")
            stderr = str(exc.stderr or "")
            returncode = None
        payload = phase_b_run.parse_claude_json(stdout)
        grade, grader_error = grade_in_subprocess(job["task_id"], workspace)
        final_diff = phase_b_run.git_text(workspace, "diff", baseline_commit, "--") if baseline_commit else ""
        status = phase_b_run.git_text(workspace, "status", "--short")
        artifact = output_dir / "artifacts" / f"{job['job_id']}.zip"
        phase_b_run.archive_workspace(workspace, artifact)
        return {
            "job_id": job["job_id"],
            "task_id": job["task_id"],
            "lens": job["lens"],
            "condition": job["condition"],
            "repeat": job["repeat"],
            "positive_control": job["positive_control"],
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
        if resolved.parent == temp_base and resolved.name.startswith("masters-nudge-calibration-"):
            shutil.rmtree(resolved, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, default=calibration_tasks.DEFAULT_SPEC)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260822)
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
    spec = calibration_tasks.load_spec(args.spec)
    calibration_tasks.validate_assets(spec)
    jobs = build_jobs(spec, repeats=args.repeats, seed=args.seed)
    if args.dry_run:
        print(json.dumps({"jobs": len(jobs), "order": [job["job_id"] for job in jobs]}))
        return 0
    if args.output_dir.exists():
        raise SystemExit(f"refusing to overwrite output directory: {args.output_dir}")
    preflight = phase_b_run.main_agent_preflight(model=args.model, effort=args.effort, timeout=args.timeout)
    if not preflight["success"]:
        print("main-agent preflight failed: " + json.dumps(preflight, ensure_ascii=False), file=sys.stderr)
        return 2
    args.output_dir.mkdir(parents=True)
    result_path = args.output_dir / "runs.jsonl"
    manifest = {
        "schema_version": 1,
        "task_set": spec["task_set"],
        "jobs": len(jobs),
        "repeats": args.repeats,
        "seed": args.seed,
        "workers": args.workers,
        "conditions": ["control", "positive_control"],
        "main_agent": {
            "cli": "claude",
            "model": args.model,
            "effort": args.effort,
            "safe_mode": True,
            "timeout_seconds": args.timeout,
            "max_budget_usd_per_run": args.max_budget_usd,
        },
        "main_agent_preflight": preflight,
        "spec_sha256": phase_b_run.sha256_file(args.spec),
        "tasks_sha256": sha256_tree(calibration_tasks.TASKS_DIR),
        "runner_sha256": phase_b_run.sha256_file(Path(__file__)),
        "grader_sha256": phase_b_run.sha256_file(HERE / "calibration_grade.py"),
        "analyzer_sha256": phase_b_run.sha256_file(HERE / "calibration_analyze.py"),
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
            phase_b_run.write_jsonl(result_path, row)
            completed += 1
            print(
                f"[{completed}/{len(jobs)}] {row['job_id']} safe_target={bool(row['grader'].get('safe_target_resolution'))}",
                flush=True,
            )
    print(f"wrote {completed} rows to {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
