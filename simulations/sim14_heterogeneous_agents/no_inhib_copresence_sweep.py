"""
No-inhibition co-presence — queued-topic #231.

Session 83 found that the co-presence at steady state is endogenous —
shaped by the boundary's feedback loop (both cause and consequence).
Measuring it inside the loop cannot test the loop's causality.

This script measures the co-presence OUTSIDE the loop: in no-inhibition
runs (mode="hetero", inh_gain=0.0 — ID-tagged deposits but no B
suppression).  Without the boundary, the fill IS density-dependent
(Session 81: without the boundary, fill ≈ same at matched density).
If the co-presence is ALSO density-dependent (same at matched density
across grid sizes), it is INTENSIVE.  If it is n-dependent (sparser on
larger grids at matched density), it is EXTENSIVE.

Session 83 refined the 53rd mechanism: the co-presence at steady state
is extensive (scales with absolute material/n); the n-dependence comes
from the normalization (extensive B / intensive b_scale).  This script
tests whether the co-presence is STILL extensive without the boundary —
if yes, the signal itself is extensive (not just the B it drives).

Combos (2 densities × 3 grid sizes, 2-seed only):
  23.4/kc: 80×80 n=150, 160×160 n=600, 320×320 n=2400
  46.9/kc: 80×80 n=300, 160×160 n=1200, 320×320 n=4800

Each combo runs BOTH g=0 (no-inhibition) and g=0.01 (with boundary)
for direct comparison.  The 1-seed control is structurally zero by
design (material_by_id[1] = 0) — no need to run it.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "no_inhib_copresence_sweep.json")

JITTER = 10.0
DIRECT_RADIUS = I14.DIRECT_RADIUS

# Combos: (grid, n_termites, density_label, seeds)
COMBOS = [
    # 23.4/kc density
    (80,  150,  "23.4kc", [42, 123, 256, 999]),
    (160, 600,  "23.4kc", [42, 123, 256, 999]),
    (320, 2400, "23.4kc", [42, 999]),
    # 46.9/kc density (skip 320×320 n=4800 — too expensive for one session)
    (80,  300,  "46.9kc", [42, 123, 256, 999]),
    (160, 1200, "46.9kc", [42, 123, 256, 999]),
    # (320, 4800, "46.9kc", [42, 999]),  # deferred to next session
]


def make_params(grid_size, n_termites, inh_gain=0.0):
    """Params for hetero mode at given grid/n.  inh_gain=0 → no boundary."""
    p = I14.curvature_params(inh_gain)
    p["grid_size"] = grid_size
    p["n_termites"] = n_termites
    if inh_gain > 0.0:
        p["boundary_mode"] = "dual"
        p["g_form"] = 0.01
        p["g_persist"] = 0.01
        p["b_decay_form"] = 0.01
        p["b_decay_persist"] = 0.005
        p["b_growth_form"] = 0.1
        p["b_growth_persist"] = 0.1
        p["direct_radius"] = DIRECT_RADIUS
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


def run_one(grid, n, density_label, seeds, g):
    """Run 2-seed at one (grid, n, g) combo.  Return per-seed entries."""
    p = make_params(grid, n, g)
    grid_area = grid * grid
    entries = []
    for sd in seeds:
        r = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s = r["summary"]
        mby = r.get("_final_material_by_id", None)
        cp_stats = None
        if mby is not None:
            cp_stats = measure_copresence(mby, p)
        e = {
            "seed": sd,
            "l2_crossed": s["l2_crossed"],
            "l2_outcome": s["l2_outcome"],
            "l2_stable": s["l2_stable"],
            "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
            "crossed_h7": s["crossed_h7"],
            "cells": s["final_n_structure_cells"],
            "fill_pct": round(s["final_n_structure_cells"] / grid_area * 100, 2),
            "copresence": cp_stats,
        }
        entries.append(e)
    return entries


def summarize_cp(entries):
    """Average co-presence stats across seeds."""
    cps = [e["copresence"] for e in entries if e["copresence"] is not None]
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


def summarize(entries):
    n = len(entries)
    return {
        "l2": f"{sum(1 for e in entries if e['l2_crossed'])}/{n}",
        "coexist": f"{sum(1 for e in entries if e['l2_outcome'] == 'coexist')}/{n}",
        "stable": f"{sum(1 for e in entries if e['l2_stable'])}/{n}",
        "h7": f"{sum(1 for e in entries if e['crossed_h7'])}/{n}",
        "mean_fill_pct": round(float(np.mean([e["fill_pct"] for e in entries])), 2),
        "mean_coexist_frac": round(float(np.mean([e["l2_coexist_frac"] for e in entries])), 3),
        "mean_cells": int(np.mean([e["cells"] for e in entries])),
    }


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "note": "Session 84: no-inhibition co-presence (#231)",
        "jitter": JITTER,
        "densities": ["23.4kc", "46.9kc"],
        "grids": [80, 160, 320],
        "gains": [0.0, 0.01],
        "prediction_intensive": "co-presence same at matched density across grids (no boundary)",
        "prediction_extensive": "co-presence sparser on larger grids at matched density (no boundary)",
    }}

    print(f"\n{'='*90}")
    print("  NO-INHIBITION CO-PRESENCE SWEEP (#231)")
    print("  Testing: is the co-presence signal intensive or extensive WITHOUT the boundary?")
    print(f"{'='*90}")

    for grid, n, dens, seeds in COMBOS:
        density = n / (grid * grid) * 1000
        for g in [0.0, 0.01]:
            glabel = "g=0 (no inhib)" if g == 0.0 else "g=0.01 (boundary)"
            print(f"\n  {grid}×{grid} n={n} (dens={density:.1f}/kc) {glabel} — "
                  f"{len(seeds)} seeds")
            t1 = time.time()
            entries = run_one(grid, n, dens, seeds, g)
            s = summarize(entries)
            cp_sum = summarize_cp(entries)
            key = f"{grid}_{dens}_g{g}"
            results[key] = {
                "grid": grid, "n_termites": n, "density": dens,
                "density_per_kcell": round(density, 2),
                "inh_gain": g,
                "entries": entries,
                "summary": s,
                "copresence_summary": cp_sum,
            }
            elapsed = time.time() - t1
            cp_str = ""
            if cp_sum:
                cp_str = (f" cp_cov={cp_sum['cp_frac_nonzero']:.4f} "
                          f"cp_mean={cp_sum['cp_mean']:.6f} "
                          f"cp_max={cp_sum['cp_max']:.3f}")
            print(f"  → fill={s['mean_fill_pct']:.2f}% l2={s['l2']} "
                  f"h7={s['h7']} cf={s['mean_coexist_frac']}{cp_str} "
                  f"({elapsed:.0f}s)")

    # --- Comparison table ---
    print(f"\n{'='*100}")
    print("  CO-PRESENCE AT MATCHED DENSITY: NO-INHIBITION vs BOUNDARY")
    print(f"{'='*100}")
    print(f"{'density':>8s} | {'grid':>5s} | {'n':>6s} | {'g':>6s} | "
          f"{'fill%':>7s} | {'cp_cov':>8s} | {'cp_mean':>10s} | "
          f"{'cp_max':>7s} | {'cp>0.01':>8s}")
    print("-" * 100)

    for dens in ["23.4kc", "46.9kc"]:
        for grid in [80, 160, 320]:
            for g in [0.0, 0.01]:
                key = f"{grid}_{dens}_g{g}"
                if key not in results:
                    continue
                r = results[key]
                s = r["summary"]
                cp = r.get("copresence_summary")
                if cp:
                    g_str = "0.00" if g == 0.0 else "0.01"
                    print(f"{dens:>8s} | {grid:>5d} | {r['n_termites']:>6d} | "
                          f"{g_str:>6s} | {s['mean_fill_pct']:>6.2f}% | "
                          f"{cp['cp_frac_nonzero']:>8.5f} | "
                          f"{cp['cp_mean']:>10.7f} | "
                          f"{cp['cp_max']:>7.3f} | "
                          f"{cp['cp_frac_significant']:>8.5f}")

    # --- Verdict ---
    print(f"\n{'='*100}")
    print("  VERDICT: IS THE CO-PRESENCE INTENSIVE OR EXTENSIVE (NO BOUNDARY)?")
    print(f"{'='*100}")

    for dens in ["23.4kc", "46.9kc"]:
        print(f"\n  {dens}:")
        for g in [0.0, 0.01]:
            g_str = "g=0 (no inhib)" if g == 0.0 else "g=0.01 (boundary)"
            fills = []
            cp_means = []
            cp_covs = []
            for grid in [80, 160, 320]:
                key = f"{grid}_{dens}_g{g}"
                if key in results and results[key].get("copresence_summary"):
                    fills.append(results[key]["summary"]["mean_fill_pct"])
                    cp_means.append(results[key]["copresence_summary"]["cp_mean"])
                    cp_covs.append(results[key]["copresence_summary"]["cp_frac_nonzero"])
            if len(fills) >= 2:
                fill_dec = all(fills[i] > fills[i+1] for i in range(len(fills)-1))
                cp_mean_dec = all(cp_means[i] > cp_means[i+1] for i in range(len(cp_means)-1))
                cp_cov_dec = all(cp_covs[i] > cp_covs[i+1] for i in range(len(cp_covs)-1))
                print(f"    {g_str}: fill={fills} cp_mean={cp_means} cp_cov={cp_covs}")
                print(f"      fill {'decreasing' if fill_dec else 'NOT decreasing'} | "
                      f"cp_mean {'decreasing' if cp_mean_dec else 'NOT decreasing'} | "
                      f"cp_cov {'decreasing' if cp_cov_dec else 'NOT decreasing'}")
                if g == 0.0:
                    if cp_mean_dec and cp_cov_dec:
                        print(f"      → co-presence is EXTENSIVE (n-dependent without boundary)")
                    elif not cp_mean_dec and not cp_cov_dec:
                        print(f"      → co-presence is INTENSIVE (density-dependent without boundary)")
                    else:
                        print(f"      → MIXED: cp_mean {'dec' if cp_mean_dec else 'not dec'} "
                              f"but cp_cov {'dec' if cp_cov_dec else 'not dec'}")

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
