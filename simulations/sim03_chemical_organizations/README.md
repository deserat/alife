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
