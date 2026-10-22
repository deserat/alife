"""
High-gain boundary n-dependence sweep — queued-topic #235.

Session 85 confirmed the absolute-spatial-scale principle: the fill is
density-dependent without the focal bias (spread 2.23%) and n-dependent
with it (spread 23.38%). The focal bias was the SOLE source of n-dependence
at g=0 (no boundary). But at g=0.01 the boundary added <0.5% to the fill.

Does the boundary CONTRIBUTE to n-dependence at higher gains (g=0.3)?
At g=0.3 the boundary's suppression is strong enough to matter — it may
convert the fill's density-dependence into n-dependence independently of
the focal bias.

The 2×2:
  g=0,   bias=0: density-dependent (Session 85: 66.25 ≈ 66.49 ≈ 64.26%)
  g=0,   bias=0.3: n-dependent from focal bias (Session 85: 48.33 → 31.58 → 24.95%)
  g=0.3, bias=0: n-dependent from BOUNDARY? ← THE TEST
  g=0.3, bias=0.3: n-dependent from BOTH — how much more?

If g=0.3, bias=0 produces n-dependent fill (monotonic decrease with grid
size), the boundary DOES convert density-dependence into n-dependence at
high gain — partially rescuing the 53rd mechanism. If the fill is still
density-dependent (same across grid sizes), the 50th mechanism is entirely
from the focal bias, and the 53rd mechanism is fully falsified.

Combos (23.4/kc density, 3 grid sizes):
  80×80 n=150, 160×160 n=600, 320×320 n=2400
Each runs at g=0.3 × bias=[0.0, 0.3] + g=0 × bias=[0.0, 0.3] (4 conditions).
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "high_gain_boundary_sweep.json")

JITTER = 10.0
G_HIGH = 0.3  # high gain for the boundary

# Combos: (grid, n_termites, seeds)
COMBOS = [
    (80,  150,  [42, 123, 256, 999]),
    (160, 600,  [42, 123, 256, 999]),
    (320, 2400, [42, 999]),
]

# Conditions: (inh_gain, movement_bias, label)
CONDITIONS = [
    (0.0, 0.0, "g0_bias0"),
    (0.0, 0.3, "g0_bias03"),
    (G_HIGH, 0.0, "g03_bias0"),
    (G_HIGH, 0.3, "g03_bias03"),
]


def make_params(grid_size, n_termites, inh_gain, movement_bias):
    """Params for hetero mode at given gain and bias."""
    p = I14.curvature_params(inh_gain)
    p["grid_size"] = grid_size
    p["n_termites"] = n_termites
    p["movement_bias"] = movement_bias
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_one(grid, n, seeds, inh_gain, bias):
    """Run 2-seed at one (grid, n, gain, bias) combo. Return per-seed entries."""
    p = make_params(grid, n, inh_gain, bias)
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
            "note": "Session 86: high-gain boundary n-dependence (#235)",
            "jitter": JITTER,
            "density": "23.4kc",
            "grids": [80, 160, 320],
            "g_high": G_HIGH,
            "conditions": [c[2] for c in CONDITIONS],
            "prediction": "g=0.3 bias=0 n-dependent → boundary rescues 53rd mechanism; "
                         "density-dependent → 50th mechanism entirely from focal bias",
        },
    }

    print(f"\n{'='*90}")
    print("  HIGH-GAIN BOUNDARY N-DEPENDENCE SWEEP (#235)")
    print("  Testing: does the boundary convert density-dependence into n-dependence at g=0.3?")
    print(f"{'='*90}")

    for grid, n, seeds in COMBOS:
        density = n / (grid * grid) * 1000
        for inh_gain, bias, label in CONDITIONS:
            glabel = f"g={inh_gain}" if inh_gain > 0 else "g=0"
            blabel = f"bias={bias}" if bias > 0 else "bias=0"
            print(f"\n  {grid}×{grid} n={n} (dens={density:.1f}/kc) {glabel} {blabel} — "
                  f"{len(seeds)} seeds")
            t1 = time.time()
            entries = run_one(grid, n, seeds, inh_gain, bias)
            s = summarize(entries)
            key = f"{grid}_n{n}_{label}"
            results[key] = {
                "grid": grid, "n_termites": n, "density": "23.4kc",
                "density_per_kcell": round(density, 2),
                "inh_gain": inh_gain, "movement_bias": bias,
                "entries": entries,
                "summary": s,
            }
            elapsed = time.time() - t1
            print(f"  → fill={s['mean_fill_pct']:.2f}% l2={s['l2']} "
                  f"h7={s['h7']} cf={s['mean_coexist_frac']} ({elapsed:.0f}s)")

    # --- Comparison table ---
    print(f"\n{'='*90}")
    print("  FILL AT MATCHED DENSITY: 4 CONDITIONS × 3 GRIDS")
    print(f"{'='*90}")
    print(f"{'grid':>6s} | {'n':>6s} | {'g':>5s} | {'bias':>5s} | {'fill%':>7s} | {'l2':>5s} | {'h7':>5s} | {'cf':>6s}")
    print("-" * 90)

    for grid, n, seeds in COMBOS:
        for inh_gain, bias, label in CONDITIONS:
            key = f"{grid}_n{n}_{label}"
            if key not in results:
                continue
            s = results[key]["summary"]
            gstr = f"{inh_gain:.1f}" if inh_gain > 0 else "0"
            bstr = f"{bias:.1f}" if bias > 0 else "0"
            print(f"{grid:>6d} | {n:>6d} | {gstr:>5s} | {bstr:>5s} | "
                  f"{s['mean_fill_pct']:>6.2f}% | {s['l2']:>5s} | {s['h7']:>5s} | "
                  f"{s['mean_coexist_frac']:>6.3f}")

    # --- Verdict ---
    print(f"\n{'='*90}")
    print("  VERDICT: DOES THE BOUNDARY CONTRIBUTE TO N-DEPENDENCE AT HIGH GAIN?")
    print(f"{'='*90}")

    for inh_gain, bias, label in CONDITIONS:
        glabel = f"g={inh_gain}" if inh_gain > 0 else "g=0"
        blabel = f"bias={bias}" if bias > 0 else "bias=0"
        fills = []
        for grid, n, seeds in COMBOS:
            key = f"{grid}_n{n}_{label}"
            if key in results:
                fills.append(results[key]["summary"]["mean_fill_pct"])
        if len(fills) >= 2:
            spread = max(fills) - min(fills)
            fill_dec = all(fills[i] > fills[i+1] for i in range(len(fills)-1))
            print(f"\n  {glabel} {blabel}:")
            print(f"    fill = {fills}")
            print(f"    spread = {spread:.2f}%")
            if spread < 2.0:
                print(f"    → DENSITY-DEPENDENT (spread <2%)")
            elif fill_dec:
                print(f"    → N-DEPENDENT (monotonic decrease)")
            else:
                print(f"    → NON-MONOTONIC (spread={spread:.2f}%)")

    # --- Key comparison: g=0.3 bias=0 ---
    print(f"\n{'='*90}")
    print("  KEY COMPARISON: g=0.3 bias=0 (boundary only, no focal bias)")
    print(f"{'='*90}")
    g03_b0_fills = []
    for grid, n, seeds in COMBOS:
        key = f"{grid}_n{n}_g03_bias0"
        if key in results:
            g03_b0_fills.append(results[key]["summary"]["mean_fill_pct"])
    if len(g03_b0_fills) >= 2:
        spread = max(g03_b0_fills) - min(g03_b0_fills)
        fill_dec = all(g03_b0_fills[i] > g03_b0_fills[i+1]
                       for i in range(len(g03_b0_fills)-1))
        print(f"  fill = {g03_b0_fills}")
        print(f"  spread = {spread:.2f}%")
        if spread < 2.0:
            print(f"  → DENSITY-DEPENDENT — boundary does NOT convert at high gain")
            print(f"  → 50th mechanism entirely from focal bias; 53rd mechanism FULLY falsified")
        elif fill_dec:
            print(f"  → N-DEPENDENT (monotonic) — boundary DOES convert at high gain")
            print(f"  → 53rd mechanism PARTIALLY RESCUED at high gain")
            print(f"  → 50th mechanism has two components: focal bias + boundary (at high gain)")
        else:
            print(f"  → NON-MONOTONIC — inconclusive")

    # --- Determinism check ---
    print(f"\n{'='*90}")
    print("  DETERMINISM CHECK")
    print(f"{'='*90}")
    p = make_params(80, 150, G_HIGH, 0.0)
    r1 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    r2 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    det_ok = (r1["summary"]["final_n_structure_cells"] ==
              r2["summary"]["final_n_structure_cells"])
    print(f"  80×80 n=150 g=0.3 bias=0 seed=42: {'PASS' if det_ok else 'FAIL'} "
          f"({r1['summary']['final_n_structure_cells']} vs "
          f"{r2['summary']['final_n_structure_cells']})")
    results["determinism"] = {"passed": det_ok}

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
