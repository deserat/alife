# sim07 — Environmental Physics Coupling (M_c phase transition)

**One-line:** Tests whether a structure-sourced transport field `T` with a mass threshold `M_c`
produces the trace→actor crossing ([H7](../../hypotheses/hypotheses.md)) as a phase transition —
extending sim06's minimal Grassé stigmergy with the Mahadevan mechanism in lumped form.

**Result:** **NULL.** No phase transition in `M_c`. Sweeping `M_c` from inert to fully active
*decreases* stability monotonically (0.876 → 0.739) and *fragments* the structure (57 → 128
pillars). The crossing detector never fires for any `M_c` or `transport_coupling`. Structure-
sourced scalar transport alone is insufficient; venting disperses the very cue that recruits
deposits.

## What sim07 adds to sim06

The **only** addition is a transport field `T` on the grid:

- `T` is sourced by structure above `M_c`: `T += transport_gain · max(0, M − M_c)`.
  Below `M_c`, no sourcing — the structure is inert (sim06 regime).
- `T` diffuses (toroidal) and decays.
- `T → P` coupling vents pheromone from high-`T` (saturated) to low-`T` (gaps):
  `P += transport_coupling · (T_neighbor_avg − T_local)`.

Agents are **unchanged** from sim06 (Grassé deposit rule, pheromone following). No self-
maintenance emission — the transport field IS the new mechanism.

**Sign correction.** The DESIGN.md sketch wrote the coupling as `(T_local − T_neighbor_avg)`,
which would *increase* pheromone at structure (positive feedback — wrong direction). The prose
("saturated pillars shed their pheromone to their flanks") describes venting, so the implemented
sign is `(T_neighbor_avg − T_local)`. This correction is documented in the 2026-07-27 daily report.

## Results (default run, seed 42)

| metric | baseline (M_c=∞) | transport (M_c=3.0) |
|---|---|---|
| final pillars | 101 | 91 |
| final structure cells | 1131 | 1344 |
| mean stability (last 25%) | 0.874 | 0.850 |
| retention | 0.96 | 1.00 |
| crossing fired | no | no |
| T ever active | no | yes |

Transport modestly consolidates (fewer pillars, more mass) but does NOT cross — stability drops
slightly (criterion 1 needs ≥ 0.90).

### Perturbation / self-repair

| condition | recovery_final |
|---|---|
| baseline | 1.01 |
| transport | 1.02 |

Both recover mass after a 25%-area damage at 60% of steps — but recovery is driven by the deposit
rule (termites wander back), not by transport. The **circularity safeguard is not satisfied**:
repair does not track `T`. This is consistent with the null — `T` is not the causal layer.

## The M_c sweep (the phase-transition test)

| M_c | pillars | stability | retention | T active | crossed |
|---|---|---|---|---|---|
| ∞ | 57 | 0.876 | 0.987 | 0 | no |
| 10.0 | 61 | 0.870 | 0.966 | 1 | no |
| 6.0 | 69 | 0.863 | 0.974 | 1 | no |
| 4.0 | 73 | 0.864 | 0.966 | 1 | no |
| 3.0 | 75 | 0.856 | 0.967 | 1 | no |
| 2.5 | 53 | 0.862 | 0.993 | 1 | no |
| 2.0 | 56 | 0.847 | 0.984 | 1 | no |
| 1.5 | 87 | 0.823 | 0.992 | 1 | no |
| 1.0 | 88 | 0.800 | 0.992 | 1 | no |
| 0.5 | 128 | 0.739 | 0.971 | 1 | no |

**No jump.** A smooth degradation, not a phase transition. A `transport_coupling` sweep
(0.0 → 0.80) confirms: no value crosses, stability stuck ~0.85.

## Why the null is informative

The negative feedback is real but its **effect has the wrong sign for consolidation**: venting
pheromone away from saturated pillars disperses the cue that attracts deposits, fragmenting
rather than consolidating. A lumped linear advection of a scalar cue does not reproduce the
Mahadevan mechanism, where *directed* flow carries the cue *along* channels to where building
should continue. The mechanism needs geometry (directed flow), not just a venting scalar.

### H7 refinement (from this null)

The crossing is not produced by "structure sources a scalar transport field" alone. Two
candidates remain:

1. **Directed transport** — channel geometry that carries cue to building fronts, not away
   from them (the Mahadevan mechanism's directionality, lost in the lumped scalar).
2. **External multi-rate driver** — the diurnal oscillation (H4) the structure rectifies into
   directed flow; sim07's lumped `T` has no external clock. Candidate sim08.

## Run

```bash
cd simulations
uv run python3 sim07_transport_coupling/sim07.py selftest     # sanity checks
uv run python3 sim07_transport_coupling/sim07.py run         # baseline+transport+perturb -> results.json
uv run python3 sim07_transport_coupling/sim07.py sweep_plot  # M_c sweep -> output/*.png
```

Visualization: [visualize.html](visualize.html) (renders results.json + the M_c sweep).

## Cross-references

- [[../concepts/environmental-physics-coupling]] — the concept this sim tests
- [[../concepts/stigmergic-consolidation]] — the negative-feedback gap
- [[../hypotheses/hypotheses.md]] — H7 refined
- sim06 — the null result this sim builds on
- King, Ocko & Mahadevan (PNAS 2015); Ocko, Heyde & Mahadevan (PNAS 2019)
