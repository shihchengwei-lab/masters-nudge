# Shader prompt replay v1 result

## Outcome

The protocol did not pass because Karis and Quilez timed out on all three calls.
The remaining four personas produced 12 valid findings.

| Persona | Findings | Timeouts | Non-imperative | Complete | Human aligned | Strength 2 |
|---|---:|---:|---:|---:|---:|---:|
| Akenine-Möller | 3 | 0 | 3 | 3 | 3 | 3 |
| Carmack | 3 | 0 | 3 | 3 | 3 | 3 |
| Karis | 0 | 3 | — | — | — | — |
| Lottes | 3 | 0 | 3 | 3 | 3 | 3 |
| Quilez | 0 | 3 | — | — | — | — |
| Tatarchuk | 3 | 0 | 3 | 3 | 3 | 3 |

## Supported conclusions

- All 12 successful raw findings stayed within 52 characters and formed complete sentences.
- All 12 were observations rather than instructions under the frozen rubric.
- All 12 linked packet evidence to a hidden cost or invariant and aligned with the forced persona.
- Timeout is concentrated by persona: Karis 3/3 and Quilez 3/3. The run does not establish why.

## Not established

- Six-persona differentiation and prompt-quality thresholds were not evaluable.
- The run does not isolate persona wording, Grok behavior, concurrency, or CLI transport as the timeout cause.
- The replay tests provider output only; it does not test later influence on the main model.
