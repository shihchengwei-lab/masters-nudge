from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
WORK_ROOT = Path(os.environ.get(
    "MASTERS_NUDGE_FORMAL_AB_ROOT",
    r"C:\Users\kk789\AppData\Local\Temp\masters-nudge-formal-ab-20260829-positive-v5",
))
SEED = "taste-blind-v1-2026-08-29"
REDACTIONS = (
    re.compile(r"masters['’]? nudge", re.IGNORECASE),
    re.compile(r"\bnudge\b", re.IGNORECASE),
    re.compile(r"\b(?:linus|torvalds|fowler|beck|carmack|hickey|feathers)\b", re.IGNORECASE),
    re.compile(r"獨立第二意見|大師(?:的)?品味|品味注入"),
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def redact(text: str) -> str:
    value = text
    for pattern in REDACTIONS:
        value = pattern.sub("[redacted treatment cue]", value)
    value = re.sub(r"(?i)\\runs\\[ab](?=\\|\b)", r"\\runs\\candidate", value)
    return value.strip()


def agent_messages(trace_path: Path) -> list[str]:
    messages: list[str] = []
    for raw in trace_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "item.completed":
            continue
        item = event.get("item") or {}
        if item.get("type") != "agent_message":
            continue
        text = item.get("text")
        if isinstance(text, str) and text.strip():
            messages.append(redact(text)[:4000])
    return messages


def label_map(task_key: str, x_is_a: set[str]) -> dict[str, str]:
    return {"X": "a", "Y": "b"} if task_key in x_is_a else {"X": "b", "Y": "a"}


def prepare() -> None:
    contract = read_json(HERE / "contract.json")
    rubric = HERE / "taste-rubric.json"
    schema = HERE / "taste-rating-schema.json"
    blind_root = HERE / "taste-blind"
    if blind_root.exists() and any(path.is_file() for path in blind_root.rglob("*")):
        raise SystemExit(f"Refusing to overwrite frozen blind material: {blind_root}")

    tasks = contract["provisional_tasks"]
    ranked_keys = sorted(
        (task["task_key"] for task in tasks),
        key=lambda key: hashlib.sha256(f"{SEED}:{key}".encode()).hexdigest(),
    )
    x_is_a = set(ranked_keys[: len(ranked_keys) // 2])
    maps: dict[str, Any] = {}
    counts: Counter[str] = Counter()
    for task in tasks:
        key = task["task_key"]
        task_record = read_json(WORK_ROOT / "tasks" / key / "task.json")
        mapping = label_map(key, x_is_a)
        maps[key] = mapping
        counts[mapping["X"]] += 1
        packet: dict[str, Any] = {
            "task_key": key,
            "problem_statement": task_record["problem_statement"],
            "instructions": "Compare only engineering taste. Correctness and test activity are intentionally absent and must not be inferred.",
            "candidates": {},
        }
        for label in ("X", "Y"):
            arm = mapping[label]
            run_root = WORK_ROOT / "tasks" / key / "runs" / arm
            packet["candidates"][label] = {
                "visible_trajectory": agent_messages(run_root / "codex-events.jsonl"),
                "product_patch": redact((run_root / "product.patch").read_text(encoding="utf-8", errors="replace")),
            }
        write_json(blind_root / key / "packet.json", packet)

    metadata = {
        "schema_version": 1,
        "seed": SEED,
        "rubric_sha256": sha256(rubric),
        "rating_schema_sha256": sha256(schema),
        "task_count": len(maps),
        "x_contains_arm_counts": dict(sorted(counts.items())),
        "allocation": "SHA-256 rank by seed; first half X=A, second half X=B",
        "pre_rating_amendment": "Initial parity allocation yielded 2/8 positional imbalance. Replaced before any rating with deterministic 5/5 allocation.",
        "material": "problem statement, chronological agent messages, final product patch",
        "excluded": "commands, test outcomes, safety scores, hook events, treatment/persona labels",
    }
    write_json(HERE / "taste-blind-metadata.json", metadata)
    write_json(HERE / "taste-blind-map.json", maps)
    print(json.dumps(metadata, ensure_ascii=False))


def rate_one(task_dir: Path, model: str, reasoning: str) -> dict[str, Any]:
    output = task_dir / "rating.json"
    events = task_dir / "rater-events.jsonl"
    prompt = (
        "You are an independent blinded evaluator. Evaluate X and Y exactly under the frozen "
        "rubric below. Do not use tools, infer treatment, or score correctness/test activity. "
        "Copy packet.task_key exactly into task_key. Return only the JSON required by the output schema.\n\n"
        "FROZEN RUBRIC:\n"
        + (HERE / "taste-rubric.json").read_text(encoding="utf-8")
        + "\nBLINDED PACKET:\n"
        + (task_dir / "packet.json").read_text(encoding="utf-8")
    )
    command = [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "--sandbox", "read-only", "--json",
        "--model", model, "-c", f'model_reasoning_effort="{reasoning}"',
        "--output-schema", str(HERE / "taste-rating-schema.json"),
        "--output-last-message", str(output), "-C", str(task_dir), "-",
    ]
    started = time.monotonic()
    print(f"RATING_START {task_dir.name}", flush=True)
    with events.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=stream,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        assert process.stdin is not None
        process.stdin.write(prompt)
        process.stdin.close()
        while process.poll() is None:
            elapsed = int(time.monotonic() - started)
            print(f"RATING_HEARTBEAT {task_dir.name} elapsed={elapsed}s", flush=True)
            time.sleep(15)
    elapsed = round(time.monotonic() - started, 3)
    if process.returncode != 0 or not output.exists():
        raise RuntimeError(f"rater failed for {task_dir.name}: rc={process.returncode}")
    rating = read_json(output)
    if rating.get("task_key") != task_dir.name:
        raise RuntimeError(f"task key mismatch for {task_dir.name}: {rating.get('task_key')}")
    print(f"RATING_DONE {task_dir.name} elapsed={elapsed}s winner={rating['winner']}", flush=True)
    return rating


def rate(model: str, reasoning: str) -> None:
    blind_root = HERE / "taste-blind"
    ratings = []
    for task_dir in sorted(path for path in blind_root.iterdir() if path.is_dir()):
        if (task_dir / "rating.json").exists() and read_json(task_dir / "rating.json").get("task_key") == task_dir.name:
            rating = read_json(task_dir / "rating.json")
            print(f"RATING_REUSE {task_dir.name} winner={rating['winner']}", flush=True)
        else:
            rating = rate_one(task_dir, model, reasoning)
        ratings.append(rating)
    write_json(HERE / "taste-blind-ratings.json", {"model": model, "reasoning": reasoning, "ratings": ratings})


def unblind() -> None:
    maps = read_json(HERE / "taste-blind-map.json")
    rated = read_json(HERE / "taste-blind-ratings.json")
    verdicts = []
    counts: Counter[str] = Counter()
    for rating in rated["ratings"]:
        key = rating["task_key"]
        winner = rating["winner"]
        if winner == "tie":
            treatment_winner = "tie"
        else:
            treatment_winner = maps[key][winner].upper()
        counts[treatment_winner] += 1
        verdicts.append({
            "task_key": key,
            "blind_winner": winner,
            "treatment_winner": treatment_winner,
            "confidence": rating["confidence"],
            "reason": rating["reason"],
            "arm_a": rating["candidate_x"] if maps[key]["X"] == "a" else rating["candidate_y"],
            "arm_b": rating["candidate_x"] if maps[key]["X"] == "b" else rating["candidate_y"],
        })
    result = {
        "schema_version": 1,
        "task_count": len(verdicts),
        "summary": {"a_wins": counts["A"], "b_wins": counts["B"], "ties": counts["tie"]},
        "verdicts": verdicts,
    }
    write_json(HERE / "taste-results.json", result)
    print(json.dumps(result["summary"], ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    rate_parser = sub.add_parser("rate")
    rate_parser.add_argument("--model", default="gpt-5.6-sol")
    rate_parser.add_argument("--reasoning", default="medium")
    sub.add_parser("unblind")
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "rate":
        rate(args.model, args.reasoning)
    else:
        unblind()


if __name__ == "__main__":
    main()
