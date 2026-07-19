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

## Methodology

1. **Research** — Broad survey across evolution, intelligence, complex systems, ecosystems, ANT, computational models. Narrow over time. Queue tangential findings for later exploration.
2. **Synthesize** — Connect ideas across domains. Novel insights come from cross-domain synthesis, not single-focus depth.
3. **Hypothesize** — Develop testable hypotheses about multi-scale emergence, network restructuring, and composition.
4. **Simulate** — Build Python simulations to test hypotheses. Start minimal, add complexity (internal state, irreducible rules) incrementally.

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
  daily-reports/         — YYYY-MM-DD.md daily research reports
  concepts/              — deep dives on key concepts
  researchers/           — notes on specific researchers
  hypotheses/            — hypotheses to test
  simulations/           — simulation design docs
  queued-topics.md       — tangential findings queued for later exploration
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
