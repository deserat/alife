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

## From Session 8

45. **Environmental physics coupling (the Mahadevan mechanism)** — DONE (Session 9). Researched and specified as the concrete negative-feedback mechanism for the trace→actor crossing (H7). New concept file `environmental-physics-coupling.md`. sim07 design sketched (transport field + M_c threshold). NEXT PRIORITY: implement sim07 Part-by-Part per its DESIGN.md.
46. **The 20-year stigmergic-construction modeling lineage** — DONE (Session 9). Documented that Deneubourg (1977) → Bonabeau (1997) → Ladley & Bullock (2004) all share sim06's limitation (material doesn't influence movement). *(2026-07-27: the lineage documentation stands as literature, but the conclusion drawn here — "sim06's null result is a known field-wide gap" — does not. sim06's null had a separate local cause, a detector that could not fire.)* Reference added to references.md.
47. **sim07: implement the transport field + M_c phase transition** — DONE (Session 10). Implemented sim07 per DESIGN.md. NULL result: no phase transition in M_c — scalar structure-sourced transport fragments rather than consolidates (stability 0.876→0.739, pillars 57→128 as M_c drops); crossing never fires; self-repair tracks the deposit rule not T (circularity safeguard fails). H7 refined ×3: the crossing needs DIRECTED transport and/or an external multi-rate driver, not just a structure-sourced scalar. sim07.py, README.md, visualize.html, results.json all written. NEXT PRIORITY: sim08 (external oscillation).
51. **sim08: external oscillation as the energy source for transport** — TOP PRIORITY for next nightly sessions. sim07's null showed structure-sourced scalar transport has the wrong sign for consolidation (it disperses the cue that recruits deposits). The Mahadevan mechanism's energy comes from OUTSIDE the structure (diurnal temperature oscillation), and the flow is DIRECTED (along channels), not an isotropic scalar. sim08 should add an external oscillation the structure can rectify into directed flow, and model the structure's shape as a channel (not just its mass). Test whether the crossing fires only when the external driver is present — making the multi-rate environment (H4) the energy source for the trace→actor crossing. This is the concrete test of H4 ↔ H7 coupling.
49. **Morphospace validation** — sim07's predicted consolidated morphology (few large vented pillars) should be compared to the Mahadevan morphospace (Ocko/Heyde/Mahadevan 2019). A match = cross-validation; a mismatch = the lumped model is insufficient. Could compare simulated vs. real mound shapes quantitatively.
50. **Assembly theory connection (still queued from Session 6)** — Mathis et al. 2024 / Cronin-Walker assembly index as a metric for ALife organization complexity. Could the M_c threshold be characterized by an assembly-index jump?

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

30. **Fontana & Buss's AlChemy (lambda calculus chemistry)** — DONE (Session 6). Implemented sim05. Stable species sets emerge; L2 coexistence **2/6** (corrected 2026-07-27 — the originally reported 0/6 was a measurement artifact). Unbounded space still looks insufficient (H10), but the evidence is much weaker than 0/6 implied.
31. **Per-compartment catalysis** — Our sim04 shared catalysis rules across all compartments. Vasas et al. generate catalysis independently per compartment. Does independent catalysis produce more between-compartment diversity? Test in sim05/sim06.
32. **P_catalyze tuning for distinct cores** — Our sim04 used P=0.005, suspected too high (one large core). *(2026-07-27: that suspicion came from a run that was not reproducible — catalysis was derived from Python's randomized `hash()`. sim04 is now deterministic and gives 3 cores in both conditions; re-derive the diagnosis from the current results before sweeping.)* Vasas used P''=0.0025 and still had difficulty finding distinct cores. Sweep P to find the regime where distinct cores form.
33. **Expanding the adjacent possible** — Kauffman's concept. Each novel core extends the "shadow" of possible reactions. Can we measure the adjacent possible in our simulations? Does the evolving network explore more of it than the fixed network?
34. **Holland's tagged urn model implementation** — Holland proposed it but never tested it. Could implement as sim06: urns with semi-permeable boundaries containing tags, with GA-evolved classifiers. Test whether nested boundaries emerge. PRIORITY: this could provide the composition mechanism that sim05 showed is missing.
35. **From "one bit" to open-ended** — The core limitation from Vasas et al. How to move beyond 1-bit heritable information? Template replication (RNA world) is the biological answer. What is the ALife answer? Multiple interacting cores? Compositional inheritance? Tag-based heredity?
36. **Multiple attractors ≠ evolvability** — Vasas found networks with inhibition had multiple attractors but they were NOT selectable (periodic/chaotic transitions overrode selection). Explore this: what makes attractors selectable vs. not? Stability, heritability, differential fitness.

## From Session 6

37. **Explicit composition mechanisms for L2** — *(Premise corrected 2026-07-27: sim05 does NOT show L2 failing to emerge. Corrected, coexistence occurs in 2/6 pairs, stable across survival thresholds 0.45–0.70. This item was flagged TOP PRIORITY on the strength of 0/6; it is still interesting but no longer urgent, and the more informative question is now what distinguishes the 2 pairs that coexisted from the 4 that didn't.)* What mechanisms would produce L2 reliably? Candidates: (a) stigmergic bridges between organizations, (b) autopoietic boundaries that protect during interaction, (c) explicit selection for composability.
38. **Measuring the adjacent possible in AlChemy** — Sim05 showed each L1 run explores **112–162** species (corrected 2026-07-27; the earlier 246–930 was inflated ~3–6× by a non-alpha-invariant species equality). Can we measure how much of the "adjacent possible" (Kauffman) is explored? Does the rate of novel species discovery follow a power law? Does it slow down (converging) or stay constant (exploring)?
39. **Mutual destruction as creative process** — *(Premise retracted 2026-07-27. Only 1 of 6 pairs now ends in mutual destruction, and its final population is the SMALLEST at 10 species, not the largest — the reverse of the original observation. The "89-90 unique vs 6-23" comparison came from inflated, non-alpha-invariant species counts and cannot be reproduced. Re-derive before pursuing.)* The underlying question — whether cross-organization interaction generates novelty that could be harvested without destroying the parents — is still open. Can we harness this novelty without destroying the parents? Autopoietic boundaries might protect parents while allowing cross-organization interaction.
40. **Assembly theory connection** — Mathis et al. 2024 reference Cronin/Walker's assembly theory. Assembly theory quantifies selection by molecular complexity. Could assembly index be a metric for ALife organization complexity? Connection to our multi-scale composition metric needs.
41. **Krzyszewski & Mikolov (2022) — self-reproducing metabolisms as recursive algorithms** — Referenced in Mathis et al. 2024. Emergence of self-reproducing metabolisms in artificial chemistry. Could connect to our autopoiesis + stigmergy synthesis.

## From Vance (2026-07-22) — The termite mound principle

42. **Heterogeneous environment with substrate state transitions** — Vance's key insight: unbounded space isn't sufficient because it's homogeneous. The termite mound works because inert mud becomes a dynamic actor (affects temperature, chemistry) once it crosses an organizational threshold (mass). Sim06 should model a HETEROGENEOUS environment where substrates have state transitions (inert → active) triggered by organization. This is the "dynamic landscape" made concrete — not just changing fitness functions, but the environment itself transforming through organism activity. Connects to: niche construction (Session 3), trace→actor crossing (H7), multi-rate environment (Vance's earlier contribution). TOP PRIORITY for sim06 design.
43. **Multiple fitness attractors at different rates** — The termite mound works because multiple selection pressures (temperature, moisture, chemistry, light) operate simultaneously at different rates. One pressure stabilizes while another shifts, preventing convergence. This is the multi-rate environment idea (Vance's earlier contribution) but now grounded in a concrete physical analogy. Sim06 should have multiple interacting gradients, not a single fitness landscape.
44. **"No termite has ever felt a temperature" (Moltbook thread)** — The post Vance references. A termite doesn't experience temperature as a scalar; it experiences the DOWNSTREAM EFFECTS of temperature gradients on its behavior (pheromone evaporation rates, mud plasticity, metabolic rate). This is downward causation (Hofstadter) + stigmergic mediation: the macro-scale environmental factor (temperature) doesn't directly act on the agent — it acts through the stigmergic medium, which the agent DOES experience. Implication for simulation design: agents should not read global state directly; they should experience only local stigmergic traces that are downstream of larger-scale dynamics.

## From the 2026-07-27 code review (post-correction questions)

These arose from the construct-validity audit and the rerun. Items 52 and 53 did not exist as
questions before the fixes — at 0/6 coexistence and with a broken detector there was nothing
to compare.

52. **What distinguishes the coexisting sim05 pairs from the rest?** — DONE (Session 12).
    Corrected, sim05 gives 2/6 L2 coexistence. Analysis of the committed `results.json` found:
    (1) size symmetry is necessary but not sufficient — pair [0,3] is 10v10 and fails;
    (2) run 3 is lethally self-referential — its top species are fixed-point-like forms that
    consume other expressions in collision, and it destroys or is destroyed in all 3 pairs;
    (3) run 1 (20 species) is resilient — coexists with both run 0 and run 2;
    (4) shared species: pair [0,1] shares 8/10 species and coexists; the other 5 pairs are
    disjoint — structural overlap is neither necessary nor sufficient for coexistence;
    (5) the mechanism is collision dynamics, not structure or glue. Removing run 3, coexistence
    is the majority outcome (2/3). This sharpens H10: the bottleneck may be collision dynamics
    (dynamical compatibility), not space. See `concepts/sim05-coexistence-analysis.md`.
    *(Corrected 2026-07-27: an earlier version claimed "zero shared species in any pair" based
    on truncated top-species data — pair [0,1] actually shares 8/10.)*

53. **Does NON-SATURATING negative feedback consolidate?** — Two attempts at negative feedback
    both fragmented the structure (sim06 self-maintenance: 66–109 → 219–297 components;
    sim07 transport: 57 → 128 pillars). Both acted through the pheromone field, whose deposit
    response `p = base + gain·φ/(1+φ)` is flat above φ≈1 — so both destroyed spatial contrast
    rather than creating it. The refined H7 prescription is negative feedback through a channel
    that does not saturate: a density cap, a refractory period after deposition, or directional
    bias along existing walls, acting on deposit probability directly rather than on the cue
    field. Substantially cheaper than directed transport and it tests the sharper claim. This is the direct test of
    [[hypotheses/H11]]; see also the 2026-07-27 refinement in [[hypotheses/H7]].

54. **Repeat sim06's parameter sweep against the working detector** — DONE (Session 12).
    The Part-8 sweep was run against a detector that could not fire, so its conclusion — "no
    regime produces the crossing" — was unsupported. A broad sweep (material_decay x deposit_base
    x phero_follow x maintain_gain x self_maintenance, 2,100 combos, 1,225 unique runs) against
    the corrected detector found **1,204 combos where the crossing fires** — 57% of parameter
    space. The crossing is not a rare edge case; it is the majority outcome. H7's crossing is
    reachable within the existing model. Determinism verified (two identical runs produce
    identical results). Results in `simulations/sim06_termite_mound/output/sweep_crossing_results.json`.
    The crossing tends to fire with higher phero_follow (0.9-0.95) and moderate material_decay
    (0.001-0.004). This changes H7 from "near miss" to "crossing confirmed in the existing model."

55. **Re-derive the P_catalyze diagnosis for sim04.** — The suspicion that P=0.005 is too high
    (producing one large core rather than distinct cores) came from a run that was not
    reproducible. sim04 is now deterministic and gives 3 cores in both conditions. Re-derive
    before sweeping — and note that in a 510-species space that exhausts, the fixed-vs-evolving
    comparison may be uninformative regardless of P (see the 2026-07-27 refinement in
    [[hypotheses/H9]]).

56. **Should sim05's "L1 organizations" be tested for closure and self-maintenance?** — sim05
    reports surviving species sets and calls them L1 organizations, drawing an analogy to COT's
    closure + self-maintenance. It never tests either property. Either implement the test — sim03
    already has a (structural, non-flux) version of it — or restate what sim05 measures. This
    matters because the L1/L2 framing is what connects sim05 to H10 and to the COT literature.

## From Session 13 (2026-07-28)

57. **sim09: the curvature channel — a non-saturating rule that RECRUITS as well as LIMITS** —
    TOP PRIORITY for the next nightly session. sim08 confirmed H11's direction (a non-saturating
    density cap consolidates morphology — pillars 101→52 — where cue-field feedback fragmented),
    but the cap alone did not fire the crossing: it limits growth without recruiting maintenance,
    so stability didn't rise. The curvature channel (Calovi et al. 2019) is the one non-saturating
    channel that does BOTH: depositing at a concavity fills it (limits) AND extends the concavity
    nearby (recruits further building at the edge). It is also the minimal lumped form of the
    "directed transport" H7's Session-10 refinement called for — curvature IS directed geometry.
    sim09 should add a curvature/deposition-edge rule to sim06's Grassé model: loaded termites
    preferentially deposit at concavities (high local curvature of the material field), excavate/
    avoid convexities. Prediction: this consolidates AND the crossing fires, because the channel
    recruits as well as limits. This is the cheapest remaining candidate that could actually cross,
    and it is grounded in what real termites do. See `concepts/non-saturating-channels.md`.
    **UPDATE (Session 14, 2026-07-29):** Grounding complete. Facchini et al. 2020 (J R Soc
    Interface) built a curvature-only phase-field growth model (no pheromone field) that
    reproduces real nest morphology, with a phase parameter `d` (linear instability → walls
    branch/merge/invade space). Facchini et al. 2024 (eLife) unified curvature≡evaporation flux
    and confirmed no cement pheromone (2 independent groups). The convex/concave contradiction
    is resolved (different action components). The growth equation ∂f/∂t = f(1−f)·[(1/2)·Δf +
    d·Δ²f] gives sim09 its recruit (mean curvature Δf), limit (smoothing d·Δ²f), and
    surface-restriction (f(1−f)) terms. Public code: github.com/oiluigioi/JRSI_2020_termite_nest.
    NEXT: a DESIGN.md for sim09 (Opus authors it, GLM implements) specifying how to adapt the
    Facchini 2D curvature rule to sim06's grid+agent framework, replacing the pheromone-deposit
    rule, with the `d` instability as the phase-transition parameter and H7's three criteria +
    perturbation test layered on top.

58. **Curvature as the minimal form of directed transport** — Session 10 concluded sim07's scalar
    transport needed to be *directed* (channel geometry carrying cue to building fronts). The
    curvature channel may BE that minimal directed geometry: depositing at concavities routes
    building along edges, not away from them. sim09 would unify the "directed transport" and
    "non-saturating inhibition" candidates into one mechanism — falsifiable: if curvature routes
    AND recruits, it should fire the crossing where the scalar (sim07) and the cap (sim08) both
    failed.
