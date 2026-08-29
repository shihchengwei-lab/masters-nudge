from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SOURCE_REPLAY = HERE.parent / "provider-only-replay-2026-08-29-opus5-seven"
sys.path.insert(0, str(REPO_ROOT))

from masters_nudge import storage
from masters_nudge.contracts import ReviewRequest, SessionRef
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


PROVIDER = "anthropic"
MODEL = "claude-opus-5"
TIMEOUT_SECONDS = 90
EXPECTED_TASKS = ("t01", "t02", "t03", "t04", "t05", "t07", "t10")


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prompt_hashes() -> dict[str, str]:
    paths = (
        Path("buddy-prompt.txt"),
        Path("masters_nudge/prompting.py"),
        *(Path("personas") / f"{lens}.txt" for lens in (
            "jeff", "linus", "fowler", "beck", "lamport", "carmack"
        )),
        Path("reaction-schema.json"),
        Path("route-schema.json"),
    )
    return {path.as_posix(): sha256(REPO_ROOT / path) for path in paths}


def freeze_inputs() -> list[dict[str, Any]]:
    source = load_json(SOURCE_REPLAY / "inputs.json")
    items = list(source["items"])
    tasks = tuple(str(item["task"]) for item in items)
    if tasks != EXPECTED_TASKS:
        raise RuntimeError(f"Unexpected packet set: {tasks}")
    frozen = {
        "schema_version": 1,
        "source": str(SOURCE_REPLAY / "inputs.json"),
        "items": items,
    }
    path = HERE / "inputs.json"
    if path.exists() and load_json(path) != frozen:
        raise RuntimeError("Frozen inputs differ from inputs.json")
    if not path.exists():
        atomic_json(path, frozen)
    return items


def freeze_contract() -> None:
    contract = {
        "schema_version": 1,
        "status": "frozen_before_calls",
        "purpose": (
            "Replay the same seven actual first-change packets after the minimal "
            "decision-delta prompt change."
        ),
        "source_replay": str(SOURCE_REPLAY),
        "provider": PROVIDER,
        "model": MODEL,
        "timeout_seconds": TIMEOUT_SECONDS,
        "prompt_hashes": prompt_hashes(),
        "rules": [
            "Use the preserved source packets without running a main coding model.",
            "Use the current repository router, persona context, prompt, and contracts.",
            "Do not overwrite or rerun a completed item.",
            "Evaluate whether each finding would change the main agent's next decision.",
        ],
    }
    path = HERE / "contract.json"
    if path.exists() and load_json(path) != contract:
        raise RuntimeError("Current prompt surface differs from frozen contract.json")
    if not path.exists():
        atomic_json(path, contract)


def replay_one(item: dict[str, Any]) -> dict[str, Any]:
    task = str(item["task"])
    result_path = HERE / "items" / f"{task}.json"
    if result_path.exists():
        return load_json(result_path)

    data_dir = HERE / "data" / task
    session = SessionRef(
        "codex_cli",
        f"decision-delta-v6-{task}",
        turn_id=f"decision-delta-v6-{task}",
        cwd=str(REPO_ROOT),
        repo_root=str(REPO_ROOT),
    )
    settings = RuntimeSettings(
        PROVIDER,
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


def run_replay(items: list[dict[str, Any]]) -> None:
    results = []
    for index, item in enumerate(items, start=1):
        print(f"[replay] starting {item['task']} ({index}/{len(items)})", flush=True)
        result = replay_one(item)
        results.append(result)
        print(
            f"[replay] {item['task']}: {result['status']} "
            f"lens={result['effective_lens']} latency_ms={result['latency_ms']} "
            f"deviations={result['contract_deviations']}",
            flush=True,
        )
    atomic_json(HERE / "results.json", {"schema_version": 1, "items": results})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("freeze", "run"))
    args = parser.parse_args()
    os.environ["BUDDY_PERSONA"] = "automatic"
    items = freeze_inputs()
    freeze_contract()
    print(f"[inputs] verified {len(items)} preserved packets", flush=True)
    if args.phase == "run":
        run_replay(items)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
