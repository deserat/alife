"""
Moore percolation threshold test (queued-topic #301).

The ~42% persistence ceiling (where stable composition collapses) is ~1.3pp
above the Moore 8-neighbor site percolation threshold (~0.407). Is this
coincidence or causation?

Test: at the ceiling (n=2500, decay=0.002, 4 seeds, dual g=0.001), measure
the spanning cluster fraction of the COMBINED structure (both IDs' material).
Compare to random-site percolation at matched fill on the same 160×160 Moore
lattice (100 realizations).

If the structure percolates at ~42% fill (spanning cluster, like random),
the ceiling IS the Moore threshold. If the structure is fragmented (5-6
components, no spanning cluster), the ceiling is NOT the percolation threshold
— it's boundary over-splitting at a fill that happens to be near the Moore
threshold.

Also: measure each individual ID's structure separately — at ~21% fill each,
random percolation would NOT span (below threshold). The combined structure
at ~42% is the one that could percolate.

Config: 160×160, dual mode, focal bias=0.3, per_step jitter=10, decay=0.002.
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

# Reuse the component labeling from percolation_spanning.py
sys.path.insert(0, os.path.join(SIM14_DIR))
from percolation_spanning import label_components, component_stats  # noqa: E402

OUTPUT_PATH = os.path.join(SIM14_DIR, "output", "moore_threshold_test.json")

GRID = 160
JITTER = 10.0
SEEDS = [42, 123, 256, 999]
STRUCT_THRESHOLD = 1.0


def make_ceiling_params(n_termites, decay):
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


def measure_structure(mat_field):
    """Measure percolation metrics on a material field."""
    struct_mask = mat_field > STRUCT_THRESHOLD
    total_cells = int(struct_mask.sum())
    fill_pct = total_cells / (GRID * GRID) * 100

    if total_cells == 0:
        return {
            "total_cells": 0, "fill_pct": 0.0, "n_components": 0,
            "largest_size": 0, "largest_frac": 0.0,
            "spans": False, "spans_x": False, "spans_y": False,
            "n_spanning": 0, "mean_comp_size": 0.0,
        }

    labels, n_comp = label_components(struct_mask)
    stats = component_stats(labels, n_comp)
    sizes = [st["size"] for st in stats]
    largest = stats[0]
    n_spanning = sum(1 for st in stats if st["spans"])

    return {
        "total_cells": total_cells,
        "fill_pct": round(fill_pct, 2),
        "n_components": n_comp,
        "largest_size": largest["size"],
        "largest_frac": round(largest["size"] / total_cells, 4),
        "spans": bool(largest["spans"]),
        "spans_x": bool(largest["spans_x"]),
        "spans_y": bool(largest["spans_y"]),
        "n_spanning": n_spanning,
        "mean_comp_size": round(float(np.mean(sizes)), 2) if sizes else 0.0,
        "sizes_top5": sizes[:5],
    }


def random_percolation(fill_frac, grid_size, rng, n_realizations=100):
    """Generate random-site percolation at given fill fraction on Moore lattice."""
    results = []
    for i in range(n_realizations):
        mask = rng.random((grid_size, grid_size)) < fill_frac
        total_cells = int(mask.sum())
        fill_pct = total_cells / (grid_size * grid_size) * 100

        if total_cells == 0:
            results.append({
                "fill_pct": round(fill_pct, 2), "n_components": 0,
                "largest_frac": 0.0, "spans": False, "n_spanning": 0,
                "mean_comp_size": 0.0,
            })
            continue

        labels, n_comp = label_components(mask)
        stats = component_stats(labels, n_comp)
        sizes = [st["size"] for st in stats]
        largest = stats[0]
        n_spanning = sum(1 for st in stats if st["spans"])

        results.append({
            "fill_pct": round(fill_pct, 2),
            "n_components": n_comp,
            "largest_frac": round(largest["size"] / total_cells, 4),
            "spans": bool(largest["spans"]),
            "n_spanning": n_spanning,
            "mean_comp_size": round(float(np.mean(sizes)), 2),
        })
    return results


def run_ceiling_simulations():
    """Run at the ceiling: n=2500, decay=0.002, 4 seeds, dual g=0.001."""
    results = []
    for seed in SEEDS:
        p = make_ceiling_params(2500, 0.002)
        r = I14.run_two_region_hetero(p, seed=seed, n_seeds=2, mode="hetero")
        s = r["summary"]

        mat = np.array(r["_final_material"], dtype=np.float64)
        mat_by_id = [
            np.array(r["_final_material_by_id"][0], dtype=np.float64),
            np.array(r["_final_material_by_id"][1], dtype=np.float64),
        ]

        # Combined structure (both IDs)
        combined = measure_structure(mat)

        # Per-ID structures
        left = measure_structure(mat_by_id[0])
        right = measure_structure(mat_by_id[1])

        results.append({
            "seed": seed,
            "fill_pct": round(s.get("fill_pct", 0.0), 2),
            "stable": s.get("stable_l2", False),
            "coexist_frac": s.get("coexist_frac", 0.0),
            "late_mean_lc": s.get("late_mean_lc", 0.0),
            "late_mean_rc": s.get("late_mean_rc", 0.0),
            "combined": combined,
            "left_id": left,
            "right_id": right,
        })
        print(f"  seed={seed}: fill={combined['fill_pct']:.1f}% "
              f"ncomp={combined['n_components']} "
              f"largest_frac={combined['largest_frac']:.3f} "
              f"spans={combined['spans']} "
              f"stable={s.get('stable_l2', False)}")
    return results


def run_random_comparison():
    """Generate random-site percolation at matched fill (~42%, ~21%)."""
    rng = np.random.default_rng(2026)
    results = {}

    # At ~42% fill (the ceiling, combined structure)
    results["42pct"] = random_percolation(0.42, GRID, rng, n_realizations=100)

    # At ~21% fill (each individual ID's structure)
    results["21pct"] = random_percolation(0.21, GRID, rng, n_realizations=100)

    # At the Moore threshold exactly (~40.7%)
    results["407pct"] = random_percolation(0.407, GRID, rng, n_realizations=100)

    # Summary statistics
    for key, runs in results.items():
        spans = sum(1 for r in runs if r["spans"])
        fill_mean = np.mean([r["fill_pct"] for r in runs])
        largest_mean = np.mean([r["largest_frac"] for r in runs])
        comp_mean = np.mean([r["n_components"] for r in runs])
        print(f"  random {key}: fill_mean={fill_mean:.1f}% "
              f"spans={spans}/100 "
              f"largest_frac_mean={largest_mean:.3f} "
              f"ncomp_mean={comp_mean:.1f}")

    return results


def main():
    t0 = time.time()
    print("=== Moore Percolation Threshold Test (queued-topic #301) ===")
    print()
    print("Part 1: Simulations at the ceiling (n=2500, decay=0.002)")
    ceiling_results = run_ceiling_simulations()

    print()
    print("Part 2: Random-site percolation at matched fill")
    random_results = run_random_comparison()

    # Aggregate ceiling results
    ceiling_fills = [r["combined"]["fill_pct"] for r in ceiling_results]
    ceiling_spans = [r["combined"]["spans"] for r in ceiling_results]
    ceiling_ncomps = [r["combined"]["n_components"] for r in ceiling_results]
    ceiling_largest = [r["combined"]["largest_frac"] for r in ceiling_results]
    ceiling_stable = [r["stable"] for r in ceiling_results]

    # Aggregate random results
    random_42_spans = sum(1 for r in random_results["42pct"] if r["spans"])
    random_42_largest = np.mean([r["largest_frac"] for r in random_results["42pct"]])
    random_42_ncomp = np.mean([r["n_components"] for r in random_results["42pct"]])

    print()
    print("=== Comparison ===")
    print(f"Ceiling sims: fill={np.mean(ceiling_fills):.1f}% "
          f"spans={sum(ceiling_spans)}/4 "
          f"mean_ncomp={np.mean(ceiling_ncomps):.1f} "
          f"mean_largest_frac={np.mean(ceiling_largest):.3f} "
          f"stable={sum(ceiling_stable)}/4")
    print(f"Random 42%:    spans={random_42_spans}/100 "
          f"mean_ncomp={random_42_ncomp:.1f} "
          f"mean_largest_frac={random_42_largest:.3f}")

    # Per-ID
    left_fills = [r["left_id"]["fill_pct"] for r in ceiling_results]
    left_spans = [r["left_id"]["spans"] for r in ceiling_results]
    left_ncomps = [r["left_id"]["n_components"] for r in ceiling_results]
    print(f"Left ID:       fill={np.mean(left_fills):.1f}% "
          f"spans={sum(left_spans)}/4 "
          f"mean_ncomp={np.mean(left_ncomps):.1f}")

    right_fills = [r["right_id"]["fill_pct"] for r in ceiling_results]
    right_spans = [r["right_id"]["spans"] for r in ceiling_results]
    right_ncomps = [r["right_id"]["n_components"] for r in ceiling_results]
    print(f"Right ID:      fill={np.mean(right_fills):.1f}% "
          f"spans={sum(right_spans)}/4 "
          f"mean_ncomp={np.mean(right_ncomps):.1f}")

    random_21_spans = sum(1 for r in random_results["21pct"] if r["spans"])
    random_21_ncomp = np.mean([r["n_components"] for r in random_results["21pct"]])
    print(f"Random 21%:    spans={random_21_spans}/100 "
          f"mean_ncomp={random_21_ncomp:.1f}")

    # Determinism check
    print()
    print("Part 3: Determinism check (2 identical runs)")
    p = make_ceiling_params(2500, 0.002)
    r1 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    r2 = I14.run_two_region_hetero(p, seed=42, n_seeds=2, mode="hetero")
    mat1 = np.array(r1["_final_material"])
    mat2 = np.array(r2["_final_material"])
    det_ok = np.allclose(mat1, mat2)
    print(f"  Determinism: {'VERIFIED' if det_ok else 'FAILED'}")
    print(f"  mat1 sum={mat1.sum():.2f} mat2 sum={mat2.sum():.2f}")

    output = {
        "ceiling_sims": ceiling_results,
        "random_percolation": {
            key: {
                "summary": {
                    "fill_mean": round(float(np.mean([r["fill_pct"] for r in runs])), 2),
                    "spans_count": sum(1 for r in runs if r["spans"]),
                    "spans_frac": round(sum(1 for r in runs if r["spans"]) / len(runs), 3),
                    "largest_frac_mean": round(float(np.mean([r["largest_frac"] for r in runs])), 4),
                    "n_components_mean": round(float(np.mean([r["n_components"] for r in runs])), 1),
                    "n_realizations": len(runs),
                },
                "runs": runs,
            }
            for key, runs in random_results.items()
        },
        "comparison": {
            "ceiling_fill_mean": round(float(np.mean(ceiling_fills)), 2),
            "ceiling_spans": sum(ceiling_spans),
            "ceiling_n_seeds": len(ceiling_results),
            "ceiling_mean_ncomp": round(float(np.mean(ceiling_ncomps)), 1),
            "ceiling_mean_largest_frac": round(float(np.mean(ceiling_largest)), 4),
            "ceiling_stable": sum(ceiling_stable),
            "random_42_spans": random_42_spans,
            "random_42_n_realizations": 100,
            "random_42_mean_ncomp": round(random_42_ncomp, 1),
            "random_42_mean_largest_frac": round(random_42_largest, 4),
            "moore_threshold": 0.407,
            "ceiling_fill": round(float(np.mean(ceiling_fills)), 2),
            "gap_pp": round(float(np.mean(ceiling_fills)) - 40.7, 2),
        },
        "determinism_ok": det_ok,
        "elapsed_sec": round(time.time() - t0, 1),
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nOutput: {OUTPUT_PATH}")
    print(f"Elapsed: {output['elapsed_sec']}s")


if __name__ == "__main__":
    main()
