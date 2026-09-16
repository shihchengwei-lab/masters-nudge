from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest

from masters_nudge import read_only_repo_mcp


class ReadOnlyRepoMcpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="mn-readonly-mcp-")
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "flags.ts").write_text(
            "const marker = NodeFlags.ContainsThis;\n", encoding="utf-8"
        )
        (self.root / ".gitignore").write_text("secret.txt\n", encoding="utf-8")
        (self.root / "secret.txt").write_text("token=hidden\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(
            ["git", "add", "src/flags.ts", ".gitignore"],
            cwd=self.root,
            check=True,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def request(self, name: str, arguments: dict) -> dict:
        return read_only_repo_mcp.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            },
            root=self.root,
        )

    def snapshot(self) -> dict[str, bytes]:
        return {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }

    def test_only_search_and_read_are_exposed(self) -> None:
        response = read_only_repo_mcp.handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            root=self.root,
        )
        names = [tool["name"] for tool in response["result"]["tools"]]
        self.assertEqual(names, ["search_repo", "read_file"])

    def test_search_and_large_file_range_are_read_only(self) -> None:
        large = self.root / "src" / "large.ts"
        large.write_text(("padding line\n" * 100_000) + "target line\n", encoding="utf-8")
        subprocess.run(["git", "add", "src/large.ts"], cwd=self.root, check=True)
        before = self.snapshot()

        search = self.request("search_repo", {"query": "NodeFlags.ContainsThis"})
        read = self.request(
            "read_file",
            {"path": "src/large.ts", "start_line": 100_001, "end_line": 100_001},
        )

        self.assertIn("src/flags.ts:1", search["result"]["content"][0]["text"])
        self.assertEqual(
            read["result"]["content"][0]["text"], "100001: target line"
        )
        self.assertEqual(before, self.snapshot())

    def test_escape_ignored_file_and_write_tool_are_rejected(self) -> None:
        before = self.snapshot()
        escaped = self.request("read_file", {"path": "../outside.txt"})
        ignored = self.request("read_file", {"path": "secret.txt"})
        write = self.request(
            "write_file", {"path": "src/flags.ts", "content": "changed"}
        )

        self.assertTrue(escaped["result"]["isError"])
        self.assertTrue(ignored["result"]["isError"])
        self.assertTrue(write["result"]["isError"])
        self.assertEqual(before, self.snapshot())


if __name__ == "__main__":
    unittest.main()
