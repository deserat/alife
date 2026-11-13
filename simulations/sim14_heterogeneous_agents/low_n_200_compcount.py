"""
Session 110: Is the ~5-6 critical count a topological invariant of 160×160? (#276)

Test: 200×200 at very low n (100-400) to find where comp drops to ~5-6.
At n=200, fill~9%, comp~6.8 — still above the 160×160 threshold (~6.1).
If comp ~5-6 on 200×200 gives stable > 0/4 → threshold is universal.
If comp ~5-6 on 200×200 gives stable 0/4 → threshold scales with grid size.

Reduced sweep: 5 n values × 4 seeds + 2 no_inhib + 1 1seed + 2 det = 25 runs.
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

GRID = 200
RADIUS = 8
JITTER = 10.0
STEPS = 2000
SAMPLE = 10
G = 0.001
SEEDS = [42, 999, 123, 256]
N_VALUES = [100, 150, 200, 300, 400]

OUTPUT_DIR = os.path.join(SIM14_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "low_n_200_compcount.json")


def make_params(n, g_form, g_persist):
    p = I14.curvature_params(g_form)
    p.update({
        'grid_size': GRID, 'n_termites': n,
        'steps': STEPS, 'sample_every': SAMPLE,
        'boundary_mode': 'dual', 'g_form': g_form, 'g_persist': g_persist,
        'b_decay_form': 0.01, 'b_decay_persist': 0.005,
        'b_growth_form': 0.1, 'b_growth_persist': 0.1,
        'movement_bias': 0.3, 'movement_mode': 'focal',
        'home_jitter': JITTER, 'jitter_mode': 'per_step',
        'recruit_response': 'linear', 'inh_gain': g_form,
        'direct_radius': RADIUS,
    })
    return p


def make_no_inhib_params(n):
    p = I14.curvature_params(0.0)
    p.update({
        'grid_size': GRID, 'n_termites': n,
        'steps': STEPS, 'sample_every': SAMPLE,
        'movement_bias': 0.3, 'movement_mode': 'focal',
        'home_jitter': JITTER, 'jitter_mode': 'per_step',
        'direct_radius': RADIUS,
    })
    return p


def run_one(n, seed, g_form, g_persist, n_seeds, no_inhib=False):
    if no_inhib:
        p = make_no_inhib_params(n)
    else:
        p = make_params(n, g_form, g_persist)
    t0 = time.time()
    r = I14.run_two_region_hetero(p, seed=seed, n_seeds=n_seeds, mode="hetero")
    dt = time.time() - t0
    s = r["summary"]
    fill = 100.0 * s["final_n_structure_cells"] / (GRID * GRID)
    bmax = max((b["b_max"] for b in r["boundary_trace"]), default=0.0)
    return {
        "n": n, "grid": GRID, "seed": seed, "n_seeds": n_seeds,
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
            "grid": GRID, "radius": RADIUS,
            "r_grid_pct": round(100.0 * RADIUS / GRID, 2),
            "steps": STEPS, "sample_every": SAMPLE,
            "jitter": JITTER, "g_boundary": G,
            "seeds": SEEDS, "n_values": N_VALUES,
            "note": "Session 110: is the ~5-6 critical count a topological invariant of 160x160? (#276)",
        },
        "runs_2seed": [],
        "runs_1seed": [],
        "runs_no_inhib": [],
        "summary": [],
    }

    for n in N_VALUES:
        stable_count = 0
        coexist_count = 0
        h7_count = 0
        lcs, rcs, fills = [], [], []
        print(f"\n--- 200x200 n={n} ---", flush=True)

        for sd in SEEDS:
            r = run_one(n, sd, G, G, n_seeds=2)
            results["runs_2seed"].append(r)
            lcs.append(r["late_mean_lc"])
            rcs.append(r["late_mean_rc"])
            fills.append(r["fill_pct"])
            if r["l2_stable"]: stable_count += 1
            if r["l2_outcome"] == "coexist": coexist_count += 1
            if r["crossed_h7"]: h7_count += 1
            print(f"  n={n} 2s s={sd}: fill={r['fill_pct']:.1f}% "
                  f"stable={r['l2_stable']} out={r['l2_outcome']:>12s} "
                  f"h7={r['crossed_h7']} lc={r['late_mean_lc']} rc={r['late_mean_rc']} "
                  f"bmax={r['b_max']:.1f} ({r['elapsed_s']:.0f}s)", flush=True)

        # 1-seed control (one seed)
        r1 = run_one(n, SEEDS[-1], G, G, n_seeds=1)
        results["runs_1seed"].append(r1)
        print(f"  n={n} 1s: fill={r1['fill_pct']:.1f}% "
              f"l2={r1['l2_crossed']} ({r1['elapsed_s']:.0f}s)", flush=True)

        # No-inhib control (one seed, just for gap reference)
        r0 = run_one(n, SEEDS[0], 0.0, 0.0, n_seeds=2, no_inhib=True)
        results["runs_no_inhib"].append(r0)
        no_inhib_fill = r0["fill_pct"]

        fill_mean = float(np.mean(fills))
        boundary_gap = round(no_inhib_fill - fill_mean, 2)
        mean_lc = float(np.mean(lcs))
        mean_rc = float(np.mean(rcs))
        mean_comp = round((mean_lc + mean_rc) / 2, 2)

        results["summary"].append({
            "n": n,
            "density_per_kc": round(n * 1000.0 / (GRID * GRID), 2),
            "fill_pct_mean": round(fill_mean, 2),
            "no_inhib_fill": round(no_inhib_fill, 2),
            "boundary_gap": boundary_gap,
            "stable_4": f"{stable_count}/4",
            "coexist_4": f"{coexist_count}/4",
            "h7_4": f"{h7_count}/4",
            "l2_1s": r1["l2_crossed"],
            "mean_lc": round(mean_lc, 2),
            "mean_rc": round(mean_rc, 2),
            "mean_comp": mean_comp,
        })
        print(f"  -> n={n}: fill={fill_mean:.1f}% stable={stable_count}/4 "
              f"coexist={coexist_count}/4 h7={h7_count}/4 "
              f"gap={boundary_gap:.1f}% comp={mean_comp:.1f}\n", flush=True)

    # Determinism check
    print("Determinism check (n=200 seed=42)...", flush=True)
    det1 = run_one(200, 42, G, G, n_seeds=2)
    det2 = run_one(200, 42, G, G, n_seeds=2)
    det_match = abs(det1["cells"] - det2["cells"]) < 0.01
    results["determinism"] = {
        "n": 200, "grid": 200, "seed": 42, "match": det_match,
        "cells_1": det1["cells"], "cells_2": det2["cells"],
    }
    print(f"Determinism: {'PASS' if det_match else 'FAIL'} "
          f"({det1['cells']} vs {det2['cells']})", flush=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {OUTPUT_PATH}")
    total = time.time() - t0_all
    print(f"Total: {total:.1f}s ({total/60:.1f}m)")

    print("\n=== SUMMARY ===")
    print(f"{'n':>6} {'fill%':>7} {'stable':>8} {'comp':>6} {'gap':>6}")
    for s in results["summary"]:
        print(f"{s['n']:6d} {s['fill_pct_mean']:7.1f} {s['stable_4']:>8s} "
              f"{s['mean_comp']:6.1f} {s['boundary_gap']:6.1f}")


if __name__ == "__main__":
    main()
