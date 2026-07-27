# Sim07: Environmental Physics Coupling — Testing the M_c Phase Transition (H7)

> **Status:** DESIGN SKETCH (Session 9). Not yet implemented. This document captures the
> design rationale and spec so a future nightly session (or a delegated coding model) can
> implement it Part-by-Part following the sim06 pattern.

## Scientific aim

sim06 tested H7 with minimal Grassé stigmergy + a self-maintenance loop and found a null
result: positive stigmergic feedback alone amplifies building but does not consolidate —
the crossing detector never fires. Session 9 research identified the specific missing
mechanism: **environmental physics coupling** — the accumulated structure must introduce a
transport dynamics absent at the deposit level (the Mahadevan mechanism). See
`../concepts/environmental-physics-coupling.md`.

sim07 tests whether adding a **minimal lumped transport field** with a **mass threshold
M_c** (Vance's inert→active state transition) produces the trace→actor crossing as a **phase
transition in M_c**.

## Hypothesis (operational H7 prediction)

Below a critical mass threshold `M_c`, the structure is inert — it behaves like sim06
(diffuse scatter, 66–109 components at baseline, stability 0.849–0.893, crossing does not
fire). Above `M_c`, the structure *activates*: it sources a transport field `T` that vents
pheromone away from saturated regions (negative feedback), producing consolidation into a few
large vented pillars and the crossing detector firing. The transition should be sharp in `M_c`.

The crossing detector has **three** criteria, all of which must hold for ≥4 consecutive
samples — sim07 must satisfy all three, not just the two named in earlier drafts of this
document:

1. `structure_stability ≥ 0.90` — **the binding constraint in sim06** (0.849–0.893 baseline;
   a near miss, so this is what consolidation must push over the line).
2. `mean_pheromone_over_structure ≥ 0.5` **and** `|material_growth_rate| < 0.01` — already
   satisfied in sim06 (130/160 samples), so transport must not break it. Watch this:
   continuous venting could keep mass churning and *lose* the saturation half of the
   criterion, which would be a regression rather than progress.
3. `deposit_on_structure_fraction ≥ 0.60` — satisfied by sim06 baseline (154/160) but
   **failed outright by sim06's self-maintenance condition (0/160)**, because
   `maintain_gain=0.3` saturates the deposit response flat at ~0.87 across the whole grid and
   destroys the spatial contrast. If sim07 keeps a self-emission term, it must avoid
   re-saturating this response, or criterion 3 will block the crossing regardless of what
   transport achieves.

> **Correction (2026-07-27).** Earlier revisions of this document cited sim06 as showing
> "~230 micro-pillars, stability ~0.55" and named only criteria 1 and 3. Those figures were
> wrong against sim06's own `results.json` (actual: 101 components, stability 0.85–0.89), and
> the omitted criterion 2 was the one that actually blocked sim06 — its original form was
> unsatisfiable by construction and has since been corrected. See `../REVIEW.md` §1 and the
> 2026-07-27 entry in `../sim06_termite_mound/DESIGN.md`. sim07 should be built against the
> corrected detector in `sim06.py`, not against the numbers previously quoted here.

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
- [[../hypotheses/H7]] — refined in Session 9
- sim06 — the null result this sim builds on
- King, Ocko & Mahadevan (PNAS 2015); Ocko, Heyde & Mahadevan (PNAS 2019)
