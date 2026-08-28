"""
Finer density sweep for sim14 — queued-topic #122.

Session 41 found a non-monotonic intermediate density: 160×300 (11.7/kcell)
achieves only 2/4 coexist at jitter=10 — worse than both 160×150 (4/4 at 5.9/kcell)
and 160×600 (4/4 at 23.4/kcell). The intermediate density may be in a regime
where the structure is too big for one half (overwhelming the midline at 300
termites) but too sparse to consolidate well (not enough for the curvature
channel to create spatial selectivity).

This sweep tests 4 density levels on the 160×160 grid:
  100, 200, 400, 800 termites (6.25, 12.5, 25, 50 per 1000 cells)
at jitter=10 (6.2% of grid) — the level where the non-monotonicity appeared.

If the non-monotonicity is genuine, there should be a U-shaped curve:
  low density (100) → sparse, may not cross
  intermediate (200) → worst (too big for one half, too sparse to consolidate)
  medium (400) → good
  high (800) → good but 1-seed may leak (structure too big)

Config: dual f=0.3 p=0.3, focal bias=0.3, per_step jitter.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "finer_density_sweep.json")

# 4 density levels on the 160×160 grid, at jitter=10 (where non-monotonicity appeared)
GRID = 160
N_TERMITES_LIST = [100, 200, 400, 800]
JITTERS = [10.0]  # the level where the non-monotonicity appeared
SEEDS = [42, 123, 256, 999]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "n_termites_list": N_TERMITES_LIST,
        "jitters": JITTERS,
        "seeds": SEEDS,
        "boundary_mode": "dual",
        "g_form": 0.3,
        "g_persist": 0.3,
        "movement_bias": 0.3,
        "movement_mode": "focal",
        "jitter_mode": "per_step",
        "note": "finer density sweep at jitter=10 — testing non-monotonic intermediate density",
    }}

    for nt in N_TERMITES_LIST:
        density = nt / (GRID * GRID) * 1000
        for jit in JITTERS:
            key = f"grid_{GRID}_n{nt}_jitter_{jit}"
            results[key] = {"hetero_2seed": [], "hetero_1seed": []}
            print(f"\n{'='*60}")
            print(f"  grid={GRID} n_termites={nt} jitter={jit} "
                  f"(density={density:.2f}/kcells, jitter/grid={jit/GRID*100:.1f}%)")
            print(f"{'='*60}")

            p = I14.curvature_params(0.5)
            p["grid_size"] = GRID
            p["n_termites"] = nt
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
                print(f"  grid={GRID} n={nt} jit={jit} 2seed s={sd}: "
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
    print(f"\n{'='*130}")
    print("  FINER DENSITY SWEEP SUMMARY (160×160, dual f=0.3 p=0.3, focal bias=0.3, jit=10)")
    print(f"{'='*130}")
    print(f"{'nT':>5s} {'density':>8s} {'frac%':>6s} | "
          f"{'l2(2s)':>7s} {'coexist':>8s} {'stable':>7s} {'h7(2s)':>7s} "
          f"{'clean':>6s} {'full':>6s} | {'l2(1s)':>7s} {'h7(1s)':>7s} "
          f"{'cells':>6s}")
    print("-" * 130)

    for nt in N_TERMITES_LIST:
        density = nt / (GRID * GRID) * 1000
        jit = JITTERS[0]
        key = f"grid_{GRID}_n{nt}_jitter_{jit}"
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
        mean_cells = int(np.mean([e["cells"] for e in h2]))
        frac = jit / GRID * 100
        print(f"{nt:>5d} {density:>7.2f} {frac:5.1f}% | "
              f"{n_l2_2:>4d}/4  {n_coexist_2:>5d}/4  {n_stable_2:>4d}/4  "
              f"{n_h7_2:>4d}/4  {clean:>4d}/4  {full:>4d}/4  | "
              f"{n_l2_1:>4d}/4  {n_h7_1:>4d}/4  {mean_cells:>6d}")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
