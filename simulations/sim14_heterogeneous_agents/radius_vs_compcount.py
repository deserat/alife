"""
Session 109: Can the critical component count (~5-6) be predicted from the dilation radius? (#273)

Focused: r=4 at n=2000 (the 30th ceiling for r=4, fill~41%) + r=10/r=12 extra seeds at n=3000.
Existing: r=8 (4 seeds, S108), r=10 (2 seeds, S97), r=12 (2 seeds, S97), r=16 (4 seeds, S98).
"""
import os, sys, json, time
import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14
import sim13 as I13

def _dilate_no_x_wrap_fast(arr, radius):
    size_y, size_x = arr.shape
    temp = arr.copy()
    for dy in range(-radius, radius + 1):
        if dy == 0: continue
        y_idx = (np.arange(size_y) - dy) % size_y
        temp = np.maximum(temp, arr[y_idx, :])
    result = temp.copy()
    for dx in range(-radius, radius + 1):
        if dx == 0: continue
        shifted = np.zeros_like(temp)
        if dx > 0: shifted[:, dx:] = temp[:, :size_x - dx]
        elif dx < 0:
            adx = abs(dx)
            shifted[:, :size_x - adx] = temp[:, adx:]
        result = np.maximum(result, shifted)
    return result

I13._dilate_no_x_wrap = _dilate_no_x_wrap_fast

GRID = 160
JITTER = 10.0
STEPS = 2000
SAMPLE = 10
G = 0.001
SEEDS = [42, 999, 123, 256]

OUTPUT_DIR = os.path.join(SIM14_DIR, "output")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "radius_vs_compcount.json")


def make_params(radius, n_termites, g_form, g_persist):
    p = I14.curvature_params(g_form)
    p.update({
        'grid_size': GRID, 'n_termites': n_termites,
        'steps': STEPS, 'sample_every': SAMPLE,
        'boundary_mode': 'dual', 'g_form': g_form, 'g_persist': g_persist,
        'b_decay_form': 0.01, 'b_decay_persist': 0.005,
        'b_growth_form': 0.1, 'b_growth_persist': 0.1,
        'movement_bias': 0.3, 'movement_mode': 'focal',
        'home_jitter': JITTER, 'jitter_mode': 'per_step',
        'recruit_response': 'linear', 'inh_gain': g_form,
        'direct_radius': radius,
    })
    return p


def make_no_inhib_params(radius, n_termites):
    p = I14.curvature_params(0.0)
    p.update({
        'grid_size': GRID, 'n_termites': n_termites,
        'steps': STEPS, 'sample_every': SAMPLE,
        'movement_bias': 0.3, 'movement_mode': 'focal',
        'home_jitter': JITTER, 'jitter_mode': 'per_step',
        'direct_radius': radius,
    })
    return p


def run_one(n, seed, g_form, g_persist, n_seeds, radius, no_inhib=False):
    if no_inhib:
        p = make_no_inhib_params(radius, n)
    else:
        p = make_params(radius, n, g_form, g_persist)
    t0 = time.time()
    r = I14.run_two_region_hetero(p, seed=seed, n_seeds=n_seeds, mode="hetero")
    dt = time.time() - t0
    s = r["summary"]
    fill = 100.0 * s["final_n_structure_cells"] / (GRID * GRID)
    bmax = max((b["b_max"] for b in r["boundary_trace"]), default=0.0)
    return {
        "n": n, "grid": GRID, "seed": seed, "n_seeds": n_seeds,
        "radius": radius,
        "g_form": g_form, "g_persist": g_persist, "no_inhib": no_inhib,
        "l2_crossed": s["l2_crossed"],
        "l2_outcome": s["l2_outcome"],
        "l2_stable": s["l2_stable"],
        "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
        "crossed_h7": s["crossed_h7"],
        "cells": s["final_n_structure_cells"],
        "fill_pct": round(fill, 2),
        "late_mean_lc": round(s.get("l2_late_mean_lc", 0.0), 2),
        "late_mean_rc": round(s.get("l2_late_mean_rc", 0.0), 2),
        "b_max": round(bmax, 2),
        "elapsed_s": round(dt, 1),
    }


def main():
    t0_all = time.time()
    results = {
        "config": {
            "grid": GRID, "steps": STEPS, "sample_every": SAMPLE,
            "jitter": JITTER, "g": G, "seeds": SEEDS,
            "note": "Session 109: can the critical component count be predicted from the dilation radius? (#273)",
        },
        "r4_n2000": [],
        "r4_no_inhib": [],
        "r10_extra": [],
        "r12_extra": [],
        "existing_data": {
            "r8_n3000": {"comp": 6.1, "stable": "0/4", "fill": 43.5, "source": "Session 108 component_count_threshold.json"},
            "r10_n3000_2seed": {"comp": 2.6, "stable": "0/2", "fill": 43.1, "source": "Session 97 crossover_sweep.json"},
            "r12_n3000_2seed": {"comp": 3.1, "stable": "0/2", "fill": 43.3, "source": "Session 97 crossover_sweep.json"},
            "r16_n3000": {"comp": 2.9, "stable": "0/4", "fill": 43.1, "source": "Session 98 r16_crossover_sweep.json"},
        },
    }

    # --- r=4 at n=2000 (the ceiling) ---
    print("\n--- r=4 n=2000 (the 30th ceiling for r=4) ---", flush=True)
    lcs, rcs, fills = [], [], []
    stable_count = 0
    for sd in SEEDS:
        r = run_one(2000, sd, G, G, n_seeds=2, radius=4)
        results["r4_n2000"].append(r)
        lcs.append(r["late_mean_lc"])
        rcs.append(r["late_mean_rc"])
        fills.append(r["fill_pct"])
        if r["l2_stable"]: stable_count += 1
        print(f"  r=4 n=2000 s={sd}: fill={r['fill_pct']:.1f}% "
              f"stable={r['l2_stable']} out={r['l2_outcome']:>12s} "
              f"h7={r['crossed_h7']} lc={r['late_mean_lc']} rc={r['late_mean_rc']} "
              f"({r['elapsed_s']:.0f}s)", flush=True)

    # No-inhib control (2 seeds)
    no_inhib_fills = []
    for sd in [SEEDS[0], SEEDS[1]]:
        r0 = run_one(2000, sd, 0.0, 0.0, n_seeds=2, radius=4, no_inhib=True)
        results["r4_no_inhib"].append(r0)
        no_inhib_fills.append(r0["fill_pct"])
        print(f"  r=4 n=2000 no-inhib s={sd}: fill={r0['fill_pct']:.1f}% "
              f"({r0['elapsed_s']:.0f}s)", flush=True)

    fill_mean = float(np.mean(fills))
    no_inhib_fill = float(np.mean(no_inhib_fills))
    boundary_gap = round(no_inhib_fill - fill_mean, 2)
    mean_comp = round((float(np.mean(lcs)) + float(np.mean(rcs))) / 2, 2)
    results["r4_n2000_summary"] = {
        "fill_pct_mean": round(fill_mean, 2),
        "no_inhib_fill_pct_mean": round(no_inhib_fill, 2),
        "boundary_gap": boundary_gap,
        "stable_4": f"{stable_count}/4",
        "mean_lc": round(float(np.mean(lcs)), 2),
        "mean_rc": round(float(np.mean(rcs)), 2),
        "mean_comp": mean_comp,
    }
    print(f"  → r=4 n=2000: fill={fill_mean:.1f}% stable={stable_count}/4 "
          f"gap={boundary_gap:.1f}% mean_comp={mean_comp:.1f}\n", flush=True)

    # --- r=10 extra seeds at n=3000 ---
    print("\n--- r=10 n=3000 extra seeds ---", flush=True)
    for sd in [123, 256]:
        r = run_one(3000, sd, G, G, n_seeds=2, radius=10)
        results["r10_extra"].append(r)
        print(f"  r=10 n=3000 s={sd}: fill={r['fill_pct']:.1f}% "
              f"stable={r['l2_stable']} lc={r['late_mean_lc']} rc={r['late_mean_rc']} "
              f"({r['elapsed_s']:.0f}s)", flush=True)

    # --- r=12 extra seeds at n=3000 ---
    print("\n--- r=12 n=3000 extra seeds ---", flush=True)
    for sd in [123, 256]:
        r = run_one(3000, sd, G, G, n_seeds=2, radius=12)
        results["r12_extra"].append(r)
        print(f"  r=12 n=3000 s={sd}: fill={r['fill_pct']:.1f}% "
              f"stable={r['l2_stable']} lc={r['late_mean_lc']} rc={r['late_mean_rc']} "
              f"({r['elapsed_s']:.0f}s)", flush=True)

    # --- Combine r=10 and r=12 at 4 seeds ---
    cx = json.load(open(os.path.join(OUTPUT_DIR, "crossover_sweep.json")))
    r10_all, r12_all = [], []
    for key in ["r10_n3000", "r12_n3000"]:
        for e in cx.get(key, {}).get("hetero_2seed", []):
            (r10_all if key == "r10_n3000" else r12_all).append(e)
    r10_all.extend(results["r10_extra"])
    r12_all.extend(results["r12_extra"])

    r10_comp = round(np.mean([e["late_mean_lc"] + e["late_mean_rc"] for e in r10_all]) / 2, 2)
    r12_comp = round(np.mean([e["late_mean_lc"] + e["late_mean_rc"] for e in r12_all]) / 2, 2)
    r10_stable = sum(1 for e in r10_all if e.get("l2_stable", e.get("stable", False)))
    r12_stable = sum(1 for e in r12_all if e.get("l2_stable", e.get("stable", False)))
    r10_fill = round(np.mean([e["fill_pct"] for e in r10_all]), 2)
    r12_fill = round(np.mean([e["fill_pct"] for e in r12_all]), 2)

    results["r10_n3000_4seed"] = {"comp": r10_comp, "stable": f"{r10_stable}/4", "fill": r10_fill}
    results["r12_n3000_4seed"] = {"comp": r12_comp, "stable": f"{r12_stable}/4", "fill": r12_fill}

    # --- Summary table ---
    print("\n=== COMPONENT COUNT AT 30TH CEILING vs RADIUS (160×160) ===", flush=True)
    print(f"{'r':>4} {'r/grid%':>7} {'n_ceiling':>9} {'fill%':>7} {'stable':>8} {'mean_comp':>10}", flush=True)
    print(f"{'4':>4} {'2.5%':>7} {'2000':>9} {fill_mean:>7.1f} {stable_count}/4 {mean_comp:>10.1f}", flush=True)
    print(f"{'8':>4} {'5.0%':>7} {'3000':>9} {'43.5':>7} {'0/4':>8s} {'6.1':>10}  (Session 108)", flush=True)
    print(f"{'10':>4} {'6.25%':>7} {'3000':>9} {r10_fill:>7.1f} {r10_stable}/4 {r10_comp:>10.1f}  (4 seeds)", flush=True)
    print(f"{'12':>4} {'7.5%':>7} {'3000':>9} {r12_fill:>7.1f} {r12_stable}/4 {r12_comp:>10.1f}  (4 seeds)", flush=True)
    print(f"{'16':>4} {'10.0%':>7} {'3000':>9} {'43.1':>7} {'0/4':>8s} {'2.9':>10}  (Session 98)", flush=True)

    print("\nPrediction: if comp INCREASES with r → connectivity of dilated footprints.")
    print("If NON-MONOTONIC or DECREASES → falsified.")

    # Determinism check
    print("\nDeterminism check (r=4 n=2000 seed=42)...", flush=True)
    det1 = run_one(2000, 42, G, G, n_seeds=2, radius=4)
    det2 = run_one(2000, 42, G, G, n_seeds=2, radius=4)
    det_match = abs(det1["cells"] - det2["cells"]) < 0.01
    results["determinism"] = {"n": 2000, "radius": 4, "seed": 42, "match": det_match,
                              "cells_1": det1["cells"], "cells_2": det2["cells"]}
    print(f"Determinism: {'PASS' if det_match else 'FAIL'} ({det1['cells']} vs {det2['cells']})", flush=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {OUTPUT_PATH}")
    total = time.time() - t0_all
    print(f"Total time: {total:.1f}s ({total/60:.1f}m)")


if __name__ == "__main__":
    main()
