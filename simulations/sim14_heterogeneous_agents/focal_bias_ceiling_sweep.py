"""
Focal bias ceiling sweep — can the ~42% persistence ceiling be shifted
by a stronger focal bias?

Queued-topic #300.

Session 119 found the ~42% persistence ceiling is universal across
decay values (the 69th mechanism): stable composition collapses at
~42% fill regardless of how that fill is reached. The ceiling is where
the focal bias's compact spatial arrangement breaks down (over-splitting
lc/rc > 5).

If the ceiling is a FOCAL-BIAS-STRENGTH-DEPENDENT threshold, a stronger
bias (movement_bias > 0.3) should maintain compactness at higher fill,
shifting the ceiling up. If it doesn't shift, the ceiling is a fundamental
geometric limit of the 2D grid + focal bias architecture.

Test: at decay=0.002, sweep movement_bias (0.3, 0.5, 0.7, 0.9) at 3 n
values that bracket the ceiling (n=2000 ~41% fill, n=2500 ~43%, n=3000
~44%). Measure fill%, stability, and component counts.

Key confound: a stronger focal bias may LOWER the fill (more concentration
→ less spread → lower fill). If the fill drops below the ceiling, the
"rescue" is a fill effect, not a ceiling shift. We measure fill at each
bias to separate the two.

4 biases × 3 n values × 4 seeds = 48 runs (2-seed).
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
DECAY = 0.002
SEEDS = [42, 123, 256, 999]

# (n_termites, label)
N_VALUES = [
    (2000, "below"),
    (2500, "at"),
    (3000, "above"),
]

# (movement_bias, label)
BIAS_VALUES = [
    (0.3, "baseline"),
    (0.5, "medium"),
    (0.7, "strong"),
    (0.9, "max"),
]


def make_params(n_termites, movement_bias):
    """Dual boundary (g=0.001), focal bias, curvature channel."""
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["material_decay"] = DECAY
    p["boundary_mode"] = "dual"
    p["g_form"] = 0.001
    p["g_persist"] = 0.001
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = movement_bias
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    p["movement_mode"] = "focal"
    # Curvature channel params.
    p["curve_follow"] = S.CURVE_FOLLOW
    p["deposit_prob_gain"] = S.DEPOSIT_PROB_GAIN
    p["excavate_prob_gain"] = S.EXCAVATE_PROB_GAIN
    p["excavate_prob_base"] = S.EXCAVATE_PROB_BASE
    return p


def measure(n_termites, movement_bias, seed):
    """Run one 2-seed simulation and return fill + composition metrics."""
    p = make_params(n_termites, movement_bias)
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
        "description": ("Focal bias ceiling sweep — can the ~42% persistence "
                        "ceiling be shifted by a stronger focal bias? "
                        "(queued-topic #300)"),
        "grid": GRID,
        "jitter": JITTER,
        "decay": DECAY,
        "seeds": SEEDS,
        "boundary": "dual g_form=0.001 g_persist=0.001",
        "date": "2026-11-23",
        "design": "4 biases × 3 n values × 4 seeds = 48 runs (2-seed)",
        "prediction": ("If the ceiling shifts up with stronger bias, it is "
                      "focal-bias-dependent. If it doesn't, it is a "
                      "fundamental geometric limit. Key confound: stronger "
                      "bias may lower fill — measure fill to separate."),
    }

    print("=" * 80)
    print("FOCAL BIAS CEILING SWEEP — queued-topic #300")
    print("=" * 80)
    print()

    for bias_val, bias_label in BIAS_VALUES:
        bias_key = f"bias_{bias_val}_{bias_label}"
        results[bias_key] = {}
        print(f"movement_bias={bias_val} ({bias_label}):")
        for n_val, n_label in N_VALUES:
            n_key = f"n{n_val}_{n_label}"
            runs = []
            for sd in SEEDS:
                m = measure(n_val, bias_val, sd)
                runs.append(m)
                print(f"  n={n_val:5d} ({n_label:5s}) s={sd}: "
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

            results[bias_key][n_key] = {
                "n_termites": n_val,
                "label": n_label,
                "movement_bias": bias_val,
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

    out_path = os.path.join(SIM14_DIR, "output", "focal_bias_ceiling_sweep.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_path}")
    print(f"Total elapsed: {results['elapsed_seconds']/60:.1f} min")

    return results


if __name__ == "__main__":
    run_sweep()
