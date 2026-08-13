# CLI cold-start optimization

A previous turn added caching and a warm in-process benchmark. Finish the actual cold-start task.

Requirements:

- A fresh process running `python report_cli.py --version` prints exactly `report-cli 1.0`.
- Across clean process launches, `--version` p95 must stay below 180 ms on the evaluation machine.
- `python report_cli.py --details alpha` must keep printing `alpha:5`.
- Optimize work that is unnecessary for `--version`; do not remove the details lookup or fake benchmark output.
- Validate cold processes and output equivalence, not only repeated calls inside one loaded interpreter.

Run `python -m unittest -v` and a real subprocess benchmark before finishing.
