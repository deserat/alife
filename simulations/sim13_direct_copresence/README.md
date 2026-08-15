# sim13: Direct-Material Co-Presence — Does Eliminating the Torus Leak Break the Memory-Specificity Trade-Off?

**One-line:** Replacing sim12's diffused-shadow co-presence (which wraps on the torus, creating false boundaries) with a direct-material max filter (no x-wrapping) eliminates the torus leak but does NOT break the memory-specificity trade-off — the false positives come from agent wander, not diffusion wrapping.

## The question

sim12's autopoietic boundary has memory (persistence) but lacks specificity (1-seed control 2/4). The hypothesis was that the false boundaries came from the co-presence signal leaking on the torus: diffused shadows wrap around, so a single structure's shadow appears on both sides of the midline.

Direct-material co-presence replaces the diffusion with a max filter (dilation) that wraps in y (toroidal) but NOT in x (zero-padded, no cross-midline leakage). For a single seed, one half is empty, its dilation is zero, and co-presence should be zero — the boundary should not grow.

## What happened

### The torus leak IS eliminated — but it wasn't the cause

The direct-material co-presence for a single seed is initially <1% of the two-seed value (0.015 vs 1.83 on the tiny grid). The diffusion torus leak is gone. But during the simulation, agents wander on the torus and deposit material in both halves. This wander material creates REAL co-presence (not phantom) — the 1-seed control still fires 1/4 (seed 123).

**The torus leak was not the primary cause of sim12's false boundaries. Agent wander was.** Eliminating the diffusion wrapping doesn't eliminate the false positives because the agents themselves distribute material across the midline.

### The radius sweep reveals a breadth-specificity dimension

| radius | 2-seed outcome | 1-seed outcome | clean? |
|--------|---------------|---------------|--------|
| 8 | none (merged) | none | no |
| 12 | none (merged) | none | no |
| 15 | none (merged) | coexist (FALSE) | no |
| 20 | none (merged) | coexist (FALSE) | no |
| 25 | none (l2 fired) | none | no |
| 30 | coexist | none | **YES** |

At small radii (8-12), the boundary is too narrow to prevent merging. At medium radii (15-20), the wider max filter picks up agent-wander material and creates false positives. At radius=30, the b_scale normalization effect (the initial co-presence is very high, so B_norm is low) produces clean composition for seed 42 — but fragmentation for 3/4 seeds.

### The robustness sweep: clean composition 1/4 (worse than sim12's 2/4)

| mode | 2-seed coexist | 1-seed coexist | stable | clean |
|------|---------------|---------------|--------|-------|
| direct (r=30) | 1/4 | 1/4 | 1/4 | **1/4** |
| shadow (sim12) | 4/4 | 2/4 | 4/4 | **2/4** |
| passive (sim11) | 2/4 | 1/4 | 1/4 | **2/4** |
| none | 0/4 | 0/4 | 0/4 | 0/4 |

The direct-material approach is WORSE than both the shadow and passive approaches. The broad boundary (radius=30) prevents merging (l2_crossed 4/4) but produces fragmentation (3/4) rather than clean coexistence (1/4). The 1-seed false positive rate (1/4) is the same as passive and only marginally better than shadow (2/4).

### A new distinction: l2_crossed ≠ l2_outcome=coexist

The direct-material boundary at radius=30 fires the L2 detector in 4/4 seeds (l2_crossed=True — there are components in both halves) but produces "fragmented" (multiple components) rather than "coexist" (two clean structures) in 3/4. The broad boundary over-suppresses deposition in the middle, creating a wide gap that fragments the structures rather than cleanly separating them. This is a third outcome (beyond "coexist" and "none/merged") that previous simulations didn't encounter because their boundaries were narrower.

## What it means

The memory-specificity trade-off is NOT a property of the co-presence signal (diffusion vs. direct-material). It's a property of the system: agents on a torus distribute material everywhere, and any boundary broad enough to prevent merging is also broad enough to pick up wander material and create false positives. The fix is not a better spatial filter — it's a mechanism that keeps agents near their structure (agent fidelity, heterogeneous policies).

This rules out the torus leak as the cause of sim12's false boundaries and redirects the research toward agent fidelity (queued-topic #79: heterogeneous agent policies) as the next approach.

## Parameters

- Grid: 80×80, 150 termites, 2000 steps
- Channel: curvature (d=1.0, material_decay=0.002, deposit_prob_base=0.01)
- Boundary: b_growth=0.1, b_decay=0.005 (half-life ~138 steps)
- Inhibition: inh_gain=0.9
- Direct-material: max filter, radius=30 (swept 8-30)
- Seeds: 42, 123, 256, 999

## Files

- `sim13.py` — imports sim12, overrides `compute_copresence` with direct-material max filter, adds radius sweep
- `visualize.html` — material + boundary grids, radius sweep table, robustness sweep table
- `results.json` — 8-condition experiment (direct/shadow/passive/none × 2/1 seeds)
- `output/radius_sweep.json` — 6-radius sweep (seed 42)
- `output/robustness_sweep.json` — 4-seed × 4-mode × 2-seed-count sweep

## Determinism

Verified at radius=30: two identical runs produce identical l2_crossed, l2_outcome, left_retain, right_retain for both 2-seed and 1-seed conditions.
