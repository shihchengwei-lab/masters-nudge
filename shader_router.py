#!/usr/bin/env python3
"""Deterministic routing for the Shader workspace specialization."""

from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from lens_router import ReviewRoute


SHADER_PERSONAS = {
    "akenine_moller": "Tomas Akenine-Moller",
    "carmack": "John Carmack",
    "karis": "Brian Karis",
    "lottes": "Timothy Lottes",
    "quilez": "Inigo Quilez",
    "tatarchuk": "Natalya Tatarchuk",
}

SHADER_PERSONA_FOCUS = {
    "akenine_moller": "幾何、可見性與 overdraw",
    "carmack": "GPU 執行路徑與效能",
    "karis": "URP 材質與渲染契約",
    "lottes": "畫質穩定與精度",
    "quilez": "程序化數學與 SDF",
    "tatarchuk": "跨硬體與上架驗證",
}

ROUTE_STATE_SUFFIX = ".shader-route.json"
ROUTE_HISTORY_LIMIT = 6


def shader_persona_label(persona: str) -> str:
    key = str(persona or "").strip().lower()
    if key not in SHADER_PERSONAS:
        raise ValueError(f"Unsupported Shader lens: {persona}")
    return f"{SHADER_PERSONAS[key]}（{SHADER_PERSONA_FOCUS[key]}）"

STAGE_PRIMARY_LENS = {
    "frame": "karis",
    "explore": "quilez",
    "optimize": "carmack",
    "verify": "tatarchuk",
}

SPECIALIST_PATTERNS = (
    (
        "lottes",
        "visual-stability-evidence",
        re.compile(
            r"temporal|shimmer|banding|precision|flicker|aliasing|ghosting|"
            r"\bssim\b|static (?:image|screenshot|camera)|moving camera|motion|"
            r"時間穩定|閃爍|色帶|精度|鋸齒|固定(?:截圖|鏡頭)|靜態(?:截圖|畫面)|移動鏡頭",
            re.IGNORECASE,
        ),
    ),
    (
        "akenine_moller",
        "visibility-geometry-evidence",
        re.compile(
            r"triangle|geometry|overdraw|occlusion|culling|visibility|lod|"
            r"fragment|sample|coverage|depth complexity|"
            r"三角形|幾何|過度繪製|遮擋|剔除|可見性|透明重疊|取樣覆蓋",
            re.IGNORECASE,
        ),
    ),
    (
        "carmack",
        "measured-performance-evidence",
        re.compile(
            r"gpu profiler|frame time|benchmark|hot path|hotspot|bandwidth|"
            r"occupancy|register pressure|compiler disassembly|\b\d+(?:\.\d+)?\s*(?:ns|us|µs|ms)\b|"
            r"GPU 效能分析|GPU 性能分析|影格時間|基準測試|熱路徑|頻寬|暫存器壓力",
            re.IGNORECASE,
        ),
    ),
    (
        "tatarchuk",
        "platform-delivery-evidence",
        re.compile(
            r"cross.hardware|platform|graphics api|vulkan|metal|directx|mobile|"
            r"asset store|marketplace|package import|"
            r"跨硬體|跨平台|圖形介面|行動裝置|上架|套件匯入",
            re.IGNORECASE,
        ),
    ),
    (
        "quilez",
        "procedural-representation-evidence",
        re.compile(
            r"sdf|raymarch|noise|procedural|distance field|lookup|texture|"
            r"interpolat|\blut\b|程序化|距離場|雜訊|噪聲|光線步進|查表|插值|表示法",
            re.IGNORECASE,
        ),
    ),
    (
        "karis",
        "render-contract-evidence",
        re.compile(
            r"pbr|lighting|material|brdf|render pass|shader variant|frame debugger|"
            r"\bforward\b|\bdepthonly\b|\bshadowcaster\b|\burp\b|\bhdr\b|"
            r"roughness|normal space|材質|光照|渲染通道|著色器變體|渲染契約",
            re.IGNORECASE,
        ),
    ),
)


def _route_state_path(state_dir: Path, session_key: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(session_key or "unknown"))[:200]
    return Path(state_dir) / f"{safe or 'unknown'}{ROUTE_STATE_SUFFIX}"


def _empty_route_state() -> dict:
    return {
        "counts": {lens: 0 for lens in SHADER_PERSONAS},
        "recent": [],
    }


def _load_route_state(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        return _empty_route_state()
    if not isinstance(payload, dict):
        return _empty_route_state()
    raw_counts = payload.get("counts")
    raw_recent = payload.get("recent")
    if not isinstance(raw_counts, dict) or not isinstance(raw_recent, list):
        return _empty_route_state()

    counts = {}
    for lens in SHADER_PERSONAS:
        try:
            counts[lens] = max(0, int(raw_counts.get(lens, 0)))
        except (TypeError, ValueError):
            counts[lens] = 0
    recent = [
        str(lens) for lens in raw_recent
        if str(lens) in SHADER_PERSONAS
    ][-ROUTE_HISTORY_LIMIT:]
    return {
        "counts": counts,
        "recent": recent,
    }


def _save_route_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".tmp",
        prefix="shader-route-",
        dir=path.parent,
        delete=False,
        encoding="utf-8",
    )
    temp_path = Path(handle.name)
    try:
        json.dump({"schema_version": 1, **state}, handle, ensure_ascii=False)
        handle.write("\n")
        handle.close()
        os.replace(temp_path, path)
    finally:
        try:
            handle.close()
        except Exception:
            pass
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


def _matching_candidates(evidence: str) -> list[tuple[str, str, int, int]]:
    text = str(evidence or "")
    matches = []
    for order, (lens, trigger, pattern) in enumerate(SPECIALIST_PATTERNS):
        strength = len(pattern.findall(text))
        if strength:
            matches.append((lens, trigger, strength, order))
    return matches


def _structured_candidates(route_signals: tuple[str, ...]) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    for raw in route_signals:
        lens, separator, basis = str(raw or "").partition("|")
        lens = lens.strip().lower()
        basis = basis.strip()
        if separator and lens in SHADER_PERSONAS and basis:
            candidates.append((lens, basis))
    return candidates


def _record_route(state: dict, lens: str) -> None:
    state["counts"][lens] = state["counts"].get(lens, 0) + 1
    state["recent"] = [*state["recent"], lens][-ROUTE_HISTORY_LIMIT:]


def _select_first_eligible(
    candidates: list[tuple[str, str, str]],
    ineligible: set[str],
) -> tuple[str, str, str] | None:
    return next(
        (candidate for candidate in candidates if candidate[0] not in ineligible),
        None,
    )


def resolve_shader_route(
    stage: str,
    prompt: str = "",
    primary_lens: str = "",
    *,
    checkpoint: bool = True,
    state_dir: Path | None = None,
    session_key: str = "",
    route_signals: tuple[str, ...] = (),
    injected_personas: tuple[str, ...] = (),
) -> ReviewRoute:
    """Use the selected primary at Stop and allow evidence overrides at checkpoints."""

    normalized_stage = str(stage or "").strip().lower()
    if normalized_stage not in STAGE_PRIMARY_LENS:
        raise ValueError(f"Unsupported Shader review stage: {stage}")

    selected = str(primary_lens or "").strip().lower()
    if selected and selected not in SHADER_PERSONAS:
        raise ValueError(f"Unsupported Shader lens: {primary_lens}")
    primary = selected or STAGE_PRIMARY_LENS[normalized_stage]
    if not checkpoint:
        return ReviewRoute(
            normalized_stage,
            primary,
            primary,
            "",
            "",
            "shader_stop_primary",
        )

    state_path = (
        _route_state_path(Path(state_dir), session_key)
        if state_dir is not None and str(session_key or "").strip()
        else None
    )
    state = _load_route_state(state_path) if state_path else _empty_route_state()
    def candidate_key(candidate: tuple[str, str, int, int]) -> tuple:
        lens, _trigger, strength, order = candidate
        return (
            -strength,
            0 if lens == primary else 1,
            order,
        )

    structured_tier: list[tuple[str, str, str]] = [
        (lens, basis, "shader_structured_evidence")
        for lens, basis in _structured_candidates(route_signals)
    ]
    matched = sorted(_matching_candidates(prompt), key=candidate_key)
    evidence_tiers: list[list[tuple[str, str, str]]] = []
    last_strength: int | None = None
    for lens, trigger, strength, _order in matched:
        if strength != last_strength:
            evidence_tiers.append([])
        evidence_tiers[-1].append((lens, trigger, "shader_evidence_override"))
        last_strength = strength
    cooldown = tuple(
        persona for persona in injected_personas[-2:]
        if persona in SHADER_PERSONAS
    )
    ineligible = set(cooldown)
    tiers = [
        *([structured_tier] if structured_tier else []),
        *evidence_tiers,
        [(primary, "", "shader_primary" if selected else "shader_stage")],
        [(lens, "", "shader_cooldown_fallback") for lens in SHADER_PERSONAS],
    ]
    selected_candidate = next(
        (
            candidate
            for tier in tiers
            if (candidate := _select_first_eligible(tier, ineligible))
            is not None
        ),
        None,
    )
    if selected_candidate is None:
        raise RuntimeError("No eligible Shader Persona after cooldown")
    lens, trigger, route_source = selected_candidate
    suppression_reason = (
        f"injected-persona-cooldown:{','.join(cooldown)}" if cooldown else ""
    )

    if state_path:
        _record_route(state, lens)
        _save_route_state(state_path, state)

    if lens == primary:
        return ReviewRoute(
            normalized_stage,
            primary,
            primary,
            "",
            trigger,
            route_source,
            candidate_lens=lens if trigger else "",
            candidate_trigger=trigger,
            suppression_reason=suppression_reason,
        )
    return ReviewRoute(
        normalized_stage,
        primary,
        lens,
        lens,
        trigger,
        route_source,
        candidate_lens=lens,
        candidate_trigger=trigger,
        suppression_reason=suppression_reason,
    )
