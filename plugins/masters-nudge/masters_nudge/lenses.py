"""Pure Lens catalog shared by settings, routing, and output validation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LensSpec:
    id: str
    name: str
    focus: str
    persona: str


LENSES = {
    "automatic": LensSpec(
        "automatic", "Automatic", "依目前決策壓力選擇濾鏡", ""
    ),
    "simplicity": LensSpec(
        "simplicity", "Simplicity", "必要複雜度與單一責任", "linus"
    ),
    "reliability": LensSpec(
        "reliability", "Reliability", "不變量、順序與部分失敗", "lamport"
    ),
    "performance": LensSpec(
        "performance", "Performance", "實際執行成本與少做工作", "carmack"
    ),
}

LENS_IDS = tuple(LENSES)
