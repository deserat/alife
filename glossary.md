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

## CAS Theory Terms (Session 4)

**Complex adaptive system (CAS)** (Holland) — A system of interacting adaptive agents where macro-level patterns emerge from micro-level interactions. Holland identified seven essential attributes: four properties (aggregation, nonlinearity, flows, diversity) and three mechanisms (tags, internal models, building blocks).

**Echo model** (Holland, Forrest, Jones) — A computational CAS model with evolving agents in a resource-limited environment. Agents interact via combat, trading, and mating, with endogenous fitness (no external fitness function). Smith & Bedau (1997) found it fails to produce hierarchical adaptive aggregates.

**Endogenous fitness** — Fitness that emerges from agent interactions with the environment and other agents, rather than being defined by an external function. Echo's key feature. Distinguished from exogenous fitness (e.g., a pre-defined NK landscape).

**NK model** (Kauffman) — A tunably rugged fitness landscape. N = string length (search space size), K = number of epistatic interactions per gene (ruggedness). K=0: smooth (single peak). K=N-1: maximally rugged. PLS-complete for K>1 — even local optima are computationally hard to find.

**Epistasis** — The interaction between genes where the fitness effect of one gene depends on the state of other genes. In the NK model, K controls the degree of epistasis. Higher K = more epistasis = more rugged landscape.

**PLS-complete** — A complexity class for local search problems. A PLS-complete problem has no known polynomial-time algorithm for finding even a local optimum. Kaznatcheev (2019) proved NK landscapes with K>1 are PLS-complete.

**Ultimate constraint** (Kaznatcheev) — A constraint on evolution due exclusively to the structure of the fitness landscape (the problem), not the evolutionary algorithm. Contrast with proximal constraint (due to population structure, mutation bias, etc.). Computational complexity is an ultimate constraint: it prevents finding fitness optima regardless of the evolutionary mechanism.

**Fitness landscape** (Wright 1932) — A mapping from genotypes to fitness values with a notion of distance between genotypes. The landscape metaphor: genotypes are points on terrain, fitness is elevation, evolution climbs uphill. Criticized for assuming static landscapes and misleading 2D/3D visualization.

**Dynamic fitness landscape** — A fitness landscape that changes as agents interact with it. Agents modify the landscape they're adapting to (niche construction, stigmergy). Contrast with static (fixed) landscapes. Necessary for multi-scale composition: cross-scale interactions require that emergent structures reshape selection pressures at other scales.

**Holey landscape** (Gavrilets) — A fitness landscape where high-fitness genotypes form connected networks (ridges). Alternative to the rugged landscape view. Speciation occurs along these high-fitness ridges, not by climbing isolated peaks.

**Smith & Bedau's 8th CAS property** — The proposed additional property of CAS: "the ability of emergent interacting components to create and flexibly maintain their own boundaries and their capacities for interacting with other components." Maps to our synthesis: stigmergy (create boundaries) + autopoiesis (maintain boundaries). The crossing from trace to 8th-property actor is our trace→actor crossing (H7).

## Multi-Rate Environment Terms

**Multi-rate bounded environment** — An environment composed of multiple actors, each changing at a different rate, each bounded by its own rules. Slow actors (geology) provide stability; fast actors (temperature) provide variation. The interaction between rates prevents fitness landscape stasis.

**Multiple fitness criteria** — Instead of a single fitness function, organisms face multiple selection pressures from different environmental actors, each with its own dynamics. No single optimum is permanent because while one pressure stabilizes, another shifts.

**Bounded change** — Environmental actors change within constraints governed by their own rules, not randomly. Land changes per geology; temperature changes per climate bounds. Each actor's change is rule-governed at its own scale.

## Chemical Organization Theory Terms (Session 5)

**Chemical Organization Theory (COT)** (Dittrich & di Fenizio, 2007) — A formal framework for analyzing self-organizing systems using reaction networks (directed hypergraphs). An **organization** is a subset of a reaction network that is both **closed** (no new resources generated) and **self-maintaining** (every consumed resource is regenerated). Organizations are attractors of the dynamics.

**Closure** (COT) — For every reaction whose inputs are all in the subset, the outputs are also in the subset. No new resources appear from within. The attractor of resource addition.

**Self-maintenance** (COT) — Every consumed resource in the subset is produced again by some other reaction. The attractor of resource removal. Together with closure, defines an organization.

**Autocatalytic core** (Vasas et al., 2012) — A set of connected autocatalytic loops within a reaction network. Each member catalyzes production of other members. A core is the "genotype" — any one member can seed the entire core. The **periphery** (molecules catalyzed by the core) is the "phenotype."

**Viable autocatalytic loop** — An autocatalytic loop that grows exponentially (uses external reactants, not just its own products). Contrast with **suicidal autocatalyst** — an autocatalytic molecule that consumes its own products, leading to self-decomposition.

**Evolving reaction network** — A reaction network where the set of reactions R itself changes over time (new reactions appear via rare uncatalyzed events). Contrast with fixed network (R is constant). The key distinction for evolvability: fixed networks converge to static organizations; evolving networks can discover novel viable cores.

**Compartmentalization** — Enclosing reaction networks in semi-permeable boundaries (compartments) that filter harmful modifications and enable between-compartment selection. Required for evolvability in chemical networks: without compartments, novel cores are diluted; with them, cores can be gained or lost at division (mutation + heredity).

**Two-level autocatalysis** (Vasas et al.) — Autocatalysis at the molecular level (reactions produce catalysts for more reactions) AND at the compartment level (compartments grow and divide). These are different scales with different rules — molecular produces novelty, compartmental selects among it.

**The "one bit" problem** — A single viable autocatalytic core carries approximately one bit of heritable information (present/absent). This severely limits the evolvability of autocatalytic networks: the number of selectable attractors is small, and the system may not sustain open-ended evolution.

## Signals and Boundaries Terms (Session 5)

**Signals and Boundaries** (Holland, 2012) — Holland's final framework: CAS as co-evolving signal/boundary hierarchies. **Signals** are environmental modifications that coordinate behavior (stigmergic traces). **Boundaries** are semi-permeable structures that filter signals (autopoietic structures). They co-evolve: signals modify boundaries, boundaries filter signals. The hierarchy of nested boundaries = multi-scale structure.

**Tagged urn model** (Holland) — A probabilistic model where urns containing tags represent boundaries. Tags circulate through semi-permeable boundaries between urns. Enables modeling nested boundaries without nested urns — a flat representation of hierarchical structure.

**Co-evolution of signals and boundaries** — The feedback loop where signals (traces) modify boundaries (organizations), and boundaries filter which signals persist. This is the stigmergic feedback loop through the medium, formalized in Holland's framework.
