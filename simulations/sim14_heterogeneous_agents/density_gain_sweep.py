"""
Density-dependent boundary gain sweep — queued-topic #126.

Session 44 found over-fragmentation at n=175 (H7=4/4, coexist=1/4): the dual
boundary at g=0.3 over-splits each region into 4+ components. At n=150
(coexist=4/4, H7=2/4), C1 (stability ≥ 0.90) is the sole bottleneck, flickering
at 0.88–0.89.

This sweep tests whether the boundary gain g should scale with density:
- At n=175: lower g (0.15, 0.20, 0.25) — does weaker boundary reduce
  over-fragmentation while preserving H7?
- At n=150: higher g (0.35, 0.40) — does stronger boundary push stability
  above 0.90 and fire H7?
- Baseline g=0.30 at both densities for comparison.

Config: 160×160, dual mode, focal bias=0.3, per_step jitter=10.
4 seeds × {2,1} seeds × 6 (g,density) combos = 48 2-seed + 48 1-seed = 96 runs.

Methodology: 1-seed controls, determinism (2 runs diffed), per-seed outcomes.
Output: output/density_gain_sweep.json
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "density_gain_sweep.json")

GRID = 160
JITTER = 10.0
SEEDS = [42, 123, 256, 999]

# (n_termites, g_form, g_persist, label)
# n=175: lower g to fight over-fragmentation
# n=150: higher g to push stability above 0.90
COMBOS = [
    (150, 0.30, 0.30, "n150_g030"),  # baseline (Session 43/44)
    (150, 0.35, 0.35, "n150_g035"),
    (150, 0.40, 0.40, "n150_g040"),
    (175, 0.15, 0.15, "n175_g015"),
    (175, 0.20, 0.20, "n175_g020"),
    (175, 0.25, 0.25, "n175_g025"),
    (175, 0.30, 0.30, "n175_g030"),  # baseline (Session 43/44)
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
        "note": "Session 45: density-dependent boundary gain sweep (#126)",
    }}

    for n_termites, g_form, g_persist, label in COMBOS:
        key = label
        results[key] = {"hetero_2seed": [], "hetero_1seed": []}
        density = n_termites / (GRID * GRID) * 1000
        max_supp = max(g_form, g_persist)  # approximate max suppression
        print(f"\n  {label} (n={n_termites}, density={density:.2f}/kcell, "
              f"g=({g_form},{g_persist}), max_supp~{max_supp:.2f})")

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
    print(f"\n{'='*110}")
    print("  DENSITY-GAIN SWEEP SUMMARY (160×160, dual, focal 0.3, jit=10)")
    print(f"{'='*110}")
    print(f"{'label':>14s} {'nT':>5s} {'density':>8s} {'g':>5s} | "
          f"{'l2(2s)':>7s} {'coexist':>8s} {'stable':>7s} {'h7(2s)':>7s} "
          f"{'clean':>6s} {'full':>6s} | "
          f"{'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 110)

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
        print(f"{label:>14s} {n_termites:>5d} {density:>7.2f} {g_str:>5s} | "
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
