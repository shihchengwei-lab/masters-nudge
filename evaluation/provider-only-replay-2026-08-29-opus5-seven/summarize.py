from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
SOURCE_WORK_ROOT = Path(
    r"C:\Users\kk789\AppData\Local\Temp\masters-nudge-formal-ab-20260829-positive-v5"
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def reported_cost(provider_outputs: list[dict[str, Any]]) -> float:
    total = 0.0
    for output in provider_outputs:
        raw = output.get("raw_output")
        if not isinstance(raw, str):
            continue
        try:
            total += float(json.loads(raw).get("total_cost_usd") or 0)
        except (ValueError, TypeError, json.JSONDecodeError):
            continue
    return total


def source_latency(task: str) -> int | None:
    path = SOURCE_WORK_ROOT / "tasks" / task / "runs" / "b" / "nudge-data" / "review-telemetry.jsonl"
    if not path.exists():
        return None
    entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    values = [entry.get("latency_ms") for entry in entries if isinstance(entry.get("latency_ms"), int)]
    return values[-1] if values else None


def main() -> None:
    inputs = {item["task"]: item for item in read_json(HERE / "inputs.json")["items"]}
    opus = {item["task"]: item for item in read_json(HERE / "results.json")["items"]}
    blind = read_json(HERE / "blind-results.json")
    mapping = read_json(HERE / "blind-metadata.json")["mapping"]
    ratings = {item["task"]: item for item in blind["pairs"]}
    dimensions = ("specific_preference", "load_bearing_reason", "actionability", "review_friction")
    dimension_totals = {provider: Counter() for provider in ("sol", "opus")}
    rows = []
    opus_latencies = []
    sol_latencies = []
    total_cost = 0.0
    lenses: Counter[str] = Counter()

    for task in inputs:
        source = inputs[task]
        replay = opus[task]
        pair = ratings[task]
        labels = mapping[task]
        for label, provider in labels.items():
            scores = pair["rating"][f"candidate_{label.lower()}"]
            for dimension in dimensions:
                dimension_totals[provider][dimension] += int(scores[dimension])
        sol_finding = str(source["sol_review"].get("reaction") or "")
        opus_finding = str(replay.get("finding") or "")
        opus_latency = int(replay["latency_ms"])
        sol_latency = source_latency(task)
        cost = reported_cost(replay.get("provider_outputs") or [])
        total_cost += cost
        opus_latencies.append(opus_latency)
        if sol_latency is not None:
            sol_latencies.append(sol_latency)
        lenses[str(replay.get("effective_lens") or "")] += 1
        rows.append({
            "task": task,
            "source_fingerprint": source["source_fingerprint"],
            "sol_finding": sol_finding,
            "opus_finding": opus_finding,
            "sol_characters": len(sol_finding),
            "opus_characters": len(opus_finding),
            "sol_latency_ms": sol_latency,
            "opus_latency_ms": opus_latency,
            "opus_reported_cost_usd": round(cost, 6),
            "lens": replay.get("effective_lens"),
            "status": replay.get("status"),
            "contract_deviations": replay.get("contract_deviations") or [],
            "blind_winner": pair["provider_winner"],
            "blind_confidence": pair["confidence"],
            "blind_reason": pair["reason"],
        })

    result = {
        "schema_version": 1,
        "counts": {
            "packets": len(rows),
            "opus_findings": sum(row["status"] == "finding" for row in rows),
            "opus_contract_clean": sum(not row["contract_deviations"] for row in rows),
            "opus_over_52": sum("over_52_characters" in row["contract_deviations"] for row in rows),
            **blind["summary"],
        },
        "lenses": dict(lenses),
        "latency_ms": {
            "sol_median": statistics.median(sol_latencies),
            "sol_max": max(sol_latencies),
            "opus_median": statistics.median(opus_latencies),
            "opus_max": max(opus_latencies),
        },
        "opus_cli_reported_cost_usd_total": round(total_cost, 6),
        "dimension_totals": {provider: dict(scores) for provider, scores in dimension_totals.items()},
        "confidence": dict(Counter(row["blind_confidence"] for row in rows)),
        "items": rows,
    }
    (HERE / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: result[key] for key in ("counts", "latency_ms", "opus_cli_reported_cost_usd_total", "dimension_totals")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
