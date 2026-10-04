"""Run all twelve sealed Round 11 B1/B2 cases with committed product b6ec0ef."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parent
PARENT = Path(r"D:\masters-nudge-benchmark\round-11-three-arm-20260927")
PRODUCT = Path(r"C:\Users\kk789\Desktop\GH_repos\masters-nudge")
CAL = Path(r"D:\masters-nudge-benchmark\round-10-calibration")
EVALUATION = PRODUCT / "benchmark/formal-v11/evaluation-v3"
HARNESS = Path(r"D:\masters-nudge-benchmark\round-10-b-quota2-20260927\run.py")
PACKAGE = ROOT / "frozen-plugin"
SELECTED = tuple(json.loads((PARENT / "plan.json").read_text(encoding="utf-8"))["cases"])
PRODUCT_COMMIT = "8f6db77147bf3e0b1855bddd82dcc422be086a37"
PROMPT_SHA256 = "213316ace53739c52f54cb8a48c413c1260848be246b97714ab0a36867bef4c0"
BINARY = Path(r"C:\Users\kk789\AppData\Local\OpenAI\Codex\bin\faa963e871dd422c\codex.exe")
BINARY_SHA256 = "8f0554ede25bbc5450921897c468b2e84635aa513c5017457997af0954581f49"
EXPECTED_PACKAGE_DIFF = {
    "buddy-prompt.txt", "nudge-schema.json", "masters_nudge/contracts.py",
    "masters_nudge/prompting.py", "masters_nudge/provider_contract.py",
}
sys.path.insert(0, str(EVALUATION))
import evaluate


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def textsha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + ".tmp")
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pending.replace(path)


def files(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in root.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def neutral_prompt(cid):
    path = PARENT / "runs" / cid / "B1" / "prompt.txt"
    value = path.read_text(encoding="utf-8")
    assert textsha(value) == read(PARENT / "plan.json")["cases"][cid]["B_prompt_sha256"]
    return value


def prepare():
    old = read(PARENT / "plan.json")
    assert old["status"] == "sealed" and old["feedback_limit"] == 3
    assert len(SELECTED) == 12
    assert evaluate.verify() == "f37b57bb8f488be4f876268125f6d1994ad03691e83cab740fdb2047bb726a28"
    assert sha(BINARY) == BINARY_SHA256
    assert sha(HARNESS) == old["harness_sha256"]
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PRODUCT, text=True).strip() == PRODUCT_COMMIT
    assert not subprocess.check_output(["git", "diff", "HEAD", "--", "plugins/masters-nudge"], cwd=PRODUCT)
    source = PRODUCT / "plugins/masters-nudge/buddy-prompt.txt"
    assert sha(source) == PROMPT_SHA256
    if not PACKAGE.exists():
        shutil.copytree(PRODUCT / "plugins/masters-nudge", PACKAGE,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    original = files(PARENT / "frozen-plugin")
    candidate = files(PACKAGE)
    assert set(candidate) == set(original)
    assert {name for name in candidate if candidate[name] != original[name]} == EXPECTED_PACKAGE_DIFF
    assert candidate["buddy-prompt.txt"] == sha(source)
    assert candidate == files(PRODUCT / "plugins/masters-nudge")
    cases = {cid: old["cases"][cid] for cid in SELECTED}
    assert all((PARENT / "runs" / cid / arm / "score-v3.json").exists()
               for cid in cases for arm in ("A1", "A2", "C1", "C2"))
    for cid in cases:
        neutral_prompt(cid)
        assert cases[cid]["A1_result_sha256"] == sha(CAL / "state" / cid / "actor.json")
    plan = {
        "name": "Round 11 committed task-framed Buddy full B", "created_utc": datetime.now(timezone.utc).isoformat(),
        "product_commit": PRODUCT_COMMIT,
        "baseline_root": str(PARENT), "baseline_plan_sha256": sha(PARENT / "plan.json"),
        "baseline_package_hashes": original, "package_hashes": candidate,
        "changed_package_files": sorted(EXPECTED_PACKAGE_DIFF),
        "evaluator_sha256": evaluate.verify(), "harness_sha256": sha(HARNESS),
        "codex_binary": str(BINARY), "codex_binary_sha256": BINARY_SHA256,
        "baseline_codex_binary_sha256": old["codex_binary_sha256"],
        "codex_cli_version": "0.158.0-alpha.2.1",
        "actor_model": "gpt-6-sol", "actor_reasoning": "medium",
        "provider_model": "gpt-6-sol", "provider_reasoning": "medium",
        "feedback_limit": 3, "workers": 2, "actor_wall_timeout_seconds": 1800,
        "new_arms": ["B1", "B2"], "trials_per_case": 2,
        "cases": cases, "sample_reason": "All twelve sealed Round 11 tasks, each with B1 and B2.",
        "retry_policy": "Preserve every scheduled B trial; retry infrastructure faults only.",
    }
    path = ROOT / "plan.json"
    if path.exists():
        existing = read(path)
        assert {k: v for k, v in existing.items() if k != "created_utc"} == {
            k: v for k, v in plan.items() if k != "created_utc"}
        return existing
    save(path, plan)
    return plan


def wsl(path):
    value = Path(path).resolve().as_posix()
    assert value[1:3] == ":/"
    return "/mnt/" + value[0].lower() + value[2:]


def verify_delivery(cid, arm, patch):
    output = ROOT / "evaluation-v3" / cid / arm
    output.parent.mkdir(parents=True, exist_ok=True)
    if (output / "evidence.json").exists():
        evidence = read(output / "evidence.json")
        assert evidence["patch_sha256"] == sha(patch)
        assert evidence["evaluator_sha256"] == evaluate.verify()
        return evidence
    case = next(c for c in read(EVALUATION / "cases.json") if c["id"] == cid)
    if case["environment"]["container"]:
        command = ["wsl.exe", "-u", "root", "--exec", "python3", wsl(EVALUATION / "container_checks.py"),
                   cid, wsl(patch), wsl(output)]
    else:
        command = [sys.executable, "-B", str(EVALUATION / "native_checks.py"), cid,
                   str(patch), str(output), "--calibration-root", str(CAL)]
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    process = subprocess.run(command, env=env, capture_output=True, timeout=2400,
                             creationflags=subprocess.CREATE_NO_WINDOW)
    (output.parent / (arm + "-console.txt")).write_bytes(process.stdout + b"\n" + process.stderr)
    if process.returncode:
        raise RuntimeError(process.stderr.decode(errors="replace")[-2500:])
    evidence = read(output / "evidence.json")
    if evidence.get("environment_error"):
        raise RuntimeError(evidence["environment_error"])
    assert evidence["evaluator_sha256"] == evaluate.verify()
    assert evidence["patch_sha256"] == sha(patch)
    return evidence


def verification(cid, arm, meta, artifact, added_tests):
    evidence = verify_delivery(cid, arm, artifact / "final.patch")
    good = bool(evidence["checks"]) and all(x == "pass" for x in evidence["checks"].values())
    return [{"exit_code": 0 if good else 1, "reward": "1" if good else "0",
             "passed": 1, "elapsed_seconds": evidence["elapsed_seconds"],
             "checks": evidence["checks"], "evaluator_sha256": evidence["evaluator_sha256"],
             "log": str(ROOT / "evaluation-v3" / cid / arm / "evidence.json")}]


def load_runner(plan):
    spec = importlib.util.spec_from_file_location("b_only_harness", HARNESS)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.OUT = ROOT
    runner.PACKAGE = PACKAGE
    runner.STOP = threading.Event()
    runner.resolve_codex_bin = lambda: plan["codex_binary"]
    runner.prompts = lambda cid: ("", neutral_prompt(cid))
    runner.verification = verification
    return runner


def status(plan):
    complete, running = [], []
    for cid in plan["cases"]:
        for arm in ("B1", "B2"):
            folder = ROOT / "runs" / cid / arm
            if (folder / "result.json").exists():
                r = read(folder / "result.json")
                complete.append({"case": cid, "arm": arm, "fault": r["execution_fault"],
                                 "seconds": r["actor_elapsed_seconds"],
                                 "fixed_checks_pass": r["contract_passed"]})
            elif (folder / "running.json").exists():
                running.append({"case": cid, "arm": arm, **read(folder / "running.json")})
    return {"complete": len(complete), "expected": len(plan["cases"]) * 2, "results": complete, "running": running}


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "run", "status"])
    parser.add_argument("--cases", nargs="*")
    parser.add_argument("--arms", nargs="+", choices=["B1", "B2"])
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    plan = prepare()
    if args.action == "prepare":
        print(json.dumps({"stage": "prepared", "cases": len(plan["cases"]),
                          "new_runs": len(plan["cases"]) * 2, "changed_files": plan["changed_package_files"],
                          "prompt_sha256": plan["package_hashes"]["buddy-prompt.txt"]}))
    elif args.action == "status":
        print(json.dumps(status(plan), ensure_ascii=False))
    else:
        selected = args.cases or list(plan["cases"])
        assert set(selected) <= set(plan["cases"])
        runner = load_runner(plan)
        if args.arms:
            runner.ARMS = args.arms
        save(ROOT / "orchestrator.json", {"pid": os.getpid(),
                                           "started_utc": datetime.now(timezone.utc).isoformat()})
        errors = []
        with ThreadPoolExecutor(max_workers=plan["workers"]) as pool:
            pending = {pool.submit(runner.run_case, cid, plan): cid for cid in selected}
            for future in as_completed(pending):
                try:
                    future.result()
                except Exception as exc:
                    row = {"case": pending[future], "error": str(exc)}
                    errors.append(row)
                    save(ROOT / "errors" / (pending[future] + ".json"), row)
                    print(json.dumps(row, ensure_ascii=False), flush=True)
        save(ROOT / "execution-summary.json", {**status(plan), "errors": errors})
        if errors:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
