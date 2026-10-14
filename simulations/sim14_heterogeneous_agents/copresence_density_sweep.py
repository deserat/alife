"""
Co-presence signal spatial density — queued-topic #230 + #225.

Session 82 confirmed the 53rd mechanism: the boundary acts on the intensive
co-presence signal, converting the extensive fill's density-dependence into
n-dependence. The fill decreases with grid size at matched density (80×80 >
160×160 > 320×320) and is NOT gain-compensable.

This script makes the extensive/intensive distinction QUANTITATIVE by measuring
the co-presence signal's spatial density directly:
  - fraction of cells with co-presence > 0 (spatial coverage)
  - mean co-presence per cell (signal magnitude)
  - fraction of cells with co-presence > 0.01 (significant coverage)
  - max co-presence (peak signal)

If the co-presence signal is intensive (arrangement-dependent), at matched
density it should have the SAME spatial density across grid sizes. If it's
n-dependent (as the 53rd mechanism predicts), it should be SPARSER on larger
grids at matched density.

Also tests #225: 320×320 at n=4800 (46.9/kc) — does the fill decrease
monotonically at a third density? Reference: 160×160 at n=1200 (46.9/kc).

Combos (2 densities × 3 grid sizes):
  23.4/kc: 80×80 n=150, 160×160 n=600, 320×320 n=2400
  46.9/kc: 80×80 n=300, 160×160 n=1200, 320×320 n=4800
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "copresence_density_sweep.json")

JITTER = 10.0

# Combos: (grid, n_termites, density_label, n_seeds_for_run)
# 80×80 and 160×160 use 4 seeds; 320×320 uses 2 seeds (compute time)
COMBOS = [
    # 23.4/kc density
    (80,  150,  "23.4kc", [42, 123, 256, 999]),
    (160, 600,  "23.4kc", [42, 123, 256, 999]),
    (320, 2400, "23.4kc", [42, 999]),
    # 46.9/kc density
    (80,  300,  "46.9kc", [42, 123, 256, 999]),
    (160, 1200, "46.9kc", [42, 123, 256, 999]),
    (320, 4800, "46.9kc", [42, 999]),
]

# No-inhibition fill references (2 seeds each, for fill comparison)
NO_INHIB_COMBOS = [
    (320, 4800, "46.9kc", [42, 999]),
    (160, 1200, "46.9kc", [42, 999]),
]


def make_params(grid_size, n_termites, g_form=0.01, g_persist=0.01):
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


def make_no_inhib_params(grid_size, n_termites):
    p = I14.curvature_params(0.0)
    p["grid_size"] = grid_size
    p["n_termites"] = n_termites
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def measure_copresence(material_by_id, params):
    """Compute co-presence field and measure its spatial density."""
    cp = I14.compute_id_copresence(material_by_id, params)
    grid_area = cp.shape[0] * cp.shape[1]
    total = float(cp.sum())
    n_nonzero = int(np.count_nonzero(cp))
    n_significant = int(np.sum(cp > 0.01))
    n_high = int(np.sum(cp > 0.1))
    return {
        "cp_mean": round(float(total / grid_area), 6),
        "cp_max": round(float(cp.max()), 4),
        "cp_frac_nonzero": round(n_nonzero / grid_area, 6),
        "cp_frac_significant": round(n_significant / grid_area, 6),
        "cp_frac_high": round(n_high / grid_area, 6),
        "cp_total": round(total, 2),
    }


def run_combo(grid, n, density_label, seeds, g=0.01):
    """Run 2-seed + 1-seed at one (grid, n) combo."""
    p = make_params(grid, n, g, g)
    grid_area = grid * grid
    entries_2 = []
    entries_1 = []

    for sd in seeds:
        # 2-seed run (for co-presence + composition)
        r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s2 = r2["summary"]
        mby2 = r2.get("_final_material_by_id", None)
        cp_stats = None
        if mby2 is not None:
            cp_stats = measure_copresence(mby2, p)
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
            "copresence": cp_stats,
        }
        entries_2.append(e2)

        # 1-seed run (for structural guarantee)
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


def run_no_inhib(grid, n, density_label, seeds):
    """Run no-inhibition 2-seed for fill reference."""
    p = make_no_inhib_params(grid, n)
    grid_area = grid * grid
    entries = []
    for sd in seeds:
        r = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="none")
        s = r["summary"]
        e = {
            "seed": sd,
            "cells": s["final_n_structure_cells"],
            "fill_pct": round(s["final_n_structure_cells"] / grid_area * 100, 2),
            "crossed_h7": s["crossed_h7"],
        }
        entries.append(e)
    return entries


def summarize_cp(entries_2):
    """Summarize co-presence stats across seeds."""
    n = len(entries_2)
    cps = [e["copresence"] for e in entries_2 if e["copresence"] is not None]
    if not cps:
        return None
    return {
        "cp_mean": round(float(np.mean([c["cp_mean"] for c in cps])), 6),
        "cp_max": round(float(np.mean([c["cp_max"] for c in cps])), 4),
        "cp_frac_nonzero": round(float(np.mean([c["cp_frac_nonzero"] for c in cps])), 6),
        "cp_frac_significant": round(float(np.mean([c["cp_frac_significant"] for c in cps])), 6),
        "cp_frac_high": round(float(np.mean([c["cp_frac_high"] for c in cps])), 6),
        "cp_total": round(float(np.mean([c["cp_total"] for c in cps])), 2),
    }


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
        "note": "Session 83: co-presence spatial density (#230) + 320×320 n=4800 (#225)",
        "jitter": JITTER,
        "densities": ["23.4kc", "46.9kc"],
        "grids": [80, 160, 320],
        "prediction_53rd": "co-presence signal sparser on larger grids at matched density",
        "prediction_intensive": "co-presence signal same at matched density across grids",
    }}

    print(f"\n{'='*90}")
    print("  CO-PRESENCE SPATIAL DENSITY SWEEP")
    print("  Testing: is the co-presence signal intensive or n-dependent?")
    print(f"{'='*90}")

    # --- Main sweep: with boundary (g=0.01) ---
    for grid, n, dens, seeds in COMBOS:
        density = n / (grid * grid) * 1000
        print(f"\n  {grid}×{grid} n={n} (dens={density:.1f}/kc) g=0.01 — "
              f"{len(seeds)} seeds")
        t1 = time.time()
        e2, e1 = run_combo(grid, n, dens, seeds)
        s = summarize(e2, e1)
        cp_sum = summarize_cp(e2)
        key = f"{grid}_{dens}"
        results[key] = {
            "grid": grid, "n_termites": n, "density": dens,
            "density_per_kcell": round(density, 2),
            "g_form": 0.01, "g_persist": 0.01,
            "hetero_2seed": e2, "hetero_1seed": e1,
            "summary": s,
            "copresence_summary": cp_sum,
        }
        elapsed = time.time() - t1
        cp_str = ""
        if cp_sum:
            cp_str = (f" cp_cov={cp_sum['cp_frac_nonzero']:.4f} "
                      f"cp_mean={cp_sum['cp_mean']:.6f} "
                      f"cp_max={cp_sum['cp_max']:.3f}")
        print(f"  → fill={s['mean_fill_pct']:.2f}% cells={s['mean_cells']} "
              f"l2={s['l2']} h7={s['h7']} cf={s['mean_coexist_frac']}"
              f"{cp_str} ({elapsed:.0f}s)")

    # --- No-inhibition fill references ---
    print(f"\n{'='*90}")
    print("  NO-INHIBITION FILL REFERENCES")
    print(f"{'='*90}")

    for grid, n, dens, seeds in NO_INHIB_COMBOS:
        density = n / (grid * grid) * 1000
        print(f"\n  {grid}×{grid} n={n} (dens={density:.1f}/kc) g=0 — "
              f"{len(seeds)} seeds")
        t1 = time.time()
        entries = run_no_inhib(grid, n, dens, seeds)
        mean_fill = round(float(np.mean([e["fill_pct"] for e in entries])), 2)
        mean_cells = int(np.mean([e["cells"] for e in entries]))
        key = f"{grid}_{dens}_noinhib"
        results[key] = {
            "grid": grid, "n_termites": n, "density": dens,
            "no_inhib": True,
            "entries": entries,
            "mean_fill_pct": mean_fill,
            "mean_cells": mean_cells,
        }
        elapsed = time.time() - t1
        print(f"  → fill={mean_fill:.2f}% cells={mean_cells} ({elapsed:.0f}s)")

    # --- Summary comparison ---
    print(f"\n{'='*100}")
    print("  CO-PRESENCE SIGNAL SPATIAL DENSITY AT MATCHED DENSITY")
    print(f"{'='*100}")
    print(f"{'density':>8s} | {'grid':>5s} | {'n':>5s} | "
          f"{'fill%':>7s} | {'cp_cov':>8s} | {'cp_mean':>10s} | "
          f"{'cp_max':>7s} | {'cp>0.01':>8s}")
    print("-" * 100)

    for dens in ["23.4kc", "46.9kc"]:
        for grid in [80, 160, 320]:
            key = f"{grid}_{dens}"
            if key not in results:
                continue
            r = results[key]
            s = r["summary"]
            cp = r.get("copresence_summary")
            if cp:
                print(f"{dens:>8s} | {grid:>5d} | {r['n_termites']:>5d} | "
                      f"{s['mean_fill_pct']:>6.2f}% | "
                      f"{cp['cp_frac_nonzero']:>8.5f} | "
                      f"{cp['cp_mean']:>10.7f} | "
                      f"{cp['cp_max']:>7.3f} | "
                      f"{cp['cp_frac_significant']:>8.5f}")
            else:
                print(f"{dens:>8s} | {grid:>5d} | {r['n_termites']:>5d} | "
                      f"{s['mean_fill_pct']:>6.2f}% | (no cp data)")

    # --- Verdict ---
    print(f"\n{'='*100}")
    print("  VERDICT")
    print(f"{'='*100}")

    for dens in ["23.4kc", "46.9kc"]:
        fills = []
        cp_covs = []
        for grid in [80, 160, 320]:
            key = f"{grid}_{dens}"
            if key in results and results[key].get("copresence_summary"):
                fills.append(results[key]["summary"]["mean_fill_pct"])
                cp_covs.append(results[key]["copresence_summary"]["cp_frac_nonzero"])
        if len(fills) >= 2:
            fill_trend = "decreasing" if all(fills[i] > fills[i+1]
                                            for i in range(len(fills)-1)) else "NOT decreasing"
            cp_trend = "decreasing" if all(cp_covs[i] > cp_covs[i+1]
                                          for i in range(len(cp_covs)-1)) else "NOT decreasing"
            print(f"\n  {dens}: fill {fills} → {fill_trend}")
            print(f"  {dens}: cp_cov {cp_covs} → {cp_trend}")
            if cp_trend == "decreasing":
                print(f"  → co-presence signal is N-DEPENDENT (sparser on larger grids)")
            else:
                print(f"  → co-presence signal is INTENSIVE (same at matched density)")

    # --- Fill cap comparison (#225) ---
    print(f"\n{'='*100}")
    print("  FILL CAP AT 46.9/kc ACROSS GRID SIZES (#225)")
    print(f"{'='*100}")
    for grid in [80, 160, 320]:
        key = f"{grid}_46.9kc"
        if key in results:
            s = results[key]["summary"]
            n = results[key]["n_termites"]
            print(f"  {grid}×{grid} n={n}: fill={s['mean_fill_pct']:.2f}% "
                  f"l2={s['l2']} h7={s['h7']} cf={s['mean_coexist_frac']}")
    # No-inhibition
    for grid in [160, 320]:
        key = f"{grid}_46.9kc_noinhib"
        if key in results:
            print(f"  {grid}×{grid} n={results[key]['n_termites']} no-inhib: "
                  f"fill={results[key]['mean_fill_pct']:.2f}%")

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
