#!/usr/bin/env python3
"""Read-only projection of structured Shader research state.

The workspace JSON files remain authoritative.  The returned state is a small,
rebuildable view used only to decide whether a reviewer call has new evidence.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CORE_RESEARCH_SOURCES = (
    "benchmark/architecture-contract.json",
    "benchmark/architecture-experiments.json",
    "benchmark/architecture-result.json",
)
CANDIDATE_RESULTS_SOURCE = "benchmark/candidate-results.json"
LIVE_EVIDENCE_ROOT = "Evidence/LongTail"
ACTIVE_STATUSES = {
    "active",
    "candidate",
    "implemented",
    "in-progress",
    "measuring",
    "pending",
    "planned",
    "running",
    "visual-passed",
}
EXPLICIT_FAILURE_STATUSES = {
    "exhausted",
    "failed",
    "performance-rejected",
    "rejected",
    "visual-rejected",
}

DECISION_MATERIAL_FIELDS = (
    "parent_frontier_id",
    "falsifiable_statement",
    "expected_removed_work",
    "actual_removed_work",
    "implementation_delta",
    "evidence_refs",
    "decision",
    "source_fingerprint",
    "trajectory",
    "nudge_ids",
)

DIMENSION_ROUTES = {
    "execution": ("carmack", "executed-work-elimination"),
    "visibility": ("akenine_moller", "visibility-work-elimination"),
    "procedural": ("quilez", "procedural-representation"),
    "material": ("karis", "render-contract-semantics"),
    "temporal": ("lottes", "spatiotemporal-stability"),
    "platform": ("tatarchuk", "platform-generality"),
}

DIMENSION_PATTERNS = {
    "platform": re.compile(
        r"platform|cross.hardware|driver|compiler version|vulkan|metal|directx|mobile|"
        r"asset store|marketplace|跨硬體|跨平台|驅動|行動裝置|上架",
        re.IGNORECASE,
    ),
    "material": re.compile(
        r"urp|material|brdf|render pass|cross.pass|variant|lighting|roughness|"
        r"normal space|\bforward\b|\bdepthonly\b|\bshadowcaster\b|alpha clip|"
        r"材質|光照|渲染通道|著色器變體|渲染契約|遮罩語意",
        re.IGNORECASE,
    ),
    "procedural": re.compile(
        r"sdf|raymarch|noise|distance field|procedural|rsqrt|reciprocal|gradient|"
        r"程序化|距離場|光線步進|雜訊|倒數平方根|梯度",
        re.IGNORECASE,
    ),
    "temporal": re.compile(
        r"temporal|motion|history|precision|half|flicker|shimmer|banding|aliasing|"
        r"時間|移動|歷史|精度|半精度|閃爍|色帶|鋸齒",
        re.IGNORECASE,
    ),
    "visibility": re.compile(
        r"triangle|geometry|overdraw|occlusion|culling|visibility|coverage|depth complexity|"
        r"幾何|過度繪製|遮擋|剔除|可見性|覆蓋|深度複雜度",
        re.IGNORECASE,
    ),
    "execution": re.compile(
        r"gpu|compiler|benchmark|hot path|bandwidth|register|occupancy|alu|texture|"
        r"executed work|removed work|效能|編譯器|基準測試|熱路徑|頻寬|暫存器|工作消除",
        re.IGNORECASE,
    ),
}


@dataclass(frozen=True)
class ResearchSnapshot:
    fingerprint: str
    projection: str
    state: dict[str, Any]
    sources: tuple[str, ...]


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _text(value: Any) -> str:
    return str(value or "").strip()


def _string_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [text for item in value if (text := _text(item))]
    text = _text(value)
    return [text] if text else []


def _evidence_refs(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return _string_list(value)
    refs: list[str] = []
    for item in value:
        if isinstance(item, dict):
            text = _text(item.get("path") or item.get("ref"))
        else:
            text = _text(item)
        if text:
            refs.append(text)
    return refs


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _candidate_state(experiments: dict[str, Any]) -> list[dict[str, Any]]:
    raw = experiments.get("experiments")
    if not isinstance(raw, list):
        return []
    candidates: list[dict[str, Any]] = []
    for value in raw:
        if not isinstance(value, dict):
            continue
        candidate_id = str(value.get("id") or value.get("candidate_id") or "").strip()
        if not candidate_id:
            continue
        candidates.append({
            "id": candidate_id,
            "family": _text(
                value.get("family")
                or value.get("mechanism_family")
                or value.get("mechanism_id")
            ),
            "status": _text(value.get("status") or "unknown").lower(),
            "bottleneck": _text(value.get("bottleneck_classification")),
            "parent_frontier_id": _text(
                value.get("parent_frontier_id")
                or value.get("parent")
                or value.get("parent_id")
            ),
            "hypothesis_family": _text(value.get("hypothesis_family")),
            "falsifiable_statement": _text(
                value.get("falsifiable_statement") or value.get("hypothesis")
            ),
            "expected_removed_work": _text(value.get("expected_removed_work")),
            "actual_removed_work": _text(
                value.get("actual_removed_work") or value.get("observed_removed_work")
            ),
            "implementation_delta": _text(
                value.get("implementation_delta")
                or value.get("change_summary")
                or value.get("single_change")
                or value.get("change")
            ),
            "evidence_refs": _evidence_refs(
                value.get("evidence_refs")
                or value.get("evidence_files")
                or value.get("evidence_ref")
            ),
            "decision": _text(value.get("decision")),
            "unresolved_question": _text(
                value.get("unresolved_question") or value.get("unresolved_contrast")
            ),
            "evidence_dimensions": [
                item.lower() for item in _string_list(
                    value.get("evidence_dimensions") or value.get("unresolved_dimensions")
                )
            ],
            "metrics": _mapping(
                value.get("metrics")
                or value.get("benchmark")
                or value.get("measurement")
                or value.get("performance")
            ),
            "quality": _mapping(value.get("quality") or value.get("visual")),
            "contract_fingerprint": _text(value.get("contract_fingerprint")),
            "source_fingerprint": _text(
                value.get("source_fingerprint") or value.get("source_sha256")
            ),
            "trajectory": _text(value.get("trajectory") or value.get("stage")),
            "nudge_ids": _string_list(value.get("nudge_ids")),
        })
    return candidates


def _result_evidence_refs(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return _evidence_refs(value)
    refs: list[str] = []
    for item in value.values():
        if isinstance(item, dict):
            text = _text(item.get("path") or item.get("ref"))
        else:
            text = _text(item)
        if text:
            refs.append(text)
    return refs


def _unique_refs(*values: Any) -> list[str]:
    refs: list[str] = []
    for value in values:
        for ref in _evidence_refs(value):
            if ref not in refs:
                refs.append(ref)
    return refs


def _valid_candidate_cell(value: dict[str, Any], status: str) -> bool:
    explicit = value.get("valid_candidate_cell")
    if isinstance(explicit, bool):
        return explicit
    actual_evidence = _mapping(value.get("actual_evidence"))
    repetitions = actual_evidence.get("valid_repetitions")
    samples = actual_evidence.get("raw_gpu_samples")
    return (
        status == "resolved"
        and isinstance(repetitions, (int, float))
        and repetitions > 0
        and isinstance(samples, (int, float))
        and samples > 0
    )


def _candidate_result_state(candidate_results: dict[str, Any]) -> list[dict[str, Any]]:
    raw = candidate_results.get("results")
    if not isinstance(raw, list):
        return []
    results: list[dict[str, Any]] = []
    for value in raw:
        if not isinstance(value, dict):
            continue
        candidate_id = _text(
            value.get("candidate") or value.get("candidate_id") or value.get("id")
        )
        if not candidate_id:
            continue
        summary = _mapping(value.get("summary"))
        status = _text(
            value.get("status")
            or (
                "measured"
                if "valid_candidate_cell" in value or "actual_evidence" in value
                else "unknown"
            )
        ).lower()
        metrics = dict(summary or _mapping(value.get("gpu_metric_ms")))
        if "improvement_percent" in value:
            metrics["improvement_percent"] = value["improvement_percent"]
        quality = dict(_mapping(value.get("visual")))
        quality.update({
            key: summary[key]
            for key in ("visual_ssim", "max_abs_channel_error")
            if key in summary
        })
        for key in (
            "all_research_targets_pass",
            "contract_checks",
            "repeat_hashes_match",
        ):
            if key in value:
                quality[key] = value[key]
        if "checks" in value and "contract_checks" not in quality:
            quality["contract_checks"] = value["checks"]
        if "actual_evidence" in value:
            quality["actual_evidence"] = value["actual_evidence"]
        quality["valid_candidate_cell"] = (
            candidate_id.lower() != "baselinev0"
            and _valid_candidate_cell(value, status)
        )
        evidence_refs = _unique_refs(
            _result_evidence_refs(value.get("evidence_files")),
            value.get("evidence_ref"),
            value.get("raw_measurement_refs"),
        )
        results.append(
            {
                "id": candidate_id,
                "family": _text(value.get("family") or value.get("mechanism_family")),
                "status": status,
                "parent_frontier_id": _text(value.get("parent_frontier_id")),
                "metrics": metrics,
                "quality": quality,
                "evidence_refs": evidence_refs,
                "source_fingerprint": _text(
                    value.get("source_fingerprint") or value.get("source_sha256")
                ),
                "trajectory": _text(value.get("trajectory") or value.get("stage")),
                "decision": _text(value.get("decision")),
            }
        )
    return results


def _payload_sha256(payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _live_evidence_results(root: Path) -> tuple[dict[str, Any], list[str]]:
    evidence_root = root / Path(LIVE_EVIDENCE_ROOT)
    if not evidence_root.is_dir():
        return {"results": []}, []
    results: list[dict[str, Any]] = []
    sources: list[str] = []
    for candidate_dir in sorted(
        (path for path in evidence_root.iterdir() if path.is_dir()),
        key=lambda path: path.name,
    ):
        result_path = candidate_dir / "result.json"
        failure_path = candidate_dir / "failure.json"
        source_path = result_path if result_path.is_file() else failure_path
        if not source_path.is_file():
            continue
        payload = _read_json(source_path)
        if payload is None:
            continue
        candidate_id = _text(payload.get("candidate") or candidate_dir.name)
        if not candidate_id:
            continue
        relative = source_path.relative_to(root).as_posix()
        if source_path == result_path:
            raw_evidence = _mapping(payload.get("raw_evidence"))
            evidence_files: dict[str, Any] = {"result": relative}
            evidence_files.update(
                {
                    key: value
                    for key, value in raw_evidence.items()
                    if isinstance(value, dict) and _text(value.get("path") or value.get("ref"))
                }
            )
            input_manifest = _mapping(raw_evidence.get("input_manifest"))
            normalized = dict(payload)
            normalized.update(
                {
                    "candidate": candidate_id,
                    "status": _text(payload.get("status") or "measured").lower(),
                    "evidence_files": evidence_files,
                    "source_sha256": _text(input_manifest.get("sha256"))
                    or _payload_sha256(payload),
                }
            )
        else:
            normalized = {
                "candidate": candidate_id,
                "status": "failed",
                "valid_candidate_cell": False,
                "summary": {"error": _text(payload.get("error") or "candidate failed")},
                "evidence_files": {"failure": relative},
                "source_sha256": _payload_sha256(payload),
            }
        results.append(normalized)
        sources.append(relative)
    return {"results": results}, sources


def _combine_candidate_results(
    *payloads: dict[str, Any],
) -> dict[str, Any]:
    by_id: dict[str, dict[str, Any]] = {}
    ordered_ids: list[str] = []
    for payload in payloads:
        raw = payload.get("results")
        if not isinstance(raw, list):
            continue
        for value in raw:
            if not isinstance(value, dict):
                continue
            candidate_id = _text(
                value.get("candidate") or value.get("candidate_id") or value.get("id")
            )
            if not candidate_id:
                continue
            if candidate_id in ordered_ids:
                ordered_ids.remove(candidate_id)
            ordered_ids.append(candidate_id)
            by_id[candidate_id] = {**by_id.get(candidate_id, {}), **value}
    return {"results": [by_id[candidate_id] for candidate_id in ordered_ids]}


def _merge_candidate_results(
    candidates: list[dict[str, Any]], candidate_results: dict[str, Any]
) -> list[dict[str, Any]]:
    by_id = {_text(item.get("id")): item for item in candidates if item.get("id")}
    result_ids: list[str] = []
    for result in _candidate_result_state(candidate_results):
        if result["id"] in result_ids:
            result_ids.remove(result["id"])
        result_ids.append(result["id"])
        candidate = by_id.get(result["id"])
        if candidate is None:
            candidate = {
                "id": result["id"],
                "family": "",
                "status": "unknown",
                "bottleneck": "",
                "parent_frontier_id": "",
                "hypothesis_family": "",
                "falsifiable_statement": "",
                "expected_removed_work": "",
                "actual_removed_work": "",
                "implementation_delta": "",
                "evidence_refs": [],
                "decision": "",
                "unresolved_question": "",
                "evidence_dimensions": [],
                "metrics": {},
                "quality": {},
                "contract_fingerprint": "",
                "source_fingerprint": "",
                "trajectory": "",
                "nudge_ids": [],
            }
            candidates.append(candidate)
            by_id[result["id"]] = candidate
        candidate.update(
            {
                key: value
                for key, value in result.items()
                if key != "id" and value not in ("", [], {})
            }
        )
    if result_ids:
        result_id_set = set(result_ids)
        candidates = [
            item for item in candidates if _text(item.get("id")) not in result_id_set
        ] + [by_id[candidate_id] for candidate_id in result_ids]
    return candidates


def _frontier_ids(result: dict[str, Any]) -> list[str]:
    raw = result.get("current_frontier")
    if raw is None:
        raw = result.get("frontier")
    if isinstance(raw, dict):
        raw = raw.get("pareto_frontier") or raw.get("candidates") or []
    if not isinstance(raw, list):
        return []
    values: list[str] = []
    for item in raw:
        if isinstance(item, dict):
            value = item.get("candidate") or item.get("id") or item.get("candidate_id")
        else:
            value = item
        text = str(value or "").strip()
        if text:
            values.append(text)
    return values


def _first_present(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload:
            return payload.get(key)
    return None


def _integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def _search_state(
    contract: dict[str, Any],
    experiments: dict[str, Any],
    result: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    search_contract = _mapping(contract.get("search_contract"))
    budget = _integer(_first_present(experiments, "candidate_budget"))
    if budget is None:
        budget = _integer(_first_present(search_contract, "candidate_budget"))
    evaluated = _integer(_first_present(result, "evaluated_candidates"))
    if evaluated is None:
        evaluated = len(candidates)

    family_distribution: dict[str, int] = {}
    for candidate in candidates:
        family = _text(candidate.get("family"))
        if family:
            family_distribution[family] = family_distribution.get(family, 0) + 1

    consecutive_failures = 0
    for candidate in reversed(candidates):
        status = _text(candidate.get("status")).lower()
        if status in EXPLICIT_FAILURE_STATUSES or status.endswith("-rejected"):
            consecutive_failures += 1
            continue
        break

    inventory = _string_list(
        search_contract.get("prefrozen_mechanism_inventory")
        or experiments.get("prefrozen_mechanism_inventory")
    )
    explored_families = set(family_distribution)
    unexplored_mechanisms = [
        mechanism for mechanism in inventory if mechanism not in explored_families
    ]
    return {
        "budget": budget,
        "candidate_id_range": _text(
            _first_present(experiments, "candidate_id_range")
            or _first_present(search_contract, "candidate_id_range")
        ),
        "evaluated": evaluated,
        "remaining": max(0, budget - evaluated) if budget is not None else None,
        "family_distribution": family_distribution,
        "consecutive_failures": consecutive_failures,
        "prefrozen_mechanism_inventory": inventory,
        "unexplored_mechanisms": unexplored_mechanisms,
    }


def _normalized_state(
    contract: dict[str, Any],
    experiments: dict[str, Any],
    result: dict[str, Any],
    candidate_results: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_results = _candidate_result_state(candidate_results or {})
    candidates = _merge_candidate_results(
        _candidate_state(experiments), candidate_results or {}
    )
    contract_fingerprint = _text(
        contract.get("contract_fingerprint")
        or contract.get("fingerprint")
        or contract.get("product_contract_sha256")
    )
    if contract_fingerprint:
        for candidate in candidates:
            if not candidate["contract_fingerprint"]:
                candidate["contract_fingerprint"] = contract_fingerprint
    declared_contract_status = str(contract.get("status") or "unknown")
    result_status = str(result.get("status") or "unknown")
    effective_contract_status = declared_contract_status
    if (
        declared_contract_status == "baseline-pending"
        and result_status not in {"unknown", "baseline-pending"}
    ):
        effective_contract_status = result_status
    return {
        "contract": {
            "status": effective_contract_status,
            "declared_status": declared_contract_status,
            "claims_permitted": contract.get("claims_permitted"),
            "research_question": str(contract.get("research_question") or ""),
            "fingerprint": contract_fingerprint,
        },
        "result": {
            "status": result_status,
            "frontier": _frontier_ids(result),
            "resolved": _first_present(
                result, "resolved_architecture_trials", "resolved_candidate_cells"
            ),
            "unresolved": _first_present(
                result, "unresolved_architecture_trials", "unresolved_candidate_cells"
            ),
            "saturation_rule_met": _first_present(
                result, "saturation_rule_met", "saturation_reached"
            ),
            "claims_permitted": result.get("claims_permitted"),
            "metrics": _mapping(
                result.get("metrics") or result.get("benchmark") or result.get("measurement")
            ),
        },
        "evidence_progress": {
            "observed": len(normalized_results),
            "valid": sum(
                item.get("quality", {}).get("valid_candidate_cell") is True
                for item in normalized_results
            ),
            "failed": sum(item.get("status") == "failed" for item in normalized_results),
        },
        "search": _search_state(contract, experiments, result, candidates),
        "candidates": candidates,
    }


def _render_projection(state: dict[str, Any]) -> str:
    contract = state["contract"]
    result = state["result"]
    candidates = state["candidates"]
    frontier = ", ".join(result["frontier"]) or "none"
    lines = [
        "[authoritative research projection]",
        f"contract: {contract['status']}; claims_permitted={str(contract['claims_permitted']).lower()}",
        f"result: {result['status']}; frontier: {frontier}",
        f"coverage: resolved={result['resolved']}; unresolved={result['unresolved']}; saturation={result['saturation_rule_met']}",
    ]
    search = state.get("search", {})
    if search.get("budget") is not None:
        lines.append(
            "search budget: "
            f"evaluated={search.get('evaluated')}/{search['budget']}; "
            f"remaining={search.get('remaining')}"
        )
    family_distribution = search.get("family_distribution", {})
    if family_distribution:
        lines.append(
            "candidate families: "
            + "; ".join(
                f"{family}={count}"
                for family, count in family_distribution.items()
            )
        )
    if candidates:
        lines.append(
            "consecutive explicit failures: "
            f"{search.get('consecutive_failures', 0)}"
        )
    inventory = search.get("prefrozen_mechanism_inventory", [])
    if inventory:
        unexplored = search.get("unexplored_mechanisms", [])
        lines.append(
            "unexplored prefrozen mechanisms: "
            f"{', '.join(unexplored) if unexplored else 'none'}"
        )
    evidence_progress = state.get("evidence_progress", {})
    if evidence_progress.get("observed"):
        lines.append(
            "live evidence: "
            f"observed={evidence_progress['observed']}; "
            f"valid={evidence_progress['valid']}; "
            f"failed={evidence_progress['failed']}"
        )
    active = [item for item in candidates if item["status"] in ACTIVE_STATUSES]
    closed = [item for item in candidates if item["status"] not in ACTIVE_STATUSES]
    lines.extend(f"active: {item['id']} ({item['status']})" for item in active[-3:])
    lines.extend(f"closed: {item['id']} ({item['status']})" for item in closed[-6:])
    if candidates:
        candidate = candidates[-1]
        lines.append(f"candidate: {candidate['id']} ({candidate['status']})")
        lines.append(
            f"parent frontier: {candidate['parent_frontier_id'] or 'unavailable'}"
        )
        lines.append(f"mechanism family: {candidate['family'] or 'unavailable'}")
        lines.append(
            "falsifiable statement: "
            f"{candidate['falsifiable_statement'] or 'unavailable'}"
        )
        lines.append(
            "expected removed work: "
            f"{candidate['expected_removed_work'] or 'unavailable'}"
        )
        direct_evidence = (
            candidate["actual_removed_work"]
            or (
                json.dumps(candidate["metrics"], ensure_ascii=False, sort_keys=True)
                if candidate["metrics"]
                else ""
            )
        )
        lines.append(f"direct evidence: {direct_evidence or 'unavailable'}")
        if candidate["unresolved_question"]:
            lines.append(f"unresolved contrast: {candidate['unresolved_question']}")
        missing = [
            field for field in DECISION_MATERIAL_FIELDS
            if not candidate.get(field)
        ]
        lines.append(f"missing: {', '.join(missing) if missing else 'none'}")
    return "\n".join(lines)


def _changed_candidate(
    previous: object, current: dict[str, Any]
) -> dict[str, Any] | None:
    candidates = [
        item for item in current.get("candidates", []) if isinstance(item, dict)
    ]
    if not candidates:
        return None
    before = {}
    if isinstance(previous, dict):
        before = {
            _text(item.get("id")): item
            for item in previous.get("candidates", [])
            if isinstance(item, dict) and item.get("id")
        }
    for item in reversed(candidates):
        if before.get(_text(item.get("id"))) != item:
            return item
    active = [item for item in candidates if item.get("status") in ACTIVE_STATUSES]
    return active[-1] if active else candidates[-1]


def _candidate_dimensions(candidate: dict[str, Any]) -> list[str]:
    explicit = [
        item for item in candidate.get("evidence_dimensions", [])
        if item in DIMENSION_ROUTES
    ]
    if explicit:
        return list(dict.fromkeys(explicit))
    evidence_text = "\n".join(
        [
            _text(candidate.get("family")),
            _text(candidate.get("hypothesis_family")),
            _text(candidate.get("falsifiable_statement")),
            _text(candidate.get("expected_removed_work")),
            _text(candidate.get("actual_removed_work")),
            _text(candidate.get("implementation_delta")),
            _text(candidate.get("unresolved_question")),
        ]
    )
    dimensions = [
        dimension for dimension, pattern in DIMENSION_PATTERNS.items()
        if pattern.search(evidence_text)
    ]
    return dimensions or ["execution"]


def research_review_metadata(
    previous: object, current: dict[str, Any]
) -> dict[str, Any]:
    """Describe one evidence-backed research opportunity for routing and dedupe."""
    candidate = _changed_candidate(previous, current) or {}
    dimensions = _candidate_dimensions(candidate) if candidate else ["execution"]
    route_signals = tuple(
        f"{DIMENSION_ROUTES[dimension][0]}|{DIMENSION_ROUTES[dimension][1]}"
        for dimension in dimensions
    )
    lens, basis = route_signals[0].split("|", 1)
    gap_key = f"{lens}:{basis}"
    evidence_material = {
        "gap_key": gap_key,
        "family": candidate.get("family"),
        "hypothesis_family": candidate.get("hypothesis_family"),
        "falsifiable_statement": candidate.get("falsifiable_statement"),
        "expected_removed_work": candidate.get("expected_removed_work"),
        "actual_removed_work": candidate.get("actual_removed_work"),
        "implementation_delta": candidate.get("implementation_delta"),
        "evidence_refs": candidate.get("evidence_refs"),
        "unresolved_question": candidate.get("unresolved_question"),
        "metrics": candidate.get("metrics"),
        "quality": candidate.get("quality"),
        "contract_fingerprint": candidate.get("contract_fingerprint"),
        "source_fingerprint": candidate.get("source_fingerprint"),
    }
    canonical = json.dumps(
        evidence_material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    available = sum(bool(candidate.get(field)) for field in DECISION_MATERIAL_FIELDS)
    completeness = round(available / len(DECISION_MATERIAL_FIELDS), 3)
    return {
        "candidate_id": _text(candidate.get("id")),
        "route_signals": route_signals,
        "route_basis": basis,
        "gap_key": gap_key,
        "gap_evidence_fingerprint": hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()[:16],
        "material_completeness": completeness,
    }


def describe_change(previous: object, current: dict[str, Any]) -> str:
    if not isinstance(previous, dict):
        return "initial structured research snapshot"
    changes: list[str] = []
    for section, keys in (
        ("contract", ("status", "claims_permitted")),
        ("result", ("status", "frontier", "resolved", "unresolved", "saturation_rule_met")),
    ):
        before = previous.get(section) if isinstance(previous.get(section), dict) else {}
        after = current.get(section) if isinstance(current.get(section), dict) else {}
        for key in keys:
            if before.get(key) != after.get(key):
                changes.append(f"{section}.{key}: {before.get(key)} -> {after.get(key)}")
    before_candidates = {
        str(item.get("id")): str(item.get("status"))
        for item in previous.get("candidates", [])
        if isinstance(item, dict) and item.get("id")
    }
    for item in current.get("candidates", []):
        if not isinstance(item, dict):
            continue
        candidate_id = str(item.get("id") or "")
        status = str(item.get("status") or "")
        if candidate_id and before_candidates.get(candidate_id) != status:
            changes.append(
                f"candidate {candidate_id}: {before_candidates.get(candidate_id)} -> {status}"
            )
    return "\n".join(changes) if changes else "structured source content changed"


def classify_change(previous: object, current: dict[str, Any]) -> str:
    """Classify the evidence opportunity without balancing personas or enforcing quotas."""
    if not isinstance(previous, dict):
        return "deepen"
    contract = current.get("contract") if isinstance(current.get("contract"), dict) else {}
    result = current.get("result") if isinstance(current.get("result"), dict) else {}
    if (
        contract.get("claims_permitted") is False
        and result.get("claims_permitted") is True
    ) or (
        result.get("saturation_rule_met") is True
        and isinstance(result.get("unresolved"), int)
        and result.get("unresolved") > 0
    ):
        return "guard"
    before_ids = {
        str(item.get("id"))
        for item in previous.get("candidates", [])
        if isinstance(item, dict) and item.get("id")
    }
    for item in current.get("candidates", []):
        if not isinstance(item, dict):
            continue
        if (
            str(item.get("id") or "") not in before_ids
            and str(item.get("status") or "") in ACTIVE_STATUSES
        ):
            return "expand"
    return "deepen"


def load_research_snapshot(workspace: str | Path) -> ResearchSnapshot | None:
    root = Path(workspace)
    payloads: list[dict[str, Any]] = []
    for relative in CORE_RESEARCH_SOURCES:
        payload = _read_json(root / Path(relative))
        if payload is None:
            return None
        payloads.append(payload)
    sources = list(CORE_RESEARCH_SOURCES)
    live_results, live_sources = _live_evidence_results(root)
    candidate_path = root / Path(CANDIDATE_RESULTS_SOURCE)
    candidate_results: dict[str, Any] = {"results": []}
    if candidate_path.exists():
        loaded_results = _read_json(candidate_path)
        if loaded_results is None:
            return None
        candidate_results = loaded_results
        sources.append(CANDIDATE_RESULTS_SOURCE)
    candidate_results = _combine_candidate_results(candidate_results, live_results)
    sources.extend(live_sources)
    contract, experiments, result = payloads
    canonical_payload = {
        "contract": contract,
        "experiments": experiments,
        "result": result,
        "candidate_results": candidate_results,
    }
    canonical = json.dumps(
        canonical_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    state = _normalized_state(contract, experiments, result, candidate_results)
    return ResearchSnapshot(
        fingerprint=hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24],
        projection=_render_projection(state),
        state=state,
        sources=tuple(sources),
    )
