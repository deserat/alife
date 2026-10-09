"""
30th mechanism permanence — does persistence recover at g=0.0001 at n=3000? (#217, revised)

The original plan tested n=12000 but runs at n=12000 take ~5-10 min each,
exceeding the compute budget. Revised: test at n=3000 (~44% fill) where the
30th mechanism first collapses (Session 71: stable 0/4 at ALL gains at n=3000).

At n=3000, runs take ~1-2 min. 3 gains × 2 seeds × {2,1} + 2 no-inhib = 14 runs,
~20-30 min total.

If stable=0/4 at g=0.0001 at n=3000: the 30th mechanism is truly permanent —
the boundary cannot maintain stable composition at the density where it first
collapsed, regardless of how weak the gain is.
If stable>0/4: the 30th mechanism is gain-dependent, not permanent — very low
gain avoids over-splitting the structure.
"""

import os, sys, json, time
import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14
import sim09 as S

OUT_PATH = os.path.join(SIM14_DIR, "output", "thirtieth_permanence.json")

GRID = 160
JITTER = 10.0
SEEDS = [42, 123]
N_TERMITES = 3000


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
                "largest_size": 0, "largest_frac": 0.0}
    fill = total / (GRID * GRID) * 100
    labels, n_comp = label_components(struct_mask)
    sizes = [int((labels == cid).sum()) for cid in range(1, n_comp + 1)]
    sizes.sort(reverse=True)
    lg = sizes[0] if sizes else 0
    return {"total_cells": total, "fill_pct": round(fill, 2),
            "n_components": n_comp, "largest_size": lg,
            "largest_frac": round(lg / total, 4)}


COMBOS = [
    (N_TERMITES, 0.0001, 0.0001, "g0001"),
    (N_TERMITES, 0.0005, 0.0005, "g0005"),
    (N_TERMITES, 0.001, 0.001, "g001"),
]


def main():
    t0 = time.time()

    results = {"config": {
        "grid": GRID, "n_termites": N_TERMITES, "jitter": JITTER,
        "seeds": SEEDS,
        "note": "Session 78: 30th mechanism permanence — does g=0.0001 rescue stability at n=3000? (#217 revised)",
        "question": "Is the 30th mechanism (stability-density trade-off) truly permanent, or gain-dependent?",
        "fill_at_n3000": "~44%",
        "n3000_session71": "stable 0/4 at ALL gains (g=0.001, 0.003, 0.005)",
    }}

    for n, gf, gp, label in COMBOS:
        density = n / (GRID * GRID) * 1000
        print(f"\n  {label} (n={n}, g={gf}, density={density:.2f}/kcell)")
        p = make_params(n, gf, gp)
        e2_list = []
        e1_list = []
        for sd in SEEDS:
            r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero")
            s2 = r2["summary"]
            e2 = {
                "seed": sd,
                "l2_crossed": s2["l2_crossed"],
                "l2_outcome": s2["l2_outcome"],
                "l2_stable": s2["l2_stable"],
                "l2_coexist_frac": round(s2.get("l2_coexist_frac", 0), 3),
                "crossed_h7": s2["crossed_h7"],
                "cells": s2["final_n_structure_cells"],
                "b_max": round(max((b["b_max"] for b in r2["boundary_trace"]), default=0), 2),
            }
            if "_final_material" in r2:
                mat = np.array(r2["_final_material"], dtype=np.float64)
                perc = percolation_analysis(mat)
                e2["perc"] = perc
            print(f"    s={sd}: l2={e2['l2_crossed']} h7={e2['crossed_h7']} "
                  f"stable={e2['l2_stable']} coexist_frac={e2['l2_coexist_frac']} "
                  f"fill={e2.get('perc', {}).get('fill_pct', '?')}% "
                  f"ncomp={e2.get('perc', {}).get('n_components', '?')} "
                  f"b_max={e2['b_max']}")
            e2_list.append(e2)

            r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
            s1 = r1["summary"]
            e1_list.append({
                "seed": sd,
                "l2_crossed": s1["l2_crossed"],
                "l2_outcome": s1["l2_outcome"],
                "l2_stable": s1["l2_stable"],
                "crossed_h7": s1["crossed_h7"],
                "cells": s1["final_n_structure_cells"],
            })

        ns = len(e2_list)
        summary = {
            "l2_2s": f"{sum(1 for e in e2_list if e['l2_crossed'])}/{ns}",
            "coexist": f"{sum(1 for e in e2_list if e['l2_outcome']=='coexist')}/{ns}",
            "stable": f"{sum(1 for e in e2_list if e['l2_stable'])}/{ns}",
            "h7_2s": f"{sum(1 for e in e2_list if e['crossed_h7'])}/{ns}",
            "l2_1s": f"{sum(1 for e in e1_list if e['l2_crossed'])}/{ns}",
            "h7_1s": f"{sum(1 for e in e1_list if e['crossed_h7'])}/{ns}",
            "mean_b_max": round(float(np.mean([e["b_max"] for e in e2_list])), 2),
            "hetero_2seed": e2_list,
            "hetero_1seed": e1_list,
        }
        perc_entries = [e for e in e2_list if "perc" in e]
        if perc_entries:
            summary["mean_fill_pct"] = round(float(np.mean([e["perc"]["fill_pct"] for e in perc_entries])), 2)
            summary["mean_ncomp"] = round(float(np.mean([e["perc"]["n_components"] for e in perc_entries])), 1)

        results[label] = {
            "n_termites": n, "g_form": gf, "g_persist": gp,
            "density_per_kcell": round(density, 2),
            "summary": summary,
        }
        s = summary
        print(f"  → stable={s['stable']} h7={s['h7_2s']} l2={s['l2_2s']} "
              f"fill={s.get('mean_fill_pct', '?')}% ncomp={s.get('mean_ncomp', '?')} "
              f"b_max={s['mean_b_max']}")

        # Save after each combo (in case of timeout)
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "w") as f:
            json.dump(S._pyify(results), f, indent=2)

    # No-inhibition control at n=3000
    print(f"\n  no_inhib (n={N_TERMITES}, g=0)")
    p_noi = make_no_inhib(N_TERMITES)
    noi_list = []
    for sd in SEEDS:
        r2 = I14.run_two_region_hetero(p_noi, seed=sd, n_seeds=2, mode="hetero")
        s2 = r2["summary"]
        e2 = {"seed": sd, "l2_crossed": s2["l2_crossed"],
              "crossed_h7": s2["crossed_h7"],
              "cells": s2["final_n_structure_cells"]}
        if "_final_material" in r2:
            mat = np.array(r2["_final_material"], dtype=np.float64)
            perc = percolation_analysis(mat)
            e2["perc"] = perc
            print(f"    s={sd}: fill={perc['fill_pct']:.1f}% ncomp={perc['n_components']} "
                  f"largest={perc['largest_size']} ({perc['largest_frac']:.1%})")
        noi_list.append(e2)

    perc_entries = [e for e in noi_list if "perc" in e]
    results["no_inhibition"] = {
        "n_termites": N_TERMITES, "g_form": 0.0, "g_persist": 0.0,
        "summary": {
            "mean_fill_pct": round(float(np.mean([e["perc"]["fill_pct"] for e in perc_entries])), 2) if perc_entries else 100.0,
            "mean_ncomp": round(float(np.mean([e["perc"]["n_components"] for e in perc_entries])), 1) if perc_entries else 1,
            "hetero_2seed": noi_list,
        }
    }

    with open(OUT_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*90}")
    print("  30TH MECHANISM PERMANENCE — n=3000 (~44% fill)")
    print(f"{'='*90}")
    print(f"{'label':>10s} {'g':>8s} | {'stable':>7s} {'h7':>5s} {'l2':>5s} {'fill%':>6s} {'ncomp':>6s} {'b_max':>7s}")
    print("-" * 90)
    for label in ["g0001", "g0005", "g001"]:
        if label not in results: continue
        s = results[label]["summary"]
        print(f"{label:>10s} {results[label]['g_form']:>8.5f} | "
              f"{s['stable']:>7s} {s['h7_2s']:>5s} {s['l2_2s']:>5s} "
              f"{str(s.get('mean_fill_pct', '?')):>6s} {str(s.get('mean_ncomp', '?')):>6s} "
              f"{s['mean_b_max']:>7.1f}")
    noi = results["no_inhibition"]["summary"]
    print(f"{'no_inhib':>10s} {'0.00000':>8s} | "
          f"{'—':>7s} {'—':>5s} {'—':>5s} "
          f"{noi['mean_fill_pct']:>6.1f} {noi['mean_ncomp']:>6.0f} {'—':>7s}")

    print(f"\n  VERDICT:")
    g0001_stable = results["g0001"]["summary"]["stable"]
    if g0001_stable == "0/2":
        print(f"  g=0.0001: stable={g0001_stable} → 30th mechanism is TRULY PERMANENT")
        print(f"  The boundary cannot maintain stable composition at n=3000 (~44% fill)")
        print(f"  at ANY gain tested (g=0.0001–0.005). The persistence condition has collapsed.")
    else:
        print(f"  g=0.0001: stable={g0001_stable} → 30th mechanism is GAIN-DEPENDENT")
        print(f"  The very low gain avoids over-splitting the large structure.")

    elapsed = time.time() - t0
    print(f"\nWrote {OUT_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    main()
