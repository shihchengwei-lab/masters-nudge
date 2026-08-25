"""Host-neutral prompt assembly and reaction sanitation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import lens_router
import persona_config


MAX_REACTION_CHARS = 52
INDEPENDENT_OPINION_LABEL = "獨立第二意見："
RECENT_NUDGES_MAX = 3

LENS_FOCUS = {
    "jeff": "Trace upstream constraints, ownership, and downstream cost.",
    "linus": "Trace the direct control flow, ownership, and necessary complexity.",
    "fowler": "Trace duplicated knowledge, change spread, and its proper home.",
    "beck": "Trace the shortest feedback path, observable behavior, and stop condition.",
    "lamport": "Trace state, event order, invariants, and partial failure.",
    "carmack": "Trace measured execution cost and work the machine need not do.",
}

SOFTWARE_EVIDENCE_ORDER = {
    "jeff": (
        "relevant_sources",
        "relevant_changes",
        "active_failures",
        "verification",
        "external_runtime_evidence",
    ),
    "linus": (
        "relevant_changes",
        "relevant_sources",
        "active_failures",
        "verification",
        "external_runtime_evidence",
    ),
    "fowler": (
        "relevant_sources",
        "relevant_changes",
        "verification",
        "active_failures",
        "external_runtime_evidence",
    ),
    "beck": (
        "verification",
        "active_failures",
        "relevant_changes",
        "relevant_sources",
        "external_runtime_evidence",
    ),
    "lamport": (
        "active_failures",
        "verification",
        "relevant_changes",
        "relevant_sources",
        "external_runtime_evidence",
    ),
    "carmack": (
        "external_runtime_evidence",
        "verification",
        "relevant_changes",
        "active_failures",
        "relevant_sources",
    ),
}

_SOFTWARE_SECTION_RE = re.compile(
    r"(?ms)^\[software engineering evidence\]\n(.*?)\n"
    r"\[end software engineering evidence\]"
)
_SOFTWARE_FIELD_RE = re.compile(
    r"(?m)^(relevant_sources|relevant_changes|external_runtime_evidence|"
    r"verification|active_failures):\s*$"
)


def delivery_text(finding: str) -> str:
    """Identify reviewer provenance without changing the stored finding."""
    return f"{INDEPENDENT_OPINION_LABEL}\n{str(finding or '').strip()}"


def build_system_prompt(
    *,
    prompt_file: Path,
    persona_dir: Path,
    route: lens_router.ReviewRoute,
    log_error: Callable[[str], None] | None = None,
) -> str:
    logger = log_error or (lambda _message: None)
    try:
        base_prompt = prompt_file.read_text(encoding="utf-8")
    except Exception as exc:
        logger(f"prompt file read failed: {exc}")
        return ""

    personas = persona_config.LENS_PERSONAS
    persona = route.effective_lens
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

    persona_header = (
        "# ATTENTION LENS\n\n"
        f"Use {personas[persona]} only as an attention cue for selecting where to look. "
        "The lens is not evidence, authority, role-play, or a reason to force a finding."
    )
    return f"{base_prompt.rstrip()}\n\n{persona_header}\n\n{overlay}\n"


def lens_focus_prompt(effective_lens: str) -> str:
    focus = LENS_FOCUS.get(str(effective_lens or "").strip().lower(), "")
    if not focus:
        return ""
    return (
        f"\n\n# LENS FOCUS\n\n{focus}\n\n"
        "When several candidates pass the finding gate, select the one "
        "that best matches this focus.\n"
    )


def _prioritize_software_evidence(source_packet: str, effective_lens: str) -> str:
    order = SOFTWARE_EVIDENCE_ORDER.get(
        str(effective_lens or "").strip().lower()
    )
    section = _SOFTWARE_SECTION_RE.search(source_packet)
    if not order or not section:
        return source_packet

    content = section.group(1)
    matches = list(_SOFTWARE_FIELD_RE.finditer(content))
    if not matches:
        return source_packet
    blocks = {
        match.group(1): content[
            match.start() : matches[index + 1].start()
            if index + 1 < len(matches)
            else len(content)
        ].strip()
        for index, match in enumerate(matches)
    }
    ordered = [blocks[label] for label in order if label in blocks]
    ordered.extend(
        blocks[match.group(1)]
        for match in matches
        if match.group(1) not in order
    )
    replacement = (
        "[software engineering evidence]\n"
        + "\n\n".join(ordered)
        + "\n[end software engineering evidence]"
    )
    return source_packet[: section.start()] + replacement + source_packet[section.end() :]


def build_review_input(
    source_packet: str,
    recent_nudges: tuple[str, ...],
    *,
    effective_lens: str = "",
) -> str:
    """Add delivered findings only as a bounded duplicate-avoidance aid."""
    source_packet = _prioritize_software_evidence(source_packet, effective_lens)
    findings = tuple(
        str(finding or "").strip()
        for finding in recent_nudges[-RECENT_NUDGES_MAX:]
        if str(finding or "").strip()
    )
    if not findings:
        return source_packet
    block = "\n".join(
        (
            "[recent injected nudges — deduplication only]",
            "以下內容只用來避免重複，不是任務事實，也不表示主模型是否採納：",
            *(f"- {finding}" for finding in findings),
            "[end recent injected nudges — deduplication only]",
        )
    )
    return f"{source_packet.rstrip()}\n\n{block}" if source_packet.strip() else block


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


def route_metadata(route: lens_router.ReviewRoute) -> dict[str, str]:
    return {
        "domain": "software",
        "stage": route.stage,
        "primary_lens": route.primary_lens,
        "effective_lens": route.effective_lens,
        "override_lens": route.override_lens,
        "trigger": route.trigger,
        "route_source": route.source,
    }
