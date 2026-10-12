"""Explicit, bounded Actor-supplied evidence; never infer intent from commands."""
from dataclasses import asdict, dataclass, replace
import hashlib
import json

from .contracts import (MATERIAL_MAX_CHARS, MaterialPacket, ToolCompleted, ToolFault,
                        find_git_root, json_text, material_lines)
from .evidence import changed_file_material, file_origin_material, value_lines

MAX_INPUT_BYTES = 65_536
MAX_EVIDENCE_RESULTS = 8


def _text(value, name, limit):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ToolFault("input", f"{name} 必須是 1–{limit} 字的非空文字")
    return value


def _canonical(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ToolFault("input", "diagnostic evidence 必須是有限 JSON 值") from exc


@dataclass(frozen=True)
class DiagnosticBatch:
    cwd: str
    task_request: str
    batch_id: str
    reason: str
    progress: str
    events: tuple[ToolCompleted, ...]
    fingerprint: str

    @classmethod
    def parse(cls, value):
        keys = {"cwd", "task_request", "batch_id", "reason", "progress", "evidence"}
        if not isinstance(value, dict) or set(value) != keys:
            raise ToolFault("input", "diagnostic checkpoint 欄位不符合契約")
        if len(_canonical(value).encode("utf-8")) > MAX_INPUT_BYTES:
            raise ToolFault("input_size", "diagnostic checkpoint 超過 64 KiB")
        cwd = _text(value["cwd"], "cwd", 4096)
        request = _text(value["task_request"], "task_request", MATERIAL_MAX_CHARS)
        batch_id = _text(value["batch_id"], "batch_id", 128)
        reason = _text(value["reason"], "reason", 1000)
        progress = _text(value["progress"], "progress", 2000)
        evidence = value["evidence"]
        if not isinstance(evidence, list) or not 1 <= len(evidence) <= MAX_EVIDENCE_RESULTS:
            raise ToolFault("input", "diagnostic evidence 必須包含 1–8 筆結果")
        events, seen = [], set()
        for item in evidence:
            if not isinstance(item, dict) or set(item) != {"tool_use_id", "tool_name", "tool_input", "tool_response"}:
                raise ToolFault("input", "diagnostic tool result 欄位不符合契約")
            identity = _text(item["tool_use_id"], "tool_use_id", 128)
            _text(item["tool_name"], "tool_name", 128)
            if identity in seen:
                raise ToolFault("input", "同一批 tool_use_id 不可重複")
            seen.add(identity)
            response = item["tool_response"]
            if (not isinstance(response, (str, dict, list)) or not response
                    or isinstance(response, str) and not response.strip()):
                raise ToolFault("input", "diagnostic tool_response 不可為空")
            events.append(ToolCompleted(**item))
        # IDs, wrapper rationale and record ordering cannot disguise an identical batch.
        originals = sorted({_canonical({k: v for k, v in asdict(event).items() if k != "tool_use_id"})
                            for event in events})
        fingerprint = hashlib.sha256(_canonical(originals).encode("utf-8")).hexdigest()
        return cls(cwd, request, batch_id, reason, progress, tuple(events), fingerprint)

    @property
    def trigger(self):
        return {"kind": "explicit_diagnostic_checkpoint", "profile": "performance",
                "evidence_origin": "actor_supplied", "batch_id": self.batch_id,
                "reason": self.reason, "progress": self.progress,
                "evidence_sha256": self.fingerprint}


def build_diagnostic_packet(session, task, batch):
    """Do not treat arbitrary diagnostic input as a patch or compress successful measurements."""
    workspace = find_git_root(session.cwd)
    lines = []
    if task["goal"] != task["request"]:
        lines.extend(material_lines("task_contract", "task/original", task["goal"]))
    lines.extend(material_lines("task_contract", "task/latest", task["request"]))
    lines.extend(material_lines("tool_result", "diagnostic/trigger", json_text(batch.trigger)))
    patches = []
    for event in batch.events:
        anchor = f"tool/{event.tool_use_id}"
        lines.extend(material_lines("tool_result", f"{anchor}/name", event.tool_name))
        lines.extend(value_lines("tool_result", f"{anchor}/input", event.tool_input))
        lines.extend(value_lines("tool_result", f"{anchor}/output", event.tool_response))
        if event.tool_name == "apply_patch" and event.modification is not None:
            patches.append(event)
            lines.extend(material_lines("batch_change", f"{anchor}/input", event.modification))
    for material in file_origin_material(session, task, tuple(patches), workspace):
        lines.extend(material)
    packet = MaterialPacket(tuple(lines), workspace, previous_nudges=tuple(task.get("previous_nudges", ())))
    if packet.material_chars > MATERIAL_MAX_CHARS:
        raise ToolFault("input_size", "diagnostic 完整材料超過 20,000 字；請縮小有界量測批次，不可截斷原文")
    for event in patches:
        for material in changed_file_material(event.modification, session.cwd, workspace):
            candidate = replace(packet, lines=packet.lines + material)
            if candidate.material_chars <= MATERIAL_MAX_CHARS:
                packet = candidate
    return packet
