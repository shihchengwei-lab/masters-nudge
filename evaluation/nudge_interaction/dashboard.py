"""Render a standalone three-chart HTML dashboard."""

from __future__ import annotations

from html import escape
from typing import Mapping


REACTION_COLORS = {
    "explicit_uptake": "#22c55e",
    "reinterpretation": "#38bdf8",
    "possible_influence": "#a78bfa",
    "temporal_only": "#f59e0b",
    "no_observable_response": "#64748b",
}


def _bar(width: float, color: str) -> str:
    safe_width = max(0.0, min(100.0, width))
    return (
        '<div class="track"><span class="fill" '
        f'style="width:{safe_width:.1f}%;background:{color}"></span></div>'
    )


def render_dashboard(metrics: Mapping[str, object]) -> str:
    funnel = list(metrics["delivery_funnel"])
    reactions = list(metrics["reactions"])
    invocations = list(metrics["invocations"])
    total = int(metrics["invocation_total"])
    coverage = metrics["annotation_coverage"]

    funnel_rows = "".join(
        '<div class="row"><div class="row-head"><span>{label}</span>'
        '<strong>{count}</strong></div>{bar}<small>{pct:.1f}% of generated</small></div>'.format(
            label=escape(str(item["label"])),
            count=item["count"],
            bar=_bar(float(item["percent_of_generated"]), "#38bdf8"),
            pct=float(item["percent_of_generated"]),
        )
        for item in funnel
    )

    reaction_segments = "".join(
        '<span title="{label}: {count}" style="width:{pct:.1f}%;background:{color}"></span>'.format(
            label=escape(str(item["label"])),
            count=item["count"],
            pct=float(item["percent"]),
            color=REACTION_COLORS[str(item["key"])],
        )
        for item in reactions
        if item["count"]
    )
    reaction_legend = "".join(
        '<li><i style="background:{color}"></i><span>{label}</span>'
        '<strong>{count} · {pct:.1f}%</strong></li>'.format(
            color=REACTION_COLORS[str(item["key"])],
            label=escape(str(item["label"])),
            count=item["count"],
            pct=float(item["percent"]),
        )
        for item in reactions
    )

    invocation_rows = "".join(
        '<div class="row"><div class="row-head"><span>{name}</span>'
        '<strong>{count} · {pct:.1f}%</strong></div>{bar}'
        '<small>{statuses}</small></div>'.format(
            name=escape(str(item["display_name"])),
            count=item["count"],
            pct=float(item["percent"]),
            bar=_bar(float(item["percent"]), "#a78bfa"),
            statuses=escape(
                " / ".join(
                    f"{key} {value}"
                    for key, value in dict(item["statuses"]).items()
                )
                or "沒有調用"
            ),
        )
        for item in invocations
    )

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Shader Nudge 互動統計</title>
<style>
:root{{--ink:#e8eef8;--muted:#94a3b8;--panel:#111827;--line:#263449;--bg:#07101f}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 10% 0,#14223d 0,transparent 34%),var(--bg);color:var(--ink);font:15px/1.55 system-ui,"Noto Sans TC",sans-serif}}
main{{width:min(1080px,calc(100% - 36px));margin:44px auto 60px}}header{{margin-bottom:24px}}h1{{font-size:30px;margin:0 0 8px}}header p,.note,small{{color:var(--muted)}}.meta{{display:flex;gap:10px;flex-wrap:wrap}}.pill{{border:1px solid var(--line);border-radius:999px;padding:5px 10px;background:#0b1629}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}}section{{background:linear-gradient(145deg,#111c30,#0c1526);border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 20px 45px #02061755}}section:last-child{{grid-column:1/-1}}h2{{font-size:18px;margin:0 0 4px}}.subtitle{{margin:0 0 18px;color:var(--muted)}}.row{{margin:14px 0}}.row-head{{display:flex;justify-content:space-between;gap:12px;margin-bottom:6px}}.track{{height:10px;background:#1e293b;border-radius:999px;overflow:hidden}}.fill{{display:block;height:100%;border-radius:999px}}small{{display:block;margin-top:4px}}.stack{{display:flex;height:28px;overflow:hidden;border-radius:9px;background:#1e293b;margin:18px 0}}.stack span{{height:100%}}ul{{list-style:none;padding:0;margin:0}}li{{display:grid;grid-template-columns:12px 1fr auto;gap:9px;align-items:center;padding:7px 0;border-bottom:1px solid #1e293b}}li i{{width:10px;height:10px;border-radius:3px}}.note{{border-left:3px solid #f59e0b;padding:9px 12px;margin-top:20px;background:#1c191755}}
@media(max-width:760px){{.grid{{grid-template-columns:1fr}}section:last-child{{grid-column:auto}}}}
</style>
</head>
<body><main>
<header><h1>Shader Nudge 互動統計</h1>
<p>Session <code>{escape(str(metrics['session_id']))}</code></p>
<div class="meta"><span class="pill">Reviewer 呼叫 {total}</span><span class="pill">人工可評註 {coverage['evaluable']}</span><span class="pill">注入覆蓋 {coverage['percent_of_session_injected']:.1f}%</span></div></header>
<div class="grid">
<section data-chart="delivery-funnel"><h2>1. 交付漏斗</h2><p class="subtitle">從產生 finding 到後續內容對應</p>{funnel_rows}</section>
<section data-chart="reaction-classes"><h2>2. 反應分類</h2><p class="subtitle">固定 cohort：{escape(str(coverage['cohort_name']))}</p><div class="stack">{reaction_segments}</div><ul>{reaction_legend}</ul></section>
<section data-chart="persona-invocations"><h2>3. 六位大師調用率</h2><p class="subtitle">分母包含 finding、no_finding 與 error；零次仍顯示</p>{invocation_rows}</section>
</div><p class="note">{escape(str(metrics['interpretation_limit']))}</p>
</main></body></html>"""
