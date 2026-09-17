"""Shared event, material and judgment data; SPEC is the behavioral authority."""
from __future__ import annotations
import json
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

SOURCES = ("task_contract", "before_structure", "batch_change", "current_structure", "tool_result")
MATERIAL_MAX_CHARS = 20_000
FEEDBACK_MAX_CHARS = 120
FEEDBACK_LIMIT = 3
SILENCE_LIMIT = 2


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


class ToolFault(Exception):
    def __init__(self, kind: str, detail: str, *, evidence: dict | None = None):
        self.kind = kind
        self.detail = detail
        self.evidence = evidence or {}
        super().__init__(f"{kind}: {detail}")


@dataclass(frozen=True)
class SessionRef:
    session_id: str
    turn_id: str
    cwd: str
    transcript_path: str = ""


@dataclass(frozen=True)
class MaterialLine:
    source: str
    path: str
    line: int
    text: str

    @property
    def location(self) -> str:
        return f"{self.path}:{self.line}"


def material_lines(source: str, path: str, text: str, start: int = 1) -> tuple[MaterialLine, ...]:
    return tuple(MaterialLine(source, path, i, line) for i, line in enumerate(text.splitlines(), start))


@dataclass(frozen=True)
class ToolCompleted:
    tool_use_id: str
    tool_name: str
    tool_input: object
    tool_response: object

    @property
    def modification(self) -> str | None:
        value = self.tool_input
        patch = value.get("command") if isinstance(value, dict) else value
        if isinstance(patch, str) and patch.splitlines()[:1] == ["*** Begin Patch"] and patch.rstrip().endswith("*** End Patch"):
            return patch
        if not isinstance(value, dict):
            return None
        for key in ("patch", "diff"):
            if isinstance(value.get(key), str) and value[key].strip():
                return value[key]
        path = value.get("path") or value.get("file_path")
        if not isinstance(path, str) or not path.strip():
            return None
        if all(isinstance(value.get(k), str) for k in ("old_string", "new_string")):
            return f"path: {path}\n[before]\n{value['old_string']}\n[after]\n{value['new_string']}"
        if isinstance(value.get("content"), str):
            return f"path: {path}\n[content]\n{value['content']}"
        return None


@dataclass(frozen=True)
class MaterialPacket:
    lines: tuple[MaterialLine, ...]
    workspace: str
    transcript_path: str = ""

    def categories(self) -> dict:
        return {source: [asdict(line) for line in self.lines if line.source == source] for source in SOURCES}

    @property
    def material_chars(self) -> int:
        return len(json_text(self.categories()))

    def render(self) -> str:
        return json_text({**self.categories(), "workspace": self.workspace, "transcript_path": self.transcript_path})


@dataclass(frozen=True)
class Evidence:
    source: str
    location: str
    excerpt: str


@dataclass(frozen=True)
class Feedback:
    criterion: int
    evidence: tuple[Evidence, ...]
    fact: str
    relationship: str
    question: str

    @property
    def message(self) -> str:
        return f"{self.fact}；{self.relationship}。{self.question}"


@dataclass(frozen=True)
class ProviderRun:
    raw_output: str
    materials: tuple[MaterialLine, ...] = ()
    usage: dict = field(default_factory=dict)
    trace: tuple[dict, ...] = ()


def find_git_root(cwd: str) -> str:
    try:
        result = subprocess.run(["git", "-C", cwd, "rev-parse", "--show-toplevel"],
                                capture_output=True, text=True, encoding="utf-8", timeout=5)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ToolFault("workspace", str(exc)) from exc
    if result.returncode:
        raise ToolFault("workspace", "工作區必須使用 Git")
    return str(Path(result.stdout.strip()).resolve())
