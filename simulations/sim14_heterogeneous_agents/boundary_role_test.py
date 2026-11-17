"""
Boundary role test — what does the boundary DO, if not cap the fill?

Queued-topic #283. Session 112 falsified the 44th mechanism (boundary does NOT
cap fill — gap <1pp). Session 113 resolved the fill cap's mechanism: it's from
material decay (deposit/decay equilibrium), not the boundary or curvature
channel. But the boundary clearly DOES something — it enables composition
(coexist_frac, stable_l2), prevents merging, and produces the 1-seed structural
guarantee.

The clean test: at MATCHED FILL (same n, same decay → same fill with and
without boundary), does the boundary improve composition quality?

If composition quality differs at matched fill, the boundary's role is in
COMPOSITION (preventing merging, enabling stable coexistence), not fill capping.
If composition quality is the same, the boundary does nothing we haven't
already accounted for.

Pairs (n, decay) → target fill:
  (2500, 0.002) → ~42%  (the 30th ceiling)
  (2500, 0.004) → ~35%  (below the ceiling — stable regime)
  (5000, 0.002) → ~48%  (above the ceiling — unstable regime)
  (3500, 0.002) → ~44%  (right at the ceiling)

For each pair: 4 seeds × {2-seed, 1-seed} × {no-inhibition, with-boundary}.
The 1-seed control tests the structural guarantee (boundary should prevent
1-seed false positives; without boundary, 1-seed should be 0/4 on l2_crossed
but may differ on l2_outcome).
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

PAIRS = [
    (2500, 0.002, "~42% (30th ceiling)"),
    (2500, 0.004, "~35% (below ceiling)"),
    (5000, 0.002, "~48% (above ceiling)"),
    (3500, 0.002, "~44% (at ceiling)"),
]


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


def measure(n_termites, decay, with_boundary, seed, n_seeds=2):
    """Run one simulation and return fill + composition metrics."""
    if with_boundary:
        p = make_with_boundary_params(n_termites, decay)
    else:
        p = make_no_inhib_params(n_termites, decay)
    r = I14.run_two_region_hetero(p, seed=seed, n_seeds=n_seeds, mode="hetero")
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


def run_pair(n_termites, decay, label):
    """Run one (n, decay) pair: 4 seeds × {2-seed, 1-seed} × {no-inhib, w/boundary}."""
    print(f"\n{'='*70}")
    print(f"Pair: n={n_termites} decay={decay} label={label}")
    print(f"{'='*70}")

    pair_results = {
        "n": n_termites,
        "decay": decay,
        "label": label,
    }

    for n_seeds in [2, 1]:
        ns_label = "2_seed" if n_seeds == 2 else "1_seed"
        print(f"\n  --- {ns_label} ---")

        for with_bnd in [False, True]:
            bnd_label = "with_boundary" if with_bnd else "no_inhibition"
            runs = []
            for sd in SEEDS:
                m = measure(n_termites, decay, with_bnd, sd, n_seeds=n_seeds)
                runs.append(m)
                print(f"    {bnd_label:14s} s={sd}: "
                      f"fill={m['fill_pct']:6.2f}%  h7={m['crossed_h7']!s:5s}  "
                      f"l2={m['l2_crossed']!s:5s}  stable={m['l2_stable']!s:5s}  "
                      f"cf={m['coexist_frac']:.4f}  "
                      f"outcome={m['l2_outcome']:10s}  "
                      f"lc={m['late_mean_lc']:.1f} rc={m['late_mean_rc']:.1f}")

            mean_fill = np.mean([m["fill_pct"] for m in runs])
            mean_cf = np.mean([m["coexist_frac"] for m in runs])
            stable_n = sum(1 for m in runs if m["l2_stable"])
            coexist_n = sum(1 for m in runs if m["l2_outcome"] == "coexist")
            h7_n = sum(1 for m in runs if m["crossed_h7"])
            l2_n = sum(1 for m in runs if m["l2_crossed"])
            mean_lc = np.mean([m["late_mean_lc"] for m in runs])
            mean_rc = np.mean([m["late_mean_rc"] for m in runs])

            print(f"    {bnd_label:14s} MEAN: fill={mean_fill:.2f}%  "
                  f"cf={mean_cf:.4f}  stable={stable_n}/4  "
                  f"coexist={coexist_n}/4  h7={h7_n}/4  l2={l2_n}/4  "
                  f"lc={mean_lc:.1f} rc={mean_rc:.1f}")

            pair_results[f"{ns_label}_{bnd_label}"] = {
                "runs": runs,
                "mean_fill": round(mean_fill, 2),
                "mean_cf": round(mean_cf, 4),
                "stable_count": stable_n,
                "coexist_count": coexist_n,
                "h7_count": h7_n,
                "l2_count": l2_n,
                "mean_lc": round(mean_lc, 2),
                "mean_rc": round(mean_rc, 2),
            }

    # Comparison summary
    for ns_label in ["2_seed", "1_seed"]:
        no = pair_results[f"{ns_label}_no_inhibition"]
        wb = pair_results[f"{ns_label}_with_boundary"]
        fill_gap = wb["mean_fill"] - no["mean_fill"]
        cf_gap = wb["mean_cf"] - no["mean_cf"]
        stable_gap = wb["stable_count"] - no["stable_count"]
        coexist_gap = wb["coexist_count"] - no["coexist_count"]
        print(f"\n  {ns_label} comparison (boundary - no-inhibition):")
        print(f"    fill gap:   {fill_gap:+.2f}pp")
        print(f"    cf gap:     {cf_gap:+.4f}")
        print(f"    stable gap: {stable_gap:+d}/4")
        print(f"    coexist gap:{coexist_gap:+d}/4")
        pair_results[f"{ns_label}_comparison"] = {
            "fill_gap_pp": round(fill_gap, 2),
            "cf_gap": round(cf_gap, 4),
            "stable_gap": stable_gap,
            "coexist_gap": coexist_gap,
        }

    return pair_results


def run_test():
    t0 = time.time()
    results = {
        "description": "Boundary role test — what does the boundary DO "
                       "if not cap the fill? (queued-topic #283)",
        "grid": GRID,
        "jitter": JITTER,
        "seeds": SEEDS,
        "pairs": [(n, d, l) for n, d, l in PAIRS],
        "date": "2026-11-17",
    }

    print("=" * 80)
    print("BOUNDARY ROLE TEST — queued-topic #283")
    print("=" * 80)

    pair_data = []
    for n_termites, decay, label in PAIRS:
        pd = run_pair(n_termites, decay, label)
        pair_data.append(pd)

    results["pairs_data"] = pair_data

    # Overall summary
    print("\n\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"\n{'Pair':30s} {'Fill gap':>10s} {'CF gap':>10s} "
          f"{'Stable gap':>12s} {'Coexist gap':>12s}")
    print("-" * 80)
    for pd in pair_data:
        for ns in ["2_seed", "1_seed"]:
            comp = pd[f"{ns}_comparison"]
            print(f"  {pd['label']:28s} {ns:8s} "
                  f"{comp['fill_gap_pp']:+8.2f}pp "
                  f"{comp['cf_gap']:+8.4f}  "
                  f"{comp['stable_gap']:+10d}/4 "
                  f"{comp['coexist_gap']:+10d}/4")

    elapsed = time.time() - t0
    results["elapsed_seconds"] = round(elapsed, 1)
    print(f"\n\nElapsed: {elapsed:.1f}s")

    out_path = os.path.join(SIM14_DIR, "output", "boundary_role_test.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {out_path}")

    return results, elapsed


if __name__ == "__main__":
    run_test()
