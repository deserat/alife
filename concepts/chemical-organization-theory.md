# Chemical Organization Theory (COT)

**Status:** Core concept — formed Session 5
**Connected to:** Autopoiesis, multi-scale composition, stigmergy, quasi-objects, ANT, trace→actor crossing, Echo model

## The Theory

Chemical Organization Theory (Dittrich & di Fenizio, 2007) is a formal framework for analyzing self-organizing systems using **reaction networks**. Unlike traditional network models (directed graphs), reaction networks are **directed hypergraphs**: reactions map *sets* of resources to *sets* of resources.

Formal definition: A reaction network is a pair ⟨M, R⟩ where:
- M = {a, b, c, …} is the set of **resources** (molecules, species, agents, ideas, decisions — any measurable phenomenon)
- R ⊆ P(M) × P(M) is the set of **reactions**, each mapping an input set to an output set: r: {x₁, x₂, …} → {y₁, y₂, …}

The "+" symbol represents conjunction (AND). Juxtaposition of reactions represents disjunction (OR). This is the key advantage over traditional networks: reaction networks can express **combinatorial interactions** (multiple inputs produce multiple outputs), while traditional networks only express one-to-one connections.

## The Organization: Closure + Self-Maintenance

An **organization** is a subset ⟨M', R⟩ of a reaction network that is both:

1. **Closure**: No new resources are generated. For every reaction whose inputs are in M', its outputs are also in M'. Formally: ∀ r ∈ R such that In(r) ⊆ M', Out(r) ⊆ M'.

2. **Self-maintenance**: No existing resource is lost. Every consumed resource is produced again by some other reaction. Quantitatively: there exists a flux vector such that the net production rate is non-negative for all resources.

**Organizations are attractors of the dynamics.** Every fixed point of the differential equations governing the reaction network corresponds to an organization (Peter & Dittrich, 2011). More complex attractors (limit cycles, chaotic regimes) also correspond to organizations in most cases.

## Self-Organization Produces Organizations

The emergence of organizations follows a two-phase self-organization process:

1. **Resource addition → closure**: Starting from an arbitrary subset, reactions produce new resources. These new resources activate further reactions, producing more resources. This growth ends when no new resources can be produced — closure is reached. Closure is the **attractor of resource addition**.

2. **Resource removal → self-maintenance**: From the closed set, resources consumed faster than produced will disappear. Their disappearance may cascade (removing reactions that depended on them). This process ends when remaining resources are all self-sustaining — self-maintenance is the **attractor of resource removal**.

The invariant set after both phases is an organization. This is a direct formalization of self-organization as convergence to an attractor.

## Key Properties for Our Project

### 1. COT formalizes autopoiesis

An organization IS a simple model of autopoiesis. The organization persistently recreates its own components: what disappears in one reaction is recreated by another. The set M' is invariant even though every resource is in constant flux. Heylighen (2024): "organizations are more primitive than living systems" — they lack the boundary production that full autopoiesis requires, but they have the self-production property.

This is crucial: COT gives us a **mathematical definition of autopoiesis** as closure + self-maintenance. Our H5 (autopoiesis persistence) and H6 (multi-scale autopoiesis) can be operationalized: a trace structure crosses from passive trace to autopoietic actor when it satisfies closure + self-maintenance.

### 2. COT naturally produces hierarchies

Organizations contain **suborganizations** — subsets that can autonomously self-sustain while exchanging resources with other subnetworks. A suborganization S can be summarized as a higher-order reaction:

S + In(S) → S + Out(S)

This means S behaves like a **higher-order agent** (superagent): it processes inputs into outputs while maintaining itself. The larger organization can be embedded in further networks, defining agents of even higher order. Heylighen (2024) explicitly notes this "opens the door to the modeling of the dynamical hierarchies and metasystem transitions that characterize the multilevel self-organization that we see in the evolution of life and society."

**This is the formalism for multi-scale composition we've been looking for.** Suborganizations = new-level actors. The hierarchy of organizations = the multi-scale structure. The crossing from subnetwork to organization = our trace→actor crossing (H7).

### 3. COT is agentless by design

Agents emerge as **catalysts** — resources that appear on both sides of reactions (a + b + c → a + d). The agent enables the reaction without being consumed. An agent's "skill set" is its set of catalyzed reactions (condition-action rules). Agents are not pre-defined; they emerge from the network structure.

This aligns with ANT's anti-essentialism: actors are defined by their relationships (reactions), not intrinsic properties. An agent IS the set of reactions it catalyzes. Change the reactions, change the agent.

### 4. Resilience, degeneracy, and evolvability

Organizations exhibit resilience through:
- **Buffering**: overproduction of crucial resources
- **Negative feedback**: deviations from equilibrium are automatically counteracted
- **Feedforward**: dormant neutralizers activated by disturbances
- **Degeneracy**: multiple independent pathways perform the same function — loss of one is compensated by others
- **Evolvability**: the system can shift between overlapping organizations (sideward shifts = add resources + remove resources)

Under continuing perturbations, systems shift between **clusters of related attractors** — overlapping organizations that share most resources. This is higher-order evolution: the organization changes while maintaining continuity of identity.

### 5. Competition and cooperation are emergent

Resources can inhibit or promote each other through shared reactions. Promotion: a enables a reaction that produces b. Inhibition: a enables a reaction that consumes b without producing it. Cycles of positive/negative influence create the ecological relationships (mutualism, competition, predation, commensalism) that structure the organization.

## Relevance to Our Project

### COT ↔ Our multi-scale composition thesis (H1)

COT provides the **mathematical formalism** for multi-scale composition. The hierarchy of organizations within organizations IS multi-scale structure. The crossing from subnetwork to organization IS the multi-scale phase transition. Our H1 (composition hypothesis) can be restated in COT terms: ALife simulations stall because they lack the reaction network structure that produces nested organizations.

### COT ↔ Trace→actor crossing (H7)

The trace→actor crossing is the transition from accumulated stigmergic traces to a self-maintaining organization. In COT terms:
- Stigmergic traces are resources deposited in the medium
- The trace→actor crossing occurs when the set of traces + agents + reactions satisfies closure + self-maintenance
- The crossing IS the convergence to an organization attractor

This makes H7 formally testable: we can check whether a set of traces satisfies the closure and self-maintenance conditions.

### COT ↔ Stigmergy

Stigmergic coordination is agentless coordination through environmental modification. COT is inherently agentless — coordination emerges from reaction network structure. The stigmergic medium is the "reaction vessel." Traces are resources. The stigmergic feedback loop (action → trace → stimulation → action) is a reaction cycle. COT can formalize stigmergic systems as reaction networks where the medium's resources are both inputs and outputs of reactions.

### COT ↔ ANT

ANT's actors are defined by relationships. COT's resources are defined by the reactions they participate in. ANT's translation (problematization → interessement → enrollment → mobilization) could be formalized as the self-organization process (resource addition → closure → resource removal → self-maintenance). The "enrollment" of actors into a collective is the convergence to an organization. The "mobilization" as one actor is the suborganization acting as a superagent.

### COT ↔ Autopoiesis (H5, H6)

COT formalizes autopoiesis as closure + self-maintenance. This makes our autopoiesis hypotheses testable. Multi-scale autopoiesis (H6) = nested organizations. The condition for H6 is that suborganizations exist within larger organizations, and that the suborganizations satisfy closure + self-maintenance independently.

### COT ↔ Quasi-objects (H3)

Resources in COT are transformed by the reactions they participate in — they are consumed and produced. This is the quasi-object property: the resource is co-determined with its carriers. A fixed-value resource (food pellet) would be represented as a resource that appears only in reaction outputs (produced but never transformed). A quasi-object resource appears in both inputs and outputs of different reactions — it circulates AND is transformed.

## Criticisms and Limitations

### 1. Autocatalytic sets lack evolvability (Vasas et al., 2010)

Vasas, Szathmáry & Santos (2010, PNAS) showed that self-sustaining autocatalytic networks (a special case of COT organizations) **lack evolvability**. They cannot undergo Darwinian evolution because the organization's identity is not heritable — small perturbations don't produce variant organizations that can be selected. This is the same stall as EvoLoop and computational autopoiesis: self-maintenance without evolution.

This is a critical limitation: COT organizations are self-maintaining but may not be **evolvable**. The missing ingredient is the ability to produce variant organizations that can compete. This connects to our H8 (computational complexity enables open-endedness): evolvability requires that the space of possible organizations is large enough that selection can explore it.

### 2. Hierarchy construction is informal

Heylighen (2024) notes that the construction of dynamical hierarchies from suborganizations is sketched but not fully mathematically developed. "While we still need to investigate this construction mathematically, this appears to open the door to the modeling of the dynamical hierarchies." The hierarchy is a promising direction, not a proven result.

### 3. Topology must be imposed by the modeler

COT assumes all resources interact in a single "reaction vessel." Introducing spatial structure requires labeling resources with cell indices (imposed by the modeler) or assuming that non-overlapping suborganizations are spatially separated (informal). The self-organization of spatial structure from reaction dynamics is an open problem. Heylighen acknowledges: "a more elegant approach is to view non-overlapping suborganizations as spatially separated... The advantage of such a construction is that the 'cells' would self-organize out of the network of reactions, instead of being imposed by the modeler" — but this remains future work.

### 4. Computational complexity

Finding all organizations of a reaction network is potentially exponential (every subset of resources could be an organization). Veloz et al. developed decomposition methods, and the problem is equivalent to Linear Programming for checking a given set, but the full enumeration remains expensive for large networks.

### 5. COT organizations may still be single-scale

While COT defines hierarchies of organizations, each organization operates under the same reaction rules. The reactions don't change across scales. True multi-scale composition requires that each scale has **fundamentally different interaction rules** (our thesis). COT's hierarchy is nested, but the rules are the same at each level. Whether COT can produce qualitatively different rules at different levels is an open question.

### 6. No built-in evolution mechanism

COT describes the attractors of a fixed reaction network. It doesn't describe how the reaction network itself evolves. For open-ended evolution, the set of reactions R must itself change over time (new reactions appear, old ones disappear). COT needs an extension to handle evolving reaction networks.

## Empirical Evidence

### COT applied to biological systems
- **HIV-immune system interaction** (Wodarz & Nowak model): organizations uncovered that correspond to functional states (Dittrich & di Fenizio, 2007)
- **E. coli sugar metabolism** (Puchalka & Kierzek model): large-scale analysis found organizations corresponding to metabolic functions
- **Cell cycle models**: Henze et al. (2019) applied multi-scale organization-oriented coarse-graining to the human mitotic checkpoint. Peter et al. (2024) explored persistent subsystems in 414 cell cycle models.

### COT applied to origin of life
- Hordijk & Steel (2018): COT as framework for modeling self-sustaining reaction networks at the origin of life. Autocatalytic sets are a special case of COT organizations.
- Peng et al. (2022): hierarchical organization of autocatalytic reaction networks, showing seed-dependent autocatalytic systems (SDAS) can self-maintain given food flux.

### COT resilience simulations
Veloz et al. (2022): computer simulations of randomly generated reaction networks settling into organizations and subjected to perturbations. Found systems shift between clusters of related attractors (overlapping organizations). This is the primary empirical evidence for COT's self-organization claims.

### No empirical evidence for multi-scale COT
The hierarchy of organizations (suborganizations as superagents) is proposed theoretically but has not been empirically demonstrated in simulations. This is the gap our project could address.

## Cross-References

- [[concepts/autopoiesis]] — COT formalizes autopoiesis as closure + self-maintenance
- [[concepts/multi-scale-composition]] — COT hierarchies provide the formalism for multi-scale composition
- [[concepts/stigmergy]] — Stigmergic coordination is agentless coordination; COT is inherently agentless
- [[concepts/echo-model]] — Echo failed to produce hierarchical aggregates; COT explains why (no organization structure)
- Dittrich & di Fenizio (2007) — original COT paper
- Heylighen, Beigi & Veloz (2024) — comprehensive review and generalization
- Peter & Dittrich (2011) — organizations as attractors theorem
- Vasas et al. (2010) — criticism: autocatalytic sets lack evolvability
- Veloz et al. (2022) — resilience simulation framework
