"""
32-seed robustness — does 14/16 degrade further? Does the +0.062 gap
stabilize or flip?

Queued-topic #185: At 16 seeds, all three configs degrade to 14/16 full
(2/16 fail each). Does 14/16 degrade to ~24/32 at 32 seeds (~12% per
seed), or is 14/16 the stable failure rate? Also: does the +0.062 gap
(50/90 > 90/50) stabilize or flip again?

Design:
  3 configs (50/50, 50/90, 90/50) × 32 seeds × {2, 1} seeds (perturbed)
  + 32-seed unperturbed baseline
  = 3 × 32 × 2 + 32 × 2 = 256 runs

  n=350, g=0.01 (the robust optimum from Session 54)
  160×160 grid, dual mode, focal bias 0.3, jitter 10
  perturb_at=1200 (60% of 2000 steps), iter_shuffle=True

  32 seeds: original 16 + 16 new for statistical power
  [42, 123, 256, 999, 100, 777, 1337, 314159,
   2024, 8888, 555, 1111, 314, 271, 9999, 12345,
   7777, 31337, 8, 16, 64, 128, 512, 1024, 2048, 4096,
   600, 700, 800, 900, 1100, 1200]

  The 16 original seeds allow direct comparison with Session 63's results.

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
RESULTS_PATH = os.path.join(OUTPUT_DIR, "seed32_robustness_sweep.json")

GRID = 160
JITTER = 10.0
STEPS = 2000
PERTURB_AT = 1200  # 60%

SEEDS_32 = [
    42, 123, 256, 999, 100, 777, 1337, 314159,
    2024, 8888, 555, 1111, 314, 271, 9999, 12345,
    7777, 31337, 8, 16, 64, 128, 512, 1024,
    2048, 4096, 600, 700, 800, 900, 1100, 1200,
]
SEEDS_16_ORIG = [
    42, 123, 256, 999, 100, 777, 1337, 314159,
    2024, 8888, 555, 1111, 314, 271, 9999, 12345,
]

N_TERMITES = 350
G_FORM = 0.01
G_PERSIST = 0.01

CONFIGS = [
    (0.50, 0.50, "50_50"),
    (0.50, 0.90, "50_90"),
    (0.90, 0.50, "90_50"),
]


def make_params(shuffle=True):
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = N_TERMITES
    p["boundary_mode"] = "dual"
    p["g_form"] = G_FORM
    p["g_persist"] = G_PERSIST
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
        "mean_cells": int(np.mean([e['cells'] for e in entries_2])),
    }


def summarize_subset(entries_2, entries_1, seeds_subset, all_seeds):
    """Summarize only the entries whose seed is in seeds_subset."""
    idx = [i for i, e in enumerate(entries_2) if e["seed"] in seeds_subset]
    e2_sub = [entries_2[i] for i in idx]
    e1_sub = [entries_1[i] for i in idx]
    return summarize(e2_sub, e1_sub, len(e2_sub))


if __name__ == "__main__":
    t0 = time.time()

    n_runs = len(CONFIGS) * len(SEEDS_32) * 2 + len(SEEDS_32) * 2
    print(f"\n{'='*80}")
    print(f"  32-SEED ROBUSTNESS SWEEP — SHUFFLED ITERATION")
    print(f"  n={N_TERMITES} g={G_FORM} perturb_at={PERTURB_AT} iter_shuffle=True")
    print(f"  configs={len(CONFIGS)} seeds={len(SEEDS_32)} "
          f"× {{2, 1}} = {n_runs} runs")
    print(f"{'='*80}")

    all_results = {}
    p = make_params(shuffle=True)

    # Unperturbed baseline (32 seeds)
    print(f"\n  Computing unperturbed baseline (shuffled, 32 seeds)...")
    unper_2 = []
    unper_1 = []
    for sd in SEEDS_32:
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

    su_baseline_32 = summarize(unper_2, unper_1, len(SEEDS_32))
    su_baseline_16 = summarize_subset(unper_2, unper_1, set(SEEDS_16_ORIG), SEEDS_32)
    print(f"\n  SHUFFLED BASELINE (32 seeds): l2={su_baseline_32['l2']} "
          f"coexist={su_baseline_32['coexist']} "
          f"stable={su_baseline_32['stable']} h7={su_baseline_32['h7']} "
          f"full={su_baseline_32['full']} cf={su_baseline_32['mean_cf']:.3f}")
    print(f"  SHUFFLED BASELINE (16 orig):  l2={su_baseline_16['l2']} "
          f"coexist={su_baseline_16['coexist']} "
          f"stable={su_baseline_16['stable']} h7={su_baseline_16['h7']} "
          f"full={su_baseline_16['full']} cf={su_baseline_16['mean_cf']:.3f}")

    all_results["baseline"] = {
        "32seed": {"2seed": unper_2, "1seed": unper_1,
                    "summary": su_baseline_32},
        "16orig": {"summary": su_baseline_16},
    }

    # Perturbed configs
    for pf_left, pf_right, label in CONFIGS:
        print(f"\n  [shuffled] CONFIG: {label} (L={pf_left*100:.0f}%, R={pf_right*100:.0f}%)")

        per_2 = []
        per_1 = []
        for sd in SEEDS_32:
            r = run_one(p, sd, 2, perturb_at=PERTURB_AT,
                        perturb_frac_left=pf_left,
                        perturb_frac_right=pf_right)
            m = extract_metrics(r, PERTURB_AT)
            m["seed"] = sd
            per_2.append(m)
            print(f"    [shuffled {label}] PERT 2s s={sd}: "
                  f"h7={m['crossed_h7']} "
                  f"out={m['l2_outcome']:>12s} "
                  f"stable={m['l2_stable']} "
                  f"cf={m['l2_coexist_frac']:.2f} "
                  f"cells={m['cells']}")

            r1 = run_one(p, sd, 1, perturb_at=PERTURB_AT,
                         perturb_frac_left=pf_left,
                         perturb_frac_right=pf_right)
            m1 = extract_metrics(r1, PERTURB_AT)
            m1["seed"] = sd
            per_1.append(m1)

        sp_32 = summarize(per_2, per_1, len(SEEDS_32))
        sp_16 = summarize_subset(per_2, per_1, set(SEEDS_16_ORIG), SEEDS_32)

        print(f"\n  shuffled {label} PERT (32 seeds): l2={sp_32['l2']} "
              f"coexist={sp_32['coexist']} "
              f"stable={sp_32['stable']} h7={sp_32['h7']} "
              f"full={sp_32['full']} cf={sp_32['mean_cf']:.3f} "
              f"tot_rec={sp_32['mean_total_rec']:.3f} "
              f"1s_l2={sp_32['l2_1s']} cells={sp_32['mean_cells']}")
        print(f"  shuffled {label} PERT (16 orig):  l2={sp_16['l2']} "
              f"coexist={sp_16['coexist']} "
              f"stable={sp_16['stable']} h7={sp_16['h7']} "
              f"full={sp_16['full']} cf={sp_16['mean_cf']:.3f}")

        all_results[label] = {
            "pf_left": pf_left,
            "pf_right": pf_right,
            "perturbed": {
                "32seed": {"2seed": per_2, "1seed": per_1,
                            "summary": sp_32},
                "16orig": {"summary": sp_16},
            },
        }

    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Summary comparison table
    print(f"\n{'='*120}")
    print(f"  32-SEED ROBUSTNESS SWEEP SUMMARY (shuffled, n=350, g=0.01, 160x160, dual, focal 0.3, jit=10)")
    print(f"  perturb_at=1200 (60%)")
    print(f"{'='*120}")
    print(f"{'config':>8s} | {'n':>3s} | "
          f"{'h7':>5s} {'coexist':>8s} {'stable':>7s} {'full':>5s} | "
          f"{'cf':>6s} {'tot_rec':>8s} {'1s_l2':>6s} {'cells':>6s}")
    print("-" * 120)
    for pf_left, pf_right, label in CONFIGS:
        if label not in all_results:
            continue
        sp32 = all_results[label]["perturbed"]["32seed"]["summary"]
        sp16 = all_results[label]["perturbed"]["16orig"]["summary"]
        print(f"{label:>8s} | {'32':>3s} | "
              f"{sp32['h7']:>5s} {sp32['coexist']:>8s} {sp32['stable']:>7s} {sp32['full']:>5s} | "
              f"{sp32['mean_cf']:>6.3f} {sp32['mean_total_rec']:>8.3f} "
              f"{sp32['l2_1s']:>6s} {sp32['mean_cells']:>6d}")
        print(f"{label:>8s} | {'16':>3s} | "
              f"{sp16['h7']:>5s} {sp16['coexist']:>8s} {sp16['stable']:>7s} {sp16['full']:>5s} | "
              f"{sp16['mean_cf']:>6.3f}")

    # Key comparisons
    cf_50_50_32 = all_results["50_50"]["perturbed"]["32seed"]["summary"]["mean_cf"]
    cf_50_90_32 = all_results["50_90"]["perturbed"]["32seed"]["summary"]["mean_cf"]
    cf_90_50_32 = all_results["90_50"]["perturbed"]["32seed"]["summary"]["mean_cf"]
    cf_50_50_16 = all_results["50_50"]["perturbed"]["16orig"]["summary"]["mean_cf"]
    cf_50_90_16 = all_results["50_90"]["perturbed"]["16orig"]["summary"]["mean_cf"]
    cf_90_50_16 = all_results["90_50"]["perturbed"]["16orig"]["summary"]["mean_cf"]

    full_50_90_32 = all_results["50_90"]["perturbed"]["32seed"]["summary"]["full"]
    full_50_90_16 = all_results["50_90"]["perturbed"]["16orig"]["summary"]["full"]
    full_90_50_32 = all_results["90_50"]["perturbed"]["32seed"]["summary"]["full"]
    full_90_50_16 = all_results["90_50"]["perturbed"]["16orig"]["summary"]["full"]
    full_50_50_32 = all_results["50_50"]["perturbed"]["32seed"]["summary"]["full"]
    full_50_50_16 = all_results["50_50"]["perturbed"]["16orig"]["summary"]["full"]

    print(f"\n{'='*80}")
    print(f"  KEY COMPARISONS")
    print(f"{'='*80}")

    print(f"\n  #185a: Does 14/16 degrade further at 32 seeds?")
    print(f"    16-seed:  50/50 full={full_50_50_16}  50/90 full={full_50_90_16}  90/50 full={full_90_50_16}")
    print(f"    32-seed:  50/50 full={full_50_50_32}  50/90 full={full_50_90_32}  90/50 full={full_90_50_32}")

    print(f"\n  #185b: Does the +0.062 gap stabilize or flip?")
    print(f"    16-seed:  50/90 cf={cf_50_90_16:.3f}  vs  90/50 cf={cf_90_50_16:.3f}  "
          f"gap={cf_50_90_16 - cf_90_50_16:+.3f}")
    print(f"    32-seed:  50/90 cf={cf_50_90_32:.3f}  vs  90/50 cf={cf_90_50_32:.3f}  "
          f"gap={cf_50_90_32 - cf_90_50_32:+.3f}")
    gap_16 = abs(cf_50_90_16 - cf_90_50_16)
    gap_32 = abs(cf_50_90_32 - cf_90_50_32)
    print(f"    Gap 16-seed:  {gap_16:.3f}")
    print(f"    Gap 32-seed: {gap_32:.3f}")
    if gap_32 < 0.01:
        print(f"    Conclusion: GAP VANISHES (statistical at 16 seeds)")
    elif gap_32 < gap_16 * 0.5:
        print(f"    Conclusion: GAP SHRINKS >50% (mostly statistical)")
    else:
        print(f"    Conclusion: GAP PERSISTS (structural at 32 seeds)")

    best_32 = max(cf_50_50_32, cf_50_90_32, cf_90_50_32)
    best_label = "50/50" if best_32 == cf_50_50_32 else ("50/90" if best_32 == cf_50_90_32 else "90/50")
    print(f"\n    Best config at 32 seeds: {best_label} (cf={best_32:.3f})")

    # Determinism verification
    print(f"\n  Determinism check...")
    p_det = make_params(shuffle=True)
    pf_l, pf_r, _ = CONFIGS[1]  # 50/90
    r1 = run_one(p_det, 42, 2, perturb_at=PERTURB_AT,
                perturb_frac_left=pf_l, perturb_frac_right=pf_r)
    r2 = run_one(p_det, 42, 2, perturb_at=PERTURB_AT,
                perturb_frac_left=pf_l, perturb_frac_right=pf_r)
    m1 = extract_metrics(r1, PERTURB_AT)
    m2 = extract_metrics(r2, PERTURB_AT)
    det = (m1["cells"] == m2["cells"] and
           m1["total_recovery"] == m2["total_recovery"])
    print(f"  shuffled 50/90 seed=42: cells={m1['cells']} vs {m2['cells']} "
          f"rec={m1['total_recovery']} vs {m2['total_recovery']} "
          f"-> {'OK' if det else 'FAIL'}")

    elapsed = time.time() - t0
    print(f"\nTotal elapsed: {elapsed:.1f}s")
    print(f"Wrote {RESULTS_PATH}")
