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


def export_json(rows):
    return json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
