# Sim07: Environmental Physics Coupling — Testing the M_c Phase Transition (H7)

> **Status:** DESIGN SKETCH (Session 8). Not yet implemented. This document captures the
> design rationale and spec so a future nightly session (or a delegated coding model) can
> implement it Part-by-Part following the sim06 pattern.

## Scientific aim

sim06 tested H7 with minimal Grassé stigmergy + a self-maintenance loop and found a null
result: positive stigmergic feedback alone amplifies building but does not consolidate —
the crossing detector never fires. Session 8 research identified the specific missing
mechanism: **environmental physics coupling** — the accumulated structure must introduce a
transport dynamics absent at the deposit level (the Mahadevan mechanism). See
`../concepts/environmental-physics-coupling.md`.

sim07 tests whether adding a **minimal lumped transport field** with a **mass threshold
M_c** (Vance's inert→active state transition) produces the trace→actor crossing as a **phase
transition in M_c**.

## Hypothesis (operational H7 prediction)

Below a critical mass threshold `M_c`, the structure is inert — it behaves like sim06
(diffuse scatter, ~230 micro-pillars, stability ~0.55, crossing does not fire). Above `M_c`,
the structure *activates*: it sources a transport field `T` that vents pheromone away from
saturated regions (negative feedback), producing consolidation into a few large vented
pillars and the crossing detector firing (stability ≥0.90, constraint ≥0.60). The transition
should be sharp in `M_c`.

## Minimal model spec (lumped)

Extend sim06's `Field` with:

- `M` — material density grid (sim06 already has this).
- `T` — transport potential grid, same shape. `T` is sourced by structure:
  `T_source = max(0, M - M_c) * transport_gain`. Below `M_c`, no sourcing (inert).
- `T` diffuses one step per field update (toroidal, like pheromone diffusion).
- **Coupling to pheromone `P`:** the transport field advects pheromone down the `T` gradient.
  Minimal lumped form: `P += transport_coupling * (T_local - T_neighbor_avg)` — pheromone
  flows from high-`T` (saturated, vented) regions to low-`T` (gaps). This is the negative
  feedback sim06 lacked: saturated pillars shed their pheromone to their flanks.
- Agents unchanged from sim06 (Grassé deposit rule, pheromone following). The ONLY addition
  is the `T` field and its coupling to `P`.

## Conditions

- **baseline:** `M_c = inf` (transport never activates) — reproduces sim06.
- **transport:** `M_c` set so some cells exceed it — transport active.
- **sweep:** sweep `M_c` from high (never active) to low (always active) and look for the
  phase transition in: (a) morphology (scatter → few consolidated pillars), (b) crossing
  detector firing, (c) self-repair after perturbation.

## The circularity safeguard (critical)

By adding the transport rule, we risk building in the crossing we claim to detect. The
safeguard is the **perturbation/self-repair test** (inherited from sim06 Part 8): damage the
structure and measure whether it recruits maintenance *through its transport dynamics*.
Prediction: self-repair succeeds when `T` is active (above `M_c`) and FAILS when `T` is
suppressed (below `M_c` or transport_coupling=0). If repair tracks `T` and not the deposit
rule, the crossing is emergent from the physics, not imposed. This is the H7 acid test.

## Verification (when implemented)

- `selftest` — runs baseline + one transport condition, checks the detector output shape.
- `run --condition transport` — writes `results.json` with the crossing metrics.
- `sweep_plot --param M_c` — sweeps `M_c` and plots the crossing metrics vs `M_c`; look for
  the sharp transition.
- `visualize.html` — renders the `M`, `P`, and `T` fields side by side, dark theme.

## Cross-References

- [[../concepts/environmental-physics-coupling]] — the concept this sim tests
- [[../concepts/stigmergic-consolidation]] — the negative-feedback gap
- [[../hypotheses/H7]] — refined in Session 8
- sim06 — the null result this sim builds on
- King, Ocko & Mahadevan (PNAS 2015); Ocko, Heyde & Mahadevan (PNAS 2019)
