"""
Grid-size scaling of the fill cap — 320×320 test (queued-topic #222).

Session 80 found the fill cap depends on absolute n, not density (the 50th
mechanism): at matched density, 80×80 fills systematically more than 160×160.
The surface-to-volume prediction (fill depends on n/grid²) was falsified.

This sweep tests a THIRD grid size (320×320) to confirm the n-dependence is
genuinely about absolute n (through the boundary's sublinear capping), not
some other grid-size scaling.

Predictions at matched density (n_320 = 4 × n_160):
  - Per-density (surface-to-volume): fill_320(n) ≈ fill_160(n/4)  [SAME fill]
  - Per-termite (50th mechanism):      fill_320(n) < fill_160(n/4)  [LOWER fill]
    because f(n) is sublinear: at higher n (larger grid), the boundary
    suppresses more (supp(n) increases), so the fill fraction is lower.

The 50th mechanism predicts the fill at matched density DECREASES with grid
size: fill_80 > fill_160 > fill_320. The per-density prediction says all three
are equal.

160×160 fill cap reference (from fill_cap_form_fit.json):
  n=300  → 43.49%    (density 11.7/kc)
  n=600  → 31.23%    (density 23.4/kc)
  n=1200 → 38.23%    (density 46.9/kc)
  n=2400 → ~41.5%    (interpolated, density 93.8/kc)

80×80 fill cap reference (from grid_fill_cap_scaling.json, Session 80):
  n=150  → 48.26%    (density 23.4/kc)
  n=250  → 60.86%    (density 39.1/kc)

Test: 320×320 at n=1200, 2400 (matching 160×160 at n=300, 600 in density)
× g=0.01 × 4 seeds × {2, 1} + no-inhibition controls.
"""

import os
import sys
import json
import time

import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14  # noqa: E402
import sim09 as S    # noqa: E402

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "grid_fill_cap_320.json")

GRID = 320
JITTER = 10.0  # same absolute jitter as all previous sweeps

SEEDS = [42, 123, 256, 999]

# 160×160 fill cap reference (from fill_cap_form_fit.json)
FILL_CAP_160 = {
    300: 43.49,
    600: 31.23,
    1200: 38.23,
    2500: 42.11,
}

# 80×80 fill cap reference (from grid_fill_cap_scaling.json, Session 80)
FILL_CAP_80 = {
    150: 48.26,
    250: 60.86,
}

# 320×320 test combos: (n_320, g_form, g_persist, label)
# n=1200 matches 160×160 at n=300 (density 11.7/kc)
# n=2400 matches 160×160 at n=600 (density 23.4/kc)
PLATEAU_COMBOS = [
    (1200, 0.01, 0.01, "n1200_g010"),
    (2400, 0.01, 0.01, "n2400_g010"),
]

# No-inhibition controls
NO_INHIB_COMBOS = [
    (1200, "n1200_g000_no_inhib"),
    (2400, "n2400_g000_no_inhib"),
]


def make_params(n_termites, g_form, g_persist):
    """Build params for the 320×320 sweep."""
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["boundary_mode"] = "dual"
    p["g_form"] = g_form
    p["g_persist"] = g_persist
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def make_no_inhib_params(n_termites):
    """Params with no boundary inhibition (g=0)."""
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_combo(n_termites, g_form, g_persist, label, seeds, no_inhib=False):
    """Run a single combo across seeds."""
    if no_inhib:
        p = make_no_inhib_params(n_termites)
    else:
        p = make_params(n_termites, g_form, g_persist)
    entries_2 = []
    entries_1 = []

    for sd in seeds:
        r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s2 = r2["summary"]
        e2 = {
            "seed": sd,
            "l2_crossed": s2["l2_crossed"],
            "l2_outcome": s2["l2_outcome"],
            "l2_stable": s2["l2_stable"],
            "l2_coexist_frac": round(s2.get("l2_coexist_frac", 0.0), 3),
            "crossed_h7": s2["crossed_h7"],
            "cells": s2["final_n_structure_cells"],
            "fill_pct": round(s2["final_n_structure_cells"] / (GRID * GRID) * 100, 2),
            "late_mean_lc": round(s2.get("l2_late_mean_lc", 0.0), 2),
            "late_mean_rc": round(s2.get("l2_late_mean_rc", 0.0), 2),
        }
        entries_2.append(e2)

        r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
        s1 = r1["summary"]
        e1 = {
            "seed": sd,
            "l2_crossed": s1["l2_crossed"],
            "l2_outcome": s1["l2_outcome"],
            "crossed_h7": s1["crossed_h7"],
            "cells": s1["final_n_structure_cells"],
            "fill_pct": round(s1["final_n_structure_cells"] / (GRID * GRID) * 100, 2),
        }
        entries_1.append(e1)

    return entries_2, entries_1


def summarize(entries_2, entries_1):
    n = len(entries_2)
    n_l2 = sum(1 for e in entries_2 if e["l2_crossed"])
    n_coexist = sum(1 for e in entries_2 if e["l2_outcome"] == "coexist")
    n_stable = sum(1 for e in entries_2 if e["l2_stable"])
    n_h7 = sum(1 for e in entries_2 if e["crossed_h7"])
    n_l2_1 = sum(1 for e in entries_1 if e["l2_crossed"])
    n_h7_1 = sum(1 for e in entries_1 if e["crossed_h7"])
    clean = sum(1 for e2, e1 in zip(entries_2, entries_1)
                if e2["l2_outcome"] == "coexist" and e1["l2_outcome"] != "coexist")
    mean_cells = int(np.mean([e["cells"] for e in entries_2]))
    mean_fill = round(float(np.mean([e["fill_pct"] for e in entries_2])), 2)
    mean_cf = round(float(np.mean([e["l2_coexist_frac"] for e in entries_2])), 3)
    return {
        "l2": f"{n_l2}/{n}", "coexist": f"{n_coexist}/{n}",
        "stable": f"{n_stable}/{n}", "h7": f"{n_h7}/{n}",
        "clean": f"{clean}/{n}", "l2_1s": f"{n_l2_1}/{n}",
        "h7_1s": f"{n_h7_1}/{n}",
        "mean_cells": mean_cells, "mean_fill_pct": mean_fill,
        "mean_coexist_frac": mean_cf,
    }


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "note": "Session 81: 320×320 grid-size scaling (#222)",
        "per_termite_prediction": "fill_320(n) < fill_160(n/4) at matched density (sublinear capping)",
        "per_density_prediction": "fill_320(n) = fill_160(n/4) at matched density (same fill)",
        "fill_cap_160_reference": FILL_CAP_160,
        "fill_cap_80_reference": FILL_CAP_80,
        "percolation_threshold_moore": 0.407,
    }}

    print(f"\n{'='*80}")
    print(f"  GRID FILL CAP 320×320: n=1200, 2400 × g=0.01 × 4 seeds × {{2,1}}")
    print(f"  160×160 ref: n=300→43.49%, n=600→31.23%, n=1200→38.23%")
    print(f"  80×80 ref:   n=150→48.26%, n=250→60.86%")
    print(f"{'='*80}")

    for n, gf, gp, label in PLATEAU_COMBOS:
        density = n / (GRID * GRID) * 1000
        n_160_equiv = n // 4
        fill_160_ref = FILL_CAP_160.get(n_160_equiv, None)
        print(f"\n  {label} (n={n}, dens={density:.1f}/kc, "
              f"equiv n_160={n_160_equiv}, fill_160={fill_160_ref}%)")
        e2, e1 = run_combo(n, gf, gp, label, SEEDS)
        s = summarize(e2, e1)
        results[label] = {
            "n_termites": n, "g_form": gf, "g_persist": gp,
            "density_per_kcell": round(density, 2),
            "n_160_equiv": n_160_equiv,
            "fill_160_ref": fill_160_ref,
            "hetero_2seed": e2, "hetero_1seed": e1,
            "summary": s,
        }
        print(f"  → fill={s['mean_fill_pct']:.2f}% (160 ref={fill_160_ref}%) "
              f"cells={s['mean_cells']} "
              f"l2={s['l2']} coexist={s['coexist']} h7={s['h7']} "
              f"cf={s['mean_coexist_frac']}")

    # No-inhibition controls
    print(f"\n{'='*80}")
    print(f"  NO-INHIBITION CONTROLS")
    print(f"{'='*80}")
    for n, label in NO_INHIB_COMBOS:
        density = n / (GRID * GRID) * 1000
        print(f"\n  {label} (n={n}, dens={density:.1f}/kc)")
        e2, e1 = run_combo(n, 0.0, 0.0, label, SEEDS, no_inhib=True)
        s = summarize(e2, e1)
        results[label] = {
            "n_termites": n, "no_inhib": True,
            "density_per_kcell": round(density, 2),
            "hetero_2seed": e2, "hetero_1seed": e1,
            "summary": s,
        }
        print(f"  → fill={s['mean_fill_pct']:.2f}% cells={s['mean_cells']} "
              f"l2={s['l2']} h7={s['h7']}")

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary comparison table
    print(f"\n{'='*100}")
    print("  FILL CAP SCALING: 80×80 vs 160×160 vs 320×320 at matched density")
    print(f"{'='*100}")
    print(f"{'density':>8s} | {'80×80':>12s} | {'160×160':>12s} | {'320×320':>12s} | {'trend':>20s}")
    print("-" * 100)

    # 23.4/kc density: 80×80 n=150, 160×160 n=600, 320×320 n=2400
    fill_80_234 = FILL_CAP_80.get(150, None)
    fill_160_234 = FILL_CAP_160.get(600, None)
    fill_320_234 = results.get("n2400_g010", {}).get("summary", {}).get("mean_fill_pct", None)
    if fill_320_234:
        trend = "decreasing ✓" if fill_80_234 > fill_160_234 > fill_320_234 else "NOT decreasing"
        print(f"{'23.4/kc':>8s} | {fill_80_234:>11.2f}% | {fill_160_234:>11.2f}% | {fill_320_234:>11.2f}% | {trend:>20s}")

    # 11.7/kc density: 80×80 n=75, 160×160 n=300, 320×320 n=1200
    fill_80_117 = 29.47  # from Session 80, n=75 g=0.01
    fill_160_117 = FILL_CAP_160.get(300, None)
    fill_320_117 = results.get("n1200_g010", {}).get("summary", {}).get("mean_fill_pct", None)
    if fill_320_117:
        trend = "decreasing ✓" if fill_80_117 > fill_160_117 > fill_320_117 else "NOT decreasing"
        print(f"{'11.7/kc':>8s} | {fill_80_117:>11.2f}% | {fill_160_117:>11.2f}% | {fill_320_117:>11.2f}% | {trend:>20s}")

    print(f"\n  Per-termite (50th mechanism): fill decreases with grid size at matched density")
    print(f"  Per-density (falsified):      fill is the same at matched density")

    # No-inhibition
    print(f"\n  NO-INHIBITION (320×320):")
    for n, label in NO_INHIB_COMBOS:
        s = results[label]["summary"]
        density = n / (GRID * GRID) * 1000
        print(f"  n={n:>5d} dens={density:.1f}: fill={s['mean_fill_pct']:.2f}% "
              f"cells={s['mean_cells']} l2={s['l2']} h7={s['h7']}")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
