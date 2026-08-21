# Claude focused rerun: Karis and Quilez

## Run boundary

This run changed the provider from Grok subscription CLI to Claude subscription
CLI using the `sonnet` alias. The provider reported `claude-sonnet-5` as the
primary canonical model. The packet, prompts, personas, seed, two workers,
90-second timeout, job order, and three repeats per persona stayed fixed.

Because protocol v1 preregistered Grok, this is a focused provider comparison,
not a protocol-v1 replacement run.

## Response time

| Persona | Repeat 1 | Repeat 2 | Repeat 3 | Mean | Median |
|---|---:|---:|---:|---:|---:|
| Karis | 13.162 s | 14.276 s | 11.277 s | 12.905 s | 13.162 s |
| Quilez | 12.450 s | 13.153 s | 18.153 s | 14.585 s | 13.153 s |

Overall mean was 13.745 seconds, with a range of 11.277 to 18.153 seconds.
All six calls completed before the 90-second timeout.

The preceding Grok focused rerun produced one finding and five timeouts, with
an observed mean call duration of 88.360 seconds. Timed-out calls are censored
at 90 seconds, so their unknown completion time cannot be compared directly.

## Quality result

| Persona | Findings | Timeouts | Non-imperative | Complete | Strength 2 | Persona aligned |
|---|---:|---:|---:|---:|---:|---:|
| Karis | 3 | 0 | 3 | 3 | 3 | 1 |
| Quilez | 3 | 0 | 3 | 3 | 3 | 0 |

The automated mechanical gates pass, but the human persona gate fails. Five of
the six findings collapse toward register or occupancy cost, which is closer to
the Carmack lens. Only `karis-2` follows a hidden cost across unverified passes;
none of the Quilez outputs names the procedural-to-lookup representation shift.

## Supported conclusion

For this six-call sample, Claude was materially more reliable and faster at
returning schema-valid findings than Grok. It did not preserve the intended
Karis-versus-Quilez distinction, so transport success did not produce persona
success. Neither persona reaches the frozen requirement of at least two aligned
outputs.

This run cannot establish whether the difference comes from the provider model,
the Claude CLI prompt wrapper or caching, or random sampling.
