"""
Threshold sweep for sim14 — pinning the H7 percolation threshold.

Session 42 found a percolation-like density threshold: H7=0/4 at n=100 (3.9/kcell),
H7=4/4 at n=200 (7.8/kcell). The transition is between two points — this sweep
densifies it: 100, 125, 150, 175, 200 termites at jitter=10 on 160×160.

Also: 8-seed robustness at n=800 (Session 42's headline result: 4/4 full co-
occurrence, but 3/4 1-seed leak). 8 seeds tests whether both results hold with
twice the sample.

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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "threshold_sweep.json")

GRID = 160
# Part 1: threshold sweep around the H7 transition
THRESHOLD_N_LIST = [100, 125, 150, 175, 200]
# Part 2: 8-seed robustness at n=800
ROBUSTNESS_N = 800
THRESHOLD_SEEDS = [42, 123, 256, 999]
ROBUSTNESS_SEEDS = [42, 123, 256, 999, 7, 17, 73, 314]
JITTER = 10.0


def run_threshold_sweep(results):
    """Part 1: finer density resolution around the H7 threshold."""
    print(f"\n{'='*70}")
    print("  PART 1: H7 THRESHOLD SWEEP (160×160, dual f=0.3 p=0.3, focal 0.3, jit=10)")
    print(f"{'='*70}")

    for nt in THRESHOLD_N_LIST:
        density = nt / (GRID * GRID) * 1000
        key = f"threshold_grid_{GRID}_n{nt}_jitter_{JITTER}"
        results[key] = {"hetero_2seed": [], "hetero_1seed": []}
        print(f"\n  n={nt} (density={density:.2f}/kcell, jitter/grid={JITTER/GRID*100:.1f}%)")

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
        p["home_jitter"] = JITTER
        p["jitter_mode"] = "per_step"

        for sd in THRESHOLD_SEEDS:
            r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
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
            print(f"    2seed s={sd}: l2={s2['l2_crossed']} "
                  f"outcome={s2['l2_outcome']} stable={s2['l2_stable']} "
                  f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']}")

            r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
            s1 = r1["summary"]
            entry1 = {
                "seed": sd,
                "l2_crossed": s1["l2_crossed"],
                "l2_outcome": s1["l2_outcome"],
                "crossed_h7": s1["crossed_h7"],
                "cells": s1["final_n_structure_cells"],
            }
            results[key]["hetero_1seed"].append(entry1)


def run_robustness_sweep(results):
    """Part 2: 8-seed robustness at n=800."""
    print(f"\n{'='*70}")
    print(f"  PART 2: 8-SEED ROBUSTNESS AT n={ROBUSTNESS_N} "
          f"(160×160, dual f=0.3 p=0.3, focal 0.3, jit={JITTER})")
    print(f"{'='*70}")

    nt = ROBUSTNESS_N
    density = nt / (GRID * GRID) * 1000
    key = f"robust8_grid_{GRID}_n{nt}_jitter_{JITTER}"
    results[key] = {"hetero_2seed": [], "hetero_1seed": []}
    print(f"\n  n={nt} (density={density:.2f}/kcell, 8 seeds)")

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
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"

    for sd in ROBUSTNESS_SEEDS:
        r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
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
        print(f"    2seed s={sd}: l2={s2['l2_crossed']} "
              f"outcome={s2['l2_outcome']} stable={s2['l2_stable']} "
              f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']}")

        r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
        s1 = r1["summary"]
        entry1 = {
            "seed": sd,
            "l2_crossed": s1["l2_crossed"],
            "l2_outcome": s1["l2_outcome"],
            "crossed_h7": s1["crossed_h7"],
            "cells": s1["final_n_structure_cells"],
        }
        results[key]["hetero_1seed"].append(entry1)
        print(f"    1seed s={sd}: l2={s1['l2_crossed']} "
              f"h7={s1['crossed_h7']} cells={s1['final_n_structure_cells']}")


def print_summary(results):
    """Print summary tables."""
    n_thresh = len(THRESHOLD_SEEDS)
    n_robust = len(ROBUSTNESS_SEEDS)

    # Part 1: threshold
    print(f"\n{'='*100}")
    print("  THRESHOLD SWEEP SUMMARY (160×160, dual f=0.3 p=0.3, focal 0.3, jit=10)")
    print(f"{'='*100}")
    print(f"{'nT':>5s} {'density':>8s} | "
          f"{'l2(2s)':>7s} {'coexist':>8s} {'stable':>7s} {'h7(2s)':>7s} "
          f"{'clean':>6s} {'full':>6s} | "
          f"{'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 100)

    for nt in THRESHOLD_N_LIST:
        density = nt / (GRID * GRID) * 1000
        key = f"threshold_grid_{GRID}_n{nt}_jitter_{JITTER}"
        h2 = results[key]["hetero_2seed"]
        h1 = results[key]["hetero_1seed"]
        n4 = n_thresh
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
        print(f"{nt:>5d} {density:>7.2f} | "
              f"{n_l2_2:>3d}/{n4:<2d}  {n_coexist_2:>4d}/{n4:<3d}  "
              f"{n_stable_2:>3d}/{n4:<2d}  {n_h7_2:>3d}/{n4:<2d}  "
              f"{clean:>3d}/{n4:<2d}  {full:>3d}/{n4:<2d}  | "
              f"{n_l2_1:>3d}/{n4:<2d}  {n_h7_1:>3d}/{n4:<2d}  {mean_cells:>6d}")

    # Part 2: robustness
    print(f"\n{'='*100}")
    print(f"  8-SEED ROBUSTNESS SUMMARY (160×160, n={ROBUSTNESS_N}, "
          f"dual f=0.3 p=0.3, focal 0.3, jit=10)")
    print(f"{'='*100}")

    key = f"robust8_grid_{GRID}_n{ROBUSTNESS_N}_jitter_{JITTER}"
    h2 = results[key]["hetero_2seed"]
    h1 = results[key]["hetero_1seed"]
    n8 = n_robust
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
    density = ROBUSTNESS_N / (GRID * GRID) * 1000
    print(f"{'nT':>5s} {'density':>8s} | "
          f"{'l2(2s)':>7s} {'coexist':>8s} {'stable':>7s} {'h7(2s)':>7s} "
          f"{'clean':>6s} {'full':>6s} | "
          f"{'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 100)
    print(f"{ROBUSTNESS_N:>5d} {density:>7.2f} | "
          f"{n_l2_2:>3d}/{n8:<2d}  {n_coexist_2:>4d}/{n8:<3d}  "
          f"{n_stable_2:>3d}/{n8:<2d}  {n_h7_2:>3d}/{n8:<2d}  "
          f"{clean:>3d}/{n8:<2d}  {full:>3d}/{n8:<2d}  | "
          f"{n_l2_1:>3d}/{n8:<2d}  {n_h7_1:>3d}/{n8:<2d}  {mean_cells:>6d}")

    # Per-seed detail for robustness
    print(f"\n  Per-seed (8-seed robustness):")
    for e2, e1 in zip(h2, h1):
        print(f"    s={e2['seed']:>4d}: 2s l2={e2['l2_crossed']} "
              f"out={e2['l2_outcome']:>10s} stable={e2['l2_stable']} "
              f"h7={e2['crossed_h7']} cells={e2['cells']:>5d} | "
              f"1s l2={e1['l2_crossed']} h7={e1['crossed_h7']} "
              f"cells={e1['cells']:>5d}")


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "threshold_n_list": THRESHOLD_N_LIST,
        "threshold_seeds": THRESHOLD_SEEDS,
        "robustness_n": ROBUSTNESS_N,
        "robustness_seeds": ROBUSTNESS_SEEDS,
        "jitter": JITTER,
        "boundary_mode": "dual",
        "g_form": 0.3,
        "g_persist": 0.3,
        "movement_bias": 0.3,
        "movement_mode": "focal",
        "jitter_mode": "per_step",
        "note": "Session 43: H7 threshold sweep + 8-seed robustness at n=800",
    }}

    run_threshold_sweep(results)
    run_robustness_sweep(results)

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    print_summary(results)

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
