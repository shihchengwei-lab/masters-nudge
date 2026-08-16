#!/usr/bin/env python3
"""Deterministic lifecycle and specialist lens routing."""

from __future__ import annotations

import json
import os
import re
import tempfile
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

DYNAMIC_OVERRIDE_LIMIT = 5
DYNAMIC_COOLDOWN_REVIEWS = 3
ROUTE_STATE_SUFFIX = ".lens-route.json"


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


def _route_state_path(base_dir: Path, session_key: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(session_key or "unknown"))[:200]
    return Path(base_dir) / f"{safe or 'unknown'}{ROUTE_STATE_SUFFIX}"


def _load_route_state(path: Path) -> dict[str, int]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}

    def nonnegative_int(value: object) -> int:
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    return {
        "override_count": nonnegative_int(payload.get("override_count")),
        "cooldown_remaining": nonnegative_int(payload.get("cooldown_remaining")),
    }


def _save_route_state(path: Path, state: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".tmp",
        prefix="lens-route-",
        dir=path.parent,
        delete=False,
        encoding="utf-8",
    )
    temp_path = Path(handle.name)
    try:
        json.dump({"schema_version": 1, **state}, handle, ensure_ascii=False)
        handle.write("\n")
        handle.close()
        os.replace(temp_path, path)
    finally:
        try:
            handle.close()
        except Exception:
            pass
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass


def _specialist_trigger(evidence: str) -> tuple[str, str]:
    text = str(evidence or "")
    lamport = bool(LAMPORT_STRONG_RE.search(text)) or bool(
        LAMPORT_MECHANISM_RE.search(text) and LAMPORT_FAILURE_RE.search(text)
    )
    carmack = bool(CARMACK_DIRECT_RE.search(text)) or bool(
        MEASUREMENT_RE.search(text) and CARMACK_COST_RE.search(text)
    )
    if lamport:
        return "lamport", "state-ordering-evidence"
    if carmack:
        return "carmack", "measured-performance-evidence"
    if LINUS_COMPLETION_RE.search(text):
        return "linus", "completion-boundary-evidence"
    if JEFF_GOAL_RE.search(text):
        return "jeff", "goal-alignment-evidence"
    if FOWLER_GROWTH_RE.search(text):
        return "fowler", "knowledge-boundary-evidence"
    if BECK_WORKFLOW_RE.search(text):
        return "beck", "feedback-loop-evidence"
    return "", ""


def resolve_review_route(
    base_dir: Path,
    evidence: str = "",
    *,
    environ: Mapping[str, str] | None = None,
    checkpoint: bool = False,
    session_key: str = "",
) -> ReviewRoute:
    selection = persona_config.resolve_stage(base_dir, environ=environ)
    primary = selection.persona

    if primary not in persona_config.PERSONA_NAMES:
        return ReviewRoute(
            selection.stage, primary, primary, "", "", selection.source
        )
    if selection.locked or primary == "general" or not checkpoint:
        return ReviewRoute(
            selection.stage, primary, primary, "", "", selection.source
        )

    override, trigger = _specialist_trigger(evidence)
    if not override or override == primary:
        return ReviewRoute(
            selection.stage, primary, primary, "", "", selection.source
        )

    state_path = _route_state_path(base_dir, session_key)
    state = _load_route_state(state_path)
    if state["cooldown_remaining"] > 0:
        state["cooldown_remaining"] -= 1
        if state["cooldown_remaining"] == 0:
            state["override_count"] = 0
        _save_route_state(state_path, state)
        return ReviewRoute(
            selection.stage,
            primary,
            primary,
            "",
            "checkpoint-cooldown",
            selection.source,
            candidate_lens=override,
            candidate_trigger=trigger,
            suppression_reason="dynamic-override-cooldown",
        )

    state["override_count"] += 1
    if state["override_count"] >= DYNAMIC_OVERRIDE_LIMIT:
        state["cooldown_remaining"] = DYNAMIC_COOLDOWN_REVIEWS
    _save_route_state(state_path, state)
    return ReviewRoute(
        selection.stage,
        primary,
        override,
        override,
        trigger,
        selection.source,
        candidate_lens=override,
        candidate_trigger=trigger,
    )
