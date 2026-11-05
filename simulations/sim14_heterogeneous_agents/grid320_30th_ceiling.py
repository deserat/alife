"""
320×320 30th ceiling sweep — does the 30th stability ceiling shift with grid size?

Queued-topic #259 (from Session 101 "What's next"):
The 30th ceiling on 160×160 is ~43.6% fill (n≈3000, stable 0/4 at all gains).
On 80×80, stability persists at 64–76% fill (Session 95) — the ceiling is NOT
a universal fill fraction.
On 320×320, the boundary's dilation radius (8) is only 2.5% of the grid (vs 5%
on 160×160). The absolute-spatial-scale principle predicts the ceiling should
be at a DIFFERENT fill% — but the 50th mechanism says the fill depends on
absolute n, so the ceiling in terms of n is at a HIGHER n on 320×320.

This sweep tests n=6000, 8000, 10000 on 320×320 (fill ~35-50% estimated)
to find where stability collapses and compare the ceiling fill% to 160×160.

Config: 320×320, dual mode g=0.001, focal bias=0.3, per_step jitter=10.
"""

import os
import sys
import json
import time

import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14  # noqa: E402

OUTPUT_DIR = os.path.join(SIM14_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

GRID = 320
JITTER = 10.0
STEPS = 2000
SAMPLE = 10

SEEDS = [42, 999, 123, 256]

N_VALUES = [6000, 8000, 10000]
G_BOUNDARY = 0.001


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
        "n": n,
        "seed": seed,
        "n_seeds": n_seeds,
        "g_form": g_form,
        "g_persist": g_persist,
        "no_inhib": no_inhib,
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
    results = {
        "config": {
            "grid": GRID,
            "steps": STEPS,
            "sample_every": SAMPLE,
            "jitter": JITTER,
            "g_boundary": G_BOUNDARY,
            "seeds": SEEDS,
            "n_values": N_VALUES,
        },
        "runs_2seed": [],
        "runs_1seed": [],
        "runs_no_inhib": [],
        "summary": [],
    }

    # Main 2-seed runs
    for n in N_VALUES:
        stable_count = 0
        coexist_count = 0
        h7_count = 0
        for sd in SEEDS:
            r = run_one(n, sd, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
            results["runs_2seed"].append(r)
            if r["l2_stable"]:
                stable_count += 1
            if r["l2_outcome"] == "coexist":
                coexist_count += 1
            if r["crossed_h7"]:
                h7_count += 1
            print(f"  320 n={n} 2s s={sd}: fill={r['fill_pct']:.1f}% "
                  f"stable={r['l2_stable']} out={r['l2_outcome']:>12s} "
                  f"h7={r['crossed_h7']} cf={r['l2_coexist_frac']:.2f} "
                  f"lc={r['late_mean_lc']} rc={r['late_mean_rc']} "
                  f"({r['elapsed_s']:.0f}s)")

        # 1-seed control (use last seed from the 2-seed loop)
        r1 = run_one(n, SEEDS[-1], G_BOUNDARY, G_BOUNDARY, n_seeds=1)
        results["runs_1seed"].append(r1)
        print(f"  320 n={n} 1s s={sd}: fill={r1['fill_pct']:.1f}% "
              f"l2={r1['l2_crossed']} out={r1['l2_outcome']:>12s} "
              f"({r1['elapsed_s']:.0f}s)")

        # No-inhibition control (2 seeds for speed)
        for sd in [SEEDS[0], SEEDS[1]]:
            r0 = run_one(n, sd, 0.0, 0.0, n_seeds=2, no_inhib=True)
            results["runs_no_inhib"].append(r0)
            print(f"  320 n={n} no-inhib s={sd}: fill={r0['fill_pct']:.1f}% "
                  f"({r0['elapsed_s']:.0f}s)")

        n_stable_1s = sum(1 for r in results["runs_1seed"]
                          if r["n"] == n and r["l2_crossed"])
        results["summary"].append({
            "n": n,
            "stable_4": f"{stable_count}/4",
            "coexist_4": f"{coexist_count}/4",
            "h7_4": f"{h7_count}/4",
            "l2_1s": r1["l2_crossed"],
            "fill_pct_mean": round(
                np.mean([r["fill_pct"] for r in results["runs_2seed"]
                         if r["n"] == n]), 2),
        })
        print(f"  → n={n}: stable={stable_count}/4 coexist={coexist_count}/4 "
              f"h7={h7_count}/4 fill={results['summary'][-1]['fill_pct_mean']:.1f}%\n")

    # Determinism check
    det1 = run_one(8000, 42, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
    det2 = run_one(8000, 42, G_BOUNDARY, G_BOUNDARY, n_seeds=2)
    det_match = abs(det1["cells"] - det2["cells"]) < 0.01
    results["determinism"] = {
        "n": 8000, "seed": 42, "match": det_match,
        "cells_1": det1["cells"], "cells_2": det2["cells"],
    }
    print(f"\nDeterminism: {'PASS' if det_match else 'FAIL'}")

    out_path = os.path.join(OUTPUT_DIR, "grid320_30th_ceiling.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWrote {out_path}")

    print("\n=== 320×320 30th Ceiling Summary ===")
    print(f"{'n':>6} {'fill%':>7} {'stable':>8} {'coexist':>9} {'h7':>5} {'l2_1s':>6}")
    for s in results["summary"]:
        print(f"{s['n']:6d} {s['fill_pct_mean']:7.1f} "
              f"{s['stable_4']:>8s} {s['coexist_4']:>9s} "
              f"{s['h7_4']:>5s} {str(s['l2_1s']):>6s}")


if __name__ == "__main__":
    main()
