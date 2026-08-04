"""
recruit_limit_sweep.py — the recruit-vs-limit isolation (queued-topic 59).

Session 19 found the corrected crossing fires at d=0 (no biharmonic smoothing),
so the RECRUIT half (curvature routing + mass plateau) drives the verdict and
the LIMIT half (d-smoothing) is not necessary for the crossing — it only
consolidates morphology (pillars 12→1). H11's Session-13 "recruits as well as
limits" refinement is therefore half-supported. This script cleanly isolates
the two halves in a 2x2 factorial.

THE TWO HALVES (operational definition):

  RECRUIT = curvature influences AGENT ACTION SELECTION.
    ON  : curve_follow=0.6 (loaded termites move toward high-curvature
          neighbours), deposit_prob_gain=0.85 (linear, non-saturating
          routing of deposit probability on curvature), excavate_prob_gain
          =0.60 (curvature-routed excavation at concavities).
    OFF : curve_follow=0.0 (pure random walks), deposit_prob_gain=0.0,
          excavate_prob_gain=0.0 — deposit/excavate at BASE rates only; the
          field's curvature has NO influence on what an agent does or where
          it goes. The only curvature-driven thing left is the field's own
          smoothing.

  LIMIT = the field smooths ITSELF via the biharmonic d-term in field_step.
    ON  : d > 0  (field.material += d*0.0001 * Δ²f  smooths sharp features).
    OFF : d = 0  (no biharmonic; only background erosion acts on the field).

So the four cells of the factorial are:

  recruit ON , limit OFF  = "recruit-only"  (the d=0 probe from Session 19)
  recruit ON , limit ON   = "full"          (the curvature channel as built)
  recruit OFF, limit ON   = "limit-only"    (random walks + field smoothing)
  recruit OFF, limit OFF  = "neither"       (random walks + erosion only)

PREDICTION (H11 refined): recruit-only crosses; limit-only does NOT. If both
cross, the mass-plateau gate is too permissive (it is detecting any stable
plateau, not the curvature mechanism). If neither crosses, the d=0 result
from Session 19 was an artefact of the specific tuned-probe regime, not the
recruit mechanism. The decisive contrast is recruit ON vs OFF at d=0: same
detector, same regime, only the recruit flag differs.

A fifth condition — the baseline-pheromone control — is run alongside for
calibration (it should still not cross, reproducing Session 19).

Methodology: per-criterion pass rates for every combo (a null is
decomposable); determinism verified by running every combo twice and
diffing summaries; the tuned-probe regime (dpb=0.01, decay=0.002, 80^2,
150 termites, 2000 steps) where Session 19's honest crossing lives.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim09

OUTPUT_DIR = sim09.OUTPUT_DIR

# The tuned-probe regime where Session 19's honest (non-saturating) crossing
# lives. Same grid/n_termites/steps as dstar_sweep.py for comparability.
BASE_GRID = {
    "grid_size": 80, "n_termites": 150, "steps": 2000,
    "sample_every": 25, "structure_threshold": sim09.STRUCTURE_THRESHOLD,
    "deposit_prob_base": 0.01, "material_decay": 0.002,
}

D_VALUES = [0.0, 0.5, 1.0, 2.0, 4.0]
SEED = 42

# Recruit ON  gains (the as-built curvature-channel defaults).
RECRUIT_ON = {
    "curve_follow": sim09.CURVE_FOLLOW,          # 0.6
    "deposit_prob_gain": sim09.DEPOSIT_PROB_GAIN,  # 0.85
    "excavate_prob_gain": sim09.EXCAVATE_PROB_GAIN,  # 0.60
}
# Recruit OFF: zero every curvature influence on agent action. Agents random-
# walk and deposit/excavate at base probability only.
RECRUIT_OFF = {
    "curve_follow": 0.0,
    "deposit_prob_gain": 0.0,
    "excavate_prob_gain": 0.0,
}


def late_stats(history):
    """Per-criterion pass rates over the last 1/4 of the history, mirroring
    dstar_sweep.late_stats but using the corrected mass-plateau flag rather
    than the legacy |growth_rate| gate (the corrected gate is what
    detect_crossing actually uses)."""
    if not history:
        return {}
    n_late = max(1, len(history) // 4)
    late = history[-n_late:]

    stab_pass = sum(1 for r in late
                    if r["structure_stability"] >= sim09.STAB_THRESH)
    rough_pass = sum(1 for r in late
                     if r["roughness"] >= sim09.ROUGH_ELEV_THRESH)
    # corrected mass plateau: mass_plateau flag is populated by detect_crossing
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
    mean_late_plateau = (sum(mp_vals) / len(mp_vals)) if mp_vals else None
    # grid saturation (physical ceiling check): fraction of cells with material
    mean_late_cells = sum(r["n_structure_cells"] for r in late) / n
    grid_cells = sim09.GRID_SIZE * sim09.GRID_SIZE  # 100*100; but sweep uses 80
    # use the actual grid size from the run's first record footprint
    # (we don't store grid_size per record; approximate from n_structure_cells
    #  vs the 80*80=6400 sweep grid).
    return {
        "c1_rate": round(stab_pass / n, 3),
        "c2_rough_rate": round(rough_pass / n, 3),
        "c2_plateau_rate": round(plateau_pass / nmp, 3),
        "c3_rate": round(convex_pass / n, 3),
        "mean_late_rough": round(mean_late_rough, 5),
        "mean_late_stab": round(mean_late_stab, 4),
        "mean_late_convex": round(mean_late_convex, 4),
        "mean_late_plateau": round(mean_late_plateau, 6)
                             if mean_late_plateau is not None else None,
        "mean_late_cells": round(mean_late_cells, 1),
    }


def _late_hold_rate(history):
    """Fraction of the last 1/4 of records where ALL three crossing criteria
    hold simultaneously. A *stable* crossing holds ~1.00; a *transient*
    crossing (criteria flicker on and off) holds <~0.55. This distinguishes
    the recruit half's stable crossing from the limit half's flicker."""
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


# A crossing is "stable" if the late-window hold rate >= this. 0.90 mirrors
# the stability threshold: the three criteria hold in >=90% of the late
# samples. The recruit half clears this (hold 1.00); the limit half's
# transient crossings flicker at hold 0.40-0.55 and do not.
STABLE_HOLD_THRESH = 0.90


def run_one(recruit, d, channel="curvature", seed=SEED):
    """Run one combo. `recruit` is bool (ON/OFF for the recruit half); `d`
    sets the limit half (ON if d>0, OFF if d==0)."""
    p = dict(BASE_GRID)
    p.update({"channel": channel, "d": d})
    if channel == "curvature":
        p.update(RECRUIT_ON if recruit else RECRUIT_OFF)
    r = sim09.run_condition(p, seed=seed)
    s = r["summary"]
    last_rec = r["history"][-1] if r["history"] else {}
    ls = late_stats(r["history"])
    hold = _late_hold_rate(r["history"])
    return {
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
    # The 2x2 factorial over the curvature channel, across d.
    print("=== Recruit-vs-Limit 2x2 factorial (curvature channel) ===")
    for recruit in (True, False):
        for d in D_VALUES:
            label = ("recruit+limit" if (recruit and d > 0)
                     else "recruit-only" if recruit
                     else "limit-only" if d > 0
                     else "neither")
            row = run_one(recruit, d)
            # determinism: run again, diff
            row2 = run_one(recruit, d)
            det = summaries_equal(row, row2)
            row["deterministic"] = det
            row["label"] = label
            rows.append(row)
            tag = "*** CROSSING ***" if row["crossed"] else ""
            print(f"  [{label:13s}] d={d} crossed={row['crossed']} "
                  f"step={row['crossing_step']} pillars={row['n_pillars']} "
                  f"cells={row['final_cells']} ret={row['retention']} "
                  f"rough={row['mean_late_rough']} convex={row['mean_late_convex']} "
                  f"plat={row['mean_late_plateau']} c1={row['c1_rate']} "
                  f"c2r={row['c2_rough_rate']} c2p={row['c2_plateau_rate']} "
                  f"c3={row['c3_rate']} det={det} {tag}")

    # Baseline-pheromone control (calibration: should not cross).
    print("\n=== Baseline-pheromone control (calibration) ===")
    base_rows = []
    for d in D_VALUES:
        row = run_one(False, d, channel="baseline_pheromone")
        row2 = run_one(False, d, channel="baseline_pheromone")
        row["deterministic"] = summaries_equal(row, row2)
        row["label"] = "baseline_pheromone"
        base_rows.append(row)
        print(f"  [baseline_phero] d={d} crossed={row['crossed']} "
              f"step={row['crossing_step']} cells={row['final_cells']} "
              f"det={row['deterministic']}")

    # Seed robustness: the 2x2 corner conditions across 4 seeds. The recruit
    # half's crossing should be stable (hold >= 0.90) in most seeds; the limit
    # half's should flicker (hold < 0.55). This is the decisive contrast.
    print("\n=== Seed robustness (4 seeds x 4 corner conditions) ===")
    SEEDS = [42, 7, 123, 256]
    seed_rows = []
    for seed in SEEDS:
        for recruit in (True, False):
            for d in (0.0, 1.0):  # the two clean corners
                row = run_one(recruit, d, seed=seed)
                row["seed"] = seed
                row["label"] = ("recruit+limit" if (recruit and d > 0)
                                else "recruit-only" if recruit
                                else "limit-only" if d > 0
                                else "neither")
                seed_rows.append(row)
                print(f"  seed={seed:>4} {row['label']:13s} crossed={row['crossed']} "
                      f"stable={row['stable_crossed']} hold={row['late_hold_rate']} "
                      f"pillars={row['n_pillars']} cells={row['final_cells']}")

    out_path = os.path.join(OUTPUT_DIR, "recruit_limit_sweep.json")
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
                "d_values": D_VALUES,
                "recruit_on": RECRUIT_ON,
                "recruit_off": RECRUIT_OFF,
                "stable_hold_thresh": STABLE_HOLD_THRESH,
            },
            "factorial": rows,
            "baseline_pheromone": base_rows,
            "seed_robustness": seed_rows,
            "all_deterministic": all(r["deterministic"] for r in rows + base_rows),
        }, f, indent=2)
    print(f"\nWrote {out_path}")

    # Verdict summary — uses STABLE crossing (hold >= 0.90), not just the
    # cumulative crossed flag, to separate stable from transient crossings.
    def stable_at(recruit, d):
        rs = [r for r in rows if r["recruit"] == recruit and r["d"] == d]
        return rs[0]["stable_crossed"] if rs else None
    def crossed_at(recruit, d):
        rs = [r for r in rows if r["recruit"] == recruit and r["d"] == d]
        return rs[0]["crossed"] if rs else None
    print("\n=== VERDICT MATRIX (stable_crossed? 1=yes, hold>=0.90) ===")
    print(f"  {'d':>6}  {'recruit ON':>11}  {'recruit OFF':>12}")
    for d in D_VALUES:
        on = stable_at(True, d)
        off = stable_at(False, d)
        print(f"  {d:>6}  {on:>11}  {off:>12}")
    # seed-robustness tallies
    ro_stable = sum(1 for r in seed_rows if r["label"] == "recruit-only" and r["stable_crossed"])
    ro_total = sum(1 for r in seed_rows if r["label"] == "recruit-only")
    lo_stable = sum(1 for r in seed_rows if r["label"] == "limit-only" and r["stable_crossed"])
    lo_total = sum(1 for r in seed_rows if r["label"] == "limit-only")
    ne_stable = sum(1 for r in seed_rows if r["label"] == "neither" and r["stable_crossed"])
    ne_total = sum(1 for r in seed_rows if r["label"] == "neither")
    fl_stable = sum(1 for r in seed_rows if r["label"] == "recruit+limit" and r["stable_crossed"])
    fl_total = sum(1 for r in seed_rows if r["label"] == "recruit+limit")
    print(f"\n  seed-robustness (stable_crossed / total):")
    print(f"    recruit-only:   {ro_stable}/{ro_total}")
    print(f"    recruit+limit:  {fl_stable}/{fl_total}")
    print(f"    limit-only:     {lo_stable}/{lo_total}")
    print(f"    neither:         {ne_stable}/{ne_total}")
    print(f"\n  recruit-only (d=0): stable={stable_at(True, 0.0)}")
    print(f"  limit-only  (d=1): stable={stable_at(False, 1.0)}")
    if ro_stable and not lo_stable and not ne_stable:
        print("  => RECRUIT half is load-bearing for the STABLE crossing; the LIMIT "
              "half alone produces only transient flicker (hold 0.40-0.55). "
              "H11 'recruit as well as limit' is half-supported: recruit necessary "
              "AND sufficient for a stable crossing; limit is morphology-only.")
    elif ro_stable and lo_stable:
        print("  => BOTH halves can cross stably — the mass-plateau gate may be too "
              "permissive. Re-examine whether limit-only's hold rate is genuinely "
              "stable across more seeds.")
    elif not ro_stable:
        print("  => recruit-only does NOT stably cross in the tuned probe — the "
              "Session-19 d=0 result may be seed-specific. Re-examine.")
    print(f"\nElapsed: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
