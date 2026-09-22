import importlib.util
import unittest
from pathlib import Path


RUNNER = Path(__file__).with_name("run.py")


def load_runner():
    spec = importlib.util.spec_from_file_location("formal_v5_report_test", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class UnblindReportTest(unittest.TestCase):
    def test_rewrites_blind_labels_to_actual_arms(self):
        runner = load_runner()

        self.assertEqual(
            runner.unblind_judgment_text("X 較直接；Y 應移除分支。", {"X": "B", "Y": "A"}),
            "B 較直接；A 應移除分支。",
        )

    def test_experiment_design_defines_both_arms(self):
        runner = load_runner()
        design = "\n".join(runner.experiment_design_lines())

        self.assertIn('A 臂：不啟用 Masters’ Nudge', design)
        self.assertIn('「請高品味的完成任務。」', design)
        self.assertIn('B 臂：啟用 Masters’ Nudge', design)
        self.assertIn('不加入上述抽象要求', design)


if __name__ == "__main__":
    unittest.main()
