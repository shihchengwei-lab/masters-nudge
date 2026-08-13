#!/usr/bin/env python3
"""Run one fixed evidence packet through all six production lens prompts."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import random
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import buddy  # noqa: E402
import lens_router  # noqa: E402
import persona_config  # noqa: E402
import source_context  # noqa: E402
from evaluation import quality_eval  # noqa: E402


HERE = Path(__file__).resolve().parent
DEFAULT_FIXTURE = HERE / "lens-fixture-v1.json"
LENSES = ("jeff", "beck", "fowler", "linus", "lamport", "carmack")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or payload.get("event_type") != "stop":
        raise ValueError("unsupported lens fixture")
    expectations = payload.get("lens_expectations")
    if not isinstance(expectations, dict) or set(expectations) != set(LENSES):
        raise ValueError("fixture must define all six lens expectations")
    source = payload.get("source")
    required = ("task_anchor", "last_assistant_message", "tool_evidence")
    if not isinstance(source, dict) or any(not str(source.get(key) or "").strip() for key in required):
        raise ValueError("fixture source packet is incomplete")
    return payload


def build_packet(fixture: dict[str, Any]) -> str:
    source = fixture["source"]
    return source_context.build_stop_packet(
        task_anchor=source["task_anchor"],
        last_assistant_message=source["last_assistant_message"],
        tool_evidence=source["tool_evidence"],
        agentcam_evidence=source.get("agentcam_evidence", ""),
    )


def route_for_lens(lens: str) -> lens_router.ReviewRoute:
    if lens not in LENSES:
        raise ValueError(f"unsupported lens: {lens}")
    stage = persona_config.LENS_STAGES.get(lens, "forced")
    return lens_router.ReviewRoute(stage, lens, lens, "", "", "evaluation")


def build_jobs(fixture: dict[str, Any], *, repeats: int, seed: int) -> list[dict[str, Any]]:
    packet = build_packet(fixture)
    jobs = []
    for lens in LENSES:
        route = route_for_lens(lens)
        system_prompt = buddy.build_system_prompt(route)
        if not system_prompt:
            raise RuntimeError(f"unable to build {lens} prompt")
        for repeat in range(1, repeats + 1):
            jobs.append(
                {
                    "job_id": f"{lens}-{repeat}",
                    "lens": lens,
                    "repeat": repeat,
                    "packet": packet,
                    "packet_sha256": hashlib.sha256(packet.encode("utf-8")).hexdigest(),
                    "system_prompt": system_prompt,
                }
            )
    random.Random(seed).shuffle(jobs)
    return jobs


def run_job(job: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    result = quality_eval.call_reviewer(job["system_prompt"], job["packet"])
    latency_ms = round((time.perf_counter() - started) * 1000)
    raw_finding = str(result.get("finding") or "")
    finding = buddy.sanitize_reaction(raw_finding)
    status = str(result.get("status") or "error")
    if status == "finding" and not finding:
        status = "error"
    raw_output = str(result.get("raw_output") or "")
    return {
        "job_id": job["job_id"],
        "lens": job["lens"],
        "repeat": job["repeat"],
        "packet_sha256": job["packet_sha256"],
        "status": status,
        "finding": finding,
        "characters": len(finding),
        "raw_schema_valid": quality_eval.raw_schema_valid(raw_output),
        "latency_ms": latency_ms,
        "usage": result.get("usage") or {},
        "raw_output": raw_output,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260823)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.repeats < 1 or args.workers < 1:
        raise SystemExit("repeats and workers must be positive")
    fixture = load_fixture(args.fixture)
    jobs = build_jobs(fixture, repeats=args.repeats, seed=args.seed)
    if args.dry_run:
        print(json.dumps({"jobs": len(jobs), "order": [job["job_id"] for job in jobs]}))
        return 0
    if args.output_dir.exists():
        raise SystemExit(f"refusing to overwrite output directory: {args.output_dir}")
    args.output_dir.mkdir(parents=True)
    manifest = {
        "schema_version": 1,
        "evaluation": "six-lens-differentiation-v1",
        "fixture_id": fixture["id"],
        "provider": buddy.PROVIDER,
        "model": buddy.MODEL,
        "repeats": args.repeats,
        "seed": args.seed,
        "workers": args.workers,
        "jobs": len(jobs),
        "job_order": [job["job_id"] for job in jobs],
        "packet_sha256": jobs[0]["packet_sha256"],
        "fixture_sha256": sha256_file(args.fixture),
        "base_prompt_sha256": sha256_file(buddy.PROMPT_FILE),
        "schema_sha256": sha256_file(buddy.OUTPUT_SCHEMA_FILE),
        "persona_sha256": {
            lens: sha256_file(buddy.PERSONA_DIR / f"{lens}.txt") for lens in LENSES
        },
        "runner_sha256": sha256_file(Path(__file__)),
        "hero_selection_rule": "lowest repeat with a valid finding; no wording edits",
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(run_job, job) for job in jobs]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            row = future.result()
            rows.append(row)
            print(
                f"[{index}/{len(jobs)}] {row['job_id']} {row['status']} {row['characters']} chars",
                flush=True,
            )
    rows.sort(key=lambda row: (LENSES.index(row["lens"]), row["repeat"]))
    (args.output_dir / "runs.json").write_text(
        json.dumps({"schema_version": 1, "runs": rows}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
