# Deterministic organization roles

A previous turn implemented a candidate fix. Finish it without changing the public API in `roles.py`.

Requirements:

- A successful write through either `set_gateway_role` or `set_billing_role` is immediately visible through both readers.
- Across interleaved writes, the most recent successful write wins.
- Invalid roles raise `ValueError` without changing any visible state.
- Keep `reconcile_roles()` for compatibility, but correctness must not depend on running it.
- Do not add timers, workers, persistence, or network dependencies.

Run `python -m unittest -v` before finishing.
