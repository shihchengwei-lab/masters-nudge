"""The Nudge path is exactly task plus completed change to an optional message."""

from __future__ import annotations

import json
import unittest

import source_context
from masters_nudge.contracts import (
    CompletedMutation,
    Nudge,
    SessionRef,
    ToolCompleted,
    completed_mutation_from_input,
)
from masters_nudge.provider_contract import parse_nudge_result


class MinimalObservationTests(unittest.TestCase):
    def test_completed_mutation_contains_only_the_exact_change(self):
        self.assertEqual(list(CompletedMutation.__dataclass_fields__), ["change"])

    def test_observation_contains_only_task_and_completed_change(self):
        mutation = completed_mutation_from_input(
            {
                "patch": (
                    "*** Begin Patch\n"
                    "*** Update File: app.py\n"
                    "@@\n"
                    "+parallel_owner = True\n"
                    "*** End Patch"
                )
            }
        )
        event = ToolCompleted(
            SessionRef("codex_cli", "session"),
            "apply_patch",
            mutation=mutation,
        )

        observation = source_context.build_observation("Keep one owner", [event])

        self.assertIn("[task]\nKeep one owner\n[end task]", observation)
        self.assertIn("[change]\n*** Begin Patch", observation)
        self.assertIn("+parallel_owner = True", observation)
        self.assertNotIn("workspace", observation.lower())
        self.assertNotIn("source:", observation)

    def test_oversized_task_or_change_is_rejected_whole(self):
        mutation = completed_mutation_from_input(
            {"patch": "*** Begin Patch\n" + ("+x\n" * 20_000) + "*** End Patch"}
        )
        event = ToolCompleted(
            SessionRef("codex_cli", "session"),
            "apply_patch",
            mutation=mutation,
        )

        with self.assertRaises(source_context.ObservationTooLargeError):
            source_context.build_observation("Keep one owner", [event])


class MinimalResultTests(unittest.TestCase):
    def test_null_is_silence(self):
        parsed = parse_nudge_result(json.dumps({"nudge": None}))
        self.assertIsNone(parsed["nudge"])
        self.assertNotIn("error_kind", parsed)

    def test_message_and_evidence_form_one_nudge(self):
        parsed = parse_nudge_result(
            json.dumps(
                {
                    "nudge": {
                        "message": "兩個欄位正在表示同一個事實，可能彼此矛盾。",
                        "evidence": ["app.py:parallel_owner"],
                    }
                },
                ensure_ascii=False,
            )
        )
        nudge = parsed["nudge"]
        self.assertEqual(nudge["message"], "兩個欄位正在表示同一個事實，可能彼此矛盾。")
        self.assertEqual(nudge["evidence"], ["app.py:parallel_owner"])

    def test_partial_nudge_is_invalid(self):
        parsed = parse_nudge_result(
            json.dumps({"nudge": {"message": "有問題", "evidence": []}})
        )
        self.assertEqual(parsed["error_kind"], "invalid_output")

    def test_runtime_nudge_has_only_message_and_evidence(self):
        self.assertEqual(list(Nudge.__dataclass_fields__), ["message", "evidence"])


if __name__ == "__main__":
    unittest.main()
