"""Keep Shader search breadth separate from within-mechanism refinements."""

from __future__ import annotations

import copy
import re
from typing import Any


FAMILY_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def new_registry(
    *,
    max_candidate_cells: int | None,
    refinement_limit_per_cell: int | None,
) -> dict[str, Any]:
    if max_candidate_cells is not None and max_candidate_cells < 1:
        raise ValueError("max_candidate_cells must be positive")
    if refinement_limit_per_cell is not None and refinement_limit_per_cell < 0:
        raise ValueError("refinement_limit_per_cell cannot be negative")
    return {
        "schema_version": 1,
        "max_candidate_cells": max_candidate_cells,
        "refinement_limit_per_cell": refinement_limit_per_cell,
        "candidates": [],
        "rejections": [],
    }

def _text(value: object) -> str:
    return str(value or "").strip()


def _proposal_missing(proposal: dict[str, Any]) -> list[str]:
    missing = []
    if not _text(proposal.get("name")):
        missing.append("name")

    hypothesis = proposal.get("bottleneck_hypothesis")
    if not isinstance(hypothesis, dict):
        return missing + ["bottleneck_hypothesis"]
    hypothesis_family = _text(hypothesis.get("family"))
    if not hypothesis_family or not FAMILY_ID_RE.fullmatch(hypothesis_family):
        missing.append("bottleneck_hypothesis.family")
    if not _text(hypothesis.get("statement")):
        missing.append("bottleneck_hypothesis.statement")
    evidence_refs = hypothesis.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not any(
        _text(item) for item in evidence_refs
    ):
        missing.append("evidence_refs")
    if not _text(hypothesis.get("falsifiable_prediction")):
        missing.append("bottleneck_hypothesis.falsifiable_prediction")

    mechanism = proposal.get("work_elimination_mechanism")
    if not isinstance(mechanism, dict):
        return missing + ["work_elimination_mechanism"]
    mechanism_family = _text(mechanism.get("family"))
    if not mechanism_family or not FAMILY_ID_RE.fullmatch(mechanism_family):
        missing.append("work_elimination_mechanism.family")
    if not _text(mechanism.get("eliminated_work")):
        missing.append("work_elimination_mechanism.eliminated_work")
    return missing


def _cell_key(proposal: dict[str, Any]) -> str:
    hypothesis = proposal["bottleneck_hypothesis"]
    mechanism = proposal["work_elimination_mechanism"]
    return f"{_text(hypothesis['family'])}::{_text(mechanism['family'])}"


def _reject(
    state: dict[str, Any],
    proposal_name: str,
    reason: str,
    **details: Any,
) -> dict[str, Any]:
    result = {
        "accepted": False,
        "reason": reason,
        **details,
    }
    state["rejections"].append(
        {
            "name": proposal_name,
            "reason": reason,
            **details,
        }
    )
    return result


def register_candidate(
    state: dict[str, Any],
    proposal: dict[str, Any],
) -> dict[str, Any]:
    missing = _proposal_missing(proposal)
    name = _text(proposal.get("name"))
    if missing:
        return _reject(
            state,
            name,
            "invalid-proposal",
            missing=missing,
        )

    cell_key = _cell_key(proposal)
    existing = next(
        (
            item
            for item in state["candidates"]
            if item.get("search_cell") == cell_key
        ),
        None,
    )
    if existing:
        return _reject(
            state,
            name,
            "existing-search-cell",
            search_cell=cell_key,
            record_as_refinement_of=existing["candidate_id"],
        )

    max_candidate_cells = state.get("max_candidate_cells")
    if (
        max_candidate_cells is not None
        and len(state["candidates"]) >= int(max_candidate_cells)
    ):
        return _reject(
            state,
            name,
            "candidate-cell-budget-exhausted",
            search_cell=cell_key,
        )

    candidate_id = f"candidate-{len(state['candidates']) + 1:03d}"
    candidate = copy.deepcopy(proposal)
    candidate.update(
        {
            "candidate_id": candidate_id,
            "search_cell": cell_key,
            "refinements": [],
        }
    )
    state["candidates"].append(candidate)
    return {
        "accepted": True,
        "candidate_id": candidate_id,
        "search_cell": cell_key,
        "candidate_slot": len(state["candidates"]),
    }


def register_refinement(
    state: dict[str, Any],
    parent_candidate_id: str,
    refinement: dict[str, Any],
) -> dict[str, Any]:
    parent = next(
        (
            item
            for item in state["candidates"]
            if item.get("candidate_id") == parent_candidate_id
        ),
        None,
    )
    name = _text(refinement.get("name"))
    if parent is None:
        return _reject(
            state,
            name,
            "unknown-parent-candidate",
            parent_candidate_id=parent_candidate_id,
        )
    missing = [
        field
        for field in ("name", "changed_variable", "discriminator")
        if not _text(refinement.get(field))
    ]
    if missing:
        return _reject(
            state,
            name,
            "invalid-refinement",
            parent_candidate_id=parent_candidate_id,
            missing=missing,
        )

    limit = state.get("refinement_limit_per_cell")
    if limit is not None and len(parent["refinements"]) >= int(limit):
        return _reject(
            state,
            name,
            "refinement-budget-exhausted",
            parent_candidate_id=parent_candidate_id,
        )

    refinement_id = (
        f"{parent_candidate_id}-r{len(parent['refinements']) + 1:02d}"
    )
    record = copy.deepcopy(refinement)
    record["refinement_id"] = refinement_id
    parent["refinements"].append(record)
    return {
        "accepted": True,
        "refinement_id": refinement_id,
        "parent_candidate_id": parent_candidate_id,
        "candidate_slot_consumed": False,
    }


def coverage_report(state: dict[str, Any]) -> dict[str, Any]:
    candidates = state.get("candidates") or []
    rejections = state.get("rejections") or []
    hypotheses = {
        item["bottleneck_hypothesis"]["family"] for item in candidates
    }
    mechanisms = {
        item["work_elimination_mechanism"]["family"] for item in candidates
    }
    max_candidate_cells = state.get("max_candidate_cells")
    refinement_limit = state.get("refinement_limit_per_cell")
    return {
        "candidate_cells": len(candidates),
        "candidate_cell_budget": (
            int(max_candidate_cells) if max_candidate_cells is not None else None
        ),
        "candidate_cells_remaining": (
            max(0, int(max_candidate_cells) - len(candidates))
            if max_candidate_cells is not None
            else None
        ),
        "refinement_budget_per_cell": (
            int(refinement_limit) if refinement_limit is not None else None
        ),
        "hypothesis_families": len(hypotheses),
        "mechanism_families": len(mechanisms),
        "refinements": sum(len(item.get("refinements") or []) for item in candidates),
        "existing_cell_rejections": sum(
            item.get("reason") == "existing-search-cell" for item in rejections
        ),
    }
