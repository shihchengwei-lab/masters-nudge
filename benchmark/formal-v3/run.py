#!/usr/bin/env python3
"""Windows-native six-task benchmark for a taste request versus Masters' Nudge."""

from __future__ import annotations

import hashlib
import json
import os
from contextlib import closing
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

ROOT = Path(os.environ.get("MN_BENCHMARK_ROOT", r"D:\masters-nudge-benchmark\round-2"))
ARTIFACT_ROOT = ROOT / "artifacts"
TMP = ROOT / "tmp"
PACKAGE = REPO / "plugins" / "masters-nudge"
DATASET = REPO.parent / "_external" / "multi-swe-bench-flash.jsonl"
DJANGO_SOURCE = REPO.parent / "_external" / "swebench-smoke" / "repos-win" / "django"
DJANGO_PYTHON = (
    REPO.parent / "_external" / "swebench-smoke" / "envcheck-win"
    / "django__django-11951" / ".venv" / "Scripts" / "python.exe"
)
REPLACEMENT_DATA = (
    Path(os.environ["LOCALAPPDATA"]) / "Temp" / "mn-replacement-check-20260919"
    / "source-cases.json"
)
HARD_CALIBRATION = Path(os.environ["LOCALAPPDATA"]) / "Temp" / "mn-formal-v3-hard-calibration"
ACTOR_MODEL = "gpt-5.6-sol"
JUDGE_MODEL = "gpt-6-astra"
TIMEOUT_SECONDS = 1800
TASTE_REQUEST = "請高品味的完成任務。"

CASES = {
    "django-window-filtering": {
        "kind": "django-window",
        "base": "f3f9d03edf17ccfa17263c7efa0b1350d1ac9278",
        "reference": "f387d024fc75569d2a4a338bfda76cc2f328f627",
        "task": (
            "Add support for filtering and excluding rows using window-function results in Django "
            "QuerySets. Support direct window comparisons, expressions containing windows, conditional "
            "annotations, aliases, column comparisons, combinations of predicates, values/values_list "
            "and select_related. Preserve ordering, apply slicing after the window-result filter, and "
            "return correct count results. Preserve existing non-window query behavior. Mixed OR or "
            "negated-AND predicates involving a window result and an ordinary field during conditional "
            "aggregation must raise the NotImplementedError required by the tests."
        ),
        "django_groups": ["expressions_window", "foreign_object"],
    },
    "django-13128": {
        "kind": "django-dataset",
        "instance": "django__django-13128",
        "base": "2d67222472f80f251607ae1b720527afceba06ad",
        "task": (
            "Make subtraction between temporal expressions infer the correct duration result without "
            "requiring ExpressionWrapper or an explicit output_field. Support date, datetime and time "
            "operands, including case expressions and subqueries, and composition with duration "
            "arithmetic. Preserve existing arithmetic behavior and correct returned values, including "
            "microseconds and native-duration database compilation paths."
        ),
        "django_groups": ["expressions.tests.FTimeDeltaTests"],
    },
    "django-16263": {
        "kind": "django-dataset",
        "instance": "django__django-16263",
        "base": "321ecb40f4da842926e1bc07e11df4aabe53ca4b",
        "task": (
            "Optimize count queries by omitting unused annotations and unnecessary subquery wrapping. "
            "Preserve annotations still needed by filters, other expressions or query semantics, and "
            "preserve correct counts for grouping, distinct and sliced queries. Support annotations and "
            "aliases without changing the original QuerySet."
        ),
        "django_groups": ["aggregation", "annotations"],
    },
    "tokio-rs__tokio-6618": {
        "kind": "dataset",
        "task": (
            "Add CancellationToken.run_until_cancelled, which runs a future to completion and returns "
            "Some(output), unless cancellation happens before completion, in which case it drops the "
            "future and returns None. When completion and cancellation are both ready, completion wins. "
            "Document cancellation safety and avoid expanding dependency features solely for this helper."
        ),
        "verify": ["cargo", "test", "-p", "tokio-util", "--test", "sync_cancellation_token",
                   "run_until_cancelled"],
    },
    "anuraghazra__github-readme-stats-3442": {
        "kind": "dataset",
        "task": (
            "Support Cloudflare Workers deployment. Add a Cloudflare entrypoint and adapter plus "
            "wrangler.toml, allow API handlers to receive environment variables, and let request logic "
            "use fetch because axios is unavailable in Workers. Preserve Vercel behavior and existing "
            "fetcher, retry and card behavior."
        ),
        "install": ["npm.cmd", "install"],
        "verify": ["npm.cmd", "test", "--", "--runInBand", "tests/fetchGist.test.js",
                   "tests/fetchRepo.test.js", "tests/fetchStats.test.js",
                   "tests/fetchTopLanguages.test.js", "tests/retryer.test.js"],
        "required_paths": ["cloudflare/adapter.js", "cloudflare/index.js", "wrangler.toml"],
    },
    "anuraghazra__github-readme-stats-2099": {
        "kind": "dataset",
        "task": (
            "Add layout=donut to the top-languages card. Render language proportions as an unfilled "
            "stroked ring with a legend, including a complete ring for one language. Preserve hide, "
            "langs_count, existing layouts, sizing, themes and translations. Update the public option "
            "type and user documentation."
        ),
        "install": ["npm.cmd", "install"],
        "verify": ["npm.cmd", "test", "--", "--runInBand", "tests/renderTopLanguages.test.js"],
    },
}

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "winner": {"type": "string", "enum": ["X", "Y", "tie"]},
        "x_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "y_score": {"type": "integer", "minimum": 1, "maximum": 5},
        "reason": {"type": "string", "maxLength": 800},
        "improvement": {"type": "string", "maxLength": 600},
    },
    "required": ["winner", "x_score", "y_score", "reason", "improvement"],
    "additionalProperties": False,
}

TOKIO_EXTRA_TEST = r'''

#[test]
fn run_until_cancelled_prefers_completed_future_when_both_ready() {
    let (waker, _) = new_count_waker();
    for _ in 0..64 {
        let token = CancellationToken::new();
        token.cancel();
        let fut = token.run_until_cancelled(std::future::ready(42));
        pin!(fut);
        assert_eq!(
            Poll::Ready(Some(42)),
            fut.as_mut().poll(&mut Context::from_waker(&waker))
        );
    }
}
'''

DONUT_EXTRA_TEST = r'''

it("should render donut segments as an unfilled stroked ring", () => {
  document.body.innerHTML = renderTopLanguages(langs, { layout: "donut" });
  queryAllByTestId(document.body, "lang-donut").forEach((segment) => {
    expect(segment).toHaveAttribute("fill", "none");
    expect(segment).toHaveAttribute("stroke");
  });
});
'''

NATIVE_DURATION_PROBE = '''"""Compile-only native-duration regression probe."""
from datetime import datetime, timedelta
from types import SimpleNamespace
from django.db.backends.base.operations import BaseDatabaseOperations
from django.db.models import DateTimeField, DurationField, Value

connection = SimpleNamespace(features=SimpleNamespace(has_native_duration_field=True))
connection.ops = BaseDatabaseOperations(connection)
compiler = SimpleNamespace(compile=lambda expression: ("%s", [expression.value]))
expression = (
    Value(datetime(2020, 1, 1), output_field=DateTimeField())
    + Value(timedelta(days=1), output_field=DurationField())
).resolve_expression()
sql, params = expression.as_sql(compiler, connection)
assert sql == "(%s + %s)"
assert len(params) == 2
'''


def run(command: list[str], cwd: Path, timeout: int = 1800,
        env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout, env=env)


def git(cwd: Path, *args: str, check: bool = True) -> str:
    result = run(["git", *args], cwd)
    if check and result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


def apply_patch_text(cwd: Path, text: str, name: str) -> None:
    patch = ROOT / name
    patch.write_text(text, encoding="utf-8", newline="\n")
    try:
        result = run(["git", "apply", "--whitespace=nowarn", str(patch)], cwd)
    finally:
        patch.unlink(missing_ok=True)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)


def dataset_rows() -> dict[str, dict]:
    wanted = {case_id for case_id, case in CASES.items() if case["kind"] == "dataset"}
    found = {}
    with DATASET.open(encoding="utf-8") as source:
        for line in source:
            row = json.loads(line)
            if row["instance_id"] in wanted:
                found[row["instance_id"]] = row
    if found.keys() != wanted:
        raise RuntimeError(f"missing dataset rows: {sorted(wanted - found.keys())}")
    return found


def replacement_rows() -> dict[str, dict]:
    data = json.loads(REPLACEMENT_DATA.read_text(encoding="utf-8"))
    return {key: data[key] for key in ("django__django-13128", "django__django-16263")}


def actor_bin() -> str:
    from masters_nudge.providers import resolve_codex_bin
    npm_launcher = shutil.which("codex.cmd")
    npm_binaries = sorted(
        (Path(npm_launcher).parent / "node_modules" / "@openai" / "codex").glob(
            "**/bin/codex.exe"
        )
    ) if npm_launcher else []
    binary = str(npm_binaries[0]) if npm_binaries else resolve_codex_bin()
    if not binary:
        raise RuntimeError("official Codex executable is unavailable")
    return binary


def export_tree(source: Path, commit: str, destination: Path) -> None:
    destination.mkdir(parents=True)
    archive = ROOT / f"{destination.name}.zip"
    result = run(["git", "archive", "--format=zip", f"--output={archive}", commit], source)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    import zipfile
    try:
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(destination)
    finally:
        archive.unlink(missing_ok=True)


def fetch_base(row: dict, destination: Path) -> None:
    destination.mkdir(parents=True)
    commands = [
        ["git", "init"],
        ["git", "remote", "add", "origin", f"https://github.com/{row['org']}/{row['repo']}.git"],
        ["git", "fetch", "--depth", "1", "origin", row["base"]["sha"]],
        ["git", "checkout", "--detach", "FETCH_HEAD"],
    ]
    for command in commands:
        result = run(command, destination)
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)


def test_paths(patch: str) -> list[str]:
    return re.findall(r"^diff --git a/(\S+)", patch, re.MULTILINE)


def fingerprint(root: Path, paths: list[str]) -> str:
    digest = hashlib.sha256()
    for name in sorted(paths):
        path = root / name
        digest.update(name.encode())
        digest.update(path.read_bytes() if path.is_file() else b"<missing>")
    return digest.hexdigest()


def environment(case_id: str) -> dict[str, str]:
    env = {**os.environ, "TEMP": str(TMP), "TMP": str(TMP), "TMPDIR": str(TMP),
           "PYTHONUTF8": "1"}
    updated_codex = Path(actor_bin()).parent
    path_entries = [entry for entry in env.get("PATH", "").split(os.pathsep)
                    if entry and not (Path(entry) / "codex.exe").is_file()]
    env["PATH"] = os.pathsep.join([str(updated_codex), *path_entries])
    if case_id.startswith("django"):
        env["PYTHONPATH"] = "."
    if case_id.startswith("tokio"):
        env["CARGO_TARGET_DIR"] = str(ROOT / "cargo-target" / "tokio")
        env["RUSTFLAGS"] = "-Awarnings"
    return env


def verify_steps(case_id: str) -> list[list[str]]:
    case = CASES[case_id]
    if case_id.startswith("django"):
        steps = [[str(DJANGO_PYTHON), "tests/runtests.py", *case["django_groups"],
                  "--parallel=1", "--verbosity=1"]]
        if case_id == "django-13128":
            steps.append([str(DJANGO_PYTHON), "tests/native_duration_probe.py"])
        return steps
    return [case["verify"]]


def verify(case_id: str, cwd: Path, artifact: Path | None = None) -> list[dict]:
    records = []
    for number, command in enumerate(verify_steps(case_id), 1):
        started = time.monotonic()
        result = run(command, cwd, 900, environment(case_id))
        record = {"command": command, "exit_code": result.returncode,
                  "elapsed_seconds": round(time.monotonic() - started, 3),
                  "stdout": result.stdout, "stderr": result.stderr}
        records.append(record)
        if artifact:
            (artifact / f"verification-{number}.json").write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if result.returncode:
            break
    return records


def contract_extras(case_id: str, cwd: Path) -> tuple[bool, list[str]]:
    missing = [name for name in CASES[case_id].get("required_paths", [])
               if not (cwd / name).is_file()]
    return not missing, missing


def append_text(path: Path, text: str) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as output:
        output.write(text)


def prepare() -> None:
    if ROOT.exists():
        raise RuntimeError(f"refusing to reuse benchmark root: {ROOT}")
    (ROOT / "cases").mkdir(parents=True)
    ARTIFACT_ROOT.mkdir()
    TMP.mkdir()
    rows = dataset_rows()
    django = replacement_rows()
    manifest = {}
    for case_id, case in CASES.items():
        workspace = ROOT / "cases" / case_id
        if case["kind"].startswith("django"):
            export_tree(DJANGO_SOURCE, case["base"], workspace)
            git(workspace, "init")
            git(workspace, "config", "core.autocrlf", "true")
            if case["kind"] == "django-window":
                patch = git(DJANGO_SOURCE, "diff", case["base"], case["reference"], "--",
                            "tests/expressions_window")
                fix = git(DJANGO_SOURCE, "diff", case["base"], case["reference"], "--", "django")
            else:
                row = django[case["instance"]]
                patch, fix = row["test_patch"], row["patch"]
        else:
            row = rows[case_id]
            fetch_base(row, workspace)
            patch, fix = row["test_patch"], row["fix_patch"]
            if case.get("install"):
                install_env = environment(case_id)
                install_env["npm_config_cache"] = str(ROOT / "npm-cache")
                result = run(case["install"], workspace, 1800, install_env)
                (ROOT / f"{case_id}-install.json").write_text(
                    json.dumps({"exit_code": result.returncode, "stdout": result.stdout,
                                "stderr": result.stderr}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
                if result.returncode:
                    raise RuntimeError(f"dependency install failed: {case_id}")
                git(workspace, "reset", "--hard", row["base"]["sha"])
        apply_patch_text(workspace, patch, f"{case_id}-tests.patch")
        paths = test_paths(patch)
        if case_id == "django-13128":
            probe = workspace / "tests" / "native_duration_probe.py"
            probe.write_text(NATIVE_DURATION_PROBE, encoding="utf-8", newline="\n")
            paths.append("tests/native_duration_probe.py")
        elif case_id == "tokio-rs__tokio-6618":
            path = workspace / "tokio-util" / "tests" / "sync_cancellation_token.rs"
            append_text(path, TOKIO_EXTRA_TEST)
            paths.append("tokio-util/tests/sync_cancellation_token.rs")
        elif case_id == "anuraghazra__github-readme-stats-2099":
            path = workspace / "tests" / "renderTopLanguages.test.js"
            append_text(path, DONUT_EXTRA_TEST)
            paths.append("tests/renderTopLanguages.test.js")
        git(workspace, "config", "user.name", "Masters Nudge Benchmark")
        git(workspace, "config", "user.email", "benchmark@local.invalid")
        git(workspace, "add", "-A")
        git(workspace, "commit", "--no-verify", "-m", "round 2 benchmark seed")
        manifest[case_id] = {"seed": git(workspace, "rev-parse", "HEAD").strip(),
                             "test_paths": sorted(set(paths)),
                             "tests_sha256": fingerprint(workspace, sorted(set(paths))),
                             "fix_patch": fix}
    (ROOT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "plan.json").write_text(json.dumps(plan_data(), ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")


def preflight() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    records = []
    for case_id in CASES:
        workspace = ROOT / "cases" / case_id
        git(workspace, "reset", "--hard", manifest[case_id]["seed"])
        git(workspace, "clean", "-fd")
        baseline = verify(case_id, workspace)
        apply_patch_text(workspace, manifest[case_id]["fix_patch"], f"{case_id}-official.patch")
        oracle = verify(case_id, workspace)
        extra_ok, missing = contract_extras(case_id, workspace)
        record = {"case": case_id,
                  "baseline_exits": [item["exit_code"] for item in baseline],
                  "oracle_exits": [item["exit_code"] for item in oracle],
                  "oracle_required_paths": extra_ok, "missing": missing}
        records.append(record)
        (ROOT / "preflight.json").write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(record, ensure_ascii=False), flush=True)
        if all(item["exit_code"] == 0 for item in baseline) or any(
            item["exit_code"] != 0 for item in oracle) or not extra_ok:
            raise RuntimeError(f"invalid benchmark contract: {case_id}")
        git(workspace, "reset", "--hard", manifest[case_id]["seed"])
        git(workspace, "clean", "-fd")


def verification_display(case_id: str) -> str:
    return " then ".join(subprocess.list2cmdline(step) for step in verify_steps(case_id))


def common_prompt(case_id: str) -> str:
    return (
        "Complete the repository task below. The checked-in tests are an immutable contract: do not "
        "edit, delete, or replace them. You own implementation and verification. Use apply_patch for "
        "edits. Do not commit, install packages, inspect Git history, use the network, delegate, or use "
        "subagents.\n\n" + CASES[case_id]["task"] + "\n\nRun `" +
        verification_display(case_id) + "`, inspect the final diff, and report the result.\n"
    )


def actor_prompt(case_id: str, arm: str) -> str:
    prompt = common_prompt(case_id)
    return prompt + (f"\n{TASTE_REQUEST}\n" if arm == "A" else "")


def toml(value) -> str:
    if isinstance(value, dict):
        return "{" + ",".join(f"{json.dumps(key)}={toml(item)}" for key, item in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ",".join(toml(item) for item in value) + "]"
    return json.dumps(value)


def hook_arguments() -> list[str]:
    hooks = json.loads((PACKAGE / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    servers = json.loads((PACKAGE / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
    def resolve(value):
        if isinstance(value, dict):
            return {key: resolve(item) for key, item in value.items()}
        if isinstance(value, list):
            return [resolve(item) for item in value]
        if isinstance(value, str):
            return value.replace("${PLUGIN_ROOT}", str(PACKAGE.resolve()).replace("\\", "/"))
        return value
    result = []
    for name, config in servers.items():
        result.extend(["-c", f"mcp_servers.{name}={toml(resolve(config))}"])
    for event, groups in hooks.items():
        result.extend(["-c", f"hooks.{event}={toml(groups)}"])
    return result


def event_usage(events: str) -> dict[str, int]:
    total = {key: 0 for key in ("input_tokens", "cached_input_tokens", "output_tokens",
                                "reasoning_output_tokens")}
    for line in events.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "turn.completed":
            for key in total:
                total[key] += int(event.get("usage", {}).get(key) or 0)
    return total


def file_change_events(events: str) -> int:
    count = 0
    for line in events.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if event.get("type") == "item.completed" and event.get("item", {}).get("type") == "file_change":
            count += 1
    return count


def attempts(data: Path) -> list[dict]:
    database = data / "feedback.sqlite3"
    if not database.is_file():
        return []
    with sqlite3.connect(database) as connection:
        connection.row_factory = sqlite3.Row
        records = connection.execute("SELECT * FROM attempts ORDER BY started").fetchall()
    result = []
    for record in records:
        item = dict(record)
        item["detail"] = json.loads(item["detail"]) if item.get("detail") else {}
        result.append(item)
    return result


def skipped_new_test_patches(data: Path) -> int:
    database = data / "feedback.sqlite3"
    if not database.is_file():
        return 0
    with closing(sqlite3.connect(database)) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(rounds)")}
        if "skipped_new_test_patches" not in columns:
            return 0
        return connection.execute(
            "SELECT COALESCE(SUM(skipped_new_test_patches),0) FROM rounds"
        ).fetchone()[0]


def unresolved_batches(data: Path) -> list[str]:
    database = data / "feedback.sqlite3"
    if not database.is_file():
        return []
    with sqlite3.connect(database) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(batches)")}
        attempt_columns = {row[1] for row in connection.execute("PRAGMA table_info(attempts)")}
        if not {"id", "round_id"} <= columns or "batch_id" not in attempt_columns:
            return []
        return [row[0] for row in connection.execute(
            "SELECT b.id FROM batches b LEFT JOIN attempts a ON a.batch_id=b.id "
            "WHERE b.round_id<>'' AND a.id IS NULL ORDER BY b.received")]


def provider_usage(records: list[dict]) -> dict[str, int]:
    total = {key: 0 for key in ("input_tokens", "cached_input_tokens", "output_tokens",
                                "reasoning_output_tokens")}
    for record in records:
        for key in total:
            total[key] += int(record.get("detail", {}).get("usage", {}).get(key) or 0)
    return total


def execute(case_id: str, repeat: int, arm: str) -> dict:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    workspace = ROOT / "cases" / case_id
    git(workspace, "reset", "--hard", manifest[case_id]["seed"])
    git(workspace, "clean", "-fd")
    artifact = ARTIFACT_ROOT / "runs" / case_id / f"repeat-{repeat}" / arm
    artifact.mkdir(parents=True)
    data = artifact / "masters-nudge-data"
    data.mkdir()
    (data / "config.json").write_text(
        json.dumps({"provider": "openai", "model": ACTOR_MODEL}), encoding="utf-8")
    enabled = arm == "B"
    command = [
        actor_bin(), "-c", "project_doc_max_bytes=0", "-c", "features.multi_agent=false",
        "-c", 'model_reasoning_effort="medium"',
        *(["--enable", "hooks", "--disable", "plugins", *hook_arguments()] if enabled else
          ["--disable", "hooks", "--disable", "plugins"]),
        "exec", "--ignore-user-config", "--ignore-rules",
        *(["--dangerously-bypass-hook-trust"] if enabled else []),
        "--skip-git-repo-check", "--ephemeral", "--json", "-s", "danger-full-access",
        "-m", ACTOR_MODEL, "-C", str(workspace), "-o", str(artifact / "actor-final.txt"), "-",
    ]
    env = environment(case_id)
    env.update({"MASTERS_NUDGE_ACTIVE": "0", "MASTERS_NUDGE_TEST_MODE": "1",
                "PLUGIN_ROOT": str(PACKAGE), "MASTERS_NUDGE_DATA_DIR": str(data),
                "MASTERS_NUDGE_RUNTIME_DIR": str(PACKAGE)})
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=workspace, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, encoding="utf-8",
                               errors="replace", env=env)
    stdout, stderr = [], []
    def collect(stream, target):
        for line in stream:
            target.append(line)
    readers = [threading.Thread(target=collect, args=(process.stdout, stdout)),
               threading.Thread(target=collect, args=(process.stderr, stderr))]
    for reader in readers:
        reader.start()
    process.stdin.write(actor_prompt(case_id, arm))
    process.stdin.close()
    fault = ""
    while process.poll() is None:
        if time.monotonic() - started > TIMEOUT_SECONDS:
            fault = "Actor timed out"
            run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"], ROOT, 60)
            break
        time.sleep(0.25)
    process.wait(timeout=30)
    for reader in readers:
        reader.join(timeout=5)
    elapsed = time.monotonic() - started
    events = "".join(stdout)
    errors = "".join(stderr)
    (artifact / "actor-events.jsonl").write_text(events, encoding="utf-8")
    (artifact / "actor-stderr.txt").write_text(errors, encoding="utf-8")
    (artifact / "final.patch").write_text(git(workspace, "diff", "--no-ext-diff", "--binary"),
                                           encoding="utf-8")
    verification = verify(case_id, workspace, artifact)
    extra_ok, missing = contract_extras(case_id, workspace)
    provider_records = attempts(data)
    skipped_tests = skipped_new_test_patches(data)
    unresolved = unresolved_batches(data)
    changes = file_change_events(events)
    if process.returncode and not fault:
        fault = f"Actor exit {process.returncode}"
    if unresolved and not fault:
        fault = "Provider interruption"
    if any(record.get("outcome") not in ("feedback", "silence") for record in provider_records) and not fault:
        fault = "Provider fault"
    if enabled and changes and not provider_records and not skipped_tests and not fault:
        fault = "PostToolUse produced no Provider judgment after a file change"
    tests_unchanged = run(
        ["git", "diff", "--quiet", "HEAD", "--", *manifest[case_id]["test_paths"]],
        workspace,
    ).returncode == 0
    result = {
        "case": case_id, "repeat": repeat, "arm": arm,
        "elapsed_seconds": round(elapsed, 3), "actor_exit_code": process.returncode,
        "actor_usage": event_usage(events), "provider_usage": provider_usage(provider_records),
        "provider_attempts": provider_records, "provider_unresolved_batches": unresolved,
        "skipped_new_test_patches": skipped_tests,
        "file_change_events": changes, "tests_unchanged": tests_unchanged,
        "verification_exits": [item["exit_code"] for item in verification],
        "required_paths_present": extra_ok, "missing_required_paths": missing,
        "contract_passed": all(item["exit_code"] == 0 for item in verification)
                           and tests_unchanged and extra_ok,
        "changed_files": git(workspace, "diff", "--name-only").splitlines(), "invalid": fault,
    }
    (artifact / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def actors(limit: int | None = None) -> None:
    summary = ARTIFACT_ROOT / "actor-summary.json"
    results = json.loads(summary.read_text(encoding="utf-8")) if summary.is_file() else []
    done = {(row["case"], row["repeat"], row["arm"]) for row in results}
    count = 0
    for case_index, case_id in enumerate(CASES):
        for repeat in (1, 2):
            order = ("A", "B") if (case_index + repeat) % 2 else ("B", "A")
            for arm in order:
                if (case_id, repeat, arm) in done:
                    continue
                result = execute(case_id, repeat, arm)
                results.append(result)
                summary.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
                print(json.dumps({key: result[key] for key in (
                    "case", "repeat", "arm", "invalid", "contract_passed", "elapsed_seconds")},
                    ensure_ascii=False), flush=True)
                if result["invalid"]:
                    raise RuntimeError(f"benchmark tool fault: {result['invalid']}")
                count += 1
                if limit is not None and count >= limit:
                    return


def judge_prompt(case_id: str, x: str, y: str) -> str:
    return f"""You are a blind code-quality judge. Both implementations passed the same immutable
contract. Compare engineering quality only; do not guess their origin.

Prefer fewer legal states, branches, timing dependencies, side effects and hidden dependencies.
Prefer one authoritative source of truth, one-way causality, locally predictable behavior, and a
solution at the earliest responsible boundary. Do not reward size, comments, formatting, tests, or
similarity to an expected patch by itself. Score each implementation from 1 to 5. Explain the
material difference and give one concrete improvement for the weaker implementation. Return tie
when neither has a material structural advantage.

TASK
{CASES[case_id]['task']}

IMPLEMENTATION X
{x}

IMPLEMENTATION Y
{y}
"""


def run_judge(case_id: str, repeat: int, number: int, x_arm: str, y_arm: str) -> dict:
    directory = ARTIFACT_ROOT / "judges" / case_id / f"repeat-{repeat}" / f"judge-{number}"
    directory.mkdir(parents=True)
    schema = directory / "schema.json"
    output = directory / "output.json"
    schema.write_text(json.dumps(JUDGE_SCHEMA, ensure_ascii=False), encoding="utf-8")
    pair = ARTIFACT_ROOT / "runs" / case_id / f"repeat-{repeat}"
    x = (pair / x_arm / "final.patch").read_text(encoding="utf-8")
    y = (pair / y_arm / "final.patch").read_text(encoding="utf-8")
    command = [actor_bin(), "-c", "project_doc_max_bytes=0", "-c", "features.multi_agent=false",
               "-c", 'model_reasoning_effort="medium"', "--disable", "hooks", "--disable", "plugins",
               "exec", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check",
               "--ephemeral", "--json", "-s", "read-only", "-m", JUDGE_MODEL,
               "--output-schema", str(schema), "-o", str(output), "-"]
    started = time.monotonic()
    result = subprocess.run(command, cwd=directory, input=judge_prompt(case_id, x, y),
                            capture_output=True, text=True, encoding="utf-8", errors="replace",
                            timeout=900, env=environment(case_id))
    (directory / "events.jsonl").write_text(result.stdout, encoding="utf-8")
    (directory / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    if result.returncode or not output.is_file():
        raise RuntimeError(f"judge failed: {case_id} repeat {repeat} judge {number}")
    judgment = json.loads(output.read_text(encoding="utf-8"))
    winner = judgment["winner"]
    record = {**judgment, "case": case_id, "repeat": repeat, "judge": number,
              "mapping": {"X": x_arm, "Y": y_arm},
              "winner_arm": winner if winner == "tie" else {"X": x_arm, "Y": y_arm}[winner],
              "elapsed_seconds": round(time.monotonic() - started, 3),
              "usage": event_usage(result.stdout)}
    (directory / "result.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


def judges() -> None:
    actors_data = json.loads((ARTIFACT_ROOT / "actor-summary.json").read_text(encoding="utf-8"))
    if len(actors_data) != 24 or any(row["invalid"] for row in actors_data):
        raise RuntimeError("actor benchmark is incomplete or contains a tool fault")
    by_key = {(row["case"], row["repeat"], row["arm"]): row for row in actors_data}
    summary_path = ARTIFACT_ROOT / "judge-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else []
    done = {(row["case"], row["repeat"]) for row in summary}
    for case_id in CASES:
        for repeat in (1, 2):
            if (case_id, repeat) in done:
                continue
            if not all(by_key[(case_id, repeat, arm)]["contract_passed"] for arm in ("A", "B")):
                item = {"case": case_id, "repeat": repeat, "winner": "not_judged",
                        "reason": "At least one arm did not complete the contract.", "judges": []}
            else:
                first = run_judge(case_id, repeat, 1, "A", "B")
                second = run_judge(case_id, repeat, 2, "B", "A")
                records = [first, second]
                if first["winner_arm"] != second["winner_arm"]:
                    records.append(run_judge(case_id, repeat, 3, "A", "B"))
                votes = [record["winner_arm"] for record in records]
                winner = next((arm for arm in ("A", "B", "tie") if votes.count(arm) >= 2), "tie")
                item = {"case": case_id, "repeat": repeat, "winner": winner, "judges": records}
            summary.append(item)
            summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")
            print(json.dumps({"case": case_id, "repeat": repeat, "winner": item["winner"]},
                             ensure_ascii=False), flush=True)


def hash_files(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(REPO).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def plan_data() -> dict:
    package_files = sorted(path for path in PACKAGE.rglob("*") if path.is_file())
    return {"root": str(ROOT), "artifact_root": str(ARTIFACT_ROOT), "cases": list(CASES),
            "runs": 24, "A_extra": TASTE_REQUEST, "B_extra": "hooks enabled only",
            "actor_model": ACTOR_MODEL, "judge_model": JUDGE_MODEL,
            "tool_commit": git(REPO, "rev-parse", "HEAD").strip(),
            "plugin_sha256": hash_files(package_files)}


def plan() -> None:
    print(json.dumps(plan_data(), ensure_ascii=False, indent=2))


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] not in {"plan", "prepare", "preflight", "actors", "judge"}:
        print("usage: run.py plan|prepare|preflight|actors [max-new-runs]|judge", file=sys.stderr)
        return 2
    command = sys.argv[1]
    if command == "plan":
        plan()
    elif command == "prepare":
        prepare()
    elif command == "preflight":
        preflight()
    elif command == "actors":
        actors(int(sys.argv[2]) if len(sys.argv) > 2 else None)
    else:
        judges()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
