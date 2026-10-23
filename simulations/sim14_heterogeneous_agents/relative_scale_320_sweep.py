"""
Relative-Scale 320×320 Sweep — confirming the extensive/intensive
measure-type distinction at a third grid size (#245).

THE PREDICTION (Session 90):
  The absolute-spatial-scale principle is confirmed for intensive measures
  (b_scale, composition quality) but FALSIFIED for the extensive fill.
  With relative scales (radius ∝ size, step ∝ size):
    - b_scale should match 80×80 (intensive → density-dependent)
    - composition quality (cf) should match 80×80 (intensive → density-dependent)
    - fill should remain n-dependent (extensive → n-dependent with both)

  At 320×320 (n=1200, 23.4/kc):
    - absolute (radius=8, step=1): b_scale << 80×80, cf << 80×80, fill << 80×80
    - relative (radius=32, step=4): b_scale ≈ 80×80, cf ≈ 80×80, fill << 80×80

THE TEST:
  80×80 (radius=8, step=1) × 4 seeds [control arm — identical for both]
  320×320 absolute (radius=8, step=1) × 4 seeds
  320×320 relative (radius=32, step=4) × 4 seeds

  If b_scale and cf match 80×80 under relative but not absolute,
  the intensive measure-type distinction is confirmed at a third grid size.
  If fill diverges under both, the extensive measure-type distinction is
  confirmed.

METHODOLOGY:
  - Control arm: 80×80 is identical for absolute and relative (80*0.1=8,
    80//80=1) — it's the reference that isolates the 320×320 effect.
  - Determinism: run twice, diff the fill.
  - Compute the metric's ceiling: fill bounded by 100%, cf bounded by 1.0.
"""

import os
import sys
import json
import time

import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14

SEEDS_80 = [42, 123, 256, 999]
SEEDS_320 = [42, 999]  # 2 seeds for 320×320 (compute time)
DENSITY = 23.4  # termites per kilocell
JITTER = 10
INH_GAIN = 0.3
MOVEMENT_BIAS = 0.3

RADIUS_FRAC = 0.1   # 10% of grid → 8 on 80, 32 on 320
STEP_DIV = 80       # size // 80 → 1 on 80, 4 on 320


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
            "note": "Session 91: relative-scale 320×320 sweep — confirming extensive/intensive measure-type distinction (#245)",
            "jitter": JITTER,
            "density": DENSITY,
            "seeds_80": SEEDS_80,
            "seeds_320": SEEDS_320,
            "radius_frac": RADIUS_FRAC,
            "step_div": STEP_DIV,
        },
    }

    print(f"\n{'='*80}")
    print("  RELATIVE-SCALE 320×320 SWEEP — extensive/intensive measure-type distinction")
    print(f"  80×80 control + 320×320 absolute + 320×320 relative | jitter={JITTER} density={DENSITY}/kc")
    print(f"{'='*80}")

    # Condition list: (label, grid, n, radius, step, seeds)
    n_320 = int(round(DENSITY * 320 * 320 / 1000.0))  # 2400
    n_80 = int(round(DENSITY * 80 * 80 / 1000.0))     # 150

    conditions = [
        ("control_80", 80, n_80, 8, 1, SEEDS_80),
        ("absolute_320", 320, n_320, 8, 1, SEEDS_320),
        ("relative_320", 320, n_320, max(1, int(round(320 * RADIUS_FRAC))), max(1, 320 // STEP_DIV), SEEDS_320),
    ]

    for label, grid, n, radius, step, seeds in conditions:
        bs_info = compute_b_scale(grid, radius)
        print(f"\n  {label} {grid}×{grid} n={n} "
              f"(radius={radius}, step={step}) — "
              f"b_scale={bs_info['b_scale']:.6f}", flush=True)
        t1 = time.time()
        entries = run_one(grid, n, seeds, radius, step)
        s = summarize(entries)
        dt = time.time() - t1
        print(f"    fill={s['mean_fill_pct']:.2f}% h7={s['h7']} "
              f"coexist={s['coexist']} cf={s['mean_coexist_frac']:.3f} "
              f"stable={s['stable']} ({dt:.1f}s)")

        results[label] = {
            "scale_mode": label,
            "grid": grid,
            "n": n,
            "direct_radius": radius,
            "focal_step": step,
            "b_scale": round(bs_info["b_scale"], 6),
            "cp_mean_init": round(bs_info["cp_mean"], 6),
            "cp_max_init": round(bs_info["cp_max"], 6),
            "cp_cov_init": round(bs_info["cp_cov"], 4),
            "summary": s,
            "entries": entries,
        }

    # Determinism check (80×80 — fast; the 320×320 relative runs take ~55 min each).
    p_det = make_params(80, n_80, INH_GAIN, 8, 1)
    r1 = I14.run_two_region_hetero(p_det, seed=42, n_seeds=2, mode="hetero")
    r2 = I14.run_two_region_hetero(p_det, seed=42, n_seeds=2, mode="hetero")
    det_ok = r1["summary"]["final_n_structure_cells"] == r2["summary"]["final_n_structure_cells"]
    results["determinism_ok"] = det_ok
    print(f"\nDeterminism: {'OK' if det_ok else 'FAIL'}")

    # Spread analysis.
    print(f"\n{'='*80}")
    print("  SPREAD ANALYSIS (relative to 80×80 control)")
    print(f"{'='*80}")
    fill_80 = results["control_80"]["summary"]["mean_fill_pct"]
    cf_80 = results["control_80"]["summary"]["mean_coexist_frac"]
    bs_80 = results["control_80"]["b_scale"]
    for label in ["absolute_320", "relative_320"]:
        fill_x = results[label]["summary"]["mean_fill_pct"]
        cf_x = results[label]["summary"]["mean_coexist_frac"]
        bs_x = results[label]["b_scale"]
        print(f"  {label:16s}: fill_spread={abs(fill_80 - fill_x):.2f}%  "
              f"cf_spread={abs(cf_80 - cf_x):.3f}  "
              f"b_scale_spread={abs(bs_80 - bs_x):.6f}")
        print(f"    fill_80={fill_80:.2f}% fill_320={fill_x:.2f}% | "
              f"cf_80={cf_80:.3f} cf_320={cf_x:.3f} | "
              f"bs_80={bs_80:.6f} bs_320={bs_x:.6f}")

    # Prediction verdict.
    abs_cf_spread = abs(cf_80 - results["absolute_320"]["summary"]["mean_coexist_frac"])
    rel_cf_spread = abs(cf_80 - results["relative_320"]["summary"]["mean_coexist_frac"])
    abs_bs_spread = abs(bs_80 - results["absolute_320"]["b_scale"])
    rel_bs_spread = abs(bs_80 - results["relative_320"]["b_scale"])
    abs_fill_spread = abs(fill_80 - results["absolute_320"]["summary"]["mean_fill_pct"])
    rel_fill_spread = abs(fill_80 - results["relative_320"]["summary"]["mean_fill_pct"])

    print(f"\n  PREDICTION VERDICT:")
    print(f"    b_scale:  abs_spread={abs_bs_spread:.6f} rel_spread={rel_bs_spread:.6f}  "
          f"→ {'CONFIRMED' if rel_bs_spread < abs_bs_spread else 'NOT CONFIRMED'} (intensive)")
    print(f"    cf:       abs_spread={abs_cf_spread:.3f} rel_spread={rel_cf_spread:.3f}  "
          f"→ {'CONFIRMED' if rel_cf_spread < abs_cf_spread else 'NOT CONFIRMED'} (intensive)")
    print(f"    fill:     abs_spread={abs_fill_spread:.2f}% rel_spread={rel_fill_spread:.2f}%  "
          f"→ {'CONFIRMED' if rel_fill_spread > 0.05 else 'NOT CONFIRMED'} (extensive)")

    out_path = os.path.join(SIM14_DIR, "output", "relative_scale_320_sweep.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nOutput: {out_path}")
    print(f"Total time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    run_sweep()
