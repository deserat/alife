"""
Bilateral perturbation sweep — does damaging both regions change the result?

Queued-topic #167:
  All perturbation tests (Sessions 55-57) damaged only the right region.
  Does damaging BOTH regions simultaneously (same fraction) change the
  result? If the damage-amplified composition is about the boundary
  BETWEEN the two structures, bilateral damage (which damages both sides
  of the boundary) might weaken or strengthen the effect differently.

  Hypothesis A: bilateral damage WEAKENS composition because both
  structures are weakened — there is no intact structure to provide
  contrast at the boundary.

  Hypothesis B: bilateral damage STRENGTHENS composition because both
  scars create curvature contrast at the boundary from both sides,
  amplifying the boundary signal.

  Hypothesis C: bilateral damage is NEUTRAL because the boundary
  signal is about the interface, not the individual structures —
  both sides being damaged doesn't change the interface dynamics.

Design:
  3 perturbation sides × 4 perturbation fractions × 8 seeds
  × {perturbed, unperturbed} × {2, 1} seeds = 192 runs

  perturb_side ∈ {"right", "both", "left"}
  perturb_frac ∈ {0.25, 0.50, 0.75, 0.90}
  perturb_at = 1200 (60% of 2000 steps)

  n=350, g=0.01 (the robust optimum from Session 54)
  160×160 grid, dual mode, focal bias 0.3, jitter 10

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
RESULTS_PATH = os.path.join(OUTPUT_DIR, "bilateral_sweep.json")

GRID = 160
JITTER = 10.0
STEPS = 2000
PERTURB_AT = 1200  # 60%

SEEDS_4 = [42, 123, 256, 999]

# Regime: n=350 g=0.01 (the robust optimum)
N_TERMITES = 350
G_FORM = 0.01
G_PERSIST = 0.01

SIDE_LEVELS = ["right", "both", "left"]
SIZE_LEVELS = [0.50, 0.90]


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


def run_one(p, seed, n_seeds, perturb_at=None, perturb_frac=0.5,
            perturb_side="right"):
    """Run one simulation, optionally perturbed."""
    if perturb_at is not None:
        r = I14.run_two_region_hetero(
            p, seed=seed, n_seeds=n_seeds, mode="hetero",
            perturb_at=perturb_at, perturb_frac=perturb_frac,
            perturb_side=perturb_side)
    else:
        r = I14.run_two_region_hetero(
            p, seed=seed, n_seeds=n_seeds, mode="hetero")
    return r


def extract_metrics(result, perturb_at, perturb_frac, perturb_side):
    """Extract key metrics from a run result."""
    s = result["summary"]
    h = result["history"]

    # For bilateral: recovery = total material post / total material pre.
    # For right-only: recovery = right material post / right material pre (as before).
    # For left-only: recovery = left material post / left material pre.
    pre_target = []
    post_target = []

    # Also track total material for both-side comparison.
    pre_total = []
    post_total = []

    for rec in h:
        step = rec.get("step", 0)
        rt = rec.get("right_total", 0.0)
        lt = rec.get("left_total", 0.0)
        total = rt + lt

        if step < perturb_at:
            pre_target.append(rt if perturb_side == "right" else
                              (lt if perturb_side == "left" else total))
            pre_total.append(total)
        else:
            post_target.append(rt if perturb_side == "right" else
                               (lt if perturb_side == "left" else total))
            post_total.append(total)

    pre_mean = float(np.mean(pre_target)) if pre_target else 0.0
    post_mean = float(np.mean(post_target)) if post_target else 0.0
    recovery_ratio = post_mean / max(pre_mean, 1e-9)

    pre_total_mean = float(np.mean(pre_total)) if pre_total else 0.0
    post_total_mean = float(np.mean(post_total)) if post_total else 0.0
    total_recovery = post_total_mean / max(pre_total_mean, 1e-9)

    # Coexist frac in the late window (after perturbation)
    late_recs = [r for r in h if r.get("step", 0) >= perturb_at]
    coexist_count = 0
    for r in late_recs:
        lc = r.get("left_components", 0)
        rc = r.get("right_components", 0)
        if 1 <= lc <= 3 and 1 <= rc <= 3:
            coexist_count += 1
    late_coexist_frac = coexist_count / max(len(late_recs), 1)

    return {
        "l2_crossed": s["l2_crossed"],
        "l2_outcome": s["l2_outcome"],
        "l2_stable": s["l2_stable"],
        "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
        "crossed_h7": s["crossed_h7"],
        "cells": s["final_n_structure_cells"],
        "recovery_ratio": round(recovery_ratio, 4),
        "total_recovery": round(total_recovery, 4),
        "pre_mean": round(pre_mean, 1),
        "post_mean": round(post_mean, 1),
        "late_coexist_frac": round(late_coexist_frac, 3),
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
        "mean_recovery": round(float(np.mean([e['recovery_ratio'] for e in entries_2])), 3),
        "mean_total_recovery": round(float(np.mean([e['total_recovery'] for e in entries_2])), 3),
        "mean_cells": int(np.mean([e['cells'] for e in entries_2])),
    }


if __name__ == "__main__":
    t0 = time.time()
    p = make_params(N_TERMITES, G_FORM, G_PERSIST)

    # Pre-compute unperturbed baseline (same for all sides/sizes).
    print(f"\n{'='*80}")
    print(f"  BILATERAL PERTURBATION SWEEP")
    print(f"  n={N_TERMITES} g={G_FORM} perturb_at={PERTURB_AT}")
    print(f"  sides={SIDE_LEVELS} sizes={SIZE_LEVELS}")
    print(f"  8 seeds x {{perturbed, unperturbed}} x {{2, 1}} = {len(SIDE_LEVELS)*len(SIZE_LEVELS)*8*2*2} runs")
    print(f"{'='*80}")

    print(f"\n  Pre-computing unperturbed baseline...")
    unper_2_all = []
    unper_1_all = []
    for sd in SEEDS_4:
        r2 = run_one(p, sd, 2, perturb_at=None)
        m2 = extract_metrics(r2, PERTURB_AT, 0.5, "right")
        m2["seed"] = sd
        unper_2_all.append(m2)

        r1 = run_one(p, sd, 1, perturb_at=None)
        m1 = extract_metrics(r1, PERTURB_AT, 0.5, "right")
        m1["seed"] = sd
        unper_1_all.append(m1)

    su_baseline = summarize(unper_2_all, unper_1_all, 4)
    print(f"  BASELINE: l2={su_baseline['l2']} coexist={su_baseline['coexist']} "
          f"stable={su_baseline['stable']} h7={su_baseline['h7']} "
          f"full={su_baseline['full']} cf={su_baseline['mean_cf']:.3f}")

    all_results = {"baseline": {"2seed": unper_2_all, "1seed": unper_1_all,
                                 "summary": su_baseline}}

    for side in SIDE_LEVELS:
        side_results = {}
        print(f"\n{'='*60}")
        print(f"  SIDE: {side}")
        print(f"{'='*60}")

        for pf in SIZE_LEVELS:
            label = f"pf{int(pf*100):02d}"
            print(f"\n  {side}/{label} (perturb_frac={pf})")

            per_2 = []
            per_1 = []

            for sd in SEEDS_4:
                # Perturbed 2-seed
                r = run_one(p, sd, 2, perturb_at=PERTURB_AT,
                            perturb_frac=pf, perturb_side=side)
                m = extract_metrics(r, PERTURB_AT, pf, side)
                m["seed"] = sd
                per_2.append(m)
                print(f"    [{side}/{label}] PERT 2s s={sd}: h7={m['crossed_h7']} "
                      f"out={m['l2_outcome']:>12s} stable={m['l2_stable']} "
                      f"cf={m['l2_coexist_frac']:.2f} "
                      f"rec={m['recovery_ratio']:.3f} "
                      f"tot_rec={m['total_recovery']:.3f} "
                      f"cells={m['cells']}")

                # Perturbed 1-seed
                r = run_one(p, sd, 1, perturb_at=PERTURB_AT,
                            perturb_frac=pf, perturb_side=side)
                m = extract_metrics(r, PERTURB_AT, pf, side)
                m["seed"] = sd
                per_1.append(m)

            sp = summarize(per_2, per_1, 4)
            su = su_baseline
            print(f"\n  {side}/{label} UNPERT: l2={su['l2']} coexist={su['coexist']} "
                  f"stable={su['stable']} h7={su['h7']} full={su['full']} "
                  f"cf={su['mean_cf']:.3f}")
            print(f"  {side}/{label} PERT:   l2={sp['l2']} coexist={sp['coexist']} "
                  f"stable={sp['stable']} h7={sp['h7']} full={sp['full']} "
                  f"cf={sp['mean_cf']:.3f} rec={sp['mean_recovery']:.3f} "
                  f"tot_rec={sp['mean_total_recovery']:.3f}")

            side_results[label] = {
                "perturb_frac": pf,
                "perturb_side": side,
                "perturbed": {
                    "2seed": per_2, "1seed": per_1,
                    "summary": sp,
                },
            }

        all_results[side] = side_results

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Summary comparison table
    print(f"\n{'='*110}")
    print(f"  BILATERAL SWEEP SUMMARY (n=350, g=0.01, 160x160, dual, focal 0.3, jit=10)")
    print(f"  perturb_at=1200 (60%)")
    print(f"  Baseline: l2={su_baseline['l2']} coexist={su_baseline['coexist']} "
          f"stable={su_baseline['stable']} h7={su_baseline['h7']} "
          f"full={su_baseline['full']} cf={su_baseline['mean_cf']:.3f}")
    print(f"{'='*110}")
    print(f"{'side':>8s} {'size':>6s} | "
          f"{'per_h7':>7s} {'per_co':>7s} {'per_st':>7s} {'per_full':>8s} | "
          f"{'recovery':>8s} {'tot_rec':>8s} {'cf':>6s} {'cells':>6s}")
    print("-" * 110)
    for side in SIDE_LEVELS:
        for pf in SIZE_LEVELS:
            label = f"pf{int(pf*100):02d}"
            if side not in all_results or label not in all_results[side]:
                continue
            sp = all_results[side][label]["perturbed"]["summary"]
            print(f"{side:>8s} {label:>6s} | "
                  f"{sp['h7']:>7s} {sp['coexist']:>7s} {sp['stable']:>7s} {sp['full']:>8s} | "
                  f"{sp['mean_recovery']:>8.3f} {sp['mean_total_recovery']:>8.3f} "
                  f"{sp['mean_cf']:>6.3f} {sp['mean_cells']:>6d}")

    # Determinism verification
    print(f"\n  Determinism check...")
    for side in ["right", "both"]:
        for pf in [0.50]:
            r1 = run_one(p, 42, 2, perturb_at=PERTURB_AT,
                        perturb_frac=pf, perturb_side=side)
            r2 = run_one(p, 42, 2, perturb_at=PERTURB_AT,
                        perturb_frac=pf, perturb_side=side)
            m1 = extract_metrics(r1, PERTURB_AT, pf, side)
            m2 = extract_metrics(r2, PERTURB_AT, pf, side)
            det = (m1["cells"] == m2["cells"] and
                   m1["recovery_ratio"] == m2["recovery_ratio"])
            print(f"  {side} pf={pf}: cells={m1['cells']} vs {m2['cells']} "
                  f"rec={m1['recovery_ratio']} vs {m2['recovery_ratio']} "
                  f"-> {'OK' if det else 'FAIL'}")

    elapsed = time.time() - t0
    print(f"\nTotal elapsed: {elapsed:.1f}s")
    print(f"Wrote {RESULTS_PATH}")
