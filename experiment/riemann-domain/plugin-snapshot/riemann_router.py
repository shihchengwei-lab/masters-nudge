#!/usr/bin/env python3
"""Deterministic workflow routing for Riemann research."""

from __future__ import annotations

import re

from lens_router import ReviewRoute


STAGE_LENSES = {
    "frame": "riemann",
    "explore": "ramanujan",
    "attack": "erdos",
    "prove": "tao",
}

SELBERG_RE = re.compile(
    r"\b(?:mollifier|mollification|mean value|moment method|zero[- ]density|"
    r"density estimate|large sieve|contour shift|truncation|smoothing)\b|"
    r"平均值|矩估計|零點密度|密度估計|大篩法|圍道位移|截斷|平滑",
    re.IGNORECASE,
)
SELBERG_OBLIGATION_RE = re.compile(
    r"\b(?:bound|estimate|loss|error term|tail|uniform(?:ly)?|control|gap|"
    r"suffices?|need(?:s|ed)?|requires?)\b|"
    r"上界|估計|損失|誤差項|尾項|一致|控制|缺口|足夠|需要|要求",
    re.IGNORECASE,
)
POLYA_RE = re.compile(
    r"\b(?:stuck|give up|giving up|no ideas|failed approach|failed attempts?|"
    r"cannot proceed|can't proceed|dead end)\b|"
    r"卡住|放棄|沒有思路|沒有想法|反覆失敗|走不通|死路|無法繼續",
    re.IGNORECASE,
)
RAMANUJAN_RE = re.compile(
    r"\b(?:series expansion|power series|generating function|special values?|"
    r"recurrence|coefficient pattern|ansatz|toy model|numerical pattern|"
    r"first (?:few )?terms?)\b|"
    r"級數展開|冪級數|生成函數|特殊值|遞迴|係數規律|猜式|前幾項|數值規律|玩具模型",
    re.IGNORECASE,
)
ERDOS_RE = re.compile(
    r"\b(?:counterexamples?|extremal|random model|probabilistic|obstruction|"
    r"lower bounds?|worst case|adversarial|construct(?:ed)? example|"
    r"sharpness)\b|"
    r"反例|極端情況|極值|隨機模型|機率方法|障礙|下界|最壞情況|對抗|構造例|尖銳性",
    re.IGNORECASE,
)
TAO_STRUCTURE_RE = re.compile(
    r"\b(?:lemma|theorem|proof chain|dependency graph|sufficien(?:t|cy)|"
    r"necessar(?:y|ily)|equivalent|implies?|bootstrap|induction|closure)\b|"
    r"引理|定理|證明鏈|依賴圖|充分|必要|等價|推出|蘊含|歸納|升階|閉合",
    re.IGNORECASE,
)
TAO_RIGOR_RE = re.compile(
    r"\b(?:quantifiers?|uniform(?:ly)?|constants?|rate|limit exchange|"
    r"order of limits|for every|there exists|fixed|independent of)\b|"
    r"量詞|一致|常數|速率|極限交換|極限順序|任意|存在|固定|無關於",
    re.IGNORECASE,
)

MATH_LENSES = frozenset({"riemann", "ramanujan", "erdos", "tao", "selberg", "polya"})


def _automatic_trigger(evidence: str) -> tuple[str, str]:
    """Map a current workflow operation to one lens; strongest signals win."""
    text = str(evidence or "")
    if POLYA_RE.search(text):
        return "polya", "stalled-search-evidence"
    if TAO_STRUCTURE_RE.search(text) and TAO_RIGOR_RE.search(text):
        return "tao", "proof-closure-evidence"
    if ERDOS_RE.search(text):
        return "erdos", "counterexample-extremal-evidence"
    if RAMANUJAN_RE.search(text):
        return "ramanujan", "expansion-pattern-evidence"
    if SELBERG_RE.search(text) and SELBERG_OBLIGATION_RE.search(text):
        return "selberg", "analytic-estimate-evidence"
    return "", ""


def resolve_riemann_route(
    stage: str, evidence: str = "", *, pinned_lens: str = ""
) -> ReviewRoute:
    selected_stage = str(stage or "explore").strip().lower()
    if selected_stage not in STAGE_LENSES:
        selected_stage = "explore"
    primary = STAGE_LENSES[selected_stage]
    pinned = str(pinned_lens or "").strip().lower()
    if pinned in MATH_LENSES:
        return ReviewRoute(
            selected_stage,
            primary,
            pinned,
            "",
            "manual-pin",
            "environment",
        )
    override, trigger = _automatic_trigger(evidence)
    if override == primary:
        override = ""
    return ReviewRoute(
        selected_stage,
        primary,
        override or primary,
        override,
        trigger if override else "",
        "workspace_profile",
    )
