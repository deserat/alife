"""
Grid-size scaling of the fill cap — queued-topic #221.

The 19-point fill cap trajectory (n=550–15000, Sessions 66–77) was all on
160×160. The surface-to-volume constraint predicts fill% should depend on
n/grid² (density per cell), not n. If true, 80×80 at n_80 = n_160/4 should
give the same fill% as 160×160 at n_160 (same density).

The existing grid_size_sweep.json already showed n=150 on 80×80 gives ~31%
fill, matching n=600 on 160×160 (~31.23%) — both at 23.4/kc — but at
g=0.3, not the fill cap's optimal gain. This sweep tests at appropriate
gains and with proper controls.

Test: n_80 = [75, 150, 200, 250] matching n_160 = [300, 600, 800, 1000]
at g = [0.01, 0.02, 0.03] × 4 seeds × {2, 1}.

160×160 fill cap data (from fill_cap_form_fit.json):
  n=300  → 43.49% fill
  n=600  → 31.23% fill
  n=800  → 34.50% fill
  n=1000 → 36.52% fill

Prediction (surface-to-volume): fill_80(n_80) ≈ fill_160(4×n_80).
Null: fill_80(n_80) ≠ fill_160(4×n_80) — the fill depends on n, not density.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "grid_fill_cap_scaling.json")

GRID_80 = 80
JITTER = 10.0  # same as 160×160 sweeps (12.5% of 80 = same as 25% of 160)

SEEDS = [42, 123, 256, 999]

# 160×160 fill cap reference data (from fill_cap_form_fit.json)
FILL_CAP_160 = {
    300: 43.49,
    600: 31.23,
    800: 34.50,
    1000: 36.52,
}

# 80×80 test combos: (n_80, g_form, g_persist, label)
# Matched to 160×160 densities: n_80 = n_160 / 4
# Gains: test a range around the expected optimal
# (the 1/√n scaling in terms of density would give the same g* as 160
#  at the same density; in terms of n it would give 2× g*)
PLATEAU_COMBOS = [
    (75,  0.01, 0.01, "n75_g010"),
    (75,  0.02, 0.02, "n75_g020"),
    (150, 0.01, 0.01, "n150_g010"),
    (150, 0.02, 0.02, "n150_g020"),
    (200, 0.01, 0.01, "n200_g010"),
    (200, 0.02, 0.02, "n200_g020"),
    (250, 0.01, 0.01, "n250_g010"),
    (250, 0.02, 0.02, "n250_g020"),
]

# No-inhibition controls at each density
NO_INHIB_COMBOS = [
    (75,  "n75_g000"),
    (150, "n150_g000"),
]


def make_params(n_termites, g_form, g_persist):
    """Build params for the 80×80 sweep."""
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID_80
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
    p["grid_size"] = GRID_80
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
            "fill_pct": round(s2["final_n_structure_cells"] / (GRID_80 * GRID_80) * 100, 2),
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
            "fill_pct": round(s1["final_n_structure_cells"] / (GRID_80 * GRID_80) * 100, 2),
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
        "grid_80": GRID_80,
        "jitter": JITTER,
        "note": "Session 80: grid-size scaling of fill cap (#221)",
        "surface_to_volume_prediction": "fill_80(n_80) ≈ fill_160(4×n_80)",
        "fill_cap_160_reference": FILL_CAP_160,
        "percolation_threshold_moore": 0.407,
    }}

    print(f"\n{'='*80}")
    print(f"  GRID FILL CAP SCALING: 80×80 at n=75-250 × g=0.01-0.03 × 4 seeds")
    print(f"  160×160 reference: n=300→43.49%, n=600→31.23%, "
          f"n=800→34.50%, n=1000→36.52%")
    print(f"{'='*80}")

    for n, gf, gp, label in PLATEAU_COMBOS:
        density = n / (GRID_80 * GRID_80) * 1000
        n_160_equiv = n * 4
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
              f"l2={s['l2']} coexist={s['coexist']} h7={s['h7']} "
              f"cf={s['mean_coexist_frac']}")

    # No-inhibition controls
    print(f"\n{'='*80}")
    print(f"  NO-INHIBITION CONTROLS")
    print(f"{'='*80}")
    for n, label in NO_INHIB_COMBOS:
        density = n / (GRID_80 * GRID_80) * 1000
        print(f"\n  {label} (n={n}, dens={density:.1f}/kc)")
        e2, e1 = run_combo(n, 0.0, 0.0, label, SEEDS, no_inhib=True)
        s = summarize(e2, e1)
        results[label] = {
            "n_termites": n, "no_inhib": True,
            "density_per_kcell": round(density, 2),
            "hetero_2seed": e2, "hetero_1seed": e1,
            "summary": s,
        }
        print(f"  → fill={s['mean_fill_pct']:.2f}% l2={s['l2']} h7={s['h7']}")

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary comparison table
    print(f"\n{'='*100}")
    print("  FILL CAP SCALING COMPARISON (80×80 vs 160×160 at matched density)")
    print(f"{'='*100}")
    print(f"{'n_80':>5s} {'n_160':>6s} {'dens':>7s} {'g':>5s} | "
          f"{'fill_80':>8s} {'fill_160':>8s} {'diff':>6s} | "
          f"{'l2':>5s} {'coex':>5s} {'h7':>5s} {'cf':>5s}")
    print("-" * 100)

    for n_160, fill_160 in sorted(FILL_CAP_160.items()):
        n_80 = n_160 // 4
        for g in [0.01, 0.02]:
            label = f"n{n_80}_g{g*100:.0f}".replace("_g0", "_g")
            label = f"n{n_80}_g{int(g*1000):03d}"
            # Find the right label format
            for n, gf, gp, lbl in PLATEAU_COMBOS:
                if n == n_80 and abs(gf - g) < 1e-9:
                    label = lbl
                    break
            if label in results:
                s = results[label]["summary"]
                diff = s["mean_fill_pct"] - fill_160
                density = n_80 / (GRID_80 * GRID_80) * 1000
                print(f"{n_80:>5d} {n_160:>6d} {density:>6.1f} {g:>5.3f} | "
                      f"{s['mean_fill_pct']:>7.2f}% {fill_160:>7.2f}% "
                      f"{diff:>+5.2f}% | "
                      f"{s['l2']:>5s} {s['coexist']:>5s} {s['h7']:>5s} "
                      f"{s['mean_coexist_frac']:>5.2f}")

    # No-inhibition
    print(f"\n  NO-INHIBITION (80×80):")
    for n, label in NO_INHIB_COMBOS:
        s = results[label]["summary"]
        density = n / (GRID_80 * GRID_80) * 1000
        print(f"  n={n:>4d} dens={density:.1f}: fill={s['mean_fill_pct']:.2f}% "
              f"l2={s['l2']} h7={s['h7']}")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
