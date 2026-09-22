"""
Bilateral damage at other densities — does the bilateral advantage scale?

Queued-topic #175:
  Bilateral 50% at n=350 (g=0.01) produces cf=0.825 — the highest
  composition quality ever. Does the bilateral advantage hold at:
  - n=150 (lower density, smaller structures, g≈0.30)?
  - n=500 (higher density, larger structures, g=0.02)?

  At n=150, bilateral damage may not create enough curvature contrast
  (smaller structures → smaller scars).
  At n=500, bilateral damage may over-split (larger structures → more
  surface area for the boundary to fragment).

  Uses the density-appropriate gain from the 1/√n scaling law
  (Session 46/48/53):
    n=150: g ≈ 0.30   (from g*(n) = -0.95 + 15.2/√n)
    n=350: g = 0.01   (the robust optimum, Session 54)
    n=500: g = 0.02   (Session 53)

Design:
  3 densities × 4 seeds × {bilateral 50/50 perturbed, unperturbed}
  × {2, 1} seeds = 48 runs + 24 baseline = 72 runs

  160×160 grid, dual mode, focal bias 0.3, jitter 10
  perturb_at=1200 (60% of 2000 steps), iter_shuffle=True
  bilateral 50/50 = perturb_side="both", perturb_frac=0.50

Control arm: unperturbed runs at the same configs.
Per-criterion pass rates are reported for every null.
Determinism verified by running twice and diffing.
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

OUTPUT_DIR = os.path.join(SIM14_DIR, "output")
RESULTS_PATH = os.path.join(OUTPUT_DIR, "bilateral_density_sweep.json")

GRID = 160
JITTER = 10.0
STEPS = 2000
PERTURB_AT = 1200  # 60%

SEEDS = [42, 123, 256, 999]

# Density-appropriate gains from the 1/√n scaling law
DENSITIES = [
    (150, 0.30, "n150_g030"),
    (350, 0.01, "n350_g010"),
    (500, 0.02, "n500_g020"),
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
    p["iter_shuffle"] = True
    return p


def run_one(p, seed, n_seeds, perturb_at=None,
            perturb_frac=0.50, perturb_side="both"):
    if perturb_at is not None:
        r = I14.run_two_region_hetero(
            p, seed=seed, n_seeds=n_seeds, mode="hetero",
            perturb_at=perturb_at, perturb_frac=perturb_frac,
            perturb_side=perturb_side)
    else:
        r = I14.run_two_region_hetero(
            p, seed=seed, n_seeds=n_seeds, mode="hetero")
    return r


def extract_metrics(result, perturb_at):
    s = result["summary"]
    h = result["history"]

    pre_total = []
    post_total = []
    for rec in h:
        step = rec.get("step", 0)
        rt = rec.get("right_total", 0.0)
        lt = rec.get("left_total", 0.0)
        total = rt + lt
        if step < perturb_at:
            pre_total.append(total)
        else:
            post_total.append(total)

    pre_mean = float(np.mean(pre_total)) if pre_total else 0.0
    post_mean = float(np.mean(post_total)) if post_total else 0.0
    total_recovery = post_mean / max(pre_mean, 1e-9)

    return {
        "l2_crossed": s["l2_crossed"],
        "l2_outcome": s["l2_outcome"],
        "l2_stable": s["l2_stable"],
        "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
        "crossed_h7": s["crossed_h7"],
        "cells": s["final_n_structure_cells"],
        "total_recovery": round(total_recovery, 4),
    }


def summarize(entries_2, entries_1, n):
    return {
        "l2": f"{sum(1 for e in entries_2 if e['l2_crossed'])}/{n}",
        "coexist": f"{sum(1 for e in entries_2 if e['l2_outcome'] == 'coexist')}/{n}",
        "stable": f"{sum(1 for e in entries_2 if e['l2_stable'])}/{n}",
        "h7": f"{sum(1 for e in entries_2 if e['crossed_h7'])}/{n}",
        "clean": f"{sum(1 for e2, e1 in zip(entries_2, entries_1) if e2['l2_outcome'] == 'coexist' and e1['l2_outcome'] != 'coexist')}/{n}",
        "full": f"{sum(1 for e2, e1 in zip(entries_2, entries_1) if e2['crossed_h7'] and e2['l2_outcome'] == 'coexist' and e1['l2_outcome'] != 'coexist' and e2['l2_stable'])}/{n}",
        "l2_1s": f"{sum(1 for e in entries_1 if e['l2_crossed'])}/{n}",
        "h7_1s": f"{sum(1 for e in entries_1 if e['crossed_h7'])}/{n}",
        "mean_cf": round(float(np.mean([e['l2_coexist_frac'] for e in entries_2])), 3),
        "mean_total_rec": round(float(np.mean([e['total_recovery'] for e in entries_2])), 3),
        "mean_cells": int(np.mean([e['cells'] for e in entries_2])),
    }


if __name__ == "__main__":
    t0 = time.time()

    n_runs = len(DENSITIES) * len(SEEDS) * 2 * 2 + len(DENSITIES) * len(SEEDS) * 2
    print(f"\n{'='*80}")
    print(f"  BILATERAL DENSITY SWEEP")
    print(f"  3 densities × 4 seeds × {{perturbed, unperturbed}} × {{2, 1}} = {n_runs} runs")
    print(f"  perturb_at={PERTURB_AT} (60%), bilateral 50/50, iter_shuffle=True")
    print(f"{'='*80}")

    all_results = {}

    for n_term, g, label in DENSITIES:
        print(f"\n{'='*60}")
        print(f"  DENSITY: {label} (n={n_term}, g={g})")
        print(f"{'='*60}")

        p = make_params(n_term, g, g)

        # Unperturbed baseline
        print(f"\n  Computing unperturbed baseline ({label})...")
        unper_2 = []
        unper_1 = []
        for sd in SEEDS:
            r2 = run_one(p, sd, 2, perturb_at=None)
            m2 = extract_metrics(r2, PERTURB_AT)
            m2["seed"] = sd
            unper_2.append(m2)
            r1 = run_one(p, sd, 1, perturb_at=None)
            m1 = extract_metrics(r1, PERTURB_AT)
            m1["seed"] = sd
            unper_1.append(m1)
            print(f"    UNPERT 2s s={sd}: h7={m2['crossed_h7']} "
                  f"out={m2['l2_outcome']:>12s} stable={m2['l2_stable']} "
                  f"cf={m2['l2_coexist_frac']:.2f} cells={m2['cells']}")

        su_base = summarize(unper_2, unper_1, len(SEEDS))
        print(f"\n  {label} BASELINE: h7={su_base['h7']} "
              f"coexist={su_base['coexist']} stable={su_base['stable']} "
              f"full={su_base['full']} cf={su_base['mean_cf']:.3f} "
              f"1s_l2={su_base['l2_1s']}")

        # Perturbed (bilateral 50/50)
        print(f"\n  Computing bilateral 50/50 perturbed ({label})...")
        per_2 = []
        per_1 = []
        for sd in SEEDS:
            r = run_one(p, sd, 2, perturb_at=PERTURB_AT,
                        perturb_frac=0.50, perturb_side="both")
            m = extract_metrics(r, PERTURB_AT)
            m["seed"] = sd
            per_2.append(m)
            print(f"    PERT 2s s={sd}: h7={m['crossed_h7']} "
                  f"out={m['l2_outcome']:>12s} stable={m['l2_stable']} "
                  f"cf={m['l2_coexist_frac']:.2f} "
                  f"rec={m['total_recovery']:.3f} cells={m['cells']}")

            r1 = run_one(p, sd, 1, perturb_at=PERTURB_AT,
                         perturb_frac=0.50, perturb_side="both")
            m1 = extract_metrics(r1, PERTURB_AT)
            m1["seed"] = sd
            per_1.append(m1)

        su_pert = summarize(per_2, per_1, len(SEEDS))
        print(f"\n  {label} PERT (50/50): h7={su_pert['h7']} "
              f"coexist={su_pert['coexist']} stable={su_pert['stable']} "
              f"full={su_pert['full']} cf={su_pert['mean_cf']:.3f} "
              f"tot_rec={su_pert['mean_total_rec']:.3f} "
              f"1s_l2={su_pert['l2_1s']} cells={su_pert['mean_cells']}")

        # Advantage
        cf_adv = su_pert['mean_cf'] - su_base['mean_cf']
        full_adv = int(su_pert['full'].split('/')[0]) - int(su_base['full'].split('/')[0])
        print(f"\n  {label} ADVANTAGE: cf_delta={cf_adv:+.3f} "
              f"full_delta={full_adv:+d}")

        all_results[label] = {
            "n_termites": n_term,
            "g": g,
            "baseline": {
                "2seed": unper_2,
                "1seed": unper_1,
                "summary": su_base,
            },
            "perturbed": {
                "2seed": per_2,
                "1seed": per_1,
                "summary": su_pert,
            },
            "cf_advantage": round(cf_adv, 3),
            "full_advantage": full_adv,
        }

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Summary table
    print(f"\n{'='*110}")
    print(f"  BILATERAL DENSITY SWEEP SUMMARY")
    print(f"  bilateral 50/50, iter_shuffle=True, perturb_at=1200 (60%)")
    print(f"{'='*110}")
    print(f"{'density':>12s} | {'h7':>5s} {'coexist':>8s} {'stable':>7s} {'full':>5s} | "
          f"{'cf':>6s} {'1s_l2':>6s} | "
          f"{'pert_h7':>7s} {'pert_co':>8s} {'pert_st':>7s} {'pert_full':>9s} | "
          f"{'pert_cf':>7s} {'cf_adv':>7s}")
    print("-" * 110)
    for n_term, g, label in DENSITIES:
        if label not in all_results:
            continue
        r = all_results[label]
        b = r["baseline"]["summary"]
        p = r["perturbed"]["summary"]
        print(f"{label:>12s} | "
              f"{b['h7']:>5s} {b['coexist']:>8s} {b['stable']:>7s} {b['full']:>5s} | "
              f"{b['mean_cf']:>6.3f} {b['l2_1s']:>6s} | "
              f"{p['h7']:>7s} {p['coexist']:>8s} {p['stable']:>7s} {p['full']:>9s} | "
              f"{p['mean_cf']:>7.3f} {r['cf_advantage']:>+7.3f}")

    # Key findings
    print(f"\n{'='*80}")
    print(f"  KEY FINDINGS")
    print(f"{'='*80}")
    for n_term, g, label in DENSITIES:
        if label not in all_results:
            continue
        r = all_results[label]
        cf_adv = r["cf_advantage"]
        full_adv = r["full_advantage"]
        if cf_adv > 0.05:
            print(f"  {label}: bilateral advantage CONFIRMED (cf_adv={cf_adv:+.3f}, full_adv={full_adv:+d})")
        elif cf_adv > 0:
            print(f"  {label}: bilateral advantage WEAK (cf_adv={cf_adv:+.3f}, full_adv={full_adv:+d})")
        else:
            print(f"  {label}: bilateral advantage REVERSED (cf_adv={cf_adv:+.3f}, full_adv={full_adv:+d})")

    # Determinism check
    print(f"\n  Determinism check...")
    p_det = make_params(350, 0.01, 0.01)
    r1 = run_one(p_det, 42, 2, perturb_at=PERTURB_AT, perturb_frac=0.50, perturb_side="both")
    r2 = run_one(p_det, 42, 2, perturb_at=PERTURB_AT, perturb_frac=0.50, perturb_side="both")
    m1 = extract_metrics(r1, PERTURB_AT)
    m2 = extract_metrics(r2, PERTURB_AT)
    det = (m1["cells"] == m2["cells"] and m1["total_recovery"] == m2["total_recovery"])
    print(f"  n=350 50/50 seed=42: cells={m1['cells']} vs {m2['cells']} "
          f"rec={m1['total_recovery']} vs {m2['total_recovery']} "
          f"-> {'OK' if det else 'FAIL'}")

    elapsed = time.time() - t0
    print(f"\nTotal elapsed: {elapsed:.1f}s")
    print(f"Wrote {RESULTS_PATH}")
