# Evolving Reaction Networks

**Status:** Core concept — formed Session 5
**Connected to:** Chemical Organization Theory, autopoiesis, multi-scale composition, computational irreducibility, ANT translation, trace→actor crossing, open-ended evolution
**Topic:** How reaction networks that generate new reactions overcome the evolvability stall

## The Problem: Fixed Networks Stall

Chemical Organization Theory (Dittrich & di Fenizio, 2007) describes organizations as attractors of a FIXED reaction network. Once the system converges to an organization, it stays there. Our sim03 confirmed this: the system reached a fixed equilibrium by generation 1 and never changed for 3000 generations. This is the same stall as EvoLoop, computational autopoiesis, and Echo — self-maintenance without evolution.

Vasas, Szathmáry & Santos (2010, PNAS) proved this formally: autocatalytic sets (a special case of COT organizations) **lack evolvability**. Compositional genomes ("composomes") cannot maintain heritable variation because replication of compositional information is too inaccurate. The system "cannot substantially depart from the asymptotic steady-state solution already built-in in the dynamical equations."

## The Resolution: Rare Novel Reactions + Compartments

Vasas et al. (2012, "Evolution before genes," Biology Direct) found the way out:

1. **Rare uncatalyzed reactions** produce novel molecular species from the "shadow" (species that could exist but don't yet). Most disappear. But rarely, a novel species catalyzes its own production from existing molecules, forming a **viable autocatalytic loop** — a new **core**.

2. **Autocatalytic cores** are sets of connected autocatalytic loops. A core is the "genotype" — it can seed itself from any one member. The **periphery** (molecules catalyzed by the core) is the "phenotype."

3. **Compartmentalization** is required. Compartments filter harmful modifications and enable between-compartment selection. Without compartments, novel cores are diluted.

4. **Multiple cores = multiple attractors.** With only one core, there's one attractor and no selection. With multiple cores, there are multiple attractors with different growth rates — the basis for natural selection.

5. **Heredity via core loss/gain.** When a compartment divides, a core may be lost (segregation instability). When rare reactions occur, a core may be gained. This is mutation. Core → periphery is genotype → phenotype. This is heredity.

6. **Two levels of autocatalysis**: molecular (within compartments) and compartmental (division). The compartment reproduces; the core replicates.

## Key Empirical Results (Vasas et al. 2012)

- In 460 simulation runs of 30,000 steps each, **5 runs** showed persistent increase in non-food set mass due to novel viable loops.
- Novel cores produce selectable attractors — a 1% selective advantage is enough to shift population composition.
- Networks with inhibition had multiple attractors but they were NOT selectable (transitions were periodic/chaotic, overriding selection). **Multiple attractors ≠ evolvability.** Selectability requires attractors that are stable, heritable, and differentially fit.
- The original Farmer/Kauffman autocatalytic sets always had exactly ONE attractor — definitively not evolvable.

## The "One Bit" Limitation

Vasas et al. note that a viable core constitutes approximately "one bit of heritable information." The number of possible selectable attractors is small, so autocatalytic networks "may not be able to sustain open-ended evolution." However, each novel core extends the "shadow" (adjacent possible), opening new possibilities for discovering further cores. This is "cooptive evolution" — stepwise expansion into the adjacent possible.

This connects directly to Kauffman's "adjacent possible" concept: the system explores the space of possible reactions by expanding into neighboring regions. Each new core opens new neighbors.

## Connection to Fontana & Buss (1994)

Fontana & Buss ("The Arrival of the Fittest," SFI 1993) pioneered this approach using lambda calculus as the "chemistry." In their AlChemy system:
- Molecules are lambda expressions
- Reactions are lambda calculus operations (application, composition)
- New molecules appear as products of reactions
- The system explores an open-ended space of possible molecules

They found that the system produces "organizational transitions" — shifts between qualitatively different organizational regimes. This is the same phenomenon as Vasas's novel cores: the reaction network itself evolves, producing new organizations.

Key Fontana & Buss insight: **"construction"** (building new molecules from existing ones) is what enables open-endedness. A system that only "copies" (identity functions) stalls. A system that constructs novel molecules from existing ones explores the adjacent possible. Parasites and side-reactions are not bugs — they are the source of novelty.

## Relevance to Our Project

### Evolving networks ↔ H7 (Trace→Actor Crossing)

The "rare novel reaction" that produces a new viable core IS the trace→actor crossing. In COT terms:
- Existing resources are "traces" (accumulated products of reactions)
- A novel reaction among existing resources produces a new self-maintaining set (organization)
- The new organization is a new "actor" at a new level
- The crossing from "trace" to "actor" is the appearance of a novel viable core

This makes H7 mechanistically concrete: the trace→actor crossing occurs when a rare novel reaction produces a viable autocatalytic core from existing resources.

### Evolving networks ↔ H8 (Computational Irreducibility)

You cannot predict which novel cores will appear — you must simulate. The space of possible reactions is too large to enumerate, and the conditions for viability (closure + self-maintenance) depend on the entire network state. This is computational irreducibility at the level of the reaction network. The system must be run to know what it will produce.

### Evolving networks ↔ ANT Translation (H2)

The appearance of a novel core is ANT's "enrollment" — a new collective forms from existing actors and begins to act as one. The core's periphery is the "mobilization" — the new collective acts on its environment (catalyzing peripheral molecules). The loss of a core at division is "disenrollment" — the collective dissolves.

### Evolving networks ↔ Multi-scale composition (H1)

Two levels of autocatalysis (molecular + compartmental) IS multi-scale composition. The molecular level (reactions within a compartment) and the compartmental level (division, selection between compartments) have different rules. The molecular level produces novelty (new cores); the compartmental level selects among them. This is the cross-scale interaction we've been looking for — and it emerges naturally from the reaction network + compartment structure.

### Evolving networks ↔ Holland's Signals and Boundaries

Holland (2012) argued that CAS are built from co-evolving signals and boundaries. In Vasas's model:
- **Boundaries** = compartment membranes (filter, contain)
- **Signals** = catalytic activities (molecules that enable reactions)
- **Co-evolution** = the boundary (compartment) determines which signals (cores) persist; the signals (cores) determine the compartment's fitness (growth rate)

Holland's framework and Vasas's model arrive at the same structure from different directions. Holland from CAS theory; Vasas from origin-of-life chemistry. Our project from ANT + computational irreducibility. Three independent paths converging on: **evolving signal/boundary hierarchies = multi-scale composition**.

## Criticisms

### 1. The "one bit" problem
Vasas et al. acknowledge that autocatalytic cores carry ~1 bit of heritable information. Open-ended evolution requires unlimited heritable information (Taylor 2012). The gap between "evolvable" and "open-ended" is enormous.

### 2. Chemical realism
All models use abstract "chemistry" (random catalysis probabilities). Real chemistry has structure-dependent catalysis (sequence → fold → function). The probability of viable cores in real chemistry may be much lower.

### 3. The supracriticality problem
For novel cores to appear at appreciable rates, the catalytic probability P must be above a threshold. In real peptide chemistry, P is likely too low. The models require "unrealistically high" catalytic probabilities.

### 4. No spatial structure
Vasas's model has no spatial structure — compartments are well-mixed. Multi-scale composition in real systems involves spatial structure (termite mounds, embryos, ecosystems). The compartment is a spatial boundary, but within it, everything mixes.

### 5. Open-endedness not demonstrated
Vasas shows limited evolvability (selection between 2-3 attractors). No demonstration of open-ended evolution (unbounded novelty). The system eventually exhausts the adjacent possible for a given food set.

## Empirical Evidence

- Vasas et al. (2012): 5/460 runs showed persistent complexity increase via novel viable loops
- Fontana & Buss (1994): organizational transitions in lambda calculus chemistry
- Bagley, Farmer & Fontana (1992): supracritical growth above catalytic threshold
- Hordijk & Steel (2018): RAF sets as special case of COT organizations

No empirical evidence for open-ended evolution in evolving reaction networks. The evidence supports limited evolvability, not open-endedness.

## Cross-References

- [[concepts/chemical-organization-theory]] — COT describes fixed networks; evolving networks extend it
- [[concepts/autopoiesis]] — Cores are autocatalytic = self-producing
- [[concepts/multi-scale-composition]] — Two-level autocatalysis = multi-scale
- [[concepts/signals-and-boundaries]] — Holland's framework converges with Vasas
- [[concepts/open-ended-evolution]] — The "one bit" limitation
- Vasas et al. (2012) — "Evolution before genes"
- Fontana & Buss (1994) — "The Arrival of the Fittest"
- Holland (2012) — "Signals and Boundaries"
