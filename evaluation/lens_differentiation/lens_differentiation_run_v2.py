#!/usr/bin/env python3
"""Run the non-terminal six-lens checkpoint without changing frozen v1 artifacts."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import random
from pathlib import Path
from typing import Any

import buddy
import lens_router
import persona_config
import source_context
from evaluation.lens_differentiation import lens_differentiation_run as base


HERE = Path(__file__).resolve().parent
DEFAULT_FIXTURE = HERE / "lens-fixture-v2.json"
LENSES = base.LENSES


def load_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or payload.get("event_type") != "checkpoint":
        raise ValueError("unsupported v2 lens fixture")
    if set(payload.get("lens_expectations") or {}) != set(LENSES):
        raise ValueError("fixture must define all six lens expectations")
    source = payload.get("source") or {}
    required = ("task_anchor", "event_context", "assistant_context")
    if any(not str(source.get(key) or "").strip() for key in required):
        raise ValueError("checkpoint source is incomplete")
    return payload


def build_packet(fixture: dict[str, Any]) -> str:
    source = fixture["source"]
    return source_context.build_checkpoint_packet(
        task_anchor=source["task_anchor"],
        event_context=source["event_context"],
        assistant_context=source["assistant_context"],
    )


def build_jobs(fixture: dict[str, Any], *, repeats: int, seed: int) -> list[dict[str, Any]]:
    packet = build_packet(fixture)
    jobs = []
    for lens in LENSES:
        route = base.route_for_lens(lens)
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260824)
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
        "evaluation": fixture["evaluation"],
        "fixture_id": fixture["id"],
        "event_type": fixture["event_type"],
        "provider": buddy.PROVIDER,
        "model": buddy.MODEL,
        "reviewer_cli_version": "codex-cli 0.147.0",
        "repeats": args.repeats,
        "seed": args.seed,
        "workers": args.workers,
        "jobs": len(jobs),
        "job_order": [job["job_id"] for job in jobs],
        "packet_sha256": jobs[0]["packet_sha256"],
        "fixture_sha256": base.sha256_file(args.fixture),
        "base_prompt_sha256": base.sha256_file(buddy.PROMPT_FILE),
        "schema_sha256": base.sha256_file(buddy.OUTPUT_SCHEMA_FILE),
        "persona_sha256": {
            lens: base.sha256_file(buddy.PERSONA_DIR / f"{lens}.txt") for lens in LENSES
        },
        "runner_sha256": base.sha256_file(Path(__file__)),
        "hero_selection_rule": "lowest repeat with a valid finding; no wording edits",
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(base.run_job, job) for job in jobs]
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
