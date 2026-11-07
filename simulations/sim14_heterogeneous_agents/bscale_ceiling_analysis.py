"""
Session 104 analysis script: b_scale measurement (#264), two-component ceiling
formula (#265), and growth-phase alpha match analysis (#263).

All three are pure analysis of existing data + fast initial-state computations.
No full simulation runs needed.
"""
import os, sys, json, time
import numpy as np

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
SIM13_DIR = os.path.join(SIM_DIR, "..", "sim13_direct_copresence")
sys.path.insert(0, SIM13_DIR)
import sim13 as I13
import sim10 as T
import sim09 as S

OUTPUT_DIR = os.path.join(SIM_DIR, "output")

# --- Seed placement (replicates sim10.seed_region) ---
SEED_SIGMA_FRAC = 0.08
SEED_HEIGHT = 4.0
SEED_OFFSET_FRAC = 0.25

def make_initial_material(size):
    """Create the initial material field with two seeded regions."""
    material = np.zeros((size, size), dtype=np.float64)
    sigma = max(1.0, size * SEED_SIGMA_FRAC)
    cy = size // 2
    for region, cx in [("left", int(size * SEED_OFFSET_FRAC)),
                      ("right", size - int(size * SEED_OFFSET_FRAC))]:
        yy, xx = np.mgrid[0:size, 0:size]
        material += SEED_HEIGHT * np.exp(
            -((yy - cy)**2 + (xx - cx)**2) / (2.0 * sigma**2))
    return material

def make_material_by_id(size):
    """Split initial material into id=0 (left) and id=1 (right)."""
    mat = make_initial_material(size)
    mid = size // 2
    m0 = mat.copy()
    m1 = np.zeros_like(mat)
    m1[:, mid:] = mat[:, mid:].copy()
    m0[:, mid:] = 0.0
    return [m0, m1]

def measure_b_scale(size, radius):
    """Compute b_scale = 95th percentile of initial ID co-presence."""
    mbi = make_material_by_id(size)
    cp = I13._dilate_no_x_wrap(mbi[0], radius)
    cp = np.minimum(cp, I13._dilate_no_x_wrap(mbi[1], radius))
    b_scale = max(float(np.percentile(cp, 95)), 1e-9)
    cp_mean = float(np.mean(cp))
    cp_max = float(np.max(cp))
    cp_cov = float(np.mean(cp > 1e-6))
    return {
        "grid": size, "radius": radius, "r_over_grid": radius / size,
        "b_scale": b_scale, "cp_mean": cp_mean, "cp_max": cp_max,
        "cp_coverage": cp_cov,
    }

def part1_bscale_measurement():
    """#264: Measure b_scale at r=16 on 320x320 (and other radii for comparison)."""
    print("=== Part 1: b_scale measurement (#264) ===")
    configs = [
        (80, 8), (160, 8), (320, 8),     # absolute r=8
        (160, 16), (320, 16),            # r=16
        (320, 4),                         # r=4 (for #262 prediction)
        (80, 4),                          # r=4 on 80
        (160, 4),                         # r=4 on 160
        (320, 32),                        # r=32 (relative on 320)
    ]
    results = []
    for size, radius in configs:
        r = measure_b_scale(size, radius)
        print(f"  {size}x{size} r={radius:2d} (r/grid={radius/size:.3f}): "
              f"b_scale={r['b_scale']:.6f} cp_mean={r['cp_mean']:.6f} "
              f"cp_cov={r['cp_coverage']:.4f}")
        results.append(r)
    return results

def part2_ceiling_formula(bscale_results):
    """#265: Two-component formula for the 30th ceiling."""
    print("\n=== Part 2: Two-component ceiling formula (#265) ===")

    # Known ceiling data points (fill% at which stability collapses):
    # (grid, radius, r/grid, b_scale, ceiling_fill_pct, source)
    # ceiling = last fill% with any stability (stable > 0)
    ceiling_points = [
        # 80x80 r=8: ceiling ~70% (gradual, 76.3% last stable)
        {"grid": 80, "radius": 8, "r_grid": 0.10,
         "b_scale": 0.123749, "ceiling_fill": 76.3,
         "source": "grid80_high_density (Session 95)"},
        # 160x160 r=8: ceiling 43.63%
        {"grid": 160, "radius": 8, "r_grid": 0.05,
         "b_scale": 0.003993, "ceiling_fill": 43.63,
         "source": "n2500-3000 plateau (Session 71)"},
        # 320x320 r=8: ceiling < 25% (stability 0/4 at all tested n)
        {"grid": 320, "radius": 8, "r_grid": 0.025,
         "b_scale": 0.000000, "ceiling_fill": 25.0,  # upper bound
         "source": "grid320_30th_ceiling (Session 102)"},
        # 320x320 r=16: ceiling < 32.7%
        {"grid": 320, "radius": 16, "r_grid": 0.05,
         "b_scale": None,  # to be measured
         "ceiling_fill": 32.7,  # upper bound (stability 0/4 at n=4000)
         "source": "r16_320_ceiling (Session 103)"},
        # 160x160 r=4: ceiling ~40%
        {"grid": 160, "radius": 4, "r_grid": 0.025,
         "b_scale": None,  # to be measured
         "ceiling_fill": 40.0,
         "source": "dilation_radius_focused (Session 96)"},
    ]

    # Fill in measured b_scale values
    for pt in ceiling_points:
        for r in bscale_results:
            if r["grid"] == pt["grid"] and r["radius"] == pt["radius"]:
                pt["b_scale_measured"] = r["b_scale"]
                pt["cp_mean_measured"] = r["cp_mean"]
                pt["cp_coverage_measured"] = r["cp_coverage"]
                break

    # Also measure b_scale for 160x160 r=4
    r_160_4 = measure_b_scale(160, 4)
    print(f"  Extra: 160x160 r=4 b_scale={r_160_4['b_scale']:.6f}")
    for pt in ceiling_points:
        if pt["grid"] == 160 and pt["radius"] == 4:
            pt["b_scale_measured"] = r_160_4["b_scale"]
            pt["cp_mean_measured"] = r_160_4["cp_mean"]
            pt["cp_coverage_measured"] = r_160_4["cp_coverage"]

    print("\n  Ceiling data points:")
    for pt in ceiling_points:
        bs = pt.get("b_scale_measured", pt["b_scale"])
        print(f"    {pt['grid']}x{pt['grid']} r={pt['radius']:2d} "
              f"r/grid={pt['r_grid']:.3f} b_scale={bs:.6f} "
              f"ceiling={pt['ceiling_fill']:.1f}% [{pt['source']}]")

    # Fit: ceiling = a * (r/grid) + b * b_scale + c
    # Use only points with measured b_scale
    fit_points = [pt for pt in ceiling_points if "b_scale_measured" in pt]
    x_rgrid = np.array([pt["r_grid"] for pt in fit_points])
    x_bscale = np.array([pt["b_scale_measured"] for pt in fit_points])
    y_ceiling = np.array([pt["ceiling_fill"] for pt in fit_points])

    # Linear fit: ceiling = a * r_grid + b * b_scale + c
    A = np.column_stack([x_rgrid, x_bscale, np.ones_like(x_rgrid)])
    coeffs, residuals, rank, sv = np.linalg.lstsq(A, y_ceiling, rcond=None)
    a, b, c = coeffs
    y_pred = A @ coeffs
    ss_res = np.sum((y_ceiling - y_pred)**2)
    ss_tot = np.sum((y_ceiling - np.mean(y_ceiling))**2)
    r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    print(f"\n  Two-component linear fit: ceiling = {a:.2f}*(r/grid) + {b:.2f}*b_scale + {c:.2f}")
    print(f"  R² = {r_sq:.4f}")
    for i, pt in enumerate(fit_points):
        print(f"    {pt['grid']}x{pt['grid']} r={pt['radius']}: predicted={y_pred[i]:.1f}% actual={pt['ceiling_fill']:.1f}%")

    # Also try: ceiling = a * r_grid + b * (b_scale * r_grid) + c
    # (interaction term: the boundary's effectiveness = reach * signal)
    x_interact = x_rgrid * x_bscale
    A2 = np.column_stack([x_rgrid, x_interact, np.ones_like(x_rgrid)])
    coeffs2, _, _, _ = np.linalg.lstsq(A2, y_ceiling, rcond=None)
    y_pred2 = A2 @ coeffs2
    ss_res2 = np.sum((y_ceiling - y_pred2)**2)
    r_sq2 = 1 - ss_res2 / ss_tot if ss_tot > 0 else 0.0
    a2, b2, c2 = coeffs2
    print(f"\n  Interaction fit: ceiling = {a2:.2f}*(r/grid) + {b2:.2f}*(r/grid*b_scale) + {c2:.2f}")
    print(f"  R² = {r_sq2:.4f}")
    for i, pt in enumerate(fit_points):
        print(f"    {pt['grid']}x{pt['grid']} r={pt['radius']}: predicted={y_pred2[i]:.1f}% actual={pt['ceiling_fill']:.1f}%")

    # Also try single-variable: ceiling = a * b_scale + c
    A3 = np.column_stack([x_bscale, np.ones_like(x_bscale)])
    coeffs3, _, _, _ = np.linalg.lstsq(A3, y_ceiling, rcond=None)
    y_pred3 = A3 @ coeffs3
    ss_res3 = np.sum((y_ceiling - y_pred3)**2)
    r_sq3 = 1 - ss_res3 / ss_tot if ss_tot > 0 else 0.0
    a3, c3 = coeffs3
    print(f"\n  b_scale-only fit: ceiling = {a3:.2f}*b_scale + {c3:.2f}")
    print(f"  R² = {r_sq3:.4f}")

    # And single-variable: ceiling = a * r_grid + c
    A4 = np.column_stack([x_rgrid, np.ones_like(x_rgrid)])
    coeffs4, _, _, _ = np.linalg.lstsq(A4, y_ceiling, rcond=None)
    y_pred4 = A4 @ coeffs4
    ss_res4 = np.sum((y_ceiling - y_pred4)**2)
    r_sq4 = 1 - ss_res4 / ss_tot if ss_tot > 0 else 0.0
    a4, c4 = coeffs4
    print(f"\n  r_grid-only fit: ceiling = {a4:.2f}*(r/grid) + {c4:.2f}")
    print(f"  R² = {r_sq4:.4f}")

    return ceiling_points, {
        "linear_2comp": {"coeffs": [float(a), float(b), float(c)], "r_sq": float(r_sq)},
        "interaction": {"coeffs": [float(a2), float(b2), float(c2)], "r_sq": float(r_sq2)},
        "bscale_only": {"coeffs": [float(a3), float(c3)], "r_sq": float(r_sq3)},
        "rgrid_only": {"coeffs": [float(a4), float(c4)], "r_sq": float(r_sq4)},
    }

def part3_growth_alpha():
    """#263: Why does the growth-phase alpha match G&G?"""
    print("\n=== Part 3: Growth-phase alpha analysis (#263) ===")
    with open(os.path.join(OUTPUT_DIR, "critical_exponents.json")) as f:
        d = json.load(f)

    gg_alpha = d["config"]["gelimson_golestanian_alpha_2d"]
    print(f"  G&G 2D alpha = {gg_alpha}")

    for s in d["summary"]:
        print(f"  n={s['n']:5d} fill={s['fill_pct']:.1f}% "
              f"alpha_nc={s['alpha_n_cells']:.4f} "
              f"alpha_lc={s['alpha_left_comps']:.4f} "
              f"alpha_rc={s['alpha_right_comps']:.4f} "
              f"late_comps={s['mean_late_comps']:.2f}")

    # Key insight: the 30th ceiling on 160x160 is ~43.6% fill.
    # At n=1500, fill=48.1% — just above the ceiling.
    # The growth-phase MSD measures the dynamics DURING the overshoot phase,
    # when the system has just crossed the stability threshold.
    # The G&G critical regime is where interactions regulate growth
    # (weakly coupled fixed point). Our system passes through this regime
    # transiently during the growth phase at fill ~43-48%.
    # The match (1.729 vs 1.72) is because the growth dynamics near the
    # 30th ceiling ARE the G&G critical dynamics — the same balance of
    # growth (extensive, ∝n) vs suppression (intensive, ∝√n).

    # Compute the balance ratio at each n
    # growth_rate ∝ n (deposit rate * n_termites)
    # suppression_rate ∝ √n (boundary suppression through diffusion length)
    # balance = n / √n = √n
    for s in d["summary"]:
        n = s["n"]
        balance = np.sqrt(n)
        ratio = s["fill_pct"] / 43.6  # ratio to the 30th ceiling
        print(f"  n={n:5d} balance(√n)={balance:.2f} fill/ceiling={ratio:.3f} "
              f"alpha_nc={s['alpha_n_cells']:.4f}")

    # The alpha_nc decreases monotonically with n:
    # n=1500: alpha=1.729 (near G&G), fill just above ceiling
    # n=4000: alpha=1.255 (well below), fill well above ceiling
    # The match at n=1500 is because the system is CLOSEST to the critical
    # regime (fill just above the 30th ceiling), and the G&G exponent
    # describes the critical dynamics AT that regime.

    # But the component-count exponents (alpha_lc, alpha_rc) are ~0.5-0.83
    # (subdiffusive), not matching G&G. The cell-count exponent matches but
    # the component-count doesn't — the cells grow superdiffusively (the
    # structure fills out) while the components fragment subdiffusively
    # (over-splitting is slower than growth).

    print("\n  Interpretation:")
    print("  The cell-count MSD exponent (alpha_nc) matches G&G's 2D")
    print("  critical exponent (1.72) at n=1500 (fill=48.1%, just above")
    print("  the 30th ceiling ~43.6%). The match is because the growth")
    print("  dynamics near the 30th ceiling pass through the G&G critical")
    print("  regime: the same balance of extensive growth (∝n) vs intensive")
    print("  suppression (∝√n). At higher n (fill >> ceiling), the system")
    print("  has moved past the critical regime and alpha_nc decreases")
    print("  monotonically toward the diffusive limit (alpha=1).")
    print()
    print("  The component-count exponents (alpha_lc/rc ~0.5-0.8) are")
    print("  SUBDIFFUSIVE — they measure fragmentation, not growth. The")
    print("  cells grow superdiffusively while components fragment")
    print("  subdiffusively. Only the cell-count (total material) carries")
    print("  the G&G exponent; the component count is on a different axis.")

    return {"gg_alpha": gg_alpha, "summary": d["summary"]}

def main():
    t0 = time.time()
    bscale_results = part1_bscale_measurement()
    ceiling_points, fits = part2_ceiling_formula(bscale_results)
    alpha_analysis = part3_growth_alpha()
    elapsed = time.time() - t0

    output = {
        "session": 104,
        "elapsed_s": elapsed,
        "bscale_measurements": bscale_results,
        "ceiling_points": ceiling_points,
        "ceiling_fits": fits,
        "alpha_analysis": alpha_analysis,
    }

    out_path = os.path.join(OUTPUT_DIR, "bscale_ceiling_analysis.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Wrote {out_path} ({elapsed:.1f}s)")

if __name__ == "__main__":
    main()
