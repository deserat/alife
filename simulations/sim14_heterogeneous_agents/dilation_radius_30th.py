"""
Dilation radius sweep — is the 30th ceiling about absolute structure size
or the structure-to-boundary ratio? (#250)

The 30th ceiling on 160×160 (radius=8) is ~43.6% fill (n=3000, stable 0/4).
On 80×80 (radius=8) it's at 64–76% fill — 23–35pp above the Moore threshold.

The absolute-spatial-scale principle (#234) predicts the 30th ceiling is about
the ratio of structure linear size to the boundary's spatial scale (dilation
radius). If so, changing the dilation radius on 160×160 should shift the 30th
ceiling:
  - radius=4  (narrower): boundary has less reach → less over-splitting →
               30th ceiling at HIGHER fill (or not reached within grid)
  - radius=16 (wider):   boundary has more reach → more over-splitting →
               30th ceiling at LOWER fill

If the 30th ceiling is about ABSOLUTE structure size (independent of radius),
all three radii should show stable=0/4 at the same fill%.

Config: 160×160, dual mode, focal bias=0.3, per_step jitter=10.
Sweep: radius ∈ {4, 8, 16} × n ∈ {2000, 2500, 3000} × g ∈ {0.001, 0.003} × 4 seeds.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "dilation_radius_30th.json")

GRID = 160
JITTER = 10.0

SEEDS_4 = [42, 123, 256, 999]

# radius × n × gain combos
COMBOS = [
    # radius=4
    (4,  2000, 0.001, 0.001, "r04_n2000_g001"),
    (4,  2000, 0.003, 0.003, "r04_n2000_g003"),
    (4,  2500, 0.001, 0.001, "r04_n2500_g001"),
    (4,  2500, 0.003, 0.003, "r04_n2500_g003"),
    (4,  3000, 0.001, 0.001, "r04_n3000_g001"),
    (4,  3000, 0.003, 0.003, "r04_n3000_g003"),
    # radius=8 (baseline — the 30th ceiling reference)
    (8,  2000, 0.001, 0.001, "r08_n2000_g001"),
    (8,  2000, 0.003, 0.003, "r08_n2000_g003"),
    (8,  2500, 0.001, 0.001, "r08_n2500_g001"),
    (8,  2500, 0.003, 0.003, "r08_n2500_g003"),
    (8,  3000, 0.001, 0.001, "r08_n3000_g001"),
    (8,  3000, 0.003, 0.003, "r08_n3000_g003"),
    # radius=16
    (16, 2000, 0.001, 0.001, "r16_n2000_g001"),
    (16, 2000, 0.003, 0.003, "r16_n2000_g003"),
    (16, 2500, 0.001, 0.001, "r16_n2500_g001"),
    (16, 2500, 0.003, 0.003, "r16_n2500_g003"),
    (16, 3000, 0.001, 0.001, "r16_n3000_g001"),
    (16, 3000, 0.003, 0.003, "r16_n3000_g003"),
]


def make_params(radius, n_termites, g_form, g_persist):
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
    p["direct_radius"] = radius
    return p


def run_combo(radius, n_termites, g_form, g_persist, label, seeds):
    entries_2 = []
    entries_1 = []
    for sd in seeds:
        p = make_params(radius, n_termites, g_form, g_persist)

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
        "note": "Session 96: dilation radius sweep — is the 30th ceiling about absolute structure size or the structure-to-boundary ratio? (#250)",
        "30th_ceiling_160_r08": "~43.6% fill (n=3000, stable 0/4 at all gains)",
        "moore_threshold": "~40.7%",
        "prediction": "radius=4 → higher 30th ceiling; radius=16 → lower 30th ceiling (if ratio-dependent); same fill if absolute-size-dependent",
    }}

    for radius, n_t, g_f, g_p, label in COMBOS:
        print(f"\n=== {label} (r={radius}, n={n_t}, g={g_f}) ===")
        e2, e1 = run_combo(radius, n_t, g_f, g_p, label, SEEDS_4)
        s = summarize(e2, e1)
        results[label] = {
            "radius": radius,
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

    elapsed = time.time() - t0
    print(f"\nTotal time: {elapsed:.1f}s")

    # Final summary table
    print("\n=== DILATION RADIUS 30TH CEILING SUMMARY ===")
    print(f"{'r':>3s} {'n':>5s} {'g':>6s} {'fill%':>7s} {'l2':>5s} {'coex':>5s} {'stab':>5s} {'h7':>5s} {'cf':>6s} {'lc':>5s} {'rc':>5s}")
    for key in results:
        if key == "config":
            continue
        r = results[key]
        s = r["summary"]
        rad = r.get("radius", "?")
        n_t = r.get("n_termites", "?")
        g = r.get("g_form", 0.0)
        print(f"{rad:>3} {n_t:>5} {g:>6.3f} {s['mean_fill_pct']:>7.1f} "
              f"{s['l2']:>5s} {s['coexist']:>5s} {s['stable']:>5s} {s['h7']:>5s} "
              f"{s['mean_coexist_frac']:>6.3f} {s['mean_late_lc']:>5.1f} {s['mean_late_rc']:>5.1f}")


if __name__ == "__main__":
    main()
