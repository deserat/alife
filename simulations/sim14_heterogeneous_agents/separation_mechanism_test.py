"""
Separation mechanism test — is the composition mechanism exogenous spatial
separation or just population separation? (#289, #290)

Session 115 found the composition mechanism is the focal bias (exogenous
spatial separation), not the curvature channel or the boundary. But is it
the EXOGENITY (external reference the system can't reach) or the POPULATION
SEPARATION (keeping two groups apart) that matters?

Three conditions (all with curvature ON, no boundary, n=2500, decay=0.004):
  1. Focal bias (exogenous, current) — agents step toward home center
  2. Region-restricted deposit (exogenous, different mechanism) — agents
     wander freely but can only deposit in their assigned half
  3. Endogenous repulsion (endogenous) — agents step away from the OTHER
     ID's material

Prediction (two-wire principle's eighth member):
  - If region-restricted works AND endogenous repulsion works → any
    population-separation mechanism suffices; exogeneity is NOT necessary.
  - If region-restricted works BUT endogenous repulsion doesn't →
    exogeneity IS necessary (the two-wire principle holds).
  - If neither works → the focal bias's specific concentration mechanism
    is required, not just separation.

4 seeds × {2-seed, 1-seed} × 3 conditions = 24 runs.
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
DECAY = 0.004
JITTER = 10.0
SEEDS = [42, 123, 256, 999]


def make_params(condition):
    """Build params for one separation-mechanism condition.

    All runs: mode="hetero", inh_gain=0 (no boundary), curvature ON.
    The only variable is the separation mechanism.
    """
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = N_TERMITES
    p["material_decay"] = DECAY
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"

    # Curvature ON for all conditions (adds fill + H7; not load-bearing for
    # coexistence per Session 115, but gives each condition the same morphology).
    p["curve_follow"] = S.CURVE_FOLLOW  # 0.6
    p["deposit_prob_gain"] = S.DEPOSIT_PROB_GAIN  # 0.85
    p["excavate_prob_gain"] = S.EXCAVATE_PROB_GAIN  # 0.60
    p["excavate_prob_base"] = S.EXCAVATE_PROB_BASE  # 0.05

    if condition == "focal":
        # Exogenous focal bias (the known-working baseline).
        p["movement_bias"] = 0.3
        p["movement_mode"] = "focal"
        p["deposit_restriction"] = False
    elif condition == "region_restricted":
        # Exogenous region restriction: agents wander freely but can only
        # deposit in their assigned half.  No focal bias.
        p["movement_bias"] = 0.0
        p["movement_mode"] = "focal"
        p["deposit_restriction"] = True
    elif condition == "endogenous_repulsion":
        # Endogenous repulsion: agents step away from other ID's material.
        # No focal bias, no region restriction.
        p["movement_bias"] = 0.0
        p["movement_mode"] = "repulsion"
        p["deposit_restriction"] = False
        p["repulsion_threshold"] = 0.05
    else:
        raise ValueError(f"Unknown condition: {condition}")

    return p


def measure(condition, seed, n_seeds=2):
    """Run one simulation and return fill + composition metrics."""
    p = make_params(condition)
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
        "id0_total": round(s.get("id0_total", 0.0), 1),
        "id1_total": round(s.get("id1_total", 0.0), 1),
    }


def run_condition(condition):
    """Run one condition: 4 seeds × {2-seed, 1-seed}."""
    labels = {
        "focal": "Focal bias (exogenous)",
        "region_restricted": "Region-restricted deposit (exogenous)",
        "endogenous_repulsion": "Endogenous repulsion (endogenous)",
    }
    print(f"\n{'='*70}")
    print(f"Condition: {condition} — {labels[condition]}")
    print(f"{'='*70}")

    cond = {"label": condition, "description": labels[condition]}

    for n_seeds in [2, 1]:
        ns_label = "2_seed" if n_seeds == 2 else "1_seed"
        print(f"\n  --- {ns_label} ---")
        runs = []
        for sd in SEEDS:
            m = measure(condition, sd, n_seeds=n_seeds)
            runs.append(m)
            print(f"    s={sd}: fill={m['fill_pct']:7.2f}%  "
                  f"h7={m['crossed_h7']!s:5s}  l2={m['l2_crossed']!s:5s}  "
                  f"stable={m['l2_stable']!s:5s}  cf={m['coexist_frac']:.4f}  "
                  f"outcome={m['l2_outcome']:10s}  "
                  f"lc={m['late_mean_lc']:.1f} rc={m['late_mean_rc']:.1f}  "
                  f"id0={m['id0_total']:.0f} id1={m['id1_total']:.0f}")

        mean_fill = np.mean([m["fill_pct"] for m in runs])
        mean_cf = np.mean([m["coexist_frac"] for m in runs])
        stable_n = sum(1 for m in runs if m["l2_stable"])
        coexist_n = sum(1 for m in runs if m["l2_outcome"] == "coexist")
        h7_n = sum(1 for m in runs if m["crossed_h7"])
        l2_n = sum(1 for m in runs if m["l2_crossed"])
        mean_lc = np.mean([m["late_mean_lc"] for m in runs])
        mean_rc = np.mean([m["late_mean_rc"] for m in runs])
        mean_id0 = np.mean([m["id0_total"] for m in runs])
        mean_id1 = np.mean([m["id1_total"] for m in runs])

        print(f"    MEAN: fill={mean_fill:.2f}%  cf={mean_cf:.4f}  "
              f"stable={stable_n}/4  coexist={coexist_n}/4  "
              f"h7={h7_n}/4  l2={l2_n}/4  "
              f"lc={mean_lc:.1f} rc={mean_rc:.1f}  "
              f"id0={mean_id0:.0f} id1={mean_id1:.0f}")

        cond[ns_label] = {
            "runs": runs,
            "mean_fill": round(mean_fill, 2),
            "mean_cf": round(mean_cf, 4),
            "stable_count": stable_n,
            "coexist_count": coexist_n,
            "h7_count": h7_n,
            "l2_count": l2_n,
            "mean_lc": round(mean_lc, 2),
            "mean_rc": round(mean_rc, 2),
            "mean_id0": round(mean_id0, 1),
            "mean_id1": round(mean_id1, 1),
        }

    return cond


def run_test():
    t0 = time.time()
    results = {
        "description": "Separation mechanism test — is the composition "
                        "mechanism exogenous spatial separation or just "
                        "population separation? (queued-topics #289, #290)",
        "grid": GRID,
        "n_termites": N_TERMITES,
        "decay": DECAY,
        "jitter": JITTER,
        "seeds": SEEDS,
        "inh_gain": 0.0,
        "date": "2026-11-19",
        "design": "3 conditions (focal, region_restricted, endogenous_repulsion) "
                  "× 4 seeds × {2,1} seeds = 24 runs",
        "prediction": "If region-restricted works AND endogenous works → "
                      "any separation suffices; exogeneity NOT necessary. "
                      "If region-restricted works BUT endogenous doesn't → "
                      "exogeneity IS necessary (two-wire principle).",
    }

    print("=" * 80)
    print("SEPARATION MECHANISM TEST — queued-topics #289, #290")
    print("=" * 80)
    print(f"Grid: {GRID}×{GRID}  n={N_TERMITES}  decay={DECAY}  "
          f"jitter={JITTER}  inh_gain=0  seeds={SEEDS}")
    print(f"Curvature: ON (all conditions)")
    print(f"Design: 3 conditions × 4 seeds × {{2,1}} = 24 runs")
    print()

    conditions = []
    for cond_name in ["focal", "region_restricted", "endogenous_repulsion"]:
        cond = run_condition(cond_name)
        conditions.append(cond)

    results["conditions"] = conditions

    # Summary table
    print("\n\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"\n{'Condition':35s} {'Seeds':6s} {'Fill':>8s} {'CF':>8s} "
          f"{'Stable':>8s} {'Coexist':>8s} {'H7':>6s} {'L2':>6s} "
          f"{'LC':>6s} {'RC':>6s} {'ID0':>8s} {'ID1':>8s}")
    print("-" * 115)
    for cond in conditions:
        for ns in ["2_seed", "1_seed"]:
            d = cond[ns]
            print(f"  {cond['label']:33s} {ns:6s} "
                  f"{d['mean_fill']:7.2f}% {d['mean_cf']:8.4f} "
                  f"{d['stable_count']:7d}/4 {d['coexist_count']:7d}/4 "
                  f"{d['h7_count']:5d}/4 {d['l2_count']:5d}/4 "
                  f"{d['mean_lc']:5.1f} {d['mean_rc']:5.1f} "
                  f"{d['mean_id0']:7.0f} {d['mean_id1']:7.0f}")

    # Analysis
    print("\n\n" + "=" * 80)
    print("ANALYSIS — is exogeneity necessary for composition?")
    print("=" * 80)

    focal_2 = conditions[0]["2_seed"]
    region_2 = conditions[1]["2_seed"]
    repul_2 = conditions[2]["2_seed"]

    print(f"\n  Focal bias (exogenous):     cf={focal_2['mean_cf']:.4f}  "
          f"stable={focal_2['stable_count']}/4  coexist={focal_2['coexist_count']}/4  "
          f"fill={focal_2['mean_fill']:.2f}%")
    print(f"  Region-restricted (exog):   cf={region_2['mean_cf']:.4f}  "
          f"stable={region_2['stable_count']}/4  coexist={region_2['coexist_count']}/4  "
          f"fill={region_2['mean_fill']:.2f}%")
    print(f"  Endogenous repulsion:       cf={repul_2['mean_cf']:.4f}  "
          f"stable={repul_2['stable_count']}/4  coexist={repul_2['coexist_count']}/4  "
          f"fill={repul_2['mean_fill']:.2f}%")

    print(f"\n  VERDICT:")
    if region_2["coexist_count"] >= 3 and repul_2["coexist_count"] >= 3:
        print("    Both exogenous and endogenous separation produce composition.")
        print("    Exogeneity is NOT necessary — any population-separation suffices.")
    elif region_2["coexist_count"] >= 3 and repul_2["coexist_count"] < 2:
        print("    Exogenous separation works; endogenous does NOT.")
        print("    Exogeneity IS necessary (two-wire principle's eighth member).")
    elif region_2["coexist_count"] < 2 and repul_2["coexist_count"] < 2:
        print("    Neither alternative works — the focal bias's specific")
        print("    concentration mechanism is required, not just separation.")
    else:
        print("    Mixed results — see data for details.")

    elapsed = time.time() - t0
    results["elapsed_seconds"] = round(elapsed, 1)
    print(f"\n\nElapsed: {elapsed:.1f}s ({elapsed/60:.1f}m)")

    out_path = os.path.join(SIM14_DIR, "output", "separation_mechanism_test.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {out_path}")

    return results, elapsed


if __name__ == "__main__":
    run_test()
