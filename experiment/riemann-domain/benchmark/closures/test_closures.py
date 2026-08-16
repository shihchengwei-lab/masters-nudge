from __future__ import annotations

import importlib.util
import hashlib
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERIFIERS = ROOT / "verifiers"


def run(name: str) -> str:
    completed = subprocess.run(
        [sys.executable, str(VERIFIERS / name)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=60,
    )
    if completed.returncode:
        raise AssertionError(completed.stdout + completed.stderr)
    return completed.stdout


class ClosureCertificateTests(unittest.TestCase):
    def test_verifier_hash_manifest(self):
        for line in (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
            expected, relative = line.split(maxsplit=1)
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected)

    def test_jensen_degree_lift_counterexamples(self):
        self.assertIn("global-J12-to-degree-4 implication: REFUTED", run("verify_degree3_not_degree4.py"))
        self.assertIn("J12 + complete monotonicity", run("verify_complete_monotone_j12_not_uniform.py"))

    def test_nyman_gram_shortcuts(self):
        output = run("verify_nyman_gram_counterexamples.py")
        self.assertIn("PASS diagonal dominance counterexample", output)
        self.assertIn("PASS total positivity counterexample", output)

    @unittest.skipUnless(importlib.util.find_spec("flint"), "python-flint not installed")
    def test_actual_kernel_pf5_counterexample(self):
        self.assertIn("matrix det strictly negative: True", run("verify_phi_pf5_arb.py"))

    @unittest.skipUnless(importlib.util.find_spec("flint"), "python-flint not installed")
    def test_t11_rank_seven_asymptotic_obstruction(self):
        self.assertIn("CERTIFIED: C_7 < 0", run("certify_t11_asymptotic_obstruction.py"))


if __name__ == "__main__":
    unittest.main()
