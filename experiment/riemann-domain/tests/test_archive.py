from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))


class RiemannArchiveTests(unittest.TestCase):
    def test_complete_persona_set_and_base_prompt_are_preserved(self):
        domain = ROOT / "domain" / "riemann"
        self.assertTrue((domain / "base-prompt.txt").is_file())
        self.assertEqual(
            {path.stem for path in (domain / "personas").glob("*.txt")},
            {"riemann", "ramanujan", "erdos", "tao", "selberg", "polya"},
        )

    def test_router_preserves_lifecycle_specialists_and_cooldown_metadata(self):
        path = ROOT / "riemann_router.py"
        spec = importlib.util.spec_from_file_location("archived_riemann_router", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(module.resolve_riemann_route("frame").effective_lens, "riemann")
        self.assertEqual(
            module.resolve_riemann_route("prove", "反覆失敗，已經卡住").effective_lens,
            "polya",
        )

    def test_retained_benchmark_and_closure_contract_is_present(self):
        expected = {
            "benchmark/README.md",
            "benchmark/interaction_annotations.json",
            "benchmark/interactions.md",
            "benchmark/snapshot/reactions.jsonl",
            "benchmark/snapshot/summary.json",
            "benchmark/test_benchmark.py",
            "benchmark/closures/README.md",
            "benchmark/closures/SHA256SUMS",
            "benchmark/closures/test_closures.py",
        }
        self.assertTrue(
            all((ROOT / relative).is_file() for relative in expected),
            "retained benchmark contract is incomplete",
        )
        self.assertEqual(
            {path.name for path in (ROOT / "benchmark" / "closures" / "arguments").glob("*.md")},
            {
                "nyman_cholesky_positivity_audit.md",
                "phi_pf5_audit.md",
                "toeplitz_uniform_route.md",
                "xi_jensen_route.md",
            },
        )
        self.assertEqual(
            {path.name for path in (ROOT / "benchmark" / "closures" / "verifiers").glob("*.py")},
            {
                "certify_t11_asymptotic_obstruction.py",
                "verify_complete_monotone_j12_not_uniform.py",
                "verify_degree3_not_degree4.py",
                "verify_nyman_gram_counterexamples.py",
                "verify_phi_pf5_arb.py",
            },
        )

    def test_readme_does_not_claim_removed_snapshot_paths(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for removed_path in (
            "plugin-snapshot/",
            "runtime-snapshot/",
            "research/staging/",
            "research/output/",
            "skill/SKILL.md",
            "tests/riemann_domain_integration_snapshot.py",
        ):
            with self.subTest(path=removed_path):
                self.assertNotIn(removed_path, readme)


if __name__ == "__main__":
    unittest.main()
