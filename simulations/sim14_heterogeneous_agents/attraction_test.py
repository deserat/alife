"""
Attraction test — can endogenous attraction produce composition? (#294)

Session 117 found the focal bias's compact spatial arrangement is specifically
required, not just lower fill. Endogenous repulsion (stepping AWAY from other
ID's material) fragmented the structures (cf=0.0, lc/rc=13.8). But attraction
to OWN ID's material (stepping TOWARD where own material is dense) is also
endogenous and might concentrate deposits without fragmenting.

Three conditions (all with curvature ON, no boundary, n=2500):
  1. Focal bias (exogenous, concentrating) — known-working baseline
  2. Endogenous attraction (endogenous, concentrating) — the test
  3. Endogenous repulsion (endogenous, separating) — control from S116

Four decay values (0.004, 0.008, 0.012, 0.016) to test across fill levels.
4 seeds × {2-seed, 1-seed} × 3 conditions × 4 decays = 96 runs.

Prediction:
  - If attraction produces composition (cf>0.5, stable>2/4) → exogeneity
    is NOT necessary; any concentration mechanism suffices.
  - If attraction fails (cf≈0, fragmented) → exogeneity IS the load-bearing
    property; the two-wire principle's eighth member is confirmed as
    necessary, not just the concentration.

The key comparison: focal bias vs endogenous attraction at matched fill.
If both concentrate deposits but only the exogenous focal bias produces
composition, the exogeneity (external reference the system can't reach)
is the irreducible property.
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
    """Build params for one condition at one decay value."""
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = N_TERMITES
    p["material_decay"] = decay
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"

    # Curvature ON for all conditions.
    p["curve_follow"] = S.CURVE_FOLLOW  # 0.6
    p["deposit_prob_gain"] = S.DEPOSIT_PROB_GAIN  # 0.85
    p["excavate_prob_gain"] = S.EXCAVATE_PROB_GAIN  # 0.60
    p["excavate_prob_base"] = S.EXCAVATE_PROB_BASE  # 0.05

    if condition == "focal":
        # Exogenous focal bias (the known-working baseline).
        p["movement_bias"] = 0.3
        p["movement_mode"] = "focal"
        p["deposit_restriction"] = False
    elif condition == "endogenous_attraction":
        # Endogenous attraction: agents step toward own ID's material.
        # No focal bias, no region restriction.
        p["movement_bias"] = 0.0
        p["movement_mode"] = "attraction"
        p["deposit_restriction"] = False
        p["direct_radius"] = 8
    elif condition == "endogenous_repulsion":
        # Endogenous repulsion: agents step away from other ID's material.
        p["movement_bias"] = 0.0
        p["movement_mode"] = "repulsion"
        p["deposit_restriction"] = False
        p["repulsion_threshold"] = 0.05
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
    """Run one condition at one decay: 4 seeds × {2, 1}."""
    for n_seeds in [2, 1]:
        ns_label = "2_seed" if n_seeds == 2 else "1_seed"
        runs = []
        for sd in SEEDS:
            m = measure(condition, decay, sd, n_seeds=n_seeds)
            runs.append(m)
            print(f"      s={sd}: fill={m['fill_pct']:7.2f}%  "
                  f"h7={m['crossed_h7']!s:5s}  l2={m['l2_crossed']!s:5s}  "
                  f"stable={m['l2_stable']!s:5s}  cf={m['coexist_frac']:.4f}  "
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

        print(f"      MEAN: fill={mean_fill:.2f}%  cf={mean_cf:.4f}  "
              f"stable={stable_n}/4  coexist={coexist_n}/4  "
              f"h7={h7_n}/4  l2={l2_n}/4  "
              f"lc={mean_lc:.1f} rc={mean_rc:.1f}")

        yield ns_label, {
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


def run_test():
    t0 = time.time()
    conditions_list = ["focal", "endogenous_attraction", "endogenous_repulsion"]
    labels = {
        "focal": "Focal bias (exogenous)",
        "endogenous_attraction": "Endogenous attraction",
        "endogenous_repulsion": "Endogenous repulsion",
    }

    results = {
        "description": "Attraction test — can endogenous attraction "
                       "produce composition? (queued-topic #294)",
        "grid": GRID,
        "n_termites": N_TERMITES,
        "decays": DECAYS,
        "jitter": JITTER,
        "seeds": SEEDS,
        "inh_gain": 0.0,
        "date": "2026-11-21",
        "design": "3 conditions × 4 decays × 4 seeds × {2,1} = 96 runs",
        "prediction": "If attraction produces composition → exogeneity NOT "
                      "necessary. If attraction fails → exogeneity IS the "
                      "load-bearing property (two-wire principle's 8th member).",
    }

    print("=" * 80)
    print("ATTRACTION TEST — queued-topic #294")
    print("=" * 80)
    print(f"Grid: {GRID}×{GRID}  n={N_TERMITES}  jitter={JITTER}  "
          f"inh_gain=0  seeds={SEEDS}")
    print(f"Decays: {DECAYS}")
    print(f"Curvature: ON (all conditions)")
    print(f"Design: 3 conditions × 4 decays × 4 seeds × {{2,1}} = 96 runs")
    print()

    all_conditions = []
    for cond_name in conditions_list:
        print(f"\n{'='*70}")
        print(f"Condition: {cond_name} — {labels[cond_name]}")
        print(f"{'='*70}")
        cond_data = {"label": cond_name, "description": labels[cond_name],
                     "decays": []}
        for decay in DECAYS:
            print(f"\n  --- decay={decay} ---")
            decay_data = {"decay": decay}
            for ns_label, data in run_condition_decay(cond_name, decay):
                decay_data[ns_label] = data
            cond_data["decays"].append(decode_data := decay_data)

        all_conditions.append(cond_data)

    results["conditions"] = all_conditions

    # Summary table
    print("\n\n" + "=" * 80)
    print("OVERALL SUMMARY — 2-seed results")
    print("=" * 80)
    print(f"\n{'Condition':30s} {'Decay':>8s} {'Fill':>8s} {'CF':>8s} "
          f"{'Stable':>8s} {'Coexist':>8s} {'H7':>6s} {'L2':>6s} "
          f"{'LC':>6s} {'RC':>6s}")
    print("-" * 100)
    for cond in all_conditions:
        for dd in cond["decays"]:
            d = dd["2_seed"]
            print(f"  {cond['label']:28s} {dd['decay']:8.3f} "
                  f"{d['mean_fill']:7.2f}% {d['mean_cf']:8.4f} "
                  f"{d['stable_count']:7d}/4 {d['coexist_count']:7d}/4 "
                  f"{d['h7_count']:5d}/4 {d['l2_count']:5d}/4 "
                  f"{d['mean_lc']:5.1f} {d['mean_rc']:5.1f}")

    # Analysis
    print("\n\n" + "=" * 80)
    print("ANALYSIS — can endogenous attraction substitute for the focal bias?")
    print("=" * 80)

    focal = all_conditions[0]
    attr = all_conditions[1]
    repul = all_conditions[2]

    print("\n  At each decay (2-seed):")
    for i, decay in enumerate(DECAYS):
        f = focal["decays"][i]["2_seed"]
        a = attr["decays"][i]["2_seed"]
        r = repul["decays"][i]["2_seed"]
        print(f"\n  decay={decay}:")
        print(f"    Focal bias:      fill={f['mean_fill']:6.1f}%  "
              f"cf={f['mean_cf']:.4f}  stable={f['stable_count']}/4  "
              f"coexist={f['coexist_count']}/4  lc={f['mean_lc']:.1f}")
        print(f"    Endog. attraction: fill={a['mean_fill']:6.1f}%  "
              f"cf={a['mean_cf']:.4f}  stable={a['stable_count']}/4  "
              f"coexist={a['coexist_count']}/4  lc={a['mean_lc']:.1f}")
        print(f"    Endog. repulsion: fill={r['mean_fill']:6.1f}%  "
              f"cf={r['mean_cf']:.4f}  stable={r['stable_count']}/4  "
              f"coexist={r['coexist_count']}/4  lc={r['mean_lc']:.1f}")

    # Verdict
    attr_any = any(
        attr["decays"][i]["2_seed"]["coexist_count"] >= 2
        for i in range(len(DECAYS))
    )
    attr_best = max(
        attr["decays"][i]["2_seed"]["coexist_count"]
        for i in range(len(DECAYS))
    )
    attr_best_cf = max(
        attr["decays"][i]["2_seed"]["mean_cf"]
        for i in range(len(DECAYS))
    )

    print(f"\n  VERDICT:")
    print(f"    Best attraction coexist: {attr_best}/4, best cf: {attr_best_cf:.4f}")
    if attr_any:
        print("    Endogenous attraction produces composition.")
        print("    Exogeneity is NOT necessary — concentration suffices.")
    else:
        print("    Endogenous attraction does NOT produce composition.")
        print("    Exogeneity IS the load-bearing property — the two-wire")
        print("    principle's eighth member is confirmed as necessary.")
        print("    The focal bias's external reference (home center) cannot")
        print("    be replaced by an endogenous concentration mechanism.")

    elapsed = time.time() - t0
    results["elapsed_seconds"] = round(elapsed, 1)
    print(f"\n\nElapsed: {elapsed:.1f}s ({elapsed/60:.1f}m)")

    out_path = os.path.join(SIM14_DIR, "output", "attraction_test.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {out_path}")

    return results, elapsed


if __name__ == "__main__":
    run_test()
