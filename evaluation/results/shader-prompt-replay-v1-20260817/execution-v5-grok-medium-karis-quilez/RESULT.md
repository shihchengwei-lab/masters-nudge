# Grok medium focused rerun: Karis and Quilez

## Run boundary

This run used Grok subscription CLI with its default `grok-4.6` model and an
explicit `--reasoning-effort medium`. The packet, prompts, personas, seed, two
workers, 90-second timeout, job order, and three repeats per persona stayed
fixed.

Because protocol v1 preregistered Grok without a fixed effort, this is a focused
effort experiment rather than a protocol-v1 replacement run.

## Response time

| Persona | Repeat 1 | Repeat 2 | Repeat 3 | Mean | Median |
|---|---:|---:|---:|---:|---:|
| Karis | 65.163 s | 64.528 s | 57.175 s | 62.289 s | 64.528 s |
| Quilez | 64.179 s | 3.909 s | 47.006 s | 38.365 s | 47.006 s |

Overall mean was 50.327 seconds, with a range of 3.909 to 65.163 seconds. All
six calls completed before the 90-second timeout. Reasoning output ranged from
0 to 4,238 tokens, so medium effort did not produce a stable latency budget.

## Quality result

| Persona | Findings | Timeouts | Non-imperative | Complete | Strength 2 | Persona aligned |
|---|---:|---:|---:|---:|---:|---:|
| Karis | 3 | 0 | 3 | 3 | 3 | 3 |
| Quilez | 3 | 0 | 3 | 3 | 3 | 2 |

The automated mechanical gates pass, and human review finds that both personas
reach the requirement of at least two aligned outputs. Karis consistently
follows one material through Forward, DepthOnly, shadow, or static-image scope.
Two Quilez findings preserve the distinction between a shorter formula and work
moved into lookup, filtering, registers, or overlap. `quilez-2` is a strong blind
spot but drifts toward pass and motion coverage.

## Provider comparison

| Provider run | Findings | Timeouts | Karis aligned | Quilez aligned | Mean duration |
|---|---:|---:|---:|---:|---:|
| Grok model default effort | 1/6 | 5 | 0 | 1 | 88.360 s observed |
| Claude Sonnet | 6/6 | 0 | 1 | 0 | 13.745 s |
| GPT-5.6 Sol | 6/6 | 0 | 0 | 2 | 8.412 s |
| Grok medium | 6/6 | 0 | 3 | 2 | 50.327 s |

The original Grok timeout calls are censored at 90 seconds, and its single
finding was Quilez-aligned. The comparison is descriptive rather than a causal
estimate.

## Supported conclusion

For this six-call sample, explicit medium effort produced the strongest persona
alignment and was the only tested setting where both selected personas crossed
the alignment threshold. It was slower and much more variable than Claude or
GPT-5.6 Sol, but the resulting findings carried more of the intended observation
taste.

This run does not establish that medium effort alone caused the improvement;
provider sampling and temporal service conditions were not controlled.
