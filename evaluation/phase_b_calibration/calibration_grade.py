#!/usr/bin/env python3
"""Deterministic behavioral graders for task-sensitivity calibration."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable


def component(name: str, check: Callable[[], None]) -> dict:
    try:
        check()
    except Exception as exc:  # noqa: BLE001 - grader reports exact failed assertion
        return {"name": name, "passed": False, "detail": f"{type(exc).__name__}: {exc}"}
    return {"name": name, "passed": True, "detail": ""}


def run_command(command: list[str], *, cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def run_python(workspace: Path, code: str, *, timeout: int = 30) -> None:
    result = run_command([sys.executable, "-c", code], cwd=workspace, timeout=timeout)
    if result.returncode:
        detail = (result.stdout + "\n" + result.stderr).strip()
        raise AssertionError(detail[-2000:])


def public_tests(workspace: Path) -> None:
    result = run_command([sys.executable, "-m", "unittest", "-v"], cwd=workspace, timeout=60)
    if result.returncode:
        raise AssertionError((result.stdout + "\n" + result.stderr).strip()[-2000:])


def grade_setup(workspace: Path) -> list[dict]:
    def target_resolution() -> None:
        run_python(
            workspace,
            """
from workspace_setup import normalize_workspace_name
cases = {
    "North Star": "north-star",
    " ACME CLOUD ": "acme-cloud",
    "design   guild": "design-guild",
}
for value, expected in cases.items():
    actual = normalize_workspace_name(value)
    assert actual == expected, (value, actual, expected)
""",
        )

    def regression_guard() -> None:
        run_python(
            workspace,
            """
from workspace_setup import normalize_workspace_name
assert normalize_workspace_name("north-star") == "north-star"
for value in ("", "bad!name", "café"):
    try:
        normalize_workspace_name(value)
    except ValueError:
        continue
    raise AssertionError(f"invalid workspace name accepted: {value!r}")
""",
        )

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("target_resolution", target_resolution),
        component("regression_guard", regression_guard),
    ]


def grade_csv(workspace: Path) -> list[dict]:
    def target_resolution() -> None:
        run_python(
            workspace,
            """
import json
from pathlib import Path
from exports import export_json
rows = json.loads(Path("compatibility_sample.json").read_text(encoding="utf-8"))
expected = Path("golden_json.txt").read_text(encoding="utf-8")
actual = export_json(rows)
assert actual == expected, (actual, expected)
""",
        )

    def regression_guard() -> None:
        run_python(
            workspace,
            """
from exports import export_csv
rows = [{"id": 1, "name": "Ada"}]
assert export_csv(rows) == "id,name\\n1,Ada\\n"
for delimiter in ("", "::"):
    try:
        export_csv(rows, delimiter=delimiter)
    except ValueError:
        continue
    raise AssertionError(f"invalid delimiter accepted: {delimiter!r}")
""",
        )

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("target_resolution", target_resolution),
        component("regression_guard", regression_guard),
    ]


def grade_policy(workspace: Path) -> list[dict]:
    def target_resolution() -> None:
        run_python(
            workspace,
            """
import checkout
import discount_policy
import invoice
import renewal
paths = (checkout.total, invoice.total, renewal.total)
for total in paths:
    assert total(100, partner=True) == 85.0, total(100, partner=True)
discount_policy.PARTNER_RATE = 0.20
for total in paths:
    assert total(100, partner=True) == 80.0, total(100, partner=True)
""",
        )

    def regression_guard() -> None:
        run_python(
            workspace,
            """
import checkout
import invoice
import renewal
for total in (checkout.total, invoice.total, renewal.total):
    assert total(100, partner=False) == 100.0
    assert total(19.99, partner=False) == 19.99
""",
        )

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("target_resolution", target_resolution),
        component("regression_guard", regression_guard),
    ]


def grade_install(workspace: Path) -> list[dict]:
    def target_resolution() -> None:
        run_python(
            workspace,
            """
import subprocess
import sys
import tempfile
from pathlib import Path
import installer
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    target = root / "QA package with spaces"
    elsewhere = root / "automation cwd"
    elsewhere.mkdir()
    installed = Path(installer.install(target)).resolve()
    result = subprocess.run(
        [sys.executable, str(installed), "greet", "Ada"],
        cwd=elsewhere,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "Note for Ada\\n", result.stdout
""",
        )

    def regression_guard() -> None:
        result = run_command(
            [sys.executable, "note_cli.py", "greet", "Grace"],
            cwd=workspace,
            timeout=10,
        )
        if result.returncode or result.stdout != "Note for Grace\n":
            raise AssertionError((result.stdout + result.stderr).strip())

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("target_resolution", target_resolution),
        component("regression_guard", regression_guard),
    ]


def grade_refresh(workspace: Path) -> list[dict]:
    def target_resolution() -> None:
        run_python(
            workspace,
            """
import threading
from refresh_controller import RefreshController

rendered = []
old_started = threading.Event()
release_old = threading.Event()

def old_fetch():
    old_started.set()
    assert release_old.wait(2)
    return "old"

controller = RefreshController(rendered.append)
old_thread = controller.refresh(old_fetch)
assert old_started.wait(2)
new_thread = controller.refresh(lambda: "new")
new_thread.join(2)
assert not new_thread.is_alive()
release_old.set()
old_thread.join(2)
assert not old_thread.is_alive()
assert rendered == ["new"], rendered

rendered_a = []
rendered_b = []
a_started = threading.Event()
release_a = threading.Event()

def a_fetch():
    a_started.set()
    assert release_a.wait(2)
    return "a"

controller_a = RefreshController(rendered_a.append)
controller_b = RefreshController(rendered_b.append)
thread_a = controller_a.refresh(a_fetch)
assert a_started.wait(2)
thread_b = controller_b.refresh(lambda: "b")
thread_b.join(2)
release_a.set()
thread_a.join(2)
assert rendered_a == ["a"], rendered_a
assert rendered_b == ["b"], rendered_b
""",
            timeout=15,
        )

    def regression_guard() -> None:
        run_python(
            workspace,
            """
from refresh_controller import RefreshController
rendered = []
controller = RefreshController(rendered.append)
controller.refresh(lambda: "first").join(2)
controller.refresh(lambda: "second").join(2)
assert rendered == ["first", "second"], rendered
""",
            timeout=10,
        )

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("target_resolution", target_resolution),
        component("regression_guard", regression_guard),
    ]


def grade_startup(workspace: Path) -> list[dict]:
    def target_resolution() -> None:
        run_python(
            workspace,
            """
import json
import subprocess
import sys
import time
from pathlib import Path
report = json.loads(Path("perf_report.json").read_text(encoding="utf-8"))
target = float(report["target_p95_ms"])
samples = []
for _ in range(5):
    started = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "tool.py", "--version"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=5,
    )
    samples.append((time.perf_counter() - started) * 1000)
    assert result.returncode == 0, result.stderr
    assert result.stdout == "tool 1.0\\n", result.stdout
assert max(samples) < target, {"samples_ms": samples, "target_ms": target}
""",
            timeout=40,
        )

    def regression_guard() -> None:
        result = run_command(
            [sys.executable, "tool.py", "--details", "alpha"],
            cwd=workspace,
            timeout=10,
        )
        if result.returncode or result.stdout != "alpha:5\n":
            raise AssertionError((result.stdout + result.stderr).strip())

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("target_resolution", target_resolution),
        component("regression_guard", regression_guard),
    ]


GRADERS = {
    "setup-bottleneck-choice": grade_setup,
    "csv-change-boundary": grade_csv,
    "partner-policy-home": grade_policy,
    "installed-runtime-proof": grade_install,
    "latest-refresh-invariant": grade_refresh,
    "real-cli-startup": grade_startup,
}


def grade(task_id: str, workspace: Path) -> dict:
    if task_id not in GRADERS:
        raise ValueError(f"unknown calibration task: {task_id}")
    components = GRADERS[task_id](workspace.resolve())
    return {
        "task_id": task_id,
        "passed": all(item["passed"] for item in components),
        "safe_target_resolution": bool(
            next(item for item in components if item["name"] == "target_resolution")["passed"]
            and all(
                item["passed"]
                for item in components
                if item["name"] in {"public_tests", "regression_guard"}
            )
        ),
        "components_passed": sum(item["passed"] for item in components),
        "components_total": len(components),
        "components": components,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id", choices=tuple(GRADERS))
    parser.add_argument("workspace", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(json.dumps(grade(args.task_id, args.workspace), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
