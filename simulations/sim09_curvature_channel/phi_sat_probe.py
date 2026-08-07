#!/usr/bin/env python3
"""φ_sat predictor probe (queued-topic #72).

Tests whether the deposit-probability saturation threshold (φ_sat) — the input
value at which deposit probability first reaches 1.0 — predicts crossing across
all four cells of the 2×2 (action×cue × linear×saturating).

Uses each sim's run_condition to get the crossing verdict, then does a short
field-sampling run to measure the operating distribution of the routing input
and the clamping fraction (fraction of surface/structure cells where p_deposit
reaches 1.0).
"""
import sys, os, json
import numpy as np

HERE = os.path.dirname(__file__)
SIM09 = os.path.join(HERE)
SIM06 = os.path.join(HERE, "..", "sim06_termite_mound")
sys.path.insert(0, SIM09)
sys.path.insert(0, SIM06)

import sim06
import sim09

# -----------------------------------------------------------------------
# Analytic φ_sat
# -----------------------------------------------------------------------
def phi_sat(base, gain, response):
    """Input value at which p_deposit first reaches 1.0.

    linear:     p = base + gain * x           -> x_sat = (1-base)/gain
    saturating: p = base + gain * x/(1+|x|)  -> max_p = base+gain
    Returns inf if the response curve never reaches p=1.0.
    """
    if response == "linear":
        if gain <= 0:
            return float("inf")  # flat response, never reaches 1.0
        return (1.0 - base) / gain
    max_p = base + gain
    if max_p < 1.0:
        return float("inf")
    r = (1.0 - base) / gain
    if r >= 1.0:
        return float("inf")
    return r / (1.0 - r)

def deposit_prob(base, gain, x, response):
    if response == "linear":
        return min(1.0, base + gain * x)
    return base + gain * x / (1.0 + abs(x))

# -----------------------------------------------------------------------
# sim06 probe (cue family)
# -----------------------------------------------------------------------
def probe_sim06(deposit_base, deposit_response, self_maintenance=False,
                seed=42, steps=2000):
    # Get crossing verdict via run_condition (matching cue_response_sweep config)
    params = sim06.baseline_params()
    params["deposit_base"] = deposit_base
    params["deposit_response"] = deposit_response
    params["grid_size"] = 80
    params["n_termites"] = 150
    params["steps"] = steps
    params["sample_every"] = 25
    params["material_decay"] = 0.002  # sweep config
    if self_maintenance:
        params = sim06.self_maintenance_params()
        params["deposit_base"] = deposit_base
        params["deposit_response"] = deposit_response
        params["grid_size"] = 80
        params["n_termites"] = 150
        params["steps"] = steps
        params["sample_every"] = 25
        params["material_decay"] = 0.002
        params["maintain_gain"] = 0.3

    result = sim06.run_condition(params, seed)
    summary = sim06.summarize(result["history"])
    crossed = summary["crossed"]

    # Field-sampling run to get pheromone distribution + clamping fraction
    gain = params.get("deposit_gain", 0.85)
    base = params.get("deposit_base", deposit_base)
    phi_s = phi_sat(base, gain, deposit_response)

    rng = sim06.make_rng(seed)
    size = 80
    field = sim06.Field(size)
    termites = sim06.Termites(150, size, rng)
    clamp_samples = []
    phero_samples = []

    for step in range(steps):
        events = sim06.termite_step(termites, field, rng, params)
        sim06.field_step(field, params)
        if step > 1000 and step % 50 == 0:
            struct_mask = field.material > params.get("structure_threshold", 1.0)
            if struct_mask.any():
                phero = field.pheromone[struct_mask]
                phero_samples.append({
                    "mean": float(phero.mean()),
                    "max": float(phero.max()),
                    "std": float(phero.std()),
                })
                ps = base + gain * phero / (1.0 + phero) if deposit_response == "saturating" else base + gain * phero
                ps = np.minimum(ps, 1.0)
                clamp_samples.append(float((ps >= 0.999).sum()) / float(ps.size))

    last = phero_samples[-1] if phero_samples else {"mean": 0, "max": 0, "std": 0}
    mean_clamp = float(np.mean(clamp_samples)) if clamp_samples else 0.0
    max_clamp = float(np.max(clamp_samples)) if clamp_samples else 0.0

    return {
        "family": "cue",
        "response": deposit_response,
        "self_maintenance": self_maintenance,
        "deposit_base": deposit_base,
        "gain": gain,
        "phi_sat": phi_s,
        "mean_phero": last["mean"],
        "max_phero": last["max"],
        "std_phero": last["std"],
        "mean_clamping_fraction": mean_clamp,
        "max_clamping_fraction": max_clamp,
        "crossed": crossed,
    }

# -----------------------------------------------------------------------
# sim09 probe (action family)
# -----------------------------------------------------------------------
def probe_sim09(deposit_prob_base, recruit_response, d_smooth=1.0,
                recruit_on=True, seed=42, steps=2000):
    params = sim09.curvature_params()
    params["deposit_prob_base"] = deposit_prob_base
    params["recruit_response"] = recruit_response
    params["d"] = d_smooth
    params["recruit_on"] = recruit_on
    params["grid_size"] = 80
    params["n_termites"] = 150
    params["steps"] = steps
    params["sample_every"] = 25
    params["material_decay"] = 0.002
    # Match sweep's recruit_off behavior exactly
    if not recruit_on:
        params["curve_follow"] = 0.0
        params["deposit_prob_gain"] = 0.0
        params["excavate_prob_gain"] = 0.0

    result = sim09.run_condition(params, seed)
    summary = sim09.summarize(result["history"])
    crossed = summary["crossed"]

    # Field-sampling run for curvature distribution + clamping
    gain = params.get("deposit_prob_gain", 0.85)
    base = params.get("deposit_prob_base", deposit_prob_base)
    c_s = phi_sat(base, gain, recruit_response)

    rng = sim09.make_rng(seed)
    size = 80
    field = sim09.Field(size)
    termites = sim09.Termites(150, size, rng)
    clamp_samples = []
    curv_samples = []

    for step in range(steps):
        curvature = sim09.compute_curvature(field, params)
        on_surface = sim09.compute_on_surface(field, params)
        events = sim09.termite_step(termites, field, rng, params, curvature, on_surface)
        sim09.field_step(field, params)
        if step > 1000 and step % 50 == 0:
            surf_mask = on_surface & (field.material > 0)
            if surf_mask.any():
                sc = curvature[surf_mask]
                curv_samples.append({
                    "mean": float(sc.mean()),
                    "max": float(sc.max()),
                    "min": float(sc.min()),
                    "std": float(sc.std()),
                })
                # Clamping on positive-curvature (deposit) cells
                pos = sc[sc > 0]
                if pos.size > 0:
                    if recruit_response == "saturating":
                        ps = base + gain * pos / (1.0 + pos)
                    else:
                        ps = base + gain * pos
                    ps = np.minimum(ps, 1.0)
                    clamp_samples.append(float((ps >= 0.999).sum()) / float(pos.size))

    last = curv_samples[-1] if curv_samples else {"mean": 0, "max": 0, "std": 0}
    mean_clamp = float(np.mean(clamp_samples)) if clamp_samples else 0.0
    max_clamp = float(np.max(clamp_samples)) if clamp_samples else 0.0

    return {
        "family": "action",
        "response": recruit_response,
        "recruit_on": recruit_on,
        "d_smooth": d_smooth,
        "deposit_prob_base": deposit_prob_base,
        "gain": gain,
        "c_sat": c_s,
        "mean_curv": last["mean"],
        "max_curv": last["max"],
        "std_curv": last["std"],
        "mean_clamping_fraction": mean_clamp,
        "max_clamping_fraction": max_clamp,
        "crossed": crossed,
    }

# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------
def main():
    results = []

    print("=" * 80)
    print("φ_sat PROBE — does the deposit-probability saturation threshold")
    print("predict crossing across all four cells of the 2×2?")
    print("=" * 80)

    # --- Cue family (sim06) — no SM (the diagnostic conditions) ---
    print("\n--- Cue family (sim06, no SM) ---")
    for resp in ["saturating", "linear"]:
        print(f"  Running cue/{resp}...", end=" ", flush=True)
        r = probe_sim06(deposit_base=0.01, deposit_response=resp,
                        self_maintenance=False, seed=42)
        results.append(r)
        sat = "SAT" if r["max_phero"] > r["phi_sat"] else "unsat"
        print(f"φ_sat={r['phi_sat']:.3f} max_p={r['max_phero']:.3f} [{sat}] "
              f"clamp={r['mean_clamping_fraction']:.3f} crossed={r['crossed']}")

    # --- Action family (sim09) — recruit ON (the crossing conditions) ---
    print("\n--- Action family (sim09, recruit ON) ---")
    for resp in ["linear", "saturating"]:
        print(f"  Running action/{resp}...", end=" ", flush=True)
        r = probe_sim09(deposit_prob_base=0.01, recruit_response=resp,
                        d_smooth=1.0, recruit_on=True, seed=42)
        results.append(r)
        sat = "SAT" if r["max_curv"] > r["c_sat"] else "unsat"
        print(f"c_sat={r['c_sat']:.3f} max_c={r['max_curv']:.3f} [{sat}] "
              f"clamp={r['mean_clamping_fraction']:.3f} crossed={r['crossed']}")

    # --- Action family (sim09) — recruit OFF (the non-crossing control) ---
    print("\n--- Action family (sim09, recruit OFF — non-crossing control) ---")
    for resp in ["linear", "saturating"]:
        print(f"  Running action/{resp}/no-recruit...", end=" ", flush=True)
        r = probe_sim09(deposit_prob_base=0.01, recruit_response=resp,
                        d_smooth=1.0, recruit_on=False, seed=42)
        results.append(r)
        sat = "SAT" if r["max_curv"] > r["c_sat"] else "unsat"
        print(f"c_sat={r['c_sat']:.3f} max_c={r['max_curv']:.3f} [{sat}] "
              f"clamp={r['mean_clamping_fraction']:.3f} crossed={r['crossed']}")

    # --- Summary table ---
    print("\n" + "=" * 80)
    print("SUMMARY: φ_sat predictor vs crossing verdict")
    print("=" * 80)
    print(f"{'family':>8} {'response':>12} {'recruit':>8} {'input_max':>10} "
          f"{'φ_sat':>8} {'saturated':>10} {'clamp_frac':>11} {'crossed':>8}")
    print("-" * 80)
    for r in results:
        if r["family"] == "cue":
            inp_max = r["max_phero"]
            psat = r["phi_sat"]
            rec = "SM" if r["self_maintenance"] else "no"
        else:
            inp_max = r["max_curv"]
            psat = r["c_sat"]
            rec = "rec" if r["recruit_on"] else "no"
        sat = "YES" if inp_max > psat else "no"
        print(f"{r['family']:>8} {r['response']:>12} {rec:>8} {inp_max:10.4f} "
              f"{psat:8.3f} {sat:>10} {r['mean_clamping_fraction']:11.4f} "
              f"{str(r['crossed']):>8}")

    # --- The verdict ---
    print("\n" + "=" * 80)
    print("PREDICTOR EVALUATION")
    print("=" * 80)

    correct = 0
    total = 0
    for r in results:
        inp_max = r["max_phero"] if r["family"] == "cue" else r["max_curv"]
        psat = r["phi_sat"] if r["family"] == "cue" else r["c_sat"]
        saturated = inp_max > psat
        predicted_fail = saturated
        actual_fail = not r["crossed"]
        match = predicted_fail == actual_fail
        total += 1
        if match:
            correct += 1
        label = "CORRECT" if match else "WRONG"
        fam = f"{r['family']}/{r['response']}"
        extra = "SM" if r["family"] == "cue" and r["self_maintenance"] else \
                ("rec" if r["family"] == "action" and r["recruit_on"] else "no")
        print(f"  {fam:>24} {extra:>4}: saturated={saturated} pred_fail={predicted_fail} "
              f"actual_fail={actual_fail} -> {label}")

    print(f"\n  φ_sat predictor accuracy: {correct}/{total} ({100*correct/total:.0f}%)")

    print("\n  Clamping-fraction predictor:")
    print(f"  {'condition':>24} {'clamp_frac':>12} {'crossed':>8} {'prediction':>12}")
    for r in results:
        cf = r["mean_clamping_fraction"]
        fam = f"{r['family']}/{r['response']}"
        extra = "SM" if r["family"] == "cue" and r["self_maintenance"] else \
                ("rec" if r["family"] == "action" and r["recruit_on"] else "no")
        verdict = "crosses" if r["crossed"] else "fails"
        # Predict: high clamp -> fails
        pred = "fails" if cf > 0.5 else "crosses"
        match = "✓" if (pred == verdict) else "✗"
        print(f"  {fam:>24} {extra:>4}: {cf:8.4f} {verdict:>8} pred={pred:>8} {match}")

    # Save results
    out_path = os.path.join(HERE, "output", "phi_sat_probe.json")
    with open(out_path, "w") as f:
        json.dump({
            "config": {
                "grid_size": 80, "n_termites": 150, "steps": 2000,
                "seed": 42, "deposit_base_cue": 0.01,
                "deposit_prob_base_action": 0.01, "material_decay_action": 0.002,
            },
            "results": results,
        }, f, indent=2)
    print(f"\nResults saved to {out_path}")

if __name__ == "__main__":
    main()
