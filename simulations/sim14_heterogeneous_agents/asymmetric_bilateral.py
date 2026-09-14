"""
Asymmetric bilateral perturbation sweep — does different damage on each
side change the result?

Queued-topic #170:
  Bilateral 50%/50% produces the highest composition quality ever (cf=0.825,
  4/4 full). What about 50%/90% (right 50%, left 90%) or 90%/50%?
  Does the asymmetric bilateral damage create an asymmetric boundary that
  degrades composition? Or does the stronger side's curvature compensate
  for the weaker?

Hypothesis A: asymmetric bilateral damage DEGRADES composition because the
  boundary becomes asymmetric — the stronger side's curvature overwhelms
  the weaker side's, creating a lopsided boundary that fragments one region.

Hypothesis B: asymmetric bilateral damage PRESERVES composition because the
  bilateral advantage is about having curvature on BOTH sides of the
  boundary, regardless of symmetry — the weaker side's curvature is still
  nonzero and contributes to boundary reinforcement.

Hypothesis C: asymmetric bilateral damage is BETWEEN symmetric bilateral
  and unilateral — the bilateral advantage scales with the minimum damage
  fraction (min(pf_left, pf_right)), not the mean.

Design:
  5 asymmetry configs × 4 seeds × {perturbed, unperturbed} × {2, 1} = 80 runs
  + baseline (unperturbed) = 80 total

  Configs (all bilateral):
    50/50  — symmetric moderate (the Session 58 best)
    50/90  — right 50%, left 90% (asymmetric)
    90/50  — right 90%, left 50% (asymmetric, mirror)
    90/90  — symmetric severe
    25/50  — right 25%, left 50% (moderate asymmetry)

  n=350, g=0.01 (the robust optimum from Session 54)
  160×160 grid, dual mode, focal bias 0.3, jitter 10
  perturb_at=1200 (60% of 2000 steps)

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
RESULTS_PATH = os.path.join(OUTPUT_DIR, "asymmetric_bilateral_sweep.json")

GRID = 160
JITTER = 10.0
STEPS = 2000
PERTURB_AT = 1200  # 60%

SEEDS = [42, 123, 256, 999]

N_TERMITES = 350
G_FORM = 0.01
G_PERSIST = 0.01

# Asymmetric bilateral configs: (pf_left, pf_right, label)
ASYMMETRY_CONFIGS = [
    (0.50, 0.50, "50_50"),
    (0.50, 0.90, "50_90"),
    (0.90, 0.50, "90_50"),
    (0.90, 0.90, "90_90"),
    (0.25, 0.50, "25_50"),
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


def run_one(p, seed, n_seeds, perturb_at=None,
            perturb_frac_left=None, perturb_frac_right=None):
    """Run one simulation, optionally perturbed with asymmetric fractions."""
    if perturb_at is not None:
        r = I14.run_two_region_hetero(
            p, seed=seed, n_seeds=n_seeds, mode="hetero",
            perturb_at=perturb_at,
            perturb_side="both",
            perturb_frac_left=perturb_frac_left,
            perturb_frac_right=perturb_frac_right)
    else:
        r = I14.run_two_region_hetero(
            p, seed=seed, n_seeds=n_seeds, mode="hetero")
    return r


def extract_metrics(result, perturb_at):
    """Extract key metrics from a run result."""
    s = result["summary"]
    h = result["history"]

    pre_total = []
    post_total = []
    pre_left = []
    pre_right = []
    post_left = []
    post_right = []

    for rec in h:
        step = rec.get("step", 0)
        rt = rec.get("right_total", 0.0)
        lt = rec.get("left_total", 0.0)
        total = rt + lt

        if step < perturb_at:
            pre_total.append(total)
            pre_left.append(lt)
            pre_right.append(rt)
        else:
            post_total.append(total)
            post_left.append(lt)
            post_right.append(rt)

    pre_total_mean = float(np.mean(pre_total)) if pre_total else 0.0
    post_total_mean = float(np.mean(post_total)) if post_total else 0.0
    total_recovery = post_total_mean / max(pre_total_mean, 1e-9)

    pre_left_mean = float(np.mean(pre_left)) if pre_left else 0.0
    post_left_mean = float(np.mean(post_left)) if post_left else 0.0
    left_recovery = post_left_mean / max(pre_left_mean, 1e-9)

    pre_right_mean = float(np.mean(pre_right)) if pre_right else 0.0
    post_right_mean = float(np.mean(post_right)) if post_right else 0.0
    right_recovery = post_right_mean / max(pre_right_mean, 1e-9)

    return {
        "l2_crossed": s["l2_crossed"],
        "l2_outcome": s["l2_outcome"],
        "l2_stable": s["l2_stable"],
        "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
        "crossed_h7": s["crossed_h7"],
        "cells": s["final_n_structure_cells"],
        "total_recovery": round(total_recovery, 4),
        "left_recovery": round(left_recovery, 4),
        "right_recovery": round(right_recovery, 4),
        "pre_left": round(pre_left_mean, 1),
        "post_left": round(post_left_mean, 1),
        "pre_right": round(pre_right_mean, 1),
        "post_right": round(post_right_mean, 1),
    }


def summarize(entries_2, entries_1, n_seeds):
    """Compute summary for one condition."""
    n = n_seeds
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
        "mean_left_rec": round(float(np.mean([e['left_recovery'] for e in entries_2])), 3),
        "mean_right_rec": round(float(np.mean([e['right_recovery'] for e in entries_2])), 3),
        "mean_cells": int(np.mean([e['cells'] for e in entries_2])),
    }


if __name__ == "__main__":
    t0 = time.time()
    p = make_params(N_TERMITES, G_FORM, G_PERSIST)

    n_runs = len(ASYMMETRY_CONFIGS) * len(SEEDS) * 2 * 2
    print(f"\n{'='*80}")
    print(f"  ASYMMETRIC BILATERAL PERTURBATION SWEEP")
    print(f"  n={N_TERMITES} g={G_FORM} perturb_at={PERTURB_AT}")
    print(f"  configs={len(ASYMMETRY_CONFIGS)} seeds={len(SEEDS)} "
          f"× {{perturbed, unperturbed}} × {{2, 1}} = {n_runs} runs")
    print(f"{'='*80}")

    # Pre-compute unperturbed baseline.
    print(f"\n  Pre-computing unperturbed baseline...")
    unper_2_all = []
    unper_1_all = []
    for sd in SEEDS:
        r2 = run_one(p, sd, 2, perturb_at=None)
        m2 = extract_metrics(r2, PERTURB_AT)
        m2["seed"] = sd
        unper_2_all.append(m2)

        r1 = run_one(p, sd, 1, perturb_at=None)
        m1 = extract_metrics(r1, PERTURB_AT)
        m1["seed"] = sd
        unper_1_all.append(m1)

    su_baseline = summarize(unper_2_all, unper_1_all, len(SEEDS))
    print(f"  BASELINE: l2={su_baseline['l2']} coexist={su_baseline['coexist']} "
          f"stable={su_baseline['stable']} h7={su_baseline['h7']} "
          f"full={su_baseline['full']} cf={su_baseline['mean_cf']:.3f}")

    all_results = {"baseline": {"2seed": unper_2_all, "1seed": unper_1_all,
                                 "summary": su_baseline}}

    for pf_left, pf_right, label in ASYMMETRY_CONFIGS:
        print(f"\n{'='*60}")
        print(f"  CONFIG: {label} (left={pf_left}%, right={pf_right}%)")
        print(f"{'='*60}")

        per_2 = []
        per_1 = []

        for sd in SEEDS:
            # Perturbed 2-seed
            r = run_one(p, sd, 2, perturb_at=PERTURB_AT,
                        perturb_frac_left=pf_left,
                        perturb_frac_right=pf_right)
            m = extract_metrics(r, PERTURB_AT)
            m["seed"] = sd
            per_2.append(m)
            print(f"    [{label}] PERT 2s s={sd}: h7={m['crossed_h7']} "
                  f"out={m['l2_outcome']:>12s} stable={m['l2_stable']} "
                  f"cf={m['l2_coexist_frac']:.2f} "
                  f"tot_rec={m['total_recovery']:.3f} "
                  f"L_rec={m['left_recovery']:.3f} "
                  f"R_rec={m['right_recovery']:.3f} "
                  f"cells={m['cells']}")

            # Perturbed 1-seed
            r = run_one(p, sd, 1, perturb_at=PERTURB_AT,
                        perturb_frac_left=pf_left,
                        perturb_frac_right=pf_right)
            m = extract_metrics(r, PERTURB_AT)
            m["seed"] = sd
            per_1.append(m)

        sp = summarize(per_2, per_1, len(SEEDS))
        su = su_baseline
        print(f"\n  {label} UNPERT: l2={su['l2']} coexist={su['coexist']} "
              f"stable={su['stable']} h7={su['h7']} full={su['full']} "
              f"cf={su['mean_cf']:.3f}")
        print(f"  {label} PERT:   l2={sp['l2']} coexist={sp['coexist']} "
              f"stable={sp['stable']} h7={sp['h7']} full={sp['full']} "
              f"cf={sp['mean_cf']:.3f} tot_rec={sp['mean_total_rec']:.3f} "
              f"L_rec={sp['mean_left_rec']:.3f} R_rec={sp['mean_right_rec']:.3f}")

        all_results[label] = {
            "pf_left": pf_left,
            "pf_right": pf_right,
            "perturbed": {
                "2seed": per_2,
                "1seed": per_1,
                "summary": sp,
            },
        }

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Summary comparison table
    print(f"\n{'='*120}")
    print(f"  ASYMMETRIC BILATERAL SWEEP SUMMARY (n=350, g=0.01, 160x160, dual, focal 0.3, jit=10)")
    print(f"  perturb_at=1200 (60%)")
    print(f"  Baseline: l2={su_baseline['l2']} coexist={su_baseline['coexist']} "
          f"stable={su_baseline['stable']} h7={su_baseline['h7']} "
          f"full={su_baseline['full']} cf={su_baseline['mean_cf']:.3f}")
    print(f"{'='*120}")
    print(f"{'config':>8s} {'L%':>5s} {'R%':>5s} | "
          f"{'h7':>5s} {'coexist':>8s} {'stable':>7s} {'full':>5s} | "
          f"{'cf':>6s} {'tot_rec':>8s} {'L_rec':>7s} {'R_rec':>7s} "
          f"{'1s_l2':>6s} {'cells':>6s}")
    print("-" * 120)
    for pf_left, pf_right, label in ASYMMETRY_CONFIGS:
        if label not in all_results:
            continue
        sp = all_results[label]["perturbed"]["summary"]
        print(f"{label:>8s} {pf_left*100:>4.0f}% {pf_right*100:>4.0f}% | "
              f"{sp['h7']:>5s} {sp['coexist']:>8s} {sp['stable']:>7s} "
              f"{sp['full']:>5s} | "
              f"{sp['mean_cf']:>6.3f} {sp['mean_total_rec']:>8.3f} "
              f"{sp['mean_left_rec']:>7.3f} {sp['mean_right_rec']:>7.3f} "
              f"{sp['l2_1s']:>6s} {sp['mean_cells']:>6d}")

    # Determinism verification
    print(f"\n  Determinism check...")
    for label in ["50_50", "50_90"]:
        pf_left, pf_right, _ = [(l, r, lbl) for l, r, lbl in ASYMMETRY_CONFIGS
                                 if lbl == label][0]
        r1 = run_one(p, 42, 2, perturb_at=PERTURB_AT,
                    perturb_frac_left=pf_left,
                    perturb_frac_right=pf_right)
        r2 = run_one(p, 42, 2, perturb_at=PERTURB_AT,
                    perturb_frac_left=pf_left,
                    perturb_frac_right=pf_right)
        m1 = extract_metrics(r1, PERTURB_AT)
        m2 = extract_metrics(r2, PERTURB_AT)
        det = (m1["cells"] == m2["cells"] and
               m1["total_recovery"] == m2["total_recovery"])
        print(f"  {label}: cells={m1['cells']} vs {m2['cells']} "
              f"rec={m1['total_recovery']} vs {m2['total_recovery']} "
              f"-> {'OK' if det else 'FAIL'}")

    elapsed = time.time() - t0
    print(f"\nTotal elapsed: {elapsed:.1f}s")
    print(f"Wrote {RESULTS_PATH}")
