# Glossary

## ANT Terms

**Actor / Actant** — Any entity that participates in a network. Can be human, non-human, institutional, or conceptual. In ANT, anything that has effects on other entities is an actor. Defined by its relationships, not its intrinsic properties.

**Translation** — The process by which actors form and restructure networks. Callon's four moments: problematization (defining a problem that interests others), interessement (attracting others into the network), enrollment (negotiating roles and relationships), mobilization (the collective acts as one).

**Quasi-object** (from Serres) — Something that circulates through a network AND is transformed by the circulation. Both the circulating object and the movers are co-determined and transformed. Contrast with a ball that stays unchanged when passed.

**Generalized symmetry** — The methodological principle that human and non-human actors should be described using the same vocabulary. No a priori distinction between social and natural.

**Network** — Not a technical network (like a phone network) but a topology of relationships. An actor-network may be local, may have no compulsory paths, no strategically positioned nodes. A technical network is one possible stabilized state of an actor-network.

## ALife Terms

**Darwinian replicator** — A structure that: (1) replicates (copies itself), (2) varies (copies are imperfect), (3) is selected (some copies survive, others don't). The algorithmic basis of evolution.

**Open-ended evolution** — Evolution that continuously produces novel, surprising complexity without converging to a stable state or repeating. The "holy grail" of ALife. No simulation has achieved it.

**Explicit design vs Implicit design** — Explicit: behaviors written in the source code. Implicit: behaviors that emerge as consequences of explicit rules but aren't in the code themselves. A glider in Game of Life is implicit.

**Genetic algorithm** — Optimization algorithm with explicit fitness function. Selects, mutates, recombines solutions. Most explicit, least emergent.

**Evolution simulation** — Shared environment with organisms, no fitness function. Reproduction and death functions replace fitness. Fitness is implicit. More emergent than genetic algorithms.

**Emergent ALife** — Zero explicit biological systems. No genes, organisms, species, mutations. Life emerges from lower-level rules (physics/chemistry). Most implicit, most emergent, hardest.

**Self-replication** — A structure that copies itself. Can be trivial (crystal growth) or meaningful (with variation, selection, adaptation). Trivial self-replication is common; meaningful self-replication leading to evolution is rare.

**Stigmergy** — Indirect coordination through environmental modification. Agents interact via the environment rather than directly. (Queued for deeper study.)

## Hofstadter / Cognition Terms

**Strange loop** — A cyclic structure that moves through levels of a hierarchy and arrives back where it started. Not simple recursion — a paradoxical level-crossing feedback loop. The defining feature is the shift between levels of abstraction.

**Tangled hierarchy** (heterarchy) — A hierarchical system with no clearly defined highest or lowest level. Moving through levels, one returns to the starting point. The topology of multi-scale systems.

**Downward causation** — High-level emergent patterns exert causal potency over low-level components. The flood reshapes topography; the self influences neurons. Challenges pure reductionism. Critical for ALife: emergent structures must be able to modify rules at their scale.

## Autopoiesis Terms

**Autopoiesis** (Maturana & Varela) — A system that produces and maintains itself. A network of processes that continuously regenerate the network that produced them. The canonical example: a biological cell. Two conditions: (1) self-production, (2) boundary maintenance.

**Operational closure** — The condition where a system's processes form a closed loop — each process is enabled by other processes in the system. Distinct from thermodynamic closure. An autopoietic system is operationally closed but thermodynamically open.

**Catalytic closure** — In computational autopoiesis, each catalyst is the product of a reaction it catalyzes. A circular dependency that creates self-maintenance.

## Complexity Science Terms

**Computational irreducibility** (Wolfram) — Some complex computations cannot be short-cut. To know the outcome, you must run the computation. No shortcut to prediction.

**Coarse-graining** — Describing a system at a lower resolution. Israeli & Goldenfeld showed that computationally irreducible systems can be predictable at coarse-grained levels, even if irreducible at fine scales.

**Edge of chaos** (Langton) — The boundary between ordered and chaotic behavior in cellular automata, where complex, life-like behavior is most likely. Quantified by the Lambda parameter.

**Complex adaptive system** (SFI) — A system of interacting agents that adapt/learn, where macro-level patterns emerge from micro-level interactions. Key properties: adaptation, emergence, self-organization, non-linearity, feedback.

## Ecology Terms

**Pattern and scale** (Levin) — The problem that ecological patterns emerge from processes operating at different scales. No single scale is correct for study. Cross-scale interactions are fundamental.

**Self-organization** — Order that emerges from local interactions without central control. In ecology, ecosystems self-assemble from components shaped by evolution.

## Stigmergy Terms

**Stigmergy** (Grassé) — A mechanism of indirect coordination where the trace left by an action in a medium stimulates a subsequent action. Agents do not communicate directly — they modify a shared environment, and those modifications guide future actions. The core feedback loop: action → trace → stimulation → action.

**Medium** (Heylighen's term for "environment" in stigmergy) — The part of the world that undergoes changes through actions AND whose states are sensed as conditions for further actions. A stigmergic medium must be both perceivable and modifiable. The beach is a stigmergic medium; the sky is not (perceivable but not modifiable); the sea floor is not (modifiable but not perceivable).

**Trace** — The perceivable change made in the medium by an action, which may trigger a subsequent action. Functions as both a memory of what has been done and a signal for what still needs doing.

**Sematectonic stigmergy** — Stimulation by the work itself (e.g., termites stimulated by the mud heap they've built). Contrast with marker-based.

**Marker-based stigmergy** — Stimulation by specially evolved signals (e.g., pheromones). More efficient than sematectonic but costlier — agents must manufacture markers in addition to doing the work.

**Quantitative stigmergy** — Stronger traces elicit more intense/frequent actions (e.g., pheromone concentration). Contrast with qualitative.

**Qualitative stigmergy** — Different traces trigger different types of actions (e.g., nest-building stages). Contrast with quantitative.

**Affordance** (Gibson) — An environmental feature that facilitates an agent's movement toward its goal. In stigmergy, positive diversions that are reinforced by positive feedback.

**Disturbance** — An environmental change that hinders an agent's movement toward its goal. In stigmergy, negative diversions that are counteracted by negative feedback.

## Niche Construction Terms

**Niche construction** (Odling-Smee) — The process whereby organisms actively modify their own and each other's evolutionary niches. When modifications alter natural selection pressures, evolution by niche construction is a possible outcome. The evolutionary biology analog of stigmergy.

**Ecological inheritance** — The legacy of modified selection pressures that persists in the environment across generations. An additional component of inheritance beyond genetic transmission. The dam, lake, and lodge persist longer than the beaver that built them, shaping selection on descendants.

**Perturbational niche construction** — Physical changes organisms bring about in their environments (building nests, burrows, dams). Contrast with relocational.

**Relocational niche construction** — When organisms move in space and are exposed to new conditions, altering their selection pressures without physically modifying the environment.

**Extended phenotype** (Dawkins) — Adaptations expressed outside the body of the individual whose genes underlie them. A narrower concept than niche construction: NCT includes selective feedback to traits unrelated to the constructing trait, and recognizes ecological inheritance.

## Cross-Domain Terms (Our Project)

**Multi-scale composition** — Our term for the process by which emergent phenomena at one scale interact to produce qualitatively new phenomena at another scale, where actors and interaction rules are fundamentally different. The gap in current ALife simulations.

**Network restructuring event** — Our term for the phase transition between scales, described using ANT's translation concept. When emergent structures become new actors with new rules.

**Trace→actor crossing** — Our term for the phase transition where accumulated stigmergic traces become autopoietic — self-maintaining structures that act as new-level actors. The crossing from coordination (within a scale) to composition (a new scale). Stigmergy provides the medium; autopoiesis provides the persistence; the crossing is the multi-scale phase transition.

**Quasi-object resource** — Our term for a resource in a simulation that is transformed as it circulates through the network (following Latour's quasi-object concept). Contrast with fixed-property resources.
