"""
Fill equilibrium formula — can the fill at arbitrary (n, decay) be predicted?

Queued-topic #302. Session 113 found the fill cap is from the deposit/decay
equilibrium (material_decay), not the boundary. The fill depends on n and
decay, but the relationship is sublinear in n (the deposit_rate is not
constant — it depends on the structure's surface-to-volume ratio, which
changes with fill).

HYPOTHESIS:
  fill = C × n^α × decay^β

  where α is the n-exponent (predicted ~0.5 from surface-to-volume, but
  possibly different because the deposit probability depends on curvature,
  which depends on structure shape) and β is the decay-exponent (predicted
  ~1.0 from the simple equilibrium, but possibly <1 because the deposit
  rate changes with fill).

ALTERNATIVE (self-consistent):
  At equilibrium, deposit_rate = decay × total_material.
  deposit_rate = n × L × <p_dep> × pellet
  where L = reload_prob / (p_dep + reload_prob) and <p_dep> depends on the
  structure shape (surface vs interior).

  <p_dep>(fill) = p_base + (surface_fraction) × p_gain × <c_surface>
  surface_fraction ~ P/A ~ 1/√(fill × grid²)

  So: fill = n × L × [p_base + K / √(fill × grid²)] × pellet / (decay × grid²)

  This is a self-consistent equation in fill. At high fill (low decay),
  the p_base term dominates (interior deposits). At low fill (high decay),
  the surface term dominates (surface deposits).

DATA SOURCES:
  - Existing material_decay_sweep.json (n=2500, 5000 × 7 decays, no boundary)
  - Existing ceiling_decay_sweep.json (3 decays × 3 n values, with boundary)
  - New runs at n=1000 × 5 decays × 4 seeds (to extend the n range)
  - Session 112 showed boundary has <1pp effect on fill, so we combine.

METHODOLOGY:
  - Fit on all unsaturated data points (fill < 95%).
  - Leave-one-out cross-validation (LOOCV) for the power law.
  - Determinism: run twice, diff the JSON.
"""

import os
import sys
import json
import time
import numpy as np

SIM14_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM14_DIR)
import sim14 as I14  # noqa: E402

GRID = 160
JITTER = 10.0
SEEDS = [42, 123, 256, 999]
NEW_DENSITIES = [1000]
NEW_DECAYS = [0.002, 0.004, 0.008, 0.016, 0.032]


# --------------------------------------------------------------------------#
# Load existing data
# --------------------------------------------------------------------------#

def load_existing_data():
    """Load fill data from existing sweep JSONs.

    Returns list of (n, decay, fill_pct, source) tuples for unsaturated
    data points (fill < 95%).
    """
    data = []

    # material_decay_sweep.json — no inhibition, n=2500, 5000
    md_path = os.path.join(SIM14_DIR, "output", "material_decay_sweep.json")
    if os.path.exists(md_path):
        with open(md_path) as f:
            md = json.load(f)
        for n_str in ["no_inhib_n2500", "no_inhib_n5000"]:
            if n_str not in md:
                continue
            n = int(n_str.replace("no_inhib_n", ""))
            for decay_str, d in md[n_str].items():
                fill = d["mean_fill"]
                if fill < 95.0:
                    data.append((n, float(decay_str), fill, "material_decay"))

    # ceiling_decay_sweep.json — with boundary, 3 decays × 3 n values
    cd_path = os.path.join(SIM14_DIR, "output", "ceiling_decay_sweep.json")
    if os.path.exists(cd_path):
        with open(cd_path) as f:
            cd = json.load(f)
        for decay_key, decay_data in cd.items():
            if not decay_key.startswith("decay_"):
                continue
            decay = float(decay_key.split("_")[1])
            for label_key, ld in decay_data.items():
                if not isinstance(ld, dict) or "n_termites" not in ld:
                    continue
                n = ld["n_termites"]
                fill = ld["mean_fill"]
                if fill < 95.0:
                    data.append((n, decay, fill, "ceiling_decay"))

    # focal_bias_ceiling_sweep.json — different bias values at n=3000
    fb_path = os.path.join(SIM14_DIR, "output", "focal_bias_ceiling_sweep.json")
    if os.path.exists(fb_path):
        with open(fb_path) as f:
            fb = json.load(f)
        # Parse if it has the right structure
        for key, val in fb.items():
            if isinstance(val, dict) and "n_termites" in val and "mean_fill" in val:
                n = val["n_termites"]
                fill = val["mean_fill"]
                decay = val.get("decay", 0.002)
                bias = val.get("movement_bias", 0.3)
                if fill < 95.0:
                    data.append((n, decay, fill, f"focal_bias_{bias}"))

    return data


# --------------------------------------------------------------------------#
# Run new simulations
# --------------------------------------------------------------------------#

def make_params(n_termites, decay):
    """No boundary (hetero, g=0), with focal bias."""
    p = I14.curvature_params(0.0)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["material_decay"] = decay
    p["movement_bias"] = 0.3
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    return p


def run_one(n, decay, seed):
    """Run one simulation and return fill_pct."""
    p = make_params(n, decay)
    r = I14.run_two_region_hetero(p, seed=seed, n_seeds=2, mode="hetero")
    s = r["summary"]
    cells = s["final_n_structure_cells"]
    fill = 100.0 * cells / (GRID * GRID)
    return {
        "n": n,
        "decay": decay,
        "seed": seed,
        "cells": cells,
        "fill_pct": round(fill, 2),
        "h7": s["crossed_h7"],
        "l2_crossed": s["l2_crossed"],
    }


def run_new_sweep():
    """Run new simulations at n=1000 × 5 decays × 4 seeds."""
    t0 = time.time()
    results = {
        "description": "Fill equilibrium — new n=1000 data points",
        "grid": GRID,
        "jitter": JITTER,
        "seeds": SEEDS,
        "decays": NEW_DECAYS,
        "densities": NEW_DENSITIES,
        "date": "2026-11-27",
    }

    new_data = []
    for n in NEW_DENSITIES:
        for decay in NEW_DECAYS:
            fills = []
            for sd in SEEDS:
                m = run_one(n, decay, sd)
                fills.append(m)
                print(f"  n={n} decay={decay:.4f} s={sd}: "
                      f"fill={m['fill_pct']:.2f}% h7={m['h7']}")
            mean_fill = np.mean([m["fill_pct"] for m in fills])
            print(f"  MEAN: n={n} decay={decay:.4f} fill={mean_fill:.2f}%")
            new_data.append({
                "n": n,
                "decay": decay,
                "mean_fill": round(mean_fill, 2),
                "runs": fills,
            })

    results["new_data"] = new_data
    results["elapsed_seconds"] = round(time.time() - t0, 1)
    return results


# --------------------------------------------------------------------------#
# Fit the power-law formula
# --------------------------------------------------------------------------#

def fit_power_law(data):
    """Fit fill = C × n^α × decay^β via log-linear regression.

    data: list of (n, decay, fill_pct, source) tuples.
    Returns (C, alpha, beta, R², predictions).
    """
    ns = np.array([d[0] for d in data], dtype=float)
    decays = np.array([d[1] for d in data], dtype=float)
    fills = np.array([d[2] for d in data], dtype=float)

    # log(fill) = log(C) + α × log(n) + β × log(decay)
    log_n = np.log(ns)
    log_decay = np.log(decays)
    log_fill = np.log(fills)

    # Design matrix: [1, log_n, log_decay]
    A = np.column_stack([np.ones(len(data)), log_n, log_decay])
    coefs, residuals, _, _ = np.linalg.lstsq(A, log_fill, rcond=None)
    log_C, alpha, beta = coefs

    C = np.exp(log_C)
    preds = C * ns**alpha * decays**beta
    ss_res = np.sum((fills - preds)**2)
    ss_tot = np.sum((fills - np.mean(fills))**2)
    r2 = 1.0 - ss_res / ss_tot

    return {
        "C": C,
        "alpha": alpha,
        "beta": beta,
        "r2": r2,
        "formula": f"fill = {C:.4f} × n^{alpha:.4f} × decay^{beta:.4f}",
        "predictions": list(zip(ns, decays, fills, np.round(preds, 2))),
    }


def fit_self_consistent(data, grid=GRID, pellet=1.0, reload_prob=0.3,
                        p_base=0.01, p_gain=0.85):
    """Fit the self-consistent formula:

    fill = n × L(p_dep) × [p_base + K / √(fill × grid²)] × pellet
           / (decay × grid²)

    where L = reload_prob / (p_dep + reload_prob) and p_dep = p_base +
    K / √(fill × grid²). At equilibrium, solve iteratively.

    Parameters: C (the K constant, surface curvature × surface_fraction
    coefficient) and possibly a correction for the p_dep in L.

    We fit K via nonlinear least squares (grid search + refine).
    """
    def golden_section(f, a, b, tol=1e-6, max_iter=200):
        """Golden section minimization (no scipy needed)."""
        gr = (np.sqrt(5) - 1) / 2
        c = b - gr * (b - a)
        d = a + gr * (b - a)
        for _ in range(max_iter):
            if abs(b - a) < tol:
                return (a + b) / 2
            if f(c) < f(d):
                b = d
                d = c
                c = b - gr * (b - a)
            else:
                a = c
                c = d
                d = a + gr * (b - a)
        return (a + b) / 2

    def predict_fill(n, decay, K, grid=grid, pellet=pellet,
                      reload_prob=reload_prob, p_base=p_base, p_gain=p_gain):
        """Iteratively solve the self-consistent equation."""
        fill_frac = 0.1  # initial guess
        for _ in range(200):
            total_mat = fill_frac * grid * grid
            surface_frac = 1.0 / max(np.sqrt(total_mat), 1.0)
            p_dep = p_base + K * surface_frac
            p_dep = min(p_dep, 1.0)
            L = reload_prob / (p_dep + reload_prob)
            new_fill = n * L * p_dep * pellet / (decay * grid * grid)
            new_fill = min(new_fill, 0.999)
            if abs(new_fill - fill_frac) < 1e-8:
                fill_frac = new_fill
                break
            fill_frac = new_fill
        return fill_frac * 100.0  # percentage

    def objective(K):
        ss = 0.0
        for n, decay, fill_pct, _ in data:
            pred = predict_fill(n, decay, K)
            ss += (pred - fill_pct)**2
        return ss

    # Grid search over K
    best_K = None
    best_ss = np.inf
    for K in np.linspace(0.01, 20.0, 2000):
        ss = objective(K)
        if ss < best_ss:
            best_ss = ss
            best_K = K

    # Refine with golden section search
    lo = max(best_K - 2.0, 0.001)
    hi = best_K + 2.0
    best_K = golden_section(objective, lo, hi)
    best_ss = objective(best_K)

    ss_tot = sum((d[2] - np.mean([d[2] for d in data]))**2 for d in data)
    r2 = 1.0 - best_ss / ss_tot

    preds = [(d[0], d[1], d[2], round(predict_fill(d[0], d[1], best_K), 2))
             for d in data]

    return {
        "K": best_K,
        "r2": r2,
        "formula": (f"fill = n × L(p_dep) × [p_base + {best_K:.4f}/√(fill×grid²)] "
                    f"× pellet / (decay × grid²)"),
        "predictions": preds,
        "predict_fn": lambda n, decay: predict_fill(n, decay, best_K),
    }


def loocv_power_law(data):
    """Leave-one-out cross-validation for the power law."""
    errors = []
    for i in range(len(data)):
        train = data[:i] + data[i+1:]
        test = data[i]
        fit = fit_power_law(train)
        pred = fit["C"] * test[0]**fit["alpha"] * test[1]**fit["beta"]
        err = abs(pred - test[2])
        errors.append({
            "n": test[0],
            "decay": test[1],
            "actual": test[2],
            "predicted": round(pred, 2),
            "abs_error": round(err, 2),
        })
    return {
        "mean_abs_error": round(np.mean([e["abs_error"] for e in errors]), 2),
        "max_abs_error": round(max([e["abs_error"] for e in errors]), 2),
        "errors": errors,
    }


# --------------------------------------------------------------------------#
# Main
# --------------------------------------------------------------------------#

def main():
    t0 = time.time()
    print("=" * 80)
    print("FILL EQUILIBRIUM FORMULA — queued-topic #302")
    print("=" * 80)

    # Step 1: Load existing data
    print("\n--- Step 1: Load existing data ---")
    existing = load_existing_data()
    print(f"Loaded {len(existing)} existing data points:")
    for n, decay, fill, src in sorted(existing, key=lambda x: (x[1], x[0])):
        print(f"  n={n:>5}  decay={decay:.4f}  fill={fill:.2f}%  ({src})")

    # Step 2: Run new data at n=1000
    print("\n--- Step 2: Run new n=1000 data ---")
    new_results = run_new_sweep()
    for nd in new_results["new_data"]:
        existing.append((nd["n"], nd["decay"], nd["mean_fill"], "new_n1000"))
        print(f"  n={nd['n']} decay={nd['decay']:.4f} fill={nd['mean_fill']:.2f}%")

    print(f"\nTotal data points: {len(existing)}")

    # Step 3: Fit power law
    print("\n--- Step 3: Fit power law fill = C × n^α × decay^β ---")
    # Exclude saturated points (fill >= 95%)
    unsaturated = [d for d in existing if d[2] < 95.0]
    print(f"Unsaturated data points: {len(unsaturated)}")

    fit = fit_power_law(unsaturated)
    print(f"\n  Formula: {fit['formula']}")
    print(f"  R² = {fit['r2']:.4f}")
    print(f"\n  Predictions vs actuals:")
    print(f"  {'n':>6}  {'decay':>8}  {'actual':>8}  {'pred':>8}  {'err':>6}")
    for n, decay, actual, pred in fit["predictions"]:
        err = pred - actual
        print(f"  {n:>6.0f}  {decay:>8.4f}  {actual:>8.2f}  {pred:>8.2f}  {err:>6.2f}")

    # Step 4: LOOCV
    print("\n--- Step 4: Leave-one-out cross-validation ---")
    loocv = loocv_power_law(unsaturated)
    print(f"  Mean absolute error: {loocv['mean_abs_error']:.2f}%")
    print(f"  Max absolute error:  {loocv['max_abs_error']:.2f}%")

    # Step 5: Fit self-consistent formula (if scipy available)
    print("\n--- Step 5: Fit self-consistent formula ---")
    try:
        sc_fit = fit_self_consistent(unsaturated)
        print(f"  Formula: {sc_fit['formula']}")
        print(f"  R² = {sc_fit['r2']:.4f}")
        print(f"\n  Predictions vs actuals:")
        print(f"  {'n':>6}  {'decay':>8}  {'actual':>8}  {'pred':>8}  {'err':>6}")
        for n, decay, actual, pred in sc_fit["predictions"]:
            err = pred - actual
            print(f"  {n:>6.0f}  {decay:>8.4f}  {actual:>8.2f}  {pred:>8.2f}  {err:>6.2f}")
        has_sc = True
    except Exception as e:
        print(f"  Could not fit self-consistent formula: {e}")
        has_sc = False

    # Step 6: Test — predict the ceiling_decay_sweep data (out-of-sample)
    print("\n--- Step 6: Out-of-sample test — predict ceiling_decay data ---")
    cd_path = os.path.join(SIM14_DIR, "output", "ceiling_decay_sweep.json")
    oos_errors = []
    if os.path.exists(cd_path):
        with open(cd_path) as f:
            cd = json.load(f)
        for decay_key, decay_data in cd.items():
            if not decay_key.startswith("decay_"):
                continue
            decay = float(decay_key.split("_")[1])
            for label_key, ld in decay_data.items():
                if not isinstance(ld, dict) or "n_termites" not in ld:
                    continue
                n = ld["n_termites"]
                actual = ld["mean_fill"]
                if actual >= 95.0:
                    continue
                pred = fit["C"] * n**fit["alpha"] * decay**fit["beta"]
                err = pred - actual
                oos_errors.append({
                    "n": n,
                    "decay": decay,
                    "actual": actual,
                    "predicted": round(pred, 2),
                    "error": round(err, 2),
                })
                print(f"  n={n:>5} decay={decay:.4f} actual={actual:.2f}% "
                      f"pred={pred:.2f}% err={err:.2f}")

    if oos_errors:
        mean_err = np.mean([abs(e["error"]) for e in oos_errors])
        max_err = max([abs(e["error"]) for e in oos_errors])
        print(f"\n  OOS mean |error| = {mean_err:.2f}%")
        print(f"  OOS max  |error| = {max_err:.2f}%")

    # Step 7: Determinism check (run n=2500, decay=0.002, seed=42 twice, diff)
    print("\n--- Step 7: Determinism check ---")
    r1 = run_one(2500, 0.002, 42)
    r2 = run_one(2500, 0.002, 42)
    det_ok = r1["cells"] == r2["cells"]
    print(f"  Run 1: cells={r1['cells']} fill={r1['fill_pct']:.2f}%")
    print(f"  Run 2: cells={r2['cells']} fill={r2['fill_pct']:.2f}%")
    print(f"  Deterministic: {det_ok}")

    # Save results
    elapsed = time.time() - t0
    output = {
        "description": "Fill equilibrium formula — queued-topic #302",
        "date": "2026-11-27",
        "grid": GRID,
        "data_points": [
            {"n": int(d[0]), "decay": d[1], "fill_pct": d[2], "source": d[3]}
            for d in sorted(unsaturated, key=lambda x: (x[1], x[0]))
        ],
        "power_law_fit": {
            "C": fit["C"],
            "alpha": fit["alpha"],
            "beta": fit["beta"],
            "r2": fit["r2"],
            "formula": fit["formula"],
        },
        "loocv": loocv,
        "oos_test": oos_errors,
        "new_data": new_results.get("new_data", []),
        "determinism": {
            "run1_cells": r1["cells"],
            "run2_cells": r2["cells"],
            "deterministic": det_ok,
        },
        "elapsed_seconds": round(elapsed, 1),
    }

    if has_sc:
        output["self_consistent_fit"] = {
            "K": sc_fit["K"],
            "r2": sc_fit["r2"],
            "formula": sc_fit["formula"],
            "predictions": [
                {"n": int(p[0]), "decay": p[1], "actual": p[2],
                 "predicted": p[3]}
                for p in sc_fit["predictions"]
            ],
        }

    out_path = os.path.join(SIM14_DIR, "output", "fill_equilibrium.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n\nSaved to {out_path}")
    print(f"Elapsed: {elapsed:.1f}s")

    return output, elapsed


if __name__ == "__main__":
    main()
