# GPT-5.6 Sol focused rerun: Karis and Quilez

## Run boundary

This run used Codex subscription CLI with `gpt-5.6-sol`. The packet, prompts,
personas, seed, two workers, 90-second timeout, job order, and three repeats per
persona stayed fixed. No explicit reasoning-effort override was supplied.

Because protocol v1 preregistered Grok, this is a focused provider comparison,
not a protocol-v1 replacement run.

## Response time

| Persona | Repeat 1 | Repeat 2 | Repeat 3 | Mean | Median |
|---|---:|---:|---:|---:|---:|
| Karis | 7.922 s | 8.147 s | 8.453 s | 8.174 s | 8.147 s |
| Quilez | 8.255 s | 8.596 s | 9.098 s | 8.650 s | 8.596 s |

Overall mean was 8.412 seconds, with a range of 7.922 to 9.098 seconds. All six
calls completed before the 90-second timeout.

| Provider run | Findings | Timeouts | Observed mean call duration |
|---|---:|---:|---:|
| Grok | 1/6 | 5 | 88.360 s |
| Claude Sonnet | 6/6 | 0 | 13.745 s |
| GPT-5.6 Sol | 6/6 | 0 | 8.412 s |

Grok's timed-out calls are censored at 90 seconds, so their unknown completion
time cannot be compared directly.

## Quality result

| Persona | Findings | Timeouts | Non-imperative | Complete | Strength 2 | Persona aligned |
|---|---:|---:|---:|---:|---:|---:|
| Karis | 3 | 0 | 3 | 3 | 3 | 0 |
| Quilez | 3 | 0 | 3 | 3 | 3 | 2 |

The automated mechanical gates pass. Human review finds that Quilez reaches the
two-aligned-output threshold because two findings identify work moved from ALU
into sampling or storage pressure. Karis does not reach the threshold: its
outputs mention material or Forward but do not follow material semantics through
unverified DepthOnly and ShadowCaster passes.

## Supported conclusion

For this six-call sample, GPT-5.6 Sol was the fastest provider and returned six
schema-valid findings. It preserved the Quilez lens better than Claude did, but
failed the Karis lens and still concentrated heavily on the packet's salient
register-cost evidence. The two-persona test therefore does not pass as a whole.

This run cannot establish whether differences come from provider behavior,
provider-specific CLI wrappers, or random sampling.
