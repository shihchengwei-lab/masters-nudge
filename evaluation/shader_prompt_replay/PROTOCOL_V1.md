# Shader prompt replay protocol v1

Frozen before provider calls on 2026-08-17.

## Question

With one identical in-progress Shader packet, do the six Shader personas produce
short observations rather than instructions, expose a packet-supported relation
that the agent has not named, and remain semantically distinguishable?

## Fixed run

- One checkpoint packet and six forced personas; the router is bypassed.
- Three repeats per persona: 18 Grok subscription CLI calls.
- Same base prompt, checkpoint prompt, schema, packet, timeout, and model default.
- Seed `20260817`, two workers, 90-second timeout per call.
- Provider raw finding is the quality evidence. Production sanitation is stored
  separately and cannot erase an imperative failure.
- No no-Nudge baseline. This run diagnoses the Shader prompt stack only.

## Automated diagnostics

- transport status and timeout count;
- nearest-rank observed p95 for all attempts and for successful responses;
- raw schema output, 52-character cap, and terminal punctuation;
- imperative-prefix and code-review-language flags;
- exact duplicates, persona-name leakage, and preregistered theme-term signal.

Imperative and theme matching are diagnostics, not semantic ground truth.

## Human rubric

Each successful raw finding receives four judgments:

1. observation rather than instruction;
2. complete proposition within 52 characters;
3. blind-spot strength: 0 repeats the packet, 1 names a hidden variable, 2 links
   packet evidence to a hidden cost or invariant;
4. alignment with the forced persona's expected attention.

The target is at least 80% non-imperative, 90% complete findings, at least two
aligned outputs per persona, at least 50% strength-2 blind spots, and six unique
representative lines. Timeout is reported separately from prompt-quality rates.

Latency p95 is descriptive rather than a pass gate. Attempt p95 includes
timeout wall time; successful p95 includes only `finding` and `no_finding`.
With three calls per persona, persona-level p95 equals the slowest observed
call and must not be presented as a population tail-latency estimate.
