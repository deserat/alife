"""
Steady-State Critical Exponents (Session 101, queued-topic #257 next-step)

Session 100 found the GROWTH-PHASE MSD exponent α_nc = 1.729 at n=1500 (R²=0.998)
matches G&G's 2D critical exponent α=1.72 to 3 sig figs — but the system was in the
growth/overshoot phase at 2000 steps (fill=48–75% vs steady-state 38–44%). The
"What's next" was: measure the STEADY-STATE critical exponent by running 4000+
steps and computing the MSD from the late-window fluctuations only.

This script runs 6000 steps at 3 densities (n=1500, 2500, 3000) and computes:
  1. Growth-phase MSD (first half, same as Session 100) for comparison
  2. Steady-state MSD (second half only) — the actual critical exponent
  3. Full-series MSD for reference

The key prediction: the steady-state α_nc at n=3000 (the 30th ceiling, fill≈44%)
should match G&G's α=1.72 if the 30th ceiling IS the dynamical critical point.
If instead it deviates, the growth-phase match was coincidental.
"""

import os
import sys
import json
import time

import numpy as np

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SIM_DIR)

import sim14 as S14

OUTPUT_DIR = os.path.join(SIM_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

GRID = 160
JITTER = 10.0
SEED = 42
N_VALUES = [1500, 2500, 3000]
GAINS = [0.001]
STEPS = 6000
SAMPLE = 10  # 600 samples total


def make_params(n, g):
    """Same params as critical_exponents.py / n2500_plateau_sweep.py."""
    p = S14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = n
    p["steps"] = STEPS
    p["sample_every"] = SAMPLE
    p["boundary_mode"] = "dual"
    p["g_form"] = g
    p["g_persist"] = g
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3
    p["movement_mode"] = "focal"
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    p["recruit_response"] = "linear"
    return p


def compute_msd(series, min_lag=3, max_lag_frac=0.25):
    """Compute detrended MSD: Var(x(t+τ) - x(t)) for each lag τ.

    Returns (lags, msd_values, alpha, r_squared).
    """
    x = np.array(series, dtype=np.float64)
    n = len(x)
    max_lag = max(int(n * max_lag_frac), 5)

    lags = []
    vals = []
    for lag in range(1, max_lag + 1):
        deltas = x[lag:] - x[:-lag]
        msd = np.mean(deltas ** 2) - np.mean(deltas) ** 2
        lags.append(lag)
        vals.append(max(msd, 1e-15))

    lags = np.array(lags, dtype=np.float64)
    vals = np.array(vals, dtype=np.float64)

    # Fit log(MSD) = α * log(τ) + c for τ ≥ min_lag.
    mask = lags >= min_lag
    if mask.sum() >= 5:
        log_l = np.log(lags[mask])
        log_v = np.log(vals[mask])
        alpha, intercept = np.polyfit(log_l, log_v, 1)
        ss_res = np.sum((log_v - (alpha * log_l + intercept)) ** 2)
        ss_tot = np.sum((log_v - np.mean(log_v)) ** 2)
        r_sq = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    else:
        alpha = 0.0
        r_sq = 0.0

    return lags, vals, float(alpha), float(r_sq)


def run_one(n, g, seed):
    """Run the simulation and extract component count time series."""
    params = make_params(n, g)
    t0 = time.time()
    result = S14.run_two_region_hetero(params, seed=seed, n_seeds=2,
                                        mode="hetero")
    elapsed = time.time() - t0

    history = result["history"]

    # Extract time series.
    left_comps = [h["left_components"] for h in history]
    right_comps = [h["right_components"] for h in history]
    n_cells = [h["n_structure_cells"] for h in history]
    steps_ts = [h["step"] for h in history]

    n_samples = len(history)
    half = max(1, n_samples // 2)

    # Fill for early, late, and overall.
    fill_early = 100.0 * np.mean(n_cells[:half]) / (GRID * GRID)
    fill_late = 100.0 * np.mean(n_cells[half:]) / (GRID * GRID)

    # Late-window fill (steady-state).
    late_n_cells = n_cells[half:]

    # Compute MSD for three windows: full, first half (growth), second half (steady).
    windows = {
        "full": (left_comps, right_comps, n_cells),
        "growth": (left_comps[:half], right_comps[:half], n_cells[:half]),
        "steady": (left_comps[half:], right_comps[half:], n_cells[half:]),
    }

    msd_results = {}
    for wname, (lc, rc, nc) in windows.items():
        lc_lags, lc_msd, lc_a, lc_r = compute_msd(lc)
        rc_lags, rc_msd, rc_a, rc_r = compute_msd(rc)
        nc_lags, nc_msd, nc_a, nc_r = compute_msd(nc)
        msd_results[wname] = {
            "alpha_left": lc_a, "r_sq_left": lc_r,
            "alpha_right": rc_a, "r_sq_right": rc_r,
            "alpha_nc": nc_a, "r_sq_nc": nc_r,
            "n_samples": len(nc),
            "msd_nc": [float(v) for v in nc_msd],
            "msd_lags": [int(l) for l in nc_lags],
        }

    return {
        "n": n,
        "gain": g,
        "seed": seed,
        "fill_early_pct": float(fill_early),
        "fill_late_pct": float(fill_late),
        "n_samples": n_samples,
        "elapsed_s": round(elapsed, 1),
        "mean_late_left_comps": float(np.mean(left_comps[half:])),
        "mean_late_right_comps": float(np.mean(right_comps[half:])),
        "std_late_left_comps": float(np.std(left_comps[half:])),
        "std_late_right_comps": float(np.std(right_comps[half:])),
        "n_cells_ts": n_cells,
        "left_comps_ts": left_comps,
        "right_comps_ts": right_comps,
        "steps_ts": steps_ts,
        "msd": msd_results,
    }


def main():
    results = {
        "config": {
            "grid": GRID, "steps": STEPS, "sample_every": SAMPLE,
            "jitter": JITTER, "n_values": N_VALUES,
            "gains": GAINS, "seed": SEED,
            "gelimson_golestanian_alpha_2d": 1.72,
            "session_100_growth_alpha_nc_n1500": 1.729,
        },
        "runs": [],
        "summary": [],
    }

    for n in N_VALUES:
        for g in GAINS:
            r = run_one(n, g, SEED)
            results["runs"].append(r)
            ss = r["msd"]["steady"]
            gr = r["msd"]["growth"]
            print(f"  n={n} g={g}: fill_early={r['fill_early_pct']:.1f}% "
                  f"fill_late={r['fill_late_pct']:.1f}% "
                  f"| growth: α_nc={gr['alpha_nc']:.3f} (R²={gr['r_sq_nc']:.3f}) "
                  f"| steady: α_nc={ss['alpha_nc']:.3f} (R²={ss['r_sq_nc']:.3f}) "
                  f"α_lc={ss['alpha_left']:.3f} α_rc={ss['alpha_right']:.3f} "
                  f"({r['elapsed_s']:.0f}s)")

    # Summary by n.
    for n in N_VALUES:
        nruns = [r for r in results["runs"] if r["n"] == n]
        if not nruns:
            continue
        r = nruns[0]
        ss = r["msd"]["steady"]
        gr = r["msd"]["growth"]
        results["summary"].append({
            "n": n,
            "fill_early_pct": r["fill_early_pct"],
            "fill_late_pct": r["fill_late_pct"],
            "growth_alpha_nc": gr["alpha_nc"],
            "growth_r_sq_nc": gr["r_sq_nc"],
            "steady_alpha_nc": ss["alpha_nc"],
            "steady_r_sq_nc": ss["r_sq_nc"],
            "steady_alpha_left": ss["alpha_left"],
            "steady_alpha_right": ss["alpha_right"],
            "steady_r_sq_left": ss["r_sq_left"],
            "steady_r_sq_right": ss["r_sq_right"],
            "mean_late_comps": float(np.mean([
                r["mean_late_left_comps"], r["mean_late_right_comps"]])),
            "gg_alpha_2d": 1.72,
        })

    # Determinism: run n=3000 twice and compare.
    print("\n  Determinism check: n=3000 run twice...")
    r1 = run_one(3000, GAINS[0], SEED)
    r2 = run_one(3000, GAINS[0], SEED)
    det_match = (r1["n_cells_ts"] == r2["n_cells_ts"])
    results["determinism"] = {
        "n": 3000, "seed": SEED, "match": det_match,
        "note": "n_cells_ts identical across two runs." if det_match
                else "MISMATCH — non-deterministic!",
    }
    print(f"  Determinism: {'PASS' if det_match else 'FAIL'}")

    # Write slim JSON.
    out_path = os.path.join(OUTPUT_DIR, "steady_state_msd.json")
    slim = {
        "config": results["config"],
        "summary": results["summary"],
        "determinism": results["determinism"],
        "runs": [],
    }
    for r in results["runs"]:
        sr = {k: v for k, v in r.items()
              if k not in ("n_cells_ts", "left_comps_ts",
                           "right_comps_ts", "steps_ts")}
        slim["runs"].append(sr)
    with open(out_path, "w") as f:
        json.dump(slim, f, indent=2)

    # Full data for visualization.
    full_path = os.path.join(OUTPUT_DIR, "steady_state_msd_full.json")
    with open(full_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nWrote {out_path}")
    print(f"Wrote {full_path}")
    print(f"\n=== Steady-State Critical Exponents Summary ===")
    print(f"{'n':>6} {'fill_E':>7} {'fill_L':>7} "
          f"{'α_grow':>7} {'α_stead':>7} {'α_lc':>6} {'α_rc':>6} {'comps':>6}")
    for s in results["summary"]:
        print(f"{s['n']:6d} {s['fill_early_pct']:7.1f} {s['fill_late_pct']:7.1f} "
              f"{s['growth_alpha_nc']:7.3f} {s['steady_alpha_nc']:7.3f} "
              f"{s['steady_alpha_left']:6.3f} {s['steady_alpha_right']:6.3f} "
              f"{s['mean_late_comps']:6.1f}")
    print(f"\nG&G 2D critical exponent: α = 1.72 (superdiffusive)")
    print(f"Session 100 growth-phase α_nc (n=1500): 1.729")


if __name__ == "__main__":
    main()
