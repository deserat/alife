"""
Composition mechanism test — what IS the composition mechanism, if not the boundary?

Queued-topic #286. Session 114 showed the boundary is a marginal stabilizer at the
fill-driven phase transition (~42% fill), NOT a composition mechanism. At ~35% fill
(below the ceiling), composition is perfect WITHOUT the boundary (cf=1.0, stable=4/4).
What makes the two structures coexist?

Three candidate components (without boundary, inh_gain=0):
  1. Curvature channel — deposit at concavities, excavate at convexities
     (curvature-following movement + curvature-routed deposit/excavate)
  2. Focal bias — agents step toward their home center (movement_bias > 0)
  3. ID tagging — deposits tagged with agent ID (but without boundary, this
     only matters for the 1-seed control; for 2-seed it's functionally inert)

The clean test: a 2×2 factorial at ~35% fill (n=2500, decay=0.004, 160×160):
  curvature × {ON, OFF} × focal_bias × {ON, OFF}
  = 4 conditions × 4 seeds × {2-seed, 1-seed} = 32 runs

For "curvature OFF":
  - curve_follow=0 (no curvature-following movement)
  - deposit_prob_gain=0 (uniform deposit rate, no curvature routing)
  - excavate_prob_gain=0 (uniform excavation, no curvature routing)
  But keep deposit_prob_base, excavate_prob_base, pickup_prob_base — erosion
  still happens, just not curvature-directed.

For "focal OFF":
  - movement_bias=0 (agents always random walk unless curvature-following)

Prediction: if focal bias is load-bearing for composition (keeping two populations
separated) and curvature is load-bearing for consolidation (compact structures),
then:
  - full (curv+focal): cf=1.0, stable=4/4 (the known baseline)
  - no_curv (focal only): coexist but fragmented (diffuse blobs, high lc/rc)
  - no_focal (curv only): merge (agents wander, structures merge into one)
  - neither: no composition (uniform field, no structure)
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


def make_params(curvature_on, focal_on):
    """Build params for one cell of the 2×2 factorial.

    All runs use mode="hetero", inh_gain=0 (no boundary).
    """
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = N_TERMITES
    p["material_decay"] = DECAY
    p["movement_bias"] = 0.3 if focal_on else 0.0
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"

    if curvature_on:
        # Default curvature channel: curvature-following + curvature-routed deposit/excavate
        p["curve_follow"] = S.CURVE_FOLLOW  # 0.6
        p["deposit_prob_gain"] = S.DEPOSIT_PROB_GAIN  # 0.85
        p["excavate_prob_gain"] = S.EXCAVATE_PROB_GAIN  # 0.60
        p["excavate_prob_base"] = S.EXCAVATE_PROB_BASE  # 0.05
    else:
        # No curvature channel: uniform deposit/excavate, no curvature following
        p["curve_follow"] = 0.0
        p["deposit_prob_gain"] = 0.0
        p["excavate_prob_gain"] = 0.0
        p["excavate_prob_base"] = S.EXCAVATE_PROB_BASE  # 0.05 — keep baseline erosion
        # pickup_prob_base stays at default (0.01)

    return p


def measure(curvature_on, focal_on, seed, n_seeds=2):
    """Run one simulation and return fill + composition metrics."""
    p = make_params(curvature_on, focal_on)
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


def run_condition(curvature_on, focal_on):
    """Run one cell of the 2×2: 4 seeds × {2-seed, 1-seed}."""
    label = f"{'curv' if curvature_on else 'no_curv'}_{'focal' if focal_on else 'no_focal'}"
    print(f"\n{'='*70}")
    print(f"Condition: {label}")
    print(f"  curvature_on={curvature_on}  focal_on={focal_on}")
    print(f"{'='*70}")

    cond = {"label": label, "curvature_on": curvature_on, "focal_on": focal_on}

    for n_seeds in [2, 1]:
        ns_label = "2_seed" if n_seeds == 2 else "1_seed"
        print(f"\n  --- {ns_label} ---")
        runs = []
        for sd in SEEDS:
            m = measure(curvature_on, focal_on, sd, n_seeds=n_seeds)
            runs.append(m)
            print(f"    s={sd}: fill={m['fill_pct']:6.2f}%  "
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

        print(f"    MEAN: fill={mean_fill:.2f}%  cf={mean_cf:.4f}  "
              f"stable={stable_n}/4  coexist={coexist_n}/4  "
              f"h7={h7_n}/4  l2={l2_n}/4  "
              f"lc={mean_lc:.1f} rc={mean_rc:.1f}")

        cond[f"{ns_label}"] = {
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

    return cond


def run_test():
    t0 = time.time()
    results = {
        "description": "Composition mechanism test — what IS the composition "
                        "mechanism if not the boundary? (queued-topic #286)",
        "grid": GRID,
        "n_termites": N_TERMITES,
        "decay": DECAY,
        "jitter": JITTER,
        "seeds": SEEDS,
        "inh_gain": 0.0,
        "date": "2026-11-18",
        "design": "2×2 factorial: curvature {ON,OFF} × focal_bias {ON,OFF}",
        "prediction": "focal bias = load-bearing for composition (population "
                      "separation); curvature = load-bearing for consolidation "
                      "(compact structures). no_curv → fragmented; no_focal → merge.",
    }

    print("=" * 80)
    print("COMPOSITION MECHANISM TEST — queued-topic #286")
    print("=" * 80)
    print(f"Grid: {GRID}×{GRID}  n={N_TERMITES}  decay={DECAY}  "
          f"jitter={JITTER}  inh_gain=0  seeds={SEEDS}")
    print(f"Design: 2×2 factorial (curvature × focal_bias)")
    print(f"Target fill: ~35% (below the 30th ceiling)")
    print()

    conditions = []
    for curv in [True, False]:
        for focal in [True, False]:
            cond = run_condition(curv, focal)
            conditions.append(cond)

    results["conditions"] = conditions

    # Summary table
    print("\n\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    print(f"\n{'Condition':20s} {'Seeds':6s} {'Fill':>8s} {'CF':>8s} "
          f"{'Stable':>8s} {'Coexist':>8s} {'H7':>6s} {'L2':>6s} "
          f"{'LC':>6s} {'RC':>6s}")
    print("-" * 90)
    for cond in conditions:
        for ns in ["2_seed", "1_seed"]:
            d = cond[ns]
            print(f"  {cond['label']:18s} {ns:6s} "
                  f"{d['mean_fill']:7.2f}% {d['mean_cf']:8.4f} "
                  f"{d['stable_count']:7d}/4 {d['coexist_count']:7d}/4 "
                  f"{d['h7_count']:5d}/4 {d['l2_count']:5d}/4 "
                  f"{d['mean_lc']:5.1f} {d['mean_rc']:5.1f}")

    # Analysis: which component is load-bearing?
    print("\n\n" + "=" * 80)
    print("ANALYSIS — which component is load-bearing for composition?")
    print("=" * 80)

    # Compare full vs no_curv (focal ON, curvature removed)
    full_2 = conditions[0]["2_seed"]
    no_curv_2 = conditions[1]["2_seed"]
    print(f"\n  focal ON: full vs no_curv (curvature removed):")
    print(f"    cf:       {full_2['mean_cf']:.4f} → {no_curv_2['mean_cf']:.4f} "
          f"(Δ={no_curv_2['mean_cf'] - full_2['mean_cf']:+.4f})")
    print(f"    stable:   {full_2['stable_count']}/4 → {no_curv_2['stable_count']}/4")
    print(f"    coexist:  {full_2['coexist_count']}/4 → {no_curv_2['coexist_count']}/4")
    print(f"    lc/rc:    {full_2['mean_lc']:.1f}/{full_2['mean_rc']:.1f} → "
          f"{no_curv_2['mean_lc']:.1f}/{no_curv_2['mean_rc']:.1f}")

    # Compare full vs no_focal (curvature ON, focal removed)
    no_focal_2 = conditions[2]["2_seed"]
    print(f"\n  curvature ON: full vs no_focal (focal removed):")
    print(f"    cf:       {full_2['mean_cf']:.4f} → {no_focal_2['mean_cf']:.4f} "
          f"(Δ={no_focal_2['mean_cf'] - full_2['mean_cf']:+.4f})")
    print(f"    stable:   {full_2['stable_count']}/4 → {no_focal_2['stable_count']}/4")
    print(f"    coexist:  {full_2['coexist_count']}/4 → {no_focal_2['coexist_count']}/4")
    print(f"    lc/rc:    {full_2['mean_lc']:.1f}/{full_2['mean_rc']:.1f} → "
          f"{no_focal_2['mean_lc']:.1f}/{no_focal_2['mean_rc']:.1f}")

    # Compare no_curv vs neither (focal removed when curvature already off)
    neither_2 = conditions[3]["2_seed"]
    print(f"\n  focal ON: no_curv vs neither (focal also removed):")
    print(f"    cf:       {no_curv_2['mean_cf']:.4f} → {neither_2['mean_cf']:.4f} "
          f"(Δ={neither_2['mean_cf'] - no_curv_2['mean_cf']:+.4f})")
    print(f"    stable:   {no_curv_2['stable_count']}/4 → {neither_2['stable_count']}/4")

    # Compare no_focal vs neither (curvature removed when focal already off)
    print(f"\n  curvature ON: no_focal vs neither (curvature also removed):")
    print(f"    cf:       {no_focal_2['mean_cf']:.4f} → {neither_2['mean_cf']:.4f} "
          f"(Δ={neither_2['mean_cf'] - no_focal_2['mean_cf']:+.4f})")
    print(f"    stable:   {no_focal_2['stable_count']}/4 → {neither_2['stable_count']}/4")

    # Verdict
    print("\n  VERDICT:")
    curv_effect = no_curv_2["mean_cf"] - full_2["mean_cf"]
    focal_effect = no_focal_2["mean_cf"] - full_2["mean_cf"]
    if abs(curv_effect) > abs(focal_effect):
        print(f"    Curvature removal has the larger effect on cf "
              f"(Δ={curv_effect:+.4f} vs {focal_effect:+.4f}).")
    else:
        print(f"    Focal removal has the larger effect on cf "
              f"(Δ={focal_effect:+.4f} vs {curv_effect:+.4f}).")
    if no_curv_2["coexist_count"] < full_2["coexist_count"]:
        print("    Curvature IS load-bearing for coexistence.")
    else:
        print("    Curvature is NOT load-bearing for coexistence "
              "(focal bias alone produces coexistence).")
    if no_focal_2["coexist_count"] < full_2["coexist_count"]:
        print("    Focal bias IS load-bearing for coexistence.")
    else:
        print("    Focal bias is NOT load-bearing for coexistence "
              "(curvature alone produces coexistence).")

    elapsed = time.time() - t0
    results["elapsed_seconds"] = round(elapsed, 1)
    print(f"\n\nElapsed: {elapsed:.1f}s ({elapsed/60:.1f}m)")

    out_path = os.path.join(SIM14_DIR, "output", "composition_mechanism_test.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved to {out_path}")

    return results, elapsed


if __name__ == "__main__":
    run_test()
