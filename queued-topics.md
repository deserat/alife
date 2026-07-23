# Queued Topics for Later Exploration

Findings from daily research that lead down a different focus track. Saved here for later exploration.

## From Session 1

1. **Holland's Echo model** — A classic SFI complex adaptive system model. How does it handle (or fail to handle) multi-scale composition?
2. **Langton's edge of chaos (Lambda parameter)** — Does the edge of chaos shift when you allow multi-scale composition? Is the edge of chaos a network restructuring event?
3. **Stigmergy** — Indirect coordination through environmental modification. ANT-compatible (environment as actor). Mechanism for cross-scale interaction.
4. **Deleuze & Guattari's rhizome** — Latour references this. No center, no hierarchy. How does this differ from a scale-free network?
5. **Blaise Agüera y Arcas** — Emergence in neural systems, social aggregation in computational systems.
6. **Renormalization group (Wilson)** — Formal method for relating descriptions at different scales in physics. Could it be adapted for ALife?
7. **von Neumann's universal constructor** — Original self-replication model. The constructor builds itself, which is a strange loop.
8. **Kauffman's NK model and fitness landscapes** — How do fitness landscapes change when actors are defined relationally?
9. **Capra & Luisi, The Systems View of Life** — Systems thinking, autopoiesis, origins of life.

## From Session 2

10. **Downward causation and computational irreducibility** — If high-level patterns causally influence low-level components, does that make the system more or less irreducible? Can we quantify this?
11. **Multi-scale autopoiesis** — Systems producing systems at different scales. Is this the mechanism for complexification? Test via simulation.
12. **Tangled hierarchy formalization** — How to represent a tangled hierarchy computationally? Not a tree, not a graph, but a level-crossing feedback structure.
13. **Gödel's incompleteness and ALife** — Hofstadter connects Gödel to strange loops. Does formal undecidability have implications for what ALife simulations can produce?
14. **Luhmann's social autopoiesis** — Niklas Luhmann applied autopoiesis to social systems. Connection to ANT's social networks.
15. **Memes and evolutionary stigmergy (Blackmore/Dawkins)** — Memes as stigmergic traces that propagate, mutate, and evolve. How does this differ from static stigmergic traces? Can stigmergic traces in a simulation evolve? Connection to quasi-objects (traces that transform through circulation). Memes as a bridge between stigmergy and Darwinian replicators.

## From Session 3

15. **Heylighen's varieties of stigmergy** — Full taxonomy (quantitative/qualitative, sematectonic/marker-based, transient/persistent, broadcast/narrowcast). How do these map to computational stigmergic mechanisms? Which varieties are most relevant for ALife?
16. **Ecosystem engineering vs. niche construction** — The distinction between Jones et al.'s ecosystem engineering and Odling-Smee's niche construction. NCT emphasizes evolutionary feedback; EE emphasizes ecological impact. Which is more relevant for multi-scale ALife?
17. **Extended evolutionary synthesis debate** — The controversy over whether niche construction requires new evolutionary theory or is accommodated by standard theory. Parallel question for ALife: does stigmergy require new simulation paradigms or is it already present in any dynamic-environment simulation?
18. **Chemical Organization Theory** — Heylighen mentions Dittrich & Fenizio's framework for agentless stigmergic coordination in chemical reaction networks. Could this formalism be adapted for ALife composition?
19. **Braitenberg vehicles and stigmergic cognition** — Heylighen's analysis of Braitenberg vehicles as stigmergic systems. Connection between stigmergy and embodied cognition.
20. **Trace decay rate optimization** — The transient/persistent trace trade-off. Is there an optimal decay rate for the trace→actor crossing? How does this relate to Wolfram's computational irreducibility?

## From Session 4

21. **Chemical Organization Theory** (Dittrich & Fenizio) — Still queued. Agentless stigmergic coordination in chemical reaction networks. Could provide formalism for ALife composition. Next session priority.
22. **Multi-scale NK model** — Define NK landscapes at each scale with cross-scale interactions reshaping landscapes. How do dynamic epistatic networks behave? Does multi-scale landscape structure produce open-ended evolution?
23. **Gavrilets' holey landscapes** — High-fitness genotype networks as alternative to rugged landscape view. How do holey landscapes behave with niche construction? Does the dynamic landscape view change the holey/rugged distinction?
24. **Holland's "Signals and Boundaries" (2012)** — His last monograph. Co-evolution of signals and semi-permeable boundaries. Connection to our stigmergy + autopoiesis synthesis.
25. **Implementing Smith & Bedau's 8th CAS property** — They proposed it in 1997 but never implemented it. Our sim02 shows naive stigmergy doesn't do it. What mechanism would? The autopoietic crossing (H7) is the candidate. Design sim03/sim04 to test.
26. **Trace competition** — Multiple trace types that interact/compete. Sim02 used a single trace field. Multiple trace types might prevent monoculture convergence and enable multi-scale structure.
27. **Kaznatcheev's hard/soft landscape distinction** — Which NK parameters produce open-ended dynamics? Sweep K and N to find the boundary. Connection to edge of chaos (Langton).
28. **Ecosystem engineering vs. niche construction (still queued)** — Jones et al. vs. Odling-Smee. Which is more relevant for ALife?
29. **Heylighen's varieties of stigmergy (still queued)** — Computational mapping of stigmergy taxonomy.

## From Session 5

30. **Fontana & Buss's AlChemy (lambda calculus chemistry)** — DONE (Session 6). Implemented sim05. L1 organizations emerge; L2 composition fails (0/6). Unbounded space is necessary but not sufficient (H10).
31. **Per-compartment catalysis** — Our sim04 shared catalysis rules across all compartments. Vasas et al. generate catalysis independently per compartment. Does independent catalysis produce more between-compartment diversity? Test in sim05/sim06.
32. **P_catalyze tuning for distinct cores** — Our sim04 used P=0.005, likely too high (one large core). Vasas used P''=0.0025 and still had difficulty finding distinct cores. Sweep P to find the regime where distinct cores form.
33. **Expanding the adjacent possible** — Kauffman's concept. Each novel core extends the "shadow" of possible reactions. Can we measure the adjacent possible in our simulations? Does the evolving network explore more of it than the fixed network?
34. **Holland's tagged urn model implementation** — Holland proposed it but never tested it. Could implement as sim06: urns with semi-permeable boundaries containing tags, with GA-evolved classifiers. Test whether nested boundaries emerge. PRIORITY: this could provide the composition mechanism that sim05 showed is missing.
35. **From "one bit" to open-ended** — The core limitation from Vasas et al. How to move beyond 1-bit heritable information? Template replication (RNA world) is the biological answer. What is the ALife answer? Multiple interacting cores? Compositional inheritance? Tag-based heredity?
36. **Multiple attractors ≠ evolvability** — Vasas found networks with inhibition had multiple attractors but they were NOT selectable (periodic/chaotic transitions overrode selection). Explore this: what makes attractors selectable vs. not? Stability, heritability, differential fitness.

## From Session 6

37. **Explicit composition mechanisms for L2** — Sim05 confirmed L2 (multi-scale composition) doesn't emerge spontaneously even with unbounded space. What mechanisms would produce it? Candidates: (a) stigmergic bridges between organizations, (b) autopoietic boundaries that protect during interaction, (c) explicit selection for composability. Design sim06 to test these. TOP PRIORITY.
38. **Measuring the adjacent possible in AlChemy** — Sim05 showed each L1 run explores 246-930 species. Can we measure how much of the "adjacent possible" (Kauffman) is explored? Does the rate of novel species discovery follow a power law? Does it slow down (converging) or stay constant (exploring)?
39. **Mutual destruction as creative process** — Sim05 found mutual destruction produces the most novel species (89-90 unique vs 6-23 for dominance). Can we harness this novelty without destroying the parents? Autopoietic boundaries might protect parents while allowing cross-organization interaction.
40. **Assembly theory connection** — Mathis et al. 2024 reference Cronin/Walker's assembly theory. Assembly theory quantifies selection by molecular complexity. Could assembly index be a metric for ALife organization complexity? Connection to our multi-scale composition metric needs.
41. **Krzyszewski & Mikolov (2022) — self-reproducing metabolisms as recursive algorithms** — Referenced in Mathis et al. 2024. Emergence of self-reproducing metabolisms in artificial chemistry. Could connect to our autopoiesis + stigmergy synthesis.
