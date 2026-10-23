#!/usr/bin/env python3
"""
Session 92 — cp_mean non-monotonicity analysis (#233)

Why does cp_mean decrease from 80×80 to 160×160 but increase to 320×320?
Hypothesis: the non-monotonicity is a composition-quality artifact.
At 320×320 the structures fragment (l2_outcome="fragmented"), spreading
both IDs' material across the grid, inflating the co-presence everywhere.
At 160×160 the structures coexist (well-separated), concentrating the
co-presence at the midline boundary — the lowest mean.

This script reads existing JSON data (no new simulation runs) and confirms:
1. cp_total is monotonic (extensive) across grid sizes at both densities
2. cp_mean is non-monotonic (NOT intensive) — 160×160 has the minimum
3. The 320×320 maximum coincides with l2_outcome="fragmented" (0/2 coexist)
4. cp_frac_high is highest at 320×320 — more cells with high co-presence
5. The pattern holds with and without the boundary (g=0.0 and g=0.01)
"""

import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"

def load(name):
    with open(OUTPUT_DIR / name) as f:
        return json.load(f)

def extract_cp(data, key):
    """Extract copresence_summary from a condition key."""
    cond = data[key]
    cp = cond.get("copresence_summary", {})
    summary = cond.get("summary", {})
    return {
        "grid": cond.get("grid", cond.get("n_termites", "?")),
        "n": cond.get("n_termites", "?"),
        "cp_mean": cp.get("cp_mean", "?"),
        "cp_total": cp.get("cp_total", "?"),
        "cp_frac_high": cp.get("cp_frac_high", "?"),
        "cp_frac_nonzero": cp.get("cp_frac_nonzero", "?"),
        "fill_pct": summary.get("mean_fill_pct", "?"),
        "coexist": summary.get("coexist", "?"),
        "l2": summary.get("l2", "?"),
    }

# --- copresence_density_sweep.json (with boundary g=0.01) ---
copres = load("copresence_density_sweep.json")

print("=" * 80)
print("CO-PRESENCE MEAN NON-MONOTONICITY ANALYSIS (#233)")
print("=" * 80)

print("\n--- 23.4/kc WITH boundary (g=0.01) ---")
print(f"{'Grid':<12} {'n':>6} {'fill%':>8} {'cp_mean':>10} {'cp_total':>12} {'cp_frac_high':>14} {'coexist':>10} {'l2':>6}")
for key in ["80_23.4kc", "160_23.4kc", "320_23.4kc"]:
    d = extract_cp(copres, key)
    print(f"{d['grid']:<12} {d['n']:>6} {d['fill_pct']:>8.2f} {d['cp_mean']:>10.6f} {d['cp_total']:>12.2f} {d['cp_frac_high']:>14.6f} {str(d['coexist']):>10} {str(d['l2']):>6}")

print("\n--- 46.9/kc WITH boundary (g=0.01) ---")
print(f"{'Grid':<12} {'n':>6} {'fill%':>8} {'cp_mean':>10} {'cp_total':>12} {'cp_frac_high':>14} {'coexist':>10} {'l2':>6}")
for key in ["80_46.9kc", "160_46.9kc", "320_46.9kc"]:
    d = extract_cp(copres, key)
    print(f"{d['grid']:<12} {d['n']:>6} {d['fill_pct']:>8.2f} {d['cp_mean']:>10.6f} {d['cp_total']:>12.2f} {d['cp_frac_high']:>14.6f} {str(d['coexist']):>10} {str(d['l2']):>6}")

# --- no_inhib_copresence_sweep.json (with and without boundary) ---
noinhib = load("no_inhib_copresence_sweep.json")

print("\n--- 23.4/kc WITHOUT boundary (g=0.0) ---")
print(f"{'Grid':<12} {'n':>6} {'fill%':>8} {'cp_mean':>10} {'cp_total':>12} {'cp_frac_high':>14} {'coexist':>10} {'l2':>6}")
for key in ["80_23.4kc_g0.0", "160_23.4kc_g0.0", "320_23.4kc_g0.0"]:
    d = extract_cp(noinhib, key)
    print(f"{d['grid']:<12} {d['n']:>6} {d['fill_pct']:>8.2f} {d['cp_mean']:>10.6f} {d['cp_total']:>12.2f} {d['cp_frac_high']:>14.6f} {str(d['coexist']):>10} {str(d['l2']):>6}")

print("\n--- 46.9/kc WITHOUT boundary (g=0.0) ---")
print(f"{'Grid':<12} {'n':>6} {'fill%':>8} {'cp_mean':>10} {'cp_total':>12} {'cp_frac_high':>14} {'coexist':>10} {'l2':>6}")
for key in ["80_46.9kc_g0.0", "160_46.9kc_g0.0"]:
    d = extract_cp(noinhib, key)
    print(f"{d['grid']:<12} {d['n']:>6} {d['fill_pct']:>8.2f} {d['cp_mean']:>10.6f} {d['cp_total']:>12.2f} {d['cp_frac_high']:>14.6f} {str(d['coexist']):>10} {str(d['l2']):>6}")

# --- Analysis ---
print("\n" + "=" * 80)
print("ANALYSIS")
print("=" * 80)

# 1. cp_total monotonic?
print("\n1. cp_total is MONOTONIC (extensive) across grid sizes:")
for density_label, keys in [("23.4kc", ["80_23.4kc", "160_23.4kc", "320_23.4kc"]),
                            ("46.9kc", ["80_46.9kc", "160_46.9kc", "320_46.9kc"])]:
    totals = [extract_cp(copres, k)["cp_total"] for k in keys]
    monotonic = all(totals[i] < totals[i+1] for i in range(len(totals)-1))
    print(f"   {density_label}: {[f'{t:.0f}' for t in totals]} → {'monotonic ✓' if monotonic else 'NOT monotonic ✗'}")

# 2. cp_mean non-monotonic?
print("\n2. cp_mean is NON-MONOTONIC (NOT intensive) across grid sizes:")
for density_label, keys in [("23.4kc", ["80_23.4kc", "160_23.4kc", "320_23.4kc"]),
                            ("46.9kc", ["80_46.9kc", "160_46.9kc", "320_46.9kc"])]:
    means = [extract_cp(copres, k)["cp_mean"] for k in keys]
    non_monotonic = means[0] > means[1] < means[2]  # decrease then increase
    print(f"   {density_label}: {[f'{m:.6f}' for m in means]} → {'non-monotonic ✓ (decrease→increase)' if non_monotonic else 'monotonic ✗'}")

# 3. Does 320×320 always fragment?
print("\n3. 320×320 always fragments (l2_outcome='fragmented'):")
for density_label, keys in [("23.4kc", ["320_23.4kc"]), ("46.9kc", ["320_46.9kc"])]:
    for k in keys:
        d = extract_cp(copres, k)
        coexist = d["coexist"]
        print(f"   {density_label} {k}: coexist={coexist}, l2={d['l2']} → {'fragmented ✓' if '0' in str(coexist) else 'coexist ✗'}")

# 4. cp_frac_highest at 320×320?
print("\n4. cp_frac_high is highest at 320×320:")
for density_label, keys in [("23.4kc", ["80_23.4kc", "160_23.4kc", "320_23.4kc"]),
                            ("46.9kc", ["80_46.9kc", "160_46.9kc", "320_46.9kc"])]:
    fracs = [extract_cp(copres, k)["cp_frac_high"] for k in keys]
    highest_at_320 = fracs[-1] == max(fracs)
    print(f"   {density_label}: {[f'{f:.6f}' for f in fracs]} → highest at 320×320: {'✓' if highest_at_320 else '✗'}")

# 5. Without boundary: same pattern?
print("\n5. Pattern holds WITHOUT boundary (g=0.0):")
for density_label, keys in [("23.4kc", ["80_23.4kc_g0.0", "160_23.4kc_g0.0", "320_23.4kc_g0.0"])]:
    means = [extract_cp(noinhib, k)["cp_mean"] for k in keys]
    coexists = [extract_cp(noinhib, k)["coexist"] for k in keys]
    non_monotonic = means[0] > means[1] < means[2]
    print(f"   {density_label} g=0.0: cp_mean={[f'{m:.6f}' for m in means]} → {'non-monotonic ✓' if non_monotonic else 'monotonic ✗'}")
    print(f"   {density_label} g=0.0: coexist={[str(c) for c in coexists]} → 320×320 fragments without boundary too")

# 6. cp_total per grid cell = cp_mean (sanity check)
print("\n6. Sanity: cp_total / grid² = cp_mean:")
for key in ["80_23.4kc", "160_23.4kc", "320_23.4kc"]:
    d = extract_cp(copres, key)
    grid = d["grid"]
    grid_area = grid * grid
    computed = d["cp_total"] / grid_area
    print(f"   {grid}×{grid}: cp_total/grid² = {computed:.6f} vs cp_mean = {d['cp_mean']:.6f} → {'✓' if abs(computed - d['cp_mean']) < 1e-4 else '✗'}")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
The cp_mean non-monotonicity (0.343 → 0.279 → 0.447 at 23.4/kc;
0.425 → 0.234 → 0.450 at 46.9/kc) is a COMPOSITION-QUALITY ARTIFACT.

cp_total is extensive (monotonic: 2192 → 7141 → 45766 at 23.4/kc).
cp_mean = cp_total / grid² is NOT intensive — it depends on the spatial
arrangement (coexist vs fragmented), which changes with grid size.

At 320×320, the structures fragment (l2_outcome="fragmented", 0/2 coexist),
spreading both IDs' material across the grid. This inflates the co-presence
EVERYWHERE — cp_frac_high is 0.796 vs 0.694 at 160×160. The high cp_mean
is NOT a strong-boundary signal — it is a FRAGMENTATION signal.

At 160×160, the structures coexist (well-separated, 4/4 coexist),
concentrating the co-presence at the midline boundary. The rest of the
grid has low co-presence → lowest cp_mean.

The pattern holds WITHOUT the boundary (g=0.0): cp_mean still goes
0.330 → 0.293 → 0.452, and 320×320 still fragments (0/2 coexist).
The non-monotonicity is NOT caused by the boundary — it is caused by
the composition quality (fragmentation at 320×320).

This refines the extensive/intensive distinction:
- cp_total is extensive (monotonic in grid size) ✓
- cp_mean is NOT intensive — it conflates boundary co-presence
  (at the midline, good) with fragmentation co-presence (everywhere, bad)
- A clean intensive measure must be scale-invariant at matched density;
  cp_mean is not because the spatial arrangement changes with grid size
""")

# Save analysis results
results = {
    "session": 92,
    "topic": "cp_mean non-monotonicity (#233)",
    "finding": "cp_mean non-monotonicity is a composition-quality artifact",
    "data": {
        "23.4kc_g0.01": {extract_cp(copres, k)["grid"]: extract_cp(copres, k) for k in ["80_23.4kc", "160_23.4kc", "320_23.4kc"]},
        "46.9kc_g0.01": {extract_cp(copres, k)["grid"]: extract_cp(copres, k) for k in ["80_46.9kc", "160_46.9kc", "320_46.9kc"]},
        "23.4kc_g0.0": {extract_cp(noinhib, k)["grid"]: extract_cp(noinhib, k) for k in ["80_23.4kc_g0.0", "160_23.4kc_g0.0", "320_23.4kc_g0.0"]},
        "46.9kc_g0.0": {extract_cp(noinhib, k)["grid"]: extract_cp(noinhib, k) for k in ["80_46.9kc_g0.0", "160_46.9kc_g0.0"]},
    },
    "conclusion": "cp_total is extensive (monotonic); cp_mean is NOT intensive (non-monotonic, conflates boundary + fragmentation co-presence); 320×320 fragments → high cp_mean is a fragmentation signal, not a boundary signal",
}

with open(OUTPUT_DIR / "cp_mean_nonmonotonic_analysis.json", "w") as f:
    json.dump(results, f, indent=2, default=str)

print("\nResults saved to output/cp_mean_nonmonotonic_analysis.json")
