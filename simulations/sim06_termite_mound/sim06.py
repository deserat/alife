"""sim06 — Termite mound: testing the H7 Trace->Actor Crossing Hypothesis.

Termites deposit soil pellets laced with a cement pheromone (Grasse stigmergy).
Deposits attract further deposits (positive feedback); pheromone decays (negative
feedback), producing pillars/archs no single agent plans. sim06 asks whether the
accumulated stigmergic trace field can *cross* from a passive coordination signal
to a self-maintaining actor — a structure with dynamics not reducible to its
parts, that constrains its builders, and that repairs itself after perturbation.

Two conditions are contrasted:
  - baseline:         termites build with decaying pheromone, no maintenance loop.
  - self_maintenance: the accumulated structure recruits termites to maintain it.

A crossing detector (Part 5) flags the timestep at which the trace field becomes
an actor; perturbation experiments (Part 8) provide the acid test for H7.
"""

import os
import sys
import json
import math
import time

import numpy as np

# ---------------------------------------------------------------------------
# Paths (built from the script's own location — never hardcode /home/vance/...)
# ---------------------------------------------------------------------------
SIM_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SIM_DIR, "results.json")
OUTPUT_DIR = os.path.join(SIM_DIR, "output")

# ---------------------------------------------------------------------------
# Simulation constants (module-level defaults; later Parts reference these)
# ---------------------------------------------------------------------------
GRID_SIZE = 100
N_TERMITES = 200
STEPS = 4000
SAMPLE_EVERY = 25
SEED = 42

# Field / stigmergy parameters
PHEROMONE_DECAY = 0.02          # per-step multiplicative decay of cement pheromone
PHEROMONE_DIFFUSE = 0.10         # fraction of pheromone that diffuses to neighbours/step
MATERIAL_DECAY = 0.0005          # slow erosion of deposited material (baseline erosion)
STRUCTURE_THRESHOLD = 1.0       # material level above which a cell counts as "structure"
DEPOSIT_PHEROMONE = 1.0          # cement pheromone added per deposit
PICKUP_PROB_BASE = 0.01          # base prob an unloaded termite picks up from its cell

# Termite agent parameters (Part 2)
PHERO_FOLLOW = 0.6               # prob a loaded termite steps toward max-pheromone neighbour
RELOAD_PROB = 0.3                # prob an unloaded termite becomes loaded from off-grid source
DEPOSIT_BASE = 0.10              # base deposit probability on bare ground (nucleation)
DEPOSIT_GAIN = 0.85              # deposit probability gain from local pheromone (saturates ~0.95)
PELLET = 1.0                     # unit of soil material transferred per pickup/deposit

# Field dynamics parameters (Part 3)
MAINTAIN_GAIN = 0.05             # self-maintenance: pheromone re-emitted per unit structure material

# Crossing detector parameters (Part 5)
CROSSING_PERSIST = 4             # consecutive samples all criteria must hold
STAB_THRESH = 0.90               # criterion 1: structure_stability threshold
PHERO_ELEV_THRESH = 0.5          # criterion 2: mean pheromone over structure threshold
CONSTRAIN_THRESH = 0.6           # criterion 3: deposit_on_structure_fraction threshold


# ---------------------------------------------------------------------------
# Numpy -> JSON helper
# ---------------------------------------------------------------------------
def _pyify(x):
    """Recursively convert numpy scalars/arrays to JSON-native types."""
    if isinstance(x, dict):
        return {k: _pyify(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_pyify(v) for v in x]
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    return x


# ---------------------------------------------------------------------------
# RNG helper
# ---------------------------------------------------------------------------
def make_rng(seed=SEED):
    """Return a numpy random Generator seeded with *seed*."""
    return np.random.default_rng(seed)


# ---------------------------------------------------------------------------
# Field container (extended in Part 3)
# ---------------------------------------------------------------------------
class Field:
    """Holds the 2D grids the stigmergic environment is made of."""

    def __init__(self, size):
        self.size = size
        self.material = np.zeros((size, size), dtype=np.float64)    # deposited soil
        self.pheromone = np.zeros((size, size), dtype=np.float64)    # cement pheromone


# ---------------------------------------------------------------------------
# Moore neighbourhood offsets (8 neighbours) for toroidal movement
# ---------------------------------------------------------------------------
_MOORE_DX = np.array([-1, 0, 1, -1, 1, -1, 0, 1], dtype=np.int32)
_MOORE_DY = np.array([-1, -1, -1, 0, 0, 1, 1, 1], dtype=np.int32)


# ---------------------------------------------------------------------------
# Termite agents (Part 2 — Grasse stigmergy rules)
# ---------------------------------------------------------------------------
class Termites:
    """Vectorized termite population. Each termite carries at most one pellet."""

    def __init__(self, n, size, rng):
        self.n = n
        self.size = size
        self.x = rng.integers(0, size, n).astype(np.int32)
        self.y = rng.integers(0, size, n).astype(np.int32)
        self.loaded = np.zeros(n, dtype=bool)


def termite_step(termites, field, rng, params):
    """Advance ALL termites one step: move, maybe reload/pickup, maybe deposit.

    Returns a small dict of per-step event counts:
        {"deposits": int, "pickups": int}

    `params` overrides module constants (missing keys fall back to defaults).
    """
    n = termites.n
    size = termites.size

    phero_follow = params.get("phero_follow", PHERO_FOLLOW)
    reload_prob = params.get("reload_prob", RELOAD_PROB)
    pickup_prob = params.get("pickup_prob", PICKUP_PROB_BASE)
    deposit_base = params.get("deposit_base", DEPOSIT_BASE)
    deposit_gain = params.get("deposit_gain", DEPOSIT_GAIN)
    pellet = params.get("pellet", PELLET)
    deposit_pheromone = params.get("deposit_pheromone", DEPOSIT_PHEROMONE)

    # --- Movement ---
    # 8-neighbour coordinates for every termite: shapes (8, n)
    nx = (termites.x[None, :] + _MOORE_DX[:, None]) % size
    ny = (termites.y[None, :] + _MOORE_DY[:, None]) % size
    phero_nb = field.pheromone[ny, nx]                       # (8, n)

    # Pheromone-following step: argmax with random tie-breaking
    noise = rng.random(phero_nb.shape) * 1e-9
    best_idx = np.argmax(phero_nb + noise, axis=0)           # (n,)
    rand_idx = rng.integers(0, 8, n)                         # (n,)

    follow = termites.loaded & (rng.random(n) < phero_follow)
    move_idx = np.where(follow, best_idx, rand_idx)

    termites.x = (termites.x + _MOORE_DX[move_idx]) % size
    termites.y = (termites.y + _MOORE_DY[move_idx]) % size

    # --- Reload (off-grid soil source — primary loading channel) ---
    unloaded = ~termites.loaded
    reload_mask = unloaded & (rng.random(n) < reload_prob)
    termites.loaded[reload_mask] = True

    # --- Pickup from cell (turnover / erosion channel) ---
    still_unloaded = ~termites.loaded
    cell_material = field.material[termites.y, termites.x]
    pick_mask = still_unloaded & (cell_material > 0) & (rng.random(n) < pickup_prob)
    if pick_mask.any():
        py = termites.y[pick_mask]
        px = termites.x[pick_mask]
        field.material[py, px] = np.maximum(field.material[py, px] - pellet, 0.0)
        termites.loaded[pick_mask] = True

    # --- Deposit (Grasse stigmergy — heart of the model) ---
    local_phero = field.pheromone[termites.y, termites.x]
    p_deposit = deposit_base + deposit_gain * (local_phero / (1.0 + local_phero))
    np.clip(p_deposit, 0.0, 1.0, out=p_deposit)
    dep_mask = termites.loaded & (rng.random(n) < p_deposit)
    structure_threshold = params.get("structure_threshold", STRUCTURE_THRESHOLD)
    deposits_on_structure = 0
    if dep_mask.any():
        dy = termites.y[dep_mask]
        dx = termites.x[dep_mask]
        already_struct = field.material[dy, dx] > structure_threshold
        deposits_on_structure = int(already_struct.sum())
        field.material[dy, dx] += pellet
        field.pheromone[dy, dx] += deposit_pheromone
        termites.loaded[dep_mask] = False

    return {
        "deposits": int(dep_mask.sum()),
        "pickups": int(pick_mask.sum()),
        "deposits_on_structure": deposits_on_structure,
    }


# ---------------------------------------------------------------------------
# Field dynamics (Part 3 — decay, diffusion, erosion, self-maintenance)
# ---------------------------------------------------------------------------
def _diffuse(a, rate):
    """Toroidal 3x3 blur diffusion. Returns (1-rate)*a + rate*neighbour_mean."""
    nb = (np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)
          + np.roll(np.roll(a, 1, 0), 1, 1) + np.roll(np.roll(a, 1, 0), -1, 1)
          + np.roll(np.roll(a, -1, 0), 1, 1) + np.roll(np.roll(a, -1, 0), -1, 1)) / 8.0
    return (1.0 - rate) * a + rate * nb


def field_step(field, params):
    """Advance the stigmergic environment one step.

    1. Pheromone decay (multiplicative).
    2. Pheromone diffusion (toroidal 3x3 blur).
    3. Material erosion (slow baseline decay).
    4. Self-maintenance emission (gated by params['self_maintenance']): the
       accumulated structure re-emits cement pheromone — the trace->actor loop.
    """
    phero_decay = params.get("pheromone_decay", PHEROMONE_DECAY)
    phero_diffuse = params.get("pheromone_diffuse", PHEROMONE_DIFFUSE)
    material_decay = params.get("material_decay", MATERIAL_DECAY)
    structure_threshold = params.get("structure_threshold", STRUCTURE_THRESHOLD)

    # 1. Pheromone decay
    field.pheromone *= (1.0 - phero_decay)

    # 2. Pheromone diffusion
    if phero_diffuse > 0.0:
        field.pheromone = _diffuse(field.pheromone, phero_diffuse)

    # 3. Material erosion
    field.material *= (1.0 - material_decay)

    # 4. Self-maintenance emission (the trace->actor feedback)
    if params.get("self_maintenance", False):
        gain = params.get("maintain_gain", MAINTAIN_GAIN)
        structure_mask = field.material > structure_threshold
        if structure_mask.any():
            field.pheromone[structure_mask] += gain * field.material[structure_mask]


# ---------------------------------------------------------------------------
# Core simulation loop + metrics (Part 4)
# ---------------------------------------------------------------------------
def compute_metrics(field, params, step, deposits, pickups, prev_mask, dep_on_struct=0):
    """Build one history record for the current sampled timestep.

    Part 5 fills n_pillars/compactness/crossing-related fields.
    """
    structure_threshold = params.get("structure_threshold", STRUCTURE_THRESHOLD)
    struct_mask = field.material > structure_threshold
    n_struct = int(struct_mask.sum())

    if n_struct > 0:
        mean_phero_over_struct = float(field.pheromone[struct_mask].mean())
        max_phero = float(field.pheromone.max())
    else:
        mean_phero_over_struct = float(field.pheromone.mean())
        max_phero = float(field.pheromone.max())

    if prev_mask is None:
        stability = 1.0
    elif prev_mask.sum() == 0:
        stability = 1.0
    else:
        survived = (struct_mask & prev_mask).sum()
        stability = float(survived / prev_mask.sum())

    # Morphology (Part 5)
    n_pillars = count_components(struct_mask)
    compactness = compute_compactness(struct_mask)

    # deposit_on_structure_fraction over this window
    if deposits > 0:
        dep_on_struct_frac = float(dep_on_struct / deposits)
    else:
        dep_on_struct_frac = 0.0

    return {
        "step": int(step),
        "total_material": float(field.material.sum()),
        "n_structure_cells": n_struct,
        "mean_pheromone": mean_phero_over_struct,
        "max_pheromone": max_phero,
        "n_pillars": n_pillars,
        "compactness": compactness,
        "mean_pheromone_over_structure": mean_phero_over_struct,
        "deposit_on_structure_fraction": dep_on_struct_frac,
        "deposits_this_window": int(deposits),
        "pickups_this_window": int(pickups),
        "structure_stability": stability,
        "crossed": False,
        "crossing_step": None,
    }


def summarize(history):
    """Compute headline summary numbers from a condition's history."""
    if not history:
        return {
            "final_total_material": 0.0,
            "final_n_structure_cells": 0,
            "peak_total_material": 0.0,
            "peak_step": None,
            "mean_stability_last25": 0.0,
            "retention": 0.0,
            "crossed": False,
            "crossing_step": None,
        }
    final = history[-1]
    peak_rec = max(history, key=lambda r: r["total_material"])
    peak = peak_rec["total_material"]
    peak_step = peak_rec["step"]

    n_last = max(1, len(history) // 4)
    last_quarter = history[-n_last:]
    mean_stab = float(sum(r["structure_stability"] for r in last_quarter) / len(last_quarter))

    retention = float(final["total_material"] / peak) if peak > 0 else 0.0

    crossed = any(r.get("crossed", False) for r in history)
    crossing_step = None
    for r in history:
        if r.get("crossed", False):
            crossing_step = r.get("crossing_step")
            break

    return {
        "final_total_material": float(final["total_material"]),
        "final_n_structure_cells": int(final["n_structure_cells"]),
        "peak_total_material": float(peak),
        "peak_step": peak_step,
        "mean_stability_last25": mean_stab,
        "retention": retention,
        "crossed": crossed,
        "crossing_step": crossing_step,
    }


def run_condition(params, seed, perturb=None):
    """Run one full simulation condition. Returns {"history": [...], "summary": {...}}.

    If `perturb={"at": step, "frac": f}` is set, zero out a central square patch
    covering fraction `f` of grid area in BOTH material and pheromone at step `at`,
    and record `recovery` (current/pre-perturb total_material) post-perturbation.
    """
    rng = make_rng(seed)
    size = params.get("grid_size", GRID_SIZE)
    n = params.get("n_termites", N_TERMITES)
    steps = params.get("steps", STEPS)
    sample = params.get("sample_every", SAMPLE_EVERY)

    field = Field(size)
    termites = Termites(n, size, rng)
    history = []
    dep_acc = 0
    pick_acc = 0
    dep_on_struct_acc = 0
    prev_structure_mask = None
    pre_perturb_total = None
    perturb_applied = False

    for step in range(steps):
        # Apply perturbation at the specified step (before termite/field updates)
        if perturb is not None and not perturb_applied and step >= perturb["at"]:
            frac = perturb.get("frac", 0.25)
            side = int(max(1, round(size * math.sqrt(frac))))
            cy, cx = size // 2, size // 2
            y0, y1 = cy - side // 2, cy - side // 2 + side
            x0, x1 = cx - side // 2, cx - side // 2 + side
            field.material[y0:y1, x0:x1] = 0.0
            field.pheromone[y0:y1, x0:x1] = 0.0
            perturb_applied = True

        ev = termite_step(termites, field, rng, params)
        field_step(field, params)
        dep_acc += ev["deposits"]
        pick_acc += ev["pickups"]
        dep_on_struct_acc += ev.get("deposits_on_structure", 0)

        if step % sample == 0:
            rec = compute_metrics(field, params, step, dep_acc, pick_acc,
                                  prev_structure_mask, dep_on_struct_acc)
            # Capture pre-perturb total at the last sample before perturbation
            if perturb is not None:
                if not perturb_applied:
                    pre_perturb_total = rec["total_material"]
                rec["recovery"] = (rec["total_material"] / pre_perturb_total
                                   if pre_perturb_total and pre_perturb_total > 0 else 1.0)
            history.append(rec)
            dep_acc = 0
            pick_acc = 0
            dep_on_struct_acc = 0
            prev_structure_mask = (field.material > params.get("structure_threshold", STRUCTURE_THRESHOLD)).copy()

    detect_crossing(history, params)
    summary = summarize(history)
    if perturb is not None:
        summary["perturb_at"] = perturb["at"]
        summary["perturb_frac"] = perturb.get("frac", 0.25)
        recs_post = [r for r in history if r.get("recovery") is not None and r["step"] >= perturb["at"]]
        summary["recovery_final"] = recs_post[-1]["recovery"] if recs_post else 1.0
    return {"history": history, "summary": summary}


# ---------------------------------------------------------------------------
# Morphology + crossing detector (Part 5 — the scientific payload)
# ---------------------------------------------------------------------------
def count_components(mask):
    """Count connected components (8-connectivity) of a boolean grid via BFS."""
    if not mask.any():
        return 0
    visited = np.zeros_like(mask, dtype=bool)
    h, w = mask.shape
    n = 0
    # 8-neighbour offsets
    nbrs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)]
    for i in range(h):
        for j in range(w):
            if mask[i, j] and not visited[i, j]:
                n += 1
                stack = [(i, j)]
                visited[i, j] = True
                while stack:
                    y, x = stack.pop()
                    for dy, dx in nbrs:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            stack.append((ny, nx))
    return n


def compute_compactness(mask):
    """n_structure_cells / bounding_box_area. 1.0 = filled box, low = scattered."""
    if not mask.any():
        return 0.0
    ys, xs = np.where(mask)
    h = ys.max() - ys.min() + 1
    w = xs.max() - xs.min() + 1
    bbox_area = h * w
    return float(mask.sum() / bbox_area) if bbox_area > 0 else 0.0


def detect_crossing(history, params):
    """Walk history; flag the trace->actor crossing per H7's three criteria.

    A crossing is declared at the first sampled step where ALL THREE hold and
    stay true for >= CROSSING_PERSIST consecutive samples. Once declared, all
    later records are marked crossed=True with crossing_step set.

    Criteria:
      1. Persistence despite erosion: structure_stability >= STAB_THRESH.
      2. Non-reducible dynamics: mean_pheromone_over_structure >= PHERO_ELEV_THRESH
         while fresh deposit rate is below its early-run average.
      3. Constraint on agents: deposit_on_structure_fraction >= CONSTRAIN_THRESH.
    """
    stab_thresh = params.get("stab_thresh", STAB_THRESH)
    phero_elev = params.get("phero_elev_thresh", PHERO_ELEV_THRESH)
    constrain_thresh = params.get("constrain_thresh", CONSTRAIN_THRESH)
    persist = params.get("crossing_persist", CROSSING_PERSIST)

    n = len(history)
    if n == 0:
        return

    # Early-run average deposit rate: first 20% of samples
    n_early = max(1, n // 5)
    early_avg = sum(r["deposits_this_window"] for r in history[:n_early]) / n_early

    run = 0
    crossing_step = None
    for r in history:
        c1 = r["structure_stability"] >= stab_thresh
        c2 = (r["mean_pheromone_over_structure"] >= phero_elev
              and r["deposits_this_window"] < early_avg)
        c3 = r["deposit_on_structure_fraction"] >= constrain_thresh

        if c1 and c2 and c3:
            run += 1
            if run >= persist and crossing_step is None:
                crossing_step = r["step"]
        else:
            run = 0

    # Mark records: once crossed, stay crossed
    for r in history:
        if crossing_step is not None and r["step"] >= crossing_step:
            r["crossed"] = True
            r["crossing_step"] = crossing_step
        else:
            r["crossed"] = False
            r["crossing_step"] = None


# ---------------------------------------------------------------------------
# CLI commands (stubs — populated by later Parts)
# ---------------------------------------------------------------------------
def baseline_params():
    """Baseline condition: decaying pheromone, no self-maintenance loop."""
    return {
        "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
        "sample_every": SAMPLE_EVERY, "structure_threshold": STRUCTURE_THRESHOLD,
        "self_maintenance": False,
        # (all agent/field tunables fall back to module constants)
    }


def self_maintenance_params():
    """Self-maintenance condition: the structure re-emits pheromone (trace->actor loop)."""
    p = baseline_params()
    p["self_maintenance"] = True
    p["maintain_gain"] = MAINTAIN_GAIN
    return p


def cmd_run():
    """Run both conditions + perturbation and write results.json (Parts 6 & 8)."""
    t0 = time.time()

    # Tuned params to maximize condition separation (Part 7 sweep showed defaults
    # give no separation). These produce self-maintenance building ~80% more
    # structure than baseline, but the formal crossing detector does NOT fire for
    # either condition — an honest partial/null result (see README).
    TUNED_MATERIAL_DECAY = 0.01
    TUNED_DEPOSIT_BASE = 0.02

    bp = baseline_params()
    bp["material_decay"] = TUNED_MATERIAL_DECAY
    bp["deposit_base"] = TUNED_DEPOSIT_BASE
    sp = self_maintenance_params()
    sp["material_decay"] = TUNED_MATERIAL_DECAY
    sp["deposit_base"] = TUNED_DEPOSIT_BASE
    sp["maintain_gain"] = 0.3

    print("Running baseline (decaying trace, no self-maintenance)...")
    base = run_condition(bp, seed=SEED)
    print("Running self-maintenance (trace->actor loop)...")
    selfm = run_condition(sp, seed=SEED)

    # Perturbation experiment (Part 8): damage at 60% of steps, 25% area
    perturb = {"at": int(0.6 * STEPS), "frac": 0.25}
    print("Running perturbation experiments (self-repair / H7 acid test)...")
    p_base = run_condition(bp, seed=SEED, perturb=perturb)
    p_sm = run_condition(sp, seed=SEED, perturb=perturb)

    results = {
        "config": {
            "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
            "sample_every": SAMPLE_EVERY, "seed": SEED,
            "pheromone_decay": PHEROMONE_DECAY, "pheromone_diffuse": PHEROMONE_DIFFUSE,
            "material_decay": TUNED_MATERIAL_DECAY, "deposit_base": TUNED_DEPOSIT_BASE,
            "maintain_gain": sp["maintain_gain"], "structure_threshold": STRUCTURE_THRESHOLD,
            "perturb_at": perturb["at"], "perturb_frac": perturb["frac"],
        },
        "baseline": base,
        "self_maintenance": selfm,
        "perturbation": {"baseline": p_base, "self_maintenance": p_sm},
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(_pyify(results), f, indent=2)

    def line(name, r):
        s = r["summary"]
        print(f"  {name:18s} crossed={str(s['crossed']):5s} "
              f"crossing_step={s['crossing_step']} "
              f"retention={s['retention']:.2f} "
              f"final_cells={s['final_n_structure_cells']}")
    print("\n=== RESULT: Trace -> Actor Crossing (H7) ===")
    line("baseline", base)
    line("self_maintenance", selfm)

    print("\n=== RESULT: Perturbation / Self-Repair ===")
    pl_b = p_base["summary"]["recovery_final"]
    pl_s = p_sm["summary"]["recovery_final"]
    print(f"  {'baseline':18s} recovery_final={pl_b:.2f}")
    print(f"  {'self_maintenance':18s} recovery_final={pl_s:.2f}")
    print(f"\nWrote {RESULTS_PATH}  ({time.time()-t0:.1f}s)")


def cmd_sweep_plot():
    """Run parameter sweeps and write PNG plots + raw data under output/ (Part 7)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Cheap sweep params (per spec)
    base = {"grid_size": 80, "n_termites": 150, "steps": 2000, "sample_every": 25}
    sweep_data = {}

    # --- Sweep 1: maintain_gain (self_maintenance ON) ---
    gains = [0.0, 0.02, 0.05, 0.1, 0.2]
    sm_rows = []
    for g in gains:
        p = dict(base)
        p["self_maintenance"] = True
        p["maintain_gain"] = g
        r = run_condition(p, SEED)
        s = r["summary"]
        sm_rows.append({
            "maintain_gain": g,
            "crossed": int(s["crossed"]),
            "crossing_step": s["crossing_step"],
            "retention": s["retention"],
        })
        print(f"  maintain_gain={g}: crossed={s['crossed']} retention={s['retention']:.3f}")
    sweep_data["maintain_gain"] = sm_rows

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax2 = ax.twinx()
    ax.plot(gains, [row["retention"] for row in sm_rows], "o-", color="#58a6ff", label="retention")
    cs = [row["crossing_step"] if row["crossing_step"] is not None else 0 for row in sm_rows]
    ax2.bar(gains, [row["crossed"] for row in sm_rows], alpha=0.25, color="#f0883e", width=0.01, label="crossed")
    ax.set_xlabel("maintain_gain")
    ax.set_ylabel("retention", color="#58a6ff")
    ax2.set_ylabel("crossed (0/1)", color="#f0883e")
    ax.set_title("Sweep: maintain_gain vs retention & crossing (self-maintenance)")
    ax.set_ylim(0, 1.05)
    ax2.set_ylim(-0.05, 1.2)
    fig.tight_layout()
    p1 = os.path.join(OUTPUT_DIR, "sweep_maintain_gain.png")
    fig.savefig(p1, dpi=120)
    plt.close(fig)
    print(f"  wrote {p1}")

    # --- Sweep 2: material_decay (both conditions) ---
    decays = [0.0002, 0.0005, 0.001, 0.002, 0.004]
    base_rows = []
    sm_rows2 = []
    for d in decays:
        pb = dict(base)
        pb["self_maintenance"] = False
        pb["material_decay"] = d
        rb = run_condition(pb, SEED)
        sb = rb["summary"]
        base_rows.append({"material_decay": d, "retention": sb["retention"]})
        ps = dict(base)
        ps["self_maintenance"] = True
        ps["material_decay"] = d
        rs = run_condition(ps, SEED)
        ss = rs["summary"]
        sm_rows2.append({"material_decay": d, "retention": ss["retention"]})
        print(f"  material_decay={d}: base_ret={sb['retention']:.3f} sm_ret={ss['retention']:.3f}")
    sweep_data["material_decay"] = {"baseline": base_rows, "self_maintenance": sm_rows2}

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(decays, [r["retention"] for r in base_rows], "o-", color="#f0883e", label="baseline")
    ax.plot(decays, [r["retention"] for r in sm_rows2], "s-", color="#58a6ff", label="self-maintenance")
    ax.set_xlabel("material_decay")
    ax.set_ylabel("retention")
    ax.set_title("Sweep: material_decay vs retention (baseline vs self-maintenance)")
    ax.set_ylim(0, 1.05)
    ax.legend()
    fig.tight_layout()
    p2 = os.path.join(OUTPUT_DIR, "sweep_material_decay.png")
    fig.savefig(p2, dpi=120)
    plt.close(fig)
    print(f"  wrote {p2}")

    # --- Optional Sweep 3: n_termites (both conditions) ---
    nts = [50, 100, 200, 400]
    nt_base = []
    nt_sm = []
    for nt in nts:
        pb = dict(base)
        pb["n_termites"] = nt
        pb["self_maintenance"] = False
        rb = run_condition(pb, SEED)
        nt_base.append({"n_termites": nt, "final_cells": rb["summary"]["final_n_structure_cells"]})
        ps = dict(base)
        ps["n_termites"] = nt
        ps["self_maintenance"] = True
        rs = run_condition(ps, SEED)
        nt_sm.append({"n_termites": nt, "final_cells": rs["summary"]["final_n_structure_cells"]})
        print(f"  n_termites={nt}: base_cells={nt_base[-1]['final_cells']} sm_cells={nt_sm[-1]['final_cells']}")
    sweep_data["n_termites"] = {"baseline": nt_base, "self_maintenance": nt_sm}

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(nts, [r["final_cells"] for r in nt_base], "o-", color="#f0883e", label="baseline")
    ax.plot(nts, [r["final_cells"] for r in nt_sm], "s-", color="#58a6ff", label="self-maintenance")
    ax.set_xlabel("n_termites")
    ax.set_ylabel("final n_structure_cells")
    ax.set_title("Sweep: n_termites vs final structure cells")
    ax.legend()
    fig.tight_layout()
    p3 = os.path.join(OUTPUT_DIR, "sweep_n_termites.png")
    fig.savefig(p3, dpi=120)
    plt.close(fig)
    print(f"  wrote {p3}")

    with open(os.path.join(OUTPUT_DIR, "sweep_data.json"), "w") as f:
        json.dump(_pyify(sweep_data), f, indent=2)
    print(f"  wrote {os.path.join(OUTPUT_DIR, 'sweep_data.json')}")


def cmd_selftest():
    # Part 1 checks
    assert GRID_SIZE > 0 and N_TERMITES > 0 and STEPS > 0
    f = Field(GRID_SIZE)
    assert f.material.shape == (GRID_SIZE, GRID_SIZE)
    assert _pyify({"a": np.float64(1.5)}) == {"a": 1.5}
    print("selftest: Part 1 OK")

    # Part 2 checks: termites move, deposit, accumulate material
    f2 = Field(50)
    t2 = Termites(50, 50, make_rng(123))
    params2 = {}
    for _ in range(100):
        termite_step(t2, f2, make_rng(456), params2)
    assert f2.material.sum() > 0, "Part 2: termites did not deposit any material"
    assert isinstance(t2.loaded, np.ndarray) and t2.loaded.dtype == bool
    assert len(t2.loaded) == 50
    print("selftest: Part 2 OK")

    # Part 3 checks: field decay/diffusion/erosion + self-maintenance
    f3 = Field(20)
    f3.material[10, 10] = 5.0
    f3.pheromone[10, 10] = 5.0
    p0 = f3.pheromone[10, 10]
    baseline3 = {}
    for _ in range(50):
        field_step(f3, baseline3)
    # pheromone at source decreased under baseline (decay wins, no replenish)
    assert f3.pheromone[10, 10] < p0
    # pheromone spread to at least one neighbour
    assert (f3.pheromone[9:12, 9:12] > 0).sum() > 1
    # material eroded (decreased)
    assert f3.material[10, 10] < 5.0

    # self-maintenance keeps pheromone elevated over a material blob
    f3b = Field(20)
    f3b.material[10, 10] = 5.0
    f3b.pheromone[10, 10] = 5.0
    sm3 = {"self_maintenance": True, "pheromone_decay": 0.2}
    for _ in range(50):
        field_step(f3b, sm3)
    assert f3b.pheromone[10, 10] > 0.1, "Part 3: self-maintenance failed to sustain pheromone"
    print("selftest: Part 3 OK")

    # Part 4 checks: run_condition produces a valid history
    p4 = {"grid_size": 30, "n_termites": 20, "steps": 200, "sample_every": 25}
    res4 = run_condition(p4, 7)
    h4 = res4["history"]
    assert len(h4) >= 4, f"Part 4: expected >=4 records, got {len(h4)}"
    required = {"step", "total_material", "n_structure_cells", "mean_pheromone",
                "max_pheromone", "deposits_this_window", "pickups_this_window",
                "structure_stability", "n_pillars", "compactness", "crossed",
                "crossing_step"}
    for r in h4:
        assert required.issubset(r.keys()), f"Part 4: record missing keys: {required - r.keys()}"
    assert "retention" in res4["summary"]
    print("selftest: Part 4 OK")

    # Part 5 checks: crossing detector + morphology fields present
    p5a = {"grid_size": 30, "n_termites": 20, "steps": 200, "sample_every": 25, "self_maintenance": True}
    p5b = {"grid_size": 30, "n_termites": 20, "steps": 200, "sample_every": 25, "self_maintenance": False}
    r5a = run_condition(p5a, 11)
    r5b = run_condition(p5b, 12)
    morpho_keys = {"n_pillars", "compactness", "mean_pheromone_over_structure",
                   "deposit_on_structure_fraction", "crossed", "crossing_step"}
    for rec in r5a["history"] + r5b["history"]:
        assert morpho_keys.issubset(rec.keys()), "Part 5: missing morphology keys"
    # detect_crossing runs without error (don't assert which crosses at tiny scale)
    assert "crossed" in r5a["summary"] and "crossing_step" in r5a["summary"]
    # count_components / compute_compactness unit checks
    assert count_components(np.zeros((10, 10), dtype=bool)) == 0
    m = np.zeros((10, 10), dtype=bool)
    m[1, 1] = True
    m[1, 2] = True
    m[5, 5] = True
    assert count_components(m) == 2
    assert abs(compute_compactness(m) - 3.0 / (2 * 5)) < 1e-9 or abs(compute_compactness(m) - 3.0 / (5 * 5)) < 1e-9
    print("selftest: Part 5 OK")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        cmd_run()
    elif cmd == "sweep_plot":
        cmd_sweep_plot()
    elif cmd == "selftest":
        cmd_selftest()
    else:
        print("usage: sim06.py [run|sweep_plot|selftest]")


if __name__ == "__main__":
    main()
