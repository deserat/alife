# sim09 — The Curvature Channel

**A non-saturating, recruit-as-well-as-limit stigmergic channel testing whether the trace→actor crossing (H7) fires where saturating cue-field feedback fragmented.**

---

## What it tests

**H7, the Trace→Actor Crossing Hypothesis** — does an accumulated stigmergic trace cross from passive coordination signal to self-maintaining actor? sim06 (saturating cement-pheromone cue) was a near-miss and then a reversal (self-maintenance *fragmented* the structure). sim07 (scalar structure-sourced transport) had the wrong sign. sim08 (non-saturating density cap) consolidated morphology but didn't recruit maintenance. **H11, the Saturating Channel Hypothesis**, diagnosed the common failure: all three acted *through the pheromone field*, whose deposit response `p = base + gain·φ/(1+φ)` saturates above φ≈1, so negative feedback through that channel destroys spatial contrast rather than creating it.

sim09 replaces the saturating cue with the **curvature channel** identified by Calovi et al. (2019, *Phil Trans R Soc B*) and Facchini et al. (2020, *J R Soc Interface*; 2024, *eLife*). The Facchini 2020 growth equation

```
∂f/∂t ≈ f(1−f)·[(1/2)·Δf + d·Δ²f]
```

becomes three operational pieces in sim06's 2D grid+agent framework:

- **`(1/2)·Δf` (mean curvature) → the recruit mechanism.** Loaded termites deposit at convex tips via a *linear, non-saturating* probability `p = base + gain·curvature`, clamped to [0,1]. Depositing at a convex tip extends the tip, recruiting further building there.
- **`d·Δ²f` (biharmonic) → the limit mechanism + phase-transition knob.** `d` is sim09's analog of sim07's `M_c`. Part 7's `d` sweep is the headline phase-transition plot.
- **`f(1−f)` (surface restriction) → `compute_on_surface`.** A Moore-dilation of the structure mask restricts deposits to the structure surface.

The **Facchini/Calovi action-component split** is the single most important design constraint: loaded termites deposit at convex tips (Facchini 2024: pellet deposition at convex tips); unloaded termites excavate at concavities (Calovi 2019: aggregate activity at concavities). sim06 conflated these into a single "build" action; sim09 splits them — conflating them would invert the rule's sign.

**Conditions:**
- `curvature_channel` — the curvature routing + biharmonic smoothing + surface restriction.
- `baseline_pheromone` — sim06's saturating Grassé rule (deposit probability `base + gain·φ/(1+φ)`), reusing the same metrics and detector. The control.

## Hypotheses tested

- **H7 (primary)** — the trace→actor crossing. sim09's crossing detector has three channel-adapted criteria: (1) `structure_stability ≥ 0.90`, (2) roughness (curvature std over surface) sustained `≥ 0.02` *while mass saturates* (`|growth_rate| < 0.01`), (3) `deposits_on_convex_fraction ≥ 0.60`. Criterion 2's mass-saturation gate is the curvature analog of sim06's fixed deposit-rate criterion, corrected after the 2026-07-27 detector-bug audit. A synthetic-history regression guard encodes that lesson as an executable test (must fire on all-true; withhold when any single criterion is negated).
- **H11 (the saturating-channel diagnosis)** — sim09 is its sufficiency test: does a non-saturating recruiting channel cross where saturating/non-recruiting channels (sim06 cue, sim07 scalar transport, sim08 cap) all failed?
- **H4 (dynamic environment)** — curvature is geometry the agents reshape; the stigmergic medium is dynamic, not a fixed fitness function.
- **H1 / H10 (composition context)** — if the curvature channel crosses, the next question is whether two self-maintaining curvature structures compose (the L2 question sim05 left open, now with a non-saturating stigmergic glue).

## Design

| parameter | default | role |
|---|---|---|
| `GRID_SIZE` | 100 | toroidal 2D grid |
| `N_TERMITES` | 200 | agents |
| `STEPS` | 4000 | steps per condition |
| `D_SMOOTH` (`d`) | 1.0 | biharmonic smoothing strength — the phase-transition knob |
| `MATERIAL_DECAY` | 0.0005 | per-step erosion |
| `DEPOSIT_PROB_BASE` | 0.10 | nucleation base (linear, non-saturating) |
| `DEPOSIT_PROB_GAIN` | 0.85 | curvature-driven deposit gain |
| `EXCAVATE_PROB_BASE` | 0.05 | baseline excavation at concavities |
| `CURVE_FOLLOW` | 0.6 | prob a termite follows the curvature cue vs random step |
| `STAB_THRESH` | 0.90 | crossing criterion 1 |
| `ROUGH_ELEV_THRESH` | 0.02 | crossing criterion 2 (roughness) |
| `CONSTRAIN_THRESH` | 0.60 | crossing criterion 3 (deposits on convex) |

The perturbation/self-repair test (Part 8) damages a central 25%-area square at step 0.6×steps and measures `recovery = total_material / pre_perturb_total_material` for each post-damage record.

**Cited:** Calovi et al. 2019 (*Phil Trans R Soc B*); Facchini, Lazarescu, Perna & Douady 2020 (*J R Soc Interface*), public code at github.com/oiluigioi/JRSI_2020_termite_nest; Facchini et al. 2024 (*eLife*).

## Results (default params, seed=42, d=1.0)

| Metric | Curvature Channel | Baseline Pheromone |
|---|---:|---:|
| final_n_structure_cells | 10,000 (grid-saturated) | 4,833 |
| final_total_material | 51,867 | 131,144,449 |
| retention | 1.0 | 1.0 |
| mean_late_stability | 1.0 | 0.999 |
| **crossed** | **false** | **false** |
| crossing_step | null | null |

**Perturbation (25% damage @ step 2400):**

| Metric | Curvature Channel | Baseline Pheromone |
|---|---:|---:|
| recovery_final | 1.13× | 47.34× |
| perturbed final_cells | 9,999 | 4,896 |

**d-sweep (reduced grid 80², 150 termites, 2000 steps):** no phase transition at default `DEPOSIT_PROB_BASE=0.10`. The curvature channel saturates the grid (pillars=1, retention=1.0 at every d ∈ {0, 0.2, 0.5, 1, 2, 4, 8}). Tuned probes (`deposit_prob_base=0.01`, `material_decay=0.002`) show the predicted consolidation **direction** (pillars 25→2 as d rises 0→4) and a roughness spike at the biharmonic instability — the mechanism's sign is right — but the crossing detector does not fire because mass never saturates (criterion 2's gate).

### Honest reading

At default parameters, **neither condition crosses**, and the perturbation recovery does not cleanly separate the channels the way H7 predicts. The baseline's 47.34× "recovery" is an artifact of unbounded material accumulation — the saturating deposit rule piles material without an erosion balance, so `total_material` grows ~47× from the early pre-damage sample. The curvature channel's 1.13× refills the 25% hole (repair-like in direction) but the grid-wide recovery ratio cannot distinguish "targeted repair at the scar" from "volume restoration / continued growth." This is H11's failure mode surfacing in a second, independent metric: a saturating channel cannot express the spatial contrast targeted repair needs.

The **clean H7 separation** — curvature recruits repair at the scar, baseline does not — requires the **mass-saturating parameter regime** Part 7 also identified as needed for the crossing: lower nucleation (`deposit_prob_base ≈ 0.01`) + higher erosion (`material_decay ≈ 0.002`) so the biharmonic instability can create spatial selectivity *before* the grid fills. In a tuned probe the curvature channel saturates and refills the hole to 1.01× (repair-like) while the baseline grows unboundedly to 4.55× (volume, not repair) — the direction is right, but the minimal grid-wide metric is not sharp enough to settle H7 on its own.

## Key findings (project arc)

- **sim06** (saturating cue): near-miss, then reversal — self-maintenance *fragmented* the structure (219–297 components vs 66–109 baseline).
- **sim07** (scalar structure-sourced transport): null — venting pheromone *away* from saturated pillars disperses the cue that recruits deposits (wrong sign for consolidation).
- **sim08** (non-saturating density cap): consolidates morphology (pillars 101→52) but **doesn't recruit** — stability didn't rise (0.874→0.775). Necessary, not sufficient.
- **sim09** (non-saturating recruit+limit curvature channel): consolidation **direction confirmed** (pillars ↓ as d ↑ in tuned probes, opposite of sim06/sim07 fragmentation). Crossing itself **not yet fired** at the parameters tried — the grid saturates before mass can plateau, so criterion 2's mass-saturation gate cannot fire.

sim09's result is **consistent with H11** (the non-saturating channel consolidates where saturating channels fragmented) but **not yet a positive test of H7** (the crossing needs the recruit half to drive maintenance, not just morphology). The curvature channel has both halves (recruit + limit) in principle; finding the parameter regime that reveals the `d` phase transition — and a spatially-targeted recovery metric that distinguishes scar repair from volume restoration — is the remaining scientific work. If the crossing fires only above the Facchini `d*` instability, sim09 unifies the directed-transport and non-saturating-inhibition candidates (queued-topic 58): curvature IS the minimal lumped form of directed geometry.

## Limitations

- Toy 2D toroidal grid; lumped curvature (half the Laplacian of a lightly-smoothed material field), not the full Facchini phase-field.
- No real evaporation, airflow, or thermal physics — the evaporation≡curvature unification (Facchini 2024) is represented only geometrically.
- Parameter-sensitive: at default `deposit_prob_base=0.10` the grid saturates before spatial selectivity emerges; the phase-transition regime needs lower nucleation + higher erosion.
- The roughness-as-maintenance mechanism (deposits roughen the surface, focusing further deposition) is **inferred**, not directly measured.
- Explicit-step integration of the biharmonic `d·Δ²f` is numerically fragile at high `d` (a `d=8` probe showed a blowup; the `0.0001` prefactor needs reducing for the upper sweep range).
- The perturbation recovery metric is grid-wide; it cannot distinguish "repair at the scar" from "continued growth elsewhere." A spatially-targeted variant would make the acid test decisive without needing the full mass-saturating regime.

## What it teaches / next steps

1. **Find `d*`.** A broad parameter sweep over `deposit_prob_base × material_decay × d` in the mass-saturating regime (low nucleation, higher erosion) to locate the biharmonic instability where the crossing fires — if it does. This is the headline remaining experiment.
2. **Spatially-targeted recovery metric.** Measure recovery in the damaged patch specifically, not grid-wide, to make the perturbation test decisive.
3. **Composition (the L2 question).** If the curvature channel crosses, do *two* self-maintaining curvature structures compose? This is the sim05 L2 question reopened with a non-saturating stigmergic glue — the direct test of H1/H10.
4. **The crowding channel (Xiao 2026).** The third non-saturating channel, independent of curvature/evaporation. A sim10 could test whether crowding (distributed inhibition preventing saturation) crosses where the density cap (sim08) didn't — the cap limited without recruiting; crowding might recruit via local density gradients.

## How to run

```bash
cd ~/brain/artificial-life/simulations
uv run python3 sim09_curvature_channel/sim09.py run          # main experiment -> results.json
uv run python3 sim09_curvature_channel/sim09.py sweep_plot   # parameter sweeps -> output/*.png
uv run python3 sim09_curvature_channel/sim09.py selftest    # fast internal sanity checks
```

Visualization: [visualize.html](https://alife.vancedubberly.com/sim09_curvature_channel/visualize.html) — fetches `results.json` and the optional `output/sweep_data.json`.
