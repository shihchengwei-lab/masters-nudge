from __future__ import annotations

import json
import socket
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.request import ProxyHandler

from masters_nudge import local_ollama, providers


HERE = Path(__file__).resolve().parents[2]
SCHEMA = HERE / "reaction-schema.json"


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, _format, *_args):
        return None

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def _handle(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        payload = json.loads(raw.decode("utf-8")) if raw else None
        self.server.requests.append((self.command, self.path, payload))
        route = self.server.routes.get(self.path, (404, {"error": "missing"}, {}))
        if callable(route):
            route = route(payload)
        status, body, headers = route
        encoded = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class FakeOllama:
    def __init__(self, routes: dict):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.server.routes = routes
        self.server.requests = []
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        host, port = self.server.server_address
        self.url = f"http://{host}:{port}"
        return self

    def __exit__(self, *_args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def ready_routes(chat: dict | None = None) -> dict:
    routes = {
        "/api/status": (200, {"cloud": {"disabled": True, "source": "env"}}, {}),
        "/api/show": (
            200,
            {"capabilities": ["completion"], "details": {"format": "gguf"}},
            {},
        ),
    }
    if chat is not None:
        routes["/api/chat"] = (200, chat, {})
    return routes


class LocalUrlTests(unittest.TestCase):
    def test_accepts_only_plain_loopback_http_urls(self):
        self.assertEqual(
            local_ollama.normalize_loopback_url("http://localhost:11434/"),
            "http://localhost:11434",
        )
        self.assertEqual(
            local_ollama.normalize_loopback_url("http://[::1]:11434"),
            "http://[::1]:11434",
        )
        self.assertEqual(
            local_ollama.normalize_loopback_url("http://127.0.0.2:11434"),
            "http://127.0.0.2:11434",
        )
        rejected = (
            "https://127.0.0.1:11434",
            "http://192.168.1.2:11434",
            "http://example.com:11434",
            "http://user:pass@127.0.0.1:11434",
            "http://127.0.0.1:11434/api",
            "http://127.0.0.1:11434?remote=1",
            "http://127.0.0.1:11434/#fragment",
        )
        for value in rejected:
            with self.subTest(value=value), self.assertRaises(ValueError):
                local_ollama.normalize_loopback_url(value)

    def test_transport_disables_environment_proxies(self):
        opener = local_ollama._default_opener()
        proxy_handlers = [
            handler for handler in opener.handlers if isinstance(handler, ProxyHandler)
        ]
        self.assertEqual(proxy_handlers, [])

    def test_model_name_is_required_and_cloud_tags_are_rejected(self):
        with self.assertRaises(ValueError):
            local_ollama.validate_model_name("  ")
        self.assertTrue(local_ollama.is_explicit_cloud_model("qwen3.5:cloud"))
        self.assertTrue(
            local_ollama.is_explicit_cloud_model("gpt-oss:120b-cloud")
        )
        self.assertFalse(local_ollama.is_explicit_cloud_model("my-local-model"))
        self.assertFalse(local_ollama.is_explicit_cloud_model("mycloud"))


class LocalInspectionTests(unittest.TestCase):
    def test_metadata_probe_confirms_cloud_disabled_local_model_without_chat(self):
        with FakeOllama(ready_routes()) as fake:
            result = local_ollama.inspect_local_ollama(fake.url, "private-model")

        self.assertTrue(result["ready"])
        self.assertTrue(result["cloud_disabled"])
        self.assertTrue(result["model_local"])
        self.assertEqual(
            [path for _method, path, _payload in fake.server.requests],
            ["/api/status", "/api/show"],
        )
        self.assertEqual(
            fake.server.requests[-1][2],
            {"model": "private-model", "verbose": False},
        )

    def test_cloud_enabled_server_fails_before_model_or_chat(self):
        routes = ready_routes()
        routes["/api/status"] = (200, {"cloud": {"disabled": False}}, {})
        with FakeOllama(routes) as fake:
            result = local_ollama.inspect_local_ollama(fake.url, "private-model")

        self.assertFalse(result["ready"])
        self.assertIn("not disabled", result["error"])
        self.assertEqual(len(fake.server.requests), 1)

    def test_remote_model_metadata_fails_closed(self):
        routes = ready_routes()
        routes["/api/show"] = (
            200,
            {"capabilities": ["completion"], "remote_host": "https://ollama.com"},
            {},
        )
        with FakeOllama(routes) as fake:
            result = local_ollama.inspect_local_ollama(fake.url, "aliased-model")

        self.assertFalse(result["ready"])
        self.assertTrue(result["cloud_disabled"])
        self.assertFalse(result["model_local"])

    def test_missing_status_endpoint_and_redirect_both_fail_closed(self):
        with FakeOllama({}) as missing:
            result = local_ollama.inspect_local_ollama(missing.url, "model")
        self.assertFalse(result["ready"])
        self.assertIn("HTTP 404", result["error"])

        redirect = {
            "/api/status": (
                302,
                {},
                {"Location": "http://example.com/api/status"},
            )
        }
        with FakeOllama(redirect) as fake:
            result = local_ollama.inspect_local_ollama(fake.url, "model")
        self.assertFalse(result["ready"])
        self.assertIn("HTTP 302", result["error"])

    def test_timeout_and_oversized_metadata_fail_closed(self):
        class TimeoutOpener:
            def open(self, *_args, **_kwargs):
                raise TimeoutError("slow")

        timed_out = local_ollama.inspect_local_ollama(
            "http://127.0.0.1:11434",
            "model",
            opener_factory=lambda: TimeoutOpener(),
        )
        self.assertFalse(timed_out["ready"])
        self.assertIn("timed out", timed_out["error"])
        self.assertEqual(timed_out["error_kind"], "timeout")

        oversized = b"{" + b" " * local_ollama.MAX_HTTP_RESPONSE_BYTES + b"}"
        routes = {"/api/status": (200, oversized, {})}
        with FakeOllama(routes) as fake:
            result = local_ollama.inspect_local_ollama(fake.url, "model")
        self.assertFalse(result["ready"])
        self.assertIn("too large", result["error"])


class LocalCallTests(unittest.TestCase):
    def test_timeout_is_machine_readable(self):
        class TimeoutOpener:
            def open(self, *_args, **_kwargs):
                raise socket.timeout("slow")

        result = local_ollama.call_local_ollama_result(
            "prompt",
            "packet",
            "model",
            schema_path=SCHEMA,
            timeout_sec=5,
            opener_factory=lambda: TimeoutOpener(),
        )

        self.assertEqual(result["error_kind"], "timeout")

    def test_invalid_chat_output_is_machine_readable(self):
        chat = {
            "done": True,
            "message": {"content": json.dumps({"wrong": "shape"})},
        }
        with FakeOllama(ready_routes(chat)) as fake:
            result = local_ollama.call_local_ollama_result(
                "prompt",
                "packet",
                "model",
                schema_path=SCHEMA,
                timeout_sec=5,
                base_url=fake.url,
            )

        self.assertEqual(result["error_kind"], "invalid_output")

    def test_structured_finding_and_usage_use_native_ollama_chat(self):
        chat = {
            "done": True,
            "message": {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "status": "finding",
                        "effective_lens": "linus",
                        "finding": "固定可觀察行為；別替內部做法蓋章，因為契約才是邊界。",
                    },
                    ensure_ascii=False,
                ),
            },
            "prompt_eval_count": 123,
            "eval_count": 17,
        }
        with FakeOllama(ready_routes(chat)) as fake:
            result = local_ollama.call_local_ollama_result(
                "system prompt",
                "evidence packet",
                "private-model",
                schema_path=SCHEMA,
                timeout_sec=5,
                base_url=fake.url,
            )

        self.assertEqual(result["status"], "finding")
        self.assertEqual(result["usage"]["input_tokens"], 123)
        self.assertEqual(result["usage"]["output_tokens"], 17)
        self.assertEqual(result["usage"]["total_tokens"], 140)
        chat_request = fake.server.requests[-1]
        self.assertEqual(chat_request[1], "/api/chat")
        payload = chat_request[2]
        self.assertFalse(payload["stream"])
        self.assertFalse(payload["think"])
        self.assertEqual(payload["options"]["temperature"], 0)
        self.assertEqual(payload["format"]["properties"]["finding"]["maxLength"], 52)
        self.assertNotIn("pattern", payload["format"]["properties"]["finding"])
        self.assertIn("evidence packet", payload["messages"][1]["content"])
        self.assertIn("JSON schema", payload["messages"][0]["content"])

    def test_schema_violation_remains_an_error(self):
        chat = {
            "done": True,
            "message": {"content": '{"status":"finding","finding":"'},
        }
        errors = []
        with FakeOllama(ready_routes(chat)) as fake:
            result = local_ollama.call_local_ollama_result(
                "prompt",
                "packet",
                "model",
                schema_path=SCHEMA,
                timeout_sec=5,
                base_url=fake.url,
                log_error=errors.append,
            )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["finding"], "")

    def test_incomplete_chat_response_is_an_error(self):
        chat = {
            "done": False,
            "message": {"content": '{"status":"no_finding","effective_lens":"none","finding":""}'},
        }
        errors = []
        with FakeOllama(ready_routes(chat)) as fake:
            result = local_ollama.call_local_ollama_result(
                "prompt",
                "packet",
                "model",
                schema_path=SCHEMA,
                timeout_sec=5,
                base_url=fake.url,
                log_error=errors.append,
            )

        self.assertEqual(result["status"], "error")
        self.assertTrue(any("incomplete" in item for item in errors))

    def test_remote_response_is_rejected_without_cloud_fallback(self):
        chat = {
            "done": True,
            "remote_model": "remote",
            "remote_host": "https://ollama.com",
            "message": {"content": '{"status":"no_finding","effective_lens":"none","finding":""}'},
        }
        with FakeOllama(ready_routes(chat)) as fake:
            with patch.object(providers, "call_codex_result") as codex, patch.object(
                providers, "call_claude_result"
            ) as claude:
                result = providers.dispatch_call_result(
                    "ollama-local",
                    "prompt",
                    "packet",
                    "model",
                    schema_path=SCHEMA,
                    timeout_sec=5,
                    ollama_url=fake.url,
                )

        self.assertEqual(result["status"], "error")
        codex.assert_not_called()
        claude.assert_not_called()

    def test_invalid_endpoint_never_calls_a_cloud_provider(self):
        with patch.object(providers, "call_codex_result") as codex, patch.object(
            providers, "call_claude_result"
        ) as claude:
            result = providers.dispatch_call_result(
                "ollama-local",
                "prompt",
                "packet",
                "model",
                schema_path=SCHEMA,
                timeout_sec=5,
                ollama_url="https://ollama.com",
            )

        self.assertEqual(result["status"], "error")
        codex.assert_not_called()
        claude.assert_not_called()


if __name__ == "__main__":
    unittest.main()
