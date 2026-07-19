# Artificial Life Simulator — Research Project

## Overview

Long-term research project toward an artificial life simulator grounded in Actor Network Theory (ANT) and computational irreducibility. The goal is to develop a thorough understanding of evolution, intelligence, complex systems, and ecosystems, synthesize knowledge across domains, develop novel hypotheses, and test them via Python simulations. The eventual artifact is a playable simulation/game.

## Core Thesis

Modern ALife simulations operate at a single scale — agents have fixed properties and interaction rules, and emergence is measured as aggregate behavior. They fail to account for **multi-scale composition**: how emergent phenomena at one scale interact to produce qualitatively new phenomena at another scale, where the actors and their interaction rules are fundamentally different.

**The water cascade:**
- Water molecule → quantum mechanics
- Water droplet → surface tension, cohesion (emergent from molecular interactions, but new rules)
- Cloud → aerosol dynamics, condensation, albedo (can't predict from droplet rules)
- Flood → fluid dynamics + topography + soil saturation (interaction between cloud and earth actors)

Each phase transition is a **network restructuring event** — actors change, relationships change, rules change. ANT gives us a language to describe this. Computational irreducibility tells us we have to run the simulation to know what happens. Together they give us: simulate the rules at each scale, and use ANT to describe/model the restructuring events between scales.

ANT works in concert with traditional irreducibility, not in isolation.

## Methodology — Spiral Loops

Knowledge develops through **spiral loops organized by topic clusters**, not sequential steps. Each loop goes through research → synthesis → hypothesis → (sometimes) simulate, within a bounded topic area. Each loop builds on previous loops' synthesis, so knowledge compounds rather than just accumulates. Hypotheses from early loops are revisited and refined as new topics bring new perspectives.

**How a loop works:**
1. Pick a topic cluster (e.g., "ANT fundamentals," "open-ended evolution," "scale and pattern")
2. Research that cluster — read papers, watch transcripts, explore
3. Synthesize with existing knowledge in `concepts/` — refine existing concept files, create new ones
4. Log cross-domain connections in `synthesis.md`
5. Develop or refine hypotheses in `hypotheses/`
6. If a hypothesis is ready, sketch or build a simulation
7. Queue tangential topics for future loops in `queued-topics.md`

**Topic clusters are not fixed.** They emerge from the research. New clusters form when ideas from different domains connect. Old clusters get revisited when new knowledge demands it.

## Key Researchers & Sources

- Stephen Wolfram — computational irreducibility, cellular automata, A New Kind of Science
- Douglas Hofstadter — strange loops, self-reference, Gödel Escher Bach, Fluid Concepts and Creative Analogies
- Santa Fe Institute — complex adaptive systems, Stuart Kauffman, John Holland, Chris Langton
- Blaise Agüera y Arcas — emergence in neural systems, computational biology
- Emergent Garden (YouTube) — transcripts to be studied
- Bruno Latour, Michel Callon, John Law — Actor Network Theory

## Budget

$5/day in tokens. Research conducted in a single session each night starting ~midnight MT. Budget tracked and reported in each daily report.

## Structure

```
~/brain/artificial-life/
  README.md              — this file
  daily-reports/         — YYYY-MM-DD.md session logs (what was read, budget, what happened)
  concepts/              — living documents, one per topic cluster, refined across sessions
  synthesis.md           — running log of cross-domain connections, accumulating across all sessions
  hypotheses/            — hypotheses, refined over time as loops add new knowledge
  researchers/           — notes on specific researchers
  simulations/           — simulation design docs and code
  queued-topics.md       — topics to spiral back to in future loops
  glossary.md            — key terms and definitions
  references.md          — bibliography
```

Simulations will be developed in a separate git repo once theoretical grounding is sufficient.

## Timeline

- Phase 1: Broad research survey (weeks-months)
- Phase 2: Synthesis and hypothesis development
- Phase 3: Minimal simulations (proof-of-concept)
- Phase 4: Iterative refinement — add internal state, irreducible rules
- Phase 5: Game/simulator artifact
