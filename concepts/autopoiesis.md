---
status: "Core concept"
formed: "Session 2"
connected_to: "Strange loops, multi-scale composition, quasi-objects, ANT"
topic: "autopoiesis and self-maintenance"
key_findings: "Self-production is self-reference through process. Persistence condition for actors across phase transitions. Self-maintenance is not complexification."
---

# Autopoiesis

**Status:** Core concept — formed Session 2
**Connected to:** Strange loops, multi-scale composition, quasi-objects, ANT

## The Concept

Autopoiesis (Maturana & Varela, 1972): a system that produces and maintains itself. From Greek: auto (self) + poiesis (creation). An autopoietic system is "a network of processes of production of components which continuously regenerate and realize the network that produced them."

Two conditions:
1. The network produces its own components
2. The components constitute the system as a bounded unity in space

The canonical example: a biological cell. The cell's biochemical network produces the components (proteins, lipids) that make up the cell membrane, which in turn bounds and protects the network. Co-dependence: network creates boundary, boundary protects network.

## Computational Autopoiesis

Varela, Maturana & Uribe (1974) implemented a computational model — one of the first ALife simulations. Key features:
- Two catalysts (A, M) that produce each other through coupled reactions
- M molecules form the boundary (membrane)
- Boundary allows nutrients (B, C) in, keeps catalysts in
- Boundary degrades; network repairs it
- Catalytic closure: each catalyst is product of a reaction it catalyzes
- Chemical closure: disintegration of products returns substrates

This was 1974. The model demonstrates self-production through circular chemistry. But like all ALife, it doesn't complexify — the system maintains itself but doesn't evolve into something more complex.

## Relevance to Our Project

1. **Autopoiesis IS a strange loop.** The network produces components that produce the network. That's a level-crossing feedback loop — the system references itself through its own production. Hofstadter's strange loop and Maturana's autopoiesis describe the same phenomenon from different angles.

2. **Autopoiesis + ANT = network that maintains itself.** Latour says actors are defined by relationships. An autopoietic system is one whose relationships are self-maintaining — the network produces the actors, the actors maintain the network. This is exactly what happens at a phase transition: when emergent structures form, they must maintain themselves to persist as new actors. Autopoiesis is the condition for persistence.

3. **The boundary problem.** Autopoiesis requires a boundary — something that separates the system from its environment. In ANT terms, the boundary is an actor too. The membrane is not a passive container; it actively filters, repairs, and maintains. This connects to our dynamic environment hypothesis: the boundary between actor and environment is itself an actor.

4. **Why autopoietic systems don't complexify.** The original computational model maintains itself but doesn't evolve. Same problem as EvoLoop. Self-maintenance is necessary but not sufficient for open-ended evolution. What's missing? Possibly: the system needs to interact with OTHER autopoietic systems at its own scale, creating a higher-level network. Autopoiesis + multi-scale interaction might be the recipe.

## Open Questions

- Can we design a simulation where autopoietic systems interact, and the interaction network becomes a higher-level autopoietic system?
- Is multi-scale autopoiesis (systems producing systems at different scales) the mechanism for complexification?
- How does autopoiesis relate to the quasi-object concept? Both involve transformation through circulation — autopoietic components transform through the production network, quasi-objects transform through circulation.

## Empirical Evidence

### Computational autopoiesis (Varela, Maturana & Uribe, 1974)
The original algorithm demonstrates self-maintaining networks in a simple 2D chemistry. The system produces its own catalysts and boundary. Quantitative: measured by system lifetime (how long the autopoietic unity persists before catalysts escape through boundary gaps). The 1974 model runs for hundreds of steps with appropriate parameters.

### 30 years of computational autopoiesis (McMullin & another, ResearchGate)
Review of computational autopoiesis models over 30 years. Findings: the original model is robust but has limitations — boundary repair is sensitive to catalyst placement, and the system doesn't evolve (same stall as EvoLoop). Multiple extensions attempted (3D models, different chemistries) but none achieved evolution.

### No empirical evidence for multi-scale autopoiesis
No studies found that test whether interacting autopoietic systems produce higher-level autopoietic structures. This is a novel hypothesis (H6) with no prior experimental or computational validation. It needs to be tested via simulation.

### Autopoiesis in social systems (Luhmann)
Luhmann applied autopoiesis to social systems (communication as the self-producing process). This is theoretical, not empirically tested in a computational setting.

## Cross-References

- [[concepts/strange-loops]] — Autopoiesis is a strange loop by definition
- [[concepts/multi-scale-composition]] — Multi-scale autopoiesis might drive complexification
- Maturana & Varela, Autopoiesis and Cognition: The Realization of the Living (1972)
- McMullin, "Computational Autopoiesis: The Original Algorithm" (SFI, 1997)
- Capra & Luisi, The Systems View of Life (2014)
