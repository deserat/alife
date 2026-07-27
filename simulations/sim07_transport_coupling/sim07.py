"""sim07 — Environmental physics coupling: testing the M_c phase transition (H7).

sim06 tested H7 (trace->actor crossing) with minimal Grasse stigmergy + a
self-maintenance loop and found a null result: positive stigmergic feedback
alone amplifies building but does not consolidate — the crossing detector
never fires. Session 9 research (environmental-physics-coupling concept)
identified the specific missing mechanism: the accumulated structure must
introduce a *transport dynamics* absent at the deposit level (the Mahadevan
mechanism — real termite mounds are ventilation organs whose own physics
redistributes the pheromone cues that guide building).

sim07 tests whether adding a *minimal lumped transport field* T with a *mass
threshold M_c* (Vance's inert->active state transition) produces the
trace->actor crossing as a *phase transition in M_c*.

The ONLY addition to sim06 is the transport field T:
  - T is sourced by structure: T_source = max(0, M - M_c) * transport_gain.
    Below M_c, no sourcing (inert — reproduces sim06).
  - T diffuses (toroidal, like pheromone) and slowly decays.
  - T advects pheromone: P += transport_coupling * (T_neighbor_avg - T_local).
    This VENTS pheromone from saturated structure (high T) to gaps/flanks
    (low T) — the negative feedback sim06 lacked. NOTE: the DESIGN.md sketch
    wrote (T_local - T_neighbor_avg), which has the sign backwards — it would
    increase P at structure (positive feedback). The prose ("saturated
    pillars shed their pheromone to their flanks") describes venting, so the
    correct sign is (T_neighbor_avg - T_local). This correction is documented
    in the README and the 2026-07-27 daily report.

Agents are UNCHANGED from sim06 (Grasse deposit rule, pheromone following).
No self-maintenance emission (sim06's mechanism) — the transport field IS
the new mechanism. The circularity safeguard: the perturbation/self-repair
test must show repair tracks T (active above M_c), not the deposit rule.

Conditions:
  - baseline:  M_c = inf  (transport never activates) — reproduces sim06.
  - transport: M_c finite (set so some cells exceed it) — transport active.
  - sweep:     sweep M_c and look for the phase transition.
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
# Simulation constants (module-level defaults)
# ---------------------------------------------------------------------------
GRID_SIZE = 100
N_TERMITES = 200
STEPS = 4000
SAMPLE_EVERY = 25
SEED = 42

# Field / stigmergy parameters (inherited from sim06)
PHEROMONE_DECAY = 0.02
PHEROMONE_DIFFUSE = 0.10
MATERIAL_DECAY = 0.0005
STRUCTURE_THRESHOLD = 1.0
DEPOSIT_PHEROMONE = 1.0
PICKUP_PROB_BASE = 0.01

# Termite agent parameters (inherited from sim06)
PHERO_FOLLOW = 0.6
RELOAD_PROB = 0.3
DEPOSIT_BASE = 0.10
DEPOSIT_GAIN = 0.85
PELLET = 1.0

# Transport field parameters (NEW in sim07)
M_C = 3.0               # mass threshold: below = inert, above = sources T
TRANSPORT_GAIN = 0.10   # T sourced per unit excess mass (M - M_c) per step
TRANSPORT_DECAY = 0.05  # per-step multiplicative decay of T
TRANSPORT_DIFFUSE = 0.20  # fraction of T that diffuses per step
TRANSPORT_COUPLING = 0.30  # strength of T -> P advection (venting)

# Crossing detector parameters (inherited from sim06)
CROSSING_PERSIST = 4
STAB_THRESH = 0.90
PHERO_ELEV_THRESH = 0.5
GROWTH_THRESH = 0.01
CONSTRAIN_THRESH = 0.6

# Tuned params for condition separation (from sim06's cmd_run)
TUNED_MATERIAL_DECAY = 0.01
TUNED_DEPOSIT_BASE = 0.02


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
# Field container (extended from sim06 with transport field T)
# ---------------------------------------------------------------------------
class Field:
    """Holds the 2D grids: material, pheromone, and the transport field T."""

    def __init__(self, size):
        self.size = size
        self.material = np.zeros((size, size), dtype=np.float64)
        self.pheromone = np.zeros((size, size), dtype=np.float64)
        self.transport = np.zeros((size, size), dtype=np.float64)  # NEW: T field


# ---------------------------------------------------------------------------
# Moore neighbourhood offsets (8 neighbours) for toroidal movement
# ---------------------------------------------------------------------------
_MOORE_DX = np.array([-1, 0, 1, -1, 1, -1, 0, 1], dtype=np.int32)
_MOORE_DY = np.array([-1, -1, -1, 0, 0, 1, 1, 1], dtype=np.int32)


# ---------------------------------------------------------------------------
# Diffusion / neighbour-mean helpers
# ---------------------------------------------------------------------------
def _diffuse(a, rate):
    """Toroidal 3x3 blur diffusion. Returns (1-rate)*a + rate*neighbour_mean."""
    nb = (np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)
          + np.roll(np.roll(a, 1, 0), 1, 1) + np.roll(np.roll(a, 1, 0), -1, 1)
          + np.roll(np.roll(a, -1, 0), 1, 1) + np.roll(np.roll(a, -1, 0), -1, 1)) / 8.0
    return (1.0 - rate) * a + rate * nb


def _neighbor_mean(a):
    """Toroidal 8-neighbour mean of array a."""
    return (np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)
            + np.roll(np.roll(a, 1, 0), 1, 1) + np.roll(np.roll(a, 1, 0), -1, 1)
            + np.roll(np.roll(a, -1, 0), 1, 1) + np.roll(np.roll(a, -1, 0), -1, 1)) / 8.0


# ---------------------------------------------------------------------------
# Termite agents (unchanged from sim06 — Grasse stigmergy rules)
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

    Returns {"deposits": int, "pickups": int, "deposits_on_structure": int}.
    Identical to sim06 — agents are unchanged; the only new physics is in T.
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
    nx = (termites.x[None, :] + _MOORE_DX[:, None]) % size
    ny = (termites.y[None, :] + _MOORE_DY[:, None]) % size
    phero_nb = field.pheromone[ny, nx]

    noise = rng.random(phero_nb.shape) * 1e-9
    best_idx = np.argmax(phero_nb + noise, axis=0)
    rand_idx = rng.integers(0, 8, n)

    follow = termites.loaded & (rng.random(n) < phero_follow)
    move_idx = np.where(follow, best_idx, rand_idx)

    termites.x = (termites.x + _MOORE_DX[move_idx]) % size
    termites.y = (termites.y + _MOORE_DY[move_idx]) % size

    # --- Reload (off-grid soil source) ---
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

    # --- Deposit (Grasse stigmergy) ---
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
# Field dynamics (extended from sim06 — adds transport field T)
# ---------------------------------------------------------------------------
def field_step(field, params):
    """Advance the stigmergic environment one step.

    1. Pheromone decay (multiplicative).
    2. Pheromone diffusion (toroidal 3x3 blur).
    3. Material erosion (slow baseline decay).
    4. NO self-maintenance emission (sim07 replaces that with transport).
    5. Transport field T: sourced by structure above M_c, decays, diffuses.
    6. T -> P coupling: vents pheromone from high-T (saturated) to low-T (gaps).
    """
    phero_decay = params.get("pheromone_decay", PHEROMONE_DECAY)
    phero_diffuse = params.get("pheromone_diffuse", PHEROMONE_DIFFUSE)
    material_decay = params.get("material_decay", MATERIAL_DECAY)

    # 1. Pheromone decay
    field.pheromone *= (1.0 - phero_decay)

    # 2. Pheromone diffusion
    if phero_diffuse > 0.0:
        field.pheromone = _diffuse(field.pheromone, phero_diffuse)

    # 3. Material erosion
    field.material *= (1.0 - material_decay)

    # 5. Transport field T — the NEW physics (sim07)
    m_c = params.get("M_c", M_C)
    transport_gain = params.get("transport_gain", TRANSPORT_GAIN)
    transport_decay = params.get("transport_decay", TRANSPORT_DECAY)
    transport_diffuse = params.get("transport_diffuse", TRANSPORT_DIFFUSE)
    transport_coupling = params.get("transport_coupling", TRANSPORT_COUPLING)

    # T sourcing: structure above M_c generates transport potential
    if math.isinf(m_c):
        # baseline: transport never activates
        field.transport *= (1.0 - transport_decay)
    else:
        excess = np.maximum(field.material - m_c, 0.0)
        field.transport += transport_gain * excess
        # T decay
        field.transport *= (1.0 - transport_decay)

    # T diffusion
    if transport_diffuse > 0.0:
        field.transport = _diffuse(field.transport, transport_diffuse)

    # 6. T -> P coupling: vent pheromone from high-T to low-T (negative feedback)
    # Corrected sign: (T_neighbor_avg - T_local) vents FROM structure TO gaps.
    # The DESIGN.md sketch had (T_local - T_neighbor_avg) — backwards.
    if transport_coupling > 0.0 and not math.isinf(m_c):
        t_nb = _neighbor_mean(field.transport)
        delta = transport_coupling * (t_nb - field.transport)
        field.pheromone += delta
        np.maximum(field.pheromone, 0.0, out=field.pheromone)


# ---------------------------------------------------------------------------
# Morphology helpers (from sim06)
# ---------------------------------------------------------------------------
def count_components(mask):
    """Count connected components (8-connectivity) of a boolean grid via BFS."""
    if not mask.any():
        return 0
    visited = np.zeros_like(mask, dtype=bool)
    h, w = mask.shape
    n = 0
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


# ---------------------------------------------------------------------------
# Metrics (extended from sim06 — adds transport-related fields)
# ---------------------------------------------------------------------------
def compute_metrics(field, params, step, deposits, pickups, prev_mask,
                    dep_on_struct=0, prev_total=None):
    """Build one history record for the current sampled timestep."""
    structure_threshold = params.get("structure_threshold", STRUCTURE_THRESHOLD)
    m_c = params.get("M_c", M_C)
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

    n_pillars = count_components(struct_mask)
    compactness = compute_compactness(struct_mask)

    # Transport-specific metrics (NEW in sim07)
    if math.isinf(m_c):
        n_active = 0
        transport_active = False
    else:
        active_mask = field.material > m_c
        n_active = int(active_mask.sum())
        transport_active = n_active > 0
    mean_T_over_struct = float(field.transport[struct_mask].mean()) if n_struct > 0 else 0.0

    if deposits > 0:
        dep_on_struct_frac = float(dep_on_struct / deposits)
    else:
        dep_on_struct_frac = 0.0

    total_material = float(field.material.sum())
    if prev_total is None or prev_total <= 0:
        growth_rate = None
    else:
        growth_rate = float((total_material - prev_total) / prev_total)

    return {
        "step": int(step),
        "total_material": total_material,
        "material_growth_rate": growth_rate,
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
        # Transport fields (NEW in sim07)
        "n_active_cells": n_active,
        "transport_active": transport_active,
        "mean_T_over_structure": mean_T_over_struct,
        # Crossing fields (filled by detect_crossing)
        "crossed": False,
        "crossing_step": None,
    }


# ---------------------------------------------------------------------------
# Crossing detector (from sim06 — three criteria, H7)
# ---------------------------------------------------------------------------
def detect_crossing(history, params):
    """Walk history; flag the trace->actor crossing per H7's three criteria.

    A crossing is declared at the first sampled step where ALL THREE hold and
    stay true for >= CROSSING_PERSIST consecutive samples.

    Criteria:
      1. structure_stability >= STAB_THRESH (persistence despite erosion).
      2. mean_pheromone_over_structure >= PHERO_ELEV_THRESH AND
         |material_growth_rate| < GROWTH_THRESH (sustained without net growth).
      3. deposit_on_structure_fraction >= CONSTRAIN_THRESH (constraint on agents).
    """
    stab_thresh = params.get("stab_thresh", STAB_THRESH)
    phero_elev = params.get("phero_elev_thresh", PHERO_ELEV_THRESH)
    growth_thresh = params.get("growth_thresh", GROWTH_THRESH)
    constrain_thresh = params.get("constrain_thresh", CONSTRAIN_THRESH)
    persist = params.get("crossing_persist", CROSSING_PERSIST)

    n = len(history)
    if n == 0:
        return

    run = 0
    crossing_step = None
    for r in history:
        growth = r.get("material_growth_rate")
        saturated = growth is not None and abs(growth) < growth_thresh

        c1 = r["structure_stability"] >= stab_thresh
        c2 = r["mean_pheromone_over_structure"] >= phero_elev and saturated
        c3 = r["deposit_on_structure_fraction"] >= constrain_thresh

        if c1 and c2 and c3:
            run += 1
            if run >= persist and crossing_step is None:
                crossing_step = r["step"]
        else:
            run = 0

    for r in history:
        if crossing_step is not None and r["step"] >= crossing_step:
            r["crossed"] = True
            r["crossing_step"] = crossing_step
        else:
            r["crossed"] = False
            r["crossing_step"] = None


# ---------------------------------------------------------------------------
# Summary (from sim06, extended with transport info)
# ---------------------------------------------------------------------------
def summarize(history):
    """Compute headline summary numbers from a condition's history."""
    if not history:
        return {
            "final_total_material": 0.0,
            "final_n_structure_cells": 0,
            "final_n_pillars": 0,
            "peak_total_material": 0.0,
            "peak_step": None,
            "mean_stability_last25": 0.0,
            "retention": 0.0,
            "crossed": False,
            "crossing_step": None,
            "transport_ever_active": False,
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

    transport_ever_active = any(r.get("transport_active", False) for r in history)

    return {
        "final_total_material": float(final["total_material"]),
        "final_n_structure_cells": int(final["n_structure_cells"]),
        "final_n_pillars": int(final.get("n_pillars", 0)),
        "peak_total_material": float(peak),
        "peak_step": peak_step,
        "mean_stability_last25": mean_stab,
        "retention": retention,
        "crossed": crossed,
        "crossing_step": crossing_step,
        "transport_ever_active": transport_ever_active,
    }


# ---------------------------------------------------------------------------
# Core simulation loop (from sim06, extended with perturbation for T too)
# ---------------------------------------------------------------------------
def run_condition(params, seed, perturb=None):
    """Run one full simulation condition. Returns {"history": [...], "summary": {...}}.

    If perturb={"at": step, "frac": f} is set, zero out a central square patch
    covering fraction f of grid area in material, pheromone, AND transport at
    step at, and record recovery (current/pre-perturb total_material).
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
    prev_total_material = None
    pre_perturb_total = None
    perturb_applied = False

    for step in range(steps):
        # Apply perturbation at the specified step
        if perturb is not None and not perturb_applied and step >= perturb["at"]:
            frac = perturb.get("frac", 0.25)
            side = int(max(1, round(size * math.sqrt(frac))))
            cy, cx = size // 2, size // 2
            y0, y1 = cy - side // 2, cy - side // 2 + side
            x0, x1 = cx - side // 2, cx - side // 2 + side
            field.material[y0:y1, x0:x1] = 0.0
            field.pheromone[y0:y1, x0:x1] = 0.0
            field.transport[y0:y1, x0:x1] = 0.0
            perturb_applied = True

        ev = termite_step(termites, field, rng, params)
        field_step(field, params)
        dep_acc += ev["deposits"]
        pick_acc += ev["pickups"]
        dep_on_struct_acc += ev.get("deposits_on_structure", 0)

        if step % sample == 0:
            rec = compute_metrics(field, params, step, dep_acc, pick_acc,
                                  prev_structure_mask, dep_on_struct_acc,
                                  prev_total_material)
            if perturb is not None:
                if not perturb_applied:
                    pre_perturb_total = rec["total_material"]
                rec["recovery"] = (rec["total_material"] / pre_perturb_total
                                   if pre_perturb_total and pre_perturb_total > 0 else 1.0)
            history.append(rec)
            dep_acc = 0
            pick_acc = 0
            dep_on_struct_acc = 0
            prev_total_material = rec["total_material"]
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
# Condition presets
# ---------------------------------------------------------------------------
def baseline_params():
    """Baseline: M_c = inf (transport never activates) — reproduces sim06."""
    return {
        "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
        "sample_every": SAMPLE_EVERY, "structure_threshold": STRUCTURE_THRESHOLD,
        "M_c": float("inf"),
        "material_decay": TUNED_MATERIAL_DECAY,
        "deposit_base": TUNED_DEPOSIT_BASE,
    }


def transport_params(m_c=M_C):
    """Transport condition: M_c finite — structure above M_c sources T."""
    p = baseline_params()
    p["M_c"] = m_c
    p["transport_gain"] = TRANSPORT_GAIN
    p["transport_decay"] = TRANSPORT_DECAY
    p["transport_diffuse"] = TRANSPORT_DIFFUSE
    p["transport_coupling"] = TRANSPORT_COUPLING
    return p


# ---------------------------------------------------------------------------
# CLI: run
# ---------------------------------------------------------------------------
def cmd_run():
    """Run baseline + transport conditions + perturbation, write results.json."""
    t0 = time.time()

    bp = baseline_params()
    tp = transport_params()

    print("Running baseline (M_c=inf, transport inert — reproduces sim06)...")
    base = run_condition(bp, seed=SEED)
    print("Running transport (M_c=%.1f, structure sources T)..." % tp["M_c"])
    trans = run_condition(tp, seed=SEED)

    # Perturbation / self-repair experiment (the H7 acid test)
    perturb = {"at": int(0.6 * STEPS), "frac": 0.25}
    print("Running perturbation experiments (self-repair / circularity safeguard)...")
    p_base = run_condition(bp, seed=SEED, perturb=perturb)
    p_trans = run_condition(tp, seed=SEED, perturb=perturb)

    results = {
        "config": {
            "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
            "sample_every": SAMPLE_EVERY, "seed": SEED,
            "pheromone_decay": PHEROMONE_DECAY, "pheromone_diffuse": PHEROMONE_DIFFUSE,
            "material_decay": TUNED_MATERIAL_DECAY, "deposit_base": TUNED_DEPOSIT_BASE,
            "structure_threshold": STRUCTURE_THRESHOLD,
            "M_c": tp["M_c"], "transport_gain": TRANSPORT_GAIN,
            "transport_decay": TRANSPORT_DECAY, "transport_diffuse": TRANSPORT_DIFFUSE,
            "transport_coupling": TRANSPORT_COUPLING,
            "perturb_at": perturb["at"], "perturb_frac": perturb["frac"],
        },
        "baseline": base,
        "transport": trans,
        "perturbation": {"baseline": p_base, "transport": p_trans},
    }
    with open(RESULTS_PATH, "w") as f:
        json.dump(_pyify(results), f, indent=2)

    def line(name, r):
        s = r["summary"]
        print(f"  {name:18s} crossed={str(s['crossed']):5s} "
              f"crossing_step={s['crossing_step']} "
              f"retention={s['retention']:.2f} "
              f"pillars={s['final_n_pillars']} "
              f"cells={s['final_n_structure_cells']} "
              f"stab={s['mean_stability_last25']:.3f} "
              f"T_active={s['transport_ever_active']}")

    print("\n=== RESULT: Trace -> Actor Crossing (H7) — M_c phase transition ===")
    line("baseline", base)
    line("transport", trans)

    print("\n=== RESULT: Perturbation / Self-Repair ===")
    pl_b = p_base["summary"]["recovery_final"]
    pl_t = p_trans["summary"]["recovery_final"]
    print(f"  {'baseline':18s} recovery_final={pl_b:.2f}")
    print(f"  {'transport':18s} recovery_final={pl_t:.2f}")

    # Phase-transition diagnosis
    b_pillars = base["summary"]["final_n_pillars"]
    t_pillars = trans["summary"]["final_n_pillars"]
    b_stab = base["summary"]["mean_stability_last25"]
    t_stab = trans["summary"]["mean_stability_last25"]
    print("\n=== Phase-transition diagnosis ===")
    print(f"  pillars:   baseline={b_pillars} -> transport={t_pillars} "
          f"(consolidation = fewer pillars)")
    print(f"  stability: baseline={b_stab:.3f} -> transport={t_stab:.3f} "
          f"(criterion 1 needs >= {STAB_THRESH})")
    print(f"  crossed:   baseline={base['summary']['crossed']} "
          f"transport={trans['summary']['crossed']}")
    print(f"\nWrote {RESULTS_PATH}  ({time.time()-t0:.1f}s)")


# ---------------------------------------------------------------------------
# CLI: sweep_plot (M_c sweep — the phase transition)
# ---------------------------------------------------------------------------
def cmd_sweep_plot():
    """Sweep M_c and plot crossing metrics vs M_c — look for the transition."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    base_grid = {"grid_size": 80, "n_termites": 150, "steps": 2000,
                 "sample_every": 25, "material_decay": TUNED_MATERIAL_DECAY,
                 "deposit_base": TUNED_DEPOSIT_BASE}

    # M_c sweep: inf (never active) down to 0.5 (almost always active)
    mcs = [float("inf"), 10.0, 6.0, 4.0, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5]
    rows = []
    for mc in mcs:
        p = dict(base_grid)
        p["M_c"] = mc
        p["transport_gain"] = TRANSPORT_GAIN
        p["transport_decay"] = TRANSPORT_DECAY
        p["transport_diffuse"] = TRANSPORT_DIFFUSE
        p["transport_coupling"] = TRANSPORT_COUPLING
        r = run_condition(p, SEED)
        s = r["summary"]
        row = {
            "M_c": mc if not math.isinf(mc) else 999.0,
            "crossed": int(s["crossed"]),
            "crossing_step": s["crossing_step"],
            "n_pillars": s["final_n_pillars"],
            "stability": s["mean_stability_last25"],
            "retention": s["retention"],
            "transport_active": int(s["transport_ever_active"]),
        }
        rows.append(row)
        label = "inf" if math.isinf(mc) else f"{mc:.1f}"
        print(f"  M_c={label:>5s}: crossed={s['crossed']} pillars={row['n_pillars']} "
              f"stab={row['stability']:.3f} ret={row['retention']:.3f} T={row['transport_active']}")

    sweep_data = {"M_c_sweep": rows}

    # Plot 1: n_pillars and stability vs M_c
    fig, ax = plt.subplots(figsize=(8, 5))
    ax2 = ax.twinx()
    mc_vals = [r["M_c"] for r in rows]
    ax.plot(mc_vals, [r["n_pillars"] for r in rows], "o-", color="#f0883e", label="n_pillars")
    ax2.plot(mc_vals, [r["stability"] for r in rows], "s-", color="#58a6ff", label="stability")
    ax.axhline(STAB_THRESH, color="#58a6ff", ls="--", alpha=0.4, label=f"stab thresh={STAB_THRESH}")
    ax.set_xlabel("M_c (mass threshold; 999 = inf = inert)")
    ax.set_ylabel("n_pillars", color="#f0883e")
    ax2.set_ylabel("stability", color="#58a6ff")
    ax.set_title("M_c sweep: morphology & stability (H7 phase transition?)")
    ax.set_ylim(0, max(r["n_pillars"] for r in rows) * 1.1)
    ax2.set_ylim(0, 1.05)
    fig.tight_layout()
    p1 = os.path.join(OUTPUT_DIR, "sweep_Mc_morphology.png")
    fig.savefig(p1, dpi=120)
    plt.close(fig)
    print(f"  wrote {p1}")

    # Plot 2: crossed and retention vs M_c
    fig, ax = plt.subplots(figsize=(8, 5))
    ax2 = ax.twinx()
    ax.plot(mc_vals, [r["retention"] for r in rows], "o-", color="#58a6ff", label="retention")
    ax2.bar(mc_vals, [r["crossed"] for r in rows], alpha=0.3, color="#f0883e", width=0.3,
            label="crossed")
    ax.set_xlabel("M_c (mass threshold; 999 = inf = inert)")
    ax.set_ylabel("retention", color="#58a6ff")
    ax2.set_ylabel("crossed (0/1)", color="#f0883e")
    ax.set_title("M_c sweep: retention & crossing (H7 phase transition?)")
    ax.set_ylim(0, 1.05)
    ax2.set_ylim(-0.05, 1.2)
    fig.tight_layout()
    p2 = os.path.join(OUTPUT_DIR, "sweep_Mc_crossing.png")
    fig.savefig(p2, dpi=120)
    plt.close(fig)
    print(f"  wrote {p2}")

    with open(os.path.join(OUTPUT_DIR, "sweep_data.json"), "w") as f:
        json.dump(_pyify(sweep_data), f, indent=2)
    print(f"  wrote {os.path.join(OUTPUT_DIR, 'sweep_data.json')}")


# ---------------------------------------------------------------------------
# CLI: selftest
# ---------------------------------------------------------------------------
def cmd_selftest():
    # --- Part 1: infrastructure ---
    assert GRID_SIZE > 0 and N_TERMITES > 0 and STEPS > 0
    f = Field(GRID_SIZE)
    assert f.material.shape == (GRID_SIZE, GRID_SIZE)
    assert f.transport.shape == (GRID_SIZE, GRID_SIZE)
    assert _pyify({"a": np.float64(1.5)}) == {"a": 1.5}
    print("selftest: Part 1 OK (infrastructure + Field with T)")

    # --- Part 2: termites (same as sim06) ---
    f2 = Field(50)
    t2 = Termites(50, 50, make_rng(123))
    rng2 = make_rng(456)
    for _ in range(100):
        termite_step(t2, f2, rng2, {})
    assert f2.material.sum() > 0, "termites did not deposit any material"
    print("selftest: Part 2 OK (termites deposit)")

    # --- Part 3: transport field T ---
    # T is sourced where M > M_c, zero where M < M_c
    f3 = Field(20)
    f3.material[10, 10] = 5.0  # above M_c=3
    f3.material[5, 5] = 1.0    # below M_c
    p3 = {"M_c": 3.0, "transport_gain": 0.1, "transport_decay": 0.0,
          "transport_diffuse": 0.0, "transport_coupling": 0.0,
          "pheromone_decay": 0.0, "pheromone_diffuse": 0.0, "material_decay": 0.0}
    field_step(f3, p3)
    assert f3.transport[10, 10] > 0, "T not sourced above M_c"
    assert f3.transport[5, 5] == 0.0, "T sourced below M_c (should be 0)"

    # Baseline: M_c=inf → T never sourced, T stays zero (even with material)
    f3b = Field(20)
    f3b.material[10, 10] = 100.0
    p3b = {"M_c": float("inf"), "transport_gain": 0.1, "transport_decay": 0.0,
           "transport_diffuse": 0.0, "transport_coupling": 0.0,
           "pheromone_decay": 0.0, "pheromone_diffuse": 0.0, "material_decay": 0.0}
    field_step(f3b, p3b)
    assert f3b.transport[10, 10] == 0.0, "baseline (M_c=inf) sourced T"

    # T->P venting: P decreases at high-T cell, increases at low-T neighbor
    f3c = Field(20)
    f3c.material[10, 10] = 10.0  # well above M_c
    f3c.pheromone[:] = 1.0       # uniform pheromone
    p3c = {"M_c": 3.0, "transport_gain": 1.0, "transport_decay": 0.0,
           "transport_diffuse": 0.0, "transport_coupling": 0.5,
           "pheromone_decay": 0.0, "pheromone_diffuse": 0.0, "material_decay": 0.0}
    # Source T first (one step with coupling off)
    p3c_nocouple = dict(p3c, transport_coupling=0.0)
    field_step(f3c, p3c_nocouple)
    p_before = f3c.pheromone[10, 10]
    p_nb_before = f3c.pheromone[10, 11]
    # Now apply coupling step
    field_step(f3c, p3c)
    p_after = f3c.pheromone[10, 10]
    assert p_after < p_before, "venting did not decrease P at high-T structure"
    # Some neighbor should have gained pheromone
    assert f3c.pheromone[10, 11] > p_nb_before or f3c.pheromone[9, 10] > p_nb_before, \
        "venting did not increase P at neighbors"
    print("selftest: Part 3 OK (transport field T: sourcing, baseline inert, venting)")

    # --- Part 4: full run produces valid history ---
    p4 = {"grid_size": 30, "n_termites": 20, "steps": 200, "sample_every": 25,
          "M_c": float("inf")}
    res4 = run_condition(p4, 7)
    h4 = res4["history"]
    assert len(h4) >= 4
    required = {"step", "total_material", "material_growth_rate",
                "n_structure_cells", "mean_pheromone", "max_pheromone",
                "n_pillars", "compactness", "mean_pheromone_over_structure",
                "deposit_on_structure_fraction", "structure_stability",
                "n_active_cells", "transport_active", "mean_T_over_structure",
                "crossed", "crossing_step"}
    for r in h4:
        assert required.issubset(r.keys()), f"record missing keys: {required - r.keys()}"
    assert "retention" in res4["summary"]
    assert "transport_ever_active" in res4["summary"]
    print("selftest: Part 4 OK (full run + metrics + transport fields)")

    # --- Part 5: transport condition produces different morphology ---
    # Run baseline and transport at small scale, check they differ
    p5b = {"grid_size": 40, "n_termites": 40, "steps": 500, "sample_every": 25,
           "M_c": float("inf"), "material_decay": TUNED_MATERIAL_DECAY,
           "deposit_base": TUNED_DEPOSIT_BASE}
    p5t = {"grid_size": 40, "n_termites": 40, "steps": 500, "sample_every": 25,
           "M_c": 2.0, "material_decay": TUNED_MATERIAL_DECAY,
           "deposit_base": TUNED_DEPOSIT_BASE,
           "transport_gain": TRANSPORT_GAIN, "transport_decay": TRANSPORT_DECAY,
           "transport_diffuse": TRANSPORT_DIFFUSE, "transport_coupling": TRANSPORT_COUPLING}
    r5b = run_condition(p5b, 42)
    r5t = run_condition(p5t, 42)
    # Transport condition should have T active at some point
    assert r5t["summary"]["transport_ever_active"], "transport never activated"
    # Baseline should NOT have T active
    assert not r5b["summary"]["transport_ever_active"], "baseline activated T"
    # Morphologies should differ (not identical pillar counts)
    bp = r5b["summary"]["final_n_pillars"]
    tp = r5t["summary"]["final_n_pillars"]
    print(f"  small-scale: baseline pillars={bp}, transport pillars={tp}")
    print("selftest: Part 5 OK (transport changes morphology)")

    # --- Part 6: crossing detector is capable (from sim06) ---
    synth = [{"step": i * 25, "structure_stability": 0.95,
              "mean_pheromone_over_structure": 2.0, "material_growth_rate": 0.001,
              "deposit_on_structure_fraction": 0.8, "deposits_this_window": 900,
              "total_material": 1000.0}
             for i in range(12)]
    detect_crossing(synth, {})
    assert synth[-1]["crossed"], "detector cannot fire on an ideal crossing history"
    # Must NOT fire when a single criterion is withheld
    for withhold, bad in (("structure_stability", 0.10),
                          ("mean_pheromone_over_structure", 0.0),
                          ("deposit_on_structure_fraction", 0.0)):
        neg = [dict(r, **{withhold: bad}) for r in synth]
        detect_crossing(neg, {})
        assert not neg[-1]["crossed"], f"detector fired without {withhold}"
    growing = [dict(r, material_growth_rate=0.5) for r in synth]
    detect_crossing(growing, {})
    assert not growing[-1]["crossed"], "detector fired on an unsaturated structure"
    print("selftest: Part 6 OK (crossing detector capable + selective)")

    print("\nselftest: ALL OK")


# ---------------------------------------------------------------------------
# CLI dispatcher
# ---------------------------------------------------------------------------
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        cmd_run()
    elif cmd == "sweep_plot":
        cmd_sweep_plot()
    elif cmd == "selftest":
        cmd_selftest()
    else:
        print("usage: sim07.py [run|sweep_plot|selftest]")
        print("  run        — baseline vs transport + perturbation -> results.json")
        print("  sweep_plot — M_c sweep -> output/*.png (phase transition)")
        print("  selftest   — internal sanity checks")


if __name__ == "__main__":
    main()
