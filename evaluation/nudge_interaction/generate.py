"""Generate metrics.json and dashboard.html from local interaction evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluation.nudge_interaction.analysis import analyze_session
from evaluation.nudge_interaction.dashboard import render_dashboard


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--telemetry", type=Path, required=True)
    parser.add_argument("--reaction-log", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    annotation_document = json.loads(args.annotations.read_text(encoding="utf-8"))
    metrics = analyze_session(
        _read_jsonl(args.telemetry),
        _read_jsonl(args.reaction_log),
        annotation_document,
        args.session_id,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "dashboard.html").write_text(
        render_dashboard(metrics), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
