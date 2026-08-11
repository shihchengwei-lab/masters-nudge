#!/usr/bin/env python3
"""Shared persistent persona selection for Masters' Nudge."""

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


def config_path(base_dir: Path) -> Path:
    return Path(base_dir) / CONFIG_FILE


def persona_label(persona: str) -> str:
    key = str(persona or "").strip().lower()
    if key not in PERSONA_NAMES:
        key = "general"
    return f"{PERSONA_NAMES[key]} lens（{PERSONA_FOCUS[key]}）"


def resolve_persona(
    base_dir: Path, *, environ: Mapping[str, str] | None = None
) -> PersonaSelection:
    """Resolve env override first, then GUI config, then General."""
    environment = os.environ if environ is None else environ
    env_persona = str(environment.get("BUDDY_PERSONA") or "").strip().lower()
    if env_persona:
        return PersonaSelection(env_persona, "environment")

    try:
        payload = json.loads(config_path(base_dir).read_text(encoding="utf-8"))
        config_persona = str(payload.get("persona") or "").strip().lower()
    except (AttributeError, OSError, TypeError, ValueError):
        config_persona = ""
    if config_persona in PERSONA_NAMES:
        return PersonaSelection(config_persona, "config")
    return PersonaSelection("general", "default")


def save_persona(base_dir: Path, persona: str) -> None:
    """Atomically persist a valid GUI selection."""
    key = str(persona or "").strip().lower()
    if key not in PERSONA_NAMES:
        raise ValueError(f"unsupported persona: {persona!r}")

    base_dir = Path(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    fd = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".tmp",
        prefix="persona-",
        dir=base_dir,
        delete=False,
        encoding="utf-8",
    )
    temp_path = Path(fd.name)
    try:
        json.dump({"persona": key}, fd, ensure_ascii=False)
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
