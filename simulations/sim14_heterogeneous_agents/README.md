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
