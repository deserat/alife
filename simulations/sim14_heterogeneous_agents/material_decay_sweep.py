"""
Material decay sweep — is the fill cap from the curvature channel's
deposit/excavate balance or from material decay?

Queued-topic #284. Session 112 falsified the 44th mechanism (boundary does
NOT cap fill — gap <1pp at all densities). The fill cap is from the curvature
channel + focal bias. But is it from:
  (a) the deposit/excavate balance (curvature routing deposits at concavities
      and excavates at convexities, limiting growth), or
  (b) material decay (material_decay=0.002, a fixed removal rate that caps
      fill at the equilibrium between deposition and decay)?

Test: sweep material_decay at fixed n (no-inhibition, hetero mode).
- If higher decay → lower fill, the fill cap is from material decay.
- If fill is insensitive to decay, the fill cap is from the deposit/excavate
  balance (the curvature routing self-limits growth).

We test at n=2500, 5000, 10000 on 160×160 (the same densities as the
boundary capping test, Session 112). No boundary (g=0) to isolate the
curvature channel's effect.

Also: we test WITH boundary (dual, g=0.001) at the same decay values to
see if the boundary's composition effect (coexist_frac, stable_l2) is
decay-dependent.
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

GRID = 160
JITTER = 10.0
SEEDS = [42, 123, 256, 999]
DECAYS = [0.0005, 0.001, 0.002, 0.004, 0.008, 0.016, 0.032]
DENSITIES = [2500, 5000, 10000]


def make_no_inhib_params(n_termites, decay):
    """No boundary (hetero, g=0), with specified material_decay."""
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["material_decay"] = decay
    p["movement_bias"] = 0.3
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def make_with_boundary_params(n_termites, decay):
    """With boundary (dual, g=0.001), with specified material_decay."""
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["material_decay"] = decay
    p["boundary_mode"] = "dual"
    p["g_form"] = 0.001
    p["g_persist"] = 0.001
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def measure(n_termites, decay, with_boundary, seed):
    """Run one simulation and return fill + composition metrics."""
    if with_boundary:
        p = make_with_boundary_params(n_termites, decay)
        r = I14.run_two_region_hetero(p, seed=seed, n_seeds=2, mode="hetero")
    else:
        p = make_no_inhib_params(n_termites, decay)
        r = I14.run_two_region_hetero(p, seed=seed, n_seeds=2, mode="hetero")

    s = r["summary"]
    cells = s["final_n_structure_cells"]
    fill_pct = 100.0 * cells / (GRID * GRID)
    return {
        "cells": cells,
        "fill_pct": round(fill_pct, 2),
        "l2_crossed": s["l2_crossed"],
        "l2_outcome": s["l2_outcome"],
        "l2_stable": s["l2_stable"],
        "crossed_h7": s["crossed_h7"],
        "coexist_frac": round(s.get("l2_coexist_frac", 0.0), 4),
        "late_mean_lc": round(s.get("l2_late_mean_lc", 0.0), 2),
        "late_mean_rc": round(s.get("l2_late_mean_rc", 0.0), 2),
    }


def run_sweep():
    t0 = time.time()
    results = {
        "description": "Material decay sweep — is the fill cap from "
                       "deposit/excavate balance or material decay? "
                       "(queued-topic #284)",
        "grid": GRID,
        "jitter": JITTER,
        "seeds": SEEDS,
        "decays": DECAYS,
        "densities": DENSITIES,
        "date": "2026-11-16",
    }

    print("=" * 80)
    print("MATERIAL DECAY SWEEP — queued-topic #284")
    print("=" * 80)
    print()

    # Part 1: no-inhibition fill vs material_decay at 3 densities
    print("Part 1: no-inhibition fill vs material_decay")
    print("-" * 70)

    for n in DENSITIES:
        print(f"\n  n={n}:")
        decay_results = {}
        for decay in DECAYS:
            fills = []
            for sd in SEEDS:
                m = measure(n, decay, with_boundary=False, seed=sd)
                fills.append(m)
                print(f"    decay={decay:.4f} s={sd}: "
                      f"fill={m['fill_pct']:.2f}%  h7={m['crossed_h7']}  "
                      f"lc={m['late_mean_lc']} rc={m['late_mean_rc']}")
            mean_fill = np.mean([m["fill_pct"] for m in fills])
            mean_lc = np.mean([m["late_mean_lc"] for m in fills])
            mean_rc = np.mean([m["late_mean_rc"] for m in fills])
            h7_count = sum(1 for m in fills if m["crossed_h7"])
            print(f"    MEAN: fill={mean_fill:.2f}%  "
                  f"lc={mean_lc:.2f} rc={mean_rc:.2f}  h7={h7_count}/4")
            decay_results[str(decay)] = {
                "fills": fills,
                "mean_fill": round(mean_fill, 2),
                "mean_lc": round(mean_lc, 2),
                "mean_rc": round(mean_rc, 2),
                "h7_count": h7_count,
            }
        results[f"no_inhib_n{n}"] = decay_results

    # Part 2: with-boundary composition vs material_decay at n=2500
    # (to see if boundary's composition effect is decay-dependent)
    print("\n\nPart 2: with-boundary composition vs material_decay at n=2500")
    print("-" * 70)

    n = 2500
    wb_results = {}
    for decay in DECAYS:
        fills = []
        for sd in SEEDS:
            m = measure(n, decay, with_boundary=True, seed=sd)
            fills.append(m)
            print(f"    decay={decay:.4f} s={sd}: "
                  f"fill={m['fill_pct']:.2f}%  h7={m['crossed_h7']}  "
                  f"l2={m['l2_crossed']} stable={m['l2_stable']}  "
                  f"cf={m['coexist_frac']}  "
                  f"outcome={m['l2_outcome']}")
        mean_fill = np.mean([m["fill_pct"] for m in fills])
        mean_cf = np.mean([m["coexist_frac"] for m in fills])
        stable_count = sum(1 for m in fills if m["l2_stable"])
        coexist_count = sum(1 for m in fills if m["l2_outcome"] == "coexist")
        h7_count = sum(1 for m in fills if m["crossed_h7"])
        print(f"    MEAN: fill={mean_fill:.2f}%  cf={mean_cf:.4f}  "
              f"stable={stable_count}/4  coexist={coexist_count}/4  "
              f"h7={h7_count}/4")
        wb_results[str(decay)] = {
            "fills": fills,
            "mean_fill": round(mean_fill, 2),
            "mean_cf": round(mean_cf, 4),
            "stable_count": stable_count,
            "coexist_count": coexist_count,
            "h7_count": h7_count,
        }
    results["with_boundary_n2500"] = wb_results

    # Summary analysis
    print("\n\nSUMMARY")
    print("=" * 80)

    # Fill sensitivity to decay (no-inhibition)
    print("\nFill sensitivity to material_decay (no-inhibition):")
    for n in DENSITIES:
        key = f"no_inhib_n{n}"
        fills = [results[key][str(d)]["mean_fill"] for d in DECAYS]
        spread = max(fills) - min(fills)
        print(f"  n={n}: fill range {fills[0]:.1f}% → {fills[-1]:.1f}%  "
              f"spread={spread:.1f}pp  "
              f"({'decay-driven' if spread > 10 else 'decay-insensitive'})")

    # With-boundary composition vs decay
    print("\nWith-boundary composition vs material_decay (n=2500):")
    for d in DECAYS:
        r = results["with_boundary_n2500"][str(d)]
        print(f"  decay={d:.4f}: fill={r['mean_fill']:.1f}%  "
              f"cf={r['mean_cf']:.4f}  stable={r['stable_count']}/4  "
              f"coexist={r['coexist_count']}/4  h7={r['h7_count']}/4")

    elapsed = time.time() - t0
    results["elapsed_seconds"] = round(elapsed, 1)
    print(f"\n\nElapsed: {elapsed:.1f}s")

    out_path = os.path.join(SIM14_DIR, "output", "material_decay_sweep.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {out_path}")

    return results, elapsed


if __name__ == "__main__":
    run_sweep()
