"""
Fill cap saturation functional form (#215).

The 19-point fill cap trajectory saturates at ~100% at n=15000. What is
the functional form of the saturation? Candidates:
  (a) logistic:      fill% = 100 / (1 + exp(-k*(n - n0)))
  (b) Gompertz:      fill% = 100 * exp(-exp(-k*(n - n0)))
  (c) stretched exp: fill% = 100 * (1 - exp(-a * n^b))
  (d) sub-saturation stretched exp (original): fill% = a * exp(b * sqrt(n))
  (e) power law:     fill% = a * n^gamma
  (f) log:           fill% = a * log(n) + b

The original 16-point fit (Session 74) found stretched_exp_sqrt (R²=0.964)
was the best sub-saturation fit. Now with n=10000 (75.25%), n=12000 (94.44%),
and n=15000 (99.93%), the saturation is present. Fit all 19 points and compare.

Session 77: continuation of Session 76's #215.
"""

import os
import json
import numpy as np

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
FIT_PATH = os.path.join(OUTPUT_DIR, "output", "fill_cap_saturation_fit.json")

# All fill cap data points (g=0.001, 160x160 grid, dual mode, focal 0.3, jit=10)
DATA = {
    550: 30.49,
    600: 31.23,
    700: 33.19,
    800: 34.50,
    900: 35.49,
    1000: 36.52,
    1200: 38.23,
    1500: 39.39,
    1800: 40.47,
    2000: 41.19,
    2500: 42.11,
    3000: 43.49,
    4000: 45.67,
    5000: 47.99,
    6000: 51.42,
    8000: 60.82,
    10000: 75.25,
    12000: 94.44,
    15000: 99.93,
}


def _fit(func, x, y, p0):
    """Fit via numpy least-squares and return R2, params, residuals."""
    try:
        # Transform to linear where possible for better initial guess
        popt, _, _, _, _ = np.polyfit(_linearize(func, x, p0), y, 0, full=True) if False else _nlsq(func, x, y, p0)
        y_pred = func(x, *popt)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1.0 - ss_res / ss_tot
        residuals = {int(xi): float(yi - yp) for xi, yi, yp in zip(x, y, y_pred)}
        names = func.__code__.co_varnames[:func.__code__.co_argcount]
        # Remove 'x' from names
        names = [n for n in names if n != 'x']
        params = {n: float(v) for n, v in zip(names, popt)}
        return {"R2": float(r2), "params": params, "residuals": residuals}
    except Exception as e:
        return {"R2": None, "error": str(e)}


def _nlsq(func, x, y, p0):
    """Simple Nelder-Mead-free least squares via numpy's curve_fit equivalent.

    Uses scipy if available; otherwise falls back to a grid search + numpy lstsq.
    """
    try:
        from scipy.optimize import curve_fit
        popt, _ = curve_fit(func, x, y, p0=p0, maxfev=50000)
        return popt, None, None, None, None
    except ImportError:
        # Grid search refinement for nonlinear params
        best_p = np.array(p0, dtype=np.float64)
        best_err = np.sum((y - func(x, *best_p)) ** 2)
        for _ in range(20):
            improved = False
            for i in range(len(best_p)):
                for delta in [0.1, 0.01, 0.001]:
                    for sign in [1, -1]:
                        trial = best_p.copy()
                        trial[i] *= (1 + sign * delta)
                        if trial[i] <= 0 and i > 0:
                            continue
                        err = np.sum((y - func(x, *trial)) ** 2)
                        if err < best_err:
                            best_err = err
                            best_p = trial
                            improved = True
            if not improved:
                break
        return best_p, None, None, None, None


def logistic(x, k, n0):
    return 100.0 / (1.0 + np.exp(-k * (x - n0)))


def gompertz(x, k, n0):
    return 100.0 * np.exp(-np.exp(-k * (x - n0)))


def stretched_exp_sat(x, a, b):
    return 100.0 * (1.0 - np.exp(-a * np.power(x, b)))


def sub_sat_stretched_exp(x, a, b):
    return a * np.exp(b * np.sqrt(x))


def power_law(x, a, gamma):
    return a * np.power(x, gamma)


def log_fit(x, a, b):
    return a * np.log(x) + b


def main():
    ns = np.array(sorted(DATA.keys()), dtype=np.float64)
    fills = np.array([DATA[int(n)] for n in ns], dtype=np.float64)
    n_points = len(ns)

    print(f"Fill cap saturation fit ({n_points} data points)")
    print(f"{'n':>6s}  {'fill%':>7s}")
    for n, f in zip(ns, fills):
        print(f"{int(n):>6d}  {f:>7.2f}")
    print()

    fits = {}

    # Logistic (saturation to 100%)
    fits["logistic"] = _fit(logistic, ns, fills, [0.001, 5000])

    # Gompertz (saturation to 100%)
    fits["gompertz"] = _fit(gompertz, ns, fills, [0.001, 5000])

    # Stretched exponential saturation (to 100)
    fits["stretched_exp_sat"] = _fit(stretched_exp_sat, ns, fills, [0.01, 0.5])

    # Sub-saturation stretched exponential (original, no 100% ceiling)
    fits["sub_sat_stretched_exp"] = _fit(sub_sat_stretched_exp, ns, fills, [26.0, 0.009])

    # Power law
    fits["power_law"] = _fit(power_law, ns, fills, [8.0, 0.21])

    # Log
    fits["log"] = _fit(log_fit, ns, fills, [20.0, -26.0])

    # Print results
    print(f"{'form':>25s}  {'R2':>8s}  params")
    print("-" * 80)
    for name in ["logistic", "gompertz", "stretched_exp_sat",
                 "sub_sat_stretched_exp", "power_law", "log"]:
        r = fits[name]
        if r["R2"] is not None:
            pstr = ", ".join(f"{k}={v:.6g}" for k, v in r["params"].items())
            print(f"{name:>25s}  {r['R2']:>8.5f}  {pstr}")
        else:
            print(f"{name:>25s}  FAILED: {r.get('error', '')}")
    print()

    # Find best fit
    valid = [(name, r["R2"]) for name, r in fits.items() if r["R2"] is not None]
    best = max(valid, key=lambda x: x[1])
    print(f"Best fit: {best[0]} (R² = {best[1]:.5f})")
    print()

    # Predictions at key points
    print("Predictions at key n values:")
    print(f"{'n':>6s}  {'observed':>8s}  ", end="")
    for name in ["logistic", "gompertz", "stretched_exp_sat", "sub_sat_stretched_exp", "power_law"]:
        print(f"{name[:12]:>12s}  ", end="")
    print()
    for n_val in [550, 1200, 3000, 5000, 8000, 10000, 12000, 15000, 20000]:
        obs = DATA.get(n_val, None)
        obs_str = f"{obs:.2f}" if obs is not None else "—"
        print(f"{n_val:>6d}  {obs_str:>8s}  ", end="")
        for name in ["logistic", "gompertz", "stretched_exp_sat", "sub_sat_stretched_exp", "power_law"]:
            r = fits[name]
            if r["R2"] is not None:
                xv = np.array([float(n_val)])
                if name == "logistic":
                    pred = float(logistic(xv, **r["params"])[0])
                elif name == "gompertz":
                    pred = float(gompertz(xv, **r["params"])[0])
                elif name == "stretched_exp_sat":
                    pred = float(stretched_exp_sat(xv, **r["params"])[0])
                elif name == "sub_sat_stretched_exp":
                    pred = float(sub_sat_stretched_exp(xv, **r["params"])[0])
                elif name == "power_law":
                    pred = float(power_law(xv, **r["params"])[0])
                print(f"{pred:>12.2f}  ", end="")
            else:
                print(f"{'—':>12s}  ", end="")
        print()

    # Saturation analysis: at what n does fill reach 99%?
    print()
    print("Saturation analysis (n where fill reaches 99%):")
    for name in ["logistic", "gompertz", "stretched_exp_sat"]:
        r = fits[name]
        if r["R2"] is None:
            continue
        p = r["params"]
        if name == "logistic":
            k, n0 = p["k"], p["n0"]
            n99 = n0 - np.log(1.0 / 99.0) / k
        elif name == "gompertz":
            k, n0 = p["k"], p["n0"]
            n99 = n0 - np.log(-np.log(0.99)) / k
        elif name == "stretched_exp_sat":
            a, b = p["a"], p["b"]
            n99 = (-np.log(0.01) / a) ** (1.0 / b)
        print(f"  {name}: n_99 = {n99:.0f}")

    # Sub-saturation fits (n <= 8000 only) for comparison
    sub_mask = ns <= 8000
    sub_ns = ns[sub_mask]
    sub_fills = fills[sub_mask]
    sub_fits = {}
    sub_fits["log"] = _fit(log_fit, sub_ns, sub_fills, [17.0, -15.0])
    sub_fits["power_law"] = _fit(power_law, sub_ns, sub_fills, [9.4, 0.19])
    sub_fits["stretched_exp"] = _fit(sub_sat_stretched_exp, sub_ns, sub_fills, [26.0, 0.009])

    print()
    print(f"Sub-saturation fits (n <= 8000, {int(sub_mask.sum())} points):")
    for name in ["log", "power_law", "stretched_exp"]:
        r = sub_fits[name]
        if r["R2"] is not None:
            pstr = ", ".join(f"{k}={v:.6g}" for k, v in r["params"].items())
            print(f"  {name:>20s}: R²={r['R2']:.5f}  {pstr}")

    # Save
    output = {
        "config": {
            "note": "Session 77: fill cap saturation functional form (#215)",
            "n_points": n_points,
            "data_source": "fill_cap_form_fit.json (16 points n=550..8000) + n10000 (75.25) + n12000 (94.44) + n15000 (99.93)",
            "grid": 160,
            "g": 0.001,
            "moore_percolation_threshold": "~0.407 (2D site, 8-neighbor)",
        },
        "data": {str(int(n)): f for n, f in zip(ns, fills)},
        "fits_all": {name: r for name, r in fits.items()},
        "fits_sub_saturation": {name: r for name, r in sub_fits.items()},
        "best_fit_all": best[0],
        "best_R2_all": float(best[1]),
    }

    os.makedirs(os.path.dirname(FIT_PATH), exist_ok=True)
    with open(FIT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {FIT_PATH}")


if __name__ == "__main__":
    main()
