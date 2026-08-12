#!/usr/bin/env python3
"""Shared persistent stage and legacy persona selection for Masters' Nudge."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


CONFIG_FILE = "config.json"
LENS_PERSONAS = {
    "jeff": "Jeff Dean",
    "linus": "Linus Torvalds",
    "fowler": "Martin Fowler",
    "beck": "Kent Beck",
    "lamport": "Leslie Lamport",
    "carmack": "John Carmack",
}
STAGE_LENSES = {
    "design": "jeff",
    "build": "beck",
    "evolve": "fowler",
    "review": "linus",
}
LENS_STAGES = {lens: stage for stage, lens in STAGE_LENSES.items()}
STAGE_NAMES = {
    "design": "Design",
    "build": "Build",
    "evolve": "Evolve",
    "review": "Review",
}
PERSONA_NAMES = {"general": "General", **LENS_PERSONAS}
PERSONA_FOCUS = {
    "general": "通用證據審查",
    "jeff": "系統因果與成本",
    "linus": "簡化與責任歸屬",
    "fowler": "重構與變更成本",
    "beck": "小步驟與測試",
    "lamport": "狀態、順序與失敗",
    "carmack": "執行路徑與效能",
}


@dataclass(frozen=True)
class PersonaSelection:
    persona: str
    source: str


@dataclass(frozen=True)
class StageSelection:
    stage: str
    persona: str
    source: str
    locked: bool = False


def config_path(base_dir: Path) -> Path:
    return Path(base_dir) / CONFIG_FILE


def persona_label(persona: str) -> str:
    key = str(persona or "").strip().lower()
    if key not in PERSONA_NAMES:
        key = "general"
    return f"{PERSONA_NAMES[key]} lens（{PERSONA_FOCUS[key]}）"


def stage_label(stage: str) -> str:
    key = str(stage or "").strip().lower()
    if key not in STAGE_LENSES:
        key = "build"
    persona = STAGE_LENSES[key]
    return f"{STAGE_NAMES[key]} · {PERSONA_NAMES[persona]}（{PERSONA_FOCUS[persona]}）"


def resolve_stage(
    base_dir: Path, *, environ: Mapping[str, str] | None = None
) -> StageSelection:
    """Resolve env override, new stage config, legacy persona config, then Build."""
    environment = os.environ if environ is None else environ
    env_persona = str(environment.get("BUDDY_PERSONA") or "").strip().lower()
    if env_persona:
        if env_persona == "general":
            return StageSelection("build", "beck", "environment", True)
        return StageSelection(
            LENS_STAGES.get(env_persona, "forced"),
            env_persona,
            "environment",
            True,
        )

    try:
        payload = json.loads(config_path(base_dir).read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    config_stage = str(payload.get("stage") or "").strip().lower()
    if config_stage in STAGE_LENSES:
        return StageSelection(
            config_stage, STAGE_LENSES[config_stage], "config", False
        )
    if config_stage == "general":
        return StageSelection("build", "beck", "legacy_config", False)

    legacy_persona = str(payload.get("persona") or "").strip().lower()
    if legacy_persona == "general":
        return StageSelection("build", "beck", "legacy_config", False)
    if legacy_persona in PERSONA_NAMES:
        legacy_stage = LENS_STAGES.get(legacy_persona, "forced")
        return StageSelection(
            legacy_stage,
            legacy_persona,
            "legacy_config",
            legacy_persona in {"lamport", "carmack"},
        )
    return StageSelection("build", "beck", "default", False)


def resolve_persona(
    base_dir: Path, *, environ: Mapping[str, str] | None = None
) -> PersonaSelection:
    """Backward-compatible primary persona view of the active stage."""
    selection = resolve_stage(base_dir, environ=environ)
    return PersonaSelection(selection.persona, selection.source)


def _atomic_save(base_dir: Path, payload: dict[str, str], prefix: str) -> None:
    base_dir = Path(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    fd = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".tmp",
        prefix=prefix,
        dir=base_dir,
        delete=False,
        encoding="utf-8",
    )
    temp_path = Path(fd.name)
    try:
        json.dump(payload, fd, ensure_ascii=False)
        fd.write("\n")
        fd.close()
        os.replace(temp_path, config_path(base_dir))
    finally:
        try:
            fd.close()
        except Exception:
            pass
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


def save_stage(base_dir: Path, stage: str) -> None:
    """Atomically persist a valid lifecycle stage in the new config format."""
    key = str(stage or "").strip().lower()
    if key not in STAGE_LENSES:
        raise ValueError(f"unsupported stage: {stage!r}")
    _atomic_save(base_dir, {"stage": key}, "stage-")


def save_persona(base_dir: Path, persona: str) -> None:
    """Persist the legacy persona format for compatibility callers."""
    key = str(persona or "").strip().lower()
    if key not in PERSONA_NAMES:
        raise ValueError(f"unsupported persona: {persona!r}")

    _atomic_save(base_dir, {"persona": key}, "persona-")
