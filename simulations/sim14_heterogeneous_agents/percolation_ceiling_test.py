"""
Percolation ceiling test — is the ~42% persistence ceiling the Moore
8-neighbor site percolation threshold (~0.407)?

Queued-topic #301 (re-prioritized from #246/#299).

The ~42% persistence ceiling is ~1.3pp above the Moore threshold (0.4072).
Is the gap significant (the boundary delays percolation) or coincidental?

KEY INSIGHT: the total fill is ~42%, but each structure (id0 left, id1 right)
fills ~42% of its OWN half-region (80×160 = 12800 cells). The percolation
threshold applies to the fill fraction within each structure's region, not
the total grid fill. If each structure percolates within its half at the
ceiling, the ceiling IS the Moore threshold for the half-region.

TEST:
  1. Run 3 n values (2000, 2500, 3000) at decay=0.002, dual boundary,
     4 seeds — fill brackets the ceiling (~41%, ~42.6%, ~43.7%).
  2. For each run, extract final material_by_id[0] (left) and [1] (right).
  3. For each structure, restrict to its half-region, threshold at
     STRUCTURE_THRESHOLD, measure:
     - fill_fraction within half-region
     - spanning cluster (largest component spans the half in both dims)
     - largest component fraction
     - n_components
  4. Random-site percolation control: generate random masks at matched
     fill fractions on the 160×160 half-region (80×160), measure the same.
  5. Compare: if the structure percolates at the same fill as random sites,
     the ceiling = Moore threshold (gap = 0). If the structure percolates
     at higher fill than random, the boundary delays percolation by the
     gap amount.

Config: 160×160, dual mode g=0.001, focal bias=0.3, per_step jitter=10.
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

GRID = 160
JITTER = 10.0
SEEDS = [42, 123, 256, 999]
STRUCTURE_THRESHOLD = S.STRUCTURE_THRESHOLD  # 1.0

# n values at decay=0.002 that bracket the ceiling
N_VALUES = [2000, 2500, 3000]
DECAY = 0.002

# Random percolation fill fractions to sweep (for the control)
RANDOM_FILLS = [0.38, 0.40, 0.407, 0.42, 0.44, 0.46]
N_RANDOM_SEEDS = 8  # more seeds for the random control


def make_params(n_termites, decay):
    """Dual boundary (g=0.001), focal bias, curvature channel."""
    p = I14.curvature_params(0.5)
    p["grid_size"] = GRID
    p["n_termites"] = n_termites
    p["material_decay"] = decay
    p["boundary_mode"] = "dual"
    p["g_form"] = 0.001
    p["g_persist"] = 0.001
    p["b_decay_form"] = 0.01
    p["b_decay_persist"] = 0.005
    p["b_growth_form"] = 0.1
    p["b_growth_persist"] = 0.1
    p["movement_bias"] = 0.3
    p["home_jitter"] = JITTER
    p["jitter_mode"] = "per_step"
    p["curve_follow"] = S.CURVE_FOLLOW
    p["deposit_prob_gain"] = S.DEPOSIT_PROB_GAIN
    p["excavate_prob_gain"] = S.EXCAVATE_PROB_GAIN
    p["excavate_prob_base"] = S.EXCAVATE_PROB_BASE
    return p


def label_components_region(mask):
    """Label Moore-connected components (8-connectivity) via BFS.
    Non-torus (no wrapping) — components within a rectangular region.
    Returns (labels, n_components)."""
    rows, cols = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    labels = np.zeros(mask.shape, dtype=np.int32)
    next_id = 0
    for r0 in range(rows):
        for c0 in range(cols):
            if mask[r0, c0] and not visited[r0, c0]:
                next_id += 1
                visited[r0, c0] = True
                labels[r0, c0] = next_id
                stack = [(r0, c0)]
                while stack:
                    r, c = stack.pop()
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            rr = r + dr
                            cc = c + dc
                            if 0 <= rr < rows and 0 <= cc < cols:
                                if mask[rr, cc] and not visited[rr, cc]:
                                    visited[rr, cc] = True
                                    labels[rr, cc] = next_id
                                    stack.append((rr, cc))
    return labels, next_id


def measure_region_percolation(mask):
    """Measure percolation properties of a binary mask within its region.
    mask is a 2D boolean array. Returns dict with:
    - fill_fraction: fraction of cells occupied
    - n_components: number of connected components
    - largest_size: size of largest component
    - largest_fraction: largest_size / total_occupied
    - spans_vertical: largest touches top and bottom rows
    - spans_horizontal: largest touches left and right cols
    - spans_both: spans_vertical and spans_horizontal
    """
    rows, cols = mask.shape
    total = rows * cols
    occupied = int(mask.sum())
    if occupied == 0:
        return {
            "fill_fraction": 0.0,
            "n_components": 0,
            "largest_size": 0,
            "largest_fraction": 0.0,
            "spans_vertical": False,
            "spans_horizontal": False,
            "spans_both": False,
        }

    labels, n_comp = label_components_region(mask)
    fill_frac = occupied / total

    # Find largest component
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0  # background
    largest_id = int(np.argmax(sizes))
    largest_size = int(sizes[largest_id])
    largest_fraction = largest_size / occupied

    # Spanning: does the largest component touch both edges in each dim?
    largest_mask = labels == largest_id
    spans_vertical = bool(largest_mask[0, :].any() and largest_mask[-1, :].any())
    spans_horizontal = bool(largest_mask[:, 0].any() and largest_mask[:, -1].any())

    return {
        "fill_fraction": round(fill_frac, 6),
        "n_components": n_comp,
        "largest_size": largest_size,
        "largest_fraction": round(largest_fraction, 6),
        "spans_vertical": spans_vertical,
        "spans_horizontal": spans_horizontal,
        "spans_both": spans_vertical and spans_horizontal,
    }


def run_structure_percolation(n_termites, decay, seed):
    """Run one 2-seed simulation and measure percolation of each structure
    within its half-region."""
    p = make_params(n_termites, decay)
    r = I14.run_two_region_hetero(p, seed=seed, n_seeds=2, mode="hetero")
    s = r["summary"]
    cells = s["final_n_structure_cells"]
    total_fill = cells / (GRID * GRID)

    # Extract final material by ID
    mat0 = r["_final_material_by_id"][0]
    mat1 = r["_final_material_by_id"][1]

    mid = GRID // 2

    # Left structure: restrict to left half (cols 0..mid-1)
    left_mask = mat0[:, :mid] > STRUCTURE_THRESHOLD
    # Right structure: restrict to right half (cols mid..end)
    right_mask = mat1[:, mid:] > STRUCTURE_THRESHOLD

    left_perc = measure_region_percolation(left_mask)
    right_perc = measure_region_percolation(right_mask)

    # Also measure the TOTAL structure (both IDs) across the full grid
    total_mask = (mat0 + mat1) > STRUCTURE_THRESHOLD
    total_perc = measure_region_percolation(total_mask)

    return {
        "n_termites": n_termites,
        "seed": seed,
        "total_fill_pct": round(100.0 * total_fill, 2),
        "stable": s["l2_stable"],
        "coexist_frac": round(s.get("l2_coexist_frac", 0.0), 4),
        "late_mean_lc": round(s.get("l2_late_mean_lc", 0.0), 2),
        "late_mean_rc": round(s.get("l2_late_mean_rc", 0.0), 2),
        "left_percolation": left_perc,
        "right_percolation": right_perc,
        "total_percolation": total_perc,
    }


def run_random_percolation(fill_frac, seed, region_shape=(GRID, GRID // 2)):
    """Generate a random site percolation mask at the given fill fraction
    and measure percolation. Control arm for the structure percolation."""
    rng = np.random.RandomState(seed)
    rows, cols = region_shape
    total = rows * cols
    n_occupied = int(round(fill_frac * total))
    flat = np.zeros(total, dtype=bool)
    flat[:n_occupied] = True
    rng.shuffle(flat)
    mask = flat.reshape(rows, cols)
    return measure_region_percolation(mask)


def run_sweep():
    t0 = time.time()
    results = {
        "description": "Percolation ceiling test — is the ~42% persistence "
                       "ceiling the Moore percolation threshold (~0.407)? "
                       "(queued-topic #301)",
        "grid": GRID,
        "half_grid_shape": [GRID, GRID // 2],
        "moore_threshold": 0.4072,
        "seeds": SEEDS,
        "boundary": "dual g_form=0.001 g_persist=0.001",
        "decay": DECAY,
        "date": "2026-11-24",
        "design": "3 n values × 4 seeds (structure) + 6 fills × 8 seeds (random)",
        "prediction": "If the ceiling = Moore threshold, each structure "
                      "percolates within its half at ~42% fill. If the gap is "
                      "significant, structures percolate at higher fill than "
                      "random sites.",
    }

    print("=" * 80)
    print("PERCOLATION CEILING TEST — queued-topic #301")
    print("=" * 80)
    print()
    print(f"Moore 8-neighbor percolation threshold: ~0.4072")
    print(f"Half-region shape: {GRID}×{GRID // 2} = {GRID * (GRID // 2)} cells")
    print()

    # --- Part 1: Structure percolation at the ceiling ---
    print("PART 1: Structure percolation at the ceiling")
    print("-" * 60)
    struct_results = {}
    for n_val in N_VALUES:
        n_key = f"n{n_val}"
        runs = []
        print(f"\nn={n_val} (decay={DECAY}):")
        for sd in SEEDS:
            m = run_structure_percolation(n_val, DECAY, sd)
            runs.append(m)
            lp = m["left_percolation"]
            rp = m["right_percolation"]
            print(f"  s={sd:4d}: total_fill={m['total_fill_pct']:6.2f}%  "
                  f"stable={m['stable']!s:5s}  "
                  f"left: fill={lp['fill_fraction']:.4f} "
                  f"span={'BOTH' if lp['spans_both'] else 'V' if lp['spans_vertical'] else 'H' if lp['spans_horizontal'] else 'none'} "
                  f"largest={lp['largest_fraction']:.4f} "
                  f"ncomp={lp['n_components']:4d}  "
                  f"right: fill={rp['fill_fraction']:.4f} "
                  f"span={'BOTH' if rp['spans_both'] else 'V' if rp['spans_vertical'] else 'H' if rp['spans_horizontal'] else 'none'} "
                  f"largest={rp['largest_fraction']:.4f} "
                  f"ncomp={rp['n_components']:4d}")

        mean_fill = np.mean([m["total_fill_pct"] for m in runs])
        mean_lf = np.mean([m["left_percolation"]["fill_fraction"] for m in runs])
        mean_rf = np.mean([m["right_percolation"]["fill_fraction"] for m in runs])
        left_span = sum(1 for m in runs if m["left_percolation"]["spans_both"])
        right_span = sum(1 for m in runs if m["right_percolation"]["spans_both"])
        left_largest = np.mean([m["left_percolation"]["largest_fraction"] for m in runs])
        right_largest = np.mean([m["right_percolation"]["largest_fraction"] for m in runs])
        stable_n = sum(1 for m in runs if m["stable"])

        print(f"\n  MEAN: total_fill={mean_fill:.2f}%  "
              f"left_fill={mean_lf:.4f}  right_fill={mean_rf:.4f}  "
              f"left_span={left_span}/4  right_span={right_span}/4  "
              f"left_largest={left_largest:.4f}  right_largest={right_largest:.4f}  "
              f"stable={stable_n}/4")

        struct_results[n_key] = {
            "n_termites": n_val,
            "runs": runs,
            "mean_total_fill": round(mean_fill, 2),
            "mean_left_fill": round(float(mean_lf), 6),
            "mean_right_fill": round(float(mean_rf), 6),
            "left_span_count": left_span,
            "right_span_count": right_span,
            "mean_left_largest": round(float(left_largest), 6),
            "mean_right_largest": round(float(right_largest), 6),
            "stable_count": stable_n,
        }

    results["structure"] = struct_results
    elapsed1 = time.time() - t0
    print(f"\n[Part 1 elapsed: {elapsed1/60:.1f} min]")

    # --- Part 2: Random-site percolation control ---
    print("\nPART 2: Random-site percolation control (half-region 160×80)")
    print("-" * 60)
    random_results = {}
    for fill in RANDOM_FILLS:
        fill_key = f"fill_{fill:.3f}"
        runs = []
        print(f"\nfill={fill:.3f} ({int(round(fill * GRID * (GRID // 2)))} / {GRID * (GRID // 2)} cells):")
        for sd in range(N_RANDOM_SEEDS):
            m = run_random_percolation(fill, sd, region_shape=(GRID, GRID // 2))
            runs.append(m)
            print(f"  s={sd}: fill={m['fill_fraction']:.4f}  "
                  f"span={'BOTH' if m['spans_both'] else 'V' if m['spans_vertical'] else 'H' if m['spans_horizontal'] else 'none'}  "
                  f"largest={m['largest_fraction']:.4f}  "
                  f"ncomp={m['n_components']:5d}")

        span_count = sum(1 for m in runs if m["spans_both"])
        mean_largest = np.mean([m["largest_fraction"] for m in runs])
        mean_ncomp = np.mean([m["n_components"] for m in runs])

        print(f"  MEAN: span={span_count}/{N_RANDOM_SEEDS}  "
              f"largest={mean_largest:.4f}  "
              f"ncomp={mean_ncomp:.1f}")

        random_results[fill_key] = {
            "fill": fill,
            "runs": runs,
            "span_count": span_count,
            "mean_largest": round(float(mean_largest), 6),
            "mean_ncomp": round(float(mean_ncomp), 1),
        }

    results["random"] = random_results
    elapsed2 = time.time() - t0
    print(f"\n[Part 2 elapsed: {elapsed2/60:.1f} min]")

    # --- Part 3: Summary comparison ---
    print("\n" + "=" * 80)
    print("SUMMARY: Structure vs Random percolation")
    print("=" * 80)
    print()
    print(f"Moore 8-neighbor threshold: ~0.4072")
    print()
    print("Random percolation (160×80 half-region):")
    for fill in RANDOM_FILLS:
        fk = f"fill_{fill:.3f}"
        r = random_results[fk]
        print(f"  fill={fill:.3f}: span={r['span_count']}/{N_RANDOM_SEEDS}  "
              f"largest_frac={r['mean_largest']:.4f}  "
              f"ncomp={r['mean_ncomp']:.1f}")
    print()
    print("Structure percolation (each ID within its half):")
    for n_val in N_VALUES:
        nk = f"n{n_val}"
        r = struct_results[nk]
        print(f"  n={n_val}: total_fill={r['mean_total_fill']:.2f}%  "
              f"left_fill={r['mean_left_fill']:.4f}  right_fill={r['mean_right_fill']:.4f}  "
              f"left_span={r['left_span_count']}/4  right_span={r['right_span_count']}/4  "
              f"left_largest={r['mean_left_largest']:.4f}  right_largest={r['mean_right_largest']:.4f}  "
              f"stable={r['stable_count']}/4")

    # Find the random percolation threshold (first fill where span > 50%)
    random_threshold = None
    for fill in RANDOM_FILLS:
        fk = f"fill_{fill:.3f}"
        r = random_results[fk]
        if r["span_count"] > N_RANDOM_SEEDS / 2:
            random_threshold = fill
            break
    print()
    if random_threshold is not None:
        print(f"Random percolation threshold (span > 50%): ~{random_threshold:.3f}")
    else:
        print("Random percolation threshold: not reached in tested range")
    print(f"Moore threshold: ~0.4072")
    print(f"Structure ceiling: ~0.42 (from Session 119)")
    print()

    results["elapsed_seconds"] = round(time.time() - t0, 1)
    out_path = os.path.join(SIM14_DIR, "output", "percolation_ceiling_test.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {out_path}")
    print(f"Total elapsed: {results['elapsed_seconds']/60:.1f} min")

    return results


if __name__ == "__main__":
    run_sweep()
