"""
8-seed robustness + asymmetric g_form/g_persist at n=220.

Session 48 found n=220 g=0.06 achieves 4/4 full co-occurrence (4 seeds) —
the first 4/4 full on 160x160. Two open questions:

  #136: Does the 4/4 full hold at 8 seeds?
  #139: Which B field drives the 4/4 full — is it g_form (formation) or
        g_persist (persistence)?

Part A (8-seed robustness, #136):
  n=220 g=0.06 at 8 seeds. If 4/4 holds at 8/8, the headline is robust.
  If it drops to ~4/8 (like n=200 g=0.14), it's a small-sample artifact.

Part B (asymmetric sweep, #139):
  4 configs at n=220, 4 seeds each:
  - symmetric (0.06, 0.06)  — the Session 48 headline
  - form-heavy (0.12, 0.06) — formation dominant
  - persist-heavy (0.06, 0.12) — persistence dominant
  - symmetric (0.12, 0.12)  — the other Session 48 4/4 full

  If form-heavy preserves 4/4 full and persist-heavy degrades, the formation
  field is load-bearing. If persist-heavy preserves and form-heavy degrades,
  persistence is load-bearing. If both degrade, symmetric is necessary.

Config: 160x160, dual mode, focal bias=0.3, per_step jitter=10.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "robustness_n220_sweep.json")

GRID = 160
JITTER = 10.0
N220 = 220

SEEDS_4 = [42, 123, 256, 999]
SEEDS_8 = [42, 123, 256, 999, 7, 100, 555, 777]

# Part A: 8-seed robustness at n=220 g=0.06
ROBUSTNESS_220 = ("n220_g006_8seed", N220, 0.06, 0.06, SEEDS_8)

# Part B: asymmetric sweep at n=220, 4 seeds
ASYM_COMBOS = [
    ("sym006", N220, 0.06, 0.06, SEEDS_4),
    ("form012", N220, 0.12, 0.06, SEEDS_4),
    ("persist012", N220, 0.06, 0.12, SEEDS_4),
    ("sym012", N220, 0.12, 0.12, SEEDS_4),
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


def run_combo(label, n_termites, g_form, g_persist, seeds):
    """Run a single (label, n, g_form, g_persist) combo across seeds."""
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
            "crossed_h7": s2["crossed_h7"],
            "cells": s2["final_n_structure_cells"],
            "left_retain": round(s2["l2_left_retain"], 4),
            "right_retain": round(s2["l2_right_retain"], 4),
            "b_max": round(max((b["b_max"] for b in r2["boundary_trace"]),
                              default=0.0), 2),
        }
        entries_2.append(e2)
        print(f"    2seed s={sd}: l2={s2['l2_crossed']} "
              f"out={s2['l2_outcome']:>12s} stable={s2['l2_stable']} "
              f"h7={s2['crossed_h7']} cells={s2['final_n_structure_cells']}")

        # 1-seed control
        r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero")
        s1 = r1["summary"]
        e1 = {
            "seed": sd,
            "l2_crossed": s1["l2_crossed"],
            "l2_outcome": s1["l2_outcome"],
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
    clean = sum(1 for e2, e1 in zip(entries_2, entries_1)
                if e2["l2_outcome"] == "coexist"
                and e1["l2_outcome"] != "coexist")
    full = sum(1 for e2, e1 in zip(entries_2, entries_1)
               if e2["crossed_h7"]
               and e2["l2_outcome"] == "coexist"
               and e1["l2_outcome"] != "coexist"
               and e2["l2_stable"])
    mean_cells = int(np.mean([e["cells"] for e in entries_2]))
    return {
        "l2_2s": f"{n_l2_2}/{n}",
        "coexist": f"{n_coexist_2}/{n}",
        "stable": f"{n_stable_2}/{n}",
        "h7_2s": f"{n_h7_2}/{n}",
        "clean": f"{clean}/{n}",
        "full": f"{full}/{n}",
        "l2_1s": f"{n_l2_1}/{n}",
        "h7_1s": f"{n_h7_1}/{n}",
        "mean_cells": mean_cells,
    }


def run_sweep():
    t0 = time.time()
    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "note": "Session 49: 8-seed robustness at n=220 g=0.06 (#136) + "
                "asymmetric g_form/g_persist at n=220 (#139)",
    }}

    # Part A: 8-seed robustness at n=220 g=0.06
    print(f"\n{'='*80}")
    print(f"  PART A: 8-seed robustness at n=220 g=0.06 (#136)")
    print(f"{'='*80}")
    label, n, gf, gp, seeds = ROBUSTNESS_220
    density = n / (GRID * GRID) * 1000
    print(f"  {label} (n={n}, density={density:.2f}/kcell, "
          f"g_form={gf}, g_persist={gp})")
    e2, e1 = run_combo(label, n, gf, gp, seeds)
    results[label] = {
        "g_form": gf,
        "g_persist": gp,
        "hetero_2seed": e2,
        "hetero_1seed": e1,
        "summary": summarize(e2, e1, len(seeds)),
    }
    s = results[label]["summary"]
    print(f"  -> l2={s['l2_2s']} coexist={s['coexist']} stable={s['stable']} "
          f"h7={s['h7_2s']} clean={s['clean']} full={s['full']} "
          f"1s_l2={s['l2_1s']} 1s_h7={s['h7_1s']} cells={s['mean_cells']}")

    # Part B: asymmetric sweep at n=220
    print(f"\n{'='*80}")
    print(f"  PART B: Asymmetric g_form/g_persist at n=220 (#139)")
    print(f"{'='*80}")
    for label, n, gf, gp, seeds in ASYM_COMBOS:
        density = n / (GRID * GRID) * 1000
        print(f"\n  {label} (n={n}, density={density:.2f}/kcell, "
              f"g_form={gf}, g_persist={gp})")
        e2, e1 = run_combo(label, n, gf, gp, seeds)
        results[label] = {
            "g_form": gf,
            "g_persist": gp,
            "hetero_2seed": e2,
            "hetero_1seed": e1,
            "summary": summarize(e2, e1, len(seeds)),
        }
        s = results[label]["summary"]
        print(f"  -> l2={s['l2_2s']} coexist={s['coexist']} "
              f"stable={s['stable']} h7={s['h7_2s']} "
              f"clean={s['clean']} full={s['full']} "
              f"1s_l2={s['l2_1s']} 1s_h7={s['h7_1s']} "
              f"cells={s['mean_cells']}")

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*100}")
    print("  ROBUSTNESS + ASYMMETRIC SWEEP SUMMARY "
          "(160x160, dual, focal 0.3, jit=10)")
    print(f"{'='*100}")
    print(f"{'label':>18s} {'nT':>5s} {'g_form':>7s} {'g_pers':>7s} | "
          f"{'l2':>5s} {'coex':>5s} {'stab':>5s} {'h7':>5s} "
          f"{'clean':>6s} {'full':>5s} | "
          f"{'l2(1s)':>6s} {'h7(1s)':>6s} {'cells':>6s}")
    print("-" * 100)

    all_combos = [ROBUSTNESS_220] + ASYM_COMBOS
    for label, n, gf, gp, seeds in all_combos:
        if label not in results:
            continue
        s = results[label]["summary"]
        density = n / (GRID * GRID) * 1000
        print(f"{label:>18s} {n:>5d} {gf:>7.2f} {gp:>7.2f} | "
              f"{s['l2_2s']:>5s} {s['coexist']:>5s} {s['stable']:>5s} "
              f"{s['h7_2s']:>5s} {s['clean']:>6s} {s['full']:>5s} | "
              f"{s['l2_1s']:>6s} {s['h7_1s']:>6s} {s['mean_cells']:>6d}")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
