"""
n=4000–5000 plateau sweep — does the log fill cap hold toward the percolation threshold?

Queued-topics #193, #194 (top priority from Session 71).

The 1/√n (Laplace pressure) scaling has been confirmed from n=170 to n=3000
(~3% to ~44% grid fill). The 43rd mechanism: the 1/√n scaling is CONSERVATIVE
— actual optimal gain is HIGHER than the formula predicts. At n=2500–3000
the formula predicts deeply NEGATIVE g* (g*≈-0.64 to -0.65) but composition
survives at every gain tested.

The 44th mechanism: the fill cap rises LOGARITHMICALLY —
fill% ≈ 13.1·log₁₀(n) − 2.14 (R²=0.991). The fill cap trajectory:
  n=1200: ~38.3%
  n=1500: ~39.4%
  n=1800: ~40.4%
  n=2000: ~41.2%
  n=2500: ~42.1%
  n=3000: ~43.6%
The log fit predicts ~45.1% at n=4000 and ~46.3% at n=5000.

At n=4000–5000 (~46% fill per log fit), the questions:
1. Does g* stay positive? (43rd mechanism, 7th density range)
2. Does the log fill cap hold or break toward the percolation threshold? (44th)
3. Does the 30th mechanism (stability-density trade-off) recover at very low gain? (#194)
4. Does the 1-seed structural guarantee hold? (stochastic at n=2500–3000)

The 1/√n formula g* = -0.95 + 15.2/√n predicts:
  g*(4000)≈-0.71, g*(5000)≈-0.74 — both deeply negative.
The 43rd mechanism says actual > predicted.

At n=3000, stable collapsed to 0/4 at ALL gains (0.001–0.005). The 30th
mechanism is a gain-density interaction. Testing very low gains (0.0005–0.003)
at n=4000–5000 tests whether stability can be recovered at very low gain
(#194) — or whether the persistence condition has collapsed entirely.

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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "n4000_plateau_sweep.json")

GRID = 160
JITTER = 10.0

SEEDS_4 = [42, 123, 256, 999]

# Part 1: n=4000, 5000 at gains 0.0005, 0.001, 0.003
# 1/√n predictions: g*(4000)≈-0.71, g*(5000)≈-0.74 (deeply negative!)
# The 43rd mechanism says actual > predicted, so test small positive gains.
# At n=3000, stable collapsed to 0/4 at all gains. Testing 0.0005 (very low)
# to see if stability can be recovered (#194).
PLATEAU_COMBOS = [
    (4000, 0.0005, 0.0005, "n4000_g0005"),
    (4000, 0.001,  0.001,  "n4000_g001"),
    (4000, 0.003,  0.003,  "n4000_g003"),
    (5000, 0.0005, 0.0005, "n5000_g0005"),
    (5000, 0.001,  0.001,  "n5000_g001"),
    (5000, 0.003,  0.003,  "n5000_g003"),
]

# Part 2: no-inhibition control at n=4000 and n=5000
NO_INHIB_COMBOS = [
    (4000, 0.0, 0.0, "n4000_g000_no_inhib"),
    (5000, 0.0, 0.0, "n5000_g000_no_inhib"),
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


def make_no_inhib_params(n_termites):
    """Params with no boundary inhibition (g=0)."""
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_combo(n_termites, g_form, g_persist, label, seeds, no_inhib=False):
    """Run a single combo across seeds."""
    if no_inhib:
        p = make_no_inhib_params(n_termites)
    else:
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
            "l2_coexist_frac": round(s2.get("l2_coexist_frac", 0.0), 3),
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
              f"cf={e2['l2_coexist_frac']:.2f} "
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
            "l2_coexist_frac": round(s1.get("l2_coexist_frac", 0.0), 3),
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
    full = sum(1 for e2, e1 in zip(entries_2, entries_1)
               if e2["crossed_h7"]
               and e2["l2_outcome"] == "coexist"
               and e1["l2_outcome"] != "coexist"
               and e2["l2_stable"])
    mean_cells = int(np.mean([e["cells"] for e in entries_2]))
    mean_late_lc = float(np.mean([e["late_mean_lc"] for e in entries_2]))
    mean_late_rc = float(np.mean([e["late_mean_rc"] for e in entries_2]))
    mean_coexist_frac = float(np.mean([e["l2_coexist_frac"] for e in entries_2]))
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
        "mean_coexist_frac": round(mean_coexist_frac, 3),
    }


def run_plateau_sweep():
    """Part 1: n=4000–5000 plateau sweep."""
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "note": "Session 72: n=4000-5000 ultra-high-density plateau (#193, #194)",
        "sqrt_prediction": "g* = -0.95 + 15.2/sqrt(n) → "
                          "g*(4000)≈-0.71 (NEG), g*(5000)≈-0.74 (NEG)",
        "log_fill_cap": "fill% ≈ 13.1·log₁₀(n) − 2.14 → "
                       "~45.1% at n=4000, ~46.3% at n=5000",
        "lsw_prediction": "g* → 0 when structure fills grid (droplet dissolves)",
        "percolation_threshold": "~59% (2D site percolation, square lattice)",
        "fill_cap_trajectory": {
            "n1200": "~38.3%",
            "n1500": "~39.4%",
            "n1800": "~40.4%",
            "n2000": "~41.2%",
            "n2500": "~42.1%",
            "n3000": "~43.6%",
        },
        "mechanism_43": "1/sqrt(n) scaling is CONSERVATIVE — actual > predicted",
        "mechanism_44": "fill cap logarithmic R²=0.991 (Session 71)",
        "mechanism_30": "stability-density trade-off — stable 0/4 at n=3000 (all gains)",
    }}

    print(f"\n{'='*80}")
    print(f"  N4000 PLATEAU: n=4000, 5000 at g=0.0005-0.003 × 4 seeds × {{2,1}}")
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
              f"cf={s['mean_coexist_frac']:.3f} "
              f"1s_l2={s['l2_1s']} 1s_h7={s['h7_1s']} "
              f"cells={s['mean_cells']} lc={s['mean_late_lc']} rc={s['mean_late_rc']}")

    return results, time.time() - t0


def run_no_inhib_sweep():
    """Part 2: no-inhibition control at n=4000 and n=5000."""
    results = {"note": "Part 2: no-inhibition control — does fragmentation "
                        "persist at n=4000-5000 without the boundary?"}

    print(f"\n{'='*80}")
    print(f"  NO-INHIBITION CONTROL: n=4000, 5000 at g=0 × 4 seeds × {{2,1}}")
    print(f"{'='*80}")

    for n, gf, gp, label in NO_INHIB_COMBOS:
        density = n / (GRID * GRID) * 1000
        print(f"\n  {label} (n={n}, density={density:.2f}/kcell, g=0)")
        e2, e1 = run_combo(n, gf, gp, label, SEEDS_4, no_inhib=True)
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
              f"h7={s['h7_2s']} cells={s['mean_cells']}")

    return results


def run_sweep():
    t0 = time.time()

    # Part 1: ultra-high-density plateau
    plateau_results, plateau_time = run_plateau_sweep()

    # Part 2: no-inhibition control
    no_inhib_results = run_no_inhib_sweep()

    # Save
    all_results = {
        "plateau": plateau_results,
        "no_inhibition_control": no_inhib_results,
    }
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Summary table
    print(f"\n{'='*120}")
    print("  N4000 PLATEAU SWEEP SUMMARY (160x160, dual, focal 0.3, jit=10)")
    print(f"{'='*120}")
    print(f"{'label':>15s} {'nT':>5s} {'dens':>6s} {'g':>7s} | "
          f"{'l2':>5s} {'coex':>5s} {'stab':>5s} {'h7':>5s} "
          f"{'clean':>6s} {'full':>5s} {'cf':>5s} | "
          f"{'l2(1s)':>6s} {'h7(1s)':>6s} {'coex(1s)':>8s} "
          f"{'cells':>6s} {'fill%':>5s}")
    print("-" * 120)

    for n, gf, gp, label in PLATEAU_COMBOS:
        if label not in plateau_results:
            continue
        s = plateau_results[label]["summary"]
        density = n / (GRID * GRID) * 1000
        fill_pct = round(s["mean_cells"] / (GRID * GRID) * 100, 1)
        print(f"{label:>15s} {n:>5d} {density:>5.2f} {gf:>7.4f} | "
              f"{s['l2_2s']:>5s} {s['coexist']:>5s} {s['stable']:>5s} "
              f"{s['h7_2s']:>5s} {s['clean']:>6s} {s['full']:>5s} "
              f"{s['mean_coexist_frac']:>5.2f} | "
              f"{s['l2_1s']:>6s} {s['h7_1s']:>6s} {s['coexist_1s']:>8s} "
              f"{s['mean_cells']:>6d} {fill_pct:>5.1f}%")

    print(f"\n  NO-INHIBITION CONTROL:")
    for n, gf, gp, label in NO_INHIB_COMBOS:
        if label not in no_inhib_results:
            continue
        s = no_inhib_results[label]["summary"]
        fill_pct = round(s["mean_cells"] / (GRID * GRID) * 100, 1)
        print(f"  {label:>25s}: l2={s['l2_2s']} coexist={s['coexist']} "
              f"stable={s['stable']} h7={s['h7_2s']} "
              f"cells={s['mean_cells']} fill={fill_pct}%")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return all_results


if __name__ == "__main__":
    run_sweep()
