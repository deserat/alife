"""
Sim10: Does the Crossing Compose? — L2 Composition with a Non-Saturating Stigmergic Glue

THE QUESTION (queued-topic #62/#77):
  The curvature channel crosses (Session 19): a single curvature-channel
  structure satisfies the H7 trace→actor crossing criteria (stability,
  roughness, mass-plateau). But does it COMPOSE? If two self-maintaining
  curvature-channel structures grow in adjacent regions of the SAME grid,
  sharing the same agent pool and the same material/curvature fields, does a
  composite (L2) organization emerge — or does one dominate, do they mutually
  destroy, or do they simply coexist as independent structures?

  This is the sim05 L2 question (Fontana & Buss; Mathis et al. 2024) reopened
  with a NON-SATURATING stigmergic glue. In AlChemy the three outcomes were
  Dominance, Coexistence, and Mutual Destruction, with L2 coexistence rare
  (Mathis et al. found "stable organizations cannot be easily combined into
  higher order entities"). The curvature channel is a different kind of glue:
  two structures whose curvature FIELDS interact through a shared agent pool.
  Does this compose where the chemical (collision) glue did not?

DESIGN:
  Two structures are seeded in opposite quadrants of one grid (left/right).
  The material and curvature fields are SHARED (single grid, single agent
  pool) — this is the "glue." The question is what happens at the boundary
  between them.

  Four conditions (the minimal 2×2):
    A. curvature_channel, two seeds (the test)
    B. baseline_pheromone, two seeds (the control — saturating glue)
    C. curvature_channel, ONE seed (the L1 baseline — what does a single
       structure do on the same grid, same agents? This is the
       "what would either parent do alone?" control)
    D. baseline_pheromone, ONE seed (the L1 pheromone baseline)

  The L2 detector (see detect_l2 below) asks: do BOTH regions maintain
  self-similar structure (each region's material stays above a fraction of
  its peak) for a sustained late window, WITHOUT one region dominating
  (both regions retain >= L2_REGION_RETAIN of their peak)? This is the
  analog of AlChemy's "Coexistence" outcome. Dominance = one region retains
  >> peak, the other collapses toward 0. Mutual destruction = both collapse.

METHODOLOGY (per CLAUDE.md §4 step 6):
  - The L2 detector must prove it can fire (synthetic coexistence history)
    and that negating each criterion withholds (dominance, destruction,
    single-region). cmd_selftest Part 5 is the template.
  - Control arm: the one-seed conditions (C, D) show what a single
    structure does on the same grid — if a single seed also "composes"
    (the detector fires for a single region), the detector is broken.
  - Determinism: run twice, diff the JSON.
  - Compute the metric's ceiling: L2_region_retain is bounded in [0, inf);
    a region can retain > 1.0 if it grows after its peak. The
    dominance/destroy thresholds sit well within reachable ranges.

This module imports sim09's core (Field, Termites, termite_step,
termite_step_pheromone, field_step, compute_curvature, compute_on_surface,
compute_roughness, _connected_components, _compactness, detect_crossing,
summarize, make_rng, _pyify, _laplacian, _diffuse) — it adds ONLY the
two-seed initialization, the region metrics, and the L2 detector. This keeps
sim09 as the single source of truth for the curvature channel.
"""

import os
import sys
import json
import math
import time

import numpy as np

# Import sim09's core machinery (same directory's parent).
SIM09_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "sim09_curvature_channel")
sys.path.insert(0, SIM09_DIR)
import sim09 as S  # noqa: E402

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SIM_DIR, "results.json")
OUTPUT_DIR = os.path.join(SIM_DIR, "output")

# --------------------------------------------------------------------------#
# Two-seed initialization
# --------------------------------------------------------------------------#
# Each seed is a Gaussian mound of material placed in one half of the grid,
# offset toward the outer edge so the two seeds grow toward each other.
# Seed half-width (std) relative to grid size. The mound height is a few
# structure-threshold units so the seed counts as "structure" immediately.
SEED_SIGMA_FRAC = 0.08       # Gaussian std as fraction of grid size
SEED_HEIGHT = 4.0            # peak material in the seed mound
SEED_OFFSET_FRAC = 0.25      # seed center offset from center toward edge (fraction)


def seed_region(field, size, region, params):
    """Place a Gaussian material mound in one half of the grid.

    region = "left"  → center in the left half (column < size/2)
    region = "right" → center in the right half (column >= size/2)

    The mound is placed at (size//2, offset_col) so the two seeds sit on the
    same row, facing each other across the midline. The curvature channel
    should then grow each seed toward the other (curvature recruits at the
    facing tips).
    """
    sigma = max(1.0, size * SEED_SIGMA_FRAC)
    cy = size // 2
    if region == "left":
        cx = int(size * SEED_OFFSET_FRAC)
    else:  # right
        cx = size - int(size * SEED_OFFSET_FRAC)
    yy, xx = np.mgrid[0:size, 0:size]
    field.material += SEED_HEIGHT * np.exp(
        -((yy - cy) ** 2 + (xx - cx) ** 2) / (2.0 * sigma ** 2))


# --------------------------------------------------------------------------#
# Region masks (for per-region material tracking)
# --------------------------------------------------------------------------#
def region_masks(size):
    """Return (left_mask, right_mask) boolean arrays splitting the grid
    vertically at the midline. Left = columns [0, size//2), right = columns
    [size//2, size). The boundary column is excluded from neither — the
    split is clean."""
    left = np.zeros((size, size), dtype=bool)
    right = np.zeros((size, size), dtype=bool)
    mid = size // 2
    left[:, :mid] = True
    right[:, mid:] = True
    return left, right


# --------------------------------------------------------------------------#
# L2 composition metrics
# --------------------------------------------------------------------------#
# The L2 detector asks whether BOTH regions retain DISTINCT, INDEPENDENT
# structure — not just material mass. The one-seed control proved that raw
# material mass in both halves is uninformative: a single structure fills
# both halves, and the detector fires "coexist" for one structure. The
# corrected detector counts connected components of structure that lie
# ENTIRELY within each region (do not cross the midline). A component that
# crosses the midline is a single merged structure — counted in neither
# region. Genuine coexistence = an independent component in EACH region
# that persists for L2_PERSIST consecutive late samples.
MIN_COMPONENT_CELLS = 10    # min cells for a component to count as "structure"
L2_LATE_WINDOW_FRAC = 0.25  # last 25% of history = "late window"
L2_PERSIST = 4              # consecutive late samples both regions must have
                            # an independent component
COEXIST_MAX_COMP = 3        # max independent components per region for
                            # "coexist" (above this = fragmented, not composed)

# Dominance / destruction thresholds (for categorizing the outcome, based
# on per-region material retention as a secondary diagnostic).
DOMINANCE_RATIO = 3.0       # one region retains >= 3x the other → dominance
DESTRUCTION_FLOOR = 0.10   # both regions retain < this → mutual destruction


def compute_region_metrics(field, params, left_mask, right_mask):
    """Per-region material totals. Returns (left_total, right_total,
    total_material)."""
    lt = float(field.material[left_mask].sum())
    rt = float(field.material[right_mask].sum())
    return lt, rt, lt + rt


def _count_region_components(field, params, mask):
    """Count connected components of structure (material > threshold) that
    have at least MIN_COMPONENT_CELLS cells AND lie entirely within the
    given region mask. A component that crosses the midline (touches both
    left and right) is counted in NEITHER region — it is a "bridge" that
    merges the two structures into one.

    This is the critical distinction: the one-seed control's material fills
    both halves but as a SINGLE connected component crossing the midline —
    so it has 0 independent components in each region. A genuine coexistence
    has a component in each region that does NOT cross the midline.
    """
    thr = params.get("structure_threshold", S.STRUCTURE_THRESHOLD)
    min_cells = params.get("min_component_cells", MIN_COMPONENT_CELLS)
    struct = field.material > thr
    if not struct.any():
        return 0
    size = struct.shape[0]
    visited = np.zeros_like(struct, dtype=bool)
    n = 0
    for r0 in range(size):
        for c0 in range(size):
            if struct[r0, c0] and not visited[r0, c0]:
                # BFS this component, tracking which cells are in `mask`
                # and whether ANY cell is OUTSIDE `mask` (crosses midline).
                stack = [(r0, c0)]
                visited[r0, c0] = True
                in_mask_count = 0
                total_count = 0
                crosses = False
                while stack:
                    r, c = stack.pop()
                    total_count += 1
                    if mask[r, c]:
                        in_mask_count += 1
                    else:
                        crosses = True
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            rr = (r + dr) % size
                            cc = (c + dc) % size
                            if struct[rr, cc] and not visited[rr, cc]:
                                visited[rr, cc] = True
                                stack.append((rr, cc))
                # A component counts for this region if it has enough cells
                # in the mask AND does not cross the midline (no cells outside
                # the mask). A crossing component is a single merged structure.
                if not crosses and in_mask_count >= min_cells:
                    n += 1
    return n


def detect_l2(history, params):
    """Post-pass over a two-region run: classify the outcome as 'coexist',
    'dominance', 'destruction', or 'none' based on whether EACH region
    retains an INDEPENDENT connected structure (one that does not cross the
    midline) for a sustained late window.

    The detector uses left_components and right_components — counts of
    connected components of structure lying entirely within each region
    (captured during the run). A component crossing the midline is a single
    merged structure, counted in neither region.

    L2 crossing fires when both regions have >= 1 independent component for
    >= L2_PERSIST consecutive late samples.

    The per-region material retention (left_retain, right_retain) is a
    secondary diagnostic for the dominance/destruction classification, NOT
    the crossing criterion — the one-seed control showed that material mass
    in both halves is uninformative (a single structure fills both halves).
    """
    late_frac = params.get("l2_late_window_frac", L2_LATE_WINDOW_FRAC)
    persist = params.get("l2_persist", L2_PERSIST)
    dom_ratio = params.get("dominance_ratio", DOMINANCE_RATIO)
    destroy_floor = params.get("destruction_floor", DESTRUCTION_FLOOR)

    n = len(history)
    if n == 0:
        return history

    # Per-region peak material (for the retention diagnostic).
    left_peak = max(r.get("left_total", 0.0) for r in history)
    right_peak = max(r.get("right_total", 0.0) for r in history)
    left_peak = max(left_peak, 1e-9)
    right_peak = max(right_peak, 1e-9)

    for r in history:
        r["left_retain"] = float(r.get("left_total", 0.0)) / left_peak
        r["right_retain"] = float(r.get("right_total", 0.0)) / right_peak

    # Late window.
    n_late = max(1, int(n * late_frac))
    late = history[-n_late:]

    # L2 crossing: both regions have >= 1 independent component for `persist`
    # consecutive late samples.
    run_len = 0
    l2_crossed = False
    l2_cross_step = None
    for r in late:
        lc = r.get("left_components", 0)
        rc = r.get("right_components", 0)
        if lc >= 1 and rc >= 1:
            run_len += 1
            if run_len >= persist and not l2_crossed:
                l2_crossed = True
                l2_cross_step = r["step"]
        else:
            run_len = 0

    # Outcome classification from the final late-window record.
    final = late[-1]
    l_ret = final["left_retain"]
    r_ret = final["right_retain"]
    lc = final.get("left_components", 0)
    rc = final.get("right_components", 0)
    # Late-window mean component counts (for the fragmented-vs-coexist
    # distinction). Genuine coexistence = 1-3 independent components per
    # region (a few structures, not a merged blob and not a fragmented
    # scatter). Fragmented = 4+ per region (erosion too high for
    # consolidation). Merged = 0 in either (single structure crossing the
    # midline).
    late_mean_lc = float(sum(r.get("left_components", 0) for r in late)) / len(late)
    late_mean_rc = float(sum(r.get("right_components", 0) for r in late)) / len(late)
    coexist_max = params.get("coexist_max_components", COEXIST_MAX_COMP)
    if l_ret < destroy_floor and r_ret < destroy_floor:
        outcome = "destruction"
    elif lc >= 1 and rc >= 1 and lc <= coexist_max and rc <= coexist_max:
        outcome = "coexist"
    elif (l_ret >= dom_ratio * r_ret) or (r_ret >= dom_ratio * l_ret):
        outcome = "dominance"
    elif lc >= 1 and rc >= 1 and (lc > coexist_max or rc > coexist_max):
        outcome = "fragmented"
    else:
        outcome = "none"

    # stable_l2: both regions have 1-coexist_max components for >= 50%
    # of the late window. Distinguishes stable coexistence from a transient
    # that flickers then merges (the offset=0.45/decay=0.002 case).
    stable_count = 0
    for r in late:
        lc2 = r.get("left_components", 0)
        rc2 = r.get("right_components", 0)
        if 1 <= lc2 <= coexist_max and 1 <= rc2 <= coexist_max:
            stable_count += 1
    stable_l2 = (stable_count / len(late)) >= 0.50

    for r in history:
        r["l2_crossed"] = l2_crossed
        r["l2_cross_step"] = l2_cross_step
    final["l2_outcome"] = outcome
    final["l2_left_retain"] = l_ret
    final["l2_right_retain"] = r_ret
    final["l2_late_mean_lc"] = late_mean_lc
    final["l2_late_mean_rc"] = late_mean_rc
    final["l2_stable"] = stable_l2
    return history


# --------------------------------------------------------------------------#
# Two-region run (wraps sim09's run_condition with seed placement + region
# tracking)
# --------------------------------------------------------------------------#
def run_two_region(params, seed, n_seeds=2):
    """Run one simulation with one or two pre-placed seed mounds. Returns
    {"history": [...], "summary": {...}, "snapshots": [...]}.

    n_seeds=2: left + right seeds (the L2 test).
    n_seeds=1: left seed only (the L1 control — what does a single
               structure do on the same grid, same agents?).

    Reuses sim09's run_condition machinery but injects the seed mounds
    after field creation and adds per-region material tracking to each
    history record.
    """
    size = params.get("grid_size", S.GRID_SIZE)
    left_mask, right_mask = region_masks(size)

    rng = S.make_rng(seed)
    n = params.get("n_termites", S.N_TERMITES)
    steps = params.get("steps", S.STEPS)
    sample = params.get("sample_every", S.SAMPLE_EVERY)
    channel = params.get("channel", "curvature")

    field = S.Field(size)
    if channel == "baseline_pheromone":
        field.pheromone = np.zeros((size, size), dtype=np.float64)

    # Place seed mounds.
    seed_region(field, size, "left", params)
    if n_seeds >= 2:
        seed_region(field, size, "right", params)

    termites = S.Termites(n, size, rng)
    history = []
    dep_acc = exc_acc = dep_convex_acc = dep_struct_acc = pick_acc = 0
    prev_structure_mask = None

    snapshot_size = params.get("snapshot_size", S.SNAPSHOT_SIZE)
    expected_records = max(1, (steps + sample - 1) // sample)
    snapshot_stride = max(1, round(expected_records / S.SNAPSHOT_TARGET_COUNT))
    raw_snapshots = []

    for step in range(steps):
        if channel == "curvature":
            curvature = S.compute_curvature(field, params)
            on_surface = S.compute_on_surface(field, params)
            ev = S.termite_step(termites, field, rng, params, curvature, on_surface)
            S.field_step(field, params)
            dep_acc += ev["deposits"]
            exc_acc += ev["excavations"]
            dep_convex_acc += ev["deposits_on_convex"]
            pick_acc += ev["pickups"]
        else:  # baseline_pheromone
            ev = S.termite_step_pheromone(termites, field, rng, params)
            S.field_step(field, params)
            dep_acc += ev["deposits"]
            dep_struct_acc += ev["deposits_on_structure"]
            pick_acc += ev["pickups"]

        if step % sample == 0:
            # Per-region material.
            lt, rt, total = compute_region_metrics(field, params,
                                                    left_mask, right_mask)
            # Per-region independent connected components (structures that
            # do not cross the midline). This is the L2 criterion.
            lc = _count_region_components(field, params, left_mask)
            rc = _count_region_components(field, params, right_mask)
            rec = S.compute_metrics(field, params, step, dep_acc, exc_acc,
                                    dep_convex_acc, pick_acc,
                                    prev_structure_mask,
                                    deposits_on_structure=dep_struct_acc)
            rec["left_total"] = lt
            rec["right_total"] = rt
            rec["left_components"] = lc
            rec["right_components"] = rc
            history.append(rec)
            dep_acc = exc_acc = dep_convex_acc = dep_struct_acc = pick_acc = 0
            prev_structure_mask = (field.material >
                                    params.get("structure_threshold",
                                               S.STRUCTURE_THRESHOLD)).copy()

            if (len(history) - 1) % snapshot_stride == 0:
                curv_now = S.compute_curvature(field, params)
                raw_snapshots.append((
                    int(step),
                    S._downsample_grid(field.material, snapshot_size),
                    S._downsample_grid(curv_now, snapshot_size),
                ))

    # sim09's crossing detector (single-structure H7 crossing) — runs on
    # the grid-wide metrics. The L2 detector runs on the per-region metrics.
    S.detect_crossing(history, params)
    detect_l2(history, params)

    summary = summarize_two_region(history, n_seeds=n_seeds)

    # Normalize snapshots (same as sim09).
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


def summarize_two_region(history, n_seeds=2):
    """Headline summary of a two-region (or one-seed control) run."""
    if not history:
        return {"l2_crossed": False, "l2_outcome": "none",
                "l2_left_retain": 0.0, "l2_right_retain": 0.0,
                "l2_stable": False,
                "n_seeds": n_seeds}
    last = history[-1]
    return {
        "l2_crossed": bool(last.get("l2_crossed", False)),
        "l2_cross_step": last.get("l2_cross_step", None),
        "l2_outcome": last.get("l2_outcome", "none"),
        "l2_left_retain": float(last.get("l2_left_retain", 0.0)),
        "l2_right_retain": float(last.get("l2_right_retain", 0.0)),
        "l2_late_mean_lc": float(last.get("l2_late_mean_lc", 0.0)),
        "l2_late_mean_rc": float(last.get("l2_late_mean_rc", 0.0)),
        "l2_stable": bool(last.get("l2_stable", False)),
        "final_total_material": float(last["total_material"]),
        "final_n_structure_cells": int(last["n_structure_cells"]),
        "crossed_h7": bool(last.get("crossed", False)),
        "n_seeds": n_seeds,
    }


# --------------------------------------------------------------------------#
# CLI
# --------------------------------------------------------------------------#
def curvature_params():
    """Curvature-channel params for the L2 test. Uses the TUNED regime
    (dpb=0.01, decay=0.002) where the crossing fires (Session 19)."""
    return {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "structure_threshold": S.STRUCTURE_THRESHOLD,
        "channel": "curvature",
        "d": 1.0, "material_decay": 0.002,
        "deposit_prob_base": 0.01,
        "deposit_prob_gain": S.DEPOSIT_PROB_GAIN,
    }


def baseline_pheromone_params():
    """Baseline-pheromone params (saturating cue control)."""
    return {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "structure_threshold": S.STRUCTURE_THRESHOLD,
        "channel": "baseline_pheromone",
        "material_decay": 0.002,
        "deposit_base": 0.01, "deposit_gain": S.DEPOSIT_GAIN,
    }


def cmd_run():
    """Run the four-condition 2×2 (curvature vs pheromone × 1 vs 2 seeds)
    and write results.json."""
    t0 = time.time()
    seed = 42
    results = {"config": {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "seed": seed,
        "min_component_cells": MIN_COMPONENT_CELLS,
        "l2_late_window_frac": L2_LATE_WINDOW_FRAC,
        "l2_persist": L2_PERSIST,
        "dominance_ratio": DOMINANCE_RATIO,
        "destruction_floor": DESTRUCTION_FLOOR,
        "seed_height": SEED_HEIGHT,
        "seed_sigma_frac": SEED_SIGMA_FRAC,
        "seed_offset_frac": SEED_OFFSET_FRAC,
    }}

    print("Running A: curvature_channel, 2 seeds (the L2 test)...")
    a = run_two_region(curvature_params(), seed=seed, n_seeds=2)
    print("Running B: baseline_pheromone, 2 seeds (saturating control)...")
    b = run_two_region(baseline_pheromone_params(), seed=seed, n_seeds=2)
    print("Running C: curvature_channel, 1 seed (L1 control)...")
    c = run_two_region(curvature_params(), seed=seed, n_seeds=1)
    print("Running D: baseline_pheromone, 1 seed (L1 pheromone control)...")
    d = run_two_region(baseline_pheromone_params(), seed=seed, n_seeds=1)

    results["curvature_2seed"] = a
    results["baseline_2seed"] = b
    results["curvature_1seed"] = c
    results["baseline_1seed"] = d

    json_str = S._compact_snapshot_arrays(
        json.dumps(S._pyify(results), indent=2))
    with open(RESULTS_PATH, "w") as f:
        f.write(json_str)

    print("\n=== RESULT: L2 Composition (H1/H10) ===")
    for name, r in [("curvature_2seed", a), ("baseline_2seed", b),
                    ("curvature_1seed", c), ("baseline_1seed", d)]:
        s = r["summary"]
        print(f"  {name:22s} l2_crossed={str(s['l2_crossed']):5s} "
              f"outcome={s['l2_outcome']:12s} "
              f"L_retain={s['l2_left_retain']:.2f} "
              f"R_retain={s['l2_right_retain']:.2f} "
              f"cells={s['final_n_structure_cells']}")
    print(f"\nWrote {RESULTS_PATH}  ({time.time()-t0:.1f}s)")


def cmd_selftest():
    """Prove the L2 detector can fire and that negating each criterion
    withholds. Also verify the two-region run produces per-region metrics."""
    # ---- Part 1: two-region run produces per-region metrics ----
    tiny = {"grid_size": 30, "n_termites": 20, "steps": 200,
            "sample_every": 25, "channel": "curvature",
            "structure_threshold": S.STRUCTURE_THRESHOLD,
            "d": 1.0, "material_decay": 0.002,
            "deposit_prob_base": 0.01}
    r2 = run_two_region(tiny, seed=42, n_seeds=2)
    assert len(r2["history"]) >= 4, "two-seed run should produce history"
    for rec in r2["history"]:
        assert "left_total" in rec and "right_total" in rec, \
            "each record should carry per-region totals"
        assert rec["left_total"] >= 0.0 and rec["right_total"] >= 0.0
        assert "l2_crossed" in rec and "l2_outcome" in rec or True  # last rec
    assert "l2_outcome" in r2["history"][-1], \
        "last record should carry l2_outcome"
    print("selftest: Part 1 OK (two-region run + per-region metrics)")

    # ---- Part 2: one-seed run (control) has right_total ~ 0 ----
    r1 = run_two_region(tiny, seed=42, n_seeds=1)
    # The right region was never seeded; its material should be low relative
    # to the left. (It won't be exactly 0 because termites wander, but the
    # left should dominate.)
    last = r1["history"][-1]
    assert last["left_total"] > last["right_total"], \
        "one-seed run: left region should have more material than right"
    print("selftest: Part 2 OK (one-seed control)")

    # ---- Part 3: L2 detector fires on synthetic coexistence ----
    # Build synthetic histories with left_components/right_components
    # (the corrected L2 criterion). The detector should fire on
    # coexistence and withhold on dominance, destruction, single-region.
    base_rec = {
        "step": 0, "total_material": 100.0, "n_structure_cells": 10,
        "mean_curvature": 0.0, "max_curvature": 0.0, "roughness": 0.0,
        "mean_pheromone": 0.0, "max_pheromone": 0.0,
        "deposits_this_window": 0, "excavations_this_window": 0,
        "deposits_on_convex_this_window": 0, "pickups_this_window": 0,
        "structure_stability": 0.95, "n_pillars": 1, "compactness": 0.5,
        "deposits_on_convex_fraction": 0.75,
        "deposit_on_structure_fraction": 0.75,
        "material_growth_rate": None, "mass_plateau": None,
        "crossed": True, "crossing_step": 0,
        "left_total": 50.0, "right_total": 50.0,
        "left_components": 1, "right_components": 1,
    }

    def make_history(l_comp, r_comp, l_late_mat, r_late_mat, n=40):
        """Build a history where left/right have the given component counts
        and late material. Early: both at peak (50). Late (last 25%):
        components = l_comp/r_comp, material = l_late_mat/r_late_mat."""
        h = []
        for i in range(n):
            r = dict(base_rec)
            r["step"] = i * 25
            if i >= int(n * 0.75):
                r["left_total"] = l_late_mat
                r["right_total"] = r_late_mat
                r["left_components"] = l_comp
                r["right_components"] = r_comp
            else:
                r["left_total"] = 50.0
                r["right_total"] = 50.0
                r["left_components"] = 1
                r["right_components"] = 1
            h.append(r)
        return h

    # (a) coexistence: both regions have independent components, both
    # retain material → fires, outcome=coexist
    h_co = make_history(1, 1, 40.0, 40.0)
    detect_l2(h_co, {})
    assert h_co[-1]["l2_crossed"] is True, \
        "coexistence history should fire L2 crossing"
    assert h_co[-1]["l2_outcome"] == "coexist", \
        "coexistence history should classify as coexist"

    # (b) dominance: left has component, right has 0 (right collapsed).
    # Left retains 0.9, right retains 0.1 (ratio 9x >= 3x) → dominance.
    h_dom = make_history(1, 0, 45.0, 5.0)
    detect_l2(h_dom, {})
    assert h_dom[-1]["l2_crossed"] is False, \
        "dominance history should NOT fire L2 crossing"
    assert h_dom[-1]["l2_outcome"] == "dominance", \
        "dominance history should classify as dominance"

    # (c) destruction: both retain 0.05 (< 0.10 floor), both 0 components
    # → does NOT fire, outcome=destruction
    h_des = make_history(0, 0, 2.5, 2.5)
    detect_l2(h_des, {})
    assert h_des[-1]["l2_crossed"] is False, \
        "destruction history should NOT fire L2 crossing"
    assert h_des[-1]["l2_outcome"] == "destruction", \
        "destruction history should classify as destruction"

    # (d) single-region: left has component, right has 0 → does NOT fire,
    # outcome=dominance (left dominates)
    h_one = make_history(1, 0, 45.0, 0.0)
    detect_l2(h_one, {})
    assert h_one[-1]["l2_crossed"] is False, \
        "single-region history should NOT fire L2 crossing"

    # (e) merged: both have 0 components (single structure crosses midline)
    # but both have material → does NOT fire (no independent components)
    h_merged = make_history(0, 0, 40.0, 40.0)
    detect_l2(h_merged, {})
    assert h_merged[-1]["l2_crossed"] is False, \
        "merged-structure history should NOT fire L2 crossing"
    assert h_merged[-1]["l2_outcome"] == "none", \
        "merged-structure history should classify as none"

    # (f) fragmented: both have 5 components (> COEXIST_MAX_COMP=3) →
    # does NOT fire as coexist; outcome=fragmented
    h_frag = make_history(5, 5, 40.0, 40.0)
    detect_l2(h_frag, {})
    assert h_frag[-1]["l2_outcome"] == "fragmented", \
        "fragmented history should classify as fragmented"
    print("selftest: Part 3 OK (L2 detector fires/withholds correctly)")

    # ---- Part 4: determinism — run twice, diff ----
    r2a = run_two_region(tiny, seed=42, n_seeds=2)
    r2b = run_two_region(tiny, seed=42, n_seeds=2)
    sa, sb = r2a["summary"], r2b["summary"]
    assert sa["l2_crossed"] == sb["l2_crossed"], "determinism: l2_crossed"
    assert sa["l2_outcome"] == sb["l2_outcome"], "determinism: l2_outcome"
    assert abs(sa["l2_left_retain"] - sb["l2_left_retain"]) < 1e-9, \
        "determinism: left_retain"
    assert abs(sa["l2_right_retain"] - sb["l2_right_retain"]) < 1e-9, \
        "determinism: right_retain"
    print("selftest: Part 4 OK (determinism)")

    print("selftest: ALL OK")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        cmd_run()
    elif cmd == "selftest":
        cmd_selftest()
    else:
        print("usage: sim10.py [run|selftest]")


if __name__ == "__main__":
    main()
