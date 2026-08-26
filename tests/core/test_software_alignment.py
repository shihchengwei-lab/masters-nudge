import json
import tempfile
import unittest
from pathlib import Path

import claude_prompt as inject
import lens_router
import persona_config
import source_context
from masters_nudge import checkpoints, storage
from masters_nudge.prompting import build_review_input
from masters_nudge.contracts import ReviewRequest, SessionRef
from masters_nudge.core import STOP_PROMPT, ReviewCore
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
    def test_base_prompt_defines_an_independent_opinion_without_reasoning_scaffolds(self):
        prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        for heading in ("# ROLE", "# EVIDENCE", "# NUDGE", "# OUTPUT"):
            self.assertIn(heading, prompt)
        self.assertNotIn("# FINDING GATE", prompt)
        for scaffold in (
            "ALTERNATIVE",
            "LEVERAGED",
            "GROUNDED",
            "DISCRIMINATING",
            "two named competing hypotheses",
            "alternative causal assumption",
        ):
            self.assertNotIn(scaffold, prompt)
        self.assertIn("Missing evidence means unknown", prompt)
        self.assertIn("Do not invent requirements", prompt)
        self.assertIn("independent second opinion", prompt)

    def test_stop_prompt_reports_timing_without_prescribing_reasoning(self):
        self.assertIn("about to close the task", STOP_PROMPT)
        self.assertNotIn("alternative causal assumption", STOP_PROMPT)
        self.assertNotIn("distinguishable now", STOP_PROMPT)
        self.assertNotIn("identify", STOP_PROMPT.lower())

    def test_prompt_keeps_one_grounded_question(self):
        prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("ask one concrete question", prompt)
        self.assertIn("at most 52", prompt)

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

    def test_readmes_limit_receipts_to_delivery_order(self):
        english = (HERE / "README.md").read_text(encoding="utf-8")
        chinese = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")

        self.assertIn(
            "Injected receipts and later response observations establish delivery order only.",
            english,
        )
        self.assertIn(
            "Injected receipts 與後續 response observations 只能證明投遞順序。",
            chinese,
        )

    def test_readmes_do_not_duplicate_the_manifest_version(self):
        english = (HERE / "README.md").read_text(encoding="utf-8")
        chinese = (HERE / "README.zh-TW.md").read_text(encoding="utf-8")

        self.assertNotIn("Current package version:", english)
        self.assertNotIn("目前套件版本：", chinese)

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
                route_metadata={"effective_lens": "beck"},
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
            ReviewCore(settings_for(root), dispatch=dispatch).review_once(
                request, persist_reaction=False
            )

        self.assertIn("CURRENT SOFTWARE STATE", seen["input"])
        self.assertIn("[recent injected nudges — deduplication only]", seen["input"])
        self.assertIn("舊問題不應進入下一次 Provider 輸入？", seen["input"])
        self.assertIn("只用來避免重複", seen["input"])

    def test_checkpoint_packet_does_not_accept_previous_findings(self):
        packet = source_context.build_checkpoint_packet(
            task_anchor="只修登入失敗",
            evidence_records=[
                {"seq": 1, "category": "change", "content": "auth_service.py changed"},
                {"seq": 2, "category": "failure", "content": "result: 1 failed"},
            ],
        )

        self.assertNotIn("recent blind spots", packet)
        self.assertNotIn("你最近說過", packet)
        self.assertNotIn("正在調整 auth_service.py", packet)

    def test_packet_contains_only_contract_and_current_result(self):
        packet = source_context.build_checkpoint_packet(
            task_anchor="修正設定解析並保留既有相容性",
            task_sources={"ISSUE.md": "原始輸入不得崩潰"},
            evidence_records=[
                {"seq": 1, "category": "change", "content": "change:\nparser updated"},
                {"seq": 2, "category": "failure", "scope": "config", "content": "failure:\n1 failed"},
                {"seq": 3, "category": "verification", "scope": "config", "content": "verification:\n20 passed"},
            ],
        )

        self.assertIn("[contract]", packet)
        self.assertIn("task:\n修正設定解析並保留既有相容性", packet)
        self.assertIn("source: ISSUE.md", packet)
        self.assertIn("原始輸入不得崩潰", packet)
        self.assertIn("[current result]", packet)
        self.assertIn("parser updated", packet)
        self.assertIn("1 failed", packet)
        self.assertIn("20 passed", packet)
        self.assertNotIn("[result #", packet)
        self.assertNotIn("scope:", packet)
        for obsolete in (
            "[decision frame]",
            "[supporting evidence]",
            "current_approach:",
            "latest_outcome:",
            "unresolved_contradiction:",
            "recent_approach_outcome_pairs:",
            "contract_excerpt:",
            "discriminating_results:",
        ):
            self.assertNotIn(obsolete, packet)

    def test_stop_packet_keeps_assistant_output_in_current_result(self):
        packet = source_context.build_stop_packet(
            task_anchor="修正設定解析",
            last_assistant_message="已完成並通過全部測試",
            evidence_records=[
                {"seq": 1, "category": "verification", "content": "20 passed"}
            ],
        )

        contract = packet.split("[end contract]", 1)[0]
        current = packet.split("[current result]", 1)[1]
        self.assertNotIn("已完成並通過全部測試", contract)
        self.assertIn("assistant_output:\n已完成並通過全部測試", current)
        self.assertNotIn("completion_claim_context:", packet)

    def test_storage_does_not_persist_generic_inspection_records(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "retention")
            storage.start_turn(root, session, "修正仍在失敗的驗證")
            storage.record_turn_evidence(
                root,
                session,
                category="failure",
                scope="validation-suite",
                record="failure:\nORIGINAL_OPEN_FAILURE",
            )
            state = storage.record_turn_evidence(
                root,
                session,
                category="inspection",
                record="inspection:\nsource excerpt",
            )

        failures = [
            record
            for record in state["evidence_records"]
            if record["category"] == "failure"
        ]
        self.assertEqual(1, len(failures))
        self.assertEqual(1, len(state["evidence_records"]))
        self.assertIn("ORIGINAL_OPEN_FAILURE", failures[0]["content"])

    def test_packet_has_one_total_budget_and_keeps_contract_and_current_result(self):
        records = []
        seq = 0
        for category, count in (
            ("change", 4),
            ("verification", 4),
            ("failure", 4),
        ):
            for _index in range(count):
                seq += 1
                records.append(
                    {
                        "seq": seq,
                        "category": category,
                        "scope": f"scope-{seq}",
                        "content": f"{category}:\n" + (category[0] * 5000),
                    }
                )

        packet = source_context.build_stop_packet(
            task_anchor="TASK_CONTRACT " + ("t" * 4000),
            last_assistant_message="COMPLETION_CLAIM " + ("c" * 4000),
            task_sources={"SPEC.md": "s" * 10000},
            evidence_records=records,
        )

        self.assertLessEqual(len(packet), source_context.PACKET_MAX_CHARS)
        self.assertIn("TASK_CONTRACT", packet)
        self.assertIn("COMPLETION_CLAIM", packet)
        self.assertIn("[contract]", packet)
        self.assertIn("[current result]", packet)

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

    def test_validation_runtime_exceptions_are_failures_not_verifications(self):
        from masters_nudge.contracts import ToolCompleted

        session = SessionRef("codex_cli", "runtime-failure")
        cases = (
            "Traceback (most recent call last):\nAssertionError: (2, 2, 3, [], [])",
            "ModuleNotFoundError: No module named 'docutils'",
            {"content": "ModuleNotFoundError: No module named 'docutils'"},
        )
        for output in cases:
            with self.subTest(output=output):
                event = ToolCompleted(
                    session,
                    "exec_command",
                    {"cmd": "python verify_behavior.py"},
                    output,
                )
                self.assertEqual("failure", checkpoints.evidence_category(event))

    def test_source_read_with_exception_text_is_not_a_runtime_failure(self):
        from masters_nudge.contracts import ToolCompleted

        event = ToolCompleted(
            SessionRef("codex_cli", "source-text"),
            "exec_command",
            {"cmd": "Get-Content src/errors.py"},
            "class ExpectedAssertionError(Exception):\n    pass",
        )

        self.assertEqual("", checkpoints.evidence_category(event))

    def test_provider_evidence_keeps_results_without_tool_identity_or_commands(self):
        from masters_nudge.contracts import ToolCompleted

        session = SessionRef("codex_cli", "evidence")
        change = checkpoints.render_evidence_record(
            ToolCompleted(
                session,
                "apply_patch",
                {
                    "command": (
                        "*** Begin Patch\n"
                        "*** Update File: src/contract.py\n"
                        "+return preserved\n"
                        "*** End Patch"
                    )
                },
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

        self.assertIn("changed_paths:\n- src/contract.py", change)
        self.assertIn("semantic_change:", change)
        self.assertIn("+return preserved", change)
        self.assertIn("12 passed, 1 failed", verification)
        self.assertNotIn("failure:\n", verification)
        self.assertNotIn("verification:\n", verification)
        self.assertIn("updated x.py", shell_change)
        for packet in (change, verification, shell_change):
            self.assertNotIn("apply_patch", packet)
            self.assertNotIn("exec_command", packet)
            self.assertNotIn("python -m pytest", packet)
            self.assertNotIn("edit x.py", packet)
            self.assertNotIn("[tool ", packet)

    def test_unreferenced_content_read_is_not_recorded_as_evidence(self):
        from masters_nudge.evidence import observe_tool_event
        from masters_nudge.contracts import ToolCompleted

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            session = SessionRef("codex_cli", "unreferenced-read")
            storage.start_turn(root, session, "修正公開行為")
            observed = observe_tool_event(
                root,
                ToolCompleted(
                    session,
                    "read_file",
                    {"file_path": "C:/repo/api.py"},
                    {"content": "def public_api(value): ..."},
                ),
            )
            turn = storage.load_turn_state(root, session)
            progress = storage.load_progress_state(root, session)

        self.assertEqual([], turn["evidence_records"])
        self.assertEqual({}, turn["task_sources"])
        self.assertEqual("", progress["recent"][-1]["evidence_category"])
        self.assertIsNone(observed.checkpoint)

    def test_packet_omits_generic_source_inspections(self):
        packet = source_context.build_checkpoint_packet(
            task_anchor="Preserve the public contract.",
            evidence_records=[
                {
                    "seq": 4,
                    "category": "inspection",
                    "content": "inspection:\nassert collect(C) == [C, A, B]",
                }
            ],
        )

        self.assertIn("[contract]", packet)
        self.assertIn("[current result]", packet)
        self.assertNotIn("approach_relevant_source:", packet)
        self.assertNotIn("assert collect(C) == [C, A, B]", packet)

    def test_packet_does_not_promote_large_inspection_output_to_current_result(self):
        content = "inspection:\n" + "x" * (source_context.TASK_SOURCE_MAX_CHARS - 20)
        packet = source_context.build_checkpoint_packet(
            task_anchor="修正公開行為",
            evidence_records=[
                {"seq": 1, "category": "inspection", "content": content}
            ],
        )

        self.assertNotIn("inspection:", packet)
        self.assertLess(len(packet), len(content))

    def test_current_result_uses_semantic_results_without_path_ranking(self):
        records = [
            {
                "seq": 1,
                "category": "inspection",
                "content": "source:\n- src/parser.py\ninspection:\nRELEVANT_BRANCH",
            },
            {
                "seq": 2,
                "category": "inspection",
                "content": "source:\n- /var/cache/pip/state.json\ninspection:\nIRRELEVANT_CACHE",
            },
            {
                "seq": 3,
                "category": "change",
                "content": "changed_paths:\n- src/parser.py\nsemantic_change:\ntry alternate parser",
            },
            {
                "seq": 4,
                "category": "failure",
                "scope": "validation:tests/test_parser.py",
                "content": "AssertionError: alternate parser still rejects empty input",
            },
        ]

        packet = source_context.build_checkpoint_packet(
            task_anchor="修正公開行為",
            evidence_records=records,
        )

        self.assertNotIn("RELEVANT_BRANCH", packet)
        self.assertNotIn("IRRELEVANT_CACHE", packet)
        self.assertIn("try alternate parser", packet)
        self.assertIn("alternate parser still rejects empty input", packet)
        self.assertNotIn("evidence #3 -> evidence #4", packet)

    def test_large_task_source_uses_plain_head_and_tail_without_heading_priority(self):
        issue = (
            "SOURCE_HEAD\n"
            + ("implementation detail\n" * 500)
            + "SOURCE_TAIL\n"
        )

        packet = source_context.build_checkpoint_packet(
            task_anchor="Fix the parser.",
            task_sources={"ISSUE.md": issue},
        )

        self.assertIn("SOURCE_HEAD", packet)
        self.assertIn("SOURCE_TAIL", packet)
        self.assertIn(source_context.TRUNCATION_MARKER, packet)
        self.assertLessEqual(len(packet), source_context.PACKET_MAX_CHARS)


class SoftwareEvidenceRoutingTests(unittest.TestCase):
    def test_same_packet_keeps_one_canonical_order_for_every_lens(self):
        packet = source_context.build_stop_packet(
            task_anchor="Preserve the public contract.",
            last_assistant_message="The work is complete.",
            evidence_records=[
                {"seq": 1, "category": "inspection", "content": "source-marker"},
                {"seq": 2, "category": "change", "content": "change-marker"},
                {"seq": 3, "category": "verification", "content": "verify-marker"},
                {"seq": 4, "category": "failure", "content": "failure-marker"},
            ],
        )
        lenses = ("jeff", "linus", "fowler", "beck", "lamport", "carmack")
        markers = (
            "change-marker",
            "verify-marker",
            "failure-marker",
        )

        ordered_packets = {
            lens: build_review_input(packet, ())
            for lens in lenses
        }

        for lens, ordered in ordered_packets.items():
            with self.subTest(lens=lens):
                for marker in markers:
                    self.assertEqual(1, ordered.count(marker))
                self.assertNotIn("source-marker", ordered)
        self.assertEqual(1, len(set(ordered_packets.values())))

    def test_lens_focus_is_the_last_system_instruction_before_evidence(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            seen = {}

            def dispatch(_provider, system_prompt, review_input, *_args, **_kwargs):
                seen["system_prompt"] = system_prompt
                seen["review_input"] = review_input
                return {"status": "no_finding", "finding": "", "usage": {}}

            persona_config.save_stage(root, "review")
            core = ReviewCore(settings_for(root), dispatch=dispatch)
            core.review_once(
                ReviewRequest(
                    schema_version=1,
                    kind="checkpoint",
                    reason="strategy-review",
                    session=SessionRef("codex_cli", "lens-position"),
                    source_packet="packet-marker",
                    source_fingerprint="packet-marker",
                ),
                persist_reaction=False,
            )

        self.assertIn("# CURRENT STATE CHECKPOINT", seen["system_prompt"])
        self.assertNotIn("# ATTENTION LENS", seen["system_prompt"])
        self.assertGreater(
            seen["system_prompt"].rfind("# LENS FOCUS"),
            seen["system_prompt"].rfind("# CURRENT STATE CHECKPOINT"),
        )
        final_focus = seen["system_prompt"].split("# LENS FOCUS", 1)[1]
        self.assertIn(
            "Trace the direct control flow, ownership, and necessary complexity.",
            final_focus,
        )
        self.assertTrue(
            seen["system_prompt"].rstrip().endswith(
                "Trace the direct control flow, ownership, and necessary complexity."
            )
        )
        self.assertNotIn(
            "When several candidates pass the finding gate",
            seen["system_prompt"],
        )
        self.assertEqual("packet-marker", seen["review_input"])

    def test_reported_specialist_focus_is_stable_across_calls(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            routes = [
                lens_router.resolve_review_route(
                    root,
                    environ={},
                    reported_focus="reliability",
                )
                for _ in range(3)
            ]

        self.assertEqual(["lamport", "lamport", "lamport"], [
            route.effective_lens for route in routes
        ])

    def test_reported_focus_selects_a_specialist(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            route = lens_router.resolve_review_route(
                root,
                environ={},
                reported_focus="reliability",
            )

        self.assertEqual("lamport", route.effective_lens)

    def test_missing_report_uses_build_fallback(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            route = lens_router.resolve_review_route(
                root,
                environ={},
            )

        self.assertEqual("beck", route.effective_lens)

    def test_explicit_design_report_routes_to_design_lens(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            route = lens_router.resolve_review_route(
                root,
                environ={},
                reported_focus="design",
            )

        self.assertEqual("jeff", route.effective_lens)

    def test_routing_does_not_own_a_standalone_intervention_classifier(self):
        self.assertFalse(hasattr(checkpoints, "classify_tool"))


class SoftwareSemanticStateTests(unittest.TestCase):
    def test_validation_scope_tracks_target_not_incidental_flags(self):
        from masters_nudge.contracts import ToolCompleted

        session = SessionRef("codex_cli", "scope")
        first = ToolCompleted(
            session,
            "exec_command",
            {"cmd": "python -m pytest -q tests/test_contract.py::test_public"},
            "1 failed",
            failed=True,
            failure_known=True,
        )
        second = ToolCompleted(
            session,
            "exec_command",
            {"cmd": "python -m pytest -vv tests/test_contract.py::test_public"},
            "1 passed",
        )

        self.assertEqual(checkpoints.evidence_scope(first), checkpoints.evidence_scope(second))
        self.assertIn("tests/test_contract.py::test_public", checkpoints.evidence_scope(first))

    def test_one_failure_is_evidence_but_not_an_immediate_interruption(self):
        progress = {
            "last_strategy_event_seq": 0,
            "recent": [
                {"event_seq": 1, "meaningful": True, "failed": True,
                 "evidence_category": "failure", "failure_family": "tests/a.py"},
            ],
        }

        self.assertIsNone(checkpoints.classify_strategy(progress))

    def test_unrelated_failures_do_not_form_a_repeated_failure_family(self):
        progress = {
            "last_strategy_event_seq": 0,
            "recent": [
                {"event_seq": 1, "meaningful": True, "failed": True,
                 "evidence_category": "failure", "failure_family": "tests/a.py"},
                {"event_seq": 2, "meaningful": True, "failed": True,
                 "evidence_category": "failure", "failure_family": "tests/b.py"},
            ],
        }

        self.assertIsNone(checkpoints.classify_strategy(progress))

    def test_same_failure_family_triggers_after_repetition(self):
        progress = {
            "last_strategy_event_seq": 0,
            "recent": [
                {"event_seq": 1, "meaningful": True, "failed": True,
                 "evidence_category": "failure", "failure_family": "tests/a.py"},
                {"event_seq": 2, "meaningful": True, "failed": True,
                 "evidence_category": "failure", "failure_family": "tests/a.py"},
            ],
        }

        review = checkpoints.classify_strategy(progress)
        self.assertEqual("repeated-failure-family", review["trigger"])

    def test_injected_nudge_waits_for_a_complete_semantic_cycle(self):
        progress = {
            "recent": [
                {"event_seq": 11, "evidence_category": "change"},
                {"event_seq": 12, "evidence_category": "inspection"},
            ]
        }
        self.assertFalse(checkpoints.semantic_cycle_after(progress, 10))
        progress["recent"].append(
            {"event_seq": 13, "evidence_category": "verification"}
        )
        self.assertTrue(checkpoints.semantic_cycle_after(progress, 10))

    def test_tool_count_alone_does_not_trigger_a_strategy_review(self):
        progress = {
            "event_seq": 8,
            "last_strategy_event_seq": 0,
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
            checkpoints.classify_strategy(progress)
        )

    def test_first_complete_semantic_cycle_triggers_validated_progress(self):
        progress = {
            "event_seq": 2,
            "last_strategy_event_seq": 0,
            "midturn_review_attempts": 0,
            "recent": [
                {
                    "event_seq": 1,
                    "tool": "apply_patch",
                    "command_family": "apply_patch",
                    "meaningful": True,
                    "failed": False,
                    "mutating": True,
                    "evidence_category": "change",
                },
                {
                    "event_seq": 2,
                    "tool": "exec_command",
                    "command_family": "python -m unittest",
                    "meaningful": True,
                    "failed": False,
                    "mutating": True,
                    "evidence_category": "verification",
                },
            ],
        }

        review = checkpoints.classify_strategy(progress)

        self.assertEqual(review["trigger"], "validated-progress")
        self.assertNotIn("routing_concern", review)

    def test_later_validated_progress_requires_two_new_semantic_cycles(self):
        progress = {
            "last_strategy_event_seq": 2,
            "midturn_review_attempts": 1,
            "recent": [
                {"event_seq": 3, "meaningful": True,
                 "evidence_category": "change"},
                {"event_seq": 4, "meaningful": True,
                 "evidence_category": "verification"},
            ],
        }

        self.assertIsNone(checkpoints.classify_strategy(progress))
        progress["recent"].extend(
            [
                {"event_seq": 5, "meaningful": True,
                 "evidence_category": "change"},
                {"event_seq": 6, "meaningful": True,
                 "evidence_category": "failure"},
            ]
        )

        review = checkpoints.classify_strategy(progress)

        self.assertEqual(review["trigger"], "validated-progress")

    def test_three_midturn_attempts_exhaust_the_shared_budget(self):
        progress = {
            "last_strategy_event_seq": 0,
            "midturn_review_attempts": 3,
            "recent": [
                {"event_seq": 1, "meaningful": True, "failed": True,
                 "evidence_category": "failure", "failure_family": "tests/a.py"},
                {"event_seq": 2, "meaningful": True, "failed": True,
                 "evidence_category": "failure", "failure_family": "tests/a.py"},
                {"event_seq": 3, "meaningful": True,
                 "evidence_category": "change"},
                {"event_seq": 4, "meaningful": True,
                 "evidence_category": "verification"},
            ],
        }

        self.assertIsNone(checkpoints.classify_strategy(progress))

    def test_goal_transition_remains_eligible_after_midturn_budget(self):
        progress = {
            "last_strategy_event_seq": 0,
            "midturn_review_attempts": 3,
            "recent": [
                {"event_seq": 1, "meaningful": True,
                 "goal_transition": "complete"},
            ],
        }

        review = checkpoints.classify_strategy(progress)

        self.assertEqual(review["trigger"], "goal-complete")

    def test_semantic_cycle_counter_ignores_inspection_and_extra_validation(self):
        progress = {
            "recent": [
                {"event_seq": 1, "evidence_category": "verification"},
                {"event_seq": 2, "evidence_category": "change"},
                {"event_seq": 3, "evidence_category": "inspection"},
                {"event_seq": 4, "evidence_category": "verification"},
                {"event_seq": 5, "evidence_category": "verification"},
                {"event_seq": 6, "evidence_category": "change"},
                {"event_seq": 7, "evidence_category": "failure"},
            ]
        }

        self.assertEqual(
            checkpoints.completed_semantic_cycles_after(progress, 0), 2
        )

    def test_repeated_command_does_not_trigger_without_state_change(self):
        progress = {
            "event_seq": 3,
            "last_strategy_event_seq": 0,
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

        self.assertIsNone(
            checkpoints.classify_strategy(progress)
        )

    def test_unverified_change_growth_does_not_trigger_without_a_failure(self):
        recent = [
            {
                "event_seq": index,
                "tool": "exec_command",
                "command_family": "python -m unittest",
                "meaningful": True,
                "failed": False,
                "mutating": False,
            }
            for index in range(11, 14)
        ]
        progress = {
            "event_seq": 13,
            "last_strategy_event_seq": 10,
            "recent": recent,
        }

        progress["recent"] = [
            {
                "event_seq": 11,
                "meaningful": True,
                "failed": False,
                "mutating": True,
                "evidence_category": "change",
            },
            {
                "event_seq": 12,
                "meaningful": True,
                "failed": False,
                "mutating": True,
                "evidence_category": "change",
            },
        ]
        progress["event_seq"] = 12

        self.assertIsNone(
            checkpoints.classify_strategy(progress)
        )

    def test_stop_review_uses_completion_boundary_route(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            seen = {}

            def dispatch(_provider, system_prompt, *_args, **_kwargs):
                seen["system_prompt"] = system_prompt
                return {"status": "no_finding", "finding": "", "usage": {}}

            core = ReviewCore(settings_for(root), dispatch=dispatch)
            core.review_once(
                ReviewRequest(
                    schema_version=1,
                    kind="stop",
                    reason="stop",
                    session=SessionRef("codex_cli", "stop-route"),
                    source_packet="final evidence",
                    source_fingerprint="final-evidence",
                ),
                persist_reaction=False,
            )

        self.assertIn("Linus Torvalds", seen["system_prompt"])

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
                route_metadata={"effective_lens": "beck"},
                source_fingerprint="software-old",
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
                route_metadata={"effective_lens": "fowler"},
                source_fingerprint="trajectory-old",
            )

            newer = storage.append_reaction(
                root,
                session,
                provider="openai",
                model="gpt-test",
                reaction="較新的問題。",
                route_metadata={"effective_lens": "fowler"},
            )
            storage.mark_emitted(root, session, newer["ts"])
            receipts = storage.load_delivery_state(root, session)["receipts"]

        self.assertNotIn(entry["ts"], receipts)
        self.assertEqual("emitted", receipts[newer["ts"]]["status"])

    def test_reaction_metadata_has_one_canonical_lens_field(self):
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
            core.review_once(
                ReviewRequest(
                    schema_version=1,
                    kind="checkpoint",
                    reason="test-fail",
                    session=session,
                    source_packet="checkpoint",
                    source_fingerprint="state-checkpoint",
                    reported_focus="build",
                ),
                persist_reaction=True,
            )

            entries = storage.read_reaction_entries(root, session)

        self.assertTrue(entries[0]["effective_lens"])
        self.assertNotIn("persona", entries[0])
        self.assertNotIn("domain", entries[0])
        self.assertNotIn("finding_scope", entries[0])


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
            outcome = core.review_once(
                ReviewRequest(
                    schema_version=1,
                    kind="checkpoint",
                    reason="test-fail",
                    session=session,
                    source_packet="current packet",
                    source_fingerprint="current-state",
                    reported_focus="performance",
                ),
                persist_reaction=True,
            )
            telemetry = json.loads(
                (root / "review-telemetry.jsonl").read_text(encoding="utf-8").splitlines()[-1]
            )
            self.assertEqual("carmack", telemetry["effective_lens"])
            self.assertNotIn("persona", telemetry)
            self.assertNotIn("domain", telemetry)
            self.assertNotIn("finding_scope", telemetry)
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
