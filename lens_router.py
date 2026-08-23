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
    r"repeated-command-family|repeated-failure-family|feedback loop|"
    r"重複(?:測試|驗證|命令)|沒有新回饋|回饋迴路",
    re.IGNORECASE,
)
JEFF_GOAL_RE = re.compile(
    r"local proxy|acceptance criteria|goal alignment|局部(?:代理|指標|成果)|"
    r"驗收條件|使用者結果|目標對齊",
    re.IGNORECASE,
)
LINUS_COMPLETION_RE = re.compile(
    r"goal-(?:complete|blocked)|goal-transition|completion boundary|"
    r"交付邊界|完成依據|路徑已耗盡",
    re.IGNORECASE,
)
FOWLER_GROWTH_RE = re.compile(
    r"diff-growth|compensation spread|knowledge boundary|變動擴散|"
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
    candidate_lens: str = ""
    candidate_trigger: str = ""
    suppression_reason: str = ""


def _specialist_candidates(evidence: str) -> list[tuple[str, str]]:
    text = str(evidence or "")
    candidates: list[tuple[str, str]] = []
    lamport = bool(LAMPORT_STRONG_RE.search(text)) or bool(
        LAMPORT_MECHANISM_RE.search(text) and LAMPORT_FAILURE_RE.search(text)
    )
    carmack = bool(CARMACK_DIRECT_RE.search(text)) or bool(
        MEASUREMENT_RE.search(text) and CARMACK_COST_RE.search(text)
    )
    if lamport:
        candidates.append(("lamport", "state-ordering-evidence"))
    if carmack:
        candidates.append(("carmack", "measured-performance-evidence"))
    if LINUS_COMPLETION_RE.search(text):
        candidates.append(("linus", "completion-boundary-evidence"))
    if JEFF_GOAL_RE.search(text):
        candidates.append(("jeff", "goal-alignment-evidence"))
    if FOWLER_GROWTH_RE.search(text):
        candidates.append(("fowler", "knowledge-boundary-evidence"))
    if BECK_WORKFLOW_RE.search(text):
        candidates.append(("beck", "feedback-loop-evidence"))
    return candidates


def resolve_review_route(
    base_dir: Path,
    evidence: str = "",
    *,
    environ: Mapping[str, str] | None = None,
    checkpoint: bool = False,
    injected_personas: tuple[str, ...] = (),
) -> ReviewRoute:
    selection = persona_config.resolve_stage(base_dir, environ=environ)
    primary = selection.persona

    if primary not in persona_config.PERSONA_NAMES:
        return ReviewRoute(
            selection.stage, primary, primary, "", "", selection.source
        )
    if primary == "general" or not checkpoint:
        return ReviewRoute(
            selection.stage, primary, primary, "", "", selection.source
        )

    cooldown = tuple(
        lens for lens in injected_personas[-2:]
        if lens in persona_config.LENS_PERSONAS
    )
    ineligible = set(cooldown)
    evidence_candidates = _specialist_candidates(evidence)
    evidence_choice = next(
        (candidate for candidate in evidence_candidates if candidate[0] not in ineligible),
        None,
    )
    if evidence_choice is not None:
        override, trigger = evidence_choice
    elif primary not in ineligible:
        override, trigger = primary, ""
    else:
        override, trigger = "general", ""
    suppression_reason = (
        f"injected-persona-cooldown:{','.join(cooldown)}" if cooldown else ""
    )
    source = (
        "software_evidence_override"
        if trigger
        else "software_cooldown_general"
        if override == "general"
        else selection.source
    )
    if override == "general":
        return ReviewRoute(
            selection.stage,
            primary,
            "general",
            "",
            "",
            source,
            candidate_lens=(evidence_candidates[0][0] if evidence_candidates else ""),
            candidate_trigger=(evidence_candidates[0][1] if evidence_candidates else ""),
            suppression_reason=suppression_reason,
        )
    if override == primary:
        return ReviewRoute(
            selection.stage,
            primary,
            primary,
            "",
            trigger,
            source,
            candidate_lens=override if trigger else "",
            candidate_trigger=trigger,
            suppression_reason=suppression_reason,
        )
    return ReviewRoute(
        selection.stage,
        primary,
        override,
        override,
        trigger,
        source,
        candidate_lens=override,
        candidate_trigger=trigger,
        suppression_reason=suppression_reason,
    )
