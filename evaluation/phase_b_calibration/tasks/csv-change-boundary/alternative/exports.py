import csv
import io
import json


def _prepare_rows(rows, *, for_csv):
    if not for_csv:
        return rows
    return [
        {key: "" if value is None else value for key, value in row.items()}
        for row in rows
    ]


def export_csv(rows, delimiter=","):
    if not isinstance(delimiter, str) or len(delimiter) != 1:
        raise ValueError("delimiter must be one character")
    prepared = _prepare_rows(rows, for_csv=True)
    output = io.StringIO()
    fieldnames = list(prepared[0]) if prepared else []
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=delimiter, lineterminator="\n")
    if fieldnames:
        writer.writeheader()
        writer.writerows(prepared)
    return output.getvalue()


def export_json(rows):
    return json.dumps(_prepare_rows(rows, for_csv=False), ensure_ascii=False, separators=(",", ":")) + "\n"
