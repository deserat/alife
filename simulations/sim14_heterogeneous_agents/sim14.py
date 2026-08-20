"""
Sim14: Heterogeneous Agent Policies — Agents Tagged with a Structure ID

THE QUESTION (queued-topic #88, #79):
  sim13 ruled out the spatial filter as the cause of false boundaries — agent
  wander on the torus deposits material in both halves, creating real (not
  phantom) co-presence from a single structure. The memory-specificity
  trade-off is a system property, not a signal property.

  The next approach: agents carry a "structure ID" (0 for left, 1 for right).
  Deposits are tagged with the agent's ID. Co-presence checks for material
  from TWO DIFFERENT IDs within a local radius — not just material on both
  sides of the midline. The boundary grows only where two distinct agent
  populations meet.

  The 1-seed control has only ONE ID, so co-presence is ALWAYS zero — the
  boundary cannot grow, regardless of agent wander. This is the critical
  test: does agent-level tagging break the memory-specificity trade-off?

DESIGN:
  Each termite has an `id` (0 or 1). Material is tracked in two arrays:
    material_by_id[0]  — material deposited by left agents
    material_by_id[1]  — material deposited by right agents
    field.material     — the total (sum), for compatibility with sim09

  When a termite with id=k deposits: material_by_id[k] += pellet.
  When excavating: remove proportionally from both arrays.
  Decay: all three arrays decay at the same rate.

  Co-presence = min(dilate(material_by_id[0]), dilate(material_by_id[1]))
  using sim13's max-filter dilation (no x-wrapping). High only where BOTH
  IDs have material nearby. For a single seed (all agents id=0),
  material_by_id[1] is zero everywhere → co-presence = 0 → B = 0.

  B's growth/decay dynamics are IDENTICAL to sim12:
    B_new = B * (1 - b_decay) + b_growth * co_presence
  The boundary suppression is IDENTICAL to sim12:
    p_dep *= (1 - g * B_norm / (1 + B_norm))

  KEY PREDICTION: the 1-seed control fires 0/4 (co-presence is structurally
  zero — no spatial filter can achieve this). If the 2-seed case coexists
  at >= 2/4, agent tagging breaks the trade-off.

SIX CONDITIONS (same as sim12/sim13):
  A: heterogeneous autopoietic boundary, 2 seeds (the L2 test)
  B: heterogeneous autopoietic boundary, 1 seed (L1 control — MUST be 0)
  C: passive inhibitor (sim11's I), 2 seeds (direct comparison)
  D: passive inhibitor (sim11's I), 1 seed (passive L1 control)
  E: no inhibition, 2 seeds (sim10 baseline — should merge)
  F: no inhibition, 1 seed (sim10 L1 control)
  G: shadow autopoietic (sim12), 2 seeds (comparison — no ID tagging)
  H: shadow autopoietic (sim12), 1 seed (comparison control)

METHODOLOGY (per CLAUDE.md §4 step 6):
  - Self-test proves ID co-presence is high for 2 seeds, ZERO for 1 seed
    (the key structural guarantee), B grows/decays, B ≈ 0 for 1 seed.
  - Control arms: 1-seed controls, passive inhibitor, no inhibition, AND
    sim12's shadow version (no ID tagging — direct comparison).
  - Determinism: run twice, diff the JSON.
  - Compute the metric's ceiling: co_presence bounded by max(material_by_id);
    B bounded by b_growth * max(co_presence) / b_decay.

This module imports sim12 (which imports sim11/sim10/sim09). It overrides the
co-presence computation, termite step, and field step. sim12/sim11/sim10/sim09
remain the single sources of truth.
"""

import os
import sys
import json
import time

import numpy as np

# Import sim13 (which imports sim12, sim11, sim10, sim09).
SIM13_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "sim13_direct_copresence")
sys.path.insert(0, SIM13_DIR)
import sim13 as I13  # noqa: E402
import sim12 as I12  # noqa: E402
import sim11 as I11  # noqa: E402
import sim10 as T    # noqa: E402
import sim09 as S    # noqa: E402

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SIM_DIR, "results.json")
OUTPUT_DIR = os.path.join(SIM_DIR, "output")

DIRECT_RADIUS = 8  # default max-filter radius for ID co-presence

# --------------------------------------------------------------------------#
# Heterogeneous termites — each agent has a structure ID
# --------------------------------------------------------------------------#
class HeteroTermites:
    """Termites with a structure_id (0 for left, 1 for right).

    First n//2 agents get id=0 (left), rest get id=1 (right). For 1-seed
    control, ALL agents get id=0.
    """

    def __init__(self, n, size, rng, n_ids=2):
        self.n = n
        self.size = size
        self.x = rng.integers(0, size, n)
        self.y = rng.integers(0, size, n)
        self.loaded = np.zeros(n, dtype=bool)
        if n_ids == 1:
            self.id = np.zeros(n, dtype=np.int8)
        else:
            half = n // 2
            self.id = np.zeros(n, dtype=np.int8)
            self.id[half:] = 1


# --------------------------------------------------------------------------#
# ID-based co-presence — min(dilate(mat_id0), dilate(mat_id1))
# --------------------------------------------------------------------------#
def compute_id_copresence(material_by_id, params):
    """Co-presence from two ID-tagged material arrays.

    Dilate each ID's material (max filter, no x-wrapping) and take the
    element-wise minimum. High only where BOTH IDs have material nearby.

    For a single seed (only id=0 material): material_by_id[1] is zero,
    its dilation is zero, and co-presence = min(anything, 0) = 0.
    This is a STRUCTURAL zero — no spatial filter can break it.
    """
    radius = params.get("direct_radius", DIRECT_RADIUS)
    left_dil = I13._dilate_no_x_wrap(material_by_id[0], radius)
    right_dil = I13._dilate_no_x_wrap(material_by_id[1], radius)
    return np.minimum(left_dil, right_dil)


# --------------------------------------------------------------------------#
# Heterogeneous termite step — deposits tagged by agent ID
# --------------------------------------------------------------------------#
_CURVE_FOLLOW = S.CURVE_FOLLOW
_RELOAD_PROB = S.RELOAD_PROB
_PELLET = S.PELLET


def termite_step_hetero(termites, field, rng, params, curvature,
                         on_surface, B, b_scale, material_by_id):
    """Curvature-channel step with ID-tagged deposits and B suppression.

    Mirrors sim12's termite_step_autopoietic exactly, except:
    - Deposits go into material_by_id[agent.id] as well as field.material
    - Excavations/pickups remove proportionally from both ID arrays
    - Movement bias: when not curvature-following, agents with movement_bias>0
      step toward their home region center (id=0 → left half, id=1 → right half).
      This concentrates each ID's material, reducing boundary fragmentation
      (queued-topic #93).
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
    movement_bias = params.get("movement_bias", 0.0)

    # Home centers for each ID (used for movement bias).
    mid = size // 2
    home_x = [mid // 2, mid + mid // 2]  # id=0 → left center, id=1 → right center

    curv = curvature
    ons = on_surface
    mat = field.material

    # Compute B_norm for boundary suppression.
    # Dual mode uses two B fields (tuple); other modes use one.
    boundary_mode = params.get("boundary_mode", "proportional")
    if boundary_mode == "dual":
        B_form, B_persist = B
        b_scale_form, b_scale_persist = b_scale
        Bf_norm = B_form / max(b_scale_form, 1e-9)
        Bp_norm = B_persist / max(b_scale_persist, 1e-9)
    else:
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
        aid = int(termites.id[i])

        # --- movement (identical to sim09/sim11/sim12) ---
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
            if movement_bias > 0.0 and rng.random() < movement_bias:
                # Biased step: move toward home region center.
                hx = home_x[aid]
                # Shortest toroidal distance in x.
                dx_h = ((hx - x + size // 2) % size) - size // 2
                # Step in x toward home (dx = sign(dx_h), dy = 0).
                dx_step = 1 if dx_h > 0 else (-1 if dx_h < 0 else 0)
                dy_step = int(rng.choice([-1, 0, 1]))
                y = (y + dy_step) % size
                x = (x + dx_step) % size
            else:
                dy, dx = S._MOORE[int(rng.integers(0, 8))]
                y = (y + dy) % size
                x = (x + dx) % size
        termites.y[i] = y
        termites.x[i] = x

        # --- reload / excavate / pickup ---
        if not termites.loaded[i]:
            if rng.random() < reload_prob:
                termites.loaded[i] = True
            elif mat[y, x] > 0:
                c = curv[y, x]
                if c < 0:
                    p_exc = min(max(_route(excavate_prob_base,
                                           excavate_prob_gain, -c), 0.0), 1.0)
                    if rng.random() < p_exc:
                        remove = min(pellet, mat[y, x])
                        _remove_material(material_by_id, mat, y, x, remove)
                        termites.loaded[i] = True
                        excavations += 1
                else:
                    if rng.random() < pickup_prob_base:
                        remove = min(pellet, mat[y, x])
                        _remove_material(material_by_id, mat, y, x, remove)
                        termites.loaded[i] = True
                        pickups += 1

        # --- deposit (loaded) — BOUNDARY GATE ---
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
                bm = params.get("boundary_mode", "proportional")
                if bm == "dual":
                    # Two separate B fields: gradient formation + binary
                    # persistence.  Tests whether the two-wire principle
                    # requires truly separate channels (queued-topic #101).
                    g_form = params.get("g_form", 0.3)
                    g_persist = params.get("g_persist", 0.5)
                    grad_supp = g_form * Bf_norm[y, x] / (
                        1.0 + Bf_norm[y, x])
                    bin_supp = (g_persist if Bp_norm[y, x] > 0.01
                                else 0.0)
                    supp = min(grad_supp + bin_supp, 0.99)
                elif bm == "decoupled":
                    # Fixed suppression wherever B exists (B_norm > threshold).
                    # Decouples suppression strength from co-presence magnitude.
                    supp = inh_gain if B_norm[y, x] > 0.01 else 0.0
                elif bm == "hybrid":
                    # Gradient at low B_norm (wide coverage for formation),
                    # capped at g*k plateau (stability without full-strength
                    # binary gate).  supp = min(g * Bn/(1+Bn), g * k)
                    hybrid_k = params.get("hybrid_k", 0.8)
                    grad = inh_gain * B_norm[y, x] / (1.0 + B_norm[y, x])
                    supp = min(grad, inh_gain * hybrid_k)
                else:
                    # Proportional suppression (original sim12/sim14 behavior).
                    supp = inh_gain * B_norm[y, x] / (1.0 + B_norm[y, x])
                p_dep = p_dep * (1.0 - supp)
            p_dep = min(max(p_dep, 0.0), 1.0)
            if rng.random() < p_dep:
                mat[y, x] += pellet
                material_by_id[aid][y, x] += pellet
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


def _remove_material(material_by_id, mat, y, x, amount):
    """Remove material proportionally from both ID arrays and the total."""
    m0 = material_by_id[0][y, x]
    m1 = material_by_id[1][y, x]
    total = m0 + m1
    if total <= 0:
        return
    frac = min(amount / total, 1.0)
    material_by_id[0][y, x] = max(0.0, m0 * (1.0 - frac))
    material_by_id[1][y, x] = max(0.0, m1 * (1.0 - frac))
    mat[y, x] = max(0.0, mat[y, x] - amount)


# --------------------------------------------------------------------------#
# Field step with ID tracking — decay all three arrays
# --------------------------------------------------------------------------#
def field_step_hetero(field, material_by_id, params):
    """Apply material decay to field.material and both ID arrays."""
    decay = params.get("material_decay", S.MATERIAL_DECAY)
    field.material *= (1.0 - decay)
    material_by_id[0] *= (1.0 - decay)
    material_by_id[1] *= (1.0 - decay)
    if field.pheromone is not None:
        field.pheromone *= (1.0 - params.get("phero_decay", S.PHERO_DECAY))
        diff = params.get("phero_diffuse", S.PHERO_DIFFUSE)
        field.pheromone = S._diffuse(field.pheromone, diff)


# --------------------------------------------------------------------------#
# Two-region run with heterogeneous agents
# --------------------------------------------------------------------------#
def run_two_region_hetero(params, seed, n_seeds=2, mode="hetero",
                            perturb_at=None, perturb_frac=0.5):
    """Run one simulation with ID-tagged agents.

    mode = "hetero"  → ID-tagged autopoietic boundary (the new test)
    mode = "shadow"  → sim12's diffused-shadow (no ID tagging, for comparison)
    mode = "passive" → sim11's passive inhibitor (no ID tagging)
    mode = "none"    → no inhibition (sim10 baseline)
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

    # Initialize ID-tagged material arrays.
    material_by_id = [
        field.material.copy(),  # id=0 (left)
        np.zeros_like(field.material),  # id=1 (right)
    ]
    # If 2 seeds, assign the right seed's material to id=1.
    if n_seeds >= 2:
        mid = size // 2
        material_by_id[1][:, mid:] = field.material[:, mid:].copy()
        material_by_id[0][:, mid:] = 0.0

    # Initialize the boundary field B.
    B = np.zeros((size, size), dtype=np.float64)
    b_scale = 1.0
    # Dual mode: separate B fields for formation (gradient) and persistence (binary).
    B_form = None
    B_persist = None
    b_scale_form = 1.0
    b_scale_persist = 1.0
    is_dual = params.get("boundary_mode") == "dual"

    # For passive mode, we need sim11's inhibitor scale.
    inh_scale = 1.0
    if mode == "passive" and inh_gain > 0.0:
        I0 = I11.compute_inhibitor(field, params)
        inh_scale = max(float(np.percentile(I0, 95)), 1e-9)
        params = dict(params)
        params["inh_scale"] = inh_scale

    # For hetero mode, compute the initial ID co-presence to set b_scale.
    if mode == "hetero" and inh_gain > 0.0:
        cp0 = compute_id_copresence(material_by_id, params)
        b_scale = max(float(np.percentile(cp0, 95)), 1e-9)
        if is_dual:
            B_form = np.zeros((size, size), dtype=np.float64)
            B_persist = np.zeros((size, size), dtype=np.float64)
            b_scale_form = b_scale
            b_scale_persist = b_scale

    # For shadow mode, use sim12's co-presence scale.
    if mode == "shadow" and inh_gain > 0.0:
        cp0 = I12.compute_copresence(field, params)
        b_scale = max(float(np.percentile(cp0, 95)), 1e-9)

    # Create termites.
    if mode == "hetero":
        termites = HeteroTermites(n, size, rng, n_ids=n_seeds)
    else:
        termites = S.Termites(n, size, rng)

    history = []
    dep_acc = exc_acc = dep_convex_acc = dep_struct_acc = pick_acc = 0
    prev_structure_mask = None

    snapshot_size = params.get("snapshot_size", S.SNAPSHOT_SIZE)
    expected_records = max(1, (steps + sample - 1) // sample)
    snapshot_stride = max(1, round(expected_records / S.SNAPSHOT_TARGET_COUNT))
    raw_snapshots = []
    boundary_trace = []

    for step in range(steps):
        # --- perturbation ---
        if perturb_at is not None and step == perturb_at:
            right_material = field.material[right_mask]
            field.material[right_mask] = right_material * (1.0 - perturb_frac)
            material_by_id[1][right_mask] *= (1.0 - perturb_frac)

        if channel == "curvature":
            curvature = S.compute_curvature(field, params)
            on_surface = S.compute_on_surface(field, params)

            if mode == "hetero" and inh_gain > 0.0:
                cp = compute_id_copresence(material_by_id, params)
                if is_dual:
                    # Update two B fields with separate growth/decay dynamics.
                    p_f = dict(params)
                    p_f["boundary_growth"] = params.get(
                        "b_growth_form", I12.BOUNDARY_GROWTH)
                    p_f["boundary_decay"] = params.get(
                        "b_decay_form", I12.BOUNDARY_DECAY * 2.0)
                    p_p = dict(params)
                    p_p["boundary_growth"] = params.get(
                        "b_growth_persist", I12.BOUNDARY_GROWTH)
                    p_p["boundary_decay"] = params.get(
                        "b_decay_persist", I12.BOUNDARY_DECAY)
                    B_form = I12.boundary_step(B_form, cp, p_f)
                    B_persist = I12.boundary_step(B_persist, cp, p_p)
                    ev = termite_step_hetero(
                        termites, field, rng, params, curvature,
                        on_surface, (B_form, B_persist),
                        (b_scale_form, b_scale_persist), material_by_id)
                else:
                    B = I12.boundary_step(B, cp, params)
                    ev = termite_step_hetero(termites, field, rng, params,
                                             curvature, on_surface, B, b_scale,
                                             material_by_id)
            elif mode == "shadow" and inh_gain > 0.0:
                cp = I12.compute_copresence(field, params)
                B = I12.boundary_step(B, cp, params)
                ev = I12.termite_step_autopoietic(termites, field, rng,
                                                  params, curvature,
                                                  on_surface, B, b_scale)
            elif mode == "passive" and inh_gain > 0.0:
                inhibitor = I11.compute_inhibitor(field, params)
                ev = I11.termite_step_inhibited(termites, field, rng,
                                               params, curvature,
                                               on_surface, inhibitor)
            else:
                ev = S.termite_step(termites, field, rng, params,
                                    curvature, on_surface)

            if mode == "hetero":
                field_step_hetero(field, material_by_id, params)
            else:
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
            # Track ID-specific material for diagnostics.
            rec["id0_total"] = float(material_by_id[0].sum())
            rec["id1_total"] = float(material_by_id[1].sum())
            history.append(rec)
            dep_acc = exc_acc = dep_convex_acc = dep_struct_acc = pick_acc = 0
            prev_structure_mask = (field.material >
                                    params.get("structure_threshold",
                                               S.STRUCTURE_THRESHOLD)).copy()

            # Boundary trace.
            if mode in ("hetero", "shadow") and inh_gain > 0.0:
                if is_dual and B_form is not None:
                    b_max = float(max(B_form.max(), B_persist.max()))
                    b_gap = float(max(B_form[size // 2, size // 2],
                                      B_persist[size // 2, size // 2]))
                else:
                    b_max = float(B.max())
                    b_gap = float(B[size // 2, size // 2])
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
                    (S._downsample_grid(
                         np.maximum(B_form, B_persist)
                         if is_dual and B_form is not None else B,
                         snapshot_size)
                     if mode in ("hetero", "shadow") and inh_gain > 0.0
                     else None),
                ))

    S.detect_crossing(history, params)
    T.detect_l2(history, params)
    summary = T.summarize_two_region(history, n_seeds=n_seeds)

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


# --------------------------------------------------------------------------#
# CLI
# --------------------------------------------------------------------------#
def curvature_params(inh_gain=0.0):
    """Curvature-channel params for sim14. Same tuned regime as sim12/sim13."""
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
        p["direct_radius"] = DIRECT_RADIUS
        p["boundary_growth"] = I12.BOUNDARY_GROWTH
        p["boundary_decay"] = I12.BOUNDARY_DECAY
        p["copresence_passes"] = I12.COPRESENCE_PASSES
        p["copresence_diffuse_rate"] = I12.COPRESENCE_DIFFUSE_RATE
        p["inhibitor_passes"] = I11.INHIBITOR_PASSES
        p["inhibitor_diffuse_rate"] = I11.INHIBITOR_DIFFUSE_RATE
    return p


def cmd_run(inh_gain=0.9):
    """Run the 8-condition experiment:
    {hetero, shadow, passive, none} × {2, 1} seeds.
    """
    t0 = time.time()
    seed = 42
    results = {"config": {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "seed": seed,
        "channel": "curvature", "d": 1.0, "material_decay": 0.002,
        "deposit_prob_base": 0.01, "inh_gain": inh_gain,
        "direct_radius": DIRECT_RADIUS,
        "boundary_growth": I12.BOUNDARY_GROWTH,
        "boundary_decay": I12.BOUNDARY_DECAY,
    }}

    print("Running A: heterogeneous autopoietic, 2 seeds (the L2 test)...")
    a = run_two_region_hetero(curvature_params(inh_gain), seed=seed,
                              n_seeds=2, mode="hetero")
    print("Running B: heterogeneous autopoietic, 1 seed (L1 control)...")
    b = run_two_region_hetero(curvature_params(inh_gain), seed=seed,
                              n_seeds=1, mode="hetero")
    print("Running C: passive inhibitor, 2 seeds (direct comparison)...")
    c = run_two_region_hetero(curvature_params(inh_gain), seed=seed,
                              n_seeds=2, mode="passive")
    print("Running D: passive inhibitor, 1 seed (passive L1 control)...")
    d = run_two_region_hetero(curvature_params(inh_gain), seed=seed,
                              n_seeds=1, mode="passive")
    print("Running E: no inhibition, 2 seeds (sim10 baseline)...")
    e = run_two_region_hetero(curvature_params(0.0), seed=seed,
                              n_seeds=2, mode="none")
    print("Running F: no inhibition, 1 seed (sim10 L1 control)...")
    f = run_two_region_hetero(curvature_params(0.0), seed=seed,
                              n_seeds=1, mode="none")
    print("Running G: shadow autopoietic (sim12), 2 seeds (comparison)...")
    g = run_two_region_hetero(curvature_params(inh_gain), seed=seed,
                              n_seeds=2, mode="shadow")
    print("Running H: shadow autopoietic (sim12), 1 seed (comparison)...")
    h = run_two_region_hetero(curvature_params(inh_gain), seed=seed,
                              n_seeds=1, mode="shadow")

    results["hetero_2seed"] = a
    results["hetero_1seed"] = b
    results["passive_2seed"] = c
    results["passive_1seed"] = d
    results["none_2seed"] = e
    results["none_1seed"] = f
    results["shadow_2seed"] = g
    results["shadow_1seed"] = h

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_str = S._compact_snapshot_arrays(
        json.dumps(S._pyify(results), indent=2))
    with open(RESULTS_PATH, "w") as f_out:
        f_out.write(json_str)

    print("\n=== RESULT: Heterogeneous Agent Policies (H5/H6/H7/H10) ===")
    for name, r in [("hetero_2seed", a), ("hetero_1seed", b),
                    ("passive_2seed", c), ("passive_1seed", d),
                    ("none_2seed", e), ("none_1seed", f),
                    ("shadow_2seed", g), ("shadow_1seed", h)]:
        s = r["summary"]
        print(f"  {name:18s} l2_crossed={str(s['l2_crossed']):5s} "
              f"outcome={s['l2_outcome']:12s} "
              f"L_retain={s['l2_left_retain']:.2f} "
              f"R_retain={s['l2_right_retain']:.2f} "
              f"stable={str(s['l2_stable']):5s} "
              f"h7={str(s['crossed_h7']):5s} "
              f"cells={s['final_n_structure_cells']}")
    print(f"\nWrote {RESULTS_PATH}  ({time.time()-t0:.1f}s)")


def cmd_robustness(inh_gain=0.9, radius=None):
    """4-seed robustness sweep: hetero vs shadow vs passive vs none."""
    t0 = time.time()
    seeds = [42, 123, 256, 999]
    r = radius if radius is not None else DIRECT_RADIUS
    results = {"config": {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "seeds": seeds,
        "channel": "curvature", "d": 1.0, "material_decay": 0.002,
        "deposit_prob_base": 0.01, "inh_gain": inh_gain,
        "direct_radius": r,
    }}

    modes = [("hetero", "hetero"), ("shadow", "shadow"),
             ("passive", "passive"), ("none", "none")]
    for mode_label, mode in modes:
        for ns in [2, 1]:
            key = f"{mode_label}_{ns}seed"
            results[key] = []
            p = (curvature_params(inh_gain) if mode != "none"
                 else curvature_params(0.0))
            if mode == "hetero":
                p["direct_radius"] = r
            for sd in seeds:
                run_res = run_two_region_hetero(p, seed=sd, n_seeds=ns,
                                          mode=mode)
                results[key].append({
                    "seed": sd,
                    "l2_crossed": run_res["summary"]["l2_crossed"],
                    "l2_outcome": run_res["summary"]["l2_outcome"],
                    "l2_stable": run_res["summary"]["l2_stable"],
                    "crossed_h7": run_res["summary"]["crossed_h7"],
                    "cells": run_res["summary"]["final_n_structure_cells"],
                    "left_retain": run_res["summary"]["l2_left_retain"],
                    "right_retain": run_res["summary"]["l2_right_retain"],
                })
                print(f"  {key} seed={sd}: l2={run_res['summary']['l2_crossed']} "
                      f"outcome={run_res['summary']['l2_outcome']} "
                      f"stable={run_res['summary']['l2_stable']} "
                      f"h7={run_res['summary']['crossed_h7']}")

    path = os.path.join(OUTPUT_DIR, "robustness_sweep.json")
    with open(path, "w") as f_out:
        json.dump(S._pyify(results), f_out, indent=2)

    # Print summary table.
    print("\n=== ROBUSTNESS SWEEP (hetero vs shadow vs passive vs none) ===")
    for mode_label, _ in modes:
        for ns in [2, 1]:
            key = f"{mode_label}_{ns}seed"
            entries = results[key]
            n_cross = sum(1 for e in entries if e["l2_crossed"])
            n_coexist = sum(1 for e in entries if e["l2_outcome"] == "coexist")
            n_stable = sum(1 for e in entries if e["l2_stable"])
            n_h7 = sum(1 for e in entries if e["crossed_h7"])
            print(f"  {key:18s} l2={n_cross}/4 coexist={n_coexist}/4 "
                  f"stable={n_stable}/4 h7={n_h7}/4")

    # Compute clean composition (2-seed coexist AND 1-seed does NOT).
    print("\n=== CLEAN COMPOSITION (2-seed coexist AND 1-seed does NOT) ===")
    for mode_label, _ in modes:
        two_key = f"{mode_label}_2seed"
        one_key = f"{mode_label}_1seed"
        two_entries = results[two_key]
        one_entries = results[one_key]
        clean = 0
        for te, oe in zip(two_entries, one_entries):
            if te["l2_outcome"] == "coexist" and oe["l2_outcome"] != "coexist":
                clean += 1
        n_stable_2 = sum(1 for e in two_entries if e["l2_stable"])
        n_coexist_2 = sum(1 for e in two_entries if e["l2_outcome"] == "coexist")
        n_coexist_1 = sum(1 for e in one_entries if e["l2_outcome"] == "coexist")
        print(f"  {mode_label:18s} 2seed_coexist={n_coexist_2}/4 "
              f"1seed_coexist={n_coexist_1}/4 "
              f"stable={n_stable_2}/4 clean={clean}/4")

    print(f"\nWrote output/robustness_sweep.json  ({time.time()-t0:.1f}s)")


def cmd_selftest():
    """Prove sim14's ID-based co-presence is structurally zero for 1 seed."""
    tiny = {"grid_size": 30, "n_termites": 20, "steps": 300,
            "sample_every": 25, "channel": "curvature",
            "structure_threshold": S.STRUCTURE_THRESHOLD,
            "d": 1.0, "material_decay": 0.002,
            "deposit_prob_base": 0.01, "inh_gain": 0.9,
            "direct_radius": 5,
            "boundary_growth": I12.BOUNDARY_GROWTH,
            "boundary_decay": I12.BOUNDARY_DECAY}

    # ---- Part 1: ID co-presence is high in the gap for 2 seeds ----
    field = S.Field(30)
    T.seed_region(field, 30, "left", {})
    T.seed_region(field, 30, "right", {})
    mid = 15
    # Create ID-tagged material arrays for the seeded field.
    mbi2 = [field.material.copy(), np.zeros_like(field.material)]
    mbi2[1][:, mid:] = field.material[:, mid:].copy()
    mbi2[0][:, mid:] = 0.0
    cp2 = compute_id_copresence(mbi2, tiny)
    gap_cp2 = float(cp2[mid, mid])
    assert gap_cp2 > 0.0, \
        f"ID co-presence in gap should be >0 for two seeds; got {gap_cp2}"
    print(f"selftest: Part 1 OK (ID co-presence gap: 2seed={gap_cp2:.4f})")

    # ---- Part 2: ID co-presence is EXACTLY ZERO for a single seed ----
    # This is the KEY structural guarantee — the improvement over sim13.
    # Even if agents wander, all material has id=0, so no id=1 material
    # exists anywhere. Co-presence = min(dilate(id0), dilate(0)) = 0.
    field1 = S.Field(30)
    T.seed_region(field, 30, "left", {})
    mbi1 = [field1.material.copy(), np.zeros_like(field1.material)]
    cp1 = compute_id_copresence(mbi1, tiny)
    gap_cp1 = float(cp1[mid, mid])
    max_cp1 = float(cp1.max())
    assert max_cp1 == 0.0, \
        f"ID co-presence for single seed should be EXACTLY zero; " \
        f"got max={max_cp1}"
    print(f"selftest: Part 2 OK (ID co-presence 1seed: max={max_cp1} "
          f"— EXACTLY zero, structural guarantee)")

    # ---- Part 2b: contrast with sim12's spatial co-presence ----
    cp1_shadow = I12.compute_copresence(field1, {
        "copresence_passes": I12.COPRESENCE_PASSES,
        "copresence_diffuse_rate": I12.COPRESENCE_DIFFUSE_RATE,
    })
    gap_cp1_shadow = float(cp1_shadow[mid, mid])
    print(f"selftest: Part 2b INFO (shadow co-presence 1seed gap: "
          f"{gap_cp1_shadow:.6f} — {'non-zero (torus leak)' if gap_cp1_shadow > 0 else 'zero'})")

    # ---- Part 2c: contrast with sim13's direct-material co-presence ----
    cp1_direct = I13.compute_direct_copresence(field1, tiny)
    gap_cp1_direct = float(cp1_direct[mid, mid])
    print(f"selftest: Part 2c INFO (direct co-presence 1seed gap: "
          f"{gap_cp1_direct:.6f} — {'non-zero' if gap_cp1_direct > 0 else 'zero'})")

    # ---- Part 3: B grows with ID co-presence and decays without it ----
    B = np.zeros((30, 30), dtype=np.float64)
    for _ in range(10):
        cp = compute_id_copresence(mbi2, tiny)
        B = I12.boundary_step(B, cp, tiny)
    b_after_growth = float(B.max())
    assert b_after_growth > 0.0, \
        f"B should grow with ID co-presence; got max={b_after_growth}"

    zero_cp = np.zeros((30, 30), dtype=np.float64)
    for _ in range(200):
        B = I12.boundary_step(B, zero_cp, tiny)
    b_after_decay = float(B.max())
    assert b_after_decay < b_after_growth * 0.5, \
        f"B should decay significantly in 200 steps; {b_after_decay} vs {b_after_growth}"
    print(f"selftest: Part 3 OK (B grows={b_after_growth:.4f}, "
          f"decays to {b_after_decay:.4f} after 200 steps)")

    # ---- Part 4: B stays zero for a single seed (structural guarantee) ----
    B1 = np.zeros((30, 30), dtype=np.float64)
    for _ in range(10):
        cp = compute_id_copresence(mbi1, tiny)
        B1 = I12.boundary_step(B1, cp, tiny)
    b1_max = float(B1.max())
    assert b1_max == 0.0, \
        f"B should be EXACTLY zero for single seed; got max={b1_max}"
    print(f"selftest: Part 4 OK (B stays zero for 1 seed: max={b1_max} "
          f"— structural guarantee, no spatial filter needed)")

    # ---- Part 5: full run with heterogeneous agents produces metrics ----
    r2 = run_two_region_hetero(tiny, seed=42, n_seeds=2, mode="hetero")
    assert len(r2["history"]) >= 4, "run should produce history"
    for rec in r2["history"]:
        assert "left_total" in rec and "right_total" in rec
        assert "id0_total" in rec and "id1_total" in rec
    assert "l2_outcome" in r2["history"][-1]
    # Verify that id1 material exists in the 2-seed case.
    final_id1 = r2["history"][-1]["id1_total"]
    assert final_id1 > 0.0, \
        f"id1 material should exist in 2-seed case; got {final_id1}"
    print(f"selftest: Part 5 OK (hetero run + per-region + ID metrics; "
          f"final id0={r2['history'][-1]['id0_total']:.1f} "
          f"id1={final_id1:.1f})")

    # ---- Part 6: 1-seed control — B is zero throughout the run ----
    r1 = run_two_region_hetero(tiny, seed=42, n_seeds=1, mode="hetero")
    bt1 = r1["boundary_trace"]
    if bt1:
        max_b_1seed = max(b["b_max"] for b in bt1)
        max_b_2seed = max(b["b_max"] for b in r2["boundary_trace"]) \
            if r2["boundary_trace"] else 1.0
        assert max_b_1seed == 0.0, \
            f"B should be exactly zero for 1-seed; got max={max_b_1seed}"
        print(f"selftest: Part 6 OK (B=0 for 1-seed throughout run: "
              f"max_b_1seed={max_b_1seed} vs max_b_2seed={max_b_2seed:.4f})")
    else:
        print("selftest: Part 6 SKIPPED (no boundary trace)")

    # ---- Part 7: determinism — run twice, diff ----
    r2a = run_two_region_hetero(tiny, seed=42, n_seeds=2, mode="hetero")
    r2b = run_two_region_hetero(tiny, seed=42, n_seeds=2, mode="hetero")
    sa, sb = r2a["summary"], r2b["summary"]
    assert sa["l2_crossed"] == sb["l2_crossed"], "determinism: l2_crossed"
    assert sa["l2_outcome"] == sb["l2_outcome"], "determinism: l2_outcome"
    assert abs(sa["l2_left_retain"] - sb["l2_left_retain"]) < 1e-9
    assert abs(sa["l2_right_retain"] - sb["l2_right_retain"]) < 1e-9
    print("selftest: Part 7 OK (determinism)")

    # ---- Part 8: hybrid mode — verify suppression formula ----
    # At B_norm=0: hybrid supp = 0 (gradient term is 0, min(0, g*k) = 0)
    # At B_norm >> 1: hybrid supp = g*k (gradient saturates at g, cap at g*k)
    # At B_norm = k/(1-k): gradient = cap (transition point)
    _g_test = 0.5
    _k_test = 0.8
    _bn_test = np.array([0.0, 0.01, 0.1, 0.5, 1.0, 5.0, 100.0])
    for bn in _bn_test:
        grad = _g_test * bn / (1.0 + bn)
        cap = _g_test * _k_test
        supp_expected = min(grad, cap)
        assert supp_expected >= 0.0, f"hybrid supp should be non-negative; got {supp_expected}"
        assert supp_expected <= _g_test * _k_test + 1e-12, \
            f"hybrid supp should never exceed g*k; got {supp_expected} > {_g_test * _k_test}"
    # Verify at B_norm=0, supp=0
    assert abs(min(0.0, _g_test * _k_test)) < 1e-12, "hybrid at B=0 should be 0"
    # Verify at large B_norm, supp approaches g*k
    bn_large = 1000.0
    supp_large = min(_g_test * bn_large / (1.0 + bn_large), _g_test * _k_test)
    assert abs(supp_large - _g_test * _k_test) < 0.001, \
        f"hybrid at large B should approach g*k; got {supp_large} vs {_g_test * _k_test}"
    # Verify the transition point: gradient = cap when B_norm = k/(1-k)
    bn_trans = _k_test / (1.0 - _k_test)  # = 4.0
    grad_trans = _g_test * bn_trans / (1.0 + bn_trans)
    assert abs(grad_trans - _g_test * _k_test) < 1e-9, \
        f"transition point mismatch: {grad_trans} vs {_g_test * _k_test}"
    # Verify a full run with hybrid mode works
    p_hyb = dict(tiny)
    p_hyb["boundary_mode"] = "hybrid"
    p_hyb["hybrid_k"] = 0.8
    r_hyb = run_two_region_hetero(p_hyb, seed=42, n_seeds=2, mode="hetero")
    assert "l2_outcome" in r_hyb["summary"], "hybrid run should produce summary"
    # 1-seed control with hybrid should still be structurally zero
    r_hyb1 = run_two_region_hetero(p_hyb, seed=42, n_seeds=1, mode="hetero")
    assert not r_hyb1["summary"]["l2_crossed"], \
        "hybrid 1-seed should not cross (structural zero)"
    print(f"selftest: Part 8 OK (hybrid mode: supp=min(grad, g*k); "
          f"transition at B_norm={bn_trans:.1f}; "
          f"2seed l2={r_hyb['summary']['l2_crossed']} "
          f"1seed l2={r_hyb1['summary']['l2_crossed']})")

    # ---- Part 9: dual mode — two separate B fields ----
    # Dual mode uses B_form (gradient, faster decay) and B_persist (binary,
    # slower decay). Verify: (a) both B fields grow from co-presence,
    # (b) 1-seed control is structurally zero (both B fields = 0),
    # (c) suppression = grad_supp + bin_supp capped at 0.99,
    # (d) full run produces metrics.
    p_dual = dict(tiny)
    p_dual["boundary_mode"] = "dual"
    p_dual["g_form"] = 0.3
    p_dual["g_persist"] = 0.5
    p_dual["b_decay_form"] = 0.01  # 2x default (faster)
    p_dual["b_decay_persist"] = 0.005  # default (slower)

    # (a) Verify suppression formula: at Bf_norm=0, Bp_norm=0 → supp=0
    #     At Bf_norm>>1, Bp_norm>>0.01 → supp = g_form + g_persist (capped 0.99)
    _gf, _gp = 0.3, 0.5
    _bf = np.array([0.0, 0.01, 0.1, 1.0, 100.0])
    _bp = np.array([0.0, 0.005, 0.02, 1.0, 100.0])
    for bf, bp in zip(_bf, _bp):
        gs = _gf * bf / (1.0 + bf)
        bs = _gp if bp > 0.01 else 0.0
        supp = min(gs + bs, 0.99)
        assert supp >= 0.0, f"dual supp should be non-negative; got {supp}"
        assert supp <= 0.99 + 1e-12, f"dual supp should never exceed 0.99; got {supp}"
    # At zero: supp = 0
    assert abs(min(0.0 + 0.0, 0.99)) < 1e-12, "dual at zero should be 0"
    # At large: supp = min(0.3 + 0.5, 0.99) = 0.8
    supp_large = min(_gf * 100.0 / 101.0 + _gp, 0.99)
    assert abs(supp_large - 0.8) < 0.01, f"dual at large should be ~0.8; got {supp_large}"

    # (b) Full run with dual mode
    r_dual2 = run_two_region_hetero(p_dual, seed=42, n_seeds=2, mode="hetero")
    assert "l2_outcome" in r_dual2["summary"], "dual run should produce summary"
    # 1-seed control with dual should still be structurally zero
    r_dual1 = run_two_region_hetero(p_dual, seed=42, n_seeds=1, mode="hetero")
    assert not r_dual1["summary"]["l2_crossed"], \
        "dual 1-seed should not cross (structural zero)"
    # Verify B fields are zero for 1-seed
    if r_dual1["boundary_trace"]:
        max_b_1 = max(b["b_max"] for b in r_dual1["boundary_trace"])
        assert max_b_1 == 0.0, \
            f"dual B should be zero for 1-seed; got max={max_b_1}"

    print(f"selftest: Part 9 OK (dual mode: supp=min(grad+bin, 0.99); "
          f"2seed l2={r_dual2['summary']['l2_crossed']} "
          f"1seed l2={r_dual1['summary']['l2_crossed']} "
          f"1seed B_max=0)")

    print("selftest: ALL OK")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        g = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9
        cmd_run(inh_gain=g)
    elif cmd == "robustness":
        g = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9
        cmd_robustness(inh_gain=g)
    elif cmd == "selftest":
        cmd_selftest()
    else:
        print("usage: sim14.py [run [inh_gain] | robustness [inh_gain] | "
              "selftest]")


if __name__ == "__main__":
    main()
