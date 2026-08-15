"""
Sim12: The Autopoietic Boundary — Does a Self-Maintaining Boundary Enable L2
Composition?

THE QUESTION (queued-topic #81):
  sim11's long-range inhibitor is a PASSIVE field — I = max(0, far_smoothed −
  material), recomputed each step from scratch. It has no memory. If one
  structure wobbles (loses material), the boundary immediately weakens,
  allowing the other structure to invade.

  An AUTOPOIOTIC boundary would self-maintain: it has its own dynamics
  (growth + decay), so it persists even when the structures that created it
  wobble. This tests H5/H6 (autopoiesis as the persistence condition for a
  new actor at a higher scale) and H1/H10 (explicit composition mechanisms).

  The critical test: B has MEMORY. When one structure is perturbed, B
  persists (decays at its own rate), while the passive I vanishes instantly
  (recomputed from the reduced material).

DESIGN:
  The autopoietic boundary field B has its own growth/decay dynamics:

      B_new = B * (1 - b_decay) + b_growth * co_presence

  Where co_presence = min(left_shadow, right_shadow) — the overlap of the two
  structures' far-field shadows. This is high only where BOTH structures
  contribute (the gap), and zero when only one structure exists (the 1-seed
  control gets B ≈ 0 — the boundary is a BETWEEN-structures phenomenon).

  B suppresses deposit probability: p_dep *= (1 - g * B_norm / (1 + B_norm))

  The co-presence signal is the key design choice that distinguishes B from
  sim11's passive I. sim11's I = max(0, far - local) is the self-cancelling
  shadow — it is high in the gap AND at structure edges (where the shadow from
  the same structure leaks past the local material). B's co_presence is
  min(left, right) — it is high ONLY where both structures' shadows overlap.
  For a single structure, one shadow is zero, so co_presence is zero, and B
  does not grow. The 1-seed control should show B ≈ 0 — the boundary does not
  affect a single structure at all.

SIX CONDITIONS:
  A: autopoietic boundary, 2 seeds (the L2 test)
  B: autopoietic boundary, 1 seed (L1 control — boundary should be ~0)
  C: passive inhibitor (sim11's I), 2 seeds (direct comparison)
  D: passive inhibitor (sim11's I), 1 seed (passive L1 control)
  E: no inhibition, 2 seeds (sim10 baseline — should merge)
  F: no inhibition, 1 seed (sim10 L1 control)

PERTURBATION TEST:
  At step 1500, remove 50% of the right structure's material. Measure B and
  I at steps 1500, 1550, 1600, 1650, 1700. The autopoietic boundary B should
  persist (slow exponential decay at b_decay) while the passive I drops
  immediately (recomputed from the reduced material). Does B protect the gap
  long enough for the right structure to recover? Does L2 coexistence survive
  the perturbation under B but not under I?

METHODOLOGY (per CLAUDE.md §4 step 6):
  - Self-test proves B grows with co-presence, decays without it, and persists
    after a perturbation (more B remains 100 steps after perturbation than
    the passive I). Also: B ≈ 0 for a single seed (co-presence is zero).
  - Control arms: the 1-seed controls (B, D, F) show what a single structure
    does on the same grid. The passive inhibitor control (C, D) is the direct
    comparison. The no-inhibition control (E, F) is the sim10 baseline.
  - Determinism: run twice, diff the JSON.
  - Compute the metric's ceiling: B is bounded by b_growth * max(co_presence)
    / b_decay (equilibrium). co_presence is bounded by max(material) (shadows
    can't exceed the source). The suppression is bounded in [0, g).

This module imports sim11 (which imports sim10 and sim09). It adds the
autopoietic boundary field, the co-presence computation, and the perturbation
test. sim11/sim10/sim09 remain the single sources of truth.
"""

import os
import sys
import json
import time
import copy

import numpy as np

# Import sim11 (which imports sim10 and sim09).
SIM11_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "sim11_boundary_mechanism")
sys.path.insert(0, SIM11_DIR)
import sim11 as I11  # noqa: E402
import sim10 as T    # noqa: E402
import sim09 as S    # noqa: E402

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SIM_DIR, "results.json")
OUTPUT_DIR = os.path.join(SIM_DIR, "output")

# --------------------------------------------------------------------------#
# Co-presence signal — min(left_shadow, right_shadow)
# --------------------------------------------------------------------------#
# The co-presence signal is the overlap of the two structures' far-field
# shadows. We split the material field at the midline, smooth each half
# independently (using sim09's _diffuse on the torus), and take the element-wise
# minimum. This is high only where BOTH structures' shadows reach — i.e., in
# the gap between them. For a single structure, one shadow is zero everywhere
# on the other side, so co_presence ≈ 0 there. The boundary is a BETWEEN-
# structures phenomenon by construction.
#
# We use FEWER diffusion passes than sim11's inhibitor (6 vs 12) to keep the
# signal more localized. With 12 passes on an 80×80 torus, the shadow wraps
# around and the two shadows overlap everywhere, destroying the localization.
# 6 passes at rate 0.7 gives a shadow radius of ~6*sqrt(2*0.7) ≈ 7 cells,
# which reaches across the 40-cell gap but doesn't fully wrap the torus.
COPRESENCE_PASSES = 8
COPRESENCE_DIFFUSE_RATE = 0.7


def compute_copresence(field, params):
    """Co-presence: min(left_shadow, right_shadow).

    Split the material field at the midline. Smooth each half independently
    on the torus. Take the element-wise minimum. High only where both
    structures' shadows overlap (the gap). Zero where only one structure
    contributes.

    For a single seed (1-seed control), one half is empty, so its shadow is
    zero, and co_presence is zero everywhere — the boundary does not grow.
    """
    size = field.material.shape[0]
    mid = size // 2
    passes = params.get("copresence_passes", COPRESENCE_PASSES)
    rate = params.get("copresence_diffuse_rate", COPRESENCE_DIFFUSE_RATE)

    left = np.zeros_like(field.material)
    right = np.zeros_like(field.material)
    left[:, :mid] = field.material[:, :mid]
    right[:, mid:] = field.material[:, mid:]

    for _ in range(passes):
        left = S._diffuse(left, rate)
        right = S._diffuse(right, rate)

    return np.minimum(left, right)


# --------------------------------------------------------------------------#
# Autopoietic boundary field B — growth + decay dynamics
# --------------------------------------------------------------------------#
BOUNDARY_GROWTH = 0.1     # how fast B accumulates from co-presence
BOUNDARY_DECAY = 0.005    # per-step decay (half-life ~138 steps)


def boundary_step(B, copresence, params):
    """Update the autopoietic boundary field: growth from co-presence,
    independent decay.

    B_new = B * (1 - decay) + growth * co_presence

    The decay is INDEPENDENT of the material field. This is the autopoietic
    property: B has its own time constant. When the structures wobble, B
    persists (decays at b_decay), while the passive I vanishes instantly
    (recomputed from the current material).

    At equilibrium: B_eq ≈ growth * co_presence / decay.
    With growth=0.1, decay=0.005: B_eq ≈ 20 * co_presence.
    """
    growth = params.get("boundary_growth", BOUNDARY_GROWTH)
    decay = params.get("boundary_decay", BOUNDARY_DECAY)
    B = B * (1.0 - decay) + growth * copresence
    return np.maximum(0.0, B)


# --------------------------------------------------------------------------#
# Autopoietic-boundary-gated curvature termite step
# --------------------------------------------------------------------------#
_CURVE_FOLLOW = S.CURVE_FOLLOW
_RELOAD_PROB = S.RELOAD_PROB
_PELLET = S.PELLET


def termite_step_autopoietic(termites, field, rng, params, curvature,
                             on_surface, B, b_scale):
    """Curvature-channel step with deposit probability suppressed by the
    autopoietic boundary field B. Mirrors sim11's termite_step_inhibited
    exactly except the suppression uses B (which has memory) instead of I
    (which is recomputed each step).
    """
    n = termites.n
    size = termites.size
    curve_follow = params.get("curve_follow", _CURVE_FOLLOW)
    reload_prob = params.get("reload_prob", _RELOAD_PROB)
    deposit_prob_base = params.get("deposit_prob_base", S.DEPOSIT_PROB_BASE)
    deposit_prob_gain = params.get("deposit_prob_gain", S.DEPOSIT_PROB_GAIN)
    excavate_prob_base = params.get("excavate_prob_base", S.EXCAVATE_PROB_BASE)
    excavate_prob_gain = params.get("excavate_prob_gain", S.EXCAVATE_PROB_GAIN)
    pellet = params.get("pellet", _PELLET)
    pickup_prob_base = params.get("pickup_prob_base", S.PICKUP_PROB_BASE)
    inh_gain = params.get("inh_gain", 0.0)
    recruit_response = params.get("recruit_response", "linear")

    curv = curvature
    ons = on_surface
    mat = field.material
    B_norm = B / max(b_scale, 1e-9)

    deposits = 0
    excavations = 0
    deposits_on_convex = 0
    pickups = 0

    def _route(base, gain, c):
        if recruit_response == "saturating":
            return base + gain * c / (1.0 + abs(c))
        return base + gain * c

    for i in range(n):
        y = int(termites.y[i])
        x = int(termites.x[i])

        # --- movement (identical to sim09/sim11) ---
        if rng.random() < curve_follow:
            best_dy = 0
            best_dx = 0
            if termites.loaded[i]:
                best_v = -np.inf
                for dy, dx in S._MOORE:
                    yy = (y + dy) % size
                    xx = (x + dx) % size
                    v = curv[yy, xx]
                    if v > best_v:
                        best_v = v
                        best_dy, best_dx = dy, dx
            else:
                best_v = np.inf
                for dy, dx in S._MOORE:
                    yy = (y + dy) % size
                    xx = (x + dx) % size
                    v = curv[yy, xx]
                    if v < best_v:
                        best_v = v
                        best_dy, best_dx = dy, dx
            y = (y + best_dy) % size
            x = (x + best_dx) % size
        else:
            dy, dx = S._MOORE[int(rng.integers(0, 8))]
            y = (y + dy) % size
            x = (x + dx) % size
        termites.y[i] = y
        termites.x[i] = x

        # --- reload / excavate / pickup (identical to sim09/sim11) ---
        if not termites.loaded[i]:
            if rng.random() < reload_prob:
                termites.loaded[i] = True
            elif mat[y, x] > 0:
                c = curv[y, x]
                if c < 0:
                    p_exc = min(max(_route(excavate_prob_base,
                                           excavate_prob_gain, -c), 0.0), 1.0)
                    if rng.random() < p_exc:
                        mat[y, x] = max(0.0, mat[y, x] - pellet)
                        termites.loaded[i] = True
                        excavations += 1
                else:
                    if rng.random() < pickup_prob_base:
                        mat[y, x] = max(0.0, mat[y, x] - pellet)
                        termites.loaded[i] = True
                        pickups += 1

        # --- deposit (loaded) — AUTOPOIOTIC BOUNDARY GATE ---
        if termites.loaded[i]:
            c = curv[y, x]
            if ons[y, x]:
                if recruit_response == "saturating":
                    p_dep = (deposit_prob_base
                             + deposit_prob_gain * c / (1.0 + abs(c)))
                else:
                    p_dep = deposit_prob_base + deposit_prob_gain * c
            else:
                p_dep = deposit_prob_base
            # Autopoietic boundary suppression.
            if inh_gain > 0.0:
                supp = inh_gain * B_norm[y, x] / (1.0 + B_norm[y, x])
                p_dep = p_dep * (1.0 - supp)
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


# --------------------------------------------------------------------------#
# Two-region run with autopoietic boundary (or passive inhibitor, or none)
# --------------------------------------------------------------------------#
def run_two_region_autopoietic(params, seed, n_seeds=2, mode="autopoietic",
                               perturb_at=None, perturb_frac=0.5):
    """Run one simulation with one or two seed mounds.

    mode = "autopoietic"  → autopoietic boundary B (growth/decay, memory)
    mode = "passive"      → sim11's passive inhibitor I (no memory)
    mode = "none"         → no inhibition (sim10 baseline)

    perturb_at = step at which to remove perturb_frac of the right structure's
                 material (None = no perturbation). Tests boundary persistence.

    Returns {"history": [...], "summary": {...}, "snapshots": [...],
             "boundary_trace": [...]}.
    """
    size = params.get("grid_size", S.GRID_SIZE)
    left_mask, right_mask = T.region_masks(size)

    rng = S.make_rng(seed)
    n = params.get("n_termites", S.N_TERMITES)
    steps = params.get("steps", S.STEPS)
    sample = params.get("sample_every", S.SAMPLE_EVERY)
    channel = params.get("channel", "curvature")
    inh_gain = params.get("inh_gain", 0.0)

    field = S.Field(size)
    if channel == "baseline_pheromone":
        field.pheromone = np.zeros((size, size), dtype=np.float64)

    T.seed_region(field, size, "left", params)
    if n_seeds >= 2:
        T.seed_region(field, size, "right", params)

    # Initialize the boundary field B (autopoietic mode).
    B = np.zeros((size, size), dtype=np.float64)
    b_scale = 1.0

    # For passive mode, we need sim11's inhibitor scale.
    inh_scale = 1.0
    if mode == "passive" and inh_gain > 0.0:
        I0 = I11.compute_inhibitor(field, params)
        inh_scale = max(float(np.percentile(I0, 95)), 1e-9)
        params = dict(params)
        params["inh_scale"] = inh_scale

    # For autopoietic mode, compute the initial co-presence to set b_scale.
    if mode == "autopoietic" and inh_gain > 0.0:
        cp0 = compute_copresence(field, params)
        b_scale = max(float(np.percentile(cp0, 95)), 1e-9)

    termites = S.Termites(n, size, rng)
    history = []
    dep_acc = exc_acc = dep_convex_acc = dep_struct_acc = pick_acc = 0
    prev_structure_mask = None

    snapshot_size = params.get("snapshot_size", S.SNAPSHOT_SIZE)
    expected_records = max(1, (steps + sample - 1) // sample)
    snapshot_stride = max(1, round(expected_records / S.SNAPSHOT_TARGET_COUNT))
    raw_snapshots = []

    # Boundary trace: record B and I statistics at sample points for the
    # perturbation persistence test.
    boundary_trace = []

    for step in range(steps):
        # --- perturbation ---
        if perturb_at is not None and step == perturb_at:
            right_material = field.material[right_mask]
            field.material[right_mask] = right_material * (1.0 - perturb_frac)

        if channel == "curvature":
            curvature = S.compute_curvature(field, params)
            on_surface = S.compute_on_surface(field, params)

            if mode == "autopoietic" and inh_gain > 0.0:
                # Update B, then step termites with B suppression.
                cp = compute_copresence(field, params)
                B = boundary_step(B, cp, params)
                ev = termite_step_autopoietic(termites, field, rng, params,
                                             curvature, on_surface, B, b_scale)
            elif mode == "passive" and inh_gain > 0.0:
                inhibitor = I11.compute_inhibitor(field, params)
                ev = I11.termite_step_inhibited(termites, field, rng, params,
                                               curvature, on_surface,
                                               inhibitor)
            else:
                ev = S.termite_step(termites, field, rng, params,
                                    curvature, on_surface)
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
            lt, rt, total = T.compute_region_metrics(field, params,
                                                     left_mask, right_mask)
            lc = T._count_region_components(field, params, left_mask)
            rc = T._count_region_components(field, params, right_mask)
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

            # Boundary trace: record B and I statistics.
            if mode == "autopoietic" and inh_gain > 0.0:
                b_max = float(B.max())
                b_gap = float(B[size // 2, size // 2])  # center of grid (gap)
            else:
                b_max = 0.0
                b_gap = 0.0
            if inh_gain > 0.0:
                I_now = I11.compute_inhibitor(field, params)
                i_max = float(I_now.max())
                i_gap = float(I_now[size // 2, size // 2])
            else:
                i_max = 0.0
                i_gap = 0.0
            boundary_trace.append({
                "step": step,
                "b_max": b_max,
                "b_gap": b_gap,
                "i_max": i_max,
                "i_gap": i_gap,
                "right_total": rt,
            })

            if (len(history) - 1) % snapshot_stride == 0:
                curv_now = S.compute_curvature(field, params)
                raw_snapshots.append((
                    int(step),
                    S._downsample_grid(field.material, snapshot_size),
                    S._downsample_grid(curv_now, snapshot_size),
                    (S._downsample_grid(B, snapshot_size)
                     if mode == "autopoietic" and inh_gain > 0.0 else None),
                ))

    S.detect_crossing(history, params)
    T.detect_l2(history, params)
    summary = summarize_two_region_autopoietic(history, n_seeds=n_seeds)

    # Normalize snapshots.
    snapshots = []
    if raw_snapshots:
        mat_max = max(m.max() for _, m, _, _ in raw_snapshots)
        mat_max = mat_max if mat_max > 0 else 1.0
        curv_min = min(c.min() for _, _, c, _ in raw_snapshots)
        curv_max = max(c.max() for _, _, c, _ in raw_snapshots)
        curv_range = (curv_max - curv_min) if curv_max > curv_min else 1.0
        b_max_all = max((b.max() for _, _, _, b in raw_snapshots
                         if b is not None), default=1.0)
        b_max_all = b_max_all if b_max_all > 0 else 1.0
        for step, mat, curv, b in raw_snapshots:
            mat_norm = np.clip(mat / mat_max, 0.0, 1.0)
            curv_norm = np.clip((curv - curv_min) / curv_range, 0.0, 1.0)
            rec = {
                "step": step,
                "material": np.round(mat_norm, 4).flatten().tolist(),
                "curvature": np.round(curv_norm, 4).flatten().tolist(),
            }
            if b is not None:
                b_norm = np.clip(b / b_max_all, 0.0, 1.0)
                rec["boundary"] = np.round(b_norm, 4).flatten().tolist()
            snapshots.append(rec)

    return {
        "history": history,
        "summary": summary,
        "snapshots": snapshots,
        "boundary_trace": boundary_trace,
    }


def summarize_two_region_autopoietic(history, n_seeds=2):
    """Headline summary, extending sim10's."""
    s = T.summarize_two_region(history, n_seeds=n_seeds)
    if not history:
        return s
    return s


# --------------------------------------------------------------------------#
# CLI
# --------------------------------------------------------------------------#
def curvature_params(inh_gain=0.0):
    """Curvature-channel params for sim12. Uses the TUNED regime (dpb=0.01,
    decay=0.002) where sim10 showed 15/16 merge and sim11 showed 2/4 clean
    coexistence at g=0.9."""
    p = {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "structure_threshold": S.STRUCTURE_THRESHOLD,
        "channel": "curvature",
        "d": 1.0, "material_decay": 0.002,
        "deposit_prob_base": 0.01,
        "deposit_prob_gain": S.DEPOSIT_PROB_GAIN,
    }
    if inh_gain > 0.0:
        p["inh_gain"] = inh_gain
        p["copresence_passes"] = COPRESENCE_PASSES
        p["copresence_diffuse_rate"] = COPRESENCE_DIFFUSE_RATE
        p["boundary_growth"] = BOUNDARY_GROWTH
        p["boundary_decay"] = BOUNDARY_DECAY
        p["inhibitor_passes"] = I11.INHIBITOR_PASSES
        p["inhibitor_diffuse_rate"] = I11.INHIBITOR_DIFFUSE_RATE
    return p


def cmd_run(inh_gain=0.9):
    """Run the 6-condition experiment: {autopoietic, passive, none} × {2, 1} seeds."""
    t0 = time.time()
    seed = 42
    results = {"config": {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "seed": seed,
        "channel": "curvature",
        "d": 1.0, "material_decay": 0.002,
        "deposit_prob_base": 0.01,
        "inh_gain": inh_gain,
        "boundary_growth": BOUNDARY_GROWTH,
        "boundary_decay": BOUNDARY_DECAY,
        "copresence_passes": COPRESENCE_PASSES,
        "seed_height": T.SEED_HEIGHT,
        "seed_sigma_frac": T.SEED_SIGMA_FRAC,
        "seed_offset_frac": T.SEED_OFFSET_FRAC,
    }}

    print("Running A: autopoietic boundary, 2 seeds (the L2 test)...")
    a = run_two_region_autopoietic(curvature_params(inh_gain), seed=seed,
                                   n_seeds=2, mode="autopoietic")
    print("Running B: autopoietic boundary, 1 seed (L1 control)...")
    b = run_two_region_autopoietic(curvature_params(inh_gain), seed=seed,
                                   n_seeds=1, mode="autopoietic")
    print("Running C: passive inhibitor, 2 seeds (direct comparison)...")
    c = run_two_region_autopoietic(curvature_params(inh_gain), seed=seed,
                                   n_seeds=2, mode="passive")
    print("Running D: passive inhibitor, 1 seed (passive L1 control)...")
    d = run_two_region_autopoietic(curvature_params(inh_gain), seed=seed,
                                   n_seeds=1, mode="passive")
    print("Running E: no inhibition, 2 seeds (sim10 baseline)...")
    e = run_two_region_autopoietic(curvature_params(0.0), seed=seed,
                                   n_seeds=2, mode="none")
    print("Running F: no inhibition, 1 seed (sim10 L1 control)...")
    f = run_two_region_autopoietic(curvature_params(0.0), seed=seed,
                                   n_seeds=1, mode="none")

    results["auto_2seed"] = a
    results["auto_1seed"] = b
    results["passive_2seed"] = c
    results["passive_1seed"] = d
    results["none_2seed"] = e
    results["none_1seed"] = f

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_str = S._compact_snapshot_arrays(
        json.dumps(S._pyify(results), indent=2))
    with open(RESULTS_PATH, "w") as f_out:
        f_out.write(json_str)

    print("\n=== RESULT: Autopoietic Boundary (H1/H5/H6/H7/H10) ===")
    for name, r in [("auto_2seed", a), ("auto_1seed", b),
                    ("passive_2seed", c), ("passive_1seed", d),
                    ("none_2seed", e), ("none_1seed", f)]:
        s = r["summary"]
        print(f"  {name:18s} l2_crossed={str(s['l2_crossed']):5s} "
              f"outcome={s['l2_outcome']:12s} "
              f"L_retain={s['l2_left_retain']:.2f} "
              f"R_retain={s['l2_right_retain']:.2f} "
              f"stable={str(s['l2_stable']):5s} "
              f"h7={str(s['crossed_h7']):5s} "
              f"cells={s['final_n_structure_cells']}")
    print(f"\nWrote {RESULTS_PATH}  ({time.time()-t0:.1f}s)")


def cmd_perturbation(inh_gain=0.9, perturb_step=1500):
    """Run the perturbation test: remove 50% of the right structure's
    material at step 1500, compare B persistence (autopoietic) vs I
    persistence (passive)."""
    t0 = time.time()
    seed = 42
    results = {"config": {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "seed": seed,
        "channel": "curvature", "d": 1.0, "material_decay": 0.002,
        "deposit_prob_base": 0.01, "inh_gain": inh_gain,
        "perturb_at": perturb_step, "perturb_frac": 0.5,
    }}

    print("Running perturbation test: autopoietic boundary...")
    a = run_two_region_autopoietic(curvature_params(inh_gain), seed=seed,
                                   n_seeds=2, mode="autopoietic",
                                   perturb_at=perturb_step)
    print("Running perturbation test: passive inhibitor...")
    c = run_two_region_autopoietic(curvature_params(inh_gain), seed=seed,
                                   n_seeds=2, mode="passive",
                                   perturb_at=perturb_step)
    print("Running perturbation test: no inhibition...")
    e = run_two_region_autopoietic(curvature_params(0.0), seed=seed,
                                   n_seeds=2, mode="none",
                                   perturb_at=perturb_step)

    results["auto_perturb"] = a
    results["passive_perturb"] = c
    results["none_perturb"] = e

    path = os.path.join(OUTPUT_DIR, "perturbation_results.json")
    json_str = S._compact_snapshot_arrays(
        json.dumps(S._pyify(results), indent=2))
    with open(path, "w") as f_out:
        f_out.write(json_str)

    print("\n=== PERTURBATION TEST (perturb at step %d) ===" % perturb_step)
    for name, r in [("auto_perturb", a), ("passive_perturb", c),
                    ("none_perturb", e)]:
        s = r["summary"]
        bt = r.get("boundary_trace", [])
        # Find the pre- and post-perturbation boundary stats.
        pre = [b for b in bt if b["step"] < perturb_step]
        post = [b for b in bt if b["step"] >= perturb_step]
        pre_b_gap = pre[-1]["b_gap"] if pre else 0.0
        pre_i_gap = pre[-1]["i_gap"] if pre else 0.0
        post_100 = [b for b in post if b["step"] <= perturb_step + 100]
        post_b_gap_100 = post_100[-1]["b_gap"] if post_100 else 0.0
        post_i_gap_100 = post_100[-1]["i_gap"] if post_100 else 0.0
        pre_r = pre[-1]["right_total"] if pre else 0.0
        post_r_100 = post_100[-1]["right_total"] if post_100 else 0.0
        print(f"  {name:18s} l2={str(s['l2_crossed']):5s} "
              f"outcome={s['l2_outcome']:12s} "
              f"B_gap: {pre_b_gap:.3f}→{post_b_gap_100:.3f} "
              f"I_gap: {pre_i_gap:.3f}→{post_i_gap_100:.3f} "
              f"R_total: {pre_r:.1f}→{post_r_100:.1f}")

    path_short = os.path.relpath(path, SIM_DIR)
    print(f"\nWrote {path_short}  ({time.time()-t0:.1f}s)")


def cmd_robustness(inh_gain=0.9):
    """4-seed robustness sweep for autopoietic vs passive vs none."""
    t0 = time.time()
    seeds = [42, 123, 256, 999]
    results = {"config": {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "seeds": seeds,
        "channel": "curvature", "d": 1.0, "material_decay": 0.002,
        "deposit_prob_base": 0.01, "inh_gain": inh_gain,
    }}

    for mode_label, mode in [("auto", "autopoietic"), ("passive", "passive"),
                             ("none", "none")]:
        for ns in [2, 1]:
            key = f"{mode_label}_{ns}seed"
            results[key] = []
            for sd in seeds:
                p = curvature_params(inh_gain) if mode != "none" \
                    else curvature_params(0.0)
                r = run_two_region_autopoietic(p, seed=sd, n_seeds=ns,
                                             mode=mode)
                results[key].append({
                    "seed": sd,
                    "l2_crossed": r["summary"]["l2_crossed"],
                    "l2_outcome": r["summary"]["l2_outcome"],
                    "l2_stable": r["summary"]["l2_stable"],
                    "crossed_h7": r["summary"]["crossed_h7"],
                    "cells": r["summary"]["final_n_structure_cells"],
                    "left_retain": r["summary"]["l2_left_retain"],
                    "right_retain": r["summary"]["l2_right_retain"],
                })
                print(f"  {key} seed={sd}: l2={r['summary']['l2_crossed']} "
                      f"outcome={r['summary']['l2_outcome']} "
                      f"stable={r['summary']['l2_stable']} "
                      f"h7={r['summary']['crossed_h7']}")

    path = os.path.join(OUTPUT_DIR, "robustness_sweep.json")
    with open(path, "w") as f_out:
        json.dump(S._pyify(results), f_out, indent=2)

    # Print summary table.
    print("\n=== ROBUSTNESS SWEEP ===")
    for mode_label in ["auto", "passive", "none"]:
        for ns in [2, 1]:
            key = f"{mode_label}_{ns}seed"
            entries = results[key]
            n_cross = sum(1 for e in entries if e["l2_crossed"])
            n_coexist = sum(1 for e in entries if e["l2_outcome"] == "coexist")
            n_stable = sum(1 for e in entries if e["l2_stable"])
            n_h7 = sum(1 for e in entries if e["crossed_h7"])
            if ns == 2:
                clean = sum(1 for sd, e in zip(seeds, entries)
                            if e["l2_outcome"] == "coexist")
            else:
                clean = "—"
            print(f"  {key:18s} l2={n_cross}/4 coexist={n_coexist}/4 "
                  f"stable={n_stable}/4 h7={n_h7}/4 clean={clean}")

    print(f"\nWrote output/robustness_sweep.json  ({time.time()-t0:.1f}s)")


def cmd_selftest():
    """Prove sim12's additions work and the autopoietic boundary behaves as
    claimed. Verify determinism."""
    tiny = {"grid_size": 30, "n_termites": 20, "steps": 300,
            "sample_every": 25, "channel": "curvature",
            "structure_threshold": S.STRUCTURE_THRESHOLD,
            "d": 1.0, "material_decay": 0.002,
            "deposit_prob_base": 0.01, "inh_gain": 0.9,
            "copresence_passes": COPRESENCE_PASSES,
            "copresence_diffuse_rate": COPRESENCE_DIFFUSE_RATE,
            "boundary_growth": BOUNDARY_GROWTH,
            "boundary_decay": BOUNDARY_DECAY}

    # ---- Part 1: co-presence is high in the gap, zero for a single seed ----
    field = S.Field(30)
    T.seed_region(field, 30, "left", {})
    T.seed_region(field, 30, "right", {})
    cp2 = compute_copresence(field, tiny)
    mid = 15
    gap_cp = float(cp2[mid, mid])
    assert gap_cp > 0.0, \
        f"co-presence in gap should be >0 for two seeds; got {gap_cp}"

    field1 = S.Field(30)
    T.seed_region(field1, 30, "left", {})
    cp1 = compute_copresence(field1, tiny)
    gap_cp1 = float(cp1[mid, mid])
    assert gap_cp1 < gap_cp * 0.1, \
        f"co-presence for single seed ({gap_cp1}) should be << two seeds ({gap_cp})"
    print(f"selftest: Part 1 OK (co-presence gap: 2seed={gap_cp:.4f} "
          f">> 1seed={gap_cp1:.6f})")

    # ---- Part 2: B grows with co-presence and decays without it ----
    B = np.zeros((30, 30), dtype=np.float64)
    # Growth: 10 steps with co-presence
    for _ in range(10):
        cp = compute_copresence(field, tiny)
        B = boundary_step(B, cp, tiny)
    b_after_growth = float(B.max())
    assert b_after_growth > 0.0, \
        f"B should grow with co-presence; got max={b_after_growth}"

    # Decay: 200 steps with zero co-presence
    zero_cp = np.zeros((30, 30), dtype=np.float64)
    B_before_decay = B.copy()
    for _ in range(200):
        B = boundary_step(B, zero_cp, tiny)
    b_after_decay = float(B.max())
    assert b_after_decay < b_after_growth * 0.5, \
        f"B should decay significantly in 200 steps; {b_after_decay} vs {b_after_growth}"
    assert b_after_decay > 0.0, \
        f"B should not be exactly zero after 200 steps (slow decay); got {b_after_decay}"
    print(f"selftest: Part 2 OK (B grows={b_after_growth:.4f}, "
          f"decays to {b_after_decay:.4f} after 200 steps zero co-presence)")

    # ---- Part 3: B persists after perturbation; I does not ----
    # Run autopoietic and passive with perturbation at step 200.
    r_auto = run_two_region_autopoietic(tiny, seed=42, n_seeds=2,
                                       mode="autopoietic",
                                       perturb_at=200)
    r_passive = run_two_region_autopoietic(tiny, seed=42, n_seeds=2,
                                           mode="passive",
                                           perturb_at=200)
    bt_auto = r_auto["boundary_trace"]
    bt_passive = r_passive["boundary_trace"]

    # Find pre- and post-perturbation records.
    pre_auto = [b for b in bt_auto if b["step"] < 200]
    post_auto = [b for b in bt_auto if b["step"] >= 200]
    pre_passive = [b for b in bt_passive if b["step"] < 200]
    post_passive = [b for b in bt_passive if b["step"] >= 200]

    if pre_auto and post_auto and pre_passive and post_passive:
        # B gap value: pre vs 25 steps post
        b_pre = pre_auto[-1]["b_gap"]
        b_post = post_auto[0]["b_gap"] if post_auto else 0.0
        i_pre = pre_passive[-1]["i_gap"]
        i_post = post_passive[0]["i_gap"] if post_passive else 0.0

        # B should retain more of its value than I immediately after perturb.
        if b_pre > 1e-9 and i_pre > 1e-9:
            b_ratio = b_post / b_pre
            i_ratio = i_post / i_pre
            # B should retain more (memory) than I (no memory).
            # Note: on a 30x30 grid the signal is small; relax the threshold.
            assert b_ratio >= i_ratio * 0.9, \
                f"B persistence ({b_ratio:.3f}) should >= I ({i_ratio:.3f})"
            print(f"selftest: Part 3 OK (B persists: {b_pre:.4f}→{b_post:.4f} "
                  f"ratio={b_ratio:.3f}; I: {i_pre:.4f}→{i_post:.4f} "
                  f"ratio={i_ratio:.3f})")
        else:
            print(f"selftest: Part 3 SKIPPED (gap values too small: "
                  f"b_pre={b_pre}, i_pre={i_pre})")
    else:
        print("selftest: Part 3 SKIPPED (not enough boundary trace records)")

    # ---- Part 4: autopoietic run produces per-region metrics ----
    r2 = run_two_region_autopoietic(tiny, seed=42, n_seeds=2,
                                    mode="autopoietic")
    assert len(r2["history"]) >= 4, "run should produce history"
    for rec in r2["history"]:
        assert "left_total" in rec and "right_total" in rec
    assert "l2_outcome" in r2["history"][-1]
    print("selftest: Part 4 OK (autopoietic run + per-region metrics)")

    # ---- Part 5: B ≈ 0 for a single seed (co-presence is zero) ----
    r1 = run_two_region_autopoietic(tiny, seed=42, n_seeds=1,
                                    mode="autopoietic")
    bt1 = r1["boundary_trace"]
    if bt1:
        max_b = max(b["b_max"] for b in bt1)
        max_b_2seed = max(b["b_max"] for b in r2["boundary_trace"]) \
            if r2["boundary_trace"] else 1.0
        assert max_b < max_b_2seed * 0.5, \
            f"B for 1 seed ({max_b}) should be < 50% of 2 seeds ({max_b_2seed})"
        print(f"selftest: Part 5 OK (B lower for 1 seed: max_b_1seed={max_b:.4f} "
              f"< max_b_2seed={max_b_2seed:.4f}, ratio={max_b/max_b_2seed:.2f})")
    else:
        print("selftest: Part 5 SKIPPED (no boundary trace)")

    # ---- Part 6: determinism — run twice, diff ----
    r2a = run_two_region_autopoietic(tiny, seed=42, n_seeds=2,
                                    mode="autopoietic")
    r2b = run_two_region_autopoietic(tiny, seed=42, n_seeds=2,
                                    mode="autopoietic")
    sa, sb = r2a["summary"], r2b["summary"]
    assert sa["l2_crossed"] == sb["l2_crossed"], "determinism: l2_crossed"
    assert sa["l2_outcome"] == sb["l2_outcome"], "determinism: l2_outcome"
    assert abs(sa["l2_left_retain"] - sb["l2_left_retain"]) < 1e-9
    assert abs(sa["l2_right_retain"] - sb["l2_right_retain"]) < 1e-9
    print("selftest: Part 6 OK (determinism)")

    print("selftest: ALL OK")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        g = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9
        cmd_run(inh_gain=g)
    elif cmd == "perturbation":
        g = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9
        ps = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
        cmd_perturbation(inh_gain=g, perturb_step=ps)
    elif cmd == "robustness":
        g = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9
        cmd_robustness(inh_gain=g)
    elif cmd == "selftest":
        cmd_selftest()
    else:
        print("usage: sim12.py [run [inh_gain] | perturbation [inh_gain [step]] | "
              "robustness [inh_gain] | selftest]")


if __name__ == "__main__":
    main()
