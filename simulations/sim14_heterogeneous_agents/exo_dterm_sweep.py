"""
Exogenous D-term sweep (queued-topic #117).

Session 39 found the PID D-term (B_deriv from cp_delta) is neutral at the
optimal config (4/4 full at all g_deriv with focal bias) but destructive
without focal bias (stable 3/4→0/4, coexist 2/4→0/4). The D term is
endogenous — it reads the system's own co-presence rate of change, creating
a stigmergic feedback loop.

This sweep tests whether an EXOGENOUS D-term (external sinusoid, independent
of system state) breaks the persistence-formation trade-off differently.
If the exogenous D-term is neutral or helpful without focal bias, the
endogenous D-term's failure is specifically its endogeneity (the two-wire
principle's 10th member). If the exogenous D-term is also destructive
without focal bias, anticipation itself is the problem.

Conditions:
  - With focal bias (movement_bias=0.3, dual f=0.3 p=0.3)
    → the optimal config (Session 39: 4/4 full at all g_deriv)
  - Without focal bias (movement_bias=0.0, dual f=0.3 p=0.3)
    → the config where the endogenous D-term was destructive

Sweep: g_deriv [0.0, 0.05, 0.1, 0.2, 0.3] × 4 seeds × {2, 1} seeds
  × 2 focal conditions (with/without focal bias)
  = 5 × 4 × 2 × 2 = 80 runs

Also: exo_period [100, 200, 400] at g_deriv=0.1 to test whether the
oscillation frequency matters.

Usage:
  python3 exo_dterm_sweep.py          # full sweep (80 runs)
  python3 exo_dterm_sweep.py --quick  # quick sweep (g_deriv only, 40 runs)
"""

import os
import sys
import json
import time

import numpy as np

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM_DIR)

import sim14 as S14  # noqa: E402

SEEDS = [42, 123, 256, 999]
G_DERIV_LEVELS = [0.0, 0.05, 0.1, 0.2, 0.3]
EXO_PERIODS = [100, 200, 400]


def base_params(g_deriv, d_signal="exogenous", exo_period=200,
                 focal_bias=0.0):
    """Triple-mode params with exogenous D-term."""
    p = S14.curvature_params(0.9)
    p["boundary_mode"] = "triple"
    p["g_form"] = 0.3
    p["g_persist"] = 0.3
    p["g_deriv"] = g_deriv
    p["b_decay_form"] = 0.01   # 2x default (faster — P term)
    p["b_decay_persist"] = 0.005  # default (slower — I term)
    p["b_decay_deriv"] = 0.02  # 4x default (fastest — D term)
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["b_growth_deriv"] = 0.2
    p["movement_bias"] = focal_bias
    p["movement_mode"] = "focal"
    p["d_signal"] = d_signal
    p["exo_period"] = exo_period
    p["exo_amplitude"] = 1.0
    return p


def run_sweep():
    t0 = time.time()
    results = {
        "config": {
            "seeds": SEEDS,
            "g_deriv_levels": G_DERIV_LEVELS,
            "exo_periods": EXO_PERIODS,
            "focal_biases": [0.0, 0.3],
            "base_config": "dual f=0.3 p=0.3, triple D-term",
        },
    }

    # --- Part 1: g_deriv sweep with focal bias ---
    print("=== Part 1: Exogenous D-term WITH focal bias (bias=0.3) ===")
    results["with_focal"] = []
    for g_deriv in G_DERIV_LEVELS:
        for ns in [2, 1]:
            for sd in SEEDS:
                p = base_params(g_deriv, focal_bias=0.3)
                r = S14.run_two_region_hetero(p, seed=sd, n_seeds=ns,
                                               mode="hetero")
                s = r["summary"]
                entry = {
                    "g_deriv": g_deriv,
                    "seed": sd,
                    "n_seeds": ns,
                    "l2_crossed": s["l2_crossed"],
                    "l2_outcome": s["l2_outcome"],
                    "l2_stable": s["l2_stable"],
                    "crossed_h7": s["crossed_h7"],
                    "cells": s["final_n_structure_cells"],
                    "left_retain": s["l2_left_retain"],
                    "right_retain": s["l2_right_retain"],
                }
                results["with_focal"].append(entry)
                if ns == 2:
                    print(f"  g_deriv={g_deriv:.2f} seed={sd}: "
                          f"l2={s['l2_crossed']} "
                          f"outcome={s['l2_outcome']:12s} "
                          f"stable={s['l2_stable']} "
                          f"h7={s['crossed_h7']} "
                          f"cells={s['final_n_structure_cells']}")

    # --- Part 2: g_deriv sweep WITHOUT focal bias ---
    print("\n=== Part 2: Exogenous D-term WITHOUT focal bias (bias=0.0) ===")
    results["without_focal"] = []
    for g_deriv in G_DERIV_LEVELS:
        for ns in [2, 1]:
            for sd in SEEDS:
                p = base_params(g_deriv, focal_bias=0.0)
                r = S14.run_two_region_hetero(p, seed=sd, n_seeds=ns,
                                               mode="hetero")
                s = r["summary"]
                entry = {
                    "g_deriv": g_deriv,
                    "seed": sd,
                    "n_seeds": ns,
                    "l2_crossed": s["l2_crossed"],
                    "l2_outcome": s["l2_outcome"],
                    "l2_stable": s["l2_stable"],
                    "crossed_h7": s["crossed_h7"],
                    "cells": s["final_n_structure_cells"],
                    "left_retain": s["l2_left_retain"],
                    "right_retain": s["l2_right_retain"],
                }
                results["without_focal"].append(entry)
                if ns == 2:
                    print(f"  g_deriv={g_deriv:.2f} seed={sd}: "
                          f"l2={s['l2_crossed']} "
                          f"outcome={s['l2_outcome']:12s} "
                          f"stable={s['l2_stable']} "
                          f"h7={s['crossed_h7']} "
                          f"cells={s['final_n_structure_cells']}")

    # --- Part 3: exo_period sweep at g_deriv=0.1, with focal bias ---
    print("\n=== Part 3: Exo period sweep (g_deriv=0.1, focal bias=0.3) ===")
    results["period_sweep"] = []
    for period in EXO_PERIODS:
        for ns in [2, 1]:
            for sd in SEEDS:
                p = base_params(0.1, exo_period=period, focal_bias=0.3)
                r = S14.run_two_region_hetero(p, seed=sd, n_seeds=ns,
                                               mode="hetero")
                s = r["summary"]
                entry = {
                    "exo_period": period,
                    "seed": sd,
                    "n_seeds": ns,
                    "l2_crossed": s["l2_crossed"],
                    "l2_outcome": s["l2_outcome"],
                    "l2_stable": s["l2_stable"],
                    "crossed_h7": s["crossed_h7"],
                    "cells": s["final_n_structure_cells"],
                }
                results["period_sweep"].append(entry)
                if ns == 2:
                    print(f"  period={period:4d} seed={sd}: "
                          f"l2={s['l2_crossed']} "
                          f"outcome={s['l2_outcome']:12s} "
                          f"stable={s['l2_stable']} "
                          f"h7={s['crossed_h7']} "
                          f"cells={s['final_n_structure_cells']}")

    # --- Summary tables ---
    print("\n=== SUMMARY: Exogenous D-term WITH focal bias ===")
    print(f"{'g_deriv':>8s} {'l2(2s)':>8s} {'coexist':>8s} "
          f"{'stable':>8s} {'h7(2s)':>8s} {'clean':>8s} "
          f"{'full':>8s} {'l2(1s)':>8s} {'h7(1s)':>8s} {'cells':>8s}")
    for g_deriv in G_DERIV_LEVELS:
        two = [e for e in results["with_focal"]
               if e["g_deriv"] == g_deriv and e["n_seeds"] == 2]
        one = [e for e in results["with_focal"]
               if e["g_deriv"] == g_deriv and e["n_seeds"] == 1]
        n_l2 = sum(1 for e in two if e["l2_crossed"])
        n_coexist = sum(1 for e in two if e["l2_outcome"] == "coexist")
        n_stable = sum(1 for e in two if e["l2_stable"])
        n_h7 = sum(1 for e in two if e["crossed_h7"])
        n_clean = sum(1 for te, oe in zip(two, one)
                      if te["l2_outcome"] == "coexist"
                      and oe["l2_outcome"] != "coexist")
        n_full = sum(1 for te, oe in zip(two, one)
                     if te["l2_crossed"] and te["l2_stable"]
                     and te["l2_outcome"] == "coexist"
                     and oe["l2_outcome"] != "coexist")
        n_l2_1 = sum(1 for e in one if e["l2_crossed"])
        n_h7_1 = sum(1 for e in one if e["crossed_h7"])
        cells = int(np.mean([e["cells"] for e in two]))
        print(f"{g_deriv:8.2f} {n_l2:7d}/4 {n_coexist:7d}/4 "
              f"{n_stable:7d}/4 {n_h7:7d}/4 {n_clean:7d}/4 "
              f"{n_full:7d}/4 {n_l2_1:7d}/4 {n_h7_1:7d}/4 "
              f"{cells:8d}")

    print("\n=== SUMMARY: Exogenous D-term WITHOUT focal bias ===")
    print(f"{'g_deriv':>8s} {'l2(2s)':>8s} {'coexist':>8s} "
          f"{'stable':>8s} {'h7(2s)':>8s} {'clean':>8s} "
          f"{'full':>8s} {'l2(1s)':>8s} {'h7(1s)':>8s} {'cells':>8s}")
    for g_deriv in G_DERIV_LEVELS:
        two = [e for e in results["without_focal"]
               if e["g_deriv"] == g_deriv and e["n_seeds"] == 2]
        one = [e for e in results["without_focal"]
               if e["g_deriv"] == g_deriv and e["n_seeds"] == 1]
        n_l2 = sum(1 for e in two if e["l2_crossed"])
        n_coexist = sum(1 for e in two if e["l2_outcome"] == "coexist")
        n_stable = sum(1 for e in two if e["l2_stable"])
        n_h7 = sum(1 for e in two if e["crossed_h7"])
        n_clean = sum(1 for te, oe in zip(two, one)
                      if te["l2_outcome"] == "coexist"
                      and oe["l2_outcome"] != "coexist")
        n_full = sum(1 for te, oe in zip(two, one)
                     if te["l2_crossed"] and te["l2_stable"]
                     and te["l2_outcome"] == "coexist"
                     and oe["l2_outcome"] != "coexist")
        n_l2_1 = sum(1 for e in one if e["l2_crossed"])
        n_h7_1 = sum(1 for e in one if e["crossed_h7"])
        cells = int(np.mean([e["cells"] for e in two]))
        print(f"{g_deriv:8.2f} {n_l2:7d}/4 {n_coexist:7d}/4 "
              f"{n_stable:7d}/4 {n_h7:7d}/4 {n_clean:7d}/4 "
              f"{n_full:7d}/4 {n_l2_1:7d}/4 {n_h7_1:7d}/4 "
              f"{cells:8d}")

    print("\n=== SUMMARY: Exo period sweep (g_deriv=0.1, focal) ===")
    print(f"{'period':>8s} {'l2(2s)':>8s} {'coexist':>8s} "
          f"{'stable':>8s} {'h7(2s)':>8s} {'cells':>8s}")
    for period in EXO_PERIODS:
        two = [e for e in results["period_sweep"]
               if e["exo_period"] == period and e["n_seeds"] == 2]
        n_l2 = sum(1 for e in two if e["l2_crossed"])
        n_coexist = sum(1 for e in two if e["l2_outcome"] == "coexist")
        n_stable = sum(1 for e in two if e["l2_stable"])
        n_h7 = sum(1 for e in two if e["crossed_h7"])
        cells = int(np.mean([e["cells"] for e in two]))
        print(f"{period:8d} {n_l2:7d}/4 {n_coexist:7d}/4 "
              f"{n_stable:7d}/4 {n_h7:7d}/4 {cells:8d}")

    # --- Determinism check ---
    print("\n=== Determinism check ===")
    p_det = base_params(0.1, focal_bias=0.0)
    r_a = S14.run_two_region_hetero(p_det, seed=42, n_seeds=2,
                                     mode="hetero")
    r_b = S14.run_two_region_hetero(p_det, seed=42, n_seeds=2,
                                     mode="hetero")
    sa, sb = r_a["summary"], r_b["summary"]
    det_ok = (sa["l2_crossed"] == sb["l2_crossed"]
              and sa["l2_outcome"] == sb["l2_outcome"]
              and abs(sa["l2_left_retain"] - sb["l2_left_retain"]) < 1e-9)
    print(f"  Determinism: {'OK' if det_ok else 'FAIL'} "
          f"(l2={sa['l2_crossed']}, outcome={sa['l2_outcome']})")

    # Write results.
    out_path = os.path.join(SIM_DIR, "output", "exo_dterm_sweep.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(S14.S._pyify(results), f, indent=2)
    print(f"\nWrote {out_path}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
