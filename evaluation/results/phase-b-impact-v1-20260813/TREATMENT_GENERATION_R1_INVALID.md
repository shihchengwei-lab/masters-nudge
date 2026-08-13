# Treatment generation R1 — infrastructure invalid

All six reviewer calls were submitted, but the harness attempted to serialize a nonexistent `ReviewRoute.specialist_override` attribute after generation. The real field is `override_lens`. No output file was written and no first-batch Nudge was inspected, selected, or reused.

The field was corrected, a regression test was added, and the complete six-task generation batch is rerun as R2. This is not a selective retry.
