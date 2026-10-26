"""
80×80 high-density plateau sweep — does the 30th ceiling shift with grid size?

Queued-topic #247 (from Session 94): If the 30th ceiling is the Moore threshold
(a universal fill fraction ~40.7%), it should be the same fill fraction on all
grid sizes. If it's boundary-specific, it might shift.

The 30th ceiling on 160×160 is ~43.6% fill (n=3000, stable 0/4 at all gains).
The existing 80×80 data (grid_fill_cap_scaling.json) shows stability at:
  - n=75  (fill 29%): stable 4/4
  - n=150 (fill 48%): stable 4/4  ← ABOVE the 160×160's 30th ceiling!
  - n=200 (fill 57%): stable 4/4  ← WAY above
  - n=250 (fill 61%): stable 4/4  ← WAY above

So the 30th ceiling does NOT hold at the same fill fraction on 80×80.
Stability persists at fill fractions well above the 160×160's 30th ceiling.

But we haven't pushed n high enough on 80×80 to find where stability actually
collapses. The 80×80 grid has 6400 cells; at n=600, the density is 93.75/kc.

This sweep runs n=300, 400, 500, 600 on 80×80 at g=0.005 and 0.01, 4 seeds,
plus no-inhibition controls, to find the 30th ceiling on 80×80 and compare
the fill fraction to the 160×160's 43.6%.

The 50th mechanism (fill depends on absolute n, not density) means the fill
at a given n is HIGHER on 80×80 than on 160×160. So the 30th ceiling is
reached at a LOWER n on 80×80 — but at what fill fraction?

Config: 80×80, dual mode, focal bias=0.3, per_step jitter=10.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "grid80_high_density_plateau.json")

GRID = 80
JITTER = 10.0

SEEDS_4 = [42, 123, 256, 999]

PLATEAU_COMBOS = [
    (300, 0.005, 0.005, "n300_g005"),
    (300, 0.01,  0.01,  "n300_g010"),
    (400, 0.005, 0.005, "n400_g005"),
    (400, 0.01,  0.01,  "n400_g010"),
    (500, 0.005, 0.005, "n500_g005"),
    (500, 0.01,  0.01,  "n500_g010"),
    (600, 0.005, 0.005, "n600_g005"),
    (600, 0.01,  0.01,  "n600_g010"),
]

NO_INHIB_COMBOS = [
    (300, "n300_g000_no_inhib"),
    (500, "n500_g000_no_inhib"),
    (600, "n600_g000_no_inhib"),
]


def make_params(n_termites, g_form, g_persist):
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
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_combo(n_termites, g_form, g_persist, label, seeds, no_inhib=False):
    entries_2 = []
    entries_1 = []
    for sd in seeds:
        if no_inhib:
            p = make_no_inhib_params(n_termites)
        else:
            p = make_params(n_termites, g_form, g_persist)

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
            "fill_pct": round(100.0 * s2["final_n_structure_cells"] / (GRID*GRID), 2),
            "late_mean_lc": round(s2.get("l2_late_mean_lc", 0.0), 2),
            "late_mean_rc": round(s2.get("l2_late_mean_rc", 0.0), 2),
            "b_max": round(max((b["b_max"] for b in r2["boundary_trace"]),
                              default=0.0), 2),
        }
        entries_2.append(e2)
        print(f"    2seed s={sd}: l2={s2['l2_crossed']} "
              f"out={s2['l2_outcome']:>12s} stable={s2['l2_stable']} "
              f"cf={e2['l2_coexist_frac']:.2f} h7={s2['crossed_h7']} "
              f"fill={e2['fill_pct']:.1f}% lc={e2['late_mean_lc']} rc={e2['late_mean_rc']}")

        r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
        s1 = r1["summary"]
        e1 = {
            "seed": sd,
            "l2_crossed": s1["l2_crossed"],
            "l2_outcome": s1["l2_outcome"],
            "l2_stable": s1["l2_stable"],
            "crossed_h7": s1["crossed_h7"],
            "cells": s1["final_n_structure_cells"],
            "fill_pct": round(100.0 * s1["final_n_structure_cells"] / (GRID*GRID), 2),
        }
        entries_1.append(e1)

    return entries_2, entries_1


def summarize(entries_2, entries_1):
    n = len(entries_2)
    n_l2 = sum(1 for e in entries_2 if e["l2_crossed"])
    n_coexist = sum(1 for e in entries_2 if e["l2_outcome"] == "coexist")
    n_stable = sum(1 for e in entries_2 if e["l2_stable"])
    n_h7 = sum(1 for e in entries_2 if e["crossed_h7"])
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
    mean_fill = float(np.mean([e["fill_pct"] for e in entries_2]))
    mean_cf = float(np.mean([e["l2_coexist_frac"] for e in entries_2]))
    mean_lc = float(np.mean([e["late_mean_lc"] for e in entries_2]))
    mean_rc = float(np.mean([e["late_mean_rc"] for e in entries_2]))
    return {
        "l2": f"{n_l2}/{n}",
        "coexist": f"{n_coexist}/{n}",
        "stable": f"{n_stable}/{n}",
        "h7": f"{n_h7}/{n}",
        "clean": f"{clean}/{n}",
        "full": f"{full}/{n}",
        "l2_1s": f"{n_l2_1}/{n}",
        "h7_1s": f"{n_h7_1}/{n}",
        "stable_1s": f"{n_stable_1}/{n}",
        "coexist_1s": f"{n_coexist_1}/{n}",
        "mean_cells": mean_cells,
        "mean_fill_pct": round(mean_fill, 2),
        "mean_coexist_frac": round(mean_cf, 3),
        "mean_late_lc": round(mean_lc, 2),
        "mean_late_rc": round(mean_rc, 2),
    }


def main():
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "note": "Session 95: 80×80 high-density plateau — does the 30th ceiling shift with grid size? (#247)",
        "30th_ceiling_160": "~43.6% fill (n=3000, stable 0/4 at all gains)",
        "moore_threshold": "~40.7%",
        "existing_80x80_data": {
            "n75_fill29": "stable 4/4",
            "n150_fill48": "stable 4/4",
            "n200_fill57": "stable 4/4",
            "n250_fill61": "stable 4/4",
        },
    }}

    # Plateau combos
    for n_t, g_f, g_p, label in PLATEAU_COMBOS:
        print(f"\n=== {label} (n={n_t}, g={g_f}) ===")
        e2, e1 = run_combo(n_t, g_f, g_p, label, SEEDS_4)
        s = summarize(e2, e1)
        results[label] = {
            "n_termites": n_t,
            "g_form": g_f,
            "g_persist": g_p,
            "hetero_2seed": e2,
            "hetero_1seed": e1,
            "summary": s,
        }
        print(f"  SUMMARY: l2={s['l2']} coexist={s['coexist']} stable={s['stable']} "
              f"h7={s['h7']} fill={s['mean_fill_pct']:.1f}% "
              f"cf={s['mean_coexist_frac']} lc={s['mean_late_lc']} rc={s['mean_late_rc']}")
        # Save incrementally
        with open(SWEEP_PATH, "w") as f:
            json.dump(results, f, indent=2)

    # No-inhibition controls
    for n_t, label in NO_INHIB_COMBOS:
        print(f"\n=== {label} (n={n_t}, no inhib) ===")
        e2, e1 = run_combo(n_t, 0.0, 0.0, label, SEEDS_4, no_inhib=True)
        s = summarize(e2, e1)
        results[label] = {
            "n_termites": n_t,
            "no_inhib": True,
            "hetero_2seed": e2,
            "hetero_1seed": e1,
            "summary": s,
        }
        print(f"  SUMMARY: l2={s['l2']} coexist={s['coexist']} stable={s['stable']} "
              f"h7={s['h7']} fill={s['mean_fill_pct']:.1f}% "
              f"cf={s['mean_coexist_frac']} lc={s['mean_late_lc']} rc={s['mean_late_rc']}")
        with open(SWEEP_PATH, "w") as f:
            json.dump(results, f, indent=2)

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")

    # Final summary
    print("\n=== 80×80 HIGH-DENSITY PLATEAU SUMMARY ===")
    print(f"{'n':>5s} {'g':>6s} {'fill%':>7s} {'l2':>5s} {'coex':>5s} {'stab':>5s} {'h7':>5s} {'cf':>6s} {'lc':>5s} {'rc':>5s}")
    for key in results:
        if key == "config":
            continue
        r = results[key]
        s = r["summary"]
        n_t = r.get("n_termites", "?")
        g = r.get("g_form", 0.0)
        print(f"{n_t:>5} {g:>6.3f} {s['mean_fill_pct']:>7.1f} "
              f"{s['l2']:>5s} {s['coexist']:>5s} {s['stable']:>5s} {s['h7']:>5s} "
              f"{s['mean_coexist_frac']:>6.3f} {s['mean_late_lc']:>5.1f} {s['mean_late_rc']:>5.1f}")


if __name__ == "__main__":
    main()
