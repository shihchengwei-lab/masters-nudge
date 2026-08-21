# Shader candidate-search governance v1

This protocol controls search breadth for the next C-only Shader experiment.
It does not select a Shader technique or claim that the search space is
complete.

## Candidate slot

One numbered candidate represents one unique search cell:

`bottleneck hypothesis family × work-elimination mechanism family`

A new numbered candidate is eligible only when at least one family differs
from every registered cell. Names such as `normal`, `half`, `reciprocal`, or
`scalarized` do not establish distinctness by themselves.

Each proposal must state:

- a stable bottleneck-hypothesis family ID and falsifiable statement;
- evidence references supporting that hypothesis;
- a stable work-elimination-mechanism family ID;
- the concrete GPU work the mechanism is expected to remove.

The registry checks structural identity, not semantic truth. Family IDs must be
assigned from the technical meaning before the run; synonyms must not be used
to manufacture new cells.

## Refinement

A proposal in an existing search cell is a refinement of that cell, not a new
candidate. A refinement records the changed variable and the measurement that
can discriminate its effect. It consumes the separately preregistered
per-cell refinement budget and never consumes one of the 50 candidate slots.

`refinement_limit_per_cell` has no production default. The next experiment
must choose and freeze it before execution; changing it mid-run invalidates the
search-budget comparison.

## Budget and stopping evidence

The 50-slot budget counts accepted distinct cells only. Invalid proposals,
same-cell variants, and rejected refinements remain in the rejection record
but do not advance the candidate number.

Exhausting 50 cells shows only that the preregistered budget was used. A search
saturation claim additionally needs the planned hypothesis/mechanism map,
coverage report, eliminated alternatives, and evidence that no supported
unvisited cell remains. The Goal rewrite will define the final stop condition.
