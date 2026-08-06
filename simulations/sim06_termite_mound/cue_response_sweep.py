#!/usr/bin/env python3
"""cue_response_sweep.py — Session 22: the cue-based non-saturating control.

Completes the 2×2 (queued-topic #67):
  - action × {linear, saturating}  — tested in sim09 (Session 21)
  - cue × {linear, saturating}     — tested HERE (sim06 with deposit_response)

sim06's as-built deposit rule is the saturating cue  p = base + gain·φ/(1+φ),
flat above φ≈1 (H11's self-defeating cue channel). The non-saturating cue is
p = base + gain·φ (clamped to 1.0). Both are cue-based: the pheromone field is
the cue the agent reads; only the response curve differs.

Prediction (from H11's Session-21 refinement — action-based is primary):
  the non-saturating *cue* should NOT cross more than the saturating cue, and
  may cross less, because making the cue non-saturating does not change the
  fundamental cue-vs-action distinction. If the non-saturating cue crosses
  substantially MORE, H11's *strict* original claim (non-saturating is what
  matters, regardless of cue/action) would be supported over the refinement.

The sweep varies response × self_maintenance × deposit_base × phero_follow
at a fixed, crossing-friendly material_decay, with:
  - determinism check (run twice, diff summaries)
  - seed robustness (4 seeds) on the key conditions
  - late_hold_rate (fraction of late-window records where all criteria hold)
  - per-criterion pass rates (c1/c2/c3) for diagnosis
"""

import json
import os
import time

import numpy as np

import sim06

SIM_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SIM_DIR, "output")

# A crossing-friendly regime (from sweep_crossing_results.json): md=0.002
# crosses 286/420 combos; pf=0.9 crosses broadly. We hold material_decay and
# deposit_gain fixed and sweep the response curve + structural params.
MATERIAL_DECAY = 0.002
DEPOSIT_GAIN = 0.85
GRID = 80
N_TERMITES = 150
STEPS = 2000
SAMPLE_EVERY = 25
SEEDS = [42, 7, 123, 256]


def _criterion_pass_rates(history, params):
    stab_thresh = params.get("stab_thresh", sim06.STAB_THRESH)
    phero_elev = params.get("phero_elev_thresh", sim06.PHERO_ELEV_THRESH)
    growth_thresh = params.get("growth_thresh", sim06.GROWTH_THRESH)
    constrain_thresh = params.get("constrain_thresh", sim06.CONSTRAIN_THRESH)
    n = len(history)
    if n == 0:
        return {"c1": 0.0, "c2": 0.0, "c3": 0.0}
    c1 = c2 = c3 = 0
    for r in history:
        growth = r.get("material_growth_rate")
        saturated = growth is not None and abs(growth) < growth_thresh
        if r["structure_stability"] >= stab_thresh:
            c1 += 1
        if r["mean_pheromone_over_structure"] >= phero_elev and saturated:
            c2 += 1
        if r["deposit_on_structure_fraction"] >= constrain_thresh:
            c3 += 1
    return {"c1": c1 / n, "c2": c2 / n, "c3": c3 / n}


def _late_hold_rate(history, params, frac=0.25):
    """Fraction of late-window records where ALL crossing criteria hold.
    Analogous to sim09's late_hold_rate: distinguishes a crossing that holds
    from one that flickers on and off."""
    if not history:
        return 0.0
    stab_thresh = params.get("stab_thresh", sim06.STAB_THRESH)
    phero_elev = params.get("phero_elev_thresh", sim06.PHERO_ELEV_THRESH)
    growth_thresh = params.get("growth_thresh", sim06.GROWTH_THRESH)
    constrain_thresh = params.get("constrain_thresh", sim06.CONSTRAIN_THRESH)
    n_late = max(1, len(history) * frac)
    late = history[-int(n_late):]
    held = 0
    for r in late:
        growth = r.get("material_growth_rate")
        saturated = growth is not None and abs(growth) < growth_thresh
        c1 = r["structure_stability"] >= stab_thresh
        c2 = r["mean_pheromone_over_structure"] >= phero_elev and saturated
        c3 = r["deposit_on_structure_fraction"] >= constrain_thresh
        if c1 and c2 and c3:
            held += 1
    return held / len(late)


def _summarise(result, params):
    s = result["summary"]
    rates = _criterion_pass_rates(result["history"], params)
    hold = _late_hold_rate(result["history"], params)
    return {
        "crossed": bool(s["crossed"]),
        "crossing_step": s["crossing_step"],
        "stable_crossed": hold >= 0.90,
        "late_hold_rate": round(hold, 4),
        "retention": round(s["retention"], 4),
        "mean_stability_last25": round(s["mean_stability_last25"], 4),
        "final_cells": s["final_n_structure_cells"],
        "n_pillars": result["history"][-1]["n_pillars"] if result["history"] else 0,
        "mean_phero_final": round(result["history"][-1]["mean_pheromone_over_structure"], 4) if result["history"] else 0,
        "max_phero_final": round(result["history"][-1]["max_pheromone"], 4) if result["history"] else 0,
        "c1": round(rates["c1"], 3),
        "c2": round(rates["c2"], 3),
        "c3": round(rates["c3"], 3),
    }


def _base_params(response, sm, db, pf):
    p = {
        "grid_size": GRID, "n_termites": N_TERMITES, "steps": STEPS,
        "sample_every": SAMPLE_EVERY,
        "deposit_response": response,
        "self_maintenance": sm,
        "material_decay": MATERIAL_DECAY,
        "deposit_base": db,
        "deposit_gain": DEPOSIT_GAIN,
        "phero_follow": pf,
    }
    if sm:
        p["maintain_gain"] = 0.1
    return p


def main():
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    responses = ["saturating", "linear"]
    self_maints = [False, True]
    deposit_bases = [0.005, 0.01, 0.02, 0.03]
    phero_follows = [0.7, 0.8, 0.9, 0.95]

    # Phase 1: single-seed (42) factorial for the headline comparison
    rows = []
    for resp in responses:
        for sm in self_maints:
            for db in deposit_bases:
                for pf in phero_follows:
                    p = _base_params(resp, sm, db, pf)
                    r = sim06.run_condition(p, 42)
                    rows.append({
                        "response": resp, "self_maintenance": sm,
                        "deposit_base": db, "phero_follow": pf, "seed": 42,
                        **_summarise(r, p),
                    })
    # Phase 2: determinism — re-run a sample of 8 conditions, diff summaries
    determinism_samples = [
        ("saturating", False, 0.01, 0.9),
        ("linear", False, 0.01, 0.9),
        ("saturating", True, 0.02, 0.95),
        ("linear", True, 0.02, 0.95),
    ]
    det_ok = True
    for resp, sm, db, pf in determinism_samples:
        p = _base_params(resp, sm, db, pf)
        r1 = sim06.run_condition(p, 42)
        r2 = sim06.run_condition(p, 42)
        s1 = _summarise(r1, p)
        s2 = _summarise(r2, p)
        if s1 != s2:
            det_ok = False
            print(f"  DETERMINISM FAIL: {resp} sm={sm} db={db} pf={pf}")
    # Phase 3: seed robustness on the 8 key conditions
    # (response × self_maintenance × 2 param sets)
    robust_conditions = [
        ("saturating", False, 0.01, 0.9),
        ("linear", False, 0.01, 0.9),
        ("saturating", False, 0.02, 0.95),
        ("linear", False, 0.02, 0.95),
        ("saturating", True, 0.01, 0.9),
        ("linear", True, 0.01, 0.9),
        ("saturating", True, 0.02, 0.95),
        ("linear", True, 0.02, 0.95),
    ]
    robust = {}
    for resp, sm, db, pf in robust_conditions:
        p = _base_params(resp, sm, db, pf)
        holds = []
        crossed = []
        for seed in SEEDS:
            r = sim06.run_condition(p, seed)
            summ = _summarise(r, p)
            holds.append(summ["late_hold_rate"])
            crossed.append(summ["crossed"])
        robust[f"{resp}_sm{sm}_db{db}_pf{pf}"] = {
            "response": resp, "self_maintenance": sm,
            "deposit_base": db, "phero_follow": pf,
            "seeds": SEEDS,
            "crossed": crossed,
            "n_crossed": sum(crossed),
            "holds": holds,
            "mean_hold": round(float(np.mean(holds)), 4),
            "stable_count": sum(1 for h in holds if h >= 0.90),
        }

    elapsed = time.time() - t0

    # Aggregate: crossing rates by response (seed-42 factorial)
    sat_rows = [r for r in rows if r["response"] == "saturating"]
    lin_rows = [r for r in rows if r["response"] == "linear"]
    sat_crossed = sum(1 for r in sat_rows if r["crossed"])
    lin_crossed = sum(1 for r in lin_rows if r["crossed"])
    sat_stable = sum(1 for r in sat_rows if r["stable_crossed"])
    lin_stable = sum(1 for r in lin_rows if r["stable_crossed"])
    sat_hold = float(np.mean([r["late_hold_rate"] for r in sat_rows]))
    lin_hold = float(np.mean([r["late_hold_rate"] for r in lin_rows]))

    output = {
        "config": {"grid_size": GRID, "n_termites": N_TERMITES, "steps": STEPS,
                   "sample_every": SAMPLE_EVERY, "material_decay": MATERIAL_DECAY,
                   "deposit_gain": DEPOSIT_GAIN, "seeds": SEEDS},
        "elapsed_seconds": round(elapsed, 1),
        "all_deterministic": det_ok,
        "factorial_seed42": {
            "n_conditions": len(rows),
            "saturating": {"crossed": sat_crossed, "stable": sat_stable,
                           "mean_hold": round(sat_hold, 4)},
            "linear": {"crossed": lin_crossed, "stable": lin_stable,
                       "mean_hold": round(lin_hold, 4)},
        },
        "rows": rows,
        "seed_robustness": robust,
    }
    out_path = os.path.join(OUTPUT_DIR, "cue_response_sweep.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n=== cue_response_sweep: {len(rows)} runs, {elapsed:.0f}s ===")
    print(f"Determinism: {'OK' if det_ok else 'FAIL'}")
    print(f"\nSeed-42 factorial ({len(rows)} conditions):")
    print(f"  saturating cue: crossed {sat_crossed}/{len(sat_rows)}, "
          f"stable {sat_stable}/{len(sat_rows)}, mean hold {sat_hold:.3f}")
    print(f"  linear cue:     crossed {lin_crossed}/{len(lin_rows)}, "
          f"stable {lin_stable}/{len(lin_rows)}, mean hold {lin_hold:.3f}")
    print(f"\nSeed robustness (4 seeds, 8 key conditions):")
    for k, v in robust.items():
        print(f"  {k}: crossed {v['n_crossed']}/4, stable {v['stable_count']}/4, "
              f"mean hold {v['mean_hold']:.3f}, holds {v['holds']}")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
