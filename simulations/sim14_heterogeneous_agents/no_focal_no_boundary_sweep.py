"""
No-focal no-boundary sweep — queued-topic #236.

Session 84 falsified the 53rd mechanism: the fill's n-dependence comes
from the focal bias (1-cell steps toward a fixed home center — an absolute
spatial scale), not the boundary. The boundary adds <0.5% at g=0.01.

But is the focal bias the ONLY source of n-dependence? Without ANY
absolute-spatial-scale mechanism (no focal bias, no boundary), is the
fill density-dependent (same at matched density across grid sizes) or
still n-dependent?

This script runs mode="hetero" with g=0 and movement_bias=0 — ID-tagged
deposits, no focal bias, no boundary — at matched density across three
grid sizes. If the fill is the same, the absolute-spatial-scale principle
(#234) is confirmed: the focal bias was the sole source. If the fill
still decreases with grid size, another absolute spatial scale (the 1-cell
step, the 1-cell curvature stencil, the 1-cell Moore dilation) causes
n-dependence.

Combos (23.4/kc density, 3 grid sizes):
  80×80 n=150, 160×160 n=600, 320×320 n=2400

Each combo runs with movement_bias=0 (no focal) AND movement_bias=0.3
(focal, for comparison with Session 84's data).
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "no_focal_no_boundary_sweep.json")

JITTER = 10.0

# Combos: (grid, n_termites, seeds)
COMBOS = [
    (80,  150,  [42, 123, 256, 999]),
    (160, 600,  [42, 123, 256, 999]),
    (320, 2400, [42, 999]),
]


def make_params(grid_size, n_termites, movement_bias):
    """Params for hetero mode, g=0, given grid/n/bias."""
    p = I14.curvature_params(0.0)  # no boundary
    p["grid_size"] = grid_size
    p["n_termites"] = n_termites
    p["movement_bias"] = movement_bias
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_one(grid, n, seeds, bias):
    """Run 2-seed at one (grid, n, bias) combo. Return per-seed entries."""
    p = make_params(grid, n, bias)
    grid_area = grid * grid
    entries = []
    for sd in seeds:
        r = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s = r["summary"]
        e = {
            "seed": sd,
            "l2_crossed": s["l2_crossed"],
            "l2_outcome": s["l2_outcome"],
            "l2_stable": s["l2_stable"],
            "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
            "crossed_h7": s["crossed_h7"],
            "cells": s["final_n_structure_cells"],
            "fill_pct": round(s["final_n_structure_cells"] / grid_area * 100, 2),
        }
        entries.append(e)
    return entries


def summarize(entries):
    n = len(entries)
    return {
        "l2": f"{sum(1 for e in entries if e['l2_crossed'])}/{n}",
        "coexist": f"{sum(1 for e in entries if e['l2_outcome'] == 'coexist')}/{n}",
        "stable": f"{sum(1 for e in entries if e['l2_stable'])}/{n}",
        "h7": f"{sum(1 for e in entries if e['crossed_h7'])}/{n}",
        "mean_fill_pct": round(float(np.mean([e["fill_pct"] for e in entries])), 2),
        "mean_coexist_frac": round(float(np.mean([e["l2_coexist_frac"] for e in entries])), 3),
        "mean_cells": int(np.mean([e["cells"] for e in entries])),
    }


def run_sweep():
    t0 = time.time()
    results = {
        "config": {
            "note": "Session 85: no-focal no-boundary (#236)",
            "jitter": JITTER,
            "density": "23.4kc",
            "grids": [80, 160, 320],
            "biases": [0.0, 0.3],
            "inh_gain": 0.0,
            "prediction": "fill density-dependent without focal bias (same at matched density)",
        },
    }

    print(f"\n{'='*90}")
    print("  NO-FOCAL NO-BOUNDARY SWEEP (#236)")
    print("  Testing: is the fill density-dependent without ANY absolute-spatial-scale mechanism?")
    print(f"{'='*90}")

    for grid, n, seeds in COMBOS:
        density = n / (grid * grid) * 1000
        for bias in [0.0, 0.3]:
            blabel = "bias=0 (no focal)" if bias == 0.0 else "bias=0.3 (focal)"
            print(f"\n  {grid}×{grid} n={n} (dens={density:.1f}/kc) {blabel} — "
                  f"{len(seeds)} seeds")
            t1 = time.time()
            entries = run_one(grid, n, seeds, bias)
            s = summarize(entries)
            key = f"{grid}_n{n}_bias{bias}"
            results[key] = {
                "grid": grid, "n_termites": n, "density": "23.4kc",
                "density_per_kcell": round(density, 2),
                "movement_bias": bias,
                "inh_gain": 0.0,
                "entries": entries,
                "summary": s,
            }
            elapsed = time.time() - t1
            print(f"  → fill={s['mean_fill_pct']:.2f}% l2={s['l2']} "
                  f"h7={s['h7']} cf={s['mean_coexist_frac']} ({elapsed:.0f}s)")

    # --- Comparison table ---
    print(f"\n{'='*90}")
    print("  FILL AT MATCHED DENSITY: NO-FOCAL vs FOCAL (NO BOUNDARY)")
    print(f"{'='*90}")
    print(f"{'grid':>6s} | {'n':>6s} | {'bias':>5s} | {'fill%':>7s} | {'l2':>5s} | {'h7':>5s} | {'cf':>6s}")
    print("-" * 90)

    for grid, n, seeds in COMBOS:
        for bias in [0.0, 0.3]:
            key = f"{grid}_n{n}_bias{bias}"
            if key not in results:
                continue
            s = results[key]["summary"]
            blabel = "0.0" if bias == 0.0 else "0.3"
            print(f"{grid:>6d} | {n:>6d} | {blabel:>5s} | {s['mean_fill_pct']:>6.2f}% | "
                  f"{s['l2']:>5s} | {s['h7']:>5s} | {s['mean_coexist_frac']:>6.3f}")

    # --- Verdict ---
    print(f"\n{'='*90}")
    print("  VERDICT: IS THE FILL DENSITY-DEPENDENT WITHOUT FOCAL BIAS?")
    print(f"{'='*90}")

    for bias in [0.0, 0.3]:
        blabel = "bias=0 (no focal)" if bias == 0.0 else "bias=0.3 (focal)"
        fills = []
        for grid, n, seeds in COMBOS:
            key = f"{grid}_n{n}_bias{bias}"
            if key in results:
                fills.append(results[key]["summary"]["mean_fill_pct"])
        if len(fills) >= 2:
            fill_dec = all(fills[i] > fills[i+1] for i in range(len(fills)-1))
            spread = max(fills) - min(fills)
            print(f"\n  {blabel}:")
            print(f"    fill = {fills}")
            print(f"    spread = {spread:.2f}%")
            if bias == 0.0:
                if spread < 2.0:
                    print(f"    → DENSITY-DEPENDENT (spread <2%) — absolute-spatial-scale principle CONFIRMED")
                elif fill_dec:
                    print(f"    → N-DEPENDENT (monotonic decrease) — another absolute spatial scale causes n-dependence")
                else:
                    print(f"    → INCONCLUSIVE (non-monotonic, spread={spread:.2f}%)")
            else:
                if fill_dec:
                    print(f"    → N-DEPENDENT (monotonic decrease) — focal bias causes n-dependence (confirmed)")

    # --- Determinism check ---
    print(f"\n{'='*90}")
    print("  DETERMINISM CHECK")
    print(f"{'='*90}")
    p = make_params(80, 150, 0.0)
    r1 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    r2 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    det_ok = (r1["summary"]["final_n_structure_cells"] == r2["summary"]["final_n_structure_cells"])
    print(f"  80×80 n=150 bias=0 seed=42: {'PASS' if det_ok else 'FAIL'} "
          f"({r1['summary']['final_n_structure_cells']} vs {r2['summary']['final_n_structure_cells']})")
    results["determinism"] = {"passed": det_ok}

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
