#!/usr/bin/env python3
"""Materialize Phase B task states without exposing reference or hidden graders."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
TASKS_DIR = HERE / "tasks"
DEFAULT_SPEC = HERE / "phase-b-task-spec-v1.json"


def load_spec(path: Path = DEFAULT_SPEC) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("task spec requires fixtures")
    ids = [str(item.get("id") or "") for item in fixtures]
    if any(not item for item in ids) or len(ids) != len(set(ids)):
        raise ValueError("task ids must be present and unique")
    return payload


def task_dirs(task_id: str) -> tuple[Path, Path, Path]:
    root = TASKS_DIR / task_id
    return root / "baseline", root / "candidate", root / "reference"


def validate_assets(spec: dict[str, Any]) -> None:
    for fixture in spec["fixtures"]:
        baseline, candidate, reference = task_dirs(fixture["id"])
        for path in (baseline, candidate, reference):
            if not path.is_dir():
                raise ValueError(f"missing task asset directory: {path}")
        if not (baseline / "TASK.md").is_file():
            raise ValueError(f"missing TASK.md: {baseline}")
        if not any(candidate.iterdir()) or not any(reference.iterdir()):
            raise ValueError(f"candidate/reference overlay is empty: {fixture['id']}")


def overlay_tree(source: Path, destination: Path) -> None:
    delete_manifest = source / ".delete"
    if delete_manifest.is_file():
        destination_root = destination.resolve()
        for line in delete_manifest.read_text(encoding="utf-8").splitlines():
            relative_text = line.strip()
            if not relative_text or relative_text.startswith("#"):
                continue
            relative = Path(relative_text)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"unsafe overlay delete path: {relative_text}")
            target = (destination / relative).resolve()
            if target.parent != destination_root and destination_root not in target.parents:
                raise ValueError(f"overlay delete escaped destination: {relative_text}")
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
        timeout=30,
    )
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")


def materialize(task_id: str, destination: Path, *, state: str = "candidate") -> Path:
    if state not in {"baseline", "candidate", "reference"}:
        raise ValueError(f"unsupported task state: {state}")
    baseline, candidate, reference = task_dirs(task_id)
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination}")
    shutil.copytree(baseline, destination)
    _git(destination, "init", "-q")
    _git(destination, "config", "user.email", "phase-b@example.invalid")
    _git(destination, "config", "user.name", "Phase B Fixture")
    _git(destination, "add", "--all")
    _git(destination, "commit", "-q", "-m", "baseline")
    if state == "candidate":
        overlay_tree(candidate, destination)
    elif state == "reference":
        overlay_tree(candidate, destination)
        overlay_tree(reference, destination)
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--state", choices=("baseline", "candidate", "reference"), default="candidate")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    spec = load_spec()
    validate_assets(spec)
    known = {fixture["id"] for fixture in spec["fixtures"]}
    if args.task_id not in known:
        raise SystemExit(f"unknown task: {args.task_id}")
    print(materialize(args.task_id, args.destination, state=args.state))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
