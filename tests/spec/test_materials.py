import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from masters_nudge.contracts import MaterialLine, MaterialPacket, ToolFault, material_lines
from masters_nudge.evidence import fit_packet
from masters_nudge.prompting import delivery_text
from masters_nudge.provider_contract import parse_feedback


class ContractTests(unittest.TestCase):
    def feedback(self):
        return {"feedback": {"criterion": 4, "evidence": [{"source": "batch_change", "location": "x:1", "excerpt": "x"}],
                             "observed": "x := y", "violates": "sources(y) = 2", "prefer": "consumer <- y"}}

    def test_actor_delivery_uses_fixed_formal_fields(self):
        feedback = parse_feedback(json.dumps(self.feedback()))
        self.assertEqual(
            delivery_text(feedback),
            "Masters’ Nudge\nOBSERVED: x := y\nVIOLATES: sources(y) = 2\nPREFER: consumer <- y\n"
            "Before continuing, decide whether OBSERVED is required by the task. "
            "If not, consider PREFER. Implementation remains yours.",
        )

    def test_output_limits_and_partial_feedback(self):
        import copy
        valid = self.feedback()
        self.assertIsNotNone(parse_feedback(json.dumps(valid)))
        invalid = []
        for key, value in (("criterion", True), ("criterion", 7), ("evidence", []),
                           ("observed", "x" * 31), ("violates", ""), ("prefer", "x" * 51)):
            item = copy.deepcopy(valid)
            item["feedback"][key] = value
            invalid.append(item)
        item = copy.deepcopy(valid)
        item["feedback"]["evidence"][0]["excerpt"] = "x" * 121
        invalid.append(item)
        item = copy.deepcopy(valid)
        item["feedback"]["prefer"] = "x" * 50
        self.assertIsNotNone(parse_feedback(json.dumps(item)))
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(ToolFault):
                parse_feedback(json.dumps(item))

    def test_schema_field_limits_make_the_combined_limit_unrepresentable(self):
        schema = json.loads((Path(__file__).resolve().parents[2] / "nudge-schema.json").read_text(encoding="utf-8"))
        feedback = schema["properties"]["feedback"]["anyOf"][1]["properties"]
        limits = [feedback[name]["maxLength"] for name in ("observed", "violates", "prefer")]
        labels = len("OBSERVED: \nVIOLATES: \nPREFER: ")
        self.assertEqual(limits, [30, 30, 50])
        self.assertLessEqual(sum(limits) + labels, 145)

    def test_before_structure_is_dropped_before_task_or_current_code(self):
        before = MaterialLine("before_structure", "old.py", 1, "x" * 21000)
        current = MaterialLine("current_structure", "now.py", 1, "current = True")
        task = MaterialLine("task_contract", "request", 1, "keep behavior")
        packet = fit_packet(MaterialPacket((task, before, current), "repo"))
        self.assertEqual(packet.lines, (task, current))

    def test_null_is_valid_but_broken_output_is_fault(self):
        self.assertIsNone(parse_feedback('{"feedback":null}'))
        for raw in ('', '{}', '{"feedback":null,"error":"timeout"}', '{"nudge":null}'):
            with self.subTest(raw=raw), self.assertRaises(ToolFault):
                parse_feedback(raw)

    def test_packet_can_have_empty_sources_and_never_silently_truncates_contract(self):
        packet = MaterialPacket(material_lines("task_contract", "task/latest", "保留 A"), "repo")
        self.assertEqual(json.loads(fit_packet(packet).render())["before_structure"], [])
        oversized = MaterialPacket(material_lines("task_contract", "task/latest", "x" * 21000), "repo")
        self.assertEqual(fit_packet(oversized), oversized)

    def test_equal_goal_and_request_have_one_latest_contract_copy(self):
        from masters_nudge.contracts import SessionRef
        from masters_nudge.evidence import build_packet
        task = "same contract"
        with tempfile.TemporaryDirectory() as raw:
            subprocess.run(["git", "init", "-q", raw], check=True)
            packet = build_packet(SessionRef("s", "t", raw), {"goal": task, "request": task}, ())
        contracts = [line for line in packet.lines if line.source == "task_contract"]
        self.assertEqual([(line.path, line.text) for line in contracts], [("task/latest", task)])

    def test_shared_budget_counts_five_categories_not_transport_metadata(self):
        packet = MaterialPacket(material_lines("task_contract", "task/latest", "保留 A"),
                                "repo", "metadata/" * 3000)
        self.assertIs(fit_packet(packet), packet)
        data = json.loads(packet.render())
        data.pop("workspace")
        data.pop("transcript_path")
        data.pop("new_test_paths")
        from masters_nudge.contracts import json_text
        self.assertEqual(packet.material_chars, len(json_text(data)))

    def test_packet_groups_one_path_instead_of_repeating_it_for_every_line(self):
        packet = MaterialPacket(material_lines("batch_change", "tool/edit/input", "a\nb\nc"), "repo")
        category = packet.categories()["batch_change"]
        self.assertEqual(category, [{"path": "tool/edit/input", "start": 1,
                                     "lines": ["a", "b", "c"]}])
        self.assertEqual(packet.render().count("tool/edit/input"), 1)

    def test_expected_large_patch_keeps_all_original_lines_within_budget(self):
        from masters_nudge.contracts import SessionRef, ToolCompleted
        from masters_nudge.evidence import build_packet
        patch = "*** Begin Patch\n" + "\n".join("+" + "x" * 38 for _ in range(293)) + "\n*** End Patch"
        event = ToolCompleted("edit-1", "apply_patch", {"command": patch}, "Success\n" + "ok\n" * 90)
        task = "t" * 1048
        with tempfile.TemporaryDirectory() as raw:
            subprocess.run(["git", "init", "-q", raw], check=True)
            packet = build_packet(SessionRef("s", "t", raw), {"goal": task, "request": task}, (event,))
        change = [line.text for line in packet.lines if line.source == "batch_change"]
        self.assertEqual(change, patch.splitlines())
        self.assertLessEqual(packet.material_chars, 20000)

    def test_oversize_success_output_is_compressed_without_losing_task_or_change(self):
        from masters_nudge.contracts import SessionRef, ToolCompleted
        from masters_nudge.evidence import build_packet
        with tempfile.TemporaryDirectory() as raw:
            subprocess.run(["git", "init", "-q", raw], check=True)
            event = ToolCompleted("write-1", "write", {"path": "job.py", "content": "x=1"},
                                  {"exit_code": 0, "output": "ok\n" * 12000})
            packet = build_packet(SessionRef("s", "t", raw), {"goal": "保留行為", "request": "修改 x"}, (event,))
            self.assertLessEqual(packet.material_chars, 20000)
            self.assertIn("x=1", packet.render())
            self.assertIn("修改 x", packet.render())
            self.assertIn("output_omitted", packet.render())

    def test_tool_result_string_fields_are_verbatim_lines_not_escaped_json(self):
        from masters_nudge.contracts import SessionRef, ToolCompleted
        from masters_nudge.evidence import build_packet
        with tempfile.TemporaryDirectory() as raw:
            subprocess.run(["git", "init", "-q", raw], check=True)
            event = ToolCompleted("run-1", "exec", {"cmd": "test"},
                                  {"exit_code": 0, "output": 'profile["enabled"] = True\r\nnext()'})
            packet = build_packet(SessionRef("s", "t", raw), {"goal": "g", "request": "r"}, (event,))
            output = [line for line in packet.lines if line.path == "tool/run-1/output/output"]
            self.assertEqual([line.text for line in output], ['profile["enabled"] = True', "next()"])
            self.assertEqual([line.line for line in output], [1, 2])


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        from masters_nudge.read_only_repo_mcp import RepositoryTools
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "job.py").write_text("status = 1\nretry_state = status\n", encoding="utf-8")
        (self.repo / ".gitignore").write_text("secret.txt\n", encoding="utf-8")
        (self.repo / "secret.txt").write_text("hidden", encoding="utf-8")
        self.tools = RepositoryTools(self.repo, 1000, self.root / "reads.jsonl")

    def test_read_returns_exact_file_line_and_original_text(self):
        result = self.tools.call("read_file", {"path": "job.py", "start_line": 2, "end_line": 2})
        payload = json.loads(result["content"][0]["text"])
        self.assertEqual(payload["segments"], [{"path": "job.py", "start": 2,
                                                 "lines": ["retry_state = status"]}])

    def test_compact_read_preserves_room_for_followup_search(self):
        from masters_nudge.read_only_repo_mcp import RepositoryTools
        source = "".join(f"value_{i} = {i}\n" for i in range(100))
        (self.repo / "long.py").write_text(source, encoding="utf-8")
        tools = RepositoryTools(self.repo, 4000, self.root / "compact-reads.jsonl")
        first = json.loads(tools.call("read_file", {"path": "long.py"})["content"][0]["text"])
        self.assertFalse(first["truncated"])
        self.assertEqual(first["segments"], [{"path": "long.py", "start": 1,
                                               "lines": source.splitlines()}])
        second = json.loads(tools.call("search_repo", {"query": "value_99"})["content"][0]["text"])
        self.assertEqual(second["segments"], [{"path": "long.py", "start": 100,
                                                "lines": ["value_99 = 99"]}])

    def test_bad_line_types_report_and_record_fault_instead_of_crashing(self):
        for value in (None, "1", [], {}):
            with self.subTest(value=value):
                result = self.tools.call("read_file", {"path": "job.py", "start_line": value, "end_line": 2})
                self.assertTrue(result["isError"])
        from masters_nudge.read_only_repo_mcp import read_audit
        records = read_audit(self.root / "reads.jsonl")
        self.assertEqual(len(records), 4)
        self.assertTrue(all(record["fault"] for record in records))
        result = self.tools.call("read_file", {"path": "job.py", "start_line": 1, "end_line": 1})
        self.assertFalse(result["isError"])

    def test_search_and_read_share_persistent_budget(self):
        from masters_nudge.read_only_repo_mcp import RepositoryTools
        last = None
        for _ in range(12):
            last = self.tools.call("search_repo", {"query": "status"})
        restarted = RepositoryTools(self.repo, 1000, self.root / "reads.jsonl")
        last = restarted.call("read_file", {"path": "job.py"})
        entries = [json.loads(line) for line in (self.root / "reads.jsonl").read_text().splitlines()]
        self.assertLessEqual(sum(len(row["text"]) for row in entries), 1000)
        self.assertTrue(any(row["exhausted"] for row in entries))
        self.assertTrue(json.loads(last["content"][0]["text"])["exhausted"])

    def test_search_does_not_spawn_one_git_process_per_file(self):
        for number in range(30):
            (self.repo / f"module_{number}.py").write_text("ordinary = 1\n", encoding="utf-8")
        with mock.patch.object(self.tools, "_git", wraps=self.tools._git) as git:
            result = self.tools.call("search_repo", {"query": "missing_identifier"})
        self.assertFalse(result["isError"])
        self.assertLessEqual(git.call_count, 1)

    def test_outside_ignored_and_write_requests_are_faults(self):
        for name, args in (("read_file", {"path": "../secret"}), ("read_file", {"path": "secret.txt"}),
                           ("write_file", {"path": "job.py", "content": "x"})):
            result = self.tools.call(name, args)
            self.assertTrue(result["isError"])
        self.assertEqual((self.repo / "job.py").read_text(), "status = 1\nretry_state = status\n")
