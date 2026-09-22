#!/usr/bin/env python3
"""Round-five benchmark using the six calibrated Windows-native tasks."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
CALIBRATION_ROOT = Path(r"D:\masters-nudge-benchmark\round-5-calibration")
ARTIFACT_ROOT = CALIBRATION_ROOT / "formal-artifacts"
ROUND_TITLE = "第五輪 Benchmark"
CALIBRATION_EVIDENCE = "round-5 calibration actor reused as formal repeat-1 A"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


calibration = load("formal_v5_calibration", HERE / "calibrate.py")
runner = load("formal_v3_runner", REPO / "benchmark" / "formal-v3" / "run.py")

CASE_IDS = list(calibration.base.CASES)
ROWS = calibration.rows()
TASTE_DEFINITIONS = [
    "讓非法狀態無法被建立，而不是事後增加防護判斷。",
    "讓原因單向產生結果；事件是已發生的事實，狀態由事件推導，避免多條更新順序互相競爭。",
    "可預測性高於靈活性；消除副作用與隱藏依賴，讓局部程式的行為可以局部判斷。",
    "每項事實只有一個權威來源；其他呈現由來源推導，不同步維護多份副本。",
    "必要複雜度留在真正的邊界，核心路徑保持直接。",
    "抽象必須消除概念或分支；只增加包裝、改名或預留未證實的彈性，不算改善。",
]

runner.ROOT = CALIBRATION_ROOT
runner.ARTIFACT_ROOT = ARTIFACT_ROOT
runner.TMP = CALIBRATION_ROOT / "tmp-formal"
runner.PACKAGE = REPO / "plugins" / "masters-nudge"
runner.CASES = {
    case_id: {
        "task": calibration._task_text(ROWS[case_id]),
        "verify": calibration.base.CASES[case_id]["verify"],
    }
    for case_id in CASE_IDS
}
runner.TIMEOUT_SECONDS = 1800


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def setup() -> None:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    runner.TMP.mkdir(parents=True, exist_ok=True)
    selected = {
        row["case"]: row
        for row in read_json(CALIBRATION_ROOT / "preflight.json")
        if row["case"] in CASE_IDS and "seed" in row
    }
    if set(selected) != set(CASE_IDS):
        raise RuntimeError("calibration seeds are incomplete")
    manifest = {
        case_id: {
            "seed": selected[case_id]["seed"],
            "test_paths": selected[case_id]["test_paths"],
            "tests_sha256": selected[case_id]["tests_sha256"],
        }
        for case_id in CASE_IDS
    }
    write_json(CALIBRATION_ROOT / "manifest.json", manifest)


def import_first_a() -> None:
    setup()
    calibration_rows = {row["case"]: row for row in read_json(CALIBRATION_ROOT / "actor-summary.json")}
    summary_path = ARTIFACT_ROOT / "actor-summary.json"
    summary = read_json(summary_path) if summary_path.is_file() else []
    done = {(row["case"], row["repeat"], row["arm"]) for row in summary}
    for case_id in CASE_IDS:
        key = (case_id, 1, "A")
        if key in done:
            continue
        source = CALIBRATION_ROOT / "actors" / case_id
        target = ARTIFACT_ROOT / "runs" / case_id / "repeat-1" / "A"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)
        original = calibration_rows[case_id]
        row = {
            "case": case_id,
            "repeat": 1,
            "arm": "A",
            "elapsed_seconds": original["elapsed_seconds"],
            "actor_exit_code": original["actor_exit"],
            "actor_usage": original["usage"],
            "provider_usage": {},
            "provider_attempts": [],
            "provider_unresolved_batches": [],
            "file_change_events": None,
            "tests_unchanged": original["tests_unchanged"],
            "verification_exits": [original["contract_exit"]],
            "required_paths_present": True,
            "missing_required_paths": [],
            "contract_passed": original["contract_passed"],
            "changed_files": original["changed_files"],
            "invalid": "" if original["actor_exit"] == 0 else f"Actor exit {original['actor_exit']}",
            "evidence_source": CALIBRATION_EVIDENCE,
        }
        write_json(target / "result.json", row)
        summary.append(row)
        write_json(summary_path, summary)


def capture_untracked(case_id: str, artifact: Path, result: dict) -> None:
    workspace = CALIBRATION_ROOT / "cases" / case_id
    untracked = runner.git(workspace, "ls-files", "--others", "--exclude-standard").splitlines()
    if not untracked:
        return
    runner.git(workspace, "add", "-N", "--", *untracked)
    try:
        (artifact / "final.patch").write_text(
            runner.git(workspace, "diff", "--no-ext-diff", "--binary"), encoding="utf-8"
        )
    finally:
        runner.git(workspace, "reset", check=False)
    result["untracked_files_captured"] = untracked
    result["changed_files"] = sorted(set(result["changed_files"] + untracked))
    write_json(artifact / "result.json", result)


def actors() -> None:
    import_first_a()
    summary_path = ARTIFACT_ROOT / "actor-summary.json"
    summary = read_json(summary_path)
    done = {(row["case"], row["repeat"], row["arm"]) for row in summary}
    schedule = []
    schedule.extend((case_id, 1, "B") for case_id in CASE_IDS)
    for index, case_id in enumerate(CASE_IDS):
        order = ("A", "B") if index % 2 == 0 else ("B", "A")
        schedule.extend((case_id, 2, arm) for arm in order)
    for case_id, repeat, arm in schedule:
        if (case_id, repeat, arm) in done:
            continue
        result = runner.execute(case_id, repeat, arm)
        artifact = ARTIFACT_ROOT / "runs" / case_id / f"repeat-{repeat}" / arm
        capture_untracked(case_id, artifact, result)
        summary.append(result)
        write_json(summary_path, summary)
        print(json.dumps({key: result[key] for key in (
            "case", "repeat", "arm", "invalid", "contract_passed", "elapsed_seconds"
        )}, ensure_ascii=False), flush=True)
        if result["invalid"]:
            raise RuntimeError(f"benchmark tool fault: {result['invalid']}")


def judge_prompt(case_id: str, x: str, y: str) -> str:
    definitions = "\n".join(
        f"{number}. {definition}" for number, definition in enumerate(TASTE_DEFINITIONS, 1)
    )
    return f"""You are a blind code-quality judge. Both implementations passed the same immutable
contract. Compare engineering quality only; do not guess their origin.

Use these six definitions of engineering taste:
{definitions}

Apply them to concrete structure in the diff. Do not reward size, comments, formatting, tests, or
similarity to an expected patch by itself. Score each implementation from 1 to 5. Explain the
material structural difference and give one concrete improvement for the weaker implementation.
Return tie when neither has a material structural advantage.

TASK
{runner.CASES[case_id]['task']}

IMPLEMENTATION X
{x}

IMPLEMENTATION Y
{y}
"""


runner.judge_prompt = judge_prompt


def unblind_judgment_text(text: str, mapping: dict[str, str]) -> str:
    """Replace blind X/Y implementation labels with their actual A/B arms."""
    return re.sub(
        r"(?<![A-Za-z0-9_])([XY])(?![A-Za-z0-9_])",
        lambda match: mapping[match.group(1)],
        text,
    )


def experiment_design_lines() -> list[str]:
    return [
        "## 測試設計",
        "",
        f"- 共同條件：六個 repository 任務；每題每臂各獨立執行兩次，共 24 次。"
        f"Actor 均使用 `{runner.ACTOR_MODEL}`、medium reasoning、相同起始 commit、"
        "相同不可修改測試與相同執行限制。",
        "- A 臂：不啟用 Masters’ Nudge；任務提示額外加入「請高品味的完成任務。」。",
        "- B 臂：啟用 Masters’ Nudge，不加入上述抽象要求；每次 `apply_patch` 後由 Provider "
        "判斷要回饋一則 Nudge 或沉默，結果回到 Actor 的工作脈絡。",
        f"- 盲評：兩位 `{runner.JUDGE_MODEL}` 評審先取得同一組六條品味定義，再以互換的 X／Y "
        "順序比較同題同次的 A／B；兩位結論不同時才啟用第三位。報告已將 X／Y 解盲為 A／B。",
        "- A 臂第一輪沿用校準時保存的六筆實作：高品味要求置於任務正文前；第二輪置於共同提示末尾。"
        "文字內容與其他執行條件相同，但位置差異仍是本輪限制。",
    ]


def report() -> None:
    actors_data = read_json(ARTIFACT_ROOT / "actor-summary.json")
    judges = read_json(ARTIFACT_ROOT / "judge-summary.json")
    by_arm = {arm: [row for row in actors_data if row["arm"] == arm] for arm in ("A", "B")}
    winners = {key: sum(row["winner"] == key for row in judges) for key in ("A", "B", "tie", "not_judged")}

    def usage(rows: list[dict], key: str) -> int:
        return sum(
            int(row.get(field, {}).get(key) or 0)
            for row in rows
            for field in ("actor_usage", "provider_usage")
        )

    def non_cached_input(rows: list[dict]) -> int:
        return usage(rows, "input_tokens") - usage(rows, "cached_input_tokens")

    lines = [
        f"# {ROUND_TITLE}", "", "## 六條品味定義", "",
        *[f"{number}. {text}" for number, text in enumerate(TASTE_DEFINITIONS, 1)],
        "", *experiment_design_lines(),
        "", "## 結果", "", "| 指標 | A | B |", "|---|---:|---:|",
        f"| 契約完成 | {sum(row['contract_passed'] for row in by_arm['A'])}/12 | {sum(row['contract_passed'] for row in by_arm['B'])}/12 |",
        f"| 品味勝出 | {winners['A']} | {winners['B']} |",
        f"| 平手 | {winners['tie']} | {winners['tie']} |",
        f"| 總耗時 | {sum(row['elapsed_seconds'] for row in by_arm['A']):,.1f} 秒 | {sum(row['elapsed_seconds'] for row in by_arm['B']):,.1f} 秒 |",
        f"| 非快取輸入 Token | {non_cached_input(by_arm['A']):,} | {non_cached_input(by_arm['B']):,} |",
        f"| 快取輸入 Token | {usage(by_arm['A'], 'cached_input_tokens'):,} | {usage(by_arm['B'], 'cached_input_tokens'):,} |",
        f"| 輸出 Token | {usage(by_arm['A'], 'output_tokens'):,} | {usage(by_arm['B'], 'output_tokens'):,} |",
        "", "## 各組盲評", "", "| 題目 | 次數 | 勝者 | 評語與改進 |", "|---|---:|:---:|---|",
    ]
    for row in judges:
        detail = " / ".join(
            f"評審{judge['judge']}（選 {judge['winner_arm']}）："
            f"{unblind_judgment_text(judge['reason'], judge['mapping'])} "
            f"改進：{unblind_judgment_text(judge['improvement'], judge['mapping'])}"
            .replace("|", "\\|").replace("\n", " ")
            for judge in row["judges"]
        ) or row.get("reason", "")
        lines.append(f"| {row['case']} | {row['repeat']} | {row['winner']} | {detail} |")
    attempts = [attempt for row in by_arm["B"] for attempt in row.get("provider_attempts", [])]
    lines.extend(["", "## 證據範圍", "", f"- 未評品味：{winners['not_judged']} 組。",
                  f"- Provider 共呼叫 {len(attempts)} 次：{sum(item['outcome'] == 'feedback' for item in attempts)} 次回饋、{sum(item['outcome'] == 'silence' for item in attempts)} 次沉默。",
                  "- A 第一輪沿用校準時相同條件下保存的六筆實作。",
                  "- 個別 Actor、Provider 與評審證據保存在 `formal-artifacts`。", ""])
    (HERE / "RESULTS.zh-TW.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"actors", "judge", "report"}:
        print("usage: run.py actors|judge|report", file=sys.stderr)
        return 2
    if sys.argv[1] == "actors":
        actors()
    elif sys.argv[1] == "judge":
        runner.judges()
    else:
        report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
