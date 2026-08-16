from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import riemann_router
from masters_nudge import storage
from masters_nudge.contracts import EvidenceBundle, ReviewRequest, SessionRef
from masters_nudge.core import ReviewCore
from masters_nudge.profiles import (
    configure_workspace_profile,
    load_workspace_profile,
    resolve_reviewer,
)
from masters_nudge.prompting import build_system_prompt, sanitize_reaction
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


ROOT = Path(__file__).resolve().parent


def settings_for(root: Path) -> RuntimeSettings:
    return RuntimeSettings(
        "openai",
        "test-model",
        60,
        15,
        RuntimePaths(ROOT, root / "data", root / "legacy", root / "error.log"),
    )


class RiemannProfileTests(unittest.TestCase):
    def test_profile_is_scoped_to_exact_workspace(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            first = root / "one"
            second = root / "two"
            first.mkdir()
            second.mkdir()
            result = configure_workspace_profile(
                root / "data", first, domain="riemann", stage="explore",
                provider="anthropic", model="claude-opus-4-6",
                review_mode="stop_only",
            )
            profile, error = load_workspace_profile(
                root / "data", SessionRef("codex_cli", "s", repo_root=str(first))
            )
            other, other_error = load_workspace_profile(
                root / "data", SessionRef("codex_cli", "s", repo_root=str(second))
            )
        self.assertTrue(result["saved"])
        self.assertFalse(error)
        self.assertEqual((profile.domain, profile.stage), ("riemann", "explore"))
        self.assertFalse(other_error)
        self.assertEqual(other.domain, "software")

    def test_environment_still_overrides_profile_reviewer(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = settings_for(root)
            workspace = root / "repo"
            workspace.mkdir()
            configure_workspace_profile(
                settings.paths.data_dir, workspace, domain="riemann", stage="prove",
                provider="anthropic", model="claude-opus-4-6", review_mode="stop_only",
            )
            profile, _ = load_workspace_profile(
                settings.paths.data_dir,
                SessionRef("codex_cli", "s", repo_root=str(workspace)),
            )
        self.assertEqual(
            resolve_reviewer(
                settings, profile,
                environ={"MASTERS_NUDGE_PROVIDER": "openai", "MASTERS_NUDGE_MODEL": "x"},
            ),
            ("openai", "x", "environment"),
        )


class RiemannRoutingTests(unittest.TestCase):
    def test_lifecycle_and_specialists_are_deterministic(self):
        self.assertEqual(riemann_router.resolve_riemann_route("frame").effective_lens, "riemann")
        self.assertEqual(riemann_router.resolve_riemann_route("explore").effective_lens, "ramanujan")
        self.assertEqual(riemann_router.resolve_riemann_route("attack").effective_lens, "erdos")
        self.assertEqual(riemann_router.resolve_riemann_route("prove").effective_lens, "tao")
        self.assertEqual(riemann_router.resolve_riemann_route("prove", "這裡使用零點密度估計").effective_lens, "selberg")
        self.assertEqual(riemann_router.resolve_riemann_route("prove", "反覆失敗，已經卡住").effective_lens, "polya")

    def test_workflow_operations_route_to_all_math_lenses(self):
        cases = {
            "先展開生成函數的前幾項尋找係數規律": "ramanujan",
            "構造反例並檢查最壞情況的下界": "erdos",
            "此引理要推出定理，仍需核對一致常數與量詞": "tao",
            "大篩法的尾項仍需要一致上界": "selberg",
            "三條路反覆失敗，現在已經卡住": "polya",
        }
        for evidence, expected in cases.items():
            with self.subTest(expected=expected):
                route = riemann_router.resolve_riemann_route("frame", evidence)
                self.assertEqual(route.effective_lens, expected)
                self.assertEqual(route.override_lens, expected)

    def test_manual_pin_has_priority_over_automatic_specialist(self):
        route = riemann_router.resolve_riemann_route(
            "frame",
            "大篩法的尾項仍需要一致上界",
            pinned_lens="tao",
        )
        self.assertEqual(route.effective_lens, "tao")
        self.assertEqual(route.override_lens, "")
        self.assertEqual(route.trigger, "manual-pin")
        self.assertEqual(route.source, "environment")

    def test_every_primary_math_lens_builds_a_distinct_prompt(self):
        prompts = []
        for stage in ("frame", "explore", "attack", "prove"):
            prompts.append(build_system_prompt(
                prompt_file=ROOT / "domains" / "riemann" / "base-prompt.txt",
                persona_dir=ROOT / "domains" / "riemann" / "personas",
                data_dir=ROOT,
                route=riemann_router.resolve_riemann_route(stage),
                domain="riemann",
            ))
        self.assertEqual(len(set(prompts)), 4)
        self.assertTrue(all("數學研究鏡頭" in prompt for prompt in prompts))

    def test_math_sanitizer_does_not_cut_formula_at_comma(self):
        raw = "考慮 F(s)=A(s,t)+B(s,t),其中此項仍需一致控制才能完成後續推導與證明閉環"
        result = sanitize_reaction(raw, max_chars=24, domain="riemann")
        self.assertLessEqual(len(result), 24)
        self.assertIn("A(s,t)+B(s,t)", result)
        self.assertTrue(result.endswith("。"))


class RiemannCoreTests(unittest.TestCase):
    def test_sixth_consecutive_specialist_review_forces_one_primary_round(self):
        with tempfile.TemporaryDirectory() as raw, mock.patch.dict(os.environ, {}, clear=True):
            root = Path(raw)
            workspace = root / "repo"
            workspace.mkdir()
            settings = settings_for(root)
            configure_workspace_profile(
                settings.paths.data_dir, workspace, domain="riemann", stage="frame",
                provider="anthropic", model="claude-opus-4-6", review_mode="all",
            )

            def dispatch(_provider, _prompt, _packet, _model, **_kwargs):
                return {"status": "no_finding", "finding": "", "usage": {}}

            core = ReviewCore(settings, dispatch=dispatch)
            outcomes = []
            for index in range(7):
                session = SessionRef(
                    "codex_cli", "cooldown", f"turn-{index}", repo_root=str(workspace)
                )
                evidence = EvidenceBundle(
                    assistant_claim="大篩法的尾項仍需要一致上界"
                )
                outcomes.append(core.review(
                    ReviewRequest(
                        1, "stop", "stop", session, evidence, "stale packet", str(index)
                    ),
                    persist_reaction=False,
                ).effective_lens)

        self.assertEqual(
            outcomes,
            ["selberg", "selberg", "selberg", "selberg", "selberg", "riemann", "selberg"],
        )

    def test_stop_routing_uses_current_claim_not_stale_packet(self):
        with tempfile.TemporaryDirectory() as raw, mock.patch.dict(os.environ, {}, clear=True):
            root = Path(raw)
            workspace = root / "repo"
            workspace.mkdir()
            settings = settings_for(root)
            configure_workspace_profile(
                settings.paths.data_dir, workspace, domain="riemann", stage="frame",
                provider="anthropic", model="claude-opus-4-6", review_mode="all",
            )

            def dispatch(_provider, _prompt, _packet, _model, **_kwargs):
                return {"status": "no_finding", "finding": "", "usage": {}}

            outcome = ReviewCore(settings, dispatch=dispatch).review(
                ReviewRequest(
                    1,
                    "stop",
                    "stop",
                    SessionRef("codex_cli", "fresh", "t", repo_root=str(workspace)),
                    EvidenceBundle(assistant_claim="我構造了一個反例來檢查最壞情況"),
                    "舊內容反覆提到大篩法與尾項上界",
                    "fresh",
                ),
                persist_reaction=False,
            )
        self.assertEqual(outcome.effective_lens, "erdos")

    def test_opus_checkpoint_gets_sixty_seconds_without_changing_general_default(self):
        with tempfile.TemporaryDirectory() as raw, mock.patch.dict(os.environ, {}, clear=True):
            root = Path(raw)
            workspace = root / "repo"
            workspace.mkdir()
            settings = settings_for(root)
            configure_workspace_profile(
                settings.paths.data_dir, workspace, domain="riemann", stage="frame",
                provider="anthropic", model="claude-opus-4-6", review_mode="all",
            )
            timeouts = []

            def dispatch(_provider, _prompt, _packet, _model, **kwargs):
                timeouts.append(kwargs["timeout_sec"])
                return {"status": "no_finding", "finding": "", "usage": {}}

            core = ReviewCore(settings, dispatch=dispatch)
            riemann = SessionRef("codex_cli", "r", repo_root=str(workspace))
            software = SessionRef("codex_cli", "s", repo_root=str(root / "other"))
            core.review(
                ReviewRequest(1, "checkpoint", "tool", riemann, EvidenceBundle(), "packet", "a"),
                persist_reaction=False,
                timeout_sec=15,
            )
            core.review(
                ReviewRequest(1, "checkpoint", "tool", software, EvidenceBundle(), "packet", "b"),
                persist_reaction=False,
                timeout_sec=15,
            )

        self.assertEqual(timeouts, [60, 15])

    def test_opus_stop_gets_180_seconds_and_timeout_is_visible_not_pending(self):
        with tempfile.TemporaryDirectory() as raw, mock.patch.dict(os.environ, {}, clear=True):
            root = Path(raw)
            workspace = root / "repo"
            workspace.mkdir()
            settings = settings_for(root)
            configure_workspace_profile(
                settings.paths.data_dir, workspace, domain="riemann", stage="frame",
                provider="anthropic", model="claude-opus-4-6", review_mode="all",
            )
            timeouts = []

            def dispatch(_provider, _prompt, _packet, _model, **kwargs):
                timeouts.append(kwargs["timeout_sec"])
                return {
                    "status": "error",
                    "finding": "",
                    "usage": {},
                    "error_kind": "timeout",
                }

            session = SessionRef("codex_cli", "s", "t", repo_root=str(workspace))
            core = ReviewCore(settings, dispatch=dispatch)
            outcome = core.review(
                ReviewRequest(1, "stop", "stop", session, EvidenceBundle(), "packet", "x"),
                persist_reaction=True,
            )

            entries = storage.read_reaction_entries(
                settings.paths.data_dir, session
            )
            pending = storage.latest_pending(settings.paths.data_dir, session)

        self.assertEqual(outcome.status, "error")
        self.assertEqual(timeouts, [180])
        self.assertEqual(entries[-1]["kind"], "review_status")
        self.assertIn("180 秒", entries[-1]["reaction"])
        self.assertIsNone(pending)

    def test_stop_uses_workspace_opus_profile_and_checkpoint_costs_no_call(self):
        with tempfile.TemporaryDirectory() as raw, mock.patch.dict(os.environ, {}, clear=True):
            root = Path(raw)
            workspace = root / "repo"
            workspace.mkdir()
            settings = settings_for(root)
            configure_workspace_profile(
                settings.paths.data_dir, workspace, domain="riemann", stage="explore",
                provider="anthropic", model="claude-opus-4-6", review_mode="stop_only",
            )
            calls = []

            def dispatch(provider, prompt, packet, model, **kwargs):
                calls.append((provider, prompt, model))
                return {"status": "no_finding", "finding": "", "usage": {}}

            core = ReviewCore(settings, dispatch=dispatch)
            session = SessionRef("codex_cli", "s", repo_root=str(workspace))
            checkpoint = ReviewRequest(1, "checkpoint", "tool", session, EvidenceBundle(), "packet", "a")
            stop = ReviewRequest(1, "stop", "stop", session, EvidenceBundle(), "packet", "b")
            checkpoint_outcome = core.review(checkpoint, persist_reaction=False)
            stop_outcome = core.review(stop, persist_reaction=False)
        self.assertEqual(checkpoint_outcome.status, "no_finding")
        self.assertEqual(len(calls), 1)
        self.assertEqual((calls[0][0], calls[0][2]), ("anthropic", "claude-opus-4-6"))
        self.assertIn("數學研究", calls[0][1])
        self.assertEqual(stop_outcome.effective_lens, "ramanujan")


if __name__ == "__main__":
    unittest.main()
