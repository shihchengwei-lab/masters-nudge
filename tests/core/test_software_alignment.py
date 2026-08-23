import json
import tempfile
import unittest
from pathlib import Path

import claude_prompt as inject
import lens_router
import persona_config
import source_context
from masters_nudge import checkpoints, storage
from masters_nudge.contracts import ReviewRequest, SessionRef
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


HERE = Path(__file__).resolve().parents[2]


def settings_for(root: Path) -> RuntimeSettings:
    return RuntimeSettings(
        provider="openai",
        model="gpt-test",
        timeout_sec=30,
        checkpoint_timeout_sec=30,
        paths=RuntimePaths(
            runtime_dir=HERE,
            data_dir=root,
            error_log=root / "error.log",
        ),
        ollama_url="http://127.0.0.1:11434",
        configuration_source="test",
        configuration_error="",
    )


class SoftwareQuestionContractTests(unittest.TestCase):
    def test_software_prompt_requires_one_open_question_without_safety_guardrails(self):
        prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("一個開放問句", prompt)
        self.assertIn("以「？」結尾", prompt)
        self.assertNotIn("可以用問句，也可以用陳述句", prompt)
        self.assertNotIn("敏感資訊或安全邊界", prompt)
        self.assertNotIn("使用者授權", prompt)

    def test_software_injection_is_the_unlabeled_question_only(self):
        question = "目前證據區分的是修正成功，還是測試剛好沒有覆蓋失敗？"

        context = inject.build_context_text(
            {
                "ts": "2026-08-22T12:00:00",
                "kind": "review",
                "domain": "software",
                "reason": "strategy-review",
                "effective_lens": "beck",
            },
            question,
        )

        self.assertEqual(question, context)

    def test_readmes_describe_questions_as_prompted_not_runtime_enforced(self):
        english = (HERE / "README.md").read_text(encoding="utf-8")
        chinese = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")

        self.assertIn("The reviewer prompt asks for one short open question", english)
        self.assertNotIn("The output is either one short open question", english)
        self.assertIn("Reviewer prompt 會要求一個簡短的開放問句", chinese)
        self.assertNotIn("輸出要嘛是一句開放問句", chinese)

    def test_readmes_limit_response_observation_to_codex(self):
        english = (HERE / "README.md").read_text(encoding="utf-8")
        chinese = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")

        self.assertIn("On Codex, a receipt may also record", english)
        self.assertIn("在 Codex 上，receipt 也可能記錄", chinese)

    def test_readmes_do_not_duplicate_the_manifest_version_or_a_cost_experiment(self):
        english = (HERE / "README.md").read_text(encoding="utf-8")
        chinese = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")

        self.assertNotIn("Current package version:", english)
        self.assertNotIn("目前套件版本：", chinese)
        self.assertIn("there is no active cost experiment", english)
        self.assertIn("目前沒有正式成本實驗", chinese)

    def test_docs_do_not_reference_removed_compatibility_or_visibility_sections(self):
        architecture = (HERE / "docs/architecture.md").read_text(
            encoding="utf-8"
        )
        prompt_entry = (HERE / "claude_prompt.py").read_text(encoding="utf-8")

        self.assertNotIn("compatibility views", architecture)
        self.assertNotIn("Two visibility channels", prompt_entry)


class SoftwareColdStartTests(unittest.TestCase):
    def test_review_provider_receives_only_the_current_packet(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "cold", cwd=str(root), repo_root=str(root))
            old = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="gpt-test",
                reaction="舊問題不應進入下一次 Provider 輸入？",
                route_metadata={"effective_lens": "beck", "domain": "software"},
            )
            storage.mark_delivered(root, session, old["ts"])
            seen = {}

            def dispatch(_provider, _system_prompt, review_input, _model, **_kwargs):
                seen["input"] = review_input
                return {
                    "status": "finding",
                    "finding": "目前證據排除了哪一個仍可能成立的解釋？",
                    "usage": {},
                }

            request = ReviewRequest(
                schema_version=1,
                kind="strategy",
                reason="strategy-review",
                session=session,
                source_packet="CURRENT SOFTWARE STATE",
                source_fingerprint="state-current",
            )
            ReviewCore(settings_for(root), dispatch=dispatch).review(
                request, persist_reaction=False
            )

        self.assertEqual("CURRENT SOFTWARE STATE", seen["input"])
        self.assertNotIn("舊問題", seen["input"])
        self.assertNotIn("你最近說過", seen["input"])

    def test_checkpoint_packet_does_not_accept_previous_findings(self):
        packet = source_context.build_checkpoint_packet(
            task_anchor="只修登入失敗",
            event_context="failure: authentication timeout",
            assistant_context="正在調整 auth_service.py",
            tool_evidence="result: 1 failed",
        )

        self.assertNotIn("recent blind spots", packet)
        self.assertNotIn("你最近說過", packet)


class SoftwareDeliveryAwareRoutingTests(unittest.TestCase):
    def test_recent_injected_personas_are_excluded_in_evidence_order(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona_config.save_stage(root, "build")
            route = lens_router.resolve_review_route(
                root,
                "retry duplicate delivery; benchmark latency 20 ms",
                checkpoint=True,
                injected_personas=("lamport",),
            )

        self.assertEqual("carmack", route.effective_lens)
        self.assertIn("lamport", route.suppression_reason)

    def test_timeout_or_expired_persona_does_not_enter_cooldown(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona_config.save_stage(root, "build")
            route = lens_router.resolve_review_route(
                root,
                "retry duplicate delivery",
                checkpoint=True,
                injected_personas=(),
            )

        self.assertEqual("lamport", route.effective_lens)


class SoftwareSemanticStateTests(unittest.TestCase):
    def test_tool_count_alone_does_not_trigger_a_strategy_review(self):
        progress = {
            "event_seq": 8,
            "last_strategy_event_seq": 0,
            "changed_lines_at_strategy": 0,
            "recent": [
                {
                    "event_seq": index,
                    "tool": f"verify_step_{index}",
                    "command_family": f"verify_step_{index}",
                    "meaningful": True,
                    "failed": False,
                    "mutating": False,
                }
                for index in range(1, 9)
            ],
        }

        self.assertIsNone(
            checkpoints.classify_strategy(progress, changed_line_count=0)
        )

    def test_edit_followed_by_validation_is_a_semantic_strategy_change(self):
        progress = {
            "event_seq": 2,
            "last_strategy_event_seq": 0,
            "changed_lines_at_strategy": 0,
            "recent": [
                {
                    "event_seq": 1,
                    "tool": "apply_patch",
                    "command_family": "apply_patch",
                    "meaningful": True,
                    "failed": False,
                    "mutating": True,
                },
                {
                    "event_seq": 2,
                    "tool": "exec_command",
                    "command_family": "python -m unittest",
                    "meaningful": True,
                    "failed": False,
                    "mutating": True,
                },
            ],
        }

        review = checkpoints.classify_strategy(progress, changed_line_count=12)

        self.assertEqual("evidence-cycle-change", review["trigger"])

    def test_local_question_is_superseded_by_new_semantic_state(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "freshness")
            entry = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="gpt-test",
                reaction="目前失敗仍支持原本的修正方向嗎？",
                route_metadata={"effective_lens": "beck", "domain": "software"},
                source_fingerprint="software-old",
                finding_scope="local",
            )

            pending = storage.latest_pending(
                root,
                session,
                current_event_seq=4,
                current_source_fingerprint="software-new",
            )

            receipt = storage.load_delivery_state(root, session)["receipts"][entry["ts"]]
        self.assertIsNone(pending)
        self.assertEqual("superseded", receipt["status"])

    def test_trajectory_question_survives_local_state_change(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "trajectory")
            entry = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="gpt-test",
                reaction="目前路徑仍在縮短原始驗收條件嗎？",
                route_metadata={"effective_lens": "fowler", "domain": "software"},
                source_fingerprint="trajectory-old",
                finding_scope="trajectory",
            )

            pending = storage.latest_pending(
                root,
                session,
                current_event_seq=4,
                current_source_fingerprint="local-new",
            )

        self.assertEqual(entry["ts"], pending["ts"])

    def test_review_scope_distinguishes_local_and_trajectory_questions(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "scope", cwd=str(root), repo_root=str(root))
            core = ReviewCore(
                settings_for(root),
                dispatch=lambda *_args, **_kwargs: {
                    "status": "finding",
                    "finding": "目前證據還留下哪個未區分的解釋？",
                    "usage": {},
                },
            )
            for kind in ("checkpoint", "strategy"):
                core.review(
                    ReviewRequest(
                        schema_version=1,
                        kind=kind,
                        reason="test-fail" if kind == "checkpoint" else "strategy-review",
                        session=session,
                        source_packet=kind,
                        source_fingerprint=f"state-{kind}",
                        routing_evidence=kind,
                    ),
                    persist_reaction=True,
                )

            entries = storage.read_reaction_entries(root, session)

        self.assertEqual(["local", "trajectory"], [entry["finding_scope"] for entry in entries])


class SoftwareTelemetrySeparationTests(unittest.TestCase):
    def test_route_provider_and_delivery_are_observable_separately(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "telemetry", cwd=str(root), repo_root=str(root))
            core = ReviewCore(
                settings_for(root),
                dispatch=lambda *_args, **_kwargs: {
                    "status": "finding",
                    "finding": "目前數據證明的是效能改善，還是量測順序差異？",
                    "usage": {},
                },
            )
            outcome = core.review(
                ReviewRequest(
                    schema_version=1,
                    kind="checkpoint",
                    reason="test-fail",
                    session=session,
                    source_packet="current packet",
                    source_fingerprint="current-state",
                    routing_evidence="benchmark latency 20 ms",
                ),
                persist_reaction=True,
            )
            telemetry = json.loads(
                (root / "review-telemetry.jsonl").read_text(encoding="utf-8").splitlines()[-1]
            )
            self.assertEqual("carmack", telemetry["persona"])
            self.assertEqual("finding", telemetry["status"])
            self.assertNotIn(
                outcome.reaction_ts,
                storage.load_delivery_state(root, session)["receipts"],
            )

            storage.mark_delivered(
                root,
                session,
                outcome.reaction_ts,
                delivered_via="PostToolUse",
            )
            receipt = storage.load_delivery_state(root, session)["receipts"][outcome.reaction_ts]

        self.assertEqual("injected", receipt["status"])
        self.assertEqual("PostToolUse", receipt["delivered_via"])


if __name__ == "__main__":
    unittest.main()
