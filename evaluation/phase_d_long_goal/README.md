# Phase D — long-goal workflow evaluation

This suite replays delivery and strategy states that short code-review fixtures miss:

- delayed, failed, and expired Nudge delivery;
- repeated test/verifier command families;
- another 80 lines of working-tree growth after the previous strategy review;
- repeated failure families;
- `update_goal complete|blocked` transition ambiguity;
- healthy progress where a strategy review may run but should return no finding.

Run `python -m unittest test_phase_d_long_goal.py`. The deterministic tests verify
triggering, routing, deduplication, and delivery receipts; reviewer quality remains a
separate model evaluation rather than a claim made by these fixtures.
