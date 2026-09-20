#!/usr/bin/env python3
"""Expanded paired A/B: champion context vs preserved-result direct channel."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


REPO = Path(__file__).resolve().parents[2]
DATASET_ROOT = REPO.parent / "_external" / "swebench-smoke"
ROWS_PATH = DATASET_ROOT / "mini50_rows.json"
SOURCE_REPOS = {
    "django/django": DATASET_ROOT / "repos-win" / "django",
    "sphinx-doc/sphinx": DATASET_ROOT / "repos-win" / "sphinx",
}
PYTHONS = {
    "django/django": DATASET_ROOT / "envcheck-win" / "django__django-11951" / ".venv" / "Scripts" / "python.exe",
    "sphinx-doc/sphinx": DATASET_ROOT / "envcheck-win" / "sphinx-doc__sphinx-8035" / ".venv" / "Scripts" / "python.exe",
}
CASE_IDS = (
    "django__django-11885",
    "django__django-12273",
    "django__django-12325",
    "sphinx-doc__sphinx-7590",
    "sphinx-doc__sphinx-7748",
    "sphinx-doc__sphinx-8548",
)
ROOT = Path(os.environ.get(
    "MN_AB_ROOT",
    str(Path.home() / "AppData" / "Local" / "Temp" / "mn-ab-preserved-result-expanded-20260920-v2"),
))
CHAMPION_PACKAGE = REPO / "plugins" / "masters-nudge"
CANDIDATE_PACKAGE = ROOT / "runtime-preserved-result"
ACTOR_BIN = Path.home() / "AppData" / "Local" / "OpenAI" / "Codex" / "bin" / "247581e40ee272fb" / "codex.exe"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


champion = load("expanded_champion_runner", REPO / "experiments" / "ab-structural-20260918" / "run_ab.py")
candidate = load("expanded_candidate_runner", REPO / "experiments" / "ab-structural-20260918" / "run_ab.py")


def fail_to_pass(row: dict) -> list[str]:
    value = row["FAIL_TO_PASS"]
    return json.loads(value) if isinstance(value, str) else value


def django_labels(items: list[str]) -> list[str]:
    labels = []
    for item in items:
        test, owner = item.rsplit(" (", 1)
        labels.append(f"{owner[:-1]}.{test}")
    return labels


def task_text(row: dict) -> str:
    return row["problem_statement"].strip()


def case_from(row: dict) -> dict:
    python = PYTHONS[row["repo"]]
    tests = fail_to_pass(row)
    if row["repo"] == "django/django":
        verify = [str(python), "tests/runtests.py", *django_labels(tests), "--parallel=1", "--verbosity=1"]
    else:
        verify = [str(python), "-m", "pytest", *tests, "-q"]
    return {
        "source": SOURCE_REPOS[row["repo"]],
        "base": row["base_commit"],
        "task": task_text(row),
        "verify": verify,
        "verify_env": {"PYTHONPATH": ".", "PYTHONUTF8": "1"},
        "verify_display": subprocess.list2cmdline(verify),
        "repo": row["repo"],
        "test_patch": row["test_patch"],
        "gold_patch": row["patch"],
    }


rows = {row["instance_id"]: row for row in json.loads(ROWS_PATH.read_text(encoding="utf-8"))}
CASES = {case_id: case_from(rows[case_id]) for case_id in CASE_IDS}
for module, package in ((champion, CHAMPION_PACKAGE), (candidate, CANDIDATE_PACKAGE)):
    module.ROOT = ROOT
    module.CASES = CASES
    module.PACKAGE = package
    module.ACTOR_BIN = ACTOR_BIN


def apply_patch_file(cwd: Path, text: str, name: str) -> None:
    patch = cwd / name
    patch.write_text(text, encoding="utf-8")
    result = champion.run(["git", "apply", "--whitespace=nowarn", str(patch)], cwd=cwd)
    patch.unlink()
    if result.returncode:
        raise RuntimeError(f"cannot apply {name} in {cwd}: {result.stderr}")


def make_candidate_runtime() -> None:
    shutil.copytree(CHAMPION_PACKAGE, CANDIDATE_PACKAGE)
    adapter = CANDIDATE_PACKAGE / "masters_nudge" / "codex_adapter.py"
    text = adapter.read_text(encoding="utf-8")
    text = text.replace(
        "from .contracts import SessionRef, ToolCompleted, ToolFault",
        "from .contracts import SessionRef, ToolCompleted, ToolFault, json_text",
    )
    old = '''            return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                            "additionalContext": delivery_text(feedback)},
                    AUDIT_MARKER_KEY: attempt}'''
    new = '''            original = event.tool_response
            original_text = original if isinstance(original, str) else json_text(original)
            return {
                "continue": False,
                "stopReason": f"{original_text}\\n\\n{delivery_text(feedback)}",
                AUDIT_MARKER_KEY: attempt,
            }'''
    if old not in text:
        raise RuntimeError("champion adapter shape changed; candidate was not built")
    adapter.write_text(text.replace(old, new), encoding="utf-8")


def prepare() -> None:
    if ROOT.exists():
        raise RuntimeError(f"refusing to reuse experiment root: {ROOT}")
    (ROOT / "seeds").mkdir(parents=True)
    make_candidate_runtime()
    plan = {}
    for case_id, case in CASES.items():
        seed = ROOT / "seeds" / case_id
        champion.export(case["source"], case["base"], seed)
        apply_patch_file(seed, case["test_patch"], "_test.patch")
        (seed / "TASK.md").write_text(champion.task_prompt(case), encoding="utf-8")
        champion.git(seed, "init")
        champion.git(seed, "config", "user.name", "Masters Nudge Test")
        champion.git(seed, "config", "user.email", "test@local.invalid")
        champion.git(seed, "add", "-A")
        champion.git(seed, "commit", "-m", "sealed test start")
        plan[case_id] = {
            "repo": case["repo"], "base": case["base"], "task": case["task"],
            "verify": case["verify"], "seed_commit": champion.git(seed, "rev-parse", "HEAD").strip(),
        }
    (ROOT / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")


def preflight() -> None:
    results = []
    for case_id, case in CASES.items():
        baseline = champion.clone_seed(case_id, ROOT / "preflight" / case_id / "baseline")
        env = {**os.environ, **case["verify_env"]}
        before = champion.run(case["verify"], cwd=baseline, timeout=600, env=env)
        oracle = champion.clone_seed(case_id, ROOT / "preflight" / case_id / "oracle")
        apply_patch_file(oracle, case["gold_patch"], "_gold.patch")
        after = champion.run(case["verify"], cwd=oracle, timeout=600, env=env)
        row = {
            "case": case_id, "baseline_exit": before.returncode, "oracle_exit": after.returncode,
            "baseline_output": before.stdout + before.stderr,
            "oracle_output": after.stdout + after.stderr,
        }
        results.append(row)
        (ROOT / "preflight.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({key: row[key] for key in ("case", "baseline_exit", "oracle_exit")}), flush=True)
        if before.returncode == 0 or after.returncode != 0:
            raise RuntimeError(f"preflight failed: {case_id}")


def execute(case_id: str, repeat: int, arm: str) -> dict:
    module = champion if arm == "A" else candidate
    return module.execute(case_id, repeat, arm, use_nudge=True)


def actors() -> None:
    results = []
    for case_id in CASE_IDS:
        for repeat in (1, 2):
            with ThreadPoolExecutor(max_workers=2) as pool:
                jobs = [pool.submit(execute, case_id, repeat, arm) for arm in ("A", "B")]
                pair = [job.result() for job in jobs]
            results.extend(pair)
            (ROOT / "actor-summary.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps([
                {key: row[key] for key in ("case", "repeat", "arm", "invalid", "contract_passed", "elapsed_seconds")}
                for row in pair
            ], ensure_ascii=False), flush=True)
            if any(row["invalid"] for row in pair):
                raise RuntimeError("tool or Actor fault; stopped")


def judges() -> None:
    judge = load("expanded_blind_judges", REPO / "experiments" / "ab-three-20260919" / "judge.py")
    judge.runner = champion
    judge.ROOT = ROOT
    judge.JUDGES_ROOT = ROOT / "judges"
    original = judge.make_prompt

    def make_prompt(case_id: str, repeat: int, x_arm: str, y_arm: str) -> str:
        changed = set()
        for arm in ("A", "B"):
            result = json.loads((ROOT / "runs" / case_id / f"repeat-{repeat}" / arm / "result.json").read_text(encoding="utf-8"))
            changed.update(result["changed_files"])
        seed = ROOT / "seeds" / case_id
        sources = "\n".join(
            f"FILE {name}\n{judge.read(seed / name)}" for name in sorted(changed) if (seed / name).is_file()
        )
        return original(case_id, repeat, x_arm, y_arm) + (
            "\nCOMPLETE BASE FILES FOR CHANGED PATHS\n" + sources
            + "\nJudge only the supplied task, patches, verification, and base files. Do not use tools. "
              "A missing test is not itself a contract failure; identify a concrete violated behavior.\n"
        )

    judge.make_prompt = make_prompt
    sys.argv = ["judge"]
    judge.main()


if __name__ == "__main__":
    {"prepare": prepare, "preflight": preflight, "actors": actors, "judges": judges}[sys.argv[1]]()
