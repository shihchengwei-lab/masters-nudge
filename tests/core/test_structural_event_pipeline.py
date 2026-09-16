"""Mutation detection wakes the Provider without assigning engineering meaning."""

from __future__ import annotations

import unittest

from masters_nudge import contracts
from masters_nudge.codex_adapter import normalize_tool_batch


class ExplicitMutationEvidenceTests(unittest.TestCase):
    def test_only_structured_mutation_payloads_create_completed_mutation(self):
        cases = (
            ({"patch": "*** Update File: app.py"}, "*** Update File: app.py"),
            ({"diff": "+++ b/app.py"}, "+++ b/app.py"),
            (
                {"path": "app.py", "old_string": "a", "new_string": "b"},
                "path: app.py\n[before]\na\n[end before]\n[after]\nb\n[end after]",
            ),
            (
                {"file_path": "empty.txt", "content": ""},
                "path: empty.txt\n[content]\n\n[end content]",
            ),
            ({"command": "echo build"}, None),
            ({"text": "preview only"}, None),
            ({"payload": {"path": "app.py", "content": "hidden"}}, None),
        )
        for payload, expected in cases:
            with self.subTest(payload=payload):
                mutation = contracts.completed_mutation_from_input(payload)
                self.assertEqual(None if mutation is None else mutation.change, expected)

    def test_patch_is_preserved_without_derived_metadata(self):
        patch = (
            "*** Begin Patch\n*** Update File: src/runtime.ts\n@@\n"
            "+const parallelOwner = true;\n*** End Patch"
        )
        mutation = contracts.completed_mutation_from_input(
            {
                "patch": patch
            }
        )
        self.assertEqual(mutation.change, patch)
        self.assertEqual(list(contracts.CompletedMutation.__dataclass_fields__), ["change"])

    def test_codex_apply_patch_command_is_explicit_mutation(self):
        events = normalize_tool_batch(
            {
                "hook_event_name": "PostToolBatch",
                "session_id": "session",
                "cwd": "",
                "tool_calls": [
                    {
                        "tool_name": "apply_patch",
                        "tool_input": {
                            "command": (
                                "*** Begin Patch\n*** Update File: app.py\n@@\n-old\n+new\n*** End Patch"
                            )
                        },
                        "tool_response": "done",
                    }
                ],
            }
        )
        self.assertIn("*** Update File: app.py", events[0].mutation.change)

    def test_command_text_does_not_infer_a_mutation_for_other_tools(self):
        events = normalize_tool_batch(
            {
                "hook_event_name": "PostToolBatch",
                "session_id": "session",
                "cwd": "",
                "tool_calls": [
                    {
                        "tool_name": "exec_command",
                        "tool_input": {"command": "*** Update File: app.py"},
                        "tool_response": "done",
                    }
                ],
            }
        )
        self.assertIsNone(events[0].mutation)


if __name__ == "__main__":
    unittest.main()
