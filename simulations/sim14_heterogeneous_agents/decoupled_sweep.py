"""
Decoupled boundary sweep for sim14 — testing whether decoupling boundary
strength from co-presence precision breaks the strength-vs-growth trade-off.

Queued-topic #92: The ID-based co-presence is both more specific AND stronger
than spatial versions, because the signal is higher and more localized.
B's suppression is proportional to B_norm, which is proportional to
co-presence, which is higher for ID-based signals. A decoupled design:
the boundary grows where two IDs meet (specificity from IDs), but the
suppression strength is fixed (not proportional to B_norm magnitude).

This tests whether the strength-vs-growth trade-off is caused by the
coupling between signal precision and boundary strength, or by the
boundary mechanism itself.

Design:
  - "proportional" mode: supp = g * B_norm / (1 + B_norm)  [original]
  - "decoupled" mode: supp = g if B_norm > 0.01 else 0     [new]

Both modes use the SAME B field (grown from ID co-presence), the SAME
b_scale, and the SAME inh_gain. Only the suppression curve differs.

Sweep: gains [0.3, 0.5, 0.7, 0.9] × modes [proportional, decoupled]
× 4 seeds × {2-seed, 1-seed}.

Methodology:
  - Control arms: 1-seed controls (must stay 0/4), no-inhibition baseline
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "decoupled_sweep.json")

GAINS = [0.3, 0.5, 0.7, 0.9]
MODES = ["proportional", "decoupled"]
SEEDS = [42, 123, 256, 999]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "gains": GAINS,
        "modes": MODES,
        "seeds": SEEDS,
        "grid_size": 80,
        "n_termites": 150,
        "steps": 2000,
        "sample_every": 25,
        "channel": "curvature",
        "d": 1.0,
        "material_decay": 0.002,
        "deposit_prob_base": 0.01,
        "direct_radius": I14.DIRECT_RADIUS,
        "decoupled_threshold": 0.01,
    }}

    for mode in MODES:
        for g in GAINS:
            key = f"{mode}_{g}"
            results[key] = {"hetero_2seed": [], "hetero_1seed": []}
            print(f"\n{'='*60}")
            print(f"  mode={mode}  inh_gain={g}")
            print(f"{'='*60}")

            p = I14.curvature_params(g)
            p["boundary_mode"] = mode

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
                print(f"  {mode} 2seed s={sd}: l2={s2['l2_crossed']} "
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
                print(f"  {mode} 1seed s={sd}: l2={s1['l2_crossed']} "
                      f"outcome={s1['l2_outcome']} h7={s1['crossed_h7']} "
                      f"cells={s1['final_n_structure_cells']}")

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*70}")
    print("  DECOUPLED SWEEP SUMMARY")
    print(f"{'='*70}")
    print(f"{'mode':>12s} {'gain':>5s} | {'l2(2s)':>7s} {'coexist':>8s} "
          f"{'stable':>7s} {'h7(2s)':>7s} {'clean':>6s} | "
          f"{'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 80)

    for mode in MODES:
        for g in GAINS:
            key = f"{mode}_{g}"
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
            print(f"{mode:>12s} {g:5.1f} | {n_l2_2:>4d}/4  {n_coexist_2:>5d}/4  "
                  f"{n_stable_2:>4d}/4  {n_h7_2:>4d}/4  {clean:>4d}/4  | "
                  f"{n_l2_1:>4d}/4  {n_h7_1:>4d}/4  {mean_cells:6.0f}")

    # Co-occurrence check
    print(f"\n{'='*70}")
    print("  CO-OCCURRENCE: H7 crossing AND clean composition")
    print(f"{'='*70}")
    found_any = False
    for mode in MODES:
        for g in GAINS:
            key = f"{mode}_{g}"
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
                    print(f"  *** {mode} g={g} seed={SEEDS[i]}: "
                          f"H7=YES clean=YES{tag}")
    if not found_any:
        print("  (no co-occurrence found)")

    # Mode comparison
    print(f"\n{'='*70}")
    print("  MODE COMPARISON (decoupled vs proportional)")
    print(f"{'='*70}")
    for g in GAINS:
        prop_key = f"proportional_{g}"
        dec_key = f"decoupled_{g}"
        ph2 = results[prop_key]["hetero_2seed"]
        dh2 = results[dec_key]["hetero_2seed"]
        prop_h7 = sum(1 for e in ph2 if e["crossed_h7"])
        dec_h7 = sum(1 for e in dh2 if e["crossed_h7"])
        prop_l2 = sum(1 for e in ph2 if e["l2_crossed"])
        dec_l2 = sum(1 for e in dh2 if e["l2_crossed"])
        prop_stable = sum(1 for e in ph2 if e["l2_stable"])
        dec_stable = sum(1 for e in dh2 if e["l2_stable"])
        prop_cells = np.mean([e["cells"] for e in ph2])
        dec_cells = np.mean([e["cells"] for e in dh2])
        print(f"  g={g}: H7 {prop_h7}/4 vs {dec_h7}/4 | "
              f"L2 {prop_l2}/4 vs {dec_l2}/4 | "
              f"stable {prop_stable}/4 vs {dec_stable}/4 | "
              f"cells {prop_cells:.0f} vs {dec_cells:.0f}")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
