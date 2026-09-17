import io
import queue
from pathlib import Path
import sqlite3
import tempfile
import unittest

from tools.verify_spec_app_server import RpcClient, hook_outputs, read_journal, test_hook_state


class AppServerDriverTests(unittest.TestCase):
    def test_journal_observation_closes_file_and_does_not_create_it(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            self.assertEqual(read_journal(directory)["attempts"], [])
            self.assertEqual(list(directory.iterdir()), [])
            path = directory / "feedback.sqlite3"
            db = sqlite3.connect(path)
            db.executescript("CREATE TABLE rounds(id); CREATE TABLE batches(id); CREATE TABLE attempts(id,detail);")
            db.close()
            self.assertEqual(read_journal(directory)["attempts"], [])
            path.unlink()  # Windows refuses this if the reader still owns a handle.

    def test_only_reviewed_packaged_hooks_receive_temporary_trust(self):
        hooks = [{"key": name, "eventName": event, "source": "sessionFlags", "command": "reviewed",
                  "currentHash": "sha256:exact", "isManaged": False}
                 for name, event in (("a", "postToolBatch"), ("b", "userPromptSubmit"))]
        hooks.append({"key": "unrelated", "source": "user", "isManaged": False})
        state = test_hook_state({"data": [{"hooks": hooks}]}, {"reviewed"})
        self.assertEqual(state["a"], {"enabled": True, "trusted_hash": "sha256:exact"})
        self.assertEqual(state["unrelated"], {"enabled": False})
        with self.assertRaises(RuntimeError):
            test_hook_state({"data": [{"hooks": hooks}]}, {"different command"})

    def test_request_retains_interleaved_notifications(self):
        stream = io.StringIO()
        client = RpcClient(stream, queue.Queue())
        notification = {"method": "hook/completed", "params": {"run": {"entries": []}}}
        client.incoming.put(notification)
        client.incoming.put({"id": 1, "result": {"ready": True}})
        self.assertEqual(client.request("initialize", {}), {"ready": True})
        self.assertEqual(client.events, [notification])
        self.assertIn('"method": "initialize"', stream.getvalue())

    def test_server_error_and_disconnect_cannot_look_like_completion(self):
        for item in ({"id": 1, "error": {"message": "failed"}}, None):
            client = RpcClient(io.StringIO(), queue.Queue())
            client.incoming.put(item)
            with self.assertRaises(RuntimeError):
                client.request("thread/start", {})

    def test_hook_text_keeps_warning_separate_from_actor_context(self):
        event = {"method": "hook/completed", "params": {"turnId": "t", "run": {
            "eventName": "postToolBatch", "entries": [{"kind": "warning", "text": "本輪反饋未執行"}]}}}
        self.assertEqual(hook_outputs([event], kind="warning"), ["本輪反饋未執行"])
        self.assertEqual(hook_outputs([event], kind="context"), [])
