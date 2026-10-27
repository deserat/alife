"""
Focused dilation radius test — 3 key combos to test the 30th ceiling shift.

Already have:
  r04_n2000_g001: fill=41.3%, stable=0/4 (from dilation_radius_30th.py partial)
  r08_n2000_g001: fill=41.2%, stable=3/4 (from n1800_plateau_sweep.json)
  r08_n1500_g003: fill=39.4%, stable=3/4 (from n1200_plateau_sweep.json)

Need:
  r04_n1500_g001: does stable survive at lower n with radius=4?
  r16_n2000_g001: does wider radius shift the 30th ceiling higher?
  r16_n1500_g001: does wider radius preserve stability at lower n?
"""
import os, sys, json, time
import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14

GRID = 160
JITTER = 10.0
SWEEP_PATH = os.path.join(SIM14_DIR, "output", "dilation_radius_30th_focused.json")

COMBOS = [
    (4,  1500, 0.001, 0.001, "r04_n1500_g001", [42, 123, 256, 999]),
    (16, 1500, 0.001, 0.001, "r16_n1500_g001", [42, 123, 256, 999]),
    (16, 2000, 0.001, 0.001, "r16_n2000_g001", [42, 123, 256, 999]),
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
            "b_max": round(max((b["b_max"] for b in r2["boundary_trace"]), default=0.0), 2),
        }
        entries_2.append(e2)
        print(f"    2seed s={sd}: out={s2['l2_outcome']:>12s} stable={s2['l2_stable']} "
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

    n = len(entries_2)
    n_stable = sum(1 for e in entries_2 if e["l2_stable"])
    n_coexist = sum(1 for e in entries_2 if e["l2_outcome"] == "coexist")
    n_h7 = sum(1 for e in entries_2 if e["crossed_h7"])
    n_l2_1 = sum(1 for e in entries_1 if e["l2_crossed"])
    n_h7_1 = sum(1 for e in entries_1 if e["crossed_h7"])
    n_stable_1 = sum(1 for e in entries_1 if e["l2_stable"])
    n_coexist_1 = sum(1 for e in entries_1 if e["l2_outcome"] == "coexist")
    clean = sum(1 for e2, e1 in zip(entries_2, entries_1) if e2["l2_outcome"] == "coexist" and e1["l2_outcome"] != "coexist")
    mean_fill = float(np.mean([e["fill_pct"] for e in entries_2]))
    mean_cf = float(np.mean([e["l2_coexist_frac"] for e in entries_2]))
    mean_lc = float(np.mean([e["late_mean_lc"] for e in entries_2]))
    mean_rc = float(np.mean([e["late_mean_rc"] for e in entries_2]))
    summary = {
        "l2": f"{sum(1 for e in entries_2 if e['l2_crossed'])}/{n}",
        "coexist": f"{n_coexist}/{n}", "stable": f"{n_stable}/{n}", "h7": f"{n_h7}/{n}",
        "clean": f"{clean}/{n}", "full": f"{sum(1 for e2,e1 in zip(entries_2,entries_1) if e2['crossed_h7'] and e2['l2_outcome']=='coexist' and e1['l2_outcome']!='coexist' and e2['l2_stable'])}/{n}",
        "l2_1s": f"{n_l2_1}/{n}", "h7_1s": f"{n_h7_1}/{n}", "stable_1s": f"{n_stable_1}/{n}", "coexist_1s": f"{n_coexist_1}/{n}",
        "mean_fill_pct": round(mean_fill, 2), "mean_coexist_frac": round(mean_cf, 3),
        "mean_late_lc": round(mean_lc, 2), "mean_late_rc": round(mean_rc, 2),
    }
    return entries_2, entries_1, summary

def main():
    t0 = time.time()
    results = {"config": {
        "grid": GRID, "jitter": JITTER,
        "note": "Session 96: focused dilation radius test — 30th ceiling shift (#250)",
        "baseline_r08": {
            "n2000_g001": "fill=41.2%, stable=3/4 (from n1800_plateau)",
            "n1500_g003": "fill=39.4%, stable=3/4 (from n1200_plateau)",
        },
        "r04_n2000_g001": "fill=41.3%, stable=0/4 (from dilation_radius_30th.py partial)",
    }}

    for radius, n_t, g_f, g_p, label, seeds in COMBOS:
        print(f"\n=== {label} (r={radius}, n={n_t}, g={g_f}) ===")
        e2, e1, s = run_combo(radius, n_t, g_f, g_p, label, seeds)
        results[label] = {
            "radius": radius, "n_termites": n_t, "g_form": g_f, "g_persist": g_p,
            "hetero_2seed": e2, "hetero_1seed": e1, "summary": s,
        }
        print(f"  SUMMARY: stable={s['stable']} coexist={s['coexist']} h7={s['h7']} "
              f"fill={s['mean_fill_pct']:.1f}% cf={s['mean_coexist_frac']} "
              f"lc={s['mean_late_lc']} rc={s['mean_late_rc']}")
        with open(SWEEP_PATH, "w") as f:
            json.dump(results, f, indent=2)

    print(f"\nTotal time: {time.time()-t0:.1f}s")
    print("\n=== 30TH CEILING SHIFT ===")
    print(f"{'radius':>6s} {'n':>5s} {'fill%':>7s} {'stable':>7s} {'lc':>5s} {'rc':>5s}")
    for key in results:
        if key == "config": continue
        r = results[key]
        s = r["summary"]
        print(f"r={r['radius']:>4} {r['n_termites']:>5} {s['mean_fill_pct']:>7.1f} "
              f"{s['stable']:>7s} {s['mean_late_lc']:>5.1f} {s['mean_late_rc']:>5.1f}")
    # Also print baseline
    print("  (baseline r=8 n=2000 g=0.001: fill=41.2%, stable=3/4)")
    print("  (baseline r=8 n=1500 g=0.003: fill=39.4%, stable=3/4)")
    print("  (r=4      n=2000 g=0.001: fill=41.3%, stable=0/4)")

if __name__ == "__main__":
    main()
