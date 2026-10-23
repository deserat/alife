"""
Higher-density finer gain sweep — queued-topic #240.

Session 87 found the 53rd mechanism's n-dependent spread (at 23.4/kc,
bias=0, no focal bias) is a saturating amplifier: spread goes
0.54% (g=0) → 0.72% (g=0.05) → 2.21% (g=0.1) → 2.72% (g=0.2) →
1.30% (g=0.3). Non-monotonic — peaks at g=0.2 then drops as the
boundary saturates.

Does the boundary's n-dependent effect STRENGTHEN at higher density
(46.9/kc)? At higher density the co-presence is more extensive (more
material per cell), so the boundary has more signal to act on. The
boundary's suppression may be stronger, widening the bandwidth, or
the saturation may come earlier (narrowing it).

This sweep replicates the 23.4/kc finer gain sweep at 46.9/kc:
  g = 0.0, 0.05, 0.1, 0.15, 0.2, 0.3 — all at bias=0 (no focal bias).
  80×80 (n=300, 4 seeds) and 160×160 (n=1200, 2 seeds).

Comparison to Session 87's 23.4/kc results: if the spread is larger
at 46.9/kc, the boundary's n-dependence strengthens with density;
if similar or smaller, the saturation limits the effect regardless
of density.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "higher_density_gain_sweep.json")

JITTER = 10.0
DENSITY_LABEL = "46.9kc"

COMBOS = [
    (80,  300,  [42, 123, 256, 999]),
    (160, 1200, [42, 999]),
]

GAINS = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3]


def make_params(grid_size, n_termites, inh_gain):
    p = I14.curvature_params(inh_gain)
    p["grid_size"] = grid_size
    p["n_termites"] = n_termites
    p["movement_bias"] = 0.0
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_one(grid, n, seeds, inh_gain):
    p = make_params(grid, n, inh_gain)
    grid_area = grid * grid
    entries = []
    for sd in seeds:
        r = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s = r["summary"]
        e = {
            "seed": sd,
            "l2_crossed": s["l2_crossed"],
            "l2_outcome": s["l2_outcome"],
            "l2_stable": s["l2_stable"],
            "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
            "crossed_h7": s["crossed_h7"],
            "cells": s["final_n_structure_cells"],
            "fill_pct": round(s["final_n_structure_cells"] / grid_area * 100, 2),
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
        "mean_cells": int(np.mean([e["cells"] for e in entries])),
    }


def run_sweep():
    t0 = time.time()
    results = {
        "config": {
            "note": "Session 88: higher-density (46.9/kc) finer gain sweep — does the boundary's n-dependence strengthen? (#240)",
            "jitter": JITTER,
            "density": DENSITY_LABEL,
            "grids": [80, 160],
            "gains": GAINS,
            "bias": 0.0,
            "comparison": "Session 87's 23.4/kc finer_gain_sweep.json",
        },
    }

    print(f"\n{'='*80}")
    print("  HIGHER-DENSITY GAIN SWEEP (#240)")
    print(f"  Density: {DENSITY_LABEL}  Gains: {GAINS}  bias=0")
    print(f"  Grids: 80×80(4s, n=300)  160×160(2s, n=1200)")
    print(f"{'='*80}")

    for g in GAINS:
        for grid, n, seeds in COMBOS:
            density = n / (grid * grid) * 1000
            print(f"\n  {grid}×{grid} n={n} g={g} bias=0 — {len(seeds)} seeds", flush=True)
            t1 = time.time()
            entries = run_one(grid, n, seeds, g)
            s = summarize(entries)
            key = f"g{g}_{grid}_n{n}"
            results[key] = {
                "gain": g, "grid": grid, "n_termites": n,
                "density_per_kcell": round(density, 2),
                "bias": 0.0,
                "entries": entries, "summary": s,
            }
            elapsed = time.time() - t1
            print(f"  → fill={s['mean_fill_pct']:.2f}% l2={s['l2']} "
                  f"h7={s['h7']} ({elapsed:.0f}s)", flush=True)

    # --- Spread analysis ---
    print(f"\n{'='*80}")
    print("  SPREAD ANALYSIS (46.9/kc)", flush=True)
    print(f"{'='*80}", flush=True)
    print(f"{'g':>6s} | {'80×80':>10s} | {'160×160':>10s} | {'spread':>8s}", flush=True)
    print("-" * 80, flush=True)

    spread_data = []
    for g in GAINS:
        fills = []
        for grid, n, seeds in COMBOS:
            key = f"g{g}_{grid}_n{n}"
            if key in results:
                fills.append(results[key]["summary"]["mean_fill_pct"])
        if len(fills) >= 2:
            spread = abs(fills[0] - fills[1])
            spread_data.append({"g": g, "fills": fills, "spread": round(spread, 3)})
            verdict = "DENSITY-DEP" if spread < 2.0 else "N-DEPENDENT"
            print(f"{g:>6.2f} | {fills[0]:>9.2f}% | {fills[1]:>9.2f}% | {spread:>7.2f}%  {verdict}", flush=True)

    results["spread_analysis"] = spread_data

    # --- Comparison to 23.4/kc ---
    ref_path = os.path.join(SIM14_DIR, "output", "finer_gain_sweep.json")
    comparison = []
    if os.path.exists(ref_path):
        with open(ref_path) as f:
            ref = json.load(f)
        ref_spread = ref.get("spread_analysis", [])
        ref_map = {sd["g"]: sd["spread"] for sd in ref_spread}
        print(f"\n{'='*80}")
        print("  COMPARISON: 23.4/kc vs 46.9/kc spread", flush=True)
        print(f"{'='*80}", flush=True)
        print(f"{'g':>6s} | {'23.4/kc':>10s} | {'46.9/kc':>10s} | {'delta':>8s}", flush=True)
        print("-" * 80, flush=True)
        for sd in spread_data:
            g = sd["g"]
            s23 = ref_map.get(g, None)
            s46 = sd["spread"]
            delta = round(s46 - s23, 3) if s23 is not None else None
            comparison.append({"g": g, "spread_23": s23, "spread_46": s46, "delta": delta})
            if s23 is not None:
                stronger = "STRONGER" if delta > 0 else "WEAKER"
                print(f"{g:>6.2f} | {s23:>9.2f}% | {s46:>9.2f}% | {delta:>7.2f}%  {stronger}", flush=True)
            else:
                print(f"{g:>6.2f} | {'—':>10s} | {s46:>9.2f}% | {'—':>8s}", flush=True)
    results["comparison"] = comparison

    # --- Transition analysis ---
    first_n = None
    for sd in spread_data:
        if sd["spread"] > 2.0:
            first_n = sd["g"]
            break
    if first_n is not None:
        print(f"\n  First gain where spread > 2%: g = {first_n}", flush=True)
    else:
        print(f"\n  No gain produces spread > 2%", flush=True)
    results["transition"] = {"first_n_dependent_gain": first_n, "threshold": 2.0}

    # --- Determinism check ---
    print(f"\n  Determinism check...", flush=True)
    p = make_params(80, 300, 0.15)
    r1 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    r2 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    det_ok = (r1["summary"]["final_n_structure_cells"] ==
              r2["summary"]["final_n_structure_cells"])
    print(f"  80×80 n=300 g=0.15 bias=0 seed=42: {'PASS' if det_ok else 'FAIL'}", flush=True)
    results["determinism"] = {"passed": det_ok}

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)", flush=True)
    return results


if __name__ == "__main__":
    run_sweep()
