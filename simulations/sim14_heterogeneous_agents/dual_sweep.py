"""
Dual B-field sweep for sim14 — testing whether separate B fields for
formation and persistence break the persistence-formation trade-off.

Queued-topic #101: The hybrid curve (Session 32) combines gradient formation
and binary persistence on ONE wire (the same B field). The cap constrains
both: it limits the gradient's max (reducing formation) while providing the
plateau (improving persistence). The tension persists.

The dual mode uses TWO B fields with separate growth/decay dynamics:
  - B_form: gradient suppression (proportional), faster decay (more responsive)
  - B_persist: binary suppression (fixed), slower decay (more memory)
  - Total: supp = min(g_form * Bf_norm/(1+Bf_norm) + g_persist * [Bp>0.01], 0.99)

This tests whether the two-wire principle requires truly separate channels
(different fields, different dynamics) or whether one field with a hybrid
curve suffices.

Prediction: if separate fields break the trade-off (full co-occurrence > 2/4),
the two-wire principle is confirmed as a design requirement. If not, the
trade-off is more fundamental than channel separation.

Sweep: g_form [0.2, 0.3, 0.5] × g_persist [0.3, 0.5, 0.7]
       × 4 seeds × {2-seed, 1-seed}
       b_decay_form = 0.01 (2x default), b_decay_persist = 0.005 (default)

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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "dual_sweep.json")

G_FORMS = [0.2, 0.3, 0.5]
G_PERSISTS = [0.3, 0.5, 0.7]
SEEDS = [42, 123, 256, 999]


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "g_forms": G_FORMS,
        "g_persists": G_PERSISTS,
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
        "b_decay_form": 0.01,
        "b_decay_persist": 0.005,
        "b_growth_form": 0.1,
        "b_growth_persist": 0.1,
    }}

    for g_form in G_FORMS:
        for g_persist in G_PERSISTS:
            key = f"dual_f{g_form}_p{g_persist}"
            results[key] = {"hetero_2seed": [], "hetero_1seed": []}
            print(f"\n{'='*60}")
            print(f"  dual  g_form={g_form}  g_persist={g_persist}")
            print(f"{'='*60}")

            p = I14.curvature_params(0.5)  # inh_gain > 0 to activate boundary
            p["boundary_mode"] = "dual"
            p["g_form"] = g_form
            p["g_persist"] = g_persist
            p["b_decay_form"] = 0.01
            p["b_decay_persist"] = 0.005

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
                print(f"  dual 2seed s={sd}: l2={s2['l2_crossed']} "
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
                print(f"  dual 1seed s={sd}: l2={s1['l2_crossed']} "
                      f"outcome={s1['l2_outcome']} h7={s1['crossed_h7']} "
                      f"cells={s1['final_n_structure_cells']}")

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*95}")
    print("  DUAL SWEEP SUMMARY")
    print(f"{'='*95}")
    print(f"{'g_form':>7s} {'g_persist':>10s} | {'l2(2s)':>7s} {'coexist':>8s} "
          f"{'stable':>7s} {'h7(2s)':>7s} {'clean':>6s} | "
          f"{'l2(1s)':>7s} {'h7(1s)':>7s} {'cells':>6s}")
    print("-" * 100)

    for g_form in G_FORMS:
        for g_persist in G_PERSISTS:
            key = f"dual_f{g_form}_p{g_persist}"
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
            print(f"{g_form:7.1f} {g_persist:10.1f} | {n_l2_2:>4d}/4  {n_coexist_2:>5d}/4  "
                  f"{n_stable_2:>4d}/4  {n_h7_2:>4d}/4  {clean:>4d}/4  | "
                  f"{n_l2_1:>4d}/4  {n_h7_1:>4d}/4  {mean_cells:6.0f}")

    # Co-occurrence check
    print(f"\n{'='*95}")
    print("  CO-OCCURRENCE: H7 crossing AND clean composition AND stable")
    print(f"{'='*95}")
    found_any = False
    for g_form in G_FORMS:
        for g_persist in G_PERSISTS:
            key = f"dual_f{g_form}_p{g_persist}"
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
                    print(f"  *** dual f={g_form} p={g_persist} "
                          f"seed={SEEDS[i]}: H7=YES clean=YES{tag}")
    if not found_any:
        print("  (no co-occurrence found)")

    # Max suppression comparison
    print(f"\n{'='*95}")
    print("  MAX SUPPRESSION ANALYSIS (g_form + g_persist)")
    print(f"{'='*95}")
    for g_form in G_FORMS:
        for g_persist in G_PERSISTS:
            max_supp = min(g_form + g_persist, 0.99)
            key = f"dual_f{g_form}_p{g_persist}"
            h2 = results[key]["hetero_2seed"]
            n_h7 = sum(1 for e in h2 if e["crossed_h7"])
            n_stable = sum(1 for e in h2 if e["l2_stable"])
            n_l2 = sum(1 for e in h2 if e["l2_crossed"])
            print(f"  f={g_form} p={g_persist} max_supp={max_supp:.2f}: "
                  f"H7={n_h7}/4 L2={n_l2}/4 stable={n_stable}/4")

    print(f"\nWrote {SWEEP_PATH}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    run_sweep()
