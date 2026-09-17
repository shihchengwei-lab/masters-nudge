#!/usr/bin/env python3
"""Replay native Provider reads after a workspace fix; not an Actor/effect trial."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from masters_nudge.contracts import MATERIAL_MAX_CHARS, SOURCES, json_text
from masters_nudge.providers import _provider_process_kwargs
from tools.verify_spec_actor import actor_workspace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--actor-bin", type=Path, required=True)
    parser.add_argument("--verification-python", type=Path, required=True)
    args = parser.parse_args()
    original = json.loads(args.record.read_text(encoding="utf-8"))
    attempt, = original["attempts"]
    packet = json.loads(attempt["detail"]["packet"])
    files = dict(original["initial_files"])
    changes = [event for batch in original["batches"] for event in json.loads(batch["payload"])
               if event["tool_name"] == "apply_patch"]
    change, = changes
    patch = change["tool_input"]["command"].splitlines()
    assert patch[0] == "*** Begin Patch" and patch[-1] == "*** End Patch"
    assert patch[1].startswith("*** Add File: ") and all(line.startswith("+") for line in patch[2:-1])
    original_workspace = Path(packet["workspace"]).resolve()
    added = (original_workspace / patch[1].removeprefix("*** Add File: ")).resolve().relative_to(original_workspace).as_posix()
    files[added] = "\n".join(line[1:] for line in patch[2:-1]) + "\n"
    calls = [{"name": entry["name"], "arguments": entry["arguments"]} for entry in attempt["detail"]["trace"]
             if entry["name"] in ("search_repo", "read_file")]
    assert calls
    # This extra range read is an explicit capability assertion, not a choice
    # attributed to the Provider in the original run.
    calls.append({"name": "read_file", "arguments": {"path": added, "start_line": 1, "end_line": 6}})
    used = len(json_text({source: packet[source] for source in SOURCES}))
    remaining = MATERIAL_MAX_CHARS - used
    args.output.mkdir(parents=True, exist_ok=False)
    with actor_workspace(args.output) as workspace:
        subprocess.run(["git", "init", "-q", str(workspace)], check=True)
        # Create all fixture files as the native sandbox identity, not as the
        # host user who will run the read-only service.
        create = "import json,sys; from pathlib import Path; files=json.load(sys.stdin); [(Path(k).parent.mkdir(parents=True,exist_ok=True),Path(k).write_text(v,encoding='utf-8')) for k,v in files.items()]; print('created')"
        for name in files:
            assert (workspace / name).resolve().is_relative_to(workspace)
        writer = subprocess.run([str(args.actor_bin.resolve()), "sandbox", "-c", 'sandbox_mode="workspace-write"',
                                 "-c", 'windows.sandbox="elevated"', str(args.verification_python.resolve()), "-B", "-c", create],
                                input=json_text(files), text=True, encoding="utf-8", cwd=workspace,
                                capture_output=True, timeout=30, **_provider_process_kwargs())
        audit = args.output.resolve() / "reads.jsonl"
        requests = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]
        requests.extend({"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": call}
                        for i, call in enumerate(calls, 3))
        service = ROOT / "plugins/masters-nudge/masters_nudge/read_only_repo_mcp.py"
        result = subprocess.run([sys.executable, str(service), "--root", str(workspace), "--budget", str(remaining), "--audit", str(audit)],
                                input="\n".join(map(json_text, requests)) + "\n", capture_output=True,
                                text=True, encoding="utf-8", timeout=30, **_provider_process_kwargs()) if writer.returncode == 0 else None
        replies = [json.loads(line) for line in result.stdout.splitlines()] if result and result.returncode == 0 else []
        records = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()] if audit.exists() else []
        exact = all(line["text"] == files[line["path"]].splitlines()[line["line"] - 1]
                    for record in records for line in record["lines"])
        checks = {"sandbox_created_files": writer.returncode == 0,
                  "service_completed": result is not None and result.returncode == 0,
                  "only_two_tools": len(replies) >= 2 and {tool["name"] for tool in replies[1]["result"]["tools"]} == {"search_repo", "read_file"},
                  "every_call_recorded": len(records) == len(calls) + 1,
                  "no_read_fault": bool(records) and not any(record["fault"] for record in records),
                  "new_file_range_returned": bool(records) and [line["line"] for line in records[-1]["lines"]] == list(range(1, 7)),
                  "verbatim_file_lines": exact, "shared_budget": used + sum(len(record["text"]) for record in records) <= MATERIAL_MAX_CHARS}
        report = {"scope": "recorded MCP read regression; no new Provider or Actor judgment", "record": str(args.record),
                  "record_sha256": hashlib.sha256(args.record.read_bytes()).hexdigest(), "calls": calls,
                  "additional_capability_call": len(calls) - 1, "initial_material_chars": used,
                  "remaining_chars": remaining, "checks": checks, "passed": all(checks.values()),
                  "writer_stdout": writer.stdout, "writer_stderr": writer.stderr,
                  "service_stdout": result.stdout if result else "", "service_stderr": result.stderr if result else ""}
        (args.output / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json_text({"output": str(args.output), "checks": checks}))
    return int(not all(checks.values()))


if __name__ == "__main__":
    raise SystemExit(main())
