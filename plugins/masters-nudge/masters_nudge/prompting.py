"""Fixed instructions and the only Actor-facing feedback rendering."""
from pathlib import Path
from .contracts import Feedback, ToolFault


def delivery_text(feedback: Feedback) -> str:
    return (
        f"Masters’ Nudge\n{feedback.message}\n"
        "Consider whether this suggests a better way to complete the task. "
        "If it does, revise your implementation."
    )


def load_system_prompt(*, prompt_file: Path) -> str:
    try:
        text = prompt_file.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ToolFault("configuration", f"無法讀取 Provider 提示：{exc}") from exc
    if not text:
        raise ToolFault("configuration", "Provider 提示是空的")
    return text
