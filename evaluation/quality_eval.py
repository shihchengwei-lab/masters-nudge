#!/usr/bin/env python3
"""Run a bounded, paired Phase A quality evaluation against the real reviewer."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import random
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import buddy  # noqa: E402
import lens_router  # noqa: E402
import persona_config  # noqa: E402
import source_context  # noqa: E402


DEFAULT_FIXTURES = Path(__file__).with_name("fixtures.json")
DEFAULT_RESULTS_DIR = Path(__file__).with_name("results")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_metadata(fixtures_path: Path) -> dict[str, Any]:
    try:
        git_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        git_commit = "unknown"
    prompt_files = [
        buddy.PROMPT_FILE,
        buddy.OUTPUT_SCHEMA_FILE,
        *sorted(buddy.PERSONA_DIR.glob("*.txt")),
    ]
    reviewer_bin = buddy._resolve_codex_bin() if buddy.PROVIDER in {"openai", "codex"} else "claude"
    reviewer_version = "unknown"
    if reviewer_bin:
        try:
            use_shell = str(reviewer_bin).lower().endswith((".cmd", ".bat"))
            command: Any = [reviewer_bin, "--version"]
            if use_shell:
                command = subprocess.list2cmdline(command)
            reviewer_version = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
                shell=use_shell,
                check=True,
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return {
        "git_commit": git_commit,
        "fixtures_sha256": file_sha256(fixtures_path),
        "runner_sha256": file_sha256(Path(__file__)),
        "reviewer_executable": str(reviewer_bin or "unknown"),
        "reviewer_cli_version": reviewer_version,
        "prompt_sha256": {
            str(path.relative_to(ROOT)): file_sha256(path) for path in prompt_files
        },
    }


def load_fixtures(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("unsupported fixture schema")
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("fixtures must be a non-empty list")
    ids = [str(item.get("id") or "") for item in fixtures]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        raise ValueError("fixture ids must be present and unique")
    return fixtures


def build_packet(fixture: dict[str, Any]) -> str:
    source = fixture["source"]
    if fixture["event_type"] == "stop":
        return source_context.build_stop_packet(
            task_anchor=source.get("task_anchor", ""),
            last_assistant_message=source.get("last_assistant_message", ""),
            tool_evidence=source.get("tool_evidence", ""),
            agentcam_evidence=source.get("agentcam_evidence", ""),
        )
    if fixture["event_type"] == "checkpoint":
        return source_context.build_checkpoint_packet(
            task_anchor=source.get("task_anchor", ""),
            event_context=source.get("event_context", ""),
            assistant_context=source.get("assistant_context", ""),
        )
    raise ValueError(f"unsupported event_type: {fixture['event_type']!r}")


def fixture_routes(fixture: dict[str, Any], packet: str) -> dict[str, lens_router.ReviewRoute]:
    stage = str(fixture["stage"])
    primary = persona_config.STAGE_LENSES[stage]
    override, trigger = lens_router._specialist_trigger(packet)
    effective = override or primary
    expected = str(fixture["expected_effective_lens"])
    if effective != expected:
        raise ValueError(
            f"{fixture['id']}: expected route {expected!r}, actual {effective!r}"
        )

    routes = {
        "baseline": lens_router.ReviewRoute(
            stage, "general", "general", "", "", "evaluation"
        ),
        "effective": lens_router.ReviewRoute(
            stage, primary, effective, override, trigger, "evaluation"
        ),
    }
    if override:
        routes["primary"] = lens_router.ReviewRoute(
            stage, primary, primary, "", "", "evaluation"
        )
    return routes


def _structured_raw(raw_output: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(str(raw_output or "").strip())
    except (TypeError, ValueError):
        return None
    if isinstance(payload, dict) and "structured_output" in payload:
        payload = payload.get("structured_output")
    return payload if isinstance(payload, dict) else None


def raw_schema_valid(raw_output: str) -> bool:
    payload = _structured_raw(raw_output)
    if not payload or set(payload) != {"status", "finding"}:
        return False
    status = payload.get("status")
    finding = payload.get("finding")
    if status not in {"finding", "no_finding"} or not isinstance(finding, str):
        return False
    if len(finding) > buddy.MAX_REACTION_CHARS:
        return False
    if status == "finding":
        return bool(finding.strip())
    return finding == ""


def issue_matches(finding: str, concept_groups: Iterable[Iterable[str]]) -> bool:
    normalized = str(finding or "").casefold()
    groups = list(concept_groups)
    return bool(groups) and all(
        any(str(term).casefold() in normalized for term in group) for group in groups
    )


def score_payload(
    fixture: dict[str, Any],
    status: str,
    finding: str,
    raw_output: str,
) -> dict[str, Any]:
    oracle = fixture["oracle"]
    expected_status = str(oracle["expected_status"])
    provider_success = status in {"finding", "no_finding"}
    schema_valid = raw_schema_valid(raw_output) if provider_success else False
    status_correct = provider_success and status == expected_status
    match = (
        issue_matches(finding, oracle.get("concept_groups", []))
        if expected_status == "finding" and status == "finding"
        else None
    )
    correct_silence = (
        status == "no_finding" if expected_status == "no_finding" else None
    )
    sentence_terminated = (
        finding.rstrip().endswith(("。", "！", "？", "!", "?"))
        if status == "finding"
        else None
    )
    correct = bool(
        schema_valid
        and status_correct
        and (match if expected_status == "finding" else correct_silence)
    )
    return {
        "expected_status": expected_status,
        "provider_success": provider_success,
        "raw_schema_valid": schema_valid,
        "status_correct": status_correct,
        "issue_match": match,
        "correct_silence": correct_silence,
        "sentence_terminated": sentence_terminated,
        "correct": correct,
    }


def score_result(
    fixture: dict[str, Any],
    condition: str,
    repeat: int,
    route: lens_router.ReviewRoute,
    call_result: dict[str, Any],
    latency_ms: int,
) -> dict[str, Any]:
    oracle = fixture["oracle"]
    status = str(call_result.get("status") or "error")
    finding = str(call_result.get("finding") or "")
    raw_output = str(call_result.get("raw_output") or "")
    scores = score_payload(fixture, status, finding, raw_output)
    return {
        "fixture_id": fixture["id"],
        "title": fixture["title"],
        "event_type": fixture["event_type"],
        "stage": fixture["stage"],
        "severity": oracle["severity"],
        "condition": condition,
        "repeat": repeat,
        "primary_lens": route.primary_lens,
        "effective_lens": route.effective_lens,
        "status": status,
        "finding": finding,
        "raw_output": raw_output,
        **scores,
        "latency_ms": latency_ms,
        "usage": call_result.get("usage") or {},
    }


def call_reviewer(system_prompt: str, packet: str) -> dict[str, Any]:
    if buddy.PROVIDER in {"openai", "codex"}:
        return buddy.call_codex_result(
            system_prompt, packet, buddy.MODEL, capture_raw=True
        )
    return buddy.call_claude_result(
        system_prompt, packet, buddy.MODEL, capture_raw=True
    )


def _run_job(job: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    result = call_reviewer(job["system_prompt"], job["packet"])
    latency_ms = round((time.perf_counter() - started) * 1000)
    return score_result(
        job["fixture"],
        job["condition"],
        job["repeat"],
        job["route"],
        result,
        latency_ms,
    )


def build_jobs(fixtures: list[dict[str, Any]], repeats: int, seed: int) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = []
    for fixture in fixtures:
        packet = build_packet(fixture)
        for condition, route in fixture_routes(fixture, packet).items():
            system_prompt = buddy.build_system_prompt(route)
            if not system_prompt:
                raise RuntimeError(f"unable to build prompt for {fixture['id']} {condition}")
            for repeat in range(1, repeats + 1):
                jobs.append(
                    {
                        "fixture": fixture,
                        "packet": packet,
                        "condition": condition,
                        "route": route,
                        "system_prompt": system_prompt,
                        "repeat": repeat,
                    }
                )
    random.Random(seed).shuffle(jobs)
    return jobs


def _rate(numerator: int, denominator: int) -> str:
    if not denominator:
        return "n/a"
    return f"{numerator}/{denominator} ({100 * numerator / denominator:.1f}%)"


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"conditions": {}, "paired": {}}
    for condition in sorted({row["condition"] for row in rows}):
        selected = [row for row in rows if row["condition"] == condition]
        positives = [row for row in selected if row["expected_status"] == "finding"]
        negatives = [row for row in selected if row["expected_status"] == "no_finding"]
        findings = [row for row in selected if row["status"] == "finding"]
        summary["conditions"][condition] = {
            "calls": len(selected),
            "provider_success": sum(row["provider_success"] for row in selected),
            "schema_valid": sum(row["raw_schema_valid"] for row in selected),
            "status_correct": sum(row["status_correct"] for row in selected),
            "issue_match": sum(row["issue_match"] is True for row in positives),
            "positive_calls": len(positives),
            "correct_silence": sum(row["correct_silence"] is True for row in negatives),
            "negative_calls": len(negatives),
            "sentence_terminated": sum(
                row.get("sentence_terminated") is True for row in findings
            ),
            "finding_calls": len(findings),
            "finding_chars_total": sum(len(row["finding"]) for row in findings),
            "at_char_limit": sum(
                len(row["finding"]) == buddy.MAX_REACTION_CHARS for row in findings
            ),
            "correct": sum(row["correct"] for row in selected),
            "latency_ms_total": sum(row["latency_ms"] for row in selected),
        }

    by_key = {(row["fixture_id"], row["repeat"], row["condition"]): row for row in rows}
    for treatment, control in (("effective", "baseline"), ("effective", "primary")):
        outcomes = Counter()
        for fixture_id, repeat, condition in list(by_key):
            if condition != treatment:
                continue
            treated = by_key[(fixture_id, repeat, treatment)]
            controlled = by_key.get((fixture_id, repeat, control))
            if not controlled:
                continue
            if treated["correct"] and not controlled["correct"]:
                outcomes["wins"] += 1
            elif controlled["correct"] and not treated["correct"]:
                outcomes["losses"] += 1
            else:
                outcomes["ties"] += 1
        if sum(outcomes.values()):
            summary["paired"][f"{treatment}_vs_{control}"] = dict(outcomes)
    return summary


def render_report(
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    *,
    fixtures_path: Path,
    repeats: int,
    seed: int,
    metadata: dict[str, Any],
) -> str:
    lines = [
        "# Phase A reaction-quality evaluation",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Provider/model: `{buddy.PROVIDER}` / `{buddy.MODEL}`",
        f"- Fixtures: `{fixtures_path}`",
        f"- Repeats: {repeats}",
        f"- Randomization seed: {seed}",
        f"- Git commit: `{metadata['git_commit']}`",
        f"- Fixtures SHA-256: `{metadata['fixtures_sha256']}`",
        f"- Runner SHA-256: `{metadata['runner_sha256']}`",
        f"- Base prompt SHA-256: `{metadata['prompt_sha256']['buddy-prompt.txt']}`",
        f"- Reviewer CLI: `{metadata['reviewer_cli_version']}`",
        "- Interpretation: calibration only; not a formal product-impact claim.",
        "",
        "## Condition summary",
        "",
        "| Condition | Calls | Provider success | Raw schema | Status | Issue match | Correct silence | Avg chars | At 52 | Sentence ended | Oracle match | Avg latency |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for condition, stats in summary["conditions"].items():
        calls = stats["calls"]
        avg_latency = stats["latency_ms_total"] / calls if calls else 0
        avg_chars = (
            stats["finding_chars_total"] / stats["finding_calls"]
            if stats["finding_calls"]
            else 0
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    condition,
                    str(calls),
                    _rate(stats["provider_success"], calls),
                    _rate(stats["schema_valid"], calls),
                    _rate(stats["status_correct"], calls),
                    _rate(stats["issue_match"], stats["positive_calls"]),
                    _rate(stats["correct_silence"], stats["negative_calls"]),
                    f"{avg_chars:.1f}",
                    _rate(stats["at_char_limit"], stats["finding_calls"]),
                    _rate(stats["sentence_terminated"], stats["finding_calls"]),
                    _rate(stats["correct"], calls),
                    f"{avg_latency:.0f} ms",
                ]
            )
            + " |"
        )

    lines.extend(["", "## Paired outcomes", ""])
    for comparison, outcomes in summary["paired"].items():
        lines.append(
            f"- `{comparison}`: {outcomes.get('wins', 0)} wins, "
            f"{outcomes.get('ties', 0)} ties, {outcomes.get('losses', 0)} losses"
        )

    lines.extend(
        [
            "",
            "## Per-call results",
            "",
            "| Fixture | Condition | Lens | Expected | Actual | Chars | Schema | Match | Ended | Correct | Finding |",
            "|---|---|---|---|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in sorted(rows, key=lambda item: (item["fixture_id"], item["condition"], item["repeat"])):
        finding = row["finding"].replace("|", "\\|").replace("\n", " ")
        match = row["issue_match"] if row["issue_match"] is not None else row["correct_silence"]
        lines.append(
            f"| {row['fixture_id']} | {row['condition']} | {row['effective_lens']} | "
            f"{row['expected_status']} | {row['status']} | {len(row['finding'])} | {row['raw_schema_valid']} | "
            f"{match} | {row.get('sentence_terminated')} | {row['correct']} | {finding} |"
        )
    lines.extend(
        [
            "",
            "## Scoring boundary",
            "",
            "`issue_match` is a deterministic concept-group check. A miss can therefore be either a true miss or a defensible wording that needs blind human adjudication. `Sentence ended` only checks final punctuation and is a review queue, not proof that wording is complete or incomplete. Raw JSONL is retained for both reviews. Correct silence is objective for these seeded clean cases.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20260813)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument(
        "--fixture",
        action="append",
        dest="fixture_ids",
        help="run only the named fixture; may be repeated",
    )
    parser.add_argument(
        "--rescore-jsonl",
        type=Path,
        help="rescore existing JSONL without making reviewer calls",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.repeats < 1 or args.workers < 1:
        raise SystemExit("repeats and workers must be positive")
    fixtures = load_fixtures(args.fixtures)
    metadata = run_metadata(args.fixtures)
    if args.fixture_ids:
        wanted = set(args.fixture_ids)
        fixtures = [fixture for fixture in fixtures if fixture["id"] in wanted]
        missing = wanted - {fixture["id"] for fixture in fixtures}
        if missing:
            raise SystemExit(f"unknown fixture ids: {', '.join(sorted(missing))}")
    if args.rescore_jsonl:
        fixture_map = {fixture["id"]: fixture for fixture in fixtures}
        rows = [
            json.loads(line)
            for line in args.rescore_jsonl.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        for row in rows:
            fixture = fixture_map.get(row["fixture_id"])
            if fixture is None:
                raise SystemExit(f"missing fixture for result: {row['fixture_id']}")
            row.update(
                score_payload(
                    fixture,
                    str(row.get("status") or "error"),
                    str(row.get("finding") or ""),
                    str(row.get("raw_output") or ""),
                )
            )
        summary = aggregate(rows)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = args.output_dir / "calibration-latest.jsonl"
        report_path = args.output_dir / "calibration-latest.md"
        jsonl_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
        report_path.write_text(
            render_report(
                rows,
                summary,
                fixtures_path=args.fixtures,
                repeats=max(int(row.get("repeat") or 1) for row in rows),
                seed=args.seed,
                metadata=metadata,
            ),
            encoding="utf-8",
        )
        print(f"rescored {len(rows)} rows", flush=True)
        print(f"wrote {jsonl_path}", flush=True)
        print(f"wrote {report_path}", flush=True)
        return 0
    jobs = build_jobs(fixtures, args.repeats, args.seed)
    print(
        f"running {len(jobs)} calls with {args.workers} workers "
        f"using {buddy.PROVIDER}/{buddy.MODEL}",
        flush=True,
    )
    rows: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(_run_job, job) for job in jobs]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            row = future.result()
            rows.append(row)
            print(
                f"[{index}/{len(jobs)}] {row['fixture_id']} {row['condition']} "
                f"{row['status']} correct={row['correct']} {row['latency_ms']}ms",
                flush=True,
            )

    rows.sort(key=lambda item: (item["fixture_id"], item["condition"], item["repeat"]))
    summary = aggregate(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = args.output_dir / "calibration-latest.jsonl"
    report_path = args.output_dir / "calibration-latest.md"
    jsonl_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )
    report_path.write_text(
        render_report(
            rows,
            summary,
            fixtures_path=args.fixtures,
            repeats=args.repeats,
            seed=args.seed,
            metadata=metadata,
        ),
        encoding="utf-8",
    )
    print(f"wrote {jsonl_path}", flush=True)
    print(f"wrote {report_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
