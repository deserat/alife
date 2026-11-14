"""
Session 111: Does the r/grid capping threshold hold at other boundary gains? (#278)
             Is the ~5-6 fragmentation count universal across boundary gains? (#279)

Session 110 bracketed the capping→no-capping transition to r/grid ∈ (4%, 5%) at
g=0.001 (dual mode). 200×200 (r/grid=4%, gap <1%) is no-capping; 160×160 (r/grid=5%,
gap ~56%) is capping. Does the threshold shift with gain?

  - If 200×200 at g=0.003 has gap > 10%, higher gain rescues capping at r/grid=4%
    → the threshold is a gain-geometry interaction, not a pure geometric threshold.
  - If gap < 1% at g=0.003, the threshold is gain-independent → pure geometric.

Also: is the ~5-6 component count at the 30th ceiling universal across gains?
Session 109 measured comp ~5-6 at g=0.001 on 160×160. At g=0.003, the ceiling
is at n=2500 (Session 71: stable 0/4 at g=0.003). Measure comp there.

Uses separable max filter (O(2r), verified identical in S97/S98).
Config: 200×200 and 160×160, dual mode, focal bias=0.3, per_step jitter=10.
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

RADIUS = 8
JITTER = 10.0
STEPS = 2000
SAMPLE = 10
SEEDS = [42, 999, 123, 256]

OUTPUT_DIR = os.path.join(SIM14_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "gain_capping_threshold.json")


def make_params(grid, n_termites, g_form, g_persist):
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


def make_no_inhib_params(grid, n_termites):
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


def run_one(grid, n, seed, g, n_seeds, no_inhib=False):
    if no_inhib:
        p = make_no_inhib_params(grid, n)
    else:
        p = make_params(grid, n, g, g)
    t0 = time.time()
    r = I14.run_two_region_hetero(p, seed=seed, n_seeds=n_seeds, mode="hetero")
    dt = time.time() - t0
    s = r["summary"]
    fill = 100.0 * s["final_n_structure_cells"] / (grid * grid)
    bmax = max((b["b_max"] for b in r["boundary_trace"]), default=0.0)
    return {
        "grid": grid, "n": n, "seed": seed, "n_seeds": n_seeds,
        "g": g, "no_inhib": no_inhib,
        "l2_crossed": s["l2_crossed"],
        "l2_outcome": s["l2_outcome"],
        "l2_stable": s["l2_stable"],
        "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
        "crossed_h7": s["crossed_h7"],
        "cells": s["final_n_structure_cells"],
        "fill_pct": round(fill, 2),
        "late_mean_lc": round(s.get("l2_late_mean_lc", 0.0), 2),
        "late_mean_rc": round(s.get("l2_late_mean_rc", 0.0), 2),
        "mean_comp": round(
            (s.get("l2_late_mean_lc", 0.0) + s.get("l2_late_mean_rc", 0.0)) / 2.0, 2),
        "b_max": round(bmax, 2),
        "elapsed_s": round(dt, 1),
    }


def main():
    t0_all = time.time()

    results = {
        "config": {
            "radius": RADIUS, "steps": STEPS, "sample_every": SAMPLE,
            "jitter": JITTER, "seeds": SEEDS,
            "note": "Session 111: r/grid capping threshold at other gains (#278, #279)",
        },
        "r_grid_ref": {
            "160_5pct": "gap ~56% at g=0.001 (capping)",
            "200_4pct": "gap <1% at g=0.001 (no-capping)",
        },
        "runs_200_g003": [],
        "runs_200_g005": [],
        "runs_200_no_inhib_g003": [],
        "runs_200_no_inhib_g005": [],
        "runs_160_g003": [],
        "runs_160_no_inhib_g003": [],
        "summary": [],
    }

    # --- Part 1: 200×200 at g=0.003 and g=0.005 at n=2000 (#278) ---
    GRID_200 = 200
    N_200 = 2000

    for g_label, g_val in [("0.003", 0.003), ("0.005", 0.005)]:
        g_key = g_label.split(".")[1]  # "0.003" -> "003", "0.005" -> "005"
        print(f"\n=== 200×200 g={g_label} n={N_200} ===", flush=True)
        stable_count = 0
        coexist_count = 0
        h7_count = 0
        fills = []

        for sd in SEEDS:
            r = run_one(GRID_200, N_200, sd, g_val, n_seeds=2)
            key = f"runs_200_g{g_key}"
            results[key].append(r)
            fills.append(r["fill_pct"])
            if r["l2_stable"]:
                stable_count += 1
            if r["l2_outcome"] == "coexist":
                coexist_count += 1
            if r["crossed_h7"]:
                h7_count += 1
            print(f"  200 r8 g={g_label} n={N_200} 2s s={sd}: "
                  f"fill={r['fill_pct']:.1f}% stable={r['l2_stable']} "
                  f"out={r['l2_outcome']:>12s} h7={r['crossed_h7']} "
                  f"cf={r['l2_coexist_frac']:.2f} comp={r['mean_comp']} "
                  f"bmax={r['b_max']:.1f} ({r['elapsed_s']:.0f}s)", flush=True)

        # 1-seed control
        r1 = run_one(GRID_200, N_200, SEEDS[-1], g_val, n_seeds=1)
        results[f"runs_200_g{g_key}"].append(r1)
        print(f"  200 r8 g={g_label} n={N_200} 1s: "
              f"fill={r1['fill_pct']:.1f}% l2={r1['l2_crossed']} "
              f"({r1['elapsed_s']:.0f}s)", flush=True)

        # No-inhibition control (2 seeds)
        for sd in [SEEDS[0], SEEDS[1]]:
            r0 = run_one(GRID_200, N_200, sd, 0.0, n_seeds=2, no_inhib=True)
            key_ni = f"runs_200_no_inhib_g{g_key}"
            results[key_ni].append(r0)
            print(f"  200 r8 g={g_label} n={N_200} no-inhib s={sd}: "
                  f"fill={r0['fill_pct']:.1f}% ({r0['elapsed_s']:.0f}s)", flush=True)

        no_inhib_fill = float(np.mean([
            r["fill_pct"] for r in results[f"runs_200_no_inhib_g{g_key}"]
        ]))
        fill_mean = float(np.mean(fills))
        gap = round(no_inhib_fill - fill_mean, 2)
        results["summary"].append({
            "grid": 200, "n": N_200, "g": g_val,
            "r_grid_pct": round(100.0 * RADIUS / GRID_200, 2),
            "stable_4": f"{stable_count}/4",
            "coexist_4": f"{coexist_count}/4",
            "h7_4": f"{h7_count}/4",
            "fill_pct_mean": round(fill_mean, 2),
            "no_inhib_fill_pct_mean": round(no_inhib_fill, 2),
            "boundary_gap": gap,
            "verdict": "capping" if gap > 10 else ("no-capping" if gap < 5 else "transition"),
        })
        print(f"  → 200×200 g={g_label}: stable={stable_count}/4 gap={gap:.1f}% "
              f"({'CAPPING' if gap > 10 else 'NO-CAPPING' if gap < 5 else 'TRANSITION'})\n",
              flush=True)

    # --- Part 2: 160×160 at g=0.003 at the 30th ceiling n=2500 (#279) ---
    GRID_160 = 160
    N_160 = 2500
    G_160 = 0.003

    print(f"\n=== 160×160 g={G_160} n={N_160} (30th ceiling, comp count) ===", flush=True)
    stable_count_160 = 0
    comps_160 = []

    for sd in SEEDS:
        r = run_one(GRID_160, N_160, sd, G_160, n_seeds=2)
        results["runs_160_g003"].append(r)
        comps_160.append(r["mean_comp"])
        if r["l2_stable"]:
            stable_count_160 += 1
        print(f"  160 r8 g={G_160} n={N_160} 2s s={sd}: "
              f"fill={r['fill_pct']:.1f}% stable={r['l2_stable']} "
              f"comp={r['mean_comp']} h7={r['crossed_h7']} "
              f"({r['elapsed_s']:.0f}s)", flush=True)

    # No-inhib control for 160
    for sd in [SEEDS[0], SEEDS[1]]:
        r0 = run_one(GRID_160, N_160, sd, 0.0, n_seeds=2, no_inhib=True)
        results["runs_160_no_inhib_g003"].append(r0)
        print(f"  160 r8 g={G_160} n={N_160} no-inhib s={sd}: "
              f"fill={r0['fill_pct']:.1f}% ({r0['elapsed_s']:.0f}s)", flush=True)

    no_inhib_fill_160 = float(np.mean([
        r["fill_pct"] for r in results["runs_160_no_inhib_g003"]
    ]))
    fill_160 = float(np.mean([r["fill_pct"] for r in results["runs_160_g003"]]))
    gap_160 = round(no_inhib_fill_160 - fill_160, 2)
    comp_mean_160 = round(float(np.mean(comps_160)), 2)
    results["summary"].append({
        "grid": 160, "n": N_160, "g": G_160,
        "r_grid_pct": round(100.0 * RADIUS / GRID_160, 2),
        "stable_4": f"{stable_count_160}/4",
        "fill_pct_mean": round(fill_160, 2),
        "no_inhib_fill_pct_mean": round(no_inhib_fill_160, 2),
        "boundary_gap": gap_160,
        "comp_mean": comp_mean_160,
        "comp_ref_g001": "5.57 (r=4), 6.12 (r=8), 5.63 (r=10), 6.13 (r=12), 5.74 (r=16)",
        "verdict": f"comp={comp_mean_160} vs g=0.001 ~5-6",
    })
    print(f"\n  → 160×160 g=0.003: stable={stable_count_160}/4 gap={gap_160:.1f}% "
          f"comp={comp_mean_160}\n", flush=True)

    # Determinism check
    print("Determinism check...", flush=True)
    det1 = run_one(GRID_200, N_200, 42, 0.003, n_seeds=2)
    det2 = run_one(GRID_200, N_200, 42, 0.003, n_seeds=2)
    det_match = abs(det1["cells"] - det2["cells"]) < 0.01
    results["determinism"] = {
        "grid": 200, "n": N_200, "g": 0.003, "seed": 42,
        "match": det_match, "cells_1": det1["cells"], "cells_2": det2["cells"],
    }
    print(f"Determinism: {'PASS' if det_match else 'FAIL'} "
          f"({det1['cells']} vs {det2['cells']})", flush=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {OUTPUT_PATH}")

    total = time.time() - t0_all
    print(f"\nTotal time: {total:.1f}s ({total/60:.1f}m)")
    print(f"\n=== Gain Capping Threshold Summary ===")
    print(f"{'grid':>5} {'n':>5} {'g':>7} {'r/grid':>7} {'stable':>8} "
          f"{'gap%':>6} {'comp':>5} {'verdict'}")
    for s in results["summary"]:
        comp_str = f"{s.get('comp_mean', '-')}"
        print(f"{s['grid']:5d} {s['n']:5d} {s['g']:7.3f} {s['r_grid_pct']:7.2f} "
              f"{s['stable_4']:>8s} {s['boundary_gap']:6.1f} {comp_str:>5} "
              f"{s['verdict']}")


if __name__ == "__main__":
    main()
