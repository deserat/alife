"""
n=320–400 high-density plateau + 8-seed robustness at n=300 g=0.02.

Queued-topics #150, #152 (top priority from Session 52).

#150: Does g* ever hit zero? The 1/√n (Laplace pressure) scaling predicts
g*(320)≈0.01, g*(350)≈0.006, g*(400)≈0.003. At n=300 (~21% grid fill), g*
never hit zero — composition was alive at every gain tested. At n=320–400
(~25–31% grid fill), does the structure finally fill enough for the LSW
"droplet dissolves" prediction? Or does g* approach zero asymptotically
without ever reaching it in any finite system?

#152: 8-seed robustness at n=300 g=0.02 — the highest mean coexist_frac
(0.775). Does the 4/4 coexist, 3/4 stable, 4/4 clean, 3/4 full hold at
8 seeds, or is it a small-sample artifact?

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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "high_density_plateau_sweep.json")

GRID = 160
JITTER = 10.0

SEEDS_4 = [42, 123, 256, 999]
SEEDS_8 = [42, 123, 256, 999, 7, 100, 555, 777]

# Part 1: n=320, 350, 400 at very low gains (0.005–0.02)
# 1/√n predictions: g*(320)≈0.01, g*(350)≈0.006, g*(400)≈0.003
# At these densities, structures fill ~25–31% of the 160×160 grid.
# If g* has hit zero, no gain should produce coexist.
PLATEAU_COMBOS = [
    (320, 0.005, 0.005, "n320_g005"),
    (320, 0.01, 0.01, "n320_g010"),
    (320, 0.02, 0.02, "n320_g020"),
    (350, 0.005, 0.005, "n350_g005"),
    (350, 0.01, 0.01, "n350_g010"),
    (350, 0.02, 0.02, "n350_g020"),
    (400, 0.005, 0.005, "n400_g005"),
    (400, 0.01, 0.01, "n400_g010"),
    (400, 0.02, 0.02, "n400_g020"),
]

# Part 2: no-inhibition control at n=320 and n=400
# Without the boundary, do the structures fragment or merge at high density?
NO_INHIB_COMBOS = [
    (320, 0.0, 0.0, "n320_g000_no_inhib"),
    (400, 0.0, 0.0, "n400_g000_no_inhib"),
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
    """Part 1: n=320–400 plateau sweep."""
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "note": "Session 53: n=320-400 high-density plateau (#150) "
                "+ 8-seed robustness at n=300 g=0.02 (#152)",
        "sqrt_prediction": "g* = -0.95 + 15.2/sqrt(n) → "
                           "g*(320)=0.01, g*(350)=0.006, g*(400)=0.003",
        "lsw_prediction": "g* → 0 when structure fills grid (droplet dissolves)",
        "grid_fill_at_n400": "~31% (n=400, ~8000 cells / 25600)",
    }}

    print(f"\n{'='*80}")
    print(f"  HIGH-DENSITY PLATEAU: n=320, 350, 400 at g=0.005-0.02 × 4 seeds × {{2,1}}")
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
    """Part 2: no-inhibition control at n=320 and n=400."""
    results = {"note": "Part 2: no-inhibition control — does fragmentation "
                        "persist at high density without the boundary?"}

    print(f"\n{'='*80}")
    print(f"  NO-INHIBITION CONTROL: n=320, 400 at g=0 × 4 seeds × {{2,1}}")
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
              f"cells={s['mean_cells']}")

    return results


def run_8seed_robustness():
    """Part 3: 8-seed robustness at n=300 g=0.02 — the highest coexist_frac."""
    results = {"note": "Part 3: 8-seed robustness at n=300 g=0.02 (#152) — "
                        "is the 0.775 coexist_frac a small-sample artifact?"}

    print(f"\n{'='*80}")
    print(f"  8-SEED ROBUSTNESS: n=300 g=0.02 × 8 seeds × {{2,1}}")
    print(f"{'='*80}")

    n = 300
    g = 0.02
    p = make_params(n, g, g)
    entries_2 = []
    entries_1 = []

    for sd in SEEDS_8:
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
            "late_mean_lc": round(s2.get("l2_late_mean_lc", 0.0), 2),
            "late_mean_rc": round(s2.get("l2_late_mean_rc", 0.0), 2),
        }
        entries_2.append(e2)
        print(f"    2seed s={sd}: l2={s2['l2_crossed']} "
              f"out={s2['l2_outcome']:>12s} stable={s2['l2_stable']} "
              f"cf={e2['l2_coexist_frac']:.2f} "
              f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']}")

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

    s = summarize(entries_2, entries_1, 8)
    results["n300_g020_8seed"] = {
        "n_termites": n,
        "g": g,
        "density_per_kcell": round(n / (GRID * GRID) * 1000, 2),
        "hetero_2seed": entries_2,
        "hetero_1seed": entries_1,
        "summary": s,
    }
    print(f"\n  → 8-seed: l2={s['l2_2s']} coexist={s['coexist']} "
          f"stable={s['stable']} h7={s['h7_2s']} clean={s['clean']} "
          f"full={s['full']} cf={s['mean_coexist_frac']:.3f} "
          f"1s_l2={s['l2_1s']} 1s_h7={s['h7_1s']}")

    return results


def run_sweep():
    t0 = time.time()

    # Part 1: high-density plateau
    plateau_results, plateau_time = run_plateau_sweep()

    # Part 2: no-inhibition control
    no_inhib_results = run_no_inhib_sweep()

    # Part 3: 8-seed robustness at n=300
    robustness_results = run_8seed_robustness()

    # Save
    all_results = {
        "plateau": plateau_results,
        "no_inhibition_control": no_inhib_results,
        "n300_8seed_robustness": robustness_results,
    }
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Summary table
    print(f"\n{'='*120}")
    print("  HIGH-DENSITY PLATEAU SWEEP SUMMARY (160x160, dual, focal 0.3, jit=10)")
    print(f"{'='*120}")
    print(f"{'label':>15s} {'nT':>5s} {'dens':>6s} {'g':>5s} | "
          f"{'l2':>5s} {'coex':>5s} {'stab':>5s} {'h7':>5s} "
          f"{'clean':>6s} {'full':>5s} {'cf':>5s} | "
          f"{'l2(1s)':>6s} {'h7(1s)':>6s} {'coex(1s)':>8s} "
          f"{'cells':>6s} {'lc':>5s} {'rc':>5s} {'fill%':>5s}")
    print("-" * 120)

    for n, gf, gp, label in PLATEAU_COMBOS:
        if label not in plateau_results:
            continue
        s = plateau_results[label]["summary"]
        density = n / (GRID * GRID) * 1000
        fill_pct = round(s["mean_cells"] / (GRID * GRID) * 100, 1)
        print(f"{label:>15s} {n:>5d} {density:>5.2f} {gf:>5.3f} | "
              f"{s['l2_2s']:>5s} {s['coexist']:>5s} {s['stable']:>5s} "
              f"{s['h7_2s']:>5s} {s['clean']:>6s} {s['full']:>5s} "
              f"{s['mean_coexist_frac']:>5.2f} | "
              f"{s['l2_1s']:>6s} {s['h7_1s']:>6s} {s['coexist_1s']:>8s} "
              f"{s['mean_cells']:>6d} {s['mean_late_lc']:>5.1f} {s['mean_late_rc']:>5.1f} "
              f"{fill_pct:>5.1f}%")

    print(f"\n  NO-INHIBITION CONTROL:")
    for n, gf, gp, label in NO_INHIB_COMBOS:
        if label not in no_inhib_results:
            continue
        s = no_inhib_results[label]["summary"]
        density = n / (GRID * GRID) * 1000
        print(f"  {label:>25s}: l2={s['l2_2s']} coexist={s['coexist']} "
              f"stable={s['stable']} h7={s['h7_2s']} "
              f"cells={s['mean_cells']}")

    print(f"\n  8-SEED ROBUSTNESS (n=300 g=0.02):")
    s = robustness_results["n300_g020_8seed"]["summary"]
    print(f"  l2={s['l2_2s']} coexist={s['coexist']} stable={s['stable']} "
          f"h7={s['h7_2s']} clean={s['clean']} full={s['full']} "
          f"cf={s['mean_coexist_frac']:.3f} "
          f"1s_l2={s['l2_1s']} 1s_h7={s['h7_1s']}")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return all_results


if __name__ == "__main__":
    run_sweep()
