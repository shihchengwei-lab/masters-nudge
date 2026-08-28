from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import source_context
from masters_nudge import checkpoints, providers
from masters_nudge.contracts import ReviewRequest, SessionRef, ToolCompleted
from masters_nudge.core import ReviewCore
from masters_nudge.provider_contract import is_taste_finding
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


HERE = Path(__file__).resolve().parent
SOURCE_ROOT = Path(
    r"C:\Users\kk789\AppData\Local\Temp\masters-nudge-rerun-ab-20260829-routing-v2"
)
TASKS = [f"t{number:02d}" for number in range(1, 11)]
MODEL = "gpt-5.6-sol"


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


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def turn_state(task: str) -> tuple[Path, dict[str, Any]]:
    paths = sorted((SOURCE_ROOT / "tasks" / task / "runs" / "b" / "nudge-data").glob("*.turn.json"))
    if len(paths) != 1:
        raise RuntimeError(f"{task}: expected one turn state, found {len(paths)}")
    return paths[0], load_json(paths[0])


def first_apply_patch(task: str) -> tuple[Path, str]:
    sessions = SOURCE_ROOT / "tasks" / task / "runs" / "b" / "codex-home" / "sessions"
    traces = sorted(sessions.rglob("*.jsonl"))
    if len(traces) != 1:
        raise RuntimeError(f"{task}: expected one rollout, found {len(traces)}")
    pattern = re.compile(r"const patch = (\"(?:\\.|[^\"\\])*\")")
    for line in traces[0].read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        payload = item.get("payload") if isinstance(item, dict) else None
        if not isinstance(payload, dict) or payload.get("type") != "custom_tool_call":
            continue
        source = str(payload.get("input") or "")
        if "tools.apply_patch" not in source:
            continue
        match = pattern.search(source)
        if match:
            return traces[0], json.loads(match.group(1))
    raise RuntimeError(f"{task}: no recorded apply_patch call")


def prepare_input(task: str) -> dict[str, Any]:
    state_path, state = turn_state(task)
    records = state.get("evidence_records") if isinstance(state.get("evidence_records"), list) else []
    selected: list[dict[str, Any]] = []
    provenance: dict[str, Any]
    for record in records:
        if not isinstance(record, dict):
            continue
        selected.append(record)
        if record.get("category") == "change":
            break
    if selected and selected[-1].get("category") == "change":
        provenance = {
            "kind": "saved_turn_through_first_change",
            "state_path": str(state_path),
            "record_count": len(selected),
        }
    elif task == "t10":
        trace_path, patch = first_apply_patch(task)
        event = ToolCompleted(
            SessionRef("codex_cli", "reviewer-only-replay", cwd=str(SOURCE_ROOT / "tasks" / task / "runs" / "b" / "checkout")),
            "apply_patch",
            tool_input={"command": patch},
            tool_output="Done!",
            mutating=True,
        )
        selected.append(
            {
                "seq": len(selected) + 1,
                "category": "change",
                "scope": "",
                "content": checkpoints.render_evidence_record(event),
            }
        )
        provenance = {
            "kind": "reconstructed_first_apply_patch_from_rollout",
            "state_path": str(state_path),
            "rollout_path": str(trace_path),
            "record_count": len(selected),
        }
    else:
        raise RuntimeError(f"{task}: saved trajectory has no change checkpoint")

    packet = source_context.build_checkpoint_packet(
        task_anchor=str(state.get("task_anchor") or ""),
        task_sources=state.get("task_sources") or {},
        evidence_records=selected,
    )
    return {
        "task": task,
        "source_packet": packet,
        "source_packet_sha256": sha256_text(packet),
        "source_packet_chars": len(packet),
        "provenance": provenance,
    }


def replay_one(item: dict[str, Any]) -> dict[str, Any]:
    task = str(item["task"])
    data_dir = HERE / "runs" / task / "data"
    settings = RuntimeSettings(
        "openai",
        MODEL,
        90,
        90,
        RuntimePaths(REPO_ROOT, data_dir, data_dir / "error.log"),
        configuration_source="reviewer_only_replay",
    )
    calls: list[dict[str, Any]] = []

    def dispatch(provider: str, system_prompt: str, review_input: str, model: str, **kwargs: Any) -> dict[str, Any]:
        schema_path = Path(kwargs["schema_path"])
        started = time.perf_counter()
        result = providers.dispatch_call_result(
            provider,
            system_prompt,
            review_input,
            model,
            schema_path=schema_path,
            timeout_sec=int(kwargs["timeout_sec"]),
            ollama_url=str(kwargs["ollama_url"]),
            log_error=kwargs["log_error"],
        )
        calls.append(
            {
                "stage": "router" if schema_path.name == "route-schema.json" else "generator",
                "schema": schema_path.name,
                "system_prompt_sha256": sha256_text(system_prompt),
                "review_input_sha256": sha256_text(review_input),
                "timeout_seconds": int(kwargs["timeout_sec"]),
                "latency_ms": round((time.perf_counter() - started) * 1000),
                "result": result,
            }
        )
        return result

    started = time.perf_counter()
    outcome = ReviewCore(settings, dispatch=dispatch).review_once(
        ReviewRequest(
            schema_version=1,
            kind="strategy",
            reason="taste-review",
            session=SessionRef("codex_cli", f"reviewer-only-{task}", turn_id="replay", cwd=str(REPO_ROOT)),
            source_packet=str(item["source_packet"]),
            source_fingerprint=str(item["source_packet_sha256"]),
            trigger="first-change-replay",
        ),
        persist_reaction=False,
        timeout_sec=90,
    )
    finding = outcome.finding if outcome else ""
    return {
        "task": task,
        "status": outcome.status if outcome else "not_run",
        "effective_lens": outcome.effective_lens if outcome else "none",
        "finding": finding,
        "finding_character_count": len(finding),
        "contract_valid": bool(
            outcome
            and (
                outcome.status == "no_finding"
                or (outcome.status == "finding" and is_taste_finding(finding))
            )
        ),
        "wall_time_ms": round((time.perf_counter() - started) * 1000),
        "usage": outcome.usage if outcome else {},
        "calls": calls,
        "source_packet_sha256": item["source_packet_sha256"],
        "provenance": item["provenance"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--finalize-existing", action="store_true")
    args = parser.parse_args()
    if args.finalize_existing:
        path = HERE / "results.json"
        payload = load_json(path)
        results = payload["tasks"]
        for result in results:
            status = str(result.get("status") or "")
            finding = str(result.get("finding") or "")
            result["contract_valid"] = bool(
                status == "no_finding"
                or (status == "finding" and is_taste_finding(finding))
            )
        counts: dict[str, int] = {}
        for result in results:
            lens = str(result.get("effective_lens") or "none")
            counts[lens] = counts.get(lens, 0) + 1
        payload["counts"] = {
            "total": len(results),
            "finding": sum(result.get("status") == "finding" for result in results),
            "no_finding": sum(result.get("status") == "no_finding" for result in results),
            "error": sum(result.get("status") not in {"finding", "no_finding"} for result in results),
            "contract_valid": sum(bool(result.get("contract_valid")) for result in results),
            "lenses": counts,
        }
        atomic_json(path, payload)
        return 0
    if (HERE / "results.json").exists():
        raise SystemExit(
            "results.json already exists; preserve this replicate and create a new "
            "preregistered directory for another Provider run"
        )
    inputs = [prepare_input(task) for task in TASKS]
    atomic_json(HERE / "inputs.json", {"schema_version": 1, "items": inputs})

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(replay_one, item): item["task"] for item in inputs}
        for future in as_completed(futures):
            task = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {"task": task, "status": "harness_error", "error": str(exc)}
            results.append(result)
            print(f"[{task}] {result.get('status')} {result.get('effective_lens', 'none')} {result.get('finding', '')}", flush=True)

    results.sort(key=lambda item: item["task"])
    counts: dict[str, int] = {}
    for result in results:
        lens = str(result.get("effective_lens") or "none")
        counts[lens] = counts.get(lens, 0) + 1
    payload = {
        "schema_version": 1,
        "commit": "226f449",
        "model": MODEL,
        "tasks": results,
        "counts": {
            "total": len(results),
            "finding": sum(result.get("status") == "finding" for result in results),
            "no_finding": sum(result.get("status") == "no_finding" for result in results),
            "error": sum(result.get("status") not in {"finding", "no_finding"} for result in results),
            "contract_valid": sum(bool(result.get("contract_valid")) for result in results),
            "lenses": counts,
        },
    }
    atomic_json(HERE / "results.json", payload)
    return 0 if payload["counts"]["error"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
