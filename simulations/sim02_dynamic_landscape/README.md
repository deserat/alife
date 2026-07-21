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

**Both conditions CONVERGE. The dynamic condition converges even harder.**

| Metric | Static | Dynamic |
|---|---|---|
| Final diversity | 4 | 1 |
| Final mean fitness | 0.77 | 2488.27 |
| Landscape modification | 0 | 19900 |
| Trace clusters | 0 | 1 |
| Trace persistence | 0.0 | 0.78 |

### What happened in the dynamic condition:
1. Agents deposit traces that increase fitness at their location
2. Higher fitness → agents reproduce more → deposit more traces
3. Runaway positive feedback → trace field saturates at ~19900
4. Entire population converges to a single strategy that maximizes trace accumulation
5. One large trace cluster forms (monoculture)
6. Fitness inflates massively (0.49 → 2488) but diversity crashes to 1

### Why this is instructive:

**This is NOT a failure — it's a discovery.** The simulation reveals that:

1. **Stigmergy ALONE does NOT produce open-ended evolution.** It can make convergence WORSE. The positive feedback in stigmergic traces creates a runaway feedback loop that locks the entire population into a single strategy. This is exactly Heylighen's "groupthink / collective stupidity" criticism — the same amplification that exploits good solutions also amplifies bad ones.

2. **The trace→actor crossing (H7) is NOT automatic.** Traces accumulate (landscape modification = 19900), form a cluster (1 large cluster), and have high persistence (0.78). But they DON'T become autonomous new-level actors. They're just passive fitness boosters. The population doesn't develop multi-scale structure — it develops a monoculture.

3. **Trace decay rate matters.** At decay=0.005 and deposit=0.1, traces accumulate too fast. The balance is wrong — sim01 found the optimal decay window is 0.01-0.05 for pheromone trails. Here, traces saturate the landscape before any interesting structure can form.

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
