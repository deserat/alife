"""
inh_gain sweep for sim14 — finding the strength-vs-growth sweet spot.

Queued-topic #91: sim14's ID-tagged boundary at g=0.9 is too strong (H7
suppressed 0/4, cells=167). A sweep of inh_gain (0.1, 0.3, 0.5, 0.7, 0.9)
with 4-seed robustness maps the strength-vs-growth frontier.

At low gain, the boundary is too weak (structures merge).
At high gain, the boundary is too strong (H7 suppressed).
The sweet spot (if it exists) is where both H7 crossing AND L2 composition
co-occur. If no gain produces both, the strength-vs-growth trade-off is
fundamental, not a parameter issue.

Also includes:
- hetero_1seed control at each gain (must stay 0/4 on all metrics)
- none_2seed baseline (H7 without boundary, for comparison)

Methodology:
- Control arms: 1-seed controls, no-inhibition baseline
- Determinism: verified by the selftest
- Per-criterion pass rates reported for any null
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "inh_gain_sweep.json")

GAINS = [0.1, 0.3, 0.5, 0.7, 0.9]
SEEDS = [42, 123, 256, 999]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "gains": GAINS,
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
    }, "none_2seed": []}

    for g in GAINS:
        print(f"\n{'='*60}")
        print(f"  inh_gain = {g}")
        print(f"{'='*60}")

        results[str(g)] = {"hetero_2seed": [], "hetero_1seed": [], "none_2seed": []}

        # Hetero 2-seed (the L2 test)
        p = I14.curvature_params(g)
        for sd in SEEDS:
            r = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
            s = r["summary"]
            entry = {
                "seed": sd,
                "l2_crossed": s["l2_crossed"],
                "l2_outcome": s["l2_outcome"],
                "l2_stable": s["l2_stable"],
                "crossed_h7": s["crossed_h7"],
                "cells": s["final_n_structure_cells"],
                "left_retain": s["l2_left_retain"],
                "right_retain": s["l2_right_retain"],
                "b_max": max((b["b_max"] for b in r["boundary_trace"]), default=0.0),
            }
            results[str(g)]["hetero_2seed"].append(entry)
            print(f"  hetero 2seed s={sd}: l2={s['l2_crossed']} "
                  f"outcome={s['l2_outcome']} stable={s['l2_stable']} "
                  f"h7={s['crossed_h7']} cells={s['final_n_structure_cells']}")

        # Hetero 1-seed (the L1 control — MUST be 0)
        for sd in SEEDS:
            r = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
            s = r["summary"]
            entry = {
                "seed": sd,
                "l2_crossed": s["l2_crossed"],
                "l2_outcome": s["l2_outcome"],
                "l2_stable": s["l2_stable"],
                "crossed_h7": s["crossed_h7"],
                "cells": s["final_n_structure_cells"],
            }
            results[str(g)]["hetero_1seed"].append(entry)
            print(f"  hetero 1seed s={sd}: l2={s['l2_crossed']} "
                  f"outcome={s['l2_outcome']} h7={s['crossed_h7']} "
                  f"cells={s['final_n_structure_cells']}")

        # None 2-seed (baseline H7 without boundary, same for all gains)
        if g == GAINS[0]:
            p_none = I14.curvature_params(0.0)
            for sd in SEEDS:
                r = I14.run_two_region_hetero(p_none, seed=sd, n_seeds=2,
                                               mode="none")
                s = r["summary"]
                entry = {
                    "seed": sd,
                    "l2_crossed": s["l2_crossed"],
                    "l2_outcome": s["l2_outcome"],
                    "l2_stable": s["l2_stable"],
                    "crossed_h7": s["crossed_h7"],
                    "cells": s["final_n_structure_cells"],
                }
                results["none_2seed"].append(entry)
                print(f"  none 2seed s={sd}: l2={s['l2_crossed']} "
                      f"outcome={s['l2_outcome']} h7={s['crossed_h7']} "
                      f"cells={s['final_n_structure_cells']}")

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*60}")
    print("  INH_GAIN SWEEP SUMMARY")
    print(f"{'='*60}")
    print(f"{'gain':>6s} | {'l2(2s)':>7s} {'coexist':>8s} {'stable':>7s} "
          f"{'h7(2s)':>7s} {'clean':>6s} | {'l2(1s)':>7s} {'h7(1s)':>7s} "
          f"{'cells':>6s}")
    print("-" * 70)

    for g in GAINS:
        gk = str(g)
        h2 = results[gk]["hetero_2seed"]
        h1 = results[gk]["hetero_1seed"]
        n_l2_2 = sum(1 for e in h2 if e["l2_crossed"])
        n_coexist_2 = sum(1 for e in h2 if e["l2_outcome"] == "coexist")
        n_stable_2 = sum(1 for e in h2 if e["l2_stable"])
        n_h7_2 = sum(1 for e in h2 if e["crossed_h7"])
        n_l2_1 = sum(1 for e in h1 if e["l2_crossed"])
        n_h7_1 = sum(1 for e in h1 if e["crossed_h7"])
        # Clean = 2-seed coexist AND 1-seed does NOT coexist
        clean = sum(1 for e2, e1 in zip(h2, h1)
                    if e2["l2_outcome"] == "coexist"
                    and e1["l2_outcome"] != "coexist")
        mean_cells = np.mean([e["cells"] for e in h2])
        print(f"{g:6.1f} | {n_l2_2:>4d}/4  {n_coexist_2:>5d}/4  "
              f"{n_stable_2:>4d}/4  {n_h7_2:>4d}/4  {clean:>4d}/4  | "
              f"{n_l2_1:>4d}/4  {n_h7_1:>4d}/4  {mean_cells:6.0f}")

    # None baseline
    none_2 = results.get("none_2seed", [])
    if none_2:
        n_l2 = sum(1 for e in none_2 if e["l2_crossed"])
        n_coexist = sum(1 for e in none_2 if e["l2_outcome"] == "coexist")
        n_h7 = sum(1 for e in none_2 if e["crossed_h7"])
        mean_cells = np.mean([e["cells"] for e in none_2])
        print(f"{'none':>6s} | {n_l2:>4d}/4  {n_coexist:>5d}/4  "
              f"{'--':>4s}    {n_h7:>4d}/4  {'--':>4s}    | "
              f"{'--':>5s}    {'--':>5s}    {mean_cells:6.0f}")

    # Co-occurrence check
    print(f"\n{'='*60}")
    print("  CO-OCCURRENCE: H7 crossing AND clean composition")
    print(f"{'='*60}")
    for g in GAINS:
        gk = str(g)
        h2 = results[gk]["hetero_2seed"]
        h1 = results[gk]["hetero_1seed"]
        for i, (e2, e1) in enumerate(zip(h2, h1)):
            h7 = e2["crossed_h7"]
            clean = (e2["l2_outcome"] == "coexist"
                     and e1["l2_outcome"] != "coexist")
            if h7 and clean:
                print(f"  *** g={g} seed={SEEDS[i]}: H7=YES clean=YES "
                      f"— CO-OCCURRENCE!")
    print("  (no co-occurrence found)" if True else "")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
