# Workflow Holdout V2 — Preregistered Protocol

Frozen before the first reviewer call on 2026-08-13 (Asia/Taipei).

## Question

Does the rewritten prompt produce short, evidence-grounded **workflow nudges**—about framing, assumptions, sequence, scope, feedback, validation, reversibility, or stopping—rather than defaulting to local code review? Does a specialist lens add its intended attention without harming reliable silence on clean workflows?

The 52-character limit is a hard delivery constraint, not a target. There is no minimum length. Cap hits and incomplete thoughts are diagnostics and will be inspected together; text is never shortened merely to improve the length metric.

## Frozen design

- Holdout: 18 unique cases; each of Jeff, Beck, Fowler, Linus, Lamport, and Carmack receives two seeded workflow blind spots and one clean workflow.
- Conditions: `baseline` (general prompt only), `effective` (routed lens), and, for Lamport/Carmack overrides, `primary` (lifecycle lens without the specialist override).
- Repeats: 2.
- Calls: 36 baseline + 36 effective + 12 primary = 84.
- Job randomization seed: `20260816`.
- Blind review shuffle seed: `20260817`.
- Provider/model: `openai` / `gpt-5.6-sol`.
- Codex CLI: isolated `0.147.0` runtime.
- Workers: 2. Per-call timeout: 60 seconds.
- Reviewer temperature/sampling is whatever the CLI/model default supplies; it is not changed between conditions.

Once calls begin, the fixture, oracle, packet builder, schema, router, base prompt, overlays, runner, seeds, and gates below may not change. Failures remain in the denominator; no selective retries are allowed.

## Preregistered gates

The `effective` condition passes this pilot only if all gates pass:

1. Provider success is at least 35/36 and raw schema validity is 36/36.
2. Finding recall is at least 21/24 on seeded workflow blind spots.
3. Correct silence is at least 11/12 on seeded clean workflows.
4. At least 20/24 positive calls are a valid workflow warning: a miss fails; a finding must be grounded, target-relevant, workflow-level, and complete.
5. At least 20/24 positive calls are aligned with the intended lens; a miss fails.
6. At most 2/24 positive calls collapse into local-artifact/code-only critique without identifying a workflow choice or attention point.
7. Across the 36 paired baseline/effective calls, effective may have at most two more invalid decisions than baseline.
8. Across the 12 paired primary/effective specialist calls, effective may lose at most one pair on valid-decision quality.

Automatic `concept_groups` matching is triage only, not a semantic gate. Length, cap-hit rate, punctuation, latency, and token usage are diagnostics only.

## Blind human rubric

All 84 outputs are shuffled and reviewed without fixture ID, condition, or repeat. The reviewer can see the evidence packet, seeded expected status, support facts, intended lens, and workflow target. This is condition-blind but not oracle-blind or author-blind; one author-rater makes the result a pilot, not an independent benchmark.

For each observed finding:

- `grounded`: every material claim is supported by the packet.
- `target_relevant`: it identifies the seeded workflow tension or a defensible, equally material workflow tension.
- `workflow_level`: it concerns a decision, assumption, ordering, scope, feedback loop, validation strategy, reversibility, or stopping condition—not merely a local code defect.
- `lens_aligned`: it expresses the intended lens's attention without roleplay or name-dropping.
- `complete`: it is a self-contained thought, even if very short; punctuation alone is insufficient.

For a seeded blind spot, `no_finding` is an automatic miss. For a seeded clean workflow, `no_finding` is objectively correct; any finding is judged for whether the fixture actually exposes a defensible problem. Judgments are frozen before the separate identity map is opened.

## Frozen input hashes (SHA-256)

```text
12cf1aefd98c83b813e63b45abc6d1d9a8c1a30bf3c9519d4e41d15e43fc5ef9  evaluation/workflow-holdout-v2.json
dfa78671791658ac1d0d794b4bb63697e95986c297ce5c56f20b2c41d092eba8  evaluation/quality_eval.py
d15b6c62f726cb840aa8522e42aad4bde32d6ccb6549bdb95aaea401e70ac82c  evaluation/workflow_blind_review.py
af8f749348b40fa59097665bafbde81c116a522082b26f35bcd81d268d5c4023  buddy.py
baa7af2b101dfd0b2a70b5d404a3ee09c01c48f648c3c059d83943783d23b80f  buddy-prompt.txt
03100643dc4042c439021fb976d6134218b387d3dd2788ca527f8f44479cc86b  reaction-schema.json
f8152356812b9ef0723e966303cc96e443f50dba48c084be490cb7c63e6a7b76  lens_router.py
b6465af87cb1cb256ac3a78ae3569cde4f3567788bf497ae931f9cad54de42fc  persona_config.py
df2ff04c8297d3c40ba98ae5813186ac0a7b17679ad0c2499fc33ad655019936  source_context.py
5d81c9461fbe5da1916a2371336aafb082654592b3006c6548ecb8f8e201d1eb  personas/beck.txt
53c36e02e7988cb872781a4cb298eb7d7513f92c81c88f89c4690d7222492317  personas/carmack.txt
f17ce3cf18a9bf34256bcf107bc1a70af883d933a779542d8c15b83f59175ad9  personas/fowler.txt
e23ba98b4a59447bd1756f6ba239970641891e7a0e4067c3e7019ae823b5a115  personas/jeff.txt
913b8870e8a1c565daeee78e8774747b1f6faa9a874c0dc35dfa2854611d5b9a  personas/lamport.txt
2dcf5c369e96d87cb0980d625e6d656a886e8c0406da48443ea942db98689df8  personas/linus.txt
```
