"""First-principles contracts for automatic taste routing."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import lens_router
from masters_nudge import checkpoints, prompting
from masters_nudge.contracts import ReviewRequest, SessionRef, ToolCompleted
from masters_nudge.core import ReviewCore
from masters_nudge.provider_contract import parse_reaction_result
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


HERE = Path(__file__).resolve().parents[2]


class TasteRouteTests(unittest.TestCase):
    def test_automatic_route_does_not_preselect_a_lens(self):
        with tempfile.TemporaryDirectory() as raw:
            route = lens_router.resolve_review_route(Path(raw), environ={})

        self.assertEqual(route.stage, "automatic")
        self.assertEqual(route.lens, "")
        self.assertEqual(route.source, "default")

    def test_manual_stage_forces_exactly_one_lens(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "config.json").write_text(
                '{"stage":"review"}\n', encoding="utf-8"
            )
            route = lens_router.resolve_review_route(root, environ={})

        self.assertEqual(route.lens, "linus")
        self.assertEqual(route.source, "config")

    def test_router_prompt_contains_no_full_persona_overlay(self):
        prompt = prompting.build_router_prompt()

        for persona in ("jeff", "linus", "fowler", "beck", "lamport", "carmack"):
            overlay = (HERE / "personas" / f"{persona}.txt").read_text(
                encoding="utf-8"
            ).strip()
            self.assertNotIn(overlay, prompt, persona)

    def test_generator_prompt_contains_only_selected_persona(self):
        route = lens_router.ReviewRoute("automatic", "linus", "automatic_router")
        prompt = prompting.build_system_prompt(
            prompt_file=HERE / "buddy-prompt.txt",
            persona_dir=HERE / "personas",
            route=route,
        )

        for persona in ("jeff", "linus", "fowler", "beck", "lamport", "carmack"):
            overlay = (HERE / "personas" / f"{persona}.txt").read_text(
                encoding="utf-8"
            ).strip()
            self.assertEqual(prompt.count(overlay), 1 if persona == "linus" else 0)

    def test_structured_finding_carries_the_selected_lens(self):
        parsed = parse_reaction_result(
            '{"status":"finding","effective_lens":"linus",'
            '"finding":"直接記錄 PK 是否由使用者提供；別用預設值猜來源，因為值相同不代表來源相同。"}'
        )

        self.assertEqual(parsed["status"], "finding")
        self.assertEqual(parsed["effective_lens"], "linus")

    def test_taste_finding_stays_within_52_characters(self):
        finding = "直接記錄 PK 是否由使用者提供；別用預設值猜來源，因為值相同不代表來源相同。"

        self.assertEqual(len(finding), 39)
        self.assertLessEqual(len(finding), prompting.MAX_REACTION_CHARS)

    def test_pure_test_instruction_is_rejected(self):
        parsed = parse_reaction_result(
            '{"status":"finding","effective_lens":"beck",'
            '"finding":"先執行新增的回歸測試再收尾。"}'
        )

        self.assertEqual(parsed["status"], "error")

    def test_no_finding_has_no_fake_lens(self):
        parsed = parse_reaction_result(
            '{"status":"no_finding","effective_lens":"none","finding":""}'
        )

        self.assertEqual(
            parsed,
            {"status": "no_finding", "effective_lens": "none", "finding": ""},
        )

    def test_automatic_review_routes_then_generates_with_one_persona(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            calls = []

            def dispatch(_provider, system_prompt, _review_input, _model, **kwargs):
                calls.append((system_prompt, Path(kwargs["schema_path"]).name))
                if len(calls) == 1:
                    return {
                        "status": "finding",
                        "effective_lens": "linus",
                        "finding": "是否直接記錄 PK 的來源",
                        "usage": {},
                    }
                return {
                    "status": "finding",
                    "effective_lens": "linus",
                    "finding": "直接記錄 PK 是否由使用者提供；別用預設值猜來源，因為值相同不代表來源相同。",
                    "usage": {},
                }

            settings = RuntimeSettings(
                "openai",
                "test-model",
                60,
                15,
                RuntimePaths(HERE, root, root / "error.log"),
            )
            outcome = ReviewCore(settings, dispatch=dispatch).review_once(
                ReviewRequest(
                    1,
                    "strategy",
                    "taste-review",
                    SessionRef("codex_cli", "automatic-two-stage"),
                    "PK value currently implies whether it was explicitly supplied.",
                    "automatic-two-stage",
                ),
                persist_reaction=False,
            )

        self.assertEqual(outcome.status, "finding")
        self.assertEqual([schema for _prompt, schema in calls], ["route-schema.json", "reaction-schema.json"])
        self.assertIn("# AUTOMATIC LENS ROUTER", calls[0][0])
        self.assertIn("Linus Torvalds", calls[1][0])
        self.assertNotIn("Kent Beck", calls[1][0])

    def test_manual_override_skips_router_call(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "config.json").write_text('{"stage":"review"}\n', encoding="utf-8")
            calls = []

            def dispatch(_provider, system_prompt, _review_input, _model, **kwargs):
                calls.append((system_prompt, Path(kwargs["schema_path"]).name))
                return {
                    "status": "no_finding",
                    "effective_lens": "none",
                    "finding": "",
                    "usage": {},
                }

            settings = RuntimeSettings(
                "openai", "test-model", 60, 15,
                RuntimePaths(HERE, root, root / "error.log"),
            )
            ReviewCore(settings, dispatch=dispatch).review_once(
                ReviewRequest(
                    1, "strategy", "taste-review",
                    SessionRef("codex_cli", "manual-one-stage"),
                    "packet", "manual-one-stage",
                ),
                persist_reaction=False,
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], "reaction-schema.json")
        self.assertIn("Linus Torvalds", calls[0][0])

    def test_core_rejects_invalid_finding_even_when_dispatch_bypasses_parser(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "config.json").write_text('{"stage":"review"}\n', encoding="utf-8")
            settings = RuntimeSettings(
                "openai", "test-model", 60, 15,
                RuntimePaths(HERE, root, root / "error.log"),
            )
            outcome = ReviewCore(
                settings,
                dispatch=lambda *_args, **_kwargs: {
                    "status": "finding",
                    "effective_lens": "linus",
                    "finding": "先跑完整測試再收尾。",
                    "usage": {},
                },
            ).review_once(
                ReviewRequest(
                    1, "strategy", "taste-review",
                    SessionRef("codex_cli", "invalid-direct-result"),
                    "packet", "invalid-direct-result",
                ),
                persist_reaction=False,
            )

        self.assertEqual(outcome.status, "error")
        self.assertEqual(outcome.finding, "")

    def test_automatic_review_sums_router_and_generator_usage(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            calls = 0

            def dispatch(*_args, **_kwargs):
                nonlocal calls
                calls += 1
                if calls == 1:
                    return {
                        "status": "finding",
                        "effective_lens": "linus",
                        "finding": "輸入來源的表示方式",
                        "usage": {"input_tokens": 10, "output_tokens": 2},
                    }
                return {
                    "status": "finding",
                    "effective_lens": "linus",
                    "finding": "直接記錄輸入來源；別用值猜測，因為相同值不代表相同來源。",
                    "usage": {"input_tokens": 20, "output_tokens": 4},
                }

            settings = RuntimeSettings(
                "openai", "test-model", 60, 15,
                RuntimePaths(HERE, root, root / "error.log"),
            )
            outcome = ReviewCore(settings, dispatch=dispatch).review_once(
                ReviewRequest(
                    1, "strategy", "taste-review",
                    SessionRef("codex_cli", "summed-usage"),
                    "packet", "summed-usage",
                ),
                persist_reaction=False,
            )

        self.assertEqual(outcome.usage, {"input_tokens": 30, "output_tokens": 6})

    def test_router_no_finding_usage_is_not_counted_twice(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            settings = RuntimeSettings(
                "openai", "test-model", 60, 15,
                RuntimePaths(HERE, root, root / "error.log"),
            )
            outcome = ReviewCore(
                settings,
                dispatch=lambda *_args, **_kwargs: {
                    "status": "no_finding",
                    "effective_lens": "none",
                    "finding": "",
                    "usage": {"input_tokens": 11, "output_tokens": 1},
                },
            ).review_once(
                ReviewRequest(
                    1, "strategy", "taste-review",
                    SessionRef("codex_cli", "router-no-finding-usage"),
                    "packet", "router-no-finding-usage",
                ),
                persist_reaction=False,
            )

        self.assertEqual(outcome.usage, {"input_tokens": 11, "output_tokens": 1})


class TasteTimingTests(unittest.TestCase):
    def test_native_file_change_is_a_semantic_change(self):
        event = ToolCompleted(
            SessionRef("codex_cli", "native-file-change"),
            "file_change",
            tool_input={"changes": [{"path": "sphinx/ext/napoleon/docstring.py"}]},
            tool_output={"status": "completed"},
            mutating=True,
        )

        self.assertEqual(checkpoints.evidence_category(event), "change")
    def test_first_semantic_change_opens_the_taste_window(self):
        review = checkpoints.classify_strategy(
            {
                "last_strategy_event_seq": 0,
                "midturn_review_attempts": 0,
                "recent": [
                    {"event_seq": 1, "evidence_category": "change", "failed": False}
                ],
            }
        )

        self.assertEqual(review["trigger"], "first-change")

    def test_successful_validation_does_not_open_a_review_window(self):
        review = checkpoints.classify_strategy(
            {
                "last_strategy_event_seq": 0,
                "midturn_review_attempts": 1,
                "recent": [
                    {"event_seq": 1, "evidence_category": "change", "failed": False},
                    {
                        "event_seq": 2,
                        "evidence_category": "verification",
                        "failed": False,
                    },
                ],
            }
        )

        self.assertIsNone(review)

    def test_goal_complete_does_not_create_a_late_nudge(self):
        review = checkpoints.classify_strategy(
            {
                "last_strategy_event_seq": 0,
                "midturn_review_attempts": 1,
                "recent": [
                    {
                        "event_seq": 1,
                        "goal_transition": "complete",
                        "evidence_category": "",
                    }
                ],
            }
        )

        self.assertIsNone(review)


if __name__ == "__main__":
    unittest.main()
