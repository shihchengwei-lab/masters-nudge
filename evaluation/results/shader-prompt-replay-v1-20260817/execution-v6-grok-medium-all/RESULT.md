# Grok medium full Shader persona run

## Run boundary

This run used the Grok subscription CLI with `grok-4.6-build` and explicit
`--reasoning-effort medium`. It kept the frozen checkpoint packet, six personas,
three repeats per persona, seed `20260817`, two workers, and 90-second timeout.

Protocol v1 preregistered the provider model default rather than medium effort.
This is therefore a full effort experiment, not a replacement for the original
protocol-v1 run.

## Transport and response time

Seventeen of 18 calls produced schema-valid findings. No call timed out. One
Karis response returned in 3.276 seconds but was rejected because its 64-character
finding exceeded the frozen 52-character cap.

| Persona | Valid findings | Errors | Mean | Median | Observed p95 | Range |
|---|---:|---:|---:|---:|---:|---:|
| Akenine-Möller | 3 | 0 | 35.273 s | 48.645 s | 53.060 s | 4.114–53.060 s |
| Carmack | 3 | 0 | 49.479 s | 51.500 s | 54.074 s | 42.864–54.074 s |
| Karis | 2 | 1 | 27.715 s | 3.276 s | 76.811 s | 3.057–76.811 s |
| Lottes | 3 | 0 | 67.208 s | 63.084 s | 75.951 s | 62.590–75.951 s |
| Quilez | 3 | 0 | 38.692 s | 52.739 s | 59.842 s | 3.495–59.842 s |
| Tatarchuk | 3 | 0 | 63.770 s | 68.021 s | 73.706 s | 49.584–73.706 s |

Overall mean was 47.023 seconds, median was 52.900 seconds, and nearest-rank
observed p95 was 76.811 seconds, with a range of 3.057 to 76.811 seconds.
Attempt p95 includes every transport outcome; successful p95 excludes the one
schema error and is also 76.811 seconds. With only three calls per persona,
each persona p95 equals its slowest observation and is not a population
tail-latency estimate. Reasoning output ranged from 0 tokens on four calls to
4,985 tokens, so medium effort still did not imply a stable reasoning or latency
budget.

## Human quality result

The percentages below use the 17 schema-valid findings. Timeout and schema
reliability are reported separately, as required by the frozen protocol.

| Persona | Valid | Non-imperative | Complete | Strength 2 | Persona aligned |
|---|---:|---:|---:|---:|---:|
| Akenine-Möller | 3 | 3 | 3 | 3 | 2 |
| Carmack | 3 | 3 | 3 | 3 | 3 |
| Karis | 2 | 2 | 2 | 2 | 2 |
| Lottes | 3 | 3 | 3 | 3 | 3 |
| Quilez | 3 | 3 | 3 | 3 | 2 |
| Tatarchuk | 3 | 3 | 3 | 3 | 3 |
| **Total** | **17** | **17** | **17** | **17** | **15** |

Two findings were deliberately not counted as persona-aligned. `akenine_moller-3`
followed register and bandwidth cost transfer rather than visibility rejection.
`quilez-3` named convergence but did not identify the representation or invariant
whose behavior changed. Both remain strength-2 blind spots for the packet.

The invalid `karis-1` candidate was semantically Karis-aligned, but it is not a
finding under the frozen schema and is excluded from every quality denominator.

## Frozen thresholds

| Criterion | Target | Result | Status |
|---|---:|---:|---|
| Observation rather than instruction | at least 80% | 17/17, 100% | Pass |
| Complete finding | at least 90% | 17/17, 100% | Pass |
| Persona alignment | at least 2 per persona | 2–3 per persona | Pass |
| Strength-2 blind spot | at least 50% | 17/17, 100% | Pass |
| Unique representative lines | 6 personas | 6 semantically distinct lines available | Pass |

Representative attention remained distinguishable: visibility-stage work for
Akenine-Möller, machine-work relocation for Carmack, cross-pass material identity
for Karis, temporal signal error for Lottes, representation-versus-hard-problem
for Quilez, and platform-local evidence for Tatarchuk.

## Supported conclusion

On this frozen packet, the complete Grok-medium run passes all five prompt-quality
and persona-differentiation thresholds. The main limitation is operational:
schema-valid delivery was 17/18 rather than perfect, and latency remained highly
variable.

This result does not show that medium effort caused the improvement, that it will
repeat on other Shader stages or packets, or that these findings alter the main
model's later token choices. Those require separate controlled runs and downstream
interaction evidence.
