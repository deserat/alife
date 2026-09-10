"""
Perturbation robustness: is the crossing a stability condition?

Queued-topic #127: "The crossing as a stability condition, not a composition
mechanism." At n=150, composition (4/4 coexist) occurs with only 2/4 H7. At
n=350 g=0.01 (robust optimum), H7=8/8 AND coexist=8/8. If H7 is what makes
composition *stable* (survive perturbation), then perturbed runs at n=350
(H7 high) should preserve coexistence better than perturbed runs at n=150
(H7 low), relative to their unperturbed baselines.

Design:
  Three density regimes × {perturbed, unperturbed} × 8 seeds × {2, 1}.

  Regimes (all 160×160, dual, focal 0.3, jit=10):
    A. n=150 g=0.30  — composition works, crossing doesn't (4/4 coexist, 2/4 H7)
    B. n=350 g=0.01  — robust optimum (8/8 coexist, 8/8 H7, 7/8 full)
    C. n=500 g=0.02  — ultra-high density (4/4 full, 1-seed 0/4 perfect)

  Perturbation: 50% of right region material removed at 60% of steps (step 1200
  of 2000). This is the same perturbation mechanism as sim09's Part 8, applied
  to the two-region hetero setup.

  Metrics:
    - coexist survival: does coexistence persist after perturbation?
    - coexist_frac pre vs post: does the coexistence fraction drop?
    - H7 survival: does the crossing survive perturbation?
    - recovery_ratio: right_total(post) / right_total(pre)

  The control arm: the unperturbed runs at the same configs. The comparison
  is perturbed-vs-unperturbed within each regime. If the crossing is a
  stability condition, the drop from unperturbed to perturbed should be
  SMALLER at n=350 (H7 high) than at n=150 (H7 low).

  Per-criterion pass rates are reported for every null.
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

SWEEP_PATH = os.path.join(SIM14_DIR, "output", "perturbation_sweep.json")

GRID = 160
JITTER = 10.0
STEPS = 2000
PERTURB_AT = 1200  # 60% of steps
PERTURB_FRAC = 0.50  # remove 50% of right region material

SEEDS_8 = [42, 123, 256, 999, 7, 100, 555, 777]

# Three regimes: (n_termites, g_form, g_persist, label)
REGIMES = [
    (150, 0.30, 0.30, "n150_g030"),   # composition w/o crossing
    (350, 0.01, 0.01, "n350_g010"),   # robust optimum
    (500, 0.02, 0.02, "n500_g020"),   # ultra-high density
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


def run_one(p, seed, n_seeds, perturb=False):
    """Run one simulation, optionally perturbed."""
    if perturb:
        r = I14.run_two_region_hetero(
            p, seed=seed, n_seeds=n_seeds, mode="hetero",
            perturb_at=PERTURB_AT, perturb_frac=PERTURB_FRAC)
    else:
        r = I14.run_two_region_hetero(
            p, seed=seed, n_seeds=n_seeds, mode="hetero")
    return r


def extract_metrics(result, perturb=False):
    """Extract key metrics from a run result."""
    s = result["summary"]
    h = result["history"]
    bt = result.get("boundary_trace", [])

    # Find pre/post perturbation metrics
    pre_right = []
    post_right = []
    pre_left = []
    post_left = []
    pre_l2 = []
    post_l2 = []

    for rec in h:
        step = rec.get("step", 0)
        rt = rec.get("right_total", 0.0)
        lt = rec.get("left_total", 0.0)
        lc = rec.get("left_components", 0)
        rc = rec.get("right_components", 0)
        l2_state = (lc >= 1 and rc >= 1)

        if perturb and step < PERTURB_AT:
            pre_right.append(rt)
            pre_left.append(lt)
            pre_l2.append(l2_state)
        elif perturb and step >= PERTURB_AT:
            post_right.append(rt)
            post_left.append(lt)
            post_l2.append(l2_state)
        # For unperturbed, use the same split point for comparison
        elif not perturb and step < PERTURB_AT:
            pre_right.append(rt)
            pre_left.append(lt)
            pre_l2.append(l2_state)
        elif not perturb and step >= PERTURB_AT:
            post_right.append(rt)
            post_left.append(lt)
            post_l2.append(l2_state)

    pre_right_mean = float(np.mean(pre_right)) if pre_right else 0.0
    post_right_mean = float(np.mean(post_right)) if post_right else 0.0
    pre_left_mean = float(np.mean(pre_left)) if pre_left else 0.0
    post_left_mean = float(np.mean(post_left)) if post_left else 0.0

    recovery_ratio = post_right_mean / max(pre_right_mean, 1e-9)

    pre_l2_frac = float(np.mean(pre_l2)) if pre_l2 else 0.0
    post_l2_frac = float(np.mean(post_l2)) if post_l2 else 0.0

    # Coexist frac (fraction of late window in coexist state)
    # For perturbed runs, late window starts AFTER perturbation
    late_start_idx = None
    for i, rec in enumerate(h):
        if perturb and rec.get("step", 0) >= PERTURB_AT:
            late_start_idx = i
            break
        elif not perturb and rec.get("step", 0) >= PERTURB_AT:
            late_start_idx = i
            break
    if late_start_idx is None:
        late_start_idx = len(h) // 2  # fallback

    late_recs = h[late_start_idx:]
    coexist_count = 0
    for r in late_recs:
        lc = r.get("left_components", 0)
        rc = r.get("right_components", 0)
        coexist_max = 3  # COEXIST_MAX_COMP
        if 1 <= lc <= coexist_max and 1 <= rc <= coexist_max:
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
        "pre_right_mean": round(pre_right_mean, 1),
        "post_right_mean": round(post_right_mean, 1),
        "pre_left_mean": round(pre_left_mean, 1),
        "post_left_mean": round(post_left_mean, 1),
        "pre_l2_frac": round(pre_l2_frac, 3),
        "post_l2_frac": round(post_l2_frac, 3),
        "late_coexist_frac": round(late_coexist_frac, 3),
    }


def run_regime(n, gf, gp, label, seeds):
    """Run one regime: perturbed + unperturbed × seeds × {2, 1}."""
    p = make_params(n, gf, gp)
    density = n / (GRID * GRID) * 1000

    unper_2 = []
    unper_1 = []
    per_2 = []
    per_1 = []

    for sd in seeds:
        # Unperturbed 2-seed
        r = run_one(p, sd, n_seeds=2, perturb=False)
        m = extract_metrics(r, perturb=False)
        m["seed"] = sd
        unper_2.append(m)
        print(f"    [{label}] unper 2s s={sd}: l2={m['l2_crossed']} "
              f"out={m['l2_outcome']:>12s} stable={m['l2_stable']} "
              f"h7={m['crossed_h7']} cf={m['l2_coexist_frac']:.2f} "
              f"cells={m['cells']}")

        # Perturbed 2-seed
        r = run_one(p, sd, n_seeds=2, perturb=True)
        m = extract_metrics(r, perturb=True)
        m["seed"] = sd
        per_2.append(m)
        print(f"    [{label}] PERT   2s s={sd}: l2={m['l2_crossed']} "
              f"out={m['l2_outcome']:>12s} stable={m['l2_stable']} "
              f"h7={m['crossed_h7']} cf={m['l2_coexist_frac']:.2f} "
              f"rec={m['recovery_ratio']:.2f} "
              f"pre_l2={m['pre_l2_frac']:.2f} post_l2={m['post_l2_frac']:.2f} "
              f"cells={m['cells']}")

        # Unperturbed 1-seed
        r = run_one(p, sd, n_seeds=1, perturb=False)
        m = extract_metrics(r, perturb=False)
        m["seed"] = sd
        unper_1.append(m)

        # Perturbed 1-seed
        r = run_one(p, sd, n_seeds=1, perturb=True)
        m = extract_metrics(r, perturb=True)
        m["seed"] = sd
        per_1.append(m)

    return unper_2, unper_1, per_2, per_1, density


def summarize_regime(entries_2, entries_1, n_seeds):
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
        "mean_pre_l2": round(float(np.mean([e['pre_l2_frac'] for e in entries_2])), 3),
        "mean_post_l2": round(float(np.mean([e['post_l2_frac'] for e in entries_2])), 3),
        "mean_late_coexist": round(float(np.mean([e['late_coexist_frac'] for e in entries_2])), 3),
        "mean_cells": int(np.mean([e['cells'] for e in entries_2])),
    }


def run_sweep():
    t0 = time.time()

    results = {"config": {
        "grid": GRID,
        "jitter": JITTER,
        "steps": STEPS,
        "perturb_at": PERTURB_AT,
        "perturb_frac": PERTURB_FRAC,
        "seeds": SEEDS_8,
        "note": "Session 55: perturbation robustness — is the crossing "
                "a stability condition? (#127)",
    }}

    print(f"\n{'='*80}")
    print(f"  PERTURBATION ROBUSTNESS SWEEP")
    print(f"  3 regimes × {{perturbed, unperturbed}} × 8 seeds × {{2, 1}}")
    print(f"  Perturbation: {PERTURB_FRAC*100:.0f}% of right region at step {PERTURB_AT}/{STEPS}")
    print(f"{'='*80}")

    for n, gf, gp, label in REGIMES:
        print(f"\n  Regime {label} (n={n}, g=({gf},{gp}))")
        unper_2, unper_1, per_2, per_1, density = run_regime(
            n, gf, gp, label, SEEDS_8)

        results[label] = {
            "n_termites": n,
            "g_form": gf,
            "g_persist": gp,
            "density_per_kcell": round(density, 2),
            "unperturbed": {
                "2seed": unper_2,
                "1seed": unper_1,
                "summary": summarize_regime(unper_2, unper_1, 8),
            },
            "perturbed": {
                "2seed": per_2,
                "1seed": per_1,
                "summary": summarize_regime(per_2, per_1, 8),
            },
        }

        su = results[label]["unperturbed"]["summary"]
        sp = results[label]["perturbed"]["summary"]
        print(f"\n  {label} UNPERTURBED: l2={su['l2']} coexist={su['coexist']} "
              f"stable={su['stable']} h7={su['h7']} full={su['full']} "
              f"cf={su['mean_cf']:.3f} pre_l2={su['mean_pre_l2']:.3f} "
              f"post_l2={su['mean_post_l2']:.3f}")
        print(f"  {label} PERTURBED:   l2={sp['l2']} coexist={sp['coexist']} "
              f"stable={sp['stable']} h7={sp['h7']} full={sp['full']} "
              f"cf={sp['mean_cf']:.3f} rec={sp['mean_recovery']:.3f} "
              f"pre_l2={sp['mean_pre_l2']:.3f} post_l2={sp['mean_post_l2']:.3f}")

    # Save
    os.makedirs(os.path.dirname(SWEEP_PATH), exist_ok=True)
    with open(SWEEP_PATH, "w") as f:
        json.dump(S._pyify(results), f, indent=2)

    # Summary table
    print(f"\n{'='*120}")
    print(f"  PERTURBATION ROBUSTNESS SUMMARY (160x160, dual, focal 0.3, jit=10)")
    print(f"  Perturbation: 50% right material removed at step {PERTURB_AT}/{STEPS}")
    print(f"{'='*120}")
    print(f"{'regime':>15s} {'nT':>5s} {'g':>5s} | "
          f"{'unper':>6s} {'per':>6s} | "
          f"{'coex_u':>6s} {'coex_p':>6s} | "
          f"{'h7_u':>5s} {'h7_p':>5s} | "
          f"{'cf_u':>5s} {'cf_p':>5s} | "
          f"{'rec':>5s} {'cells':>6s}")
    print("-" * 120)

    for n, gf, gp, label in REGIMES:
        if label not in results:
            continue
        su = results[label]["unperturbed"]["summary"]
        sp = results[label]["perturbed"]["summary"]
        print(f"{label:>15s} {n:>5d} {gf:>5.3f} | "
              f"{su['l2']:>6s} {sp['l2']:>6s} | "
              f"{su['coexist']:>6s} {sp['coexist']:>6s} | "
              f"{su['h7']:>5s} {sp['h7']:>5s} | "
              f"{su['mean_cf']:>5.3f} {sp['mean_cf']:>5.3f} | "
              f"{sp['mean_recovery']:>5.3f} {sp['mean_cells']:>6d}")

    elapsed = time.time() - t0
    print(f"\nWrote {SWEEP_PATH}  ({elapsed:.1f}s)")
    return results


if __name__ == "__main__":
    run_sweep()
