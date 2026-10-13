"""
Density-dependent gain on 320×320 — queued-topic #226.

Session 81 found the 53rd mechanism: the boundary converts density-
dependence into n-dependence by acting on the intensive co-presence
signal. On 320×320 at n=1200 (11.7/kc), fill=15.82% vs 160×160 at n=300
(11.7/kc), fill=43.49% — the boundary is weaker on the larger grid
because the co-presence signal is sparser (4× the area, same n).

Can a higher gain compensate? If the co-presence signal is 4× sparser on
320×320, then 4× gain (g=0.04) should restore the boundary's suppression
to the 160×160 level (fill ≈ 43.49%). If fill_320(n=1200, g=0.04) < 43.49%,
the sparsity is NOT gain-compensable — the boundary's weakness is a
structural property of the signal's spatial arrangement, not a gain-
tuning problem.

Prediction (gain-compensable): fill_320(1200, 0.04) ≈ 43.49%
  → the co-presence signal's sparsity is linearly gain-compensable
Null (not gain-compensable): fill_320(1600, 0.04) << 43.49%
  → the boundary's suppression depends on signal density, not gain

160×160 reference (from fill_cap_form_fit.json, Session 74):
  n=300, g=0.01 → 43.49% fill (density 11.7/kc)
  n=300, g=0.02 → ~41% fill (from grid_fill_cap_scaling.py)
  n=300, g=0.03 → ~38% fill (approximate)

320×320 Session 81 baseline:
  n=1200, g=0.01 → 15.82% fill (density 11.7/kc)

Test: 320×320 at n=1200 × g=[0.01, 0.02, 0.04, 0.08, 0.12] × 4 seeds
× {2, 1} + 160×160 at n=300 × g=[0.01, 0.04] × 4 seeds × {2, 1}
(direct comparison at matched density).
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "gain_compensation_320.json")

JITTER = 10.0
SEEDS = [42, 123, 256, 999]

# 160×160 reference at n=300 (11.7/kc density)
FILL_CAP_160_REF = {
    300: 43.49,  # g=0.01, from fill_cap_form_fit.json
}

# 320×320 gain sweep at n=1200 (11.7/kc density)
# Test: can higher gain compensate for the sparser co-presence signal?
GAIN_320_COMBOS = [
    (1200, 0.01, 0.01, "g010"),
    (1200, 0.02, 0.02, "g020"),
    (1200, 0.04, 0.04, "g040"),
    (1200, 0.08, 0.08, "g080"),
    (1200, 0.12, 0.12, "g120"),
]

# 160×160 direct comparison at n=300 (same density, optimal + 4× gain)
GAIN_160_COMBOS = [
    (300, 0.01, 0.01, "160_g010"),
    (300, 0.04, 0.04, "160_g040"),
]


def make_params(grid_size, n_termites, g_form, g_persist):
    """Build params for the sweep."""
    p = I14.curvature_params(0.5)
    p["grid_size"] = grid_size
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


def run_combo(grid_size, n_termites, g_form, g_persist, label, seeds):
    """Run a single combo across seeds (2-seed + 1-seed)."""
    p = make_params(grid_size, n_termites, g_form, g_persist)
    entries_2 = []
    entries_1 = []
    grid_area = grid_size * grid_size

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
            "fill_pct": round(s2["final_n_structure_cells"] / grid_area * 100, 2),
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
            "fill_pct": round(s1["final_n_structure_cells"] / grid_area * 100, 2),
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
        "note": "Session 82: gain compensation on 320×320 (#226)",
        "jitter": JITTER,
        "seeds": SEEDS,
        "fill_cap_160_ref": FILL_CAP_160_REF,
        "prediction_gain_compensable": "fill_320(1200, 0.04) ≈ 43.49%",
        "prediction_not_compensable": "fill_320(1200, 0.04) << 43.49%",
        "percolation_threshold_moore": 0.407,
    }}

    # 320×320 gain sweep
    print(f"\n{'='*80}")
    print(f"  GAIN COMPENSATION: 320×320 at n=1200 × g=[0.01–0.12] × 4 seeds × {{2,1}}")
    print(f"  160×160 ref: n=300 g=0.01 → 43.49% fill")
    print(f"  320×320 Session 81: n=1200 g=0.01 → 15.82% fill")
    print(f"  Question: does g=0.04 restore fill to ~43.49%?")
    print(f"{'='*80}")

    for n, gf, gp, label in GAIN_320_COMBOS:
        grid = 320
        density = n / (grid * grid) * 1000
        print(f"\n  320_{label} (n={n}, g={gf}, dens={density:.1f}/kc)")
        e2, e1 = run_combo(grid, n, gf, gp, label, SEEDS)
        s = summarize(e2, e1)
        results[f"320_{label}"] = {
            "grid": 320, "n_termites": n, "g_form": gf, "g_persist": gp,
            "density_per_kcell": round(density, 2),
            "hetero_2seed": e2, "hetero_1seed": e1,
            "summary": s,
        }
        print(f"  → fill={s['mean_fill_pct']:.2f}% cells={s['mean_cells']} "
              f"l2={s['l2']} coexist={s['coexist']} h7={s['h7']} cf={s['mean_coexist_frac']}")

    # 160×160 direct comparison
    print(f"\n{'='*80}")
    print(f"  160×160 DIRECT COMPARISON: n=300 × g=[0.01, 0.04]")
    print(f"{'='*80}")

    for n, gf, gp, label in GAIN_160_COMBOS:
        grid = 160
        density = n / (grid * grid) * 1000
        print(f"\n  {label} (n={n}, g={gf}, dens={density:.1f}/kc)")
        e2, e1 = run_combo(grid, n, gf, gp, label, SEEDS)
        s = summarize(e2, e1)
        results[label] = {
            "grid": 160, "n_termites": n, "g_form": gf, "g_persist": gp,
            "density_per_kcell": round(density, 2),
            "hetero_2seed": e2, "hetero_1seed": e1,
            "summary": s,
        }
        print(f"  → fill={s['mean_fill_pct']:.2f}% cells={s['mean_cells']} "
              f"l2={s['l2']} coexist={s['coexist']} h7={s['h7']} cf={s['mean_coexist_frac']}")

    # Summary comparison
    print(f"\n{'='*100}")
    print("  GAIN COMPENSATION COMPARISON")
    print(f"{'='*100}")
    print(f"{'grid':>5s} {'n':>5s} {'g':>6s} {'dens':>7s} | "
          f"{'fill%':>7s} {'cells':>7s} {'l2':>5s} {'coex':>5s} {'h7':>5s} {'cf':>5s}")
    print("-" * 100)

    # 160×160 reference
    s160 = results["160_g010"]["summary"]
    print(f"{'160':>5s} {'300':>5s} {'0.01':>6s} {'11.7':>7s} | "
          f"{s160['mean_fill_pct']:>6.2f}% {s160['mean_cells']:>7d} "
          f"{s160['l2']:>5s} {s160['coexist']:>5s} {s160['h7']:>5s} "
          f"{s160['mean_coexist_frac']:>5.2f}")

    s160g4 = results["160_g040"]["summary"]
    print(f"{'160':>5s} {'300':>5s} {'0.04':>6s} {'11.7':>7s} | "
          f"{s160g4['mean_fill_pct']:>6.2f}% {s160g4['mean_cells']:>7d} "
          f"{s160g4['l2']:>5s} {s160g4['coexist']:>5s} {s160g4['h7']:>5s} "
          f"{s160g4['mean_coexist_frac']:>5.2f}")

    for n, gf, gp, label in GAIN_320_COMBOS:
        key = f"320_{label}"
        s = results[key]["summary"]
        density = n / (320 * 320) * 1000
        print(f"{'320':>5s} {'1200':>5s} {gf:>6.2f} {density:>6.1f} | "
              f"{s['mean_fill_pct']:>6.2f}% {s['mean_cells']:>7d} "
              f"{s['l2']:>5s} {s['coexist']:>5s} {s['h7']:>5s} "
              f"{s['mean_coexist_frac']:>5.2f}")

    # Verdict
    fill_320_g04 = results["320_g040"]["summary"]["mean_fill_pct"]
    fill_160_g01 = s160["mean_fill_pct"]
    print(f"\n  VERDICT:")
    print(f"  160×160 g=0.01 fill = {fill_160_g01:.2f}%")
    print(f"  320×320 g=0.04  fill = {fill_320_g04:.2f}%")
    if abs(fill_320_g04 - fill_160_g01) < 5.0:
        print(f"  → GAIN-COMPENSABLE (within 5%): the co-presence signal's sparsity is linearly gain-compensable")
    elif fill_320_g04 < fill_160_g01:
        print(f"  → NOT GAIN-COMPENSABLE (gap {fill_160_g01 - fill_320_g04:.1f}%): the boundary's weakness is structural, not gain-tunable")
    else:
        print(f"  → OVER-COMPENSATED (320 fills more): gain overshoots")

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
