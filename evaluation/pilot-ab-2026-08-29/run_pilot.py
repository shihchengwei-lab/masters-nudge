from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any

import pyarrow.parquet as pq


HERE = Path(__file__).resolve().parent
CONTRACT_PATH = HERE / "contract.json"
DEFAULT_PARQUET = Path(os.environ.get(
    "SWE_BENCH_PARQUET",
    r"C:\Users\kk789\AppData\Local\Temp\masters-nudge-swebench-sphinx-9229-b91bf7fe\swe-bench-verified.parquet",
))
DEFAULT_WORK_ROOT = Path(os.environ.get(
    "MASTERS_NUDGE_AB_WORK_ROOT",
    r"C:\Users\kk789\AppData\Local\Temp\masters-nudge-pilot-ab-20260829",
))
DEFAULT_REPO_ROOT = HERE.parents[1]
CODEX_MODEL = "gpt-5.6-sol"
REASONING_EFFORT = "medium"
RUN_TIMEOUT_SECONDS = 1800
TEST_TIMEOUT_SECONDS = 900


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def command_text(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        env=merged_env,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def require_success(result: subprocess.CompletedProcess[bytes], label: str) -> None:
    if result.returncode != 0:
        output = result.stdout.decode("utf-8", errors="replace")[-8000:]
        raise RuntimeError(f"{label} failed ({result.returncode})\n{output}")


def git(*args: str, cwd: Path | None = None, timeout: int = 600) -> subprocess.CompletedProcess[bytes]:
    return run_command(
        ["git", "-c", "core.autocrlf=false", *args],
        cwd=cwd,
        timeout=timeout,
    )


def read_dataset(parquet_path: Path) -> dict[str, dict[str, Any]]:
    rows = pq.read_table(parquet_path).to_pylist()
    return {str(row["instance_id"]): row for row in rows}


def task_rows(contract: dict[str, Any], dataset: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for configured in contract["provisional_tasks"]:
        row = dict(dataset[configured["instance_id"]])
        row.update(configured)
        row["FAIL_TO_PASS"] = json.loads(row["FAIL_TO_PASS"])
        row["PASS_TO_PASS"] = json.loads(row["PASS_TO_PASS"])
        rows.append(row)
    return rows


def mirror_path(work_root: Path, repo: str) -> Path:
    return work_root / "mirrors" / f"{repo.replace('/', '__')}.git"


def ensure_mirror(work_root: Path, repo: str, base_commit: str) -> Path:
    mirror = mirror_path(work_root, repo)
    if not mirror.exists():
        mirror.parent.mkdir(parents=True, exist_ok=True)
        print(f"[prepare] cloning mirror {repo}", flush=True)
        result = git(
            "clone",
            "--mirror",
            "--filter=blob:none",
            f"https://github.com/{repo}.git",
            str(mirror),
            timeout=1800,
        )
        require_success(result, f"clone mirror {repo}")
    present = git("--git-dir", str(mirror), "cat-file", "-e", f"{base_commit}^{{commit}}")
    if present.returncode != 0:
        print(f"[prepare] fetching {repo}@{base_commit[:10]}", flush=True)
        fetched = git(
            "--git-dir",
            str(mirror),
            "fetch",
            "--filter=blob:none",
            "origin",
            base_commit,
            timeout=1800,
        )
        require_success(fetched, f"fetch {repo}@{base_commit}")
    return mirror


def configure_checkout(path: Path) -> None:
    require_success(git("config", "core.autocrlf", "false", cwd=path), "configure checkout")
    exclude = path / ".git" / "info" / "exclude"
    with exclude.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write("\n.venv/\n__pycache__/\n.pytest_cache/\n.tox/\nbuild/\ndist/\n")


def clone_checkout(source: Path, destination: Path, base_commit: str) -> None:
    if destination.exists():
        current = git("rev-parse", "HEAD", cwd=destination)
        if (
            current.returncode == 0
            and current.stdout.decode("utf-8", errors="replace").strip() == base_commit
        ):
            return
        raise RuntimeError(f"invalid existing checkout: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    result = git("clone", "--no-hardlinks", "--quiet", str(source), str(destination), timeout=1800)
    require_success(result, f"clone checkout {destination.name}")
    configure_checkout(destination)
    checkout = git("checkout", "--detach", base_commit, cwd=destination, timeout=1800)
    require_success(checkout, f"checkout {base_commit}")


def clone_remote_base(task: dict[str, Any], destination: Path) -> None:
    if destination.exists():
        current = git("rev-parse", "HEAD", cwd=destination)
        if (
            current.returncode == 0
            and current.stdout.decode("utf-8", errors="replace").strip() == task["base_commit"]
        ):
            return
        raise RuntimeError(f"invalid existing base checkout: {destination}")
    destination.mkdir(parents=True, exist_ok=False)
    require_success(git("init", "--quiet", cwd=destination), "initialize base checkout")
    require_success(
        git(
            "remote",
            "add",
            "origin",
            f"https://github.com/{task['repo']}.git",
            cwd=destination,
        ),
        "configure upstream remote",
    )
    fetched = git(
        "fetch",
        "--depth",
        "1",
        "--filter=blob:none",
        "origin",
        task["base_commit"],
        cwd=destination,
        timeout=1800,
    )
    require_success(fetched, f"fetch {task['instance_id']}")
    checked_out = git(
        "checkout",
        "--detach",
        task["base_commit"],
        cwd=destination,
        timeout=1800,
    )
    require_success(checked_out, f"checkout {task['base_commit']}")
    configure_checkout(destination)


def python_version(task: dict[str, Any]) -> str:
    repo = task["repo"]
    version = str(task["version"])
    if repo == "pytest-dev/pytest" and version.startswith("5."):
        return "3.8"
    if repo == "django/django" and version.startswith("4."):
        return "3.10"
    if repo == "sympy/sympy" and version.startswith("1.12"):
        return "3.11"
    return "3.9"


def venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def setup_environment(task: dict[str, Any], base: Path, env_dir: Path) -> Path:
    python = venv_python(env_dir)
    if python.exists():
        return python
    env_dir.parent.mkdir(parents=True, exist_ok=True)
    print(f"[prepare] creating Python {python_version(task)} env for {task['instance_id']}", flush=True)
    created = run_command(
        ["uv", "venv", str(env_dir), "--python", python_version(task)],
        timeout=1800,
    )
    require_success(created, f"create venv for {task['instance_id']}")
    repo = task["repo"]
    if repo == "django/django":
        packages = ["-e", str(base), "tblib"]
    elif repo == "pytest-dev/pytest":
        packages = ["-e", f"{base}[testing]"]
    elif repo == "sphinx-doc/sphinx":
        packages = [
            "setuptools<81",
            "jinja2<3.1",
            "roman",
            "alabaster==0.7.12",
            # Sphinx 4.x declared these without upper bounds. Current 2.x
            # releases require Sphinx >= 5 and make this historical checkout
            # fail before the target regression test can run.
            "sphinxcontrib-applehelp==1.0.4",
            "sphinxcontrib-devhelp==1.0.2",
            "sphinxcontrib-htmlhelp==2.0.0",
            "sphinxcontrib-qthelp==1.0.3",
            "sphinxcontrib-serializinghtml==1.1.5",
            "-e",
            f"{base}[test]",
        ]
    elif repo == "sympy/sympy":
        packages = ["-e", str(base), "pytest"]
    else:
        raise ValueError(f"unsupported repo: {repo}")
    install_env: dict[str, str] = {}
    if repo == "pytest-dev/pytest":
        normalized_version = str(task["version"])
        if normalized_version.count(".") == 1:
            normalized_version += ".0"
        install_env = {
            "SETUPTOOLS_SCM_PRETEND_VERSION": normalized_version,
            "SETUPTOOLS_SCM_PRETEND_VERSION_FOR_PYTEST": normalized_version,
        }
    installed = run_command(
        ["uv", "pip", "install", "--python", str(python), *packages],
        env=install_env,
        timeout=1800,
    )
    require_success(installed, f"install dependencies for {task['instance_id']}")
    return python


def patch_paths(test_patch: str) -> list[str]:
    paths: list[str] = []
    for match in re.finditer(r"^\+\+\+ b/(.+)$", test_patch, flags=re.MULTILINE):
        path = match.group(1).strip()
        if path.endswith(".py") and path not in paths:
            paths.append(path)
    return paths


def django_label(path: str) -> str:
    relative = Path(path).as_posix()
    if relative.startswith("tests/"):
        relative = relative[len("tests/"):]
    parts = relative.removesuffix(".py").split("/")
    if parts[-1] in {"tests", "test"}:
        parts = parts[:-1]
    return ".".join(parts)


def score_command(task: dict[str, Any], python: Path) -> list[str]:
    paths = patch_paths(str(task["test_patch"]))
    if not paths:
        raise RuntimeError(f"no Python test paths in test patch for {task['instance_id']}")
    if task["repo"] == "django/django":
        labels = list(dict.fromkeys(django_label(path) for path in paths))
        return [str(python), "tests/runtests.py", *labels, "--verbosity", "1"]
    return [str(python), "-m", "pytest", *paths, "-q"]


def task_dir(work_root: Path, task: dict[str, Any]) -> Path:
    return work_root / "tasks" / task["task_key"]


def write_task_material(task: dict[str, Any], root: Path) -> None:
    material = {
        key: task[key]
        for key in (
            "task_key",
            "instance_id",
            "repo",
            "base_commit",
            "version",
            "problem_statement",
            "FAIL_TO_PASS",
            "PASS_TO_PASS",
            "order",
        )
    }
    atomic_json(root / "task.json", material)
    (root / "test.patch").write_text(str(task["test_patch"]), encoding="utf-8", newline="\n")


def prepare_task(task: dict[str, Any], work_root: Path) -> dict[str, Any]:
    root = task_dir(work_root, task)
    root.mkdir(parents=True, exist_ok=True)
    write_task_material(task, root)
    base = root / "base"
    clone_remote_base(task, base)
    python = setup_environment(task, base, root / "venv")
    command = score_command(task, python)
    result = {
        "status": "prepared",
        "python": str(python),
        "score_command": command,
        "score_command_text": command_text(command),
    }
    atomic_json(root / "prepare.json", result)
    return result


def prepare_runtime_checkout(task: dict[str, Any], checkout: Path, base: Path) -> None:
    if task["repo"] != "pytest-dev/pytest":
        return
    generated_version = base / "src" / "_pytest" / "_version.py"
    destination = checkout / "src" / "_pytest" / "_version.py"
    if not generated_version.exists():
        raise RuntimeError(f"pytest generated version is missing: {generated_version}")
    shutil.copy2(generated_version, destination)


def test_environment(task: dict[str, Any], checkout: Path) -> dict[str, str]:
    python_path = checkout / "src" if task["repo"] == "pytest-dev/pytest" else checkout
    return {
        "PYTHONPATH": str(python_path),
        "PYTHONUTF8": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def preflight_task(task: dict[str, Any], work_root: Path) -> dict[str, Any]:
    root = task_dir(work_root, task)
    prepared = load_json(root / "prepare.json")
    checkout = root / "baseline-with-tests-v4"
    clone_checkout(root / "base", checkout, task["base_commit"])
    prepare_runtime_checkout(task, checkout, root / "base")
    patch = (root / "test.patch").read_bytes()
    applied = run_command(["git", "apply", "--whitespace=nowarn", "-"], cwd=checkout, input_bytes=patch)
    if applied.returncode != 0:
        result = {
            "status": "excluded",
            "reason": "test_patch_apply_failed",
            "output": applied.stdout.decode("utf-8", errors="replace")[-8000:],
        }
        atomic_json(root / "preflight.json", result)
        return result
    started = time.monotonic()
    try:
        tested = run_command(
            list(prepared["score_command"]),
            cwd=checkout,
            env=test_environment(task, checkout),
            timeout=TEST_TIMEOUT_SECONDS,
        )
        timed_out = False
        output = tested.stdout.decode("utf-8", errors="replace")
        returncode = tested.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        output = (exc.stdout or b"").decode("utf-8", errors="replace")
        returncode = None
    wall = round(time.monotonic() - started, 3)
    infrastructure_markers = (
        "ERROR collecting",
        "ModuleNotFoundError",
        "ImportError while importing test module",
        "no tests ran",
        "Ran 0 tests",
    )
    failure_markers = ("FAILED", "FAIL:", "AssertionError", "failures=", "errors=")
    valid = (
        not timed_out
        and returncode not in (None, 0)
        and any(marker in output for marker in failure_markers)
        and not any(marker in output for marker in infrastructure_markers)
    )
    result = {
        "status": "eligible" if valid else "excluded",
        "reason": "baseline_failure_reproduced" if valid else "baseline_not_reproduced_cleanly",
        "returncode": returncode,
        "timed_out": timed_out,
        "wall_time_seconds": wall,
        "output_tail": output[-12000:],
    }
    atomic_json(root / "preflight.json", result)
    return result


def frozen_plugin(work_root: Path, repo_root: Path) -> Path:
    target = work_root / "frozen-plugin"
    if not target.exists():
        shutil.copytree(repo_root / "plugins" / "masters-nudge", target)
    return target


def copy_auth(codex_home: Path) -> None:
    codex_home.mkdir(parents=True, exist_ok=True)
    source = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "auth.json"
    if not source.exists():
        raise RuntimeError(f"Codex auth file not found: {source}")
    shutil.copy2(source, codex_home / "auth.json")


def build_prompt(task: dict[str, Any], python: Path, score_text: str) -> str:
    return (
        "You are solving one SWE-bench Verified task in the checked-out repository.\n\n"
        f"Instance: {task['instance_id']}\n"
        f"Base commit: {task['base_commit']}\n\n"
        "Work only from the checked-out repository and the problem statement below.\n"
        "Do not inspect parent directories, external benchmark traces, gold patches, or hidden tests.\n"
        "Diagnose the issue, implement the smallest correct fix, and run focused tests.\n"
        "Do not stop at an explanation: leave the working tree with the proposed fix.\n"
        f"A prepared Python interpreter is available at: {python}\n"
        f"A broad relevant test command is: {score_text}\n"
        "The evaluator may add held-out regression tests after your turn.\n\n"
        "Problem statement:\n\n"
        f"{task['problem_statement']}\n"
    )


def codex_executable() -> str:
    located = shutil.which("codex.cmd") or shutil.which("codex")
    if not located:
        raise RuntimeError("codex executable not found")
    return located


def run_with_heartbeat(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    prompt: bytes,
    trace_path: Path,
    timeout: int,
    label: str,
) -> tuple[int | None, float, bool]:
    started = time.monotonic()
    timed_out = False
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("wb") as trace:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=env,
            stdin=subprocess.PIPE,
            stdout=trace,
            stderr=subprocess.STDOUT,
        )
        assert process.stdin is not None
        process.stdin.write(prompt)
        process.stdin.close()
        last_reported = -30
        while process.poll() is None:
            elapsed = time.monotonic() - started
            if elapsed > timeout:
                timed_out = True
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=False,
                    )
                else:
                    process.kill()
                break
            if elapsed - last_reported >= 30:
                print(f"[{label}] running {int(elapsed)}s", flush=True)
                last_reported = elapsed
            time.sleep(5)
        try:
            returncode = process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            returncode = None
    return returncode, round(time.monotonic() - started, 3), timed_out


def trace_usage(trace_path: Path) -> dict[str, int]:
    usage: dict[str, int] = {}
    if not trace_path.exists():
        return usage
    for line in trace_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = {str(key): int(value) for key, value in event["usage"].items()}
    return usage


def run_arm(task: dict[str, Any], arm: str, work_root: Path, repo_root: Path) -> dict[str, Any]:
    root = task_dir(work_root, task)
    run_root = root / "runs" / arm.lower()
    result_path = run_root / "run.json"
    if result_path.exists():
        return load_json(result_path)
    prepared = load_json(root / "prepare.json")
    checkout = run_root / "checkout"
    clone_checkout(root / "base", checkout, task["base_commit"])
    prepare_runtime_checkout(task, checkout, root / "base")
    codex_home = run_root / "codex-home"
    copy_auth(codex_home)
    plugin = frozen_plugin(work_root, repo_root)
    if arm == "B":
        shutil.copy2(plugin / "hooks" / "hooks.json", codex_home / "hooks.json")
    nudge_data = run_root / "nudge-data"
    prompt_text = build_prompt(
        task,
        Path(prepared["python"]),
        str(prepared["score_command_text"]),
    )
    (run_root / "prompt.txt").write_text(prompt_text, encoding="utf-8", newline="\n")
    trace = run_root / "codex-events.jsonl"
    last_message = run_root / "last-message.txt"
    command = [
        codex_executable(),
        "exec",
        "-m",
        CODEX_MODEL,
        "-c",
        f'model_reasoning_effort="{REASONING_EFFORT}"',
        "--dangerously-bypass-approvals-and-sandbox",
        "--dangerously-bypass-hook-trust",
        "--json",
        "--color",
        "never",
        "-o",
        str(last_message),
        "-C",
        str(checkout),
        "-",
    ]
    env = os.environ.copy()
    env.update({
        "CODEX_HOME": str(codex_home),
        "PLUGIN_ROOT": str(plugin),
        "MASTERS_NUDGE_DATA_DIR": str(nudge_data),
        "MASTERS_NUDGE_PROVIDER": "openai",
        "MASTERS_NUDGE_MODEL": "gpt-5.6-sol",
        "MASTERS_NUDGE_STAGE": "automatic",
        "MASTERS_NUDGE_TIMEOUT": "90",
        "PYTHONPATH": str(
            checkout / "src" if task["repo"] == "pytest-dev/pytest" else checkout
        ),
        "PYTHONUTF8": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    label = f"{task['task_key']}-{arm}"
    print(f"[run] starting {label} {task['instance_id']}", flush=True)
    returncode, wall, timed_out = run_with_heartbeat(
        command,
        cwd=checkout,
        env=env,
        prompt=prompt_text.encode("utf-8"),
        trace_path=trace,
        timeout=RUN_TIMEOUT_SECONDS,
        label=label,
    )
    status = git("status", "--short", cwd=checkout)
    result = {
        "status": "completed" if returncode == 0 and not timed_out else "runtime_failure",
        "returncode": returncode,
        "timed_out": timed_out,
        "wall_time_seconds": wall,
        "usage": trace_usage(trace),
        "working_tree": status.stdout.decode("utf-8", errors="replace").splitlines(),
        "trace_sha256": sha256_bytes(trace.read_bytes()) if trace.exists() else None,
    }
    atomic_json(result_path, result)
    print(f"[run] finished {label}: {result['status']} in {wall}s", flush=True)
    return result


def product_patch(checkout: Path, repo: str) -> bytes:
    git("add", "-N", "--", ".", cwd=checkout, timeout=600)
    includes = {
        "django/django": ["django"],
        "pytest-dev/pytest": ["src"],
        "sphinx-doc/sphinx": ["sphinx"],
        "sympy/sympy": ["sympy", ":(exclude,glob)sympy/**/tests/**"],
    }[repo]
    diff = git("diff", "--binary", "--", *includes, cwd=checkout, timeout=600)
    require_success(diff, "collect product diff")
    return diff.stdout


def nudge_summary(nudge_data: Path) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    for log in nudge_data.glob("*.log") if nudge_data.exists() else []:
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("kind") == "review":
                findings.append(record)
            elif record.get("kind") == "delivery_receipt":
                receipts.append(record)
            elif record.get("kind") == "response_observation":
                observations.append(record)
    return {
        "findings": len(findings),
        "injected": sum(1 for row in receipts if row.get("delivery_status") == "injected"),
        "response_observations": len(observations),
        "lenses": [row.get("effective_lens") for row in findings],
        "nudges": [row.get("reaction") for row in findings],
    }


def score_arm(task: dict[str, Any], arm: str, work_root: Path) -> dict[str, Any]:
    root = task_dir(work_root, task)
    run_root = root / "runs" / arm.lower()
    score_path = run_root / "score.json"
    if score_path.exists():
        return load_json(score_path)
    prepared = load_json(root / "prepare.json")
    run_result = load_json(run_root / "run.json")
    evaluator = run_root / "evaluator"
    clone_checkout(root / "base", evaluator, task["base_commit"])
    prepare_runtime_checkout(task, evaluator, root / "base")
    patch = product_patch(run_root / "checkout", task["repo"])
    (run_root / "product.patch").write_bytes(patch)
    if patch:
        applied = run_command(
            ["git", "apply", "--whitespace=nowarn", "-"],
            cwd=evaluator,
            input_bytes=patch,
        )
        if applied.returncode != 0:
            result = {
                "status": "evaluator_error",
                "reason": "product_patch_apply_failed",
                "output_tail": applied.stdout.decode("utf-8", errors="replace")[-8000:],
            }
            atomic_json(score_path, result)
            return result
    test_patch = (root / "test.patch").read_bytes()
    tested_patch = run_command(
        ["git", "apply", "--whitespace=nowarn", "-"],
        cwd=evaluator,
        input_bytes=test_patch,
    )
    if tested_patch.returncode != 0:
        result = {
            "status": "evaluator_error",
            "reason": "test_patch_apply_failed",
            "output_tail": tested_patch.stdout.decode("utf-8", errors="replace")[-8000:],
        }
        atomic_json(score_path, result)
        return result
    started = time.monotonic()
    try:
        tested = run_command(
            list(prepared["score_command"]),
            cwd=evaluator,
            env=test_environment(task, evaluator),
            timeout=TEST_TIMEOUT_SECONDS,
        )
        timed_out = False
        returncode = tested.returncode
        output = tested.stdout.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        output = (exc.stdout or b"").decode("utf-8", errors="replace")
    wall = round(time.monotonic() - started, 3)
    result = {
        "status": "scored",
        "passed": returncode == 0 and not timed_out,
        "returncode": returncode,
        "timed_out": timed_out,
        "wall_time_seconds": wall,
        "product_patch_sha256": sha256_bytes(patch),
        "product_patch_bytes": len(patch),
        "output_tail": output[-16000:],
        "main_run_status": run_result["status"],
    }
    if arm == "B":
        result["nudge"] = nudge_summary(run_root / "nudge-data")
    atomic_json(score_path, result)
    print(f"[score] {task['task_key']}-{arm}: {'pass' if result['passed'] else 'fail'}", flush=True)
    return result


def current_tasks(contract: dict[str, Any], dataset: dict[str, dict[str, Any]], work_root: Path) -> list[dict[str, Any]]:
    return task_rows(contract, dataset)


def phase_prepare(tasks: list[dict[str, Any]], work_root: Path) -> None:
    for task in tasks:
        print(f"[prepare] {task['task_key']} {task['instance_id']}", flush=True)
        try:
            prepare_task(task, work_root)
        except Exception as exc:
            atomic_json(task_dir(work_root, task) / "prepare.json", {
                "status": "excluded",
                "reason": "prepare_failed",
                "error": str(exc),
            })
            print(f"[prepare] excluded {task['instance_id']}: {exc}", flush=True)


def phase_preflight(tasks: list[dict[str, Any]], work_root: Path) -> None:
    for task in tasks:
        prepared_path = task_dir(work_root, task) / "prepare.json"
        if not prepared_path.exists() or load_json(prepared_path).get("status") != "prepared":
            continue
        preflight_path = task_dir(work_root, task) / "preflight.json"
        if preflight_path.exists():
            existing = load_json(preflight_path)
            print(
                f"[preflight] {task['instance_id']}: cached {existing.get('status')}",
                flush=True,
            )
            continue
        print(f"[preflight] {task['task_key']} {task['instance_id']}", flush=True)
        result = preflight_task(task, work_root)
        print(f"[preflight] {task['instance_id']}: {result['status']} ({result['reason']})", flush=True)


def phase_run(tasks: list[dict[str, Any]], work_root: Path, repo_root: Path) -> None:
    for task in tasks:
        preflight = load_json(task_dir(work_root, task) / "preflight.json")
        if preflight.get("status") != "eligible":
            continue
        order = ["A", "B"] if task["order"] == "A_then_B" else ["B", "A"]
        for arm in order:
            run_arm(task, arm, work_root, repo_root)


def phase_score(tasks: list[dict[str, Any]], work_root: Path) -> None:
    for task in tasks:
        preflight = load_json(task_dir(work_root, task) / "preflight.json")
        if preflight.get("status") != "eligible":
            continue
        for arm in ("A", "B"):
            run_path = task_dir(work_root, task) / "runs" / arm.lower() / "run.json"
            if run_path.exists():
                score_arm(task, arm, work_root)


def phase_summarize(tasks: list[dict[str, Any]], work_root: Path) -> None:
    rows: list[dict[str, Any]] = []
    for task in tasks:
        root = task_dir(work_root, task)
        preflight = load_json(root / "preflight.json") if (root / "preflight.json").exists() else None
        row: dict[str, Any] = {
            "task_key": task["task_key"],
            "instance_id": task["instance_id"],
            "repo": task["repo"],
            "order": task["order"],
            "preflight": preflight,
        }
        for arm in ("A", "B"):
            run_path = root / "runs" / arm.lower() / "run.json"
            score_path = root / "runs" / arm.lower() / "score.json"
            row[f"arm_{arm.lower()}"] = {
                "run": load_json(run_path) if run_path.exists() else None,
                "score": load_json(score_path) if score_path.exists() else None,
            }
        rows.append(row)
    eligible = [row for row in rows if row["preflight"] and row["preflight"].get("status") == "eligible"]
    scored = [
        row for row in eligible
        if row["arm_a"]["score"] and row["arm_b"]["score"]
        and row["arm_a"]["score"].get("status") == "scored"
        and row["arm_b"]["score"].get("status") == "scored"
    ]
    summary = {
        "schema_version": 1,
        "work_root": str(work_root),
        "tasks": rows,
        "counts": {
            "preregistered": len(rows),
            "eligible": len(eligible),
            "paired_scored": len(scored),
            "arm_a_passed": sum(bool(row["arm_a"]["score"].get("passed")) for row in scored),
            "arm_b_passed": sum(bool(row["arm_b"]["score"].get("passed")) for row in scored),
            "a_only": sum(
                bool(row["arm_a"]["score"].get("passed"))
                and not bool(row["arm_b"]["score"].get("passed"))
                for row in scored
            ),
            "b_only": sum(
                bool(row["arm_b"]["score"].get("passed"))
                and not bool(row["arm_a"]["score"].get("passed"))
                for row in scored
            ),
        },
    }
    atomic_json(HERE / "results.json", summary)
    print(json.dumps(summary["counts"], ensure_ascii=False, indent=2), flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "phase",
        choices=("prepare", "preflight", "run", "score", "summarize", "all"),
    )
    parser.add_argument("--parquet", type=Path, default=DEFAULT_PARQUET)
    parser.add_argument("--work-root", type=Path, default=DEFAULT_WORK_ROOT)
    parser.add_argument("--repo-root", type=Path, default=DEFAULT_REPO_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract = load_json(CONTRACT_PATH)
    dataset = read_dataset(args.parquet)
    tasks = current_tasks(contract, dataset, args.work_root)
    args.work_root.mkdir(parents=True, exist_ok=True)
    phases = (
        ("prepare", phase_prepare),
        ("preflight", phase_preflight),
        ("run", phase_run),
        ("score", phase_score),
        ("summarize", phase_summarize),
    )
    for name, function in phases:
        if args.phase not in (name, "all"):
            continue
        if name == "run":
            function(tasks, args.work_root, args.repo_root)
        else:
            function(tasks, args.work_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
