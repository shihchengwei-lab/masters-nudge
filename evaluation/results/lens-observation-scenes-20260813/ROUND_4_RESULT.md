# Workflow observation scenes — round 4 local closure

Executed on 2026-08-13 through the production OpenAI reviewer path
(`gpt-5.6-sol`, `codex-cli 0.147.0`).

## Bottom line

The delivery-preserving local fallback passed all declared gates. All 18 paid
calls returned findings; all 18 delivered findings were complete, ended in
terminal punctuation, and stayed within 52 characters. All six lenses retained
3/3 semantic alignment and no output named or imitated a persona.

Four raw model findings reached exactly 52 characters. One was already a
complete punctuated sentence and remained unchanged. Three ended without a
complete final clause; the local sanitizer closed each at its preceding clause
boundary. No result was rejected and no retry or additional provider call was
made.

## Comparison

| Metric | Prompt-only round 3 | Local-closure round 4 |
|---|---:|---:|
| Semantically stable lenses | 6/6 | **6/6** |
| Lens-aligned repeats | 18/18 | **18/18** |
| Complete delivered thoughts | 15/18 | **18/18** |
| Terminal punctuation | 13/18 | **18/18** |
| Raw exact-cap hits | 5/18 | 4/18 |
| Delivered exact-cap hits | 5/18 | **1/18** |
| Findings delivered | 18/18 | **18/18** |
| Additional provider calls | 0 | **0** |

Six delivered findings landed inside the 36–42-character target range, one was
shorter and complete, and 11 exceeded the soft target while remaining within
the hard cap. Mean delivered length was 44.4 characters. The target remains a
generation preference rather than a delivery requirement.

## Fallback audit

Three findings changed. In each case the removed suffix was already incomplete,
while the retained clause remained evidence-grounded and lens-specific:

- Beck 2: `local-json 尚未端到端試跑，卻先鋪三個未用後端並準備 cloud。`
- Beck 3: `local-json 尚未端到端驗證，卻已鋪三個未用後端並先做 cloud。`
- Fowler 1: `大小寫、filter、extension 規則散在三處，下一個相似需求仍得同步修改。`

The five exact-cap failures from round 3 are also fixed by deterministic replay
tests, including the prior Lamport and Carmack fragments.

## Claim boundary

This validates deterministic delivery behavior against both preserved failures
and one fresh 18-call run on the development fixture. It does not establish
general six-lens reliability; that still requires a new holdout packet.

Raw outputs, delivered findings, manifest, automated analysis, selection, and
human adjudication are under `execution-v4/`.

## Real Tk hero

The formal selection uses the lowest-numbered valid delivered finding for each
lens, without editorial rewriting. Six actual `BuddyWindow` instances read
those findings through the production JSONL path; the result is a direct Windows
desktop capture, not an AI-generated mockup. Fowler's selected line demonstrates
the deterministic local closure, while the other five selected lines passed
through unchanged.

- README hero: `docs/images/masters-nudge-six-lenses-hero.png`
- Six individual captures: `execution-v4/screenshots/`
- Capture manifest: `execution-v4/hero-capture.json`
- Formal selection: `execution-v4/hero-selection.json`

| Artifact | SHA-256 |
|---|---|
| hero PNG | `118b275bfc20549ea673473250afe14eb605d9d1e9757073816cc08f63fba74b` |
| raw runs | `ce68e4f4acc7990fda85e631cbac06796eab3664d4fabbfa1b8b26caa4ca480f` |
| automated analysis | `9b6f039e4dc8c4735f9c201849aecd1d54d18d094356ad63380c8f791fc7d508` |
| human audit | `28042ff73bd2df6f42d20f62ebe3582e7c48b6f756d9bfdac1e3484d574ad5e8` |
| formal selection | `a9f14b0b2816479a17f7f244337689421b120db2445fa94f3814e8e73e2c6b76` |
