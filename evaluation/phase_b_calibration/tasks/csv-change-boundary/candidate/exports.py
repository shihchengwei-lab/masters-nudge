import csv
import io
import json


def _normalize_scalar(value):
    return "" if value is None else value


def export_csv(rows, delimiter=","):
    if len(delimiter) != 1:
        raise ValueError("delimiter must be one character")
    normalized = [
        {key: _normalize_scalar(value) for key, value in row.items()}
        for row in rows
    ]
    output = io.StringIO()
    fieldnames = list(normalized[0]) if normalized else []
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        delimiter=delimiter,
        lineterminator="\n",
    )
    if fieldnames:
        writer.writeheader()
        writer.writerows(normalized)
    return output.getvalue()


def export_json(rows):
    normalized = [
        {key: _normalize_scalar(value) for key, value in row.items()}
        for row in rows
    ]
    return json.dumps(normalized, ensure_ascii=False, indent=2) + "\n"
