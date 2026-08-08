"""
patch_recovery_probe.py — the spatially-targeted recovery acid test (queued-topic #60).

The grid-wide `recovery = total_material / pre_perturb_total` cannot distinguish
scar repair from volume restoration elsewhere. The baseline's 47.34× "recovery"
(Session 18) was unbounded material accumulation, not targeted repair. This probe
adds `patch_recovery = material_in_patch / pre_perturb_material_in_patch` (Part 8b)
and runs the perturbation experiment at BOTH the default params (grid-saturating)
and the tuned probe params (dpb=0.01, decay=0.002, mass-plateauing) where the
crossing fires properly.

Reports both grid-wide and patch recovery for curvature vs baseline, plus the
patch recovery trajectory (does the scar refill monotonically, stall, or
overshoot?). Determinism verified by running each condition twice and diffing.

Methodology: per-criterion patch recovery trajectory is reported (not just the
final number), so a null or partial result is decomposable.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim09

OUTPUT_DIR = sim09.OUTPUT_DIR
SEED = 42

# Two parameter regimes:
# 1. DEFAULT: grid_size=100, n=200, steps=4000, dpb=0.10, decay=0.0005
#    (grid-saturating — the original Session 18 perturbation run)
# 2. TUNED: grid_size=80, n=150, steps=2000, dpb=0.01, decay=0.002
#    (mass-plateauing — where the corrected detector fires the crossing)
REGIMES = {
    "default": {
        "grid_size": 100, "n_termites": 200, "steps": 4000,
        "sample_every": 25, "structure_threshold": sim09.STRUCTURE_THRESHOLD,
        "d": sim09.D_SMOOTH, "material_decay": sim09.MATERIAL_DECAY,
        "deposit_prob_base": sim09.DEPOSIT_PROB_BASE,
    },
    "tuned": {
        "grid_size": 80, "n_termites": 150, "steps": 2000,
        "sample_every": 25, "structure_threshold": sim09.STRUCTURE_THRESHOLD,
        "d": 1.0, "material_decay": 0.002,
        "deposit_prob_base": 0.01,
    },
}


def curv_params(regime):
    p = dict(REGIMES[regime])
    p["channel"] = "curvature"
    return p


def base_params(regime):
    p = dict(REGIMES[regime])
    p["channel"] = "baseline_pheromone"
    p["pheromone_decay"] = sim09.PHEROMONE_DECAY
    p["pheromone_diffuse"] = sim09.PHEROMONE_DIFFUSE
    p["deposit_base"] = sim09.DEPOSIT_BASE
    p["deposit_gain"] = sim09.DEPOSIT_GAIN
    # baseline doesn't use deposit_prob_base (curvature-specific); remove it
    p.pop("deposit_prob_base", None)
    return p


def trajectory(history):
    """Extract the patch/mirror recovery trajectory from post-damage records."""
    post = [(r["step"], r.get("patch_recovery"), r.get("mirror_recovery"),
             r.get("recovery"), r["total_material"], r["n_structure_cells"])
            for r in history if r.get("patch_recovery") is not None]
    if not post:
        return {"n_post_damage": 0}
    first = post[0]
    last = post[-1]
    # targeted repair = patch - mirror (positive = scar grows faster)
    tr_first = (first[1] - first[2]) if (first[1] is not None and first[2] is not None) else None
    tr_last = (last[1] - last[2]) if (last[1] is not None and last[2] is not None) else None
    tr_traj = [(p[1] - p[2]) for p in post if p[1] is not None and p[2] is not None]
    tr_peak = max(tr_traj) if tr_traj else None
    tr_trough = min(tr_traj) if tr_traj else None
    return {
        "n_post_damage": len(post),
        "patch_first": round(first[1], 4),
        "patch_last": round(last[1], 4),
        "patch_peak": round(max(p[1] for p in post), 4),
        "mirror_first": round(first[2], 4) if first[2] is not None else None,
        "mirror_last": round(last[2], 4) if last[2] is not None else None,
        "mirror_peak": round(max(p[2] for p in post), 4) if all(p[2] is not None for p in post) else None,
        "targeted_repair_first": round(tr_first, 4) if tr_first is not None else None,
        "targeted_repair_last": round(tr_last, 4) if tr_last is not None else None,
        "targeted_repair_peak": round(tr_peak, 4) if tr_peak is not None else None,
        "targeted_repair_trough": round(tr_trough, 4) if tr_trough is not None else None,
        "grid_first": round(first[3], 4) if first[3] is not None else None,
        "grid_last": round(last[3], 4) if last[3] is not None else None,
        "first_step": first[0],
        "last_step": last[0],
    }


def run_one(params, seed, perturb):
    r = sim09.run_condition(params, seed=seed, perturb=perturb)
    s = r["summary"]
    t = trajectory(r["history"])
    return {
        "crossed": s["crossed"],
        "crossing_step": s["crossing_step"],
        "recovery_final": s["recovery_final"],
        "patch_recovery_final": s["patch_recovery_final"],
        "mirror_recovery_final": s["mirror_recovery_final"],
        "targeted_repair_final": ((s["patch_recovery_final"] - s["mirror_recovery_final"])
                                  if s["patch_recovery_final"] is not None
                                  and s["mirror_recovery_final"] is not None
                                  else None),
        "final_cells": s["final_n_structure_cells"],
        "perturb_at": s["perturb_at"],
        "perturb_frac": s["perturb_frac"],
        "trajectory": t,
    }


def main():
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    perturb_spec = {"frac": 0.25}  # at = default 0.6 * steps

    results = {}
    for regime in ("tuned", "default"):
        print(f"\n=== Regime: {regime} ===")
        steps = REGIMES[regime]["steps"]
        perturb_spec["at"] = int(0.6 * steps)

        regime_results = {}
        for name, p in (("curvature", curv_params(regime)),
                        ("baseline", base_params(regime))):
            print(f"  Running {name} (perturbation)...")
            r1 = run_one(p, SEED, perturb_spec)
            # determinism: run twice, diff key fields
            r2 = run_one(p, SEED, perturb_spec)
            det_ok = (r1["crossed"] == r2["crossed"]
                      and r1["recovery_final"] == r2["recovery_final"]
                      and r1["patch_recovery_final"] == r2["patch_recovery_final"]
                      and r1["final_cells"] == r2["final_cells"])
            print(f"    crossed={r1['crossed']} "
                  f"recovery={r1['recovery_final']:.2f} "
                  f"patch={r1['patch_recovery_final']:.3f} "
                  f"mirror={r1['mirror_recovery_final']:.3f} "
                  f"targeted={r1['targeted_repair_final']:+.3f} "
                  f"cells={r1['final_cells']} "
                  f"deterministic={det_ok}")
            regime_results[name] = {"run": r1, "deterministic": det_ok}
        results[regime] = regime_results

        # comparison
        c = regime_results["curvature"]["run"]
        b = regime_results["baseline"]["run"]
        print(f"  --- comparison ---")
        print(f"  curvature  recovery={c['recovery_final']:.2f} "
              f"patch={c['patch_recovery_final']:.3f} "
              f"mirror={c['mirror_recovery_final']:.3f} "
              f"targeted={c['targeted_repair_final']:+.3f}")
        print(f"  baseline   recovery={b['recovery_final']:.2f} "
              f"patch={b['patch_recovery_final']:.3f} "
              f"mirror={b['mirror_recovery_final']:.3f} "
              f"targeted={b['targeted_repair_final']:+.3f}")
        print(f"  targeted:  curv - base = {c['targeted_repair_final'] - b['targeted_repair_final']:+.3f}")

    out_path = os.path.join(OUTPUT_DIR, "patch_recovery_probe.json")
    with open(out_path, "w") as f:
        json.dump({
            "seed": SEED,
            "perturb_frac": 0.25,
            "regimes": {regime: {
                name: {"run": v["run"], "deterministic": v["deterministic"]}
                for name, v in rv.items()
            } for regime, rv in results.items()},
        }, f, indent=2)
    print(f"\nWrote {out_path}")
    print(f"Elapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
