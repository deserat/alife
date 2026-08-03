"""
Sim09: The Curvature Channel — Does a Non-Saturating Channel That Recruits as
Well as Limits Fire the Trace→Actor Crossing?

This simulation tests H7's Session-13/14 refinement: the trace→actor crossing
needs a NON-SATURATING channel that RECRUITS as well as LIMITS. The curvature
channel — what real termites actually use — does both: depositing at a convex
tip extends the tip (recruits further building there), and a smoothing term
caps feature size (limits). It is also the minimal lumped form of the "directed
transport" H7's Session-10 refinement called for (curvature IS directed
geometry).

The substrate is the Facchini, Lazarescu, Perna & Douady (2020, J R Soc
Interface) curvature-only phase-field growth model for termite nests, with NO
pheromone field:

    ∂f/∂t ≈ f(1−f) · [ (1/2)·Δf  +  d·Δ²f ]

- (1/2)·Δf (mean curvature)  = the RECRUIT mechanism (growth at convex tips)
- d·Δ²f   (biharmonic)       = the LIMIT mechanism (caps feature size); `d` is
                              the phase-transition knob (sim09's analog of
                              sim07's M_c)
- f(1−f)                      = surface restriction (deposits at the boundary,
                              not the bulk) — spatial selectivity without a
                              saturating cue.

Following the Facchini/Calovi action-component resolution, sim09 splits the
action: loaded termites DEPOSIT at convex tips (Facchini 2024); unloaded
termites EXCAVATE at concavities (Calovi 2019). Conflating them would invert
the rule's sign. A baseline-pheromone condition (sim06's saturating Grassé
rule) serves as the control. The deliverable is a phase transition in `d`:
below the curvature-instability threshold, diffuse growth with no crossing;
above it, consolidated morphology + the crossing detector firing.
"""

import os
import re
import sys
import json
import math
import time

import numpy as np


# --------------------------------------------------------------------------
# Paths (built from the script's own location — never hardcode home dirs)
# --------------------------------------------------------------------------
SIM_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SIM_DIR, "results.json")
OUTPUT_DIR = os.path.join(SIM_DIR, "output")


# --------------------------------------------------------------------------
# Simulation constants (module-level defaults; Parts reference these)
# --------------------------------------------------------------------------
GRID_SIZE = 100
N_TERMITES = 200
STEPS = 4000
SAMPLE_EVERY = 25
SEED = 42

# Material field / curvature-channel parameters (the Facchini model, 2D)
D_SMOOTH = 1.0               # the d parameter — smoothing strength / phase-transition knob
MATERIAL_DECAY = 0.0005       # slow background erosion (same role as sim06)
STRUCTURE_THRESHOLD = 1.0     # material level above which a cell counts as "structure"
PELLET = 1.0                  # material added per deposit, removed per excavation
SURFACE_THRESHOLD = 0.05      # material above which a cell is "on the structure surface" (for f(1-f))

# Agent / curvature-routing parameters
RELOAD_PROB = 0.3             # prob an unloaded termite refills off-grid (same as sim06)
CURVE_FOLLOW = 0.6            # prob a termite follows the curvature cue (vs random step)
DEPOSIT_PROB_BASE = 0.10      # baseline deposit probability (nucleation on bare ground)
DEPOSIT_PROB_GAIN = 0.85      # curvature-driven deposit probability gain (non-saturating routing)
EXCAVATE_PROB_BASE = 0.05     # baseline excavation probability at concavities
EXCAVATE_PROB_GAIN = 0.60     # curvature-driven excavation probability gain
PICKUP_PROB_BASE = 0.01       # prob an unloaded termite erodes a structure cell (turnover)

# Baseline-pheromone condition (sim06's saturating rule, for the control comparison)
PHEROMONE_DECAY = 0.02
PHEROMONE_DIFFUSE = 0.10
DEPOSIT_PHEROMONE = 1.0
DEPOSIT_BASE = 0.10           # pheromone-condition deposit base (saturating rule)
DEPOSIT_GAIN = 0.85           # pheromone-condition deposit gain (saturating rule)

# Grid snapshots (for visualize.html's grid renderer — not a metric, just a
# downscaled record of field state at sampled steps)
SNAPSHOT_SIZE = 40            # downscaled snapshot side length
SNAPSHOT_TARGET_COUNT = 25    # aim for roughly this many snapshots per run

# Crossing detector (carried over from sim06/sim08 — Part 5 tunes)
CROSSING_PERSIST = 4
STAB_THRESH = 0.90
ROUGH_ELEV_THRESH = 0.02      # crossing criterion 2 for the curvature condition:
                             # roughness (curvature std over surface) sustained above this
PHERO_ELEV_THRESH = 0.5      # crossing criterion 2 for the pheromone condition (as sim06)
CONSTRAIN_THRESH = 0.60

# Mass-plateau gate (Session 19 correction). The original mass-saturation gate
# (|dM/dt|/sample_every < 0.01) sat ~100x below the stochastic noise floor of
# a 150-termite deposit process (Poisson std of the centered window sum),
# making it unfalsifiable. The corrected gate uses a K-sample linear
# regression slope of total_material, taken relative to its mean:
#   |slope(M over last K samples)| / mean(M) < MASS_PLATEAU_REL
# K=16 (400 steps at sample_every=25) and rel=0.001 (0.1% drift per step)
# sit above the noise floor: the relative-slope fires ~98-100% in the late
# equilibrium of a plateauing run while the baseline control still never
# crosses on its pheromone-elevation gate.
MASS_PLATEAU_WINDOW = 16
MASS_PLATEAU_REL = 0.001


# --------------------------------------------------------------------------
# Numpy → JSON helper
# --------------------------------------------------------------------------
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


_FLAT_ARRAY_RE = re.compile(
    r'("(?:material|curvature)": )\[\n((?:\s*-?[0-9.eE+-]+,?\n)+?)(\s*)\]'
)


def _compact_snapshot_arrays(json_str):
    """Collapse the one-float-per-line arrays indent=2 produces for the
    snapshot material/curvature lists back onto a single line each. Keeps the
    rest of results.json human-readable while avoiding a multi-megabyte
    whitespace blowup for the ~1600-float-per-snapshot grids."""
    def repl(m):
        prefix, body, _ = m.groups()
        nums = (line.strip().rstrip(",") for line in body.splitlines() if line.strip())
        return prefix + "[" + ", ".join(nums) + "]"
    return _FLAT_ARRAY_RE.sub(repl, json_str)


# --------------------------------------------------------------------------
# RNG helper
# --------------------------------------------------------------------------
def make_rng(seed=SEED):
    """Create a seeded numpy Generator (never use module-level randomness)."""
    return np.random.default_rng(seed)


# --------------------------------------------------------------------------
# Field container (extended in Part 3)
# --------------------------------------------------------------------------
class Field:
    """Holds the 2D material field the curvature channel acts on, plus an
    optional pheromone field for the baseline-pheromone control condition."""

    def __init__(self, size):
        self.size = size
        self.material = np.zeros((size, size), dtype=np.float64)   # deposited soil (the f field)
        self.pheromone = None  # set to a np.zeros grid only in the baseline_pheromone condition


# --------------------------------------------------------------------------
# Moore neighbourhood offsets (8-neighbourhood, toroidal wrap)
# --------------------------------------------------------------------------
_MOORE = [(-1, -1), (-1, 0), (-1, 1),
          (0, -1),           (0, 1),
          (1, -1),  (1, 0),  (1, 1)]


# --------------------------------------------------------------------------
# Termite agents (vectorized state, per-step behaviour in a small loop)
# --------------------------------------------------------------------------
class Termites:
    """All termites represented as parallel numpy arrays for state."""

    def __init__(self, n, size, rng):
        self.n = n
        self.size = size
        self.x = rng.integers(0, size, n)          # int array (column)
        self.y = rng.integers(0, size, n)         # int array (row)
        self.loaded = np.zeros(n, dtype=bool)      # carrying a pellet?


# --------------------------------------------------------------------------
# Curvature-channel termite step (state-gated deposit/excavate split)
# --------------------------------------------------------------------------
def termite_step(termites, field, rng, params, curvature, on_surface):
    """Advance ALL termites one step under the curvature channel rule.

    Loaded termites deposit at convex tips (high curvature); unloaded termites
    excavate at concavities (negative curvature). This is the Facchini/Calovi
    action-component split — do NOT conflate. Movement is biased up the
    curvature gradient when loaded (recruit) and down when unloaded (seek).

    `curvature`: local mean-curvature field (Part 3 computes it; passed by
    Part 4). `on_surface`: boolean surface mask (Part 3). Both are supplied
    externally so this function stays pure.

    Returns per-step event counts:
        {"deposits": int, "excavations": int,
         "deposits_on_convex": int, "pickups": int}
    """
    n = termites.n
    size = termites.size
    curve_follow = params.get("curve_follow", CURVE_FOLLOW)
    reload_prob = params.get("reload_prob", RELOAD_PROB)
    deposit_prob_base = params.get("deposit_prob_base", DEPOSIT_PROB_BASE)
    deposit_prob_gain = params.get("deposit_prob_gain", DEPOSIT_PROB_GAIN)
    excavate_prob_base = params.get("excavate_prob_base", EXCAVATE_PROB_BASE)
    excavate_prob_gain = params.get("excavate_prob_gain", EXCAVATE_PROB_GAIN)
    pellet = params.get("pellet", PELLET)
    pickup_prob_base = params.get("pickup_prob_base", PICKUP_PROB_BASE)

    curv = curvature
    ons = on_surface
    mat = field.material

    deposits = 0
    excavations = 0
    deposits_on_convex = 0
    pickups = 0

    for i in range(n):
        y = int(termites.y[i])
        x = int(termites.x[i])

        # --- movement ---
        if rng.random() < curve_follow:
            best_dy = 0
            best_dx = 0
            if termites.loaded[i]:
                # loaded: move toward highest-curvature neighbour (recruit)
                best_v = -np.inf
                for dy, dx in _MOORE:
                    yy = (y + dy) % size
                    xx = (x + dx) % size
                    v = curv[yy, xx]
                    if v > best_v:
                        best_v = v
                        best_dy, best_dx = dy, dx
            else:
                # unloaded: move toward lowest-curvature neighbour (seek pit)
                best_v = np.inf
                for dy, dx in _MOORE:
                    yy = (y + dy) % size
                    xx = (x + dx) % size
                    v = curv[yy, xx]
                    if v < best_v:
                        best_v = v
                        best_dy, best_dx = dy, dx
            y = (y + best_dy) % size
            x = (x + best_dx) % size
        else:
            dy, dx = _MOORE[int(rng.integers(0, 8))]
            y = (y + dy) % size
            x = (x + dx) % size
        termites.y[i] = y
        termites.x[i] = x

        # --- reload / excavate / pickup (unloaded) ---
        if not termites.loaded[i]:
            if rng.random() < reload_prob:
                # off-grid sourcing (primary load channel)
                termites.loaded[i] = True
            elif mat[y, x] > 0:
                c = curv[y, x]
                if c < 0:
                    # concavity → excavate (Calovi/Facchini limit mechanism)
                    p_exc = excavate_prob_base + excavate_prob_gain * (-c)
                    p_exc = min(max(p_exc, 0.0), 1.0)
                    if rng.random() < p_exc:
                        mat[y, x] = max(0.0, mat[y, x] - pellet)
                        termites.loaded[i] = True
                        excavations += 1
                else:
                    # turnover pickup (rare erosion channel)
                    if rng.random() < pickup_prob_base:
                        mat[y, x] = max(0.0, mat[y, x] - pellet)
                        termites.loaded[i] = True
                        pickups += 1

        # --- deposit (loaded) ---
        if termites.loaded[i]:
            c = curv[y, x]
            if ons[y, x]:
                # surface-gated: linear (non-saturating) routing on curvature
                p_dep = deposit_prob_base + deposit_prob_gain * c
            else:
                # bare ground far from structure: nucleation only
                p_dep = deposit_prob_base
            p_dep = min(max(p_dep, 0.0), 1.0)
            if rng.random() < p_dep:
                mat[y, x] += pellet
                termites.loaded[i] = False
                deposits += 1
                if c > 0:
                    deposits_on_convex += 1

    return {
        "deposits": deposits,
        "excavations": excavations,
        "deposits_on_convex": deposits_on_convex,
        "pickups": pickups,
    }


# --------------------------------------------------------------------------
# Baseline-pheromone termite step (sim06's saturating Grassé rule — control)
# --------------------------------------------------------------------------
def termite_step_pheromone(termites, field, rng, params):
    """sim06's Grassé rule for the baseline_pheromone condition.

    Loaded termites deposit with p = deposit_base + deposit_gain *
    local_pheromone/(1+local_pheromone) (the SATURATING response H11 flags),
    follow the pheromone gradient when loaded, reload off-grid. No curvature
    routing, no excavation. Returns:
        {"deposits": int, "pickups": int, "deposits_on_structure": int}
    """
    n = termites.n
    size = termites.size
    phero_follow = params.get("phero_follow", CURVE_FOLLOW)
    reload_prob = params.get("reload_prob", RELOAD_PROB)
    deposit_base = params.get("deposit_base", DEPOSIT_BASE)
    deposit_gain = params.get("deposit_gain", DEPOSIT_GAIN)
    deposit_pheromone = params.get("deposit_pheromone", DEPOSIT_PHEROMONE)
    pellet = params.get("pellet", PELLET)
    pickup_prob_base = params.get("pickup_prob_base", PICKUP_PROB_BASE)
    structure_threshold = params.get("structure_threshold", STRUCTURE_THRESHOLD)

    pher = field.pheromone
    mat = field.material

    deposits = 0
    pickups = 0
    deposits_on_structure = 0

    for i in range(n):
        y = int(termites.y[i])
        x = int(termites.x[i])

        # --- movement: loaded termites follow pheromone gradient up ---
        if termites.loaded[i] and rng.random() < phero_follow:
            best_v = -np.inf
            best_dy = 0
            best_dx = 0
            for dy, dx in _MOORE:
                yy = (y + dy) % size
                xx = (x + dx) % size
                v = pher[yy, xx]
                if v > best_v:
                    best_v = v
                    best_dy, best_dx = dy, dx
            y = (y + best_dy) % size
            x = (x + best_dx) % size
        else:
            dy, dx = _MOORE[int(rng.integers(0, 8))]
            y = (y + dy) % size
            x = (x + dx) % size
        termites.y[i] = y
        termites.x[i] = x

        # --- reload / pickup (unloaded) ---
        if not termites.loaded[i]:
            if rng.random() < reload_prob:
                termites.loaded[i] = True
            elif mat[y, x] > 0 and rng.random() < pickup_prob_base:
                mat[y, x] = max(0.0, mat[y, x] - pellet)
                termites.loaded[i] = True
                pickups += 1

        # --- deposit (loaded): saturating Grassé rule ---
        if termites.loaded[i]:
            local = pher[y, x]
            p_dep = deposit_base + deposit_gain * (local / (1.0 + local))
            p_dep = min(max(p_dep, 0.0), 1.0)
            if rng.random() < p_dep:
                was_structure = mat[y, x] > structure_threshold
                mat[y, x] += pellet
                pher[y, x] += deposit_pheromone
                termites.loaded[i] = False
                deposits += 1
                if was_structure:
                    deposits_on_structure += 1

    return {
        "deposits": deposits,
        "pickups": pickups,
        "deposits_on_structure": deposits_on_structure,
    }


# --------------------------------------------------------------------------
# Toroidal grid operators (Laplacian + 3x3 diffusion blur)
# --------------------------------------------------------------------------
def _laplacian(a):
    """5-point stencil Laplacian on a torus: 4-neighbour sum minus 4*center."""
    return (np.roll(a, 1, 0) + np.roll(a, -1, 0)
            + np.roll(a, 1, 1) + np.roll(a, -1, 1) - 4.0 * a)


def _diffuse(a, rate):
    """Toroidal 3x3 Moore-neighbourhood blur (project standard diffusion)."""
    nb = (np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1)
          + np.roll(np.roll(a, 1, 0), 1, 1) + np.roll(np.roll(a, 1, 0), -1, 1)
          + np.roll(np.roll(a, -1, 0), 1, 1) + np.roll(np.roll(a, -1, 0), -1, 1)) / 8.0
    return (1.0 - rate) * a + rate * nb


def _downsample_grid(a, target):
    """Average-pool a square grid down to target x target for compact
    snapshot JSON. Uses np.array_split so it works for any grid size, not
    just exact multiples of target (sim09's grid is 100, not 80)."""
    size = a.shape[0]
    if size <= target:
        return a.copy()
    row_chunks = np.array_split(np.arange(size), target)
    col_chunks = np.array_split(np.arange(size), target)
    out = np.empty((target, target), dtype=np.float64)
    for i, rows in enumerate(row_chunks):
        sub = a[rows, :]
        for j, cols in enumerate(col_chunks):
            out[i, j] = sub[:, cols].mean()
    return out


# --------------------------------------------------------------------------
# Curvature / surface / roughness (the Facchini growth-equation terms, 2D)
# --------------------------------------------------------------------------
def compute_curvature(field, params):
    """Local mean curvature of the material height field ≈ (1/2) * Laplacian
    of a lightly-smoothed material field. Positive = convex (tip/growth site);
    negative = concave (pit/excavation site). This is the (1/2)·Δf term."""
    smooth_m = _diffuse(field.material, 0.2)
    return 0.5 * _laplacian(smooth_m)


def compute_on_surface(field, params):
    """Boolean surface mask — the f(1−f) prefactor made operational. A cell
    is on-surface if it has material > 0 OR is Moore-adjacent to a structure
    cell (material > structure_threshold). Deposits happen at edges/bulk
    surface, not open air."""
    thr = params.get("structure_threshold", STRUCTURE_THRESHOLD)
    struct = field.material > thr
    dil = struct.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            dil |= np.roll(np.roll(struct, dy, 0), dx, 1)
    return (field.material > 0) | dil


def compute_roughness(field, params, curvature, on_surface):
    """Std of curvature over surface cells — the recruit proxy (Facchini 2024:
    deposits roughen the surface, focusing further evaporation/deposition).
    Returns 0.0 when no surface cells are present."""
    mask = on_surface & (field.material > 0)
    if mask.sum() == 0:
        return 0.0
    return float(curvature[mask].std())


# --------------------------------------------------------------------------
# Field step — advance the environment one step (erosion + d-smoothing +
# baseline pheromone dynamics)
# --------------------------------------------------------------------------
def field_step(field, params):
    """Advance the material field one step:
      1. background erosion (material_decay),
      2. d-gated biharmonic smoothing (the d·Δ²f LIMIT term),
      3. baseline-pheromone decay + diffusion (baseline condition only).
    The curvature condition has no pheromone field.
    """
    material_decay = params.get("material_decay", MATERIAL_DECAY)
    field.material *= (1.0 - material_decay)

    d = params.get("d", D_SMOOTH)
    if d != 0.0:
        lap = _laplacian(field.material)
        biharmonic = _laplacian(lap)   # Δ²f
        field.material = field.material + d * 0.0001 * biharmonic
        field.material = np.clip(field.material, 0.0, None)

    if params.get("channel") == "baseline_pheromone" and field.pheromone is not None:
        decay = params.get("pheromone_decay", PHEROMONE_DECAY)
        field.pheromone *= (1.0 - decay)
        field.pheromone = _diffuse(field.pheromone,
                                  params.get("pheromone_diffuse", PHEROMONE_DIFFUSE))


def _connected_components(mask):
    """Count Moore-connected components (8-connectivity) of a boolean grid
    via iterative BFS flood-fill. No scipy. Returns the component count."""
    visited = np.zeros_like(mask, dtype=bool)
    n = 0
    rows, cols = mask.shape
    for r0 in range(rows):
        for c0 in range(cols):
            if mask[r0, c0] and not visited[r0, c0]:
                n += 1
                stack = [(r0, c0)]
                visited[r0, c0] = True
                while stack:
                    r, c = stack.pop()
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            rr = (r + dr) % rows
                            cc = (c + dc) % cols
                            if mask[rr, cc] and not visited[rr, cc]:
                                visited[rr, cc] = True
                                stack.append((rr, cc))
    return n


def _compactness(mask):
    """n_structure_cells / bounding_box_area (1.0 = filled box, low = sparse).
    Bounding box uses min/max row & col of structure cells. 0.0 if no structure."""
    if not mask.any():
        return 0.0
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if rows.size == 0 or cols.size == 0:
        return 0.0
    box_h = rows.max() - rows.min() + 1
    box_w = cols.max() - cols.min() + 1
    area = float(box_h * box_w)
    if area == 0:
        return 0.0
    return float(mask.sum()) / area


# --------------------------------------------------------------------------
# Core simulation loop + metrics
# --------------------------------------------------------------------------
def compute_metrics(field, params, step, deposits, excavations,
                     deposits_on_convex, pickups, prev_mask, deposits_on_structure=0,
                     pre_perturb_total=None):
    """Compute one history record from the current field state + window event
    counters. Part 5 upgrades this to fill n_pillars/compactness/crossing.
    `deposits_on_structure` is accumulated only by the baseline_pheromone
    condition (sim06's deposit-on-structure metric); 0 for the curvature channel.

    Part 8: `pre_perturb_total` is the total_material captured at the last
    pre-perturbation sample; when set, each record carries
    `recovery = current_total_material / pre_perturb_total`. When None
    (no perturbation, or before the perturbation sample), recovery is None."""
    structure_threshold = params.get("structure_threshold", STRUCTURE_THRESHOLD)
    channel = params.get("channel", "curvature")

    total_material = float(field.material.sum())
    struct_mask = field.material > structure_threshold
    n_structure_cells = int(struct_mask.sum())

    # curvature / roughness (computed for both conditions so they compare)
    curv = compute_curvature(field, params)
    on_surface = compute_on_surface(field, params)
    mean_curvature = float(curv[on_surface & (field.material > 0)].mean()) \
        if (on_surface & (field.material > 0)).any() else 0.0
    max_curvature = float(curv.max())
    roughness = compute_roughness(field, params, curv, on_surface)

    # pheromone (baseline condition carries a field; curvature does not)
    if field.pheromone is not None:
        active_phero = field.pheromone[field.pheromone > 0]
        mean_pheromone = float(active_phero.mean()) if active_phero.size else 0.0
        max_pheromone = float(field.pheromone.max())
    else:
        mean_pheromone = 0.0
        max_pheromone = 0.0

    # structure_stability: fraction of prev_mask cells still above threshold
    if prev_mask is None:
        structure_stability = 1.0
    elif prev_mask.sum() == 0:
        structure_stability = 1.0
    else:
        survived = (field.material[prev_mask] > structure_threshold).sum()
        structure_stability = float(survived) / float(prev_mask.sum())
        structure_stability = min(max(structure_stability, 0.0), 1.0)

    # --- Part 5 morphology + fractions + growth rate ---
    n_pillars = _connected_components(struct_mask)
    compactness = _compactness(struct_mask)
    deposits_on_convex_fraction = (float(deposits_on_convex) / float(deposits)
                                   if deposits > 0 else 0.0)
    deposit_on_structure_fraction = (float(deposits_on_structure) / float(deposits)
                                     if deposits > 0 else 0.0)
    # material_growth_rate is filled by detect_crossing's pre-pass (needs the
    # previous record's total_material); left None here.

    rec = {
        "step": int(step),
        "total_material": total_material,
        "n_structure_cells": n_structure_cells,
        "mean_curvature": mean_curvature,
        "max_curvature": max_curvature,
        "roughness": roughness,
        "mean_pheromone": mean_pheromone,
        "max_pheromone": max_pheromone,
        "deposits_this_window": int(deposits),
        "excavations_this_window": int(excavations),
        "deposits_on_convex_this_window": int(deposits_on_convex),
        "pickups_this_window": int(pickups),
        "structure_stability": structure_stability,
        # --- Part 5 fields ---
        "n_pillars": int(n_pillars),
        "compactness": float(compactness),
        "deposits_on_convex_fraction": float(deposits_on_convex_fraction),
        "deposit_on_structure_fraction": float(deposit_on_structure_fraction),
        "material_growth_rate": None,
        "crossed": False,
        "crossing_step": None,
        # --- Part 8 (perturbation) ---
        "recovery": (float(total_material) / float(pre_perturb_total)
                     if pre_perturb_total and pre_perturb_total > 0 else None),
    }
    return rec


def detect_crossing(history, params):
    """Post-pass over a condition's history: fill material_growth_rate AND the
    regression-based mass_plateau flag, then apply H7's three-criteria crossing
    detector, channel-aware. Sets `crossed=True` / `crossing_step=<step>` on
    the crossing record and all later records once the run-length of
    satisfying samples hits CROSSING_PERSIST.

    Criteria (all must hold for >= CROSSING_PERSIST consecutive samples):
      1. Persistence despite erosion: structure_stability >= STAB_THRESH.
      2. Non-reducible dynamics:
         - curvature channel: roughness >= ROUGH_ELEV_THRESH AND mass plateau
           (relative-slope |b/mean(M)| < MASS_PLATEAU_REL over a K-sample
           regression window).
         - baseline_pheromone: mean_pheromone >= PHERO_ELEV_THRESH AND mass
           plateau.
      3. Constraint on agents:
         - curvature: deposits_on_convex_fraction >= CONSTRAIN_THRESH.
         - baseline_pheromone: deposit_on_structure_fraction >= CONSTRAIN_THRESH.

    Session 19 (2026-08-03) correction: the original mass-saturation gate used
    the per-sample-window |dM/dt|/sample_every < 0.01. For a 150-termite
    stochastic deposit process that quantity has a noise floor of ~0.5-1.0
    (Poisson std of the centered window sum / window), ~100x above the 0.01
    threshold — the gate was unfalsifiable (no finite-population run could
    ever pass it). The corrected gate uses a K-sample linear-regression slope
    of total_material, taken relative to its mean (|b/mean(M)|), which is
    scale-invariant and sits above the noise floor. 0/100 swept combos passed
    the old gate; the corrected gate passes the curvature channel while the
    baseline-pheromone control (same detector) still never crosses — the
    crossing now has a control arm. See dstar_sweep.py + this session's
    daily report.
    """
    channel = params.get("channel", "curvature")
    stab_thresh = params.get("stab_thresh", STAB_THRESH)
    rough_thresh = params.get("rough_elev_thresh", ROUGH_ELEV_THRESH)
    phero_thresh = params.get("phero_elev_thresh", PHERO_ELEV_THRESH)
    constrain_thresh = params.get("constrain_thresh", CONSTRAIN_THRESH)
    persist = params.get("crossing_persist", CROSSING_PERSIST)
    K = params.get("plateau_window", MASS_PLATEAU_WINDOW)
    rel_thresh = params.get("mass_plateau_rel", MASS_PLATEAU_REL)

    # Pre-pass 1: material_growth_rate = abs delta of total_material between
    # consecutive samples / window size. First record = None. (Retained for
    # the visualize.html chart and for diagnostics; NOT the crossing gate.)
    sample_every = params.get("sample_every", SAMPLE_EVERY)
    for i in range(len(history)):
        if i == 0:
            history[i]["material_growth_rate"] = None
        else:
            d_total = history[i]["total_material"] - history[i - 1]["total_material"]
            history[i]["material_growth_rate"] = float(abs(d_total) / float(sample_every))

    # Pre-pass 2: relative-slope mass plateau (the corrected gate).
    # |slope(total_material over last K samples)| / mean(total_material over
    # those samples) < rel_thresh. None for the first K records.
    for i in range(len(history)):
        if i < K:
            history[i]["mass_plateau"] = None
        else:
            t = np.array([history[j]["step"] for j in range(i - K, i)], dtype=float)
            m = np.array([history[j]["total_material"] for j in range(i - K, i)])
            b = np.polyfit(t, m, 1)[0]
            mean_m = m.mean()
            history[i]["mass_plateau"] = float(abs(b / mean_m)) if mean_m > 0 else float("inf")

    def criterion2_ok(rec):
        mp = rec.get("mass_plateau")
        plateau = (mp is not None) and (mp < rel_thresh)
        if channel == "baseline_pheromone":
            return rec["mean_pheromone"] >= phero_thresh and plateau
        return rec["roughness"] >= rough_thresh and plateau

    def criterion3_ok(rec):
        if channel == "baseline_pheromone":
            return rec["deposit_on_structure_fraction"] >= constrain_thresh
        return rec["deposits_on_convex_fraction"] >= constrain_thresh

    run_len = 0
    crossed = False
    crossing_step = None
    for rec in history:
        c1 = rec["structure_stability"] >= stab_thresh
        c2 = criterion2_ok(rec)
        c3 = criterion3_ok(rec)
        if c1 and c2 and c3:
            run_len += 1
            if run_len >= persist and not crossed:
                crossed = True
                crossing_step = rec["step"]
        else:
            run_len = 0
        rec["crossed"] = crossed
        rec["crossing_step"] = crossing_step

    return history


def summarize(history, perturb=None):
    """Headline summary of a condition's run. Part 5 adds crossed/crossing_step.
    Part 8: when perturb is set, adds recovery_final + perturb_at + perturb_frac."""
    perturb_at = (perturb or {}).get("at")
    perturb_frac = (perturb or {}).get("frac")
    if not history:
        return {
            "final_total_material": 0.0, "final_n_structure_cells": 0,
            "peak_total_material": 0.0, "peak_step": 0,
            "mean_late_stability": 0.0, "retention": 0.0,
            "crossed": False, "crossing_step": None,
            "recovery_final": None, "perturb_at": perturb_at,
            "perturb_frac": perturb_frac,
        }
    last = history[-1]
    final_total = last["total_material"]
    final_cells = last["n_structure_cells"]
    peak_total = max(r["total_material"] for r in history)
    peak_step = next(r["step"] for r in history if r["total_material"] == peak_total)
    n_late = max(1, len(history) // 4)
    late = history[-n_late:]
    mean_late_stab = float(sum(r["structure_stability"] for r in late)) / float(len(late))
    retention = (final_total / peak_total) if peak_total > 0 else 0.0
    # Part 5: pull the crossing verdict from the last record (cumulative flag).
    crossed = bool(history[-1].get("crossed", False))
    crossing_step = history[-1].get("crossing_step", None)
    # Part 8: recovery_final from the last record's recovery (None if no perturb).
    recovery_final = last.get("recovery", None)
    return {
        "final_total_material": float(final_total),
        "final_n_structure_cells": int(final_cells),
        "peak_total_material": float(peak_total),
        "peak_step": int(peak_step),
        "mean_late_stability": float(mean_late_stab),
        "retention": float(retention),
        "crossed": crossed,
        "crossing_step": crossing_step,
        "recovery_final": (float(recovery_final)
                          if recovery_final is not None else None),
        "perturb_at": perturb_at,
        "perturb_frac": perturb_frac,
    }


def run_condition(params, seed, perturb=None):
    """Run one full simulation condition. Returns {"history": [...], "summary": {...}}.

    Part 8: optional perturb={"at": step, "frac": f} damages the structure at
    step perturb_at (default int(0.6*steps)) by zeroing a central rectangular
    patch of the grid covering perturb_frac (default 0.25) of the grid area,
    clearing field.material and (baseline) field.pheromone in that patch. Each
    post-perturbation record carries
    recovery = current_total_material / pre_perturb_total_material.
    Defaults to perturb=None (Part 6 behavior unchanged)."""
    rng = make_rng(seed)
    size = params.get("grid_size", GRID_SIZE)
    n = params.get("n_termites", N_TERMITES)
    steps = params.get("steps", STEPS)
    sample = params.get("sample_every", SAMPLE_EVERY)
    channel = params.get("channel", "curvature")

    field = Field(size)
    if channel == "baseline_pheromone":
        field.pheromone = np.zeros((size, size), dtype=np.float64)
    termites = Termites(n, size, rng)
    history = []
    dep_acc = exc_acc = dep_convex_acc = dep_struct_acc = pick_acc = 0
    prev_structure_mask = None

    # --- grid snapshots (for visualize.html's grid renderer) ---
    snapshot_size = params.get("snapshot_size", SNAPSHOT_SIZE)
    expected_records = max(1, (steps + sample - 1) // sample)
    snapshot_stride = max(1, round(expected_records / SNAPSHOT_TARGET_COUNT))
    raw_snapshots = []  # [(step, material_downsampled, curvature_downsampled)]

    # --- Part 8: perturbation setup ---
    perturb_at = None
    perturb_frac = None
    r0 = r1 = c0_patch = c1 = 0
    pre_perturb_total = None
    perturb_applied = False
    if perturb:
        perturb_at = int(perturb.get("at", int(0.6 * steps)))
        perturb_frac = float(perturb.get("frac", 0.25))
        # central square block covering perturb_frac of the grid area
        side = max(1, int(round(size * math.sqrt(perturb_frac))))
        r0 = (size - side) // 2
        c0_patch = (size - side) // 2
        r1 = r0 + side
        c1 = c0_patch + side

    for step in range(steps):
        if channel == "curvature":
            curvature = compute_curvature(field, params)
            on_surface = compute_on_surface(field, params)
            ev = termite_step(termites, field, rng, params, curvature, on_surface)
            field_step(field, params)
            dep_acc += ev["deposits"]
            exc_acc += ev["excavations"]
            dep_convex_acc += ev["deposits_on_convex"]
            pick_acc += ev["pickups"]
        else:  # baseline_pheromone
            ev = termite_step_pheromone(termites, field, rng, params)
            field_step(field, params)
            dep_acc += ev["deposits"]
            dep_struct_acc += ev["deposits_on_structure"]
            pick_acc += ev["pickups"]

        # --- Part 8: apply damage at perturb_at (once) ---
        if perturb and perturb_at is not None and not perturb_applied and step >= perturb_at:
            field.material[r0:r1, c0_patch:c1] = 0.0
            if field.pheromone is not None:
                field.pheromone[r0:r1, c0_patch:c1] = 0.0
            perturb_applied = True

        if step % sample == 0:
            # capture pre-perturb total at the first sample AFTER damage applied,
            # using the last pre-damage sample's total_material
            if (perturb and pre_perturb_total is None
                    and perturb_applied and history):
                pre_perturb_total = float(history[-1]["total_material"])
            rec = compute_metrics(field, params, step, dep_acc, exc_acc,
                                  dep_convex_acc, pick_acc, prev_structure_mask,
                                  deposits_on_structure=dep_struct_acc,
                                  pre_perturb_total=pre_perturb_total)
            history.append(rec)
            dep_acc = exc_acc = dep_convex_acc = dep_struct_acc = pick_acc = 0
            prev_structure_mask = (field.material >
                                    params.get("structure_threshold", STRUCTURE_THRESHOLD)).copy()

            if (len(history) - 1) % snapshot_stride == 0:
                curv_now = compute_curvature(field, params)
                raw_snapshots.append((
                    int(step),
                    _downsample_grid(field.material, snapshot_size),
                    _downsample_grid(curv_now, snapshot_size),
                ))

    # Part 5: detect the trace->actor crossing (channel-aware) over the history.
    detect_crossing(history, params)

    summary = summarize(history, perturb=perturb)

    # Normalize snapshots to 0.0-1.0: material by the run's peak material value
    # (matches total_material's own scale); curvature by its own min/max since
    # it is signed (concave/convex) rather than a monotonically-accumulating
    # quantity like material.
    snapshots = []
    if raw_snapshots:
        mat_max = max(m.max() for _, m, _ in raw_snapshots)
        mat_max = mat_max if mat_max > 0 else 1.0
        curv_min = min(c.min() for _, _, c in raw_snapshots)
        curv_max = max(c.max() for _, _, c in raw_snapshots)
        curv_range = (curv_max - curv_min) if curv_max > curv_min else 1.0
        for step, mat, curv in raw_snapshots:
            mat_norm = np.clip(mat / mat_max, 0.0, 1.0)
            curv_norm = np.clip((curv - curv_min) / curv_range, 0.0, 1.0)
            snapshots.append({
                "step": step,
                "material": np.round(mat_norm, 4).flatten().tolist(),
                "curvature": np.round(curv_norm, 4).flatten().tolist(),
            })

    return {"history": history, "summary": summary, "snapshots": snapshots}


# --------------------------------------------------------------------------
# CLI dispatcher (Parts append to these functions incrementally)
# --------------------------------------------------------------------------
def curvature_params():
    """Parameter dict for the curvature-channel condition (the Facchini
    non-saturating recruit+limit rule). All agent/field tunables fall back to
    module constants."""
    return {
        "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
        "sample_every": SAMPLE_EVERY, "structure_threshold": STRUCTURE_THRESHOLD,
        "channel": "curvature",
        "d": D_SMOOTH, "material_decay": MATERIAL_DECAY,
    }


def baseline_pheromone_params():
    """Parameter dict for the baseline-pheromone control (sim06's saturating
    Grassé rule). No curvature routing, no excavation."""
    return {
        "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
        "sample_every": SAMPLE_EVERY, "structure_threshold": STRUCTURE_THRESHOLD,
        "channel": "baseline_pheromone",
        "pheromone_decay": PHEROMONE_DECAY, "pheromone_diffuse": PHEROMONE_DIFFUSE,
        "material_decay": MATERIAL_DECAY,
        "deposit_base": DEPOSIT_BASE, "deposit_gain": DEPOSIT_GAIN,
    }


def cmd_run():
    """Run both headline conditions (curvature-channel vs baseline-pheromone),
    assemble the full results.json, and print the H7 comparison."""
    t0 = time.time()
    print("Running curvature_channel (non-saturating recruit+limit)...")
    curv = run_condition(curvature_params(), seed=SEED)
    print("Running baseline_pheromone (saturating cue control)...")
    base = run_condition(baseline_pheromone_params(), seed=SEED)

    # --- Part 8: perturbation / self-repair experiment ---
    print("Running perturbation experiment (self-repair after damage)...")
    perturb_spec = {"at": int(0.6 * STEPS), "frac": 0.25}
    curv_perturb = run_condition(curvature_params(), seed=SEED,
                                 perturb=perturb_spec)
    base_perturb = run_condition(baseline_pheromone_params(), seed=SEED,
                                 perturb=perturb_spec)
    perturbation = {
        "curvature_channel": curv_perturb,
        "baseline_pheromone": base_perturb,
    }

    results = {
        "config": {
            "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
            "sample_every": SAMPLE_EVERY, "seed": SEED,
            "d": D_SMOOTH, "material_decay": MATERIAL_DECAY,
            "structure_threshold": STRUCTURE_THRESHOLD,
            "snapshot_size": SNAPSHOT_SIZE,
        },
        "curvature_channel": curv,
        "baseline_pheromone": base,
        "perturbation": perturbation,
    }
    json_str = _compact_snapshot_arrays(json.dumps(_pyify(results), indent=2))
    with open(RESULTS_PATH, "w") as f:
        f.write(json_str)

    def line(name, r):
        s = r["summary"]
        print(f"  {name:20s} crossed={str(s['crossed']):5s} "
              f"crossing_step={s['crossing_step']} "
              f"retention={s['retention']:.2f} "
              f"final_cells={s['final_n_structure_cells']}")
    print("\n=== RESULT: Trace -> Actor Crossing (H7) — curvature channel ===")
    line("curvature_channel", curv)
    line("baseline_pheromone", base)

    # Part 8: recovery comparison (the H7 acid test)
    curv_rec = curv_perturb["summary"]["recovery_final"]
    base_rec = base_perturb["summary"]["recovery_final"]
    curv_rec_s = f"{curv_rec:.2f}" if curv_rec is not None else "n/a"
    base_rec_s = f"{base_rec:.2f}" if base_rec is not None else "n/a"
    print("\n=== RESULT: Self-repair after perturbation (H7 acid test) ===")
    print(f"  curvature_channel     recovery_final={curv_rec_s}")
    print(f"  baseline_pheromone    recovery_final={base_rec_s}")
    if curv_rec is not None and base_rec is not None:
        print(f"  curvature - baseline = {curv_rec - base_rec:+.2f}")
    print(f"\nWrote {RESULTS_PATH}  ({time.time()-t0:.1f}s)")


def cmd_sweep_plot():
    """Parameter sweeps producing PNG plots under output/. Imports matplotlib
    LAZILY (Agg backend) so it is not a module-load dependency."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Reduced-cost sweep params (per the DESIGN: grid 80, 150 termites, 2000 steps).
    sweep_grid = {"grid_size": 80, "n_termites": 150, "steps": 2000,
                  "sample_every": 25, "structure_threshold": STRUCTURE_THRESHOLD}

    d_values = [0.0, 0.2, 0.5, 1.0, 2.0, 4.0, 8.0]
    decay_values = [0.0002, 0.0005, 0.001, 0.002, 0.004]

    sweep_data = {"d_sweep": [], "material_decay_sweep": {"curvature": [], "baseline": []}}

    # ---- Sweep 1: d (curvature_channel) — THE HEADLINE PLOT ----
    print("Sweep 1/2: d (curvature_channel)...")
    d_results = []
    for d in d_values:
        p = dict(sweep_grid)
        p.update({"channel": "curvature", "d": d,
                  "material_decay": MATERIAL_DECAY})
        r = run_condition(p, seed=SEED)
        s = r["summary"]
        last_rec = r["history"][-1] if r["history"] else {}
        row = {
            "d": d, "crossed": int(s["crossed"]),
            "crossing_step": s["crossing_step"],
            "retention": s["retention"],
            "n_pillars": last_rec.get("n_pillars", 0),
            "final_cells": s["final_n_structure_cells"],
        }
        d_results.append(row)
        sweep_data["d_sweep"].append(row)
        print(f"  d={d:.2f} crossed={row['crossed']} retention={row['retention']:.2f} "
              f"pillars={row['n_pillars']}")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax1, ax2 = axes
    ds = [r["d"] for r in d_results]
    ax1.plot(ds, [r["retention"] for r in d_results], "o-", color="#58a6ff", label="retention")
    ax1.plot(ds, [r["crossed"] for r in d_results], "s--", color="#f85149", label="crossed (0/1)")
    ax1.set_xlabel("d (smoothing / phase-transition knob)")
    ax1.set_ylabel("retention / crossed")
    ax1.set_title("Curvature channel: retention & crossing vs d")
    ax1.set_xscale("symlog", linthresh=0.1)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax2.plot(ds, [r["n_pillars"] for r in d_results], "^-", color="#3fb950", label="final n_pillars")
    ax2.plot(ds, [r["crossing_step"] if r["crossing_step"] is not None else 0
             for r in d_results], "x--", color="#f85149", label="crossing_step (0=none)")
    ax2.set_xlabel("d")
    ax2.set_ylabel("n_pillars / crossing_step")
    ax2.set_title("Curvature channel: morphology vs d")
    ax2.set_xscale("symlog", linthresh=0.1)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    sweep_d_path = os.path.join(OUTPUT_DIR, "sweep_d.png")
    fig.savefig(sweep_d_path, dpi=110)
    plt.close(fig)
    print(f"  wrote {sweep_d_path}")

    # ---- Sweep 2: material_decay (both conditions) ----
    print("Sweep 2/2: material_decay (both conditions)...")
    curv_rows, base_rows = [], []
    for dec in decay_values:
        pc = dict(sweep_grid)
        pc.update({"channel": "curvature", "d": D_SMOOTH, "material_decay": dec})
        rc = run_condition(pc, seed=SEED)
        sc = rc["summary"]
        row_c = {"material_decay": dec, "retention": sc["retention"],
                 "crossed": int(sc["crossed"]),
                 "final_cells": sc["final_n_structure_cells"]}
        curv_rows.append(row_c)
        sweep_data["material_decay_sweep"]["curvature"].append(row_c)

        pb = dict(sweep_grid)
        pb.update({"channel": "baseline_pheromone", "material_decay": dec})
        rb = run_condition(pb, seed=SEED)
        sb = rb["summary"]
        row_b = {"material_decay": dec, "retention": sb["retention"],
                 "crossed": int(sb["crossed"]),
                 "final_cells": sb["final_n_structure_cells"]}
        base_rows.append(row_b)
        sweep_data["material_decay_sweep"]["baseline"].append(row_b)
        print(f"  decay={dec:.4f} curv_ret={row_c['retention']:.2f} "
              f"base_ret={row_b['retention']:.2f}")

    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    decs = [r["material_decay"] for r in curv_rows]
    ax.plot(decs, [r["retention"] for r in curv_rows], "o-", color="#58a6ff",
            label="curvature_channel")
    ax.plot(decs, [r["retention"] for r in base_rows], "s--", color="#f85149",
            label="baseline_pheromone")
    ax.set_xlabel("material_decay")
    ax.set_ylabel("retention")
    ax.set_title("Retention vs erosion: curvature channel vs baseline")
    ax.set_xscale("log")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    sweep_decay_path = os.path.join(OUTPUT_DIR, "sweep_material_decay.png")
    fig.savefig(sweep_decay_path, dpi=110)
    plt.close(fig)
    print(f"  wrote {sweep_decay_path}")

    sweep_json_path = os.path.join(OUTPUT_DIR, "sweep_data.json")
    with open(sweep_json_path, "w") as f:
        json.dump(_pyify(sweep_data), f, indent=2)
    print(f"  wrote {sweep_json_path}")
    print("sweep_plot done.")


def cmd_selftest():
    # Part 1 checks:
    assert GRID_SIZE > 0 and N_TERMITES > 0 and STEPS > 0
    f = Field(GRID_SIZE)
    assert f.material.shape == (GRID_SIZE, GRID_SIZE)
    assert _pyify({"a": np.float64(1.5)}) == {"a": 1.5}
    print("selftest: Part 1 OK")

    # Part 2 checks: curvature-channel termite step on a synthetic bump.
    f2 = Field(GRID_SIZE)
    ts = Termites(50, GRID_SIZE, make_rng(42))
    yy, xx = np.mgrid[0:GRID_SIZE, 0:GRID_SIZE]
    cy = cx = GRID_SIZE // 2
    # Gaussian bump: material high in center, decaying outward.
    f2.material = 5.0 * np.exp(-((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * 8.0 ** 2))
    # Synthetic curvature ≈ (1/2) * Laplacian(bump): negative at the peak
    # (concave down), positive at the rim (concave up) — built inline without
    # the Part 3 helpers.
    curv = 0.5 * (np.roll(f2.material, 1, 0) + np.roll(f2.material, -1, 0)
                  + np.roll(f2.material, 1, 1) + np.roll(f2.material, -1, 1)
                  - 4.0 * f2.material)
    # surface mask: the bump core (where material exceeds the surface threshold)
    on_surface = f2.material > SURFACE_THRESHOLD
    # sanity on the synthetic field
    rim_mask = on_surface & (curv > 0)
    assert rim_mask.sum() > 0, "synthetic bump should have a positive-curvature rim"

    params = {"channel": "curvature"}
    total_deposits = 0
    total_dep_convex = 0
    for _ in range(100):
        ev = termite_step(ts, f2, make_rng(42), params, curv, on_surface)
        total_deposits += ev["deposits"]
        total_dep_convex += ev["deposits_on_convex"]
    assert f2.material.sum() > 0, "material should accumulate"
    assert ts.loaded.dtype == bool and len(ts.loaded) == 50
    assert total_deposits > 0, "deposits should have happened over 100 steps"
    assert total_dep_convex > 0, "some deposits should land on convex rim"
    print("selftest: Part 2 OK")

    # Part 3 checks: curvature, surface mask, roughness, field_step on a blob.
    f3 = Field(GRID_SIZE)
    yy, xx = np.mgrid[0:GRID_SIZE, 0:GRID_SIZE]
    cy = cx = GRID_SIZE // 2
    f3.material = 8.0 * np.exp(-((yy - cy) ** 2 + (xx - cx) ** 2) / (2 * 6.0 ** 2))
    params3 = {"channel": "curvature", "d": D_SMOOTH, "material_decay": MATERIAL_DECAY,
               "structure_threshold": STRUCTURE_THRESHOLD}
    curv3 = compute_curvature(f3, params3)
    # The rim (ring of cells with material but not the very center) should have
    # positive curvature; the peak should be near-zero or negative.
    rim = (f3.material > SURFACE_THRESHOLD) & (f3.material < 0.5 * f3.material.max())
    assert curv3[rim].max() > 0, "blob rim should have positive curvature"
    center_cell = (cy, cx)
    assert curv3[center_cell] <= 0 or curv3[center_cell] < curv3[rim].max(), \
        "center curvature should not exceed the rim"

    on_surface3 = compute_on_surface(f3, params3)
    assert on_surface3[rim].any(), "surface mask should be True around the blob rim"
    rough3 = compute_roughness(f3, params3, curv3, on_surface3)
    assert rough3 >= 0.0, "roughness should be a non-negative float"

    max_curv_before = curv3.max()
    total_mat_before = f3.material.sum()
    for _ in range(50):
        field_step(f3, params3)
    curv_after = compute_curvature(f3, params3)
    assert curv_after.max() <= max_curv_before + 1e-9, \
        "blob should smooth (max curvature not increase) under field_step"
    assert f3.material.sum() < total_mat_before, \
        "blob should erode (total material decrease) under field_step"
    print("selftest: Part 3 OK")

    # Part 4 checks: run_condition produces a non-empty history with the
    # required keys, using tiny params for speed.
    tiny_params = {"grid_size": 30, "n_termites": 20, "steps": 200,
                   "sample_every": 25, "channel": "curvature",
                   "structure_threshold": STRUCTURE_THRESHOLD,
                   "d": D_SMOOTH, "material_decay": MATERIAL_DECAY}
    res = run_condition(tiny_params, seed=SEED)
    hist = res["history"]
    required_keys = {"step", "total_material", "n_structure_cells",
                     "mean_curvature", "max_curvature", "roughness",
                     "mean_pheromone", "max_pheromone",
                     "deposits_this_window", "excavations_this_window",
                     "deposits_on_convex_this_window", "pickups_this_window",
                     "structure_stability", "n_pillars", "compactness",
                     "crossed", "crossing_step"}
    assert len(hist) >= 4, "tiny run should produce >= 4 records"
    for r in hist:
        assert required_keys.issubset(r.keys()), \
            f"record missing keys: {required_keys - set(r.keys())}"
    print("selftest: Part 4 OK")

    # Part 5 checks: crossing detector + regression guard.
    # (a) tiny curvature and baseline runs carry the Part-5 fields and
    #     detect_crossing runs without error.
    tiny_curv = {"grid_size": 30, "n_termites": 20, "steps": 200,
                 "sample_every": 25, "channel": "curvature",
                 "structure_threshold": STRUCTURE_THRESHOLD,
                 "d": D_SMOOTH, "material_decay": MATERIAL_DECAY}
    tiny_base = {"grid_size": 30, "n_termites": 20, "steps": 200,
                 "sample_every": 25, "channel": "baseline_pheromone",
                 "structure_threshold": STRUCTURE_THRESHOLD,
                 "material_decay": MATERIAL_DECAY}
    rc = run_condition(tiny_curv, seed=SEED)
    rb = run_condition(tiny_base, seed=SEED)
    for r in rc["history"]:
        assert "n_pillars" in r and "compactness" in r
        assert "crossed" in r and "crossing_step" in r
        assert "material_growth_rate" in r
    # baseline carries deposit_on_structure_fraction
    for r in rb["history"]:
        assert "deposit_on_structure_fraction" in r

    # (b) Regression guard (learned from sim06's bug, updated Session 19 for
    #     the relative-slope plateau gate): a synthetic history where all
    #     three criteria are satisfied for CROSSING_PERSIST samples must fire;
    #     negating ANY ONE criterion must withhold. The history is long enough
    #     (persist + MASS_PLATEAU_WINDOW) that the plateau pre-pass populates
    #     mass_plateau for the later records.
    persist = CROSSING_PERSIST
    K = MASS_PLATEAU_WINDOW
    n = persist + K + 2  # enough records for the plateau window to populate
    base_rec = {
        "step": 0, "total_material": 100.0, "n_structure_cells": 10,
        "mean_curvature": 0.0, "max_curvature": 0.0, "roughness": 0.0,
        "mean_pheromone": 0.0, "max_pheromone": 0.0,
        "deposits_this_window": 0, "excavations_this_window": 0,
        "deposits_on_convex_this_window": 0, "pickups_this_window": 0,
        "structure_stability": 0.0, "n_pillars": 0, "compactness": 0.0,
        "deposits_on_convex_fraction": 0.0, "deposit_on_structure_fraction": 0.0,
        "material_growth_rate": None, "mass_plateau": None,
        "crossed": False, "crossing_step": None,
    }

    def make_history(c1, c2_rough, c2_phero, c3_convex, c3_struct,
                     plateau=True):
        # Build a total_material trajectory: a flat plateau (if plateau=True)
        # keeps the relative-slope ~0 < MASS_PLATEAU_REL; a linear ramp (if
        # False) drives the relative-slope above the gate.
        h = []
        for i in range(n):
            r = dict(base_rec)
            r["step"] = i * 25
            if plateau:
                r["total_material"] = 100.0  # flat → rel slope 0
            else:
                r["total_material"] = 100.0 + 20.0 * i  # steep ramp → rel slope high
            r["structure_stability"] = 0.95 if c1 else 0.80
            r["roughness"] = 0.05 if c2_rough else 0.005
            r["mean_pheromone"] = 0.8 if c2_phero else 0.1
            r["deposits_on_convex_fraction"] = 0.75 if c3_convex else 0.30
            r["deposit_on_structure_fraction"] = 0.75 if c3_struct else 0.30
            h.append(r)
        return h

    p = {"channel": "curvature"}
    # all-true → fires
    h_all = make_history(True, True, True, True, True, plateau=True)
    detect_crossing(h_all, p)
    assert h_all[-1]["crossed"] is True, "all-true curvature history should cross"
    # negate criterion 1 → withholds
    h1 = make_history(False, True, True, True, True, plateau=True)
    detect_crossing(h1, p)
    assert h1[-1]["crossed"] is False, "negating c1 should withhold crossing"
    # negate criterion 2 (curvature: roughness) → withholds
    h2 = make_history(True, False, True, True, True, plateau=True)
    detect_crossing(h2, p)
    assert h2[-1]["crossed"] is False, "negating c2 (roughness) should withhold"
    # negate criterion 2b (mass plateau: ramp instead of flat) → withholds
    h2p = make_history(True, True, True, True, True, plateau=False)
    detect_crossing(h2p, p)
    assert h2p[-1]["crossed"] is False, "negating c2 (mass plateau) should withhold"
    # negate criterion 3 (curvature: convex fraction) → withholds
    h3 = make_history(True, True, True, False, True, plateau=True)
    detect_crossing(h3, p)
    assert h3[-1]["crossed"] is False, "negating c3 (convex fraction) should withhold"

    # baseline channel: criterion 2 uses pheromone, criterion 3 uses structure
    pb = {"channel": "baseline_pheromone"}
    h_all_b = make_history(True, True, True, True, True, plateau=True)
    detect_crossing(h_all_b, pb)
    assert h_all_b[-1]["crossed"] is True, "all-true baseline history should cross"
    h2b = make_history(True, True, False, True, True, plateau=True)
    detect_crossing(h2b, pb)
    assert h2b[-1]["crossed"] is False, "negating c2 (pheromone) should withhold"
    h2pb = make_history(True, True, True, True, True, plateau=False)
    detect_crossing(h2pb, pb)
    assert h2pb[-1]["crossed"] is False, "negating c2 (mass plateau) baseline should withhold"
    h3b = make_history(True, True, True, True, False, plateau=True)
    detect_crossing(h3b, pb)
    assert h3b[-1]["crossed"] is False, "negating c3 (structure fraction) should withhold"
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
        print("usage: sim09.py [run|sweep_plot|selftest]")


if __name__ == "__main__":
    main()
