"""
Session 106: Where does the capping→no-capping transition occur? (#269)

Session 105 found the 30th ceiling has two regimes:
  - Capping regime (160×160 r=8, gap ~56%; 80×80 r=8, gap ~10%+):
    boundary caps fill; ceiling is the fill where growth overwhelms suppression.
  - No-capping regime (320×320 at all r, gap <1%):
    boundary fragments without capping; stability is 0/4 at all fill.

Where does the transition occur? Test 240×240 (intermediate grid) at r=8
(3.33% of grid — between 160×160 r=8 at 5% and 320×320 r=8 at 2.5%).

The two-component formula predicts ceiling = 185.82*(8/240) + 3822.55*(1/240)
  + 10.34 = 6.19 + 15.93 + 10.34 = 32.5%.

Key metrics:
  - boundary_gap = fill_no_inhib - fill_with_boundary
    (160×160: ~56%; 320×320: <1%; 240×240: ???)
  - stable composition at each fill
  - H7 crossing

If the gap is intermediate (10-40%), the transition is gradual and 240×240
is in the capping regime with a lower ceiling. If the gap is <5%, the
transition is sharp and 240×240 is already in the no-capping regime.

Uses separable max filter (O(2r), verified identical in S97).
Config: 240×240, dual mode g=0.001, focal bias=0.3, per_step jitter=10.
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

GRID = 240
RADIUS = 8
JITTER = 10.0
STEPS = 2000
SAMPLE = 10
G_BOUNDARY = 0.001

SEEDS = [42, 999, 123, 256]

# n values to bracket the predicted ceiling (~32.5%)
# On 240×240 without boundary, fill ≈ density-dependent (~66% at 23.4/kc).
# With boundary, fill should be capped lower if the boundary has capping power.
# n=1000 (4.1/kc) → fill ~20%, n=2000 (8.7/kc) → fill ~35%,
# n=3000 (13.0/kc) → fill ~50%, n=4000 (17.4/kc) → fill ~60%
# The ceiling (~32.5%) is around n=1500-2000.
N_VALUES = [1000, 2000, 3000, 4000]

OUTPUT_DIR = os.path.join(SIM14_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "capping_transition_240.json")


def make_params(n_termites, g_form, g_persist):
    p = I14.curvature_params(g_form)
    p["grid_size"] = GRID
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


def make_no_inhib_params(n_termites):
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["steps"] = STEPS
    p["sample_every"] = SAMPLE
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    p["direct_radius"] = RADIUS
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
        "n": n, "seed": seed, "n_seeds": n_seeds,
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
    r_grid_pct = round(100.0 * RADIUS / GRID, 4)
    predicted_ceiling = round(
        185.82 * (RADIUS / GRID) + 3822.55 * (1.0 / GRID) + 10.34, 2)

    results = {
        "config": {
            "grid": GRID, "radius": RADIUS,
            "r_grid_pct": r_grid_pct,
            "steps": STEPS, "sample_every": SAMPLE,
            "jitter": JITTER, "g_boundary": G_BOUNDARY,
            "seeds": SEEDS, "n_values": N_VALUES,
            "predicted_ceiling_pct": predicted_ceiling,
            "note": "Session 106: 240×240 r=8 (3.33%) — where does the capping→no-capping transition occur? (#269)",
        },
        "baselines": {
            "r8_160_5pct": {
                "n3000": "fill=43.6%, stable=0/4, gap~56%",
                "n2500": "fill=42.1%, stable=2/4 (last stable)",
                "ceiling": "~43.6%",
                "gap": "~56%",
            },
            "r8_320_2.5pct": {
                "n6000": "fill=39.7%, stable=0/4, gap<1%",
                "n8000": "fill=48.8%, stable=0/4, gap<1%",
                "ceiling": "below 25%",
                "gap": "<1%",
            },
            "r4_320_1.25pct": {
                "n2000": "fill=22.2%, stable=0/4, gap<1%",
                "ceiling": "below 22%",
                "gap": "<1%",
            },
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
        print(f"\n--- n={n} ---", flush=True)

        for sd in SEEDS:
            r = run_one(n, sd, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
            results["runs_2seed"].append(r)
            if r["l2_stable"]:
                stable_count += 1
            if r["l2_outcome"] == "coexist":
                coexist_count += 1
            if r["crossed_h7"]:
                h7_count += 1
            print(f"  240 r8 n={n} 2s s={sd}: fill={r['fill_pct']:.1f}% "
                  f"stable={r['l2_stable']} out={r['l2_outcome']:>12s} "
                  f"h7={r['crossed_h7']} cf={r['l2_coexist_frac']:.2f} "
                  f"lc={r['late_mean_lc']} rc={r['late_mean_rc']} "
                  f"bmax={r['b_max']:.1f} ({r['elapsed_s']:.0f}s)", flush=True)

        # 1-seed control
        r1 = run_one(n, SEEDS[-1], G_BOUNDARY, G_BOUNDARY, n_seeds=1)
        results["runs_1seed"].append(r1)
        print(f"  240 r8 n={n} 1s: fill={r1['fill_pct']:.1f}% "
              f"l2={r1['l2_crossed']} out={r1['l2_outcome']:>12s} "
              f"({r1['elapsed_s']:.0f}s)", flush=True)

        # No-inhibition control (2 seeds)
        for sd in [SEEDS[0], SEEDS[1]]:
            r0 = run_one(n, sd, 0.0, 0.0, n_seeds=2, no_inhib=True)
            results["runs_no_inhib"].append(r0)
            print(f"  240 r8 n={n} no-inhib s={sd}: fill={r0['fill_pct']:.1f}% "
                  f"({r0['elapsed_s']:.0f}s)", flush=True)

        fill_mean = float(np.mean([r["fill_pct"] for r in results["runs_2seed"]
                                   if r["n"] == n]))
        no_inhib_fill = float(np.mean([r["fill_pct"] for r in results["runs_no_inhib"]
                                       if r["n"] == n]))
        boundary_gap = round(no_inhib_fill - fill_mean, 2)
        results["summary"].append({
            "n": n,
            "density_per_kc": round(n * 1000.0 / (GRID * GRID), 2),
            "stable_4": f"{stable_count}/4",
            "coexist_4": f"{coexist_count}/4",
            "h7_4": f"{h7_count}/4",
            "l2_1s": r1["l2_crossed"],
            "fill_pct_mean": round(fill_mean, 2),
            "no_inhib_fill_pct_mean": round(no_inhib_fill, 2),
            "boundary_gap": boundary_gap,
        })
        print(f"  → n={n}: stable={stable_count}/4 coexist={coexist_count}/4 "
              f"h7={h7_count}/4 fill={fill_mean:.1f}% "
              f"no_inhib={no_inhib_fill:.1f}% gap={boundary_gap:.1f}%\n", flush=True)

    # Determinism check
    print("Determinism check...", flush=True)
    det1 = run_one(2000, 42, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
    det2 = run_one(2000, 42, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
    det_match = abs(det1["cells"] - det2["cells"]) < 0.01
    results["determinism"] = {
        "n": 2000, "seed": 42, "match": det_match,
        "cells_1": det1["cells"], "cells_2": det2["cells"],
    }
    print(f"Determinism: {'PASS' if det_match else 'FAIL'} "
          f"({det1['cells']} vs {det2['cells']})", flush=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {OUTPUT_PATH}")

    total = time.time() - t0_all
    print(f"\nTotal time: {total:.1f}s ({total/60:.1f}m)")
    print(f"\n=== 240×240 r=8 Capping Transition Summary ===")
    print(f"Predicted ceiling: {predicted_ceiling}%")
    print(f"{'n':>6} {'dens/kc':>8} {'fill%':>7} {'stable':>8} {'coexist':>9} "
          f"{'h7':>5} {'no_inh':>7} {'gap':>6}")
    for s in results["summary"]:
        print(f"{s['n']:6d} {s['density_per_kc']:8.1f} "
              f"{s['fill_pct_mean']:7.1f} "
              f"{s['stable_4']:>8s} {s['coexist_4']:>9s} "
              f"{s['h7_4']:>5s} "
              f"{s['no_inhib_fill_pct_mean']:7.1f} {s['boundary_gap']:6.1f}")
    print(f"\nKey: if gap > 10%, 240×240 is in the capping regime.")
    print(f"     If gap < 5%, 240×240 is in the no-capping regime.")
    print(f"     If gap is 5-10%, the transition is gradual.")


if __name__ == "__main__":
    main()
