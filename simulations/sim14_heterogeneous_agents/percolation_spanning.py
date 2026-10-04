"""
Percolation spanning cluster analysis (queued-topic #206).

At n=8000 the fill is ~60.7% (above the 2D site percolation threshold ~59%).
But the structure is fragmented by the boundary (late_mean_lc 1.25–5.05).
Is there a spanning cluster, or is the "percolation" in fill fraction only?

This script runs n=8000 (and n=6000 for comparison) at the standard config,
captures the final material field, and measures:
  1. Largest connected component (Moore 8-connectivity)
  2. Does the largest component span the grid (touch all 4 edges)?
  3. What fraction of structure cells are in the largest component?
  4. Component size distribution

Also runs the no-inhibition control (g=0) for comparison.

Config: 160×160, dual mode, focal bias=0.3, per_step jitter=10.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "percolation_spanning.json")

GRID = 160
JITTER = 10.0
SEEDS = [42, 123, 256, 999]


def make_params(n_termites, g_form, g_persist):
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
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def label_components(mask):
    """Label Moore-connected components (8-connectivity) via BFS.
    Returns (labels, n_components) where labels is an int array
    with 0=background, 1..N=component IDs."""
    visited = np.zeros_like(mask, dtype=bool)
    labels = np.zeros_like(mask, dtype=np.int32)
    rows, cols = mask.shape
    next_id = 0
    for r0 in range(rows):
        for c0 in range(cols):
            if mask[r0, c0] and not visited[r0, c0]:
                next_id += 1
                visited[r0, c0] = True
                labels[r0, c0] = next_id
                stack = [(r0, c0)]
                while stack:
                    r, c = stack.pop()
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            rr = (r + dr) % rows
                            cc = (c + dc) % cols
                            if mask[rr, cc] and not visited[rr, cc]:
                                visited[rr, cc] = True
                                labels[rr, cc] = next_id
                                stack.append((rr, cc))
    return labels, next_id


def component_stats(labels, n_components):
    """Compute size, bounding box, and spanning status for each component."""
    stats = []
    rows, cols = labels.shape
    for cid in range(1, n_components + 1):
        mask_cid = labels == cid
        size = int(mask_cid.sum())
        if size == 0:
            continue
        rows_where = np.where(mask_cid.any(axis=1))[0]
        cols_where = np.where(mask_cid.any(axis=0))[0]
        r_min, r_max = int(rows_where[0]), int(rows_where[-1])
        c_min, c_max = int(cols_where[0]), int(cols_where[-1])
        # Spanning: touches all 4 edges (wraps on torus)
        touches_top = bool(mask_cid[0, :].any())
        touches_bottom = bool(mask_cid[-1, :].any())
        touches_left = bool(mask_cid[:, 0].any())
        touches_right = bool(mask_cid[:, -1].any())
        # Spanning in x (wraps): touches both left and right
        spans_x = touches_left and touches_right
        # Spanning in y (wraps): touches both top and bottom
        spans_y = touches_top and touches_bottom
        # Spanning in either dimension
        spans = spans_x or spans_y
        stats.append({
            "id": cid,
            "size": size,
            "bbox": [r_min, r_max, c_min, c_max],
            "touches_top": touches_top,
            "touches_bottom": touches_bottom,
            "touches_left": touches_left,
            "touches_right": touches_right,
            "spans_x": spans_x,
            "spans_y": spans_y,
            "spans": spans,
        })
    stats.sort(key=lambda s: s["size"], reverse=True)
    return stats


def analyze_run(n_termites, g_form, g_persist, seed, no_inhib=False):
    """Run one simulation and analyze the final material field."""
    if no_inhib:
        p = make_no_inhib_params(n_termites)
    else:
        p = make_params(n_termites, g_form, g_persist)

    r = I14.run_two_region_hetero(p, seed=seed, n_seeds=2, mode="hetero")
    s = r["summary"]

    # Get the final material field (full resolution, from _final_material).
    if "_final_material" not in r:
        return {"error": "no _final_material", "summary": s}

    mat = np.array(r["_final_material"], dtype=np.float64)

    # Structure mask: material > STRUCTURE_THRESHOLD (1.0, same as sim09)
    STRUCT_THRESHOLD = 1.0
    struct_mask = mat > STRUCT_THRESHOLD

    total_cells = int(struct_mask.sum())
    fill_pct = total_cells / (GRID * GRID) * 100

    # Label components
    labels, n_comp = label_components(struct_mask)

    if n_comp == 0:
        return {
            "n_termites": n_termites,
            "g": g_form if not no_inhib else 0.0,
            "seed": seed,
            "no_inhib": no_inhib,
            "total_cells": 0,
            "fill_pct": 0.0,
            "n_components": 0,
            "largest_size": 0,
            "largest_frac": 0.0,
            "spans": False,
            "spans_x": False,
            "spans_y": False,
            "summary": s,
        }

    stats = component_stats(labels, n_comp)
    largest = stats[0]
    largest_frac = largest["size"] / total_cells

    # Size distribution
    sizes = [st["size"] for st in stats]
    n_spanning = sum(1 for st in stats if st["spans"])
    n_span_x = sum(1 for st in stats if st["spans_x"])
    n_span_y = sum(1 for st in stats if st["spans_y"])

    result = {
        "n_termites": n_termites,
        "g": g_form if not no_inhib else 0.0,
        "seed": seed,
        "no_inhib": no_inhib,
        "total_cells": total_cells,
        "fill_pct": round(fill_pct, 2),
        "n_components": n_comp,
        "largest_size": largest["size"],
        "largest_frac": round(largest_frac, 4),
        "largest_spans": largest["spans"],
        "largest_spans_x": largest["spans_x"],
        "largest_spans_y": largest["spans_y"],
        "n_spanning": n_spanning,
        "n_span_x": n_span_x,
        "n_span_y": n_span_y,
        "top5_sizes": sizes[:5],
        "l2_crossed": s["l2_crossed"],
        "l2_outcome": s["l2_outcome"],
        "crossed_h7": s["crossed_h7"],
        "mean_lc": round(s.get("l2_late_mean_lc", 0.0), 2),
        "mean_rc": round(s.get("l2_late_mean_rc", 0.0), 2),
    }
    return result


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "note": "Session 74: percolation spanning cluster analysis (#206)",
        "percolation_threshold": "~59% (2D site percolation, square lattice)",
    }}

    combos = [
        # (n, g, no_inhib, label)
        (8000, 0.001, False, "n8000_g001"),
        (8000, 0.0005, False, "n8000_g0005"),
        (8000, 0.003, False, "n8000_g003"),
        (6000, 0.001, False, "n6000_g001"),
        (8000, 0.0, True, "n8000_no_inhib"),
        (6000, 0.0, True, "n6000_no_inhib"),
    ]

    for n, g, no_inhib, label in combos:
        results[label] = []
        for seed in SEEDS:
            print(f"  Running {label} seed={seed}...")
            t_start = time.time()
            res = analyze_run(n, g, g, seed, no_inhib=no_inhib)
            elapsed = time.time() - t_start
            print(f"    ({elapsed:.1f}s) cells={res.get('total_cells', 0)} "
                  f"fill={res.get('fill_pct', 0):.1f}% "
                  f"ncomp={res.get('n_components', 0)} "
                  f"largest={res.get('largest_size', 0)} "
                  f"({res.get('largest_frac', 0):.1%}) "
                  f"spans={res.get('largest_spans', False)} "
                  f"span_x={res.get('largest_spans_x', False)} "
                  f"span_y={res.get('largest_spans_y', False)}")
            results[label].append(res)

    # Summary
    print(f"\n{'='*100}")
    print("  PERCOLATION SPANNING CLUSTER ANALYSIS SUMMARY")
    print(f"{'='*100}")
    print(f"{'label':>20s} {'n':>5s} {'g':>7s} | {'fill%':>5s} {'ncomp':>5s} "
          f"{'largest':>7s} {'frac':>5s} {'spans':>5s} {'span_x':>6s} "
          f"{'span_y':>6s} {'l2':>5s} {'h7':>5s}")
    print("-" * 100)
    for n, g, no_inhib, label in combos:
        entries = results[label]
        for e in entries:
            no_flag = " (no_inhib)" if e.get("no_inhib") else ""
            print(f"{label+no_flag:>20s} {e['n_termites']:5d} {e['g']:7.4f} | "
                  f"{e['fill_pct']:5.1f} {e['n_components']:5d} "
                  f"{e['largest_size']:7d} {e['largest_frac']:5.1%} "
                  f"{'Y' if e['largest_spans'] else 'N':>5s} "
                  f"{'Y' if e['largest_spans_x'] else 'N':>6s} "
                  f"{'Y' if e['largest_spans_y'] else 'N':>6s} "
                  f"{'Y' if e['l2_crossed'] else 'N':>5s} "
                  f"{'Y' if e['crossed_h7'] else 'N':>5s}")

    # Aggregate per condition
    print(f"\n  AGGREGATE (mean across 4 seeds):")
    print(f"{'label':>20s} {'fill%':>6s} {'ncomp':>6s} {'largest':>7s} "
          f"{'frac':>6s} {'span%':>6s}")
    for n, g, no_inhib, label in combos:
        entries = results[label]
        mean_fill = np.mean([e["fill_pct"] for e in entries])
        mean_ncomp = np.mean([e["n_components"] for e in entries])
        mean_largest = np.mean([e["largest_size"] for e in entries])
        mean_frac = np.mean([e["largest_frac"] for e in entries])
        n_spanning = sum(1 for e in entries if e["largest_spans"])
        print(f"{label:>20s} {mean_fill:6.1f} {mean_ncomp:6.1f} "
              f"{mean_largest:7.0f} {mean_frac:6.1%} {n_spanning}/4")

    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
