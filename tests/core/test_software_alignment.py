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


class SoftwareNudgeContractTests(unittest.TestCase):
    def test_software_prompt_allows_a_grounded_alternative_not_only_a_question(self):
        prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("限制、反例、替代假設或方向", prompt)
        self.assertIn("可以是陳述或問題", prompt)
        self.assertIn("推論", prompt)
        self.assertNotIn("finding 只放一個開放問句", prompt)
        self.assertNotIn("以「？」結尾", prompt)
        self.assertNotIn("敏感資訊或安全邊界", prompt)
        self.assertNotIn("使用者授權", prompt)

    def test_prompt_entry_has_no_legacy_queue_wrapper(self):
        self.assertFalse(hasattr(inject, "build_context_text"))
        self.assertFalse(hasattr(storage, "latest_pending"))

    def test_readmes_describe_one_short_grounded_second_opinion(self):
        english = (HERE / "README.md").read_text(encoding="utf-8")
        chinese = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")

        self.assertIn("one short, evidence-grounded second opinion", english)
        self.assertIn("Independent second opinion:", english)
        self.assertNotIn("one short open question", english)
        self.assertIn("一則簡短、以證據為錨點的獨立第二意見", chinese)
        self.assertIn("獨立第二意見：", chinese)
        self.assertNotIn("開放問句", chinese)

    def test_readmes_require_later_host_evidence_before_confirming_injection(self):
        english = (HERE / "README.md").read_text(encoding="utf-8")
        chinese = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")

        self.assertIn("only a later Claude or Codex host event", english)
        self.assertIn("後續 Claude 或 Codex host event", chinese)

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
    def test_review_provider_receives_current_packet_and_recent_injected_nudges(self):
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
            storage.mark_emitted(root, session, old["ts"])
            storage.observe_injected_response(
                root,
                session,
                observation_kind="tool",
                observation={"tool": "exec_command"},
            )
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

        self.assertIn("CURRENT SOFTWARE STATE", seen["input"])
        self.assertIn("[recent injected nudges — deduplication only]", seen["input"])
        self.assertIn("舊問題不應進入下一次 Provider 輸入？", seen["input"])
        self.assertIn("只用來避免重複", seen["input"])

    def test_checkpoint_packet_does_not_accept_previous_findings(self):
        packet = source_context.build_checkpoint_packet(
            task_anchor="只修登入失敗",
            event_context="failure: authentication timeout",
            change_evidence="auth_service.py changed",
            failure_history="result: 1 failed",
        )

        self.assertNotIn("recent blind spots", packet)
        self.assertNotIn("你最近說過", packet)
        self.assertNotIn("正在調整 auth_service.py", packet)

    def test_evidence_categories_filter_navigation_and_keep_decisions(self):
        from masters_nudge.contracts import ToolCompleted

        session = SessionRef("codex_cli", "evidence")
        cases = [
            (
                ToolCompleted(
                    session,
                    "exec_command",
                    {"cmd": "rg -n foo src"},
                    "src/a.py:1",
                ),
                "",
            ),
            (
                ToolCompleted(
                    session,
                    "exec_command",
                    {"cmd": "rg -n EventLedger tests/test_ledger.py"},
                    "tests/test_ledger.py:8:class EventLedgerTests",
                ),
                "",
            ),
            (
                ToolCompleted(
                    session,
                    "exec_command",
                    {"cmd": "Get-Content tests/test_ledger.py"},
                    "class EventLedgerTests",
                ),
                "",
            ),
            (
                ToolCompleted(
                    session,
                    "apply_patch",
                    "*** Begin Patch",
                    "Done!",
                    mutating=True,
                ),
                "change",
            ),
            (
                ToolCompleted(
                    session,
                    "exec_command",
                    {"cmd": "pytest -q"},
                    "8 passed",
                ),
                "verification",
            ),
            (
                ToolCompleted(
                    session,
                    "exec_command",
                    {"cmd": "pytest -q"},
                    "1 failed",
                    failed=True,
                    failure_known=True,
                ),
                "failure",
            ),
        ]

        for event, expected in cases:
            with self.subTest(tool=event.tool_name, expected=expected):
                self.assertEqual(checkpoints.evidence_category(event), expected)

    def test_provider_evidence_keeps_results_without_tool_identity_or_commands(self):
        from masters_nudge.contracts import ToolCompleted

        session = SessionRef("codex_cli", "evidence")
        change = checkpoints.render_evidence_record(
            ToolCompleted(
                session,
                "apply_patch",
                {"command": "*** Begin Patch\n+return preserved\n*** End Patch"},
                "Done!",
                mutating=True,
            )
        )
        verification = checkpoints.render_evidence_record(
            ToolCompleted(
                session,
                "exec_command",
                {"cmd": "python -m pytest tests/test_contract.py"},
                "12 passed, 1 failed: expected legacy_code",
                failed=True,
                failure_known=True,
            )
        )
        shell_change = checkpoints.render_evidence_record(
            ToolCompleted(
                session,
                "exec_command",
                {"cmd": "edit x.py --replace secret"},
                "updated x.py",
                mutating=True,
            )
        )

        self.assertIn("return preserved", change)
        self.assertIn("12 passed, 1 failed", verification)
        self.assertIn("updated x.py", shell_change)
        for packet in (change, verification, shell_change):
            self.assertNotIn("apply_patch", packet)
            self.assertNotIn("exec_command", packet)
            self.assertNotIn("python -m pytest", packet)
            self.assertNotIn("edit x.py", packet)
            self.assertNotIn("[tool ", packet)


class SoftwareEvidenceRoutingTests(unittest.TestCase):
    def test_specialist_route_does_not_rotate_away_from_the_best_evidence_lens(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona_config.save_stage(root, "build")
            routes = [
                lens_router.resolve_review_route(
                    root,
                    "retry duplicate delivery",
                    checkpoint=True,
                )
                for _ in range(3)
            ]

        self.assertEqual(["lamport", "lamport", "lamport"], [
            route.effective_lens for route in routes
        ])

    def test_evidence_still_selects_a_specialist(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona_config.save_stage(root, "build")
            route = lens_router.resolve_review_route(
                root,
                "retry duplicate delivery",
                checkpoint=True,
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

    def test_one_edit_validation_cycle_does_not_trigger_strategy_review(self):
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

        self.assertIsNone(
            checkpoints.classify_strategy(progress, changed_line_count=12)
        )

    def test_repeated_command_still_triggers_without_repeating_goal(self):
        progress = {
            "event_seq": 3,
            "last_strategy_event_seq": 0,
            "changed_lines_at_strategy": 0,
            "goal_objective": "只修登入失敗",
            "recent": [
                {
                    "event_seq": index,
                    "tool": "exec_command",
                    "command_family": "python -m unittest",
                    "meaningful": True,
                    "failed": False,
                    "mutating": True,
                }
                for index in range(1, 4)
            ],
        }

        review = checkpoints.classify_strategy(progress, changed_line_count=12)

        self.assertEqual("repeated-command-family", review["trigger"])
        self.assertNotIn("goal objective:", review["context"])

    def test_storage_does_not_select_or_supersede_queued_findings(self):
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

            self.assertFalse(hasattr(storage, "latest_pending"))
            self.assertNotIn(
                entry["ts"], storage.load_delivery_state(root, session)["receipts"]
            )

    def test_marking_one_delivery_does_not_supersede_an_older_finding(self):
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

            newer = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="gpt-test",
                reaction="較新的問題。",
                route_metadata={"effective_lens": "fowler", "domain": "software"},
            )
            storage.mark_emitted(root, session, newer["ts"])
            receipts = storage.load_delivery_state(root, session)["receipts"]

        self.assertNotIn(entry["ts"], receipts)
        self.assertEqual("emitted", receipts[newer["ts"]]["status"])

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

            storage.mark_emitted(
                root,
                session,
                outcome.reaction_ts,
                delivered_via="PostToolUse",
            )
            emitted = storage.load_delivery_state(root, session)["receipts"][
                outcome.reaction_ts
            ]
            self.assertEqual("emitted", emitted["status"])
            storage.observe_injected_response(
                root,
                session,
                observation_kind="tool",
                observation={"tool": "exec_command"},
            )
            receipt = storage.load_delivery_state(root, session)["receipts"][outcome.reaction_ts]

        self.assertEqual("injected", receipt["status"])
        self.assertEqual("PostToolUse", receipt["delivered_via"])


if __name__ == "__main__":
    unittest.main()
