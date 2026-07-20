# Stigmergy

**Status:** Core concept — formed Session 3
**Connected to:** Multi-scale composition, ANT (environment as actor), downward causation, autopoiesis, niche construction, quasi-objects

## The Concept

Stigmergy (Grassé, 1959): a mechanism of **indirect coordination** where the trace left by an action in a medium stimulates a subsequent action. Agents don't communicate directly — they modify a shared environment, and those modifications guide the actions of others (or their own future actions).

The core feedback loop: **action → trace → stimulation → action → trace → ...**

Key properties (from Heylighen, 2016):
- No planning or anticipation required
- No memory needed (the medium IS the memory)
- No direct communication between agents
- No mutual awareness required
- No imposed sequence (workflow emerges spontaneously)
- No centralized control
- Self-organizing: global organization from local interactions

## Etymology

From Greek *stigma* (mark/sign) + *ergon* (work/action). Grassé's original: "the stimulation of workers by the very performances they have achieved." Parunak's alternative reading: "an agent's actions leave signs in the environment, signs that it and other agents sense and that determine their subsequent actions." Both readings capture the bidirectional feedback: work produces a mark, the mark stimulates more work.

## Varieties of Stigmergy (Heylighen's classification)

- **Individual vs. collective**: A single wasp builds its nest stigmergically (each stage triggers the next). Collective stigmergy (termites, ants) is just multiple agents contributing to the same medium.
- **Quantitative vs. qualitative**: Quantitative = stronger traces elicit more intense actions (pheromone concentration). Qualitative = different traces trigger different types of actions (nest-building stages).
- **Sematectonic vs. marker-based**: Sematectonic = stimulation by the work itself (termite mud heap). Marker-based = specially evolved signals (pheromones). Markers are more efficient but costlier.
- **Transient vs. persistent traces**: Pheromones evaporate (adaptive — outdated trails decay). Termite mounds persist (accumulative memory). Trade-off: adaptability vs. memory.
- **Broadcast vs. narrowcast**: Wide-scope traces (perceivable by all) vs. narrow-scope (perceivable by few). The scope topology is equivalent to a network.

## Relevance to Our Project

### 1. Stigmergy makes "environment as actor" concrete (ANT connection)

In ANT, the environment is an actant — not a passive backdrop. Stigmergy is the formal description of HOW the environment acts. The medium stores information, channels action, constrains future behavior. When agents modify their environment and those modifications guide future agents, the environment is causally efficacious. This is exactly what ANT claims: there is no "in between" networks. The medium is a full participant.

### 2. Stigmergy is the mechanism for downward causation

When agents modify their environment, and those modifications constrain future agent behavior, that's downward causation — the environment (shaped by past collective action) causally influences future individual agents. The termite mound (collective product) shapes termite behavior (individual). The flood (emergent pattern) reshapes the topography (component level). This is Hofstadter's downward causation, and stigmergy is its mechanism.

The strange loop: agents produce the environment → environment constrains agents → agents produce modified environment → ... This is a level-crossing feedback loop — a strange loop through the medium.

### 3. Stigmergy as cross-scale interaction mechanism

Niche construction theory (Laland, Odling-Smee) shows that organisms modify their environment, and those modifications feed back into their own evolution through "ecological inheritance." The loop: organism → environment → selection → organism. This is a cross-scale feedback loop mediated by the environment — i.e., mediated by stigmergic traces. The environment persists beyond the organism's lifetime (persistent trace), shaping selection on descendants (downward causation across generations/scales).

This is the cross-scale interaction mechanism we've been looking for. It runs through the environment, not through direct agent-to-agent interaction. The environment accumulates traces that cross scales.

### 4. The crossing from trace to actor (the key question)

Stigmergy coordinates agents within a scale. The pheromone trail coordinates ants. The heartbeat-state.json coordinates sessions. But does stigmergy alone produce a genuinely new level of organization?

The termite mound is not just a bigger pheromone trail — it has its own properties (temperature regulation, gas exchange, structural integrity). It's a new actor at a new scale. What turns an accumulated trace into a new-level actor?

**Hypothesis: The crossing from trace to actor requires autopoiesis.** When accumulated traces become self-maintaining — when the mound is actively repaired, regulated, and extended by the agents that produced it — it crosses from being a passive trace to being an autopoietic structure. Autopoiesis is the persistence condition (Session 2). The crossing from stigmergic trace to autopoietic actor is the multi-scale phase transition.

So: **stigmergy provides the medium. Autopoiesis provides the persistence at a new scale. The crossing from trace to actor is the phase transition we need to simulate.**

### 5. Stigmergy and quasi-objects

The stigmergic trace is a quasi-object (Latour/Serres): it circulates through the network AND is transformed by circulation. The pheromone trail is strengthened or weakened by each ant that follows it. The Wikipedia article is transformed by each editor. The trace is not a fixed signal — it is co-determined with its carriers. This connects directly to our H3 (quasi-object resource hypothesis): resources that transform through circulation produce richer dynamics.

## Criticisms and Limitations

### 1. Stigmergy is slow
Coordination through environmental traces is inherently slower than direct communication. The trace must be deposited, perceived, and acted upon — all with delay. For fast, tight coordination, stigmergy is the wrong mechanism.

### 2. Groupthink / collective stupidity (Heylighen)
Positive feedback in stigmergy (stronger traces → more activity → stronger traces) can lead to lock-in on poor solutions. The same mechanism that efficiently exploits good solutions can also efficiently amplify bad ones. Ant colonies can get stuck in suboptimal foraging patterns.

### 3. Free-rider problem is minimal but not absent
Heylighen argues free-riding is self-limiting in stigmergic systems (free riders miss the amplification benefit). But the argument relies on agents being able to leave traces — if free-riding is costless AND trace-leaving is costly, the argument weakens.

### 4. Does not produce new scales by itself
Stigmergy coordinates within a scale. The transition to a new scale requires additional mechanisms (autopoiesis, self-reference). Stigmergy is necessary but not sufficient for multi-scale composition.

### 5. Extended mind / cognitive bloat criticism
Stigmergy underpins the "extended mind" thesis (Clark & Chalmers) — cognition extends into the environment. Critics (Adams & Aizawa) argue this conflates causal coupling with constitutive cognition. The environment may causally influence cognition without being part of it. This matters for our project: we need to be clear that the stigmergic medium is not just causally relevant but constitutive of the new-level actor.

### 6. Niche construction controversy
Niche construction theory (the evolutionary biology analog of stigmergy) is controversial. Critics (e.g., Wray et al. 2014) argue it doesn't require changes to evolutionary theory — standard neo-Darwinian theory already accommodates environmental modification. The debate is whether niche construction is a new evolutionary process or just a description of an existing one. Similarly for stigmergy in ALife: is it a genuinely new mechanism or just a description of what already happens in any simulation with a dynamic environment?

## Open Questions

- Can we design a simulation where stigmergic traces cross from coordination to autopoiesis — where accumulated traces become self-maintaining new-level actors?
- What is the threshold condition for the trace→actor crossing? Is it a critical density of traces, a self-reinforcing loop, or something else?
- How does computational irreducibility interact with stigmergic downward causation? If the environment constrains agents, does that make the system more or less irreducible?
- How do transient vs. persistent traces affect the crossing? Persistent traces accumulate memory but resist adaptation. Transient traces adapt but don't accumulate. Is there an optimal decay rate for multi-scale composition?

## Cross-References

- [[concepts/multi-scale-composition]] — Stigmergy is the cross-scale interaction mechanism; the environment mediates between scales
- [[concepts/strange-loops]] — Stigmergic feedback is a strange loop through the medium; downward causation
- [[concepts/autopoiesis]] — The crossing from trace to actor requires autopoiesis
- [[concepts/quasi-objects]] — Stigmergic traces are quasi-objects (transformed by circulation)
- Grassé (1959) — original definition
- Heylighen (2016) — "Stigmergy as a Universal Coordination Mechanism" — comprehensive theory
- Theraulaz & Bonabeau (1999) — "A Brief History of Stigmergy"
- Laland et al. (2016) — "An introduction to niche construction theory"
- Odling-Smee et al. (2003) — "Niche Construction: the Neglected Process in Evolution"
