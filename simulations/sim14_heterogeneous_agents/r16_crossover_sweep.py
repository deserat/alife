"""
Session 98: Test r=16 on 160×160 (10% of grid) with separable max-filter (#254).

THE QUESTION: Session 97 found the over-splitting → under-splitting crossover
requires r/grid ≥ 10%. The 80×80 r=8 (10%) data showed under-splitting, but
that was confounded by the 50th mechanism (grid-size effect). r=16 on 160×160
is 10% of grid on the SAME grid — the clean test.

If r=16 on 160×160 shows under-splitting (lc/rc < 1): crossover is a
  boundary-width effect (r/grid = 10%).
If r=16 on 160×160 shows over-splitting (lc/rc > 3): the 80×80
  under-splitting is a grid-size effect (the 50th mechanism).

Uses separable max filter optimization (verified identical to original in S97).
4 seeds for robustness.
"""
import os, sys, json, time
import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14
import sim13 as I13

GRID = 160
JITTER = 10.0
SEEDS = [42, 999, 123, 256]
G_FORM = 0.001
G_PERSIST = 0.001

def _dilate_no_x_wrap_fast(arr, radius):
    """Separable max filter: O(2r) instead of O(r²). Verified identical."""
    size_y, size_x = arr.shape
    # Y: periodic (torus in y)
    temp = arr.copy()
    for dy in range(-radius, radius + 1):
        if dy == 0:
            continue
        y_idx = (np.arange(size_y) - dy) % size_y
        temp = np.maximum(temp, arr[y_idx, :])
    # X: zero-padded (no x-wrapping)
    result = temp.copy()
    for dx in range(-radius, radius + 1):
        if dx == 0:
            continue
        shifted = np.zeros_like(temp)
        if dx > 0:
            shifted[:, dx:] = temp[:, :size_x - dx]
        elif dx < 0:
            adx = abs(dx)
            shifted[:, :size_x - adx] = temp[:, adx:]
        else:
            shifted[:] = temp
        result = np.maximum(result, shifted)
    return result

I13._dilate_no_x_wrap = _dilate_no_x_wrap_fast

OUTPUT_PATH = os.path.join(SIM14_DIR, "output", "r16_crossover_sweep.json")

COMBOS = [
    (16, 3000, "r16_n3000"),
    (16, 5000, "r16_n5000"),
]

def make_params(radius, n_termites):
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["boundary_mode"] = "dual"
    p["g_form"] = G_FORM; p["g_persist"] = G_PERSIST
    p["b_decay_form"] = 0.01; p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1; p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3; p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER; p["jitter_mode"] = "per_step"
    p["direct_radius"] = radius
    return p

def run_combo(radius, n_termites, label):
    entries_2 = []; entries_1 = []
    for sd in SEEDS:
        p = make_params(radius, n_termites)
        r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s2 = r2["summary"]
        e2 = {
            "seed": sd, "l2_crossed": s2["l2_crossed"],
            "l2_outcome": s2["l2_outcome"], "l2_stable": s2["l2_stable"],
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
              f"fill={e2['fill_pct']:.1f}% lc={e2['late_mean_lc']} rc={e2['late_mean_rc']}", flush=True)
        r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
        s1 = r1["summary"]
        e1 = {"seed": sd, "l2_crossed": s1["l2_crossed"], "l2_outcome": s1["l2_outcome"],
              "l2_stable": s1["l2_stable"], "crossed_h7": s1["crossed_h7"],
              "cells": s1["final_n_structure_cells"],
              "fill_pct": round(100.0 * s1["final_n_structure_cells"] / (GRID*GRID), 2)}
        entries_1.append(e1)
    n = len(entries_2)
    n_stable = sum(1 for e in entries_2 if e["l2_stable"])
    n_coexist = sum(1 for e in entries_2 if e["l2_outcome"] == "coexist")
    n_h7 = sum(1 for e in entries_2 if e["crossed_h7"])
    n_l2_1 = sum(1 for e in entries_1 if e["l2_crossed"])
    n_h7_1 = sum(1 for e in entries_1 if e["crossed_h7"])
    n_stable_1 = sum(1 for e in entries_1 if e["l2_stable"])
    n_coexist_1 = sum(1 for e in entries_1 if e["l2_outcome"] == "coexist")
    clean = sum(1 for e2, e1 in zip(entries_2, entries_1)
                if e2["l2_outcome"] == "coexist" and e1["l2_outcome"] != "coexist")
    mean_fill = float(np.mean([e["fill_pct"] for e in entries_2]))
    mean_cf = float(np.mean([e["l2_coexist_frac"] for e in entries_2]))
    mean_lc = float(np.mean([e["late_mean_lc"] for e in entries_2]))
    mean_rc = float(np.mean([e["late_mean_rc"] for e in entries_2]))
    if mean_lc > 3 or mean_rc > 3:
        mode = "over-splitting"
    elif mean_lc < 1 and mean_rc < 1:
        mode = "under-splitting"
    else:
        mode = "mixed"
    # L/r ratio at the ceiling
    L_est = np.sqrt(mean_fill / 100.0 * GRID * GRID / 2.0)
    L_over_r = round(L_est / radius, 1)
    summary = {
        "l2": f"{sum(1 for e in entries_2 if e['l2_crossed'])}/{n}",
        "coexist": f"{n_coexist}/{n}", "stable": f"{n_stable}/{n}", "h7": f"{n_h7}/{n}",
        "clean": f"{clean}/{n}",
        "full": f"{sum(1 for e2,e1 in zip(entries_2,entries_1) if e2['crossed_h7'] and e2['l2_outcome']=='coexist' and e1['l2_outcome']!='coexist' and e2['l2_stable'])}/{n}",
        "l2_1s": f"{n_l2_1}/{n}", "h7_1s": f"{n_h7_1}/{n}",
        "stable_1s": f"{n_stable_1}/{n}", "coexist_1s": f"{n_coexist_1}/{n}",
        "mean_fill_pct": round(mean_fill, 2), "mean_coexist_frac": round(mean_cf, 3),
        "mean_late_lc": round(mean_lc, 2), "mean_late_rc": round(mean_rc, 2),
        "degradation_mode": mode,
        "radius_pct": round(100.0 * (2*radius) / GRID, 2),
        "L_over_r": L_over_r,
    }
    return entries_2, entries_1, summary

def main():
    t0 = time.time()
    results = {"config": {"grid": GRID, "jitter": JITTER, "g_form": G_FORM,
                          "g_persist": G_PERSIST, "seeds": SEEDS,
                          "note": "Session 98: r=16 crossover test (#254) — 10% of grid on 160x160"},
               "baselines": {
                   "r4_160_2.5pct":  {"n2000": "fill=41.3%, stable=0/4, over-splitting, L/r=18.2"},
                   "r8_160_5pct":   {"n3000": "fill=43.6%, stable=0/4, over-splitting, L/r=9.3"},
                   "r10_160_6.25pct": {"n3000": "fill=43.1%, stable=0/2, over-splitting, L/r=7.4"},
                   "r12_160_7.5pct":  {"n3000": "fill=43.3%, stable=0/2, over-splitting, L/r=6.2"},
                   "r8_80_10pct":   {"n600":  "fill=76.3%, stable=2/4, under-splitting"},
               }}
    for radius, n_t, label in COMBOS:
        print(f"\n=== {label} (r={radius}, n={n_t}) ===", flush=True)
        t1 = time.time()
        e2, e1, s = run_combo(radius, n_t, label)
        dt = time.time() - t1
        results[label] = {"radius": radius, "n_termites": n_t, "g_form": G_FORM,
                         "g_persist": G_PERSIST, "hetero_2seed": e2, "hetero_1seed": e1,
                         "summary": s}
        print(f"  SUMMARY: stable={s['stable']} coexist={s['coexist']} h7={s['h7']} "
              f"fill={s['mean_fill_pct']:.1f}% cf={s['mean_coexist_frac']} "
              f"lc={s['mean_late_lc']} rc={s['mean_late_rc']} mode={s['degradation_mode']} "
              f"L/r={s['L_over_r']} ({s['radius_pct']}% of grid) [{dt:.1f}s]", flush=True)
        with open(OUTPUT_PATH, "w") as f:
            json.dump(results, f, indent=2)
    total = time.time() - t0
    print(f"\nTotal time: {total:.1f}s")
    print("\n=== FULL CROSSOVER TABLE ===")
    print(f"{'label':>18s} {'r':>4s} {'r%':>6s} {'grid':>5s} {'n':>5s} {'fill%':>7s} {'stable':>7s} "
          f"{'lc':>5s} {'rc':>5s} {'L/r':>5s} {'mode':>15s}")
    baselines = [
        ("r04_160", 4, 2.5, 160, 2000, 41.3, "0/4", 3.81, 5.55, 18.2, "over-splitting"),
        ("r08_160", 8, 5.0, 160, 3000, 43.6, "0/4", 5.50, 6.80, 9.3, "over-splitting"),
        ("r10_160", 10, 6.25, 160, 3000, 43.1, "0/2", 4.60, 5.88, 7.4, "over-splitting"),
        ("r12_160", 12, 7.5, 160, 3000, 43.3, "0/2", 5.85, 6.53, 6.2, "over-splitting"),
        ("r08_80",  8, 10.0,  80,  600, 76.3, "2/4", 0.42, 0.57, None, "under-splitting"),
    ]
    for label, r, rpct, grid, n, fill, st, lc, rc, lr, mode in baselines:
        lr_str = f"{lr}" if lr else "n/a"
        print(f"{label:>18s} {r:>4} {rpct:>5.1f}% {grid:>5} {n:>5} {fill:>7.1f} {st:>7s} "
              f"{lc:>5.2f} {rc:>5.2f} {lr_str:>5s} {mode:>15s}")
    for radius, n_t, lbl in COMBOS:
        s = results[lbl]["summary"]
        print(f"{lbl:>18s} {radius:>4} {s['radius_pct']:>5.1f}% {GRID:>5} {n_t:>5} "
              f"{s['mean_fill_pct']:>7.1f} {s['stable']:>7s} {s['mean_late_lc']:>5.2f} "
              f"{s['mean_late_rc']:>5.2f} {s['L_over_r']:>5.1f} {s['degradation_mode']:>15s}")

if __name__ == "__main__":
    main()
