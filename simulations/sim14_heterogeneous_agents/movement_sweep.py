"""
Movement-bias sweep for sim14 — testing whether restricting agent movement
to their home region improves outcome quality (clean coexistence).

Queued-topic #93: sim14 tags deposits with the agent's structure ID, so
co-presence is structurally specific. But agents still wander freely on the
torus, distributing each ID's material across both halves. This produces
fragmented compositions (multiple small components) and late merging
(structures held for most of the late window but merged at the end).

The movement_bias parameter (already in sim14.py) biases the random walk:
when not curvature-following, agents step toward their home center with
probability movement_bias. This concentrates each ID's material.

Test: at the best dual config (f=0.3 p=0.3, max_supp=0.60), sweep
movement_bias [0.0, 0.3, 0.5, 0.7, 0.9] × 4 seeds × {2, 1} seeds.

Prediction: moderate movement_bias (~0.5) improves clean coexistence by
concentrating each ID's material, reducing boundary fragmentation. High
movement_bias (~0.9) may over-concentrate agents and reduce structure
growth (H7 crossing).

Methodology:
  - Control arms: 1-seed controls (must stay 0/4)
  - Determinism: verified by the selftest
  - Per-seed outcomes reported
  - Baseline: movement_bias=0.0 replicates Session 33 dual f=0.3 p=0.3
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "movement_sweep.json")

BIASES = [0.0, 0.3, 0.5, 0.7, 0.9]
SEEDS = [42, 123, 256, 999]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "biases": BIASES,
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

    for bias in BIASES:
        key = f"bias_{bias}"
        results[key] = {"hetero_2seed": [], "hetero_1seed": []}
        print(f"\n{'='*60}")
        print(f"  movement_bias={bias}")
        print(f"{'='*60}")

        p = I14.curvature_params(0.5)  # inh_gain > 0 to activate boundary
        p["boundary_mode"] = "dual"
        p["g_form"] = 0.3
        p["g_persist"] = 0.3
        p["b_decay_form"] = 0.01
        p["b_decay_persist"] = 0.005
        p["movement_bias"] = bias

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
            print(f"  bias={bias} 2seed s={sd}: l2={s2['l2_crossed']} "
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
            print(f"  bias={bias} 1seed s={sd}: l2={s1['l2_crossed']} "
                  f"outcome={s1['l2_outcome']} h7={s1['crossed_h7']} "
                  f"cells={s1['final_n_structure_cells']}")

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*95}")
    print("  MOVEMENT-BIAS SWEEP SUMMARY (dual f=0.3 p=0.3)")
    print(f"{'='*95}")
    print(f"{'bias':>6s} | {'l2(2s)':>7s} {'coexist':>8s} {'stable':>7s} "
          f"{'h7(2s)':>7s} {'clean':>6s} {'full':>6s} | "
          f"{'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 100)

    for bias in BIASES:
        key = f"bias_{bias}"
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
        # Full co-occurrence: H7 + clean + stable
        full = sum(1 for e2, e1 in zip(h2, h1)
                   if e2["crossed_h7"]
                   and e2["l2_outcome"] == "coexist"
                   and e1["l2_outcome"] != "coexist"
                   and e2["l2_stable"])
        mean_cells = np.mean([e["cells"] for e in h2])
        print(f"{bias:6.1f} | {n_l2_2:>4d}/4  {n_coexist_2:>5d}/4  "
              f"{n_stable_2:>4d}/4  {n_h7_2:>4d}/4  {clean:>4d}/4  {full:>4d}/4  | "
              f"{n_l2_1:>4d}/4  {n_h7_1:>4d}/4  {mean_cells:6.0f}")

    # Co-occurrence check
    print(f"\n{'='*95}")
    print("  CO-OCCURRENCE: H7 crossing AND clean composition AND stable")
    print(f"{'='*95}")
    found_any = False
    for bias in BIASES:
        key = f"bias_{bias}"
        h2 = results[key]["hetero_2seed"]
        h1 = results[key]["hetero_1seed"]
        for i, (e2, e1) in enumerate(zip(h2, h1)):
            h7 = e2["crossed_h7"]
            clean = (e2["l2_outcome"] == "coexist"
                     and e1["l2_outcome"] != "coexist")
            stable = e2["l2_stable"]
            if h7 and clean:
                found_any = True
                tag = " + STABLE!" if stable else ""
                print(f"  *** bias={bias} seed={SEEDS[i]}: "
                      f"H7=YES clean=YES{tag}")
    if not found_any:
        print("  (no co-occurrence found)")

    # Outcome detail
    print(f"\n{'='*95}")
    print("  PER-SEED OUTCOME DETAIL")
    print(f"{'='*95}")
    for bias in BIASES:
        key = f"bias_{bias}"
        h2 = results[key]["hetero_2seed"]
        for e in h2:
            print(f"  bias={bias} seed={e['seed']:3d}: "
                  f"outcome={e['l2_outcome']:12s} "
                  f"stable={str(e['l2_stable']):5s} "
                  f"h7={str(e['crossed_h7']):5s} "
                  f"cells={e['cells']:5d} "
                  f"L_ret={e['left_retain']:.2f} "
                  f"R_ret={e['right_retain']:.2f}")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
