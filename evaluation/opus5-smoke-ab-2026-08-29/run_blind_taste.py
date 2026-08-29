from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
FORMAL = REPO_ROOT / "evaluation" / "formal-ab-2026-08-29-positive-examples-v5"
WORK_ROOT = Path(r"C:\Users\kk789\AppData\Local\Temp\masters-nudge-opus5-smoke-ab-20260829")
SCHEMA = FORMAL / "taste-rating-schema.json"
RUBRIC = FORMAL / "taste-rubric.json"


def load_helpers():
    spec = importlib.util.spec_from_file_location("taste_helpers", FORMAL / "run_taste_blind.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_packets() -> list[tuple[Path, dict[str, str]]]:
    helpers = load_helpers()
    task = read_json(WORK_ROOT / "tasks" / "t01" / "task.json")
    mappings = ({"X": "a", "Y": "b"}, {"X": "b", "Y": "a"})
    prepared = []
    for index, mapping in enumerate(mappings, start=1):
        root = HERE / "taste-blind" / f"pass{index}"
        packet_path = root / "packet.json"
        if not packet_path.exists():
            packet = {
                "task_key": f"t01-pass{index}",
                "problem_statement": task["problem_statement"],
                "instructions": "Compare only engineering taste. Correctness and test activity are intentionally absent and must not be inferred.",
                "candidates": {},
            }
            for label, arm in mapping.items():
                run_root = WORK_ROOT / "tasks" / "t01" / "runs" / arm
                packet["candidates"][label] = {
                    "visible_trajectory": helpers.agent_messages(run_root / "codex-events.jsonl"),
                    "product_patch": helpers.redact(
                        (run_root / "product.patch").read_text(encoding="utf-8", errors="replace")
                    ),
                }
            write_json(packet_path, packet)
        prepared.append((root, mapping))
    metadata = {
        "rubric_sha256": hashlib.sha256(RUBRIC.read_bytes()).hexdigest(),
        "passes": [mapping for _, mapping in prepared],
        "treatment_cues_removed": True,
        "correctness_and_test_activity_excluded": True,
    }
    write_json(HERE / "taste-blind-metadata.json", metadata)
    return prepared


def rate(root: Path) -> dict[str, Any]:
    output = root / "rating.json"
    if output.exists():
        return read_json(output)
    events = root / "rater-events.jsonl"
    prompt = (
        "You are an independent blinded evaluator. Evaluate X and Y exactly under the frozen "
        "rubric below. Do not use tools, infer treatment, or score correctness/test activity. "
        "Copy packet.task_key exactly into task_key. Return only schema-compliant JSON.\n\n"
        "FROZEN RUBRIC:\n" + RUBRIC.read_text(encoding="utf-8")
        + "\nBLINDED PACKET:\n" + (root / "packet.json").read_text(encoding="utf-8")
    )
    command = [
        "codex", "exec", "--ephemeral", "--ignore-user-config", "--ignore-rules",
        "--skip-git-repo-check", "--sandbox", "read-only", "--json",
        "--model", "gpt-5.6-sol", "-c", 'model_reasoning_effort="medium"',
        "--output-schema", str(SCHEMA), "--output-last-message", str(output),
        "-C", str(root), "-",
    ]
    started = time.monotonic()
    print(f"RATING_START {root.name}", flush=True)
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
            print(f"RATING_HEARTBEAT {root.name} elapsed={int(time.monotonic()-started)}s", flush=True)
            time.sleep(15)
    if process.returncode != 0 or not output.exists():
        raise RuntimeError(f"rating failed for {root.name}: rc={process.returncode}")
    result = read_json(output)
    print(f"RATING_DONE {root.name} winner={result['winner']}", flush=True)
    return result


def treatment_winner(rating: dict[str, Any], mapping: dict[str, str]) -> str:
    winner = rating["winner"]
    return "tie" if winner == "tie" else mapping[winner].upper()


def main() -> None:
    prepared = prepare_packets()
    passes = []
    for root, mapping in prepared:
        rating = rate(root)
        passes.append({
            "pass": root.name,
            "mapping": mapping,
            "blind_winner": rating["winner"],
            "treatment_winner": treatment_winner(rating, mapping),
            "rating": rating,
        })
    winners = [item["treatment_winner"] for item in passes]
    consensus = winners[0] if winners[0] == winners[1] else "inconclusive"
    result = {"schema_version": 1, "consensus": consensus, "passes": passes}
    write_json(HERE / "taste-result.json", result)
    print(json.dumps({"consensus": consensus, "passes": winners}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
