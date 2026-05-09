#!/usr/bin/env python3
"""Buddy_similar — Stop hook worker.

Reads the transcript path from the Stop-hook JSON on stdin, gathers the recent
turns, calls the Claude CLI with the Buddy personality prompt, and appends the
reaction to ~/.claude/buddy.log.

Never raises out of main() — hook must not block on our errors.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

CLAUDE_DIR = Path(os.environ.get("BUDDY_CLAUDE_DIR", os.path.expanduser("~/.claude")))
SCRIPT_DIR = Path(__file__).resolve().parent
PROMPT_FILE = SCRIPT_DIR / "buddy-prompt.txt"
BUDDY_DIR = CLAUDE_DIR / "buddy"
ERROR_LOG = CLAUDE_DIR / "buddy-error.log"

PROVIDER = os.environ.get("BUDDY_PROVIDER", "openai").lower()
# BUDDY_MODEL meaning depends on provider:
#   anthropic: sonnet (default), opus, haiku
#   openai/codex: gpt-5.5 (default), other model names codex CLI accepts
_DEFAULT_MODELS = {"anthropic": "sonnet", "openai": "gpt-5.5", "codex": "gpt-5.5"}
MODEL = os.environ.get("BUDDY_MODEL", _DEFAULT_MODELS.get(PROVIDER, "sonnet"))
MAX_TRANSCRIPT_CHARS = int(os.environ.get("BUDDY_MAX_TRANSCRIPT", "2000"))
TIMEOUT_SEC = int(os.environ.get("BUDDY_TIMEOUT", "60"))


def log_error(msg: str) -> None:
    try:
        ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        with ERROR_LOG.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] buddy: {msg}\n")
    except Exception:
        pass


def read_hook_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except Exception as e:
        log_error(f"hook input parse failed: {e}")
        return {}


def format_transcript_entry(obj: dict) -> str:
    """Render one transcript JSONL entry into a prompt-friendly block."""
    typ = obj.get("type")
    if typ not in ("user", "assistant"):
        return ""

    msg = obj.get("message", {}) or {}
    role = msg.get("role", typ)
    content = msg.get("content", "")

    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                parts.append(block.get("text", ""))
            elif btype == "tool_use":
                name = block.get("name", "?")
                parts.append(f"[tool_use: {name}]")
            elif btype == "tool_result":
                parts.append("[tool_result]")
        text = "\n".join(p for p in parts if p)
    else:
        text = str(content)

    if len(text) > 1500:
        text = text[:1500] + "\n...[truncated]"

    return f"[{role}]\n{text}"


def read_recent_transcript(transcript_path: str, max_chars: int) -> str:
    if not transcript_path or not os.path.exists(transcript_path):
        return ""
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        log_error(f"transcript read failed: {e}")
        return ""

    blocks = []
    total = 0
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        block = format_transcript_entry(obj)
        if not block:
            continue
        if total + len(block) > max_chars:
            break
        blocks.append(block)
        total += len(block)

    return "\n\n".join(reversed(blocks))


def build_system_prompt() -> str:
    if not PROMPT_FILE.exists():
        log_error(f"prompt file missing: {PROMPT_FILE}")
        return ""
    try:
        return PROMPT_FILE.read_text(encoding="utf-8")
    except Exception as e:
        log_error(f"prompt file read failed: {e}")
        return ""


def parse_reaction(stdout: str) -> str:
    """Robustly extract Buddy's text from claude CLI stdout.

    Handles both raw-text output and JSON-envelope output.
    """
    stdout = stdout.strip()
    if not stdout:
        return ""
    if stdout.startswith("{"):
        try:
            obj = json.loads(stdout)
            if isinstance(obj, dict):
                for k in ("result", "content", "text"):
                    v = obj.get(k)
                    if isinstance(v, str) and v.strip():
                        return v.strip()
        except Exception:
            pass
    return stdout


def call_claude(system_prompt: str, transcript_text: str, model: str) -> str:
    user_prompt = "請對 stdin 提供的對話片段寫一句簡短的旁觀者反應。"

    fd = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    fd.write(system_prompt)
    fd.close()

    env = {**os.environ, "BUDDY_ACTIVE": "1"}
    try:
        r = subprocess.run(
            [
                "claude", "-p", user_prompt,
                "--model", model,
                "--append-system-prompt-file", fd.name,
            ],
            input=transcript_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
            timeout=TIMEOUT_SEC,
        )
        if r.returncode != 0:
            log_error(f"claude CLI exit {r.returncode}: {r.stderr[:500]}")
            return ""
        return parse_reaction(r.stdout)
    except subprocess.TimeoutExpired:
        log_error("claude CLI timeout")
        return ""
    except FileNotFoundError:
        log_error("claude CLI not found in PATH")
        return ""
    finally:
        try:
            os.unlink(fd.name)
        except OSError:
            pass


def _resolve_codex_bin() -> str | None:
    """Find codex executable. PATH lookup may miss it (e.g. npm on Windows
    isn't in the env Python sees), so probe known install locations too."""
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
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def call_codex(system_prompt: str, transcript_text: str, model: str) -> str:
    """Invoke codex exec for OpenAI-side critique. Returns last assistant message."""
    codex_bin = _resolve_codex_bin()
    if not codex_bin:
        log_error("codex CLI not found (checked PATH + common npm paths)")
        return ""

    # codex has no separate system-prompt slot — bundle everything into one prompt.
    user_prompt = "請對下方 [transcript] 區塊裡的對話片段寫一句簡短的旁觀者反應。"
    combined = (
        f"{system_prompt}\n\n"
        f"---\n\n"
        f"{user_prompt}\n\n"
        f"[transcript]\n{transcript_text}\n[end transcript]"
    )

    output_fd = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    output_fd.close()

    env = {**os.environ, "BUDDY_ACTIVE": "1"}
    # On Windows, .cmd files need shell=True or cmd /c. Detect by extension.
    use_shell = codex_bin.lower().endswith((".cmd", ".bat"))
    try:
        cmd = [
            codex_bin, "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--ignore-user-config",
            "-s", "read-only",
            "-m", model,
            "-o", output_fd.name,
            "-",  # read prompt from stdin
        ]
        if use_shell:
            # Quote args properly for cmd shell
            cmd_str = " ".join(f'"{a}"' if " " in a else a for a in cmd)
            r = subprocess.run(
                cmd_str,
                input=combined,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=TIMEOUT_SEC,
                shell=True,
            )
        else:
            r = subprocess.run(
                cmd,
                input=combined,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=env,
                timeout=TIMEOUT_SEC,
            )
        if r.returncode != 0:
            log_error(f"codex exit {r.returncode}: {r.stderr[:500]}")
            return ""
        try:
            with open(output_fd.name, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            log_error(f"codex output read failed: {e}")
            return ""
    except subprocess.TimeoutExpired:
        log_error("codex timeout")
        return ""
    except FileNotFoundError:
        log_error(f"codex CLI not executable: {codex_bin}")
        return ""
    finally:
        try:
            os.unlink(output_fd.name)
        except OSError:
            pass


def dispatch_call(system_prompt: str, transcript_text: str) -> str:
    """Route to the right provider based on BUDDY_PROVIDER."""
    if PROVIDER in ("openai", "codex"):
        return call_codex(system_prompt, transcript_text, MODEL)
    return call_claude(system_prompt, transcript_text, MODEL)


def append_buddy_log(session_id: str, provider: str, model: str, reaction: str) -> None:
    if not reaction.strip():
        return
    BUDDY_DIR.mkdir(parents=True, exist_ok=True)
    log_path = BUDDY_DIR / f"{session_id}.log"
    entry = {
        "ts": datetime.now().isoformat(),
        "session_id": session_id,
        "provider": provider,
        "model": model,
        "reaction": reaction,
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> None:
    hook = read_hook_input()
    transcript_path = hook.get("transcript_path", "")
    session_id = hook.get("session_id", "unknown")

    transcript_text = read_recent_transcript(transcript_path, MAX_TRANSCRIPT_CHARS)
    if not transcript_text:
        log_error("empty transcript, skipping")
        return

    system_prompt = build_system_prompt()
    if not system_prompt:
        return

    reaction = dispatch_call(system_prompt, transcript_text)
    if reaction:
        append_buddy_log(session_id, PROVIDER, MODEL, reaction)
    else:
        log_error("empty reaction, not logged")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_error(f"main exception: {e}")
        sys.exit(0)
