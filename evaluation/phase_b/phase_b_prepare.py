#!/usr/bin/env python3
"""Generate and freeze one task-specific treatment Nudge per Phase B task."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import random
import time
from pathlib import Path
from typing import Any

import buddy
from evaluation import quality_eval
from evaluation.phase_b import phase_b_tasks


def prepare_job(fixture: dict[str, Any]) -> dict[str, Any]:
    routed = dict(fixture)
    routed["expected_effective_lens"] = fixture["lens"]
    packet = quality_eval.build_packet(routed)
    route = quality_eval.fixture_routes(routed, packet)["effective"]
    prompt = buddy.build_system_prompt(route)
    if not prompt:
        raise RuntimeError(f"unable to build prompt for {fixture['id']}")
    return {
        "fixture": fixture,
        "packet": packet,
        "route": route,
        "prompt": prompt,
    }


def run_job(job: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    result = quality_eval.call_reviewer(job["prompt"], job["packet"])
    latency_ms = round((time.perf_counter() - started) * 1000)
    fixture = job["fixture"]
    raw_output = str(result.get("raw_output") or "")
    return {
        "task_id": fixture["id"],
        "lens": fixture["lens"],
        "route": {
            "stage": job["route"].stage,
            "primary_lens": job["route"].primary_lens,
            "effective_lens": job["route"].effective_lens,
            "override_lens": job["route"].override_lens,
            "trigger": job["route"].trigger,
        },
        "status": result.get("status") or "error",
        "nudge": result.get("finding") or "",
        "chars": len(str(result.get("finding") or "")),
        "raw_schema_valid": quality_eval.raw_schema_valid(raw_output),
        "raw_output": raw_output,
        "latency_ms": latency_ms,
        "usage": result.get("usage") or {},
        "packet_sha256": hashlib.sha256(job["packet"].encode("utf-8")).hexdigest(),
        "system_prompt_sha256": hashlib.sha256(job["prompt"].encode("utf-8")).hexdigest(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, default=phase_b_tasks.DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260819)
    parser.add_argument("--task", action="append", dest="task_ids")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec = phase_b_tasks.load_spec(args.spec)
    phase_b_tasks.validate_assets(spec)
    fixtures = spec["fixtures"]
    if args.task_ids:
        wanted = set(args.task_ids)
        fixtures = [fixture for fixture in fixtures if fixture["id"] in wanted]
        missing = wanted - {fixture["id"] for fixture in fixtures}
        if missing:
            raise SystemExit(f"unknown task ids: {', '.join(sorted(missing))}")
    jobs = [prepare_job(fixture) for fixture in fixtures]
    random.Random(args.seed).shuffle(jobs)
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(run_job, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda row: row["task_id"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "provider": buddy.PROVIDER,
                "model": buddy.MODEL,
                "seed": args.seed,
                "treatments": rows,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    valid = sum(
        row["status"] == "finding"
        and row["raw_schema_valid"]
        and 0 < row["chars"] <= buddy.MAX_REACTION_CHARS
        for row in rows
    )
    print(f"wrote {len(rows)} treatments; structurally valid {valid}/{len(rows)}")
    return 0 if valid == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
