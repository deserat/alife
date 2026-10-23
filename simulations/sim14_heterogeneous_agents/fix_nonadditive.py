"""Fix the label swap in nonadditive_sweep.json and recompute analysis correctly."""
import json, os, numpy as np

SWEEP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "output", "nonadditive_sweep.json")
with open(SWEEP_PATH) as f:
    data = json.load(f)

# The labels in the original sweep were swapped:
#   "focal_only" (g=0.3, bias=0.0) → actually boundary_only
#   "boundary_only" (g=0.0, bias=0.3) → actually focal_only
# Swap the keys in the data dict.
for grid, n in [(80, 150), (160, 600)]:
    fo_key = f"focal_only_{grid}_n{n}"
    bo_key = f"boundary_only_{grid}_n{n}"
    if fo_key in data and bo_key in data:
        # Save references, then swap keys
        fo_data = data.pop(fo_key)  # g=0.3, bias=0.0 → boundary_only
        bo_data = data.pop(bo_key)  # g=0.0, bias=0.3 → focal_only
        fo_data["condition"] = "boundary_only"
        bo_data["condition"] = "focal_only"
        data[f"boundary_only_{grid}_n{n}"] = fo_data
        data[f"focal_only_{grid}_n{n}"] = bo_data

# Fix config conditions
data["config"]["conditions"] = [
    ["neither", 0.0, 0.0],
    ["focal_only", 0.0, 0.3],
    ["boundary_only", 0.3, 0.0],
    ["combined", 0.3, 0.3],
]

# Recompute spread_data with correct labels
spread_data = []
for name, gain, bias in [("neither", 0.0, 0.0), ("focal_only", 0.0, 0.3),
                          ("boundary_only", 0.3, 0.0), ("combined", 0.3, 0.3)]:
    fills = {}
    bmaxes = {}
    for grid, n in [(80, 150), (160, 600)]:
        key = f"{name}_{grid}_n{n}"
        if key in data:
            fills[grid] = data[key]["summary"]["mean_fill_pct"]
            bmaxes[grid] = data[key]["summary"]["mean_b_max"]
    if len(fills) >= 2:
        spread = abs(fills[80] - fills[160])
        spread_data.append({
            "condition": name, "gain": gain, "bias": bias,
            "fill_80": fills[80], "fill_160": fills[160],
            "spread": round(spread, 3),
            "b_max_80": bmaxes.get(80, 0.0),
            "b_max_160": bmaxes.get(160, 0.0),
        })

data["spread_data"] = spread_data

# Recompute interaction
spreads = {d["condition"]: d["spread"] for d in spread_data}
additive = spreads["focal_only"] + spreads["boundary_only"] - spreads["neither"]
actual = spreads["combined"]
interaction = actual - additive
data["interaction"] = {
    "additive_prediction": round(additive, 3),
    "actual_combined": round(actual, 3),
    "interaction_term": round(interaction, 3),
    "verdict": "SUB-ADDITIVE" if interaction < -0.5 else ("SUPER-ADDITIVE" if interaction > 0.5 else "ADDITIVE"),
    "focal_minus_combined": round(spreads["focal_only"] - actual, 3),
    "boundary_minus_combined": round(spreads["boundary_only"] - actual, 3),
}

# Correct b_max comparison: boundary_only vs combined
print("=== CORRECTED ANALYSIS ===")
print(f"{'condition':>16s} | {'80×80 fill':>10s} | {'160×160 fill':>12s} | {'spread':>8s} | {'80 b_max':>10s} | {'160 b_max':>10s}")
print("-" * 80)
for d in spread_data:
    print(f"{d['condition']:>16s} | {d['fill_80']:>9.2f}% | {d['fill_160']:>11.2f}% | {d['spread']:>7.2f}% | {d['b_max_80']:>10.4f} | {d['b_max_160']:>10.4f}")

print(f"\nInteraction analysis:")
print(f"  Additive prediction: focal({spreads['focal_only']:.2f}) + boundary({spreads['boundary_only']:.2f}) - neither({spreads['neither']:.2f}) = {additive:.2f}%")
print(f"  Actual combined:     {actual:.2f}%")
print(f"  Interaction term:    {interaction:.2f}%  ({data['interaction']['verdict']})")

print(f"\nb_max comparison (focal bias reduces boundary strength):")
for grid in [80, 160]:
    bo_bmax = next((d[f"b_max_{grid}"] for d in spread_data if d["condition"] == "boundary_only"), 0)
    co_bmax = next((d[f"b_max_{grid}"] for d in spread_data if d["condition"] == "combined"), 0)
    if bo_bmax > 0:
        ratio = co_bmax / bo_bmax
        reduction = (1 - ratio) * 100
        print(f"  {grid}×{grid}: b_max(boundary_only)={bo_bmax:.4f}  b_max(combined)={co_bmax:.4f}  "
              f"ratio={ratio:.3f}  reduction={reduction:.1f}%  WEAKENED")

# Boundary effect: standalone vs combined
print(f"\nBoundary suppression effect (standalone vs with focal bias):")
for grid in [80, 160]:
    n_fill = next((d[f"fill_{grid}"] for d in spread_data if d["condition"] == "neither"), 0)
    bo_fill = next((d[f"fill_{grid}"] for d in spread_data if d["condition"] == "boundary_only"), 0)
    fo_fill = next((d[f"fill_{grid}"] for d in spread_data if d["condition"] == "focal_only"), 0)
    co_fill = next((d[f"fill_{grid}"] for d in spread_data if d["condition"] == "combined"), 0)
    standalone = n_fill - bo_fill  # boundary's standalone suppression
    with_focal = fo_fill - co_fill  # boundary's suppression with focal bias
    print(f"  {grid}×{grid}: standalone={standalone:.2f}%  with_focal={with_focal:.2f}%  "
          f"reduction={((standalone-with_focal)/standalone*100):.1f}%")

# Focal bias effect: standalone vs with boundary
print(f"\nFocal bias suppression effect (standalone vs with boundary):")
for grid in [80, 160]:
    n_fill = next((d[f"fill_{grid}"] for d in spread_data if d["condition"] == "neither"), 0)
    bo_fill = next((d[f"fill_{grid}"] for d in spread_data if d["condition"] == "boundary_only"), 0)
    fo_fill = next((d[f"fill_{grid}"] for d in spread_data if d["condition"] == "focal_only"), 0)
    co_fill = next((d[f"fill_{grid}"] for d in spread_data if d["condition"] == "combined"), 0)
    standalone = n_fill - fo_fill
    with_boundary = bo_fill - co_fill
    print(f"  {grid}×{grid}: standalone={standalone:.2f}%  with_boundary={with_boundary:.2f}%  "
          f"reduction={((standalone-with_boundary)/standalone*100):.1f}%")

with open(SWEEP_PATH, "w") as f:
    json.dump(data, f, indent=2)
print(f"\nFixed {SWEEP_PATH}")
