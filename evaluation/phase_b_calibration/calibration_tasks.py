#!/usr/bin/env python3
"""Materialize calibration task states without exposing graders to the agent."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
TASKS_DIR = HERE / "tasks"
DEFAULT_SPEC = HERE / "calibration-task-spec-v1.json"
OVERLAY_STATES = ("candidate", "reference", "alternative", "near_miss_1", "near_miss_2")
ALL_STATES = ("baseline", *OVERLAY_STATES)


def load_spec(path: Path = DEFAULT_SPEC) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("calibration spec requires a non-empty fixtures list")
    ids = [str(item.get("id") or "") for item in fixtures]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        raise ValueError("fixture ids must be present and unique")
    return payload


def task_root(task_id: str) -> Path:
    return TASKS_DIR / task_id


def validate_assets(spec: dict[str, Any]) -> None:
    for fixture in spec["fixtures"]:
        root = task_root(fixture["id"])
        baseline = root / "baseline"
        if not baseline.is_dir() or not (baseline / "TASK.md").is_file():
            raise ValueError(f"missing baseline/TASK.md for {fixture['id']}")
        for state in OVERLAY_STATES:
            path = root / state
            if not path.is_dir() or not any(path.iterdir()):
                raise ValueError(f"missing non-empty {state} overlay for {fixture['id']}")
        required = ("lens", "objective", "prior_assistant", "recent_evidence", "positive_control")
        if any(not str(fixture.get(key) or "").strip() for key in required):
            raise ValueError(f"incomplete continuation envelope for {fixture['id']}")


def overlay_tree(source: Path, destination: Path) -> None:
    delete_manifest = source / ".delete"
    if delete_manifest.is_file():
        destination_root = destination.resolve()
        for line in delete_manifest.read_text(encoding="utf-8").splitlines():
            relative_text = line.strip()
            if not relative_text:
                continue
            target = (destination / relative_text).resolve()
            if destination_root not in target.parents:
                raise ValueError(f"unsafe delete path: {relative_text}")
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if relative == Path(".delete"):
            continue
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def _git(workspace: Path, *args: str) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")


def materialize(task_id: str, destination: Path, *, state: str = "candidate") -> Path:
    if state not in ALL_STATES:
        raise ValueError(f"unsupported calibration state: {state}")
    root = task_root(task_id)
    if not root.is_dir():
        raise ValueError(f"unknown calibration task: {task_id}")
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination}")
    shutil.copytree(root / "baseline", destination)
    _git(destination, "init", "-q")
    _git(destination, "config", "user.email", "phase-b-calibration@example.invalid")
    _git(destination, "config", "user.name", "Phase B Calibration")
    _git(destination, "add", "--all")
    _git(destination, "commit", "-q", "-m", "baseline")
    if state != "baseline":
        overlay_tree(root / "candidate", destination)
    if state not in {"baseline", "candidate"}:
        overlay_tree(root / state, destination)
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--state", choices=ALL_STATES, default="candidate")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec = load_spec()
    validate_assets(spec)
    known = {fixture["id"] for fixture in spec["fixtures"]}
    if args.task_id not in known:
        raise SystemExit(f"unknown task: {args.task_id}")
    materialize(args.task_id, args.destination, state=args.state)
    print(args.destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
