"""
d* sweep — the headline H7 experiment.

Broad `deposit_prob_base × material_decay × d` sweep in the mass-saturating
regime (low nucleation, higher erosion) to locate d*, the Facchini
biharmonic-instability threshold above which the crossing fires.

Rationale (from Session 18, 2026-08-02):
  At default params (deposit_prob_base=0.10, material_decay=0.0005) the
  curvature channel grid-saturates — the nucleation base floods the grid
  before curvature routing creates spatial selectivity, so mass never
  plateaus and crossing criterion 2 (|growth_rate| < 0.01 while roughness is
  sustained) cannot fire. The tuned probes (deposit_prob_base=0.01,
  material_decay=0.002) confirmed the consolidation DIRECTION (pillars 25→2
  as d rises) but the crossing still didn't fire because mass didn't
  saturate.

  This sweep explores a wider erosion/nucleation space to find the regime
  where mass DOES saturate (equilibrium: deposit_rate = decay * total_mass),
  then asks whether the crossing fires there as d varies.

Methodology: per-criterion pass rates are reported for every combo so a null
result is decomposable (methodology: "Report per-criterion pass rates for any
null"). Determinism is verified by running one combo twice and diffing.
"""

import json
import os
import sys
import time

# Import sim09 as a module (same directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim09

SIM_DIR = sim09.SIM_DIR
OUTPUT_DIR = sim09.OUTPUT_DIR

# Sweep grid (same reduced-cost params as cmd_sweep_plot)
SWEEP_GRID = {"grid_size": 80, "n_termites": 150, "steps": 2000,
              "sample_every": 25, "structure_threshold": sim09.STRUCTURE_THRESHOLD}

# The three axes
DEPOSIT_PROB_BASES = [0.005, 0.01, 0.02, 0.04]
MATERIAL_DECAYS = [0.002, 0.005, 0.01, 0.02, 0.04]
D_VALUES = [0.0, 0.5, 1.0, 2.0, 4.0]

SEED = 42


def late_stats(history):
    """Per-criterion pass rates over the last 1/4 of the history, plus the
    mean late |growth_rate|. Returns a dict the sweep row carries."""
    if not history:
        return {}
    n_late = max(1, len(history) // 4)
    late = history[-n_late:]

    stab_pass = sum(1 for r in late if r["structure_stability"] >= sim09.STAB_THRESH)
    rough_pass = sum(1 for r in late if r["roughness"] >= sim09.ROUGH_ELEV_THRESH)
    # mass-saturating: |growth_rate| < 0.01 (excluding the None first record)
    mgr_vals = [r["material_growth_rate"] for r in late
                if r.get("material_growth_rate") is not None]
    sat_pass = sum(1 for v in mgr_vals if v < 0.01)
    convex_pass = sum(1 for r in late
                      if r["deposits_on_convex_fraction"] >= sim09.CONSTRAIN_THRESH)

    n = len(late)
    nmgr = len(mgr_vals) if mgr_vals else 1
    mean_late_mgr = sum(mgr_vals) / len(mgr_vals) if mgr_vals else None
    mean_late_rough = sum(r["roughness"] for r in late) / n
    mean_late_stab = sum(r["structure_stability"] for r in late) / n
    mean_late_convex = sum(r["deposits_on_convex_fraction"] for r in late) / n

    return {
        "c1_rate": round(stab_pass / n, 3),
        "c2_rough_rate": round(rough_pass / n, 3),
        "c2_sat_rate": round(sat_pass / nmgr, 3),
        "c3_rate": round(convex_pass / n, 3),
        "mean_late_mgr": round(mean_late_mgr, 5) if mean_late_mgr is not None else None,
        "mean_late_rough": round(mean_late_rough, 5),
        "mean_late_stab": round(mean_late_stab, 4),
        "mean_late_convex": round(mean_late_convex, 4),
    }


def run_one(deposit_prob_base, material_decay, d):
    p = dict(SWEEP_GRID)
    p.update({
        "channel": "curvature",
        "d": d,
        "material_decay": material_decay,
        "deposit_prob_base": deposit_prob_base,
    })
    r = sim09.run_condition(p, seed=SEED)
    s = r["summary"]
    last_rec = r["history"][-1] if r["history"] else {}
    ls = late_stats(r["history"])
    return {
        "deposit_prob_base": deposit_prob_base,
        "material_decay": material_decay,
        "d": d,
        "crossed": int(s["crossed"]),
        "crossing_step": s["crossing_step"],
        "retention": round(s["retention"], 4),
        "final_cells": s["final_n_structure_cells"],
        "n_pillars": last_rec.get("n_pillars", 0),
        "compactness": round(last_rec.get("compactness", 0.0), 4),
        **ls,
    }


def main():
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ---- Determinism check: run one combo twice, diff ----
    print("Determinism check (dpb=0.01, decay=0.005, d=1.0)...")
    a = run_one(0.01, 0.005, 1.0)
    b = run_one(0.01, 0.005, 1.0)
    det_ok = (a["crossed"] == b["crossed"]
              and a["final_cells"] == b["final_cells"]
              and a["n_pillars"] == b["n_pillars"]
              and abs(a["retention"] - b["retention"]) < 1e-9)
    print(f"  deterministic: {det_ok}")
    if not det_ok:
        print("  WARNING: non-deterministic — aborting sweep.")
        return

    rows = []
    total = len(DEPOSIT_PROB_BASES) * len(MATERIAL_DECAYS) * len(D_VALUES)
    i = 0
    any_crossed = False
    for dpb in DEPOSIT_PROB_BASES:
        for dec in MATERIAL_DECAYS:
            for d in D_VALUES:
                i += 1
                row = run_one(dpb, dec, d)
                rows.append(row)
                if row["crossed"]:
                    any_crossed = True
                tag = "*** CROSSING ***" if row["crossed"] else ""
                print(f"  [{i}/{total}] dpb={dpb} decay={dec} d={d} "
                      f"crossed={row['crossed']} ret={row['retention']} "
                      f"pillars={row['n_pillars']} cells={row['final_cells']} "
                      f"mgr={row['mean_late_mgr']} rough={row['mean_late_rough']} "
                      f"c1={row['c1_rate']} c2r={row['c2_rough_rate']} "
                      f"c2s={row['c2_sat_rate']} c3={row['c3_rate']} {tag}")

    out_path = os.path.join(OUTPUT_DIR, "dstar_sweep.json")
    with open(out_path, "w") as f:
        json.dump({
            "config": {
                "grid_size": SWEEP_GRID["grid_size"],
                "n_termites": SWEEP_GRID["n_termites"],
                "steps": SWEEP_GRID["steps"],
                "seed": SEED,
                "axes": {
                    "deposit_prob_base": DEPOSIT_PROB_BASES,
                    "material_decay": MATERIAL_DECAYS,
                    "d": D_VALUES,
                },
            },
            "deterministic": det_ok,
            "any_crossed": any_crossed,
            "n_combos": len(rows),
            "rows": rows,
        }, f, indent=2)
    print(f"\nWrote {out_path}")
    print(f"Total combos: {len(rows)}  Any crossed: {any_crossed}")
    print(f"Elapsed: {time.time() - t0:.1f}s")

    # Summary: which combos crossed?
    crossed_rows = [r for r in rows if r["crossed"]]
    if crossed_rows:
        print(f"\n=== {len(crossed_rows)} CROSSING COMBOS ===")
        for r in crossed_rows:
            print(f"  dpb={r['deposit_prob_base']} decay={r['material_decay']} "
                  f"d={r['d']} crossing_step={r['crossing_step']} "
                  f"pillars={r['n_pillars']} ret={r['retention']}")
    else:
        print("\n=== NO CROSSING COMBOS — per-criterion diagnosis ===")
        # Find combos closest to crossing (highest c2_sat_rate with c1+c3 passing)
        best = sorted(rows,
                      key=lambda r: (-(r["c1_rate"] + r["c3_rate"]),
                                     -r["c2_sat_rate"]))
        print("Top 5 by c1+c3 then c2_sat:")
        for r in best[:5]:
            print(f"  dpb={r['deposit_prob_base']} decay={r['material_decay']} "
                  f"d={r['d']} c1={r['c1_rate']} c2r={r['c2_rough_rate']} "
                  f"c2s={r['c2_sat_rate']} c3={r['c3_rate']} "
                  f"mgr={r['mean_late_mgr']} rough={r['mean_late_rough']}")


if __name__ == "__main__":
    main()
