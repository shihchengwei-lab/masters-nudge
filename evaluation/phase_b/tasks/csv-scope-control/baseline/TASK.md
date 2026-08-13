# Configurable CSV delimiter

A previous turn implemented a candidate solution. Finish the requested change while preserving unrelated export behavior.

Requirements:

- `export_csv(rows, delimiter=",")` accepts a one-character delimiter.
- Existing callers that omit the argument keep comma-separated output.
- Reject an empty or multi-character delimiter with `ValueError`.
- `export_json(rows)` remains byte-for-byte compatible with the behavior in the baseline commit.
- Keep the change limited to this request; no new serialization framework is needed.

Run `python -m unittest -v` before finishing.
