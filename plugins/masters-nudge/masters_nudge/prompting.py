"""Host-neutral prompt assembly and reaction sanitation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import lens_router
import persona_config


MAX_REACTION_CHARS = 52


def build_system_prompt(
    *,
    prompt_file: Path,
    persona_dir: Path,
    data_dir: Path,
    route: lens_router.ReviewRoute | None = None,
    log_error: Callable[[str], None] | None = None,
) -> str:
    logger = log_error or (lambda _message: None)
    try:
        base_prompt = prompt_file.read_text(encoding="utf-8")
    except Exception as exc:
        logger(f"prompt file read failed: {exc}")
        return ""

    route = route or lens_router.resolve_review_route(data_dir)
    persona = route.effective_lens
    if persona == "general":
        return base_prompt
    if persona not in persona_config.LENS_PERSONAS:
        supported = ", ".join(persona_config.LENS_PERSONAS)
        logger(f"unknown persona: {persona!r}; supported: {supported}")
        return ""

    persona_file = persona_dir / f"{persona}.txt"
    try:
        overlay = persona_file.read_text(encoding="utf-8").strip()
    except Exception as exc:
        logger(f"persona prompt read failed ({persona}): {exc}")
        return ""

    persona_header = (
        "# 工作流觀察鏡頭\n\n"
        f"這一輪借用 {persona_config.LENS_PERSONAS[persona]} 的核心概念與關注面向，"
        "決定從哪裡看這段工作流。\n"
        "不是扮演或模仿人物，也不是增加一份 code review。\n"
        "共同的證據邊界、可靠沉默、單一 Nudge 與字數規則仍然優先；"
        "其餘由下方鏡頭決定。"
    )
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


def strip_boilerplate(text: str) -> str:
    previous = None
    while text and text != previous:
        previous = text
        for pattern in _BOILERPLATE_PREFIX_RES:
            text = pattern.sub("", text, count=1).lstrip()
        text = _BOILERPLATE_SUFFIX_RE.sub("", text, count=1).rstrip()
    return text


def sanitize_reaction(raw: str, max_chars: int = MAX_REACTION_CHARS) -> str:
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
    return text[:max_chars]


def route_metadata(route: lens_router.ReviewRoute) -> dict[str, str]:
    return {
        "stage": route.stage,
        "primary_lens": route.primary_lens,
        "effective_lens": route.effective_lens,
        "override_lens": route.override_lens,
        "trigger": route.trigger,
        "route_source": route.source,
    }
