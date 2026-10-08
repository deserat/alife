"""
g* limit sweep — LEAN version (Session 77, #216)

2 seeds only, g=0.001 only, n=12000, 13000, 14000 + no-inhib at each.
The n=11000 g=0.001 data was already collected (4 seeds) by the full sweep.

Key question: at what n does fill at g=0.001 ≈ fill at g=0 (100%)?
If so, the boundary has no effect — g*=0.
"""

import os, sys, json, time
import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14
import sim09 as S

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "g_star_limit_sweep.json")
EXISTING = os.path.join(SIM14_DIR, "output", "g_star_limit_sweep.json")

GRID = 160
JITTER = 10.0
SEEDS = [42, 123]

COMBOS = [
    (12000, 0.001, 0.001, "n12000_g001"),
    (13000, 0.001, 0.001, "n13000_g001"),
    (14000, 0.001, 0.001, "n14000_g001"),
]

NO_INHIB = [
    (11000, "n11000_g000_no_inhib"),
    (12000, "n12000_g000_no_inhib"),
    (13000, "n13000_g000_no_inhib"),
    (14000, "n14000_g000_no_inhib"),
]


def make_params(n, gf, gp):
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID; p["n_termites"] = n
    p["boundary_mode"] = "dual"; p["g_form"] = gf; p["g_persist"] = gp
    p["b_decay_form"] = 0.01; p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1; p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3; p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER; p["jitter_mode"] = "per_step"
    return p


def make_no_inhib(n):
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID; p["n_termites"] = n
    p["movement_bias"] = 0.3; p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER; p["jitter_mode"] = "per_step"
    return p


def label_components(mask):
    visited = np.zeros_like(mask, dtype=bool)
    labels = np.zeros_like(mask, dtype=np.int32)
    rows, cols = mask.shape
    next_id = 0
    for r0 in range(rows):
        for c0 in range(cols):
            if mask[r0, c0] and not visited[r0, c0]:
                next_id += 1; visited[r0, c0] = True; labels[r0, c0] = next_id
                stack = [(r0, c0)]
                while stack:
                    r, c = stack.pop()
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0: continue
                            rr = (r + dr) % rows; cc = (c + dc) % cols
                            if mask[rr, cc] and not visited[rr, cc]:
                                visited[rr, cc] = True; labels[rr, cc] = next_id
                                stack.append((rr, cc))
    return labels, next_id


def percolation_analysis(mat, threshold=1.0):
    struct_mask = mat > threshold
    total = int(struct_mask.sum())
    if total == 0:
        return {"total_cells": 0, "fill_pct": 0.0, "n_components": 0,
                "largest_size": 0, "largest_frac": 0.0, "largest_spans": False,
                "largest_spans_x": False, "largest_spans_y": False, "n_spanning": 0}
    fill = total / (GRID * GRID) * 100
    labels, n_comp = label_components(struct_mask)
    stats = []
    for cid in range(1, n_comp + 1):
        m = labels == cid; size = int(m.sum())
        if size == 0: continue
        r0 = int(np.where(m.any(axis=1))[0][0])
        r1 = int(np.where(m.any(axis=1))[0][-1])
        c0 = int(np.where(m.any(axis=0))[0][0])
        c1 = int(np.where(m.any(axis=0))[0][-1])
        spans_x = bool(m[:, 0].any() and m[:, -1].any())
        spans_y = bool(m[0, :].any() and m[-1, :].any())
        stats.append({"size": size, "spans": spans_x or spans_y,
                      "spans_x": spans_x, "spans_y": spans_y})
    stats.sort(key=lambda s: s["size"], reverse=True)
    lg = stats[0]
    return {"total_cells": total, "fill_pct": round(fill, 2),
            "n_components": n_comp, "largest_size": lg["size"],
            "largest_frac": round(lg["size"] / total, 4),
            "largest_spans": lg["spans"], "largest_spans_x": lg["spans_x"],
            "largest_spans_y": lg["spans_y"], "n_spanning": sum(1 for s in stats if s["spans"])}


def run_combo(n, gf, gp, label, seeds):
    p = make_params(n, gf, gp)
    e2_list = []
    e1_list = []
    for sd in seeds:
        r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s2 = r2["summary"]
        e2 = {"seed": sd, "l2_crossed": s2["l2_crossed"], "l2_outcome": s2["l2_outcome"],
              "l2_stable": s2["l2_stable"], "l2_coexist_frac": round(s2.get("l2_coexist_frac", 0), 3),
              "crossed_h7": s2["crossed_h7"], "cells": s2["final_n_structure_cells"],
              "b_max": round(max((b["b_max"] for b in r2["boundary_trace"]), default=0), 2)}
        if "_final_material" in r2:
            mat = np.array(r2["_final_material"], dtype=np.float64)
            perc = percolation_analysis(mat)
            e2["perc"] = perc
            print(f"    s={sd}: l2={e2['l2_crossed']} h7={e2['crossed_h7']} "
                  f"fill={perc['fill_pct']:.1f}% ncomp={perc['n_components']} "
                  f"largest={perc['largest_size']} ({perc['largest_frac']:.1%}) "
                  f"b_max={e2['b_max']}")
        e2_list.append(e2)

        r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
        s1 = r1["summary"]
        e1_list.append({"seed": sd, "l2_crossed": s1["l2_crossed"],
                        "l2_outcome": s1["l2_outcome"], "l2_stable": s1["l2_stable"],
                        "crossed_h7": s1["crossed_h7"], "cells": s1["final_n_structure_cells"]})
    return e2_list, e1_list


def run_no_inhib(n, label, seeds):
    p = make_no_inhib(n)
    e2_list = []
    for sd in seeds:
        r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
        s2 = r2["summary"]
        e2 = {"seed": sd, "l2_crossed": s2["l2_crossed"], "crossed_h7": s2["crossed_h7"],
              "cells": s2["final_n_structure_cells"]}
        if "_final_material" in r2:
            mat = np.array(r2["_final_material"], dtype=np.float64)
            perc = percolation_analysis(mat)
            e2["perc"] = perc
            print(f"    s={sd}: fill={perc['fill_pct']:.1f}% ncomp={perc['n_components']} "
                  f"largest={perc['largest_size']} ({perc['largest_frac']:.1%})")
        e2_list.append(e2)
    return e2_list


def summarize(e2_list, e1_list):
    n = len(e2_list)
    perc_entries = [e for e in e2_list if "perc" in e]
    mean_fill = float(np.mean([e["perc"]["fill_pct"] for e in perc_entries])) if perc_entries else 0
    mean_ncomp = float(np.mean([e["perc"]["n_components"] for e in perc_entries])) if perc_entries else 0
    mean_largest = float(np.mean([e["perc"]["largest_size"] for e in perc_entries])) if perc_entries else 0
    mean_lfrac = float(np.mean([e["perc"]["largest_frac"] for e in perc_entries])) if perc_entries else 0
    n_span = sum(1 for e in perc_entries if e["perc"]["largest_spans"])
    return {
        "l2_2s": f"{sum(1 for e in e2_list if e['l2_crossed'])}/{n}",
        "coexist": f"{sum(1 for e in e2_list if e['l2_outcome']=='coexist')}/{n}",
        "stable": f"{sum(1 for e in e2_list if e['l2_stable'])}/{n}",
        "h7_2s": f"{sum(1 for e in e2_list if e['crossed_h7'])}/{n}",
        "l2_1s": f"{sum(1 for e in e1_list if e['l2_crossed'])}/{n}",
        "h7_1s": f"{sum(1 for e in e1_list if e['crossed_h7'])}/{n}",
        "mean_fill_pct": round(mean_fill, 2),
        "mean_ncomp": round(mean_ncomp, 1),
        "mean_largest": round(mean_largest, 0),
        "mean_largest_frac": round(mean_lfrac, 4),
        "n_spanning": f"{n_span}/{len(perc_entries)}",
        "mean_b_max": round(float(np.mean([e["b_max"] for e in e2_list])), 2),
    }


def main():
    t0 = time.time()

    # Load existing data (n11000_g001 from full sweep)
    existing = {}
    if os.path.exists(EXISTING):
        with open(EXISTING) as f:
            existing = json.load(f)

    results = {"config": {
        "grid": GRID, "jitter": JITTER,
        "note": "Session 77: g* limit sweep — where does g* hit zero? (#216)",
        "question": "At what n does fill at g=0.001 ≈ fill at g=0 (100%)?",
        "moore_percolation_threshold": "~0.407 (2D site, 8-neighbor)",
        "n11000_g001_note": "4 seeds from full sweep; n=12000-14000 are 2 seeds (lean)",
    }}

    # Keep n11000_g001 (4-seed) from existing data
    if "n11000_g001" in existing:
        results["n11000_g001"] = existing["n11000_g001"]
        s = results["n11000_g001"]["summary"]
        print(f"  n11000_g001 (existing, 4 seeds): fill={s['mean_fill_pct']}% "
              f"h7={s['h7_2s']} l2={s['l2_2s']}")

    print(f"\n{'='*80}")
    print(f"  G* LIMIT SWEEP (LEAN): n=12000-14000 at g=0.001 × 2 seeds × {{2,1}}")
    print(f"  + no-inhibition controls at each n")
    print(f"{'='*80}")

    for n, gf, gp, label in COMBOS:
        density = n / (GRID * GRID) * 1000
        print(f"\n  {label} (n={n}, density={density:.2f}/kcell)")
        e2, e1 = run_combo(n, gf, gp, label, SEEDS)
        results[label] = {
            "n_termites": n, "g_form": gf, "g_persist": gp,
            "density_per_kcell": round(density, 2),
            "hetero_2seed": e2, "hetero_1seed": e1,
            "summary": summarize(e2, e1),
        }
        s = results[label]["summary"]
        print(f"  → fill={s['mean_fill_pct']}% h7={s['h7_2s']} l2={s['l2_2s']} "
              f"ncomp={s['mean_ncomp']:.0f} largest={s['mean_largest']:.0f} "
              f"({s['mean_largest_frac']:.1%}) b_max={s['mean_b_max']}")

        os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
        with open(SWEEP_PATH, "w") as f:
            json.dump(S._pyify(results), f, indent=2)

    # No-inhibition controls
    no_inhib = {}
    print(f"\n  NO-INHIBITION CONTROLS (g=0, 2-seed)")
    for n, label in NO_INHIB:
        print(f"\n  {label} (n={n})")
        e2 = run_no_inhib(n, label, SEEDS)
        perc_entries = [e for e in e2 if "perc" in e]
        mean_fill = float(np.mean([e["perc"]["fill_pct"] for e in perc_entries])) if perc_entries else 0
        mean_ncomp = float(np.mean([e["perc"]["n_components"] for e in perc_entries])) if perc_entries else 0
        mean_largest = float(np.mean([e["perc"]["largest_size"] for e in perc_entries])) if perc_entries else 0
        mean_lfrac = float(np.mean([e["perc"]["largest_frac"] for e in perc_entries])) if perc_entries else 0
        no_inhib[label] = {
            "n_termites": n, "g_form": 0.0, "g_persist": 0.0,
            "density_per_kcell": round(n / (GRID * GRID) * 1000, 2),
            "hetero_2seed": e2,
            "summary": {
                "mean_fill_pct": round(mean_fill, 2),
                "mean_ncomp": round(mean_ncomp, 1),
                "mean_largest": round(mean_largest, 0),
                "mean_largest_frac": round(mean_lfrac, 4),
                "n_spanning": f"{sum(1 for e in perc_entries if e['perc']['largest_spans'])}/{len(perc_entries)}",
            },
        }
        print(f"  → fill={mean_fill:.1f}% ncomp={mean_ncomp:.0f} largest={mean_largest:.0f} ({mean_lfrac:.1%})")

    results["no_inhibition_control"] = no_inhib
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary
    print(f"\n{'='*100}")
    print("  G* LIMIT SWEEP SUMMARY")
    print(f"{'='*100}")
    print(f"{'label':>25s} {'nT':>5s} {'g':>7s} | {'fill%':>5s} {'ncomp':>5s} {'largest':>7s} {'frac':>5s} {'b_max':>6s} | {'l2':>4s} {'h7':>4s} | {'noinhib_fill':>12s} {'Δ':>5s}")
    print("-" * 100)

    all_labels = ["n11000_g001", "n12000_g001", "n13000_g001", "n14000_g001"]
    for label in all_labels:
        entry = results.get(label)
        if not entry or "summary" not in entry:
            continue
        s = entry["summary"]
        n = entry["n_termites"]
        no_inhib_label = f"n{n}_g000_no_inhib"
        no_inhib_entry = no_inhib.get(no_inhib_label, {})
        no_inhib_fill = no_inhib_entry.get("summary", {}).get("mean_fill_pct", 100.0)
        diff = no_inhib_fill - s["mean_fill_pct"]
        print(f"{label:>25s} {n:>5d} {entry['g_form']:>7.4f} | "
              f"{s['mean_fill_pct']:>5.1f} {s['mean_ncomp']:>5.0f} "
              f"{s['mean_largest']:>7.0f} {s['mean_largest_frac']:>5.1%} "
              f"{s.get('mean_b_max', 0):>6.1f} | "
              f"{s['l2_2s']:>4s} {s['h7_2s']:>4s} | "
              f"{no_inhib_fill:>12.1f} {diff:>+5.1f}")

    # g* analysis
    print(f"\n  G* ANALYSIS:")
    print(f"  The boundary's effect = gap between g=0.001 fill and g=0 (no-inhib) fill.")
    print(f"  g*=0 when the gap = 0 (boundary has no effect on fill).")
    for label in all_labels:
        entry = results.get(label)
        if not entry or "summary" not in entry:
            continue
        n = entry["n_termites"]
        s = entry["summary"]
        no_inhib_label = f"n{n}_g000_no_inhib"
        no_inhib_fill = no_inhib.get(no_inhib_label, {}).get("summary", {}).get("mean_fill_pct", 100.0)
        gap = no_inhib_fill - s["mean_fill_pct"]
        print(f"  n={n}: fill(g=0.001)={s['mean_fill_pct']:.1f}% fill(g=0)={no_inhib_fill:.1f}% gap={gap:.1f}% — {'boundary irrelevant' if gap < 1 else 'boundary has effect' if gap > 5 else 'boundary weakening'}")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    main()
