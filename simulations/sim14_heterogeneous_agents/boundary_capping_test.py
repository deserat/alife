"""
Boundary capping test — does the boundary actually cap the fill, or does
the curvature channel + focal bias cap it independently?

Queued-topic #280. The no-inhibition control changed in Session 83:
- Before: mode="hetero" with inh_gain=0 fell through to S.termite_step
  (different deposit dynamics, fill ~100%).
- After:  elif mode == "hetero" uses termite_step_hetero (same deposit
  dynamics, fill ~42%).

The 44th mechanism's "boundary gap ~56%" was computed with the OLD control.
The NEW no-inhibition fill at 160×160 n=2500 is ~42.7% (vs ~42.3% with
boundary → gap ~0.4%). The boundary may NOT be capping the fill.

Test: measure no-inhibition fill at n=2500, 5000, 10000 on 160×160.
- If fill ≈ with-boundary fill (~42%, ~48%, ~75%), the boundary adds nothing.
- If fill = 100%, the boundary IS capping at high density.

Also: compare no-inhibition fill with mode="hetero" (new) vs mode="none"
(old S.termite_step) to quantify the code-path difference.
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

DENSITIES = [2500, 5000, 10000]
GAINS = [0.001]  # representative gain for with-boundary comparison


def make_params_with_boundary(n_termites, g_form, g_persist):
    """Params WITH boundary (dual mode)."""
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["boundary_mode"] = "dual"
    p["g_form"] = g_form
    p["g_persist"] = g_persist
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def make_no_inhib_params(n_termites):
    """Params with NO boundary (hetero mode, inh_gain=0)."""
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["movement_bias"] = 0.3
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def measure_fill(n_termites, mode, g_form=0.001, g_persist=0.001, seed=42):
    """Run a single simulation and return fill metrics."""
    if mode == "hetero_no_inhib":
        p = make_no_inhib_params(n_termites)
        r = I14.run_two_region_hetero(p, seed=seed, n_seeds=2, mode="hetero")
    elif mode == "hetero_with_boundary":
        p = make_params_with_boundary(n_termites, g_form, g_persist)
        r = I14.run_two_region_hetero(p, seed=seed, n_seeds=2, mode="hetero")
    elif mode == "none_old":
        # Old no-inhibition: mode="none" → S.termite_step
        p = make_no_inhib_params(n_termites)
        r = I14.run_two_region_hetero(p, seed=seed, n_seeds=2, mode="none")
    else:
        raise ValueError(f"Unknown mode: {mode}")

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
        "late_mean_lc": round(s.get("l2_late_mean_lc", 0.0), 2),
        "late_mean_rc": round(s.get("l2_late_mean_rc", 0.0), 2),
    }


def run_test():
    """Run the boundary capping test."""
    t0 = time.time()
    results = {
        "description": "Boundary capping test — does the boundary cap fill "
                       "or does the curvature channel + focal bias cap it "
                       "independently? (queued-topic #280)",
        "grid": GRID,
        "jitter": JITTER,
        "seeds": SEEDS,
        "date": "2026-11-15",
    }

    print("=" * 80)
    print("BOUNDARY CAPPING TEST — queued-topic #280")
    print("=" * 80)
    print()

    # Part 1: no-inhibition vs with-boundary at 3 densities
    print("Part 1: no-inhibition (hetero, g=0) vs with-boundary (dual, g=0.001)")
    print("-" * 70)

    for n in DENSITIES:
        print(f"\n  n={n} ({100*n/(GRID*GRID):.1f}% if full grid):")

        # no-inhibition: hetero mode, inh_gain=0 (NEW control)
        no_inhib_fills = []
        for sd in SEEDS:
            m = measure_fill(n, "hetero_no_inhib", seed=sd)
            no_inhib_fills.append(m)
            print(f"    no-inhib  s={sd}: fill={m['fill_pct']:.2f}%  "
                  f"cells={m['cells']}  h7={m['crossed_h7']}  "
                  f"lc={m['late_mean_lc']} rc={m['late_mean_rc']}")

        # with-boundary: hetero mode, dual, g=0.001
        with_bnd_fills = []
        for sd in SEEDS:
            m = measure_fill(n, "hetero_with_boundary", seed=sd)
            with_bnd_fills.append(m)
            print(f"    w/boundary s={sd}: fill={m['fill_pct']:.2f}%  "
                  f"cells={m['cells']}  h7={m['crossed_h7']}  "
                  f"lc={m['late_mean_lc']} rc={m['late_mean_rc']}")

        mean_no_inhib = np.mean([m["fill_pct"] for m in no_inhib_fills])
        mean_with_bnd = np.mean([m["fill_pct"] for m in with_bnd_fills])
        gap = mean_with_bnd - mean_no_inhib
        print(f"    MEAN: no-inhib={mean_no_inhib:.2f}%  "
              f"w/boundary={mean_with_bnd:.2f}%  gap={gap:.2f}pp")

        results[f"n{n}"] = {
            "no_inhibition": no_inhib_fills,
            "with_boundary": with_bnd_fills,
            "mean_no_inhib_fill": round(mean_no_inhib, 2),
            "mean_with_boundary_fill": round(mean_with_bnd, 2),
            "gap_pp": round(gap, 2),
        }

    # Part 2: old no-inhibition (mode="none") at n=2500 for comparison
    print("\n\nPart 2: old no-inhibition (mode='none', S.termite_step) at n=2500")
    print("-" * 70)
    old_fills = []
    for sd in SEEDS:
        m = measure_fill(2500, "none_old", seed=sd)
        old_fills.append(m)
        print(f"    old-none  s={sd}: fill={m['fill_pct']:.2f}%  "
              f"cells={m['cells']}  h7={m['crossed_h7']}")
    mean_old = np.mean([m["fill_pct"] for m in old_fills])
    mean_new = results["n2500"]["mean_no_inhib_fill"]
    print(f"    MEAN: old-none={mean_old:.2f}%  new-hetero={mean_new:.2f}%  "
          f"diff={mean_old - mean_new:.2f}pp")
    results["old_none_n2500"] = {
        "fills": old_fills,
        "mean_fill": round(mean_old, 2),
        "new_hetero_mean": mean_new,
        "diff_pp": round(mean_old - mean_new, 2),
    }

    elapsed = time.time() - t0
    results["elapsed_seconds"] = round(elapsed, 1)
    print(f"\n\nElapsed: {elapsed:.1f}s")

    # Save
    out_path = os.path.join(SIM14_DIR, "output", "boundary_capping_test.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {out_path}")

    return results, elapsed


if __name__ == "__main__":
    run_test()
