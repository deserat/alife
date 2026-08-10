"""Sweep inh_gain for sim11: find the regime where inhibition creates a
boundary between two structures WITHOUT killing the single-structure crossing
(the L1 control must still cross H7).

Tests: inh_gain in {0.0, 0.05, 0.10, 0.15, 0.20, 0.30} × {1, 2} seeds,
seed=42 (one seed per cell — a quick probe, not a robustness pass).
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

OUT = os.path.join(SIM11_DIR, "output", "inh_gain_sweep.json")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

GAINS = [0.0, 0.3, 0.5, 0.7, 0.9, 0.95, 0.99]
SEED = 42

t0 = time.time()
results = {"config": {"gains": GAINS, "seed": SEED}, "runs": []}

for g in GAINS:
    for n_seeds in (2, 1):
        p = E.curvature_params(g if g > 0 else 0.0)
        inhibited = g > 0.0
        r = E.run_two_region_inhibited(p, seed=SEED, n_seeds=n_seeds,
                                       inhibited=inhibited)
        s = r["summary"]
        row = {
            "inh_gain": g, "n_seeds": n_seeds,
            "l2_crossed": s["l2_crossed"], "l2_outcome": s["l2_outcome"],
            "l2_stable": s["l2_stable"],
            "l2_left_retain": round(s["l2_left_retain"], 3),
            "l2_right_retain": round(s["l2_right_retain"], 3),
            "crossed_h7": s["crossed_h7"],
            "final_cells": s["final_n_structure_cells"],
            "final_material": round(s["final_total_material"], 1),
        }
        results["runs"].append(row)
        tag = "INH" if inhibited else "NOINH"
        print(f"  g={g:.2f} seeds={n_seeds} [{tag}] "
              f"l2={str(row['l2_crossed']):5s} "
              f"outcome={row['l2_outcome']:12s} "
              f"h7={str(row['crossed_h7']):5s} "
              f"cells={row['final_cells']} "
              f"mat={row['final_material']:.0f}")

with open(OUT, "w") as f:
    json.dump(json.loads(json.dumps(results)), f, indent=2)
print(f"\nWrote {OUT}  ({time.time()-t0:.1f}s)")
