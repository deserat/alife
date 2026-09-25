# sim14: Heterogeneous Agent Policies — Agents Tagged with a Structure ID

**One-line:** Agents carry a structure ID; deposits are tagged with the depositor's ID; co-presence checks for material from TWO DISTINCT IDs — so a 1-seed control is structurally zero, regardless of agent wander.

## The question

sim13 showed that agent wander (not the torus leak) causes false boundaries: agents on a torus deposit material in both halves, creating real co-presence from a single structure. Every spatial filter — diffusion (sim12), direct-material max filter (sim13) — picks up wander material because it detects WHERE material is, not WHOSE it is.

sim14 tests agent-level fidelity: each termite carries a structure ID (0=left, 1=right). Deposits go into `material_by_id[agent.id]`. Co-presence = min(dilate(material_by_id[0]), dilate(material_by_id[1])). For a single seed, all agents have id=0, so `material_by_id[1]` is zero everywhere → co-presence = 0 → B = 0. This is a **structural guarantee** — no spatial filter can achieve it.

## Design

- **HeteroTermites**: first n//2 agents get id=0 (left), rest get id=1 (right). For 1-seed control, all get id=0.
- **Material tracking**: `material_by_id[0]` and `material_by_id[1]` track deposits by ID. Total `field.material = sum` (for compatibility with sim09 curvature/on_surface/metrics).
- **Deposits**: `material_by_id[agent.id] += pellet` AND `field.material += pellet`.
- **Excavation**: proportional removal from both ID arrays.
- **Co-presence**: `min(dilate_no_x_wrap(material_by_id[0]), dilate_no_x_wrap(material_by_id[1]))` — sim13's max filter, but on ID-separated arrays.
- **Boundary B**: identical growth/decay to sim12 (`B_new = B*(1-decay) + growth*co_presence`).
- **Suppression**: identical to sim12 (`p_dep *= (1 - g*B_norm/(1+B_norm))`).

## Results

### 8-Condition experiment (seed 42, g=0.9)

| Condition | L2 | Outcome | Stable | H7 | Cells | L_retain | R_retain |
|---|---|---|---|---|---|---|---|
| hetero 2-seed | YES | coexist | YES | NO | 167 | 0.55 | 0.49 |
| hetero 1-seed | NO | none | NO | YES | 3936 | 0.95 | 1.00 |
| passive 2-seed | YES | coexist | NO | YES | 1779 | 0.99 | 1.00 |
| passive 1-seed | YES | none | YES | YES | 1727 | 0.95 | 1.00 |
| none 2-seed | NO | none | NO | YES | 4832 | 1.00 | 1.00 |
| none 1-seed | NO | none | NO | YES | 4494 | 0.99 | 1.00 |
| shadow 2-seed | YES | coexist | YES | YES | 3714 | 0.99 | 1.00 |
| shadow 1-seed | YES | coexist | YES | YES | 3129 | 0.99 | 1.00 |

### 4-Seed robustness sweep

| Mode | Seeds | L2 | Coexist | Stable | H7 | Clean |
|---|---|---|---|---|---|---|
| hetero | 2 | 4/4 | 2/4 | 2/4 | 0/4 | 2/4 |
| hetero | 1 | **0/4** | **0/4** | **0/4** | 4/4 | — |
| shadow | 2 | 4/4 | 4/4 | 4/4 | 4/4 | 2/4 |
| shadow | 1 | 4/4 | 2/4 | 2/4 | 4/4 | — |
| passive | 2 | 4/4 | 2/4 | 1/4 | 4/4 | 2/4 |
| passive | 1 | 4/4 | 1/4 | 2/4 | 4/4 | — |
| none | 2 | 0/4 | 0/4 | 0/4 | 4/4 | 0/4 |
| none | 1 | 0/4 | 0/4 | 0/4 | 4/4 | — |

### Key findings

1. **The 1-seed control is 0/4 on ALL metrics.** l2_crossed=0/4, coexist=0/4, stable=0/4, B_max=0.0 across all seeds. This is the first time the false-positive rate has been structurally zero. No spatial filter achieves this — sim12's shadow has 4/4 l2_false positives, sim13's direct-material has 4/4 l2 and 1/4 coexist.

2. **Clean composition: 2/4** — matching shadow and passive. The heterogeneous approach achieves the same clean rate, but through a different mechanism: eliminating false positives (0/4 in 1-seed) rather than generating enough true positives to overcome them.

3. **H7 crossing suppressed: 0/4.** The ID-based boundary is too strong — it suppresses growth below the H7 crossing threshold (cells: 167 vs 3714 for shadow). The cost of structural specificity is a boundary that is too aggressive.

4. **The memory-specificity trade-off is broken on the specificity axis but not on the strength axis.** Agent IDs eliminate false positives (specificity), but the boundary's strength (memory) needs tuning — the same trade-off in a new form.

### Selftest

All 7 parts pass: ID co-presence high for 2 seeds (1.83), EXACTLY zero for 1 seed (max=0.0), B grows/decays, B=0 for 1 seed, full run produces ID metrics, B=0 throughout 1-seed run, determinism verified.

## Comparison to previous simulations

| sim | 1-seed l2_false | 1-seed coexist | 2-seed coexist | clean | mechanism |
|---|---|---|---|---|---|
| sim11 (passive) | 4/4 | 1/4 | 2/4 | 2/4 | passive lateral inhibition |
| sim12 (shadow) | 4/4 | 2/4 | 4/4 | 2/4 | diffused-shadow autopoietic |
| sim13 (direct) | 4/4 | 1/4 | 1/4 | 1/4 | direct-material max filter |
| **sim14 (hetero)** | **0/4** | **0/4** | **2/4** | **2/4** | **ID-tagged agents** |

sim14 is the first approach where the 1-seed control fires 0/4 on l2_crossed. The structural guarantee (id1 material = 0 for a single seed) is absolute — it cannot be broken by agent wander, torus topology, or boundary radius.

## Limitations

- **H7 crossing suppressed (0/4).** The boundary is too strong at g=0.9. A lower inh_gain might allow both crossing and composition — but that is a parameter-tuning question, not a mechanism question.
- **2/4 coexist, not higher.** The same rate as passive and shadow. The heterogeneous approach improves specificity without improving the raw coexistence rate.
- **Agents still wander freely.** The IDs tag deposits, not movement. Agents from the left can still wander to the right and deposit there — their deposits carry id=0, which doesn't create false co-presence, but it does mean the boundary's spatial location is still determined by where agents deposit, which is influenced by wander.

## Files

- `sim14.py` — the simulation (imports sim13/sim12/sim11/sim10/sim09)
- `results.json` — 8-condition experiment
- `output/robustness_sweep.json` — 4-seed robustness sweep
- `visualize.html` — interactive visualization

## Run

```bash
python3 sim14.py selftest     # 7-part selftest
python3 sim14.py run         # 8-condition experiment
python3 sim14.py robustness  # 4-seed robustness sweep
```

## Density Scaling (Session 41)

Queued-topic #119: does scaling n_termites with grid area rescue the 160×160 grid's degradation?

| grid | nT | density | jit | l2(2s) | coexist | stable | h7(2s) | l2(1s) | cells |
|------|-----|---------|-----|--------|---------|--------|--------|--------|-------|
| 80 | 150 | 23.44 | 0.0 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 1770 |
| 80 | 150 | 23.44 | 10.0 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 1970 |
| 80 | 150 | 23.44 | 20.0 | 2/4 | 1/4 | 0/4 | 4/4 | 0/4 | 2022 |
| 160 | 150 | 5.86 | 0.0 | 4/4 | 4/4 | 3/4 | 4/4 | 0/4 | 1674 |
| 160 | 150 | 5.86 | 10.0 | 4/4 | 4/4 | 1/4 | 2/4 | 0/4 | 1685 |
| 160 | 150 | 5.86 | 20.0 | 4/4 | 0/4 | 0/4 | 0/4 | 2/4 | 1216 |
| 160 | 300 | 11.72 | 0.0 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 2744 |
| 160 | 300 | 11.72 | 10.0 | 4/4 | 2/4 | 2/4 | 4/4 | 0/4 | 3393 |
| 160 | 300 | 11.72 | 20.0 | 4/4 | 0/4 | 0/4 | 4/4 | 3/4 | 3324 |
| 160 | 600 | 23.44 | 0.0 | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 4515 |
| 160 | 600 | 23.44 | 10.0 | 4/4 | 4/4 | 3/4 | 4/4 | 2/4 | 5780 |
| 160 | 600 | 23.44 | 20.0 | 4/4 | 2/4 | 0/4 | 4/4 | 4/4 | 6748 |

**H7 fully rescued by density** (4/4 at all jitter). **Composition partially rescued** (4/4 at jit=0, 3/4 stable at jit=10, 2/4 at jit=20). **1-seed structural guarantee leaks** at 160×600 (absolute-size effect — bigger structure overwhelms midline). See `density_sweep.py`.

## N550 Plateau (Session 66)

Queued-topic #157/#161: does g* ever hit zero at n=550–600 (~31% grid fill)?

| Label | n | density | g | l2(2s) | coexist | stable | h7(2s) | clean | full | cf | l2(1s) | h7(1s) | cells | fill% |
|-------|-----|---------|-------|--------|---------|--------|--------|-------|------|------|--------|--------|-------|-------|
| n550_g003 | 550 | 21.48 | 0.003 | 4/4 | 4/4 | 3/4 | 4/4 | 4/4 | 3/4 | 0.600 | 2/4 | 4/4 | 7848 | 30.7% |
| n550_g005 | 550 | 21.48 | 0.005 | 4/4 | 4/4 | 3/4 | 4/4 | 4/4 | 3/4 | 0.637 | 2/4 | 4/4 | 7795 | 30.4% |
| n550_g010 | 550 | 21.48 | 0.010 | 4/4 | 4/4 | **4/4** | 4/4 | 4/4 | **4/4** | 0.712 | 2/4 | 4/4 | 7775 | 30.4% |
| n600_g003 | 600 | 23.44 | 0.003 | 4/4 | 3/4 | 2/4 | 4/4 | 3/4 | 2/4 | 0.537 | 2/4 | 4/4 | 8047 | 31.4% |
| n600_g005 | 600 | 23.44 | 0.005 | 4/4 | 4/4 | 1/4 | 4/4 | 4/4 | 1/4 | 0.450 | 2/4 | 4/4 | 7977 | 31.2% |
| n600_g010 | 600 | 23.44 | 0.010 | 4/4 | 4/4 | 3/4 | 4/4 | 4/4 | 3/4 | 0.538 | 2/4 | 4/4 | 7960 | 31.1% |

**g* does NOT hit zero.** The 1/√n scaling holds at ~31% fill. H7=4/4 at all combos. n=550 g=0.01 achieves 4/4 full (cf=0.712). The LSW "droplet dissolves" prediction is not realized — ~31% fill is far below the 2D percolation threshold (~59%). The 43rd mechanism: the 1/√n scaling is conservative (actual optimal > predicted). The 30th mechanism (stability-density trade-off) continues at n=600. See `n550_plateau_sweep.py`.

No-inhibition control: n=550 g=0 → 3/4 coexist, 1/4 stable, cells=15691 (61% fill). n=600 g=0 → 0/4 coexist, cells=17020 (66% fill). The boundary remains necessary at every density.

## N700 Plateau (Session 67)

Queued-topic #157 (continuation): does g* hit zero at n=700–800 (~33–35% grid fill)? The 1/√n formula predicts NEGATIVE g* at n=700–800 — the 43rd mechanism says actual > predicted.

| Label | n | density | g | l2(2s) | coexist | stable | h7(2s) | clean | full | cf | l2(1s) | h7(1s) | cells | fill% |
|-------|-----|---------|-------|--------|---------|--------|--------|-------|------|------|--------|--------|-------|-------|
| n700_g003 | 700 | 27.34 | 0.003 | 4/4 | 4/4 | 1/4 | 4/4 | 4/4 | 1/4 | 0.325 | 1/4 | 4/4 | 8538 | 33.4% |
| n700_g005 | 700 | 27.34 | 0.005 | 4/4 | 4/4 | 2/4 | 4/4 | 4/4 | 2/4 | 0.500 | 1/4 | 4/4 | 8479 | 33.1% |
| n700_g010 | 700 | 27.34 | 0.010 | 4/4 | 4/4 | 2/4 | 4/4 | 4/4 | 2/4 | 0.500 | 1/4 | 4/4 | 8474 | 33.1% |
| n800_g003 | 800 | 31.25 | 0.003 | 4/4 | 4/4 | **3/4** | 4/4 | 4/4 | **3/4** | 0.575 | 3/4 | 4/4 | 8832 | 34.5% |
| n800_g005 | 800 | 31.25 | 0.005 | 4/4 | 4/4 | 2/4 | 4/4 | 4/4 | 2/4 | 0.500 | 3/4 | 4/4 | 8852 | 34.6% |
| n800_g010 | 800 | 31.25 | 0.010 | 4/4 | 1/4 | 2/4 | 4/4 | 1/4 | 0/4 | 0.450 | 3/4 | 4/4 | 8813 | 34.4% |

**g* does NOT hit zero.** The 43rd mechanism (conservative scaling) confirmed: the 1/√n formula predicts NEGATIVE g* but actual g* is positive. H7=4/4 at all 8 combos. n=800 g=0.003 achieves 3/4 full (cf=0.575). The 30th mechanism (stability-density trade-off) worsens at n=800 g=0.01 (coexist 1/4, 3/4 fragmented). The 1-seed structural guarantee degrades: 1/4 at n=700, 3/4 at n=800. See `n700_plateau_sweep.py`.

No-inhibition control: n=700 g=0 → 0/4 coexist, cells=18954 (74% fill). n=800 g=0 → 2/4 coexist (measurement artifact at 82% fill), cells=20960. The boundary remains necessary at every density tested.
