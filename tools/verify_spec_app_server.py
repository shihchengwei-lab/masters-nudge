#!/usr/bin/env python3
"""Observe native hook entries and interruption, using the existing Codex binary.

This driver never injects Provider material or feedback. Fault trials deliberately
select an invalid Provider model and cannot be used to score tool effectiveness.
Protocol: https://learn.chatgpt.com/docs/app-server
"""
import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import queue
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from masters_nudge.plugin_inventory import package_files
from masters_nudge.providers import _provider_process_kwargs
from tools.verify_spec_actor import SOURCE, TASK, actor_workspace, packaged_hook_overrides, runtime_helpers


class RpcClient:
    def __init__(self, stream, incoming):
        self.stream, self.incoming = stream, incoming
        self.events, self.sent = [], []
        self.next_id = 1

    def send(self, message):
        self.sent.append(message)
        self.stream.write(json.dumps(message, ensure_ascii=True) + "\n")
        self.stream.flush()

    def receive(self, timeout):
        message = self.incoming.get(timeout=timeout)
        if message is None:
            raise RuntimeError("Codex 事件連線已關閉")
        if isinstance(message, Exception):
            raise RuntimeError(f"無法讀取 Codex 事件：{message}")
        if "method" in message:
            self.events.append(message)
            if "id" in message:
                raise RuntimeError(f"出現未授權的伺服器要求：{message['method']}")
        return message

    def request(self, method, params, timeout=45):
        request_id = self.next_id
        self.next_id += 1
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"等待 {method} 回覆超時")
            try:
                message = self.receive(remaining)
            except queue.Empty as exc:
                raise TimeoutError(f"等待 {method} 回覆超時") from exc
            if message.get("id") == request_id and "method" not in message:
                if "error" in message:
                    raise RuntimeError(json.dumps(message["error"], ensure_ascii=False))
                return message["result"]

    def wait(self, predicate, timeout):
        deadline = time.monotonic() + timeout
        while not predicate():
            if time.monotonic() >= deadline:
                raise TimeoutError("原生事件驗證超時，不能當作完成")
            try:
                self.receive(min(0.2, max(0, deadline - time.monotonic())))
            except queue.Empty:
                continue


def hook_outputs(events, *, kind, turn_id=None):
    return [entry["text"] for event in events if event.get("method") == "hook/completed"
            for params in [event["params"]]
            if turn_id is None or params.get("turnId") == turn_id
            if params["run"].get("eventName") == "postToolBatch"
            for entry in params["run"].get("entries", []) if entry["kind"] == kind]


def test_hook_state(listing, reviewed_commands):
    state, selected = {}, []
    for group in listing["data"]:
        for hook in group["hooks"]:
            if hook["source"] == "sessionFlags" and hook.get("command") in reviewed_commands:
                state[hook["key"]] = {"enabled": True, "trusted_hash": hook["currentHash"]}
                selected.append(hook["eventName"])
            elif not hook["isManaged"]:
                state[hook["key"]] = {"enabled": False}
    if sorted(selected) != ["postToolBatch", "userPromptSubmit"]:
        raise RuntimeError("未辨認出兩個已核對的插件入口，不啟動 Actor")
    return state


def read_journal(data):
    """Observation must not create or migrate the journal under test."""
    path = data / "feedback.sqlite3"
    if not path.exists():
        return {"attempts": [], "rounds": [], "batches": []}
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        result = {table: [dict(row) for row in db.execute(f"SELECT * FROM {table}")]
                  for table in ("attempts", "rounds", "batches")}
    for row in result["attempts"]:
        row["detail"] = json.loads(row["detail"])
    return result


def completed_turn(events, turn_id):
    return next((event["params"]["turn"] for event in events
                 if event.get("method") == "turn/completed"
                 and event["params"]["turn"]["id"] == turn_id), None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--actor-bin", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verification-python", type=Path, required=True)
    parser.add_argument("--mode", choices=("normal", "fault", "interrupt"), required=True)
    parser.add_argument("--model", default="gpt-5.6-sol")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit("結果目錄已存在，不覆蓋先前證據")
    binary = args.actor_bin.resolve()
    helpers = runtime_helpers(binary, windows=os.name == "nt")
    package = ROOT / "plugins/masters-nudge"
    output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="nudge-app-server-") as raw, actor_workspace(output) as workspace:
        root = Path(raw)
        data = root / "data"
        data.mkdir()
        subprocess.run(["git", "init", "-q", str(workspace)], check=True)
        (workspace / "job.py").write_text(SOURCE, encoding="utf-8")
        provider_model = "masters-nudge-invalid-model-for-fault-test" if args.mode == "fault" else args.model
        (data / "config.json").write_text(json.dumps({"provider": "openai", "model": provider_model}), encoding="utf-8")
        command = [str(binary), "-c", "project_doc_max_bytes=0", "-c", "features.multi_agent=false",
                   "-c", 'windows.sandbox="elevated"', "-c", 'web_search="disabled"',
                   "--enable", "hooks", "--disable", "plugins", *packaged_hook_overrides(package),
                   "app-server", "--listen", "stdio://"]
        env = {**os.environ, "MASTERS_NUDGE_ACTIVE": "0", "MASTERS_NUDGE_TEST_MODE": "0",
               "PLUGIN_ROOT": str(package), "MASTERS_NUDGE_DATA_DIR": str(data),
               "MASTERS_NUDGE_RUNTIME_DIR": str(package)}
        process = subprocess.Popen(command, cwd=workspace, env=env, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                                   **_provider_process_kwargs())
        incoming = queue.Queue()
        client = RpcClient(process.stdin, incoming)
        def collect_events():
            try:
                with (output / "events.jsonl").open("w", encoding="utf-8") as stream:
                    for line in process.stdout:
                        stream.write(line)
                        stream.flush()
                        incoming.put(json.loads(line))
            except Exception as exc:
                incoming.put(exc)
            finally:
                incoming.put(None)
        def collect_errors():
            with (output / "stderr.txt").open("w", encoding="utf-8") as stream:
                for line in process.stderr:
                    stream.write(line)
                    stream.flush()
        workers = [threading.Thread(target=collect_events), threading.Thread(target=collect_errors)]
        for worker in workers:
            worker.start()
        task = TASK + f"驗證用 Python 已安裝於 {args.verification_python.resolve()}，使用完整路徑及 -B，不需安裝環境。"
        started = time.monotonic()
        report = {"scope": "native app-server and packaged tool; delivery only", "mode": args.mode,
                  "command": command, "model": args.model, "provider_model": provider_model,
                  "runtime_helpers": helpers, "prompt": task, "initial_source": SOURCE,
                  "spec_sha256": hashlib.sha256((ROOT / "SPEC.zh-TW.md").read_bytes()).hexdigest(),
                  "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                  "package_sha256": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                                     for name in package_files()}, "error": "", "checks": {}}
        try:
            report["initialize"] = client.request("initialize", {
                "clientInfo": {"name": "masters_nudge_spec_test", "version": "1"},
                "capabilities": {"experimentalApi": True}})
            client.send({"method": "initialized", "params": {}})
            report["hook_listing"] = client.request("hooks/list", {})
            hook_config = json.loads((package / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
            reviewed = {hook["commandWindows" if os.name == "nt" else "command"]
                        for groups in hook_config.values() for group in groups for hook in group["hooks"]}
            hook_state = test_hook_state(report["hook_listing"], reviewed)
            # Inherit this process's fixture cwd. Explicit thread/start cwd would
            # persist project trust in the user's configuration in this Codex build.
            thread = client.request("thread/start", {"model": args.model, "ephemeral": True,
                                    "sandbox": "workspace-write", "approvalPolicy": "never",
                                    "config": {"hooks.state": hook_state}})
            thread_id = thread["thread"]["id"]
            report["thread_id"] = thread_id
            turn = client.request("turn/start", {"threadId": thread_id, "input": [{"type": "text", "text": task}]})
            turn_id = turn["turn"]["id"]
            report["turn_id"] = turn_id
            if args.mode == "interrupt":
                def pending():
                    return [row for row in read_journal(data)["attempts"] if row["outcome"] is None]
                client.wait(lambda: bool(pending()) or completed_turn(client.events, turn_id), 120)
                report["pending_at_interrupt"] = pending()
                if not report["pending_at_interrupt"]:
                    raise RuntimeError("沒有觀察到進行中的修改判斷，不能宣告測到中斷")
                client.request("turn/interrupt", {"threadId": thread_id, "turnId": turn_id})
                client.wait(lambda: completed_turn(client.events, turn_id), 30)
                report["first_turn"] = completed_turn(client.events, turn_id)
                followup = "停止修改與讀檔，只回覆 INTERRUPT_OK。"
                next_turn = client.request("turn/start", {"threadId": thread_id,
                                           "input": [{"type": "text", "text": followup}]})
                next_id = next_turn["turn"]["id"]
                report["next_turn_id"] = next_id
                client.wait(lambda: completed_turn(client.events, next_id), 90)
                report["next_turn"] = completed_turn(client.events, next_id)
                report["checks"] = {
                    "native_interrupted": report["first_turn"]["status"] == "interrupted",
                    "next_turn_completed": report["next_turn"]["status"] == "completed",
                    "no_new_feedback_on_followup": not hook_outputs(client.events, kind="context", turn_id=next_id),
                    "new_requirement_recorded": any(row["request"] == followup for row in read_journal(data)["rounds"])}
            else:
                client.wait(lambda: completed_turn(client.events, turn_id), 240)
                report["turn"] = completed_turn(client.events, turn_id)
                verification = subprocess.run([sys.executable, "-B", "-c",
                    'from job import new_job, finish, label; j=new_job(); assert label(j)=="pending"; finish(j); assert label(j)=="done"'],
                    cwd=workspace, capture_output=True, text=True, timeout=10)
                report["contract_exit_code"] = verification.returncode
                report["contract_stderr"] = verification.stderr
                attempts = read_journal(data)["attempts"]
                report["checks"] = {"actor_completed": report["turn"]["status"] == "completed",
                                    "contract_passed": verification.returncode == 0, "provider_called": bool(attempts)}
                if args.mode == "fault":
                    report["checks"].update({"fault_recorded": any(row["outcome"] == "fault" for row in attempts),
                        "warning_returned": any(text.startswith("本輪反饋未執行")
                                                for text in hook_outputs(client.events, kind="warning")),
                        "no_fault_in_actor_context": not hook_outputs(client.events, kind="context")})
                else:
                    report["checks"]["no_fault"] = all(row["outcome"] in ("feedback", "silence") for row in attempts)
        except Exception as exc:
            report["error"] = f"{type(exc).__name__}: {exc}"
        finally:
            # Terminate only this test's process tree, including pending Providers.
            if process.poll() is None:
                if os.name == "nt":
                    subprocess.run(["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                                   capture_output=True, timeout=10, **_provider_process_kwargs())
                else:
                    process.kill()
            process.wait(timeout=15)
            for worker in workers:
                worker.join(timeout=5)
            report.update(read_journal(data))
            report["elapsed_seconds"] = time.monotonic() - started
            report["final_source"] = (workspace / "job.py").read_text(encoding="utf-8")
            report["requests"] = client.sent
            report["post_tool_warnings"] = hook_outputs(client.events, kind="warning")
            report["post_tool_context"] = hook_outputs(client.events, kind="context")
            report["event_checks_passed"] = not report["error"] and bool(report["checks"]) and all(report["checks"].values())
            report["cleanup_completed"] = False
            report["passed"] = False
            (output / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Do not publish a successful command while fixture cleanup can still fail.
    report["cleanup_completed"] = True
    report["passed"] = report["event_checks_passed"]
    (output / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "error": report["error"], "checks": report["checks"]}, ensure_ascii=True))
    return int(not report["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
