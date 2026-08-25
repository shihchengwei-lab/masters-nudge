#!/usr/bin/env python3
"""Deterministic lifecycle and specialist lens routing."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import persona_config


LAMPORT_STRONG_RE = re.compile(
    r"\b(?:retry|retries|retrying|idempotenc(?:y|e)|race condition|deadlock|"
    r"out[- ]of[- ]order|duplicate delivery|partial failure)\b|"
    r"重試|冪等|競態|死鎖|亂序|重複(?:交付|投遞|處理)|部分失敗",
    re.IGNORECASE,
)
LAMPORT_MECHANISM_RE = re.compile(
    r"\b(?:async|await|queue|lock|mutex|semaphore|cache|state|event|message)\b|"
    r"非同步|佇列|隊列|鎖|快取|緩存|狀態|事件|訊息|消息",
    re.IGNORECASE,
)
LAMPORT_FAILURE_RE = re.compile(
    r"\b(?:timeout|ordering|stale|duplicate|concurrent|atomic|lost update)\b|"
    r"逾時|超時|順序|過期|陳舊|重複|並發|併發|原子|更新遺失",
    re.IGNORECASE,
)

CARMACK_DIRECT_RE = re.compile(
    r"\b(?:profiler|profiling|benchmark(?:ing)?|flamegraph|flame graph|"
    r"performance trace|perf record)\b|基準測試|效能分析|性能分析|火焰圖",
    re.IGNORECASE,
)
CARMACK_COST_RE = re.compile(
    r"\b(?:latency|throughput|allocations?|copies|copying|i/o|io bound|"
    r"hot path|hotspot|syscalls?|data movement)\b|"
    r"延遲|吞吐|配置|分配|複製|拷貝|輸入輸出|熱路徑|熱點|系統呼叫|資料搬運|數據搬運",
    re.IGNORECASE,
)
MEASUREMENT_RE = re.compile(
    r"(?:\b\d+(?:\.\d+)?\s*(?:ns|us|µs|ms|s|kb|mb|gb|kib|mib|gib|%|"
    r"rps|qps|ops/s|req/s)\b)|(?:快|慢|降低|提升|增加|減少)\s*\d+(?:\.\d+)?\s*%",
    re.IGNORECASE,
)
BECK_WORKFLOW_RE = re.compile(
    r"feedback loop|"
    r"重複(?:測試|驗證|命令)|沒有新回饋|回饋迴路",
    re.IGNORECASE,
)
JEFF_CAUSE_RE = re.compile(
    r"source of truth|ownership|upstream constraint|system boundary|"
    r"資料來源|狀態擁有者|上游限制|系統邊界",
    re.IGNORECASE,
)
JEFF_COMPENSATION_RE = re.compile(
    r"downstream|fallback|bypass|compensation|synchroni[sz]|"
    r"下游|備援|旁路|補償|同步層",
    re.IGNORECASE,
)
LINUS_DIRECT_RE = re.compile(
    r"compatibility wrapper|pass[- ]through|forwarding layer|delegate\(\)|"
    r"相容包裝|轉交層|只轉交|委派層",
    re.IGNORECASE,
)
LINUS_COMPLETION_RE = re.compile(
    r"completion boundary|"
    r"交付邊界|完成依據|路徑已耗盡",
    re.IGNORECASE,
)
FOWLER_GROWTH_RE = re.compile(
    r"compensation spread|knowledge boundary|變動擴散|"
    r"補償邏輯|知識邊界",
    re.IGNORECASE,
)

@dataclass(frozen=True)
class ReviewRoute:
    stage: str
    primary_lens: str
    effective_lens: str
    override_lens: str
    trigger: str
    source: str


STRUCTURED_CONCERNS = {
    "feedback-loop": ("beck", "feedback-loop-evidence"),
    "system-causality": ("jeff", "system-causality-evidence"),
    "completion-boundary": ("linus", "completion-boundary-evidence"),
    "knowledge-boundary": ("fowler", "knowledge-boundary-evidence"),
    "state-ordering": ("lamport", "state-ordering-evidence"),
    "measured-performance": ("carmack", "measured-performance-evidence"),
}


def _specialist_concerns(evidence: str) -> list[str]:
    text = str(evidence or "")
    concerns: list[str] = []
    lamport = bool(LAMPORT_STRONG_RE.search(text)) or bool(
        LAMPORT_MECHANISM_RE.search(text) and LAMPORT_FAILURE_RE.search(text)
    )
    carmack = bool(CARMACK_DIRECT_RE.search(text)) or bool(
        MEASUREMENT_RE.search(text) and CARMACK_COST_RE.search(text)
    )
    if lamport:
        concerns.append("state-ordering")
    if carmack:
        concerns.append("measured-performance")
    if LINUS_COMPLETION_RE.search(text) or LINUS_DIRECT_RE.search(text):
        concerns.append("completion-boundary")
    if JEFF_CAUSE_RE.search(text) and JEFF_COMPENSATION_RE.search(text):
        concerns.append("system-causality")
    if FOWLER_GROWTH_RE.search(text):
        concerns.append("knowledge-boundary")
    if BECK_WORKFLOW_RE.search(text):
        concerns.append("feedback-loop")
    return concerns


def structured_concern_for_evidence(evidence: str) -> str:
    """Return the first evidence-backed lens concern, if any."""
    concerns = _specialist_concerns(evidence)
    return concerns[0] if concerns else ""


def resolve_review_route(
    base_dir: Path,
    evidence: str = "",
    *,
    environ: Mapping[str, str] | None = None,
    checkpoint: bool = False,
    routing_concern: str = "",
) -> ReviewRoute:
    selection = persona_config.resolve_stage(base_dir, environ=environ)
    primary = selection.persona

    if primary not in persona_config.PERSONA_NAMES:
        return ReviewRoute(
            selection.stage, primary, primary, "", "", selection.source
        )
    if not checkpoint:
        return ReviewRoute(
            selection.stage, primary, primary, "", "", selection.source
        )

    evidence_candidates = []
    structured_candidate = STRUCTURED_CONCERNS.get(str(routing_concern or ""))
    if structured_candidate is not None:
        evidence_candidates.append(structured_candidate)
    for concern in _specialist_concerns(evidence):
        candidate = STRUCTURED_CONCERNS[concern]
        if candidate not in evidence_candidates:
            evidence_candidates.append(candidate)
    evidence_choice = evidence_candidates[0] if evidence_candidates else None
    if evidence_choice is not None:
        override, trigger = evidence_choice
    else:
        override, trigger = primary, ""
    source = (
        "software_evidence_override"
        if trigger
        else selection.source
    )
    if override == primary:
        return ReviewRoute(
            selection.stage,
            primary,
            primary,
            "",
            trigger,
            source,
        )
    return ReviewRoute(
        selection.stage,
        primary,
        override,
        override,
        trigger,
        source,
    )
