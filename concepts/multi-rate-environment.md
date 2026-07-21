# Multi-Rate Bounded Environment

**Status:** Core concept — contributed by Vance, Session 3 follow-up
**Connected to:** Multi-scale composition, stigmergy, dynamic environment (H4), open-ended evolution, ANT

## The Insight

Single fitness goals lead to stasis — this is obvious and doesn't mimic the real world. Open-ended evolution requires an environment with:

1. **Multiple fitness criteria** — not one fitness function, but many actors each affecting organisms in different ways
2. **Diverse rates of change** — some actors change slowly, others quickly
3. **Bounded change** — each changing actor is governed by its own rules/constraints

## The Real-World Analogies

- **Land** changes slowly, bound by laws of geology (tectonic plates, erosion, uplift)
- **Air temperature** changes rapidly but within a range, bounded by external actors (sun, rotation of earth, atmosphere)
- **Water availability** changes seasonally, bounded by climate patterns
- **Predator populations** change on ecological timescales, bounded by prey availability
- **Soil chemistry** changes over generations, bounded by mineral composition and biological activity

Each of these is an actor (ANT sense) that exerts selection pressure on organisms. Each changes at a different rate. Each is bounded by its own rules. Together they create a multi-dimensional, multi-rate fitness landscape that never settles — because while one pressure stabilizes, another is shifting.

## Why This Produces Open-Ended Evolution

A single fitness goal leads to stasis because once the optimum is found, there's nowhere else to go. But with multiple fitness criteria changing at different rates:

- When temperature pressure stabilizes, predator pressure is still shifting
- When predator pressure stabilizes, geological change has altered the landscape
- Organisms optimized for one criterion are always being pulled by another
- The fitness landscape is never static — it's a moving target in multiple dimensions simultaneously

This prevents the EvoLoop problem (converge to small/fast and stop) because the definition of "optimal" keeps changing.

## The Trade-Off: Complexity vs. Organization Speed

Vance's observation: more complex environments will produce more complex and diverse organisms, but it will probably take longer for those organisms to organize into autopoietic phenomena. This is a real trade-off:

- Simple environment → fast organization, but stasis (EvoLoop)
- Complex environment → slow organization, but potential for open-ended evolution
- The challenge is finding the sweet spot — complex enough to prevent stasis, simple enough to allow organization within reasonable simulation time

## Connection to Existing Concepts

### Multi-scale composition
Different rates of change = different scales. Geological change operates at one scale, temperature at another. The interaction between these scales IS multi-scale composition. The slow actors provide stability (memory), the fast actors provide variation (adaptation). This is the same trade-off as the transient/persistent pheromone decay — but at the environmental level, not the trace level.

### Stigmergy
Each environmental actor leaves traces (stigmergic modifications) at its own rate. Land leaves geological traces (persistent). Temperature leaves weather patterns (transient). The environment is not one stigmergic medium — it's multiple media with different decay rates, each carrying different information.

### ANT (multiple actors)
This is ANT made concrete: the environment is not a single actor but a network of actors, each with its own rules, each changing at its own rate, each exerting different selection pressure. The organism doesn't face "the environment" — it faces a network of actants with different relationships and different dynamics.

### Dynamic environment hypothesis (H4) — refined
The environment must be not just dynamic but **multi-rate and bounded**. Not one environment changing, but many actors each changing within their own rule sets at their own timescales.

## Implications for Simulation

1. The simulation environment must have multiple subsystems (geology, climate, biota) each with their own rules and update rates
2. Each subsystem exerts different selection pressure on organisms
3. Each subsystem is bounded — changes within constraints, not randomly
4. The rates should span orders of magnitude (some update every step, some every 1000 steps)
5. The interactions between subsystems create the multi-scale dynamics

This is testable: compare a simulation with a single dynamic environment vs one with multiple bounded environments at different rates. Hypothesis: the multi-rate environment produces more diversity and resists stasis longer.

## New Hypothesis

### H8: The Multi-Rate Environment Hypothesis
Open-ended evolution requires an environment composed of multiple actors, each exerting different selection pressure, each changing at different rates, each bounded by its own rules. No single-rate, single-criterion environment can produce open-ended evolution because it converges to stasis. The diversity of rates prevents any single optimization from being permanent.

**Test:** Build a simulation with N environmental subsystems, each updating at a different rate (1x, 10x, 100x, 1000x steps). Compare diversity and stasis onset to a single-rate control. Hypothesis: multi-rate environments resist stasis significantly longer.
