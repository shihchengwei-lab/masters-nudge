"""Nudge provider clients, independent of the coding-agent host."""

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
from .provider_contract import call_result, parse_nudge_result
from .runtime import provider_environment


Logger = Callable[[str], None]

def _noop(_message: str) -> None:
    return None


def _provider_process_kwargs() -> dict[str, int]:
    """Keep Provider CLIs from opening a transient console on Windows."""
    if os.name != "nt":
        return {}
    return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0)}


def _terminate_process_tree(
    process: subprocess.Popen,
    *,
    log_error: Logger = _noop,
) -> tuple[str, str]:
    """Terminate a timed-out Provider and every descendant it started."""
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
                **_provider_process_kwargs(),
            )
        else:
            # `_run_cli_process` makes the Provider PID its process-group ID.
            # The group can outlive its leader, so do not look the PID up first.
            os.killpg(process.pid, signal.SIGKILL)
    except (OSError, subprocess.SubprocessError) as exc:
        log_error(f"Provider process-tree cleanup failed: {exc}")
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
    kwargs = _provider_process_kwargs()
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


def load_output_schema_json(schema_path: Path, log_error: Logger = _noop) -> str:
    try:
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        log_error(f"Nudge schema unavailable: {exc}")
        return ""
    if not isinstance(schema, dict):
        log_error("Nudge schema root must be an object")
        return ""
    return json.dumps(schema, ensure_ascii=False, separators=(",", ":"))


def parse_schema_result(stdout: str) -> dict:
    return parse_nudge_result(stdout)


def _parse_codex_jsonl_result(stdout: str) -> dict:
    recovered = call_result()
    for line in str(stdout or "").splitlines():
        try:
            event = json.loads(line)
        except (TypeError, ValueError):
            continue
        if event.get("type") != "item.completed":
            continue
        item = event.get("item")
        if not isinstance(item, dict) or item.get("type") != "agent_message":
            continue
        parsed = parse_schema_result(str(item.get("text") or ""))
        if not parsed.get("error_kind"):
            recovered = parsed
    return recovered


def call_claude_result(
    system_prompt: str,
    nudge_input: str,
    model: str,
    *,
    schema_path: Path,
    timeout_sec: int,
    log_error: Logger = _noop,
) -> dict:
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
                nudge_input,
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
            environment=provider_environment(),
            timeout_sec=timeout_sec,
            log_error=log_error,
        )
        if result.returncode != 0:
            detail = str(result.stderr or result.stdout or "")[:500]
            log_error(f"claude CLI exit {result.returncode}: {detail}")
            return call_result(error_kind="nonzero_exit")
        parsed = parse_schema_result(result.stdout)
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
        parsed = parse_schema_result(str(partial_stdout))
        if not parsed.get("error_kind"):
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


def call_codex_result(
    system_prompt: str,
    nudge_input: str,
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

    combined = f"{system_prompt}\n\n---\n\n{nudge_input}"
    use_shell = codex_bin.lower().endswith((".cmd", ".bat"))
    with tempfile.TemporaryDirectory(prefix="masters-nudge-provider-") as temp_dir:
        output_path = Path(temp_dir) / "output.json"
        try:
            command = [
                codex_bin,
                "-c",
                "features.shell_tool=false",
                "-c",
                "project_doc_max_bytes=0",
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
                str(output_path),
                "-",
            ]
            if use_shell:
                command_value: list[str] | str = subprocess.list2cmdline(command)
            else:
                command_value = command
            result = _run_cli_process(
                command_value,
                input_text=combined,
                cwd=temp_dir,
                environment=provider_environment(),
                timeout_sec=timeout_sec,
                shell=use_shell,
                log_error=log_error,
            )
            if result.returncode != 0:
                log_error(f"codex exit {result.returncode}: {result.stderr[:500]}")
                return call_result(error_kind="nonzero_exit")
            try:
                raw_output = output_path.read_text(encoding="utf-8")
            except Exception as exc:
                log_error(f"codex output read failed: {exc}")
                return call_result(error_kind="invalid_output")
            parsed = parse_schema_result(raw_output)
            event_result = _parse_codex_jsonl_result(result.stdout)
            if not event_result.get("error_kind"):
                parsed = event_result
            return parsed
        except subprocess.TimeoutExpired:
            log_error("codex timeout")
            return call_result(error_kind="timeout")
        except FileNotFoundError:
            log_error(f"codex CLI not executable: {codex_bin}")
            return call_result(error_kind="not_found")


def dispatch_call_result(
    provider: str,
    system_prompt: str,
    nudge_input: str,
    model: str,
    *,
    schema_path: Path,
    timeout_sec: int,
    ollama_url: str = DEFAULT_OLLAMA_URL,
    log_error: Logger = _noop,
) -> dict:
    if provider in ("openai", "codex"):
        return call_codex_result(
            system_prompt,
            nudge_input,
            model,
            schema_path=schema_path,
            timeout_sec=timeout_sec,
            log_error=log_error,
        )
    if provider == "anthropic":
        return call_claude_result(
            system_prompt,
            nudge_input,
            model,
            schema_path=schema_path,
            timeout_sec=timeout_sec,
            log_error=log_error,
        )
    if provider == "ollama":
        return call_local_ollama_result(
            system_prompt,
            nudge_input,
            model,
            schema_path=schema_path,
            timeout_sec=timeout_sec,
            base_url=ollama_url,
            log_error=log_error,
            parse_result=parse_schema_result,
        )
    log_error(f"unsupported Nudge Provider: {provider!r}")
    return call_result()
