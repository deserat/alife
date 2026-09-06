"""
n=240-250 plateau sweep — queued-topic #144 (continuation of #140, #137).

The 1/√n (Laplace pressure) scaling predicts g*(240)≈0.04, g*(250)≈0.02.
The linear fit (falsified at n=200, Session 47) predicts g*(240)≈0.
The LSW analogy says g* should hit zero when the structure fills the grid
(the droplet dissolves into the continuous phase).

At n=240-250, structures fill most of the 160×160 grid. The 1-seed
structural guarantee should be at its strongest (more material = more
curvature routing = tighter concentration). Does g* plateau at a small
positive value, or does it truly hit zero?

Key predictions:
- If g*≈0.02-0.04 still produces 4/4 coexist → 1/√n holds, g*→0 asymptotically
- If no gain produces coexist → g* has hit zero (LSW: droplet dissolves)
- If the 1-seed control is 0/4 at all gains → structural guarantee strengthens

Config: 160×160, dual mode, focal bias=0.3, per_step jitter=10.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "plateau_240_sweep.json")

GRID = 160
JITTER = 10.0

SEEDS_4 = [42, 123, 256, 999]

# n=240 and n=250 at very low gains (0.01–0.06)
# 1/√n predictions: g*(240)≈0.04, g*(250)≈0.02
PLATEAU_COMBOS = [
    (240, 0.01, 0.01, "n240_g001"),
    (240, 0.02, 0.02, "n240_g002"),
    (240, 0.03, 0.03, "n240_g003"),
    (240, 0.04, 0.04, "n240_g004"),
    (240, 0.06, 0.06, "n240_g006"),
    (250, 0.01, 0.01, "n250_g001"),
    (250, 0.02, 0.02, "n250_g002"),
    (250, 0.03, 0.03, "n250_g003"),
    (250, 0.04, 0.04, "n250_g004"),
    (250, 0.06, 0.06, "n250_g006"),
]


def make_params(n_termites, g_form, g_persist):
    """Build params for the sweep."""
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["boundary_mode"] = "dual"
    p["g_form"] = g_form
    p["g_persist"] = g_persist
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_combo(n_termites, g_form, g_persist, label, seeds):
    """Run a single (n, g) combo across seeds."""
    p = make_params(n_termites, g_form, g_persist)
    entries_2 = []
    entries_1 = []

    for sd in seeds:
        # 2-seed
        r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s2 = r2["summary"]
        e2 = {
            "seed": sd,
            "l2_crossed": s2["l2_crossed"],
            "l2_outcome": s2["l2_outcome"],
            "l2_stable": s2["l2_stable"],
            "crossed_h7": s2["crossed_h7"],
            "cells": s2["final_n_structure_cells"],
            "left_retain": round(s2["l2_left_retain"], 4),
            "right_retain": round(s2["l2_right_retain"], 4),
            "late_mean_lc": round(s2.get("l2_late_mean_lc", 0.0), 2),
            "late_mean_rc": round(s2.get("l2_late_mean_rc", 0.0), 2),
            "b_max": round(max((b["b_max"] for b in r2["boundary_trace"]),
                              default=0.0), 2),
        }
        entries_2.append(e2)
        print(f"    2seed s={sd}: l2={s2['l2_crossed']} "
              f"out={s2['l2_outcome']:>12s} stable={s2['l2_stable']} "
              f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']} "
              f"lc={e2['late_mean_lc']} rc={e2['late_mean_rc']}")

        # 1-seed control
        r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
        s1 = r1["summary"]
        e1 = {
            "seed": sd,
            "l2_crossed": s1["l2_crossed"],
            "l2_outcome": s1["l2_outcome"],
            "l2_stable": s1["l2_stable"],
            "crossed_h7": s1["crossed_h7"],
            "cells": s1["final_n_structure_cells"],
        }
        entries_1.append(e1)

    return entries_2, entries_1


def summarize(entries_2, entries_1, n_seeds):
    """Compute summary metrics."""
    n = n_seeds
    n_l2_2 = sum(1 for e in entries_2 if e["l2_crossed"])
    n_coexist_2 = sum(1 for e in entries_2 if e["l2_outcome"] == "coexist")
    n_stable_2 = sum(1 for e in entries_2 if e["l2_stable"])
    n_h7_2 = sum(1 for e in entries_2 if e["crossed_h7"])
    n_l2_1 = sum(1 for e in entries_1 if e["l2_crossed"])
    n_h7_1 = sum(1 for e in entries_1 if e["crossed_h7"])
    n_stable_1 = sum(1 for e in entries_1 if e["l2_stable"])
    n_coexist_1 = sum(1 for e in entries_1 if e["l2_outcome"] == "coexist")
    clean = sum(1 for e2, e1 in zip(entries_2, entries_1)
                if e2["l2_outcome"] == "coexist"
                and e1["l2_outcome"] != "coexist")
    # full = H7 + coexist + stable + clean (1-seed not coexist)
    full = sum(1 for e2, e1 in zip(entries_2, entries_1)
               if e2["crossed_h7"]
               and e2["l2_outcome"] == "coexist"
               and e1["l2_outcome"] != "coexist"
               and e2["l2_stable"])
    # stable_l2-based composition: use stable_l2 as primary
    n_stable_l2_2 = sum(1 for e in entries_2 if e["l2_stable"])
    mean_cells = int(np.mean([e["cells"] for e in entries_2]))
    mean_late_lc = float(np.mean([e["late_mean_lc"] for e in entries_2]))
    mean_late_rc = float(np.mean([e["late_mean_rc"] for e in entries_2]))
    return {
        "l2_2s": f"{n_l2_2}/{n}",
        "coexist": f"{n_coexist_2}/{n}",
        "stable": f"{n_stable_2}/{n}",
        "h7_2s": f"{n_h7_2}/{n}",
        "clean": f"{clean}/{n}",
        "full": f"{full}/{n}",
        "l2_1s": f"{n_l2_1}/{n}",
        "h7_1s": f"{n_h7_1}/{n}",
        "stable_1s": f"{n_stable_1}/{n}",
        "coexist_1s": f"{n_coexist_1}/{n}",
        "mean_cells": mean_cells,
        "mean_late_lc": round(mean_late_lc, 2),
        "mean_late_rc": round(mean_late_rc, 2),
    }


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "note": "Session 51: n=240-250 plateau (#144) — where does g* hit zero?",
        "linear_prediction": "g* = 0.82 - 0.0036*n → g*(240)=0.00, g*(250)=-0.08 (falsified)",
        "sqrt_prediction": "g* = -0.95 + 15.2/sqrt(n) → g*(240)=0.04, g*(250)=0.02",
        "lsw_prediction": "g* → 0 when structure fills grid (droplet dissolves)",
    }}

    print(f"\n{'='*80}")
    print(f"  PLATEAU SWEEP: n=240, 250 at g=0.01-0.06 × 4 seeds × {{2,1}}")
    print(f"{'='*80}")

    for n, gf, gp, label in PLATEAU_COMBOS:
        density = n / (GRID * GRID) * 1000
        print(f"\n  {label} (n={n}, density={density:.2f}/kcell, g=({gf},{gp}))")
        e2, e1 = run_combo(n, gf, gp, label, SEEDS_4)
        results[label] = {
            "n_termites": n,
            "g_form": gf,
            "g_persist": gp,
            "density_per_kcell": round(density, 2),
            "hetero_2seed": e2,
            "hetero_1seed": e1,
            "summary": summarize(e2, e1, len(SEEDS_4)),
        }
        s = results[label]["summary"]
        print(f"  → l2={s['l2_2s']} coexist={s['coexist']} stable={s['stable']} "
              f"h7={s['h7_2s']} clean={s['clean']} full={s['full']} "
              f"1s_l2={s['l2_1s']} 1s_h7={s['h7_1s']} "
              f"1s_coex={s['coexist_1s']} 1s_stab={s['stable_1s']} "
              f"cells={s['mean_cells']} lc={s['mean_late_lc']} rc={s['mean_late_rc']}")

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*110}")
    print("  PLATEAU 240-250 SWEEP SUMMARY (160x160, dual, focal 0.3, jit=10)")
    print(f"{'='*110}")
    print(f"{'label':>15s} {'nT':>5s} {'dens':>6s} {'g':>5s} | "
          f"{'l2':>5s} {'coex':>5s} {'stab':>5s} {'h7':>5s} "
          f"{'clean':>6s} {'full':>5s} | "
          f"{'l2(1s)':>6s} {'h7(1s)':>6s} {'coex(1s)':>8s} {'stab(1s)':>8s} "
          f"{'cells':>6s} {'lc':>5s} {'rc':>5s}")
    print("-" * 110)

    for n, gf, gp, label in PLATEAU_COMBOS:
        if label not in results:
            continue
        s = results[label]["summary"]
        density = n / (GRID * GRID) * 1000
        print(f"{label:>15s} {n:>5d} {density:>5.2f} {gf:>5.2f} | "
              f"{s['l2_2s']:>5s} {s['coexist']:>5s} {s['stable']:>5s} "
              f"{s['h7_2s']:>5s} {s['clean']:>6s} {s['full']:>5s} | "
              f"{s['l2_1s']:>6s} {s['h7_1s']:>6s} {s['coexist_1s']:>8s} "
              f"{s['stable_1s']:>8s} {s['mean_cells']:>6d} "
              f"{s['mean_late_lc']:>5.1f} {s['mean_late_rc']:>5.1f}")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
