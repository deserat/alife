"""
Session 105: r=4 on 320×320 (1.25% of grid) — does the 30th ceiling disappear?

Queued-topic #266: The two-component formula predicts ceiling = 185.82×(r/grid) +
3822.55×(1/grid) + 10.34. At r=4 on 320×320: ceiling ≈ 24.6%.
At r=2 on 320×320: ceiling ≈ 23.4% (approaching the 1/grid floor ~22.3%).

The key tension: the H7 crossing threshold is ~4/kc ≈ n~4096 on 320×320
(fill ~32%). If the ceiling is truly ~24.6%, there is NO n where both H7
fires AND fill is below the ceiling — the boundary is too weak for stable
composition at any density where the crossing fires.

The formula was fit to 5 data points at r/grid ≥ 2.5%. Extrapolating to
r/grid = 1.25% may not hold. This sweep tests the extrapolation directly.

Uses separable max filter (O(2r), verified identical in S97).
Config: 320×320, dual mode g=0.001, focal bias=0.3, per_step jitter=10.
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

GRID = 320
RADIUS = 4
JITTER = 10.0
STEPS = 2000
SAMPLE = 10
G_BOUNDARY = 0.001

SEEDS = [42, 999, 123, 256]

# n values to bracket the predicted ceiling (~24.6%)
# Fill scales ~linearly with n on 320×320 (no-inhibition, since boundary gap <1%):
#   n=2000 → fill ~16%, n=3000 → fill ~24%, n=4000 → fill ~32%, n=5000 → fill ~40%
# Predicted ceiling ~24.6%: n=2000 below, n=3000 at ceiling, n=4000 above.
# H7 threshold ~4/kc ≈ n~4096 on 320×320: n=2000-3000 may not fire H7.
# If 0/4 stable at ALL n, the ceiling dropped below the H7 threshold.
N_VALUES = [2000, 3000, 4000, 5000]

OUTPUT_DIR = os.path.join(SIM14_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "r4_320_ceiling.json")


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
    results = {
        "config": {
            "grid": GRID, "radius": RADIUS,
            "r_grid_pct": round(100.0 * RADIUS / GRID, 4),
            "steps": STEPS, "sample_every": SAMPLE,
            "jitter": JITTER, "g_boundary": G_BOUNDARY,
            "seeds": SEEDS, "n_values": N_VALUES,
            "predicted_ceiling_pct": round(
                185.82 * (RADIUS / GRID) + 3822.55 * (1.0 / GRID) + 10.34, 2),
            "note": "Session 105: r=4 on 320×320 (1.25% of grid) — does the 30th ceiling disappear? (#266)",
        },
        "baselines": {
            "r8_320_2.5pct": {
                "n6000": "fill=39.67%, stable=0/4",
                "n8000": "fill=48.78%, stable=0/4",
                "n10000": "fill=58.47%, stable=0/4",
                "ceiling": "below 25%",
            },
            "r16_320_5pct": {
                "n4000": "fill=32.65%, stable=0/4",
                "n6000": "fill=40.18%, stable=0/4",
                "n8000": "fill=49.01%, stable=0/4",
                "ceiling": "below 32.7%",
            },
            "r8_160_5pct": {
                "n2500": "fill=42.08%, stable=2/4 (last stable)",
                "n3000": "fill=43.63%, stable=0/4 (ceiling)",
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
            print(f"  320 r4 n={n} 2s s={sd}: fill={r['fill_pct']:.1f}% "
                  f"stable={r['l2_stable']} out={r['l2_outcome']:>12s} "
                  f"h7={r['crossed_h7']} cf={r['l2_coexist_frac']:.2f} "
                  f"lc={r['late_mean_lc']} rc={r['late_mean_rc']} "
                  f"bmax={r['b_max']:.1f} ({r['elapsed_s']:.0f}s)", flush=True)

        # 1-seed control
        r1 = run_one(n, SEEDS[-1], G_BOUNDARY, G_BOUNDARY, n_seeds=1)
        results["runs_1seed"].append(r1)
        print(f"  320 r4 n={n} 1s: fill={r1['fill_pct']:.1f}% "
              f"l2={r1['l2_crossed']} out={r1['l2_outcome']:>12s} "
              f"({r1['elapsed_s']:.0f}s)", flush=True)

        # No-inhibition control (2 seeds)
        for sd in [SEEDS[0], SEEDS[1]]:
            r0 = run_one(n, sd, 0.0, 0.0, n_seeds=2, no_inhib=True)
            results["runs_no_inhib"].append(r0)
            print(f"  320 r4 n={n} no-inhib s={sd}: fill={r0['fill_pct']:.1f}% "
                  f"({r0['elapsed_s']:.0f}s)", flush=True)

        fill_mean = float(np.mean([r["fill_pct"] for r in results["runs_2seed"]
                                   if r["n"] == n]))
        no_inhib_fill = float(np.mean([r["fill_pct"] for r in results["runs_no_inhib"]
                                       if r["n"] == n]))
        boundary_gap = round(no_inhib_fill - fill_mean, 2)
        results["summary"].append({
            "n": n,
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
    det1 = run_one(4000, 42, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
    det2 = run_one(4000, 42, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
    det_match = abs(det1["cells"] - det2["cells"]) < 0.01
    results["determinism"] = {
        "n": 4000, "seed": 42, "match": det_match,
        "cells_1": det1["cells"], "cells_2": det2["cells"],
    }
    print(f"Determinism: {'PASS' if det_match else 'FAIL'} "
          f"({det1['cells']} vs {det2['cells']})", flush=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {OUTPUT_PATH}")

    total = time.time() - t0_all
    print(f"\nTotal time: {total:.1f}s ({total/60:.1f}m)")
    pred = results["config"]["predicted_ceiling_pct"]
    print(f"\n=== r=4 320×320 30th Ceiling Summary ===")
    print(f"Predicted ceiling: {pred}%")
    print(f"{'n':>6} {'fill%':>7} {'stable':>8} {'coexist':>9} {'h7':>5} "
          f"{'l2_1s':>6} {'no_inh':>7} {'gap':>5}")
    for s in results["summary"]:
        print(f"{s['n']:6d} {s['fill_pct_mean']:7.1f} "
              f"{s['stable_4']:>8s} {s['coexist_4']:>9s} "
              f"{s['h7_4']:>5s} {str(s['l2_1s']):>6s} "
              f"{s['no_inhib_fill_pct_mean']:7.1f} {s['boundary_gap']:5.1f}")
    print(f"\nKey: if 0/4 stable at ALL n, the ceiling dropped below the")
    print(f"     H7 density threshold (~4/kc) — the boundary is too weak")
    print(f"     for stable composition at any density where H7 fires.")


if __name__ == "__main__":
    main()
