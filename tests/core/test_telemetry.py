from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import review_telemetry


class ReviewTelemetryTests(unittest.TestCase):
    def test_record_review_only_appends_content_free_metadata(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            result = review_telemetry.record_review(
                root,
                {
                    "session_id": "session-1",
                    "status": "finding",
                    "kind": "stop",
                    "model": "model-1",
                    "input_chars": 20,
                    "latency_ms": 30,
                    "hook_event": "PostToolBatch",
                    "usage": {"input_tokens": 10},
                    "finding": "must never be persisted",
                    "shadow_candidates": ["no_new_evidence"],
                },
                now=datetime(2026, 8, 23, tzinfo=timezone.utc),
            )

            records = [
                json.loads(line)
                for line in (root / review_telemetry.TELEMETRY_FILE)
                .read_text(encoding="utf-8")
                .splitlines()
            ]

            self.assertEqual(result, {"recorded": True})
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["hook_event"], "PostToolBatch")
            self.assertNotIn("finding", records[0])
            self.assertNotIn("shadow_candidates", records[0])
            self.assertFalse((root / "shadow-evaluation.json").exists())
            self.assertFalse((root / "shadow-evaluation.md").exists())
            self.assertEqual(list(root.glob("*.log")), [])

    def test_runtime_has_no_shadow_policy_api(self):
        self.assertFalse(hasattr(review_telemetry, "stop_shadow_candidates"))
        self.assertFalse(hasattr(review_telemetry, "configured_evaluation_days"))
        self.assertFalse(hasattr(review_telemetry, "configured_target_calls"))


if __name__ == "__main__":
    unittest.main()
