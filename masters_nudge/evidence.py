"""Pack known facts; the Provider chooses relevant repository structure."""
from dataclasses import replace
from .contracts import (
    MATERIAL_MAX_CHARS, MaterialPacket, SessionRef, ToolCompleted, ToolFault,
    find_git_root, json_text, material_lines,
)


def value_lines(source: str, path: str, value: object):
    """Keep returned text verbatim instead of hiding it behind JSON escapes."""
    if isinstance(value, str):
        return material_lines(source, path, value)
    if isinstance(value, dict) and value:
        lines = []
        for key, item in value.items():
            child = f"{path}/{key}"
            lines.extend(material_lines(source, child, item if isinstance(item, str) else json_text(item)))
        return tuple(lines)
    return material_lines(source, path, json_text(value))


def build_packet(session: SessionRef, task: dict, events: tuple[ToolCompleted, ...]) -> MaterialPacket:
    lines = []
    lines.extend(material_lines("task_contract", "task/original", task["goal"]))
    lines.extend(material_lines("task_contract", "task/latest", task["request"]))
    for event in events:
        if event.modification is not None:
            lines.extend(material_lines("batch_change", f"tool/{event.tool_use_id}/input", event.modification))
        lines.extend(material_lines("tool_result", f"tool/{event.tool_use_id}/name", event.tool_name))
        if event.modification is None:
            lines.extend(value_lines("tool_result", f"tool/{event.tool_use_id}/input", event.tool_input))
        lines.extend(value_lines("tool_result", f"tool/{event.tool_use_id}/output", event.tool_response))
    packet = MaterialPacket(tuple(lines), find_git_root(session.cwd), session.transcript_path)
    try:
        return fit_packet(packet)
    except ToolFault as exc:
        if exc.kind != "input_size":
            raise
        # Only an explicit successful exit permits dropping verbose output.
        # Arbitrary text is not classified as success by keyword matching.
        compressed_paths = {f"tool/{event.tool_use_id}/output": event.tool_response
                            for event in events if isinstance(event.tool_response, dict)
                            and type(event.tool_response.get("exit_code")) is int
                            and event.tool_response["exit_code"] == 0}
        kept = [line for line in lines if not any(
            line.path == path or line.path.startswith(path + "/") for path in compressed_paths)]
        for path in compressed_paths:
            kept.extend(material_lines("tool_result", f"{path}/summary", '{"exit_code":0,"output_omitted":true}'))
        return fit_packet(replace(packet, lines=tuple(kept)))


def fit_packet(packet: MaterialPacket) -> MaterialPacket:
    if packet.material_chars <= MATERIAL_MAX_CHARS:
        return packet
    packet = replace(packet, lines=tuple(line for line in packet.lines if line.source != "before_structure"))
    if packet.material_chars <= MATERIAL_MAX_CHARS:
        return packet
    # Generic result text does not identify dispensable success output.
    # Oversized mandatory data is a fault, never silent truncation.
    raise ToolFault("input_size", "材料超過上限，無法保留必要原文")


def verify_evidence(feedback, materials):
    for reference in feedback.evidence:
        candidates = (line for line in materials
                      if line.source == reference.source and line.location == reference.location)
        if not any(reference.excerpt in line.text for line in candidates):
            raise ToolFault("evidence", f"引文不在本次材料的指定位置：{reference.location}")
