#!/usr/bin/env python3
"""Real Provider/MCP probe. This does not claim to test native Actor delivery."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from masters_nudge.codex_adapter import CodexAdapter
from masters_nudge.core import NudgeCore
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--indirect", action="store_true", help="use a call whose implementation requires repository reading")
    parser.add_argument("--transport-read-check", action="store_true", help="explicit real-MCP capability check, not feedback-effect evidence")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="nudge-provider-probe-") as raw:
        root = Path(raw)
        repo = root / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        code = 'def finish(job):\n    job["status"] = "done"\n\ndef label(job):\n    return "done" if job["is_done"] else job["status"]\n'
        (repo / "job.py").write_text(code, encoding="utf-8")
        if args.indirect:
            (repo / "view.py").write_text('from job import label\n\ndef view(job):\n    return label(job)\n', encoding="utf-8")
        paths = RuntimePaths(ROOT, root / "data", root / "settings", root / "error.log")
        core = NudgeCore(RuntimeSettings("openai", args.model, paths, strict=True))
        if args.transport_read_check:
            from masters_nudge.providers import call_codex_result
            def checked_dispatch(**kwargs):
                kwargs["system_prompt"] += '\nTransport capability check only: use read_file to read job.py before returning JSON. This check is not an engineering-effect evaluation.\n'
                return call_codex_result(**kwargs)
            core.dispatch = checked_dispatch
        adapter = CodexAdapter(core)
        common = {"session_id": "probe", "turn_id": "turn-1", "cwd": str(repo), "transcript_path": None}
        adapter.process(dict(common, hook_event_name="UserPromptSubmit",
                             prompt="新增畫面完成狀態顯示，工作完成後應顯示 done。保留 finish 與 label 的呼叫介面。"))
        result = None
        fault = None
        try:
            change = ('*** Begin Patch\n*** Add File: view.py\n+from job import label\n+\n+def view(job):\n+    return label(job)\n*** End Patch'
                      if args.indirect else '*** Begin Patch\n*** Update File: job.py\n@@\n-def label(job):\n-    return job["status"]\n+def label(job):\n+    return "done" if job["is_done"] else job["status"]\n*** End Patch')
            result = adapter.process(dict(common, hook_event_name="PostToolUse",
                tool_use_id="edit-1", tool_name="apply_patch", tool_input=change,
                tool_response="Success. Added view.py" if args.indirect else "Success. Updated job.py"))
        except Exception as exc:
            fault = str(exc)
        attempts = core.journal.recent()
        report = {"scope": "explicit real-MCP capability check" if args.transport_read_check else "real Provider; synthetic batch, no Actor",
                  "model": args.model,
                  "source": code, "result": result, "fault": fault, "attempts": attempts}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(args.output), "fault": fault,
                          "outcome": attempts[0]["outcome"] if attempts else None}, ensure_ascii=True))
        did_read = any(entry["name"] == "read_file" for attempt in attempts for entry in attempt["detail"].get("trace", []))
        return int(fault is not None or (args.transport_read_check and not did_read))


if __name__ == "__main__":
    raise SystemExit(main())
