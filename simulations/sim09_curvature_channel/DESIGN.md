# Sim09: The Curvature Channel — Does a Non-Saturating Channel That Recruits as Well as Limits Fire the Crossing?

> **Audience:** This is an implementation spec for a coding model (GLM 5.2) that will
> build the simulation in Python over multiple nightly sessions, one *Part* per
> session. Each Part is written to be **independently implementable without having
> read the others**. Read the "How to use this document" section first, then find
> the first unchecked Part in the Progress Tracker and implement only that Part.

---

## How to use this document (READ THIS FIRST, EVERY SESSION)

1. Open the **Progress Tracker** near the top. Find the FIRST Part whose checkbox is
   unchecked (`[ ]`).
2. Read only:
   - This "How to use" section
   - The "Scientific framing" section (short — gives you the *why*)
   - The "Global conventions" section (file layout, CLI, JSON, coding rules)
   - The full text of the ONE Part you are implementing
   - The "Data contract" for any earlier Part your Part depends on (each Part lists
     its dependencies and the exact function signatures / data shapes it consumes).
3. Implement that Part. Every Part ends with a **Definition of Done** checklist and a
   **Verification command** you must run. Do not mark a Part done until its
   verification command runs clean.
4. When done, edit THIS file: change that Part's checkbox from `[ ]` to `[x]` and add
   a one-line note (date + what you did) under "Session log" at the bottom.
5. Commit your work (the nightly cron handles git/deploy separately; you just leave
   the files in place). Stop. Do not start the next Part in the same session.

**Golden rules for a less-capable model working here:**
- Do ONE Part per session. Do not try to build the whole thing at once.
- Do NOT refactor code from earlier Parts unless a Part explicitly tells you to.
- Every Part is additive: you add functions/classes to `sim09.py`, you do not rewrite
  what exists. If a function already exists from a prior Part, reuse it; do not
  duplicate it.
- Prefer plain Python + numpy. No new dependencies beyond numpy (already in
  `../pyproject.toml`). Do not add matplotlib imports until Part 7 (visualization).
- Keep it deterministic: every stochastic function takes a `seed` or uses a passed-in
  `numpy.random.Generator`. Never call the global `numpy.random` or `random` without a
  seed.
- If you get stuck on a Part, implement the simplest correct version that passes the
  Definition of Done. Do not gold-plate.

---

## Progress Tracker

- [ ] **Part 1** — Project skeleton: files, CLI dispatcher, config, RNG, grid, JSON writer
- [ ] **Part 2** — Termite agents: state, movement, state-gated curvature routing (the deposit/excavate split)
- [ ] **Part 3** — The material field: curvature computation, smoothing, erosion, roughness feedback
- [ ] **Part 4** — Core simulation loop + metrics collection (history records)
- [ ] **Part 5** — The trace→actor crossing detector (H7's three criteria, adapted to curvature)
- [ ] **Part 6** — Experiment conditions + `run` command (baseline-pheromone vs curvature-channel)
- [ ] **Part 7** — Parameter sweeps + `sweep_plot` (the `d` phase-transition sweep — the headline plot)
- [ ] **Part 8** — Perturbation / self-repair experiment (the H7 acid test, applied to the curvature channel)
- [ ] **Part 9** — `visualize.html` (HTML5 Canvas, self-contained) + README.md

Each Part below is self-contained. Do the first unchecked one.

---

## Scientific framing (short — this is the *why*)

This simulation is the next step in the project's spiral-loop investigation of
**H7, the Trace→Actor Crossing Hypothesis**. The arc so far:

- **sim06** (termite mound, saturating cement pheromone): positive feedback builds
  66% more structure under self-maintenance, but the crossing detector's near-miss
  (stability 0.849–0.893 vs a 0.90 threshold) plus a *reversal* — self-maintenance is
  *more* fragmented than baseline — pointed at the deposit rule's saturating response
  `p = base + gain·φ/(1+φ)`, which is flat above φ≈1 and destroys the spatial contrast
  stigmergy needs.
- **sim07** (scalar structure-sourced transport): the null deepened — venting
  pheromone *away* from saturated regions dispersed the very cue that recruits
  deposits. Structure-sourced *scalar* transport has the wrong sign for
  consolidation; it fragments.
- **sim08** (non-saturating density cap): confirmed H11's *direction* — a hard
  action-gate de-saturates the cue field and prunes nucleation (pillars 101→52,
  max pheromone 8.01→2.50) — but the crossing does not fire, because a pure limiter
  reduces growth *volume* without recruiting *maintenance* (stability doesn't rise).

**H7's Session-13/14 refinement (the load-bearing claim sim09 tests):** the crossing
needs a **non-saturating channel that RECRUITS as well as LIMITS**. The curvature
channel — the one real termites actually use — does both: depositing at a convex tip
*extends* the tip (recruits further building there), and a smoothing term caps feature
size (limits). It is also the minimal lumped form of the "directed transport"
H7's Session-10 refinement called for: curvature *is* directed geometry.

**The published substrate (Facchini, Lazarescu, Perna & Douady 2020, J R Soc
Interface 17:20200093):** a curvature-only phase-field growth model for arboreal
*Nasutitermes* nests with **no pheromone field at all**:

```
∂f/∂t ≈ f(1−f) · [ (1/2)·Δf  +  d·Δ²f ]
```

- The growth term `(1/2)·Δf` (mean curvature of the height field) is the **recruit**
  mechanism — positive at convex tips (growth extends the structure outward).
- The smoothing term `d·Δ²f` (biharmonic) is the **limit** mechanism — caps feature
  size, mimicking the pellet-size cutoff.
- The prefactor `f(1−f)` restricts growth to the *surface* (the structure boundary),
  not the bulk — spatial selectivity without a saturating cue.
- For large `d` the equation is **linearly unstable**: walls expand, branch, merge,
  and invade space — the consolidation morphology sim06 never reached.

Facchini et al. 2024 (eLife 13:86843) then showed *why* curvature works: evaporation
flux ∝ surface curvature (Langmuir 1918), so the curvature and humidity channels are
**one physical quantity**. They explicitly state "experiments do not support a role
for a putative cement pheromone" — two independent groups now. H11 is corroborated at
the level of *sufficiency* (biology doesn't need the pheromone), not just absence.

**The convex/concave resolution (a methodological warning for sim09):** Calovi 2019
measured *aggregate* activity (digging + building) and found it at concavities;
Facchini 2024 isolated pellet *deposition* and found it at convex tips. Both are
curvature-driven; the *action component* differs. **sim09 must separate deposit
(loaded termites at convex tips) from excavate (unloaded termites at concavities).**
Conflating them — as a single "build" action — would invert the rule's sign. This is
the single most important design constraint in this document.

**What sim09 must demonstrate (the deliverable finding):**
- A **baseline-pheromone** condition (sim06's saturating Grassé rule) that
  consolidates weakly or not at all — the control.
- A **curvature-channel** condition (the Facchini rule: state-gated deposit at convex
  tips, excavate at concavities, smoothing term `d`) that consolidates morphology
  AND fires the crossing detector, AND recovers from perturbation.
- A **phase transition in `d`**: below the curvature-instability threshold, diffuse
  growth (sim06 regime, no crossing); above it, consolidated morphology + the crossing.
  `d` is to sim09 what `M_c` was to sim07 — but with a mechanism that recruits where
  the scalar transport only dispersed, and a non-saturating channel where the density
  cap only limited.
- The H7 three-criteria crossing detector (carried over from sim06/sim08, adapted to
  the curvature model) firing only above the `d` instability and not below it.

**The risk (stated honestly):** Facchini's curvature model reproduces *morphology*
but does not test self-maintenance, persistence against erosion, or perturbation
repair. Reproducing the morphology is necessary but not sufficient for the crossing.
The **roughness feedback** (deposits roughen the surface, focusing further
evaporation/deposition there — Facchini 2024) is the candidate *maintenance*
mechanism that must be tested, not assumed. If sim09 consolidates morphology but
still does not fire the crossing, that is a real null — and a sharper one than sim08,
because the curvature channel has both the recruit and limit halves.

You do NOT need to reproduce real termite biology. You need a minimal model that can
exhibit — or fail to exhibit — the crossing under the curvature channel, measured
quantitatively, with a phase-transition sweep in `d`.

---

## Global conventions (apply to every Part)

### File layout
```
simulations/
  pyproject.toml                      # already exists (numpy, matplotlib) — do NOT edit
  sim09_curvature_channel/
    DESIGN.md                         # this file
    sim09.py                          # the simulation (you build this across Parts)
    README.md                         # written in Part 9
    results.json                      # produced by `run` (Part 6) — COMMITTED (site fetches it)
    visualize.html                    # written in Part 9
    output/                           # gitignored: PNGs from sweeps (Part 7)
```
Notes:
- `output/`, `*.png`, `*.mp4` are already gitignored by `../.gitignore`. Do not add a
  local `.gitignore`.
- `results.json` is **committed** (the website visualization fetches it). Write it to
  the sim folder root: `sim09_curvature_channel/results.json`. PNG plots go under
  `output/`.

### How to run (must work from the simulations/ directory)
```bash
cd ~/brain/artificial-life/simulations
uv run python3 sim09_curvature_channel/sim09.py run          # main experiment -> results.json
uv run python3 sim09_curvature_channel/sim09.py sweep_plot   # parameter sweeps -> output/*.png
uv run python3 sim09_curvature_channel/sim09.py selftest    # fast internal sanity checks
```
Because the script may be run from `simulations/` (cwd) rather than from the sim
folder, **always build absolute output paths from the script's own location**:
```python
import os
SIM_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SIM_DIR, "results.json")
OUTPUT_DIR = os.path.join(SIM_DIR, "output")
```
Do NOT hardcode `/home/vance/...`. Use `SIM_DIR`.

### CLI dispatcher
`sim09.py` has a single `main()` reading `sys.argv[1]`:
- `run`        → runs the full experiment, writes `results.json`, prints a summary.
- `sweep_plot` → runs parameter sweeps, writes PNGs under `output/`.
- `selftest`   → runs the cheap self-checks registered by each Part; exits non-zero on failure.
- no arg / unknown → print usage and exit 0.

Each command is a top-level function: `cmd_run()`, `cmd_sweep_plot()`, `cmd_selftest()`.
Parts add to these functions incrementally (a Part will say "append to `cmd_selftest`").

### RNG discipline
- Create generators with `rng = np.random.default_rng(seed)`.
- Pass `rng` down into every stochastic function. Never use module-level randomness.
- The default master seed is `SEED = 42`.

### JSON output shape (the data contract for the website)
Follow the established project convention (same shape as sim06/sim08): a top-level
dict with a `config` block and named conditions, each holding a `history` list of
per-timestep records. Sim09's shape (final target, fully populated by Part 6/8):
```jsonc
{
  "config": { "grid_size": 100, "n_termites": 200, "steps": 4000, "seed": 42,
              "d": 1.0, "channel": "curvature", ... },
  "baseline_pheromone":  { "history": [ <record>, ... ], "summary": { ... } },
  "curvature_channel":   { "history": [ <record>, ... ], "summary": { ... } },
  "perturbation":        { "baseline_pheromone": {...}, "curvature_channel": {...} }  // added Part 8
}
```
A `<record>` (one per sampled timestep) has these fields (Part 4 defines the base
fields; Part 5 adds the crossing fields):
```jsonc
{
  "step": 1200,
  "total_material": 5312,          // sum of material on grid
  "n_structure_cells": 410,        // cells with material above STRUCTURE_THRESHOLD
  "mean_curvature": 0.031,         // mean local curvature over structure-surface cells (Part 3/4)
  "max_curvature": 0.18,
  "roughness": 0.042,              // std of curvature over surface (the recruit proxy, Part 3)
  "n_pillars": 7,                  // connected components of structure (Part 5)
  "compactness": 0.62,             // structure compactness (Part 5)
  "deposits_this_window": 340,     // deposit events since last sample
  "excavations_this_window": 45,  // excavation events since last sample (sim09 splits the action)
  "deposits_on_convex": 280,       // deposits landing on convex (high-curvature) surface — the rule check
  "structure_stability": 0.94,    // frac of structure cells that survived the window (Part 5)
  "crossed": false,                // has the trace->actor crossing occurred yet? (Part 5)
  "crossing_step": null            // step at which crossing first detected, else null
}
```
NOTE the sim09-specific fields absent from sim06: `mean_curvature`, `max_curvature`,
`roughness`, `excavations_this_window`, `deposits_on_convex`. There is NO `mean_pheromone`
field in the curvature_channel condition — that condition has no pheromone field. Keep
the record schema **unioned** across conditions: a condition that doesn't use a field
writes it as `0` / `0.0` / `null` rather than omitting it. This keeps the visualization
and the detector uniform. (The baseline_pheromone condition DOES carry a pheromone field;
it may report `mean_pheromone` but should still report `mean_curvature` of its material
field so the two are comparable. See Part 4.)

Sample history every `SAMPLE_EVERY` steps (default 25) to keep the file reasonable
(~160 records per condition at 4000 steps). Use `json.dump(..., indent=2)`. Cast numpy
scalars to Python `float`/`int` before dumping (helper below). NEVER emit `Infinity` or
`NaN` — `JSON.parse` rejects them; use `null` instead.

### Numpy → JSON helper (put in Part 1)
```python
def _pyify(x):
    """Recursively convert numpy scalars/arrays to JSON-native types."""
    import numpy as _np
    if isinstance(x, dict):  return {k: _pyify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [_pyify(v) for v in x]
    if isinstance(x, _np.generic): return x.item()
    if isinstance(x, _np.ndarray): return x.tolist()
    return x
```
Always call `json.dump(_pyify(results), f, indent=2)`.

### Coding style
- One file, `sim09.py`. Reasonable functions, small classes. No external state files
  except `results.json` and PNGs.
- Add a module docstring at the top (Part 1) describing the sim and its hypothesis.
- Keep the whole `run` under ~2 minutes wall-clock at default params (grid 100x100,
  200 termites, 4000 steps, 2 conditions). If it's too slow, reduce steps to 3000 —
  correctness over scale. Use numpy vectorization for curvature/erosion/smoothing.
- The Laplacian `Δf` and biharmonic `Δ²f` on a 2D grid are the workhorses. Implement
  them with `np.roll` on a toroidal grid (see Part 3) — do NOT add scipy.

---

## Part 1 — Project skeleton

**Goal:** Create `sim09.py` with the module docstring, imports, global constants, the
`_pyify` helper, an RNG helper, a minimal `Field` container, the CLI dispatcher, and
a `cmd_selftest()` that (for now) just asserts imports and constants exist.

**Dependencies:** none.

**Implement:**
1. Module docstring: 1 paragraph describing sim09 (the curvature channel, the
   Facchini 2020 growth model, state-gated deposit/excavate, testing H7's
   "non-saturating channel that recruits as well as limits" prescription, with `d` as
   the phase-transition parameter) — paraphrase the "Scientific framing" section.
2. Imports: `import os, sys, json, math, time` and `import numpy as np`. Do NOT import
   matplotlib here (Part 7 does that lazily inside its function).
3. Path constants: `SIM_DIR`, `RESULTS_PATH`, `OUTPUT_DIR` (see Global conventions).
   `os.makedirs(OUTPUT_DIR, exist_ok=True)` inside the functions that write PNGs, not at
   import time.
4. Simulation constants (module level, used as defaults everywhere):
   ```python
   GRID_SIZE = 100
   N_TERMITES = 200
   STEPS = 4000
   SAMPLE_EVERY = 25
   SEED = 42

   # Material field / curvature-channel parameters (the Facchini model, 2D)
   D_SMOOTH = 1.0               # the d parameter — smoothing strength / phase-transition knob
   MATERIAL_DECAY = 0.0005      # slow background erosion (same role as sim06)
   STRUCTURE_THRESHOLD = 1.0    # material level above which a cell counts as "structure"
   PELLET = 1.0                 # material added per deposit, removed per excavation
   SURFACE_THRESHOLD = 0.05     # material above which a cell is "on the structure surface" (for f(1-f))

   # Agent / curvature-routing parameters
   RELOAD_PROB = 0.3            # prob an unloaded termite refills off-grid (same as sim06)
   CURVE_FOLLOW = 0.6           # prob a termite follows the curvature cue (vs random step)
   DEPOSIT_PROB_BASE = 0.10     # baseline deposit probability (nucleation on bare ground)
   DEPOSIT_PROB_GAIN = 0.85     # curvature-driven deposit probability gain (non-saturating routing)
   EXCAVATE_PROB_BASE = 0.05    # baseline excavation probability at concavities
   EXCAVATE_PROB_GAIN = 0.60    # curvature-driven excavation probability gain
   PICKUP_PROB_BASE = 0.01      # prob an unloaded termite erodes a structure cell (turnover)

   # Baseline-pheromone condition (sim06's saturating rule, for the control comparison)
   PHEROMONE_DECAY = 0.02
   PHEROMONE_DIFFUSE = 0.10
   DEPOSIT_PHEROMONE = 1.0
   DEPOSIT_BASE = 0.10          # pheromone-condition deposit base (saturating rule)
   DEPOSIT_GAIN = 0.85         # pheromone-condition deposit gain (saturating rule)

   # Crossing detector (carried over from sim06/sim08 — Part 5 tunes)
   CROSSING_PERSIST = 4
   STAB_THRESH = 0.90
   ROUGH_ELEV_THRESH = 0.02     # crossing criterion 2 for the curvature condition:
                               # roughness (curvature std over surface) sustained above this
   PHERO_ELEV_THRESH = 0.5      # crossing criterion 2 for the pheromone condition (as sim06)
   CONSTRAIN_THRESH = 0.60
   ```
   (Later Parts reference these. If a constant you need is missing, add it here.)
   Note the **non-saturating** deposit rule for the curvature condition: deposit
   probability routes with curvature via `DEPOSIT_PROB_GAIN` but the *response shape*
   is linear in curvature (not `φ/(1+φ)`-flattening) — this is the H11 point made
   concrete. Part 2 specifies the exact formula.
5. `_pyify` helper (from Global conventions).
6. `make_rng(seed=SEED)` returning `np.random.default_rng(seed)`.
7. A minimal field container (extended in Part 3):
   ```python
   class Field:
       """Holds the 2D material field the curvature channel acts on, plus an optional
       pheromone field for the baseline-pheromone control condition."""
       def __init__(self, size):
           self.size = size
           self.material = np.zeros((size, size), dtype=np.float64)   # deposited soil (the f field)
           self.pheromone = None  # set to a np.zeros grid only in the baseline_pheromone condition
   ```
8. CLI:
   ```python
   def cmd_run(): print("cmd_run not implemented yet (Part 6)")
   def cmd_sweep_plot(): print("cmd_sweep_plot not implemented yet (Part 7)")
   def cmd_selftest():
       # Part 1 checks:
       assert GRID_SIZE > 0 and N_TERMITES > 0 and STEPS > 0
       f = Field(GRID_SIZE)
       assert f.material.shape == (GRID_SIZE, GRID_SIZE)
       assert _pyify({"a": np.float64(1.5)}) == {"a": 1.5}
       print("selftest: Part 1 OK")

   def main():
       cmd = sys.argv[1] if len(sys.argv) > 1 else ""
       if cmd == "run": cmd_run()
       elif cmd == "sweep_plot": cmd_sweep_plot()
       elif cmd == "selftest": cmd_selftest()
       else:
           print("usage: sim09.py [run|sweep_plot|selftest]")

   if __name__ == "__main__":
       main()
   ```

**Definition of Done:**
- [ ] `sim09.py` exists with docstring, imports, constants, `_pyify`, `make_rng`,
      `Field`, and the CLI dispatcher.
- [ ] Running the verification command prints `selftest: Part 1 OK` and exits 0.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && uv run python3 sim09_curvature_channel/sim09.py selftest
```

---

## Part 2 — Termite agents (state-gated curvature routing)

**Goal:** Add termite agents that move on the grid, carry at most one soil pellet, and
follow the **state-gated curvature rule** — the load-bearing distinction from the
Facchini/Calovi resolution. Loaded termites deposit at convex tips; unloaded termites
excavate at concavities. This Part defines agent *behavior in isolation* — it does not
yet run a full loop (Part 4 does).

**Dependencies:** Part 1 (`Field`, constants, `make_rng`).

**Data contract you consume:** `Field` with `.material` numpy grid (and `.pheromone`
which is `None` in the curvature condition, a grid in the baseline condition). The
curvature field is computed from `material` in Part 3; Part 2 receives the curvature
array as an argument to `termite_step` (Part 4 wires `compute_curvature` →
`termite_step`). For Part 2's selftest, build a synthetic curvature array directly.

**The convex/concave resolution (the rule, in one place):** Facchini 2024 found
*deposition* at convex tips (high positive curvature); Calovi 2019 found *aggregate
activity* at concavities, which includes *excavation* at concave pits (high negative
curvature / low curvature). The state-gating: a **loaded** termite deposits at high
curvature; an **unloaded** termite excavates at low curvature. sim06 had only deposit;
sim09 splits the action. Conflating them would invert the rule's sign — do not.

**Model of a termite (vectorized, as in sim06):**
```python
class Termites:
    def __init__(self, n, size, rng):
        self.n = n
        self.size = size
        self.x = rng.integers(0, size, n)          # int array
        self.y = rng.integers(0, size, n)
        self.loaded = np.zeros(n, dtype=bool)       # carrying a pellet?
```

**Movement:** each step, every termite takes a random step to one of 8 neighbours
(Moore neighbourhood) with toroidal wrap-around (`% size`). Bias movement up the
curvature gradient when **loaded** (loaded termites are attracted to convex tips —
the deposit-recruitment positive feedback) and down the curvature gradient when
**unloaded and seeking** (unloaded termites are attracted to concavities — the
excavation sites). Implementation guidance:
- Loaded termites: with probability `CURVE_FOLLOW`, move toward the neighbour with
  the *highest* curvature (ties → random among the max); otherwise random step.
- Unloaded termites: with probability `CURVE_FOLLOW`, move toward the neighbour with
  the *lowest* curvature; otherwise random step.
- Keep it vectorized if you can; a Python loop over `n=200` termites for ~4000 steps
  is acceptable (~800k iterations). Correctness first.

**Reload (off-grid sourcing) — same as sim06:** an unloaded termite becomes loaded
with probability `RELOAD_PROB` each step *regardless of cell* (models fetching soil
from an off-grid source). This is the primary way termites become loaded.

**Deposit rule (loaded termite on a cell — the Facchini recruit mechanism):**
- Deposit probability increases with local curvature (positive feedback that
  EXTENDS the convex tip — non-saturating because each deposit changes the
  curvature):
  ```
  local = curvature[y, x]
  p_deposit = deposit_prob_base + deposit_prob_gain * local   # LINEAR, not φ/(1+φ)
  ```
  with `deposit_prob_base = params.get("deposit_prob_base", DEPOSIT_PROB_BASE)`,
  `deposit_prob_gain = params.get("deposit_prob_gain", DEPOSIT_PROB_GAIN)`. The
  linear (not saturating) form is the H11 prescription made concrete. Clamp
  `p_deposit` to `[0, 1]` before the Bernoulli draw.
- **Surface restriction (the `f(1−f)` prefactor, action-based):** a loaded termite
  deposits only if the cell is on the structure surface — `material[y,x] > 0` OR
  an adjacent cell has `material > SURFACE_THRESHOLD` (i.e. it is at the edge of
  existing structure, not in open air or in the bulk). This is the spatial selectivity
  the prefactor gives, without a saturating cue. On bare ground far from structure,
  fall back to `DEPOSIT_PROB_BASE` nucleation probability (so the first pillars can
  seed). A simple implementation: compute a boolean `on_surface` mask in Part 3
  (dilation of the structure mask by one cell, OR'd with bare-ground-adjacent);
  pass it to `termite_step`. For Part 2's selftest, build a synthetic mask.
- On deposit: `material[y,x] += PELLET`, set `loaded=False`. Count
  `deposits_on_convex += 1` if `curvature[y,x] > 0` (for the rule-check metric and
  criterion 3 — see Part 5).

**Excavate rule (unloaded termite on a concavity — the Calovi/Facchini limit
mechanism):**
- An unloaded (seeking) termite at a concavity (`curvature[y,x] < 0` and
  `material[y,x] > 0`) excavates with probability:
  ```
  p_excavate = excavate_prob_base + excavate_prob_gain * (-curvature[y,x])
  ```
  clamped to `[0,1]`. On excavate: `material[y,x] -= PELLET` (clamp at 0), set
  `loaded=True` (the termite now carries the excavated pellet). Count
  `excavations_this_window += 1`.
- Keep excavation rarer than deposit (lower gains/base) so the structure grows net;
  excavation provides turnover and the concavity-fill negative feedback.

**Functions to implement:**
```python
def termite_step(termites: "Termites", field: "Field", rng, params: dict,
                 curvature: np.ndarray, on_surface: np.ndarray) -> dict:
    """Advance ALL termites one step: move, maybe reload, maybe deposit/excavate.
    `curvature`: the local mean-curvature field (computed in Part 3 / passed by Part 4).
    `on_surface`: boolean mask of structure-surface cells (computed in Part 3 / passed by Part 4).
    Returns a small dict of per-step event counts:
        {"deposits": int, "excavations": int, "deposits_on_convex": int, "pickups": int}
    `params` overrides constants (see Part 6). Fall back to the module constant when a
    key is absent, e.g. deposit_prob_base = params.get("deposit_prob_base", DEPOSIT_PROB_BASE).
    """
```
Make `termite_step` read ALL tunables from `params` with constant fallbacks:
`curve_follow, reload_prob, deposit_prob_base, deposit_prob_gain, excavate_prob_base,
excavate_prob_gain, pellet, pickup_prob_base, surface_threshold`. This lets Part 6/7/8
sweep them without touching this code.

**Also implement the baseline-pheromone deposit rule** (sim06's saturating rule, used
only in the baseline condition so the comparison is apples-to-apples):
```python
def termite_step_pheromone(termites, field, rng, params) -> dict:
    """sim06's Grassé rule for the baseline_pheromone condition: loaded termites
    deposit with p = deposit_base + deposit_gain * local_pheromone/(1+local_pheromone),
    follow the pheromone gradient when loaded, reload off-grid. No curvature routing,
    no excavation. Returns {"deposits": int, "pickups": int, "deposits_on_structure": int}."""
```
This is essentially sim06's `termite_step` transcribed. The baseline condition uses
`field.pheromone` (a grid); the curvature condition does not. Part 4 dispatches on
`params["channel"]`.

**Append to `cmd_selftest`:** create a Field, Termites(50, ...), a synthetic curvature
field (e.g. a Gaussian bump in the center → positive curvature at the rim, negative at
the center), a synthetic `on_surface` mask (True near the bump), run `termite_step`
100 times, assert `field.material.sum() > 0` (deposits happened), that `loaded` is a
bool array of length 50, and that at least some `deposits_on_convex` were counted when
the bump rim has positive curvature. Print `selftest: Part 2 OK`.

**Definition of Done:**
- [ ] `Termites` class, `termite_step` (curvature, state-gated) and `termite_step_pheromone`
      (baseline) implemented, fully parameterized via `params`.
- [ ] `termite_step` splits deposit (loaded, convex) from excavate (unloaded, concave).
- [ ] After 100 steps in selftest, material has accumulated (`sum > 0`) and
      `deposits_on_convex > 0` on a convex-bump curvature field.
- [ ] Verification command prints both `Part 1 OK` and `Part 2 OK`, exits 0.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && uv run python3 sim09_curvature_channel/sim09.py selftest
```

---

## Part 3 — The material field: curvature, smoothing, erosion, roughness feedback

**Goal:** Give the `Field` its own dynamics — the Facchini growth equation adapted to
the 2D grid + agent framework. Compute the local mean curvature, apply the smoothing
term (`d`), apply background erosion, and compute the roughness (curvature std over
the surface) that is the **recruit proxy** and the crossing detector's input. This
Part implements the *environment's* rules — the non-saturating "actor candidate."

**Dependencies:** Part 1 (`Field`, constants).

**Implement:**

1. **`compute_curvature(field, params)` → `np.ndarray` (same shape as material):**
   the local mean curvature of the material height field, approximated as half the
   Laplacian of a smoothed material field. On a 2D toroidal grid with `np.roll`:
   ```python
   def _laplacian(a):
       # 5-point stencil on a torus: center - 4-neighbour mean
       return (np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1) - 4.0*a)
   def compute_curvature(field, params):
       m = field.material
       # curvature ≈ (1/2) * Laplacian(m), but only meaningful near the surface.
       # Use a light smoothing of m first to avoid grid noise dominating.
       smooth_m = _diffuse(m, 0.2)   # the 3x3 toroidal blur from sim06, rate 0.2
       return 0.5 * _laplacian(smooth_m)
   ```
   Positive curvature = convex (tip/growth site); negative = concave (pit/excavation
   site). This is the `(1/2)·Δf` term.

2. **`_diffuse(a, rate)` — toroidal 3x3 blur** (copy verbatim from sim06/sim08; it is
   the project's standard diffusion):
   ```python
   def _diffuse(a, rate):
       nb = (np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1)
             + np.roll(np.roll(a,1,0),1,1)+np.roll(np.roll(a,1,0),-1,1)
             + np.roll(np.roll(a,-1,0),1,1)+np.roll(np.roll(a,-1,0),-1,1)) / 8.0
       return (1-rate)*a + rate*nb
   ```

3. **`compute_on_surface(field, params)` → `np.ndarray` (boolean):** the surface
   mask — cells where `material > 0` OR adjacent (Moore) to a structure cell
   (`material > structure_threshold`). This is the `f(1−f)` prefactor made operational
   (deposits happen at edges, not bulk or open air). Vectorize with `np.roll`:
   ```python
   def compute_on_surface(field, params):
       thr = params.get("structure_threshold", STRUCTURE_THRESHOLD)
       struct = field.material > thr
       # dilate struct by one Moore-neighbourhood
       dil = struct.copy()
       for dy in (-1,0,1):
           for dx in (-1,0,1):
               dil |= np.roll(np.roll(struct, dy, 0), dx, 1)
       on_surface = (field.material > 0) | dil
       return on_surface
   ```
   (Bare ground far from structure is False → deposits there use only the
   `DEPOSIT_PROB_BASE` nucleation path in Part 2, not the surface-gated path.)

4. **`field_step(field, params)` — advance the environment one step:**
   - **Material erosion (background decay):**
     `field.material *= (1.0 - material_decay)` with
     `material_decay = params.get("material_decay", MATERIAL_DECAY)`. (Same role as
     sim06: the slow erosion the structure must overcome to persist.)
   - **Smoothing (the `d·Δ²f` limit term):** apply a small biharmonic smoothing to the
     material field, gated by `d`:
     ```python
     d = params.get("d", D_SMOOTH)
     lap = _laplacian(field.material)
     biharmonic = _laplacian(lap)   # Δ²f
     field.material += d * 0.0001 * biharmonic   # small timestep; tune the prefactor
     field.material = np.clip(field.material, 0, None)
     ```
     The prefactor `0.0001` keeps the explicit step stable on a 100x100 grid; Part 7
     sweeps `d` over a range that crosses the instability. The smoothing term caps
     feature size — the LIMIT mechanism. (If the explicit biharmonic is unstable at
     the default `d`, reduce the prefactor or sub-step it; document the choice in the
     session log. Correctness over fidelity.)
   - **Pheromone field dynamics (baseline condition only):** if
     `params.get("channel") == "baseline_pheromone"` and `field.pheromone is not None`,
     apply sim06's pheromone decay + diffusion (copy from sim06/sim08):
     ```python
     if params.get("channel") == "baseline_pheromone" and field.pheromone is not None:
         decay = params.get("pheromone_decay", PHEROMONE_DECAY)
         field.pheromone *= (1.0 - decay)
         field.pheromone = _diffuse(field.pheromone, params.get("pheromone_diffuse", PHEROMONE_DIFFUSE))
     ```
     The curvature condition skips this entirely — it has no pheromone field.

5. **`compute_roughness(field, params, curvature, on_surface)` → float:** the
   standard deviation of curvature over the surface cells (the recruit proxy —
   Facchini 2024: deposits roughen the surface, focusing further evaporation/
   deposition there). Return `0.0` if no surface cells:
   ```python
   def compute_roughness(field, params, curvature, on_surface):
       mask = on_surface & (field.material > 0)
       if mask.sum() == 0: return 0.0
       return float(curvature[mask].std())
   ```

**Why this is the experiment's crux:** baseline_pheromone = the saturating cue field
that H11 flags as self-defeating. curvature_channel = the non-saturating geometry
channel that recruits (convex-tip growth extends the tip) AND limits (smoothing caps
size), with no cue to saturate. Part 5 detects whether/when the curvature channel
crosses.

**Append to `cmd_selftest`:** put a blob of material in the center, compute
curvature, assert the rim has positive curvature and the center has near-zero or
negative curvature. Run `field_step` (curvature params) 50 times, assert the blob
has smoothed (max curvature decreased) and eroded (total material decreased).
Compute `on_surface` and assert it is True around the blob rim. Compute `roughness`
and assert it is a non-negative float. Print `selftest: Part 3 OK`.

**Definition of Done:**
- [ ] `compute_curvature`, `compute_on_surface`, `compute_roughness`, `field_step`
      implemented. `_diffuse` and `_laplacian` present.
- [ ] `field_step` applies erosion, the `d`-gated biharmonic smoothing, and (baseline
      only) pheromone decay/diffusion.
- [ ] selftest confirms a blob has positive rim curvature, smooths and erodes under
      `field_step`, and has a non-negative roughness. Prints `Part 3 OK`.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && uv run python3 sim09_curvature_channel/sim09.py selftest
```

---

## Part 4 — Core simulation loop + metrics

**Goal:** Wire termites + field into one loop, sample metrics every `SAMPLE_EVERY`
steps, and produce a `history` list of records matching the Data contract (minus the
crossing fields, which Part 5 fills in — include them as `False`/`None` placeholders
here so Part 5 can upgrade).

**Dependencies:** Part 2 (`Termites`, `termite_step`, `termite_step_pheromone`),
Part 3 (`Field`, `field_step`, `compute_curvature`, `compute_on_surface`,
`compute_roughness`), Part 1 constants.

**Implement `run_condition(params, seed)` → dict:**
```python
def run_condition(params, seed):
    """Run one full simulation condition. Returns {"history": [...], "summary": {...}}."""
    rng = make_rng(seed)
    size   = params.get("grid_size", GRID_SIZE)
    n      = params.get("n_termites", N_TERMITES)
    steps  = params.get("steps", STEPS)
    sample = params.get("sample_every", SAMPLE_EVERY)
    channel = params.get("channel", "curvature")   # "curvature" or "baseline_pheromone"

    field = Field(size)
    if channel == "baseline_pheromone":
        field.pheromone = np.zeros((size, size), dtype=np.float64)
    termites = Termites(n, size, rng)
    history = []
    dep_acc = exc_acc = dep_convex_acc = pick_acc = 0
    prev_structure_mask = None

    for step in range(steps):
        if channel == "curvature":
            curvature = compute_curvature(field, params)
            on_surface = compute_on_surface(field, params)
            ev = termite_step(termites, field, rng, params, curvature, on_surface)
            field_step(field, params)
            dep_acc += ev["deposits"]; exc_acc += ev["excavations"]
            dep_convex_acc += ev["deposits_on_convex"]; pick_acc += ev["pickups"]
        else:  # baseline_pheromone
            ev = termite_step_pheromone(termites, field, rng, params)
            field_step(field, params)
            dep_acc += ev["deposits"]; pick_acc += ev["pickups"]

        if step % sample == 0:
            rec = compute_metrics(field, params, step, dep_acc, exc_acc,
                                  dep_convex_acc, pick_acc, prev_structure_mask)
            history.append(rec)
            dep_acc = exc_acc = dep_convex_acc = pick_acc = 0
            prev_structure_mask = (field.material > params.get("structure_threshold",
                                          STRUCTURE_THRESHOLD)).copy()

    summary = summarize(history)
    return {"history": history, "summary": summary}
```

**Implement `compute_metrics(field, params, step, deposits, excavations,
deposits_on_convex, pickups, prev_mask)` → record dict** with fields: `step,
total_material, n_structure_cells, mean_curvature, max_curvature, roughness,
mean_pheromone (0.0 if no pheromone field), max_pheromone, deposits_this_window,
excavations_this_window, deposits_on_convex_this_window, pickups_this_window,
structure_stability`. Also compute `structure_stability`: fraction of `prev_mask`
cells still above threshold now (1.0 on the first sample when `prev_mask is None`).
Leave `n_pillars`, `compactness`, `crossed`, `crossing_step` as `0`, `0.0`, `False`,
`None` here — **Part 5 upgrades this function** to fill them. (Write
`compute_metrics` so Part 5 can extend it; put a clear comment
`# --- Part 5 fills n_pillars/compactness/crossing below ---`.) For the curvature
condition compute `mean_curvature`/`max_curvature`/`roughness` from
`compute_curvature`/`compute_roughness` over the surface; for the baseline condition
compute them too (so the two conditions are comparable on the same axes) and set
`mean_pheromone`/`max_pheromone` from the pheromone field.

**Implement `summarize(history)` → dict:** final `total_material`, final
`n_structure_cells`, peak `total_material` and the step it occurred, mean
`structure_stability` over the last 25% of samples, and `retention` =
`final_total_material / peak_total_material` (0..1; high = structure persisted, low =
it eroded away). These summary numbers are the headline comparison between conditions.

**Wire `cmd_run` minimally now** (Part 6 expands it): run ONE curvature condition,
write `{"config": {...}, "curvature_channel": run_condition(curvature_params, SEED)}`
to `results.json` via `_pyify`, print the summary. This gives an end-to-end smoke test
before adding the second condition.

**Append to `cmd_selftest`:** run `run_condition` with tiny params
(`grid_size=30, n_termites=20, steps=200, sample_every=25, channel="curvature"`),
assert `len(history) >= 4` and each record has the required keys. Print `Part 4 OK`.

**Definition of Done:**
- [ ] `run_condition`, `compute_metrics`, `summarize` implemented; `cmd_run` writes a
      valid `results.json` with a `curvature_channel.history`.
- [ ] `selftest` prints `Part 4 OK`.
- [ ] `run` completes and `results.json` parses as JSON with
      `data["curvature_channel"]["history"]` being a non-empty list.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && \
uv run python3 sim09_curvature_channel/sim09.py selftest && \
uv run python3 sim09_curvature_channel/sim09.py run && \
uv run python3 -c "import json;d=json.load(open('sim09_curvature_channel/results.json'));assert d['curvature_channel']['history'];print('run OK, records:',len(d['curvature_channel']['history']))"
```

---

## Part 5 — The trace→actor crossing detector (scientific payload, adapted to curvature)

**Goal:** This is the intellectual core. Upgrade `compute_metrics` to also compute
structure morphology (`n_pillars`, `compactness`) and implement the **crossing
detector** adapted to the curvature channel: an operational, quantitative test of
when the accumulated material structure becomes a self-maintaining actor per H7.

**Dependencies:** Part 4 (`compute_metrics`, `run_condition`). Part 1 constants.

**H7's three criteria, made operational for the curvature channel.** A crossing is
declared at the first sampled step where ALL THREE hold and stay true for at least
`CROSSING_PERSIST` consecutive samples (constant `CROSSING_PERSIST = 4`):

1. **Persistence despite erosion** — `structure_stability >= STAB_THRESH` (default
   0.90): ≥90% of structure cells survive window-to-window even though
   `material_decay` is eroding everything. The structure is maintaining itself, not
   just accreting. (Same as sim06/sim08.)
2. **Non-reducible dynamics** — the recruit channel is self-sustaining. For the
   **curvature** condition: `roughness >= ROUGH_ELEV_THRESH` (default 0.02) **while
   the structure's mass is saturating** (`|material_growth_rate| < 0.01`, computed as
   the abs delta of `total_material` between consecutive samples divided by the
   window size — i.e. the surface's curvature variation stays elevated without
   continued net accumulation). This is the curvature analog of sim06's corrected
   criterion 2: the field stays energized by the structure's own shape, not by
   ongoing fresh deposits. For the **baseline_pheromone** condition: use sim06's
   corrected criterion 2 — `mean_pheromone >= PHERO_ELEV_THRESH` AND mass saturating
   (so the two conditions share the "non-reducible dynamics" logic but through their
   respective fields). Add `material_growth_rate` to each record (null on the first
   sample; NOT `inf`).
3. **Constraint on agents** — for the curvature condition, the fraction of deposits
   landing on convex (high-curvature) surface cells
   (`deposits_on_convex_fraction = deposits_on_convex_this_window / max(1,
   deposits_this_window)`) is high (`>= CONSTRAIN_THRESH`, default 0.6): the
   structure's curvature is channeling where termites deposit. (For the baseline
   condition, use sim06's `deposit_on_structure_fraction >= CONSTRAIN_THRESH` —
   deposits landing on already-structure cells. Part 2's `termite_step_pheromone`
   returns `deposits_on_structure` for this.)

Store per-record: `n_pillars`, `compactness`, `deposits_on_convex_fraction` (or
`deposit_on_structure_fraction` for baseline — store BOTH, filling the unused one
with 0.0), `material_growth_rate`, `crossed` (bool, cumulative once true),
`crossing_step` (int or null).

**Morphology metrics (same as sim06):**
- `n_pillars`: number of connected components (Moore/8-connectivity) of the boolean
  mask `material > structure_threshold`. Implement a small flood-fill / union-find in
  numpy or plain Python (do NOT add scipy). A simple iterative BFS labeling over the
  boolean grid is fine — the grid is 100x100. (Copy from sim06/sim08 if you can see
  it; otherwise re-implement.)
- `compactness`: `n_structure_cells / (bounding_box_area_of_structure)` where
  bounding box is min/max row & col of structure cells (1.0 = perfectly filled box,
  low = sparse scattered). If no structure, `0.0`.

**Crossing detection is a post-pass over `history`.** Cleanest approach: compute the
per-record fields inside `compute_metrics`, then implement
`detect_crossing(history, params)` that walks the history, tracks a run-length of
samples satisfying all three criteria (using the channel-appropriate criterion 2 and
3), and sets `crossed=True` / `crossing_step=<step>` on that record and all later
records once the run-length hits `CROSSING_PERSIST`. Call `detect_crossing` at the
end of `run_condition`, before `summarize`.

Add to `summarize`: `crossed` (bool — did this condition ever cross?) and
`crossing_step` (int or null). These two numbers, compared across baseline_pheromone
vs curvature_channel, ARE the paper result.

**Regression guard (important — learn from sim06's bug):** add to `cmd_selftest` a
synthetic-history test: build a small `history` list where all three criteria are
satisfied for `CROSSING_PERSIST` samples and assert `detect_crossing` sets
`crossed=True`. Then build three variants each negating ONE criterion and assert
`crossed` stays False for each. This is the regression test against reintroducing an
unsatisfiable criterion (sim06's original bug). Print `selftest: Part 5 OK`.

**Expected/target result (state in README later, verify qualitatively):** the
curvature_channel should cross above the `d` instability and not below it; the
baseline_pheromone should typically NOT cross (or cross late and unstably) — it is
the control that has only the saturating cue. If your defaults produce
both-crossing or neither-crossing, tune `material_decay` (raise it so baseline
erodes) and `D_SMOOTH` (so the curvature channel consolidates) — the whole point is
a *separation* between conditions and a *phase transition* in `d`. Document
whatever separation you achieve honestly; a null result is still a result, but first
try to find parameters that reveal the mechanism.

**Append to `cmd_selftest`:** run a tiny curvature condition and a tiny baseline;
assert `detect_crossing` runs without error and that records now contain `n_pillars`,
`compactness`, `crossed`, `crossing_step`, `material_growth_rate`. Run the synthetic
regression guard above. Print `Part 5 OK`.

**Definition of Done:**
- [ ] `compute_metrics` now fills `n_pillars`, `compactness`,
      `deposits_on_convex_fraction` / `deposit_on_structure_fraction`,
      `material_growth_rate`.
- [ ] `detect_crossing` implemented and called in `run_condition`; channel-aware
      (curvature uses roughness+mass-saturation; baseline uses pheromone+mass-saturation).
- [ ] `summarize` reports `crossed` and `crossing_step`.
- [ ] Regression guard passes (fires on all-true, withholds when any one criterion
      negated).
- [ ] `selftest` prints `Part 5 OK`.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && uv run python3 sim09_curvature_channel/sim09.py selftest
```

---

## Part 6 — Experiment conditions + full `run`

**Goal:** Define the two headline conditions and make `cmd_run` execute both,
assemble the full `results.json`, and print a clear comparison.

**Dependencies:** Parts 4 & 5 (`run_condition`, `summarize`, crossing fields).

**Define condition param dicts:**
```python
def curvature_params():
    return {
        "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
        "sample_every": SAMPLE_EVERY, "structure_threshold": STRUCTURE_THRESHOLD,
        "channel": "curvature",
        "d": D_SMOOTH, "material_decay": MATERIAL_DECAY,
        # (all agent/field tunables fall back to module constants)
    }

def baseline_pheromone_params():
    return {
        "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
        "sample_every": SAMPLE_EVERY, "structure_threshold": STRUCTURE_THRESHOLD,
        "channel": "baseline_pheromone",
        "pheromone_decay": PHEROMONE_DECAY, "pheromone_diffuse": PHEROMONE_DIFFUSE,
        "material_decay": MATERIAL_DECAY,
        "deposit_base": DEPOSIT_BASE, "deposit_gain": DEPOSIT_GAIN,
        # (no curvature routing; no excavation)
    }
```

**Rewrite `cmd_run`:**
```python
def cmd_run():
    t0 = time.time()
    print("Running curvature_channel (non-saturating recruit+limit)...")
    curv = run_condition(curvature_params(), seed=SEED)
    print("Running baseline_pheromone (saturating cue control)...")
    base = run_condition(baseline_pheromone_params(), seed=SEED)

    results = {
        "config": {
            "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
            "sample_every": SAMPLE_EVERY, "seed": SEED,
            "d": D_SMOOTH, "material_decay": MATERIAL_DECAY,
            "structure_threshold": STRUCTURE_THRESHOLD,
        },
        "curvature_channel": curv,
        "baseline_pheromone": base,
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(_pyify(results), f, indent=2)

    # Comparison printout — this is the headline finding
    def line(name, r):
        s = r["summary"]
        print(f"  {name:20s} crossed={str(s['crossed']):5s} "
              f"crossing_step={s['crossing_step']} "
              f"retention={s['retention']:.2f} "
              f"final_cells={s['final_n_structure_cells']}")
    print("\n=== RESULT: Trace -> Actor Crossing (H7) — curvature channel ===")
    line("curvature_channel", curv)
    line("baseline_pheromone", base)
    print(f"\nWrote {RESULTS_PATH}  ({time.time()-t0:.1f}s)")
```
(Adjust summary key names to whatever you used in `summarize` — keep them consistent.)

**Definition of Done:**
- [ ] `cmd_run` runs both conditions, writes full `results.json` with `config`,
      `curvature_channel`, `baseline_pheromone`.
- [ ] The comparison printout shows `crossed` / `crossing_step` / `retention` for both.
- [ ] Total runtime under ~2 min at defaults (reduce `STEPS` to 3000 if needed).

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && \
uv run python3 sim09_curvature_channel/sim09.py run && \
uv run python3 -c "import json;d=json.load(open('sim09_curvature_channel/results.json'));print('curvature crossed:',d['curvature_channel']['summary']['crossed']);print('baseline crossed:',d['baseline_pheromone']['summary']['crossed'])"
```

---

## Part 7 — Parameter sweeps + `sweep_plot` (the `d` phase transition)

**Goal:** Show HOW the crossing depends on `d` — the headline phase-transition plot
— and produce PNG plots. This is the quantitative-results requirement and the
core scientific deliverable of sim09.

**Dependencies:** Part 6 (`run_condition`, param builders). Imports matplotlib LAZILY
inside `cmd_sweep_plot` (`import matplotlib; matplotlib.use("Agg"); import
matplotlib.pyplot as plt`). Do NOT import at module top.

**Sweeps (run with reduced cost — `steps≈2000`, `grid_size=80` to keep it fast):**
1. **`d` sweep (curvature_channel) — THE HEADLINE PLOT:** sweep `d` over a range
   bracketing the Facchini instability, e.g. `[0.0, 0.2, 0.5, 1.0, 2.0, 4.0, 8.0]`.
   For each, record `crossed` (0/1), `crossing_step`, `retention`, `n_pillars`
   (final). Plot retention, crossing_step, and final `n_pillars` vs `d` (two panels
   or twin axes). **Expectation: a phase transition** — below some `d*`, no crossing
   and diffuse growth (many pillars, low retention); above `d*`, the crossing fires
   and morphology consolidates (few pillars, high retention). This is the sim09
   analog of sim07's `M_c` sweep, but with a mechanism that recruits. If the
   transition exists, `d*` is the phase-transition parameter H7's Session-14
   refinement predicted.
2. **`material_decay` sweep (both conditions):** sweep `material_decay` over
   `[0.0002, 0.0005, 0.001, 0.002, 0.004]`. Plot `retention` for curvature_channel vs
   baseline_pheromone on the same axes. **Expectation:** the curvature channel
   retains structure across a wider erosion range than the saturating-cue baseline
   (the separation widens with erosion — the H11 prediction).
3. (Optional, if time) **`curve_follow` sweep `[0.3, 0.5, 0.6, 0.8, 0.95]`** for the
   curvature condition: plot final `n_structure_cells` and `crossed`. Tests how
   strongly the agents must follow the curvature cue for the crossing to fire.

**Output:** save each plot to `OUTPUT_DIR` (create it): e.g.
`output/sweep_d.png`, `output/sweep_material_decay.png`. Use clear titles, axis
labels, and a legend. Also dump the raw sweep numbers to
`output/sweep_data.json` (handy for the write-up; `output/` is gitignored so this is
a local artifact only).

**Keep sweeps cheap.** Each sweep point is a full `run_condition`; with 7 points x
2000 steps you want each run ~5-10s. Use `grid_size=80, n_termites=150, steps=2000,
sample_every=25`. If it's too slow, drop to `steps=1500`.

**Definition of Done:**
- [ ] `cmd_sweep_plot` produces at least `sweep_d.png` and
      `sweep_material_decay.png` under `output/`.
- [ ] Uses `matplotlib.use("Agg")` (headless) — no display needed.
- [ ] Prints where it wrote the PNGs. Runs in a few minutes at most.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && \
uv run python3 sim09_curvature_channel/sim09.py sweep_plot && \
ls -la sim09_curvature_channel/output/*.png
```

---

## Part 8 — Perturbation / self-repair experiment (the H7 acid test, applied to curvature)

**Goal:** The strongest test of "actor-hood": does the curvature-channel structure
*repair itself* after damage? Add a perturbation experiment: build a structure,
damage it, keep running, and measure recovery. The curvature channel should recover
(roughness feedback recruits maintenance at the scar); the baseline should recover
far less (no recruit mechanism).

**Dependencies:** Part 4 (`run_condition` internals — you'll add an option), Part 5
(metrics), Part 6 (param builders).

**Implement:** add an optional `perturb=None` argument to `run_condition` of the form
`perturb={"at": step, "frac": f}`; when set, at step `perturb_at` (default
`int(0.6*steps)`), zero out a rectangular patch of `field.material` (and, for the
baseline condition, `field.pheromone`) covering `perturb_frac` (default 0.25) of the
grid area (e.g. a square block near the densest structure region, or simply the
central quarter). Record in each post-perturbation record the metric
`recovery = current_total_material / pre_perturb_total_material` (capture
`pre_perturb_total_material` at the sample just before `perturb_at`). Add
`perturb_at` and `perturb_frac` to the returned summary.

(This is the ONE place you may modify an earlier Part's function — do it minimally
and keep the default `perturb=None` so Part 6 behavior is unchanged. Copy sim06/sim08's
proven pattern.)

**Add to `cmd_run`:** after the two main conditions, run the perturbation experiment
for both curvature_channel and baseline_pheromone (same `perturb` spec, `seed=SEED`)
and store under a top-level `"perturbation"` key:
```jsonc
"perturbation": {
  "curvature_channel":  { "history": [...], "summary": {..., "recovery_final": 0.93} },
  "baseline_pheromone": { "history": [...], "summary": {..., "recovery_final": 0.41} }
}
```
Compute `recovery_final` = last record's `recovery`. Print a recovery comparison line.

**The H7 interpretation (state in README):** if the curvature channel recovers
substantially more than the baseline after the SAME damage, the roughness feedback is
acting as a genuine maintenance mechanism (the recruit half doing repair), not just a
growth rule — which is the strongest evidence the curvature channel produces an
"actor," not just a morphology. If both recover equally (as sim06/sim08 found, repair
tracking the deposit rule not the proposed mechanism), the crossing claim is weakened
— state it honestly.

**Definition of Done:**
- [ ] `run_condition` accepts `perturb=None`; damage applied at the right step when set.
- [ ] `results.json` gains a `perturbation` block with curvature_channel &
      baseline_pheromone, each with `recovery_final` in its summary.
- [ ] `cmd_run` prints the recovery comparison.
- [ ] Part 6's non-perturbed behavior is unchanged (perturb defaults off).

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && \
uv run python3 sim09_curvature_channel/sim09.py run && \
uv run python3 -c "import json;d=json.load(open('sim09_curvature_channel/results.json'));p=d['perturbation'];print('curvature recovery:',p['curvature_channel']['summary']['recovery_final']);print('baseline recovery:',p['baseline_pheromone']['summary']['recovery_final'])"
```

---

## Part 9 — visualize.html + README.md

**Goal:** Ship the interactive visualization and the documentation. Two deliverables.

**Dependencies:** a valid `results.json` from Part 6/8. **Before writing any JS, run
`run` and inspect the ACTUAL `results.json` structure** (top-level keys, the history
array path `data.curvature_channel.history`, and one sample record's field names).
Use the EXACT field paths — do not guess. (This is a hard-won project rule: prior
visualizations broke because the coder guessed the JSON shape.)

### 9a. `visualize.html` (self-contained HTML5 Canvas)
Requirements (match the style of prior sims — dark theme `#0d1117` bg, `#c9d1d9`
text, self-contained inline CSS/JS, no external deps, runnable via
`python3 -m http.server 8080` in the sim folder):
- `fetch('results.json')` at runtime (relative URL). Handle load errors with a visible
  message.
- Two side-by-side (or toggle) time-series charts driven by the history arrays:
  - **Structure over time:** plot `total_material` (or `n_structure_cells`) for
    `curvature_channel` vs `baseline_pheromone` on one chart; draw a vertical marker
    at each condition's `crossing_step` (if not null) labeled "crossing".
  - **Roughness / stability:** plot `roughness` (curvature condition) and
    `structure_stability` (both) over time, with the `STAB_THRESH=0.90` dashed line.
- A **phase-transition panel** if `output/sweep_data.json` is available (optional —
  try to fetch it; if 404, skip gracefully): plot `crossed` (0/1) and `retention` vs
  `d` from the sweep, highlighting `d*` if a transition is visible.
- A short header explaining the experiment (curvature channel, H7 trace→actor
  crossing, non-saturating recruit+limit vs saturating cue baseline, the Facchini
  growth model) and a one-line takeaway pulled from the summaries (e.g. "curvature
  channel crossed at step N and recovered X% after damage; baseline did not").
- Draw with plain Canvas 2D (no chart library). Keep the code readable.

Verify: `cd sim09_curvature_channel && python3 -m http.server 8080` then confirm the
page loads and both charts render (no console 404 for results.json). Kill the server
after.

### 9b. `README.md`
Write it in the established sim-README style (see sim06/sim08 for tone). Sections:
- Title + one-line summary.
- **What it tests** — H7 trace→actor crossing via the curvature channel (the
  non-saturating, recruit-as-well-as-limit mechanism Facchini 2020 identified);
  curvature_channel vs baseline_pheromone control; the `d` phase transition.
- **Hypotheses tested** — H7 (primary), H11 (the saturating-channel diagnosis —
  sim09 is its sufficiency test: does a non-saturating recruiting channel cross where
  saturating/non-recruiting channels failed?), H4 (dynamic environment — curvature is
  geometry the agents reshape, the stigmergic medium), H1/H10 (composition context).
- **Design** — grid, termites, state-gated curvature routing (deposit at convex
  tips, excavate at concavities — the Facchini/Calovi resolution), the smoothing term
  `d`, surface restriction, roughness feedback, the three crossing criteria
  (channel-adapted), perturbation test. Cite Facchini 2020/2024 and Calovi 2019.
- **Results** — FILL IN with the ACTUAL numbers from your `results.json` run: did
  curvature_channel cross? did baseline_pheromone? crossing steps, retention,
  recovery_final after perturbation, the `d*` threshold if the sweep found one.
  Include a small table. Report honestly — if the separation is weak or the
  transition absent, say so and note what you tuned.
- **Key findings** — connect to the project arc: sim06 (saturating cue, near-miss +
  reversal) → sim07 (scalar transport, wrong sign) → sim08 (non-saturating cap,
  necessary-not-sufficient) → sim09 (non-saturating recruit+limit). State whether
  sim09's results support H7's refined prescription and H11's sufficiency claim.
  If the crossing fires only above the `d` instability, sim09 unifies the
  directed-transport and non-saturating-inhibition candidates (queued-topic 58).
- **Limitations** — toy 2D model, lumped curvature (not full Facchini phase-field),
  no real evaporation/airflow, parameter-sensitivity, the roughness-as-maintenance
  mechanism is inferred not measured, explicit-step stability of the biharmonic.
- **What it teaches / next steps** — e.g. if the curvature channel crosses, does it
  compose? Two self-maintaining curvature structures interacting (the L2 question
  sim05 left open, now with a non-saturating stigmergic glue). Or: test the
  crowding channel (Xiao 2026) as the independent third channel.
- **How to run** — the three CLI commands.

**Definition of Done:**
- [ ] `visualize.html` loads `results.json` and renders the crossing/stability charts;
      no console errors; runnable via a local http server.
- [ ] `README.md` written with REAL results filled in from an actual `run`.
- [ ] All prior selftests still pass.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && \
uv run python3 sim09_curvature_channel/sim09.py selftest && \
uv run python3 sim09_curvature_channel/sim09.py run && \
test -f sim09_curvature_channel/visualize.html && test -f sim09_curvature_channel/README.md && \
echo "Part 9 artifacts present"
```

---

## Appendix A — Full constant reference (single source of truth)

Put all of these in Part 1's constants block (add any a later Part introduces if
missing). Defaults are starting points; Part 5/7 say tune them to reveal the
mechanism.

| Constant | Default | Meaning |
|---|---|---|
| `GRID_SIZE` | 100 | square grid side (toroidal) |
| `N_TERMITES` | 200 | number of agents |
| `STEPS` | 4000 | steps per condition (drop to 3000 if slow) |
| `SAMPLE_EVERY` | 25 | history sampling interval |
| `SEED` | 42 | master RNG seed |
| `D_SMOOTH` | 1.0 | the `d` parameter — biharmonic smoothing strength / phase-transition knob |
| `MATERIAL_DECAY` | 0.0005 | per-step erosion of deposited material |
| `STRUCTURE_THRESHOLD` | 1.0 | material level counting as "structure" |
| `PELLET` | 1.0 | material added per deposit, removed per excavation |
| `SURFACE_THRESHOLD` | 0.05 | material above which a cell is "on the structure surface" |
| `RELOAD_PROB` | 0.3 | prob an unloaded termite refills off-grid |
| `CURVE_FOLLOW` | 0.6 | prob a termite follows the curvature cue (vs random step) |
| `DEPOSIT_PROB_BASE` | 0.10 | baseline deposit prob (nucleation) |
| `DEPOSIT_PROB_GAIN` | 0.85 | curvature-driven deposit prob gain (LINEAR — non-saturating) |
| `EXCAVATE_PROB_BASE` | 0.05 | baseline excavation prob at concavities |
| `EXCAVATE_PROB_GAIN` | 0.60 | curvature-driven excavation prob gain |
| `PICKUP_PROB_BASE` | 0.01 | prob an unloaded termite erodes a structure cell (turnover) |
| `PHEROMONE_DECAY` | 0.02 | per-step pheromone decay (baseline condition only) |
| `PHEROMONE_DIFFUSE` | 0.10 | per-step pheromone diffusion (baseline condition only) |
| `DEPOSIT_PHEROMONE` | 1.0 | cement pheromone per deposit (baseline condition only) |
| `DEPOSIT_BASE` | 0.10 | baseline deposit base (saturating rule, baseline condition only) |
| `DEPOSIT_GAIN` | 0.85 | baseline deposit gain (saturating rule, baseline condition only) |
| `CROSSING_PERSIST` | 4 | consecutive samples needed to declare a crossing |
| `STAB_THRESH` | 0.90 | crossing criterion 1: structure stability |
| `ROUGH_ELEV_THRESH` | 0.02 | crossing criterion 2 (curvature): sustained roughness |
| `PHERO_ELEV_THRESH` | 0.5 | crossing criterion 2 (baseline): sustained pheromone |
| `CONSTRAIN_THRESH` | 0.6 | crossing criterion 3: deposits on convex / on structure |

## Appendix B — Dependency graph (what needs what)

```
Part 1 (skeleton)
  └─ Part 2 (termites — curvature + baseline) ── needs Field, constants
  └─ Part 3 (field — curvature/smoothing/roughness) ── needs Field, constants
        └─ Part 4 (loop)      ── needs Parts 2 & 3
              └─ Part 5 (crossing) ── extends compute_metrics from Part 4
                    └─ Part 6 (run)  ── needs Parts 4 & 5
                          └─ Part 7 (sweeps) ── needs Part 6
                          └─ Part 8 (perturb) ── needs Parts 4,5,6 (minor edit to run_condition)
                                └─ Part 9 (viz + README) ── needs a real results.json
```
Implement strictly in numeric order; each Part's Verification command exercises all
prior Parts via `selftest`, so regressions surface immediately.

---

## Session log
(Each session: append one line — date, Part number, what you did / any deviation.)

- (Design authored 2026-07-30 — awaiting Part 1 implementation.)
