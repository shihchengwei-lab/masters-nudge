import csv
import io
import json


def export_csv(rows, delimiter=","):
    if not isinstance(delimiter, str) or len(delimiter) != 1:
        raise ValueError("delimiter must be one character")
    output = io.StringIO()
    fieldnames = list(rows[0]) if rows else []
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        delimiter=delimiter,
        lineterminator="\n",
    )
    if fieldnames:
        writer.writeheader()
        writer.writerows(rows)
    return output.getvalue()


def export_json(rows):
    return json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + "\n"
