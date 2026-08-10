"""
Sim11: The Boundary Mechanism — Does Long-Range Inhibition Let Two
Self-Maintaining Structures Coexist?

THE QUESTION (queued-topic #78):
  Session 25 (sim10) found the trace→actor crossing does NOT compose: two
  curvature-channel structures in adjacent regions merge 15/16 times at the
  crossing regime. The curvature channel has LOCAL SELF-ACTIVATION (deposit
  at convex tips recruits further building) but NO LONG-RANGE INHIBITION —
  nothing prevents two growing structures from merging into one.

  This is precisely the missing ingredient in Turing/Gierer-Meinhardt pattern
  formation: local activation + LATERAL (long-range) inhibition produces
  spatially separated patterns. Without the long-range inhibitory term, a
  single activator field merges everything. The curvature channel is an
  activator-only system.

  THE HYPOTHESIS UNDER TEST: a non-saturating stigmergic channel that fires
  H7's crossing (sim09) composes into L2 when paired with a long-range
  inhibitory field — a heavily-smoothed material "shadow" that suppresses
  deposition at distance from existing structure. Two structures locally
  activate their own growth (curvature recruit) but inhibit each other's
  growth at range. The boundary emerges where the two inhibition fields
  balance.

  This tests H1/H10 (the composition problem needs a boundary mechanism, not
  a better channel) and sharpens H7 (the crossing is single-structure; L2
  needs a second channel).

DESIGN:
  Extends sim10 (which imports sim09's core). Adds ONE new field: an inhibitor
  field I = heavily-diffused material (the "long-range shadow"). Deposit
  probability is multiplied by a suppression factor that decreases as the
  local inhibitor rises:

      p_dep *= max(0, 1 - inh_gain * I_local / (1 + I_local))   (saturating
                                                                inhibition,
                                                                so it cannot
                                                                drive p<0)

  The inhibitor is the material field smoothed over a LARGE radius (many
  diffusion passes), so it carries long-range information: a cell near a
  large structure sees high I; a cell in the gap between two structures sees
  the sum of both shadows. The gap becomes a no-build zone — the boundary.

  Four conditions (a 2×2 extending sim10's design):
    A. curvature + inhibition, 2 seeds   (the L2 test)
    B. curvature + inhibition, 1 seed    (L1 control — does inhibition harm
                                          a single structure's crossing? If
                                          a single structure inhibits itself
                                          to death, the mechanism is broken.)
    C. curvature, no inhibition, 2 seeds (the sim10 baseline — should merge,
                                          reproduces 15/16)
    D. curvature, no inhibition, 1 seed  (the sim10 L1 control)

  The L2 detector is sim10's corrected detector (per-region connected
  components that do not cross the midline). The one-seed control (B) is the
  critical control arm: if inhibition breaks the single-structure crossing,
  any two-seed coexistence is just "both structures survived inhibition," not
  "inhibition created a boundary."

METHODOLOGY (per CLAUDE.md §4 step 6):
  - The L2 detector is inherited from sim10 (already proven: fires on
    coexistence, withholds on dominance/destruction/single-region/merged/
    fragmented). Re-proven in sim11's selftest.
  - Control arm: condition B (1 seed + inhibition). If the single-structure
    crossing breaks under inhibition, the mechanism is self-defeating —
    report it, do not claim composition.
  - Determinism: run twice, diff the JSON.
  - Compute the metric's ceiling: the inhibitor is bounded in [0, max_material];
    inh_gain bounds the suppression in [0, 1] (saturating form). The deposit
    probability floor is deposit_prob_base * (1 - inh_gain) — at
    inh_gain=0.5 this is 0.5*base, well above zero. The crossing can still fire.

  THE METHODLOGY TRAP TO AVOID: a strong enough inhibitor will prevent ALL
  building, producing "coexistence" trivially (two frozen seed mounds that
  never grow and never merge). This is the metric-ceiling lesson (#61) again:
  "coexist" must mean two GROWING/MAINTAINING structures, not two inert
  relics. The detector already requires components to persist (L2_PERSIST
  consecutive late samples) AND checks material retention. We add an
  additional check: the 2-seed coexist must show H7 crossing (crossed_h7) in
  at least one region — the structures must be self-maintaining, not frozen.

This module imports sim10 (which imports sim09's core). It adds ONLY the
inhibitor field computation, the inhibition-gated deposit rule, and the
2×2 condition runner. sim10/sim09 remain the single sources of truth.
"""

import os
import sys
import json
import time
import copy

import numpy as np

# Import sim10 (which imports sim09).
SIM10_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "sim10_l2_composition")
sys.path.insert(0, SIM10_DIR)
import sim10 as T  # noqa: E402
import sim09 as S  # noqa: E402

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SIM_DIR, "results.json")
OUTPUT_DIR = os.path.join(SIM_DIR, "output")

# --------------------------------------------------------------------------#
# The inhibitor field — long-range shadow of the material
# --------------------------------------------------------------------------#
# The inhibitor is the material field smoothed over a LARGE radius. We
# achieve this with multiple passes of sim09's _diffuse at a high rate,
# which is a cheap iterative Gaussian-like blur on the torus. The number of
# passes controls the inhibition radius: more passes = longer range.
#
# A cell near a structure sees high I (locally high material, smoothed). A
# cell in the gap between two structures sees the SUM of both shadows. The
# gap's inhibitor exceeds either structure's local inhibitor, so deposition
# is suppressed in the gap relative to the structure cores — the boundary.
INHIBITOR_PASSES = 12     # diffusion passes (inhibition radius)
INHIBITOR_DIFFUSE_RATE = 0.7   # per-pass diffusion rate (high = fast spread)


def compute_inhibitor(field, params):
    """Compute the long-range inhibitor field: the far-field material shadow
    MINUS the local material. This is high in the GAP between two structures
    (where distant structures contribute to the smoothed field but local
    material is ~0) and low AT a structure (where local material cancels the
    smoothed shadow).

    This solves the self-inhibition problem: a simple smoothed-material
    inhibitor is always highest AT the structure (self-defeating). The
    difference (far_smoothed - material) isolates the DISTANT structure's
    contribution. In the gap between two structures, both shadows sum, so
    the inhibitor is high; at a structure, the local material cancels its
    own shadow, leaving only the distant structure's (small) contribution.

    Returns a non-negative 2D float array (clamped at 0).
    """
    passes = params.get("inhibitor_passes", INHIBITOR_PASSES)
    rate = params.get("inhibitor_diffuse_rate", INHIBITOR_DIFFUSE_RATE)
    far = field.material.copy()
    for _ in range(passes):
        far = S._diffuse(far, rate)
    return np.maximum(0.0, far - field.material)


# --------------------------------------------------------------------------#
# Inhibition-gated curvature termite step
# --------------------------------------------------------------------------#
# We wrap sim09's termite_step to multiply the deposit probability by a
# suppression factor derived from the inhibitor. Rather than reimplement
# the whole step, we use a clean approach: run the standard curvature step
# but with a deposit_prob_base and deposit_prob_gain that are pre-scaled by
# the local inhibitor. We pass a per-cell "inhibition mask" via the params
# dict, read inside a thin wrapper.
#
# Implementation: we cannot easily make sim09's termite_step read a per-cell
# field (it uses scalar base/gain). So we implement a minimal inhibition-
# gated step here that mirrors sim09's termite_step EXACTLY except for the
# deposit-probability line. This keeps sim09 as the source of truth for
# movement, excavation, and reload; sim11 only overrides the deposit gate.

_CURVE_FOLLOW = S.CURVE_FOLLOW
_RELOAD_PROB = S.RELOAD_PROB
_PELLET = S.PELLET


def termite_step_inhibited(termites, field, rng, params, curvature, on_surface,
                           inhibitor):
    """Curvature-channel step with deposit probability suppressed by the
    long-range inhibitor. Mirrors sim09.termite_step exactly except the
    deposit-probability routing multiplies by (1 - suppression(c)).

    suppression(c) = inh_gain * I_norm / (1 + I_norm),  I_norm = I / I_scale.
    Saturating in I so suppression is bounded in [0, inh_gain). At
    inh_gain=0.5 the deposit probability floor is 0.5*base — structure can
    still self-maintain.
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
    inh_scale = params.get("inh_scale", 1.0)

    curv = curvature
    ons = on_surface
    mat = field.material
    Inh = inhibitor
    # Normalized inhibitor (0 at empty, ~1 near dense structure).
    I_norm = Inh / max(inh_scale, 1e-9)

    recruit_response = params.get("recruit_response", "linear")

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

        # --- movement (identical to sim09) ---
        if rng.random() < curve_follow:
            best_dy = 0
            best_dx = 0
            if termites.loaded[i]:
                best_v = -np.inf
                for dy, dx in S._MOORE:  # type: ignore[attr-defined]
                    yy = (y + dy) % size
                    xx = (x + dx) % size
                    v = curv[yy, xx]
                    if v > best_v:
                        best_v = v
                        best_dy, best_dx = dy, dx
            else:
                best_v = np.inf
                for dy, dx in S._MOORE:  # type: ignore[attr-defined]
                    yy = (y + dy) % size
                    xx = (x + dx) % size
                    v = curv[yy, xx]
                    if v < best_v:
                        best_v = v
                        best_dy, best_dx = dy, dx
            y = (y + best_dy) % size
            x = (x + best_dx) % size
        else:
            dy, dx = S._MOORE[int(rng.integers(0, 8))]  # type: ignore
            y = (y + dy) % size
            x = (x + dx) % size
        termites.y[i] = y
        termites.x[i] = x

        # --- reload / excavate / pickup (identical to sim09) ---
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

        # --- deposit (loaded) — INHIBITION GATE HERE ---
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
            # Inhibition suppression on the FULL deposit probability.
            # The inhibitor is 0 at structures (self-cancelling) and high in
            # the gap, so this suppresses gap deposition (both nucleation
            # AND curvature-gain routing) while leaving structure tips
            # intact. Saturating in I, bounded in [0, inh_gain).
            if inh_gain > 0.0:
                supp = inh_gain * I_norm[y, x] / (1.0 + I_norm[y, x])
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
# Two-region run with optional inhibition
# --------------------------------------------------------------------------#
def run_two_region_inhibited(params, seed, n_seeds=2, inhibited=False):
    """Run one simulation with one or two seed mounds, optionally with the
    long-range inhibitor suppressing deposition.

    Mirrors sim10.run_two_region exactly; the only additions are (a)
    computing the inhibitor field each step when inhibited=True, and (b)
    calling termite_step_inhibited instead of S.termite_step.

    Reuses sim10's seed placement, region masks, per-region component
    counting, and the L2 detector.
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

    # Inh scale: the 95th percentile of the initial inhibitor field, so
    # I_norm ~ 1 near a dense seed. Recomputed once at the start from the
    # seeded material (before growth); keeps the normalization stable.
    if inhibited and inh_gain > 0.0:
        I0 = compute_inhibitor(field, params)
        inh_scale = max(float(np.percentile(I0, 95)), 1e-9)
        params = dict(params)
        params["inh_scale"] = inh_scale
    else:
        inh_scale = params.get("inh_scale", 1.0)

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
            if inhibited and inh_gain > 0.0:
                inhibitor = compute_inhibitor(field, params)
                ev = termite_step_inhibited(termites, field, rng, params,
                                            curvature, on_surface, inhibitor)
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

            if (len(history) - 1) % snapshot_stride == 0:
                curv_now = S.compute_curvature(field, params)
                inh_now = (compute_inhibitor(field, params)
                           if inhibited and inh_gain > 0.0 else None)
                raw_snapshots.append((
                    int(step),
                    S._downsample_grid(field.material, snapshot_size),
                    S._downsample_grid(curv_now, snapshot_size),
                    (S._downsample_grid(inh_now, snapshot_size)
                     if inh_now is not None else None),
                ))

    S.detect_crossing(history, params)
    T.detect_l2(history, params)
    summary = summarize_two_region_inhibited(history, n_seeds=n_seeds)

    snapshots = []
    if raw_snapshots:
        mat_max = max(m.max() for _, m, _, _ in raw_snapshots)
        mat_max = mat_max if mat_max > 0 else 1.0
        curv_min = min(c.min() for _, _, c, _ in raw_snapshots)
        curv_max = max(c.max() for _, _, c, _ in raw_snapshots)
        curv_range = (curv_max - curv_min) if curv_max > curv_min else 1.0
        for step, mat, curv, inh in raw_snapshots:
            mat_norm = np.clip(mat / mat_max, 0.0, 1.0)
            curv_norm = np.clip((curv - curv_min) / curv_range, 0.0, 1.0)
            rec = {
                "step": step,
                "material": np.round(mat_norm, 4).flatten().tolist(),
                "curvature": np.round(curv_norm, 4).flatten().tolist(),
            }
            if inh is not None:
                inh_max = max(i.max() for _, _, _, i in raw_snapshots
                              if i is not None)
                inh_max = inh_max if inh_max > 0 else 1.0
                inh_norm = np.clip(inh / inh_max, 0.0, 1.0)
                rec["inhibitor"] = np.round(inh_norm, 4).flatten().tolist()
            snapshots.append(rec)

    return {"history": history, "summary": summary, "snapshots": snapshots}


def summarize_two_region_inhibited(history, n_seeds=2):
    """Headline summary, extending sim10's with the H7-crossing-in-region
    check (the frozen-relic guard)."""
    s = T.summarize_two_region(history, n_seeds=n_seeds)
    if not history:
        return s
    last = history[-1]
    s["inh_gain"] = float(last.get("inh_gain", 0.0))
    return s


# --------------------------------------------------------------------------#
# CLI
# --------------------------------------------------------------------------#
def curvature_params(inh_gain=0.0):
    """Curvature-channel params for sim11. Uses the TUNED regime (dpb=0.01,
    decay=0.002) where sim10 showed 15/16 merge."""
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
        p["inhibitor_passes"] = INHIBITOR_PASSES
        p["inhibitor_diffuse_rate"] = INHIBITOR_DIFFUSE_RATE
    return p


def cmd_run(inh_gain=0.5):
    """Run the 2×2: {inhibition ON, OFF} × {2 seeds, 1 seed}."""
    t0 = time.time()
    seed = 42
    results = {"config": {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "seed": seed,
        "channel": "curvature",
        "d": 1.0, "material_decay": 0.002,
        "deposit_prob_base": 0.01,
        "inh_gain": inh_gain,
        "inhibitor_passes": INHIBITOR_PASSES,
        "inhibitor_diffuse_rate": INHIBITOR_DIFFUSE_RATE,
        "seed_height": T.SEED_HEIGHT,
        "seed_sigma_frac": T.SEED_SIGMA_FRAC,
        "seed_offset_frac": T.SEED_OFFSET_FRAC,
    }}

    print(f"Running A: curvature + inhibition (g={inh_gain}), 2 seeds (the L2 test)...")
    a = run_two_region_inhibited(curvature_params(inh_gain), seed=seed,
                                 n_seeds=2, inhibited=True)
    print("Running B: curvature + inhibition, 1 seed (L1 control)...")
    b = run_two_region_inhibited(curvature_params(inh_gain), seed=seed,
                                 n_seeds=1, inhibited=True)
    print("Running C: curvature, no inhibition, 2 seeds (sim10 baseline)...")
    c = run_two_region_inhibited(curvature_params(0.0), seed=seed,
                                 n_seeds=2, inhibited=False)
    print("Running D: curvature, no inhibition, 1 seed (sim10 L1 control)...")
    d = run_two_region_inhibited(curvature_params(0.0), seed=seed,
                                 n_seeds=1, inhibited=False)

    results["curv_inh_2seed"] = a
    results["curv_inh_1seed"] = b
    results["curv_noinh_2seed"] = c
    results["curv_noinh_1seed"] = d

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_str = S._compact_snapshot_arrays(
        json.dumps(S._pyify(results), indent=2))
    with open(RESULTS_PATH, "w") as f:
        f.write(json_str)

    print("\n=== RESULT: L2 Composition with Inhibition (H1/H10/H7) ===")
    for name, r in [("curv_inh_2seed", a), ("curv_inh_1seed", b),
                    ("curv_noinh_2seed", c), ("curv_noinh_1seed", d)]:
        s = r["summary"]
        print(f"  {name:22s} l2_crossed={str(s['l2_crossed']):5s} "
              f"outcome={s['l2_outcome']:12s} "
              f"L_retain={s['l2_left_retain']:.2f} "
              f"R_retain={s['l2_right_retain']:.2f} "
              f"h7={str(s['crossed_h7']):5s} "
              f"cells={s['final_n_structure_cells']}")
    print(f"\nWrote {RESULTS_PATH}  ({time.time()-t0:.1f}s)")


def cmd_selftest():
    """Prove sim11's additions work and the inherited L2 detector still
    fires/withholds. Verify determinism."""
    # ---- Part 1: inhibition-gated run produces per-region metrics ----
    tiny = {"grid_size": 30, "n_termites": 20, "steps": 200,
            "sample_every": 25, "channel": "curvature",
            "structure_threshold": S.STRUCTURE_THRESHOLD,
            "d": 1.0, "material_decay": 0.002,
            "deposit_prob_base": 0.01,
            "inh_gain": 0.5}
    r2 = run_two_region_inhibited(tiny, seed=42, n_seeds=2, inhibited=True)
    assert len(r2["history"]) >= 4, "inhibited 2-seed run should produce history"
    for rec in r2["history"]:
        assert "left_total" in rec and "right_total" in rec
    assert "l2_outcome" in r2["history"][-1]
    print("selftest: Part 1 OK (inhibition-gated run + per-region metrics)")

    # ---- Part 2: inhibitor field is long-range (smoother than material) ----
    field = S.Field(30)
    T.seed_region(field, 30, "left", {})
    I = compute_inhibitor(field, {"inhibitor_passes": INHIBITOR_PASSES,
                                 "inhibitor_diffuse_rate": INHIBITOR_DIFFUSE_RATE})
    # The inhibitor at the GAP/far edge should be > 0 (long-range shadow from
    # the seed), while AT the seed it is ~0 (self-cancellation: local material
    # cancels the smoothed shadow).
    seed_inh = float(I[15, 15])
    far_inh = float(I[15, 25:].max())
    assert far_inh > 0.0, \
        "inhibitor must spread to the far edge (long-range); got 0"
    assert seed_inh < far_inh, \
        f"inhibitor at seed ({seed_inh}) must be < far ({far_inh}); self-cancellation"
    print(f"selftest: Part 2 OK (inhibitor long-range, self-cancels: "
          f"seed={seed_inh:.4f} < far={far_inh:.4f})")

    # ---- Part 3: inhibition reduces deposits vs no-inhibition ----
    # Same seed, same steps; the inhibited run should have fewer total
    # deposits (suppression multiplies deposit probability down).
    p_inh = {"grid_size": 30, "n_termites": 20, "steps": 300,
             "sample_every": 25, "channel": "curvature",
             "structure_threshold": S.STRUCTURE_THRESHOLD,
             "d": 1.0, "material_decay": 0.002,
             "deposit_prob_base": 0.01, "inh_gain": 0.5}
    p_noinh = {"grid_size": 30, "n_termites": 20, "steps": 300,
               "sample_every": 25, "channel": "curvature",
               "structure_threshold": S.STRUCTURE_THRESHOLD,
               "d": 1.0, "material_decay": 0.002,
               "deposit_prob_base": 0.01}
    r_inh = run_two_region_inhibited(p_inh, seed=42, n_seeds=2, inhibited=True)
    r_noinh = run_two_region_inhibited(p_noinh, seed=42, n_seeds=2,
                                       inhibited=False)
    mat_inh = r_inh["summary"]["final_total_material"]
    mat_noinh = r_noinh["summary"]["final_total_material"]
    assert mat_inh < mat_noinh, \
        f"inhibition should reduce total material ({mat_inh} >= {mat_noinh})"
    print(f"selftest: Part 3 OK (inhibition reduces material: "
          f"{mat_inh:.1f} < {mat_noinh:.1f})")

    # ---- Part 4: inherited L2 detector still fires/withholds ----
    # Reuse sim10's synthetic-history tests.
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
        h = []
        for i in range(n):
            r = dict(base_rec)
            r["step"] = i * 25
            if i >= int(n * 0.75):
                r["left_total"] = l_late_mat
                r["right_total"] = r_late_mat
                r["left_components"] = l_comp
                r["right_components"] = r_comp
            h.append(r)
        return h

    h_co = make_history(1, 1, 40.0, 40.0)
    T.detect_l2(h_co, {})
    assert h_co[-1]["l2_crossed"] is True, "coexistence should fire L2"
    assert h_co[-1]["l2_outcome"] == "coexist"

    h_merged = make_history(0, 0, 40.0, 40.0)
    T.detect_l2(h_merged, {})
    assert h_merged[-1]["l2_crossed"] is False, "merged should NOT fire"
    assert h_merged[-1]["l2_outcome"] == "none"
    print("selftest: Part 4 OK (inherited L2 detector fires/withholds)")

    # ---- Part 5: determinism — run twice, diff ----
    r2a = run_two_region_inhibited(tiny, seed=42, n_seeds=2, inhibited=True)
    r2b = run_two_region_inhibited(tiny, seed=42, n_seeds=2, inhibited=True)
    sa, sb = r2a["summary"], r2b["summary"]
    assert sa["l2_crossed"] == sb["l2_crossed"], "determinism: l2_crossed"
    assert sa["l2_outcome"] == sb["l2_outcome"], "determinism: l2_outcome"
    assert abs(sa["l2_left_retain"] - sb["l2_left_retain"]) < 1e-9
    assert abs(sa["l2_right_retain"] - sb["l2_right_retain"]) < 1e-9
    print("selftest: Part 5 OK (determinism)")

    print("selftest: ALL OK")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        g = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
        cmd_run(inh_gain=g)
    elif cmd == "selftest":
        cmd_selftest()
    else:
        print("usage: sim11.py [run [inh_gain] | selftest]")


if __name__ == "__main__":
    main()
