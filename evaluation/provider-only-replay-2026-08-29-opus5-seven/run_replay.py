from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE_WORK_ROOT = Path(
    r"C:\Users\kk789\AppData\Local\Temp\masters-nudge-formal-ab-20260829-positive-v5"
)
FROZEN_PLUGIN = SOURCE_WORK_ROOT / "frozen-plugin"
sys.path.insert(0, str(FROZEN_PLUGIN))

import source_context
from masters_nudge import storage
from masters_nudge.contracts import ReviewRequest, SessionRef
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


TASKS = ("t01", "t02", "t03", "t04", "t05", "t07", "t10")
PROVIDER = "anthropic"
MODEL = "claude-opus-5"
TIMEOUT_SECONDS = 90


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def one_file(root: Path, pattern: str) -> Path:
    matches = list(root.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {pattern} under {root}, found {len(matches)}")
    return matches[0]


def log_entries(data_dir: Path) -> list[dict[str, Any]]:
    log_path = one_file(data_dir, "codex_cli--*.log")
    return [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def original_review_entry(data_dir: Path) -> dict[str, Any]:
    reviews = [
        entry
        for entry in log_entries(data_dir)
        if entry.get("kind") in {"review", "review_status"}
    ]
    if len(reviews) != 1:
        raise RuntimeError(f"Expected one original review under {data_dir}")
    return reviews[0]


def original_provider_outputs(data_dir: Path) -> list[dict[str, Any]]:
    return [entry for entry in log_entries(data_dir) if entry.get("kind") == "provider_output"]


def reconstruct_input(task: str) -> dict[str, Any]:
    data_dir = SOURCE_WORK_ROOT / "tasks" / task / "runs" / "b" / "nudge-data"
    turn = load_json(one_file(data_dir, "*.turn.json"))
    review = original_review_entry(data_dir)
    source_event_seq = int(review["source_event_seq"])
    original_fingerprint = str(review.get("source_fingerprint") or "")
    all_records = sorted(
        turn.get("evidence_records", []),
        key=lambda record: int(record.get("seq") or 0),
    )
    matches: list[tuple[list[dict[str, Any]], str]] = []
    for count in range(len(all_records) + 1):
        candidate_records = all_records[:count]
        candidate_packet = source_context.build_checkpoint_packet(
            task_anchor=str(turn.get("task_anchor") or ""),
            task_sources=turn.get("task_sources") or {},
            evidence_records=candidate_records,
        )
        candidate_fingerprint = hashlib.sha256(
            f"strategy:first-change\n{candidate_packet}".encode("utf-8", errors="replace")
        ).hexdigest()[:24]
        if candidate_fingerprint == original_fingerprint:
            matches.append((candidate_records, candidate_packet))
    if len(matches) != 1:
        raise RuntimeError(
            f"{task} packet reconstruction expected one fingerprint match, found {len(matches)}"
        )
    records, packet = matches[0]
    fingerprint = original_fingerprint
    return {
        "task": task,
        "source_event_seq": source_event_seq,
        "evidence_record_count": len(records),
        "source_fingerprint": fingerprint,
        "source_packet_sha256": hashlib.sha256(packet.encode("utf-8")).hexdigest(),
        "source_packet": packet,
        "sol_review": review,
        "sol_provider_outputs": original_provider_outputs(data_dir),
    }


def freeze_inputs() -> list[dict[str, Any]]:
    inputs = [reconstruct_input(task) for task in TASKS]
    payload = {
        "schema_version": 1,
        "frozen_plugin": str(FROZEN_PLUGIN),
        "items": inputs,
    }
    path = HERE / "inputs.json"
    if path.exists() and load_json(path) != payload:
        raise RuntimeError("Reconstructed inputs differ from frozen inputs.json")
    if not path.exists():
        atomic_json(path, payload)
    return inputs


def replay_one(item: dict[str, Any]) -> dict[str, Any]:
    task = str(item["task"])
    result_path = HERE / "items" / f"{task}.json"
    if result_path.exists():
        return load_json(result_path)
    data_dir = HERE / "data" / task
    session = SessionRef(
        "codex_cli",
        f"opus5-provider-replay-{task}",
        turn_id=f"opus5-provider-replay-{task}",
        cwd=str(FROZEN_PLUGIN),
        repo_root=str(FROZEN_PLUGIN),
    )
    settings = RuntimeSettings(
        PROVIDER,
        MODEL,
        TIMEOUT_SECONDS,
        TIMEOUT_SECONDS,
        RuntimePaths(FROZEN_PLUGIN, data_dir, data_dir / "error.log"),
    )
    outcome = ReviewCore(settings).review_once(
        ReviewRequest(
            1,
            "strategy",
            "taste-review",
            session,
            str(item["source_packet"]),
            str(item["source_fingerprint"]),
            int(item["source_event_seq"]),
            "first-change",
        ),
        persist_reaction=True,
        timeout_sec=TIMEOUT_SECONDS,
    )
    if outcome is None:
        raise RuntimeError(f"{task} review attempt was not claimed")
    provider_outputs = [
        entry
        for entry in storage.read_audit_entries(data_dir, session)
        if entry.get("kind") == "provider_output"
    ]
    result = {
        "task": task,
        "source_fingerprint": item["source_fingerprint"],
        "status": outcome.status,
        "effective_lens": outcome.effective_lens,
        "finding": outcome.finding,
        "contract_deviations": list(outcome.contract_deviations),
        "error_stage": outcome.error_stage,
        "error_kind": outcome.error_kind,
        "latency_ms": outcome.latency_ms,
        "usage": outcome.usage,
        "provider_outputs": provider_outputs,
    }
    atomic_json(result_path, result)
    return result


def run_replay(inputs: list[dict[str, Any]]) -> None:
    results = []
    for index, item in enumerate(inputs, start=1):
        print(f"[replay] starting {item['task']} ({index}/{len(inputs)})", flush=True)
        result = replay_one(item)
        results.append(result)
        print(
            f"[replay] {item['task']}: {result['status']} lens={result['effective_lens']} "
            f"latency_ms={result['latency_ms']} deviations={result['contract_deviations']}",
            flush=True,
        )
    atomic_json(HERE / "results.json", {"schema_version": 1, "items": results})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("freeze", "run"))
    args = parser.parse_args()
    os.environ["BUDDY_PERSONA"] = "automatic"
    inputs = freeze_inputs()
    print(f"[inputs] verified {len(inputs)} original fingerprints", flush=True)
    if args.phase == "run":
        run_replay(inputs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
