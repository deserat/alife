"""
Density scaling sweep for sim14 — queued-topic #119.

Session 38 found the 160×160 grid with 150 termites degrades: H7 drops to 2/4
at jitter=10, 0/4 at jitter≥20, and the 1-seed control leaks (2/4 at jit=20).
The same 150 termites on 4× the area produce sparser structures.

Does scaling n_termites with grid area (150→600 for 160×160, maintaining
constant termite density) rescue the 160×160 failure?

Sweep: grid_size [80, 160] × n_termites [150, 300, 600] × jitter [0, 10, 20]
       × 4 seeds × {2, 1} seeds.

If 160×600 matches 80×150 on all metrics → the problem is purely density-
dependent. If it doesn't → there's a grid-size effect beyond density.

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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "density_sweep.json")

# (grid_size, n_termites) combos — 80×150 is the baseline density.
# 160×600 = 4× area, 4× termites → same density.
# 160×150 = 4× area, 1× termites → 1/4 density (the failing case).
# 160×300 = 4× area, 2× termites → 1/2 density (intermediate).
COMBOS = [
    (80, 150),    # baseline: 150 termites on 80×80
    (160, 150),   # same termites, 4× area → 1/4 density
    (160, 300),   # 2× termites, 4× area → 1/2 density
    (160, 600),   # 4× termites, 4× area → same density
]
JITTERS = [0.0, 10.0, 20.0]
SEEDS = [42, 123, 256, 999]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "combos": [(gs, nt) for gs, nt in COMBOS],
        "jitters": JITTERS,
        "seeds": SEEDS,
        "boundary_mode": "dual",
        "g_form": 0.3,
        "g_persist": 0.3,
        "movement_bias": 0.3,
        "movement_mode": "focal",
        "jitter_mode": "per_step",
    }}

    for gs, nt in COMBOS:
        density = nt / (gs * gs) * 1000  # termites per 1000 cells
        for jit in JITTERS:
            key = f"grid_{gs}_n{nt}_jitter_{jit}"
            results[key] = {"hetero_2seed": [], "hetero_1seed": []}
            print(f"\n{'='*60}")
            print(f"  grid={gs} n_termites={nt} jitter={jit} "
                  f"(density={density:.2f}/kcells, jitter/grid={jit/gs*100:.1f}%)")
            print(f"{'='*60}")

            p = I14.curvature_params(0.5)
            p["grid_size"] = gs
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
                print(f"  grid={gs} n={nt} jit={jit} 2seed s={sd}: "
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
    print("  DENSITY SCALING SWEEP SUMMARY (dual f=0.3 p=0.3, focal bias=0.3)")
    print(f"{'='*130}")
    print(f"{'grid':>5s} {'nT':>5s} {'density':>8s} {'jit':>5s} {'frac%':>6s} | "
          f"{'l2(2s)':>7s} {'coexist':>8s} {'stable':>7s} {'h7(2s)':>7s} "
          f"{'clean':>6s} {'full':>6s} | {'l2(1s)':>7s} {'h7(1s)':>7s} "
          f"{'cells':>6s}")
    print("-" * 130)

    for gs, nt in COMBOS:
        density = nt / (gs * gs) * 1000
        for jit in JITTERS:
            key = f"grid_{gs}_n{nt}_jitter_{jit}"
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
            frac = jit / gs * 100
            print(f"{gs:>5d} {nt:>5d} {density:>7.2f} {jit:>5.1f} {frac:5.1f}% | "
                  f"{n_l2_2:>4d}/4  {n_coexist_2:>5d}/4  {n_stable_2:>4d}/4  "
                  f"{n_h7_2:>4d}/4  {clean:>4d}/4  {full:>4d}/4  | "
                  f"{n_l2_1:>4d}/4  {n_h7_1:>4d}/4  {mean_cells:>6d}")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
