# Sim06: Termite Mound — Testing the Trace→Actor Crossing (H7)

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
- Every Part is additive: you add functions/classes to `sim06.py`, you do not rewrite
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

- [x] **Part 1** — Project skeleton: files, CLI dispatcher, config, RNG, grid, JSON writer
- [ ] **Part 2** — Termite agents: state, movement, pickup/deposit rules (Grassé stigmergy)
- [ ] **Part 3** — The stigmergic field: material grid, cement pheromone, decay & diffusion
- [ ] **Part 4** — Core simulation loop + metrics collection (history records)
- [ ] **Part 5** — The trace→actor crossing detector (the scientific payload)
- [ ] **Part 6** — Experiment conditions + `run` command (baseline vs. self-maintenance)
- [ ] **Part 7** — Parameter sweeps + `sweep_plot` (matplotlib PNGs)
- [ ] **Part 8** — Perturbation / self-repair experiment (the H7 acid test)
- [ ] **Part 9** — `visualize.html` (HTML5 Canvas, self-contained) + README.md

Each Part below is self-contained. Do the first unchecked one.

---

## Scientific framing (short — this is the *why*)

This project studies **multi-scale composition**: how patterns at one scale become new
"actors" at a higher scale with their own rules. Prior simulations found that
composition does **not** emerge spontaneously:

- sim03 (chemical organizations) and sim04 (finite reaction networks): fixed/evolving
  networks converge and stall.
- sim05 (lambda-calculus chemistry, *unbounded* species space): single-scale
  organizations (L1) form, but they never compose into higher-order organizations (L2).
  0/6 composition attempts succeeded. Conclusion (**H10**): unbounded space is
  necessary but not sufficient — you need an *explicit composition mechanism*.

sim05's closing recommendation was explicit: the missing "glue" is **stigmergy** —
persistent environmental traces that bridge and stabilize organizations
(**H7, the Trace→Actor Crossing Hypothesis**).

**H7 in one sentence:** accumulated stigmergic traces can *cross* from being passive
coordination signals to being a self-maintaining actor — a structure that (1) has
dynamics not reducible to individual traces, (2) constrains the agents that build it,
and (3) resists perturbation by repairing itself.

**Why a termite mound?** Termite mound construction is the *original* example of
stigmergy (Grassé, 1959, coined the term for exactly this). Termites deposit soil
pellets impregnated with a "cement pheromone." Deposits attract more deposits (positive
feedback), the pheromone decays (negative feedback), and the resulting pillars/arches
are a macro-structure that no single termite plans — the *structure itself* then
channels airflow and further building. It is the cleanest concrete substrate for
testing whether a trace field can become a self-maintaining actor. sim01 already built
basic pheromone trails; sim06 asks the deeper question sim01 flagged as a next step:
**"do accumulated traces ever become self-maintaining?"**

**What sim06 must demonstrate (the deliverable finding):**
- A **baseline** condition where termites build with decaying pheromone but no
  self-maintenance loop → structure forms then may erode / not stabilize.
- A **self-maintenance** condition where the accumulated structure recruits termites to
  maintain it (the trace→actor loop) → structure persists, stabilizes, and repairs
  after perturbation.
- Quantitative metrics distinguishing the two, plus a **crossing detector** that flags
  *when* (which timestep) the structure crosses from "trace" to "actor."

You do NOT need to reproduce real termite biology. You need a minimal model that can
exhibit — or fail to exhibit — the crossing, measured quantitatively.

---

## Global conventions (apply to every Part)

### File layout
```
simulations/
  pyproject.toml                      # already exists (numpy, matplotlib) — do NOT edit
  sim06_termite_mound/
    DESIGN.md                         # this file
    sim06.py                          # the simulation (you build this across Parts)
    README.md                         # written in Part 9
    results.json                      # produced by `run` (Part 6) — gitignored via *.json? NO: committed
    visualize.html                    # written in Part 9
    output/                           # gitignored: PNGs from sweeps (Part 7)
```
Notes:
- `output/`, `*.png`, `*.mp4` are already gitignored by `../.gitignore`. Do not add a
  local `.gitignore`.
- `results.json` is **committed** (the website visualization fetches it). Write it to
  the sim folder root: `sim06_termite_mound/results.json`. PNG plots go under
  `output/`.

### How to run (must work from the simulations/ directory)
```bash
cd ~/brain/artificial-life/simulations
uv run python3 sim06_termite_mound/sim06.py run          # main experiment -> results.json
uv run python3 sim06_termite_mound/sim06.py sweep_plot   # parameter sweeps -> output/*.png
uv run python3 sim06_termite_mound/sim06.py selftest     # fast internal sanity checks
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
`sim06.py` has a single `main()` reading `sys.argv[1]`:
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
Follow the established project convention: a top-level dict with a `config` block and
one or more named conditions, each holding a `history` list of per-timestep records.
Sim06's shape (final target, fully populated by Part 6/8):
```jsonc
{
  "config": { "grid_size": 100, "n_termites": 200, "steps": 4000, "seed": 42, ... },
  "baseline":         { "history": [ <record>, ... ], "summary": { ... } },
  "self_maintenance": { "history": [ <record>, ... ], "summary": { ... } },
  "perturbation":     { "baseline": {...}, "self_maintenance": {...} }   // added Part 8
}
```
A `<record>` (one per sampled timestep) has these fields (Part 4 defines them; later
Parts add crossing fields):
```jsonc
{
  "step": 1200,
  "total_material": 5312,          // sum of deposited material on grid
  "n_structure_cells": 410,        // cells with material above STRUCTURE_THRESHOLD
  "mean_pheromone": 0.83,          // mean cement-pheromone over active cells
  "max_pheromone": 4.1,
  "n_pillars": 7,                  // connected components of the structure (Part 5)
  "compactness": 0.62,             // structure compactness metric (Part 5)
  "deposits_this_window": 340,     // deposit events since last sample
  "pickups_this_window": 120,
  "structure_stability": 0.94,     // frac of structure cells that survived the window (Part 5)
  "crossed": false,                // has the trace->actor crossing occurred yet? (Part 5)
  "crossing_step": null            // step at which crossing first detected, else null
}
```
Sample history every `SAMPLE_EVERY` steps (default 25) to keep the file reasonable
(~160 records per condition at 4000 steps). Use `json.dump(..., indent=2)`. Cast numpy
scalars to Python `float`/`int` before dumping (helper below).

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
- One file, `sim06.py`. Reasonable functions, small classes. No external state files
  except `results.json` and PNGs.
- Add a module docstring at the top (Part 1) describing the sim and its hypothesis.
- Keep the whole `run` under ~2 minutes wall-clock at default params (grid 100x100,
  200 termites, 4000 steps, 2 conditions). If it's too slow, reduce steps to 3000 —
  correctness over scale. Use numpy vectorization for field decay/diffusion.

---

## Part 1 — Project skeleton

**Goal:** Create `sim06.py` with the module docstring, imports, global constants, the
`_pyify` helper, an RNG helper, an empty `Grid`/field container, the CLI dispatcher, and
a `cmd_selftest()` that (for now) just asserts imports and constants exist.

**Dependencies:** none.

**Implement:**
1. Module docstring: 1 paragraph describing sim06 (termite mound, stigmergy, testing H7
   trace→actor crossing, baseline vs self-maintenance) — you can paraphrase the
   "Scientific framing" section.
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

   # Field / stigmergy parameters
   PHEROMONE_DECAY = 0.02          # per-step multiplicative decay of cement pheromone
   PHEROMONE_DIFFUSE = 0.10        # fraction of pheromone that diffuses to neighbours/step
   MATERIAL_DECAY = 0.0005         # slow erosion of deposited material (baseline erosion)
   STRUCTURE_THRESHOLD = 1.0       # material level above which a cell counts as "structure"
   DEPOSIT_PHEROMONE = 1.0         # cement pheromone added per deposit
   PICKUP_PROB_BASE = 0.01         # base prob a loaded... (agent rules live in Part 2)
   ```
   (Later Parts reference these. If a constant you need is missing, add it here.)
5. `_pyify` helper (from Global conventions).
6. `make_rng(seed=SEED)` returning `np.random.default_rng(seed)`.
7. A minimal field container. Prefer a simple class you will extend in Part 3:
   ```python
   class Field:
       """Holds the 2D grids the stigmergic environment is made of."""
       def __init__(self, size):
           self.size = size
           self.material = np.zeros((size, size), dtype=np.float64)   # deposited soil
           self.pheromone = np.zeros((size, size), dtype=np.float64)  # cement pheromone
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
           print("usage: sim06.py [run|sweep_plot|selftest]")

   if __name__ == "__main__":
       main()
   ```

**Definition of Done:**
- [ ] `sim06.py` exists with docstring, imports, constants, `_pyify`, `make_rng`,
      `Field`, and the CLI dispatcher.
- [ ] Running the verification command prints `selftest: Part 1 OK` and exits 0.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && uv run python3 sim06_termite_mound/sim06.py selftest
```

---

## Part 2 — Termite agents (Grassé stigmergy rules)

**Goal:** Add termite agents that move on the grid, carry at most one soil pellet, and
follow the classic stigmergic pickup/deposit rules. This Part defines agent *behavior in
isolation* — it does not yet run a full loop (Part 4 does).

**Dependencies:** Part 1 (`Field`, constants, `make_rng`).

**Data contract you consume:** `Field` with `.material` and `.pheromone` numpy grids.

**Model of a termite (keep it vectorized OR a small class — vectorized preferred):**
Represent all termites with numpy arrays for speed:
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
(Moore neighbourhood) with toroidal wrap-around (`% size`). Bias movement slightly up
the pheromone gradient when *loaded* (loaded termites are attracted to existing cement —
this is the positive-feedback recruitment). Implementation guidance:
- Unloaded termites: pure random walk (they are foraging for material to pick up, or
  wandering).
- Loaded termites: with probability `PHERO_FOLLOW = 0.6`, move toward the neighbour with
  the highest pheromone (ties → random among the max); otherwise random step. This makes
  deposits cluster where cement already is → pillars form.
- Keep it vectorized if you can; if that's too hard, a Python loop over `n=200`
  termites for ~4000 steps is acceptable (~800k iterations — fine within the time
  budget). Correctness first.

**Pickup rule (unloaded termite on a cell):**
- A termite picks up material only if the cell has material available to pick
  (`material[y,x] > 0`) AND it is unloaded. Pickup probability:
  `p_pickup = PICKUP_PROB_BASE` (small; erosion agent). When it picks up, subtract a
  unit pellet (`PELLET = 1.0`) from `material[y,x]` (clamp at 0) and set `loaded=True`.
  Model note: this is the *erosion / turnover* channel. Most termites are depositors;
  keep pickup rare so structure can grow.
- Actually, to keep the model simple and always have material to deposit, give each
  termite an internal "reserve": an unloaded termite becomes loaded with probability
  `RELOAD_PROB = 0.3` each step *regardless of cell* (models fetching soil from an
  off-grid source). Use this reload channel as the primary way termites become loaded;
  keep the cell-pickup channel too (it drives turnover). Add constant
  `RELOAD_PROB = 0.3` in Part 1's constants block if missing.

**Deposit rule (loaded termite on a cell):** the heart of Grassé stigmergy.
- Deposit probability increases with local pheromone (positive feedback):
  ```
  local = pheromone[y, x]
  p_deposit = DEPOSIT_BASE + DEPOSIT_GAIN * (local / (1.0 + local))
  ```
  with `DEPOSIT_BASE = 0.10`, `DEPOSIT_GAIN = 0.85` (add to constants). This saturates at
  ~0.95, so cells with lots of cement strongly attract deposits, but even bare ground
  gets occasional seed deposits (`DEPOSIT_BASE`) — needed to nucleate the first pillars.
- On deposit: `material[y,x] += PELLET`, `pheromone[y,x] += DEPOSIT_PHEROMONE`,
  set `loaded=False`.

**Functions to implement:**
```python
def termite_step(termites: "Termites", field: "Field", rng, params: dict) -> dict:
    """Advance ALL termites one step: move, maybe reload/pickup, maybe deposit.
    Returns a small dict of per-step event counts:
        {"deposits": int, "pickups": int}
    `params` overrides constants (see Part 6). Fall back to the module constant when a
    key is absent, e.g. deposit_base = params.get("deposit_base", DEPOSIT_BASE).
    """
```
Make `termite_step` read ALL tunables from `params` with constant fallbacks:
`phero_follow, reload_prob, pickup_prob, deposit_base, deposit_gain, pellet,
deposit_pheromone`. This lets Part 6/7/8 sweep them without touching this code.

**Append to `cmd_selftest`:** create a Field, Termites(50, ...), run `termite_step` 100
times, assert `field.material.sum() > 0` (deposits happened) and that `loaded` is a bool
array of length 50. Print `selftest: Part 2 OK`.

**Definition of Done:**
- [ ] `Termites` class and `termite_step` implemented, fully parameterized via `params`.
- [ ] After 100 steps in selftest, material has accumulated (`sum > 0`).
- [ ] Verification command prints both `Part 1 OK` and `Part 2 OK`, exits 0.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && uv run python3 sim06_termite_mound/sim06.py selftest
```

---

## Part 3 — The stigmergic field: decay & diffusion

**Goal:** Give the `Field` its own dynamics — cement pheromone decays and diffuses;
deposited material slowly erodes (baseline). Optionally (self-maintenance condition,
wired in Part 6) the structure emits maintenance pheromone. This Part implements the
*environment's* rules — the "actor candidate."

**Dependencies:** Part 1 (`Field`, constants).

**Implement `field_step(field, params)`** — advance the environment one step:
1. **Pheromone decay:** `field.pheromone *= (1.0 - decay)` with
   `decay = params.get("pheromone_decay", PHEROMONE_DECAY)`.
2. **Pheromone diffusion:** convolve with a simple 3x3 blur weighted by
   `diffuse = params.get("pheromone_diffuse", PHEROMONE_DIFFUSE)`. Efficient toroidal
   diffusion via `np.roll`:
   ```python
   def _diffuse(a, rate):
       nb = (np.roll(a,1,0)+np.roll(a,-1,0)+np.roll(a,1,1)+np.roll(a,-1,1)
             + np.roll(np.roll(a,1,0),1,1)+np.roll(np.roll(a,1,0),-1,1)
             + np.roll(np.roll(a,-1,0),1,1)+np.roll(np.roll(a,-1,0),-1,1)) / 8.0
       return (1-rate)*a + rate*nb
   ```
3. **Material erosion (baseline decay):** `field.material *= (1.0 - material_decay)`
   with `material_decay = params.get("material_decay", MATERIAL_DECAY)`. This is the slow
   background collapse the structure must overcome to persist.
4. **Self-maintenance emission (KEY, gated by a param):** if
   `params.get("self_maintenance", False)` is True, the *structure itself* re-emits
   cement pheromone proportional to how much material is there — modeling the mound
   channeling termites back to maintain it (the trace→actor feedback):
   ```python
   if params.get("self_maintenance", False):
       gain = params.get("maintain_gain", MAINTAIN_GAIN)   # add MAINTAIN_GAIN=0.05 to Part 1 constants
       structure_mask = field.material > structure_threshold
       field.pheromone[structure_mask] += gain * field.material[structure_mask]
   ```
   In the **baseline** condition `self_maintenance=False`, so the structure is inert —
   it can only be maintained by termites happening to wander back, with no active
   recruitment from the structure. This is the difference that should produce or fail to
   produce the crossing.

**Why this is the experiment's crux:** baseline = pheromone comes ONLY from fresh
termite deposits (a decaying trace). self_maintenance = the accumulated structure
becomes a *source* of the very signal that recruits builders → a closed self-maintaining
loop → candidate "actor." Part 5 detects whether/when this loop actually crosses.

**Append to `cmd_selftest`:** put a blob of material+pheromone in the center, run
`field_step` (baseline params) 50 times, assert pheromone decreased and spread
(non-zero neighbours). Then run with `self_maintenance=True` and assert pheromone over a
material blob does NOT go to ~0 (it's being replenished). Print `selftest: Part 3 OK`.

**Definition of Done:**
- [ ] `field_step` implements decay, diffusion, material erosion, gated self-maintenance.
- [ ] selftest confirms baseline pheromone decays toward 0 but self_maintenance keeps it
      elevated over structure. Prints `Part 3 OK`.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && uv run python3 sim06_termite_mound/sim06.py selftest
```

---

## Part 4 — Core simulation loop + metrics

**Goal:** Wire termites + field into one loop, sample metrics every `SAMPLE_EVERY`
steps, and produce a `history` list of records matching the Data contract (minus the
crossing fields, which Part 5 fills in — leave `crossed`/`crossing_step` as placeholders
here, or omit and let Part 5 add them; simplest: include them as `False`/`None`).

**Dependencies:** Part 2 (`Termites`, `termite_step`), Part 3 (`Field`, `field_step`),
Part 1 constants.

**Implement `run_condition(params, seed)` → dict:**
```python
def run_condition(params, seed):
    """Run one full simulation condition. Returns {"history": [...], "summary": {...}}."""
    rng = make_rng(seed)
    size   = params.get("grid_size", GRID_SIZE)
    n      = params.get("n_termites", N_TERMITES)
    steps  = params.get("steps", STEPS)
    sample = params.get("sample_every", SAMPLE_EVERY)

    field = Field(size)
    termites = Termites(n, size, rng)
    history = []
    dep_acc = pick_acc = 0
    prev_structure_mask = None

    for step in range(steps):
        ev = termite_step(termites, field, rng, params)
        field_step(field, params)
        dep_acc += ev["deposits"]; pick_acc += ev["pickups"]

        if step % sample == 0:
            rec = compute_metrics(field, params, step, dep_acc, pick_acc, prev_structure_mask)
            history.append(rec)
            dep_acc = pick_acc = 0
            prev_structure_mask = (field.material > params.get("structure_threshold", STRUCTURE_THRESHOLD)).copy()

    summary = summarize(history)
    return {"history": history, "summary": summary}
```

**Implement `compute_metrics(field, params, step, deposits, pickups, prev_mask)` →
record dict** with fields: `step, total_material, n_structure_cells, mean_pheromone,
max_pheromone, deposits_this_window, pickups_this_window`. Also compute
`structure_stability`: fraction of `prev_mask` cells still above threshold now (1.0 on
the first sample when `prev_mask is None`). Leave `n_pillars`, `compactness`, `crossed`,
`crossing_step` as `0`, `0.0`, `False`, `None` here — **Part 5 upgrades this function**
to fill them. (Write `compute_metrics` so Part 5 can extend it; put a clear comment
`# --- Part 5 fills n_pillars/compactness/crossing below ---`.)

**Implement `summarize(history)` → dict:** final `total_material`, final
`n_structure_cells`, peak `total_material` and the step it occurred, mean
`structure_stability` over the last 25% of samples, and `retention` =
`final_total_material / peak_total_material` (0..1; high = structure persisted, low =
it eroded away). These summary numbers are the headline comparison between conditions.

**Wire `cmd_run` minimally now** (Part 6 expands it): run ONE baseline condition, write
`{"config": {...}, "baseline": run_condition(baseline_params, SEED)}` to
`results.json` via `_pyify`, print the summary. This gives an end-to-end smoke test
before adding the second condition.

**Append to `cmd_selftest`:** run `run_condition` with tiny params
(`grid_size=30, n_termites=20, steps=200, sample_every=25`), assert `len(history) >= 4`
and each record has the required keys. Print `Part 4 OK`.

**Definition of Done:**
- [ ] `run_condition`, `compute_metrics`, `summarize` implemented; `cmd_run` writes a
      valid `results.json` with a `baseline.history`.
- [ ] `selftest` prints `Part 4 OK`.
- [ ] `run` completes and `results.json` parses as JSON with `data["baseline"]["history"]`
      being a non-empty list.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && \
uv run python3 sim06_termite_mound/sim06.py selftest && \
uv run python3 sim06_termite_mound/sim06.py run && \
uv run python3 -c "import json;d=json.load(open('sim06_termite_mound/results.json'));assert d['baseline']['history'];print('run OK, records:',len(d['baseline']['history']))"
```

---

## Part 5 — The trace→actor crossing detector (scientific payload)

**Goal:** This is the intellectual core. Upgrade `compute_metrics` to also compute
structure morphology (`n_pillars`, `compactness`) and implement the **crossing
detector**: an operational, quantitative test of when the accumulated trace field
becomes a self-maintaining actor per H7.

**Dependencies:** Part 4 (`compute_metrics`, `run_condition`). Part 1 constants.

**H7's three criteria, made operational.** A crossing is declared at the first sampled
step where ALL THREE hold and stay true for at least `CROSSING_PERSIST` consecutive
samples (add `CROSSING_PERSIST = 4` to constants):

1. **Persistence despite erosion** — `structure_stability >= STAB_THRESH` (default 0.90):
   ≥90% of structure cells survive window-to-window even though `material_decay` is
   eroding everything. The structure is maintaining itself, not just accreting.
2. **Non-reducible dynamics** — `mean_pheromone_over_structure` stays elevated
   (`>= PHERO_ELEV_THRESH`, default 0.5) **while fresh deposit rate is falling**
   (`deposits_this_window` below its early-run average). I.e. the pheromone field is
   sustained by the *structure* (self-maintenance emission), not by ongoing fresh
   deposits — a property of the whole, not of individual recent traces.
3. **Constraint on agents** — the fraction of deposits landing on already-structure
   cells (`deposit_on_structure_fraction`) is high (`>= CONSTRAIN_THRESH`, default 0.6):
   the structure is channeling where termites build. (To measure this, have
   `termite_step` also return `deposits_on_structure` — count deposits where the target
   cell was already above threshold. Add that to the event dict; if you didn't in Part 2,
   add it now: it's a one-line check inside the deposit branch.)

Store per-record: `n_pillars`, `compactness`, `mean_pheromone_over_structure`,
`deposit_on_structure_fraction`, `crossed` (bool, cumulative once true),
`crossing_step` (int or null).

**Morphology metrics:**
- `n_pillars`: number of connected components (Moore/8-connectivity) of the boolean mask
  `material > structure_threshold`. Implement a small flood-fill / union-find in numpy or
  plain Python (do NOT add scipy). A simple iterative BFS labeling over the boolean grid
  is fine — the grid is 100x100.
- `compactness`: `n_structure_cells / (bounding_box_area_of_structure)` where bounding
  box is min/max row & col of structure cells (1.0 = perfectly filled box, low = sparse
  scattered). If no structure, `0.0`.

**Crossing detection is a post-pass over `history`.** Cleanest approach: compute the
per-record fields inside `compute_metrics`, then implement
`detect_crossing(history, params)` that walks the history, tracks a run-length of
samples satisfying all three criteria, and sets `crossed=True` / `crossing_step=<step>`
on that record and all later records once the run-length hits `CROSSING_PERSIST`. Call
`detect_crossing` at the end of `run_condition`, before `summarize`. The
"early-run average" for criterion 2 = mean `deposits_this_window` over the first 20% of
samples.

Add to `summarize`: `crossed` (bool — did this condition ever cross?) and
`crossing_step` (int or null). These two numbers, compared across baseline vs
self_maintenance, ARE the paper result.

**Expected/target result (state in README later, verify qualitatively):** baseline
should typically NOT cross (or cross late and unstably); self_maintenance should cross
and stay crossed. If your defaults produce baseline-also-crosses or
neither-crosses, tune `material_decay` (raise it so baseline erodes) and `maintain_gain`
(so self-maintenance overcomes erosion) — the whole point is a *separation* between
conditions. Document whatever separation you achieve honestly; a null result is still a
result, but first try to find parameters that reveal the mechanism.

**Append to `cmd_selftest`:** run a tiny self_maintenance condition and a tiny baseline;
assert `detect_crossing` runs without error and that records now contain `n_pillars`,
`compactness`, `crossed`, `crossing_step`. (Don't assert *which* crosses at tiny scale —
too noisy.) Print `Part 5 OK`.

**Definition of Done:**
- [ ] `compute_metrics` now fills `n_pillars`, `compactness`,
      `mean_pheromone_over_structure`, `deposit_on_structure_fraction`.
- [ ] `detect_crossing` implemented and called in `run_condition`.
- [ ] `summarize` reports `crossed` and `crossing_step`.
- [ ] `selftest` prints `Part 5 OK`.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && uv run python3 sim06_termite_mound/sim06.py selftest
```

---

## Part 6 — Experiment conditions + full `run`

**Goal:** Define the two headline conditions and make `cmd_run` execute both, assemble
the full `results.json`, and print a clear comparison.

**Dependencies:** Parts 4 & 5 (`run_condition`, `summarize`, crossing fields).

**Define condition param dicts:**
```python
def baseline_params():
    return {
        "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
        "sample_every": SAMPLE_EVERY, "structure_threshold": STRUCTURE_THRESHOLD,
        "self_maintenance": False,
        # (all agent/field tunables fall back to module constants)
    }

def self_maintenance_params():
    p = baseline_params()
    p["self_maintenance"] = True
    p["maintain_gain"] = MAINTAIN_GAIN
    return p
```

**Rewrite `cmd_run`:**
```python
def cmd_run():
    t0 = time.time()
    print("Running baseline (decaying trace, no self-maintenance)...")
    base = run_condition(baseline_params(), seed=SEED)
    print("Running self-maintenance (trace->actor loop)...")
    selfm = run_condition(self_maintenance_params(), seed=SEED)

    results = {
        "config": {
            "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
            "sample_every": SAMPLE_EVERY, "seed": SEED,
            "pheromone_decay": PHEROMONE_DECAY, "material_decay": MATERIAL_DECAY,
            "maintain_gain": MAINTAIN_GAIN, "structure_threshold": STRUCTURE_THRESHOLD,
        },
        "baseline": base,
        "self_maintenance": selfm,
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(_pyify(results), f, indent=2)

    # Comparison printout — this is the headline finding
    def line(name, r):
        s = r["summary"]
        print(f"  {name:18s} crossed={str(s['crossed']):5s} "
              f"crossing_step={s['crossing_step']} "
              f"retention={s['retention']:.2f} "
              f"final_cells={s['final_n_structure_cells']}")
    print("\n=== RESULT: Trace -> Actor Crossing (H7) ===")
    line("baseline", base)
    line("self_maintenance", selfm)
    print(f"\nWrote {RESULTS_PATH}  ({time.time()-t0:.1f}s)")
```
(Adjust summary key names to whatever you used in `summarize` — keep them consistent.)

**Definition of Done:**
- [ ] `cmd_run` runs both conditions, writes full `results.json` with `config`,
      `baseline`, `self_maintenance`.
- [ ] The comparison printout shows `crossed` / `crossing_step` / `retention` for both.
- [ ] Total runtime under ~2 min at defaults (reduce `STEPS` to 3000 if needed).

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && \
uv run python3 sim06_termite_mound/sim06.py run && \
uv run python3 -c "import json;d=json.load(open('sim06_termite_mound/results.json'));print('baseline crossed:',d['baseline']['summary']['crossed']);print('selfmaint crossed:',d['self_maintenance']['summary']['crossed'])"
```

---

## Part 7 — Parameter sweeps + `sweep_plot`

**Goal:** Show HOW the crossing depends on key parameters, and produce PNG plots. This
is the quantitative-results requirement for a good mini-sim.

**Dependencies:** Part 6 (`run_condition`, param builders). Imports matplotlib LAZILY
inside `cmd_sweep_plot` (`import matplotlib; matplotlib.use("Agg"); import
matplotlib.pyplot as plt`). Do NOT import at module top.

**Sweeps (run with reduced cost — `steps≈2000`, `grid_size=80` to keep it fast):**
1. **maintain_gain sweep** (self_maintenance ON): sweep `maintain_gain` over
   `[0.0, 0.02, 0.05, 0.1, 0.2]`. For each, record `crossed` (0/1), `crossing_step`,
   and `retention`. Plot retention & crossing_step vs maintain_gain. Expectation: below
   some threshold gain, no crossing; above it, crossing (a phase transition — the
   headline plot).
2. **material_decay sweep** (both conditions): sweep `material_decay` over
   `[0.0002, 0.0005, 0.001, 0.002, 0.004]`. Plot `retention` for baseline vs
   self_maintenance on the same axes. Expectation: self_maintenance retains structure
   across a wider erosion range than baseline (the separation widens with erosion).
3. (Optional, if time) **n_termites sweep** `[50,100,200,400]`: plot final
   `n_structure_cells` for both conditions.

**Output:** save each plot to `OUTPUT_DIR` (create it): e.g.
`output/sweep_maintain_gain.png`, `output/sweep_material_decay.png`. Use clear titles,
axis labels, and a legend. Also dump the raw sweep numbers to
`output/sweep_data.json` (handy for the write-up; `output/` is gitignored so this is a
local artifact only).

**Keep sweeps cheap.** Each sweep point is a full `run_condition`; with 5 points x 2
conditions x 2000 steps you want each run ~5-10s. Use `grid_size=80, n_termites=150,
steps=2000, sample_every=25`. If it's too slow, drop to `steps=1500`.

**Definition of Done:**
- [ ] `cmd_sweep_plot` produces at least `sweep_maintain_gain.png` and
      `sweep_material_decay.png` under `output/`.
- [ ] Uses `matplotlib.use("Agg")` (headless) — no display needed.
- [ ] Prints where it wrote the PNGs. Runs in a few minutes at most.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && \
uv run python3 sim06_termite_mound/sim06.py sweep_plot && \
ls -la sim06_termite_mound/output/*.png
```

---

## Part 8 — Perturbation / self-repair experiment (the H7 acid test)

**Goal:** The strongest test of "actor-hood": does the structure *repair itself* after
damage? Add a perturbation experiment: build a structure, damage it, keep running, and
measure recovery. Self-maintenance should recover; baseline should not (or recover far
less).

**Dependencies:** Part 4 (`run_condition` internals — you'll write a variant),
Part 5 (metrics), Part 6 (param builders).

**Implement `run_condition_perturbed(params, seed, perturb_at, perturb_frac)`:** a copy
of `run_condition`'s loop with one addition — at step `perturb_at` (default
`int(0.6*steps)`), zero out a rectangular patch of BOTH `field.material` and
`field.pheromone` covering `perturb_frac` (default 0.25) of the grid area (e.g. a square
block near the densest structure region, or simply the central quarter). Record in each
post-perturbation record the metric `recovery = current_total_material /
pre_perturb_total_material` (capture `pre_perturb_total_material` at the sample just
before `perturb_at`). Add `perturb_at` and `perturb_frac` to the returned summary.

Rather than duplicating the whole loop, prefer refactoring: add an optional
`perturb=None` argument to `run_condition` of the form
`perturb={"at": step, "frac": f}`; when set, apply the damage at that step. This avoids a
near-duplicate function. (This is the ONE place you may modify an earlier Part's
function — do it minimally and keep the default `perturb=None` so Part 6 behavior is
unchanged.)

**Add to `cmd_run`:** after the two main conditions, run the perturbation experiment for
both baseline and self_maintenance (same `perturb` spec, `seed=SEED`) and store under a
top-level `"perturbation"` key:
```jsonc
"perturbation": {
  "baseline":         { "history": [...], "summary": {..., "recovery_final": 0.41} },
  "self_maintenance": { "history": [...], "summary": {..., "recovery_final": 0.93} }
}
```
Compute `recovery_final` = last record's `recovery`. Print a recovery comparison line.

**Definition of Done:**
- [ ] `run_condition` accepts `perturb=None`; damage applied at the right step when set.
- [ ] `results.json` gains a `perturbation` block with baseline & self_maintenance,
      each with `recovery_final` in its summary.
- [ ] `cmd_run` prints the recovery comparison.
- [ ] Part 6's non-perturbed behavior is unchanged (perturb defaults off).

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && \
uv run python3 sim06_termite_mound/sim06.py run && \
uv run python3 -c "import json;d=json.load(open('sim06_termite_mound/results.json'));p=d['perturbation'];print('baseline recovery:',p['baseline']['summary']['recovery_final']);print('selfmaint recovery:',p['self_maintenance']['summary']['recovery_final'])"
```

---

## Part 9 — visualize.html + README.md

**Goal:** Ship the interactive visualization and the documentation. Two deliverables.

**Dependencies:** a valid `results.json` from Part 6/8. **Before writing any JS, run
`run` and inspect the ACTUAL `results.json` structure** (top-level keys, the history
array path `data.baseline.history`, and one sample record's field names). Use the EXACT
field paths — do not guess. (This is a hard-won project rule: prior visualizations broke
because the coder guessed the JSON shape.)

### 9a. `visualize.html` (self-contained HTML5 Canvas)
Requirements (match the style of prior sims — dark theme, self-contained, no external
deps, runnable via `python3 -m http.server 8080` in the sim folder):
- `fetch('results.json')` at runtime (relative URL). Handle load errors with a visible
  message.
- Two side-by-side (or toggle) time-series charts driven by the history arrays:
  - **Structure over time:** plot `total_material` (or `n_structure_cells`) for
    `baseline` vs `self_maintenance` on one chart; draw a vertical marker at each
    condition's `crossing_step` (if not null) labeled "crossing".
  - **Retention / stability:** plot `structure_stability` over time for both conditions.
- A small **replay canvas** is optional but nice: if you also dump a few grid snapshots
  (you can add an optional `snapshots` list to `results.json` — a handful of downsampled
  `material` grids at chosen steps — but ONLY if it doesn't bloat the file past ~2-3 MB;
  otherwise skip snapshots and just do the charts).
- A short header explaining the experiment (termite mound, H7 trace→actor crossing,
  baseline vs self-maintenance) and a one-line takeaway pulled from the summaries
  (e.g. "self-maintenance crossed at step N and recovered X% after damage; baseline did
  not").
- Draw with plain Canvas 2D (no chart library). Keep the code readable.

Verify: `cd sim06_termite_mound && python3 -m http.server 8080` then confirm the page
loads and both charts render (no console 404 for results.json). Kill the server after.

### 9b. `README.md`
Write it in the established sim-README style (see sim01/sim05 for tone). Sections:
- Title + one-line summary.
- **What it tests** — H7 trace→actor crossing via termite-mound stigmergy; baseline
  (decaying trace) vs self-maintenance (trace→actor loop).
- **Hypotheses tested** — H7 (primary), H1/H10 (composition context), H4 (dynamic
  environment), H8 (irreducibility, if relevant).
- **Design** — grid, termites, Grassé pickup/deposit rules, field decay/diffusion,
  self-maintenance emission, the three crossing criteria, perturbation test.
- **Results** — FILL IN with the ACTUAL numbers from your `results.json` run: did
  baseline cross? did self_maintenance? crossing steps, retention, recovery_final after
  perturbation. Include a small table. Report honestly — if the separation is weak, say
  so and note what you tuned.
- **Key findings** — connect to the project arc: sims 03-05 showed composition fails
  without a mechanism; sim06 tests whether stigmergic self-maintenance is that
  mechanism. State whether the results support H7.
- **Limitations** — toy model, single mechanism, no real airflow/thermoregulation,
  parameter-sensitivity, 2D, etc.
- **What it teaches / next steps** — e.g. if self-maintenance produces the crossing,
  sim07 could test whether two such self-maintaining structures *compose* (the L2
  question sim05 left open, now with the stigmergic glue in place).
- **How to run** — the three CLI commands.

**Definition of Done:**
- [ ] `visualize.html` loads `results.json` and renders the crossing/stability charts;
      no console errors; runnable via a local http server.
- [ ] `README.md` written with REAL results filled in from an actual `run`.
- [ ] All prior selftests still pass.

**Verification command:**
```bash
cd ~/brain/artificial-life/simulations && \
uv run python3 sim06_termite_mound/sim06.py selftest && \
uv run python3 sim06_termite_mound/sim06.py run && \
test -f sim06_termite_mound/visualize.html && test -f sim06_termite_mound/README.md && \
echo "Part 9 artifacts present"
```

---

## Appendix A — Full constant reference (single source of truth)

Put all of these in Part 1's constants block (add any a later Part introduces if
missing). Defaults are starting points; Part 5 says tune them to reveal the mechanism.

| Constant | Default | Meaning |
|---|---|---|
| `GRID_SIZE` | 100 | square grid side (toroidal) |
| `N_TERMITES` | 200 | number of agents |
| `STEPS` | 4000 | steps per condition (drop to 3000 if slow) |
| `SAMPLE_EVERY` | 25 | history sampling interval |
| `SEED` | 42 | master RNG seed |
| `PHEROMONE_DECAY` | 0.02 | per-step cement-pheromone decay |
| `PHEROMONE_DIFFUSE` | 0.10 | per-step pheromone diffusion rate |
| `MATERIAL_DECAY` | 0.0005 | per-step erosion of deposited material |
| `STRUCTURE_THRESHOLD` | 1.0 | material level counting as "structure" |
| `DEPOSIT_PHEROMONE` | 1.0 | cement pheromone per deposit |
| `PELLET` | 1.0 | material added/removed per deposit/pickup |
| `PICKUP_PROB_BASE` | 0.01 | prob an unloaded termite erodes a cell |
| `RELOAD_PROB` | 0.3 | prob an unloaded termite refills off-grid |
| `PHERO_FOLLOW` | 0.6 | prob a loaded termite climbs pheromone gradient |
| `DEPOSIT_BASE` | 0.10 | baseline deposit prob (nucleation) |
| `DEPOSIT_GAIN` | 0.85 | pheromone-driven deposit prob gain |
| `MAINTAIN_GAIN` | 0.05 | structure self-emission of pheromone (self-maint only) |
| `CROSSING_PERSIST` | 4 | consecutive samples needed to declare a crossing |
| `STAB_THRESH` | 0.90 | crossing criterion 1: structure stability |
| `PHERO_ELEV_THRESH` | 0.5 | crossing criterion 2: sustained pheromone over structure |
| `CONSTRAIN_THRESH` | 0.6 | crossing criterion 3: deposits landing on structure |

## Appendix B — Dependency graph (what needs what)

```
Part 1 (skeleton)
  └─ Part 2 (termites) ── needs Field, constants
  └─ Part 3 (field)    ── needs Field, constants
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

- (Design authored — awaiting Part 1 implementation.)
- 2026-07-24 — Part 1 implemented: created sim06.py with module docstring, imports, constants, `_pyify`, `make_rng`, `Field` class, CLI dispatcher, `cmd_selftest`. `selftest` prints "selftest: Part 1 OK" and exits 0.
