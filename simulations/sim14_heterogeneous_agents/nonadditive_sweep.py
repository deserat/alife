"""
Non-additive interaction sweep — queued-topic #241.

Session 86 found the combined condition (g=0.3, bias=0.3) has spread 21.66%
— LESS than the focal-only spread (23.38%). The focal bias weakens the
boundary by concentrating each ID's material (less co-presence at the
midline → weaker B → less suppression). This is a non-additive interaction:
the two n-dependence sources are not independent.

This sweep runs the 2×2 factorial:
  {bias=0.0, bias=0.3} × {g=0.0, g=0.3} at 23.4/kc
  80×80 (n=150, 4 seeds) and 160×160 (n=600, 2 seeds)

Measures:
  - fill_pct under each condition (for spread computation)
  - b_max (max boundary field over the run) — proxy for co-presence strength
  - The interaction term: spread_combined - spread_focal - spread_boundary + spread_neither

If the interaction is negative (sub-additive), the focal bias suppresses
the boundary's contribution. If b_max is lower with focal bias than without,
the mechanism is co-presence reduction.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "nonadditive_sweep.json")

JITTER = 10.0
DENSITY = "23.4kc"

COMBOS = [
    (80,  150, [42, 123, 256, 999]),
    (160, 600, [42, 999]),
]

# The 2×2: (movement_bias, inh_gain)
CONDITIONS = [
    ("neither",      0.0, 0.0),
    ("focal_only",   0.3, 0.0),
    ("boundary_only", 0.0, 0.3),
    ("combined",     0.3, 0.3),
]


def make_params(grid_size, n_termites, inh_gain, movement_bias):
    p = I14.curvature_params(inh_gain)
    p["grid_size"] = grid_size
    p["n_termites"] = n_termites
    p["movement_bias"] = movement_bias
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_one(grid, n, seeds, inh_gain, bias):
    p = make_params(grid, n, inh_gain, bias)
    grid_area = grid * grid
    entries = []
    for sd in seeds:
        r = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s = r["summary"]
        # Extract b_max from boundary_trace (max over the run).
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
            "note": "Session 89: non-additive interaction between focal bias and boundary (#241)",
            "jitter": JITTER,
            "density": DENSITY,
            "grids": [80, 160],
            "conditions": [(name, g, b) for name, g, b in CONDITIONS],
        },
    }

    print(f"\n{'='*80}")
    print("  NON-ADDITIVE INTERACTION SWEEP (#241)")
    print(f"  2×2: bias×gain  |  80×80(4s) 160×160(2s)  |  jitter={JITTER}")
    print(f"{'='*80}")

    for name, gain, bias in CONDITIONS:
        for grid, n, seeds in COMBOS:
            density = n / (grid * grid) * 1000
            print(f"\n  {grid}×{grid} n={n} {name} (g={gain}, bias={bias}) — {len(seeds)} seeds", flush=True)
            t1 = time.time()
            entries = run_one(grid, n, seeds, gain, bias)
            s = summarize(entries)
            key = f"{name}_{grid}_n{n}"
            results[key] = {
                "condition": name, "gain": gain, "bias": bias,
                "grid": grid, "n_termites": n,
                "density_per_kcell": round(density, 2),
                "entries": entries, "summary": s,
            }
            elapsed = time.time() - t1
            print(f"  → fill={s['mean_fill_pct']:.2f}% b_max={s['mean_b_max']:.4f} "
                  f"l2={s['l2']} h7={s['h7']} ({elapsed:.0f}s)", flush=True)

    # --- Spread & interaction analysis ---
    print(f"\n{'='*80}")
    print("  SPREAD & INTERACTION ANALYSIS", flush=True)
    print(f"{'='*80}", flush=True)

    spread_data = {}
    for grid, n, _ in COMBOS:
        grid_label = f"{grid}×{grid}"
        fills = {}
        b_maxes = {}
        for name, gain, bias in CONDITIONS:
            key = f"{name}_{grid}_n{n}"
            if key in results:
                fills[name] = results[key]["summary"]["mean_fill_pct"]
                b_maxes[name] = results[key]["summary"]["mean_b_max"]

        if len(fills) >= 4:
            spread_neither = abs(fills.get("neither", 0) - fills.get("neither", 0))  # placeholder
            # Compute spreads: fill_80 - fill_160 for each condition
            # Actually, we compute spread per condition as fill at this grid minus fill at other grid
            # But we're iterating per grid. Let me restructure.

    # Compute spreads across grids for each condition
    print(f"\n  {'condition':>16s} | {'80×80 fill':>10s} | {'160×160 fill':>12s} | "
          f"{'spread':>8s} | {'80 b_max':>10s} | {'160 b_max':>10s}", flush=True)
    print("  " + "-" * 78, flush=True)

    interaction_data = []
    for name, gain, bias in CONDITIONS:
        fills = {}
        b_maxes = {}
        for grid, n, _ in COMBOS:
            key = f"{name}_{grid}_n{n}"
            if key in results:
                fills[grid] = results[key]["summary"]["mean_fill_pct"]
                b_maxes[grid] = results[key]["summary"]["mean_b_max"]

        if len(fills) >= 2:
            spread = abs(fills[80] - fills[160])
            interaction_data.append({
                "condition": name, "gain": gain, "bias": bias,
                "fill_80": fills[80], "fill_160": fills[160],
                "spread": round(spread, 3),
                "b_max_80": b_maxes.get(80, 0.0), "b_max_160": b_maxes.get(160, 0.0),
            })
            print(f"  {name:>16s} | {fills[80]:>9.2f}% | {fills[160]:>11.2f}% | "
                  f"{spread:>7.2f}% | {b_maxes.get(80,0):>10.4f} | {b_maxes.get(160,0):>10.4f}",
                  flush=True)

    # Compute interaction term
    spreads = {d["condition"]: d["spread"] for d in interaction_data}
    if all(k in spreads for k in ["neither", "focal_only", "boundary_only", "combined"]):
        # Additive prediction: combined_additive = focal + boundary - neither
        additive_pred = spreads["focal_only"] + spreads["boundary_only"] - spreads["neither"]
        actual_combined = spreads["combined"]
        interaction = actual_combined - additive_pred

        print(f"\n  Interaction analysis:", flush=True)
        print(f"    Additive prediction: focal + boundary - neither = "
              f"{spreads['focal_only']:.2f} + {spreads['boundary_only']:.2f} - "
              f"{spreads['neither']:.2f} = {additive_pred:.2f}%", flush=True)
        print(f"    Actual combined:     {actual_combined:.2f}%", flush=True)
        print(f"    Interaction term:     {interaction:.2f}%  "
              f"({'SUB-ADDITIVE' if interaction < -0.5 else 'SUPER-ADDITIVE' if interaction > 0.5 else 'ADDITIVE'})",
              flush=True)
        print(f"    Focal-only spread:    {spreads['focal_only']:.2f}%  (combined is "
              f"{spreads['focal_only'] - actual_combined:.2f}% LESS)", flush=True)

        results["interaction"] = {
            "additive_prediction": round(additive_pred, 3),
            "actual_combined": round(actual_combined, 3),
            "interaction_term": round(interaction, 3),
            "verdict": "SUB-ADDITIVE" if interaction < -0.5 else ("SUPER-ADDITIVE" if interaction > 0.5 else "ADDITIVE"),
            "focal_minus_combined": round(spreads["focal_only"] - actual_combined, 3),
        }

    # b_max comparison: does focal bias reduce b_max?
    print(f"\n  b_max comparison (focal bias reduces co-presence?):", flush=True)
    for grid, n, _ in COMBOS:
        key_b = f"boundary_only_{grid}_n{n}"
        key_c = f"combined_{grid}_n{n}"
        if key_b in results and key_c in results:
            b_only = results[key_b]["summary"]["mean_b_max"]
            b_comb = results[key_c]["summary"]["mean_b_max"]
            ratio = b_comb / max(b_only, 1e-9)
            print(f"    {grid}×{grid}: b_max(boundary_only)={b_only:.4f}  "
                  f"b_max(combined)={b_comb:.4f}  ratio={ratio:.3f}  "
                  f"({'WEAKENED' if b_comb < b_only else 'UNCHANGED'})", flush=True)

    results["spread_data"] = interaction_data

    # --- Determinism check ---
    print(f"\n  Determinism check...", flush=True)
    p = make_params(80, 150, 0.3, 0.3)
    r1 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    r2 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    det_ok = (r1["summary"]["final_n_structure_cells"] ==
              r2["summary"]["final_n_structure_cells"])
    print(f"  80×80 n=150 g=0.3 bias=0.3 seed=42: {'PASS' if det_ok else 'FAIL'}", flush=True)
    results["determinism"] = {"passed": det_ok}

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)", flush=True)
    return results


if __name__ == "__main__":
    run_sweep()
