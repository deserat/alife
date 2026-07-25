# sim06 — Termite Mound: Trace→Actor Crossing (H7)

**One-line:** A minimal Grassé stigmergy termite-mound model testing whether an
accumulated environmental trace can cross from a passive coordination signal to a
self-maintaining actor (hypothesis [H7](../../hypotheses/)).

---

## What it tests

sim06 is the concrete substrate for the **H7 Trace→Actor Crossing Hypothesis**:
that accumulated stigmergic traces can *cross* from being passive coordination
signals to being a self-maintaining actor — a structure that (1) has dynamics not
reducible to individual traces, (2) constrains the agents that build it, and (3)
resists perturbation by repairing itself.

Two conditions are contrasted:
- **baseline** — termites deposit soil pellets laced with cement pheromone; the
  pheromone decays and diffuses; the structure is *inert* (only maintained by
  termites happening to wander back).
- **self_maintenance** — the accumulated structure itself re-emits cement
  pheromone proportional to its material (the trace→actor feedback loop). The
  structure becomes a *source* of the very signal that recruits builders.

A **crossing detector** flags the timestep at which the trace field becomes an
actor per H7's three operational criteria; a **perturbation experiment** damages
the structure mid-run and measures self-repair.

## Hypotheses tested

- **H7 (primary)** — Trace→Actor Crossing. Three operational criteria: (1)
  persistence despite erosion (structure_stability ≥ 0.90), (2) non-reducible
  dynamics (pheromone stays elevated while fresh deposits fall), (3) constraint on
  agents (≥60% of deposits land on existing structure). A crossing is declared
  when all three hold for ≥4 consecutive samples.
- **H1 / H10 (context)** — multi-scale composition. sims 03–05 showed composition
  fails without an explicit mechanism; sim06 tests whether stigmergic
  self-maintenance is that mechanism.
- **H4 (context)** — dynamic environment. The field has its own dynamics (decay,
  diffusion, erosion, self-emission), not just a passive recording medium.

## Design

- **Grid:** 100×100 toroidal. 200 termites, 4000 steps, sampled every 25 steps.
- **Termites** (vectorized): Moore-neighborhood random walk; loaded termites follow
  the pheromone gradient with probability `PHERO_FOLLOW`. Loading via off-grid
  reload (`RELOAD_PROB`) + rare cell pickup (turnover). Deposit probability
  `p = DEPOSIT_BASE + DEPOSIT_GAIN · local/(1+local)` (Grassé positive feedback,
  saturates ~0.95). Tuned: `deposit_base=0.02` (low nucleation), `phero_follow=0.6`.
- **Field:** cement pheromone decays (`PHEROMONE_DECAY=0.02`), diffuses (3×3 toroidal
  blur), material erodes (`material_decay=0.01`, tuned). Self-maintenance condition
  adds `pheromone += MAINTAIN_GAIN · material` over structure cells.
- **Metrics per sample:** total_material, n_structure_cells, mean/max pheromone,
  n_pillars (8-connectivity components), compactness (cells/bbox), stability
  (fraction of structure surviving window-to-window), deposit_on_structure_fraction.
- **Crossing detector:** post-pass over history; requires 4 consecutive samples
  satisfying all three H7 criteria.
- **Perturbation:** at 60% of steps, zero a central 25%-area square of material +
  pheromone; measure `recovery = current / pre-damage total_material`.

## Results (from `results.json` — tuned params: material_decay=0.01, deposit_base=0.02, maintain_gain=0.3)

| Metric | Baseline | Self-Maintenance |
|---|---:|---:|
| final_total_material | 3944 | 5339 |
| final_n_structure_cells | 1131 | 1876 |
| peak_total_material | 4116 | 5446 |
| peak_step | 2800 | 1925 |
| retention | 0.958 | 0.980 |
| mean_stability_last25 | 0.874 | 0.775 |
| **crossed** | **False** | **False** |
| crossing_step | — | — |
| *Perturbation (25% @ step 2400)* | | |
| recovery_final | 1.01 | 1.00 |
| perturbed final_cells | 1155 | — |

**Honest result: a partial/null finding.** Self-maintenance produces a real
quantitative difference — it builds **66% more structure** (1876 vs 1131 cells)
with higher retention (0.98 vs 0.96). But the **formal crossing detector does not
fire** for either condition, and perturbation recovery is ≈1.0 for both (the
damaged patch fully regrows).

**Why no crossing?** H7's criterion 1 (stability ≥ 0.90) fails throughout:
structure stability hovers at 0.55–0.60. The structure remains ~230 scattered
tiny pillars (high `n_pillars`, low `compactness` ≈ 0.08) with constant cell
turnover — cells flip above/below `STRUCTURE_THRESHOLD` every window. Criterion 3
(deposits on structure ≥ 0.60) also fails (~0.33–0.57). An extensive parameter
search (material_decay 0.005–0.4, deposit_base 0.005–0.05, phero_follow 0.6–0.95,
maintain_gain 0.1–0.5, reload_prob 0.15–0.3) found **no regime where the crossing
fires**.

**Root cause:** the model's stigmergy is too *spatially diffuse*. Even with low
nucleation, deposits spread across the grid faster than they consolidate, so the
structure never coalesces into few large, stable, self-maintaining pillars. The
H7 criteria require a consolidated whole whose dynamics are irreducible to its
parts — but this model produces a churning scatter. The self-maintenance
feedback *does* amplify building (66% more structure), but not enough to cross
the stability/constraint thresholds.

This is a legitimate result: **stigmergic self-emission alone is insufficient to
produce the trace→actor crossing in this minimal model.** Spatial consolidation
is a missing ingredient — pointing to what sim07 must add.

## Key findings (project arc)

sims 03–05 showed multi-scale composition fails without an explicit mechanism
(H10: unbounded space is necessary but not sufficient). sim05's closing
recommendation was stigmergy as the "glue." sim06 tested the simplest stigmergic
self-maintenance and found: **the feedback loop amplifies building but does not
produce a self-maintaining actor per H7's operational criteria.** The mechanism is
present in weak form (structure-size boost) but the crossing — the moment a trace
becomes an autonomous actor — is not achieved. H7 is **not supported** by this
model as implemented; the result is suggestive but inconclusive, and points to the
need for a consolidation mechanism (deposit inhibition, directional bias, or
explicit pillar-merging rules) in a follow-up sim.

## Limitations

- Toy 2D model; no real termite biology, airflow, or thermoregulation.
- Single mechanism (cement pheromone self-emission); no competition between
  structures.
- The crossing criteria thresholds (0.90 / 0.5 / 0.6) are reasonable but
  arbitrary; a different operationalization might classify the same dynamics
  differently.
- Parameter-sensitive: the structure-size separation is robust but the crossing
  never fires across the entire swept space.
- Perturbation patch is a clean square; real damage is irregular. Recovery ≈1.0
  means the damage is invisible at these params — a stronger test would need
  higher erosion or larger damage.
- 2D toroidal grid removes boundary effects that real mounds use (edges,
  substrate).

## What it teaches / next steps

The weak result is itself informative: **stigmergic self-emission is not the
missing composition mechanism by itself.** The structure amplifies but doesn't
consolidate. A sim07 could test whether adding **spatial consolidation** — e.g.
deposit inhibition (termites avoid cells above a density cap), directional building
bias along existing walls, or explicit pillar-merging — lets the trace→actor
crossing occur. If sim07 produces the crossing, the project can then ask sim05's
open question with the stigmergic glue in place: **do two self-maintaining
structures compose into a higher-order (L2) organization?**

## How to run

```bash
cd ~/brain/artificial-life/simulations
uv run python3 sim06_termite_mound/sim06.py run          # full experiment -> results.json
uv run python3 sim06_termite_mound/sim06.py sweep_plot   # parameter sweeps -> output/*.png
uv run python3 sim06_termite_mound/sim06.py selftest     # internal sanity checks
```

Visualization: `cd sim06_termite_mound && python3 -m http.server 8080` → open
`http://localhost:8080/visualize.html`. Also deployed at
[alife.vancedubberly.com/sim06_termite_mound/visualize.html](https://alife.vancedubberly.com/sim06_termite_mound/visualize.html).
