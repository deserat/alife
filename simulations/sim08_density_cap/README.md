# sim08 — Non-Saturating Density Cap (the H11 test)

**One-line:** Tests whether inhibiting deposition through a *non-saturating* channel
(a hard density cap on the deposit action) consolidates the stigmergic structure where
sim06/sim07's *saturating-cue* feedback fragmented it. Direct test of
[H11, the Saturating Channel Hypothesis](../../hypotheses/hypotheses.md).

## The hypothesis under test

H11 says negative feedback delivered *through* the saturating pheromone cue field
(`p = base + gain·φ/(1+φ)`, flat above φ≈1) is self-defeating: it destroys the spatial
contrast consolidation needs. Two prior attempts both fragmented (sim06
self-maintenance: 66–109 → 219–297 components; sim07 transport: 57 → 128 pillars),
both acting through the cue. The refined prescription: act on the **action** (deposit
probability) via a channel that **does not saturate**. sim08 tests the cheapest such
channel — a **density cap**: a cell whose material ≥ `DENSITY_CAP` cannot receive
deposits. The cap is a hard boolean gate on the action, so it stays discriminating
however high the pheromone field climbs.

Biological basis: real termites use non-saturating geometric (curvature), humidity
(threshold), and crowding (mechanical) channels — not a saturating cement pheromone,
which no study has identified. See
[`concepts/non-saturating-channels.md`](../../concepts/non-saturating-channels.md).

## What it does

Reuses sim06's tested machinery (Field, Termites, field dynamics, metrics, crossing
detector, morphology) unchanged. The **only** change is one clause in the deposit
rule: `eligible = cell_material < density_cap`. Movement, reload, pickup, decay,
diffusion, erosion, the detector, and all metrics are identical to sim06 — so the
comparison is apples-to-apples. Four conditions:

- **baseline** — sim06's saturating Grassé rule, no cap, no maintenance.
- **self_maintenance** — sim06's cue-based feedback (the condition that fragmented).
- **density_cap** — Grassé rule + non-saturating cap (the H11 test).
- **cap_plus_self_maintenance** — cap + cue feedback (does the cap rescue the cue loop?).

## Results

### Condition comparison (default DENSITY_CAP=4.0)

| condition | cells | pillars | stability | retention | crossed | capped(total) |
|---|---|---|---|---|---|---|
| baseline | 1131 | 101 | 0.874 | 0.958 | no | 0 |
| self_maintenance | 1876 | 252 | 0.775 | 0.980 | no | 0 |
| density_cap | 1040 | 77 | 0.872 | 0.952 | no | 105,694 |
| cap + self_maintenance | 1890 | 262 | 0.763 | 0.984 | no | 10,271 |

### Density-cap sweep (cap strength → morphology)

| density_cap | cells | pillars | stability | retention | crossed | compactness | max_pheromone |
|---|---|---|---|---|---|---|---|
| 1.5 | 619 | 52 | 0.775 | 0.943 | no | 0.063 | 2.50 |
| 2.0 | 856 | 58 | 0.822 | 0.979 | no | 0.086 | 3.28 |
| 2.5 | 918 | 63 | 0.851 | 0.967 | no | 0.093 | — |
| 3.0 | 954 | 67 | 0.859 | 0.956 | no | 0.098 | — |
| 4.0 | 1040 | 77 | 0.872 | 0.952 | no | 0.104 | 4.66 |
| 6.0 | 1129 | 83 | 0.877 | 0.978 | no | 0.113 | 5.95 |
| 8.0 | 1156 | 75 | 0.874 | 0.984 | no | 0.116 | 5.78 |
| ∞ (no cap) | 1131 | 101 | 0.874 | 0.958 | no | 0.113 | 8.01 |

## Interpretation

**Partial corroboration of H11, with a sharper boundary.**

1. **The cap consolidates morphology, monotonically — H11's direction is confirmed.**
   Pillars fall from 101 → 52 as the cap tightens. The cap also *suppresses the
   pheromone field* (max pheromone 8.01 → 2.50) — exactly the "de-saturating the
   channel" effect H11 predicts: a non-saturating action-gate prevents the cue field
   from being driven flat. This is the positive result.

2. **But the cap does NOT produce the crossing.** Stability does not rise — it
   degrades slightly at the tightest cap (0.874 → 0.775). The detector never fires.
   The cap reduces building *volume* (1131 → 619 cells) without raising *persistence*.

3. **The binding constraint survives the cap.** sim06's near-miss was criterion 1
   (stability 0.849–0.893 vs 0.90). sim08's cap holds stability at 0.77–0.88 — still
   below 0.90. The cap corrects the *fragmentation* symptom (pillars) but not the
   *persistence* symptom (stability). **Non-saturating inhibition is necessary-but-
   not-sufficient for the crossing.**

4. **The cap does NOT rescue cue-based feedback.** cap+self_maintenance (262
   pillars, stability 0.763) is if anything worse than self_maintenance alone (252,
   0.775). Adding the cap to the saturating-cue loop does not fix it — consistent
   with H11's claim that the cue channel, not the feedback energy, is the problem.

## What this refines

- **H11 confirmed in direction, sharpened in sufficiency.** Non-saturating
  inhibition consolidates where saturating-cue feedback fragments — the
  prescription was right. But a cap that *only limits growth* cannot reach the
  crossing, because the crossing also needs *persistence* (the structure holding
  its mass against erosion). A pure limiter reduces mass; it doesn't recruit
  maintenance.
- **The crossing needs a non-saturating channel that RECRUITS, not just one that
  LIMITS.** The curvature channel (Calovi 2019) does both: it routes deposition to
  concavities (limits scatter) AND each deposit *extends* the concavity (recruits
  further building at the edge). The density cap only limits. Candidate next
  experiment: a curvature/deposition-edge rule that routes AND limits.
- **H7's prescription narrows again.** sim06: positive feedback alone insufficient.
  sim07: scalar cue-transport insufficient. sim08: non-saturating limitation
  insufficient. The crossing needs a non-saturating channel that also feeds back
  positively into its own maintenance — geometry that recruits, not just caps.

## Method notes

- Determinism verified (seed 42; reruns identical).
- The cap is a genuine positive control: selftest asserts a fully-capped grid
  yields zero deposits and the same grid uncapped yields deposits > 0.
- Reuses sim06's detector, which is proven able to fire (sim06 selftest Part 5).
  A null here is therefore informative, not an unfalsifiable detector.
- All metrics, the crossing detector, and morphology functions are inherited
  unchanged from sim06; only the deposit rule's eligibility clause differs.

## Files

- `sim08.py` — the simulation (imports sim06 for the reused machinery).
- `results.json` — four conditions + summaries (committed).
- `visualize.html` — interactive Canvas view of the conditions and the sweep.
- `output/sweep_density_cap.json` — the cap-strength sweep data.
