# Sim03: Chemical Organization Theory — Trace Competition and Nested Organizations

## What it tests

Whether reaction networks with multiple competing trace types produce nested organizations (multi-scale structure), and whether the organization structure satisfies the 8th CAS property (closure + self-maintenance).

## Hypotheses tested

- **H7** (Trace→Actor Crossing): Do traces form self-maintaining organizations?
- **H6** (Multi-Scale Autopoiesis): Do organizations contain suborganizations?
- **H1** (Composition): Does multi-scale structure emerge from reaction dynamics?
- COT formalism: Can we operationalize closure + self-maintenance in a simulation?

## Design

A reaction network with:
- **Resources**: Energy (E), trace types (T0, T1, T2), agent types (A0, A1, A2)
- **Reactions**: Energy inflow, trace deposition, trace consumption, trace decay, agent replication, agent death, trace-trace interactions
- **Two conditions**: Single trace type (baseline, sim02-like) vs. 3 competing trace types

Key reactions:
1. ∅ → E (energy inflow)
2. A_i + E → A_i + T_i (agents deposit traces)
3. T_i → ∅ (trace decay)
4. A_i + T_j → A_i + E (same-type: energy recovery) or A_i (cross-type: competition)
5. A_i + 2E → 2 A_i (replication)
6. A_i → ∅ (death)
7. T0 + T1 → T2, T2 + T0 → T1 (trace-trace interactions: cooperation/competition cycle)

The simulation checks for organizations (closed + self-maintaining subsets) every 100 generations and tracks:
- Number of active organizations
- Maximum organization size
- Nested organizations (suborganizations within organizations)
- Resilience: recovery from perturbation at generation 2000

## What it teaches

1. Whether COT formalism can be operationalized for ALife
2. Whether multiple trace types prevent monoculture convergence (sim02's failure)
3. Whether organizations emerge naturally from reaction network dynamics
4. Whether nested organizations (multi-scale structure) form
5. Whether the 8th CAS property (closure + self-maintenance) is achievable

## Results

Corrected 2026-07-27 — see "Two fixes" below and `../REVIEW.md` §4.

| Metric | Single trace | Multi trace |
|---|---:|---:|
| Organizations in the network | 8 | 9 |
| Active organizations (all resources present) | 2 | 9 |
| Nested organization pairs | 1 | 24 |
| Largest active organization | 3 resources | 7 resources |

Every organization contains `E`, as it must: the energy inflow `∅ → E` is applicable to every
subset, so closure forces `E` into all of them. Multi-trace organizations nest cleanly —
`{E} ⊂ {A0,E,T0} ⊂ {A0,E,T0,T1,T2} ⊂ {A0,A1,A2,E,T0,T1,T2}` — giving 24 containment pairs
against the single-trace condition's 1.

**Multiple trace types do produce nested structure** (24 nested pairs vs 1), which is the one
clear positive result here. Perturbation at generation 2000 (halving every concentration)
changes nothing: 2 → 2 → 2 active organizations for single trace, 9 → 9 → 9 for multi. The
organizations are resilient to that perturbation, but see the caveat below for why that is
less impressive than it sounds.

### Two fixes and one caveat

Two defects were corrected in the organization test:

1. **Closure skipped zero-input reactions.** The guard read `if rxn.inputs and all(...)`,
   which excluded the energy inflow `∅ → E`. Since `∅ ⊆ S` for every subset, that reaction is
   always applicable and forces `E` into every organization — subsets were being declared
   closed that were not.
2. **The catalyst exclusion corrupted a shared accumulator.** `consumed.discard(rxn.catalyst)`
   mutated the running `consumed` set, so a later reaction that merely *catalysed* X erased
   the record that an earlier reaction genuinely *consumed* X, making the result depend on
   reaction ordering. The exclusion is now scoped to the reaction being examined.

Separately, the resilience report compared generation 1999 — where organizations are not
computed, so the counts are placeholder zeros — against generation 2000, where they are. It
printed "0 orgs → 9 orgs" and read as the perturbation creating organizations. Records now
carry an `orgs_computed` flag and the comparison uses the last measured generation.

**Caveat — nothing here emerges.** `find_organizations()` enumerates subsets of a fixed
resource set against a fixed, hand-authored reaction network, so the organization count is a
structural property fixed at construction: it is identical at every sampled generation of
every run. Only *which* organizations are populated varies with concentrations. This
simulation therefore cannot answer "do organizations emerge from reaction dynamics" (item 3
under "What it teaches") — it measures which pre-existing organizations are occupied. Note
also that the self-maintenance test is a qualitative proxy ("if consumed, then also produced
somewhere") and not COT's flux condition, so a set can pass it while actually being depleted.
Answering the emergence question needs sim04's evolving network, where new reactions appear.
