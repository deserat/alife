"""
Saturating-cue perturbation control — does the saturating-cue channel
also show damage-amplified composition? (queued-topic #164)

Session 56 found the 33rd mechanism: damage-amplified composition —
larger damage produces BETTER composition (75%/90% → 8/8 full vs 4/8 at
25%) at n=350 g=0.01 with the non-saturating curvature channel. The
mechanism: more damage creates more curvature contrast at the scar,
sharpening the boundary.

Is this unique to the non-saturating curvature channel, or does the
saturating-cue channel (sim06's pheromone) also benefit from damage?

The saturating cue's deposit probability is p = base + gain·φ/(1+φ).
Damage reduces material → reduces pheromone → reduces deposit
probability at the scar. The curvature channel INCREASES deposit
probability at the scar (more curvature at the edge). The question:
does the saturating cue also show damage-amplified recovery, or does
it show damage-suppressed recovery (the expected saturating-cue
behavior)?

Design:
  Size sweep: n=350, 8 seeds, perturb_at=1200 (60%)
  perturb_frac ∈ {0.25, 0.50, 0.75, 0.90}
  × {perturbed, unperturbed} × {2, 1} = 96 runs
  Two channels: "curvature" (treatment) and "baseline_pheromone" (control)
  Total: 192 runs

The curvature channel results are already committed (Session 56's
size_sweep.json). We re-run them for a clean side-by-side comparison
and to verify determinism.

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
RESULTS_PATH = os.path.join(OUTPUT_DIR, "saturating_cue_sweep.json")

GRID = 160
JITTER = 10.0
STEPS = 2000

SEEDS_8 = [42, 123, 256, 999, 7, 100, 555, 777]

# Regime: n=350 g=0.01 (the robust optimum from Session 54)
N_TERMITES = 350
G_FORM = 0.01
G_PERSIST = 0.01


def make_params(n_termites, g_form, g_persist, channel="curvature"):
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
    p["channel"] = channel
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

    for rec in h:
        step = rec.get("step", 0)
        rt = rec.get("right_total", 0.0)

        if step < perturb_at:
            pre_right.append(rt)
        else:
            post_right.append(rt)

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
        "mean_cells": int(np.mean([e['cells'] for e in entries_2])),
    }


def run_channel_sweep(channel_name, perturb_at, size_levels):
    """Run the size sweep for one channel."""
    t0 = time.time()
    p = make_params(N_TERMITES, G_FORM, G_PERSIST, channel=channel_name)

    print(f"\n{'='*80}")
    print(f"  CHANNEL: {channel_name}")
    print(f"  SIZE SWEEP: n={N_TERMITES} g={G_FORM} perturb_at={perturb_at}")
    print(f"  perturb_frac ∈ {size_levels}")
    print(f"  8 seeds × {{perturbed, unperturbed}} × {{2, 1}} = 96 runs")
    print(f"{'='*80}")

    # Pre-compute unperturbed runs once
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

    results = {"config": {
        "channel": channel_name,
        "grid": GRID, "n_termites": N_TERMITES,
        "g_form": G_FORM, "g_persist": G_PERSIST,
        "jitter": JITTER, "steps": STEPS,
        "perturb_at": perturb_at,
        "seeds": SEEDS_8,
        "note": f"Session 57: saturating-cue control — channel={channel_name} (#164)",
    }}

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

    elapsed = time.time() - t0
    print(f"\n  Channel {channel_name} elapsed: {elapsed:.1f}s")
    return results, su_baseline


if __name__ == "__main__":
    perturb_at = 1200  # 60% (same as Session 56)
    size_levels = [0.25, 0.50, 0.75, 0.90]

    t0 = time.time()

    # Run both channels
    curv_results, curv_baseline = run_channel_sweep("curvature", perturb_at, size_levels)
    pher_results, pher_baseline = run_channel_sweep("baseline_pheromone", perturb_at, size_levels)

    # Save combined results
    all_results = {
        "curvature": curv_results,
        "baseline_pheromone": pher_results,
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Summary comparison table
    print(f"\n{'='*100}")
    print(f"  SATURATING-CUE CONTROL COMPARISON (n=350, g=0.01, 160x160, dual, focal 0.3, jit=10)")
    print(f"  perturb_at=1200 (60%), perturb_frac varies")
    print(f"{'='*100}")
    print(f"{'channel':>20s} {'size':>6s} | "
          f"{'per_h7':>7s} {'per_co':>7s} {'per_st':>7s} {'per_full':>8s} | "
          f"{'recovery':>8s} {'cf':>6s} {'cells':>6s}")
    print("-" * 100)
    for channel_name, results in [("curvature", curv_results), ("baseline_pheromone", pher_results)]:
        for pf in size_levels:
            label = f"pf{int(pf*100):02d}"
            if label not in results:
                continue
            sp = results[label]["perturbed"]["summary"]
            print(f"{channel_name:>20s} {label:>6s} | "
                  f"{sp['h7']:>7s} {sp['coexist']:>7s} {sp['stable']:>7s} {sp['full']:>8s} | "
                  f"{sp['mean_recovery']:>8.3f} {sp['mean_cf']:>6.3f} {sp['mean_cells']:>6d}")

    # Determinism verification
    print(f"\n  Determinism check...")
    p_curv = make_params(N_TERMITES, G_FORM, G_PERSIST, channel="curvature")
    p_pher = make_params(N_TERMITES, G_FORM, G_PERSIST, channel="baseline_pheromone")

    r1 = run_one(p_curv, 42, 2, perturb_at=perturb_at, perturb_frac=0.50)
    r2 = run_one(p_curv, 42, 2, perturb_at=perturb_at, perturb_frac=0.50)
    m1 = extract_metrics(r1, perturb_at, 0.50)
    m2 = extract_metrics(r2, perturb_at, 0.50)
    det_curv = (m1["cells"] == m2["cells"] and m1["recovery_ratio"] == m2["recovery_ratio"])
    print(f"  Curvature det: cells={m1['cells']} vs {m2['cells']} → {'OK' if det_curv else 'FAIL'}")

    r1 = run_one(p_pher, 42, 2, perturb_at=perturb_at, perturb_frac=0.50)
    r2 = run_one(p_pher, 42, 2, perturb_at=perturb_at, perturb_frac=0.50)
    m1 = extract_metrics(r1, perturb_at, 0.50)
    m2 = extract_metrics(r2, perturb_at, 0.50)
    det_pher = (m1["cells"] == m2["cells"] and m1["recovery_ratio"] == m2["recovery_ratio"])
    print(f"  Pheromone det: cells={m1['cells']} vs {m2['cells']} → {'OK' if det_pher else 'FAIL'}")

    elapsed = time.time() - t0
    print(f"\nTotal elapsed: {elapsed:.1f}s")
    print(f"Wrote {RESULTS_PATH}")
