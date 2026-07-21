# Fitness Landscapes

**Status:** Supporting concept — formed Session 4
**Connected to:** NK model, Echo model, stigmergy, niche construction, computational irreducibility

## The Concept

A fitness landscape (Wright, 1932) maps genotypes (or phenotypes) to fitness values, with a notion of distance (mutation graph) between genotypes. The landscape metaphor: genotypes are points on a terrain, fitness is elevation, evolution climbs uphill.

Key assumptions:
1. **Fixed mapping:** genotype → fitness is a pre-defined function
2. **Local search:** evolution proceeds via mutations to adjacent genotypes (adaptive walk)
3. **Peak climbing:** selection drives populations toward local fitness peaks
4. **Static landscape:** the landscape doesn't change during evolution

## The Problem: Static vs. Dynamic Landscapes

### Static landscapes (traditional view)
The fitness landscape is fixed. Agents adapt TO the landscape. This is the NK model, the Echo model (partially), and most optimization algorithms.

### Dynamic landscapes (niche construction / stigmergy view)
Agents MODIFY the landscape as they adapt to it. The landscape changes as a function of agent behavior. This is:
- **Niche construction** (Laland, Odling-Smee): organisms modify selection pressures
- **Stigmergy** (Session 3): agents leave traces that constrain future behavior
- **Downward causation** (Hofstadter): emergent patterns reshape lower-level dynamics

The fitness function becomes: F(genotype, environment_state), where environment_state is a function of the history of agent actions.

### Why this matters for multi-scale composition
A dynamic landscape is the mechanism for cross-scale interaction:
- Agents at scale S1 modify their environment (stigmergic traces)
- These modifications change the fitness landscape for agents at scale S1
- When accumulated traces become self-maintaining (autopoietic), they become a new actor at scale S2
- The new actor at S2 has its own fitness landscape, which it in turn modifies
- This creates a cascade of dynamic landscapes across scales

## The Fitness Landscape Metaphor Criticism

### Kaplan (2008, 126 citations) — "The end of the adaptive landscape metaphor?"
- The metaphor is "deeply problematic" because genotype space is high-dimensional
- The 2D/3D visualization is misleading
- "Peak climbing" ignores drift, recombination, non-adaptive processes
- Argues for abandoning the metaphor in favor of rigorous mathematical models

### Petkov (2015) — "The Fitness Landscape Metaphor: Dead but Not Gone"
- The metaphor persists despite criticisms
- Its primary function is as a "general unifying conceptual framework"
- It reconciles heterogeneous evolutionary phenomena
- Should not be abandoned even when specific models built on it fail
- The metaphor is a linguistic-theoretical tool, not a falsifiable model

### Gavrilets (2004) — "Fitness Landscapes and the Origin of Species"
- Proposes "holey landscapes" — landscapes where high-fitness genotypes form connected networks
- Alternative to the "rugged landscape" view
- Speciation occurs along these high-fitness ridges, not by climbing peaks

## Relevance to Our Project

### 1. Static landscapes cannot produce multi-scale composition
If the landscape is fixed, agents can only climb to local optima. They cannot reshape the landscape to create new scales. This is why Echo fails — even with endogenous fitness, the landscape is effectively static within a run.

### 2. Dynamic landscapes are necessary but not sufficient
Making the landscape dynamic (agents modify it) is necessary for multi-scale composition, but not sufficient. The modifications must:
- **Persist** (stigmergic traces with appropriate decay rate)
- **Accumulate** (build up over time)
- **Become self-maintaining** (autopoietic crossing — H7)
- **Constrain agents at the original scale** (downward causation)

### 3. The metaphor problem applies to ALife
ALife simulations implicitly use fitness landscapes. Even "emergent" ALife (Lenia, EvoLoop) has implicit landscapes defined by the rules. The criticism applies: if we think in terms of "fitness peaks," we'll design simulations that converge to peaks. We need to think in terms of dynamic, multi-scale landscape cascades.

## Empirical Evidence

### Wright (1932) — original metaphor
Visual representation of genotype frequency space. Not a mathematical model.

### Gavrilets (2004) — holey landscapes
Mathematical framework for high-fitness networks. Alternative to rugged landscape view. Supported by speciation models.

### Wiser, Ribeck & Lenski (2013) — long-term E. coli
50,000+ generations show power-law (not exponential) fitness growth. Consistent with hard (rugged) landscape dynamics.

### No empirical studies on dynamic multi-scale landscapes
No study tests whether dynamic, multi-scale fitness landscapes produce open-ended evolution. This is our novel contribution territory.

## Cross-References

- [[concepts/nk-model]] — The formal mathematical framework for rugged landscapes
- [[concepts/echo-model]] — Echo's endogenous fitness is a step toward dynamic landscapes
- [[concepts/stigmergy]] — Stigmergy makes landscapes dynamic (agents reshape the landscape)
- [[concepts/multi-scale-composition]] — Multi-scale dynamic landscapes are the unaddressed problem
- Wright (1932) — original metaphor
- Kaplan (2008) — "end of the metaphor" criticism
- Petkov (2015) — "dead but not gone" defense
- Gavrilets (2004) — holey landscapes alternative
