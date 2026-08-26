"""Strict loopback-only Ollama transport for private reviewer calls."""

from __future__ import annotations

import ipaddress
import json
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    ProxyHandler,
    Request,
    build_opener,
)

from .provider_contract import call_result, parse_reaction_result


DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
MAX_HTTP_RESPONSE_BYTES = 1024 * 1024
MAX_MODEL_NAME_CHARS = 256


class LocalOllamaError(RuntimeError):
    """A sanitized local-provider failure safe to write to the error log."""


class LocalOllamaTimeout(LocalOllamaError):
    """The loopback Ollama server exceeded the configured deadline."""


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _default_opener():
    return build_opener(ProxyHandler({}), _RejectRedirects())


def validate_model_name(model: str) -> str:
    value = str(model or "").strip()
    if not value:
        raise ValueError("a local model name is required")
    if len(value) > MAX_MODEL_NAME_CHARS:
        raise ValueError("local model name is too long")
    if any(ord(char) < 32 for char in value):
        raise ValueError("local model name contains control characters")
    return value


def is_explicit_cloud_model(model: str) -> bool:
    value = str(model or "").strip().lower()
    tag = value.rsplit(":", 1)[-1]
    return tag == "cloud" or tag.endswith("-cloud")


def normalize_loopback_url(value: str) -> str:
    raw = str(value or "").strip()
    try:
        parsed = urlsplit(raw)
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"invalid Ollama URL: {exc}") from exc
    if parsed.scheme.lower() != "http":
        raise ValueError("Ollama URL must use http")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Ollama URL must not contain credentials")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("Ollama URL must not contain a path, query, or fragment")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("Ollama URL must contain a host")
    if host != "localhost":
        try:
            address = ipaddress.ip_address(host)
        except ValueError as exc:
            raise ValueError("Ollama URL must use a loopback host") from exc
        if not address.is_loopback:
            raise ValueError("Ollama URL must use a loopback host")
    rendered_host = f"[{host}]" if ":" in host else host
    return f"http://{rendered_host}{f':{port}' if port is not None else ''}"


def _request_json(
    base_url: str,
    path: str,
    *,
    timeout_sec: int,
    payload: dict | None = None,
    opener_factory: Callable = _default_opener,
) -> dict:
    body = None
    method = "GET"
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        method = "POST"
    request = Request(
        f"{base_url}{path}",
        data=body,
        method=method,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "masters-nudge/local-only",
        },
    )
    try:
        with opener_factory().open(request, timeout=timeout_sec) as response:
            raw = response.read(MAX_HTTP_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        try:
            raise LocalOllamaError(
                f"Ollama {path} returned HTTP {exc.code}"
            ) from exc
        finally:
            exc.close()
    except (TimeoutError, URLError) as exc:
        reason = getattr(exc, "reason", None)
        if isinstance(exc, TimeoutError) or isinstance(reason, TimeoutError):
            raise LocalOllamaTimeout(f"Ollama {path} timed out") from exc
        raise LocalOllamaError(f"Ollama {path} is unavailable") from exc
    except OSError as exc:
        raise LocalOllamaError(f"Ollama {path} is unavailable") from exc
    if len(raw) > MAX_HTTP_RESPONSE_BYTES:
        raise LocalOllamaError(f"Ollama {path} response is too large")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise LocalOllamaError(f"Ollama {path} returned invalid JSON") from exc
    if not isinstance(result, dict):
        raise LocalOllamaError(f"Ollama {path} returned a non-object response")
    if result.get("error"):
        raise LocalOllamaError(f"Ollama {path} reported an error")
    return result


def inspect_local_ollama(
    base_url: str,
    model: str,
    *,
    timeout_sec: int = 3,
    opener_factory: Callable = _default_opener,
) -> dict:
    result = {
        "ready": False,
        "endpoint": str(base_url or ""),
        "endpoint_loopback": False,
        "server_ready": False,
        "cloud_disabled": False,
        "model_ready": False,
        "model_local": False,
        "error": "",
        "error_kind": "",
    }
    try:
        endpoint = normalize_loopback_url(base_url)
        selected_model = validate_model_name(model)
        result["endpoint"] = endpoint
        result["endpoint_loopback"] = True
        if is_explicit_cloud_model(selected_model):
            raise LocalOllamaError("cloud model names are not allowed")

        status = _request_json(
            endpoint,
            "/api/status",
            timeout_sec=timeout_sec,
            opener_factory=opener_factory,
        )
        result["server_ready"] = True
        cloud = status.get("cloud")
        if not isinstance(cloud, dict) or cloud.get("disabled") is not True:
            raise LocalOllamaError("Ollama cloud features are not disabled")
        result["cloud_disabled"] = True

        show = _request_json(
            endpoint,
            "/api/show",
            timeout_sec=timeout_sec,
            payload={"model": selected_model, "verbose": False},
            opener_factory=opener_factory,
        )
        result["model_ready"] = True
        if show.get("remote_model") or show.get("remote_host"):
            raise LocalOllamaError("selected Ollama model is remote")
        capabilities = show.get("capabilities")
        if isinstance(capabilities, list) and capabilities:
            if "completion" not in capabilities:
                raise LocalOllamaError("selected Ollama model cannot complete text")
        result["model_local"] = True
        result["ready"] = True
    except (LocalOllamaError, ValueError) as exc:
        result["error"] = str(exc)
        result["error_kind"] = (
            "timeout" if isinstance(exc, LocalOllamaTimeout) else "not_found"
        )
    return result


def _usage_from_chat(response: dict) -> dict[str, int]:
    usage: dict[str, int] = {}
    prompt = response.get("prompt_eval_count")
    output = response.get("eval_count")
    if isinstance(prompt, (int, float)) and not isinstance(prompt, bool):
        usage["input_tokens"] = int(prompt)
    if isinstance(output, (int, float)) and not isinstance(output, bool):
        usage["output_tokens"] = int(output)
    if usage:
        usage["total_tokens"] = sum(usage.values())
    return usage


def call_local_ollama_result(
    system_prompt: str,
    review_input: str,
    model: str,
    *,
    schema_path: Path,
    timeout_sec: int,
    base_url: str = DEFAULT_OLLAMA_URL,
    log_error: Callable[[str], None] = lambda _message: None,
    opener_factory: Callable = _default_opener,
    parse_result: Callable[[str], dict] | None = None,
) -> dict:
    parser = parse_result or parse_reaction_result
    try:
        schema = json.loads(Path(schema_path).read_text(encoding="utf-8"))
        if not isinstance(schema, dict):
            raise ValueError("schema root is not an object")
    except (OSError, ValueError) as exc:
        log_error(f"reaction schema unavailable for ollama-local: {exc}")
        return call_result(error_kind="invalid_output")

    inspection = inspect_local_ollama(
        base_url,
        model,
        timeout_sec=min(timeout_sec, 3),
        opener_factory=opener_factory,
    )
    if not inspection["ready"]:
        log_error(f"ollama-local unavailable: {inspection['error']}")
        return call_result(
            error_kind=str(inspection.get("error_kind") or "not_found")
        )

    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    request_system = (
        f"{system_prompt}\n\n輸出必須符合這份 JSON schema：{schema_text}"
    )
    try:
        response = _request_json(
            inspection["endpoint"],
            "/api/chat",
            timeout_sec=timeout_sec,
            payload={
                "model": validate_model_name(model),
                "messages": [
                    {"role": "system", "content": request_system},
                    {"role": "user", "content": review_input},
                ],
                "stream": False,
                "think": False,
                "format": schema,
                "options": {"temperature": 0},
            },
            opener_factory=opener_factory,
        )
        if response.get("remote_model") or response.get("remote_host"):
            raise LocalOllamaError("Ollama returned a remote model response")
        if response.get("done") is not True:
            raise LocalOllamaError("Ollama returned an incomplete response")
        message = response.get("message")
        raw_output = message.get("content") if isinstance(message, dict) else None
        if not isinstance(raw_output, str):
            raise LocalOllamaError("Ollama response has no message content")
        parsed = parser(raw_output)
        if not isinstance(parsed, dict):
            raise LocalOllamaError("Ollama response parser returned an invalid result")
        parsed["usage"] = _usage_from_chat(response)
        if parsed.get("status") == "error":
            parsed["error_kind"] = "invalid_output"
        return parsed
    except (LocalOllamaError, ValueError) as exc:
        log_error(f"ollama-local call failed: {exc}")
        return call_result(
            error_kind=(
                "timeout" if isinstance(exc, LocalOllamaTimeout) else "invalid_output"
            )
        )
