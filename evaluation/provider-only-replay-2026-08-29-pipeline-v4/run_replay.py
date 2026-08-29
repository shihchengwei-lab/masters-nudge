from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(REPO_ROOT))

import source_context
from masters_nudge import storage
from masters_nudge.contracts import ReviewRequest, SessionRef
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


SOURCE_WORK_ROOT = Path(
    r"C:\Users\kk789\AppData\Local\Temp\masters-nudge-fresh-ab-20260829-taste-v3"
)
TASKS = ("t03", "t07", "t08", "t10")
MODEL = "gpt-5.6-sol"
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


def original_review_entry(data_dir: Path) -> dict[str, Any]:
    log_path = one_file(data_dir, "codex_cli--*.log")
    entries = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    reviews = [
        entry
        for entry in entries
        if entry.get("kind") in {"review", "review_status"}
    ]
    if len(reviews) != 1:
        raise RuntimeError(f"Expected one original review entry in {log_path}")
    return reviews[0]


def reconstruct_input(task: str) -> dict[str, Any]:
    data_dir = SOURCE_WORK_ROOT / "tasks" / task / "runs" / "b" / "nudge-data"
    turn = load_json(one_file(data_dir, "*.turn.json"))
    progress = load_json(one_file(data_dir, "*.progress.json"))
    review = original_review_entry(data_dir)
    source_event_seq = int(review["source_event_seq"])
    evidence_count = sum(
        1
        for event in progress.get("recent", [])
        if int(event.get("event_seq") or 0) <= source_event_seq
        and str(event.get("evidence_category") or "")
    )
    records = sorted(
        (
            record
            for record in turn.get("evidence_records", [])
            if int(record.get("seq") or 0) <= evidence_count
        ),
        key=lambda record: int(record.get("seq") or 0),
    )
    packet = source_context.build_checkpoint_packet(
        task_anchor=str(turn.get("task_anchor") or ""),
        task_sources=turn.get("task_sources") or {},
        evidence_records=records,
    )
    fingerprint = hashlib.sha256(
        f"strategy:first-change\n{packet}".encode("utf-8", errors="replace")
    ).hexdigest()[:24]
    original_fingerprint = str(review.get("source_fingerprint") or "")
    if fingerprint != original_fingerprint:
        raise RuntimeError(
            f"{task} packet mismatch: reconstructed={fingerprint} "
            f"original={original_fingerprint}"
        )
    return {
        "task": task,
        "source_event_seq": source_event_seq,
        "evidence_record_count": len(records),
        "source_fingerprint": fingerprint,
        "source_packet": packet,
    }


def freeze_inputs() -> list[dict[str, Any]]:
    inputs = [reconstruct_input(task) for task in TASKS]
    path = HERE / "inputs.json"
    payload = {"schema_version": 1, "items": inputs}
    if path.exists():
        if load_json(path) != payload:
            raise RuntimeError("Reconstructed inputs differ from frozen inputs.json")
    else:
        atomic_json(path, payload)
    return inputs


def replay_one(item: dict[str, Any]) -> dict[str, Any]:
    task = str(item["task"])
    result_path = HERE / "items" / f"{task}.json"
    if result_path.exists():
        cached = load_json(result_path)
        changed = False
        for output in cached.get("provider_outputs", []):
            if (
                output.get("provider_stage") == "router"
                and output.get("contract_deviations")
            ):
                output["recorded_contract_deviations"] = list(
                    output["contract_deviations"]
                )
                output["contract_deviations"] = []
                output["normalization_note"] = (
                    "Router decisions do not use the Nudge output contract; "
                    "normalized from preserved raw output without a provider rerun."
                )
                changed = True
        if changed:
            atomic_json(result_path, cached)
        return cached
    data_dir = HERE / "data" / task
    session = SessionRef(
        "codex_cli",
        f"provider-replay-{task}",
        turn_id=f"provider-replay-{task}",
        cwd=str(REPO_ROOT),
        repo_root=str(REPO_ROOT),
    )
    settings = RuntimeSettings(
        "openai",
        MODEL,
        TIMEOUT_SECONDS,
        TIMEOUT_SECONDS,
        RuntimePaths(REPO_ROOT, data_dir, data_dir / "error.log"),
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


def main() -> int:
    os.environ["BUDDY_PERSONA"] = "automatic"
    inputs = freeze_inputs()
    print(f"[inputs] verified {len(inputs)} original fingerprints", flush=True)
    results = []
    for item in inputs:
        print(f"[replay] starting {item['task']}", flush=True)
        result = replay_one(item)
        results.append(result)
        print(
            f"[replay] {item['task']}: {result['status']} "
            f"lens={result['effective_lens']} deviations={result['contract_deviations']}",
            flush=True,
        )
    atomic_json(
        HERE / "results.json",
        {"schema_version": 1, "items": results},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
