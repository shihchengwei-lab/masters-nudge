from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SEED = "opus5-seven-reviewer-blind-v1"
RUBRIC = HERE / "comparison-rubric.json"
SCHEMA = HERE / "rating-schema.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def redact(text: str) -> str:
    value = re.sub(r"(?i)\\runs\\[ab](?=\\|\b)", r"\\runs\\candidate", text)
    value = re.sub(r"(?i)\b(?:openai|anthropic|gpt-5\.6-sol|claude-opus-5)\b", "[provider]", value)
    return value


def prepare() -> None:
    inputs = read_json(HERE / "inputs.json")["items"]
    results = {item["task"]: item for item in read_json(HERE / "results.json")["items"]}
    blind_root = HERE / "blind"
    if blind_root.exists() and any(path.name == "rating.json" for path in blind_root.rglob("rating.json")):
        raise RuntimeError("ratings already exist; refusing to regenerate blind allocation")
    ranked = sorted(
        (item["task"] for item in inputs),
        key=lambda task: hashlib.sha256(f"{SEED}:{task}".encode()).hexdigest(),
    )
    x_is_sol = set(ranked[: len(ranked) // 2])
    mapping = {}
    for item in inputs:
        task = item["task"]
        labels = {"X": "sol", "Y": "opus"} if task in x_is_sol else {"X": "opus", "Y": "sol"}
        mapping[task] = labels
        findings = {
            "sol": str(item["sol_review"].get("reaction") or ""),
            "opus": str(results[task].get("finding") or ""),
        }
        packet = {
            "task": task,
            "source_packet": redact(str(item["source_packet"])),
            "candidates": {label: redact(findings[provider]) for label, provider in labels.items()},
        }
        write_json(blind_root / task / "packet.json", packet)
    metadata = {
        "schema_version": 1,
        "seed": SEED,
        "rubric_sha256": hashlib.sha256(RUBRIC.read_bytes()).hexdigest(),
        "schema_sha256": hashlib.sha256(SCHEMA.read_bytes()).hexdigest(),
        "x_provider_counts": dict(Counter(labels["X"] for labels in mapping.values())),
        "mapping": mapping,
    }
    write_json(HERE / "blind-metadata.json", metadata)
    print(json.dumps({k: v for k, v in metadata.items() if k != "mapping"}, ensure_ascii=False))


def rate_one(root: Path) -> dict[str, Any]:
    output = root / "rating.json"
    if output.exists():
        return read_json(output)
    prompt = (
        "You are an independent blinded evaluator. Compare the two candidate Nudge outputs under "
        "the frozen rubric. The source packet is context, not an answer to grade. Do not infer providers, "
        "reward verbosity, or score eventual test success. Copy packet.task exactly into task. "
        "Return only schema-compliant JSON.\n\nFROZEN RUBRIC:\n"
        + RUBRIC.read_text(encoding="utf-8")
        + "\nBLINDED PACKET:\n"
        + (root / "packet.json").read_text(encoding="utf-8")
    )
    command = [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "--sandbox", "read-only", "--json",
        "--model", "gpt-5.6-sol", "-c", 'model_reasoning_effort="medium"',
        "--output-schema", str(SCHEMA), "--output-last-message", str(output),
        "-C", str(root), "-",
    ]
    events = root / "rater-events.jsonl"
    started = time.monotonic()
    print(f"[rating] starting {root.name}", flush=True)
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
            print(f"[rating] {root.name} running {int(time.monotonic()-started)}s", flush=True)
            time.sleep(15)
    if process.returncode != 0 or not output.exists():
        raise RuntimeError(f"rating failed for {root.name}: rc={process.returncode}")
    result = read_json(output)
    if result.get("task") != root.name:
        raise RuntimeError(f"rating task mismatch for {root.name}")
    print(f"[rating] {root.name}: {result['winner']}", flush=True)
    return result


def rate() -> None:
    roots = sorted(path for path in (HERE / "blind").iterdir() if path.is_dir())
    ratings = [rate_one(root) for root in roots]
    write_json(HERE / "blind-ratings.json", {"schema_version": 1, "ratings": ratings})


def unblind() -> None:
    metadata = read_json(HERE / "blind-metadata.json")
    ratings = read_json(HERE / "blind-ratings.json")["ratings"]
    counts: Counter[str] = Counter()
    pairs = []
    for rating in ratings:
        task = rating["task"]
        winner = rating["winner"]
        provider_winner = "tie" if winner == "tie" else metadata["mapping"][task][winner]
        counts[provider_winner] += 1
        pairs.append({
            "task": task,
            "blind_winner": winner,
            "provider_winner": provider_winner,
            "confidence": rating["confidence"],
            "reason": rating["reason"],
            "rating": rating,
        })
    result = {
        "schema_version": 1,
        "summary": {"sol_wins": counts["sol"], "opus_wins": counts["opus"], "ties": counts["tie"]},
        "pairs": pairs,
    }
    write_json(HERE / "blind-results.json", result)
    print(json.dumps(result["summary"], ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("prepare", "rate", "unblind"))
    args = parser.parse_args()
    {"prepare": prepare, "rate": rate, "unblind": unblind}[args.phase]()


if __name__ == "__main__":
    main()
