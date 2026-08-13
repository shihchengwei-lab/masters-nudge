import csv
import io
import json


def export_csv(rows):
    if not rows:
        return ""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def export_json(rows):
    return json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
