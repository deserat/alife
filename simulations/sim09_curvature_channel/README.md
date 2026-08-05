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

- **H7 (primary)** — the trace→actor crossing. sim09's crossing detector has three channel-adapted criteria: (1) `structure_stability ≥ 0.90`, (2) roughness (curvature std over surface) sustained `≥ 0.02` *while mass plateaus* — corrected in Session 19 to a relative-slope plateau `|slope(total_material over last K=16 samples)|/mean(total_material) < 0.001` (the original `|growth_rate| < 0.01` gate was an unfalsifiable metric-ceiling bug, its threshold ~100× below the Poisson noise floor of a 150-termite deposit process), (3) `deposits_on_convex_fraction ≥ 0.60`. A synthetic-history regression guard encodes that lesson as an executable test (must fire on all-true; withhold when any single criterion — including the mass plateau — is negated).
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
| **crossed** | **true** (step 1125) | **false** |

**Note (Session 19):** at default params the curvature channel grid-saturates (10000/10000 cells), so the mass plateau is a physical ceiling (nowhere left to deposit), not a dynamic equilibrium. The honest crossing result is the tuned probe below, where the grid does not saturate. The baseline never crosses under the corrected detector at any parameter.

**Perturbation (25% damage @ step 2400):**

| Metric | Curvature Channel | Baseline Pheromone |
|---|---:|---:|
| recovery_final | 1.13× | 47.34× |
| perturbed final_cells | 9,999 | 4,896 |

**d-sweep (reduced grid 80², 150 termites, 2000 steps):** under the original detector, no phase transition at default `DEPOSIT_PROB_BASE=0.10` — the curvature channel saturates the grid (pillars=1, retention=1.0 at every d ∈ {0, 0.2, 0.5, 1, 2, 4, 8}). **Session 19 d* sweep (100 combos, `dpb × decay × d`): 0/100 crossed under the original detector** — criterion 2's mass-saturation gate (`|growth_rate|<0.01`) was an unfalsifiable metric-ceiling bug (threshold ~100× below the Poisson noise floor of a 150-termite deposit process). **Corrected to a relative-slope plateau** (`|slope(M)|/mean(M)<0.001` over K=16 samples): the crossing fires in the curvature channel at every d∈[0,4] in the tuned probe (dpb=0.01, decay=0.002, non-saturating grid 3123–5754/6400 cells) and does NOT fire in the baseline-pheromone control (same detector, 0/3 — saturating rule never elevates the pheromone cue enough). crossing_step 1550→900, pillars 12→1, roughness 0.44→0.77 as d rises. Determinism verified (0/80 history diffs).

### Honest reading

At default parameters the corrected detector fires for the curvature channel (step 1125) and not the baseline — but the grid saturates (10000/10000 cells), so the mass plateau is a physical ceiling, not a dynamic equilibrium. The **honest crossing result is the tuned probe** (dpb=0.01, decay=0.002), where the grid does not saturate (3123–5754/6400 cells): the curvature channel crosses at every d∈[0,4] and the baseline-pheromone control (same detector) does not (0/3). This is the first H7 crossing with a control arm. The baseline's 47.34× perturbation "recovery" remains an artifact of unbounded material accumulation (the saturating deposit rule piles material without an erosion balance) — a saturating channel cannot express the spatial contrast targeted repair needs. **Honest limitation:** the crossing fires at d=0 (no smoothing), so the recruit half (curvature routing) drives the verdict; the limit half (d-smoothing) consolidates morphology (pillars 12→1, crossing_step 1550→900) but is not necessary for the crossing. The recruit-vs-limit isolation is the next test.

The **clean H7 separation** — curvature recruits repair at the scar, baseline does not — requires the **mass-saturating parameter regime** Part 7 also identified as needed for the crossing: lower nucleation (`deposit_prob_base ≈ 0.01`) + higher erosion (`material_decay ≈ 0.002`) so the biharmonic instability can create spatial selectivity *before* the grid fills. In a tuned probe the curvature channel saturates and refills the hole to 1.01× (repair-like) while the baseline grows unboundedly to 4.55× (volume, not repair) — the direction is right, but the minimal grid-wide metric is not sharp enough to settle H7 on its own.

## Key findings (project arc)

- **sim06** (saturating cue): near-miss, then reversal — self-maintenance *fragmented* the structure (219–297 components vs 66–109 baseline).
- **sim07** (scalar structure-sourced transport): null — venting pheromone *away* from saturated pillars disperses the cue that recruits deposits (wrong sign for consolidation).
- **sim08** (non-saturating density cap): consolidates morphology (pillars 101→52) but **doesn't recruit** — stability didn't rise (0.874→0.775). Necessary, not sufficient.
- **sim09** (non-saturating recruit+limit curvature channel): **crossing FIRES** (Session 19, corrected detector). The d* sweep (100 combos) found 0/100 under the original detector — criterion 2's mass-saturation gate (`|growth_rate|<0.01`) was an unfalsifiable metric-ceiling bug (threshold ~100× below the Poisson noise floor of a 150-termite deposit process). Corrected to a relative-slope plateau (`|slope(M)|/mean(M)<0.001` over K=16 samples), the crossing fires in the curvature channel at every d∈[0,4] in the tuned probe (dpb=0.01, decay=0.002, non-saturating grid 3123–5754/6400 cells) and does NOT fire in the baseline-pheromone control (same detector, 0/3). crossing_step 1550→900, pillars 12→1, roughness 0.44→0.77 as d rises. **Honest limitation:** the crossing fires at d=0, so the recruit half (curvature routing) drives the verdict; the limit half (d-smoothing) consolidates morphology but is not necessary for the crossing.

sim09's result is now a **positive test of H7 with a control arm and a mechanism decomposition** — the corrected detector fires the crossing in the curvature channel and not in the baseline-pheromone control (same detector). H11's channel distinction (non-saturating action-channel vs saturating cue-channel) is the causal variable separating crossing from non-crossing, not just a directional correlate.

**Session 20 (2026-08-04) recruit-vs-limit isolation:** a 2×2 factorial (recruit ON/OFF × limit ON/OFF, 4-seed robustness pass) decomposed the curvature channel into its two halves. The **recruit half** (curvature routing: `curve_follow`, `deposit_prob_gain`, `excavate_prob_gain`) is necessary and almost-sufficient for a *stable* crossing: recruit-only (d=0) crosses stably in 3/4 seeds (hold rate 1.00 in 3, 0.65 in the borderline seed); neither (no recruit, no limit) never crosses (0/4). The **limit half** (biharmonic d-smoothing) alone is never stable (0/4 — criteria flicker, hold 0.40–0.55, because the smoothing shapes convex geometry that no agent is routed to; criterion 3 `deposits_on_convex_fraction` oscillates around 0.60 without the routing to concentrate deposits at convex tips). But the limit half is not morphology-only: it is a **stability amplifier** — recruit+limit is stable in 4/4 seeds where recruit-only is 3/4; the borderline seed becomes fully stable (hold 1.0) when d>0 is added. So H11's "recruit as well as limit" is: recruit = necessary + almost-sufficient; limit = stabilizer + morphology optimizer (causally contributes to robustness, not strictly necessary). The decisive contrast is recruit ON vs OFF at d=0 (same detector, same regime, only the recruit flag differs). See `recruit_limit_sweep.py`.

**Session 21 (2026-08-05) saturating-action control:** the recruit half is action-based AND non-saturating simultaneously — H11's two claimed properties are confounded. A saturating response `p = base + gain·c/(1+|c|)` (action-based, compresses) was tested against the linear `p = base + gain·c` (action-based, non-saturating) in a 2×2×2 factorial (response × recruit × d) with a 4-seed robustness pass. The saturating action crosses in 8/8 recruit-ON seeds and is stable in 6/8 (linear is 7/8); the limit half rescues both to 4/4 at d=1. Saturation costs ~0.05 in mean hold rate at d=0 (0.91→0.86) but does not collapse the crossing — criterion 3 (deposits_on_convex_fraction) holds 1.00 for both forms; only the mass-plateau gate (criterion 2p) flickers more under saturation. **Action-based routing is the primary load-bearing property; non-saturating is a secondary stability amplifier.** H11's strict "non-saturating" claim is partially weakened: a saturating action-based channel still crosses stably, but less robustly. See `saturating_action_sweep.py`.

The next test is a **spatially-targeted recovery metric** (measure repair in the damaged patch, not grid-wide) to make the perturbation acid test decisive, and then the **L2 composition question**: do two self-maintaining curvature structures compose (the sim05 L2 question reopened with a non-saturating stigmergic glue — the direct test of H1/H10)?

## Limitations

- Toy 2D toroidal grid; lumped curvature (half the Laplacian of a lightly-smoothed material field), not the full Facchini phase-field.
- No real evaporation, airflow, or thermal physics — the evaporation≡curvature unification (Facchini 2024) is represented only geometrically.
- Parameter-sensitive: at default `deposit_prob_base=0.10` the grid saturates before spatial selectivity emerges; the phase-transition regime needs lower nucleation + higher erosion.
- The roughness-as-maintenance mechanism (deposits roughen the surface, focusing further deposition) is **inferred**, not directly measured.
- Explicit-step integration of the biharmonic `d·Δ²f` is numerically fragile at high `d` (a `d=8` probe showed a blowup; the `0.0001` prefactor needs reducing for the upper sweep range).
- The perturbation recovery metric is grid-wide; it cannot distinguish "repair at the scar" from "continued growth elsewhere." A spatially-targeted variant would make the acid test decisive without needing the full mass-saturating regime.

## What it teaches / next steps

1. **The crossing fires (Session 19).** The d* sweep found the original detector's mass-saturation gate was an unfalsifiable metric-ceiling bug (threshold ~100× below the Poisson noise floor). Corrected to a relative-slope plateau, the crossing fires in the curvature channel and not in the baseline-pheromone control — the first H7 crossing with a control arm. `dstar_sweep.py` is the sweep script; `sim09.py`'s `detect_crossing` carries the corrected gate.
2. **The recruit and limit halves are isolated (Session 20).** A 2×2 factorial (recruit ON/OFF × limit ON/OFF, 4-seed robustness pass) found the recruit half is necessary and almost-sufficient for a stable crossing (3/4 seeds stable at d=0; neither = 0/4); the limit half alone is never stable (0/4 — criteria flicker) but is a stability amplifier (recruit+limit = 4/4 stable, rescuing the borderline seed). See `recruit_limit_sweep.py`.
3. **The action-based vs non-saturating confound is resolved (Session 21).** A saturating-action control (same curvature routing, saturating response `c/(1+|c|)` vs linear `c`) found action-based routing is the primary load-bearing property (saturating crosses 8/8 seeds, stable 6/8; linear 8/8, stable 7/8); non-saturating is a secondary stability amplifier (mean hold drops 0.91→0.86 at d=0; criterion 3 holds 1.00 for both). The limit half rescues both to 4/4 at d=1. See `saturating_action_sweep.py`.
4. **Spatially-targeted recovery metric.** Measure recovery in the damaged patch specifically, not grid-wide, to make the perturbation test decisive.
5. **Composition (the L2 question).** The curvature channel crosses — do *two* self-maintaining curvature structures compose? This is the sim05 L2 question reopened with a non-saturating stigmergic glue — the direct test of H1/H10.
6. **The crowding channel (Xiao 2026).** The third non-saturating channel, independent of curvature/evaporation. A sim10 could test whether crowding (distributed inhibition preventing saturation) crosses where the density cap (sim08) didn't — the cap limited without recruiting; crowding might recruit via local density gradients.

## How to run

```bash
cd ~/brain/artificial-life/simulations
uv run python3 sim09_curvature_channel/sim09.py run          # main experiment -> results.json
uv run python3 sim09_curvature_channel/sim09.py sweep_plot   # parameter sweeps -> output/*.png
uv run python3 sim09_curvature_channel/sim09.py selftest    # fast internal sanity checks
uv run python3 sim09_curvature_channel/saturating_action_sweep.py  # Session 21 confound test
uv run python3 sim09_curvature_channel/recruit_limit_sweep.py  # Session 20 2x2 isolation
uv run python3 sim09_curvature_channel/dstar_sweep.py          # Session 19 d* sweep
```

Visualization: [visualize.html](https://alife.vancedubberly.com/simulations/sim09_curvature_channel/visualize.html) — fetches `results.json` and the optional `output/sweep_data.json`.
