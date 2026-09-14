"""Asymmetric bilateral sweep - perturbed-only version (no unperturbed baseline)."""
import os, sys, json, time
import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14
import sim09 as S

OUTPUT_DIR = os.path.join(SIM14_DIR, "output")
RESULTS_PATH = os.path.join(OUTPUT_DIR, "asymmetric_bilateral_sweep.json")

GRID = 160
JITTER = 10.0
STEPS = 2000
PERTURB_AT = 1200

SEEDS = [42, 123, 256, 999]
N_TERMITES = 350
G_FORM = 0.01
G_PERSIST = 0.01

# (pf_left, pf_right, label)
CONFIGS = [
    (0.50, 0.50, "50_50"),
    (0.50, 0.90, "50_90"),
    (0.90, 0.50, "90_50"),
    (0.90, 0.90, "90_90"),
    (0.25, 0.50, "25_50"),
]


def make_params(n, gf, gp):
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = n
    p["boundary_mode"] = "dual"
    p["g_form"] = gf
    p["g_persist"] = gp
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def extract_metrics(result, perturb_at):
    s = result["summary"]
    h = result["history"]
    pre_total, post_total = [], []
    pre_left, pre_right, post_left, post_right = [], [], [], []
    for rec in h:
        step = rec.get("step", 0)
        rt = rec.get("right_total", 0.0)
        lt = rec.get("left_total", 0.0)
        total = rt + lt
        if step < perturb_at:
            pre_total.append(total); pre_left.append(lt); pre_right.append(rt)
        else:
            post_total.append(total); post_left.append(lt); post_right.append(rt)
    pre_tm = float(np.mean(pre_total)) if pre_total else 0.0
    post_tm = float(np.mean(post_total)) if post_total else 0.0
    total_rec = post_tm / max(pre_tm, 1e-9)
    pre_lm = float(np.mean(pre_left)) if pre_left else 0.0
    post_lm = float(np.mean(post_left)) if post_left else 0.0
    left_rec = post_lm / max(pre_lm, 1e-9)
    pre_rm = float(np.mean(pre_right)) if pre_right else 0.0
    post_rm = float(np.mean(post_right)) if post_right else 0.0
    right_rec = post_rm / max(pre_rm, 1e-9)
    return {
        "l2_crossed": s["l2_crossed"], "l2_outcome": s["l2_outcome"],
        "l2_stable": s["l2_stable"],
        "l2_coexist_frac": round(s.get("l2_coexist_frac", 0.0), 3),
        "crossed_h7": s["crossed_h7"],
        "cells": s["final_n_structure_cells"],
        "total_recovery": round(total_rec, 4),
        "left_recovery": round(left_rec, 4),
        "right_recovery": round(right_rec, 4),
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
        "mean_left_rec": round(float(np.mean([e['left_recovery'] for e in entries_2])), 3),
        "mean_right_rec": round(float(np.mean([e['right_recovery'] for e in entries_2])), 3),
        "mean_cells": int(np.mean([e['cells'] for e in entries_2])),
    }


if __name__ == "__main__":
    t0 = time.time()
    p = make_params(N_TERMITES, G_FORM, G_PERSIST)

    all_results = {}

    for pf_left, pf_right, label in CONFIGS:
        print(f"\n{'='*60}")
        print(f"  {label} (L={pf_left*100:.0f}% R={pf_right*100:.0f}%)")
        print(f"{'='*60}")
        per_2, per_1 = [], []
        for sd in SEEDS:
            r2 = I14.run_two_region_hetero(p, seed=sd, n_seeds=2, mode="hetero",
                perturb_at=PERTURB_AT, perturb_side="both",
                perturb_frac_left=pf_left, perturb_frac_right=pf_right)
            m2 = extract_metrics(r2, PERTURB_AT); m2["seed"] = sd; per_2.append(m2)
            print(f"    2s s={sd}: h7={m2['crossed_h7']} out={m2['l2_outcome']:>12s} "
                  f"stable={m2['l2_stable']} cf={m2['l2_coexist_frac']:.2f} "
                  f"tot_rec={m2['total_recovery']:.3f} L={m2['left_recovery']:.3f} "
                  f"R={m2['right_recovery']:.3f} cells={m2['cells']}")
            r1 = I14.run_two_region_hetero(p, seed=sd, n_seeds=1, mode="hetero",
                perturb_at=PERTURB_AT, perturb_side="both",
                perturb_frac_left=pf_left, perturb_frac_right=pf_right)
            m1 = extract_metrics(r1, PERTURB_AT); m1["seed"] = sd; per_1.append(m1)
        sp = summarize(per_2, per_1, len(SEEDS))
        print(f"  {label}: h7={sp['h7']} coexist={sp['coexist']} stable={sp['stable']} "
              f"full={sp['full']} cf={sp['mean_cf']:.3f} tot_rec={sp['mean_total_rec']:.3f} "
              f"L_rec={sp['mean_left_rec']:.3f} R_rec={sp['mean_right_rec']:.3f} "
              f"1s_l2={sp['l2_1s']}")
        all_results[label] = {"pf_left": pf_left, "pf_right": pf_right,
            "perturbed": {"2seed": per_2, "1seed": per_1, "summary": sp}}

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(S._pyify(all_results), f, indent=2)

    # Determinism
    print("\n  Determinism check...")
    for lbl in ["50_50", "50_90"]:
        pf_l, pf_r, _ = [(l,r,lb) for l,r,lb in CONFIGS if lb==lbl][0]
        r1 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero",
            perturb_at=PERTURB_AT, perturb_side="both",
            perturb_frac_left=pf_l, perturb_frac_right=pf_r)
        r2 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero",
            perturb_at=PERTURB_AT, perturb_side="both",
            perturb_frac_left=pf_l, perturb_frac_right=pf_r)
        m1 = extract_metrics(r1, PERTURB_AT); m2 = extract_metrics(r2, PERTURB_AT)
        det = m1["cells"]==m2["cells"] and m1["total_recovery"]==m2["total_recovery"]
        print(f"  {lbl}: {'OK' if det else 'FAIL'} ({m1['cells']} vs {m2['cells']})")

    print(f"\n{'='*110}")
    print(f"  SUMMARY (n=350 g=0.01 160x160 dual focal=0.3 jit=10 perturb_at=1200)")
    print(f"{'config':>8s} {'L%':>5s} {'R%':>5s} | {'h7':>5s} {'co':>5s} {'st':>5s} "
          f"{'full':>5s} | {'cf':>6s} {'totR':>7s} {'Lrec':>7s} {'Rrec':>7s} {'1s':>5s}")
    print("-"*110)
    for _, _, lbl in CONFIGS:
        if lbl not in all_results: continue
        sp = all_results[lbl]["perturbed"]["summary"]
        pfl = all_results[lbl]["pf_left"]; pfr = all_results[lbl]["pf_right"]
        print(f"{lbl:>8s} {pfl*100:>4.0f}% {pfr*100:>4.0f}% | "
              f"{sp['h7']:>5s} {sp['coexist'].split('/')[0]:>5s} "
              f"{sp['stable'].split('/')[0]:>5s} {sp['full'].split('/')[0]:>5s} | "
              f"{sp['mean_cf']:>6.3f} {sp['mean_total_rec']:>7.3f} "
              f"{sp['mean_left_rec']:>7.3f} {sp['mean_right_rec']:>7.3f} "
              f"{sp['l2_1s']:>5s}")

    print(f"\nTotal elapsed: {time.time()-t0:.1f}s")
    print(f"Wrote {RESULTS_PATH}")
