"""
Shuffle the agent iteration order — does randomization eliminate the L/R asymmetry?

Queued-topic #179: The reverse-iteration sweep (Session 61) found the L/R asymmetry
(50/90 >> 90/50) is a pure processing-order artifact — reversing the iteration order
flips the optimum from 50/90 to 90/50. But the reverse gap (-0.025) is smaller than
the forward gap (+0.113), suggesting the asymmetry doesn't fully mirror.

Randomizing the agent order each step (rng.permutation(n)) should eliminate the
systematic bias entirely. If 50/50 becomes the best config under shuffled iteration
(it was at 4 seeds in Session 59 before the 8-seed robustness revealed the
processing-order effect), the processing-order control is confirmed as the fix.

Design:
  3 configs (50/50, 50/90, 90/50) × 8 seeds × {shuffled, forward} × {2, 1} seeds
  = 3 × 8 × 2 × 2 = 96 perturbed + 8 × 2 × 2 = 32 unperturbed = 128 runs

  Forward order is the baseline (same as reverse_iteration_sweep.py's forward).
  Shuffled order uses rng.permutation(n) each step — a fresh random order.

  n=350, g=0.01 (the robust optimum from Session 54)
  160×160 grid, dual mode, focal bias 0.3, jitter 10
  perturb_at=1200 (60% of 2000 steps)

  8 seeds: [42, 123, 256, 999, 100, 777, 1337, 314159]

Control arm: unperturbed runs at the same configs.
Per-criterion pass rates are reported for every null.
Determinism verified by running twice and diffing.

Prediction:
  If the L/R asymmetry is a pure processing-order artifact, shuffled iteration
  eliminates the 50/90 vs 90/50 gap: both configs converge to the same cf, and
  50/50 (symmetric perturbation) becomes the best config. H7 should remain 8/8
  (the crossing is robust to iteration order, per Session 61).
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
RESULTS_PATH = os.path.join(OUTPUT_DIR, "shuffle_iteration_sweep.json")

GRID = 160
JITTER = 10.0
STEPS = 2000
PERTURB_AT = 1200  # 60%

SEEDS = [42, 123, 256, 999, 100, 777, 1337, 314159]

N_TERMITES = 350
G_FORM = 0.01
G_PERSIST = 0.01

CONFIGS = [
    (0.50, 0.50, "50_50"),
    (0.50, 0.90, "50_90"),
    (0.90, 0.50, "90_50"),
]


def make_params(n_termites, g_form, g_persist, shuffle=False):
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
    p["iter_shuffle"] = shuffle
    return p


def run_one(p, seed, n_seeds, perturb_at=None,
            perturb_frac_left=None, perturb_frac_right=None):
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
    }


def summarize(entries_2, entries_1, n_seeds):
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

    n_runs = len(CONFIGS) * len(SEEDS) * 2 * 2  # 3×8×2×2=96 perturbed
    print(f"\n{'='*80}")
    print(f"  SHUFFLE ITERATION SWEEP — DOES RANDOMIZATION ELIMINATE THE L/R ASYMMETRY?")
    print(f"  n={N_TERMITES} g={G_FORM} perturb_at={PERTURB_AT}")
    print(f"  configs={len(CONFIGS)} seeds={len(SEEDS)} "
          f"× {{shuffled, forward}} × {{2, 1}} = {n_runs} runs")
    print(f"{'='*80}")

    all_results = {}

    for direction, shuffle in [("shuffled", True), ("forward", False)]:
        p = make_params(N_TERMITES, G_FORM, G_PERSIST, shuffle=shuffle)

        print(f"\n{'='*60}")
        print(f"  DIRECTION: {direction} (iter_shuffle={shuffle})")
        print(f"{'='*60}")

        # Unperturbed baseline (8 seeds, this direction only)
        print(f"\n  Computing unperturbed baseline ({direction}, 8 seeds)...")
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
                  f"cf={m2['l2_coexist_frac']:.2f}")

        su_baseline = summarize(unper_2, unper_1, len(SEEDS))
        print(f"\n  {direction.upper()} BASELINE: l2={su_baseline['l2']} "
              f"coexist={su_baseline['coexist']} "
              f"stable={su_baseline['stable']} h7={su_baseline['h7']} "
              f"full={su_baseline['full']} cf={su_baseline['mean_cf']:.3f}")

        dir_results = {"baseline": {"2seed": unper_2, "1seed": unper_1,
                                     "summary": su_baseline}}

        for pf_left, pf_right, label in CONFIGS:
            print(f"\n  [{direction}] CONFIG: {label} (L={pf_left*100:.0f}%, R={pf_right*100:.0f}%)")

            per_2 = []
            per_1 = []
            for sd in SEEDS:
                r = run_one(p, sd, 2, perturb_at=PERTURB_AT,
                            perturb_frac_left=pf_left,
                            perturb_frac_right=pf_right)
                m = extract_metrics(r, PERTURB_AT)
                m["seed"] = sd
                per_2.append(m)
                print(f"    [{direction} {label}] PERT 2s s={sd}: "
                      f"h7={m['crossed_h7']} "
                      f"out={m['l2_outcome']:>12s} "
                      f"stable={m['l2_stable']} "
                      f"cf={m['l2_coexist_frac']:.2f} "
                      f"tot_rec={m['total_recovery']:.3f} "
                      f"L_rec={m['left_recovery']:.3f} "
                      f"R_rec={m['right_recovery']:.3f} "
                      f"cells={m['cells']}")

                r1 = run_one(p, sd, 1, perturb_at=PERTURB_AT,
                             perturb_frac_left=pf_left,
                             perturb_frac_right=pf_right)
                m1 = extract_metrics(r1, PERTURB_AT)
                m1["seed"] = sd
                per_1.append(m1)

            sp = summarize(per_2, per_1, len(SEEDS))
            su = su_baseline
            print(f"\n  {direction} {label} PERT: l2={sp['l2']} "
                  f"coexist={sp['coexist']} "
                  f"stable={sp['stable']} h7={sp['h7']} "
                  f"full={sp['full']} cf={sp['mean_cf']:.3f} "
                  f"tot_rec={sp['mean_total_rec']:.3f} "
                  f"1s_l2={sp['l2_1s']} cells={sp['mean_cells']}")

            dir_results[label] = {
                "pf_left": pf_left,
                "pf_right": pf_right,
                "perturbed": {
                    "2seed": per_2,
                    "1seed": per_1,
                    "summary": sp,
                },
            }

        all_results[direction] = dir_results

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Summary comparison table
    print(f"\n{'='*120}")
    print(f"  SHUFFLE ITERATION SWEEP SUMMARY (n=350, g=0.01, 160x160, dual, focal 0.3, jit=10)")
    print(f"  perturb_at=1200 (60%)")
    print(f"{'='*120}")
    print(f"{'dir':>10s} {'config':>8s} {'L%':>5s} {'R%':>5s} | "
          f"{'h7':>5s} {'coexist':>8s} {'stable':>7s} {'full':>5s} | "
          f"{'cf':>6s} {'tot_rec':>8s} {'1s_l2':>6s} {'cells':>6s}")
    print("-" * 120)
    for direction in ["shuffled", "forward"]:
        dres = all_results[direction]
        for pf_left, pf_right, label in CONFIGS:
            if label not in dres:
                continue
            sp = dres[label]["perturbed"]["summary"]
            print(f"{direction:>10s} {label:>8s} {pf_left*100:>4.0f}% {pf_right*100:>4.0f}% | "
                  f"{sp['h7']:>5s} {sp['coexist']:>8s} {sp['stable']:>7s} {sp['full']:>5s} | "
                  f"{sp['mean_cf']:>6.3f} {sp['mean_total_rec']:>8.3f} "
                  f"{sp['l2_1s']:>6s} {sp['mean_cells']:>6d}")

    # The key comparison: does 50/90 == 90/50 under shuffle?
    fwd_50_90 = all_results["forward"]["50_90"]["perturbed"]["summary"]
    fwd_90_50 = all_results["forward"]["90_50"]["perturbed"]["summary"]
    shf_50_90 = all_results["shuffled"]["50_90"]["perturbed"]["summary"]
    shf_90_50 = all_results["shuffled"]["90_50"]["perturbed"]["summary"]
    shf_50_50 = all_results["shuffled"]["50_50"]["perturbed"]["summary"]

    print(f"\n{'='*80}")
    print(f"  KEY COMPARISON: Does shuffling eliminate the L/R asymmetry?")
    print(f"{'='*80}")
    print(f"  Forward:  50/90 cf={fwd_50_90['mean_cf']:.3f}  vs  90/50 cf={fwd_90_50['mean_cf']:.3f}  "
          f"gap={fwd_50_90['mean_cf'] - fwd_90_50['mean_cf']:+.3f}")
    print(f"  Shuffled: 50/90 cf={shf_50_90['mean_cf']:.3f}  vs  90/50 cf={shf_90_50['mean_cf']:.3f}  "
          f"gap={shf_50_90['mean_cf'] - shf_90_50['mean_cf']:+.3f}")
    print(f"  Shuffled: 50/50 cf={shf_50_50['mean_cf']:.3f}")
    gap_closed = abs(shf_50_90['mean_cf'] - shf_90_50['mean_cf']) < abs(fwd_50_90['mean_cf'] - fwd_90_50['mean_cf'])
    fifty_fifty_best = shf_50_50['mean_cf'] >= max(shf_50_90['mean_cf'], shf_90_50['mean_cf'])
    print(f"\n  Gap shrinks under shuffle: {'YES' if gap_closed else 'NO'}")
    print(f"  50/50 is best under shuffle: {'YES' if fifty_fifty_best else 'NO'}")

    # Determinism verification
    print(f"\n  Determinism check...")
    p_shf = make_params(N_TERMITES, G_FORM, G_PERSIST, shuffle=True)
    p_fwd = make_params(N_TERMITES, G_FORM, G_PERSIST, shuffle=False)
    for label, p_test in [("shuffled", p_shf), ("forward", p_fwd)]:
        pf_l, pf_r, _ = CONFIGS[0]  # 50/50
        r1 = run_one(p_test, 42, 2, perturb_at=PERTURB_AT,
                    perturb_frac_left=pf_l, perturb_frac_right=pf_r)
        r2 = run_one(p_test, 42, 2, perturb_at=PERTURB_AT,
                    perturb_frac_left=pf_l, perturb_frac_right=pf_r)
        m1 = extract_metrics(r1, PERTURB_AT)
        m2 = extract_metrics(r2, PERTURB_AT)
        det = (m1["cells"] == m2["cells"] and
               m1["total_recovery"] == m2["total_recovery"])
        print(f"  {label} 50/50: cells={m1['cells']} vs {m2['cells']} "
              f"rec={m1['total_recovery']} vs {m2['total_recovery']} "
              f"-> {'OK' if det else 'FAIL'}")

    elapsed = time.time() - t0
    print(f"\nTotal elapsed: {elapsed:.1f}s")
    print(f"Wrote {RESULTS_PATH}")
