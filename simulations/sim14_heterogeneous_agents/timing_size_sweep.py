"""
Perturbation timing and size sweep — is over-recovery genuine self-repair?

Queued-topics #162 and #163:
  Session 55 found perturbation over-recovery (recovery >1.0) at n=350/500
  where H7 fires. The main criticism: the perturbation hits at 60% of steps
  (step 1200/2000), when the structure is still growing. Over-recovery could
  be a growth artifact — the perturbation resets the right region's material
  to a lower base, and growth continues from there, producing more growth by
  step 2000 than the unperturbed run (which had plateaued).

  #162: Does over-recovery occur at LATE perturbation (80%, 90% of steps),
  after mass equilibration? If yes → genuine self-repair. If no → growth
  artifact.

  #163: Does the damage signal saturate? Sweep perturb_frac at n=350 g=0.01.
  If the scar is too large, the curvature signal may flatten (too much
  damage = no signal), creating a perturbation-size threshold for
  self-repair. If over-recovery degrades at high perturb_frac, the damage
  signal saturates.

Design:
  Part A — timing sweep:
    n=350, g=0.01, 8 seeds, perturb_frac=0.50
    perturb_at ∈ {1200 (60%), 1600 (80%), 1800 (90%)}
    × {perturbed, unperturbed} × {2, 1} = 96 runs

  Part B — size sweep:
    n=350, g=0.01, 8 seeds, perturb_at=1200 (60%)
    perturb_frac ∈ {0.25, 0.50, 0.75, 0.90}
    × {perturbed, unperturbed} × {2, 1} = 96 runs

  Total: 192 runs.

Control arm: unperturbed runs at the same configs.
The comparison is perturbed-vs-unperturbed within each timing/size.

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
TIMING_PATH = os.path.join(OUTPUT_DIR, "timing_sweep.json")
SIZE_PATH = os.path.join(OUTPUT_DIR, "size_sweep.json")

GRID = 160
JITTER = 10.0
STEPS = 2000

SEEDS_8 = [42, 123, 256, 999, 7, 100, 555, 777]

# Regime: n=350 g=0.01 (the robust optimum)
N_TERMITES = 350
G_FORM = 0.01
G_PERSIST = 0.01


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


def run_one(p, seed, n_seeds, perturb_at=None, perturb_frac=0.5):
    """Run one simulation, optionally perturbed."""
    if perturb_at is not None:
        r = I14.run_two_region_hetero(
            p, seed=seed, n_seeds=n_seeds, mode="hetero",
            perturb_at=perturb_at, perturb_frac=perturb_frac)
    else:
        r = I14.run_two_region_hetero(
            p, seed=seed, n_seeds=n_seeds, mode="hetero")
    return r


def extract_metrics(result, perturb_at, perturb_frac):
    """Extract key metrics from a run result."""
    s = result["summary"]
    h = result["history"]

    pre_right = []
    post_right = []
    pre_l2 = []
    post_l2 = []

    for rec in h:
        step = rec.get("step", 0)
        rt = rec.get("right_total", 0.0)
        lc = rec.get("left_components", 0)
        rc = rec.get("right_components", 0)
        l2_state = (lc >= 1 and rc >= 1)

        if perturb_at is not None:
            if step < perturb_at:
                pre_right.append(rt)
                pre_l2.append(l2_state)
            else:
                post_right.append(rt)
                post_l2.append(l2_state)
        else:
            # Unperturbed: use perturb_at as the split point for comparison
            if step < perturb_at:
                pre_right.append(rt)
                pre_l2.append(l2_state)
            else:
                post_right.append(rt)
                post_l2.append(l2_state)

    pre_right_mean = float(np.mean(pre_right)) if pre_right else 0.0
    post_right_mean = float(np.mean(post_right)) if post_right else 0.0
    recovery_ratio = post_right_mean / max(pre_right_mean, 1e-9)

    # Coexist frac in the late window (after perturbation)
    late_recs = [r for r in h if r.get("step", 0) >= perturb_at]
    coexist_count = 0
    for r in late_recs:
        lc = r.get("left_components", 0)
        rc = r.get("right_components", 0)
        if 1 <= lc <= 3 and 1 <= rc <= 3:
            coexist_count += 1
    late_coexist_frac = coexist_count / max(len(late_recs), 1)

    # Pre-perturbation coexist frac
    pre_recs = [r for r in h if r.get("step", 0) < perturb_at]
    pre_coexist = 0
    for r in pre_recs:
        lc = r.get("left_components", 0)
        rc = r.get("right_components", 0)
        if 1 <= lc <= 3 and 1 <= rc <= 3:
            pre_coexist += 1
    pre_coexist_frac = pre_coexist / max(len(pre_recs), 1)

    return {
        "l2_crossed": s["l2_crossed"],
        "l2_outcome": s["l2_outcome"],
        "l2_stable": s["l2_stable"],
        "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
        "crossed_h7": s["crossed_h7"],
        "cells": s["final_n_structure_cells"],
        "recovery_ratio": round(recovery_ratio, 4),
        "pre_right_mean": round(pre_right_mean, 1),
        "post_right_mean": round(post_right_mean, 1),
        "late_coexist_frac": round(late_coexist_frac, 3),
        "pre_coexist_frac": round(pre_coexist_frac, 3),
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
        "mean_pre_cf": round(float(np.mean([e['pre_coexist_frac'] for e in entries_2])), 3),
        "mean_post_cf": round(float(np.mean([e['late_coexist_frac'] for e in entries_2])), 3),
        "mean_cells": int(np.mean([e['cells'] for e in entries_2])),
    }


# ----------------------------------------------------------------- #
# Part A — timing sweep
# ----------------------------------------------------------------- #
def run_timing_sweep():
    t0 = time.time()
    p = make_params(N_TERMITES, G_FORM, G_PERSIST)
    timing_levels = [1200, 1600, 1800]  # 60%, 80%, 90%
    perturb_frac = 0.50

    results = {"config": {
        "grid": GRID, "n_termites": N_TERMITES,
        "g_form": G_FORM, "g_persist": G_PERSIST,
        "jitter": JITTER, "steps": STEPS,
        "perturb_frac": perturb_frac,
        "seeds": SEEDS_8,
        "note": "Session 56: timing sweep — is over-recovery genuine? (#162)",
    }}

    print(f"\n{'='*80}")
    print(f"  TIMING SWEEP: n={N_TERMITES} g={G_FORM} perturb_frac={perturb_frac}")
    print(f"  perturb_at ∈ {timing_levels} (60%, 80%, 90% of {STEPS})")
    print(f"  8 seeds × {{perturbed, unperturbed}} × {{2, 1}} = 96 runs")
    print(f"{'='*80}")

    for pa in timing_levels:
        label = f"pa{pa}"
        print(f"\n  Timing {label} ({pa}/{STEPS} = {100*pa/STEPS:.0f}%)")

        unper_2 = []
        unper_1 = []
        per_2 = []
        per_1 = []

        for sd in SEEDS_8:
            # Unperturbed 2-seed
            r = run_one(p, sd, 2, perturb_at=None)
            m = extract_metrics(r, pa, perturb_frac)
            m["seed"] = sd
            unper_2.append(m)

            # Perturbed 2-seed
            r = run_one(p, sd, 2, perturb_at=pa, perturb_frac=perturb_frac)
            m = extract_metrics(r, pa, perturb_frac)
            m["seed"] = sd
            per_2.append(m)
            print(f"    [{label}] PERT 2s s={sd}: h7={m['crossed_h7']} "
                  f"out={m['l2_outcome']:>12s} stable={m['l2_stable']} "
                  f"cf={m['l2_coexist_frac']:.2f} "
                  f"rec={m['recovery_ratio']:.3f} "
                  f"pre_r={m['pre_right_mean']:.0f} "
                  f"post_r={m['post_right_mean']:.0f} "
                  f"pre_cf={m['pre_coexist_frac']:.2f} "
                  f"post_cf={m['late_coexist_frac']:.2f}")

            # Unperturbed 1-seed
            r = run_one(p, sd, 1, perturb_at=None)
            m = extract_metrics(r, pa, perturb_frac)
            m["seed"] = sd
            unper_1.append(m)

            # Perturbed 1-seed
            r = run_one(p, sd, 1, perturb_at=pa, perturb_frac=perturb_frac)
            m = extract_metrics(r, pa, perturb_frac)
            m["seed"] = sd
            per_1.append(m)

        su = summarize(unper_2, unper_1, 8)
        sp = summarize(per_2, per_1, 8)
        print(f"\n  {label} UNPERT: l2={su['l2']} coexist={su['coexist']} "
              f"stable={su['stable']} h7={su['h7']} full={su['full']} "
              f"cf={su['mean_cf']:.3f}")
        print(f"  {label} PERT:   l2={sp['l2']} coexist={sp['coexist']} "
              f"stable={sp['stable']} h7={sp['h7']} full={sp['full']} "
              f"cf={sp['mean_cf']:.3f} rec={sp['mean_recovery']:.3f} "
              f"pre_cf={sp['mean_pre_cf']:.3f} post_cf={sp['mean_post_cf']:.3f}")

        results[label] = {
            "perturb_at": pa,
            "perturb_frac": perturb_frac,
            "pct_of_steps": round(100 * pa / STEPS, 1),
            "unperturbed": {
                "2seed": unper_2, "1seed": unper_1,
                "summary": su,
            },
            "perturbed": {
                "2seed": per_2, "1seed": per_1,
                "summary": sp,
            },
        }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(TIMING_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*100}")
    print(f"  TIMING SWEEP SUMMARY (n=350, g=0.01, 160x160, dual, focal 0.3, jit=10)")
    print(f"  perturb_frac=0.50, perturb_at varies")
    print(f"{'='*100}")
    print(f"{'timing':>10s} {'pct':>5s} | "
          f"{'unper_cf':>8s} {'per_cf':>7s} | "
          f"{'unper_h7':>8s} {'per_h7':>7s} | "
          f"{'unper_st':>8s} {'per_st':>7s} | "
          f"{'recovery':>8s} {'cells':>6s}")
    print("-" * 100)
    for pa in timing_levels:
        label = f"pa{pa}"
        if label not in results:
            continue
        su = results[label]["unperturbed"]["summary"]
        sp = results[label]["perturbed"]["summary"]
        print(f"{label:>10s} {100*pa/STEPS:>4.0f}% | "
              f"{su['mean_cf']:>8.3f} {sp['mean_cf']:>7.3f} | "
              f"{su['h7']:>8s} {sp['h7']:>7s} | "
              f"{su['stable']:>8s} {sp['stable']:>7s} | "
              f"{sp['mean_recovery']:>8.3f} {sp['mean_cells']:>6d}")

    elapsed = time.time() - t0
    print(f"\nWrote {TIMING_PATH}  ({elapsed:.1f}s)")
    return results


# ----------------------------------------------------------------- #
# Part B — size sweep
# ----------------------------------------------------------------- #
def run_size_sweep():
    t0 = time.time()
    p = make_params(N_TERMITES, G_FORM, G_PERSIST)
    perturb_at = 1200  # 60% (same as Session 55)
    size_levels = [0.25, 0.50, 0.75, 0.90]

    results = {"config": {
        "grid": GRID, "n_termites": N_TERMITES,
        "g_form": G_FORM, "g_persist": G_PERSIST,
        "jitter": JITTER, "steps": STEPS,
        "perturb_at": perturb_at,
        "seeds": SEEDS_8,
        "note": "Session 56: size sweep — does the damage signal saturate? (#163)",
    }}

    print(f"\n{'='*80}")
    print(f"  SIZE SWEEP: n={N_TERMITES} g={G_FORM} perturb_at={perturb_at}")
    print(f"  perturb_frac ∈ {size_levels}")
    print(f"  8 seeds × {{perturbed, unperturbed}} × {{2, 1}} = 96 runs")
    print(f"{'='*80}")

    # Pre-compute unperturbed runs once (they don't change with perturb_frac).
    print(f"\n  Pre-computing unperturbed baseline...")
    unper_2_all = []
    unper_1_all = []
    for sd in SEEDS_8:
        r2 = run_one(p, sd, 2, perturb_at=None)
        m2 = extract_metrics(r2, perturb_at, 0.5)
        m2["seed"] = sd
        unper_2_all.append(m2)

        r1 = run_one(p, sd, 1, perturb_at=None)
        m1 = extract_metrics(r1, perturb_at, 0.5)
        m1["seed"] = sd
        unper_1_all.append(m1)

    su_baseline = summarize(unper_2_all, unper_1_all, 8)
    print(f"  BASELINE: l2={su_baseline['l2']} coexist={su_baseline['coexist']} "
          f"stable={su_baseline['stable']} h7={su_baseline['h7']} "
          f"full={su_baseline['full']} cf={su_baseline['mean_cf']:.3f}")

    for pf in size_levels:
        label = f"pf{int(pf*100):02d}"
        print(f"\n  Size {label} (perturb_frac={pf})")

        per_2 = []
        per_1 = []

        for sd in SEEDS_8:
            # Perturbed 2-seed
            r = run_one(p, sd, 2, perturb_at=perturb_at, perturb_frac=pf)
            m = extract_metrics(r, perturb_at, pf)
            m["seed"] = sd
            per_2.append(m)
            print(f"    [{label}] PERT 2s s={sd}: h7={m['crossed_h7']} "
                  f"out={m['l2_outcome']:>12s} stable={m['l2_stable']} "
                  f"cf={m['l2_coexist_frac']:.2f} "
                  f"rec={m['recovery_ratio']:.3f} "
                  f"pre_r={m['pre_right_mean']:.0f} "
                  f"post_r={m['post_right_mean']:.0f}")

            # Perturbed 1-seed
            r = run_one(p, sd, 1, perturb_at=perturb_at, perturb_frac=pf)
            m = extract_metrics(r, perturb_at, pf)
            m["seed"] = sd
            per_1.append(m)

        su = su_baseline
        sp = summarize(per_2, per_1, 8)
        print(f"\n  {label} UNPERT: l2={su['l2']} coexist={su['coexist']} "
              f"stable={su['stable']} h7={su['h7']} full={su['full']} "
              f"cf={su['mean_cf']:.3f}")
        print(f"  {label} PERT:   l2={sp['l2']} coexist={sp['coexist']} "
              f"stable={sp['stable']} h7={sp['h7']} full={sp['full']} "
              f"cf={sp['mean_cf']:.3f} rec={sp['mean_recovery']:.3f}")

        results[label] = {
            "perturb_at": perturb_at,
            "perturb_frac": pf,
            "unperturbed": {
                "2seed": unper_2_all, "1seed": unper_1_all,
                "summary": su,
            },
            "perturbed": {
                "2seed": per_2, "1seed": per_1,
                "summary": sp,
            },
        }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(SIZE_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*100}")
    print(f"  SIZE SWEEP SUMMARY (n=350, g=0.01, 160x160, dual, focal 0.3, jit=10)")
    print(f"  perturb_at=1200 (60%), perturb_frac varies")
    print(f"{'='*100}")
    print(f"{'size':>6s} {'frac':>5s} | "
          f"{'per_cf':>7s} | "
          f"{'per_h7':>7s} {'per_st':>7s} | "
          f"{'recovery':>8s} {'cells':>6s}")
    print("-" * 100)
    for pf in size_levels:
        label = f"pf{int(pf*100):02d}"
        if label not in results:
            continue
        sp = results[label]["perturbed"]["summary"]
        print(f"{label:>6s} {pf:>5.2f} | "
              f"{sp['mean_cf']:>7.3f} | "
              f"{sp['h7']:>7s} {sp['stable']:>7s} | "
              f"{sp['mean_recovery']:>8.3f} {sp['mean_cells']:>6d}")

    elapsed = time.time() - t0
    print(f"\nWrote {SIZE_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    # Run both sweeps
    timing_results = run_timing_sweep()
    size_results = run_size_sweep()
