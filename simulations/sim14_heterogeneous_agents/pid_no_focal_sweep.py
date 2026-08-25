"""
PID D-term sweep without focal bias — queued-topic #103 extension.

Session 39's main sweep found the D term is neutral at the optimal
configuration (dual f=0.3 p=0.3, focal bias=0.3): 4/4 full co-occurrence
at all g_deriv.  The D term can't improve on 4/4.

This sweep removes the focal bias to test whether the D term SUBSTITUTES
for agent locality.  Without focal bias, the dual mode achieves 1/4 full
co-occurrence (Session 34).  Does the D term's anticipatory suppression
recover the co-occurrence that agent wander destroys?

Sweep: g_deriv [0.0, 0.1, 0.2, 0.3, 0.5] × 4 seeds × {2, 1} seeds.
  No focal bias (movement_bias=0.0).
  Dual f=0.3 p=0.3 baseline.

If g_deriv > 0 recovers co-occurrence without focal bias, the D term
substitutes for agent locality — anticipatory boundary strengthening
prevents merging where it couldn't be prevented by keeping agents local.
If it doesn't, the D term is truly neutral — it works only when the
system is already stable.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "pid_no_focal_sweep.json")

G_DERIVS = [0.0, 0.1, 0.2, 0.3, 0.5]
SEEDS = [42, 123, 256, 999]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "g_derivs": G_DERIVS,
        "seeds": SEEDS,
        "boundary_mode": "triple",
        "g_form": 0.3,
        "g_persist": 0.3,
        "movement_bias": 0.0,
        "movement_mode": "focal",
        "jitter_mode": "per_step",
        "home_jitter": 0.0,
        "note": "No focal bias — testing D-term substitution for locality",
    }}

    for g_deriv in G_DERIVS:
        key = f"gderiv_{g_deriv}"
        results[key] = {"hetero_2seed": [], "hetero_1seed": []}
        print(f"\n{'='*60}")
        print(f"  g_deriv={g_deriv} (max_supp={0.3+0.3+g_deriv:.2f}) "
              f"[NO FOCAL BIAS]")
        print(f"{'='*60}")

        for sd in SEEDS:
            p = I14.curvature_params(0.5)
            p["boundary_mode"] = "triple"
            p["g_form"] = 0.3
            p["g_persist"] = 0.3
            p["g_deriv"] = g_deriv
            p["b_decay_form"] = 0.01
            p["b_decay_persist"] = 0.005
            p["b_decay_deriv"] = 0.02
            p["b_growth_form"] = 0.1
            p["b_growth_persist"] = 0.1
            p["b_growth_deriv"] = 0.2
            p["movement_bias"] = 0.0  # NO focal bias
            p["movement_mode"] = "focal"
            p["home_jitter"] = 0.0
            p["jitter_mode"] = "per_step"

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
            print(f"  g_deriv={g_deriv} 2seed s={sd}: "
                  f"l2={s2['l2_crossed']} outcome={s2['l2_outcome']} "
                  f"stable={s2['l2_stable']} h7={s2['crossed_h7']} "
                  f"cells={s2['final_n_structure_cells']}")

            # 1-seed (L1 control)
            r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1,
                                           mode="hetero")
            s1 = r1["summary"]
            entry1 = {
                "seed": sd,
                "l2_crossed": s1["l2_crossed"],
                "l2_outcome": s1["l2_outcome"],
                "crossed_h7": s1["crossed_h7"],
                "cells": s1["final_n_structure_cells"],
            }
            results[key]["hetero_1seed"].append(entry1)

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*100}")
    print("  PID D-TERM NO-FOCAL SWEEP (triple f=0.3 p=0.3, NO focal bias)")
    print(f"{'='*100}")
    print(f"{'g_deriv':>8s} {'max_supp':>9s} | {'l2(2s)':>7s} "
          f"{'coexist':>8s} {'stable':>7s} {'h7(2s)':>7s} {'clean':>6s} "
          f"{'full':>6s} | {'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 100)

    for g_deriv in G_DERIVS:
        key = f"gderiv_{g_deriv}"
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
        max_supp = 0.3 + 0.3 + g_deriv
        print(f"{g_deriv:8.2f} {max_supp:9.2f} | {n_l2_2:>4d}/4  "
              f"{n_coexist_2:>5d}/4  {n_stable_2:>4d}/4  "
              f"{n_h7_2:>4d}/4  {clean:>4d}/4  {full:>4d}/4  | "
              f"{n_l2_1:>4d}/4  {n_h7_1:>4d}/4  {mean_cells:6.0f}")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
