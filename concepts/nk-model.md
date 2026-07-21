# NK Model (Kauffman)

**Status:** Core concept — formed Session 4
**Connected to:** Fitness landscapes, computational irreducibility, Echo model, open-ended evolution

## The Model

The NK model (Kauffman & Levin, 1987; Kauffman & Weinberger, 1989) is a mathematical model of a "tunably rugged" fitness landscape. Two parameters:

- **N** — length of the binary string (genotype). Defines the size of the search space (2^N genotypes).
- **K** — number of other loci that each locus epistatically interacts with. Controls landscape ruggedness.

Fitness of a string S: F(S) = Σᵢ fᵢ(Sᵢ, Sₖᵢ₁, ..., Sₖᵢₖ)

Each locus contributes to total fitness, and each contribution depends on the locus's own state plus K other loci. The fitness contributions fᵢ are typically drawn from a uniform distribution.

### Tunable Ruggedness
- **K = 0**: No epistasis. Each gene contributes independently. Single fitness peak. Smooth landscape. Easy to find global optimum.
- **K = N-1**: Maximum epistasis. Every gene interacts with every other. Maximally rugged. Many local peaks. Random landscape.
- **0 < K < N-1**: Intermediate ruggedness. Multiple peaks of varying height.

## Computational Complexity

### NP-complete (Weinberger, 1996)
Finding the global optimum on an NK landscape is NP-complete. No polynomial-time algorithm can guarantee finding the best genotype.

### PLS-complete for K > 1 (Kaznatcheev, 2019)
Even finding a LOCAL fitness optimum is computationally hard. PLS-complete (Polynomial Local Search complete) means no known efficient algorithm can find even a local peak. This overturns the traditional assumption (Wright, 1932) that "selection will easily carry the species to the nearest peak."

**Implication:** On hard landscapes (K > 1), evolution cannot reliably find local fitness optima. This is an ULTIMATE constraint — it's a property of the landscape (the problem), not the evolutionary algorithm.

## Relevance to Our Project

### 1. Static landscapes are the wrong model for multi-scale systems

The NK model assumes a FIXED fitness landscape — the genotype-fitness mapping doesn't change. But in multi-scale systems:
- Emergent structures modify the environment (stigmergy, niche construction)
- These modifications change selection pressures (downward causation)
- The fitness landscape is DYNAMIC — it changes as agents adapt to it

This is the key limitation: NK models adaptation TO a landscape, but real complex systems adapt AND reshape the landscape simultaneously. Niche construction theory (Laland) shows this in biology. Stigmergy (Session 3) provides the mechanism.

### 2. Computational complexity enables open-ended evolution

Kaznatcheev (2019) makes a profound argument: computational complexity is an ULTIMATE constraint that ENABLES open-ended evolution:

- On EASY landscapes (K=0, K=1): evolution finds the peak quickly and stops. No open-endedness.
- On HARD landscapes (K>1): evolution cannot find optima. It keeps searching. Fitness advantage follows a power law (not exponential decay). This enables unbounded growth in fitness — the signature of open-ended evolution.

This connects to Wolfram's computational irreducibility: you can't shortcut the evolutionary process on hard landscapes. But Kaznatcheev goes further — the IRREDUCIBILITY is what MAKES evolution open-ended. Without it, evolution converges and stops.

**For our thesis:** Computational irreducibility isn't just a property of our simulation — it's a NECESSARY CONDITION for open-ended evolution. A multi-scale ALife simulation must have computationally irreducible dynamics at each scale, and the cross-scale interactions must preserve this irreducibility.

### 3. Fitness landscapes are always single-scale

The NK model defines fitness for individual genotypes. But in a multi-scale system, fitness is scale-dependent:
- A molecule's "fitness" is about chemical affinity
- A droplet's "fitness" is about surface tension and cohesion
- A cloud's "fitness" is about condensation and albedo

Each scale has its own "fitness landscape" with its own N and K. The multi-scale composition problem is about how these landscapes INTERACT — how changes at one scale reshape the landscape at another.

### 4. NK model's epistasis ↔ ANT's network relations

In the NK model, epistasis (K > 0) means a gene's fitness contribution depends on other genes. This is a network of dependencies. In ANT, an actor's properties ARE its connections. The NK model with K > 0 is an ANT-compatible model: genes are actors, epistatic links are relationships, and fitness is emergent from the network.

But the NK model's network is FIXED (the epistatic links don't change). In ANT, network restructuring is the key process. A multi-scale NK model would need DYNAMIC epistasis — links that form, break, and restructure as the system evolves.

## Criticisms and Limitations

### 1. The fitness landscape metaphor is problematic (Kaplan 2008, Petkov 2015)
- Wright's original landscape was a visual metaphor, not a rigorous model
- Genotype space is high-dimensional; the 2D/3D visual is misleading
- "Peak climbing" assumes adaptive walks, but real evolution includes drift, recombination, non-adaptive processes
- Petkov argues the metaphor persists as a conceptual framework, not because the models work

### 2. NK model's random fitness contributions are unrealistic
The fᵢ values are drawn from uniform random distributions. Real biological fitness landscapes have structure (e.g., nearby genotypes tend to have similar fitness). The random model may overestimate ruggedness.

### 3. Static epistasis is unrealistic
Real epistatic interactions change as the environment changes. The NK model's fixed epistatic network is a simplification that may be deeply misleading for multi-scale systems.

### 4. No empirical validation of landscape ruggedness predictions
Song et al. (2021): "previously reported fitness landscape ruggedness is likely upward biased owing to the negligence of fitness estimation error." The actual ruggedness of real biological landscapes is uncertain.

### 5. NK model doesn't produce emergence
The NK model is an optimization model — it describes search on a landscape. It doesn't model agents, interactions, or emergence. It's a component of a CAS model (like Echo uses implicit fitness landscapes), not a CAS model itself.

## Empirical Evidence

### Kauffman & Levin (1987), Kauffman & Weinberger (1989)
Original mathematical framework. Showed tunable ruggedness and the relationship between K and number of local optima.

### Weinberger (1991)
"Local properties of Kauffman's N-k model" — Physical Review A. Mathematical analysis of landscape structure.

### Kaznatcheev (2019, 74 citations)
"Computational Complexity as an Ultimate Constraint on Evolution" — Genetics. Proved PLS-completeness for K > 1. Connected computational complexity to open-ended evolution. Key theoretical contribution.

### Wiser, Ribeck & Lenski (2013)
Long-term evolution experiments (E. coli, 50,000+ generations) show power-law fitness growth, not exponential. Supports Kaznatcheev's prediction about hard landscapes.

### Song et al. (2021, 14 citations)
Empirical estimation of fitness landscape ruggedness is upward-biased due to fitness estimation error. Caveats the field's quantitative claims.

## Open Questions

- How would a DYNAMIC NK model (where epistatic links change) behave? Would it produce multi-scale structure?
- Can we define a multi-scale NK model where each scale has its own landscape, and cross-scale interactions reshape landscapes at other scales?
- Does computational complexity at one scale imply computational irreducibility at the next scale up?

## Cross-References

- [[concepts/echo-model]] — Echo uses implicit fitness landscapes; NK provides the formal framework
- [[concepts/fitness-landscapes]] — The broader concept and its criticisms
- [[concepts/multi-scale-composition]] — Multi-scale fitness landscapes are the unaddressed problem
- [[concepts/stigmergy]] — Stigmergy makes landscapes dynamic (agents reshape the landscape they adapt to)
- Kauffman & Levin (1987) — original model
- Kaznatcheev (2019) — computational complexity as ultimate constraint
