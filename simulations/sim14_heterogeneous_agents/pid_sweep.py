"""
PID D-term sweep for sim14 — queued-topic #103.

The dual mode (Session 33) maps onto a PID controller:
  B_form = P (proportional — gradient, responsive)
  B_persist = I (integral — binary, memory)
  B_deriv = D (derivative — anticipatory)

The D term responds to the rate of change of co-presence:
  cp_delta = max(0, cp - cp_prev)
  B_deriv grows from cp_delta and decays fast.

The D term is anticipatory: it strengthens the boundary BEFORE the
structures merge (when co-presence is rising), not after.  This might
prevent the "merged at the end" outcome (seed 999 at dual f=0.3 p=0.3)
by detecting the merger trend early.

Sweep: g_deriv [0.0, 0.05, 0.1, 0.2, 0.3] × 4 seeds × {2, 1} seeds.
  g_deriv=0.0 = dual mode (P+I only, the baseline).
  g_deriv>0.0 = triple mode (P+I+D).

Config: dual f=0.3 p=0.3 (max_supp=0.60), focal bias=0.3, per_step jitter.
The max suppression with D is g_form + g_persist + g_deriv = 0.3+0.3+g_deriv.
At g_deriv=0.3, max_supp=0.90 — at the H7 threshold (0.72-0.81).

Methodology: 1-seed controls, determinism, per-seed outcomes.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "pid_sweep.json")

G_DERIVS = [0.0, 0.05, 0.1, 0.2, 0.3]
SEEDS = [42, 123, 256, 999]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "g_derivs": G_DERIVS,
        "seeds": SEEDS,
        "boundary_mode": "triple",
        "g_form": 0.3,
        "g_persist": 0.3,
        "movement_bias": 0.3,
        "movement_mode": "focal",
        "jitter_mode": "per_step",
        "home_jitter": 0.0,
    }}

    for g_deriv in G_DERIVS:
        key = f"gderiv_{g_deriv}"
        results[key] = {"hetero_2seed": [], "hetero_1seed": []}
        print(f"\n{'='*60}")
        print(f"  g_deriv={g_deriv} (max_supp={0.3+0.3+g_deriv:.2f})")
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
            p["movement_bias"] = 0.3
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
    print("  PID D-TERM SWEEP SUMMARY (triple f=0.3 p=0.3, focal bias=0.3)")
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

    # Determinism check at g_deriv=0.1
    print("\n  Determinism check at g_deriv=0.1 seed=42...")
    p_det = I14.curvature_params(0.5)
    p_det["boundary_mode"] = "triple"
    p_det["g_form"] = 0.3
    p_det["g_persist"] = 0.3
    p_det["g_deriv"] = 0.1
    p_det["b_decay_form"] = 0.01
    p_det["b_decay_persist"] = 0.005
    p_det["b_decay_deriv"] = 0.02
    p_det["b_growth_form"] = 0.1
    p_det["b_growth_persist"] = 0.1
    p_det["b_growth_deriv"] = 0.2
    p_det["movement_bias"] = 0.3
    p_det["movement_mode"] = "focal"
    r_a = I14.run_two_region_hetero(p_det, seed=42, n_seeds=2,
                                     mode="hetero")
    r_b = I14.run_two_region_hetero(p_det, seed=42, n_seeds=2,
                                     mode="hetero")
    sa, sb = r_a["summary"], r_b["summary"]
    det_ok = (sa["l2_crossed"] == sb["l2_crossed"]
              and sa["l2_outcome"] == sb["l2_outcome"]
              and abs(sa["l2_left_retain"] - sb["l2_left_retain"]) < 1e-9)
    print(f"  Determinism: {'OK' if det_ok else 'FAILED'} "
          f"(l2={sa['l2_crossed']}, outcome={sa['l2_outcome']})")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
