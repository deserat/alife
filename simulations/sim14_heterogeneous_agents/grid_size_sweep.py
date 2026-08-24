"""
Grid-size scaling sweep for sim14 — queued-topic #115.

Session 37 found jitter tolerance collapses at jitter=20 (25% of 80-cell grid)
because the noisy home center can cross the midline. Is this a grid-size
artifact? On a 160×160 grid with home centers at x=40 and x=120, jitter=20 is
only 12.5% — does it preserve 4/4?

Sweep: grid_size [80, 120, 160] × jitter [0, 10, 20, 40] × 4 seeds × {2, 1} seeds.
Home centers scale with grid: mid//2 and mid+mid//2 for each grid size.

If the 160×160 grid tolerates jitter=20 (25% of 80 → 12.5% of 160), the
tolerance is about jitter/grid_size (fraction), not absolute displacement.
If it does not, the tolerance is about absolute displacement from center.

Config: dual f=0.3 p=0.3, focal bias=0.3, per_step jitter (Session 37's mode).
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "grid_size_sweep.json")

GRID_SIZES = [80, 160]
JITTERS = [0.0, 10.0, 20.0, 40.0]
SEEDS = [42, 123, 256, 999]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "grid_sizes": GRID_SIZES,
        "jitters": JITTERS,
        "seeds": SEEDS,
        "boundary_mode": "dual",
        "g_form": 0.3,
        "g_persist": 0.3,
        "movement_bias": 0.3,
        "movement_mode": "focal",
        "jitter_mode": "per_step",
    }}

    for gs in GRID_SIZES:
        for jit in JITTERS:
            key = f"grid_{gs}_jitter_{jit}"
            results[key] = {"hetero_2seed": [], "hetero_1seed": []}
            print(f"\n{'='*60}")
            print(f"  grid_size={gs} home_jitter={jit} "
                  f"(jitter/grid={jit/gs*100:.1f}%)")
            print(f"{'='*60}")

            p = I14.curvature_params(0.5)
            p["grid_size"] = gs
            p["boundary_mode"] = "dual"
            p["g_form"] = 0.3
            p["g_persist"] = 0.3
            p["b_decay_form"] = 0.01
            p["b_decay_persist"] = 0.005
            p["b_growth_form"] = 0.1
            p["b_growth_persist"] = 0.1
            p["movement_bias"] = 0.3
            p["movement_mode"] = "focal"
            p["home_jitter"] = jit
            p["jitter_mode"] = "per_step"

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
                print(f"  grid={gs} jit={jit} 2seed s={sd}: "
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
    print(f"\n{'='*120}")
    print("  GRID-SIZE SCALING SWEEP SUMMARY (dual f=0.3 p=0.3, focal bias=0.3)")
    print(f"{'='*120}")
    print(f"{'grid':>5s} {'jitter':>7s} {'frac%':>6s} | {'l2(2s)':>7s} "
          f"{'coexist':>8s} {'stable':>7s} {'h7(2s)':>7s} {'clean':>6s} "
          f"{'full':>6s} | {'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 120)

    for gs in GRID_SIZES:
        for jit in JITTERS:
            key = f"grid_{gs}_jitter_{jit}"
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
            frac = jit / gs * 100
            print(f"{gs:>5d} {jit:7.1f} {frac:5.1f}% | {n_l2_2:>4d}/4  "
                  f"{n_coexist_2:>5d}/4  {n_stable_2:>4d}/4  "
                  f"{n_h7_2:>4d}/4  {clean:>4d}/4  {full:>4d}/4  | "
                  f"{n_l2_1:>4d}/4  {n_h7_1:>4d}/4  {mean_cells:6.0f}")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
