"""
Matched-fill test — is the focal bias's advantage concentration (lower fill)
or compact spatial arrangement? (#293)

Session 116 found:
  - Focal bias (exogenous + concentrating): cf=1.0, fill=34.5%
  - Region-restricted (exogenous, diffuse):   cf=0.40, fill=75.7%

The confound: region-restricted has 2× the fill (above the ~44% ceiling).
If region-restricted at matched fill (~34%) still matches the focal bias, the
advantage is just concentration (lower fill → below ceiling).  If it doesn't,
the focal bias's compact spatial arrangement (stepping toward a center) is
specifically required — not just lower fill.

DESIGN:
  Sweep decay for both conditions to find matched-fill pairs.
  - Focal: decay = 0.004, 0.008, 0.012, 0.016
  - Region-restricted: decay = 0.004, 0.008, 0.012, 0.016

  At each decay, compare fill and cf.  Find the region-restricted decay
  where fill ≈ 34% (the focal's baseline).  Compare cf at matched fill.

  4 decay × 2 conditions × 4 seeds × {2, 1} = 64 runs.
  Curvature ON, no boundary (inh_gain=0), 160×160, n=2500, jitter=10.
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
N_TERMITES = 2500
JITTER = 10.0
SEEDS = [42, 123, 256, 999]
DECAYS = [0.004, 0.008, 0.012, 0.016]


def make_params(condition, decay):
    """Build params for one condition + decay."""
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = N_TERMITES
    p["material_decay"] = decay
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    # Curvature ON (adds fill + H7; Session 115 showed not load-bearing
    # for coexistence but gives each condition the same morphology).
    p["curve_follow"] = S.CURVE_FOLLOW
    p["deposit_prob_gain"] = S.DEPOSIT_PROB_GAIN
    p["excavate_prob_gain"] = S.EXCAVATE_PROB_GAIN
    p["excavate_prob_base"] = S.EXCAVATE_PROB_BASE

    if condition == "focal":
        p["movement_bias"] = 0.3
        p["movement_mode"] = "focal"
        p["deposit_restriction"] = False
    elif condition == "region_restricted":
        p["movement_bias"] = 0.0
        p["movement_mode"] = "focal"
        p["deposit_restriction"] = True
    else:
        raise ValueError(f"Unknown condition: {condition}")
    return p


def measure(condition, decay, seed, n_seeds=2):
    """Run one simulation and return fill + composition metrics."""
    p = make_params(condition, decay)
    r = I14.run_two_region_hetero(p, seed=seed, n_seeds=n_seeds, mode="hetero")
    s = r["summary"]
    cells = s["final_n_structure_cells"]
    fill_pct = 100.0 * cells / (GRID * GRID)
    return {
        "decay": decay,
        "cells": cells,
        "fill_pct": round(fill_pct, 2),
        "l2_crossed": s["l2_crossed"],
        "l2_outcome": s["l2_outcome"],
        "l2_stable": s["l2_stable"],
        "crossed_h7": s["crossed_h7"],
        "coexist_frac": round(s.get("l2_coexist_frac", 0.0), 4),
        "late_mean_lc": round(s.get("l2_late_mean_lc", 0.0), 2),
        "late_mean_rc": round(s.get("l2_late_mean_rc", 0.0), 2),
        "id0_total": round(s.get("id0_total", 0.0), 1),
        "id1_total": round(s.get("id1_total", 0.0), 1),
    }


def run_condition_decay(condition, decay):
    """Run one condition × one decay: 4 seeds × {2, 1}."""
    label = {
        "focal": "Focal bias",
        "region_restricted": "Region-restricted",
    }[condition]

    cd = {
        "condition": condition,
        "label": label,
        "decay": decay,
    }

    for n_seeds in [2, 1]:
        ns_label = "2_seed" if n_seeds == 2 else "1_seed"
        runs = []
        for sd in SEEDS:
            m = measure(condition, decay, sd, n_seeds=n_seeds)
            runs.append(m)
            print(f"    {label:20s} d={decay:.3f} {ns_label:7s} s={sd}: "
                  f"fill={m['fill_pct']:7.2f}%  cf={m['coexist_frac']:.4f}  "
                  f"stable={m['l2_stable']!s:5s}  h7={m['crossed_h7']!s:5s}  "
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

        print(f"    MEAN {label:20s} d={decay:.3f} {ns_label:7s}: "
              f"fill={mean_fill:.2f}%  cf={mean_cf:.4f}  "
              f"stable={stable_n}/4  coexist={coexist_n}/4  "
              f"h7={h7_n}/4  l2={l2_n}/4  "
              f"lc={mean_lc:.1f} rc={mean_rc:.1f}")

        cd[ns_label] = {
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

    return cd


def run_test():
    t0 = time.time()
    results = {
        "description": "Matched-fill test — is the focal bias's advantage "
                       "concentration (lower fill) or compact spatial "
                       "arrangement? (queued-topic #293)",
        "grid": GRID,
        "n_termites": N_TERMITES,
        "jitter": JITTER,
        "seeds": SEEDS,
        "decays": DECAYS,
        "inh_gain": 0.0,
        "date": "2026-11-20",
        "design": "2 conditions × 4 decays × 4 seeds × {2,1} = 64 runs",
        "prediction": "If region-restricted at matched fill (~34%) matches "
                      "the focal bias (cf~1.0), the advantage is concentration "
                      "(lower fill). If cf<1.0, the focal bias's compactness "
                      "is specifically required.",
    }

    print("=" * 80)
    print("MATCHED-FILL TEST — queued-topic #293")
    print("=" * 80)
    print(f"Grid: {GRID}×{GRID}  n={N_TERMITES}  jitter={JITTER}  "
          f"inh_gain=0  seeds={SEEDS}")
    print(f"Decays: {DECAYS}")
    print(f"Curvature: ON (all conditions)")
    print(f"Design: 2 conditions × 4 decays × 4 seeds × {{2,1}} = 64 runs")
    print()

    all_cd = []
    for decay in DECAYS:
        for condition in ["focal", "region_restricted"]:
            print(f"\n  --- decay={decay:.3f}  condition={condition} ---")
            cd = run_condition_decay(condition, decay)
            all_cd.append(cd)

    results["configs"] = all_cd

    # Summary: 2-seed results by condition × decay
    print("\n\n" + "=" * 80)
    print("OVERALL SUMMARY (2-seed)")
    print("=" * 80)
    print(f"\n{'Condition':22s} {'Decay':>8s} {'Fill':>8s} {'CF':>8s} "
          f"{'Stable':>8s} {'Coexist':>8s} {'H7':>6s} {'L2':>6s} "
          f"{'LC':>6s} {'RC':>6s}")
    print("-" * 95)
    for cd in all_cd:
        d = cd["2_seed"]
        print(f"  {cd['label']:20s} {cd['decay']:8.3f} "
              f"{d['mean_fill']:7.2f}% {d['mean_cf']:8.4f} "
              f"{d['stable_count']:7d}/4 {d['coexist_count']:7d}/4 "
              f"{d['h7_count']:5d}/4 {d['l2_count']:5d}/4 "
              f"{d['mean_lc']:5.1f} {d['mean_rc']:5.1f}")

    # 1-seed summary
    print(f"\n{'Condition':22s} {'Decay':>8s} {'Fill':>8s} {'CF':>8s} "
          f"{'Stable':>8s} {'L2':>6s} {'LC':>6s} {'RC':>6s}")
    print("-" * 80)
    for cd in all_cd:
        d = cd["1_seed"]
        print(f"  {cd['label']:20s} {cd['decay']:8.3f} "
              f"{d['mean_fill']:7.2f}% {d['mean_cf']:8.4f} "
              f"{d['stable_count']:7d}/4 {d['l2_count']:5d}/4 "
              f"{d['mean_lc']:5.1f} {d['mean_rc']:5.1f}")

    # Analysis: find matched-fill pairs
    print("\n\n" + "=" * 80)
    print("ANALYSIS — matched-fill comparison")
    print("=" * 80)

    # Group by condition
    focal_2 = [c for c in all_cd if c["condition"] == "focal"]
    region_2 = [c for c in all_cd if c["condition"] == "region_restricted"]

    print(f"\n  Focal bias at each decay:")
    for cd in focal_2:
        d = cd["2_seed"]
        print(f"    decay={cd['decay']:.3f}: fill={d['mean_fill']:.2f}%  "
              f"cf={d['mean_cf']:.4f}  stable={d['stable_count']}/4")

    print(f"\n  Region-restricted at each decay:")
    for cd in region_2:
        d = cd["2_seed"]
        print(f"    decay={cd['decay']:.3f}: fill={d['mean_fill']:.2f}%  "
              f"cf={d['mean_cf']:.4f}  stable={d['stable_count']}/4")

    # Find the region-restricted decay closest to focal's fill at each decay
    print(f"\n  Matched-fill pairs (region fill closest to focal fill):")
    for fcd in focal_2:
        f_fill = fcd["2_seed"]["mean_fill"]
        best = min(region_2, key=lambda r: abs(r["2_seed"]["mean_fill"] - f_fill))
        r_fill = best["2_seed"]["mean_fill"]
        r_cf = best["2_seed"]["mean_cf"]
        f_cf = fcd["2_seed"]["mean_cf"]
        print(f"    decay={fcd['decay']:.3f}: focal fill={f_fill:.2f}% cf={f_cf:.4f}  "
              f"region fill={r_fill:.2f}% cf={r_cf:.4f}  "
              f"fill_diff={abs(f_fill - r_fill):.2f}pp  cf_diff={f_cf - r_cf:.4f}")

    # Verdict
    print(f"\n  VERDICT:")
    # Compare focal at decay=0.004 (fill~34%) with region at the decay
    # where fill is closest to 34%
    f0 = focal_2[0]  # decay=0.004
    f_fill0 = f0["2_seed"]["mean_fill"]
    f_cf0 = f0["2_seed"]["mean_cf"]
    f_st0 = f0["2_seed"]["stable_count"]

    best_r = min(region_2, key=lambda r: abs(r["2_seed"]["mean_fill"] - f_fill0))
    r_fill0 = best_r["2_seed"]["mean_fill"]
    r_cf0 = best_r["2_seed"]["mean_cf"]
    r_st0 = best_r["2_seed"]["stable_count"]

    if abs(r_fill0 - f_fill0) < 5.0:
        if r_cf0 >= 0.8:
            print(f"    Region-restricted at matched fill ({r_fill0:.1f}%) "
                  f"matches focal bias (cf={r_cf0:.3f} vs {f_cf0:.3f}).")
            print(f"    The advantage is CONCENTRATION (lower fill), not "
                  f"compact spatial arrangement.")
        else:
            print(f"    Region-restricted at matched fill ({r_fill0:.1f}%) "
                  f"does NOT match focal bias (cf={r_cf0:.3f} vs {f_cf0:.3f}).")
            print(f"    The focal bias's COMPACT SPATIAL ARRANGEMENT is "
                  f"specifically required, not just lower fill.")
    else:
        print(f"    No exact matched-fill pair found. Focal fill={f_fill0:.1f}%, "
              f"closest region fill={r_fill0:.1f}%. See data for interpretation.")

    elapsed = time.time() - t0
    results["elapsed_seconds"] = round(elapsed, 1)
    print(f"\n\nElapsed: {elapsed:.1f}s ({elapsed/60:.1f}m)")

    out_path = os.path.join(SIM14_DIR, "output", "matched_fill_test.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {out_path}")

    return results, elapsed


if __name__ == "__main__":
    run_test()
