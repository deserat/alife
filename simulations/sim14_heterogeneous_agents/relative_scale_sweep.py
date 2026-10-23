"""
Relative-Scale Sweep — testing the absolute-spatial-scale principle's
central prediction (#234, #232, #233).

THE PRINCIPLE (Session 85–86):
  Any mechanism acting through an absolute spatial scale converts
  density-dependence into n-dependence. The focal bias (1-cell step)
  and the co-presence dilation (8-cell radius) are both absolute
  spatial scales. On a larger grid at matched density, each covers a
  smaller fraction of the grid, making the mechanism less effective.

THE PREDICTION:
  If ALL spatial scales are made relative (step ∝ size, radius ∝ size),
  the system becomes scale-invariant — the fill at matched density
  should be the SAME across grid sizes. With absolute scales, the fill
  is n-dependent (lower on larger grids).

THE TEST:
  2 conditions × 2 grid sizes × 4 seeds at 23.4/kc:
  - absolute: 80×80 (step=1, radius=8), 160×160 (step=1, radius=8)
  - relative: 80×80 (step=1, radius=8), 160×160 (step=2, radius=16)

  80×80 is the SAME for both conditions (80*0.1=8, 80/80=1). Only the
  160×160 differs. Prediction:
    spread_absolute = |fill_80 - fill_160_abs| ≈ 16-23% (n-dependent)
    spread_relative = |fill_80 - fill_160_rel| ≈ 0% (density-dependent)

  Also measures b_scale (95th percentile of initial co-presence) to
  answer queued-topic #232: is b_scale the same at matched density
  when the dilation radius is relative?

METHODOLOGY (per CLAUDE.md §4 step 6):
  - Control arm: the 80×80 condition is identical for both conditions
    (same parameters) — it's the reference that isolates the 160×160
    effect.
  - Determinism: run twice, diff the fill.
  - Compute the metric's ceiling: fill is bounded by 100% (checked).
"""

import os
import sys
import json
import time

import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14

SEEDS = [42, 123, 256, 999]
DENSITY = 23.4  # termites per kilocell
JITTER = 10
INH_GAIN = 0.3
MOVEMENT_BIAS = 0.3

# Grid sizes and corresponding n at matched density.
COMBOS = [
    (80, 150, SEEDS),    # 23.4/kc on 80×80
    (160, 600, SEEDS),   # 23.4/kc on 160×160
]

# Relative-scale fractions: radius = size * RADIUS_FRAC, step = max(1, size // STEP_DIV)
RADIUS_FRAC = 0.1   # 10% of grid → 8 on 80, 16 on 160
STEP_DIV = 80       # size // 80 → 1 on 80, 2 on 160


def make_params(grid_size, n_termites, inh_gain, direct_radius, focal_step):
    p = I14.curvature_params(inh_gain)
    p["grid_size"] = grid_size
    p["n_termites"] = n_termites
    p["movement_bias"] = MOVEMENT_BIAS
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    p["boundary_mode"] = "dual"
    p["g_form"] = 0.3
    p["g_persist"] = 0.3
    p["direct_radius"] = direct_radius
    p["focal_step"] = focal_step
    return p


def compute_b_scale(size, direct_radius):
    """Compute b_scale (95th percentile of initial co-presence) for a given
    (size, radius) combo. Uses the same initialization as run_two_region_hetero."""
    import sim09 as S
    import sim10 as T
    p = I14.curvature_params(INH_GAIN)
    p["grid_size"] = size
    p["n_termites"] = int(round(DENSITY * size * size / 1000.0))
    p["direct_radius"] = direct_radius

    field = S.Field(size)
    T.seed_region(field, size, "left", p)
    T.seed_region(field, size, "right", p)

    material_by_id = [
        field.material.copy(),
        np.zeros_like(field.material),
    ]
    mid = size // 2
    material_by_id[1][:, mid:] = field.material[:, mid:].copy()
    material_by_id[0][:, mid:] = 0.0

    cp0 = I14.compute_id_copresence(material_by_id, p)
    return {
        "b_scale": max(float(np.percentile(cp0, 95)), 1e-9),
        "cp_mean": float(np.mean(cp0)),
        "cp_max": float(np.max(cp0)),
        "cp_cov": float(np.mean(cp0 > 1e-9)),
    }


def run_one(grid, n, seeds, direct_radius, focal_step):
    p = make_params(grid, n, INH_GAIN, direct_radius, focal_step)
    grid_area = grid * grid
    entries = []
    for sd in seeds:
        r = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s = r["summary"]
        bt = r.get("boundary_trace", [])
        b_max = max((b["b_max"] for b in bt), default=0.0)
        e = {
            "seed": sd,
            "l2_crossed": s["l2_crossed"],
            "l2_outcome": s["l2_outcome"],
            "l2_stable": s["l2_stable"],
            "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
            "crossed_h7": s["crossed_h7"],
            "cells": s["final_n_structure_cells"],
            "fill_pct": round(s["final_n_structure_cells"] / grid_area * 100, 2),
            "b_max": round(b_max, 4),
            "total_material": round(s.get("final_total_material", 0.0), 2),
        }
        entries.append(e)
    return entries


def summarize(entries):
    n = len(entries)
    return {
        "l2": f"{sum(1 for e in entries if e['l2_crossed'])}/{n}",
        "coexist": f"{sum(1 for e in entries if e['l2_outcome'] == 'coexist')}/{n}",
        "stable": f"{sum(1 for e in entries if e['l2_stable'])}/{n}",
        "h7": f"{sum(1 for e in entries if e['crossed_h7'])}/{n}",
        "mean_fill_pct": round(float(np.mean([e["fill_pct"] for e in entries])), 2),
        "mean_coexist_frac": round(float(np.mean([e["l2_coexist_frac"] for e in entries])), 3),
        "mean_b_max": round(float(np.mean([e["b_max"] for e in entries])), 4),
        "mean_cells": int(np.mean([e["cells"] for e in entries])),
    }


def run_sweep():
    t0 = time.time()
    results = {
        "config": {
            "note": "Session 90: relative-scale sweep — absolute-spatial-scale principle test (#234, #232)",
            "jitter": JITTER,
            "density": DENSITY,
            "grids": [80, 160],
            "seeds": SEEDS,
            "radius_frac": RADIUS_FRAC,
            "step_div": STEP_DIV,
        },
    }

    print(f"\n{'='*80}")
    print("  RELATIVE-SCALE SWEEP — absolute-spatial-scale principle test")
    print(f"  2 conditions × 2 grids × 4 seeds | jitter={JITTER} density={DENSITY}/kc")
    print(f"{'='*80}")

    for scale_mode in ["absolute", "relative"]:
        for grid, n, seeds in COMBOS:
            if scale_mode == "relative":
                direct_radius = max(1, int(round(grid * RADIUS_FRAC)))
                focal_step = max(1, grid // STEP_DIV)
            else:
                direct_radius = 8
                focal_step = 1

            # Measure b_scale from initial co-presence.
            bs_info = compute_b_scale(grid, direct_radius)

            print(f"\n  {grid}×{grid} n={n} {scale_mode} "
                  f"(radius={direct_radius}, step={focal_step}) — "
                  f"b_scale={bs_info['b_scale']:.6f}", flush=True)
            t1 = time.time()
            entries = run_one(grid, n, seeds, direct_radius, focal_step)
            s = summarize(entries)
            dt = time.time() - t1
            print(f"    fill={s['mean_fill_pct']:.2f}% h7={s['h7']} "
                  f"coexist={s['coexist']} cf={s['mean_coexist_frac']:.3f} "
                  f"({dt:.1f}s)")

            key = f"{scale_mode}_{grid}"
            results[key] = {
                "scale_mode": scale_mode,
                "grid": grid,
                "n": n,
                "direct_radius": direct_radius,
                "focal_step": focal_step,
                "b_scale": round(bs_info["b_scale"], 6),
                "cp_mean_init": round(bs_info["cp_mean"], 6),
                "cp_max_init": round(bs_info["cp_max"], 6),
                "cp_cov_init": round(bs_info["cp_cov"], 4),
                "summary": s,
                "entries": entries,
            }

    # Determinism check.
    p_det = make_params(160, 600, INH_GAIN, 8, 1)
    r1 = I14.run_two_region_hetero(p_det, seed=42, n_seeds=2, mode="hetero")
    r2 = I14.run_two_region_hetero(p_det, seed=42, n_seeds=2, mode="hetero")
    det_ok = r1["summary"]["final_n_structure_cells"] == r2["summary"]["final_n_structure_cells"]
    results["determinism_ok"] = det_ok
    print(f"\nDeterminism: {'OK' if det_ok else 'FAIL'}")

    # Spread analysis.
    print(f"\n{'='*80}")
    print("  SPREAD ANALYSIS")
    print(f"{'='*80}")
    for scale_mode in ["absolute", "relative"]:
        fill_80 = results[f"{scale_mode}_80"]["summary"]["mean_fill_pct"]
        fill_160 = results[f"{scale_mode}_160"]["summary"]["mean_fill_pct"]
        spread = abs(fill_80 - fill_160)
        print(f"  {scale_mode:8s}: fill_80={fill_80:.2f}% fill_160={fill_160:.2f}% "
              f"spread={spread:.2f}%")

    # b_scale analysis.
    print(f"\n{'='*80}")
    print("  B_SCALE ANALYSIS (queued-topic #232)")
    print(f"{'='*80}")
    for scale_mode in ["absolute", "relative"]:
        for grid in [80, 160]:
            key = f"{scale_mode}_{grid}"
            bs = results[key]["b_scale"]
            cpm = results[key]["cp_mean_init"]
            cpx = results[key]["cp_max_init"]
            cpc = results[key]["cp_cov_init"]
            print(f"  {scale_mode:8s} {grid:4d}: b_scale={bs:.6f} "
                  f"cp_mean={cpm:.6f} cp_max={cpx:.6f} cp_cov={cpc:.4f}")

    out_path = os.path.join(SIM14_DIR, "output", "relative_scale_sweep.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nOutput: {out_path}")
    print(f"Total time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    run_sweep()
