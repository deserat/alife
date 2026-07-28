"""sim08 — Non-saturating inhibition (the H11 density-cap test).

H11 (The Saturating Channel Hypothesis) predicts that negative feedback delivered
THROUGH the saturating pheromone cue field is self-defeating: it destroys the
spatial contrast consolidation needs. Two prior attempts (sim06 self-maintenance,
sim07 transport venting) both fragmented the structure monotonically, both acting
through the cue field whose deposit response is flat above phi~1.

The refined prescription: act on the ACTION (deposit probability) via a channel
that does NOT saturate. This sim tests the cheapest such channel — a DENSITY CAP:
a cell whose material already exceeds DENSITY_CAP cannot receive further deposits.
The cap is a hard threshold on the deposit action, not a graded function of the cue
field, so it cannot be saturated however high pheromone climbs. Biologically this
is the crowding/inactivity channel Xiao et al. 2026 describe ("inactivity as
distributed inhibition that prevents saturation") and is one of three
non-saturating channels real termites use (see concepts/non-saturating-channels.md).

Three conditions are contrasted (same grid/termites/steps as sim06 for comparability):
  - baseline:        sim06's saturating-pheromone Grassé rule, no maintenance.
  - self_maintenance: sim06's cue-based feedback (structure re-emits pheromone) —
                     the condition that fragmented (66-109 -> 219-297 components).
  - density_cap:     sim06's Grassé rule + a non-saturating density cap on deposits.

PREDICTION (H11): density_cap consolidates — components FALL, stability RISES,
and the crossing detector may fire — where self_maintenance fragmented. If
density_cap ALSO fragments, H11 is wrong and the problem lies deeper than the
response curve. The detector and metrics are reused unchanged from sim06 so the
comparison is apples-to-apples.
"""

import os
import sys
import json
import time

import numpy as np

# Reuse sim06's tested machinery: Field, Termites, field dynamics, metrics,
# crossing detector, morphology helpers, JSON/pyify, RNG, constants.
_SIM06_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "sim06_termite_mound")
sys.path.insert(0, _SIM06_DIR)
import sim06  # noqa: E402

# Re-export the pieces we build on (so this module is self-documenting).
Field = sim06.Field
Termites = sim06.Termites
field_step = sim06.field_step
compute_metrics = sim06.compute_metrics
summarize = sim06.summarize
detect_crossing = sim06.detect_crossing
count_components = sim06.count_components
compute_compactness = sim06.compute_compactness
_pyify = sim06._pyify
make_rng = sim06.make_rng
_MOORE_DX = sim06._MOORE_DX
_MOORE_DY = sim06._MOORE_DY

# sim06 constants we rely on for comparability
GRID_SIZE = sim06.GRID_SIZE
N_TERMITES = sim06.N_TERMITES
STEPS = sim06.STEPS
SAMPLE_EVERY = sim06.SAMPLE_EVERY
SEED = sim06.SEED
STRUCTURE_THRESHOLD = sim06.STRUCTURE_THRESHOLD

# sim08's own parameter: the non-saturating density cap.
DENSITY_CAP = 4.0   # a cell with material >= DENSITY_CAP cannot receive deposits

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(SIM_DIR, "results.json")


# ---------------------------------------------------------------------------
# The ONE change: a density-capped deposit rule (non-saturating, action-based)
# ---------------------------------------------------------------------------
def termite_step_capped(termites, field, rng, params):
    """sim06's Grassé termite_step + a non-saturating density cap on deposits.

    Movement, reload, pickup are IDENTICAL to sim06 (reused). The deposit step
    adds one clause: a cell already at or above DENSITY_CAP is ineligible to
    receive a deposit. This is the H11 test — the cap is a hard threshold on the
    action, not a graded function of the cue, so it cannot saturate.
    """
    n = termites.n
    size = termites.size

    phero_follow = params.get("phero_follow", sim06.PHERO_FOLLOW)
    reload_prob = params.get("reload_prob", sim06.RELOAD_PROB)
    pickup_prob = params.get("pickup_prob", sim06.PICKUP_PROB_BASE)
    deposit_base = params.get("deposit_base", sim06.DEPOSIT_BASE)
    deposit_gain = params.get("deposit_gain", sim06.DEPOSIT_GAIN)
    pellet = params.get("pellet", sim06.PELLET)
    deposit_pheromone = params.get("deposit_pheromone", sim06.DEPOSIT_PHEROMONE)
    density_cap = params.get("density_cap", DENSITY_CAP)
    structure_threshold = params.get("structure_threshold", STRUCTURE_THRESHOLD)

    # --- Movement (identical to sim06) ---
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

    # --- Reload (identical to sim06) ---
    unloaded = ~termites.loaded
    reload_mask = unloaded & (rng.random(n) < reload_prob)
    termites.loaded[reload_mask] = True

    # --- Pickup from cell (identical to sim06) ---
    still_unloaded = ~termites.loaded
    cell_material = field.material[termites.y, termites.x]
    pick_mask = still_unloaded & (cell_material > 0) & (rng.random(n) < pickup_prob)
    if pick_mask.any():
        py = termites.y[pick_mask]
        px = termites.x[pick_mask]
        field.material[py, px] = np.maximum(field.material[py, px] - pellet, 0.0)
        termites.loaded[pick_mask] = True

    # --- Deposit (Grassé stigmergy + NON-SATURATING DENSITY CAP) ---
    local_phero = field.pheromone[termites.y, termites.x]
    p_deposit = deposit_base + deposit_gain * (local_phero / (1.0 + local_phero))
    np.clip(p_deposit, 0.0, 1.0, out=p_deposit)
    # The cap: a cell at/above density_cap cannot be deposited onto. This is the
    # only addition vs sim06. It is a hard boolean gate on the action, so it
    # stays discriminating however high the pheromone field climbs.
    cell_mat = field.material[termites.y, termites.x]
    eligible = cell_mat < density_cap
    dep_mask = termites.loaded & eligible & (rng.random(n) < p_deposit)
    deposits_on_structure = 0
    deposits_capped = 0
    if dep_mask.any():
        dy = termites.y[dep_mask]
        dx = termites.x[dep_mask]
        already_struct = field.material[dy, dx] > structure_threshold
        deposits_on_structure = int(already_struct.sum())
        field.material[dy, dx] += pellet
        field.pheromone[dy, dx] += deposit_pheromone
        termites.loaded[dep_mask] = False
    # Count how many loaded termites were blocked by the cap this step
    blocked = termites.loaded & ~eligible
    deposits_capped = int(blocked.sum())

    return {
        "deposits": int(dep_mask.sum()),
        "pickups": int(pick_mask.sum()),
        "deposits_on_structure": deposits_on_structure,
        "deposits_capped": deposits_capped,
    }


# ---------------------------------------------------------------------------
# Condition runner (mirrors sim06.run_condition, uses the capped termite step)
# ---------------------------------------------------------------------------
def run_condition(params, seed):
    """Run one condition with the density-capped deposit rule. Returns
    {"history": [...], "summary": {...}}. Metrics/detector reused from sim06."""
    rng = make_rng(seed)
    size = params.get("grid_size", GRID_SIZE)
    n = params.get("n_termites", N_TERMITES)
    steps = params.get("steps", STEPS)
    sample = params.get("sample_every", SAMPLE_EVERY)

    field = Field(size)
    termites = Termites(n, size, rng)
    history = []
    dep_acc = pick_acc = 0
    dep_on_struct_acc = 0
    capped_acc = 0
    prev_structure_mask = None
    prev_total_material = None

    for step in range(steps):
        ev = termite_step_capped(termites, field, rng, params)
        field_step(field, params)
        dep_acc += ev["deposits"]
        pick_acc += ev["pickups"]
        dep_on_struct_acc += ev.get("deposits_on_structure", 0)
        capped_acc += ev.get("deposits_capped", 0)

        if step % sample == 0:
            rec = compute_metrics(field, params, step, dep_acc, pick_acc,
                                  prev_structure_mask, dep_on_struct_acc,
                                  prev_total_material)
            rec["deposits_capped_this_window"] = capped_acc
            history.append(rec)
            dep_acc = 0
            pick_acc = 0
            dep_on_struct_acc = 0
            capped_acc = 0
            prev_total_material = rec["total_material"]
            prev_structure_mask = (field.material >
                                   params.get("structure_threshold", STRUCTURE_THRESHOLD)).copy()

    detect_crossing(history, params)
    summary = summarize(history)
    summary["n_capped_total"] = sum(r.get("deposits_capped_this_window", 0) for r in history)
    return {"history": history, "summary": summary}


# ---------------------------------------------------------------------------
# Conditions
# ---------------------------------------------------------------------------
def baseline_params():
    """sim06 baseline: saturating Grassé pheromone, no self-maintenance, no cap."""
    p = sim06.baseline_params()
    p["density_cap"] = float("inf")   # cap disabled
    return p


def self_maintenance_params():
    """sim06 self-maintenance: cue-based feedback (fragmented in sim06/sim07)."""
    p = sim06.self_maintenance_params()
    p["density_cap"] = float("inf")   # cap disabled — isolate the cue-feedback effect
    return p


def density_cap_params():
    """H11 test: Grassé rule + non-saturating density cap (cap, no cue feedback)."""
    p = sim06.baseline_params()
    p["density_cap"] = DENSITY_CAP
    return p


def combined_params():
    """Cap + self-maintenance: does the cap rescue the cue-based feedback?"""
    p = sim06.self_maintenance_params()
    p["density_cap"] = DENSITY_CAP
    return p


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def cmd_run():
    """Run all four conditions, write results.json, print a comparison summary."""
    t0 = time.time()
    # Use sim06's tuned erosion/deposit_base so the baseline matches the
    # committed sim06 numbers (66-109 components, stability 0.849-0.893).
    TUNED_MATERIAL_DECAY = 0.01
    TUNED_DEPOSIT_BASE = 0.02

    conds = {
        "baseline": baseline_params(),
        "self_maintenance": self_maintenance_params(),
        "density_cap": density_cap_params(),
        "cap_plus_self_maintenance": combined_params(),
    }
    for p in conds.values():
        p["material_decay"] = TUNED_MATERIAL_DECAY
        p["deposit_base"] = TUNED_DEPOSIT_BASE
    # self_maintenance uses the stronger maintain_gain from sim06's run
    conds["self_maintenance"]["maintain_gain"] = 0.3
    conds["cap_plus_self_maintenance"]["maintain_gain"] = 0.3

    results = {"config": {
        "grid_size": GRID_SIZE, "n_termites": N_TERMITES, "steps": STEPS,
        "sample_every": SAMPLE_EVERY, "seed": SEED,
        "density_cap": DENSITY_CAP,
        "material_decay": TUNED_MATERIAL_DECAY,
        "deposit_base": TUNED_DEPOSIT_BASE,
        "structure_threshold": STRUCTURE_THRESHOLD,
    }}

    for name, p in conds.items():
        print(f"Running {name}...")
        results[name] = run_condition(p, seed=SEED)

    results["meta"] = {"wallclock_s": round(time.time() - t0, 2)}

    with open(RESULTS_PATH, "w") as f:
        json.dump(_pyify(results), f, indent=2)

    # Print a comparison table
    print("\n=== sim08: H11 density-cap test ===")
    print(f"{'condition':<26} {'cells':>6} {'pillars':>8} {'stability':>10} "
          f"{'retention':>10} {'crossed':>8} {'capped':>8}")
    for name in conds:
        s = results[name]["summary"]
        # final pillars = last record's n_pillars
        hist = results[name]["history"]
        final_pillars = hist[-1]["n_pillars"] if hist else 0
        print(f"{name:<26} {s['final_n_structure_cells']:>6} "
              f"{final_pillars:>8} {s['mean_stability_last25']:>10.3f} "
              f"{s['retention']:>10.3f} {str(s['crossed']):>8} "
              f"{s.get('n_capped_total',0):>8}")
    print(f"\nResults written to {RESULTS_PATH} "
          f"({results['meta']['wallclock_s']}s)")


def cmd_selftest():
    """Fast sanity checks that the density cap actually gates deposits and
    that the machinery imports cleanly."""
    # 1. Imports/constants
    assert GRID_SIZE > 0 and N_TERMITES > 0 and STEPS > 0
    assert DENSITY_CAP > 0
    # 2. The cap must actually block. Termites move before depositing, so cap
    #    the WHOLE grid: no matter where they wander, they are on an ineligible
    #    cell, so zero deposits should occur.
    rng = make_rng(123)
    f = Field(10)
    t = Termites(5, 10, rng)
    f.material[:] = DENSITY_CAP     # every cell at/above the cap -> all ineligible
    t.loaded[:] = True
    p = density_cap_params()
    p["grid_size"] = 10
    p["n_termites"] = 5
    p["steps"] = 1
    ev = termite_step_capped(t, f, rng, p)
    assert ev["deposits"] == 0, f"cap failed to block: {ev['deposits']} deposits"
    assert ev["deposits_capped"] == 5, f"capped count wrong: {ev['deposits_capped']}"
    # 3. Positive control: same setup with the cap disabled -> deposits occur,
    #    proving the cap (not movement or loading) is what blocked them.
    rng2 = make_rng(123)
    f2 = Field(10)
    t2 = Termites(5, 10, rng2)
    t2.loaded[:] = True             # empty grid, cap disabled
    p2 = baseline_params()
    p2["grid_size"] = 10
    p2["n_termites"] = 5
    p2["steps"] = 1
    p2["density_cap"] = float("inf")
    ev2 = termite_step_capped(t2, f2, rng2, p2)
    assert ev2["deposits"] > 0, "positive control failed: no deposits without cap"
    # 4. A short full run produces structure under the cap.
    p3 = density_cap_params()
    p3["steps"] = 500
    res = run_condition(p3, seed=42)
    assert res["summary"]["final_n_structure_cells"] > 0, "no structure built under cap"
    print("selftest: sim08 OK (cap gates deposits; positive control deposits; run builds structure)")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "run":
        cmd_run()
    elif cmd == "selftest":
        cmd_selftest()
    else:
        print("usage: sim08.py [run|selftest]")


if __name__ == "__main__":
    main()
