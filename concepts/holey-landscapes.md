# Holey Fitness Landscapes

**Status:** Core concept — formed Session 5
**Connected to:** Fitness landscapes, NK model, multi-scale composition, dynamic landscapes, computational irreducibility

## The Concept

Gavrilets (1997, 1999, 2004) proposed **holey adaptive landscapes** as an alternative to Wright's (1932) rugged landscape metaphor. The key insight: in high-dimensional genotype spaces, the geometry of fitness landscapes is fundamentally different from what 3D intuition suggests.

A holey landscape is one where:
- **Relatively infrequent well-fit genotype combinations form a contiguous set that expands throughout the genotype space** — a connected network (ridge) of high-fitness genotypes
- The landscape looks like a flat plain of high fitness with "holes" (low-fitness regions) punched through it
- Evolution proceeds along these high-fitness ridges by nearly neutral drift, not by climbing peaks

## Why Holey, Not Rugged

Gavrilets' argument is dimensional. In 2D or 3D, fitness landscapes have peaks and valleys — the rugged landscape. But in high-dimensional spaces (real genotype spaces have thousands of dimensions):

1. **Peaks and valleys average out.** With many traits, the fitness gradients that create peaks in low dimensions create holes in high dimensions. A "peak" in 3D becomes a flat ridge when more dimensions are added.

2. **Connected networks of high-fitness genotypes are inevitable.** Gavrilets & Gravner (1997) proved analytically that under fairly general conditions, high-fitness genotypes form percolating connected networks. This was confirmed in RNA fitness landscapes (Fontana & Schuster, 1987; Schuster et al., 1994) and protein fitness landscapes.

3. **The valley-crossing problem disappears.** On rugged landscapes, evolving from one peak to another requires crossing a fitness valley — selection opposes this. On holey landscapes, there are no valleys: high-fitness genotypes are connected, so populations can drift along ridges without fitness loss.

## Implications for Speciation

The primary motivation for holey landscapes is speciation. On a rugged landscape, speciation requires crossing valleys (the "peak-shift problem"). On a holey landscape:

- Populations can diverge along high-fitness ridges by nearly neutral drift
- Reproductive isolation accumulates as a by-product of genetic divergence along the ridge (Dobzhansky's "complementary genes" idea, formalized)
- Rapid speciation is possible, including simultaneous emergence of multiple species
- Population subdivision (many small subpopulations) facilitates speciation
- Selection for local adaptation is NOT necessary for rapid speciation

## Relevance to Our Project

### Holey landscapes ↔ Dynamic landscapes (H4)

Gavrilets' holey landscapes are still **static** — the high-fitness network is fixed. But the holey landscape view changes what "dynamic" means. On a rugged landscape, making the landscape dynamic means moving the peaks. On a holey landscape, making it dynamic means **reshaping the ridges** — reconnecting the high-fitness network.

This is a fundamentally different kind of dynamics. Niche construction (stigmergy) on a holey landscape doesn't move peaks; it creates new connections between high-fitness regions, or severs existing ones. The landscape's topology changes, not its elevation.

### Holey landscapes ↔ Open-ended evolution (H8)

On a rugged landscape, open-ended evolution requires continuously finding new peaks (hard — PLS-complete, Kaznatcheev 2019). On a holey landscape, open-ended evolution requires continuously extending the high-fitness network. This is potentially easier: any mutation that creates a new high-fitness variant extends the ridge. But it's also potentially limited: if the ridge network is finite, drift along it eventually explores all of it and stops.

The key question: does niche construction (stigmergic modification of the landscape) **extend** the high-fitness network? If agents can create new high-fitness connections through environmental modification, the holey landscape becomes open-ended. This connects H4 (dynamic environment) to H8 (complexity enables open-endedness) through the holey landscape framework.

### Holey landscapes ↔ Multi-scale composition

The high-fitness ridge network IS a structure at a different scale from individual genotypes. It has its own topology (connectedness, branch points, dead ends). A population drifting along the ridge "experiences" the ridge's topology, not the underlying genotype space. The ridge is a macroscopic structure with its own dynamics (drift, branching, extinction of branches).

If the ridge itself can be modified by the agents drifting along it (niche construction), then the ridge is both the path AND the product of evolution. This is a strange loop: the landscape shapes the agents; the agents shape the landscape. In holey landscape terms: the high-fitness network constrains drift; drift modifies the network.

### Holey landscapes ↔ Computational irreducibility

The question of whether the high-fitness network percolates (connects across the entire genotype space) depends on the fitness function. For random fitness assignments, percolation occurs above a threshold (Gravner & Gravner, 2007). For structured fitness functions, the network may or may not percolate. Determining the percolation threshold for a given fitness function is computationally irreducible in general — you must simulate to know. This is H8 in the holey landscape framework.

## Criticisms and Limitations

### 1. Holey landscapes are an approximation
Real fitness landscapes have continuous fitness values, not binary (viable/inviable). Gavrilets' model assumes high-fitness genotypes have approximately equal fitness, but real fitness variation along the ridge may matter. The model is a useful approximation but may not capture the full dynamics.

### 2. The metaphor depends on high dimensionality
Gavrilets explicitly states: "properties of multidimensional adaptive landscapes are very different from those of fewer dimensions." The holey landscape metaphor only applies when the genotype space has many dimensions. For low-dimensional trait spaces (e.g., 2-3 quantitative traits), the rugged landscape may be more appropriate. The 2024 PNAS paper (see below) found empirical support in high-dimensional systems (60 species, 6 phyla).

### 3. Speciation without selection is controversial
Gavrilets argues selection for local adaptation is not necessary for rapid speciation — drift alone suffices. This challenges traditional speciation theory. Some evolutionary biologists find this implausible (Coyne et al., 1997, criticized Wright's landscape; similar arguments apply to Gavrilets).

### 4. Limited empirical validation until recently
Until 2024, evidence for holey landscapes was mostly from RNA/protein fitness landscapes (computational studies) and theoretical percolation results. Direct empirical evidence in natural populations was limited.

### 5. Static network assumption
The high-fitness network is assumed fixed. In reality, environmental change shifts which genotypes are high-fitness, potentially reconfiguring the network. The interaction between holey landscape structure and environmental dynamics is underexplored.

## Empirical Evidence

### RNA fitness landscapes (Fontana & Schuster, 1987; Schuster et al., 1994)
Extensive computational studies of RNA secondary structure landscapes. Found **neutral networks** — connected sets of sequences that fold to the same structure. These networks extend throughout sequence space, confirming the holey landscape prediction. Genotypes on the same neutral network can be reached by single mutations without fitness loss.

### Protein fitness landscapes (Babajide et al., 1997)
Similar neutral networks found in computational protein folding landscapes.

### Analytical proof of percolation (Gavrilets & Gravner, 1997)
Proved that under fairly general conditions, connected networks of high-fitness genotypes exist and percolate through genotype space. This is a mathematical result, not empirical, but it establishes that the holey landscape is a generic property of high-dimensional fitness landscapes, not a special case.

### Empirical: Drift on holey landscapes (2024 PNAS)
**Key empirical finding.** A 2024 PNAS paper (multiple authors, ~60 species across 6 phyla) found that genetic variation in quantitative traits is **consistent with evolution on high-dimensional holey landscapes**, not with the Gaussian (rugged) landscapes that underpin standard evolutionary models. This is the first large-scale empirical support for the holey landscape view in natural populations. The authors conclude: "this suggests that the leading conceptualizations and modeling of the evolution of trait integration fail to capture how phenotypes are shaped."

### NK model and holey landscapes
Barnett (1997) and Newman & Engelhardt (1998) found connected high-fitness networks in Kauffman's NK model, linking the holey landscape view to the NK framework we studied in Session 4.

## Cross-References

- [[concepts/fitness-landscapes]] — Holey landscapes as alternative to rugged landscapes
- [[concepts/nk-model]] — NK landscapes show holey structure at high N
- [[concepts/echo-model]] — Echo's failure may be because its implicit landscape is not holey enough
- [[concepts/multi-scale-composition]] — High-fitness ridges as macroscopic structures
- Gavrilets (1997) — "Evolution and speciation on holey adaptive landscapes" (Trends Ecol. Evol.)
- Gavrilets (1999) — "A Dynamical Theory of Speciation on Holey Adaptive Landscapes" (Am. Nat.)
- Gavrilets (2004) — *Fitness Landscapes and the Origin of Species* (Princeton)
- Gravner & Gravner (2007) — Percolation on fitness landscapes
- 2024 PNAS — Empirical validation across 60 species
