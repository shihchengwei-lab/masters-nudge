"""Invalid output raises a fault; it cannot become silence."""
import json
from .contracts import (Evidence, Feedback, EVIDENCE_EXCERPT_MAX_CHARS,
                        FEEDBACK_MAX_CHARS, PREFER_MAX_CHARS, SOURCES, ToolFault)


def parse_feedback(raw: str) -> Feedback | None:
    try:
        value = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise ToolFault("output", "Provider 未回傳 JSON") from exc
    if not isinstance(value, dict) or set(value) != {"feedback"}:
        raise ToolFault("output", "必須只回傳 feedback 欄位")
    item = value["feedback"]
    if item is None:
        return None
    if not isinstance(item, dict) or set(item) != {"criterion", "evidence", "observed", "violates", "prefer"}:
        raise ToolFault("output", "反饋欄位不符合契約")
    if type(item["criterion"]) is not int or not 1 <= item["criterion"] <= 6:
        raise ToolFault("output", "criterion 必須是 1 到 6")
    for key in ("observed", "violates", "prefer"):
        if not isinstance(item[key], str) or not item[key].strip():
            raise ToolFault("output", f"{key} 必須是非空文字")
        limit = PREFER_MAX_CHARS if key == "prefer" else 30
        if len(item[key]) > limit:
            raise ToolFault("output", f"{key} 超過 {limit} 字")
    refs = item["evidence"]
    if not isinstance(refs, list) or not 1 <= len(refs) <= 2:
        raise ToolFault("output", "必須提供一至兩筆引文")
    evidence = []
    for ref in refs:
        if not isinstance(ref, dict) or set(ref) != {"source", "location", "excerpt"}:
            raise ToolFault("output", "引文欄位不符合契約")
        if not all(isinstance(v, str) and v.strip() for v in ref.values()):
            raise ToolFault("output", "引文欄位不能為空")
        if ref["source"] not in SOURCES or len(ref["excerpt"]) > EVIDENCE_EXCERPT_MAX_CHARS:
            raise ToolFault("output", "引文來源或長度不符合契約")
        evidence.append(Evidence(**ref))
    feedback = Feedback(item["criterion"], tuple(evidence), item["observed"], item["violates"], item["prefer"])
    if len(feedback.message) > FEEDBACK_MAX_CHARS:
        raise ToolFault("output", f"反饋超過 {FEEDBACK_MAX_CHARS} 字")
    return feedback
