#!/usr/bin/env python3
"""Replay one frozen Shader checkpoint through all six production personas."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import random
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import lens_router  # noqa: E402
import shader_router  # noqa: E402
import source_context  # noqa: E402
from masters_nudge import providers  # noqa: E402
from masters_nudge.core import CHECKPOINT_PROMPT  # noqa: E402
from masters_nudge.prompting import build_system_prompt, sanitize_reaction  # noqa: E402


HERE = Path(__file__).resolve().parent
DEFAULT_FIXTURE = HERE / "fixture-v1.json"
PROMPT_FILE = ROOT / "domains" / "shader" / "base-prompt.txt"
PERSONA_DIR = ROOT / "domains" / "shader" / "personas"
SCHEMA_PATH = ROOT / "reaction-schema.json"
LENSES = tuple(shader_router.SHADER_PERSONAS)
REPEATS = 3
DEFAULT_SEED = 20260817
DEFAULT_WORKERS = 2
DEFAULT_TIMEOUT_SEC = 90
REPLAY_PROVIDERS = ("grok", "claude", "codex")
PROVIDER_MANIFEST = {
    "grok": ("grok-subscription-cli", "subscription default"),
    "claude": ("claude-subscription-cli", "sonnet"),
    "codex": ("codex-subscription-cli", "gpt-5.6-sol"),
}

_TERMINAL_PUNCTUATION = ("。", "！", "？", ".", "!", "?")
_CLAUSE_SPLIT_RE = re.compile(r"[，,；;。！？!?]\s*")
_IMPERATIVE_PREFIX_RE = re.compile(
    r"^(?:請|先|應該|應|必須|務必|立即|立刻|停止|停|凍結|重跑|重測|"
    r"改用|改|加入|移除|檢查|確認|驗證|記錄|比較|避免|不要|不准|把|用)"
)
_REVIEW_TONE_MARKERS = (
    "否決",
    "驗收",
    "修正",
    "下一步",
    "建議",
    "應該",
    "必須",
    "重跑",
    "重測",
    "先做",
    "通過則",
)
_PERSON_NAMES = (
    "Akenine",
    "Möller",
    "Moller",
    "Carmack",
    "Karis",
    "Lottes",
    "Quilez",
    "Tatarchuk",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_fixture(path: Path = DEFAULT_FIXTURE) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("unsupported Shader replay fixture schema")
    if payload.get("event_type") != "checkpoint":
        raise ValueError("Shader replay fixture must be a checkpoint")
    expectations = payload.get("lens_expectations")
    if not isinstance(expectations, dict) or set(expectations) != set(LENSES):
        raise ValueError("fixture must define all six Shader lens expectations")
    source = payload.get("source")
    required = ("task_anchor", "event_context", "assistant_context")
    if not isinstance(source, dict) or any(
        not str(source.get(key) or "").strip() for key in required
    ):
        raise ValueError("Shader checkpoint source is incomplete")
    return payload


def build_packet(fixture: dict[str, Any]) -> str:
    source = fixture["source"]
    return source_context.build_checkpoint_packet(
        task_anchor=source["task_anchor"],
        event_context=source["event_context"],
        assistant_context=source["assistant_context"],
    )


def route_for_lens(lens: str) -> lens_router.ReviewRoute:
    if lens not in LENSES:
        raise ValueError(f"unsupported Shader lens: {lens}")
    return lens_router.ReviewRoute(
        "replay", lens, lens, "", "", "shader_prompt_replay"
    )


def prompt_for_lens(lens: str) -> str:
    prompt = build_system_prompt(
        prompt_file=PROMPT_FILE,
        persona_dir=PERSONA_DIR,
        data_dir=ROOT,
        route=route_for_lens(lens),
        persona_names=shader_router.SHADER_PERSONAS,
        domain="shader",
    )
    if not prompt:
        raise RuntimeError(f"unable to build Shader prompt for {lens}")
    return f"{prompt}{CHECKPOINT_PROMPT}"


def build_jobs(
    fixture: dict[str, Any],
    *,
    repeats: int,
    seed: int,
    lenses: tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    if repeats < 1:
        raise ValueError("repeats must be positive")
    selected_lenses = tuple(lenses or LENSES)
    if (
        not selected_lenses
        or len(selected_lenses) != len(set(selected_lenses))
        or any(lens not in LENSES for lens in selected_lenses)
    ):
        raise ValueError("lenses must be unique supported Shader personas")
    packet = build_packet(fixture)
    packet_sha256 = hashlib.sha256(packet.encode("utf-8")).hexdigest()
    jobs = []
    for lens in LENSES:
        system_prompt = prompt_for_lens(lens)
        for repeat in range(1, repeats + 1):
            jobs.append(
                {
                    "job_id": f"{lens}-{repeat}",
                    "lens": lens,
                    "repeat": repeat,
                    "packet": packet,
                    "packet_sha256": packet_sha256,
                    "system_prompt": system_prompt,
                }
            )
    random.Random(seed).shuffle(jobs)
    selected = set(selected_lenses)
    return [job for job in jobs if job["lens"] in selected]


def imperative_flags(finding: str) -> list[str]:
    hits = []
    for clause in _CLAUSE_SPLIT_RE.split(str(finding or "")):
        match = _IMPERATIVE_PREFIX_RE.match(clause.strip())
        if match:
            hits.append(match.group(0))
    return hits


def review_tone_flags(finding: str) -> list[str]:
    return [marker for marker in _REVIEW_TONE_MARKERS if marker in finding]


def persona_name_hits(finding: str) -> list[str]:
    folded = str(finding or "").casefold()
    return [name for name in _PERSON_NAMES if name.casefold() in folded]


def call_grok(
    system_prompt: str,
    packet: str,
    timeout_sec: int,
    *,
    reasoning_effort: str = "",
) -> dict[str, Any]:
    errors: list[str] = []
    result = providers.call_grok_result(
        system_prompt,
        packet,
        "",
        schema_path=SCHEMA_PATH,
        timeout_sec=timeout_sec,
        reasoning_effort=reasoning_effort,
        capture_raw=True,
        log_error=errors.append,
    )
    result["provider_errors"] = errors
    return result


def call_claude(system_prompt: str, packet: str, timeout_sec: int) -> dict[str, Any]:
    errors: list[str] = []
    result = providers.call_claude_result(
        system_prompt,
        packet,
        "sonnet",
        schema_path=SCHEMA_PATH,
        timeout_sec=timeout_sec,
        capture_raw=True,
        log_error=errors.append,
    )
    result["provider_errors"] = errors
    return result


def call_codex(system_prompt: str, packet: str, timeout_sec: int) -> dict[str, Any]:
    errors: list[str] = []
    result = providers.call_codex_result(
        system_prompt,
        packet,
        "gpt-5.6-sol",
        schema_path=SCHEMA_PATH,
        timeout_sec=timeout_sec,
        capture_raw=True,
        log_error=errors.append,
    )
    result["provider_errors"] = errors
    return result


def score_row(
    *,
    lens: str,
    repeat: int,
    result: dict[str, Any],
    latency_ms: int,
    job_id: str | None = None,
    packet_sha256: str = "",
) -> dict[str, Any]:
    status = str(result.get("status") or "error")
    if status not in {"finding", "no_finding", "error"}:
        status = "error"
    raw_finding = str(result.get("finding") or "")
    production_finding = sanitize_reaction(raw_finding)
    return {
        "job_id": job_id or f"{lens}-{repeat}",
        "lens": lens,
        "repeat": repeat,
        "packet_sha256": packet_sha256,
        "status": status,
        "error_kind": str(result.get("error_kind") or ""),
        "raw_finding": raw_finding,
        "production_finding": production_finding,
        "raw_characters": len(raw_finding),
        "within_52_chars": len(raw_finding) <= 52,
        "sentence_complete": bool(
            raw_finding and raw_finding.rstrip().endswith(_TERMINAL_PUNCTUATION)
        ),
        "imperative_flags": imperative_flags(raw_finding),
        "review_tone_flags": review_tone_flags(raw_finding),
        "persona_name_hits": persona_name_hits(raw_finding),
        "latency_ms": latency_ms,
        "usage": result.get("usage") or {},
        "raw_output": str(result.get("raw_output") or ""),
        "provider_errors": list(result.get("provider_errors") or []),
    }


def run_job(
    job: dict[str, Any],
    *,
    timeout_sec: int,
    provider: str = "grok",
    reasoning_effort: str = "",
) -> dict[str, Any]:
    if provider not in REPLAY_PROVIDERS:
        raise ValueError(f"unsupported replay provider: {provider}")
    started = time.perf_counter()
    if provider == "grok" and reasoning_effort:
        result = call_grok(
            job["system_prompt"],
            job["packet"],
            timeout_sec,
            reasoning_effort=reasoning_effort,
        )
    else:
        caller = {
            "grok": call_grok,
            "claude": call_claude,
            "codex": call_codex,
        }[provider]
        result = caller(job["system_prompt"], job["packet"], timeout_sec)
    latency_ms = round((time.perf_counter() - started) * 1000)
    return score_row(
        lens=job["lens"],
        repeat=job["repeat"],
        result=result,
        latency_ms=latency_ms,
        job_id=job["job_id"],
        packet_sha256=job["packet_sha256"],
    )


def _rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 3) if denominator else None


def _nearest_rank(values: list[int], percentile: float) -> int | None:
    if not values:
        return None
    if not 0 < percentile <= 1:
        raise ValueError("percentile must be in (0, 1]")
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


def latency_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    attempts = [
        int(row["latency_ms"])
        for row in rows
        if isinstance(row.get("latency_ms"), (int, float))
        and int(row["latency_ms"]) >= 0
    ]
    successful = [
        int(row["latency_ms"])
        for row in rows
        if row.get("status") in {"finding", "no_finding"}
        and isinstance(row.get("latency_ms"), (int, float))
        and int(row["latency_ms"]) >= 0
    ]
    return {
        "method": "nearest-rank",
        "attempts": {
            "samples": len(attempts),
            "p95": _nearest_rank(attempts, 0.95),
        },
        "successful": {
            "samples": len(successful),
            "p95": _nearest_rank(successful, 0.95),
        },
    }


def _theme_hits(finding: str, terms: list[str]) -> list[str]:
    folded = finding.casefold()
    return [term for term in terms if term.casefold() in folded]


def analyze(
    fixture: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    lenses: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    selected_lenses = tuple(lenses or LENSES)
    if (
        not selected_lenses
        or len(selected_lenses) != len(set(selected_lenses))
        or any(lens not in LENSES for lens in selected_lenses)
    ):
        raise ValueError("lenses must be unique supported Shader personas")
    expected = {
        (lens, repeat)
        for lens in selected_lenses
        for repeat in range(1, REPEATS + 1)
    }
    actual = {(row["lens"], int(row["repeat"])) for row in rows}
    findings = [row for row in rows if row.get("status") == "finding"]
    timeouts = [row for row in rows if row.get("error_kind") == "timeout"]
    by_lens = {}
    selected = []
    for lens in selected_lenses:
        lens_rows = sorted(
            (row for row in rows if row["lens"] == lens),
            key=lambda row: int(row["repeat"]),
        )
        lens_findings = [row for row in lens_rows if row.get("status") == "finding"]
        terms = fixture["lens_expectations"][lens]["terms"]
        aligned = []
        for row in lens_findings:
            hits = _theme_hits(row["raw_finding"], terms)
            if hits:
                aligned.append({"repeat": row["repeat"], "hits": hits})
        if lens_findings:
            selected.append(lens_findings[0]["raw_finding"])
        by_lens[lens] = {
            "calls": len(lens_rows),
            "findings": len(lens_findings),
            "timeouts": sum(row.get("error_kind") == "timeout" for row in lens_rows),
            "latency_ms": latency_summary(lens_rows),
            "non_imperative": sum(not row["imperative_flags"] for row in lens_findings),
            "complete": sum(
                row["within_52_chars"] and row["sentence_complete"]
                for row in lens_findings
            ),
            "theme_term_aligned": len(aligned),
            "theme_hits": aligned,
        }

    denominator = len(findings)
    non_imperative = sum(not row["imperative_flags"] for row in findings)
    complete = sum(
        row["within_52_chars"] and row["sentence_complete"] for row in findings
    )
    review_free = sum(not row["review_tone_flags"] for row in findings)
    rates = {
        "non_imperative": _rate(non_imperative, denominator),
        "complete_finding": _rate(complete, denominator),
        "review_tone_free": _rate(review_free, denominator),
    }
    evaluable = all(item["findings"] >= 2 for item in by_lens.values())
    gates = {
        "integrity": len(rows) == len(expected) and actual == expected,
        "evaluable": evaluable,
        "non_imperative_80pct": bool(
            rates["non_imperative"] is not None
            and rates["non_imperative"] >= 0.8
        ),
        "complete_90pct": bool(
            rates["complete_finding"] is not None
            and rates["complete_finding"] >= 0.9
        ),
        "unique_representatives": (
            len(selected) == len(selected_lenses)
            and len(set(selected)) == len(selected_lenses)
        ),
        "no_person_name_leakage": not any(row["persona_name_hits"] for row in findings),
    }
    return {
        "schema_version": 1,
        "fixture_id": fixture["id"],
        "lenses": list(selected_lenses),
        "rows": len(rows),
        "timeouts": len(timeouts),
        "prompt_quality_denominator": denominator,
        "latency_ms": latency_summary(rows),
        "rates": rates,
        "by_lens": by_lens,
        "gates": gates,
        "automated_passed": all(gates.values()),
        "claim_boundary": (
            "Theme terms and imperative flags are diagnostics. Blind-spot strength "
            "and persona alignment require human review of raw findings."
        ),
        "latency_claim_boundary": (
            "Observed sample p95 uses nearest-rank. Attempt p95 includes timeout "
            "wall time; successful p95 excludes every error. With three calls per "
            "lens, per-lens p95 equals that lens's maximum observed latency and is "
            "not a population tail-latency estimate."
        ),
    }


def human_review_template(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "rubric": {
            "observation_not_instruction": "true or false",
            "complete_finding": "true or false",
            "blind_spot_strength": "0, 1, or 2",
            "persona_aligned": "true or false",
        },
        "reviews": [
            {
                "job_id": row["job_id"],
                "lens": row["lens"],
                "repeat": row["repeat"],
                "status": row["status"],
                "raw_finding": row["raw_finding"],
                "judgment": {
                    "observation_not_instruction": None,
                    "complete_finding": None,
                    "blind_spot_strength": None,
                    "persona_aligned": None,
                    "note": "",
                },
            }
            for row in rows
        ],
    }


def git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=REPEATS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--timeout-sec", type=int, default=DEFAULT_TIMEOUT_SEC)
    parser.add_argument(
        "--provider",
        choices=REPLAY_PROVIDERS,
        default="grok",
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=("low", "medium", "high", "xhigh"),
        default="",
    )
    parser.add_argument(
        "--lenses",
        nargs="+",
        choices=LENSES,
        default=list(LENSES),
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.repeats != REPEATS:
        raise SystemExit(f"protocol v1 requires exactly {REPEATS} repeats")
    if args.workers < 1 or args.timeout_sec < 1:
        raise SystemExit("workers and timeout-sec must be positive")
    if args.reasoning_effort and args.provider != "grok":
        raise SystemExit("reasoning-effort is supported only for Grok replay")
    fixture = load_fixture(args.fixture)
    selected_lenses = tuple(args.lenses)
    jobs = build_jobs(
        fixture,
        repeats=args.repeats,
        seed=args.seed,
        lenses=selected_lenses,
    )
    if args.dry_run:
        print(
            json.dumps(
                {
                    "jobs": len(jobs),
                    "provider": args.provider,
                    "reasoning_effort": args.reasoning_effort or "model default",
                    "packet_sha256": jobs[0]["packet_sha256"],
                    "order": [job["job_id"] for job in jobs],
                },
                ensure_ascii=False,
            )
        )
        return 0
    if args.output_dir.exists():
        raise SystemExit(f"refusing to overwrite output directory: {args.output_dir}")
    args.output_dir.mkdir(parents=True)
    provider_name, provider_model = PROVIDER_MANIFEST[args.provider]
    manifest = {
        "schema_version": 1,
        "evaluation": fixture["evaluation"],
        "fixture_id": fixture["id"],
        "provider": provider_name,
        "model": provider_model,
        "reasoning_effort": args.reasoning_effort or "model default",
        "git_commit": git_commit(),
        "repeats": args.repeats,
        "seed": args.seed,
        "workers": args.workers,
        "timeout_sec": args.timeout_sec,
        "jobs": len(jobs),
        "lenses": list(selected_lenses),
        "job_order": [job["job_id"] for job in jobs],
        "packet_sha256": jobs[0]["packet_sha256"],
        "fixture_sha256": sha256_file(args.fixture),
        "base_prompt_sha256": sha256_file(PROMPT_FILE),
        "checkpoint_prompt_sha256": hashlib.sha256(
            CHECKPOINT_PROMPT.encode("utf-8")
        ).hexdigest(),
        "schema_sha256": sha256_file(SCHEMA_PATH),
        "persona_sha256": {
            lens: sha256_file(PERSONA_DIR / f"{lens}.txt") for lens in LENSES
        },
        "runner_sha256": sha256_file(Path(__file__)),
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(
                run_job,
                job,
                timeout_sec=args.timeout_sec,
                provider=args.provider,
                reasoning_effort=args.reasoning_effort,
            )
            for job in jobs
        ]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            row = future.result()
            rows.append(row)
            print(
                f"[{index}/{len(jobs)}] {row['job_id']} {row['status']} "
                f"{row['raw_characters']} chars {row['latency_ms']} ms",
                flush=True,
            )
    rows.sort(key=lambda row: (LENSES.index(row["lens"]), row["repeat"]))
    (args.output_dir / "runs.json").write_text(
        json.dumps({"schema_version": 1, "runs": rows}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "analysis.json").write_text(
        json.dumps(
            analyze(fixture, rows, lenses=selected_lenses),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "human-review.json").write_text(
        json.dumps(human_review_template(rows), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
