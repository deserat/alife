# Sim02: Dynamic Fitness Landscape

## What It Tests

Whether agents that modify their fitness landscape (stigmergic niche construction) produce qualitatively different dynamics from agents on a static landscape.

Tests H4 (Dynamic Environment) and H8 (Computational Complexity Enables Open-Endedness).

## Design

- Population of 200 agents on a 20x20 grid
- Each agent has a binary strategy string of length N=8
- Fitness depends on strategy, position, and landscape state
- NK-like fitness function with K=3 epistatic interactions per gene
- Two conditions:
  - **Static**: Fixed landscape. Agents adapt TO it.
  - **Dynamic**: Agents deposit stigmergic traces that modify fitness contributions. Traces decay at rate 0.005.

## Key Results

> **Rerun 2026-07-27 after a fix to the trace term.** The earlier numbers came from a trace
> bonus that was (a) added regardless of the agent's own `strategy[i]`, so it was identical
> for every strategy at a cell and could not change which strategy won, and (b) unbounded,
> which drove dynamic mean fitness to 2488 against static's 0.77 — a 3224× scale difference
> that made the conditions incomparable. The bonus is now strategy-dependent and saturating
> (capped at `TRACE_WEIGHT=0.5` per gene). See `../REVIEW.md` §3.

**Both conditions CONVERGE. The dynamic condition converges even harder.**

| Metric | Static | Dynamic |
|---|---|---|
| Final diversity | 4 | 2 |
| Final mean fitness | 0.7718 | 1.1137 |
| Landscape modification | 0 | 27303 |
| Trace clusters | 0 | 1 |
| Trace persistence | 0.0 | 0.74 |

Fitness ratio is now 1.44× (was 3224×), so the two conditions are on comparable scales and
the comparison is meaningful. Both plateau by generation ~100 and neither moves for the
remaining 4,900 generations (diversity range 0 in the final 1000 for both).

### What happened in the dynamic condition:
1. Agents deposit traces on the gene channels they carry, raising fitness for *those*
   strategies at that location
2. Higher fitness → agents reproduce more → deposit more traces
3. Positive feedback concentrates the population; the trace field grows to ~27300
4. The population converges to 2 strategies (vs 4 in the static condition)
5. One trace cluster remains at the end
6. Fitness rises from 0.49 to 1.11 and then plateaus

### Why this is instructive:

**This is NOT a failure — it's a discovery.** The simulation reveals that:

1. **Stigmergy ALONE does NOT produce open-ended evolution.** It can make convergence WORSE:
   the dynamic condition ends with half the diversity of the static one. The positive feedback
   in stigmergic traces narrows the population rather than opening it up. This is Heylighen's
   "groupthink / collective stupidity" criticism — the same amplification that exploits good
   solutions also amplifies bad ones. Note this conclusion survived the fix, but it now rests
   on a diversity difference (2 vs 4) rather than on a fitness number that was an artifact.

2. **The trace→actor crossing (H7) is NOT automatic.** Traces accumulate, form a cluster, and
   persist (0.74). But they don't become autonomous new-level actors — they remain fitness
   modifiers. The population develops a monoculture, not multi-scale structure.

3. **Bounding the trace term matters as much as its decay rate.** With an unbounded additive
   bonus the landscape term swamps the base landscape entirely (it contributed 99.97% of
   dynamic fitness before the fix) and the model stops being a fitness-landscape experiment
   at all. Any "dynamic landscape" term needs to stay commensurate with the base landscape it
   is supposed to be modifying.

4. **What's missing for open-endedness:** The simulation confirms that three additional mechanisms are needed:
   - **Trace autonomy**: Traces must develop their own dynamics, not just be passive fitness modifiers
   - **Competing traces**: Multiple trace types that compete/interact, not just one global trace field
   - **Autopoietic crossing**: A mechanism for accumulated traces to become self-maintaining structures with their own rules (the H7 phase transition)

## Connection to Echo's Failure

Smith & Bedau (1997) found that Echo converges to simple trading ecologies. Our simulation shows the same convergence, even WITH stigmergic landscape modification. This confirms that adding stigmergy to a single-scale model doesn't produce multi-scale composition — it just changes the convergence dynamics.

The key insight: **stigmergy is necessary but not sufficient** (as argued in Session 3). The missing ingredient is the autopoietic crossing — the mechanism by which accumulated traces become self-maintaining new-level actors.

## Next Steps

- Sim03: Add trace competition (multiple trace types that interact)
- Sim04: Add the autopoietic crossing mechanism (traces that develop self-maintenance)
- Sweep trace decay rate to find the optimal balance for structure formation
- Test whether traces can develop their own dynamics (not just modify fitness)

## How to Run

```bash
cd ~/brain/artificial-life/simulations/sim02_dynamic_landscape
python3 sim02.py
```

Results are saved to `results.json`.
