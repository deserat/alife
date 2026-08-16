"""
Hybrid suppression-curve sweep for sim14 — testing whether a hybrid curve
combines gradient formation with binary stability.

Queued-topic #99: Session 31 found binary gates (decoupled) are more stable
but less effective at L2 formation than gradient gates (proportional) at the
same max gain. A hybrid curve is proportional at low B_norm (wide coverage
for formation) with a fixed plateau at high B_norm (stability):

    supp = min(g * B_norm / (1 + B_norm), g * k)

where k is a plateau fraction (0 < k <= 1).  k=1.0 reproduces the gradient
(the min is never binding since the gradient's max is g).  Low k approaches
a weaker binary gate.

This tests whether the persistence-formation trade-off is truly about curve
shape or can be broken by a hybrid that combines both properties.

Sweep: modes [proportional, decoupled, hybrid(k=0.5), hybrid(k=0.7),
              hybrid(k=0.8), hybrid(k=0.9)]
       × gains [0.3, 0.5, 0.7, 0.9] × 4 seeds × {2-seed, 1-seed}

Methodology:
  - Control arms: 1-seed controls (must stay 0/4)
  - Determinism: verified by the selftest
  - Per-criterion pass rates reported
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "hybrid_sweep.json")

GAINS = [0.3, 0.5, 0.7, 0.9]
SEEDS = [42, 123, 256, 999]

# Modes: (label, boundary_mode, hybrid_k or None)
MODES = [
    ("proportional", "proportional", None),
    ("decoupled", "decoupled", None),
    ("hybrid_k05", "hybrid", 0.5),
    ("hybrid_k07", "hybrid", 0.7),
    ("hybrid_k08", "hybrid", 0.8),
    ("hybrid_k09", "hybrid", 0.9),
]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "gains": GAINS,
        "seeds": SEEDS,
        "modes": [m[0] for m in MODES],
        "grid_size": 80,
        "n_termites": 150,
        "steps": 2000,
        "sample_every": 25,
        "channel": "curvature",
        "d": 1.0,
        "material_decay": 0.002,
        "deposit_prob_base": 0.01,
        "direct_radius": I14.DIRECT_RADIUS,
    }}

    for mode_label, bmode, hk in MODES:
        for g in GAINS:
            key = f"{mode_label}_{g}"
            results[key] = {"hetero_2seed": [], "hetero_1seed": []}
            print(f"\n{'='*60}")
            hk_str = f" k={hk}" if hk is not None else ""
            print(f"  mode={mode_label}  inh_gain={g}{hk_str}")
            print(f"{'='*60}")

            p = I14.curvature_params(g)
            p["boundary_mode"] = bmode
            if hk is not None:
                p["hybrid_k"] = hk

            for sd in SEEDS:
                # 2-seed (L2 test)
                r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2,
                                               mode="hetero")
                s2 = r2["summary"]
                entry2 = {
                    "seed": sd,
                    "l2_crossed": s2["l2_crossed"],
                    "l2_outcome": s2["l2_outcome"],
                    "l2_stable": s2["l2_stable"],
                    "crossed_h7": s2["crossed_h7"],
                    "cells": s2["final_n_structure_cells"],
                    "left_retain": s2["l2_left_retain"],
                    "right_retain": s2["l2_right_retain"],
                    "b_max": max((b["b_max"] for b in r2["boundary_trace"]),
                                 default=0.0),
                }
                results[key]["hetero_2seed"].append(entry2)
                print(f"  {mode_label} 2seed s={sd}: l2={s2['l2_crossed']} "
                      f"outcome={s2['l2_outcome']} stable={s2['l2_stable']} "
                      f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']}")

                # 1-seed (L1 control — must be 0)
                r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1,
                                               mode="hetero")
                s1 = r1["summary"]
                entry1 = {
                    "seed": sd,
                    "l2_crossed": s1["l2_crossed"],
                    "l2_outcome": s1["l2_outcome"],
                    "l2_stable": s1["l2_stable"],
                    "crossed_h7": s1["crossed_h7"],
                    "cells": s1["final_n_structure_cells"],
                }
                results[key]["hetero_1seed"].append(entry1)
                print(f"  {mode_label} 1seed s={sd}: l2={s1['l2_crossed']} "
                      f"outcome={s1['l2_outcome']} h7={s1['crossed_h7']} "
                      f"cells={s1['final_n_structure_cells']}")

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*90}")
    print("  HYBRID SWEEP SUMMARY")
    print(f"{'='*90}")
    print(f"{'mode':>14s} {'gain':>5s} | {'l2(2s)':>7s} {'coexist':>8s} "
          f"{'stable':>7s} {'h7(2s)':>7s} {'clean':>6s} | "
          f"{'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 95)

    for mode_label, _, _ in MODES:
        for g in GAINS:
            key = f"{mode_label}_{g}"
            h2 = results[key]["hetero_2seed"]
            h1 = results[key]["hetero_1seed"]
            n_l2_2 = sum(1 for e in h2 if e["l2_crossed"])
            n_coexist_2 = sum(1 for e in h2 if e["l2_outcome"] == "coexist")
            n_stable_2 = sum(1 for e in h2 if e["l2_stable"])
            n_h7_2 = sum(1 for e in h2 if e["crossed_h7"])
            n_l2_1 = sum(1 for e in h1 if e["l2_crossed"])
            n_h7_1 = sum(1 for e in h1 if e["crossed_h7"])
            clean = sum(1 for e2, e1 in zip(h2, h1)
                        if e2["l2_outcome"] == "coexist"
                        and e1["l2_outcome"] != "coexist")
            mean_cells = np.mean([e["cells"] for e in h2])
            print(f"{mode_label:>14s} {g:5.1f} | {n_l2_2:>4d}/4  {n_coexist_2:>5d}/4  "
                  f"{n_stable_2:>4d}/4  {n_h7_2:>4d}/4  {clean:>4d}/4  | "
                  f"{n_l2_1:>4d}/4  {n_h7_1:>4d}/4  {mean_cells:6.0f}")

    # Co-occurrence check
    print(f"\n{'='*90}")
    print("  CO-OCCURRENCE: H7 crossing AND clean composition AND stable")
    print(f"{'='*90}")
    found_any = False
    for mode_label, _, _ in MODES:
        for g in GAINS:
            key = f"{mode_label}_{g}"
            h2 = results[key]["hetero_2seed"]
            h1 = results[key]["hetero_1seed"]
            for i, (e2, e1) in enumerate(zip(h2, h1)):
                h7 = e2["crossed_h7"]
                clean = (e2["l2_outcome"] == "coexist"
                         and e1["l2_outcome"] != "coexist")
                stable = e2["l2_stable"]
                if h7 and clean:
                    found_any = True
                    tag = " + STABLE!" if stable else ""
                    print(f"  *** {mode_label} g={g} seed={SEEDS[i]}: "
                          f"H7=YES clean=YES{tag}")
    if not found_any:
        print("  (no co-occurrence found)")

    # Mode comparison at each gain
    print(f"\n{'='*90}")
    print("  MODE COMPARISON (stable + L2 + H7 at each gain)")
    print(f"{'='*90}")
    for g in GAINS:
        print(f"\n  g={g}:")
        for mode_label, _, _ in MODES:
            key = f"{mode_label}_{g}"
            h2 = results[key]["hetero_2seed"]
            n_h7 = sum(1 for e in h2 if e["crossed_h7"])
            n_l2 = sum(1 for e in h2 if e["l2_crossed"])
            n_coexist = sum(1 for e in h2 if e["l2_outcome"] == "coexist")
            n_stable = sum(1 for e in h2 if e["l2_stable"])
            mean_cells = np.mean([e["cells"] for e in h2])
            print(f"    {mode_label:>14s}: H7={n_h7}/4 L2={n_l2}/4 "
                  f"coexist={n_coexist}/4 stable={n_stable}/4 "
                  f"cells={mean_cells:.0f}")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
