"""
Growth-Suppression Balance Analysis (Session 99)

Derives the 30th ceiling from growth_rate ≈ suppression_rate.
Minimal version: 3 n values × 1 seed × 2 conditions + 1000 steps.
"""

import os
import sys
import json
import time

import numpy as np

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM_DIR)

import sim14 as S14

OUTPUT_DIR = os.path.join(SIM_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SEED = 42
N_VALUES = [1000, 2000, 3000]
GRID = 160
STEPS = 1000
SAMPLE = 50
JITTER = 10.0


def make_params(n, inh_gain):
    p = S14.curvature_params(inh_gain)
    p["grid_size"] = GRID
    p["n_termites"] = n
    p["steps"] = STEPS
    p["sample_every"] = SAMPLE
    if inh_gain > 0.0:
        p["boundary_mode"] = "dual"
        p["g_form"] = inh_gain
        p["g_persist"] = inh_gain
    else:
        p["boundary_mode"] = "proportional"
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    p["recruit_response"] = "linear"
    p["inh_gain"] = inh_gain
    return p


def run_one(n, seed, inh_gain):
    params = make_params(n, inh_gain)
    result = S14.run_two_region_hetero(params, seed=seed, n_seeds=2,
                                        mode="hetero")
    history = result["history"]
    btrace = result["boundary_trace"]

    ts = []
    for h, bt in zip(history, btrace):
        cells = h["n_structure_cells"]
        fill_pct = 100.0 * cells / (GRID * GRID)
        deposits = h.get("deposits_this_window", 0)
        excavations = h.get("excavations_this_window", 0)
        pickups = h.get("pickups_this_window", 0)
        growth_rate = (deposits - excavations - pickups) / SAMPLE
        ts.append({
            "step": h["step"],
            "cells": cells,
            "fill_pct": fill_pct,
            "growth_rate": growth_rate,
            "b_max": bt["b_max"],
        })

    late = [r for r in ts if r["step"] >= STEPS * 0.7]
    if not late:
        late = ts[-3:]
    ss_fill = float(np.mean([r["fill_pct"] for r in late]))
    ss_cells = float(np.mean([r["cells"] for r in late]))
    ss_bmax = float(np.mean([r["b_max"] for r in late]))

    early = [r for r in ts if r["step"] < STEPS * 0.25]
    if len(early) >= 3:
        xs = np.array([r["step"] for r in early], dtype=float)
        ys = np.array([r["cells"] for r in early], dtype=float)
        growth_slope = float(np.polyfit(xs, ys, 1)[0])
    else:
        growth_slope = 0.0

    return {
        "n": n,
        "seed": seed,
        "inh_gain": inh_gain,
        "ss_fill_pct": ss_fill,
        "ss_cells": ss_cells,
        "ss_bmax": ss_bmax,
        "early_growth_rate": growth_slope,
        "time_series": ts,
    }


def main():
    results = {
        "config": {
            "grid": GRID, "steps": STEPS, "seed": SEED,
            "n_values": N_VALUES, "g_boundary": 0.001,
        },
        "runs": [],
    }

    for n in N_VALUES:
        for inh_gain, label in [(0.001, "with_boundary"), (0.0, "no_boundary")]:
            t0 = time.time()
            r = run_one(n, SEED, inh_gain)
            r["condition"] = label
            r["elapsed_s"] = round(time.time() - t0, 1)
            results["runs"].append(r)
            print(f"  n={n} {label}: fill={r['ss_fill_pct']:.1f}% "
                  f"growth={r['early_growth_rate']:.1f} "
                  f"bmax={r['ss_bmax']:.1f} ({r['elapsed_s']:.0f}s)")

    balance = []
    for n in N_VALUES:
        wb = [r for r in results["runs"]
              if r["n"] == n and r["condition"] == "with_boundary"]
        nb = [r for r in results["runs"]
              if r["n"] == n and r["condition"] == "no_boundary"]
        if not wb or not nb:
            continue
        fill_wb = wb[0]["ss_fill_pct"]
        fill_nb = nb[0]["ss_fill_pct"]
        growth_wb = wb[0]["early_growth_rate"]
        growth_nb = nb[0]["early_growth_rate"]
        bmax_wb = wb[0]["ss_bmax"]
        suppression = fill_nb - fill_wb

        balance.append({
            "n": n,
            "fill_with_boundary_pct": float(fill_wb),
            "fill_no_boundary_pct": float(fill_nb),
            "suppression_capacity_pct": float(suppression),
            "growth_rate_with": float(growth_wb),
            "growth_rate_without": float(growth_nb),
            "b_max": float(bmax_wb),
            "growth_per_n": float(growth_nb / n),
            "suppression_per_sqrt_n": float(suppression / np.sqrt(n)),
        })

    results["balance"] = balance
    results["ceiling_reference"] = {
        "last_stable_n": 2500,
        "last_stable_fill": 42.08,
        "first_unstable_n": 3000,
        "first_unstable_fill": 43.63,
        "measured_ceiling_fill_pct": 43.6,
        "source": "Session 94 percolation_threshold_analysis",
    }

    # Determinism
    det1 = run_one(2000, SEED, 0.001)
    det2 = run_one(2000, SEED, 0.001)
    det_match = abs(det1["ss_cells"] - det2["ss_cells"]) < 0.01
    results["determinism"] = {
        "n": 2000, "seed": SEED, "match": det_match,
        "cells_1": det1["ss_cells"], "cells_2": det2["ss_cells"],
    }

    out_path = os.path.join(OUTPUT_DIR, "growth_suppression_balance.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {out_path}")
    print(f"Determinism: {'PASS' if det_match else 'FAIL'}")

    print("\n=== Growth-Suppression Balance ===")
    print(f"{'n':>6} {'fill_wb':>8} {'fill_nb':>8} {'supp':>7} "
          f"{'growth':>8} {'g/n':>8} {'s/√n':>8}")
    for b in balance:
        print(f"{b['n']:6d} {b['fill_with_boundary_pct']:8.2f} "
              f"{b['fill_no_boundary_pct']:8.2f} "
              f"{b['suppression_capacity_pct']:7.2f} "
              f"{b['growth_rate_without']:8.1f} "
              f"{b['growth_per_n']:8.4f} "
              f"{b['suppression_per_sqrt_n']:8.3f}")


if __name__ == "__main__":
    main()
