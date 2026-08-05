"""
saturating_action_sweep.py — the saturating-action control (queued-topic 64).

Session 20's recruit-vs-limit isolation found the recruit half (curvature
routing) is necessary + almost-sufficient for a STABLE crossing. But the
recruit half is action-based AND non-saturating simultaneously — the two
properties H11 says matter are confounded. This script disentangles them.

THE TEST:

  The recruit half routes deposit/excavate probability on curvature:
    linear (non-saturating, as-built):  p = base + gain · c
    saturating (action-based, compresses):  p = base + gain · c/(1+|c|)

  Both are ACTION-BASED (curvature routes the agent's action selection).
  Only the linear form is NON-SATURATING. If the saturating form still
  crosses stably, "action-based" is the load-bearing property. If it
  degrades to a transient flicker (hold < 0.90), "non-saturating" is.

  This is the clean test of H11's core distinction, currently confounded.

METHODOLOGY:
  - Same tuned-probe regime as Session 19/20 (dpb=0.01, decay=0.002,
    80^2 grid, 150 termites, 2000 steps) where the honest crossing lives.
  - 2×2×2 factorial: recruit_response {linear, saturating} × recruit
    {ON, OFF} × d {0, 1}, plus the baseline-pheromone control.
  - 4-seed robustness pass on the key conditions.
  - Per-criterion pass rates for every null (a null is decomposable).
  - Determinism verified by running every combo twice and diffing.
  - stable_crossed = crossed AND late_hold_rate >= 0.90 (Session 20's
    metric, separating stable from transient crossings).
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim09

OUTPUT_DIR = sim09.OUTPUT_DIR

# The tuned-probe regime where Session 19/20's honest crossing lives.
BASE_GRID = {
    "grid_size": 80, "n_termites": 150, "steps": 2000,
    "sample_every": 25, "structure_threshold": sim09.STRUCTURE_THRESHOLD,
    "deposit_prob_base": 0.01, "material_decay": 0.002,
}

SEED = 42

# Recruit ON  gains (the as-built curvature-channel defaults).
RECRUIT_ON = {
    "curve_follow": sim09.CURVE_FOLLOW,          # 0.6
    "deposit_prob_gain": sim09.DEPOSIT_PROB_GAIN,  # 0.85
    "excavate_prob_gain": sim09.EXCAVATE_PROB_GAIN,  # 0.60
}
# Recruit OFF: zero every curvature influence on agent action.
RECRUIT_OFF = {
    "curve_follow": 0.0,
    "deposit_prob_gain": 0.0,
    "excavate_prob_gain": 0.0,
}

STABLE_HOLD_THRESH = 0.90


def late_stats(history):
    """Per-criterion pass rates over the last 1/4 of the history."""
    if not history:
        return {}
    n_late = max(1, len(history) // 4)
    late = history[-n_late:]

    stab_pass = sum(1 for r in late
                    if r["structure_stability"] >= sim09.STAB_THRESH)
    rough_pass = sum(1 for r in late
                     if r["roughness"] >= sim09.ROUGH_ELEV_THRESH)
    mp_vals = [r.get("mass_plateau") for r in late
              if r.get("mass_plateau") is not None]
    plateau_pass = sum(1 for v in mp_vals if v < sim09.MASS_PLATEAU_REL) \
        if mp_vals else 0
    convex_pass = sum(1 for r in late
                      if r["deposits_on_convex_fraction"] >= sim09.CONSTRAIN_THRESH)

    n = len(late)
    nmp = len(mp_vals) if mp_vals else 1
    mean_late_rough = sum(r["roughness"] for r in late) / n
    mean_late_stab = sum(r["structure_stability"] for r in late) / n
    mean_late_convex = sum(r["deposits_on_convex_fraction"] for r in late) / n
    mean_late_cells = sum(r["n_structure_cells"] for r in late) / n
    return {
        "c1_rate": round(stab_pass / n, 3),
        "c2_rough_rate": round(rough_pass / n, 3),
        "c2_plateau_rate": round(plateau_pass / nmp, 3),
        "c3_rate": round(convex_pass / n, 3),
        "mean_late_rough": round(mean_late_rough, 5),
        "mean_late_stab": round(mean_late_stab, 4),
        "mean_late_convex": round(mean_late_convex, 4),
        "mean_late_cells": round(mean_late_cells, 1),
    }


def _late_hold_rate(history):
    """Fraction of the last 1/4 of records where ALL three crossing
    criteria hold simultaneously (Session 20's stable_crossed metric)."""
    if not history:
        return 0.0
    n_late = max(1, len(history) // 4)
    late = history[-n_late:]
    STAB = sim09.STAB_THRESH
    ROUGH = sim09.ROUGH_ELEV_THRESH
    CON = sim09.CONSTRAIN_THRESH
    REL = sim09.MASS_PLATEAU_REL
    def holds(rec):
        c1 = rec["structure_stability"] >= STAB
        c2r = rec["roughness"] >= ROUGH
        mp = rec.get("mass_plateau")
        c2p = mp is not None and mp < REL
        c3 = rec["deposits_on_convex_fraction"] >= CON
        return c1 and c2r and c2p and c3
    return sum(1 for r in late if holds(r)) / n_late


def run_one(response, recruit, d, channel="curvature", seed=SEED):
    """Run one combo. `response` is 'linear' or 'saturating'; `recruit` is
    bool; `d` sets the limit half."""
    p = dict(BASE_GRID)
    p.update({"channel": channel, "d": d, "recruit_response": response})
    if channel == "curvature":
        p.update(RECRUIT_ON if recruit else RECRUIT_OFF)
    r = sim09.run_condition(p, seed=seed)
    s = r["summary"]
    last_rec = r["history"][-1] if r["history"] else {}
    ls = late_stats(r["history"])
    hold = _late_hold_rate(r["history"])
    return {
        "response": response,
        "recruit": recruit,
        "d": d,
        "channel": channel,
        "crossed": int(s["crossed"]),
        "crossing_step": s["crossing_step"],
        "stable_crossed": int(s["crossed"] and hold >= STABLE_HOLD_THRESH),
        "late_hold_rate": round(hold, 3),
        "retention": round(s["retention"], 4),
        "final_cells": s["final_n_structure_cells"],
        "n_pillars": last_rec.get("n_pillars", 0),
        "compactness": round(last_rec.get("compactness", 0.0), 4),
        "final_total_material": round(s["final_total_material"], 2),
        **ls,
    }


def summaries_equal(a, b):
    """Two run_one results are equal iff the crossing verdict + morphology
    agree (floating morphology allowed a tiny tolerance)."""
    return (a["crossed"] == b["crossed"]
            and a["crossing_step"] == b["crossing_step"]
            and a["n_pillars"] == b["n_pillars"]
            and a["final_cells"] == b["final_cells"]
            and abs(a["retention"] - b["retention"]) < 1e-9
            and abs(a["final_total_material"] - b["final_total_material"]) < 1e-6)


def main():
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows = []
    print("=== Saturating-Action Control: 2×2×2 factorial ===")
    print("  (response {linear,saturating} × recruit {ON,OFF} × d {0,1})")
    for response in ("linear", "saturating"):
        for recruit in (True, False):
            for d in (0.0, 1.0):
                label = (f"{response[:4]}-rec{'On' if recruit else 'Off'}-d{d:.0f}")
                row = run_one(response, recruit, d)
                row2 = run_one(response, recruit, d)
                det = summaries_equal(row, row2)
                row["deterministic"] = det
                row["label"] = label
                rows.append(row)
                tag = "*** STABLE CROSSING ***" if row["stable_crossed"] \
                    else ("*** crossed (transient) ***" if row["crossed"] else "")
                print(f"  [{label:16s}] crossed={row['crossed']} "
                      f"stable={row['stable_crossed']} hold={row['late_hold_rate']} "
                      f"step={row['crossing_step']} pillars={row['n_pillars']} "
                      f"cells={row['final_cells']} "
                      f"c1={row['c1_rate']} c2r={row['c2_rough_rate']} "
                      f"c2p={row['c2_plateau_rate']} c3={row['c3_rate']} "
                      f"det={det} {tag}")

    # Baseline-pheromone control (calibration: should not cross).
    print("\n=== Baseline-pheromone control (calibration) ===")
    base_rows = []
    for d in (0.0, 1.0):
        row = run_one("linear", False, d, channel="baseline_pheromone")
        row2 = run_one("linear", False, d, channel="baseline_pheromone")
        row["deterministic"] = summaries_equal(row, row2)
        row["label"] = "baseline_pheromone"
        base_rows.append(row)
        print(f"  [baseline_phero] d={d} crossed={row['crossed']} "
              f"step={row['crossing_step']} cells={row['final_cells']} "
              f"det={row['deterministic']}")

    # Seed robustness: the 4 key conditions across 4 seeds.
    # The decisive contrast: linear-recruit-on-d0 vs saturating-recruit-on-d0.
    # If linear is stable (hold>=0.90) and saturating is not, "non-saturating"
    # is load-bearing. If both are stable, "action-based" is load-bearing.
    print("\n=== Seed robustness (4 seeds × 4 key conditions) ===")
    SEEDS = [42, 7, 123, 256]
    seed_rows = []
    key_conds = [
        ("linear", True, 0.0, "linear-recOn-d0"),
        ("saturating", True, 0.0, "sat-recOn-d0"),
        ("linear", True, 1.0, "linear-recOn-d1"),
        ("saturating", True, 1.0, "sat-recOn-d1"),
    ]
    for seed in SEEDS:
        for response, recruit, d, label in key_conds:
            row = run_one(response, recruit, d, seed=seed)
            row["seed"] = seed
            row["label"] = label
            seed_rows.append(row)
            print(f"  seed={seed:>4} {label:16s} crossed={row['crossed']} "
                  f"stable={row['stable_crossed']} hold={row['late_hold_rate']} "
                  f"pillars={row['n_pillars']} cells={row['final_cells']}")

    out_path = os.path.join(OUTPUT_DIR, "saturating_action_sweep.json")
    with open(out_path, "w") as f:
        json.dump({
            "config": {
                "grid_size": BASE_GRID["grid_size"],
                "n_termites": BASE_GRID["n_termites"],
                "steps": BASE_GRID["steps"],
                "sample_every": BASE_GRID["sample_every"],
                "seed": SEED,
                "deposit_prob_base": BASE_GRID["deposit_prob_base"],
                "material_decay": BASE_GRID["material_decay"],
                "recruit_on": RECRUIT_ON,
                "recruit_off": RECRUIT_OFF,
                "stable_hold_thresh": STABLE_HOLD_THRESH,
            },
            "factorial": rows,
            "baseline_pheromone": base_rows,
            "seed_robustness": seed_rows,
            "all_deterministic": all(r["deterministic"]
                                      for r in rows + base_rows),
        }, f, indent=2)
    print(f"\nWrote {out_path}")

    # Verdict summary.
    def stable_at(response, recruit, d):
        rs = [r for r in rows if r["response"] == response
              and r["recruit"] == recruit and r["d"] == d]
        return rs[0]["stable_crossed"] if rs else None
    def hold_at(response, recruit, d):
        rs = [r for r in rows if r["response"] == response
              and r["recruit"] == recruit and r["d"] == d]
        return rs[0]["late_hold_rate"] if rs else None

    print("\n=== VERDICT: stable_crossed? (1=yes, hold>=0.90) ===")
    print(f"  {'':>22}  {'recruit ON':>11}  {'recruit OFF':>12}")
    for response in ("linear", "saturating"):
        for d in (0.0, 1.0):
            on = stable_at(response, True, d)
            off = stable_at(response, False, d)
            print(f"  {response:>10s} d={d:.0f}  {on:>11}  {off:>12}")

    print("\n=== late_hold_rate ===")
    print(f"  {'':>22}  {'recruit ON':>11}  {'recruit OFF':>12}")
    for response in ("linear", "saturating"):
        for d in (0.0, 1.0):
            on = hold_at(response, True, d)
            off = hold_at(response, False, d)
            print(f"  {response:>10s} d={d:.0f}  {on:>11.3f}  {off:>12.3f}")

    # Seed-robustness tallies for the decisive contrast.
    lin_stable = sum(1 for r in seed_rows
                     if r["label"] == "linear-recOn-d0" and r["stable_crossed"])
    lin_total = sum(1 for r in seed_rows if r["label"] == "linear-recOn-d0")
    sat_stable = sum(1 for r in seed_rows
                     if r["label"] == "sat-recOn-d0" and r["stable_crossed"])
    sat_total = sum(1 for r in seed_rows if r["label"] == "sat-recOn-d0")
    lin_d1_stable = sum(1 for r in seed_rows
                        if r["label"] == "linear-recOn-d1" and r["stable_crossed"])
    lin_d1_total = sum(1 for r in seed_rows if r["label"] == "linear-recOn-d1")
    sat_d1_stable = sum(1 for r in seed_rows
                        if r["label"] == "sat-recOn-d1" and r["stable_crossed"])
    sat_d1_total = sum(1 for r in seed_rows if r["label"] == "sat-recOn-d1")

    print(f"\n=== Seed robustness (stable_crossed / total, 4 seeds) ===")
    print(f"  linear  recruit+ON  d=0: {lin_stable}/{lin_total}")
    print(f"  saturat recruit+ON  d=0: {sat_stable}/{sat_total}")
    print(f"  linear  recruit+ON  d=1: {lin_d1_stable}/{lin_d1_total}")
    print(f"  saturat recruit+ON  d=1: {sat_d1_stable}/{sat_d1_total}")

    print(f"\n  Decisive contrast (recruit ON, d=0, only response differs):")
    print(f"    linear:    {lin_stable}/{lin_total} stable")
    print(f"    saturating: {sat_stable}/{sat_total} stable")
    if lin_stable and not sat_stable:
        print("  => NON-SATURATING is the load-bearing property: the saturating")
        print("     action degrades the stable crossing. H11's distinction holds.")
    elif lin_stable and sat_stable:
        print("  => ACTION-BASED is the load-bearing property: both linear and")
        print("     saturating action cross stably. H11's 'non-saturating' claim")
        print("     is weakened — the confound is resolved in favor of action-based.")
    elif not lin_stable:
        print("  => Neither crosses stably at d=0 — re-examine the tuned probe.")
    else:
        print("  => Mixed result — examine per-seed hold rates for the pattern.")

    print(f"\nElapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
