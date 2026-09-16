"""The Provider judges workspace facts early without taking implementation ownership."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from masters_nudge.core import NudgeCore
from masters_nudge.provider_contract import parse_nudge_result
from masters_nudge.providers import call_codex_result
from masters_nudge.runtime import RuntimePaths, RuntimeSettings
import source_context


ROOT = Path(__file__).resolve().parents[2]


class DecisionContractTests(unittest.TestCase):
    def test_pass_has_no_advice_payload(self):
        result = parse_nudge_result(
            json.dumps(
                {
                    "decision": "pass",
                    "current_choice": "",
                    "structural_cost": "",
                    "direction": "",
                    "evidence": [],
                }
            )
        )

        self.assertEqual(result["decision"], "pass")

    def test_intervention_can_propose_direction_from_concrete_evidence(self):
        result = parse_nudge_result(
            json.dumps(
                {
                    "decision": "intervene",
                    "current_choice": "新增第二組旗標追蹤相同狀態",
                    "structural_cost": "兩組旗標可以互相矛盾",
                    "direction": "讓 NodeFlags.ContainsThis 成為唯一狀態來源",
                    "evidence": ["src/checker.ts:NodeFlags.ContainsThis"],
                }
            )
        )

        self.assertEqual(result["decision"], "intervene")
        self.assertIn("NodeFlags.ContainsThis", result["direction"])
        self.assertEqual(result["evidence"], ["src/checker.ts:NodeFlags.ContainsThis"])

    def test_intervention_rejects_empty_direction_or_evidence(self):
        payload = {
            "decision": "intervene",
            "current_choice": "新增平行狀態",
            "structural_cost": "狀態可能矛盾",
            "direction": "",
            "evidence": [],
        }

        self.assertEqual(
            parse_nudge_result(json.dumps(payload))["decision"],
            "error",
        )


class WorkspaceAccessTests(unittest.TestCase):
    def test_codex_provider_runs_read_only_in_the_actor_workspace(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            schema = root / "schema.json"
            schema.write_text('{"type":"object"}', encoding="utf-8")
            output = json.dumps(
                {
                    "decision": "pass",
                    "current_choice": "",
                    "structural_cost": "",
                    "direction": "",
                    "evidence": [],
                }
            )

            def fake_run(_command, **kwargs):
                Path(_command[_command.index("-o") + 1]).write_text(output, encoding="utf-8")
                return subprocess.CompletedProcess([], 0, "", "")

            with mock.patch(
                "masters_nudge.providers._run_cli_process", side_effect=fake_run
            ) as run:
                result = call_codex_result(
                    "prompt",
                    "snapshot",
                    "model",
                    schema_path=schema,
                    timeout_sec=10,
                    workspace_root=str(root),
                    codex_bin_resolver=lambda: "codex.exe",
                )

        self.assertEqual(result["decision"], "pass")
        self.assertEqual(run.call_args.kwargs["cwd"], str(root))
        command = run.call_args.args[0]
        self.assertIn('mcp_servers.readrepo.enabled_tools=["search_repo","read_file"]', command)
        self.assertIn(
            'mcp_servers.readrepo.default_tools_approval_mode="approve"',
            command,
        )
        self.assertTrue(any("read_only_repo_mcp.py" in part for part in command))

    def test_codex_provider_recovers_clean_result_from_json_events(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            schema = root / "schema.json"
            schema.write_text('{"type":"object"}', encoding="utf-8")
            clean = json.dumps(
                {
                    "decision": "intervene",
                    "current_choice": "局部掃描",
                    "structural_cost": "重做既有語意",
                    "direction": "回到既有 owner",
                    "evidence": ["src/owner.ts:fact"],
                },
                ensure_ascii=False,
            )
            event = json.dumps(
                {
                    "type": "item.completed",
                    "item": {"type": "agent_message", "text": clean},
                },
                ensure_ascii=False,
            )

            def fake_run(command, **kwargs):
                Path(command[command.index("-o") + 1]).write_text(
                    json.dumps(
                        {
                            "decision": "intervene",
                            "current_choice": "�",
                            "structural_cost": "�",
                            "direction": "�",
                            "evidence": ["�"],
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess([], 0, event + "\n", "")

            with mock.patch(
                "masters_nudge.providers._run_cli_process", side_effect=fake_run
            ):
                result = call_codex_result(
                    "prompt",
                    "snapshot",
                    "model",
                    schema_path=schema,
                    timeout_sec=10,
                    workspace_root=str(root),
                    codex_bin_resolver=lambda: "codex.exe",
                )

        self.assertEqual(result["decision"], "intervene")
        self.assertEqual(result["direction"], "回到既有 owner")


class DecisionSnapshotTests(unittest.TestCase):
    def test_snapshot_compares_task_start_and_current_workspace(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"], cwd=root, check=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Test"], cwd=root, check=True
            )
            source = root / "state.ts"
            source.write_text("export const owner = 'existing';\n", encoding="utf-8")
            subprocess.run(["git", "add", "state.ts"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "baseline"], cwd=root, check=True)

            baseline = source_context.capture_workspace_state(str(root))
            source.write_text(
                "export const owner = 'existing';\nexport const parallelOwner = true;\n",
                encoding="utf-8",
            )
            packet = source_context.build_decision_snapshot(
                task_contract="Keep one owner",
                task_start=baseline,
                workspace_root=str(root),
                changed_paths=("state.ts",),
            )

        self.assertIn("[task contract]", packet)
        self.assertIn("[task-start workspace]", packet)
        self.assertIn("[current workspace]", packet)
        self.assertIn("parallelOwner", packet)
        self.assertNotIn("actual_input", packet)
        self.assertNotIn("tool result", packet.lower())


class CoreWorkspaceTests(unittest.TestCase):
    def test_core_passes_workspace_to_provider(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            captured = {}
            settings = RuntimeSettings(
                "openai",
                "test-model",
                RuntimePaths(ROOT, root, root, root / "error.log"),
            )

            def dispatch(*_args, **kwargs):
                captured.update(kwargs)
                return {
                    "decision": "pass",
                    "current_choice": "",
                    "structural_cost": "",
                    "direction": "",
                    "evidence": [],
                }

            outcome = NudgeCore(settings, dispatch=dispatch).nudge_once(
                "snapshot", workspace_root=str(root)
            )

        self.assertEqual(outcome.decision, "pass")
        self.assertEqual(captured["workspace_root"], str(root))


if __name__ == "__main__":
    unittest.main()
