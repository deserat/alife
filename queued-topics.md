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
    DONE (Session 15, 2026-07-30): DESIGN.md authored at
    `simulations/sim09_curvature_channel/DESIGN.md` — 9 independently-implementable Parts
    mirroring sim06's structure. The Facchini 2020 growth equation `∂f/∂t ≈ f(1−f)·[(1/2)·Δf +
    d·Δ²f]` is adapted to sim06's 2D grid+agent framework: state-gated deposit at convex tips
    (loaded) / excavate at concavities (unloaded) — the Facchini/Calovi action-component
    resolution made operational; a linear (non-saturating) deposit-probability routing on
    curvature; the `f(1−f)` surface-restriction prefactor as an `on_surface` dilation mask; the
    `d`-gated biharmonic smoothing as the phase-transition knob (sim09's analog of sim07's `M_c`);
    roughness (curvature std over surface) as the recruit proxy and the channel-adapted crossing
    criterion 2; baseline_pheromone condition (sim06's saturating rule) as the control. Part 7's
    `d` sweep is the headline phase-transition plot. NEXT: implement Part 1 (GLM, next nightly).
    **UPDATE (Session 17/18, 2026-08-02):** sim09 FULLY IMPLEMENTED — all 9 Parts [x]. Part 9
    (visualize.html + README.md) shipped; verification passes (selftests OK, run produces
    results.json, local http server 200 for page/results/sweep). At default params (d=1.0)
    neither condition crosses — the curvature channel grid-saturates (10000/10000 cells)
    because the nucleation base floods the grid before curvature routing creates spatial
    selectivity, so crossing criterion 2 (roughness sustained while mass saturates) cannot
    fire. Tuned probes (deposit_prob_base=0.01, material_decay=0.002) confirm the predicted
    consolidation DIRECTION (pillars 25→2 as d rises 0→4, roughness spike at the biharmonic
    instability) — opposite of sim06/sim07 fragmentation, H11's direction in a 4th mechanism.
    Perturbation: curvature 1.13× vs baseline 47.34× (baseline inflated by unbounded
    accumulation). The crossing is now a parameter-regime question, not a mechanism question.
    NEXT PRIORITY: a broad `deposit_prob_base × material_decay × d` sweep in the mass-saturating
    regime (low nucleation, higher erosion) to locate `d*`, plus a spatially-targeted recovery
    metric distinguishing scar repair from volume restoration.
    **DONE (Session 19, 2026-08-03):** The d* sweep ran (100 combos, `dpb × decay × d`). 0/100
    crossed under the original detector. Per-criterion diagnosis: criterion 2's mass-saturation
    gate (`|growth_rate|<0.01`) passed 0/100 — it was an **unfalsifiable metric-ceiling bug**,
    its threshold ~100× below the Poisson noise floor of a 150-termite deposit process (the
    sim06 detector-bug lesson repeating). Corrected to a relative-slope plateau
    (`|slope(M)|/mean(M)<0.001` over K=16 samples): the crossing now FIRES in the curvature
    channel at every d∈[0,4] in the tuned probe (non-saturating grid, cells 3123–5754/6400) and
    does NOT fire in the baseline-pheromone control (same detector, 0/3 — saturating rule never
    elevates the pheromone cue enough). crossing_step 1550→900, pillars 12→1, roughness
    0.44→0.77 as d rises. Determinism verified (0/80 diffs). **Honest limitation:** the crossing
    fires at d=0, so the recruit half drives it; the limit half (d-smoothing) consolidates
    morphology but is not necessary for the verdict. See `dstar_sweep.py` and H7/H11 Session-19
    refinements. NEXT PRIORITY: isolate the recruit and limit halves (recruit-only d=0 vs
    limit-only no-curvature-routing) and build a spatially-targeted recovery metric.

58. **Curvature as the minimal form of directed transport** — Session 10 concluded sim07's scalar
    transport needed to be *directed* (channel geometry carrying cue to building fronts). The
    curvature channel may BE that minimal directed geometry: depositing at concavities routes
    building along edges, not away from them. sim09 would unify the "directed transport" and
    "non-saturating inhibition" candidates into one mechanism — falsifiable: if curvature routes
    AND recruits, it should fire the crossing where the scalar (sim07) and the cap (sim08) both
    failed.

## From Session 19 (2026-08-03)

59. **Recruit-vs-limit isolation — which half of the curvature channel drives the crossing?** —
    TOP PRIORITY for the next nightly session. The corrected detector fires the crossing at
    d=0 (no biharmonic smoothing), which means the **recruit half** (curvature routing + mass
    plateau) is sufficient for the verdict and the **limit half** (d-smoothing) is not
    necessary — it only consolidates morphology (pillars 12→1, crossing_step 1550→900). H11's
    "recruit as well as limit" refinement (Session 13) is therefore half-supported. A clean
    test needs two new conditions in sim09: (a) **recruit-only** — curvature routing ON, d=0
    (smoothing OFF); (b) **limit-only** — d-smoothing ON, curvature routing OFF (termites
    follow random walks, no curvature-biased movement, but the biharmonic still smooths the
    field). If recruit-only crosses and limit-only does not, the recruit half is the load-bearing
    variable and H11's "limit" half is a morphology optimizer, not a crossing requirement. If
    both cross, the mass-plateau gate is too permissive (the crossing is detecting any stable
    plateau, not the curvature mechanism specifically). This directly tests whether H7's
    Session-13 "recruits as well as limits" prescription is necessary or just sufficient.
    **DONE (Session 20, 2026-08-04):** The 2×2 factorial (recruit ON/OFF × limit ON/OFF, 4-seed
    robustness pass) found the **recruit half is necessary and almost-sufficient** for a
    *stable* crossing: recruit-only (d=0) is stable 3/4 seeds (hold 1.00 in 3, 0.65 in the
    borderline seed); neither (no recruit, no limit) is 0/4. The **limit half alone is never
    stable** (0/4 — criteria flicker, hold 0.40–0.55, because the biharmonic shapes convex
    geometry no agent is routed to; criterion 3 `deposits_on_convex_fraction` oscillates around
    0.60). But the limit half is a **stability amplifier**: recruit+limit is stable 4/4 where
    recruit-only is 3/4 — the borderline seed becomes fully stable (hold 1.0) when d>0 is
    added. So "recruit as well as limit" = recruit necessary + almost-sufficient; limit =
    stabilizer + morphology optimizer (causal, not strictly necessary). The decisive contrast
    is recruit ON vs OFF at d=0 (same detector, same regime, only the recruit flag differs).
    A new `stable_crossed` metric (`late_hold_rate` ≥ 0.90) separates the recruit half's stable
    crossing from the limit half's transient flicker. Determinism verified. See
    `recruit_limit_sweep.py` and H7/H11 Session-20 refinements. NEXT PRIORITY: spatially-
    targeted recovery metric (#60), then L2 composition (#62).

60. **Spatially-targeted recovery metric — scar repair vs volume restoration** — DONE (Session 24).
    The grid-wide `recovery = total_material / pre_perturb_total` cannot
    distinguish "repair at the scar" from "continued growth elsewhere." The
    baseline's 47.34× "recovery" was the cleanest demonstration — it was
    unbounded material accumulation, not targeted repair. A spatially-targeted
    variant (recovery measured in the damaged patch specifically:
    `material_in_patch / pre_perturb_material_in_patch`) would make the
    perturbation acid test decisive. **Implemented as `patch_recovery` in
    sim09.py, plus a `mirror_recovery` control arm (an undamaged same-size
    region).** Result: `targeted_repair = patch_recovery − mirror_recovery` is
    **negative in all four conditions** (tuned: curvature −1.95, baseline
    −1.65; default: curvature −0.60, baseline −51.0). Neither channel
    preferentially repairs the damage site. The scar grows slower than an
    undamaged mirror (re-nucleation lag). The crossing fires but the structure
    does not self-repair in the targeted sense — the crossing is a stability
    claim, not a scar-repair claim. The Session 17 "self-repair" report was an
    artifact of the grid-wide metric. Determinism verified. See
    `patch_recovery_probe.py`, H7 Session-24 refinement.

61. **The mass-plateau gate as a reusable methodology pattern** — The sim06 and sim09
    detector-bug corrections share a pattern: a threshold set below the noise floor of the
    quantity it gates on, making the detector unfalsifiable. sim06's deposit-rate gate could
    not fire because Grassé positive feedback makes deposit probability rise; sim09's
    mass-saturation gate could not fire because Poisson window noise sits ~100× above the
    threshold. Both were caught by computing the metric's ceiling. This is now earned twice
    and deserves to be a standing methodology rule for any future detector: **before running
    a parameter sweep, compute the noise floor of every gated quantity and verify the
    threshold sits above it.** Could be added to CLAUDE.md §4 step 6 as a checklist item.

62. **Does the crossing compose? — the L2 question with a non-saturating glue** — If the
    curvature channel crosses (it does, Session 19), do two self-maintaining curvature
    structures compose into a higher-level entity? This is the sim05 L2 question reopened
    with a non-saturating stigmergic glue — the direct test of H1/H10. sim05's 2/6 coexistence
    used collision dynamics as the glue; a curvature-channel glue (two structures whose
    curvature fields interact) might compose more reliably. Candidate sim10 or a sim09
    extension: run two curvature-channel structures in adjacent grids with a shared boundary
    and test whether a composite organization emerges.

## From Session 20 (2026-08-04)

63. **The borderline-seed question — what makes seed 123 unstable for recruit-only?** —
    Recruit-only (d=0) is stable in 3/4 seeds but borderline in seed 123 (hold 0.65, still
    crosses). Recruit+limit (d=1) is stable 4/4 — the limit half rescues seed 123. What is
    different about seed 123's nucleation trajectory that makes the recruit-only crossing
    unstable, and is it a morphological difference (initial deposit scatter) or a dynamical
    one (criterion 3 flickering near threshold)? If it is nucleation scatter, the limit half
    (smoothing) regularizes it; if it is dynamical, the limit half stabilizes criterion 3
    indirectly. Inspect seed 123's history for recruit-only vs recruit+limit: where does
    hold drop (which criterion flickers), and does d-smoothing fix that criterion
    specifically? Cheap analysis of the committed sweep JSON; no new runs needed.

64. **A saturating-action control — disentangling "action-based" from "non-saturating"** —
    H11's evidence (sim08 cap, sim09 curvature) is both action-based AND non-saturating
    simultaneously, so it cannot fully distinguish "action-based" from "non-saturating" as
    the causal variable (this was flagged in H11's Criticisms section from Session 13). The
    recruit-vs-limit isolation sharpens this: the recruit half is action-based
    (curvature routes deposit/excavate selection) and non-saturating (linear gain). A
    saturating-action control — a deposit-probability routing that saturates
    (`p = base + gain·curvature/(1+|curvature|)`) rather than the linear `p = base +
    gain·curvature` — would isolate the two factors. If a saturating recruit half still
    crosses stably, "action-based" is the load-bearing property; if it degrades to a
    transient flicker (like limit-only), "non-saturating" is. This is the clean test of H11's
    core distinction, currently confounded.
    **DONE (Session 21, 2026-08-05):** The 2×2×2 factorial (response {linear, saturating}
    × recruit {ON, OFF} × d {0, 1}, 4-seed robustness pass) found **action-based is the
    primary load-bearing property; non-saturating is a secondary stability amplifier.**
    The saturating action crosses in 8/8 recruit-ON seeds (stable 6/8); the linear action
    crosses in 8/8 (stable 7/8). The limit half rescues both to 4/4 at d=1. Saturation costs
    ~0.05 in mean hold rate at d=0 (0.91→0.86) but does not collapse the crossing — criterion 3
    (deposits_on_convex_fraction) holds 1.00 for both forms; only the mass-plateau gate
    (criterion 2p) flickers more under saturation. H11's strict "non-saturating" claim is
    partially weakened: a saturating action-based channel still crosses stably, but less
    robustly. The "self-defeating" language applies to *cue-based* saturating channels
    (sim06/sim07), not to *action-based* saturating channels. The three-level causal
    decomposition: (1) action-based routing = primary, (2) non-saturating response =
    secondary stability, (3) biharmonic smoothing = tertiary stability + morphology. See
    `saturating_action_sweep.py` and H7/H11 Session-21 refinements. NEXT PRIORITY:
    spatially-targeted recovery metric (#60), then L2 composition (#62).

65. **The stable_crossed metric as a reusable methodology pattern** — The cumulative
    `crossed` flag (set once criteria hold for `CROSSING_PERSIST` consecutive samples, never
    unset) hides the difference between a crossing that holds and one that flickers on and
    off. The `late_hold_rate` (fraction of late-window records where all criteria hold)
    exposes it. This is now earned once (sim09 Session 20: the limit half's transient
    crossing was invisible until late_hold_rate was computed) and deserves to be a standing
    metric for any crossing detector: report both the cumulative verdict AND the late-window
    hold rate. A crossing that fires then degrades is not the same phenomenon as one that
    holds. Could be added to CLAUDE.md §4 step 6 alongside the metric-ceiling rule (#61).

66. **Continuous Game of Life — self-organizing cells at the edge of growth (Guillet & Jülicher 2026)** —
    A continuous-space, continuous-time Game of Life (cGoL) that produces self-replicating,
    motile, dying cell-like patterns with just 7 parameters. The key finding: a global resource
    constraint (conservation law) causes the system to self-organize to a phase transition
    boundary — the "edge of growth" — where morphologies are richest and most life-like.
    Reference code cloned to `simulations/cGoL_reference/` (Julia, FFT-based convolution,
    GPLv3). Paper: arXiv:2607.27402, to appear in Artificial Life journal.

    Relevance to our hypotheses:
    - **H1/H7 (Composition / Trace→Actor Crossing):** The cGoL cell patterns have a
      nucleus+shell structure that emerges from simple convolution rules — a spatially
      organized, self-maintaining entity. The field L is the "trace"; the emergent cell with
      homeostatic morphogen concentrations is the "actor." Self-replication and persistence
      of these cells is a concrete trace→actor crossing. Can we layer H7's crossing detector
      onto the cGoL cells? Do they satisfy the three operational criteria (persistence,
      non-reducible dynamics, constraint on agents)?
    - **H4 (Dynamic Environment):** Resource feedback is exactly H4 — the environment
      participates in a feedback loop. Growth consumes resource → resource depletion retunes
      parameters → system self-organizes at the phase boundary. A stigmergic medium with its
      own dynamics.
    - **H11 (Saturating Channel):** The "edge of growth" is a non-saturating channel —
      resource scarcity acts as feedback that doesn't saturate the way a pheromone field does.
      The system self-tunes to the transition boundary rather than collapsing.
    - **H8 (Computational Irreducibility):** The phase structure is mapped empirically through
      extensive simulation — morphologies at the edge of growth can't be predicted from rules
      alone.
    - **Multi-scale composition (H1/H10):** The cell-like patterns interact, divide, and
      collide. Whether two such self-maintaining patterns compose into a higher-order
      structure is directly testable.

    The reaction-diffusion interpretation (§4) maps the cGoL onto morphogen concentrations
    held at homeostatic levels by the nonlinear survival rule — connecting to sim03 (chemical
    organizations) and sim09 (curvature channel). The "survival rule" is a non-saturating
    channel that maintains homeostasis.

    Next step: port `cGoL_minimal.jl` to Python (numpy FFT convolution, ~100 lines), add
    resource feedback, and test whether the emergent cells satisfy H7's crossing criteria.
    The minimal Julia implementation uses: (1) two Gaussian FFT convolutions for M and N
    fields, (2) a sigmoid-based survival rule `rule0(M,N,p)`, (3) explicit Euler time
    integration. Parameters: p=(0.50, 0.10, 0.23, 0.015, 0.35, 0.26), λ=3.

## From Session 21 (2026-08-05)

67. **A truly cue-based saturating action control — completing the 2×2** — The Session 21
    saturating-action control tested *within* the action-based family (linear vs saturating
    action routing). The remaining cell of the 2×2 is a *cue-based non-saturating* channel:
    deposit probability routed on a non-saturating cue field (e.g. `p = base + gain·φ`
    without saturation, instead of `p = base + gain·φ/(1+φ)`). If a non-saturating *cue*
    channel crosses, then the action/cue distinction (H11's original framing) is the real
    divide, not the saturating/non-saturating one. If it does not, the action-based property
    is confirmed as primary even when the cue is non-saturating. This completes the 2×2:
    action×{linear,saturating} × cue×{linear,saturating}, isolating which of the two
    properties (action-based, non-saturating) is truly load-bearing. Cheap: the cue-based
    condition is sim06 with the deposit rule changed from `φ/(1+φ)` to linear `φ`.
    **DONE (Session 22, 2026-08-06):** The cue-based non-saturating control (sim06 with
    `deposit_response` parameter, `cue_response_sweep.py`) found the non-saturating cue
    crosses LESS, not more — the opposite of the action family and opposite to H11's strict
    prediction. Without self-maintenance: saturating cue 16/16 stable (hold 1.000); linear
    cue 0/16 stable (hold 0.053). With SM: both 16/16 stable. Seed robustness (4 seeds)
    confirms. **The non-saturating property reverses sign across families**: it amplifies
    stability in the action family (sim09: 7/8 vs 6/8) but destroys it in the cue family
    (sim06: 0/16 vs 16/16 w/o SM). Mechanism: the linear cue `p = base + gain·φ` clamps to
    p=1.0 at φ≈1.15, flattening the gradient (mean pheromone drops to 0.467 < 0.5 threshold);
    the saturating cue's `φ/(1+φ)` compression *prevents* deposit-probability saturation
    and preserves spatial contrast. The "self-defeating" channel is the non-saturating cue
    (deposit-probability clamping), not the saturating cue — H11's original framing was
    backwards for the cue family. Self-maintenance rescues the linear cue (4/4 stable). See
    `cue_response_sweep.py`, H7/H11 Session-22 refinements. NEXT PRIORITY:
    spatially-targeted recovery metric (#60), then L2 composition (#62).

68. **The three-level causal decomposition as a methodology pattern** — Sessions 19–21
    decomposed the crossing's causal structure into three levels: (1) action-based routing
    (primary — the causal variable separating crossing from non-crossing), (2)
    non-saturating response (secondary — stability amplifier), (3) biharmonic smoothing
    (tertiary — stability amplifier + morphology optimizer). This is a generalizable
    pattern: when a hypothesis claims two properties matter (H11: action-based AND
    non-saturating), a single confounded experiment cannot distinguish them; a factorial
    isolating each property separately, plus a seed-robustness pass with a stable-vs-transient
    metric, can. The pattern: (a) identify the confounded properties, (b) build a saturating
    control that holds one constant, (c) run a 2×2×2 factorial, (d) use late_hold_rate to
    separate stable from transient effects, (e) decompose the result into primary/secondary/
    tertiary causal levels. Could be added to CLAUDE.md §4 step 6 alongside the metric-ceiling
    and stable_crossed rules.

69. **The borderline-seed flip — seed 123 is borderline for linear but stable for saturating**
    — Session 20 found seed 123 is the borderline seed for linear recruit-only (hold 0.65).
    Session 21 found seed 123 is *stable* for saturating recruit-only (hold 0.95) — and seeds
    42 and 256 are borderline for saturating (holds 0.85, 0.70) but stable for linear. The
    borderline seeds *flip* between response curves. This means the linear and saturating
    forms are not simply "one more stable than the other" — they are fragile to *different*
    nucleation trajectories. What makes a seed borderline for one form but not the other?
    If the nucleation scatter differs, the saturating form's compressed gain may regularize
    seeds where linear's high gain overshoots, while linear's full gain may stabilize seeds
    where saturating's compression is too weak. Inspect the borderline seeds' histories: does
    the hold drop at the same criterion, and does the response curve change which criterion
    flickers? Cheap analysis of the committed sweep JSON; no new runs needed.

## From Session 22 (2026-08-06)

70. **Deposit-probability clamping vs cue-response compression — the two kinds of
    "saturation"** — Session 22's cue-based control revealed that H11's original framing
    conflated two distinct saturation phenomena: (a) **cue-response compression** (the
    `φ/(1+φ)` form flattens at high φ — what the saturating cue has) and (b)
    **deposit-probability clamping** (the linear `gain·φ` form hits p=1.0 at φ≈1.15, so every
    high-pheromone cell deposits at 100% — what the non-saturating cue has). The
    "self-defeating" saturation is (b), not (a): the non-saturating cue clamps to p=1.0 and
    flattens the gradient; the saturating cue's compression *prevents* clamping and preserves
    spatial contrast. This distinction should be formalized: a channel is self-defeating when
    its response curve saturates the *probability* (the output), not when it compresses the
    *cue* (the input). H11's "self-defeating saturating channel" should be re-read as
    "self-defeating probability-saturating channel." This is a refinement of the concept, not
    a new experiment — but it deserves a formal write-up and possibly a concept file, because
    it changes how the 2×2 should be interpreted. The action family's response curve
    (`base + gain·c` vs `base + gain·c/(1+|c|)`) saturates only the *gain* (the routing
    decision is preserved); the cue family's response curve saturates the *probability*
    (the output clamps). That is why the sign reverses.

71. **The self-maintenance rescue — is SM necessary or merely sufficient for the
    non-saturating cue?** — Session 22 found self-maintenance rescues the non-saturating cue
    completely (0/16 → 16/16 stable). But is SM the *only* mechanism that can rescue it, or
    would any pheromone-sustaining mechanism work (e.g. slower pheromone decay, higher deposit
    pheromone, lower diffusion)? If the linear cue's failure is purely "mean pheromone drops
    below 0.5," then any mechanism that keeps pheromone elevated should rescue it — and SM is
    just one way to do that. A sweep of pheromone_decay × deposit_pheromone at the linear-cue
    condition would map the rescue surface. If the rescue is specific to SM (the
    structure-reemits-pheromone loop), that connects to H7's self-maintenance crossing
    mechanism; if it is generic (any pheromone elevation), the non-saturating cue's failure is
    just a parameter-regime issue, not a mechanistic one. Cheap: a small sweep around the
    linear-cue condition.

72. **The deposit-probability saturation threshold as a predictor** — DONE (Session 23).
    The φ_sat predictor (the input value at which p_deposit first reaches 1.0) was tested
    as a unifying diagnostic across all four cells of the 2×2. A direct probe (`phi_sat_probe.py`)
    of sim06 (cue) and sim09 (action) at their crossing-proven regimes found the predictor is
    **50% accurate — no better than chance.** It correctly predicts the cue family (saturated→fails,
    unsaturated→crosses) but fails for the action family: action/linear is saturated (max curvature
    2.55 > c_sat 1.165, clamp fraction 1.0%) but still crosses stably. The clamping fraction is
    tiny everywhere (0–7%). The difference: in the cue family, the deposit probability IS the
    spatial signal — clamping it destroys the gradient. In the action family, spatial contrast
    lives in the *routing decision* (which direction the agent moves), not the deposit
    probability — the response curve saturates the *gain* (how hard to deposit), not the *routing*
    (where to go). The unifying diagnostic is **whether spatial contrast in the routing input
    survives the response curve**, which depends on channel architecture, not just the saturation
    threshold. Determinism verified. See `phi_sat_probe.py` and H7/H11 Session-23 refinements.

## From Session 23 (2026-08-07)

73. **The two-wire principle — feedback signal and spatial signal on separate
    channels** — Session 23's φ_sat probe found the predictor fails for the action
    family because spatial contrast survives via the *routing decision* (which
    direction to move), not the deposit probability. The cue family puts the
    feedback signal and the spatial signal on the same wire (the pheromone field
    → deposit probability → spatial contrast); saturating one destroys the other.
    The action family puts them on separate wires (curvature → routing decision
    for spatial contrast; curvature → deposit gain for feedback); saturating one
    leaves the other intact. This is a generalizable design principle: a
    self-defeating channel is one where the feedback signal and the spatial
    signal travel on the same wire. Does this principle hold beyond stigmergic
    channels? In ACO, the pheromone trail IS both the feedback signal and the
    spatial signal — but ACO's response function (τ^a·η^β) is unbounded, so it
    never saturates. In development, morphogen gradients carry positional
    information (spatial signal) AND feedback (concentration-dependent gene
    expression) on the same wire — and morphogen saturation is a known
    developmental pathology. This deserves a concept file and possibly a
    cross-domain synthesis. Cheap: no new runs; pure synthesis.

## From Vance (2026-08-04)

74. **Singh et al. (2025/2026) — MARL-trained weakly electric fish collectives:
    emergent social behavior from biophysical sensing + individual fitness
    reward** — arXiv:2511.08436. Found via a Bluesky follower (Naomi Saphra is a
    co-author). The paper is a complete worked example of several things our
    project has been circling, and it connects to at least five of our
    hypotheses:

    **H1 (Multi-scale composition) ↔ emergent collective behavior from
    individual incentives alone.** The paper's central claim: collective
    foraging, dominance hierarchies, aggression, and context-dependent EOD
    communication all *emerged* from individual fitness rewards with *no* reward
    for communication, coordination, chasing, or aggression. This is the same
    "emergence from individual incentives" pattern our project studies, but at
    a single scale (fish-to-fish). The open question for us: does their
    framework compose across scales? Their fish are homogeneous agents with the
    same policy — can heterogeneous policies at different scales produce
    multi-scale composition?

    **H7 (Trace→Actor Crossing) ↔ EOD as a stigmergic medium.** The EOD is a
    stigmergic signal: it modifies the electric field (environment), persists
    briefly, is sensed by conspecifics, and influences their behavior. The
    paper's Mormyromast "cons-image" (detecting conspecific EOD distortions)
    IS stigmergic sensing — agents read the environmental trace of another
    agent's action. The Knollenorgan (long-range conspecific-only sensor) is a
    dedicated stigmergic channel. The paper shows that ablating the
    Knollenorgan doesn't affect foraging but *reshapes social organization*
    (more aggression, less spacing) — the stigmergic medium is causally
    efficacious for social structure, not just foraging. This is direct evidence
    for H4 (dynamic environment as participant, not backdrop) and the ANT
    claim that the medium is an actant.

    **H11 (Saturating Channel) ↔ EOD self-cancellation.** The Mormyromast has
    an internal cancellation signal that suppresses the reafferent (self-generated)
    EOD component — the self-field is ~729× stronger than the conspecific field
    at 10 cm, so without active cancellation the self-signal would saturate the
    sensor and mask the conspecific signal entirely. This is a biological
    instance of our "two-wire principle" (queued topic 73): the self-image and
    the cons-image travel on separate wires (separate processing channels
    within the same receptor), so saturation of the self-signal doesn't
    destroy the cons-specific spatial signal. The paper's "collective sensing"
    experiment (gating self- vs cons-EOD inputs independently) is exactly the
    kind of channel-factor decomposition our Session 21–22 factorial
    experiments did with sim09.

    **H4 (Dynamic Environment) ↔ the electric field as a shared stigmergic
    medium.** The electric field is not a static backdrop — it's co-determined
    by all agents' EODs AND the environment (walls, prey distort it). Agents
    sense not only each other but "how their own and others' EODs are
    transformed by the shared environment." This is niche construction in the
    electric domain: agents modify the field they sense through, and the
    field's distortions carry information about the environment. The field IS
    the stigmergic medium.

    **RNN dynamics ↔ cross-scale neural representation.** The effective
    dimensionality of RNN activity scales with group size only when the
    Knollenorgan (long-range stigmergic channel) is intact — ablate it and
    dimensionality stays flat at the solo baseline. The social context
    *expands the neural representation space*, and this expansion is driven by
    the stigmergic channel, not by direct interaction. Proximity-dependent
    correlated latent dynamics (PLSC) between interacting agents' RNN states
    collapse to zero beyond communication range. This is a potential model
    for how multi-scale composition could work in a neural system: the
    stigmergic medium creates a shared subspace between agents that doesn't
    exist at the individual level — a new dynamical degree of freedom. Could
    our sim09 curvature structures show a similar dimensionality expansion
    when two structures interact through a shared curvature field?

    **Methodological relevance:** their in silico intervention design (ablate
    sensors, silence EODs, change food distribution) is exactly the kind of
    causal decomposition our project uses. Their "seed selection criterion"
    (balance biological desiderata across multiple converged policies) is a
    pattern we could adopt for our sim runs. Their GRU-based actor-critic with
    recurrent dynamics analysis (PCA, linear decoding, PLSC, power spectrum)
    is a toolkit we haven't used but could apply to sim09's agent states.

    NEXT: This should be a nightly research session topic. The paper deserves a
    full concept file and a synthesis entry. Key questions: (1) Does the EOD
    stigmergic medium satisfy our H7 crossing criteria? (2) Can their MARL
    framework be extended to multi-scale composition (heterogeneous policies
    at different scales)? (3) Does the two-wire principle (self/cons-image
    separation in Mormyromasts) generalize to our action/cue channel
    distinction? (4) Can RNN dimensionality analysis detect when a stigmergic
    medium creates a new dynamical degree of freedom?

## From Session 24 (2026-08-08)

75. **The control-arm methodology pattern — a metric that responds is a
    description, not a test** — Session 24's spatially-targeted recovery
    metric revealed that every metric in this project needed a control arm
    to become a test rather than a description. The crossing detector
    responded to stability (needed the baseline-pheromone control); the
    recovery metric responded to growth (needed the mirror patch); the φ_sat
    predictor responded to saturation (needed the action/linear condition).
    A metric that responds to a phenomenon but cannot distinguish it from
    confounds is a description, not a test. This is now earned three times
    (mass-saturation gate, φ_sat predictor, grid-wide recovery) and deserves
    to be a standing methodology rule: **before claiming a metric tests a
    phenomenon, identify the confound and add a control arm that holds it
    constant.** Could be added to CLAUDE.md §4 step 6 alongside the
    metric-ceiling rule (#61) and the stable_crossed rule (#65).

76. **Late perturbation after true mass plateau** — The current perturbation
    hits at 60% of steps, when the crossing has fired but the total material
    is still rising (not truly plateaued). A later perturbation (80-90% of
    steps, after the mass has equilibrated) may give a different self-repair
    result: the structure would be at equilibrium, and scar repair would be
    purely about restoring the damage, not about continuing growth. If the
    late-perturbation targeted_repair is still negative, the no-self-repair
    finding is robust; if it becomes positive, the current result is a
    timing artifact. Cheap: change perturb_at and re-run the probe.

77. **The L2 composition question with a non-saturating glue** — DONE (Session 25).
    The curvature channel crosses (Session 19), but it does not self-repair
    (Session 24). Does it compose? sim10 ran two curvature-channel structures
    in adjacent regions of one grid (shared field, shared agent pool, one-seed
    control, baseline-pheromone control). The first L2 detector (per-region
    material retention) was broken — the one-seed control fired "coexist"
    because a single structure fills both halves (control-arm lesson #75
    again). The corrected detector counts connected components lying entirely
    within each region (crossing the midline = merged). Result: at the H7
    crossing regime (decay=0.002), **15/16 two-seed runs merge into a single
    structure** — the curvature channel consolidates too aggressively for
    coexistence. At higher erosion, apparent coexistence appears but the
    1-seed control fires too (fragmentation, not composition). The
    non-saturating glue composes no better than the saturating control
    (2-seed coexist: 25/96 curvature vs 21/96 baseline; 1-seed: 16/96 vs
    22/96). The crossing is a single-structure phenomenon; L2 needs a
    boundary mechanism the curvature channel lacks. H7 refined ×14, H10
    strengthened. Determinism verified. See `sim10_l2_composition/`,
    `l2_sweep.py`, and H7/H10 Session-25 refinements. NEXT PRIORITY:
    what mechanism prevents merging? (#78, #79, #80).

## From Session 25 (2026-08-09)

78. **The boundary mechanism — what prevents two self-maintaining
    structures from merging?** — DONE (Session 26). sim11 tested the
    textbook boundary mechanism from Turing/Gierer-Meinhardt: a
    long-range inhibitor (`I = max(0, far_smoothed_material − material)` —
    self-cancelling: zero at structures, high in the gap). Deposit
    probability is multiplied by `(1 − g·I_norm/(1+I_norm))`. Result: a
    **weak positive**. At g=0.9, 2/4 seeds show clean composition (2-seed
    coexist AND 1-seed does NOT) — up from 0/4 with no inhibition. But
    2/4 seeds fragment (the 1-seed control fires too), and stable_l2
    shows no stable advantage (0/4 at all gains). The H7 crossing
    survives inhibition (h7=4/4 at all gains). The self-cancelling
    inhibitor is the critical design insight: a simple smoothed-material
    inhibitor (without the far−local subtraction) is self-defeating — it
    is always highest AT the structure and kills all building. The
    composition problem is not just missing lateral inhibition; even the
    textbook boundary mechanism produces only weak, non-robust partial
    coexistence. Determinism verified. See `sim11_boundary_mechanism/`
    and H7/H10 Session-26 refinements. NEXT PRIORITY: heterogeneous agent
    policies (#79), autopoietic boundary (#81).

79. **Heterogeneous agent policies as a composition mechanism** — The
    Singh et al. (2025/2026) MARL fish paper (queued-topic #74) shows
    emergent collective behavior from individual fitness rewards with
    homogeneous policies. What if the two L1 structures are built by
    DIFFERENT agent types (different deposit rules, different curvature
    responses)? Would two heterogeneous-built structures coexist where
    two homogeneous-built structures merge? This tests whether
    compositional diversity (H1) requires agent heterogeneity, not just
    a non-saturating glue. Could be a sim10 extension: two agent
    populations with different deposit_prob_gain or curve_follow.

80. **The one-seed control as a standing methodology pattern** — sim10's
    L2 detector was broken until the one-seed control proved it was
    measuring "material exists in both halves" not "two structures
    coexist." This generalizes the control-arm lesson (#75): any
    composition or plurality detector needs a single-component control
    to prove it is detecting plurality, not ubiquity. Could be added to
    CLAUDE.md §4 step 6 alongside the metric-ceiling (#61),
    stable_crossed (#65), and control-arm (#75) rules.

## From Session 26 (2026-08-10)

81. **An autopoietic boundary — a self-maintaining inhibitor, not a
    passive field** — DONE (Session 27).
    sim12 tested a boundary field B with its own growth/decay dynamics
    (memory): `B_new = B * (1 − b_decay) + b_growth * co_presence`
    where `co_presence = min(left_shadow, right_shadow)`. B is more
    stable (4/4 vs 1/4 for the passive) and survives a 50%
    material-removal perturbation (B retains 91% at 100 steps,
    coexistence persists). But its memory also creates false
    boundaries — the 1-seed control fires in 2/4 (vs 1/4 for the
    passive). Clean composition is 2/4 for both — the
    memory-specificity trade-off cancels out. The co-presence signal
    leaks on the torus (agent-deposited material in both halves
    creates a non-zero co-presence even for one seed). The H7
    crossing survives all conditions (h7=4/4). See
    `sim12_autopoietic_boundary/` and H5/H6/H7/H10 Session-27
    refinements. NEXT PRIORITY: a mechanism that combines memory with
    specificity (#84, #85, #79).

82. **The self-cancelling inhibitor as a general principle** — sim11's
    critical design insight was that a long-range inhibitor must not
    self-inhibit: `I = max(0, far_smoothed − local)` isolates the
    distant signal from the local. This is the spatial analog of the
    two-wire principle (#73, Session 23): the distant-structure signal
    and the local-structure signal travel on separate wires. Without
    separation, saturating one (the local) destroys the other (the
    distant). This deserves a formal write-up: in any system where a
    long-range inhibitory field is derived from a local activator
    (material → smoothed shadow), the naive form (just the shadow) is
    self-defeating. The difference form (shadow − source) is necessary.
    This may connect to lateral inhibition in neural systems (where the
    inhibitory interneuron receives excitation from the very cells it
    inhibits — and the circuit architecture separates self-excitation
    from lateral inhibition).

83. **The crossing is separable from composition** — Session 26 found
    the H7 crossing survives inhibition (h7=4/4) while composition is
    only weakly improved (2/4 clean). This means the single-structure
    crossing and the multi-structure composition are independent
    problems needing different mechanisms. The crossing is about one
    structure's self-maintenance; composition is about two structures'
    interaction. This sharpens H1/H10: "explicit composition mechanisms"
    are not just better channels or better single-structure rules —
    they are a separate class of mechanism (boundary, interaction,
    heterogeneous policies) that operates BETWEEN structures, not
    within them. The research program should now separate these two
    tracks explicitly.

## From Session 27 (2026-08-11)

84. **The memory-specificity trade-off — a mechanism that combines both** —
    DONE (Session 28).
    sim13 tested the direct-material co-presence approach (#85): replacing
    sim12's diffused-shadow co-presence with a max filter that doesn't wrap
    in x, eliminating the torus leak. Result: the torus leak IS eliminated
    (initial 1-seed co-presence <1% of 2-seed) but the false boundaries
    persist (1-seed control 1/4) — **agent wander on the torus, not the
    spatial filter, causes false boundaries**. A radius sweep (8-30)
    reveals a breadth-specificity dimension: small → merges, medium → false
    positives, large → fragmentation. Clean composition is 1/4 (worse than
    sim12's 2/4). The memory-specificity trade-off is a system property
    (agents on a torus distribute material everywhere), not a signal
    property (diffusion vs. direct-material). The fix requires agent
    fidelity, not a better spatial filter. See `sim13_direct_copresence/`
    and H5/H6/H7/H10 Session-28 refinements. NEXT PRIORITY: heterogeneous
    agent policies (#79) — agents tagged with a structure ID so the
    boundary grows only where two distinct populations meet.

85. **Direct-material co-presence — eliminating the torus leak** — DONE (Session 28).
    See #84 above. The direct-material max filter (no x-wrapping) eliminates
    the diffusion torus leak but does not eliminate false boundaries — agent
    wander is the true cause.

86. **The memory-specificity trade-off as a general principle** — The
    three "separate wires" principles now form a family: (1) two-wire
    principle (#73): feedback signal and spatial signal on separate
    channels; (2) self-cancelling inhibitor (#82): distant signal and
    local signal on separate wires; (3) memory-specificity trade-off:
    persistence and specificity on separate wires. All three say the
    same thing: when two properties are carried on the same wire,
    saturating one destroys the other. This is a general design
    principle for self-organizing systems. Could be added to CLAUDE.md
    §4 step 6 alongside the metric-ceiling (#61), stable_crossed (#65),
    and control-arm (#75) rules.

87. **B parameter sweep — growth, decay, and copresence_passes** —
    sim12's B parameters (b_growth=0.1, b_decay=0.005, 8 passes) were
    chosen, not swept. A systematic sweep of b_growth × b_decay ×
    copresence_passes would map the stability-specificity frontier:
    faster decay (less memory) should move toward the passive inhibitor
    (more specific, less stable); slower decay (more memory) should
    move toward more false boundaries. The optimal point on this
    frontier might break the 2/4 clean composition ceiling — or it
    might not. Cheap: re-run the robustness sweep at different
    parameter settings.

## From Session 28 (2026-08-12)

88. **Heterogeneous agent policies — agents tagged with a structure ID**
    — DONE (Session 29).
    sim14 tested agent-level fidelity: agents carry a structure ID
    (0=left, 1=right). Deposits are tagged with the depositor's ID.
    Co-presence = min(dilate(material_by_id[0]), dilate(material_by_id[1])).
    For a single seed, all material is id=0 — co-presence is structurally
    zero (B_max=0.0 across all seeds). The 1-seed control is 0/4 on ALL
    metrics — the first structurally clean composition. Clean composition
    is 2/4 (matching shadow/passive). But the stronger boundary suppresses
    H7 crossing (0/4 — first time crossing lost across all seeds). The
    trade-off shifts from specificity-vs-memory to strength-vs-growth:
    the boundary that enables composition kills the crossing. See
    `sim14_heterogeneous_agents/` and H5/H6/H7/H10 Session-29
    refinements. NEXT PRIORITY: tune inh_gain to find the regime where
    both crossing and composition co-occur (#91, #92).

89. **The l2_crossed ≠ l2_outcome distinction — fragmentation as a third
    outcome** — sim13 revealed that the L2 detector can fire (l2_crossed:
    components in both halves) while the outcome is "fragmented" (multiple
    components, not two clean structures) rather than "coexist." This is a
    third outcome beyond "coexist" and "none/merged" that previous
    simulations didn't encounter. The broad boundary (radius=30) prevents
    merging but over-fragments. This suggests the L2 detector should
    distinguish "two clean structures" (coexist) from "multiple fragments
    in both halves" (fragmented) — the latter is not genuine composition.
    Could refine the L2 outcome classifier in sim10's detect_l2.

90. **The b_scale normalization effect — a hidden parameter** — sim13's
    radius sweep found that at radius=30, the b_scale (set from the 95th
    percentile of initial co-presence) is very large because the dilated
    seeds overlap strongly. This makes B_norm = B / b_scale small, weakening
    the boundary suppression. The clean composition at seed 42 may be an
    artifact of this normalization rather than a genuine property of the
    direct-material approach. A sweep of b_scale (or using a fixed scale
    instead of the 95th percentile) would determine whether the
    normalization is load-bearing.

## From Session 29 (2026-08-13)

91. **The inh_gain sweep — finding the strength-vs-growth sweet spot** —
    DONE (Session 30).
    A sweep of inh_gain (0.1, 0.3, 0.5, 0.7, 0.9) with 4-seed robustness
    found the trade-off is PARTIALLY BREAKABLE. At g=0.5, H7=4/4 and
    L2=4/4 co-occur with 2/4 clean composition — the first co-occurrence
    of crossing and composition. At g=0.3, seed 999 achieves stable
    composition WITH H7 crossing. But stable composition (2/4 at g=0.9)
    requires the strong boundary that kills H7 (0/4). The 1-seed control
    is 0/4 at ALL gains — the structural specificity guarantee holds
    across the entire strength spectrum. The tension is between crossing
    and *stable* composition, not crossing and composition per se. See
    `inh_gain_sweep.py` and H7/H5/H6/H10 Session-30 refinements. NEXT
    PRIORITY: structural decoupling (#92), agent movement restriction
    (#93).

92. **Decoupling boundary strength from co-presence precision** — The
    ID-based co-presence is both more specific AND stronger than spatial
    versions, because the signal is higher and more localized. The
    boundary's suppression is proportional to B_norm, which is
    proportional to co-presence, which is higher for ID-based signals.
    A decoupled design: the boundary grows where two IDs meet (specificity
    from IDs), but the suppression strength is fixed (not proportional to
    co-presence magnitude). This would test whether the strength-vs-growth
    trade-off is caused by the coupling between signal precision and
    boundary strength, or by the boundary mechanism itself. Could be a
    sim14 variant: `p_dep *= (1 - g * B_threshold)` where B_threshold is
    a fixed constant, not B_norm.

93. **Agent movement restriction — keeping agents near their structure** —
    DONE (Session 34).
    sim14's movement_bias parameter (agents step toward home center when
    not curvature-following) was swept at dual f=0.3 p=0.3:
    bias [0.0, 0.3, 0.5, 0.7, 0.9] × 4 seeds × {2, 1} seeds. Result:
    **movement_bias ≥ 0.3 produces 4/4 full co-occurrence** (H7+clean+stable)
    — up from 1/4 at bias=0.0. The transition is sharp: 0.0→1/4, 0.3→4/4.
    H7=4/4 at all bias values (crossing independent of agent distribution).
    1-seed control 0/4 at all bias values. Agent wander was saturating the
    co-presence signal (high everywhere, not just at the boundary);
    movement_bias concentrates each ID's material, making the boundary
    signal sharper. This breaks the outcome-quality ceiling that 11 boundary
    mechanisms couldn't. Cross-domain: Richardson et al. (2022) found real
    insects use local mechanisms (diffusivity adjustment, boundary effects),
    not focal-point attraction. See `movement_sweep.py` and H5/H6/H7/H10
    Session-34 refinements. NEXT PRIORITY: finer threshold sweep, local
    movement mechanisms (#105), test at proportional mode (#106).

94. **The strength-vs-growth trade-off as a general principle** — The
    memory-specificity trade-off (Sessions 27-28) was about temporal
    properties (persistence vs. false positives). The strength-vs-growth
    trade-off (Session 29) is about spatial properties (boundary strength
    vs. structure growth). Both are instances of a general principle: in
    any system where a boundary separates two self-organizing structures,
    the boundary must be strong enough to prevent merging but weak enough
    to allow growth. This connects to surface tension (Laplace pressure),
    cell membranes (permeability vs. integrity), and control theory (gain
    margin). Could be added to CLAUDE.md §4 step 6 alongside the
    metric-ceiling (#61), stable_crossed (#65), control-arm (#75), and
    one-seed control (#80) rules.

## From Session 30 (2026-08-14)

95. **The stable-vs-transient distinction — why does composition at the
    sweet spot (g=0.5) not persist?** — At g=0.5, H7=4/4 and L2=4/4
    co-occur, but 0/4 are stable (l2_stable). The composition is present
    but transient. What makes a composition transient vs. stable? Is
    it that the boundary is too weak to prevent slow merging over time
    (the structures eventually drift together)? Or is it that the
    crossing detector's criteria flicker (like the limit-only case in
    Session 20)? Inspect the late-window hold rates and the l2_outcome
    trajectory over time for the g=0.5 co-occurring seeds. Cheap: the
    sweep JSON has per-seed outcomes; need to run a time-series probe
    at g=0.5 seed=42 to see if the composition degrades.

96. **The gain margin analogy — formalizing the strength-vs-growth
    trade-off** — The inh_gain sweep maps directly to the gain margin
    problem in control theory. The boundary's inh_gain is the feedback
    gain: too low → disturbance rejection fails (structures merge),
    too high → suppression (growth killed). The sweet spot (g=0.5)
    is the gain margin — the range where the system is stable. But
    "stable" here means the crossing fires AND composition holds, not
    just that the system doesn't diverge. Could formalize this as a
    transfer function: input = deposit probability, output = structure
    growth, feedback = boundary suppression. The phase margin would
    predict the robustness of the co-occurrence. Could connect to
    queued-topic #94 (strength-vs-growth as a general principle).

97. **Finer inh_gain resolution around the sweet spot** — The sweep
    tested 5 gains (0.1, 0.3, 0.5, 0.7, 0.9). The H7 transition
    happens between 0.7 (4/4) and 0.9 (0/4). A finer sweep (0.7, 0.75,
    0.8, 0.85, 0.9) would locate the exact H7 threshold and whether
    there's a narrow window where H7=4/4 AND stable>0/4. Also: finer
    resolution around g=0.3-0.5 (0.3, 0.35, 0.4, 0.45, 0.5) to see if
    the stable+H7 co-occurrence (seed 999 at g=0.3) is robust at nearby
    gains. Cheap: re-run the sweep at finer resolution.

## From Session 31 (2026-08-15)

98. **Decoupling boundary strength from co-presence precision** — DONE (Session 31).
    The decoupled boundary sweep tested fixed suppression (binary
    gate: `supp = g` wherever B exists) vs proportional suppression
    (gradient gate: `supp = g * B_norm/(1+B_norm)`). Result: H7
    unchanged between modes (4/4 at g=0.3–0.7, 0/4 at g=0.9 in both).
    Binary gate produces MORE STABLE composition (g=0.5: 0/4→2/4;
    g=0.9: 2/4→4/4) but LESS L2 formation (g=0.5: 4/4→2/4). The
    suppression curve's SHAPE matters for stability, not just its
    magnitude. A new stable co-occurrence at decoupled g=0.7 seed=999
    (H7=YES + coexist + stable). 1-seed control 0/4 at ALL gains in
    BOTH modes. The trade-off is not just strength vs growth — it is
    gradient vs binary suppression. See `decoupled_sweep.py` and
    H7/H5/H6/H10 Session-31 refinements. NEXT PRIORITY: a hybrid
    curve (wide coverage + full strength) — e.g. a clipped gradient
    that is proportional at low B_norm but saturates at a fixed
    plateau, combining the formation advantage of the gradient with
    the stability advantage of the binary (#99).

99. **The hybrid suppression curve — combining gradient formation with
     binary stability** — DONE (Session 32).
     The hybrid `supp = min(g * B_norm / (1 + B_norm), g * k)` was
     tested across 6 modes × 4 gains × 4 seeds (192 runs). Result:
     the hybrid cap PRESERVES the H7 crossing at g=0.9 where both
     proportional and decoupled lose it (hybrid_k08 H7=4/4 vs 0/4 for
     both pure modes). The transition is between g*k=0.72 and 0.81.
     A new stable co-occurrence at g=0.9 (hybrid_k05 seed=123:
     H7=YES + coexist + stable) — the first at the highest gain.
     The hybrid produces the most clean co-occurrences (5, hybrid_k08).
     But the full co-occurrence ceiling (H7 + L2 + stable + clean)
     remains 2/4 — the trade-off is only partially broken. The key
     insight: H7 depends on max suppression magnitude (g*k), not gain
     (g) or curve shape. The hybrid cap is analogous to MAX-MIN Ant
     System's τ_max bound (Stützle & Hoos, 2000). See `hybrid_sweep.py`
     and H7/H5/H6/H10/H11 Session-32 refinements. NEXT PRIORITY:
     separate B fields for formation and persistence (#101), agent
     movement restriction (#93).

100. **The H7 crossing depends on max suppression, not curve shape** —
     REFINED (Session 32). Session 31 found H7 is identical between
     proportional and decoupled modes at every gain, suggesting the
     crossing is independent of the suppression curve. Session 32's
     hybrid sweep refines this: the crossing IS independent of the
     curve SHAPE at a given max suppression, but NOT independent of
     the max suppression magnitude. At g=0.9, proportional (max
     supp=0.9) and decoupled (max supp=0.9) both lose H7; hybrid_k08
     (max supp=g*k=0.72) preserves it. The threshold is between
     g*k=0.72 and 0.81. The crossing is a single-structure property;
     the boundary is a multi-structure property; they operate on
     independent axes — but the crossing's axis is max suppression,
     not gain. The boundary can be tuned (curve shape, gain) without
     affecting the crossing AS LONG AS the max suppression stays below
     the threshold.

## From Session 32 (2026-08-16)

101. **Separate B fields for formation and persistence — the two-wire
     principle's next test** — DONE (Session 33).
     The dual mode uses TWO B fields with separate growth/decay
     dynamics — B_form (gradient, faster decay 2×) for formation
     and B_persist (binary, slower decay 1×) for persistence.
     Total suppression = min(g_form * Bf_norm/(1+Bf_norm) + g_persist
     * [Bp>0.01], 0.99). Result: the two-wire principle BREAKS the
     persistence-formation trade-off for stability. At dual f=0.3
     p=0.3 (max_supp=0.60): H7=4/4, L2=4/4, clean=2/4, **stable=3/4**
     — the highest stability rate ever with full H7 and L2. At the
     same L2 and clean as proportional g=0.5 (stable=0/4), stability
     improved 0/4 → 3/4. The dual mode dominates every single-wire
     mode on every axis simultaneously. But the full co-occurrence
     (H7+clean+stable) remains 1/4 — the outcome-quality ceiling is
     not broken. The max suppression threshold (0.72–0.81) is
     channel-architecture-independent. 1-seed control 0/4 at ALL 9
     configs. Determinism verified. See `dual_sweep.py` and
     H5/H6/H7/H10/H11 Session-33 refinements. NEXT PRIORITY: agent
     movement restriction (#93), the outcome-quality ceiling
     (fragmented/merged outcomes), the PID D-term (B_derivative).

## From Session 33 (2026-08-18)

102. **The outcome-quality ceiling — why is the composed state
     fragmented or merged, not clean coexistence?** — The dual mode
     achieves 3/4 stable with H7=4/4 and L2=4/4, but only 1/4 is
     clean coexistence. The other stable seeds are "fragmented"
     (multiple small components) or "merged at the end" (structures
     held for most of the late window but merged in the final steps).
     What mechanism ensures the composed state is two clean
     structures, not fragmentation or late merging? Candidate:
     agent movement restriction (#93) to concentrate each ID's
     material, reducing boundary width and fragmentation. Or: a
     repulsive force between the two structures that prevents late
     merging.

103. **The PID D-term — a B_derivative field** — DONE (Session 39).
     The dual mode maps onto a PID controller: B_form = P
     (proportional, responsive), B_persist = I (integral, memory).
     The D (derivative) term was implemented as B_deriv, growing from
     the positive part of the co-presence rate of change (cp_delta =
     max(0, cp - cp_prev)) with fast decay (4× default). RESULT: The
     D term is NEUTRAL at the optimal config (dual f=0.3 p=0.3, focal
     bias=0.3: 4/4 full co-occurrence at all g_deriv 0.0–0.3). Without
     focal bias: DESTRUCTIVE — stable 3/4→0/4 at g_deriv=0.1, coexist
     2/4→0/4 at g_deriv=0.3 (all fragmented). The D term is
     endogenous (cp_delta from system state), creating a stigmergic
     feedback loop — the two-wire principle's tenth instance: an
     endogenous anticipatory signal amplifies the oscillation it tries
     to damp. The D term cannot substitute for agent locality (the
     exogenous focal bias). See `pid_sweep.py`,
     `pid_no_focal_sweep.py`, and H5/H6/H7/H10 Session-39 refinements.
     not after. This might prevent the "merged at the end" outcome
     (seed 999 at f=0.3 p=0.3) by detecting the merger trend early.
     Could be a sim14 variant: B_deriv = d(co-presence)/dt, supp +=
     g_deriv * sigmoid(B_deriv).

## From Session 39 (2026-08-25)

117. **The exogenous D-term — can an external anticipatory signal
     help?** — DONE (Session 40).
     An external sinusoid driving B_deriv independently of system
     state. RESULT: less destructive than endogenous (stable 3/4→1/4
     vs 3/4→0/4 at g_deriv=0.1 without focal bias) but still harmful.
     The D-term's failure is PARTIALLY endogeneity (exogenous is less
     destructive) and PARTIALLY anticipation itself (exogenous is
     still destructive). The 1-seed control leaks (2/4 at g_deriv=0.05
     and 0.2) — the spatially uniform exogenous signal creates B_deriv
     even for 1-seed, breaking the structural guarantee. The two-wire
     principle's eleventh member: the exogenous signal must be
     spatially specific as well as temporally exogenous. The
     Heisenberg trade-off: the signal cannot be simultaneously
     exogenous (unreachable by dynamics) and spatially specific
     (shaped by spatial structure). See `exo_dterm_sweep.py` and
     H5/H6/H7/H10 Session-40 refinements.

118. **The two-wire principle as a formal write-up — eleven members
     and counting** — DONE (Session 42). The two-wire principle now
     has a standalone concept file: `concepts/two-wire-principle.md`.
     Twelve members across Sessions 23–41 form a progression: (1-3)
     channel separation, (4-5) field separation, (6-7) signal quality,
     (8) exogeneity, (9) noise structure, (10) endogeneity, (11)
     spatial specificity, (12) structure-to-grid ratio. Each level
     is a stronger form: the signal must not be reachable by the
     dynamics it controls, must be specific to where it acts, and
     the structure must be small enough for the boundary to separate
     it. The Heisenberg trade-off (Members 10-11): the signal cannot
     be simultaneously exogenous and spatially specific — the focal
     mode's fixed home center is the unique signal that resolves it
     (an external spatial reference). Cross-domain connections to
     ACO, developmental morphogens, control theory, and statistical
     physics. The finer density sweep (Session 42) provided the first
     modest predictive confirmation: the 12th member predicted higher
     density would worsen the 1-seed leak — confirmed (0/4 → 1/4 →
     1/4 → 3/4).

119. **Scale termites with grid area — does density rescue the
     160×160 failure?** — DONE (Session 41).
     Scaling n_termites with grid area (150→600 for 160×160,
     maintaining constant density ~23.4/kcell) FULLY rescues H7
     (4/4 at all jitter) but only PARTIALLY rescues composition
     (4/4 at jit=0, 3/4 stable at jit=10, 2/4 at jit=20). The 1-seed
     structural guarantee leaks at 160×600 (2/4 at jit=10, 4/4 at
     jit=20) — an absolute-size effect: the bigger single structure
     (~2700 cells) overwhelms the midline even with focal bias.
     The two-wire principle's twelfth member: the structural
     guarantee depends on structure-to-grid ratio, not just agent
     density. The crossing is density-dependent, not grid-size-
     dependent. See `density_sweep.py` and H5/H6/H7/H10 Session-41
     refinement. NEXT PRIORITY: the non-monotonic intermediate
     density (#122), the two-wire principle formal write-up (#118).

122. **The non-monotonic intermediate density — why is 160×300
     worse than both 160×150 and 160×600?** — DONE (Session 42).
     At jitter=10, 160×300 (11.7/kcell) achieves only 2/4 coexist —
     worse than 160×150 (4/4 at 5.9/kcell) and 160×600 (4/4 at
     23.4/kcell). A finer density sweep (100, 200, 400, 800 termites)
     at jitter=10 found composition improves MONOTONICALLY with density:
     n=100 → 0/4, n=200 → 1/4, n=400 → 4/4 (3/4 stable), n=800 → 4/4
     (4/4 full). The non-monotonicity was a 4-seed noise artifact —
     160×300's 2/4 was within the noise band. n=800 achieves 4/4 full
     co-occurrence (first on 160×160) but the 1-seed control leaks
     (3/4) — the structure-to-grid ratio problem persists. H7 has a
     percolation-like density threshold (0/4 below ~4/kcell, 4/4 above
     ~8/kcell). See `finer_density_sweep.py`.

## From Session 41 (2026-08-27)

104. **Finer g_form/g_persist resolution around the sweet spot** — The
     sweep tested 3×3 (g_form × g_persist). The best config (f=0.3
     p=0.3) has max_supp=0.60. A finer sweep (0.2, 0.25, 0.3, 0.35,
     0.4 for each) might find a config with 4/4 stable or 2/4 full
     co-occurrence. Also: test asymmetric decay rates (b_decay_form
     = 3×, 4× default) to see if the decay ratio matters as much as
     the gain ratio. Cheap: re-run the sweep at finer resolution.

## From Session 34 (2026-08-20)

105. **Local movement mechanisms — boundary effects and diffusivity
     adjustment** — DONE (Session 35).
     Richardson et al. (2022, Nature Comms) found that real social
     insects achieve spatial fidelity through LOCAL mechanisms, not
     focal-point attraction (our movement_bias). Two candidate
     mechanisms: (a) boundary effects — agents turn back when they
     encounter the B field (an agent at a high-B cell reverses
     direction, staying within its home region); (b) diffusivity
     adjustment — agents move with low diffusivity (small steps)
     inside their home region and high diffusivity (large steps)
     outside it. These are more biologically grounded than
     focal-point attraction and might produce different (better or
     worse) results. A boundary-effect mechanism would also close
     the loop: the B field (grown from co-presence) influences agent
     movement (agents stay in their region) which influences co-
     presence (concentrated material) which influences B — a true
     stigmergic feedback loop. RESULT: Both local mechanisms FAIL.
     Boundary mode is self-defeating — the stigmergic feedback loop
     (B → movement → co-presence → B) over-amplifies B (b_max 70-203
     vs 30-50 for focal), fragmenting all structures (4/4 fragmented,
     0/4 coexist). Diffusivity mode is worse than baseline (1/4 vs
     2/4 coexist). The global focal-point attraction outperforms
     both. The boundary mode's failure is the two-wire principle's
     sixth instance: deposit suppression and agent movement on the
     same signal create a self-defeating positive feedback. The
     biological lesson: local mechanisms require separate sensory
     channels (Richardson et al.) — our simulation lacks those
     channels. See `local_movement_sweep.py` and H5/H6/H7/H10
     Session-35 refinements.

106. **Finer movement_bias resolution around the threshold** — The
     transition from 1/4 to 4/4 full co-occurrence happens between
     bias=0.0 and 0.3. A finer sweep (0.05, 0.1, 0.15, 0.2, 0.25)
     would locate the exact threshold and confirm it's a genuine
     phase transition rather than a discretization artifact. Also:
     8 seeds at the threshold for robustness. Cheap: re-run the
     sweep at finer resolution.

107. **Test movement_bias at proportional mode** — The movement sweep
     was run only at dual f=0.3 p=0.3. Does movement_bias help with
     single-wire boundaries (proportional g=0.5) too, or only with
     the dual mode? If it helps equally, the agent distribution is
     truly independent of the boundary mechanism. If it helps more
     with the dual mode, there's an interaction between agent
     distribution and channel architecture. Cheap: re-run the sweep
     at proportional g=0.5 with the same bias values.

108. **The three-wire principle as a general design principle** — The
     family of "separate wires" principles now has six members: (1)
     two-wire (#73): feedback signal and spatial signal on separate
     channels; (2) self-cancelling inhibitor (#82): distant signal
     and local signal on separate wires; (3) memory-specificity
     (#86): persistence and specificity on separate wires; (4) dual
     mode (S33): formation and persistence on separate B fields;
     (5) agent distribution (S34): boundary and agent movement on
     separate axes; (6) movement-wire decoupling (S35): deposit
     suppression and agent movement on separate signals. All six
     say the same thing: when two properties are carried on the same
     wire, the feedback amplifying one destroys the other. The sixth
     adds a new dimension: when one signal is a feedback signal the
     system generates from its own state, the positive feedback loop
     doesn't just saturate — it actively amplifies until the structure
     fragments. This deserves a formal write-up as a general design
     principle for self-organizing systems. Could be added to
     CLAUDE.md §4 step 6 alongside the metric-ceiling (#61),
     stable_crossed (#65), control-arm (#75), one-seed control (#80),
     and strength-vs-growth (#94) rules.

## From Session 35 (2026-08-21)

109. **Richer sensory channels — a second signal field for zone
    identification** — DONE (Session 36).
    The boundary mode's failure shows that local mechanisms need
    separate sensory channels. Real insects have chemical blends on
    nest surfaces, tactile cues, temperature gradients — multiple
    signals for zone identification vs. boundary detection. Our
    simulation has only one signal (the B field). A second signal
    field (independent of B, e.g. a "zone field" that marks each
    agent's home region) could provide the separate wire that local
    mechanisms need. A boundary-effect mechanism that reads the zone
    field (not B) for movement decisions would close a DIFFERENT loop
    (zone → movement → material concentration → co-presence → B →
    deposit suppression) where the movement signal is independent of
    B. RESULT: The zone mode (agents read own-ID dilated material,
    not B) broke the stigmergic feedback loop (b_max 50.2 ≈ none's
    47.9 vs boundary's 104.5) but produced 0/4 coexist — WORSE than
    no restriction (2/4). The separate wire exists but carries a
    noisy signal: dilated own-ID material is diffuse and endogenous.
    The two-wire principle's seventh member: a separate wire with a
    noisy signal doesn't recover the function. The focal mode's
    exogenous fixed-center signal remains the gold standard — it is
    the only mechanism achieving 4/4 full co-occurrence. The 1-seed
    l2_crossed=0/4 (structural guarantee holds); l2_outcome has a new
    leak (1/4 "coexist" from movement-induced fragmentation). See
    `zone_sweep.py` and H5/H6/H7/H10 Session-36 refinements.

110. **The stigmergic feedback loop as a control-theory instability —
     formalizing the gain margin** — The boundary mode's
     stigmergic loop (B → movement → co-presence → B) is a positive
     feedback loop with gain > 1 (unstable). The focal mode breaks
     the loop by making the movement signal exogenous (zero feedback
     gain). Could formalize this as a transfer function: input =
     deposit probability, output = structure growth, feedback =
     boundary suppression, movement feedback = additional loop.
     The gain margin would predict which movement modes are stable.
     Could connect to queued-topic #96 (gain margin analogy).

## From Session 36 (2026-08-22)

111. **A precise endogenous signal — can the zone signal be sharpened?** — The
     zone mode's signal (dilated own-ID material) is too noisy. The
     dilation radius (8) spreads the signal, making zone boundaries
     diffuse. A sharper signal — e.g. a threshold on undilated own-ID
     material (radius=0), or a smaller radius (2-3), or a gradient
     rather than a threshold — might produce a more precise zone
     boundary without the stigmergic feedback loop. Alternatively, a
     decayed "scent trail" (own-ID material decayed at a faster rate
     than the structure) might give a sharper boundary. Test: sweep
     the dilation radius and the zone_threshold for the zone mode.

112. **The l2_outcome leak — movement-induced fragmentation as a
     false positive** — The zone mode's 1-seed control has
     l2_crossed=0/4 (structural guarantee holds) but l2_outcome="coexist"
     in 1/4. The movement restriction fragments the single-seed
     structure, creating components on both sides of the midline.
     The l2_crossed metric (sustained persistence) catches this;
     the l2_outcome classifier (final-state) does not. This is a new
     failure mode: the movement mechanism itself creates the
     appearance of composition. Should the l2_outcome classifier
     be hardened against this? Or is this a genuine limitation of
     any movement-based zone mechanism?

113. **The focal mode's exogenous advantage — why does a fixed
     reference outperform endogenous signals?** — DONE (Session 37).
     The home-jitter sweep added Gaussian noise to the focal home
     center: jitter ∈ {0, 2, 5, 10, 20, 40} cells (0–50% of the 80-cell
     grid). RESULT: **exogeneity is load-bearing, not precision.** A
     noisy exogenous signal (jitter=10, 12.5% of grid) preserves 4/4
     full co-occurrence. The collapse at jitter=20 is misdirection (home
     center crosses midline — agents directed to wrong half), not noise
     intolerance. The non-monotonic partial recovery at jitter=40 (3/4
     coexist) confirms: random direction beats systematically wrong
     direction. The decisive comparison: jitter=40 (exogenous, b_max=49.0)
     produces 3/4 coexist; zone mode (endogenous, b_max=50.2) produces
     0/4 — at nearly identical B magnitude, the exogenous signal
     outperforms the endogenous signal on every axis. The two-wire
     principle's eighth member: the signal must be on a wire the system
     cannot reach. See `jitter_sweep.py` and H5/H6/H7/H10 Session-37
     refinements. NEXT PRIORITY: per-agent persistent jitter (#114),
     larger grid scaling (#115).

## From Session 37 (2026-08-23)

114. **Per-agent persistent jitter — temporal averaging vs spatial
     correlation** — DONE (Session 38).
     The current jitter is per-step (each agent draws a fresh home center
     each step it moves focally). A per-agent persistent jitter (each
     agent has a fixed noisy home center for its lifetime) is spatially
     correlated rather than temporally averaged. RESULT: **the noise
     structure matters, non-monotonically.** At jitter=10 (12.5% of
     80-cell grid): per_step 4/4 full co-occurrence, per_agent 1/4
     coexist — temporal averaging wins (errors cancel). At jitter=20
     (25%): per_step 1/4 coexist 0/4 stable, per_agent 3/4 coexist 4/4
     stable — spatial correlation wins (consistency prevents
     fragmentation). The crossover is non-monotonic: at moderate noise
     temporal averaging is better; at high noise spatial correlation is
     better. The two-wire principle's ninth member: the noise structure
     on the exogenous wire must match the noise magnitude. H7 4/4 at
     all conditions at 80×80. 1-seed 0/4 at all conditions. See
     `jitter_mode_sweep.py` and H5/H6/H7/H10 Session-38 refinements.

115. **Grid-size scaling — does the jitter tolerance scale?** — DONE
     (Session 38).
     The collapse at jitter=20 (25% of 80) is a grid-size artifact: home_x=20,
     jitter=20 → home can be at x=40 (midline). On a 160×160 grid with
     home centers at x=40 and x=120, jitter=20 is only 12.5% of grid —
     does it preserve 4/4? RESULT: **it does NOT scale.** The 160×160
     grid at jitter=20 (12.5%) produces 0/4 coexist, 0/4 H7 — worse
     than 80×80 at 25%. The same 150 termites on 4× the area produce
     sparser structures; the curvature channel has less material to
     consolidate. The 1-seed l2 control leaks (2/4 at jit=20, 4/4 at
     jit=40) because the sparser single structure spreads across the
     midline. The tolerance is about absolute displacement relative to
     structure density, not jitter/grid fraction. H7 drops at 160×160
     with jitter≥10 — a density effect, not a crossing-mechanism effect.
     See `grid_size_sweep.py` and H5/H6/H7/H10 Session-38 refinements.
     NEXT PRIORITY: scale n_termites with grid area (150→600) to
     maintain density and test whether the tolerance is truly
     density-dependent.

116. **The exogeneity principle as a formal write-up** — The two-wire
     principle now has nine members. The eighth (exogeneity) is the
     deepest: the signal must be on a wire the system cannot reach. The
     ninth (noise structure, Session 38) refines it: the noise on the
     exogenous wire must match the noise magnitude — temporal averaging
     at moderate noise, spatial correlation at high noise. This
     deserves a standalone concept file or a formal section in CLAUDE.md
     §4, alongside the metric-ceiling (#61), stable_crossed (#65),
     control-arm (#75), one-seed control (#80), and strength-vs-growth
     (#94) rules. The nine members form a taxonomy: (1-3) channel
     separation, (4-5) field separation, (6-7) signal quality, (8)
     exogeneity, (9) noise structure. The progression is from
     structural separation to dynamical unreachability to noise-
     structure matching — each level is a stronger form of the same
     principle.

## From Session 40 (2026-08-26)

120. **The Heisenberg trade-off in control signals — exogeneity vs.
     spatial specificity** — The exogenous D-term (Session 40) is
     less destructive than endogenous but still harmful, and the
     1-seed control leaks because the spatially uniform signal
     creates B_deriv even for a single seed. The signal cannot be
     simultaneously exogenous (unreachable by the system's dynamics)
     and spatially specific (shaped by the spatial arrangement of
     structures). Exogeneity requires independence from system state;
     spatial specificity requires dependence on the spatial structure
     — which IS system state. The focal mode's fixed home center is
     the unique signal that is both (exogenous per-ID + spatially
     specific per-ID). This may be the composition problem's
     fundamental limit: the missing ingredient is a signal that is
     both exogenous and spatially specific, which requires an external
     spatial reference. Could be a standalone concept file.

121. **A spatially structured exogenous signal** — The exogenous
     D-term's 1-seed leak is caused by the signal being spatially
     uniform. A spatially structured exogenous signal — one that is
     highest at the boundary between the two home regions and zero
     elsewhere — could preserve the 1-seed structural guarantee
     while being exogenous. But this requires an external spatial
     reference for the boundary location, which is the same as the
     focal mode's fixed home center. The question is whether a
     boundary-centered exogenous signal (rather than a uniform one)
     can provide anticipatory suppression without the 1-seed leak.
     Could be a sim14 variant: B_deriv driven by a sinusoid modulated
     by a fixed Gaussian centered at the midline.

## From Session 43 (2026-08-29)

123. **The composition optimum ≠ crossing threshold — two phase
     transitions at different densities** — DONE (Session 43).
     The threshold sweep (5 density levels: 100, 125, 150, 175, 200
     on 160×160 at jitter=10, 4 seeds) found H7 transitions gradually
     (0/4 at 3.9/kc → 4/4 at 6.8/kc) — not a sharp percolation
     threshold. The composition optimum (coexist=4/4) peaks at n=150
     (5.9/kc) where H7=2/4, and drops to 1/4 at n=175-200 where
     H7=4/4. The crossing and composition are governed by different
     density regimes: the crossing needs more material than
     composition. At the crossing threshold, structures are large
     enough to interact destructively (merge/fragment); at the
     composition optimum, structures are large enough to consolidate
     but not yet too large to separate. This connects to H1: the
     composition problem is not "make the crossing work for two
     structures" but "find the regime where two different phase
     transitions co-occur." 8-seed robustness at n=800: 8/8 full
     (7/8 clean), 1-seed leak 4/8. See `threshold_sweep.py`.

124. **The n=150 regime — where composition works but the crossing
     doesn't fully fire** — DONE (Session 44).
     At n=150 (5.9/kc), coexist=4/4, clean=4/4, but H7=2/4 and
     stable=1/4. Per-criteria analysis: C1 (stability ≥ 0.90) is the
     sole bottleneck — C2 and C3 pass 20/20 in all seeds, but stability
     hovers at 0.88–0.89 (seeds 42, 123), just below the 0.90 threshold.
     Max consecutive all-3 run is 2 (needs 4). **Composition does not
     require the crossing** — 4/4 coexist with only 2/4 H7. The boundary
     + ID-tagging is sufficient for coexistence at this density. The
     crossing may be necessary for *stable* coexistence (1/4 stable)
     but not for coexistence itself. This weakens H7's claim that the
     crossing is the mechanism for composition. See
     `criteria_analysis.py`.

125. **The destructive interaction at n=175-200 — why does
     composition degrade when the crossing fires?** — DONE (Session 44).
     At n=175 (6.8/kc), H7=4/4 but coexist=1/4. Per-criteria analysis:
     3/4 seeds have l2_outcome="fragmented" — both regions have 4+
     connected components (mean_lc: 6.5, 2.5, 3.5, 6.0; mean_rc: 4.0,
     6.5, 3.2, 4.0). The structures do NOT merge (l2_crossed=4/4);
     they **over-fragment** — the boundary (dual g=0.3) over-splits
     each region. The degradation mode is over-fragmentation, not
     merging or boundary weakness. The boundary strength that enables
     composition at n=150 is too strong at n=175 because the larger
     structure has more surface area for the boundary to split. This
     is a density-dependent expression of the strength-vs-growth
     trade-off (Session 30). See `criteria_analysis.py`.

## From Session 44 (2026-08-30)

126. **Density-dependent boundary strength — should g scale with n?** —
     DONE (Session 45).
     A sweep of 7 (n, g) combos (n=150 at g=0.30, 0.35, 0.40; n=175
     at g=0.15, 0.20, 0.25, 0.30) × 4 seeds on 160×160 at jitter=10
     found lowering g at n=175 RESCUES composition (1/4 → 4/4 coexist)
     while preserving H7 (4/4 at all gains). Raising g at n=150
     DESTROYS composition (4/4 → 0/4). The optimal gain is density-
     dependent: g*≈0.30 at n=150 (5.9/kc), g*≈0.20 at n=175 (6.8/kc).
     n=175 g=0.20 achieves 2/4 full co-occurrence (H7+coexist+stable+
     clean) — the first at moderate density. The 1-seed control leaks
     at n=175 (1/4 at all gains) — density-dependent, not gain-
     dependent. The two-wire principle's 13th member: the signal
     strength must scale with the structure size. See
     `density_gain_sweep.py`.

127. **The crossing as a stability condition, not a composition
     mechanism** — If composition at n=150 (4/4 coexist, 4/4 clean)
     does not require the crossing (2/4 H7), the crossing may be a
     stability condition (stable=1/4 at n=150, 8/8 stable at n=800
     where H7=8/8) rather than the mechanism that produces
     coexistence. This would reframe H7: the crossing is not what
     creates multi-scale composition — the boundary + ID-tagging is.
     The crossing is what makes composition *stable* (persistent
     across perturbation). Test: does perturbation survival
     correlate with H7 at n=150? If the 2/4 H7 seeds survive
     perturbation less than the 2/4 non-H7 seeds, the crossing is
     a stability condition. Cheap: re-run n=150 with perturbation.

128. **The COEXIST_MAX_COMP threshold as a parameter** — The
     fragmented/coexist distinction uses COEXIST_MAX_COMP=3 (1-3
     components per region = coexist; 4+ = fragmented). Is this
     threshold principled or arbitrary? At n=175, seed 256 has
     mean_lc=3.6, mean_rc=3.3 — just above the threshold, classified
     "coexist." If the threshold were 4, 3/4 seeds at n=175 would be
     "coexist." The composition degradation at n=175 may be partly
     an artifact of the COEXIST_MAX_COMP threshold being too
     conservative. A sensitivity sweep of COEXIST_MAX_COMP (3, 4, 5)
     at n=175 would test this. Cheap: re-classify the existing data.

## From Session 45 (2026-08-31)

129. **The g*(n) scaling law — finer resolution and functional form** —
     DONE (Session 46).
     A sweep of 20 (n, g) combos (n=155, 160, 165, 170, 180 × 4 gains each,
     4 seeds × {2, 1} seeds = 160 runs) found the linear fit g* = 0.82 −
     0.0036n (R²=0.75) and the 1/√n fit g* = −0.95 + 15.2/√n (R²=0.77).
     Neither is strong — 4-seed variability produces ±0.02–0.04 uncertainty
     in g* at each n. The 1/√n fit corresponds to Laplace pressure (ΔP =
     2γ/R, R ∝ √n). n=170 g=0.24 achieves 3/4 full co-occurrence — the
     best ever. H7 is 4/4 at all n≥155 except at the density boundary with
     excessive gain. The 1-seed leak at n≥170 (1/4 at all gains) is
     density-dependent and gain-independent. See `gain_scaling_sweep.py`.

130. **Asymmetric g_form and g_persist at n=175** — The density-gain
     sweep used symmetric g_form=g_persist. At n=175, the over-
     fragmentation is from the boundary over-splitting — which B field
     (form or persist) is responsible? An asymmetric sweep (g_form=0.30
     + g_persist=0.15, or g_form=0.15 + g_persist=0.30) would isolate
     which field's strength matters for over-fragmentation. If g_form
     drives fragmentation (it shapes the surface), the 13th member is
     specifically about the formation signal's strength, not the
     persistence signal's.

131. **The 1-seed leak at n=175 — is it fixable?** — The 1-seed control
     leaks at n=175 (1/4 at all gains). The leak is density-dependent
     (the bigger single structure overwhelms the midline) and gain-
     independent. Can a spatially-structured exogenous signal (#121)
     or a finer focal bias (#106) fix it without breaking composition?
     Or is the 1-seed leak at n≥175 the fundamental limit of the
     structure-to-grid ratio (the 12th member)?

## From Session 46 (2026-09-01)

132. **The 8-seed robustness of n=170 g=0.24** — DONE (Session 47).
    n=170 g=0.24 at 8 seeds: l2=8/8, coexist=6/8, stable=3/8, h7=8/8,
    clean=6/8, full=3/8. The 3/4 full from 4 seeds holds at 3/8 with 8
    seeds — the headline is robust, not a small-sample artifact. The 1-seed
    leak drops to 1/8 (was 1/4 at 4 seeds). See
    `robustness_n200_sweep.py`.

133. **The n=200+ plateau — does g* plateau or keep decreasing?** — DONE (Session 48).
    The n=210–230 plateau sweep falsifies the linear scaling and confirms the
    1/√n (Laplace pressure) scaling. At n=230 (the linear's predicted g*=0),
    composition is alive: 3/4 coexist, 3/4 stable at g=0.08. n=220 g=0.06
    and g=0.12 achieve 4/4 full — the first 4/4 full on 160×160. The
    1-seed structural guarantee strengthens at higher density (0/4 at n=230).
    8-seed robustness at n=200 g=0.14: 4/8 full (not a 4-seed artifact).
    See `plateau_sweep.py`.

134. **The 1/√n vs linear distinction — can it be resolved?** — DONE (Session 47).
    The n=200 sweep resolves it: g*(200)≈0.12 matches the 1/√n prediction
    (0.125), not the linear (0.10). g=0.12 achieves 3/4 full; g=0.10
    produces only 2/4 full. The 1/√n (Laplace pressure) scaling is confirmed.
    See `robustness_n200_sweep.py`.

135. **The composition optimum shift — why n=170, not n=150?** — The
     composition optimum shifted from n=150 (Sessions 43–44, 4/4 coexist
     but 2/4 H7) to n=170 (3/4 full, 4/4 H7) to n=220 (4/4 full, Session 48)
     with density-dependent gain. Is this because the crossing threshold
     (~6/kc) and the composition optimum are converging at higher density?
     Or because the gain-scaling fix (13th member) changed the optimum?
     Test: re-sweep n=150 at g=0.24–0.28 (the n=170 optimal) to see if the
     lower-density optimum moves with the gain.

## From Session 48 (2026-09-03)

136. **8-seed robustness at n=220 g=0.06** — DONE (Session 49).
    n=220 g=0.06 at 8 seeds: l2=8/8, coexist=6/8, stable=8/8, h7=8/8, clean=6/8,
    full=6/8, 1s_l2=1/8, 1s_h7=8/8. The 4/4 full from Session 48 holds at
    6/8 — robust but not universal. Two seeds (100, 777) fragment. The
    composition regime has a stochastic boundary (consistent with LSW
    finite-N fluctuations, Wilkinson 2025). See
    `robustness_n220_sweep.py`.

137. **The n=240–250 plateau — where does g* actually hit zero?** — The
     1/√n fit predicts g*(240)≈0.04, g*(250)≈0.02. The linear is already
     falsified. Does g* plateau at a small positive value, or does it
     truly hit zero at some n? The LSW theory analogy says g* should hit
     zero when the structure fills the grid (the droplet dissolves into
     the continuous phase). Test: sweep n=240, 250 at g=0.02–0.08.

138. **The 1-seed structural guarantee at n=230 (0/4) — why does it
     strengthen?** — The 1-seed leak was 1/4 at n=200 and 1/8 at n=170
     (8 seeds), but drops to 0/4 at n=230. More termites produce more
     material, but the focal bias + curvature channel concentrate it
     more effectively on the correct side. Is this because the bigger
     single structure is more strongly confined by the curvature channel
     (more material = more curvature = more routing)? Or because the
     focal bias is more effective with more agents (more agents following
     the home center = tighter concentration)? Inspect the 1-seed runs
     at n=230 vs n=200: compare B_max, structure extent, and mean
     curvature. Cheap: analysis of committed JSON.

139. **Asymmetric g_form and g_persist at n=220** — DONE (Session 49).
     The asymmetric sweep found **neither B field is load-bearing — the
     symmetric balance is the optimum.** sym006 (0.06, 0.06) = 4/4 full;
     form012 (0.12, 0.06) = 2/4 full (stability degrades);
     persist012 (0.06, 0.12) = 1/4 full (stability degrades worse);
     sym012 (0.12, 0.12) = 4/4 full. The 26th mechanism: the
     formation-persistence balance. The two-wire principle's 14th member:
     formation and persistence must be balanced, not just separated. See
     `robustness_n220_sweep.py`.

## From Session 49 (2026-09-04)

140. **The n=240–250 plateau (continuation of #137)** — Where does g*
     actually hit zero? The 1/√n predicts g*(240)≈0.04, g*(250)≈0.02.
     At n=240–250 the structures fill most of the grid; the 1-seed
     structural guarantee should be at its strongest. Does g* plateau at
     a small positive value, or does it truly hit zero?

141. **The stochastic composition boundary — what distinguishes the 2/8
     fragmenting seeds?** At n=220 g=0.06, seeds 100 and 777 produce
     "fragmented" outcomes while the other 6 produce "coexist." Is it
     nucleation trajectory (initial deposit scatter) or dynamical
     (criterion flickering)? Inspect the 2 fragmenting seeds' histories
     vs the 6 coexisting seeds: where does l2_outcome diverge?

142. **Finer asymmetric resolution — is there an asymmetric config that
     matches sym006?** The asymmetric sweep tested (0.12, 0.06) and
     (0.06, 0.12). A finer sweep (0.08, 0.06), (0.06, 0.08), (0.10,
     0.06), (0.06, 0.10) might find an asymmetric config that preserves
     4/4 full — or confirm that only symmetric configs achieve it.
