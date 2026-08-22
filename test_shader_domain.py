#!/usr/bin/env python3
"""Shader workspace specialization integration tests."""

from __future__ import annotations

import tempfile
import unittest
import json
from pathlib import Path

import shader_router
from masters_nudge import profiles
from masters_nudge import prompting
from masters_nudge import storage
from masters_nudge.contracts import EvidenceBundle, ReviewRequest, SessionRef
from masters_nudge.core import ReviewCore
from masters_nudge.runtime import RuntimePaths, RuntimeSettings


HERE = Path(__file__).resolve().parent
SHADER_FIXTURES = HERE / "tests" / "fixtures" / "shader"


class ShaderRouteTests(unittest.TestCase):
    def test_structured_route_keeps_original_evidence_order(self):
        with tempfile.TemporaryDirectory() as raw:
            state_dir = Path(raw)
            route = shader_router.resolve_shader_route(
                "optimize",
                primary_lens="karis",
                checkpoint=True,
                state_dir=state_dir,
                session_key="session",
                route_signals=(
                    "karis|render-contract-evidence",
                    "carmack|executed-work-elimination",
                ),
            )

        self.assertEqual("karis", route.effective_lens)
        self.assertEqual("render-contract-evidence", route.trigger)

    def test_structured_research_signal_routes_without_keyword_competition(self):
        route = shader_router.resolve_shader_route(
            "optimize",
            "precision fragment benchmark words would otherwise dominate",
            primary_lens="lottes",
            checkpoint=True,
            route_signals=("quilez|procedural-representation",),
        )

        self.assertEqual("quilez", route.effective_lens)
        self.assertEqual("procedural-representation", route.trigger)
        self.assertEqual("shader_structured_evidence", route.source)

    def test_structured_route_skips_the_two_most_recent_injected_personas(self):
        route = shader_router.resolve_shader_route(
            "optimize",
            primary_lens="karis",
            checkpoint=True,
            route_signals=(
                "carmack|executed-work-elimination",
                "akenine_moller|visibility-work-elimination",
                "quilez|procedural-representation",
            ),
            injected_personas=("carmack", "akenine_moller"),
        )

        self.assertEqual("quilez", route.effective_lens)
        self.assertEqual("procedural-representation", route.trigger)
        self.assertEqual("shader_structured_evidence", route.source)

    def test_stop_primary_is_not_changed_by_checkpoint_cooldown(self):
        route = shader_router.resolve_shader_route(
            "optimize",
            primary_lens="carmack",
            checkpoint=False,
            route_signals=("akenine_moller|visibility-work-elimination",),
            injected_personas=("carmack", "akenine_moller"),
        )

        self.assertEqual("carmack", route.effective_lens)

    def test_stage_defaults_cover_the_four_shader_lifecycle_stages(self):
        self.assertEqual(shader_router.resolve_shader_route("frame").effective_lens, "karis")
        self.assertEqual(shader_router.resolve_shader_route("explore").effective_lens, "quilez")
        self.assertEqual(shader_router.resolve_shader_route("optimize").effective_lens, "carmack")
        self.assertEqual(shader_router.resolve_shader_route("verify").effective_lens, "tatarchuk")

    def test_measured_gpu_hotspot_beats_generic_unity_integration_words(self):
        route = shader_router.resolve_shader_route(
            "frame",
            "Unity URP GPU profiler shows 8 ms fragment hot path and high bandwidth.",
        )
        self.assertEqual(route.effective_lens, "carmack")
        self.assertEqual(route.trigger, "measured-performance-evidence")

    def test_checkpoint_override_keeps_the_selected_primary_lens(self):
        route = shader_router.resolve_shader_route(
            "frame",
            "GPU profiler reports an 8 ms fragment hotspot",
            primary_lens="lottes",
            checkpoint=True,
        )

        self.assertEqual(route.primary_lens, "lottes")
        self.assertEqual(route.effective_lens, "carmack")

    def test_stop_uses_the_selected_primary_without_evidence_override(self):
        route = shader_router.resolve_shader_route(
            "frame",
            "GPU profiler reports an 8 ms fragment hotspot",
            primary_lens="lottes",
            checkpoint=False,
        )

        self.assertEqual(route.primary_lens, "lottes")
        self.assertEqual(route.effective_lens, "lottes")

    def test_invalid_primary_lens_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported Shader lens"):
            shader_router.resolve_shader_route(
                "optimize", primary_lens="not_a_lens"
            )

    def test_multi_signal_checkpoints_keep_the_strongest_matching_lens(self):
        evidence = (
            "GPU profiler benchmark shows 8 ms bandwidth, register pressure, "
            "compiler disassembly, hot path, and occupancy; twelve-layer overdraw "
            "and culling; procedural noise distance field; material BRDF render pass."
        )
        with tempfile.TemporaryDirectory() as raw:
            routes = [
                shader_router.resolve_shader_route(
                    "frame",
                    evidence,
                    primary_lens="karis",
                    checkpoint=True,
                    state_dir=Path(raw),
                    session_key="shader-session",
                )
                for _ in range(4)
            ]

        self.assertEqual([route.effective_lens for route in routes], ["carmack"] * 4)

    def test_novelty_never_selects_a_lens_without_matching_evidence(self):
        with tempfile.TemporaryDirectory() as raw:
            routes = [
                shader_router.resolve_shader_route(
                    "frame",
                    "GPU profiler reports 8 ms bandwidth",
                    primary_lens="karis",
                    checkpoint=True,
                    state_dir=Path(raw),
                    session_key="shader-session",
                )
                for _ in range(3)
            ]

        self.assertEqual(
            [route.effective_lens for route in routes],
            ["carmack", "carmack", "carmack"],
        )

    def test_shader_route_history_does_not_override_evidence_strength(self):
        evidence = "GPU profiler shows 8 ms bandwidth and procedural noise."
        with tempfile.TemporaryDirectory() as raw:
            state_dir = Path(raw)
            first = shader_router.resolve_shader_route(
                "frame",
                evidence,
                checkpoint=True,
                state_dir=state_dir,
                session_key="session-a",
            )
            second = shader_router.resolve_shader_route(
                "frame",
                evidence,
                checkpoint=True,
                state_dir=state_dir,
                session_key="session-a",
            )
            other_session = shader_router.resolve_shader_route(
                "frame",
                evidence,
                checkpoint=True,
                state_dir=state_dir,
                session_key="session-b",
            )

        self.assertEqual(first.effective_lens, second.effective_lens)
        self.assertEqual(other_session.effective_lens, first.effective_lens)

    def test_frozen_c17_packet_keeps_one_evidence_selected_lens(self):
        fixture = json.loads(
            (SHADER_FIXTURES / "prompt-replay-c17-v1.json").read_text(
                encoding="utf-8"
            )
        )
        evidence = "\n".join(fixture["source"].values())
        with tempfile.TemporaryDirectory() as raw:
            routes = [
                shader_router.resolve_shader_route(
                    "frame",
                    evidence,
                    primary_lens="karis",
                    checkpoint=True,
                    state_dir=Path(raw),
                    session_key="c17-session",
                )
                for _ in range(6)
            ]

        self.assertEqual(len({route.effective_lens for route in routes}), 1)


class ShaderPersonaContractTests(unittest.TestCase):
    def test_base_prompt_is_written_for_a_cold_start_reviewer(self):
        prompt = (HERE / "domains" / "shader" / "base-prompt.txt").read_text(
            encoding="utf-8"
        )

        self.assertIn("只處理眼前這份 Shader 研究證據封包", prompt)
        self.assertIn("只留一個最值得主模型追問的 finding", prompt)
        self.assertIn("每則 finding 都必須錨定封包中可見的內容", prompt)
        self.assertNotIn("第三方", prompt)
        for diluted_context in (
            "技術推理卡帶",
            "濾鏡",
            "persona",
            "延遲注入",
            "填空",
        ):
            with self.subTest(diluted_context=diluted_context):
                self.assertNotIn(diluted_context, prompt)

    def test_base_prompt_requests_a_finding_not_an_instruction(self):
        prompt = (HERE / "domains" / "shader" / "base-prompt.txt").read_text(
            encoding="utf-8"
        )

        required_contract = (
            "尚未被注意的關係",
            "finding 只放一個開放問句",
            "必須以「？」收束",
            "不要替主模型回答問題",
            "不要提供修改方式、下一步計畫",
            "不要寫成 code review",
            "52 字",
        )
        for clause in required_contract:
            with self.subTest(clause=clause):
                self.assertIn(clause, prompt)

        self.assertNotIn("陳述句或問句", prompt)
        self.assertNotIn("可以參考的語氣", prompt)

    def test_base_prompt_prefers_a_discriminant_and_silences_unchanged_gaps(self):
        prompt = (HERE / "domains" / "shader" / "base-prompt.txt").read_text(
            encoding="utf-8"
        )

        self.assertIn("仍混在一起的兩種解釋", prompt)
        self.assertIn("新材料沒有改變支持它的證據", prompt)
        self.assertIn("使用 no_finding", prompt)

    def test_shader_persona_is_appended_without_product_meta_context(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            prompt_file = root / "base-prompt.txt"
            persona_dir = root / "personas"
            persona_dir.mkdir()
            prompt_file.write_text("BASE", encoding="utf-8")
            (persona_dir / "carmack.txt").write_text("PERSONA", encoding="utf-8")

            result = prompting.build_system_prompt(
                prompt_file=prompt_file,
                persona_dir=persona_dir,
                data_dir=root,
                route=shader_router.resolve_shader_route(
                    "optimize", checkpoint=False
                ),
                persona_names=shader_router.SHADER_PERSONAS,
                domain="shader",
            )

        self.assertEqual(result, "BASE\n\nPERSONA\n")
        self.assertNotIn("技術濾鏡", result)
        self.assertNotIn("這一輪借用", result)

    def test_each_persona_encodes_a_distinct_reasoning_program(self):
        persona_dir = HERE / "domains" / "shader" / "personas"
        required_sections = (
            "## 核心概念",
            "## 引導場景",
            "## 兩個簡短案例",
            "## 形成 Nudge",
        )
        signature_anchors = {
            "akenine_moller.txt": ("screen-space coverage", "depth complexity", "conservative bound"),
            "carmack.txt": ("機器真正少做工作", "完整執行路徑", "register lifetime"),
            "karis.txt": ("Forward", "DepthOnly", "ShadowCaster"),
            "lottes.txt": ("Nyquist", "fwidth", "spatiotemporal"),
            "quilez.txt": ("Lipschitz", "raymarch", "domain repetition"),
            "tatarchuk.txt": ("wave/warp", "tile-based", "validation matrix"),
        }

        for filename, anchors in signature_anchors.items():
            with self.subTest(persona=filename):
                text = (persona_dir / filename).read_text(encoding="utf-8")
                for section in required_sections:
                    self.assertIn(section, text)
                for anchor in anchors:
                    self.assertIn(anchor, text)
                self.assertNotIn("只借用公開技術工作的問題意識", text)
                self.assertNotIn("不要扮演人物", text)
                self.assertNotIn("## 內部推理", text)
                self.assertNotIn("必須", text)
                self.assertEqual(text.count("\n## "), 4)

                guidance = text.split("## 引導場景", 1)[1].split(
                    "## 兩個簡短案例", 1
                )[0]
                self.assertTrue(guidance.rstrip().endswith("？"))

                case_block = text.split("## 兩個簡短案例", 1)[1].split(
                    "## 形成 Nudge", 1
                )[0]
                cases = [
                    line for line in case_block.splitlines() if line.startswith("- ")
                ]
                self.assertEqual(len(cases), 2)
                nudge_block = text.split("## 形成 Nudge", 1)[1]
                for imperative in (
                    "要求",
                    "指定一個",
                    "下一步",
                    "重測",
                    "最小實驗",
                ):
                    self.assertNotIn(imperative, nudge_block)
                self.assertLessEqual(len(text), 700)
                self.assertLessEqual(len(text.splitlines()), 26)

    def test_karis_persona_stays_on_cross_pass_material_semantics(self):
        text = (
            HERE / "domains" / "shader" / "personas" / "karis.txt"
        ).read_text(encoding="utf-8")

        for anchor in ("Forward", "DepthOnly", "ShadowCaster", "alpha clip"):
            self.assertIn(anchor, text)
        for cost_drift in ("shader variant", "每個 pixel", "語意或成本"):
            self.assertNotIn(cost_drift, text)


class ShaderWorkspaceProfileTests(unittest.TestCase):
    def test_recommended_shader_profile_matches_v12_environment(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw) / "data"
            workspace = Path(raw) / "shader-workspace"

            result = profiles.configure_recommended_shader_profile(
                data_dir, workspace
            )
            profile, error = profiles.load_workspace_profile(
                data_dir,
                SessionRef("codex_cli", "session", cwd=str(workspace)),
            )

        self.assertTrue(result["saved"])
        self.assertEqual(error, "")
        self.assertEqual(profile.domain, "shader")
        self.assertEqual(profile.stage, "explore")
        self.assertEqual((profile.provider, profile.model), ("anthropic", "opus"))
        self.assertEqual(profile.review_mode, "all")
        self.assertEqual(profile.primary_lens, "")
        self.assertEqual(profile.reasoning_effort, "")

    def test_existing_shader_profile_without_primary_lens_remains_valid(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw) / "data"
            workspace = Path(raw) / "shader-workspace"
            path = profiles.workspace_profile_path(data_dir, workspace)
            path.parent.mkdir(parents=True)
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "workspace": profiles.normalize_workspace(workspace),
                        "domain": "shader",
                        "stage": "frame",
                        "provider": "grok",
                        "model": "",
                        "review_mode": "all",
                    }
                ),
                encoding="utf-8",
            )

            profile, error = profiles.load_workspace_profile(
                data_dir,
                SessionRef("codex_cli", "session", cwd=str(workspace)),
            )

        self.assertEqual(error, "")
        self.assertEqual(profile.primary_lens, "")
        self.assertEqual(profile.reasoning_effort, "")

    def test_shader_profile_accepts_grok_cli_default_model(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw) / "data"
            workspace = Path(raw) / "shader-workspace"
            result = profiles.configure_workspace_profile(
                data_dir,
                workspace,
                domain="shader",
                stage="frame",
                provider="grok",
                model="",
                review_mode="all",
                reasoning_effort="medium",
            )
            profile, error = profiles.load_workspace_profile(
                data_dir,
                SessionRef("codex_cli", "session", cwd=str(workspace)),
            )

        self.assertTrue(result["saved"])
        self.assertEqual(error, "")
        self.assertEqual((profile.domain, profile.stage), ("shader", "frame"))
        self.assertEqual((profile.provider, profile.model), ("grok", ""))
        self.assertEqual(profile.reasoning_effort, "medium")
        self.assertEqual(profile.primary_lens, "")

    def test_shader_primary_lens_selection_is_saved_per_workspace(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw) / "data"
            workspace = Path(raw) / "shader-workspace"
            profiles.configure_workspace_profile(
                data_dir,
                workspace,
                domain="shader",
                stage="frame",
                provider="grok",
                model="",
                review_mode="all",
                reasoning_effort="medium",
            )

            result = profiles.set_shader_primary_lens(
                data_dir, workspace, "quilez"
            )
            profile, error = profiles.load_workspace_profile(
                data_dir,
                SessionRef("codex_cli", "session", cwd=str(workspace)),
            )

        self.assertTrue(result["saved"])
        self.assertEqual(error, "")
        self.assertEqual(profile.primary_lens, "quilez")
        self.assertEqual(profile.stage, "frame")
        self.assertEqual((profile.provider, profile.model), ("grok", ""))
        self.assertEqual(profile.reasoning_effort, "medium")

    def test_shader_primary_lens_selection_rejects_unknown_lens(self):
        with tempfile.TemporaryDirectory() as raw:
            data_dir = Path(raw) / "data"
            workspace = Path(raw) / "shader-workspace"
            profiles.configure_workspace_profile(
                data_dir,
                workspace,
                domain="shader",
                stage="frame",
                provider="grok",
                model="",
                review_mode="all",
                reasoning_effort="medium",
            )

            result = profiles.set_shader_primary_lens(
                data_dir, workspace, "not_a_lens"
            )

        self.assertFalse(result["saved"])
        self.assertIn("unsupported Shader lens", result["error"])

    def test_review_core_loads_shader_prompt_persona_and_workspace_provider(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "shader-workspace"
            workspace.mkdir()
            settings = RuntimeSettings(
                "openai",
                "host-default-model",
                60,
                15,
                RuntimePaths(HERE, root / "data", root / "error.log"),
            )
            configured = profiles.configure_workspace_profile(
                settings.paths.data_dir,
                workspace,
                domain="shader",
                stage="frame",
                provider="grok",
                model="",
                review_mode="all",
                reasoning_effort="medium",
            )
            calls = []

            def dispatch(provider, system_prompt, review_input, model, **kwargs):
                calls.append((provider, system_prompt, review_input, model, kwargs))
                return {"status": "no_finding", "finding": "", "usage": {}}

            outcome = ReviewCore(settings, dispatch=dispatch).review(
                ReviewRequest(
                    schema_version=1,
                    kind="checkpoint",
                    reason="contract-check",
                    session=SessionRef(
                        "codex_cli", "session", cwd=str(workspace), repo_root=str(workspace)
                    ),
                    evidence=EvidenceBundle(checkpoint_event="material contract is incomplete"),
                    source_packet="shader evidence packet",
                    source_fingerprint="fingerprint",
                ),
                persist_reaction=False,
            )

        self.assertTrue(configured["saved"])
        self.assertEqual((outcome.provider, outcome.model), ("grok", ""))
        self.assertEqual(outcome.effective_lens, "karis")
        self.assertEqual(len(calls), 1)
        provider, system_prompt, _review_input, model, dispatch_kwargs = calls[0]
        self.assertEqual((provider, model), ("grok", ""))
        self.assertEqual(dispatch_kwargs["reasoning_effort"], "medium")
        self.assertIn("只處理眼前這份 Shader 研究證據封包", system_prompt)
        self.assertNotIn("第三方", system_prompt)
        self.assertIn("DepthOnly", system_prompt)
        self.assertIn("ShadowCaster", system_prompt)
        self.assertNotIn("# Shader 技術濾鏡", system_prompt)
        self.assertNotIn("這一輪借用", system_prompt)

    def test_stop_uses_selected_shader_primary_lens(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "shader-workspace"
            workspace.mkdir()
            settings = RuntimeSettings(
                "openai",
                "host-default-model",
                60,
                15,
                RuntimePaths(HERE, root / "data", root / "error.log"),
            )
            profiles.configure_workspace_profile(
                settings.paths.data_dir,
                workspace,
                domain="shader",
                stage="frame",
                provider="grok",
                model="",
                review_mode="all",
                primary_lens="lottes",
            )

            outcome = ReviewCore(
                settings,
                dispatch=lambda *_args, **_kwargs: {
                    "status": "no_finding",
                    "finding": "",
                    "usage": {},
                },
            ).review(
                ReviewRequest(
                    schema_version=1,
                    kind="stop",
                    reason="stop",
                    session=SessionRef(
                        "codex_cli", "session", cwd=str(workspace), repo_root=str(workspace)
                    ),
                    evidence=EvidenceBundle(
                        checkpoint_event="GPU profiler reports an 8 ms fragment hotspot"
                    ),
                    source_packet="shader evidence packet",
                    source_fingerprint="fingerprint",
                ),
                persist_reaction=False,
            )

        self.assertEqual(outcome.effective_lens, "lottes")

    def test_checkpoint_can_override_selected_shader_primary_lens(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "shader-workspace"
            workspace.mkdir()
            settings = RuntimeSettings(
                "openai",
                "host-default-model",
                60,
                15,
                RuntimePaths(HERE, root / "data", root / "error.log"),
            )
            profiles.configure_workspace_profile(
                settings.paths.data_dir,
                workspace,
                domain="shader",
                stage="frame",
                provider="grok",
                model="",
                review_mode="all",
                primary_lens="lottes",
            )

            outcome = ReviewCore(
                settings,
                dispatch=lambda *_args, **_kwargs: {
                    "status": "no_finding",
                    "finding": "",
                    "usage": {},
                },
            ).review(
                ReviewRequest(
                    schema_version=1,
                    kind="checkpoint",
                    reason="benchmark",
                    session=SessionRef(
                        "codex_cli", "session", cwd=str(workspace), repo_root=str(workspace)
                    ),
                    evidence=EvidenceBundle(
                        checkpoint_event="GPU profiler reports an 8 ms fragment hotspot"
                    ),
                    source_packet="shader evidence packet",
                    source_fingerprint="fingerprint",
                ),
                persist_reaction=False,
            )
            route_state_files = list(
                settings.paths.data_dir.glob("*.shader-route.json")
            )

        self.assertEqual(outcome.effective_lens, "carmack")
        self.assertEqual(len(route_state_files), 1)

    def test_shader_research_change_uses_projection_without_generic_strategy_overlay(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "shader-workspace"
            workspace.mkdir()
            settings = RuntimeSettings(
                "openai",
                "host-default-model",
                60,
                15,
                RuntimePaths(HERE, root / "data", root / "error.log"),
            )
            profiles.configure_workspace_profile(
                settings.paths.data_dir,
                workspace,
                domain="shader",
                stage="optimize",
                provider="grok",
                model="",
                review_mode="all",
                primary_lens="carmack",
                reasoning_effort="medium",
            )
            calls = []

            def dispatch(provider, system_prompt, review_input, model, **kwargs):
                calls.append((system_prompt, review_input))
                return {"status": "no_finding", "finding": "", "usage": {}}

            storage.append_reaction(
                settings.paths.data_dir,
                SessionRef(
                    "codex_cli", "session", cwd=str(workspace), repo_root=str(workspace)
                ),
                provider="grok",
                model="",
                reaction="舊盲點已由材料包自行標示。",
                route_metadata={"effective_lens": "carmack"},
                reason="shader-research-change",
            )

            ReviewCore(settings, dispatch=dispatch).review(
                ReviewRequest(
                    schema_version=1,
                    kind="strategy",
                    reason="shader-research-change",
                    session=SessionRef(
                        "codex_cli", "session", cwd=str(workspace), repo_root=str(workspace)
                    ),
                    evidence=EvidenceBundle(
                        checkpoint_event="[new research-state delta]\nA28: planned -> measured"
                    ),
                    source_packet="[current research state]\nfrontier: A26",
                    source_fingerprint="shader-research-abc",
                ),
                persist_reaction=False,
            )

        system_prompt, review_input = calls[0]
        self.assertNotIn("長流程策略 checkpoint", system_prompt)
        self.assertNotIn("工作途中 checkpoint", system_prompt)
        self.assertEqual(review_input, "[current research state]\nfrontier: A26")
        self.assertNotIn("[你最近說過]", review_input)

    def test_shader_research_metadata_controls_route_and_is_persisted(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "shader-workspace"
            workspace.mkdir()
            settings = RuntimeSettings(
                "openai",
                "host-default-model",
                60,
                15,
                RuntimePaths(HERE, root / "data", root / "error.log"),
            )
            profiles.configure_workspace_profile(
                settings.paths.data_dir,
                workspace,
                domain="shader",
                stage="optimize",
                provider="grok",
                model="",
                review_mode="all",
                primary_lens="lottes",
            )
            session = SessionRef(
                "codex_cli", "structured-route", cwd=str(workspace), repo_root=str(workspace)
            )
            outcome = ReviewCore(
                settings,
                dispatch=lambda *_args, **_kwargs: {
                    "status": "finding",
                    "finding": "公式變短與距離場仍可靠，是兩個尚未分開的結果。",
                    "usage": {},
                },
            ).review(
                ReviewRequest(
                    schema_version=1,
                    kind="strategy",
                    reason="shader-research-change",
                    session=session,
                    evidence=EvidenceBundle(checkpoint_event="precision fragment benchmark"),
                    source_packet="structured packet",
                    source_fingerprint="source-1",
                    route_signals=("quilez|procedural-representation",),
                    route_basis="procedural-representation",
                    gap_key="quilez:procedural-representation",
                    gap_evidence_fingerprint="gap-1",
                    material_completeness=0.7,
                ),
                persist_reaction=True,
            )
            entry = [
                item
                for item in storage.read_reaction_entries(
                    settings.paths.data_dir, session
                )
                if item.get("kind") == "review"
            ][0]
            telemetry = [
                json.loads(line)
                for line in (settings.paths.data_dir / "review-telemetry.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ][0]

        self.assertEqual("quilez", outcome.effective_lens)
        self.assertEqual("quilez:procedural-representation", entry["gap_key"])
        self.assertEqual("procedural-representation", entry["route_basis"])
        self.assertEqual("quilez:procedural-representation", telemetry["gap_key"])
        self.assertEqual(0.7, telemetry["material_completeness"])
        self.assertEqual("shader_structured_evidence", telemetry["route_source"])

    def test_review_core_uses_injected_persona_cooldown_without_warming_provider(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "shader-workspace"
            workspace.mkdir()
            settings = RuntimeSettings(
                "openai",
                "host-default-model",
                60,
                15,
                RuntimePaths(HERE, root / "data", root / "error.log"),
            )
            profiles.configure_workspace_profile(
                settings.paths.data_dir,
                workspace,
                domain="shader",
                stage="optimize",
                provider="grok",
                model="",
                review_mode="all",
                primary_lens="carmack",
            )
            session = SessionRef(
                "codex_cli", "cooldown-route", cwd=str(workspace), repo_root=str(workspace)
            )
            for persona in ("carmack", "akenine_moller"):
                entry = storage.append_reaction(
                    settings.paths.data_dir,
                    session,
                    provider="grok",
                    model="",
                    reaction=f"{persona} 的舊 finding。",
                    route_metadata={"effective_lens": persona},
                    reason="shader-research-change",
                )
                storage.mark_delivered(settings.paths.data_dir, session, entry["ts"])

            calls = []

            def dispatch(_provider, _system_prompt, review_input, _model, **_kwargs):
                calls.append(review_input)
                return {"status": "no_finding", "finding": "", "usage": {}}

            outcome = ReviewCore(settings, dispatch=dispatch).review(
                ReviewRequest(
                    schema_version=1,
                    kind="strategy",
                    reason="shader-research-change",
                    session=session,
                    evidence=EvidenceBundle(checkpoint_event="new candidate evidence"),
                    source_packet="cold current packet",
                    source_fingerprint="source-2",
                    route_signals=(
                        "carmack|executed-work-elimination",
                        "akenine_moller|visibility-work-elimination",
                        "quilez|procedural-representation",
                    ),
                ),
                persist_reaction=False,
            )
            route_state = json.loads(
                next(settings.paths.data_dir.glob("*.shader-route.json")).read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual("quilez", outcome.effective_lens)
        self.assertEqual(["cold current packet"], calls)
        self.assertNotIn("provider_call_seq", route_state)
        self.assertNotIn("provider_last_called", route_state)

    def test_provider_error_does_not_add_call_recency_state(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "shader-workspace"
            workspace.mkdir()
            settings = RuntimeSettings(
                "openai",
                "host-default-model",
                60,
                15,
                RuntimePaths(HERE, root / "data", root / "error.log"),
            )
            profiles.configure_workspace_profile(
                settings.paths.data_dir,
                workspace,
                domain="shader",
                stage="optimize",
                provider="grok",
                model="",
                review_mode="all",
                primary_lens="carmack",
            )
            session = SessionRef(
                "codex_cli", "provider-error", cwd=str(workspace), repo_root=str(workspace)
            )

            outcome = ReviewCore(
                settings,
                dispatch=lambda *_args, **_kwargs: {
                    "status": "error",
                    "finding": "",
                    "usage": {},
                },
            ).review(
                ReviewRequest(
                    schema_version=1,
                    kind="strategy",
                    reason="shader-research-change",
                    session=session,
                    evidence=EvidenceBundle(checkpoint_event="candidate evidence"),
                    source_packet="cold current packet",
                    source_fingerprint="source-error",
                    route_signals=("carmack|executed-work-elimination",),
                ),
                persist_reaction=False,
            )
            route_state = json.loads(
                next(settings.paths.data_dir.glob("*.shader-route.json")).read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual("error", outcome.status)
        self.assertNotIn("provider_call_seq", route_state)
        self.assertNotIn("provider_last_called", route_state)

    def test_review_core_assigns_scope_from_host_trigger_semantics(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            workspace = root / "shader-workspace"
            workspace.mkdir()
            settings = RuntimeSettings(
                "openai",
                "host-default-model",
                60,
                15,
                RuntimePaths(HERE, root / "data", root / "error.log"),
            )
            profiles.configure_workspace_profile(
                settings.paths.data_dir,
                workspace,
                domain="shader",
                stage="optimize",
                provider="grok",
                model="",
                review_mode="all",
                primary_lens="carmack",
            )
            session = SessionRef(
                "codex_cli",
                "session",
                cwd=str(workspace),
                repo_root=str(workspace),
            )

            def dispatch(*_args, **_kwargs):
                return {
                    "status": "finding",
                    "finding": "候選仍只消除抵達 sample 後的片元工作。",
                    "usage": {},
                }

            core = ReviewCore(settings, dispatch=dispatch)
            core.review(
                ReviewRequest(
                    schema_version=1,
                    kind="strategy",
                    reason="shader-research-change",
                    session=session,
                    evidence=EvidenceBundle(),
                    source_packet="research state",
                    source_fingerprint="research-a",
                ),
                persist_reaction=True,
            )
            core.review(
                ReviewRequest(
                    schema_version=1,
                    kind="checkpoint",
                    reason="benchmark",
                    session=session,
                    evidence=EvidenceBundle(),
                    source_packet="candidate state",
                    source_fingerprint="candidate-a",
                ),
                persist_reaction=True,
            )

            entries = [
                entry
                for entry in storage.read_reaction_entries(
                    settings.paths.data_dir, session
                )
                if entry.get("kind") == "review"
            ]

        self.assertEqual(
            [(entry["reason"], entry["finding_scope"]) for entry in entries],
            [
                ("shader-research-change", "trajectory"),
                ("benchmark", "candidate"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
