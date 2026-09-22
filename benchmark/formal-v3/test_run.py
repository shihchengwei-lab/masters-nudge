import os
from pathlib import Path
import unittest

import run


class BenchmarkContractTests(unittest.TestCase):
    def test_fixed_six_cases(self):
        self.assertEqual(
            [
                "django-window-filtering",
                "django-13128",
                "django-16263",
                "tokio-rs__tokio-6618",
                "anuraghazra__github-readme-stats-3442",
                "anuraghazra__github-readme-stats-2099",
            ],
            list(run.CASES),
        )

    def test_default_root_is_on_d_drive(self):
        if "MN_BENCHMARK_ROOT" not in os.environ:
            self.assertEqual("D:\\", Path(run.ROOT).anchor)

    def test_uses_updated_npm_codex_for_actor_and_provider(self):
        actor = Path(run.actor_bin())
        self.assertEqual("codex.exe", actor.name.lower())
        self.assertIn("appdata\\roaming\\npm", str(actor).lower())
        path_entries = run.environment("django-13128")["PATH"].split(os.pathsep)
        self.assertEqual(str(actor.parent).lower(), path_entries[0].lower())
        self.assertFalse(any(
            (Path(entry) / "codex.exe").is_file()
            for entry in path_entries[1:]
        ))

    def test_a_prompt_only_adds_the_taste_request(self):
        common = run.actor_prompt("django-13128", "B")
        a_prompt = run.actor_prompt("django-13128", "A")
        self.assertEqual(common + "\n請高品味的完成任務。\n", a_prompt)
        self.assertNotIn("Masters' Nudge", common)

    def test_judgment_keeps_scores_reason_and_improvement(self):
        required = set(run.JUDGE_SCHEMA["required"])
        self.assertEqual(
            {"winner", "x_score", "y_score", "reason", "improvement"},
            required,
        )


if __name__ == "__main__":
    unittest.main()
