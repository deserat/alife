"""
g*(n) scaling-law sweep — queued-topic #129.

Session 45 found the optimal boundary gain g* is density-dependent:
  g*≈0.30 at n=150 (5.86/kcell), g*≈0.20 at n=175 (6.84/kcell).

A linear fit gives g* = 0.90 - 0.004*n, predicting g*(n)=0 at n=225 —
composition impossible above that density. This sweep tests the linear
hypothesis by filling in n=155, 160, 165, 170, 180 at g values centered
on the linear prediction:

  n=155: predicted g*≈0.28 → test g=0.26, 0.28, 0.30, 0.32
  n=160: predicted g*≈0.26 → test g=0.22, 0.24, 0.26, 0.28
  n=165: predicted g*≈0.24 → test g=0.20, 0.22, 0.24, 0.26
  n=170: predicted g*≈0.22 → test g=0.18, 0.20, 0.22, 0.24
  n=180: predicted g*≈0.18 → test g=0.14, 0.16, 0.18, 0.20

20 combos × 4 seeds × {2, 1} seeds = 160 runs.
Config: 160×160, dual mode, focal bias=0.3, per_step jitter=10.

Methodology: 1-seed controls, determinism (2 runs diffed), per-seed outcomes.
Output: output/gain_scaling_sweep.json
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "gain_scaling_sweep.json")

GRID = 160
JITTER = 10.0
SEEDS = [42, 123, 256, 999]

# (n_termites, g_form, g_persist, label)
# g values centered on linear prediction g* = 0.90 - 0.004*n
COMBOS = [
    # n=155: predicted g*≈0.28
    (155, 0.26, 0.26, "n155_g026"),
    (155, 0.28, 0.28, "n155_g028"),
    (155, 0.30, 0.30, "n155_g030"),
    (155, 0.32, 0.32, "n155_g032"),
    # n=160: predicted g*≈0.26
    (160, 0.22, 0.22, "n160_g022"),
    (160, 0.24, 0.24, "n160_g024"),
    (160, 0.26, 0.26, "n160_g026"),
    (160, 0.28, 0.28, "n160_g028"),
    # n=165: predicted g*≈0.24
    (165, 0.20, 0.20, "n165_g020"),
    (165, 0.22, 0.22, "n165_g022"),
    (165, 0.24, 0.24, "n165_g024"),
    (165, 0.26, 0.26, "n165_g026"),
    # n=170: predicted g*≈0.22
    (170, 0.18, 0.18, "n170_g018"),
    (170, 0.20, 0.20, "n170_g020"),
    (170, 0.22, 0.22, "n170_g022"),
    (170, 0.24, 0.24, "n170_g024"),
    # n=180: predicted g*≈0.18
    (180, 0.14, 0.14, "n180_g014"),
    (180, 0.16, 0.16, "n180_g016"),
    (180, 0.18, 0.18, "n180_g018"),
    (180, 0.20, 0.20, "n180_g020"),
]


def make_params(n_termites, g_form, g_persist):
    """Build params for the sweep."""
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["boundary_mode"] = "dual"
    p["g_form"] = g_form
    p["g_persist"] = g_persist
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "seeds": SEEDS,
        "combos": [(n, gf, gp, lbl) for n, gf, gp, lbl in COMBOS],
        "boundary_mode": "dual",
        "movement_bias": 0.3,
        "movement_mode": "focal",
        "jitter_mode": "per_step",
        "note": "Session 46: g*(n) scaling-law sweep (#129)",
        "linear_prediction": "g* = 0.90 - 0.004*n",
    }}

    for n_termites, g_form, g_persist, label in COMBOS:
        key = label
        results[key] = {"hetero_2seed": [], "hetero_1seed": []}
        density = n_termites / (GRID * GRID) * 1000
        print(f"\n  {label} (n={n_termites}, density={density:.2f}/kcell, "
              f"g=({g_form},{g_persist}))")

        p = make_params(n_termites, g_form, g_persist)

        for sd in SEEDS:
            # 2-seed
            r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
            s2 = r2["summary"]
            entry2 = {
                "seed": sd,
                "l2_crossed": s2["l2_crossed"],
                "l2_outcome": s2["l2_outcome"],
                "l2_stable": s2["l2_stable"],
                "crossed_h7": s2["crossed_h7"],
                "cells": s2["final_n_structure_cells"],
                "left_retain": round(s2["l2_left_retain"], 4),
                "right_retain": round(s2["l2_right_retain"], 4),
                "b_max": round(max((b["b_max"] for b in r2["boundary_trace"]),
                                  default=0.0), 2),
            }
            results[key]["hetero_2seed"].append(entry2)
            print(f"    2seed s={sd}: l2={s2['l2_crossed']} "
                  f"out={s2['l2_outcome']:>12s} stable={s2['l2_stable']} "
                  f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']}")

            # 1-seed control
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

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*120}")
    print("  G*(N) SCALING-LAW SWEEP SUMMARY (160x160, dual, focal 0.3, jit=10)")
    print(f"{'='*120}")
    print(f"{'label':>14s} {'nT':>5s} {'dens':>6s} {'g':>5s} | "
          f"{'l2(2s)':>7s} {'coexist':>8s} {'stable':>7s} {'h7(2s)':>7s} "
          f"{'clean':>6s} {'full':>6s} | "
          f"{'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 120)

    for n_termites, g_form, g_persist, label in COMBOS:
        h2 = results[label]["hetero_2seed"]
        h1 = results[label]["hetero_1seed"]
        n4 = len(SEEDS)
        density = n_termites / (GRID * GRID) * 1000
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
        g_str = f"{g_form:.2f}"
        print(f"{label:>14s} {n_termites:>5d} {density:>5.2f} {g_str:>5s} | "
              f"{n_l2_2:>3d}/{n4:<2d}  {n_coexist_2:>4d}/{n4:<3d}  "
              f"{n_stable_2:>3d}/{n4:<2d}  {n_h7_2:>3d}/{n4:<2d}  "
              f"{clean:>3d}/{n4:<2d}  {full:>3d}/{n4:<2d}  | "
              f"{n_l2_1:>3d}/{n4:<2d}  {n_h7_1:>3d}/{n4:<2d}  {mean_cells:>6d}")

    # Per-seed detail
    print(f"\n  Per-seed detail:")
    for n_termites, g_form, g_persist, label in COMBOS:
        h2 = results[label]["hetero_2seed"]
        h1 = results[label]["hetero_1seed"]
        print(f"  {label}:")
        for e2, e1 in zip(h2, h1):
            print(f"    s={e2['seed']:>4d}: 2s l2={e2['l2_crossed']} "
                  f"out={e2['l2_outcome']:>12s} stable={e2['l2_stable']} "
                  f"h7={e2['crossed_h7']} cells={e2['cells']:>5d} | "
                  f"1s l2={e1['l2_crossed']} h7={e1['crossed_h7']} "
                  f"cells={e1['cells']:>5d}")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
