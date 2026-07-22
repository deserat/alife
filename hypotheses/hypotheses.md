# Hypotheses

All hypotheses for the artificial life simulator project. Each hypothesis is testable through simulation. Hypotheses are refined across sessions as new evidence accumulates.

---

## H1: The Composition Hypothesis

**ALife simulations stall because they lack multi-scale composition.** Emergent structures at one scale must interact to produce qualitatively new phenomena at another scale, where actors and interaction rules are fundamentally different. Without this, simulations converge to simple stable states.

**Refinement (Session 3):** The cross-scale interaction mechanism is stigmergy. Agents modify their environment (stigmergic traces), and those modifications persist and constrain future agents. The environment mediates between scales.

**Refinement (Session 4):** Smith & Bedau (1997) independently confirmed this hypothesis through empirical study of Echo. They found Echo lacks "the diversity of hierarchically organized adaptive aggregates" and proposed that the missing CAS property is "robust, open-ended emergence of hierarchical, adaptive structures."

**Test:** Build a simulation with explicit multi-scale composition mechanisms and compare to single-scale baseline. Measure: does the multi-scale version produce open-ended dynamics where the single-scale version stalls?

---

## H2: The ANT Translation Hypothesis

**ANT's translation (Callon's four moments) provides the computational primitives for phase transitions between scales.** Problematization → interessement → enrollment → mobilization maps to: pattern formation → attraction → collective formation → collective action as one. When a cluster of actors reaches threshold interaction density, they undergo enrollment and mobilize as a new actor at a higher scale.

**Status:** Unchanged. Still untested.

---

## H3: The Quasi-Object Resource Hypothesis

**Resources that transform through circulation (quasi-objects) produce richer dynamics than fixed-property resources.** A pheromone trail that strengthens/weaken with use is a quasi-object. A fixed-value food pellet is not.

**Refinement (Session 3):** Stigmergic traces are quasi-objects by definition — they are transformed by circulation. This provides independent support from the stigmergy literature.

**Support (Session 4):** Echo's trading resource behaves as a partial quasi-object — more copies of the traded resource in a genome change the population dynamics. But Echo's resources don't transform through circulation in the full Latourian sense.

**Test:** Compare simulations with fixed-value resources vs. quasi-object resources (resources that change properties as they circulate).

---

## H4: The Dynamic Environment Hypothesis

**The environment must be a stigmergic medium — both perceivable and modifiable.** Not just dynamic, but a participant in a stigmergic feedback loop. The environment stores information (trace), channels action (stimulation), and constrains future behavior.

**Refinement (Session 4):** The fitness landscape must be DYNAMIC — agents modify the landscape they're adapting to. Static landscapes (NK model, Echo) cannot produce multi-scale composition. Niche construction makes landscapes dynamic in biology; stigmergy makes them dynamic in simulation.

**Test:** Compare agents on static vs. dynamic fitness landscapes. The dynamic landscape is modified by agent behavior (stigmergic traces change the fitness function).

---

## H5: The Autopoiesis Persistence Hypothesis

**For an emergent structure to persist as a new actor at a higher scale, it must be autopoietic — it must maintain the network that constitutes it.** Self-maintenance is the persistence condition. Without it, emergent structures are transient patterns, not new actors.

**Status:** Unchanged. Theoretical grounding from Maturana & Varela.

---

## H6: The Multi-Scale Autopoiesis Hypothesis

**Complexification occurs when autopoietic systems interact stigmergically — through environmental modifications that persist and constrain.** The interaction network itself (mediated by stigmergic traces) becomes a candidate for higher-level autopoiesis.

**Refinement (Session 4):** Smith & Bedau's proposed 8th CAS property — "the ability of emergent interacting components to create and flexibly maintain their own boundaries" — is autopoiesis. They identified it independently from a different starting point (empirical study of Echo vs. our ANT/stigmergy path). This is strong corroboration.

---

## H7: The Trace→Actor Crossing Hypothesis

**Multi-scale composition occurs when accumulated stigmergic traces cross from passive coordination to autopoietic self-maintenance.** The crossing requires: (1) sufficient trace density, (2) self-reinforcing feedback (agents maintain the traces that constrain them), (3) the trace structure developing properties not reducible to individual traces.

**Refinement (Session 4):** This IS Smith & Bedau's 8th CAS property. Stigmergy provides the mechanism for "creating boundaries" (traces that accumulate). Autopoiesis provides the mechanism for "flexibly maintaining boundaries" (self-production). The crossing from trace to actor is the phase transition they identified but never implemented.

**Test:** Build a simulation where agents leave persistent traces, and observe whether traces cross from coordination to self-maintenance. Measure: does the trace structure develop its own dynamics? Does it resist perturbation (self-repair)? Does it constrain agent behavior in ways not derivable from individual traces?

---

## H8: The Computational Complexity Enables Open-Endedness Hypothesis (NEW — Session 4)

**Computational irreducibility at each scale is a NECESSARY condition for open-ended evolution.** On easy (computationally reducible) landscapes, evolution finds optima quickly and stops. On hard (computationally irreducible) landscapes, evolution cannot find optima and keeps searching — this IS open-endedness.

**Evidence:** Kaznatcheev (2019) proved that NK landscapes with K > 1 are PLS-complete — even local optima cannot be found in polynomial time. Wiser et al. (2013) showed E. coli fitness grows by power law (not exponential), consistent with hard landscape dynamics. Kaznatcheev argues this computational constraint ENABLES unbounded fitness growth.

**Implication for multi-scale composition:** Each scale in a multi-scale ALife simulation must have computationally irreducible dynamics. Cross-scale interactions must PRESERVE this irreducibility — if one scale becomes computationally reducible (e.g., agents find the optimal strategy), the system converges and stalls. The multi-scale structure must maintain irreducibility at all scales simultaneously.

**Test:** Compare simulations with reducible vs. irreducible dynamics at each scale. Measure: does the irreducible version produce open-ended dynamics where the reducible version converges?

---

## H9: The Evolving Network Hypothesis (NEW — Session 5)

**A reaction network that generates new reactions (evolving network) can produce evolvable organizations where a fixed reaction network (same initial conditions, no new reactions) converges to a single static organization and stalls.** The key mechanism is the appearance of novel viable autocatalytic cores via rare uncatalyzed reactions, combined with compartmentalization that enables selection between cores.

**Evidence:**
- Vasas et al. (2010, PNAS): Autocatalytic sets (fixed networks) lack evolvability — they converge to a single attractor and cannot depart from the steady-state built into the dynamical equations.
- Vasas et al. (2012, Biology Direct): When rare uncatalyzed reactions are allowed, novel viable cores appear (5/460 runs). Multiple cores create multiple attractors with different growth rates, enabling natural selection. A 1% selective advantage shifts population composition.
- Our sim03 confirmed: fixed reaction network converges immediately (by generation 1) and never changes for 3000 generations.
- Fontana & Buss (1994): Lambda calculus chemistry (AlChemy) produces "organizational transitions" — shifts between qualitatively different organizational regimes — when new molecules appear as products of reactions.

**Connection to H7:** The appearance of a novel viable core IS the trace→actor crossing. Existing resources are traces; the novel reaction produces a new self-maintaining set (organization/actor) from them.

**Connection to H8:** You cannot predict which novel cores will appear — you must simulate. The space of possible reactions is too large to enumerate, and viability depends on the entire network state.

**The "one bit" limitation:** A single viable core carries ~1 bit of heritable information (present/absent). Open-ended evolution requires unlimited heritable information. The evolving network extends the "adjacent possible" — each new core opens new reaction possibilities — but whether this produces true open-endedness or just limited multi-attractor dynamics is an open question.

**Test:** Compare fixed network (no new reactions, sim03-like) vs. evolving network (new reactions appear) with compartmentalization. Measure: does the evolving network discover new species, new organizations, and maintain between-compartment diversity where the fixed network converges?

---

## Summary Table

| Hypothesis | Status | Evidence |
|---|---|---|
| H1: Composition | Refined | Smith & Bedau (1997) independent confirmation; sim03 COT confirms fixed networks stall |
| H2: ANT Translation | Unchanged | Theoretical, untested |
| H3: Quasi-Object | Strengthened | Stigmergy literature support; Echo partial support |
| H4: Dynamic Environment | Refined | Fitness landscape criticism supports this |
| H5: Autopoiesis | Unchanged | Maturana & Varela grounding |
| H6: Multi-Scale Autopoiesis | Strengthened | Smith & Bedau 8th property = autopoiesis |
| H7: Trace→Actor Crossing | Strengthened | Smith & Bedau 8th property = stigmergy + autopoiesis; COT gives formal test |
| H8: Complexity Enables OEE | NEW | Kaznatcheev (2019), Wiser et al. (2013) |
| H9: Evolving Network | NEW | Vasas et al. (2012), sim03 negative result, sim04 testing |
