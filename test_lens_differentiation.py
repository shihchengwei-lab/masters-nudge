import json
import unittest
from pathlib import Path

from evaluation.lens_differentiation import lens_differentiation_analyze
from evaluation.lens_differentiation import lens_differentiation_run
from evaluation.lens_differentiation import lens_differentiation_run_v2


HERE = Path(__file__).resolve().parent
V2_RESULT = HERE / "evaluation" / "results" / "lens-differentiation-v2-20260813" / "execution-v1"


class LensDifferentiationTests(unittest.TestCase):
    def test_fixture_defines_same_packet_and_six_expectations(self):
        fixture = lens_differentiation_run.load_fixture()
        packet = lens_differentiation_run.build_packet(fixture)
        self.assertIn("[task anchor]", packet)
        self.assertIn("[agent final claim]", packet)
        self.assertIn("[tool evidence]", packet)
        self.assertEqual(
            set(lens_differentiation_run.LENSES),
            set(fixture["lens_expectations"]),
        )

    def test_jobs_share_packet_but_have_unique_lens_prompts(self):
        fixture = lens_differentiation_run.load_fixture()
        jobs = lens_differentiation_run.build_jobs(fixture, repeats=3, seed=20260823)
        self.assertEqual(18, len(jobs))
        self.assertEqual(1, len({job["packet_sha256"] for job in jobs}))
        prompt_by_lens = {}
        for job in jobs:
            prompt_by_lens.setdefault(job["lens"], job["system_prompt"])
        self.assertEqual(6, len(set(prompt_by_lens.values())))
        for lens, prompt in prompt_by_lens.items():
            display_name = {
                "jeff": "Jeff Dean",
                "beck": "Kent Beck",
                "fowler": "Martin Fowler",
                "linus": "Linus Torvalds",
                "lamport": "Leslie Lamport",
                "carmack": "John Carmack",
            }[lens]
            self.assertIn(display_name, prompt)

    def test_v2_uses_non_terminal_checkpoint_with_the_same_six_lenses(self):
        fixture = lens_differentiation_run_v2.load_fixture()
        packet = lens_differentiation_run_v2.build_packet(fixture)
        self.assertIn("[checkpoint evidence]", packet)
        self.assertIn("[recent agent context]", packet)
        self.assertNotIn("[agent final claim]", packet)
        jobs = lens_differentiation_run_v2.build_jobs(
            fixture, repeats=3, seed=20260824
        )
        self.assertEqual(18, len(jobs))
        self.assertEqual(1, len({job["packet_sha256"] for job in jobs}))

    def test_analyzer_selects_first_valid_finding_without_rewriting(self):
        fixture = lens_differentiation_run.load_fixture()
        rows = []
        expected_findings = []
        for lens_index, lens in enumerate(lens_differentiation_run.LENSES, 1):
            terms = fixture["lens_expectations"][lens]["terms"]
            for repeat in range(1, 4):
                finding = f"{terms[0]}：第{lens_index}視角第{repeat}次。"
                rows.append(
                    {
                        "lens": lens,
                        "repeat": repeat,
                        "status": "finding",
                        "finding": finding,
                        "characters": len(finding),
                        "raw_schema_valid": True,
                    }
                )
            expected_findings.append(f"{terms[0]}：第{lens_index}視角第1次。")
        summary, selection = lens_differentiation_analyze.analyze(fixture, rows)
        self.assertTrue(summary["automated_passed"])
        self.assertEqual(
            expected_findings,
            [row["finding"] for row in selection["selections"]],
        )

    def test_editorial_hero_lines_are_unedited_complete_run_outputs(self):
        runs = json.loads((V2_RESULT / "runs.json").read_text(encoding="utf-8"))["runs"]
        selections = json.loads(
            (V2_RESULT / "hero-selection-editorial.json").read_text(encoding="utf-8")
        )["selections"]
        by_key = {(row["lens"], row["repeat"]): row["finding"] for row in runs}
        self.assertEqual(6, len(selections))
        self.assertEqual(6, len({row["finding"] for row in selections}))
        for row in selections:
            self.assertEqual(by_key[(row["lens"], row["repeat"])], row["finding"])
            self.assertLessEqual(len(row["finding"]), 52)
            self.assertTrue(row["finding"].endswith(("。", "？", "！", "?", "!")))

    def test_readmes_use_the_real_tk_hero(self):
        from PIL import Image

        relative = "docs/images/masters-nudge-six-lenses-hero.png"
        self.assertIn(relative, (HERE / "README.md").read_text(encoding="utf-8"))
        self.assertIn(relative, (HERE / "README.zh-TW.md").read_text(encoding="utf-8"))
        with Image.open(HERE / relative) as hero:
            self.assertEqual("PNG", hero.format)
            self.assertEqual((1580, 650), hero.size)


if __name__ == "__main__":
    unittest.main()
