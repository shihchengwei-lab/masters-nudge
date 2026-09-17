import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from masters_nudge.contracts import MaterialLine, MaterialPacket, ToolFault, material_lines
from masters_nudge.evidence import fit_packet
from masters_nudge.provider_contract import parse_feedback


class ContractTests(unittest.TestCase):
    def feedback(self):
        return {"feedback": {"criterion": 4, "evidence": [{"source": "batch_change", "location": "x:1", "excerpt": "x"}],
                             "fact": "x 複製 y", "relationship": "同一值有兩份表示", "question": "哪個必要行為需要 x？"}}

    def test_output_limits_and_partial_feedback(self):
        import copy
        valid = self.feedback()
        self.assertIsNotNone(parse_feedback(json.dumps(valid)))
        invalid = []
        for key, value in (("criterion", True), ("criterion", 7), ("evidence", []), ("fact", "x" * 121),
                           ("question", "請刪除 x"), ("question", "為什麼？怎麼改？")):
            item = copy.deepcopy(valid)
            item["feedback"][key] = value
            invalid.append(item)
        item = copy.deepcopy(valid)
        item["feedback"]["evidence"][0]["excerpt"] = "x" * 121
        invalid.append(item)
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(ToolFault):
                parse_feedback(json.dumps(item))

    def test_schema_field_limits_make_the_combined_limit_unrepresentable(self):
        schema = json.loads((Path(__file__).resolve().parents[2] / "nudge-schema.json").read_text(encoding="utf-8"))
        feedback = schema["properties"]["feedback"]["anyOf"][1]["properties"]
        limits = [feedback[name]["maxLength"] for name in ("fact", "relationship", "question")]
        self.assertLessEqual(sum(limits) + 2, 120)

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
        with self.assertRaises(ToolFault):
            fit_packet(MaterialPacket(material_lines("task_contract", "task/latest", "x" * 21000), "repo"))

    def test_shared_budget_counts_five_categories_not_transport_metadata(self):
        packet = MaterialPacket(material_lines("task_contract", "task/latest", "保留 A"),
                                "repo", "metadata/" * 3000)
        self.assertIs(fit_packet(packet), packet)
        data = json.loads(packet.render())
        data.pop("workspace")
        data.pop("transcript_path")
        from masters_nudge.contracts import json_text
        self.assertEqual(packet.material_chars, len(json_text(data)))

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
        self.assertEqual(payload["lines"], [{"source": "current_structure", "path": "job.py", "line": 2,
                                           "text": "retry_state = status"}])

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
        for _ in range(12):
            self.tools.call("search_repo", {"query": "status"})
        restarted = RepositoryTools(self.repo, 1000, self.root / "reads.jsonl")
        restarted.call("read_file", {"path": "job.py"})
        entries = [json.loads(line) for line in (self.root / "reads.jsonl").read_text().splitlines()]
        self.assertLessEqual(sum(len(row["text"]) for row in entries), 1000)
        self.assertTrue(any(row["exhausted"] for row in entries))

    def test_outside_ignored_and_write_requests_are_faults(self):
        for name, args in (("read_file", {"path": "../secret"}), ("read_file", {"path": "secret.txt"}),
                           ("write_file", {"path": "job.py", "content": "x"})):
            result = self.tools.call(name, args)
            self.assertTrue(result["isError"])
        self.assertEqual((self.repo / "job.py").read_text(), "status = 1\nretry_state = status\n")
