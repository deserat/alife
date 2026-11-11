"""
Session 108: Is the capping→no-capping transition a percolation-like threshold? (#272)

Session 107 found 200×200 (r/grid=4%) is already in the no-capping regime: boundary gap
< 1% at all n, 0/4 stable at fill 28-36%. The 55th mechanism (extensive over-splitting)
is the cause. The question: is there a critical COMPONENT COUNT per region at which
coherent suppression breaks down?

From existing data:
  160×160 (capping) at g=0.001:
    n=2000 (fill 41%, stable 3/4): lc~3-5, rc~3-5 → ~4 components/region (capping)
    n=2500 (fill 42%, stable 2/4): lc~3-5, rc~4-6 → ~4-5 components/region (capping, barely)
    n=3000 (fill 43%, stable 0/4): lc~5-6, rc~6-8 → ~6-7 components/region (ceiling)
  200×200 (no-capping) at g=0.001:
    n=1000 (fill 28%, stable 0/4): lc~6-10, rc~8-9 → ~8 components/region (no-capping)
    n=2000 (fill 33%, stable 0/4): lc~8-12, rc~10-15 → ~11 components/region

The transition seems to occur at ~6-8 components/region. 200×200 at 28% fill already
exceeds this; 160×160 at 43% fill just reaches it.

TEST: Run 160×160 at a range of n values (1200, 1500, 1800, 2000, 2500, 3000) at g=0.001
with 4 seeds, measuring component counts. Map the component count vs fill on the capping
grid and compare to the 200×200 no-capping data.

If the critical variable is the component COUNT (~6-8 per region), the transition is
percolation-like (topological threshold). If it's the fill FRACTION, the transition
is a different mechanism.

Uses separable max filter (O(2r), verified identical in S97).
Config: 160×160, dual mode g=0.001, focal bias=0.3, per_step jitter=10.
"""
import os, sys, json, time
import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14
import sim13 as I13

# --- Separable max filter (O(2r) instead of O(r²)) ---
def _dilate_no_x_wrap_fast(arr, radius):
    """Separable max filter: O(2r) instead of O(r²). Verified identical."""
    size_y, size_x = arr.shape
    temp = arr.copy()
    for dy in range(-radius, radius + 1):
        if dy == 0:
            continue
        y_idx = (np.arange(size_y) - dy) % size_y
        temp = np.maximum(temp, arr[y_idx, :])
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

GRID_160 = 160
GRID_200 = 200
RADIUS = 8
JITTER = 10.0
STEPS = 2000
SAMPLE = 10
G_BOUNDARY = 0.001

SEEDS = [42, 999, 123, 256]

# 160×160 n values to map component count vs fill
N_160 = [1200, 1500, 1800, 2000, 2500, 3000]

OUTPUT_DIR = os.path.join(SIM14_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "component_count_threshold.json")


def make_params(n_termites, grid, g_form, g_persist):
    p = I14.curvature_params(g_form)
    p["grid_size"] = grid
    p["n_termites"] = n_termites
    p["steps"] = STEPS
    p["sample_every"] = SAMPLE
    if g_form > 0.0 or g_persist > 0.0:
        p["boundary_mode"] = "dual"
        p["g_form"] = g_form
        p["g_persist"] = g_persist
    else:
        p["boundary_mode"] = "proportional"
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    p["recruit_response"] = "linear"
    p["inh_gain"] = g_form
    p["direct_radius"] = RADIUS
    return p


def make_no_inhib_params(n_termites, grid):
    p = I14.curvature_params(0.0)
    p["grid_size"] = grid
    p["n_termites"] = n_termites
    p["steps"] = STEPS
    p["sample_every"] = SAMPLE
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    p["direct_radius"] = RADIUS
    return p


def run_one(n, grid, seed, g_form, g_persist, n_seeds, no_inhib=False):
    if no_inhib:
        p = make_no_inhib_params(n, grid)
    else:
        p = make_params(n, grid, g_form, g_persist)
    t0 = time.time()
    r = I14.run_two_region_hetero(p, seed=seed, n_seeds=n_seeds, mode="hetero")
    dt = time.time() - t0
    s = r["summary"]
    fill = 100.0 * s["final_n_structure_cells"] / (grid * grid)
    bmax = max((b["b_max"] for b in r["boundary_trace"]), default=0.0)
    return {
        "n": n, "grid": grid, "seed": seed, "n_seeds": n_seeds,
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
        "late_max_lc": round(s.get("l2_late_max_lc", 0.0), 2),
        "late_max_rc": round(s.get("l2_late_max_rc", 0.0), 2),
        "b_max": round(bmax, 2),
        "elapsed_s": round(dt, 1),
    }


def main():
    t0_all = time.time()

    results = {
        "config": {
            "grid_160": GRID_160,
            "grid_200": GRID_200,
            "radius": RADIUS,
            "r_grid_160_pct": round(100.0 * RADIUS / GRID_160, 2),
            "r_grid_200_pct": round(100.0 * RADIUS / GRID_200, 2),
            "steps": STEPS,
            "sample_every": SAMPLE,
            "jitter": JITTER,
            "g_boundary": G_BOUNDARY,
            "seeds": SEEDS,
            "n_160": N_160,
            "note": "Session 108: component count threshold — is the capping→no-capping transition percolation-like? (#272)",
        },
        "runs_160": [],
        "runs_160_no_inhib": [],
        "summary_160": [],
        "summary_200_existing": [],  # from capping_transition_200.json
    }

    # Load existing 200×200 data
    p200 = os.path.join(OUTPUT_DIR, "capping_transition_200.json")
    if os.path.exists(p200):
        d200 = json.load(open(p200))
        for r in d200.get("runs_2seed", []):
            results["summary_200_existing"].append({
                "n": r["n"],
                "fill_pct": r["fill_pct"],
                "late_mean_lc": r["late_mean_lc"],
                "late_mean_rc": r["late_mean_rc"],
                "l2_stable": r["l2_stable"],
                "l2_outcome": r["l2_outcome"],
                "l2_coexist_frac": r["l2_coexist_frac"],
            })

    # --- 160×160 sweep ---
    for n in N_160:
        stable_count = 0
        coexist_count = 0
        h7_count = 0
        lcs = []
        rcs = []
        print(f"\n--- 160×160 n={n} ---", flush=True)

        for sd in SEEDS:
            r = run_one(n, GRID_160, sd, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
            results["runs_160"].append(r)
            lcs.append(r["late_mean_lc"])
            rcs.append(r["late_mean_rc"])
            if r["l2_stable"]:
                stable_count += 1
            if r["l2_outcome"] == "coexist":
                coexist_count += 1
            if r["crossed_h7"]:
                h7_count += 1
            print(f"  160 n={n} s={sd}: fill={r['fill_pct']:.1f}% "
                  f"stable={r['l2_stable']} out={r['l2_outcome']:>12s} "
                  f"h7={r['crossed_h7']} cf={r['l2_coexist_frac']:.2f} "
                  f"lc={r['late_mean_lc']} rc={r['late_mean_rc']} "
                  f"bmax={r['b_max']:.1f} ({r['elapsed_s']:.0f}s)", flush=True)

        # No-inhibition control (2 seeds)
        no_inhib_fills = []
        for sd in [SEEDS[0], SEEDS[1]]:
            r0 = run_one(n, GRID_160, sd, 0.0, 0.0, n_seeds=2, no_inhib=True)
            results["runs_160_no_inhib"].append(r0)
            no_inhib_fills.append(r0["fill_pct"])
            print(f"  160 n={n} no-inhib s={sd}: fill={r0['fill_pct']:.1f}% "
                  f"({r0['elapsed_s']:.0f}s)", flush=True)

        fill_mean = float(np.mean([r["fill_pct"] for r in results["runs_160"]
                                   if r["n"] == n and r["grid"] == GRID_160]))
        no_inhib_fill = float(np.mean(no_inhib_fills))
        boundary_gap = round(no_inhib_fill - fill_mean, 2)

        # Component count stats
        mean_lc = float(np.mean(lcs))
        mean_rc = float(np.mean(rcs))
        mean_comp = round((mean_lc + mean_rc) / 2, 2)
        max_comp = max(max(lcs), max(rcs))
        min_comp = min(min(lcs), min(rcs))

        results["summary_160"].append({
            "n": n,
            "density_per_kc": round(n * 1000.0 / (GRID_160 * GRID_160), 2),
            "fill_pct_mean": round(fill_mean, 2),
            "no_inhib_fill_pct_mean": round(no_inhib_fill, 2),
            "boundary_gap": boundary_gap,
            "stable_4": f"{stable_count}/4",
            "coexist_4": f"{coexist_count}/4",
            "h7_4": f"{h7_count}/4",
            "mean_lc": round(mean_lc, 2),
            "mean_rc": round(mean_rc, 2),
            "mean_comp": mean_comp,
            "max_comp": round(max_comp, 2),
            "min_comp": round(min_comp, 2),
        })
        print(f"  → n={n}: fill={fill_mean:.1f}% stable={stable_count}/4 "
              f"gap={boundary_gap:.1f}% mean_comp={mean_comp:.1f} "
              f"(lc={mean_lc:.1f} rc={mean_rc:.1f})\n", flush=True)

    # --- Analysis: critical component count ---
    print("\n=== Component Count Threshold Analysis ===", flush=True)
    print(f"{'Grid':>6} {'n':>6} {'fill%':>7} {'stable':>8} {'mean_lc':>8} "
          f"{'mean_rc':>8} {'mean_comp':>10} {'gap':>6}", flush=True)
    for s in results["summary_160"]:
        print(f"{'160':>6} {s['n']:6d} {s['fill_pct_mean']:7.1f} "
              f"{s['stable_4']:>8s} {s['mean_lc']:8.1f} {s['mean_rc']:8.1f} "
              f"{s['mean_comp']:10.1f} {s['boundary_gap']:6.1f}", flush=True)
    for s in results["summary_200_existing"]:
        print(f"{'200':>6} {s['n']:6d} {s['fill_pct']:7.1f} "
              f"{'stable' if s['l2_stable'] else 'unstable':>8s} "
              f"{s['late_mean_lc']:8.1f} {s['late_mean_rc']:8.1f} "
              f"{round((s['late_mean_lc']+s['late_mean_rc'])/2,1):10.1f} "
              f"{'~0':>6s}", flush=True)

    # Determinism check
    print("\nDeterminism check...", flush=True)
    det1 = run_one(2000, GRID_160, 42, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
    det2 = run_one(2000, GRID_160, 42, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
    det_match = abs(det1["cells"] - det2["cells"]) < 0.01
    results["determinism"] = {
        "n": 2000, "grid": 160, "seed": 42, "match": det_match,
        "cells_1": det1["cells"], "cells_2": det2["cells"],
    }
    print(f"Determinism: {'PASS' if det_match else 'FAIL'} "
          f"({det1['cells']} vs {det2['cells']})", flush=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {OUTPUT_PATH}")

    total = time.time() - t0_all
    print(f"\nTotal time: {total:.1f}s ({total/60:.1f}m)")


if __name__ == "__main__":
    main()
