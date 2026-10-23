"""
Finer gain sweep — queued-topic #239.

Session 86 found the boundary at g=0.3 (bias=0, no focal) produces a small
n-dependent effect (fill 54.92→54.14→51.61%, spread 3.31%). At g=0 (bias=0)
the fill is density-dependent (spread 2.23%). Where does the transition from
negligible (<0.5%) to visible (3.31%) n-dependence happen?

This sweep maps the transition at finer gain resolution:
  g = 0.0, 0.05, 0.1, 0.15, 0.2, 0.3 — all at bias=0 (no focal bias).
  80×80 (n=150, 4 seeds) and 160×160 (n=600, 2 seeds).
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "finer_gain_sweep.json")

JITTER = 10.0

COMBOS = [
    (80,  150, [42, 123, 256, 999]),
    (160, 600, [42, 999]),
]

GAINS = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3]


def make_params(grid_size, n_termites, inh_gain):
    p = I14.curvature_params(inh_gain)
    p["grid_size"] = grid_size
    p["n_termites"] = n_termites
    p["movement_bias"] = 0.0
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_one(grid, n, seeds, inh_gain):
    p = make_params(grid, n, inh_gain)
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
            "note": "Session 87: finer gain sweep — transition from negligible to visible boundary n-dependence (#239)",
            "jitter": JITTER,
            "density": "23.4kc",
            "grids": [80, 160],
            "gains": GAINS,
            "bias": 0.0,
        },
    }

    print(f"\n{'='*80}")
    print("  FINER GAIN SWEEP (#239)")
    print(f"  Gains: {GAINS}  bias=0  grids: 80×80(4s) 160×160(2s)")
    print(f"{'='*80}")

    for g in GAINS:
        for grid, n, seeds in COMBOS:
            density = n / (grid * grid) * 1000
            print(f"\n  {grid}×{grid} n={n} g={g} bias=0 — {len(seeds)} seeds", flush=True)
            t1 = time.time()
            entries = run_one(grid, n, seeds, g)
            s = summarize(entries)
            key = f"g{g}_{grid}_n{n}"
            results[key] = {
                "gain": g, "grid": grid, "n_termites": n,
                "density_per_kcell": round(density, 2),
                "bias": 0.0,
                "entries": entries, "summary": s,
            }
            elapsed = time.time() - t1
            print(f"  → fill={s['mean_fill_pct']:.2f}% l2={s['l2']} "
                  f"h7={s['h7']} ({elapsed:.0f}s)", flush=True)

    # --- Spread analysis ---
    print(f"\n{'='*80}")
    print("  SPREAD ANALYSIS", flush=True)
    print(f"{'='*80}", flush=True)
    print(f"{'g':>6s} | {'80×80':>10s} | {'160×160':>10s} | {'spread':>8s}", flush=True)
    print("-" * 80, flush=True)

    spread_data = []
    for g in GAINS:
        fills = []
        for grid, n, seeds in COMBOS:
            key = f"g{g}_{grid}_n{n}"
            if key in results:
                fills.append(results[key]["summary"]["mean_fill_pct"])
        if len(fills) >= 2:
            spread = abs(fills[0] - fills[1])
            spread_data.append({"g": g, "fills": fills, "spread": round(spread, 3)})
            verdict = "DENSITY-DEP" if spread < 2.0 else "N-DEPENDENT"
            print(f"{g:>6.2f} | {fills[0]:>9.2f}% | {fills[1]:>9.2f}% | {spread:>7.2f}%  {verdict}", flush=True)

    results["spread_analysis"] = spread_data

    # --- Transition analysis ---
    print(f"\n  g → spread curve:", flush=True)
    for sd in spread_data:
        print(f"    g={sd['g']:.2f}: spread={sd['spread']:.2f}%  fills={sd['fills']}", flush=True)

    first_n = None
    for sd in spread_data:
        if sd["spread"] > 2.0:
            first_n = sd["g"]
            break
    if first_n is not None:
        print(f"\n  First gain where spread > 2%: g = {first_n}", flush=True)
    else:
        print(f"\n  No gain produces spread > 2%", flush=True)
    results["transition"] = {"first_n_dependent_gain": first_n, "threshold": 2.0}

    # --- Determinism check ---
    print(f"\n  Determinism check...", flush=True)
    p = make_params(80, 150, 0.15)
    r1 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    r2 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    det_ok = (r1["summary"]["final_n_structure_cells"] ==
              r2["summary"]["final_n_structure_cells"])
    print(f"  80×80 n=150 g=0.15 bias=0 seed=42: {'PASS' if det_ok else 'FAIL'}", flush=True)
    results["determinism"] = {"passed": det_ok}

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)", flush=True)
    return results


if __name__ == "__main__":
    run_sweep()
