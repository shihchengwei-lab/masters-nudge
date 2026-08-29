from __future__ import annotations

import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
if "pyarrow.parquet" not in sys.modules:
    pyarrow = types.ModuleType("pyarrow")
    parquet = types.ModuleType("pyarrow.parquet")
    pyarrow.parquet = parquet
    sys.modules["pyarrow"] = pyarrow
    sys.modules["pyarrow.parquet"] = parquet
SPEC = importlib.util.spec_from_file_location("formal_run_pilot", HERE / "run_pilot.py")
assert SPEC and SPEC.loader
RUN_PILOT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RUN_PILOT
SPEC.loader.exec_module(RUN_PILOT)


class ReviewerOptionTests(unittest.TestCase):
    def test_anthropic_opus_settings_are_explicit(self) -> None:
        values = RUN_PILOT.reviewer_env("anthropic", "claude-opus-5")

        self.assertEqual(values["MASTERS_NUDGE_PROVIDER"], "anthropic")
        self.assertEqual(values["MASTERS_NUDGE_MODEL"], "claude-opus-5")
        self.assertEqual(values["MASTERS_NUDGE_STAGE"], "automatic")
        self.assertEqual(values["MASTERS_NUDGE_TIMEOUT"], "90")

    def test_reviewer_settings_reject_empty_values(self) -> None:
        with self.assertRaises(ValueError):
            RUN_PILOT.reviewer_env("", "claude-opus-5")
        with self.assertRaises(ValueError):
            RUN_PILOT.reviewer_env("anthropic", "")

    def test_task_records_can_be_reused_without_dataset_loading(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            task_root = root / "tasks" / "s01"
            task_root.mkdir(parents=True)
            (task_root / "task.json").write_text(
                '{"task_key":"old","instance_id":"sample","repo":"org/repo",'
                '"base_commit":"abc","version":"1","problem_statement":"problem",'
                '"FAIL_TO_PASS":[],"PASS_TO_PASS":[],"order":"B_then_A"}',
                encoding="utf-8",
            )
            (task_root / "test.patch").write_text("patch-body", encoding="utf-8")
            contract = {
                "provisional_tasks": [
                    {
                        "task_key": "s01",
                        "instance_id": "sample",
                        "repo": "org/repo",
                        "base_commit": "abc",
                        "order": "A_then_B",
                    }
                ]
            }

            tasks = RUN_PILOT.tasks_from_records(contract, root / "tasks")

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["task_key"], "s01")
        self.assertEqual(tasks[0]["order"], "A_then_B")
        self.assertEqual(tasks[0]["test_patch"], "patch-body")


if __name__ == "__main__":
    unittest.main()
