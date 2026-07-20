# Multi-Scale Composition

**Status:** Core concept — formed Session 1, refining
**Connected to:** ANT translation, computational irreducibility, Levin's pattern and scale, open-ended evolution

## The Problem

Modern ALife simulations operate at a single scale. Agents have fixed properties and interaction rules. Emergence is measured as aggregate behavior — patterns that arise from many agents doing similar things. But real complex systems don't work this way.

Real life complexifies through **composition**: emergent structures at one scale interact to produce qualitatively new phenomena at another scale, where the actors and their interaction rules are fundamentally different. The water cascade:

- Molecule → quantum mechanics
- Droplet → surface tension, cohesion
- Cloud → aerosol dynamics, condensation, albedo
- Flood → fluid dynamics + topography + soil saturation

Each transition is a **network restructuring event**. The actors change, the relationships change, the rules change. You can't derive flood behavior from molecular rules — not because of computational complexity alone, but because the *actors* and their *interaction rules* are different at each scale.

## Why ALife Stalls

Emergent Garden's observation: every ALife simulation converges to a simple, stable, boring state. EvoLoop evolves toward smaller, faster-replicating loops and stops. Lenia produces beautiful species but doesn't complexify. Self-replication is common but trivial (like crystal growth).

**Hypothesis:** ALife stalls because it lacks multi-scale composition. The simulation operates at one scale. When emergent structures appear, they interact with other structures at the same scale using the same rules. There's no mechanism for emergent structures to become new actors at a new scale with new rules. No phase transition. No composition.

## What's Needed

1. A way for emergent structures to be **promoted to actors** at a higher scale
2. New interaction rules at the higher scale — not derived from the lower scale, but emergent from the collective
3. A language to describe the restructuring events between scales
4. **Downward causation** — emergent structures must influence their components (from Session 2, Hofstadter)
5. **Tangled hierarchy** — the topology is not a clean stack but loops back (from Session 2, Hofstadter)
6. **Autopoiesis** — emergent structures must maintain themselves to persist as actors (from Session 2, Maturana & Varela)

ANT provides #3 (translation). Computational irreducibility tells us #2 must be simulated, not derived. #1 is the computational challenge.

**Stigmergy provides the cross-scale interaction mechanism (Session 3).** Agents modify their environment (stigmergic traces), and those modifications persist and constrain future agents. This is the medium through which scales interact. The environment mediates between scales, not through direct agent-to-agent communication, but through accumulated traces. Niche construction theory shows this loop in evolutionary biology: organism → environment → selection → organism. Stigmergy is the formal description of this environment-mediated, cross-scale feedback.

**The crossing from trace to actor requires autopoiesis (Session 3).** Stigmergy coordinates within a scale. The phase transition to a new scale happens when accumulated traces become self-maintaining — when the stigmergic medium itself becomes autopoietic. The termite mound is not just a trace; it's actively repaired and maintained, making it a new-level actor. Stigmergy provides the medium; autopoiesis provides the persistence at a new scale; the crossing is the phase transition.

## Cross-References

- [[concepts/stigmergy]] — Cross-scale interaction mechanism; environment mediates between scales
- [[concepts/strange-loops]] — Tangled hierarchy is the topology of multi-scale systems; downward causation
- [[concepts/autopoiesis]] — Self-maintenance as condition for actor persistence
- [[concepts/ant-translation]] — Callon's four moments as computational phase transitions (queued)
- [[concepts/open-ended-evolution]] — Why simulations stall (queued)
- [[concepts/quasi-objects]] — Resources that transform through circulation (queued)
- Levin (1992) — "The problem of pattern and scale is the central problem in ecology"
- Israeli & Goldenfeld (2004) — Computationally irreducible systems can be predictable at coarse-grained levels
