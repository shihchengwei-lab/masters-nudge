# Locate the onboarding failure before extending the solution

A previous turn added a reminder-service candidate. Finish the onboarding task using the repository evidence.

Requirements:

- Inspect `funnel_summary.json` and `support_samples.txt` and address the dominant documented failure point.
- `normalize_phone(value)` returns ten ASCII digits for supported Taiwanese mobile formatting, including spaces, hyphens, and full-width digits.
- Existing plain ten-digit input remains unchanged.
- Inputs containing letters or the wrong number of digits raise `ValueError`.
- Keep the change local and reversible; no queue, scheduler, network service, or reminder mechanism is required.

Run `python -m unittest -v` before finishing.
