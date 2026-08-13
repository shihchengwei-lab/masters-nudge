"""Reviewer provider clients, independent of the coding-agent host."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from .prompting import MAX_REACTION_CHARS
from .runtime import reviewer_environment


Logger = Callable[[str], None]


def _noop(_message: str) -> None:
    return None


def load_output_schema_json(schema_path: Path, log_error: Logger = _noop) -> str:
    try:
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        log_error(f"reaction schema unavailable: {exc}")
        return ""
    if not isinstance(schema, dict):
        log_error("reaction schema root must be an object")
        return ""
    return json.dumps(schema, ensure_ascii=False, separators=(",", ":"))


def parse_reaction_result(
    stdout: str, max_chars: int = MAX_REACTION_CHARS
) -> dict:
    stdout = str(stdout or "").strip()
    if not stdout:
        return {"status": "error", "finding": ""}
    try:
        obj = json.loads(stdout)
    except (TypeError, ValueError):
        return {"status": "error", "finding": ""}
    if isinstance(obj, dict) and "structured_output" in obj:
        obj = obj.get("structured_output")
    if not isinstance(obj, dict) or set(obj) != {"status", "finding"}:
        return {"status": "error", "finding": ""}
    status = obj.get("status")
    finding = obj.get("finding")
    if not isinstance(finding, str):
        return {"status": "error", "finding": ""}
    if status == "no_finding":
        return {"status": "no_finding", "finding": ""}
    if status != "finding":
        return {"status": "error", "finding": ""}
    finding = finding.strip()
    if not finding or len(finding) > max_chars:
        return {"status": "error", "finding": ""}
    return {"status": "finding", "finding": finding}


def parse_usage(stdout: str) -> dict[str, int]:
    usage_fields = {
        "input_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
        "total_tokens",
    }
    best: dict[str, int] = {}

    def visit(value) -> None:
        nonlocal best
        if isinstance(value, dict):
            candidate = {
                key: int(item)
                for key, item in value.items()
                if key in usage_fields and isinstance(item, (int, float))
            }
            if len(candidate) > len(best):
                best = candidate
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    for line in str(stdout or "").splitlines():
        try:
            visit(json.loads(line))
        except (TypeError, ValueError):
            continue
    return best


def call_result(status: str = "error", finding: str = "", **extra) -> dict:
    return {"status": status, "finding": finding, "usage": {}, **extra}


def call_claude_result(
    system_prompt: str,
    transcript_text: str,
    model: str,
    *,
    schema_path: Path,
    timeout_sec: int,
    capture_raw: bool = False,
    log_error: Logger = _noop,
) -> dict:
    user_prompt = "請對 stdin 提供的對話片段寫一句簡短的旁觀者反應。"
    schema_json = load_output_schema_json(schema_path, log_error)
    if not schema_json:
        return call_result()

    handle = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    handle.write(system_prompt)
    handle.close()
    try:
        result = subprocess.run(
            [
                "claude",
                "-p",
                user_prompt,
                "--model",
                model,
                "--append-system-prompt-file",
                handle.name,
                "--output-format",
                "json",
                "--json-schema",
                schema_json,
            ],
            input=transcript_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=reviewer_environment(),
            timeout=timeout_sec,
        )
        if result.returncode != 0:
            log_error(f"claude CLI exit {result.returncode}: {result.stderr[:500]}")
            return call_result()
        parsed = parse_reaction_result(result.stdout)
        parsed["usage"] = parse_usage(result.stdout)
        if capture_raw:
            parsed["raw_output"] = result.stdout
        return parsed
    except subprocess.TimeoutExpired:
        log_error("claude CLI timeout")
        return call_result()
    except FileNotFoundError:
        log_error("claude CLI not found in PATH")
        return call_result()
    finally:
        try:
            os.unlink(handle.name)
        except OSError:
            pass


def resolve_codex_bin() -> str | None:
    direct = shutil.which("codex")
    if direct and os.path.exists(direct):
        return direct
    candidates = [
        os.path.expanduser(r"~\AppData\Roaming\npm\codex.cmd"),
        os.path.expanduser(r"~\AppData\Roaming\npm\codex.exe"),
        os.path.expanduser(r"~\AppData\Roaming\npm\codex"),
        os.path.expanduser("~/.codex/bin/codex"),
        "/usr/local/bin/codex",
        "/usr/bin/codex",
    ]
    return next((candidate for candidate in candidates if os.path.exists(candidate)), None)


def call_codex_result(
    system_prompt: str,
    transcript_text: str,
    model: str,
    *,
    schema_path: Path,
    timeout_sec: int,
    capture_raw: bool = False,
    log_error: Logger = _noop,
    codex_bin_resolver: Callable[[], str | None] = resolve_codex_bin,
) -> dict:
    codex_bin = codex_bin_resolver()
    if not codex_bin:
        log_error("codex CLI not found (checked PATH + common npm paths)")
        return call_result()
    if not load_output_schema_json(schema_path, log_error):
        return call_result()

    user_prompt = "請對下方 [transcript] 區塊裡的對話片段寫一句簡短的旁觀者反應。"
    combined = (
        f"{system_prompt}\n\n---\n\n{user_prompt}\n\n"
        f"[transcript]\n{transcript_text}\n[end transcript]"
    )
    output = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    output.close()
    use_shell = codex_bin.lower().endswith((".cmd", ".bat"))
    try:
        command = [
            codex_bin,
            "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--ignore-user-config",
            "--json",
            "-s",
            "read-only",
            "-m",
            model,
            "--output-schema",
            str(schema_path),
            "-o",
            output.name,
            "-",
        ]
        if use_shell:
            command_value: list[str] | str = " ".join(
                f'"{part}"' if " " in part else part for part in command
            )
        else:
            command_value = command
        result = subprocess.run(
            command_value,
            input=combined,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=reviewer_environment(),
            timeout=timeout_sec,
            shell=use_shell,
        )
        if result.returncode != 0:
            log_error(f"codex exit {result.returncode}: {result.stderr[:500]}")
            return call_result(usage=parse_usage(result.stdout))
        try:
            raw_output = Path(output.name).read_text(encoding="utf-8")
        except Exception as exc:
            log_error(f"codex output read failed: {exc}")
            return call_result(usage=parse_usage(result.stdout))
        parsed = parse_reaction_result(raw_output)
        parsed["usage"] = parse_usage(result.stdout)
        if capture_raw:
            parsed["raw_output"] = raw_output
        return parsed
    except subprocess.TimeoutExpired:
        log_error("codex timeout")
        return call_result()
    except FileNotFoundError:
        log_error(f"codex CLI not executable: {codex_bin}")
        return call_result()
    finally:
        try:
            os.unlink(output.name)
        except OSError:
            pass


def dispatch_call_result(
    provider: str,
    system_prompt: str,
    transcript_text: str,
    model: str,
    *,
    schema_path: Path,
    timeout_sec: int,
    capture_raw: bool = False,
    log_error: Logger = _noop,
) -> dict:
    if provider in ("openai", "codex"):
        return call_codex_result(
            system_prompt,
            transcript_text,
            model,
            schema_path=schema_path,
            timeout_sec=timeout_sec,
            capture_raw=capture_raw,
            log_error=log_error,
        )
    if provider == "anthropic":
        return call_claude_result(
            system_prompt,
            transcript_text,
            model,
            schema_path=schema_path,
            timeout_sec=timeout_sec,
            capture_raw=capture_raw,
            log_error=log_error,
        )
    log_error(f"unsupported reviewer provider: {provider!r}")
    return call_result()
