"""
n=260-300 plateau + stability-density trade-off + 1-seed leak robustness.

Queued-topics #147, #148, #149.

#147: Does g* eventually hit zero? The 1/√n (Laplace pressure) scaling predicts
g*(260)≈0.02, g*(280)≈0.01. At n=240-250, g* ≤ 0.01 (composition works at every
gain tested). Does g* plateau or hit zero at n=260-300? The LSW analogy says
the droplet dissolves when it fills the grid — but at n=250 the structures are
~4800/25,600 cells (19%). Grid may need n=300+ for LSW dissolution.

#148: The stability-density trade-off — is it boundary-mediated or density-
independent? Run n=250 at g=0 (no inhibition). If structures merge without the
boundary, degradation is boundary-mediated; if they fragment on their own, it
is a density effect independent of the boundary.

#149: The 1-seed l2_crossed leak at n=250 — does it worsen with n? Run 8 seeds
at n=240 and n=250, 1-seed only, and compare the leak rate.

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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "plateau_260_sweep.json")

GRID = 160
JITTER = 10.0

SEEDS_4 = [42, 123, 256, 999]
SEEDS_8 = [42, 123, 256, 999, 7, 100, 555, 777]

# Part 1: n=260, 280, 300 at very low gains (0.005–0.04)
# 1/√n predictions: g*(260)≈0.02, g*(280)≈0.01, g*(300)≈0.01
PLATEAU_COMBOS = [
    (260, 0.005, 0.005, "n260_g005"),
    (260, 0.01, 0.01, "n260_g010"),
    (260, 0.02, 0.02, "n260_g020"),
    (260, 0.03, 0.03, "n260_g030"),
    (280, 0.005, 0.005, "n280_g005"),
    (280, 0.01, 0.01, "n280_g010"),
    (280, 0.02, 0.02, "n280_g020"),
    (300, 0.005, 0.005, "n300_g005"),
    (300, 0.01, 0.01, "n300_g010"),
    (300, 0.02, 0.02, "n300_g020"),
]

# Part 2: n=250 at g=0 (no inhibition) — stability-density trade-off
NO_INHIB_COMBOS = [
    (250, 0.0, 0.0, "n250_g000_no_inhib"),
    (240, 0.0, 0.0, "n240_g000_no_inhib"),
    (260, 0.0, 0.0, "n260_g000_no_inhib"),
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
    """Part 1: n=260-300 plateau sweep."""
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "note": "Session 52: n=260-300 plateau (#147) + stability-density "
                "trade-off (#148) + 1-seed leak (#149)",
        "sqrt_prediction": "g* = -0.95 + 15.2/sqrt(n) → g*(260)=0.02, "
                           "g*(280)=0.01, g*(300)=0.01",
        "lsw_prediction": "g* → 0 when structure fills grid (droplet dissolves)",
    }}

    print(f"\n{'='*80}")
    print(f"  PLATEAU SWEEP: n=260, 280, 300 at g=0.005-0.03 × 4 seeds × {{2,1}}")
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
    """Part 2: n=250 at g=0 — is the stability-density trade-off boundary-mediated?"""
    results = {"note": "Part 2: no-inhibition control (#148) — is the "
                        "stability-density trade-off boundary-mediated?"}

    print(f"\n{'='*80}")
    print(f"  NO-INHIBITION CONTROL: n=240, 250, 260 at g=0 × 4 seeds × {{2,1}}")
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
              f"h7={s['h7_2s']} clean={s['clean']} full={s['full']} "
              f"cf={s['mean_coexist_frac']:.3f} "
              f"1s_l2={s['l2_1s']} 1s_h7={s['h7_1s']} "
              f"cells={s['mean_cells']} lc={s['mean_late_lc']} rc={s['mean_late_rc']}")

    return results


def run_1seed_robustness():
    """Part 3: 1-seed l2_crossed leak at n=240 vs n=250, 8 seeds."""
    results = {"note": "Part 3: 1-seed leak robustness (#149) — 8 seeds at "
                        "n=240 and n=250, 1-seed only"}

    print(f"\n{'='*80}")
    print(f"  1-SEED LEAK ROBUSTNESS: n=240, 250 at 8 seeds, 1-seed only")
    print(f"{'='*80}")

    for n, label in [(240, "n240_1seed_8s"), (250, "n250_1seed_8s")]:
        density = n / (GRID * GRID) * 1000
        # Use g=0.01 for n=240 (best config), g=0.02 for n=250
        g = 0.01 if n == 240 else 0.02
        p = make_params(n, g, g)
        entries_1 = []
        for sd in SEEDS_8:
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
            print(f"    1seed s={sd}: l2={s1['l2_crossed']} "
                  f"out={s1['l2_outcome']:>12s} h7={s1['crossed_h7']} "
                  f"cells={s1['final_n_structure_cells']}")

        n_l2 = sum(1 for e in entries_1 if e["l2_crossed"])
        n_h7 = sum(1 for e in entries_1 if e["crossed_h7"])
        n_stable = sum(1 for e in entries_1 if e["l2_stable"])
        n_coexist = sum(1 for e in entries_1 if e["l2_outcome"] == "coexist")
        results[label] = {
            "n_termites": n,
            "g": g,
            "density_per_kcell": round(density, 2),
            "seeds": SEEDS_8,
            "entries": entries_1,
            "summary": {
                "l2_leak": f"{n_l2}/8",
                "h7": f"{n_h7}/8",
                "stable": f"{n_stable}/8",
                "coexist": f"{n_coexist}/8",
                "mean_cells": int(np.mean([e["cells"] for e in entries_1])),
            },
        }
        print(f"  → {label}: l2_leak={n_l2}/8 h7={n_h7}/8 "
              f"stable={n_stable}/8 coexist={n_coexist}/8")

    return results


def run_sweep():
    t0 = time.time()

    # Part 1: plateau
    plateau_results, plateau_time = run_plateau_sweep()

    # Part 2: no-inhibition control
    no_inhib_results = run_no_inhib_sweep()

    # Part 3: 1-seed robustness
    leak_results = run_1seed_robustness()

    # Save
    all_results = {
        "plateau": plateau_results,
        "no_inhibition_control": no_inhib_results,
        "seed_1_leak_robustness": leak_results,
    }
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Summary table
    print(f"\n{'='*120}")
    print("  PLATEAU 260-300 SWEEP SUMMARY (160x160, dual, focal 0.3, jit=10)")
    print(f"{'='*120}")
    print(f"{'label':>15s} {'nT':>5s} {'dens':>6s} {'g':>5s} | "
          f"{'l2':>5s} {'coex':>5s} {'stab':>5s} {'h7':>5s} "
          f"{'clean':>6s} {'full':>5s} {'cf':>5s} | "
          f"{'l2(1s)':>6s} {'h7(1s)':>6s} {'coex(1s)':>8s} "
          f"{'cells':>6s} {'lc':>5s} {'rc':>5s}")
    print("-" * 120)

    for n, gf, gp, label in PLATEAU_COMBOS:
        if label not in plateau_results:
            continue
        s = plateau_results[label]["summary"]
        density = n / (GRID * GRID) * 1000
        print(f"{label:>15s} {n:>5d} {density:>5.2f} {gf:>5.3f} | "
              f"{s['l2_2s']:>5s} {s['coexist']:>5s} {s['stable']:>5s} "
              f"{s['h7_2s']:>5s} {s['clean']:>6s} {s['full']:>5s} "
              f"{s['mean_coexist_frac']:>5.2f} | "
              f"{s['l2_1s']:>6s} {s['h7_1s']:>6s} {s['coexist_1s']:>8s} "
              f"{s['mean_cells']:>6d} {s['mean_late_lc']:>5.1f} {s['mean_late_rc']:>5.1f}")

    print(f"\n  NO-INHIBITION CONTROL:")
    print(f"{'label':>25s} {'nT':>5s} {'dens':>6s} | "
          f"{'l2':>5s} {'coex':>5s} {'stab':>5s} {'h7':>5s} "
          f"{'clean':>6s} {'full':>5s} | "
          f"{'l2(1s)':>6s} {'h7(1s)':>6s} {'cells':>6s}")
    print("-" * 100)
    for n, gf, gp, label in NO_INHIB_COMBOS:
        if label not in no_inhib_results:
            continue
        s = no_inhib_results[label]["summary"]
        density = n / (GRID * GRID) * 1000
        print(f"{label:>25s} {n:>5d} {density:>5.2f} | "
              f"{s['l2_2s']:>5s} {s['coexist']:>5s} {s['stable']:>5s} "
              f"{s['h7_2s']:>5s} {s['clean']:>6s} {s['full']:>5s} | "
              f"{s['l2_1s']:>6s} {s['h7_1s']:>6s} {s['mean_cells']:>6d}")

    print(f"\n  1-SEED LEAK ROBUSTNESS (8 seeds):")
    for label in ["n240_1seed_8s", "n250_1seed_8s"]:
        if label not in leak_results:
            continue
        s = leak_results[label]["summary"]
        print(f"  {label:>20s}: l2_leak={s['l2_leak']} h7={s['h7']} "
              f"stable={s['stable']} coexist={s['coexist']} "
              f"mean_cells={s['mean_cells']}")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return all_results


if __name__ == "__main__":
    run_sweep()
