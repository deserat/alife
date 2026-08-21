"""
Local-movement sweep for sim14 — comparing focal-point attraction vs
biologically-grounded local mechanisms (Richardson et al. 2022).

Queued-topic #105: The current movement_bias is a global focal-point
attraction (agents step toward home center). Richardson et al. (2022)
found that real social insects use LOCAL mechanisms instead:
  (1) boundary effects — agents turn back at zone borders
  (2) locomotion adjustment — low diffusivity inside zone, high outside

The boundary-effect mode is especially interesting because it closes a
stigmergic feedback loop: B field → agent movement → co-presence → B.
The B field (grown from co-presence) influences agent movement, which
concentrates material, which sharpens co-presence, which grows B.

Test: at the best dual config (f=0.3 p=0.3, max_supp=0.60), sweep
movement modes: focal (bias=0.3), boundary, diffusivity, and none
(bias=0.0). 4 seeds × {2, 1} seeds.

Methodology:
  - Control arms: 1-seed controls (must stay 0/4)
  - Determinism: verified by the selftest
  - Per-seed outcomes reported
  - Baseline: focal bias=0.0 replicates Session 34 dual f=0.3 p=0.3
"""

import os
import sys
import json
import time

import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14  # noqa: E402
import sim09 as S    # noqa: E402

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "local_movement_sweep.json")
SEEDS = [42, 123, 256, 999]

# Movement modes to test:
#   "none"      — focal mode, bias=0.0 (no movement restriction)
#   "focal"     — focal-point attraction, bias=0.3 (Session 34 winner)
#   "boundary"  — agents turn back at high B (stigmergic loop)
#   "diffusivity" — low diffusivity inside home, high outside
MODES = [
    ("none",        {"movement_mode": "focal", "movement_bias": 0.0}),
    ("focal_0.3",   {"movement_mode": "focal", "movement_bias": 0.3}),
    ("boundary",    {"movement_mode": "boundary", "movement_bias": 0.0}),
    ("diffusivity", {"movement_mode": "diffusivity", "movement_bias": 0.0}),
]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "modes": [m[0] for m in MODES],
        "seeds": SEEDS,
        "boundary_mode": "dual",
        "g_form": 0.3,
        "g_persist": 0.3,
        "grid_size": 80,
        "n_termites": 150,
        "steps": 2000,
        "sample_every": 25,
        "channel": "curvature",
        "d": 1.0,
        "material_decay": 0.002,
        "deposit_prob_base": 0.01,
        "direct_radius": I14.DIRECT_RADIUS,
        "b_decay_form": 0.01,
        "b_decay_persist": 0.005,
        "b_growth_form": 0.1,
        "b_growth_persist": 0.1,
    }}

    for mode_label, mode_params in MODES:
        key = mode_label
        results[key] = {"hetero_2seed": [], "hetero_1seed": []}
        print(f"\n{'='*60}")
        print(f"  movement_mode={mode_label}")
        print(f"{'='*60}")

        p = I14.curvature_params(0.5)  # inh_gain > 0 to activate boundary
        p["boundary_mode"] = "dual"
        p["g_form"] = 0.3
        p["g_persist"] = 0.3
        p["b_decay_form"] = 0.01
        p["b_decay_persist"] = 0.005
        p.update(mode_params)

        for sd in SEEDS:
            # 2-seed (L2 test)
            r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2,
                                           mode="hetero")
            s2 = r2["summary"]
            entry2 = {
                "seed": sd,
                "l2_crossed": s2["l2_crossed"],
                "l2_outcome": s2["l2_outcome"],
                "l2_stable": s2["l2_stable"],
                "crossed_h7": s2["crossed_h7"],
                "cells": s2["final_n_structure_cells"],
                "left_retain": s2["l2_left_retain"],
                "right_retain": s2["l2_right_retain"],
                "b_max": max((b["b_max"] for b in r2["boundary_trace"]),
                             default=0.0),
            }
            results[key]["hetero_2seed"].append(entry2)
            print(f"  {mode_label} 2seed s={sd}: l2={s2['l2_crossed']} "
                  f"outcome={s2['l2_outcome']} stable={s2['l2_stable']} "
                  f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']}")

            # 1-seed (L1 control — must be 0)
            r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1,
                                           mode="hetero")
            s1 = r1["summary"]
            entry1 = {
                "seed": sd,
                "l2_crossed": s1["l2_crossed"],
                "l2_outcome": s1["l2_outcome"],
                "l2_stable": s1["l2_stable"],
                "crossed_h7": s1["crossed_h7"],
                "cells": s1["final_n_structure_cells"],
            }
            results[key]["hetero_1seed"].append(entry1)
            print(f"  {mode_label} 1seed s={sd}: l2={s1['l2_crossed']} "
                  f"outcome={s1['l2_outcome']} h7={s1['crossed_h7']} "
                  f"cells={s1['final_n_structure_cells']}")

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*100}")
    print("  LOCAL MOVEMENT SWEEP SUMMARY (dual f=0.3 p=0.3)")
    print(f"{'='*100}")
    print(f"{'mode':>14s} | {'l2(2s)':>7s} {'coexist':>8s} {'stable':>7s} "
          f"{'h7(2s)':>7s} {'clean':>6s} {'full':>6s} | "
          f"{'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 105)

    for mode_label, _ in MODES:
        key = mode_label
        h2 = results[key]["hetero_2seed"]
        h1 = results[key]["hetero_1seed"]
        n_l2_2 = sum(1 for e in h2 if e["l2_crossed"])
        n_coexist_2 = sum(1 for e in h2 if e["l2_outcome"] == "coexist")
        n_stable_2 = sum(1 for e in h2 if e["l2_stable"])
        n_h7_2 = sum(1 for e in h2 if e["crossed_h7"])
        n_l2_1 = sum(1 for e in h1 if e["l2_crossed"])
        n_h7_1 = sum(1 for e in h1 if e["crossed_h7"])
        clean = sum(1 for e2, e1 in zip(h2, h1)
                    if e2["l2_outcome"] == "coexist"
                    and e1["l2_outcome"] != "coexist")
        full = sum(1 for e2, e1 in zip(h2, h1)
                   if e2["crossed_h7"]
                   and e2["l2_outcome"] == "coexist"
                   and e1["l2_outcome"] != "coexist"
                   and e2["l2_stable"])
        mean_cells = np.mean([e["cells"] for e in h2])
        print(f"{mode_label:>14s} | {n_l2_2:>4d}/4  {n_coexist_2:>5d}/4  "
              f"{n_stable_2:>4d}/4  {n_h7_2:>4d}/4  {clean:>4d}/4  {full:>4d}/4  | "
              f"{n_l2_1:>4d}/4  {n_h7_1:>4d}/4  {mean_cells:6.0f}")

    # Per-seed outcome detail
    print(f"\n{'='*100}")
    print("  PER-SEED OUTCOME DETAIL")
    print(f"{'='*100}")
    for mode_label, _ in MODES:
        key = mode_label
        h2 = results[key]["hetero_2seed"]
        for e in h2:
            print(f"  {mode_label:>14s} seed={e['seed']:3d}: "
                  f"outcome={e['l2_outcome']:12s} "
                  f"stable={str(e['l2_stable']):5s} "
                  f"h7={str(e['crossed_h7']):5s} "
                  f"cells={e['cells']:5d} "
                  f"L_ret={e['left_retain']:.2f} "
                  f"R_ret={e['right_retain']:.2f} "
                  f"b_max={e.get('b_max', 0):.2f}")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
