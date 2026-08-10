"""Multi-seed robustness sweep for sim11's inhibition boundary.

At g=0.9, the 2-seed fires 'coexist' while the 1-seed fires 'none' (seed 42).
This is the critical comparison: the 1-seed control FAILS while the 2-seed
Fires. But is this robust across seeds, or is it a seed-42 artifact?

Tests: inh_gain in {0.0, 0.7, 0.9, 0.95} × seeds {42, 123, 256, 999} ×
{1, 2} seeds. Reports l2_crossed, l2_outcome, l2_stable, and the critical
2-seed-vs-1-seed comparison.
"""
import os
import sys
import json
import time

import numpy as np

SIM11_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM11_DIR)
import sim11 as E  # noqa: E402
import sim09 as S  # noqa: E402

OUT = os.path.join(SIM11_DIR, "output", "robustness_sweep.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

GAINS = [0.0, 0.7, 0.9, 0.95]
SEEDS = [42, 123, 256, 999]

t0 = time.time()
results = {"config": {"gains": GAINS, "seeds": SEEDS}, "runs": []}

for g in GAINS:
    for seed in SEEDS:
        for n_seeds in (2, 1):
            p = E.curvature_params(g if g > 0 else 0.0)
            inhibited = g > 0.0
            r = E.run_two_region_inhibited(p, seed=seed, n_seeds=n_seeds,
                                           inhibited=inhibited)
            s = r["summary"]
            row = {
                "inh_gain": g, "seed": seed, "n_seeds": n_seeds,
                "l2_crossed": s["l2_crossed"],
                "l2_outcome": s["l2_outcome"],
                "l2_stable": s["l2_stable"],
                "l2_left_retain": round(s["l2_left_retain"], 3),
                "l2_right_retain": round(s["l2_right_retain"], 3),
                "crossed_h7": s["crossed_h7"],
                "final_cells": s["final_n_structure_cells"],
                "final_material": round(s["final_total_material"], 1),
            }
            results["runs"].append(row)
            tag = "INH" if inhibited else "NOINH"
            print(f"  g={g:.2f} seed={seed:3d} n={n_seeds} [{tag}] "
                  f"l2={str(row['l2_crossed']):5s} stab={str(row['l2_stable']):5s} "
                  f"outcome={row['l2_outcome']:12s} "
                  f"h7={str(row['crossed_h7']):5s} "
                  f"cells={row['final_cells']}")

# Summary: per-gain, per-n_seeds pass rates
print("\n=== SUMMARY (pass rates across 4 seeds) ===")
for g in GAINS:
    for n_seeds in (2, 1):
        runs = [r for r in results["runs"]
                if r["inh_gain"] == g and r["n_seeds"] == n_seeds]
        n = len(runs)
        l2_count = sum(1 for r in runs if r["l2_crossed"])
        coexist = sum(1 for r in runs if r["l2_outcome"] == "coexist")
        stable = sum(1 for r in runs if r["l2_stable"])
        h7 = sum(1 for r in runs if r["crossed_h7"])
        print(f"  g={g:.2f} n={n_seeds}: l2_crossed={l2_count}/{n} "
              f"coexist={coexist}/{n} stable={stable}/{n} h7={h7}/{n}")

with open(OUT, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nWrote {OUT}  ({time.time()-t0:.1f}s)")
