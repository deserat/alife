# sim10_l2_composition

**One-line:** Does the trace→actor crossing compose? Two curvature-channel structures in adjacent regions of one grid — does a composite (L2) organization emerge, or do the structures merge, dominate, or fragment?

## The question (queued-topic #62/#77)

The curvature channel crosses (Session 19): a single structure satisfies H7's trace→actor crossing criteria. But does it **compose**? This is the sim05 L2 question (Fontana & Buss; Mathis et al. 2024) reopened with a non-saturating stigmergic glue. In AlChemy, combining two L1 organizations produced Dominance, Coexistence, or Mutual Destruction, with L2 coexistence rare. The curvature channel is a different glue: two structures whose curvature fields interact through a shared agent pool. Does it compose where the chemical (collision) glue did not?

## Design

Two Gaussian material mounds are seeded in opposite halves (left/right) of one grid. The material and curvature fields are shared (single grid, single agent pool). Four conditions form a 2×2:

| condition | channel | seeds | role |
|---|---|---|---|
| A | curvature | 2 | the L2 test |
| B | baseline_pheromone | 2 | saturating-cue control |
| C | curvature | 1 | L1 control (what does one structure do alone?) |
| D | baseline_pheromone | 1 | L1 pheromone control |

## The L2 detector

The detector asks whether EACH region retains an **independent connected structure** — a connected component of structure (material > threshold) that lies *entirely* within one region and does not cross the midline. A component that crosses the midline is a single merged structure, counted in neither region. Genuine coexistence = an independent component in EACH region for ≥ L2_PERSIST consecutive late samples.

The one-seed control (C, D) is the critical control arm: a single structure that fills both halves should NOT fire "coexist" — and it does not, at the crossing regime. The detector distinguishes:
- **coexist**: 1–3 independent components in each region (few structures, sustained)
- **fragmented**: 4+ components per region (erosion too high for consolidation)
- **merged (none)**: 0 components in either region (single structure crossing the midline)
- **dominance**: one region retains ≥3× the other
- **destruction**: both regions retain <10% of peak

## Results

### Headline (H7 crossing regime: decay=0.002, where the single-structure crossing fires)

At the regime where H7's crossing fires, **15/16 two-seed runs merge into a single structure crossing the midline** — the curvature channel consolidates so aggressively that two structures become one. The 1-seed control correctly shows 0/16 coexist (a single structure fills both halves as one connected component).

| condition | coexist | merged | fragmented |
|---|---|---|---|
| curvature 2-seed | 1/16 | 15/16 | 0/16 |
| baseline 2-seed | 1/16 | 15/16 | 0/16 |
| curvature 1-seed | 0/16 | 16/16 | 0/16 |
| baseline 1-seed | 0/16 | 16/16 | 0/16 |

The curvature channel and the baseline-pheromone control produce the *same* outcome at this regime: both merge. The non-saturating glue does not compose better than the saturating glue at the crossing regime.

### The offset×decay sweep (4 offsets × 6 decays × 4 seeds × 2 channels)

At the crossing regime (decay=0.002), there is no composition advantage — both channels merge 15/16. At higher decay (0.003–0.015, the fragmentation regime), the curvature channel shows a modest stable_l2 advantage (+11/80 over the 1-seed control) that the baseline does not (+3/80) — but the 1-seed control still fires there (16/80 coexist, 11/80 stable), so this is partial composition at best, not clean L2 emergence.

### Determinism

Verified: two identical runs produce identical results (outcome, stable flag, mean component counts all match).

## What this means

The crossing does not compose. The curvature channel that produces a stable single-structure crossing (H7) consolidates too aggressively for two structures to coexist — at the crossing regime, two seeds merge into one. At higher erosion rates where coexistence appears, the 1-seed control fires too, so the apparent coexistence is fragmentation, not composition. The non-saturating stigmergic glue does not compose better than the saturating glue.

This is consistent with H10 (unbounded space insufficiency) and Mathis et al. 2024 ("stable organizations cannot be easily combined into higher order entities"). The crossing is a single-structure phenomenon; L2 composition needs something the curvature channel does not provide — possibly a boundary mechanism that prevents merging, or a genuinely different interaction (not shared-field growth).

## Files

- `sim10.py` — the simulation (imports sim09's core; adds two-seed init, per-region component tracking, L2 detector)
- `l2_sweep.py` — offset×decay×seed sweep (384 runs)
- `results.json` — the headline 4-condition run
- `output/l2_sweep.json` — the full sweep
- `visualize.html` — interactive visualization (dark theme)

## Selftest

`python3 sim10.py selftest` — proves the L2 detector fires on synthetic coexistence and withholds on dominance, destruction, single-region, merged, and fragmented cases. Verifies determinism.
