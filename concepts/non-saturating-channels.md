---
status: active
formed: "Session 13"
connected_to: "stigmergic consolidation, environmental physics coupling, stigmergy, H7, H11, multi-rate environment, niche construction"
topic: "non-saturating stigmergic channels — geometry, humidity thresholds, and crowding as the biological grounding for H11"
key_findings: "Real termite construction is guided by THREE non-saturating, action-based channels rather than by a saturating pheromone field: (1) surface CURVATURE — Calovi et al. 2019 (Phil Trans R Soc B) disambiguated curvature from inclination and height across three orientations and found curvature is the 'consistent and sole driver' of both early exploration and soil displacement in Macrotermes michaelseni; convex regions are excavated, concave regions filled, and the SAME cue elicits OPPOSING actions depending on the termite's loaded/seeking state — a state-gated, non-saturating rule. (2) HUMIDITY THRESHOLDS — Carey/Bardunias/Nagpal/Werfel 2021 validated with a robot that termites deposit at the EDGE of the high-humidity zone, a threshold-triggered deposition rule; wind disturbing the bubble closes the tunnel. (3) CROWDING/INACTIVITY — Xiao et al. 2026 (arXiv:2607.19594) frame inactivity under confinement as 'distributed inhibition that prevents saturation.' These are exactly the density-cap / refractory / directional-bias channels H11 prescribes, and they are biological mechanisms, not modeling choices. The ACO literature (MAX-MIN Ant System, Stützle & Hoos 2000) bounds the CUE rather than the ACTION; H11's distinction (act on the action, not the cue) is novel within ALife but corroborated by termite biology, which evolved non-saturating geometric channels in preference to a cement pheromone that no study has yet identified."
---

# Non-Saturating Stigmergic Channels

**Status:** Active — formed Session 13
**Connected to:** [stigmergic consolidation](stigmergic-consolidation.md), [environmental physics coupling](environmental-physics-coupling.md), [stigmergy](stigmergy.md), H7, H11, [multi-rate environment](multi-rate-environment.md), [niche construction](stigmergy-vance-notes.md)

## The Concept

[H11](../hypotheses/hypotheses.md) predicts that the trace→actor crossing needs negative feedback
through a **channel that does not saturate** — acting on the *action* (deposit probability, geometry)
rather than on the *cue* field the agents read. This file supplies the biological grounding: real
termites appear to have evolved exactly such channels, and the saturating "cement pheromone" that
the classic Grassé model assumes is increasingly in doubt. Three independent lines of experimental
evidence converge on non-saturating, action-based feedback.

## 1. Surface curvature — the geometric channel (Calovi et al. 2019)

Calovi, Bardunias, Carey, Turner, Nagpal & Werfel (Phil Trans R Soc B, 2019; DOI 10.1098/rstb.2018.0374)
ran controlled field experiments on *Macrotermes michaelseni* in Namibia. They 3D-printed a test
surface with continuously varying curvature (concave, convex, flat), coated it with nest soil, and
mounted it in **three orientations** (horizontal, 45°, vertical) to disambiguate curvature from
inclination and geotaxis.

**Finding:** "curvature is the consistent and sole driver, among the measured geometric candidates,
of both early termite positioning and construction activity." Soil displacement correlated with
curvature across all three orientations; inclination and height did not. Concave (high positive
curvature) regions attract deposition; convex regions attract excavation.

**Why this matters for H11:**

- **Curvature is non-saturating.** Unlike a pheromone field whose deposit response flattens above
  φ≈1, curvature is a geometric quantity that the structure carries regardless of how much
  pheromone is present. You cannot "saturate" curvature by adding more deposits — each deposit
  *changes* the curvature, so the channel stays responsive. This is precisely the property H11
  says the crossing requires.
- **The rule is action-based and state-gated.** The same high-curvature cue elicits *opposing*
  actions — excavation OR deposition — depending on whether the termite is loaded with soil or
  seeking a digging site. The cue does not monotonically increase deposit probability; it routes
  the agent's current action. This is the "act on the action, not the cue" prescription, observed
  in the animal.
- **It is a genuine negative feedback.** Filling a concavity reduces its curvature, which
  removes the cue for further filling — a self-limiting loop. Excavating a convexity reduces its
  convexity, removing the cue for further excavation. The geometry carries its own inhibition.
- **It supplies the "directional bias" H11 listed.** Deposition preferentially at concavities IS
  building along existing wall edges rather than onto their centers.

The paper's own framing: "These two possibilities represent computations the liquid/solid brain
can perform, amplifying or smoothing out initial irregularities in tunnel walls." Amplify =
positive feedback (a concavity fills, deepening the concavity elsewhere); smooth = negative
feedback (a concavity fills and disappears). Both are mediated by the same non-saturating
geometric channel.

## 2. Humidity thresholds — the template channel (Carey et al. 2021; Bardunias et al. 2020)

Carey, Bardunias, Nagpal & Werfel (Front Robot AI, 2021; DOI 10.3389/frobt.2021.645728) tested the
"humidity template" hypothesis with a physical robot: termites deposit wet soil at the **edge** of
the high-humidity zone that extends from a tunnel mouth. The robot, controlled only by a local
humidity sensor, replicated the behavior — extending a semi-enclosed area in still air and closing
it off when a fan disturbed the humidity bubble.

**Why this matters for H11:**

- **Threshold-triggered, not graded.** Deposition fires at a humidity boundary (a level
  crossing), not as a saturating function of humidity level. This is the "refractory / threshold"
  channel — a discrete, non-saturating trigger.
- **The cue and the action are decoupled in the right way.** Humidity is the cue, but the
  feedback (depositing wet soil *extends* the humidity zone, moving the boundary) acts on the
  *geometry* of the boundary, not by raising the humidity level everywhere. Adding wet soil does
  not saturate a humidity response; it relocates a threshold.
- **External perturbation reroutes the action.** Wind shrinks the bubble → the same rule now
  *closes* the tunnel instead of extending it. A single non-saturating rule produces opposite
  morphological outcomes under different external conditions — a multi-rate-environment (H4)
  coupling, mediated by a non-saturating channel.

## 3. Crowding / inactivity as distributed inhibition (Xiao et al. 2026)

Xiao, Wu, Lim, Su, Bardunias, Chatterjee & Bhamla (arXiv:2607.19594, Jul 2026, "Sensing, Traffic,
and Construction in Termites") review the coupled sensing-traffic-construction loop in subterranean
termites. Their framing of crowding is directly H11-relevant: "Under confinement, inactivity can
act as a form of distributed inhibition that prevents saturation." Congestion at an excavation
front generates queues that *redirect* workers to lateral digging (tunnel widening, branching)
rather than continuing to pile in.

**Why this matters for H11:**

- **Crowding is a density cap on action.** A cell that is "full" of termites suppresses further
  entry — a refractory period on the spatial slot. This is the "density cap" channel, the third
  mechanism H11 listed.
- **It acts on the action (where the termite goes), not on a cue field.** The termite does not
  read a saturating "crowding pheromone"; it physically cannot proceed, so it does something else.
  The inhibition is mechanical, not chemical, and therefore cannot saturate.

## The convergence, and what it implies

Three channels — curvature (geometry), humidity (threshold), crowding (mechanical density) — each
non-saturating, each acting on the action rather than the cue. Real termite construction appears to
rely on these and NOT on a saturating cement pheromone, which despite 60+ years of search
**"no cement pheromone has yet been identified"** (Calovi et al. 2019). The biological system
evolved away from the saturating channel H11 flags as self-defeating.

**This is strong external support for H11.** The hypothesis was derived from a bug fix in our own
code (two failed feedback attempts, both through the saturating pheromone field). The termite
literature independently shows that the channels real termites use are precisely the non-saturating
ones H11 prescribes, and that the saturating channel (cement pheromone) is the one biology may not
use at all. H11 may be less a rediscovery of ACO (which bounds the cue) and more a rediscovery of
what termites actually do.

**Implication for sim08 (the cheap test):** the density cap / curvature rule / humidity threshold
are not ad hoc additions chosen to make the crossing fire — they are the mechanisms the model
organism actually uses. sim06 used a saturating pheromone response because the lineage (Deneubourg
→ Bonabeau → Ladley) assumed a cement pheromone. The biological evidence now says that assumption
is likely wrong, and H11 explains *why* it fails: a saturating cue channel cannot express the
spatial contrast consolidation needs.

## Connection to the saturating response curve (H11's mechanism)

The deposit rule in sim06/sim07 is `p = DEPOSIT_BASE + DEPOSIT_GAIN · φ/(1+φ)`, flat above φ≈1.
Curvature feedback is the complementary case: the "response" to curvature is a *routing* decision
(excavate vs deposit, depending on state), not a saturating probability. The curvature channel
has no "flat above threshold" region — it stays discriminating because it is redefined by each
action. This is the formal distinction: **a saturating channel maps cue level → action intensity
and compresses; a non-saturating channel maps cue geometry → action selection and preserves
contrast.**

## Criticisms

- **Correlation, not mechanism.** Calovi et al. establish correlation of construction with
  curvature, disambiguated from confounds, but the mechanism by which termites *assess* curvature
  "is unknown, but presumably involves a combination of antennation and proprioception." We know
  they respond to it; we do not know the sensing transduction.
- **The three channels may not be independent.** Curvature, humidity, and crowding are coupled
  in real mounds (concavities hold humid air; narrow concavities crowd). A simulation that adds
  only one may not reproduce the full dynamics, and separating their effects is an open
  experimental problem in the biology itself.
- **State-gating complicates replication.** The same curvature cue elicits excavation OR
  deposition depending on the termite's loaded state. A simulation must model that state to
  reproduce the effect — a richer agent than sim06's deposit-only rule.
- **No cement pheromone identified ≠ no chemical cue.** Absence of identification is not proof
  of absence; other chemical cues (trail pheromones, CO₂) may yet play roles. The claim is that
  the *saturating deposit-response* channel is not the primary one, not that chemistry is absent.

## Empirical Evidence

- **Calovi, Bardunias, Carey, Turner, Nagpal & Werfel (2019)**, Phil Trans R Soc B 374:20180374.
  Field experiments on *M. michaelseni*; curvature is the sole consistent driver of construction
  across three surface orientations, disambiguated from inclination and height. DOI 10.1098/rstb.2018.0374
- **Carey, Bardunias, Nagpal & Werfel (2021)**, Front Robot AI 8:645728. Robot validation of the
  humidity-template deposition rule; threshold-triggered, wind-rerouted. DOI 10.3389/frobt.2021.645728
- **Bardunias et al. (2020)** — the humidity-template hypothesis in *M. michaelseni* mounds.
- **Xiao, Wu, Lim, Su, Bardunias, Chatterjee & Bhamla (2026)**, arXiv:2607.19594. Review framing
  crowding/inactivity as distributed inhibition preventing saturation; curvature-biased
  excavation/deposition across subterranean and mound-building taxa.
- **Werfel, Petersen & Nagpal (2014)**, Science 343:754–758. Termite-inspired construction robots
  using only local sensing; inverse-problem design with threshold-triggered deposition.
  DOI 10.1126/science.1245842
- **Reina & Marshall (2022)**, PLoS Comput Biol 18:e1010090. Negative feedback in social-insect
  foraging suppresses *variance* (not just convergence) in small populations — an additional
  function for non-saturating inhibitory signals. DOI 10.1371/journal.pcbi.1010090
- **Stützle & Hoos (2000)**, MAX-MIN Ant System. Bounds the cue τ ∈ [τ_min, τ_max] to prevent
  stagnation — the closest ACO prior art, but acts on the cue field, not the action. H11's
  distinction: when the response saturates, cue-bounding is insufficient; action-based feedback
  is needed.

## Open Questions

- Does a minimal simulation with a curvature-based deposit rule (concavity → fill, convexity →
  excavate, state-gated) consolidate where sim06's saturating-pheromone rule fragmented? This is
  the direct, cheap test of H11 and is candidate sim08.
- Can the three channels be separated in simulation (curvature alone, humidity alone, crowding
  alone) to identify which is load-bearing for the crossing?
- Is the state-gating (loaded vs seeking) essential, or does a simpler "deposit at concavity,
  excavate at convexity" rule without state suffice to consolidate?
- How does curvature feedback relate to the directed-transport candidate (environmental-physics
  coupling)? Curvature *is* a form of directed geometry — it may subsume the "directed transport"
  refinement H7 carries.

## Cross-References

- [[hypotheses/H11]] — the saturating channel hypothesis; this file is its biological grounding
- [[hypotheses/H7]] — the trace→actor crossing; non-saturating channels are the candidate
  mechanism the crossing needs
- [[concepts/stigmergic-consolidation]] — names the negative-feedback gap; this file supplies the
  biological channels that fill it
- [[concepts/environmental-physics-coupling]] — the directed-transport candidate; curvature may
  be its geometric minimal form
- [[concepts/stigmergy]] — the base mechanism; the cement pheromone assumption is in doubt
- [[concepts/multi-rate-environment]] — humidity template's wind-perturbation is a multi-rate
  external driver acting through a non-saturating channel
