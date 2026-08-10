# sim11_boundary_mechanism

**One-line:** Does a long-range inhibitor (Turing/Gierer-Meinhardt lateral inhibition) create a boundary that lets two curvature-channel structures coexist where sim10 showed they merge?

## The question (queued-topic #78)

Session 25 (sim10) found the trace→actor crossing does NOT compose: two curvature-channel structures merge 15/16 times at the crossing regime. The curvature channel has **local self-activation** (deposit at convex tips recruits further building) but **no long-range inhibition** — nothing prevents two growing structures from merging.

The Turing/Gierer-Meinhardt pattern-formation principle says local activation + long-range (lateral) inhibition produces spatially separated patterns. Without the long-range inhibitory term, a single activator field merges everything. The curvature channel is an activator-only system.

**Hypothesis under test:** a non-saturating stigmergic channel that fires H7's crossing (sim09) composes into L2 when paired with a long-range inhibitory field. The inhibitor = heavily-smoothed material MINUS local material (the far-field shadow with self-cancellation). It is zero at structures (local material cancels the shadow) and high in the gap between two structures (both shadows sum). Deposit probability is multiplied by (1 − suppression), where suppression is a saturating function of the normalized inhibitor.

## Design

Two Gaussian seed mounds in opposite halves of one grid (as in sim10). Four conditions:

| condition | inhibition | seeds | role |
|---|---|---|---|
| A | ON (g=0.9) | 2 | the L2 test |
| B | ON (g=0.9) | 1 | L1 control — does inhibition break the single-structure crossing? |
| C | OFF | 2 | the sim10 baseline — should merge |
| D | OFF | 1 | the sim10 L1 control |

The L2 detector is sim10's corrected detector: per-region connected components of structure that do not cross the midline. The one-seed control (B) is the critical control arm: if a single structure under inhibition also "coexists" (creates independent components on both sides), the detector is catching fragmentation, not composition.

## The inhibitor field

```
I = max(0, far_smoothed_material − material)
```

`far_smoothed_material` = material field after 12 diffusion passes at rate 0.7 (a broad Gaussian-like blur). The subtraction is the key: at a structure, local material ≈ smoothed material, so I ≈ 0 (self-cancellation). In the gap, smoothed material > 0 (shadows from both structures) but local material ≈ 0, so I is high. A cell at the structure edge sees partial cancellation; a cell in the gap sees the sum of both structures' shadows.

Deposit probability: `p_dep *= (1 − g · I_norm / (1 + I_norm))`, where `I_norm = I / I_scale` (I_scale = 95th percentile of the initial inhibitor). Saturating in I, bounded in [0, g). At g=0.9, the maximum suppression is 0.9 — near-complete suppression in the gap, near-zero at structure cores.

## Results

### Headline (seed 42, g=0.9)

At g=0.9, the 2-seed condition fires `coexist` and the 1-seed control fires `none` — a clean composition case. The no-inhibition conditions reproduce sim10's merge (4832 cells, outcome=none). The inhibition reduces total structure (1779 vs 4832 cells) but creates a boundary.

| condition | l2_crossed | outcome | L_retain | R_retain | h7 | cells |
|---|---|---|---|---|---|---|
| A: curv+inh, 2 seeds | **True** | **coexist** | 0.99 | 1.00 | True | 1779 |
| B: curv+inh, 1 seed | True | none | 0.95 | 1.00 | True | 1727 |
| C: curv, 2 seeds | False | none | 1.00 | 1.00 | True | 4832 |
| D: curv, 1 seed | False | none | 0.99 | 1.00 | True | 4494 |

### Robustness sweep (4 seeds × {0.0, 0.7, 0.9, 0.95})

| inh_gain | seeds | l2_crossed | coexist | stable | h7 | clean comp |
|---|---|---|---|---|---|---|
| 0.00 | 2 | 0/4 | 0/4 | 0/4 | 4/4 | 0/4 |
| 0.00 | 1 | 0/4 | 0/4 | 0/4 | 4/4 | — |
| 0.70 | 2 | 2/4 | 2/4 | 1/4 | 4/4 | 1/4 |
| 0.70 | 1 | 3/4 | 2/4 | 1/4 | 4/4 | — |
| 0.90 | 2 | 4/4 | 2/4 | 1/4 | 4/4 | **2/4** |
| 0.90 | 1 | 4/4 | 1/4 | 2/4 | 4/4 | — |
| 0.95 | 2 | 4/4 | 1/4 | 0/4 | 4/4 | 0/4 |
| 0.95 | 1 | 3/4 | 1/4 | 1/4 | 4/4 | — |

**Clean composition** = 2-seed coexist AND 1-seed does NOT. At g=0.9, 2/4 seeds show clean composition (seeds 42, 123); the other 2 seeds (256, 999) fragment (the 1-seed control also fires). At g=0.95, both 2-seed and 1-seed fragment — too much inhibition.

### Determinism

Verified: two identical runs produce identical results (l2_crossed, l2_outcome, retention, cells all match).

## What this means

**The boundary mechanism is a weak positive, not a solution.** The long-range inhibitor converts the 0/4 merge (no inhibition) to 2/4 clean coexistence at g=0.9 — a real improvement. But it is not robust: the other 2 seeds fragment (the 1-seed control fires too), and the stable_l2 metric shows no stable composition advantage (0/4 at all gains). The inhibitor creates a boundary in some nucleation trajectories but fragments the structure in others. The composition problem is not just "missing lateral inhibition."

**The H7 crossing survives inhibition.** At all gains (0.0–0.95), the single-structure H7 crossing fires 4/4 (crossed_h7). The inhibitor does not break the L1 crossing — it only adds a boundary/fragmentation effect. This means the crossing and the composition are separable: you can have the crossing without composition, and adding a boundary mechanism doesn't trade away the crossing.

**The methodological lesson (a fifth instance of the control-arm pattern #75/#80):** the one-seed control is essential here. Without it, g=0.9's 4/4 l2_crossed and 2/4 coexist would look like a success. The 1-seed control's 4/4 l2_crossed reveals that the detector is catching fragmentation — a single structure under inhibition also creates independent components on both sides. The clean composition metric (2-seed coexist AND 1-seed does NOT) is the only honest test.

## Criticisms / limitations (honest)

- **The inhibitor is a design choice, not derived from biology.** Real termite territoriality involves chemical cues (cuticular hydrocarbons), not a smoothed-material shadow. The far-field-minus-local form is a convenient computational abstraction of lateral inhibition, not a biological mechanism.
- **The 2/4 clean composition is not robust.** Two of four seeds fragment. A different seed set might give 0/4 or 4/4. The result is seed-dependent and should be treated as "the boundary mechanism helps in some regimes," not "the boundary mechanism solves composition."
- **The stable_l2 metric shows 0/4 at all gains.** Even at g=0.9 where 2/4 clean-compose, the stable_l2 is only 1/4 (seed 999). The coexistence is not sustained — it flickers.
- **The inhibitor reduces total structure by ~60%** (4832 → 1779 cells). This is expected (suppression reduces deposits) but means the L2 structures are smaller than the L1 baseline. A fair comparison should account for this.
- **If every bug I found pushed toward the expected result, I should treat it as unproven.** The pellet bug (my reimplementation used pellet=0.1 instead of sim09's 1.0) initially killed all structures, which pushed toward "inhibition doesn't work." Fixing it pushed toward "inhibition works partially" — the expected direction. But the fix was a correctness fix (matching sim09's constant), not a tuning choice, so the corrected result stands.
- **The self-cancelling inhibitor (far − local) is the critical design insight.** Without it, the inhibitor is highest AT the structure (self-defeating). This insight came from debugging the first attempt, not from theory. It should be tested: does a simple smoothed-material inhibitor (without self-cancellation) also produce 2/4, or is the self-cancellation necessary?

## Files

- `sim11.py` — the simulation (imports sim10/sim09; adds inhibitor field, inhibition-gated deposit rule, 2×2 condition runner)
- `inh_gain_sweep.py` — single-seed gain sweep (7 gains × 2 seed counts)
- `robustness_sweep.py` — 4-seed robustness sweep (4 gains × 4 seeds × 2 seed counts = 32 runs)
- `results.json` — the headline 4-condition run (g=0.9, seed 42)
- `output/inh_gain_sweep.json` — the gain sweep
- `output/robustness_sweep.json` — the robustness sweep
- `visualize.html` — interactive visualization (dark theme, material + inhibitor grids, component charts, sweep table)

## Selftest

`python3 sim11.py selftest` — proves the inhibitor is long-range and self-cancelling, the inhibition-gated run produces per-region metrics, inhibition reduces total material, the inherited L2 detector fires/withholds, and determinism holds.
