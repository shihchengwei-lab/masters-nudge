#!/usr/bin/env python3
"""Hidden, deterministic graders for the Phase B impact tasks."""

from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import threading
import time
from decimal import Decimal
from pathlib import Path
from typing import Callable


def component(name: str, check: Callable[[], None]) -> dict:
    try:
        check()
        return {"name": name, "passed": True, "detail": ""}
    except Exception as exc:  # grader must retain all component outcomes
        return {"name": name, "passed": False, "detail": f"{type(exc).__name__}: {exc}"}


def assert_equal(expected, actual) -> None:
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def import_workspace(workspace: Path, module_name: str):
    sys.path.insert(0, str(workspace))
    importlib.invalidate_caches()
    sys.modules.pop(module_name, None)
    return importlib.import_module(module_name)


def public_tests(workspace: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "-v"],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=45,
    )
    if result.returncode:
        tail = (result.stdout + "\n" + result.stderr)[-1200:]
        raise AssertionError(f"public tests failed:\n{tail}")


def grade_ownership(workspace: Path) -> list[dict]:
    roles = import_workspace(workspace, "roles")

    def billing_write_visible() -> None:
        roles.reset_state()
        roles.set_billing_role("acme", "u1", "admin")
        assert_equal("admin", roles.get_gateway_role("acme", "u1"))
        assert_equal("admin", roles.get_billing_role("acme", "u1"))

    def latest_write_wins() -> None:
        roles.reset_state()
        roles.set_gateway_role("acme", "u1", "viewer")
        roles.set_billing_role("acme", "u1", "editor")
        assert_equal("editor", roles.get_gateway_role("acme", "u1"))
        assert_equal("editor", roles.get_billing_role("acme", "u1"))
        roles.set_gateway_role("acme", "u1", "admin")
        assert_equal("admin", roles.get_gateway_role("acme", "u1"))
        assert_equal("admin", roles.get_billing_role("acme", "u1"))

    def invalid_is_atomic() -> None:
        roles.reset_state()
        roles.set_billing_role("acme", "u1", "viewer")
        try:
            roles.set_gateway_role("acme", "u1", "owner")
        except ValueError:
            pass
        else:
            raise AssertionError("invalid role did not raise ValueError")
        assert_equal("viewer", roles.get_gateway_role("acme", "u1"))
        assert_equal("viewer", roles.get_billing_role("acme", "u1"))

    def reconcile_is_not_required() -> None:
        roles.reset_state()
        roles.set_billing_role("acme", "u2", "editor")
        roles.reconcile_roles()
        assert_equal("editor", roles.get_gateway_role("acme", "u2"))
        assert_equal("editor", roles.get_billing_role("acme", "u2"))

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("billing_write_visible_to_both", billing_write_visible),
        component("latest_successful_write_wins", latest_write_wins),
        component("invalid_write_is_atomic", invalid_is_atomic),
        component("reconcile_not_required_for_correctness", reconcile_is_not_required),
    ]


def grade_onboarding(workspace: Path) -> list[dict]:
    onboarding = import_workspace(workspace, "onboarding")

    def documented_formats() -> None:
        cases = {
            "0912-345-678": "0912345678",
            "0912 345 678": "0912345678",
            "０９１２３４５６７８": "0912345678",
        }
        for value, expected in cases.items():
            assert_equal(expected, onboarding.normalize_phone(value))

    def invalid_inputs() -> None:
        for value in ("0912ABC678", "091234567", "09123456789"):
            try:
                onboarding.normalize_phone(value)
            except ValueError:
                continue
            raise AssertionError(f"invalid phone {value!r} was accepted")

    def no_unneeded_reminder_mechanism() -> None:
        if (workspace / "reminder_service.py").exists():
            raise AssertionError("unrequested reminder service remains in the candidate")

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("documented_phone_formats_normalized", documented_formats),
        component("invalid_phone_inputs_rejected", invalid_inputs),
        component("unneeded_reminder_mechanism_removed", no_unneeded_reminder_mechanism),
    ]


def grade_csv(workspace: Path) -> list[dict]:
    exports = import_workspace(workspace, "exports")

    def invalid_delimiters() -> None:
        for delimiter in ("", "||"):
            try:
                exports.export_csv([{"a": 1}], delimiter=delimiter)
            except ValueError:
                continue
            raise AssertionError(f"delimiter {delimiter!r} was accepted")

    def json_compatibility() -> None:
        rows = [{"name": "林", "note": None, "nested": {"b": 2, "a": 1}}]
        expected = json.dumps(
            rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        assert_equal(expected, exports.export_json(rows))

    def empty_csv() -> None:
        assert_equal("", exports.export_csv([], delimiter=";"))

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("invalid_delimiters_rejected", invalid_delimiters),
        component("json_byte_compatibility", json_compatibility),
        component("empty_csv_compatibility", empty_csv),
    ]


def grade_discount(workspace: Path) -> list[dict]:
    checkout = import_workspace(workspace, "checkout")
    invoice = import_workspace(workspace, "invoice")
    quote = import_workspace(workspace, "quote")

    def all_student_paths() -> None:
        assert_equal(Decimal("84.99"), checkout.checkout_total("99.99", True))
        assert_equal(Decimal("84.99"), invoice.invoice_total("99.99", "student"))
        assert_equal(Decimal("84.99"), quote.quote_total("99.99", {"student"}))

    def non_students_unchanged() -> None:
        assert_equal(Decimal("99.99"), checkout.checkout_total("99.99", False))
        assert_equal(Decimal("99.99"), invoice.invoice_total("99.99", "staff"))
        assert_equal(Decimal("99.99"), quote.quote_total("99.99", {"vip"}))

    def one_policy_home() -> None:
        core = [path for path in workspace.glob("*.py") if not path.name.startswith("test_")]
        texts = [path.read_text(encoding="utf-8") for path in core]
        old_count = sum(text.count("0.10") for text in texts)
        new_count = sum(text.count("0.15") for text in texts)
        if old_count:
            raise AssertionError(f"old policy remains in {old_count} place(s)")
        if new_count > 1:
            raise AssertionError(f"new policy duplicated in {new_count} places")

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("all_student_paths_use_fifteen_percent", all_student_paths),
        component("non_students_unchanged", non_students_unchanged),
        component("single_policy_definition", one_policy_home),
    ]


def grade_install(workspace: Path) -> list[dict]:
    installer = import_workspace(workspace, "installer")

    def clean_install_executes() -> None:
        with tempfile.TemporaryDirectory(prefix="phase b install ") as install_raw:
            with tempfile.TemporaryDirectory(prefix="phase-b-cwd-") as cwd_raw:
                installed = Path(installer.install(Path(install_raw)))
                result = subprocess.run(
                    [sys.executable, str(installed), "greet", "Ada"],
                    cwd=cwd_raw,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=20,
                )
                assert_equal(0, result.returncode)
                assert_equal("Hello, Ada!\n", result.stdout)

    def runtime_asset_is_installed() -> None:
        with tempfile.TemporaryDirectory(prefix="phase b assets ") as raw:
            installed = Path(installer.install(Path(raw)))
            if not installed.with_name("defaults.json").is_file():
                raise AssertionError("defaults.json was not installed beside the script")

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("clean_install_runs_from_unrelated_cwd", clean_install_executes),
        component("runtime_asset_is_self_contained", runtime_asset_is_installed),
    ]


def grade_ordering(workspace: Path) -> list[dict]:
    module = import_workspace(workspace, "search_controller")

    def forced_out_of_order() -> None:
        rendered = []
        a_started = threading.Event()
        release_a = threading.Event()

        def fetch_a(query):
            a_started.set()
            if not release_a.wait(timeout=3):
                raise RuntimeError("grader did not release A")
            return "old"

        controller = module.SearchController(
            lambda query, result: rendered.append((query, result)),
            debounce_seconds=0,
        )
        first = controller.submit("A", fetch_a)
        if not a_started.wait(timeout=3):
            raise AssertionError("A did not start")
        second = controller.submit("B", lambda query: "new")
        second.join(timeout=3)
        release_a.set()
        first.join(timeout=3)
        if first.is_alive() or second.is_alive():
            raise AssertionError("worker thread did not finish")
        assert_equal([("B", "new")], rendered)

    def controllers_are_independent() -> None:
        left = []
        right = []
        one = module.SearchController(lambda q, r: left.append((q, r)), debounce_seconds=0)
        two = module.SearchController(lambda q, r: right.append((q, r)), debounce_seconds=0)
        a = one.submit("L", lambda q: "left")
        b = two.submit("R", lambda q: "right")
        a.join(timeout=3)
        b.join(timeout=3)
        assert_equal([("L", "left")], left)
        assert_equal([("R", "right")], right)

    def no_sleep_based_ordering() -> None:
        source = (workspace / "search_controller.py").read_text(encoding="utf-8")
        if "time.sleep" in source:
            raise AssertionError("ordering still depends on time.sleep")

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("forced_out_of_order_latest_wins", forced_out_of_order),
        component("controller_instances_are_independent", controllers_are_independent),
        component("ordering_does_not_use_sleep", no_sleep_based_ordering),
    ]


def grade_cold_start(workspace: Path) -> list[dict]:
    script = workspace / "report_cli.py"

    def version_output() -> None:
        result = subprocess.run(
            [sys.executable, str(script), "--version"],
            cwd=workspace.parent,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
        )
        assert_equal(0, result.returncode)
        assert_equal("report-cli 1.0\n", result.stdout)

    def cold_p95() -> None:
        durations = []
        for _ in range(5):
            started = time.perf_counter()
            result = subprocess.run(
                [sys.executable, str(script), "--version"],
                cwd=workspace.parent,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )
            durations.append(time.perf_counter() - started)
            if result.returncode or result.stdout != "report-cli 1.0\n":
                raise AssertionError("cold process output changed")
        ordered = sorted(durations)
        index = max(0, math.ceil(0.95 * len(ordered)) - 1)
        p95 = ordered[index]
        if p95 >= 0.180:
            raise AssertionError(f"cold p95 {p95 * 1000:.1f}ms is not below 180ms")

    def details_output() -> None:
        result = subprocess.run(
            [sys.executable, str(script), "--details", "alpha"],
            cwd=workspace.parent,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
        )
        assert_equal(0, result.returncode)
        assert_equal("alpha:5\n", result.stdout)

    return [
        component("public_tests", lambda: public_tests(workspace)),
        component("version_output_equivalent", version_output),
        component("cold_process_p95_below_180ms", cold_p95),
        component("details_behavior_preserved", details_output),
    ]


GRADERS = {
    "ownership-role-store": grade_ownership,
    "onboarding-problem-location": grade_onboarding,
    "csv-scope-control": grade_csv,
    "discount-policy-home": grade_discount,
    "clean-install-proof": grade_install,
    "last-query-wins": grade_ordering,
    "cold-start-cli": grade_cold_start,
}


def grade(task_id: str, workspace: Path) -> dict:
    grader = GRADERS.get(task_id)
    if grader is None:
        raise ValueError(f"unknown task: {task_id}")
    workspace = workspace.resolve()
    if not workspace.is_dir():
        raise ValueError(f"workspace is not a directory: {workspace}")
    components = grader(workspace)
    return {
        "task_id": task_id,
        "passed": all(item["passed"] for item in components),
        "components_passed": sum(item["passed"] for item in components),
        "components_total": len(components),
        "components": components,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id", choices=sorted(GRADERS))
    parser.add_argument("workspace", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(json.dumps(grade(args.task_id, args.workspace), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
