"""
Ceiling decay sweep — is the ~44% persistence ceiling universal
across decay values, or is it a decay-dependent equilibrium?

Queued-topic #295 (re-prioritization of #285).

Session 113 showed the fill is the deposit/decay equilibrium
(fill ∝ √n/decay). The 30th ceiling (~44% fill, where stable
composition collapses) was measured at fixed decay=0.002.

If the ceiling is a UNIVERSAL fill fraction, it should be ~44%
regardless of how that fill is reached (by changing n or decay).
If it is a DECAY-DEPENDENT equilibrium, it should shift with decay.

Test: for each of 3 decay values, run with boundary (dual g=0.001)
at 3 n values that bracket the ~44% fill point. Measure fill% and
stability at each. If the ceiling is universal, stability collapses
at ~44% fill at every decay. If it shifts, the ceiling is
decay-dependent.

Calibration from no-inhib data (Session 113):
  decay=0.002: fill(2500)=42.6%, fill(3000)≈44%, fill(2000)≈38%
  decay=0.004: fill(5000)=37.1%, fill(8000)≈47% (√n extrapolation)
  decay=0.008: fill(5000)=30.4%, fill(10000)≈43% (√n extrapolation)

3 decays × 3 n values × 4 seeds × 2-seed = 36 runs.
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

# (decay, [(n, label), ...])
SWEEPS = [
    (0.002, [(2000, "below"), (2500, "at"), (3000, "above")]),
    (0.004, [(5000, "below"), (6000, "at"), (8000, "above")]),
    (0.008, [(8000, "below"), (10000, "at"), (12000, "above")]),
]


def make_params(n_termites, decay):
    """Dual boundary (g=0.001), focal bias, curvature channel."""
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
    # Curvature channel params.
    p["curve_follow"] = S.CURVE_FOLLOW
    p["deposit_prob_gain"] = S.DEPOSIT_PROB_GAIN
    p["excavate_prob_gain"] = S.EXCAVATE_PROB_GAIN
    p["excavate_prob_base"] = S.EXCAVATE_PROB_BASE
    return p


def measure(n_termites, decay, seed):
    """Run one 2-seed simulation and return fill + composition metrics."""
    p = make_params(n_termites, decay)
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
        "description": "Ceiling decay sweep — is the ~44% persistence "
                       "ceiling universal across decay values? "
                       "(queued-topic #295)",
        "grid": GRID,
        "jitter": JITTER,
        "seeds": SEEDS,
        "boundary": "dual g_form=0.001 g_persist=0.001",
        "date": "2026-11-23",
        "design": "3 decays × 3 n values × 4 seeds = 36 runs (2-seed)",
        "prediction": "If the ceiling is universal, stable collapses at "
                      "~44% fill at every decay. If it shifts, the ceiling "
                      "is a decay-dependent equilibrium.",
    }

    print("=" * 80)
    print("CEILING DECAY SWEEP — queued-topic #295")
    print("=" * 80)
    print()

    for decay, n_list in SWEEPS:
        decay_key = f"decay_{decay}"
        results[decay_key] = {}
        print(f"decay={decay:.4f}:")
        for n_val, label in n_list:
            n_key = f"n{n_val}_{label}"
            runs = []
            for sd in SEEDS:
                m = measure(n_val, decay, sd)
                runs.append(m)
                print(f"  n={n_val:5d} ({label:5s}) s={sd}: "
                      f"fill={m['fill_pct']:7.2f}%  "
                      f"h7={m['crossed_h7']!s:5s}  "
                      f"stable={m['l2_stable']!s:5s}  "
                      f"cf={m['coexist_frac']:.4f}  "
                      f"outcome={m['l2_outcome']:10s}  "
                      f"lc={m['late_mean_lc']:.1f} rc={m['late_mean_rc']:.1f}")

            mean_fill = np.mean([m["fill_pct"] for m in runs])
            mean_cf = np.mean([m["coexist_frac"] for m in runs])
            stable_n = sum(1 for m in runs if m["l2_stable"])
            coexist_n = sum(1 for m in runs if m["l2_outcome"] == "coexist")
            h7_n = sum(1 for m in runs if m["crossed_h7"])
            mean_lc = np.mean([m["late_mean_lc"] for m in runs])
            mean_rc = np.mean([m["late_mean_rc"] for m in runs])

            print(f"  MEAN: fill={mean_fill:.2f}%  cf={mean_cf:.4f}  "
                  f"stable={stable_n}/4  coexist={coexist_n}/4  "
                  f"h7={h7_n}/4  "
                  f"lc={mean_lc:.1f} rc={mean_rc:.1f}")
            print()

            results[decay_key][n_key] = {
                "n_termites": n_val,
                "label": label,
                "decay": decay,
                "runs": runs,
                "mean_fill": round(mean_fill, 2),
                "mean_cf": round(mean_cf, 4),
                "stable_count": stable_n,
                "coexist_count": coexist_n,
                "h7_count": h7_n,
                "mean_lc": round(mean_lc, 2),
                "mean_rc": round(mean_rc, 2),
            }

        elapsed = time.time() - t0
        print(f"  [elapsed: {elapsed/60:.1f} min]")
        print()

    results["elapsed_seconds"] = round(time.time() - t0, 1)

    out_path = os.path.join(SIM14_DIR, "output", "ceiling_decay_sweep.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_path}")
    print(f"Total elapsed: {results['elapsed_seconds']/60:.1f} min")

    return results


if __name__ == "__main__":
    run_sweep()
