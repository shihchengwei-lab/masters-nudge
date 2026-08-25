"""Reviewer provider clients, independent of the coding-agent host."""

from __future__ import annotations

import json
import os
import signal
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable

from .local_ollama import DEFAULT_OLLAMA_URL, call_local_ollama_result
from .provider_contract import call_result, parse_reaction_result
from .runtime import reviewer_environment


Logger = Callable[[str], None]

GROK_REVIEWER_DENIED_TOOLS = (
    "run_terminal_cmd",
    "grep",
    "read_file",
    "search_replace",
    "list_dir",
    "web_search",
    "web_fetch",
    "todo_write",
    "task",
    "Agent",
)
GROK_COMPATIBILITY_SOURCES = (
    "SKILLS",
    "RULES",
    "AGENTS",
    "MCPS",
    "HOOKS",
    "SESSIONS",
)


def _noop(_message: str) -> None:
    return None


def _reviewer_process_kwargs() -> dict[str, int]:
    """Keep reviewer CLIs from opening a transient console on Windows."""
    if os.name != "nt":
        return {}
    return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)}


def _terminate_process_tree(
    process: subprocess.Popen,
    *,
    log_error: Logger = _noop,
) -> tuple[str, str]:
    """Terminate a timed-out reviewer and every descendant it started."""
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
                **_reviewer_process_kwargs(),
            )
        else:
            # `_run_cli_process` makes the reviewer PID its process-group ID.
            # The group can outlive its leader, so do not look the PID up first.
            os.killpg(process.pid, signal.SIGKILL)
    except (OSError, subprocess.SubprocessError) as exc:
        log_error(f"reviewer process-tree cleanup failed: {exc}")
        try:
            process.kill()
        except OSError:
            pass
    try:
        stdout, stderr = process.communicate(timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        try:
            process.kill()
        except OSError:
            pass
        try:
            stdout, stderr = process.communicate(timeout=1)
        except (OSError, subprocess.TimeoutExpired):
            return "", ""
    return str(stdout or ""), str(stderr or "")


def _run_cli_process(
    command: list[str] | str,
    *,
    input_text: str | None = None,
    cwd: str | None = None,
    environment: dict[str, str],
    timeout_sec: int,
    shell: bool = False,
    log_error: Logger = _noop,
) -> subprocess.CompletedProcess:
    kwargs = _reviewer_process_kwargs()
    if os.name != "nt":
        kwargs["start_new_session"] = True
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE if input_text is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        env=environment,
        cwd=cwd,
        shell=shell,
        **kwargs,
    )
    try:
        stdout, stderr = process.communicate(input=input_text, timeout=timeout_sec)
    except subprocess.TimeoutExpired as exc:
        collected = _terminate_process_tree(process, log_error=log_error)
        if isinstance(collected, tuple) and len(collected) == 2:
            stdout, stderr = collected
            if stdout:
                exc.output = stdout
            if stderr:
                exc.stderr = stderr
        raise
    return subprocess.CompletedProcess(
        command,
        process.returncode,
        stdout,
        stderr,
    )


def grok_subscription_environment() -> dict[str, str]:
    """Use Grok Build's signed-in subscription session, not API-key billing."""
    environment = reviewer_environment()
    environment.pop("XAI_API_KEY", None)
    for vendor in ("CLAUDE", "CURSOR"):
        for source in GROK_COMPATIBILITY_SOURCES:
            environment[f"GROK_{vendor}_{source}_ENABLED"] = "false"
    return environment


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
    aliases = {
        "inputTokens": "input_tokens",
        "outputTokens": "output_tokens",
        "totalTokens": "total_tokens",
        "cacheReadInputTokens": "cached_input_tokens",
        "cacheCreationInputTokens": "cache_write_input_tokens",
        "cache_read_input_tokens": "cached_input_tokens",
        "cache_creation_input_tokens": "cache_write_input_tokens",
        "reasoningTokens": "reasoning_output_tokens",
        "reasoning_tokens": "reasoning_output_tokens",
    }

    def visit(value) -> None:
        nonlocal best
        if isinstance(value, dict):
            candidate = {}
            for key, item in value.items():
                canonical = aliases.get(key, key)
                if canonical in usage_fields and isinstance(item, (int, float)):
                    candidate[canonical] = int(item)
            if len(candidate) > len(best):
                best = candidate
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    raw = str(stdout or "")
    try:
        visit(json.loads(raw))
    except (TypeError, ValueError):
        pass
    for line in raw.splitlines():
        try:
            visit(json.loads(line))
        except (TypeError, ValueError):
            continue
    return best


def call_claude_result(
    system_prompt: str,
    transcript_text: str,
    model: str,
    *,
    schema_path: Path,
    timeout_sec: int,
    log_error: Logger = _noop,
) -> dict:
    user_prompt = (
        "只輸出一個由證據支持、主模型可能忽略且可立即驗證的高價值 Nudge。\n\n"
        f"{transcript_text}"
    )
    schema_json = load_output_schema_json(schema_path, log_error)
    if not schema_json:
        return call_result()

    handle = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    handle.write(system_prompt)
    handle.close()
    try:
        result = _run_cli_process(
            [
                "claude",
                "-p",
                user_prompt,
                "--model",
                model,
                "--effort",
                "medium",
                "--no-session-persistence",
                "--system-prompt-file",
                handle.name,
                "--tools",
                "",
                "--setting-sources",
                "",
                "--output-format",
                "json",
                "--json-schema",
                schema_json,
            ],
            input_text=None,
            environment=reviewer_environment(),
            timeout_sec=timeout_sec,
            log_error=log_error,
        )
        if result.returncode != 0:
            detail = str(result.stderr or result.stdout or "")[:500]
            log_error(f"claude CLI exit {result.returncode}: {detail}")
            return call_result(error_kind="nonzero_exit")
        parsed = parse_reaction_result(result.stdout)
        parsed["usage"] = parse_usage(result.stdout)
        if parsed.get("status") == "error":
            parsed["error_kind"] = "invalid_output"
        return parsed
    except subprocess.TimeoutExpired as exc:
        partial_stdout = (
            getattr(exc, "stdout", None) or getattr(exc, "output", None) or ""
        )
        partial_stderr = getattr(exc, "stderr", None) or ""
        if isinstance(partial_stdout, bytes):
            partial_stdout = partial_stdout.decode("utf-8", errors="replace")
        if isinstance(partial_stderr, bytes):
            partial_stderr = partial_stderr.decode("utf-8", errors="replace")
        parsed = parse_reaction_result(str(partial_stdout))
        if parsed.get("status") != "error":
            parsed["usage"] = parse_usage(str(partial_stdout))
            log_error("claude CLI timed out after complete structured output; recovered")
            return parsed
        error_kind = (
            "timeout_after_partial_output"
            if str(partial_stdout).strip()
            else "timeout_before_output"
        )
        detail = str(partial_stderr).strip()[:500]
        log_error(
            f"claude CLI {error_kind}"
            + (f": {detail}" if detail else "")
        )
        return call_result(error_kind=error_kind)
    except FileNotFoundError:
        log_error("claude CLI not found in PATH")
        return call_result(error_kind="not_found")
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


def resolve_grok_bin() -> str | None:
    direct = shutil.which("grok")
    if direct and os.path.exists(direct):
        return direct
    candidates = [
        os.path.expanduser(r"~\.grok\bin\grok.exe"),
        os.path.expanduser(r"~\.grok\bin\grok"),
        "/usr/local/bin/grok",
        "/usr/bin/grok",
    ]
    return next((candidate for candidate in candidates if os.path.exists(candidate)), None)


def parse_grok_reaction_result(stdout: str) -> dict:
    """Extract schema output from direct or Grok headless JSON envelopes."""
    direct = parse_reaction_result(stdout)
    if direct.get("status") != "error":
        return direct
    try:
        outer = json.loads(str(stdout or ""))
    except (TypeError, ValueError):
        return call_result()
    candidates = []
    if isinstance(outer, dict):
        for key in (
            "structured_output",
            "structuredOutput",
            "result",
            "output",
            "response",
            "text",
        ):
            if key in outer:
                candidates.append(outer[key])
    for value in candidates:
        if isinstance(value, str):
            parsed = parse_reaction_result(value)
        else:
            try:
                parsed = parse_reaction_result(json.dumps(value, ensure_ascii=False))
            except (TypeError, ValueError):
                continue
        if parsed.get("status") != "error":
            return parsed
    return call_result()


def call_grok_result(
    system_prompt: str,
    transcript_text: str,
    model: str,
    *,
    schema_path: Path,
    timeout_sec: int,
    reasoning_effort: str = "",
    log_error: Logger = _noop,
    grok_bin_resolver: Callable[[], str | None] = resolve_grok_bin,
) -> dict:
    grok_bin = grok_bin_resolver()
    if not grok_bin:
        log_error("grok CLI not found (checked PATH + ~/.grok/bin)")
        return call_result(error_kind="not_found")
    schema_json = load_output_schema_json(schema_path, log_error)
    if not schema_json:
        return call_result()
    prompt = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    prompt.write(
        "請對下方 [transcript] 區塊裡的對話片段寫一句簡短的旁觀者反應。\n\n"
        f"[transcript]\n{transcript_text}\n[end transcript]\n"
    )
    prompt.close()
    isolated_workspace = tempfile.TemporaryDirectory(prefix="masters-nudge-grok-")
    try:
        isolated_cwd = isolated_workspace.name
        command = [
            grok_bin,
            "--prompt-file",
            prompt.name,
            "--system-prompt-override",
            system_prompt,
            "--json-schema",
            schema_json,
            "--output-format",
            "json",
            "--disable-web-search",
            "--disallowed-tools",
            ",".join(GROK_REVIEWER_DENIED_TOOLS),
            "--cwd",
            isolated_cwd,
            "--no-memory",
            "--no-subagents",
            "--max-turns",
            "1",
            "--permission-mode",
            "dontAsk",
            "--verbatim",
        ]
        if str(model or "").strip():
            command.extend(["--model", str(model).strip()])
        if str(reasoning_effort or "").strip():
            command.extend(
                ["--reasoning-effort", str(reasoning_effort).strip()]
            )
        result = _run_cli_process(
            command,
            cwd=isolated_cwd,
            environment=grok_subscription_environment(),
            timeout_sec=timeout_sec,
            log_error=log_error,
        )
        parsed = parse_grok_reaction_result(result.stdout)
        parsed["usage"] = parse_usage(result.stdout)
        if parsed.get("status") != "error":
            return parsed
        if result.returncode != 0:
            log_error(f"grok CLI exit {result.returncode}: {result.stderr[:500]}")
            return call_result(
                usage=parsed["usage"], error_kind="nonzero_exit"
            )
        return parsed
    except subprocess.TimeoutExpired:
        log_error("grok CLI timeout")
        return call_result(error_kind="timeout")
    except FileNotFoundError:
        log_error(f"grok CLI not executable: {grok_bin}")
        return call_result(error_kind="not_found")
    finally:
        isolated_workspace.cleanup()
        try:
            os.unlink(prompt.name)
        except OSError:
            pass


def call_codex_result(
    system_prompt: str,
    transcript_text: str,
    model: str,
    *,
    schema_path: Path,
    timeout_sec: int,
    log_error: Logger = _noop,
    codex_bin_resolver: Callable[[], str | None] = resolve_codex_bin,
) -> dict:
    codex_bin = codex_bin_resolver()
    if not codex_bin:
        log_error("codex CLI not found (checked PATH + common npm paths)")
        return call_result(error_kind="not_found")
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
        result = _run_cli_process(
            command_value,
            input_text=combined,
            environment=reviewer_environment(),
            timeout_sec=timeout_sec,
            shell=use_shell,
            log_error=log_error,
        )
        if result.returncode != 0:
            log_error(f"codex exit {result.returncode}: {result.stderr[:500]}")
            return call_result(
                usage=parse_usage(result.stdout), error_kind="nonzero_exit"
            )
        try:
            raw_output = Path(output.name).read_text(encoding="utf-8")
        except Exception as exc:
            log_error(f"codex output read failed: {exc}")
            return call_result(
                usage=parse_usage(result.stdout), error_kind="invalid_output"
            )
        parsed = parse_reaction_result(raw_output)
        parsed["usage"] = parse_usage(result.stdout)
        if parsed.get("status") == "error":
            parsed["error_kind"] = "invalid_output"
        return parsed
    except subprocess.TimeoutExpired:
        log_error("codex timeout")
        return call_result(error_kind="timeout")
    except FileNotFoundError:
        log_error(f"codex CLI not executable: {codex_bin}")
        return call_result(error_kind="not_found")
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
    ollama_url: str = DEFAULT_OLLAMA_URL,
    reasoning_effort: str = "",
    log_error: Logger = _noop,
) -> dict:
    if provider in ("openai", "codex"):
        return call_codex_result(
            system_prompt,
            transcript_text,
            model,
            schema_path=schema_path,
            timeout_sec=timeout_sec,
            log_error=log_error,
        )
    if provider == "anthropic":
        return call_claude_result(
            system_prompt,
            transcript_text,
            model,
            schema_path=schema_path,
            timeout_sec=timeout_sec,
            log_error=log_error,
        )
    if provider == "grok":
        return call_grok_result(
            system_prompt,
            transcript_text,
            model,
            schema_path=schema_path,
            timeout_sec=timeout_sec,
            reasoning_effort=reasoning_effort,
            log_error=log_error,
        )
    if provider == "ollama-local":
        return call_local_ollama_result(
            system_prompt,
            transcript_text,
            model,
            schema_path=schema_path,
            timeout_sec=timeout_sec,
            base_url=ollama_url,
            log_error=log_error,
        )
    log_error(f"unsupported reviewer provider: {provider!r}")
    return call_result()
