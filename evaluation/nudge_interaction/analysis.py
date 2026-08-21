"""Aggregate delivery, reaction, and routing evidence for one Shader session."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping, Sequence


SHADER_PERSONAS = (
    ("akenine_moller", "Tomas Akenine-Moller"),
    ("carmack", "John Carmack"),
    ("karis", "Brian Karis"),
    ("lottes", "Timothy Lottes"),
    ("quilez", "Inigo Quilez"),
    ("tatarchuk", "Natalya Tatarchuk"),
)

REACTION_CLASSES = (
    ("explicit_uptake", "明確接住"),
    ("reinterpretation", "重新詮釋"),
    ("possible_influence", "可能影響"),
    ("temporal_only", "僅時間／內容相關"),
    ("no_observable_response", "無可觀察反應"),
)


def _percent(part: int, whole: int) -> float:
    if whole <= 0:
        return 0.0
    return round(part * 100.0 / whole, 1)


def _session_telemetry(
    rows: Iterable[Mapping[str, object]], session_id: str
) -> list[Mapping[str, object]]:
    return [
        row
        for row in rows
        if row.get("session_id") == session_id and row.get("domain") == "shader"
    ]


def _delivery_index(
    rows: Iterable[Mapping[str, object]], session_id: str
) -> tuple[list[Mapping[str, object]], dict[str, str]]:
    reviews: list[Mapping[str, object]] = []
    receipts: dict[str, str] = {}
    for row in rows:
        if row.get("session_id") != session_id:
            continue
        kind = row.get("kind")
        if kind == "review":
            reviews.append(row)
        elif kind == "delivery_receipt" and row.get("reaction_ts"):
            receipts[str(row["reaction_ts"])] = str(
                row.get("delivery_status", "unknown")
            )
    return reviews, receipts


def _validate_annotations(
    document: Mapping[str, object],
    session_id: str,
    reviews: Sequence[Mapping[str, object]],
    receipts: Mapping[str, str],
) -> list[Mapping[str, object]]:
    if document.get("schema_version") != 1:
        raise ValueError("annotation schema_version must be 1")
    if document.get("session_id") != session_id:
        raise ValueError("annotation session_id does not match analysis session")

    review_ids = {str(row.get("ts")) for row in reviews}
    allowed_classes = {key for key, _ in REACTION_CLASSES}
    annotations = list(document.get("annotations", []))
    seen: set[str] = set()

    for item in annotations:
        if not isinstance(item, Mapping):
            raise ValueError("each annotation must be an object")
        reaction_ts = str(item.get("reaction_ts", ""))
        if not reaction_ts or reaction_ts not in review_ids:
            raise ValueError(f"annotation {reaction_ts!r} has no matching finding")
        if reaction_ts in seen:
            raise ValueError(f"duplicate annotation for {reaction_ts}")
        seen.add(reaction_ts)
        if receipts.get(reaction_ts) != "injected":
            raise ValueError(f"annotation {reaction_ts} references a finding that was not injected")
        if not item.get("evaluable"):
            raise ValueError(f"annotation {reaction_ts} is not evaluable")
        reaction_class = str(item.get("reaction_class", ""))
        if reaction_class not in allowed_classes:
            raise ValueError(f"unknown reaction_class {reaction_class!r}")
        if not str(item.get("evidence", "")).strip():
            raise ValueError(f"annotation {reaction_ts} has no evidence")

        content_match = bool(item.get("content_match"))
        behavior_change = bool(item.get("behavior_change"))
        explicit_reference = bool(item.get("explicit_reference"))
        reframed = bool(item.get("reframed"))
        if reaction_class == "explicit_uptake" and not (
            content_match and explicit_reference
        ):
            raise ValueError("explicit_uptake requires content_match and explicit_reference")
        if reaction_class == "reinterpretation" and not (content_match and reframed):
            raise ValueError("reinterpretation requires content_match and reframed evidence")
        if reaction_class == "possible_influence" and not (
            content_match and behavior_change
        ):
            raise ValueError(
                "possible_influence requires content_match and behavior_change"
            )
        if reaction_class == "temporal_only" and not (
            content_match and not behavior_change
        ):
            raise ValueError(
                "temporal_only requires content_match without observable behavior_change"
            )
        if reaction_class == "no_observable_response" and (
            content_match or behavior_change
        ):
            raise ValueError(
                "no_observable_response cannot claim content_match or behavior_change"
            )
    return annotations


def analyze_session(
    telemetry_rows: Iterable[Mapping[str, object]],
    reaction_rows: Iterable[Mapping[str, object]],
    annotation_document: Mapping[str, object],
    session_id: str,
) -> dict[str, object]:
    """Return deterministic aggregates without making a causal claim."""

    telemetry = _session_telemetry(telemetry_rows, session_id)
    reviews, receipts = _delivery_index(reaction_rows, session_id)
    annotations = _validate_annotations(
        annotation_document, session_id, reviews, receipts
    )

    invocation_total = len(telemetry)
    persona_counts = Counter(str(row.get("effective_lens", "")) for row in telemetry)
    status_counts: dict[str, Counter[str]] = {
        persona: Counter() for persona, _ in SHADER_PERSONAS
    }
    for row in telemetry:
        persona = str(row.get("effective_lens", ""))
        if persona in status_counts:
            status_counts[persona][str(row.get("status", "unknown"))] += 1

    invocations = []
    for persona, display_name in SHADER_PERSONAS:
        count = persona_counts[persona]
        invocations.append(
            {
                "persona": persona,
                "display_name": display_name,
                "count": count,
                "percent": _percent(count, invocation_total),
                "statuses": dict(sorted(status_counts[persona].items())),
            }
        )

    generated = len(reviews)
    injected = sum(
        1 for row in reviews if receipts.get(str(row.get("ts"))) == "injected"
    )
    evaluable = len(annotations)
    content_matched = sum(1 for item in annotations if item.get("content_match"))
    funnel_values = (
        ("generated", "產生 finding", generated),
        ("injected", "成功注入", injected),
        ("evaluable", "有可評註後續", evaluable),
        ("content_match", "內容對應", content_matched),
    )
    delivery_funnel = []
    previous = generated
    for index, (key, label, count) in enumerate(funnel_values):
        delivery_funnel.append(
            {
                "key": key,
                "label": label,
                "count": count,
                "percent_of_generated": _percent(count, generated),
                "percent_of_previous": 100.0 if index == 0 else _percent(count, previous),
            }
        )
        previous = count

    reaction_counts = Counter(str(item["reaction_class"]) for item in annotations)
    reactions = [
        {
            "key": key,
            "label": label,
            "count": reaction_counts[key],
            "percent": _percent(reaction_counts[key], evaluable),
        }
        for key, label in REACTION_CLASSES
    ]

    cohort = annotation_document.get("cohort", {})
    if not isinstance(cohort, Mapping):
        raise ValueError("cohort must be an object")
    research_mode_counts = Counter()
    for row in telemetry:
        trigger = str(row.get("review_trigger") or "")
        prefix = "shader-research-"
        if trigger.startswith(prefix):
            mode = trigger[len(prefix):]
            if mode in {"expand", "deepen", "guard"}:
                research_mode_counts[mode] += 1
    mode_counts = {
        mode: research_mode_counts[mode] for mode in ("expand", "deepen", "guard")
    }
    forward_opportunities = mode_counts["expand"] + mode_counts["deepen"]
    return {
        "schema_version": 1,
        "session_id": session_id,
        "invocation_total": invocation_total,
        "invocations": invocations,
        "delivery_funnel": delivery_funnel,
        "reactions": reactions,
        "annotation_coverage": {
            "cohort_name": str(cohort.get("name", "")),
            "cohort_generated": int(cohort.get("generated_count", 0)),
            "evaluable": evaluable,
            "percent_of_session_injected": _percent(evaluable, injected),
        },
        "delivery_statuses": dict(
            sorted(
                Counter(
                    receipts.get(str(row.get("ts")), "no_receipt") for row in reviews
                ).items()
            )
        ),
        "research_modes": {
            "counts": mode_counts,
            "forward_opportunities": forward_opportunities,
            "forward_exceeds_guard": forward_opportunities > mode_counts["guard"],
            "interpretation": (
                "這是呼叫機會分布，不是主模型前進率，也不是 runtime 配額。"
            ),
        },
        "interpretation_limit": (
            "分類只描述時間順序、內容對應與可觀察行為；沒有無 Nudge 對照，"
            "不能證明因果。"
        ),
    }
