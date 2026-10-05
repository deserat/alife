"""
n=10000+ plateau sweep — does the fill cap continue to rise above the
percolation threshold, and does the spanning cluster fraction converge to 1?

Queued-topics #207, #208, #209 (top priority from Session 74).

The fill cap at n=8000 is ~60.7% (above the 2D site percolation threshold
for Moore 8-connectivity, ~0.407). The stretched exponential fit
(fill% ≈ 26.7·exp(0.0089·√n), R²=0.964) predicts ~65% at n=10000.

Key insight: the 2D site percolation threshold for Moore (8-neighbor)
connectivity is ~0.407, NOT ~0.59 (that's von Neumann 4-neighbor). At
n=8000 (fill ~60%), we're well above the Moore threshold — yet the
bimodality (6/12 giant, 6/12 two-halves) shows some runs DON'T percolate.
The structure is spatially correlated (curvature-grown, not random), so
the boundary's spatial correlations prevent percolation even above the
random-site threshold. The bimodality is the boundary's effect, not
random percolation criticality.

Questions for n=10000 (~65% predicted fill):
1. Does the fill cap continue to rise? (44th mechanism, 9th density range)
2. Does g* stay positive? (43rd mechanism, 9th density range)
3. Does the spanning cluster fraction converge to 1? (#209)
4. Does the 30th mechanism persist? (stable 0/4 at all gains)
5. Does composition recover or collapse further?
6. Does the 1-seed structural guarantee recover or worsen?

The Haugen & Gilbert (2022, arXiv:2211.05653) coherence framework:
- Gompertz growth = coherent (long-range) interactions; θ → 0
- Logistic growth = pairwise (local) interactions; θ = 1
- The boundary's coherent suppression produces Gompertz-like fill cap
  below the percolation threshold; the departure from coherence at
  percolation is the Gompertz-to-logistic transition.
- At n=10000 (~65% fill), is the boundary's suppression still coherent
  (Gompertz) or has it broken down to logistic (pairwise)?

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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "n10000_plateau_sweep.json")

GRID = 160
JITTER = 10.0

SEEDS_4 = [42, 123, 256, 999]

# Part 1: n=10000 at gains 0.001, 0.003 (2 gains × 4 seeds × {2,1} = 16 runs)
PLATEAU_COMBOS = [
    (10000, 0.001,  0.001,  "n10000_g001"),
    (10000, 0.003,  0.003,  "n10000_g003"),
]

# Part 2: no-inhibition control at n=10000
NO_INHIB_COMBOS = [
    (10000, 0.0, 0.0, "n10000_g000_no_inhib"),
]


def make_params(n_termites, g_form, g_persist):
    """Build params for the sweep."""
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


# ---------------------------------------------------------------------------
# Percolation spanning analysis (from percolation_spanning.py)
# ---------------------------------------------------------------------------

def label_components(mask):
    """Label Moore-connected components (8-connectivity) via BFS."""
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
            "touches_top": touches_top,
            "touches_bottom": touches_bottom,
            "touches_left": touches_left,
            "touches_right": touches_right,
            "spans_x": spans_x, "spans_y": spans_y, "spans": spans,
        })
    stats.sort(key=lambda s: s["size"], reverse=True)
    return stats


def percolation_analysis(mat, struct_threshold=1.0):
    """Compute percolation spanning stats from a material field."""
    struct_mask = mat > struct_threshold
    total_cells = int(struct_mask.sum())
    if total_cells == 0:
        return {"total_cells": 0, "fill_pct": 0.0, "n_components": 0,
                "largest_size": 0, "largest_frac": 0.0,
                "spans": False, "spans_x": False, "spans_y": False,
                "top5_sizes": []}
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


# ---------------------------------------------------------------------------
# Combined plateau + spanning run
# ---------------------------------------------------------------------------

def run_combo(n_termites, g_form, g_persist, label, seeds, no_inhib=False):
    """Run a single combo across seeds, with percolation spanning analysis."""
    if no_inhib:
        p = make_no_inhib_params(n_termites)
    else:
        p = make_params(n_termites, g_form, g_persist)
    entries_2 = []
    entries_1 = []

    for sd in seeds:
        # 2-seed
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
            "left_retain": round(s2["l2_left_retain"], 4),
            "right_retain": round(s2["l2_right_retain"], 4),
            "late_mean_lc": round(s2.get("l2_late_mean_lc", 0.0), 2),
            "late_mean_rc": round(s2.get("l2_late_mean_rc", 0.0), 2),
            "b_max": round(max((b["b_max"] for b in r2["boundary_trace"]),
                              default=0.0), 2),
        }

        # Percolation spanning analysis on _final_material
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
                  f"span_x={perc['largest_spans_x']} "
                  f"span_y={perc['largest_spans_y']}")
        else:
            print(f"    2seed s={sd}: l2={s2['l2_crossed']} "
                  f"out={s2['l2_outcome']:>12s} stable={s2['l2_stable']} "
                  f"cf={e2['l2_coexist_frac']:.2f} "
                  f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']} "
                  f"(no _final_material)")
        entries_2.append(e2)

        # 1-seed control
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
    """Compute summary metrics."""
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

    # Percolation stats (from 2-seed runs)
    perc_entries = [e for e in entries_2 if "perc" in e]
    mean_fill = float(np.mean([e["perc"]["fill_pct"] for e in perc_entries])) if perc_entries else 0.0
    mean_ncomp = float(np.mean([e["perc"]["n_components"] for e in perc_entries])) if perc_entries else 0.0
    mean_largest = float(np.mean([e["perc"]["largest_size"] for e in perc_entries])) if perc_entries else 0.0
    mean_largest_frac = float(np.mean([e["perc"]["largest_frac"] for e in perc_entries])) if perc_entries else 0.0
    n_spanning = sum(1 for e in perc_entries if e["perc"]["largest_spans"])
    n_span_x = sum(1 for e in perc_entries if e["perc"]["largest_spans_x"])
    n_span_y = sum(1 for e in perc_entries if e["perc"]["largest_spans_y"])

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
    }


def run_plateau_sweep():
    """Part 1: n=10000 plateau sweep with percolation spanning."""
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "note": "Session 75: n=10000 plateau + percolation spanning (#207, #208, #209)",
        "stretched_exp_prediction": "fill% ≈ 26.7·exp(0.0089·√n) → ~65.1% at n=10000",
        "moore_percolation_threshold": "~0.407 (2D site, 8-neighbor)",
        "von_neumann_percolation_threshold": "~0.593 (2D site, 4-neighbor)",
        "mechanism_43": "1/sqrt(n) scaling is CONSERVATIVE — actual > predicted",
        "mechanism_44": "fill cap super-logarithmic (stretched exp R²=0.964); breaks at percolation",
        "mechanism_30": "stability-density trade-off — stable 0/4 at n>=3000 (all gains)",
        "mechanism_47": "bimodal largest-component fraction = percolation order parameter",
        "fill_cap_trajectory": {
            "n1200": "~38.3%", "n1500": "~39.4%", "n1800": "~40.4%",
            "n2000": "~41.2%", "n2500": "~42.1%", "n3000": "~43.6%",
            "n4000": "~45.8%", "n5000": "~48.0%", "n6000": "~50.6%",
            "n8000": "~60.7%",
        },
    }}

    print(f"\n{'='*80}")
    print(f"  N10000 PLATEAU: n=10000 at g=0.001-0.003 × 4 seeds × {{2,1}}")
    print(f"  + percolation spanning analysis on 2-seed runs")
    print(f"{'='*80}")

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
              f"h7={s['h7_2s']} clean={s['clean']} full={s['full']} "
              f"cf={s['mean_coexist_frac']:.3f} "
              f"1s_l2={s['l2_1s']} 1s_h7={s['h7_1s']} "
              f"cells={s['mean_cells']} fill={s['mean_fill_pct']:.1f}% "
              f"ncomp={s['mean_ncomp']:.0f} largest={s['mean_largest']:.0f} "
              f"({s['mean_largest_frac']:.1%}) "
              f"spans={s['n_spanning']} span_y={s['n_span_y']}")

    return results, time.time() - t0


def run_no_inhib_sweep():
    """Part 2: no-inhibition control at n=10000."""
    results = {"note": "Part 2: no-inhibition control — boundary necessity at n=10000"}

    print(f"\n{'='*80}")
    print(f"  NO-INHIBITION CONTROL: n=10000 at g=0 × 4 seeds × {{2,1}}")
    print(f"{'='*80}")

    for n, gf, gp, label in NO_INHIB_COMBOS:
        density = n / (GRID * GRID) * 1000
        print(f"\n  {label} (n={n}, density={density:.2f}/kcell, g=0)")
        e2, e1 = run_combo(n, gf, gp, label, SEEDS_4, no_inhib=True)
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
              f"h7={s['h7_2s']} cells={s['mean_cells']} fill={s['mean_fill_pct']:.1f}% "
              f"ncomp={s['mean_ncomp']:.0f} largest={s['mean_largest']:.0f} "
              f"({s['mean_largest_frac']:.1%}) spans={s['n_spanning']}")

    return results


def run_sweep():
    t0 = time.time()

    # Part 1: n=10000 plateau + percolation spanning
    plateau_results, plateau_time = run_plateau_sweep()

    # Part 2: no-inhibition control
    no_inhib_results = run_no_inhib_sweep()

    # Save
    all_results = {
        "plateau": plateau_results,
        "no_inhibition_control": no_inhib_results,
    }
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Summary table
    print(f"\n{'='*130}")
    print("  N10000 PLATEAU SWEEP SUMMARY (160x160, dual, focal 0.3, jit=10)")
    print(f"{'='*130}")
    print(f"{'label':>15s} {'nT':>5s} {'g':>7s} | "
          f"{'l2':>5s} {'coex':>5s} {'stab':>5s} {'h7':>5s} "
          f"{'full':>5s} {'cf':>5s} | "
          f"{'fill%':>5s} {'ncomp':>5s} {'largest':>7s} {'frac':>5s} "
          f"{'spans':>5s} {'span_y':>6s} | "
          f"{'l2(1s)':>6s} {'h7(1s)':>6s}")
    print("-" * 130)

    for n, gf, gp, label in PLATEAU_COMBOS:
        if label not in plateau_results:
            continue
        s = plateau_results[label]["summary"]
        print(f"{label:>15s} {n:>5d} {gf:>7.4f} | "
              f"{s['l2_2s']:>5s} {s['coexist']:>5s} {s['stable']:>5s} "
              f"{s['h7_2s']:>5s} {s['full']:>5s} {s['mean_coexist_frac']:>5.2f} | "
              f"{s['mean_fill_pct']:>5.1f} {s['mean_ncomp']:>5.0f} "
              f"{s['mean_largest']:>7.0f} {s['mean_largest_frac']:>5.1%} "
              f"{s['n_spanning']:>5s} {s['n_span_y']:>6s} | "
              f"{s['l2_1s']:>6s} {s['h7_1s']:>6s}")

    print(f"\n  NO-INHIBITION CONTROL:")
    for n, gf, gp, label in NO_INHIB_COMBOS:
        if label not in no_inhib_results:
            continue
        s = no_inhib_results[label]["summary"]
        print(f"  {label:>25s}: l2={s['l2_2s']} coexist={s['coexist']} "
              f"stable={s['stable']} h7={s['h7_2s']} "
              f"cells={s['mean_cells']} fill={s['mean_fill_pct']:.1f}% "
              f"ncomp={s['mean_ncomp']:.0f} largest={s['mean_largest']:.0f} "
              f"({s['mean_largest_frac']:.1%}) spans={s['n_spanning']}")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return all_results


if __name__ == "__main__":
    run_sweep()
