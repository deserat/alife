"""
g* limit sweep — where does g* hit zero? (#216)

At n=12000, g* does NOT hit zero (composition is alive, though collapsed:
l2=0/4, h7=4/4 at g=0.001). At n=15000, g* is undefined (the boundary
has no effect: g=0.001 ≡ g=0, both fill ~100%).

Where exactly does g* hit zero? A sweep at n=11000–14000 at very low
gains (0.0005, 0.001) × 4 seeds × {2,1} will locate the density where
the boundary's effect vanishes.

g* is defined as the highest gain at which composition (l2_crossed or
coexist) is still non-zero. If l2=0/4 at all gains, g*=0 (boundary
has no effect on composition). If l2 > 0 at some gain, g* > 0.

The key test: does the boundary condition (g=0.001) differ from the
no-boundary condition (g=0) at n=11000–14000? If fill at g=0.001 ≈
fill at g=0 (100%), the boundary has no effect — g*=0.

Config: 160×160, dual mode, focal bias=0.3, per_step jitter=10.
Session 77.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "g_star_limit_sweep.json")

GRID = 160
JITTER = 10.0
SEEDS_4 = [42, 123, 256, 999]

# n=11000, 12000, 13000, 14000 at g=0.0005, 0.001 × 4 seeds × {2,1}
# + no-inhibition controls at each n (g=0, 2-seed only)
PLATEAU_COMBOS = [
    (11000, 0.001,  0.001,  "n11000_g001"),
    (11000, 0.0005, 0.0005, "n11000_g0005"),
    (12000, 0.001,  0.001,  "n12000_g001"),
    (12000, 0.0005, 0.0005, "n12000_g0005"),
    (13000, 0.001,  0.001,  "n13000_g001"),
    (13000, 0.0005, 0.0005, "n13000_g0005"),
    (14000, 0.001,  0.001,  "n14000_g001"),
    (14000, 0.0005, 0.0005, "n14000_g0005"),
]

NO_INHIB_COMBOS = [
    (11000, 0.0, 0.0, "n11000_g000_no_inhib"),
    (12000, 0.0, 0.0, "n12000_g000_no_inhib"),
    (13000, 0.0, 0.0, "n13000_g000_no_inhib"),
    (14000, 0.0, 0.0, "n14000_g000_no_inhib"),
]


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
        touches_top = bool(mask_cid[0, :].any())
        touches_bottom = bool(mask_cid[-1, :].any())
        touches_left = bool(mask_cid[:, 0].any())
        touches_right = bool(mask_cid[:, -1].any())
        spans_x = touches_left and touches_right
        spans_y = touches_top and touches_bottom
        spans = spans_x or spans_y
        stats.append({
            "id": cid, "size": size,
            "bbox": [r_min, r_max, c_min, c_max],
            "spans_x": spans_x, "spans_y": spans_y, "spans": spans,
        })
    stats.sort(key=lambda s: s["size"], reverse=True)
    return stats


def percolation_analysis(mat, struct_threshold=1.0):
    struct_mask = mat > struct_threshold
    total_cells = int(struct_mask.sum())
    if total_cells == 0:
        return {"total_cells": 0, "fill_pct": 0.0, "n_components": 0,
                "largest_size": 0, "largest_frac": 0.0,
                "spans": False, "spans_x": False, "spans_y": False,
                "n_spanning": 0, "top5_sizes": []}
    fill_pct = total_cells / (GRID * GRID) * 100
    labels, n_comp = label_components(struct_mask)
    stats = component_stats(labels, n_comp)
    largest = stats[0]
    sizes = [st["size"] for st in stats]
    n_spanning = sum(1 for st in stats if st["spans"])
    return {
        "total_cells": total_cells,
        "fill_pct": round(fill_pct, 2),
        "n_components": n_comp,
        "largest_size": largest["size"],
        "largest_frac": round(largest["size"] / total_cells, 4),
        "largest_spans": largest["spans"],
        "largest_spans_x": largest["spans_x"],
        "largest_spans_y": largest["spans_y"],
        "n_spanning": n_spanning,
        "top5_sizes": sizes[:5],
    }


def run_combo(n_termites, g_form, g_persist, label, seeds, mode="dual"):
    if mode == "no_inhib":
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
            "late_mean_lc": round(s2.get("l2_late_mean_lc", 0.0), 2),
            "late_mean_rc": round(s2.get("l2_late_mean_rc", 0.0), 2),
            "b_max": round(max((b["b_max"] for b in r2["boundary_trace"]),
                              default=0.0), 2),
        }
        if "_final_material" in r2:
            mat = np.array(r2["_final_material"], dtype=np.float64)
            perc = percolation_analysis(mat)
            e2["perc"] = perc
            print(f"    2seed s={sd}: l2={s2['l2_crossed']} "
                  f"out={s2['l2_outcome']:>12s} stable={s2['l2_stable']} "
                  f"cf={e2['l2_coexist_frac']:.2f} "
                  f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']} "
                  f"fill={perc['fill_pct']:.1f}% ncomp={perc['n_components']} "
                  f"largest={perc['largest_size']} "
                  f"({perc['largest_frac']:.1%}) "
                  f"spans={perc['largest_spans']} "
                  f"b_max={e2['b_max']}")
        else:
            print(f"    2seed s={sd}: l2={s2['l2_crossed']} "
                  f"out={s2['l2_outcome']:>12s} stable={s2['l2_stable']} "
                  f"cf={e2['l2_coexist_frac']:.2f} "
                  f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']}")
        entries_2.append(e2)

        r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
        s1 = r1["summary"]
        e1 = {
            "seed": sd,
            "l2_crossed": s1["l2_crossed"],
            "l2_outcome": s1["l2_outcome"],
            "l2_stable": s1["l2_stable"],
            "l2_coexist_frac": round(s1.get("l2_coexist_frac", 0.0), 3),
            "crossed_h7": s1["crossed_h7"],
            "cells": s1["final_n_structure_cells"],
        }
        entries_1.append(e1)

    return entries_2, entries_1


def summarize(entries_2, entries_1, n_seeds):
    n = n_seeds
    n_l2_2 = sum(1 for e in entries_2 if e["l2_crossed"])
    n_coexist_2 = sum(1 for e in entries_2 if e["l2_outcome"] == "coexist")
    n_stable_2 = sum(1 for e in entries_2 if e["l2_stable"])
    n_h7_2 = sum(1 for e in entries_2 if e["crossed_h7"])
    n_l2_1 = sum(1 for e in entries_1 if e["l2_crossed"])
    n_h7_1 = sum(1 for e in entries_1 if e["crossed_h7"])
    n_stable_1 = sum(1 for e in entries_1 if e["l2_stable"])
    n_coexist_1 = sum(1 for e in entries_1 if e["l2_outcome"] == "coexist")
    clean = sum(1 for e2, e1 in zip(entries_2, entries_1)
                if e2["l2_outcome"] == "coexist"
                and e1["l2_outcome"] != "coexist")
    full = sum(1 for e2, e1 in zip(entries_2, entries_1)
               if e2["crossed_h7"]
               and e2["l2_outcome"] == "coexist"
               and e1["l2_outcome"] != "coexist"
               and e2["l2_stable"])
    mean_cells = int(np.mean([e["cells"] for e in entries_2]))
    mean_late_lc = float(np.mean([e["late_mean_lc"] for e in entries_2]))
    mean_late_rc = float(np.mean([e["late_mean_rc"] for e in entries_2]))
    mean_coexist_frac = float(np.mean([e["l2_coexist_frac"] for e in entries_2]))
    perc_entries = [e for e in entries_2 if "perc" in e]
    mean_fill = float(np.mean([e["perc"]["fill_pct"] for e in perc_entries])) if perc_entries else 0.0
    mean_ncomp = float(np.mean([e["perc"]["n_components"] for e in perc_entries])) if perc_entries else 0.0
    mean_largest = float(np.mean([e["perc"]["largest_size"] for e in perc_entries])) if perc_entries else 0.0
    mean_largest_frac = float(np.mean([e["perc"]["largest_frac"] for e in perc_entries])) if perc_entries else 0.0
    n_spanning = sum(1 for e in perc_entries if e["perc"]["largest_spans"])
    n_span_x = sum(1 for e in perc_entries if e["perc"]["largest_spans_x"])
    n_span_y = sum(1 for e in perc_entries if e["perc"]["largest_spans_y"])
    mean_b_max = float(np.mean([e["b_max"] for e in entries_2]))
    return {
        "l2_2s": f"{n_l2_2}/{n}",
        "coexist": f"{n_coexist_2}/{n}",
        "stable": f"{n_stable_2}/{n}",
        "h7_2s": f"{n_h7_2}/{n}",
        "clean": f"{clean}/{n}",
        "full": f"{full}/{n}",
        "l2_1s": f"{n_l2_1}/{n}",
        "h7_1s": f"{n_h7_1}/{n}",
        "stable_1s": f"{n_stable_1}/{n}",
        "coexist_1s": f"{n_coexist_1}/{n}",
        "mean_cells": mean_cells,
        "mean_late_lc": round(mean_late_lc, 2),
        "mean_late_rc": round(mean_late_rc, 2),
        "mean_coexist_frac": round(mean_coexist_frac, 3),
        "mean_fill_pct": round(mean_fill, 2),
        "mean_ncomp": round(mean_ncomp, 1),
        "mean_largest": round(mean_largest, 0),
        "mean_largest_frac": round(mean_largest_frac, 4),
        "n_spanning": f"{n_spanning}/{len(perc_entries)}",
        "n_span_x": f"{n_span_x}/{len(perc_entries)}",
        "n_span_y": f"{n_span_y}/{len(perc_entries)}",
        "mean_b_max": round(mean_b_max, 2),
    }


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "note": "Session 77: g* limit sweep — where does g* hit zero? (#216)",
        "question": "At what density does the boundary's effect vanish (g=0.001 ≡ g=0)?",
        "moore_percolation_threshold": "~0.407 (2D site, 8-neighbor)",
        "prior": {
            "n10000_g001": "fill ~75.25%",
            "n12000_g001": "fill ~94.44%",
            "n15000_g001": "fill ~99.93%",
            "n12000_g0": "fill 100%",
        },
    }}

    print(f"\n{'='*80}")
    print(f"  G* LIMIT SWEEP: n=11000-14000 at g=0.0005,0.001 × 4 seeds × {{2,1}}")
    print(f"  + no-inhibition controls at each n")
    print(f"{'='*80}")

    # Part 1: g* sweep
    for n, gf, gp, label in PLATEAU_COMBOS:
        density = n / (GRID * GRID) * 1000
        print(f"\n  {label} (n={n}, density={density:.2f}/kcell, g=({gf},{gp}))")
        e2, e1 = run_combo(n, gf, gp, label, SEEDS_4)
        results[label] = {
            "n_termites": n,
            "g_form": gf,
            "g_persist": gp,
            "density_per_kcell": round(density, 2),
            "hetero_2seed": e2,
            "hetero_1seed": e1,
            "summary": summarize(e2, e1, len(SEEDS_4)),
        }
        s = results[label]["summary"]
        print(f"  → l2={s['l2_2s']} coexist={s['coexist']} stable={s['stable']} "
              f"h7={s['h7_2s']} full={s['full']} "
              f"1s_l2={s['l2_1s']} 1s_h7={s['h7_1s']} "
              f"fill={s['mean_fill_pct']:.1f}% ncomp={s['mean_ncomp']:.0f} "
              f"largest={s['mean_largest']:.0f} ({s['mean_largest_frac']:.1%}) "
              f"b_max={s['mean_b_max']}")

        # Save incrementally
        os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
        with open(SWEEP_PATH, "w") as f:
            json.dump(S._pyify(results), f, indent=2)

    # Part 2: no-inhibition controls
    no_inhib_results = {}
    print(f"\n  NO-INHIBITION CONTROLS (g=0, 2-seed only)")
    for n, gf, gp, label in NO_INHIB_COMBOS:
        density = n / (GRID * GRID) * 1000
        print(f"\n  {label} (n={n})")
        e2, e1 = run_combo(n, gf, gp, label, SEEDS_4, mode="no_inhib")
        no_inhib_results[label] = {
            "n_termites": n,
            "g_form": gf,
            "g_persist": gp,
            "density_per_kcell": round(density, 2),
            "hetero_2seed": e2,
            "hetero_1seed": e1,
            "summary": summarize(e2, e1, len(SEEDS_4)),
        }
        s = no_inhib_results[label]["summary"]
        print(f"  → fill={s['mean_fill_pct']:.1f}% ncomp={s['mean_ncomp']:.0f} "
              f"largest={s['mean_largest']:.0f} ({s['mean_largest_frac']:.1%})")

    results["no_inhibition_control"] = no_inhib_results

    # Final save
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*130}")
    print("  G* LIMIT SWEEP SUMMARY (160x160, dual, focal 0.3, jit=10)")
    print(f"{'='*130}")
    print(f"{'label':>25s} {'nT':>5s} {'g':>7s} | "
          f"{'l2':>5s} {'coex':>5s} {'stab':>5s} {'h7':>5s} "
          f"{'full':>5s} {'cf':>5s} | "
          f"{'fill%':>5s} {'ncomp':>5s} {'largest':>7s} {'frac':>5s} "
          f"{'b_max':>6s} | "
          f"{'l2(1s)':>6s} {'h7(1s)':>6s}")
    print("-" * 130)

    for n, gf, gp, label in PLATEAU_COMBOS:
        if label not in results:
            continue
        s = results[label]["summary"]
        print(f"{label:>25s} {n:>5d} {gf:>7.4f} | "
              f"{s['l2_2s']:>5s} {s['coexist']:>5s} {s['stable']:>5s} "
              f"{s['h7_2s']:>5s} {s['full']:>5s} {s['mean_coexist_frac']:>5.2f} | "
              f"{s['mean_fill_pct']:>5.1f} {s['mean_ncomp']:>5.0f} "
              f"{s['mean_largest']:>7.0f} {s['mean_largest_frac']:>5.1%} "
              f"{s['mean_b_max']:>6.1f} | "
              f"{s['l2_1s']:>6s} {s['h7_1s']:>6s}")

    print(f"\n  NO-INHIBITION CONTROLS:")
    for n, gf, gp, label in NO_INHIB_COMBOS:
        if label not in no_inhib_results:
            continue
        s = no_inhib_results[label]["summary"]
        print(f"  {label:>25s}: fill={s['mean_fill_pct']:.1f}% "
              f"ncomp={s['mean_ncomp']:.0f} largest={s['mean_largest']:.0f} "
              f"({s['mean_largest_frac']:.1%})")

    # g* analysis
    print(f"\n  G* ANALYSIS:")
    print(f"  g* = highest gain where l2_crossed is True (composition alive)")
    for n_val in [11000, 12000, 13000, 14000]:
        l2_at_g001 = results.get(f"n{n_val}_g001", {}).get("summary", {}).get("l2_2s", "—")
        l2_at_g0005 = results.get(f"n{n_val}_g0005", {}).get("summary", {}).get("l2_2s", "—")
        fill_g001 = results.get(f"n{n_val}_g001", {}).get("summary", {}).get("mean_fill_pct", 0)
        fill_g0005 = results.get(f"n{n_val}_g0005", {}).get("summary", {}).get("mean_fill_pct", 0)
        fill_noinhib = no_inhib_results.get(f"n{n_val}_g000_no_inhib", {}).get("summary", {}).get("mean_fill_pct", 0)
        diff = fill_noinhib - fill_g001
        print(f"  n={n_val}: l2(g=0.001)={l2_at_g001} l2(g=0.0005)={l2_at_g0005} | "
              f"fill(g=0.001)={fill_g001:.1f}% fill(g=0.0005)={fill_g0005:.1f}% "
              f"fill(g=0)={fill_noinhib:.1f}% Δ={diff:.1f}%")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
