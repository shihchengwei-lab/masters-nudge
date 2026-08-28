#!/usr/bin/env python3
"""Shared persistent Lens selection for Masters' Nudge."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


CONFIG_FILE = "config.json"
AUTOMATIC_STAGE = "automatic"
AUTOMATIC_LABEL = "Automatic · 依目前決策壓力選擇濾鏡"


@dataclass(frozen=True)
class StageSpec:
    name: str
    focus: str
    persona: str

    @property
    def label(self) -> str:
        return f"{self.name} · {self.focus}"


LENS_PERSONAS = {
    "jeff": "Jeff Dean",
    "linus": "Linus Torvalds",
    "fowler": "Martin Fowler",
    "beck": "Kent Beck",
    "lamport": "Leslie Lamport",
    "carmack": "John Carmack",
}
STAGE_SPECS = {
    "design": StageSpec("Design", "系統結構、因果與成本", "jeff"),
    "build": StageSpec("Build", "小步驟、測試與回饋", "beck"),
    "evolve": StageSpec("Evolve", "重構與變更成本", "fowler"),
    "review": StageSpec("Review", "簡化與責任歸屬", "linus"),
    "reliability": StageSpec("Reliability", "狀態、順序與失敗", "lamport"),
    "performance": StageSpec("Performance", "執行路徑與效能", "carmack"),
}
PERSONA_NAMES = dict(LENS_PERSONAS)
PERSONA_PUBLIC_LABELS = {
    spec.persona: spec.label for spec in STAGE_SPECS.values()
}


@dataclass(frozen=True)
class StageSelection:
    stage: str
    persona: str
    source: str


def config_path(base_dir: Path) -> Path:
    return Path(base_dir) / CONFIG_FILE


def persona_label(persona: str) -> str:
    """Return a user-facing work label without exposing persona identity."""
    key = str(persona or "").strip().lower()
    return PERSONA_PUBLIC_LABELS.get(key, "未記錄")


def stage_label(stage: str) -> str:
    key = str(stage or "").strip().lower()
    if key == AUTOMATIC_STAGE:
        return AUTOMATIC_LABEL
    if key not in STAGE_SPECS:
        return AUTOMATIC_LABEL
    return STAGE_SPECS[key].label


def resolve_stage(
    base_dir: Path, *, environ: Mapping[str, str] | None = None
) -> StageSelection:
    """Resolve a manual Lens override or the default automatic Router mode."""
    environment = os.environ if environ is None else environ
    env_stage = str(environment.get("MASTERS_NUDGE_STAGE") or "").strip().lower()
    if env_stage:
        if env_stage == AUTOMATIC_STAGE:
            return StageSelection(AUTOMATIC_STAGE, "", "environment")
        if env_stage in STAGE_SPECS:
            return StageSelection(
                env_stage, STAGE_SPECS[env_stage].persona, "environment"
            )
        return StageSelection(AUTOMATIC_STAGE, "", "invalid_environment")

    try:
        payload = json.loads(config_path(base_dir).read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    config_stage = str(payload.get("stage") or "").strip().lower()
    if config_stage == AUTOMATIC_STAGE:
        return StageSelection(AUTOMATIC_STAGE, "", "config")
    if config_stage in STAGE_SPECS:
        return StageSelection(
            config_stage, STAGE_SPECS[config_stage].persona, "config"
        )
    return StageSelection(AUTOMATIC_STAGE, "", "default")


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
    """Atomically persist a valid public Lens selection."""
    key = str(stage or "").strip().lower()
    if key != AUTOMATIC_STAGE and key not in STAGE_SPECS:
        raise ValueError(f"unsupported stage: {stage!r}")
    _atomic_save(base_dir, {"stage": key}, "stage-")
