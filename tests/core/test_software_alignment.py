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
    def test_base_prompt_is_an_attention_gate_not_a_case_catalog(self):
        prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        for heading in ("# ROLE", "# EVIDENCE", "# FINDING GATE", "# NUDGE", "# OUTPUT"):
            self.assertIn(heading, prompt)
        for gate in ("NOVEL", "GROUNDED", "CONSEQUENTIAL", "OPEN"):
            self.assertIn(gate, prompt)
        self.assertIn("Missing evidence means unknown, not undone", prompt)
        self.assertIn("Prefer `no_finding`", prompt)
        self.assertNotIn("具體型別、順序、重複與是否延遲求值", prompt)
        self.assertNotIn("新接受案例與一個相鄰拒絕案例", prompt)

    def test_stop_prompt_does_not_force_every_conflict_into_a_question(self):
        self.assertIn("completion claim", STOP_PROMPT)
        self.assertNotIn("時提問", STOP_PROMPT)

    def test_prompt_keeps_one_grounded_nudge_without_forcing_a_question(self):
        prompt = (HERE / "buddy-prompt.txt").read_text(encoding="utf-8")

        self.assertIn("constraint, counterexample, alternative assumption", prompt)
        self.assertIn("at most 52", prompt)
        self.assertNotIn("finding 只放一個開放問句", prompt)
        self.assertNotIn("以「？」結尾", prompt)

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
            evidence_records=[
                {"seq": 1, "category": "change", "content": "auth_service.py changed"},
                {"seq": 2, "category": "failure", "content": "result: 1 failed"},
            ],
        )

        self.assertNotIn("recent blind spots", packet)
        self.assertNotIn("你最近說過", packet)
        self.assertNotIn("正在調整 auth_service.py", packet)

    def test_packet_separates_universal_state_from_software_evidence(self):
        packet = source_context.build_checkpoint_packet(
            task_anchor="修正設定解析並保留既有相容性",
            event_context="reason: verification-gap",
            task_sources={"ISSUE.md": "原始輸入不得崩潰"},
            evidence_records=[
                {"seq": 1, "category": "change", "content": "change:\nparser updated"},
                {"seq": 2, "category": "failure", "scope": "config", "content": "failure:\n1 failed"},
                {"seq": 3, "category": "verification", "scope": "config", "content": "verification:\n20 passed"},
            ],
        )

        self.assertIn("[universal task state]", packet)
        self.assertIn("task_contract:", packet)
        self.assertIn("verified_facts:", packet)
        self.assertIn("open_issues: []", packet)
        self.assertIn("[software engineering evidence]", packet)
        self.assertIn("relevant_changes:", packet)
        self.assertIn("verification:", packet)
        self.assertNotIn("[failure history]", packet)
        self.assertNotIn("[inspection evidence]", packet)

    def test_stop_packet_labels_completion_claim_inside_universal_state(self):
        packet = source_context.build_stop_packet(
            task_anchor="修正設定解析",
            last_assistant_message="已完成並通過全部測試",
            evidence_records=[
                {"seq": 1, "category": "verification", "content": "20 passed"}
            ],
        )

        universal = packet.split("[end universal task state]", 1)[0]
        self.assertIn("completion_claim:", universal)
        self.assertIn("已完成並通過全部測試", universal)

    def test_unrelated_inspections_do_not_evict_an_open_failure(self):
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
            for index in range(storage.EVIDENCE_RECORDS_MAX):
                storage.record_turn_evidence(
                    root,
                    session,
                    category="inspection",
                    record=f"inspection:\nsource excerpt {index}",
                )
            state = storage.load_turn_state(root, session)

        failures = [
            record
            for record in state["evidence_records"]
            if record["category"] == "failure"
        ]
        self.assertEqual(1, len(failures))
        self.assertIn("ORIGINAL_OPEN_FAILURE", failures[0]["content"])

    def test_packet_has_one_total_budget_and_keeps_decision_critical_edges(self):
        records = []
        seq = 0
        for category, count in (
            ("inspection", 4),
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
            agentcam_evidence="a" * 4000,
        )

        self.assertLessEqual(len(packet), source_context.PACKET_MAX_CHARS)
        self.assertIn("TASK_CONTRACT", packet)
        self.assertIn("COMPLETION_CLAIM", packet)
        self.assertIn("active_failures:", packet)

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
        self.assertNotIn("return preserved", change)
        self.assertIn("12 passed, 1 failed", verification)
        self.assertIn("updated x.py", shell_change)
        for packet in (change, verification, shell_change):
            self.assertNotIn("apply_patch", packet)
            self.assertNotIn("exec_command", packet)
            self.assertNotIn("python -m pytest", packet)
            self.assertNotIn("edit x.py", packet)
            self.assertNotIn("[tool ", packet)

    def test_successful_content_read_becomes_inspection_evidence_without_operation_details(self):
        content = source_context.capture_inspection_evidence(
            "exec_command",
            {"cmd": "Get-Content tests/test_contract.py | Select-Object -First 80"},
            {"content": "assert collect(C) == [C, A, B]"},
        )
        direct = source_context.capture_inspection_evidence(
            "read_file",
            {"file_path": "C:/repo/api.py"},
            {"content": "def public_api(value): ..."},
        )

        self.assertIn("assert collect(C) == [C, A, B]", content)
        self.assertIn("def public_api", direct)
        self.assertIn("source:\n- tests/test_contract.py", content)
        self.assertIn("source:\n- C:/repo/api.py", direct)
        self.assertNotIn("Get-Content", content)

    def test_search_and_compound_read_results_keep_evidence_without_operations(self):
        search = source_context.capture_inspection_evidence(
            "exec_command",
            {"cmd": "rg -n get_unpacked_marks src tests"},
            {"content": "src/api.py:12:def get_unpacked_marks(obj):\n"
                        "tests/test_api.py:8:assert list(get_unpacked_marks(C)) == [C, A]"},
        )
        compound = source_context.capture_inspection_evidence(
            "exec_command",
            {"cmd": "sed -n '1,80p' src/api.py && git diff -- src/api.py"},
            {"content": "def get_unpacked_marks(obj):\n"
                        "+    return normalize_mark_list(mark_list)"},
        )

        self.assertIn("def get_unpacked_marks", search)
        self.assertIn("assert list", search)
        self.assertIn("normalize_mark_list", compound)
        for packet in (search, compound):
            self.assertNotIn("rg -n", packet)
            self.assertNotIn("sed -n", packet)
            self.assertNotIn("git diff", packet)

    def test_navigation_and_search_do_not_become_inspection_evidence(self):
        cases = (
            {"cmd": "Get-ChildItem tests"},
            {"cmd": "git status --short"},
            {"cmd": "pwd"},
        )

        for tool_input in cases:
            with self.subTest(tool_input=tool_input):
                self.assertEqual(
                    "",
                    source_context.capture_inspection_evidence(
                        "exec_command",
                        tool_input, {"content": "tests/test_contract.py:42"}
                    ),
                )

    def test_packet_keeps_source_evidence_inside_the_software_block(self):
        packet = source_context.build_checkpoint_packet(
            task_anchor="Preserve the public contract.",
            event_context="reason: review",
            evidence_records=[
                {
                    "seq": 4,
                    "category": "inspection",
                    "content": "inspection:\nassert collect(C) == [C, A, B]",
                }
            ],
        )

        self.assertIn("[software engineering evidence]", packet)
        self.assertIn("relevant_sources:", packet)
        self.assertIn("assert collect(C) == [C, A, B]", packet)

    def test_packet_reduces_large_source_evidence_to_a_current_excerpt(self):
        content = "inspection:\n" + "x" * (source_context.TASK_SOURCE_MAX_CHARS - 20)
        packet = source_context.build_checkpoint_packet(
            task_anchor="修正公開行為",
            event_context="reason: review",
            evidence_records=[
                {"seq": 1, "category": "inspection", "content": content}
            ],
        )

        self.assertIn("inspection:", packet)
        self.assertIn(source_context.TRUNCATION_MARKER, packet)
        self.assertLess(len(packet), len(content))

    def test_only_two_latest_source_excerpts_enter_the_current_snapshot(self):
        records = []
        for seq, marker in enumerate(("accept-boundary", "semantic-owner", "api-shape"), 1):
            content = source_context.capture_inspection_evidence(
                "exec_command",
                {"cmd": f"sed -n '1,240p' source-{seq}.py"},
                {"content": marker + "\n" + (str(seq) * 5000)},
            )
            records.append({"seq": seq, "category": "inspection", "content": content})

        packet = source_context.build_checkpoint_packet(
            task_anchor="修正公開行為",
            event_context="reason: review",
            evidence_records=records,
        )

        self.assertNotIn("accept-boundary", packet)
        self.assertIn("semantic-owner", packet)
        self.assertIn("api-shape", packet)


class SoftwareEvidenceRoutingTests(unittest.TestCase):
    def test_same_packet_is_reordered_for_each_lens_without_losing_evidence(self):
        packet = source_context.build_stop_packet(
            task_anchor="Preserve the public contract.",
            last_assistant_message="The work is complete.",
            agentcam_evidence="runtime-marker",
            evidence_records=[
                {"seq": 1, "category": "inspection", "content": "source-marker"},
                {"seq": 2, "category": "change", "content": "change-marker"},
                {"seq": 3, "category": "verification", "content": "verify-marker"},
                {"seq": 4, "category": "failure", "content": "failure-marker"},
            ],
        )
        expected_first = {
            "jeff": "relevant_sources:",
            "linus": "relevant_changes:",
            "fowler": "relevant_sources:",
            "beck": "verification:",
            "lamport": "active_failures:",
            "carmack": "external_runtime_evidence:",
        }
        markers = (
            "source-marker",
            "change-marker",
            "verify-marker",
            "failure-marker",
            "runtime-marker",
        )

        ordered_packets = {
            lens: build_review_input(packet, (), effective_lens=lens)
            for lens in expected_first
        }

        for lens, ordered in ordered_packets.items():
            with self.subTest(lens=lens):
                software = ordered.split("[software engineering evidence]", 1)[1]
                first_label = next(
                    line for line in software.splitlines() if line.endswith(":")
                )
                self.assertEqual(expected_first[lens], first_label)
                for marker in markers:
                    self.assertEqual(1, ordered.count(marker))
        self.assertEqual(6, len(set(ordered_packets.values())))

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
            core.review(
                ReviewRequest(
                    schema_version=1,
                    kind="checkpoint",
                    reason="large-diff",
                    session=SessionRef("codex_cli", "lens-position"),
                    source_packet="packet-marker",
                    source_fingerprint="packet-marker",
                ),
                persist_reaction=False,
            )

        self.assertIn("# CURRENT STATE CHECKPOINT", seen["system_prompt"])
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
                "When several candidates pass the finding gate, select the one "
                "that best matches this focus."
            )
        )
        self.assertEqual("packet-marker", seen["review_input"])

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

    def test_goal_words_alone_do_not_misroute_to_system_causality(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona_config.save_stage(root, "build")
            route = lens_router.resolve_review_route(
                root,
                "acceptance criteria are not yet verified",
                checkpoint=True,
            )

        self.assertEqual("beck", route.effective_lens)

    def test_upstream_constraint_and_downstream_compensation_route_to_jeff(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            persona_config.save_stage(root, "build")
            route = lens_router.resolve_review_route(
                root,
                "source of truth ownership forced a downstream fallback",
                checkpoint=True,
            )

        self.assertEqual("jeff", route.effective_lens)

    def test_successful_measurement_is_a_carmack_checkpoint(self):
        from masters_nudge.contracts import ToolCompleted

        event = ToolCompleted(
            SessionRef("codex_cli", "perf"),
            "exec_command",
            {"cmd": "python benchmark.py"},
            "baseline latency 18ms, candidate latency 12ms",
            mutating=False,
        )

        checkpoint = checkpoints.classify_tool(event)

        self.assertEqual("measured-performance", checkpoint["routing_concern"])

    def test_new_forwarding_layer_is_a_linus_checkpoint(self):
        from masters_nudge.contracts import ToolCompleted

        event = ToolCompleted(
            SessionRef("codex_cli", "directness"),
            "apply_patch",
            {"cmd": "*** Begin Patch\n+def compatibility_wrapper():\n+    return delegate()\n*** End Patch"},
            "Success",
            mutating=True,
        )

        checkpoint = checkpoints.classify_tool(event, changed_line_count=12)

        self.assertEqual("completion-boundary", checkpoint["routing_concern"])


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

    def test_repeated_command_does_not_trigger_without_state_change(self):
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

        self.assertIsNone(
            checkpoints.classify_strategy(progress, changed_line_count=12)
        )

    def test_unverified_change_growth_routes_to_feedback_loop_once(self):
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
            "changed_lines_at_strategy": 0,
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

        review = checkpoints.classify_strategy(progress, changed_line_count=12)

        self.assertEqual("verification-gap", review["trigger"])
        self.assertEqual("feedback-loop", review["routing_concern"])

    def test_stop_review_uses_completion_boundary_route(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            seen = {}

            def dispatch(_provider, system_prompt, *_args, **_kwargs):
                seen["system_prompt"] = system_prompt
                return {"status": "no_finding", "finding": "", "usage": {}}

            core = ReviewCore(settings_for(root), dispatch=dispatch)
            core.review(
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
