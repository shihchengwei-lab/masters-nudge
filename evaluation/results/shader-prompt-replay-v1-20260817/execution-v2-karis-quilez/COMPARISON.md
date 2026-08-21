# Karis and Quilez focused rerun

## Controlled change

One persona-local occurrence of `必須` was removed from Karis and Quilez.
The fixture packet, base prompt, checkpoint prompt, schema, seed, worker count,
timeout, provider, model default, and three repeats per selected persona stayed
fixed. The focused runner preserved the two personas' relative positions from
the original shuffled 18-job order.

## Result

| Persona | Original findings | Original timeouts | Rerun findings | Rerun timeouts | Threshold met |
|---|---:|---:|---:|---:|---:|
| Karis | 0 | 3 | 0 | 3 | No |
| Quilez | 0 | 3 | 1 | 2 | No |

The sole finding was:

> 兩次查找讓公式變短，十二層重疊卻把工作量藏進頻寬與暫存器。

Human adjudication rates it as a complete observation, strength 2, and aligned
with Quilez's representation-versus-invariant lens.

## Supported conclusion

Removing `必須` was not sufficient to eliminate the timeout failure: five of
six calls still timed out. Quilez changed from zero to one finding, but this
single stochastic rerun without a simultaneous old-prompt control cannot
attribute that change to the wording edit.

Karis remains unevaluable, and Quilez has only one aligned output; neither
persona reaches the protocol requirement of at least two aligned outputs.
