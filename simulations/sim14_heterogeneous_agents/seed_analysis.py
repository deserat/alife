"""
Seed analysis — what distinguishes the 2/8 fragmenting seeds (100, 777)
from the 6/8 coexisting seeds at n=220 g=0.06?

Queued-topic #141: Is it nucleation trajectory (initial deposit scatter)
or dynamical (criterion flickering / late fragmentation)?

This probe runs all 8 seeds with time-series recording of:
  - left_components, right_components at each sample step
  - b_max, b_gap at each boundary trace step
  - total cells (material on surface)
  - l2_outcome at each time point (using rolling window)

Config: 160x160, dual mode (g_form=0.06, g_persist=0.06), focal bias=0.3,
  per_step jitter=10, n=220, 2 seeds.
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

PROBE_PATH = os.path.join(SIM14_DIR, "output", "seed_analysis.json")

GRID = 160
JITTER = 10.0
N220 = 220
SEEDS_8 = [42, 123, 256, 999, 7, 100, 555, 777]


def make_params():
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = N220
    p["boundary_mode"] = "dual"
    p["g_form"] = 0.06
    p["g_persist"] = 0.06
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_probe():
    t0 = time.time()
    p = make_params()
    results = {"config": {
        "grid": GRID, "n": N220, "g_form": 0.06, "g_persist": 0.06,
        "jitter": JITTER, "mode": "dual", "focal_bias": 0.3,
        "note": "Session 50: seed analysis — #141 what distinguishes "
                "fragmenting seeds from coexisting seeds",
    }}

    for sd in SEEDS_8:
        r = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s = r["summary"]
        hist = r["history"]

        # Extract time-series of component counts and totals
        lc_series = [rec.get("left_components", 0) for rec in hist]
        rc_series = [rec.get("right_components", 0) for rec in hist]
        steps_series = [rec.get("step", 0) for rec in hist]
        lt_series = [rec.get("left_total", 0) for rec in hist]
        rt_series = [rec.get("right_total", 0) for rec in hist]
        total_series = [rec.get("total_material", 0) for rec in hist]

        # Boundary trace
        bt = r["boundary_trace"]
        bt_steps = [b["step"] for b in bt]
        bt_bmax = [b["b_max"] for b in bt]
        bt_bgap = [b["b_gap"] for b in bt]

        # Final outcome
        outcome = s["l2_outcome"]
        is_fragmented = (outcome == "fragmented")

        # When does fragmentation appear? Find first step where lc or rc
        # exceeds COEXIST_MAX_COMP (3)
        COEXIST_MAX_COMP = 3
        frag_first_step = None
        for i, (lc, rc) in enumerate(zip(lc_series, rc_series)):
            if lc > COEXIST_MAX_COMP or rc > COEXIST_MAX_COMP:
                frag_first_step = steps_series[i]
                break

        # Mean component counts in early (first 25%) and late (last 25%)
        n = len(lc_series)
        q1 = max(1, n // 4)
        q3 = n - q1
        early_lc = np.mean(lc_series[:q1])
        late_lc = np.mean(lc_series[q3:])
        early_rc = np.mean(rc_series[:q1])
        late_rc = np.mean(rc_series[q3:])

        # Max component count over the whole run
        max_lc = max(lc_series)
        max_rc = max(rc_series)

        # Total cells
        final_cells = s.get("final_n_structure_cells", 0)

        entry = {
            "seed": sd,
            "outcome": outcome,
            "fragmented": is_fragmented,
            "final_cells": final_cells,
            "frag_first_step": frag_first_step,
            "early_lc": round(early_lc, 2),
            "early_rc": round(early_rc, 2),
            "late_lc": round(late_lc, 2),
            "late_rc": round(late_rc, 2),
            "max_lc": max_lc,
            "max_rc": max_rc,
            "lc_series": lc_series,
            "rc_series": rc_series,
            "steps_series": steps_series,
            "lt_series": [round(x, 1) for x in lt_series],
            "rt_series": [round(x, 1) for x in rt_series],
            "total_series": [round(x, 1) for x in total_series],
            "b_max_series": [round(x, 2) for x in bt_bmax],
            "b_gap_series": [round(x, 2) for x in bt_bgap],
            "bt_steps": bt_steps,
        }
        results[f"seed_{sd}"] = entry
        star = " *** FRAG" if is_fragmented else ""
        print(f"  seed={sd:>4d} out={outcome:>12s} cells={final_cells:>5d} "
              f"early_lc={early_lc:.1f} late_lc={late_lc:.1f} "
              f"max_lc={max_lc} max_rc={max_rc} "
              f"frag_step={frag_first_step}{star}")

    # Save
    os.makedirs(os.path.dirname(PROBE_PATH), exist_ok=True)
    with open(PROBE_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\nWrote {PROBE_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_probe()
