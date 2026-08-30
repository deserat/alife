"""
Analysis script for queued-topics #124 and #125.

#124: At n=150, coexist=4/4 but H7=2/4. Which H7 criterion fails, and by how
much? Is the crossing necessary for composition, or does the boundary +
ID-tagging suffice?

#125: At n=175, H7=4/4 but coexist=1/4. Are structures merging (too big for
the midline) or fragmenting (boundary too weak relative to growth)?

This script re-runs n=150 and n=175 (4 seeds each, 2-seed + 1-seed) with the
same config as threshold_sweep.py, but captures per-step H7 criteria values
and per-region component counts to diagnose WHY H7 fires/fails and WHY
composition degrades.

Output: output/criteria_analysis.json
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

ANALYSIS_PATH = os.path.join(SIM14_DIR, "output", "criteria_analysis.json")

GRID = 160
JITTER = 10.0
SEEDS = [42, 123, 256, 999]
N_LIST = [150, 175]

# H7 thresholds (from sim09.py constants)
STAB_THRESH = S.STAB_THRESH            # 0.90
ROUGH_THRESH = S.ROUGH_ELEV_THRESH      # 0.02
CONSTRAIN_THRESH = S.CONSTRAIN_THRESH    # 0.60
PLATEAU_REL = S.MASS_PLATEAU_REL        # 0.001
PLATEAU_WINDOW = S.MASS_PLATEAU_WINDOW  # 16
CROSSING_PERSIST = S.CROSSING_PERSIST    # 4


def run_criteria_analysis(params, seed, n_seeds=2):
    """Run a two-region hetero simulation and return per-step criteria +
    per-region component counts for the late window."""
    r = I14.run_two_region_hetero(params, seed=seed, n_seeds=n_seeds, mode="hetero")
    history = r["history"]
    summary = r["summary"]

    # Extract late-window records (same fraction as detect_l2)
    late_frac = 0.25  # default L2_LATE_WINDOW_FRAC
    n_late = max(1, int(len(history) * late_frac))
    late = history[-n_late:]

    # Per-step criteria in the late window
    per_step = []
    for rec in late:
        stab = rec.get("structure_stability", 0.0)
        rough = rec.get("roughness", 0.0)
        mp = rec.get("mass_plateau")
        dep_convex = rec.get("deposits_on_convex_fraction", 0.0)
        lc = rec.get("left_components", 0)
        rc = rec.get("right_components", 0)
        lt = rec.get("left_total", 0.0)
        rt = rec.get("right_total", 0.0)
        total = rec.get("total_material", 0.0)
        cells = rec.get("n_structure_cells", 0)

        c1 = stab >= STAB_THRESH
        c2 = (mp is not None) and (mp < PLATEAU_REL) and (rough >= ROUGH_THRESH)
        c3 = dep_convex >= CONSTRAIN_THRESH

        per_step.append({
            "step": rec["step"],
            "stab": round(stab, 4),
            "c1": c1,
            "rough": round(rough, 6),
            "mass_plateau": round(mp, 6) if mp is not None else None,
            "c2": c2,
            "dep_convex": round(dep_convex, 4),
            "c3": c3,
            "left_comp": lc,
            "right_comp": rc,
            "left_total": round(lt, 1),
            "right_total": round(rt, 1),
            "total": round(total, 1),
            "cells": cells,
        })

    # Summarize: which criteria fail most often in the late window?
    n_late_actual = len(per_step)
    c1_pass = sum(1 for s in per_step if s["c1"])
    c2_pass = sum(1 for s in per_step if s["c2"])
    c3_pass = sum(1 for s in per_step if s["c3"])
    all3_pass = sum(1 for s in per_step if s["c1"] and s["c2"] and s["c3"])

    # The max consecutive run of all-3-passing
    max_run = 0
    cur_run = 0
    for s in per_step:
        if s["c1"] and s["c2"] and s["c3"]:
            cur_run += 1
            max_run = max(max_run, cur_run)
        else:
            cur_run = 0

    # Late-window mean stability (to see how close to threshold)
    mean_stab = float(np.mean([s["stab"] for s in per_step]))
    min_stab = float(np.min([s["stab"] for s in per_step]))
    max_stab = float(np.max([s["stab"] for s in per_step]))

    # Late-window mean roughness
    mean_rough = float(np.mean([s["rough"] for s in per_step]))

    # Late-window mean mass_plateau (excluding None)
    mps = [s["mass_plateau"] for s in per_step if s["mass_plateau"] is not None]
    mean_mp = float(np.mean(mps)) if mps else None

    # Late-window mean dep_convex
    mean_dc = float(np.mean([s["dep_convex"] for s in per_step]))

    # Component count stats
    mean_lc = float(np.mean([s["left_comp"] for s in per_step]))
    mean_rc = float(np.mean([s["right_comp"] for s in per_step]))
    max_lc = max(s["left_comp"] for s in per_step)
    max_rc = max(s["right_comp"] for s in per_step)

    # Per-region retention
    left_peak = max(r2.get("left_total", 0.0) for r2 in history)
    right_peak = max(r2.get("right_total", 0.0) for r2 in history)
    final_lt = late[-1].get("left_total", 0.0)
    final_rt = late[-1].get("right_total", 0.0)
    left_retain = final_lt / max(left_peak, 1e-9)
    right_retain = final_rt / max(right_peak, 1e-9)

    # L2 outcome
    l2_outcome = summary["l2_outcome"]
    l2_crossed = summary["l2_crossed"]
    l2_stable = summary["l2_stable"]
    crossed_h7 = summary["crossed_h7"]

    return {
        "seed": seed,
        "n_seeds": n_seeds,
        "l2_outcome": l2_outcome,
        "l2_crossed": l2_crossed,
        "l2_stable": l2_stable,
        "crossed_h7": crossed_h7,
        "cells": summary["final_n_structure_cells"],
        "left_retain": round(left_retain, 4),
        "right_retain": round(right_retain, 4),
        # H7 per-criterion pass rates (late window)
        "c1_pass": f"{c1_pass}/{n_late_actual}",
        "c2_pass": f"{c2_pass}/{n_late_actual}",
        "c3_pass": f"{c3_pass}/{n_late_actual}",
        "all3_pass": f"{all3_pass}/{n_late_actual}",
        "max_consec_all3": max_run,
        "crossing_persist_needed": CROSSING_PERSIST,
        # Stability stats
        "mean_stab": round(mean_stab, 4),
        "min_stab": round(min_stab, 4),
        "max_stab": round(max_stab, 4),
        "stab_thresh": STAB_THRESH,
        # Roughness stats
        "mean_rough": round(mean_rough, 6),
        "rough_thresh": ROUGH_THRESH,
        # Mass plateau stats
        "mean_mp": round(mean_mp, 6) if mean_mp is not None else None,
        "mp_thresh": PLATEAU_REL,
        # Deposit convex fraction
        "mean_dep_convex": round(mean_dc, 4),
        "dep_convex_thresh": CONSTRAIN_THRESH,
        # Component stats
        "mean_lc": round(mean_lc, 2),
        "mean_rc": round(mean_rc, 2),
        "max_lc": max_lc,
        "max_rc": max_rc,
        # Per-step detail (last 10 steps)
        "late_detail": per_step[-10:],
    }


def run_sweep():
    t0 = time.time()
    results = {
        "config": {
            "grid": GRID,
            "jitter": JITTER,
            "seeds": SEEDS,
            "n_list": N_LIST,
            "boundary_mode": "dual",
            "g_form": 0.3,
            "g_persist": 0.3,
            "movement_bias": 0.3,
            "movement_mode": "focal",
            "jitter_mode": "per_step",
            "h7_thresholds": {
                "stab": STAB_THRESH,
                "rough": ROUGH_THRESH,
                "constrain": CONSTRAIN_THRESH,
                "plateau_rel": PLATEAU_REL,
                "plateau_window": PLATEAU_WINDOW,
                "crossing_persist": CROSSING_PERSIST,
            },
        },
        "note": "Session 44: per-criteria analysis for #124 (n=150) and #125 (n=175)",
    }

    for nt in N_LIST:
        density = nt / (GRID * GRID) * 1000
        key = f"n{nt}"
        results[key] = {"2seed": [], "1seed": []}
        print(f"\n{'='*70}")
        print(f"  n={nt} (density={density:.2f}/kcell)")
        print(f"{'='*70}")

        for nt_actual in [nt]:
            p = I14.curvature_params(0.5)
            p["grid_size"] = GRID
            p["n_termites"] = nt_actual
            p["boundary_mode"] = "dual"
            p["g_form"] = 0.3
            p["g_persist"] = 0.3
            p["b_decay_form"] = 0.01
            p["b_decay_persist"] = 0.005
            p["b_growth_form"] = 0.1
            p["b_growth_persist"] = 0.1
            p["movement_bias"] = 0.3
            p["movement_mode"] = "focal"
            p["home_jitter"] = JITTER
            p["jitter_mode"] = "per_step"

            for sd in SEEDS:
                # 2-seed
                a = run_criteria_analysis(p, sd, n_seeds=2)
                results[key]["2seed"].append(a)
                print(f"  2s s={sd}: h7={a['crossed_h7']} "
                      f"l2={a['l2_crossed']} outcome={a['l2_outcome']:12s} "
                      f"stable={a['l2_stable']}")
                print(f"    c1={a['c1_pass']} c2={a['c2_pass']} c3={a['c3_pass']} "
                      f"max_run={a['max_consec_all3']}")
                print(f"    stab={a['mean_stab']:.4f} (min={a['min_stab']:.4f}, "
                      f"thresh={STAB_THRESH}) rough={a['mean_rough']:.6f} "
                      f"(thresh={ROUGH_THRESH})")
                print(f"    dep_convex={a['mean_dep_convex']:.4f} "
                      f"(thresh={CONSTRAIN_THRESH}) mp={a['mean_mp']}")
                print(f"    comps: lc={a['mean_lc']:.1f} rc={a['mean_rc']:.1f} "
                      f"max_lc={a['max_lc']} max_rc={a['max_rc']}")

                # 1-seed
                b = run_criteria_analysis(p, sd, n_seeds=1)
                results[key]["1seed"].append(b)

    os.makedirs(os.path.dirname(ANALYSIS_PATH), exist_ok=True)
    with open(ANALYSIS_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    elapsed = time.time() - t0
    print(f"\n{'='*70}")
    print(f"  ANALYSIS COMPLETE ({elapsed:.1f}s)")
    print(f"  Wrote {ANALYSIS_PATH}")
    print(f"{'='*70}")

    # Print summary table
    print(f"\n{'='*100}")
    print(f"  SUMMARY: Per-criteria H7 pass rates (late window)")
    print(f"{'='*100}")
    print(f"{'nT':>5s} {'seed':>5s} | {'h7':>5s} {'l2':>5s} {'outcome':>12s} "
          f"| {'c1':>7s} {'c2':>7s} {'c3':>7s} {'max_run':>8s} "
          f"| {'stab':>8s} {'rough':>8s} {'dep_cx':>8s} "
          f"| {'lc':>5s} {'rc':>5s}")
    print("-" * 100)

    for nt in N_LIST:
        key = f"n{nt}"
        for a in results[key]["2seed"]:
            print(f"{nt:>5d} {a['seed']:>5d} | {str(a['crossed_h7']):>5s} "
                  f"{str(a['l2_crossed']):>5s} {a['l2_outcome']:>12s} "
                  f"| {a['c1_pass']:>7s} {a['c2_pass']:>7s} {a['c3_pass']:>7s} "
                  f"{a['max_consec_all3']:>8d} "
                  f"| {a['mean_stab']:>8.4f} {a['mean_rough']:>8.6f} "
                  f"{a['mean_dep_convex']:>8.4f} "
                  f"| {a['mean_lc']:>5.1f} {a['mean_rc']:>5.1f}")
        print()

    return results


if __name__ == "__main__":
    run_sweep()
