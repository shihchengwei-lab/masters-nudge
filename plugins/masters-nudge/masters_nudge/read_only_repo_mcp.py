#!/usr/bin/env python3
"""Read-only repository tools with one durable, shared output budget."""
from __future__ import annotations
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from masters_nudge.contracts import MaterialLine, ToolFault, find_git_root, json_text

TOOLS = [
    {"name": "search_repo", "description": "Search literal text in the Git workspace; return exact file/line/text. exhausted=true means the shared evidence budget is finished and no later repository call can return more evidence.",
     "inputSchema": {"type": "object", "properties": {
         "query": {"type": "string", "minLength": 1},
         "path": {"type": "string"},
         "max_results": {"type": "integer", "minimum": 1, "maximum": 50}},
         "required": ["query"], "additionalProperties": False}},
    {"name": "read_file", "description": "Read a file range in the Git workspace; return exact file/line/text. exhausted=true means the shared evidence budget is finished and no later repository call can return more evidence.",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "minLength": 1},
         "start_line": {"type": "integer", "minimum": 1},
         "end_line": {"type": "integer", "minimum": 1}},
         "required": ["path"], "additionalProperties": False}},
]


def read_audit(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    except (OSError, ValueError) as exc:
        raise ToolFault("mcp_audit", "材料讀取紀錄損壞") from exc


class RepositoryTools:
    def __init__(self, root: Path, budget: int, audit: Path):
        self.root = Path(find_git_root(str(root)))
        self.budget = max(0, budget)
        self.audit = audit
        self.audit.parent.mkdir(parents=True, exist_ok=True)

    def _git(self, *args) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, timeout=15)

    def _path(self, value: str) -> Path:
        if not isinstance(value, str):
            raise ToolFault("mcp_input", "path 必須是相對路徑")
        path = (self.root / value).resolve()
        try:
            relative = path.relative_to(self.root)
        except ValueError as exc:
            raise ToolFault("mcp_path", "路徑超出工作區") from exc
        if ".git" in relative.parts:
            raise ToolFault("mcp_path", "不能讀取 Git 內部資料")
        return path

    def _allowed(self, path: Path):
        relative = path.relative_to(self.root).as_posix()
        ignored = self._git("check-ignore", "--no-index", "--", relative)
        if ignored.returncode not in (0, 1):
            raise ToolFault("mcp_git", "無法確認忽略規則")
        if ignored.returncode == 0:
            raise ToolFault("mcp_path", "檔案被忽略")
        listed = self._git("ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", relative)
        if listed.returncode or relative.encode("utf-8") not in listed.stdout.split(b"\0"):
            raise ToolFault("mcp_path", "檔案不在 Git 工作區範圍")
        if not path.is_file():
            raise ToolFault("mcp_path", "檔案不存在")

    def _read(self, args: dict):
        if set(args) - {"path", "start_line", "end_line"} or "path" not in args:
            raise ToolFault("mcp_input", "read_file 參數不合法")
        start = args.get("start_line", 1)
        if type(start) is not int or start < 1:
            raise ToolFault("mcp_input", "起始行號必須是正整數")
        end = args.get("end_line", start + 199)
        if type(end) is not int or end < start:
            raise ToolFault("mcp_input", "行號範圍不合法")
        path = self._path(args["path"])
        self._allowed(path)
        relative = path.relative_to(self.root).as_posix()
        with path.open(encoding="utf-8") as stream:
            for number, text in enumerate(stream, 1):
                if number > end:
                    break
                if number >= start:
                    yield MaterialLine("current_structure", relative, number, text.rstrip("\r\n"))

    def _search(self, args: dict):
        if set(args) - {"query", "path", "max_results"}:
            raise ToolFault("mcp_input", "search_repo 參數不合法")
        query, count = args.get("query"), args.get("max_results", 30)
        if not isinstance(query, str) or not query or type(count) is not int or not 1 <= count <= 50:
            raise ToolFault("mcp_input", "搜尋文字或筆數不合法")
        prefix = self._path(args.get("path", ""))
        if not prefix.exists():
            return
        relative_prefix = prefix.relative_to(self.root).as_posix() or "."
        searched = subprocess.run(
            [
                "rg", "--fixed-strings", "--line-number", "--with-filename",
                "--no-heading", "--color", "never", "--hidden", "--glob", "!.git/**",
                "--max-count", str(count), "--", query, relative_prefix,
            ],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        if searched.returncode not in (0, 1):
            raise ToolFault("mcp_search", searched.stderr.strip() or "無法搜尋工作區")
        found = 0
        for raw in searched.stdout.splitlines():
            parts = raw.split(":", 2)
            if len(parts) != 3:
                continue
            relative, number, text = parts
            try:
                line_number = int(number)
            except ValueError:
                continue
            yield MaterialLine("current_structure", Path(relative).as_posix(), line_number, text)
            found += 1
            if found >= count:
                return

    def call(self, name: str, args: dict) -> dict:
        history = read_audit(self.audit)
        remaining = self.budget - sum(len(entry["text"]) for entry in history)
        lines = []
        fault = ""
        exhausted = False
        truncated = False
        try:
            if name not in ("search_repo", "read_file") or not isinstance(args, dict):
                raise ToolFault("mcp_input", "只允許搜尋與讀檔")
            if remaining <= 0:
                exhausted = True
                text = ""
            else:
                iterator = self._search(args) if name == "search_repo" else self._read(args)
                for line in iterator:
                    candidate = json_text({"lines": [*lines, asdict(line)], "truncated": False})
                    if len(candidate) > remaining:
                        truncated = exhausted = True
                        break
                    lines.append(asdict(line))
                text = json_text({"lines": lines, "truncated": truncated})
                if len(text) > remaining:
                    text = ""
                    exhausted = True
        except (ToolFault, OSError, UnicodeError, subprocess.SubprocessError) as exc:
            fault = str(exc)
            text = json_text({"error": fault})
            if len(text) > remaining:
                text = ""
        record = {"name": name, "arguments": args, "text": text, "fault": fault,
                  "exhausted": exhausted, "lines": lines}
        with self.audit.open("a", encoding="utf-8") as stream:
            stream.write(json_text(record) + "\n")
        response = {"lines": lines, "truncated": truncated, "exhausted": exhausted}
        if fault:
            response["error"] = fault
        return {"content": [{"type": "text", "text": json_text(response)}],
                "isError": bool(fault)}


def serve(tools: RepositoryTools):
    for line in sys.stdin:
        request = json.loads(line)
        if "id" not in request:
            continue
        method, params = request.get("method"), request.get("params") or {}
        if method == "initialize":
            with tools.audit.open("a", encoding="utf-8") as stream:
                stream.write(json_text({"name": "initialize", "arguments": params, "text": "", "fault": "",
                                        "exhausted": False, "lines": []}) + "\n")
            result = {"protocolVersion": params.get("protocolVersion", "2025-06-18"),
                      "capabilities": {"tools": {}}, "serverInfo": {"name": "masters-nudge-readrepo", "version": "1.0"}}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            result = tools.call(params.get("name"), params.get("arguments"))
        elif method == "ping":
            result = {}
        else:
            print(json_text({"jsonrpc": "2.0", "id": request["id"],
                             "error": {"code": -32601, "message": "Unknown method"}}), flush=True)
            continue
        print(json_text({"jsonrpc": "2.0", "id": request["id"], "result": result}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--budget", required=True, type=int)
    parser.add_argument("--audit", required=True, type=Path)
    args = parser.parse_args()
    serve(RepositoryTools(Path(args.root), args.budget, args.audit))


if __name__ == "__main__":
    main()
