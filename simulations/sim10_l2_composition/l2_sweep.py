"""
Sim10 sweep: seed offset × material decay for the curvature channel and
baseline-pheromone control. Maps the L2 outcome (coexist / fragmented /
merged / dominance / destruction) across the parameter space.

Also includes the one-seed controls at each parameter point (the L1
baseline) and seed-robustness passes (4 seeds) at the headline points.
"""

import os
import sys
import json

SIM10_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SIM10_DIR, "..", "sim09_curvature_channel"))
sys.path.insert(0, SIM10_DIR)
import sim10
import sim09 as S  # noqa: F401

OUTPUT = os.path.join(SIM10_DIR, "output", "l2_sweep.json")

# Sweep grid: offset_frac × decay × channel
OFFSETS = [0.15, 0.25, 0.35, 0.45]
DECAYS = [0.002, 0.003, 0.005, 0.008, 0.010, 0.015]
CHANNELS = ["curvature", "baseline_pheromone"]
SEEDS = [42, 123, 256, 7]


def base_params(channel, decay):
    p = {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "structure_threshold": S.STRUCTURE_THRESHOLD,
        "material_decay": decay,
    }
    if channel == "curvature":
        p["channel"] = "curvature"
        p["d"] = 1.0
        p["deposit_prob_base"] = 0.01
    else:
        p["channel"] = "baseline_pheromone"
        p["deposit_base"] = 0.01
    return p


def main():
    results = []
    old_offset = sim10.SEED_OFFSET_FRAC
    total = len(OFFSETS) * len(DECAYS) * len(CHANNELS) * len(SEEDS) * 2  # ×2 for 1/2 seed
    done = 0
    for channel in CHANNELS:
        for offset in OFFSETS:
            sim10.SEED_OFFSET_FRAC = offset
            for decay in DECAYS:
                params = base_params(channel, decay)
                for seed in SEEDS:
                    for n_seeds in (2, 1):
                        r = sim10.run_two_region(params, seed=seed, n_seeds=n_seeds)
                        s = r["summary"]
                        results.append({
                            "channel": channel,
                            "offset": offset,
                            "decay": decay,
                            "seed": seed,
                            "n_seeds": n_seeds,
                            "l2_crossed": s["l2_crossed"],
                            "l2_outcome": s["l2_outcome"],
                            "l2_stable": s["l2_stable"],
                            "l2_late_mean_lc": round(s["l2_late_mean_lc"], 1),
                            "l2_late_mean_rc": round(s["l2_late_mean_rc"], 1),
                            "l2_left_retain": round(s["l2_left_retain"], 2),
                            "l2_right_retain": round(s["l2_right_retain"], 2),
                            "cells": s["final_n_structure_cells"],
                            "crossed_h7": s["crossed_h7"],
                        })
                        done += 1
                        if done % 20 == 0:
                            print(f"  {done}/{total}...")
    sim10.SEED_OFFSET_FRAC = old_offset
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Wrote {OUTPUT} ({len(results)} runs)")

    # Summary table: 2-seed curvature, per offset×decay, outcome counts
    # across 4 seeds.
    print("\n=== 2-seed CURVATURE: outcome by offset×decay (4 seeds) ===")
    print(f"{'offset':>7} {'decay':>7} {'coexist':>8} {'frag':>6} {'merge':>6} "
          f"{'dom':>5} {'dest':>5} {'stable':>7} {'meanLC':>7} {'meanRC':>7}")
    for offset in OFFSETS:
        for decay in DECAYS:
            subset = [r for r in results if r["channel"] == "curvature"
                      and r["offset"] == offset and r["decay"] == decay
                      and r["n_seeds"] == 2]
            counts = {"coexist": 0, "fragmented": 0, "none": 0,
                      "dominance": 0, "destruction": 0}
            stable = 0
            mlc = mrc = 0.0
            for r in subset:
                counts[r["l2_outcome"]] = counts.get(r["l2_outcome"], 0) + 1
                if r["l2_stable"]:
                    stable += 1
                mlc += r["l2_late_mean_lc"]
                mrc += r["l2_late_mean_rc"]
            n = len(subset)
            mlc /= max(1, n)
            mrc /= max(1, n)
            print(f"{offset:7.2f} {decay:7.3f} {counts['coexist']:8d} "
                  f"{counts['fragmented']:6d} {counts['none']:6d} "
                  f"{counts['dominance']:5d} {counts['destruction']:5d} "
                  f"{stable:7d} {mlc:7.1f} {mrc:7.1f}")

    print("\n=== 2-seed BASELINE: outcome by offset×decay (4 seeds) ===")
    print(f"{'offset':>7} {'decay':>7} {'coexist':>8} {'frag':>6} {'merge':>6} "
          f"{'dom':>5} {'dest':>5} {'stable':>7} {'meanLC':>7} {'meanRC':>7}")
    for offset in OFFSETS:
        for decay in DECAYS:
            subset = [r for r in results if r["channel"] == "baseline_pheromone"
                      and r["offset"] == offset and r["decay"] == decay
                      and r["n_seeds"] == 2]
            counts = {"coexist": 0, "fragmented": 0, "none": 0,
                      "dominance": 0, "destruction": 0}
            stable = 0
            mlc = mrc = 0.0
            for r in subset:
                counts[r["l2_outcome"]] = counts.get(r["l2_outcome"], 0) + 1
                if r["l2_stable"]:
                    stable += 1
                mlc += r["l2_late_mean_lc"]
                mrc += r["l2_late_mean_rc"]
            n = len(subset)
            mlc /= max(1, n)
            mrc /= max(1, n)
            print(f"{offset:7.2f} {decay:7.3f} {counts['coexist']:8d} "
                  f"{counts['fragmented']:6d} {counts['none']:6d} "
                  f"{counts['dominance']:5d} {counts['destruction']:5d} "
                  f"{stable:7d} {mlc:7.1f} {mrc:7.1f}")

    # 1-seed control: should NEVER show coexist (only one structure)
    print("\n=== 1-seed control: any coexist? (should be 0) ===")
    coexist_1seed = [r for r in results if r["n_seeds"] == 1
                     and r["l2_outcome"] == "coexist"]
    print(f"  1-seed coexist count: {len(coexist_1seed)} / "
          f"{len([r for r in results if r['n_seeds'] == 1])}")


if __name__ == "__main__":
    main()
