from __future__ import annotations

import json
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class BenchmarkSnapshotTests(unittest.TestCase):
    def test_frozen_counts_match_reported_run(self):
        summary = json.loads((ROOT / "snapshot" / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["runs"], 3)
        self.assertEqual(summary["records"], 142)
        self.assertEqual(summary["findings"], 102)
        self.assertEqual(summary["review_statuses"], 23)
        self.assertEqual(summary["confirmed_injections"], 17)
        self.assertEqual(summary["generated_with_receipt_tracking"], 19)

    def test_snapshot_has_no_local_paths_or_raw_session_ids(self):
        raw = (ROOT / "snapshot" / "reactions.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("C:\\Users", raw)
        self.assertNotIn("D:\\riemann", raw)
        self.assertNotIn("session_id", raw)
        self.assertNotIn("turn_id", raw)
        rows = [json.loads(line) for line in raw.splitlines()]
        self.assertEqual({row["run"] for row in rows}, {"run-1", "run-2", "run-3"})

    def test_all_transcript_visible_injections_are_annotated(self):
        payload = json.loads((ROOT / "interaction_annotations.json").read_text(encoding="utf-8"))
        annotations = payload["annotations"]
        self.assertEqual(len(annotations), 17)
        counts: dict[str, int] = {}
        for item in annotations:
            counts[item["classification"]] = counts.get(item["classification"], 0) + 1
        self.assertEqual(
            counts,
            {
                "direction_aligned": 10,
                "engaged_reframed": 2,
                "delayed": 1,
                "ambiguous_in_flight": 2,
                "not_adopted_or_late": 2,
            },
        )

    def test_human_readable_interactions_are_current(self):
        path = ROOT / "render_interactions.py"
        spec = importlib.util.spec_from_file_location("render_interactions", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        rendered = (ROOT / "interactions.md").read_text(encoding="utf-8")
        self.assertEqual(rendered, module.render())
        self.assertEqual(rendered.count("\n### "), 17)
        self.assertIn("102 findings", rendered)
        self.assertIn("19 findings", rendered)


if __name__ == "__main__":
    unittest.main()
