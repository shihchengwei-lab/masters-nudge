from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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

    def test_runtime_and_research_snapshots_are_present(self):
        expected_runtime = {
            "core.py", "prompting.py", "storage.py", "profiles.py",
            "buddy_window.py", "masters_nudge_cli.py", "persona_config.py",
        }
        runtime = {path.name for path in (ROOT / "runtime-snapshot").glob("*.py")}
        self.assertEqual(runtime, expected_runtime)
        staging = ROOT / "research" / "staging"
        self.assertTrue((staging / "research_log.md").is_file())
        self.assertTrue((staging / "HANDOFF.md").is_file())
        self.assertTrue((staging / "COMPLETION_AUDIT_2026-08-16.md").is_file())
        self.assertTrue((staging / "strategy_audit.md").is_file())
        self.assertTrue((ROOT / "research" / "output" / "verification_report.json").is_file())
        self.assertTrue((ROOT / "skill" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
