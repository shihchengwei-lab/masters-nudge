#!/usr/bin/env python3
"""Bounded stdio MCP tools for repository evidence, with no mutation surface."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


PROTOCOL_VERSION = "2025-06-18"
MAX_OUTPUT_CHARS = 32_000
MAX_READ_LINES = 400
MAX_RESULTS = 50

TOOLS = [
    {
        "name": "search_repo",
        "description": (
            "Search tracked and non-ignored repository text files for a literal string. "
            "Returns bounded path:line evidence and never modifies the repository."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "minLength": 1, "maxLength": 200},
                "path": {
                    "type": "string",
                    "description": "Optional repository-relative file or directory prefix.",
                },
                "max_results": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": MAX_RESULTS,
                    "default": 30,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "read_file",
        "description": (
            "Read a bounded line range from one tracked or non-ignored repository file. "
            "Ignored files and paths outside the repository are unavailable."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "minLength": 1},
                "start_line": {"type": "integer", "minimum": 1, "default": 1},
                "end_line": {"type": "integer", "minimum": 1},
            },
            "required": ["path"],
            "additionalProperties": False,
        },
    },
]


def _text_result(text: str, *, is_error: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {"content": [{"type": "text", "text": text}]}
    if is_error:
        result["isError"] = True
    return result


def _safe_path(root: Path, value: str) -> Path:
    candidate = (root / value).resolve()
    candidate.relative_to(root)
    return candidate


def _git_paths(root: Path, *arguments: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", *arguments],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("workspace is not a readable Git repository")
    return [
        raw.decode("utf-8", errors="replace")
        for raw in result.stdout.split(b"\0")
        if raw
    ]


def _untracked_files(root: Path) -> list[Path]:
    return [
        _safe_path(root, relative)
        for relative in _git_paths(root, "--others", "--exclude-standard")
    ]


def _is_repository_file(root: Path, candidate: Path) -> bool:
    relative = candidate.relative_to(root).as_posix()
    try:
        matches = _git_paths(
            root,
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            relative,
        )
    except (OSError, subprocess.SubprocessError, ValueError):
        return False
    return relative in {value.replace("\\", "/") for value in matches}


def _search_repo(root: Path, arguments: dict[str, Any]) -> dict[str, Any]:
    query = arguments.get("query")
    if not isinstance(query, str) or not query or len(query) > 200:
        return _text_result("query must contain 1 to 200 characters", is_error=True)
    path_filter = arguments.get("path", "")
    if not isinstance(path_filter, str):
        return _text_result("path must be a repository-relative string", is_error=True)
    try:
        filter_target = _safe_path(root, path_filter) if path_filter else root
    except (OSError, RuntimeError, ValueError):
        return _text_result("path escapes the repository", is_error=True)
    requested_max = arguments.get("max_results", 30)
    if not isinstance(requested_max, int) or isinstance(requested_max, bool):
        return _text_result("max_results must be an integer", is_error=True)
    limit = max(1, min(requested_max, MAX_RESULTS))

    command = ["git", "grep", "-n", "-F", "-I", "-e", query, "--"]
    if path_filter:
        command.append(path_filter)
    try:
        grep = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return _text_result("Git search failed", is_error=True)
    if grep.returncode not in (0, 1):
        return _text_result("Git search failed", is_error=True)
    matches = grep.stdout.splitlines()[:limit]

    try:
        untracked = _untracked_files(root)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        return _text_result(str(exc), is_error=True)
    for candidate in untracked:
        if len(matches) >= limit:
            break
        try:
            if filter_target != root:
                if filter_target.is_file() and candidate != filter_target:
                    continue
                if filter_target.is_dir():
                    candidate.relative_to(filter_target)
            content = candidate.read_text(encoding="utf-8", errors="replace")
        except (OSError, RuntimeError, ValueError):
            continue
        relative = candidate.relative_to(root).as_posix()
        for number, line in enumerate(content.splitlines(), start=1):
            if query in line:
                matches.append(f"{relative}:{number}: {line[:500]}")
                if len(matches) >= limit:
                    break
    rendered = "\n".join(matches) if matches else "No matches."
    return _text_result(rendered[:MAX_OUTPUT_CHARS])


def _read_file(root: Path, arguments: dict[str, Any]) -> dict[str, Any]:
    value = arguments.get("path")
    if not isinstance(value, str) or not value:
        return _text_result("path is required", is_error=True)
    try:
        candidate = _safe_path(root, value)
    except (OSError, RuntimeError, ValueError):
        return _text_result("path escapes the repository", is_error=True)
    if not candidate.is_file() or not _is_repository_file(root, candidate):
        return _text_result(
            "path is not a tracked or non-ignored repository file", is_error=True
        )
    start = arguments.get("start_line", 1)
    end = arguments.get("end_line", start + MAX_READ_LINES - 1)
    if (
        not isinstance(start, int)
        or isinstance(start, bool)
        or not isinstance(end, int)
        or isinstance(end, bool)
        or start < 1
        or end < start
    ):
        return _text_result("line range is invalid", is_error=True)
    end = min(end, start + MAX_READ_LINES - 1)
    selected: list[str] = []
    try:
        with candidate.open("r", encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, start=1):
                if number < start:
                    continue
                if number > end:
                    break
                selected.append(f"{number}: {line.rstrip()[:4000]}")
    except OSError as exc:
        return _text_result(f"read failed: {exc}", is_error=True)
    return _text_result(("\n".join(selected)[:MAX_OUTPUT_CHARS]) or "(empty range)")


def handle_request(message: dict[str, Any], *, root: Path) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    if request_id is None:
        return None
    if method == "initialize":
        requested = message.get("params", {}).get("protocolVersion")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": requested or PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "read-only-repo", "version": "1.0.0"},
            },
        }
    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = message.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})
        if not isinstance(arguments, dict):
            result = _text_result("arguments must be an object", is_error=True)
        elif name == "search_repo":
            result = _search_repo(root, arguments)
        elif name == "read_file":
            result = _read_file(root, arguments)
        else:
            result = _text_result(f"unknown or unavailable tool: {name}", is_error=True)
        return {"jsonrpc": "2.0", "id": request_id, "result": result}
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"method not found: {method}"},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=os.environ.get("MN_READONLY_ROOT"))
    args = parser.parse_args()
    if not args.root:
        parser.error("--root or MN_READONLY_ROOT is required")
    root = Path(args.root).resolve()
    if not root.is_dir():
        parser.error("repository root is not a directory")

    for line in sys.stdin:
        try:
            message = json.loads(line)
            response = handle_request(message, root=root)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as exc:
            sys.stdout.write(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32603, "message": str(exc)},
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
