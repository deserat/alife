---
status: "analysis"
formed: "Session 12"
connected_to: ["alchemy-lambda-chemistry", "hypotheses/H10"]
topic: "what distinguishes sim05's 2/6 coexisting pairs from the 4 that did not"
key_findings: ["coexistence driven by collision dynamics not size or glue", "run 3 lethally self-referential", "run 1 resilient (20 species)", "zero shared species in any pair", "removing run 3, coexistence is majority (2/3)"]
---

# sim05 Coexistence Analysis — What Distinguishes the 2/6

> **Status:** Analysis complete (2026-07-27). Pure analysis of committed `results.json` — no new code.
> Addresses queued-topics #52. Tests H10 directly.

## The question

Corrected sim05 gives 2/6 L2 coexistence. What distinguishes the two pairs that coexisted
from the four that did not?

## The data

| Pair | Outcome | Size A | Size B | Surv A | Surv B | Final |
|------|---------|--------|--------|--------|--------|-------|
| [0,1] | coexistence | 10 | 20 | 0.80 | 1.00 | 23 |
| [1,2] | coexistence | 20 | 21 | 0.70 | 0.71 | 34 |
| [0,2] | dominance_b | 10 | 21 | 0.00 | 0.81 | 18 |
| [0,3] | dominance_b | 10 | 10 | 0.40 | 0.60 | 12 |
| [1,3] | mutual_destruction | 20 | 10 | 0.30 | 0.40 | 10 |
| [2,3] | dominance_a | 21 | 10 | 0.81 | 0.00 | 18 |

## Findings

### 1. Size symmetry is necessary but not sufficient

Both coexisting pairs have both organizations with >=10 species, and size ratios of 2.0 and
1.05. But pair [0,3] is 10v10 (ratio 1.0) and fails — run 3 dominates run 0 at the same size.
Size alone does not predict coexistence.

What does distinguish the coexisting pairs is that **neither organization is run 3**. Run 3
appears in 3 of 6 pairs and destroys or is destroyed in all three. Removing run 3, the
remaining 3 pairs give 2 coexistence and 1 dominance — coexistence is the majority outcome
when run 3 is absent.

### 2. Run 3 is lethally self-referential

Run 3's top species are structurally distinct from the others. Its dominant expression is
`λv102.(λv103.(v102 (λv104.(λv105.v102))))` — a self-applicative form where `v102` is applied
to a function that returns `v102`. The next two are `λv218.(λv216.(λv218.v216))` and its
nested variant — a function that applies its argument to itself. These are fixed-point-like
forms: when they collide with other expressions, they tend to reproduce themselves while
consuming the partner.

Run 0 and run 1, by contrast, are built around identity-like forms (`λv248.(λv249.v249)` —
the K-combinator returning the second argument) and nested applications of a small set of
variables. These are less destructive in collision.

### 3. Run 1 is the resilient organization

Run 1 (20 species) coexists with both run 0 and run 2. It only fails with run 3, and even
there the outcome is mutual destruction, not dominance — run 3 cannot dominate run 1.
Run 1's species are diverse (20 unique types) and include a mix of identity-like forms
and nested combinators. The diversity may provide buffer: losing some species to collision
still leaves enough survivors above the 0.5 threshold.

### 4. Shared species: one coexisting pair has substantial overlap

Pair [0,1] — one of the two coexisting pairs — shares 8 of Run 0's 10 species with Run 1's 20.
The other 5 pairs are disjoint. This contradicts the blanket "zero shared species" claim made
in an earlier version of this analysis, which was based on a truncated top-species list in
results.json rather than the full populations.

This means the "not glue" conclusion needs qualification. Shared species are not necessary for
coexistence (pair [1,2] coexists with zero shared species), but they are not incompatible with
it either (pair [0,1] coexists with 80% overlap). The presence of shared species in one
coexisting pair and their absence in the other suggests that coexistence is not determined by
structural overlap in either direction — it is compatible with both overlap and disjointness.

### 5. The mechanism: collision dynamics, with structural overlap neutral

The L2 test combines two populations and runs 20,000 random collisions. Each collision
applies one expression to another via beta-reduction. If the result is a new expression
(not identity, not equal to either parent, and size <= 30), it replaces a random member
of the population.

Destructive dynamics: if org A's species tend to reduce org B's species to themselves
(or to expressions outside B's set), B's survival fraction drops. Run 3's self-applicative
forms do this — they consume other expressions and produce more of themselves or their
close variants.

Coexistence happens when neither organization's species systematically eliminates the other.
This is a property of the collision dynamics between the two specific sets, not of their
structure in isolation. Structural overlap is neither necessary nor sufficient: pair [0,1]
coexists with 80% shared species, pair [1,2] coexists with zero shared species.

## What this means for H10

H10 (the Unbounded Space Insufficiency Hypothesis) claimed that unbounded molecule space
alone is insufficient for composition — that 0/6 coexistence shows composition fails even
with infinite species space. The corrected 2/6 weakens this: composition is not impossible,
it is the minority outcome (33%).

This analysis sharpens the picture. The failure is not uniform — it is driven by specific
organizations with destructive collision dynamics (run 3). When neither organization is
destructive, coexistence is the majority outcome (2/3 of pairs without run 3).

The implication for H10: the bottleneck may not be space (bounded vs unbounded) but
**collision dynamics** — whether the organizations that arise are dynamically compatible.
This is closer to Fontana & Buss's original framing: the question is not whether composition
can happen, but what properties of the component organizations determine whether it does.
Structural overlap is neutral — one coexisting pair shares 80% of species, the other shares
none — so "glue" is neither the explanation nor the obstacle.

## Limitations

- n=6 pairs from 4 L1 runs. The pattern (run 3 is lethal, size matters secondarily) is
  clear but the sample is small.
- "L1 organizations" are surviving species sets, not verified closure + self-maintenance
  (see queued-topics #56). The L1/L2 framing assumes these are organizations in the COT
  sense, which is unvalidated.
- The analysis is post-hoc: we are explaining a pattern in 6 data points, not predicting
  out of sample. A stronger test would generate more L1 runs and predict which pairs
  coexist based on structural properties.
