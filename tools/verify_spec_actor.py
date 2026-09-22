#!/usr/bin/env python3
"""Native Actor -> packaged hook -> real Provider/MCP -> next Actor inference.

This is a delivery/contract check, not a taste comparison. A tool fault stops
the process immediately and invalidates the trial. Only small result files remain.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from masters_nudge.providers import _provider_process_kwargs
from masters_nudge.plugin_inventory import package_files
from masters_nudge.storage import Journal

SOURCE = '''def new_job():
    return {"status": "pending", "is_done": False}

def finish(job):
    job["status"] = "done"
    job["is_done"] = True
'''
TASK = '''在 job.py 增加 label(job)，工作完成時回傳 done，否則回傳 pending。
保留 new_job() 與 finish(job) 的呼叫介面；工作完成與否仍由 finish(job) 改變。
請直接使用 apply_patch 修改程式，執行一個涵蓋完成前後的驗證即可。
最後簡短回報結果。如果過程收到 Masters’ Nudge，說明收到的疑問以及你的處理。
'''


@contextmanager
def actor_workspace(result_directory: Path):
    # Python's private TemporaryDirectory uses OWNER RIGHTS on Windows. Files
    # created there by the sandbox account become unreadable to the Provider.
    # An ordinary directory inherits the result directory's user permissions.
    parent = result_directory.resolve()
    workspace = parent / "workspace"
    workspace.mkdir()
    try:
        yield workspace
    finally:
        if workspace.resolve().parent != parent:
            raise ValueError("測試工作區路徑已改變，停止清理")
        shutil.rmtree(workspace)


def prepare_case(workspace: Path, *, split_state: bool = False, fixture: Path | None = None):
    if fixture is not None:
        case = json.loads(fixture.read_text(encoding="utf-8"))
        files, task, verify = case["files"], case["task"], case["verify"]
    else:
        files = {"job.py": "from state import new_job, finish\n" if split_state else SOURCE}
        if split_state:
            files["state.py"] = SOURCE
        task = TASK
        verify = 'from job import new_job, finish, label; j=new_job(); assert label(j)=="pending"; finish(j); assert label(j)=="done"'
    for name, content in files.items():
        path = (workspace / name).resolve()
        if not path.is_relative_to(workspace.resolve()) or ".git" in path.relative_to(workspace.resolve()).parts:
            raise ValueError("測試來源必須位於工作區內")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return files, task, verify


def capture_sources(workspace: Path):
    files, errors = {}, {}
    for path in workspace.rglob("*.py"):
        relative = path.relative_to(workspace)
        if ".git" in relative.parts:
            continue
        try:
            files[relative.as_posix()] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors[relative.as_posix()] = f"{type(exc).__name__}: {exc}"
    return files, errors


def runtime_helpers(binary: Path, *, windows: bool) -> dict:
    if not windows:
        return {}
    runner = next((path for path in (binary.parent / "codex-command-runner.exe",
                  binary.parent / "codex-resources/codex-command-runner.exe") if path.is_file()), None)
    if runner is None:
        raise ValueError("Actor 缺少 codex-command-runner.exe，不能啟動 Windows 沙盒")
    return {runner.name: {"path": str(runner), "sha256": hashlib.sha256(runner.read_bytes()).hexdigest()}}


def trial_invalid_reason(fault: str, exit_code: int, batches: list, attempts: list, *, require_attempts: bool = True) -> str:
    if fault:
        return fault
    if exit_code:
        return f"Actor 或啟動環境結束碼 {exit_code}"
    if require_attempts and not batches:
        return "未收到原生 PostToolUse，沒有測到工具"
    if require_attempts and not attempts:
        return "沒有明確修改觸發 Provider，沒有測到完整工具"
    if any(attempt["outcome"] not in ("feedback", "silence") for attempt in attempts):
        return "Provider 判斷故障、中斷或被取代，本輪無效"
    return ""


def packaged_hook_overrides(package: Path) -> list[str]:
    def toml(value):
        if isinstance(value, dict):
            return "{" + ",".join(json.dumps(key) + "=" + toml(item) for key, item in value.items()) + "}"
        if isinstance(value, list):
            return "[" + ",".join(toml(item) for item in value) + "]"
        if isinstance(value, str):
            value = value.replace("${PLUGIN_ROOT}", str(package.resolve()).replace("\\", "/"))
        return json.dumps(value)
    hooks = json.loads((package / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
    servers = json.loads((package / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]
    result = [argument for name, config in servers.items()
              for argument in ("-c", f"mcp_servers.{name}={toml(config)}")]
    result.extend(argument for event, groups in hooks.items()
                  for argument in ("-c", f"hooks.{event}={toml(groups)}"))
    return result


def arm_hook_arguments(package: Path, arm: str) -> list[str]:
    if arm == "direct":
        return []
    if arm == "nudge":
        return packaged_hook_overrides(package)
    raise ValueError(f"未知測試臂：{arm}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--actor-bin", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--verification-python", type=Path, default=Path(sys.executable))
    parser.add_argument("--provider-model", help="Only override the Provider, for explicit fault-path tests")
    parser.add_argument("--mode", choices=("formal", "production"), default="formal")
    parser.add_argument("--arm", choices=("direct", "nudge"), default="nudge")
    parser.add_argument("--human-output", action="store_true", help="Capture visible hook status from the human CLI renderer")
    cases = parser.add_mutually_exclusive_group()
    cases.add_argument("--split-state", action="store_true", help="Keep state ownership in a separate source file")
    cases.add_argument("--fixture", type=Path, help="JSON containing files, task and independent verification")
    args = parser.parse_args()
    binary = args.actor_bin.resolve()
    if not binary.is_file():
        raise SystemExit("Actor 執行檔不存在")
    try:
        helpers = runtime_helpers(binary, windows=os.name == "nt")
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if (args.output / "result.json").exists():
        raise SystemExit("結果檔已存在，不覆蓋先前證據")
    verify_python = args.verification_python.resolve()
    if os.name == "nt":
        preflight = subprocess.run([str(binary), "sandbox", str(verify_python), "-B", "-c", "print('ready')"],
                                  capture_output=True, text=True, timeout=30, **_provider_process_kwargs())
        if preflight.returncode:
            raise SystemExit(f"驗證用 Python 無法在 Actor 沙盒啟動：{preflight.stderr}")
    args.output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="nudge-native-actor-") as raw, actor_workspace(args.output) as workspace:
        root = Path(raw)
        subprocess.run(["git", "init", "-q", str(workspace)], check=True)
        initial_files, task, verify = prepare_case(workspace, split_state=args.split_state, fixture=args.fixture)
        source = initial_files.get("job.py")
        data = root / "data"
        data.mkdir()
        (data / "config.json").write_text(json.dumps({"provider": "openai", "model": args.provider_model or args.model}))
        hook = ROOT / "plugins/masters-nudge/hook_entry.py"
        package_hashes = {name: hashlib.sha256((hook.parent / name).read_bytes()).hexdigest() for name in package_files()}
        hook_arguments = arm_hook_arguments(hook.parent, args.arm)
        command = [str(binary), "-c", "project_doc_max_bytes=0", "-c", "features.multi_agent=false",
                   "-c", 'windows.sandbox="elevated"',
                   *(["--enable", "hooks", "--disable", "plugins", *hook_arguments] if hook_arguments else ["--disable", "hooks", "--disable", "plugins"]),
                   "exec", "--ignore-user-config", "--ignore-rules", "--dangerously-bypass-hook-trust",
                   "--skip-git-repo-check", "--ephemeral", *([] if args.human_output else ["--json"]), "-s", "workspace-write",
                   "-m", args.model, "-C", str(workspace), "-o", str(root / "final.txt"), "-"]
        env = {**os.environ, "MASTERS_NUDGE_ACTIVE": "0", "MASTERS_NUDGE_TEST_MODE": "1" if args.mode == "formal" else "0",
               "PLUGIN_ROOT": str(hook.parent),
               "MASTERS_NUDGE_DATA_DIR": str(data), "MASTERS_NUDGE_RUNTIME_DIR": str(hook.parent)}
        task += f'\n驗證環境：Python 已安裝於 {verify_python}；用此完整路徑搭配 -B 執行，不需安裝環境或清理檔案。\n'
        started = time.monotonic()
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, encoding="utf-8", cwd=workspace, env=env, **_provider_process_kwargs())
        stdout, stderr = [], []
        def collect(stream, destination):
            for line in stream:
                destination.append(line)
        workers = [threading.Thread(target=collect, args=(process.stdout, stdout)),
                   threading.Thread(target=collect, args=(process.stderr, stderr))]
        for worker in workers:
            worker.start()
        process.stdin.write(task)
        process.stdin.close()
        invalid = ""
        while process.poll() is None:
            if args.mode == "formal" and (data / "error.log").exists():
                invalid = (data / "error.log").read_text(encoding="utf-8")
                break
            if time.monotonic() - started > 240:
                invalid = "Actor 超時"
                break
            time.sleep(0.2)
        if invalid:
            # Our reader threads own the pipes; terminate this test's process tree.
            if os.name == "nt":
                subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"], capture_output=True,
                               timeout=10, **_provider_process_kwargs())
            else:
                process.kill()
        process.wait(timeout=15)
        for worker in workers:
            worker.join(timeout=5)
        # Preserve original events before inspecting Actor-created files: a host
        # read failure must not erase the run's evidence with the temporary tree.
        (args.output / ("actor.txt" if args.human_output else "actor.jsonl")).write_text("".join(stdout), encoding="utf-8")
        (args.output / "stderr.txt").write_text("".join(stderr), encoding="utf-8")
        attempts = Journal(data).recent() if (data / "feedback.sqlite3").exists() else []
        batches = []
        if (data / "feedback.sqlite3").exists():
            with Journal(data).connect() as db:
                batches = [dict(row) for row in db.execute("SELECT * FROM batches ORDER BY received")]
        if not invalid and (data / "error.log").exists():
            invalid = (data / "error.log").read_text(encoding="utf-8")
        invalid = trial_invalid_reason(invalid, process.returncode, batches, attempts,
                                       require_attempts=args.arm == "nudge")
        final_files, capture_errors = capture_sources(workspace)
        if capture_errors:
            invalid = invalid or "無法完整保存 Actor 成品：" + json.dumps(capture_errors, ensure_ascii=False)
        final_source = final_files.get("job.py")
        verification = None
        if (not invalid or args.mode == "production") and process.returncode == 0:
            verification = subprocess.run([sys.executable, "-B", "-c", verify],
                cwd=workspace, capture_output=True, text=True, timeout=10)
        report = {"scope": "native Actor and complete packaged tool" if args.arm == "nudge" else "native Actor without Masters' Nudge",
                  "arm": args.arm, "binary": str(binary),
                  "runtime_helpers": helpers, "command": command,
                  "mode": args.mode, "provider_model": args.provider_model or args.model,
                  "package_sha256": package_hashes,
                  "spec_sha256": hashlib.sha256((ROOT / "SPEC.zh-TW.md").read_bytes()).hexdigest(),
                  "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "model": args.model,
                  "prompt": task, "initial_source": source, "final_source": final_source,
                  "initial_files": initial_files, "final_files": final_files, "verification": verify,
                  "capture_errors": capture_errors,
                  "fixture": str(args.fixture) if args.fixture else None,
                  "split_state": args.split_state,
                  "state_source": (workspace / "state.py").read_text(encoding="utf-8") if args.split_state else None,
                  "elapsed_seconds": time.monotonic() - started, "exit_code": process.returncode,
                  "invalid": invalid, "attempts": attempts, "batches": batches,
                  "contract_exit_code": verification.returncode if verification else None,
                  "contract_stderr": verification.stderr if verification else None,
                  "actor_final": (root / "final.txt").read_text(encoding="utf-8") if (root / "final.txt").exists() else ""}
        (args.output / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(args.output), "invalid": invalid, "attempts": len(attempts),
                          "batches": len(batches), "contract_exit_code": report["contract_exit_code"]}, ensure_ascii=True))
        return int(bool(invalid) or (args.arm == "nudge" and not attempts) or report["contract_exit_code"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
