import csv
import io
import json


def export_csv(rows, delimiter=","):
    if len(delimiter) != 1:
        raise ValueError("delimiter must be one character")
    if not rows:
        return ""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=list(rows[0]),
        delimiter=delimiter,
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def _normalize_for_export(value):
    if isinstance(value, dict):
        return {key: _normalize_for_export(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_for_export(item) for item in value]
    return "" if value is None else value


def export_json(rows):
    normalized = _normalize_for_export(rows)
    return json.dumps(normalized, ensure_ascii=False, indent=2)
