"""Fixed instructions and the only Actor-facing feedback rendering."""
from pathlib import Path
from .contracts import Feedback, ToolFault, FEEDBACK_MAX_CHARS


def delivery_text(feedback: Feedback) -> str:
    return (
        f"Masters’ Nudge\n{feedback.message}\n"
        "Before continuing, decide whether OBSERVED is required by the task. "
        "If not, consider PREFER. Implementation remains yours."
    )


def load_system_prompt(*, prompt_file: Path) -> str:
    try:
        text = prompt_file.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ToolFault("configuration", f"無法讀取 Provider 提示：{exc}") from exc
    if not text:
        raise ToolFault("configuration", "Provider 提示是空的")
    return text.replace("$FEEDBACK_MAX_CHARS", str(FEEDBACK_MAX_CHARS))
