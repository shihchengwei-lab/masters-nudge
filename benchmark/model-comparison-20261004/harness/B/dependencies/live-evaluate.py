"""Arm-independent evaluation records and immutable manifests.

Use `verify` before executing checks. A result carries the exact evaluator and
patch hashes; missing checks never become passes. `seal` is an explicit release
step, not a side effect of running checks.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tracked_files():
    return sorted(p for p in ROOT.rglob("*") if p.is_file()
                  and p.name != "manifest.json" and "__pycache__" not in p.parts)


def inventory():
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in tracked_files()}


def validate_contracts():
    errors = []
    cases = read(ROOT / "cases.json")
    for case in cases:
        folder = ROOT / "cases" / case["id"]
        if digest(folder / "task.md") != case["task_sha256"]:
            errors.append(case["id"] + ": task hash differs")
        path = folder / "contract.json"
        if not path.exists():
            errors.append(case["id"] + ": missing contract map")
            continue
        spec = read(path)
        lines = (folder / "task.md").read_text(encoding="utf-8").splitlines()
        checks = {check["id"] for check in spec["checks"]}
        ids = set()
        for clause in spec["requirements"]:
            if clause["id"] in ids:
                errors.append(case["id"] + ": duplicate clause ID")
            ids.add(clause["id"])
            excerpt = "\n".join(lines[n - 1] for n in clause["source_lines"])
            if excerpt != clause["source_text"]:
                errors.append(case["id"] + ": stale source " + clause["id"])
            if not clause["checks"] or not set(clause["checks"]) <= checks:
                errors.append(case["id"] + ": missing check " + clause["id"])
        if spec.get("unresolved"):
            errors.append(case["id"] + ": unresolved contract")
        for check in spec["checks"]:
            if not any(check["id"] in r["checks"] for r in spec["requirements"]):
                errors.append(case["id"] + ": check without contract " + check["id"])
    return errors


def verify():
    manifest = read(ROOT / "manifest.json")
    actual = inventory()
    expected = manifest["files"]
    changed = sorted(p for p in actual.keys() | expected.keys()
                     if actual.get(p) != expected.get(p))
    errors = validate_contracts()
    if changed or errors:
        raise ValueError({"changed_files": changed, "contract_errors": errors})
    return digest(ROOT / "manifest.json")


def score(case_id, patch, evidence):
    evaluator = verify()
    spec = read(ROOT / "cases" / case_id / "contract.json")
    patch_hash = digest(patch)
    if evidence["case"] != case_id or evidence["patch_sha256"] != patch_hash:
        raise ValueError("Evidence does not describe this patch and case")
    if evidence["evaluator_sha256"] != evaluator:
        raise ValueError("Evidence belongs to a different evaluator")
    expected = {c["id"] for c in spec["checks"]}
    checks = evidence["checks"]
    if set(checks) - expected:
        raise ValueError("Unregistered checks cannot affect the score")
    allowed = {"pass", "fail", "environment_error", "missing"}
    if any(x not in allowed for x in checks.values()):
        raise ValueError("Unknown check status")
    clauses = {r["id"]: [checks.get(c, "missing") for c in r["checks"]]
               for r in spec["requirements"]}
    missing = sorted(expected - checks.keys())
    failed_checks = [cid for cid, state in checks.items() if state == "fail"]
    # A shared suite failure does not mean every requirement it covers failed.
    # Keep the failed assertion names in evidence; this is a tracing map, not an
    # invented count of violated clauses.
    affected = [rid for rid, states in clauses.items() if "fail" in states]
    pending = [rid for rid, states in clauses.items()
               if any(s in {"environment_error", "missing"} for s in states)]
    # A reproducible contractual failure is still a failure if another check is pending.
    status = "fail" if failed_checks else "incomplete" if pending or missing else "pass"
    execution = evidence.get("execution_review")
    execution_status = "unreviewed"
    if execution is not None:
        if execution.get("status") not in {"pass", "fail", "environment_error"}:
            raise ValueError("Unknown execution contract status")
        if execution.get("patch_sha256") != patch_hash or not execution.get("evidence"):
            raise ValueError("Execution review must reference this delivery and its records")
        execution_status = execution["status"]
    completed = (False if status == "fail" or execution_status == "fail" else
                 True if status == "pass" and execution_status == "pass" else None)
    return {"case": case_id, "patch_sha256": patch_hash,
            "evaluator_sha256": evaluator, "status": status,
            "execution_contract_status": execution_status, "task_completed": completed,
            "failed_checks": failed_checks, "requirements_linked_to_failed_checks": affected,
            "pending_requirements": pending,
            "checks": checks, "evidence": evidence.get("logs", [])}


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("audit")
    commands.add_parser("verify")
    seal = commands.add_parser("seal")
    seal.add_argument("--version", required=True)
    seal.add_argument("--validation", type=Path, required=True)
    grade = commands.add_parser("score")
    grade.add_argument("case")
    grade.add_argument("patch", type=Path)
    grade.add_argument("evidence", type=Path)
    grade.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "audit":
        errors = validate_contracts()
        print(json.dumps({"errors": errors}, ensure_ascii=False))
        raise SystemExit(bool(errors))
    if args.command == "verify":
        print(verify())
    elif args.command == "seal":
        errors = validate_contracts()
        validation = read(args.validation)
        if errors or not validation.get("ready"):
            raise ValueError({"contract_errors": errors, "validation": validation})
        files = inventory()
        if validation.get("files") != files:
            raise ValueError("Validation does not cover current evaluator files")
        write_new(ROOT / "manifest.json", {"version": args.version, "files": files,
                  "validation_sha256": digest(args.validation)})
        print(verify())
    elif args.command == "score":
        result = score(args.case, args.patch, read(args.evidence))
        write_new(args.output, result)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
