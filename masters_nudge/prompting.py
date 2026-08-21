"""Host-neutral prompt assembly and reaction sanitation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Mapping

import lens_router
import persona_config


MAX_REACTION_CHARS = 52


def build_system_prompt(
    *,
    prompt_file: Path,
    persona_dir: Path,
    data_dir: Path,
    route: lens_router.ReviewRoute | None = None,
    persona_names: Mapping[str, str] | None = None,
    domain: str = "software",
    log_error: Callable[[str], None] | None = None,
) -> str:
    logger = log_error or (lambda _message: None)
    try:
        base_prompt = prompt_file.read_text(encoding="utf-8")
    except Exception as exc:
        logger(f"prompt file read failed: {exc}")
        return ""

    route = route or lens_router.resolve_review_route(data_dir)
    personas = persona_config.LENS_PERSONAS if persona_names is None else persona_names
    persona = route.effective_lens
    if persona == "general":
        return base_prompt
    if persona not in personas:
        supported = ", ".join(personas)
        logger(f"unknown persona: {persona!r}; supported: {supported}")
        return ""

    persona_file = persona_dir / f"{persona}.txt"
    try:
        overlay = persona_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger(f"persona prompt read failed ({persona}): {exc}")
        return ""

    if domain == "shader":
        return f"{base_prompt.rstrip()}\n\n{overlay}\n"

    heading = "工作流觀察鏡頭"
    first_paragraph = (
        f"這一輪借用 {personas[persona]} 的核心概念、"
        "觀察方法與關注面向，決定如何整理證據、從哪裡看這段工作。\n"
    )
    final_line = "不是扮演或模仿人物，也不是增加一份 code review。\n"
    persona_header = "".join((
        f"# {heading}\n\n",
        first_paragraph,
        "下方場景中的小動作只用來啟動思考，不表示人物真的如此行動，"
        "也不能補足 packet 缺少的證據。輸出仍只談工作，不提人物或場景。\n",
        "觀察場景不是裝飾：先完整執行它指定的證據操作。若 packet 直接支持"
        "該場景的專屬張力，優先由它形成 Nudge，不要改談相鄰鏡頭也能提出的"
        "泛用問題。\n",
        "場景只決定選哪一件事，不提供輸出素材；不要重述人物、動作或推理過程，"
        "也不要因此增加 Nudge 字數。\n",
        final_line,
        "共同的證據邊界、可靠沉默、單一 Nudge 與字數規則仍然優先；"
        "其餘由下方鏡頭決定。",
    ))
    return f"{base_prompt.rstrip()}\n\n{persona_header}\n\n{overlay}\n"


_WRAPPER_RE = re.compile(r"\[(?:end )?(?:Buddy|Masters[’'] Nudge)[^\]]*\]")
_CODEBLOCK_RE = re.compile(r"```[\s\S]*?```")
_INLINE_CODE_RE = re.compile(r"`([^`]*)`")
_MD_BOLD_RE = re.compile(r"\*{1,3}([^*]+)\*{1,3}")
_MD_HEADER_RE = re.compile(r"^#{1,6}\s*", re.MULTILINE)
_BOILERPLATE_PREFIX_RES = (
    re.compile(r"^(?:作為|身為)[^，,：:。！？!?]{1,40}[，,：:]\s*"),
    re.compile(
        r"^(?:整體來說|總體而言|總的來說|簡單來說|先說結論|"
        r"值得注意的是|需要注意的是|我認為|在我看來|以下是我的觀察)"
        r"[，,:：。.!！\s]*"
    ),
    re.compile(
        r"^(?:做得很好|整體做得不錯|這個方向很好|方向很清楚|"
        r"這是一個很好的(?:做法|方向|實作))"
        r"[，,:：。.!！\s]*"
    ),
)
_BOILERPLATE_SUFFIX_RE = re.compile(
    r"(?:希望(?:這|以上)?(?:對你)?有幫助|希望能幫到你|供參考|"
    r"以上(?:是我的觀察)?|謝謝(?:閱讀)?)"
    r"[。.!！\s]*$"
)
_TERMINAL_PUNCTUATION = frozenset("。？！.!?")
_CLAUSE_BOUNDARIES = frozenset("，,；;")
_QUESTION_ENDING_RE = re.compile(
    r"(?:嗎|呢|哪裡|何處|什麼|為何|怎麼|如何|是否|誰|哪個|多少|多久|幾次|幾個)$"
)
_MIXED_SCRIPT_SPACE_RES = (
    re.compile(r"(?<=[\u3400-\u9fff])\s+(?=[A-Za-z0-9])"),
    re.compile(r"(?<=[A-Za-z0-9])\s+(?=[\u3400-\u9fff])"),
)


def strip_boilerplate(text: str) -> str:
    previous = None
    while text and text != previous:
        previous = text
        for pattern in _BOILERPLATE_PREFIX_RES:
            text = pattern.sub("", text, count=1).lstrip()
        text = _BOILERPLATE_SUFFIX_RE.sub("", text, count=1).rstrip()
    return text


def _terminal_punctuation(text: str) -> str:
    return "？" if _QUESTION_ENDING_RE.search(text.rstrip()) else "。"


def _close_reaction(text: str, max_chars: int) -> str:
    """Close a finding without rejecting or spending another model call."""
    if not text or max_chars < 1:
        return ""
    if len(text) <= max_chars and text[-1] in _TERMINAL_PUNCTUATION:
        return text
    if len(text) < max_chars:
        return f"{text}{_terminal_punctuation(text)}"

    clipped = text[:max_chars]
    terminal_index = max(clipped.rfind(mark) for mark in _TERMINAL_PUNCTUATION)
    if terminal_index >= 0:
        return clipped[: terminal_index + 1].rstrip()

    boundary_index = max(clipped.rfind(mark) for mark in _CLAUSE_BOUNDARIES)
    if boundary_index >= 12:
        return f"{clipped[:boundary_index].rstrip()}。"

    compacted = clipped
    for pattern in _MIXED_SCRIPT_SPACE_RES:
        compacted = pattern.sub("", compacted)
    compacted = compacted[: max_chars - 1].rstrip()
    return f"{compacted}{_terminal_punctuation(compacted)}"


def sanitize_reaction(
    raw: str,
    max_chars: int = MAX_REACTION_CHARS,
) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    text = _CODEBLOCK_RE.sub("", text)
    text = _INLINE_CODE_RE.sub(r"\1", text)
    text = _MD_BOLD_RE.sub(r"\1", text)
    text = _MD_HEADER_RE.sub("", text)
    text = _WRAPPER_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = strip_boilerplate(text)
    return _close_reaction(text, max_chars)


def route_metadata(
    route: lens_router.ReviewRoute, *, domain: str = "software"
) -> dict[str, str]:
    return {
        "domain": domain,
        "stage": route.stage,
        "primary_lens": route.primary_lens,
        "effective_lens": route.effective_lens,
        "override_lens": route.override_lens,
        "trigger": route.trigger,
        "route_source": route.source,
        "candidate_lens": getattr(route, "candidate_lens", ""),
        "candidate_trigger": getattr(route, "candidate_trigger", ""),
        "suppression_reason": getattr(route, "suppression_reason", ""),
    }
