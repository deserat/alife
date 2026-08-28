---
status: active
formed: "Session 42"
connected_to: "non-saturating-channels, stigmergic-consolidation, stigmergy, autopoiesis, H5, H6, H7, H10, H11"
topic: "the two-wire principle — a general design law for self-organizing systems: when two functional properties are carried on the same wire, saturating one destroys the other"
key_findings: "Twelve members across Sessions 23–41 form a progression: (1-3) channel separation, (4-5) field separation, (6-7) signal quality, (8) exogeneity, (9) noise structure, (10) endogeneity, (11) spatial specificity, (12) structure-to-grid ratio. Each level is a stronger form of the same principle: the signal must not be reachable by the dynamics it controls, must be specific to where it acts, and the structure must be small enough for the boundary to separate it. The principle applies to stigmergic channels (pheromone saturation), boundary design (feedback-loop amplification), control signals (exogeneity vs spatial specificity), and finite-size geometry (structure-to-grid ratio). The deepest form (the Heisenberg trade-off, Sessions 40-41): the signal cannot be simultaneously exogenous (unreachable by dynamics) and spatially specific (shaped by spatial structure) — because spatial specificity IS system state. The focal mode's fixed home center is the unique signal that is both exogenous (per-ID) and spatially specific (per-ID) — an external spatial reference."
---

# The Two-Wire Principle

**Status:** Active — formed Session 42
**Connected to:** [non-saturating channels](non-saturating-channels.md), [stigmergic consolidation](stigmergic-consolidation.md), [stigmergy](stigmergy.md), [autopoiesis](autopoiesis.md), H5, H6, H7, H10, H11

## The Principle

> **When two functional properties are carried on the same wire, saturating one destroys the other.**

A "wire" is any channel that carries a signal — a pheromone field, a boundary field, a spatial
cue, a control signal. When two properties the system needs (e.g., spatial contrast and
feedback suppression) travel on the same wire, saturating one (driving it high enough that it
can no longer distinguish signal from noise) destroys the other. The cure is **separation**:
put the two properties on separate wires, so each can be tuned independently.

This principle emerged from 19 sessions of simulation work (Sessions 23–41) on the trace→actor
crossing (H7) and the composition problem (H10). Each session found a new instance of the same
principle, progressively deepening it from structural separation to dynamical unreachability to
the Heisenberg trade-off.

## The Twelve Members

### Level 1: Channel Separation (Sessions 23–26)

**Member 1 — The two-wire principle (Session 23, queued-topic #73).** The feedback signal
(adjusting deposit probability) and the spatial signal (where to deposit) travel on the same
wire in cue-based stigmergic channels: the pheromone field → deposit probability → spatial
contrast. Saturating the deposit probability (driving it to 1.0 everywhere) destroys the
spatial contrast. In action-based channels, the routing decision (which direction to move)
and the deposit gain (how hard to deposit) are on separate wires — saturating the gain leaves
the routing intact. *A self-defeating channel is one where the feedback signal and the spatial
signal travel on the same wire.*

**Member 2 — The self-cancelling inhibitor (Session 26, queued-topic #82).** A long-range
inhibitor derived from a local activator (material → smoothed shadow) must not self-inhibit.
The naive form (just the shadow) is highest AT the structure and kills all building. The
difference form (`I = max(0, far_smoothed − local)`) isolates the distant signal from the
local. *The distant signal and the local signal must travel on separate wires.* Spatial analog
of Member 1.

**Member 3 — The memory-specificity trade-off (Session 27-28, queued-topic #86).** An
autopoietic boundary with memory (growth/decay dynamics) is more stable (4/4 vs 1/4) but less
specific (1-seed control fires 2/4). The memory that enables persistence also creates false
boundaries. *Persistence and specificity must travel on separate wires.*

### Level 2: Field Separation (Sessions 33–34)

**Member 4 — The dual mode (Session 33, queued-topic #101).** A single B field cannot
simultaneously achieve formation (needs gradient, fast response) and persistence (needs
plateau, slow decay). Two B fields with separate growth/decay dynamics — B_form (gradient,
2× decay) for formation and B_persist (binary, 1× decay) for persistence — break the
trade-off: stability improved from 0/4 to 3/4 at the same L2 and clean rates. *Formation and
persistence must travel on separate B fields.*

**Member 5 — Agent distribution (Session 34, queued-topic #93).** The boundary signal
(co-presence → B) and the spatial noise (agent wander) were on the same wire — agents wandering
across the torus deposit material in both halves, saturating co-presence everywhere.
Movement_bias (focal-point attraction) separates them by concentrating each ID's material,
making the boundary signal sharper. Full co-occurrence jumped from 1/4 to 4/4. *The boundary
signal and the agent distribution must travel on separate axes.*

### Level 3: Signal Quality (Sessions 35–36)

**Member 6 — Movement-wire decoupling (Session 35, queued-topic #105).** The boundary mode
(agents turn back at high B) uses the B field for both deposit suppression AND agent movement —
a stigmergic feedback loop (B → movement → co-presence → B) that over-amplifies B (b_max 70–203
vs 30–50 for focal) and fragments all structures. The focal mode succeeds because the movement
target (fixed home center) is independent of B. *Deposit suppression and agent movement must
travel on separate signals.*

**Member 7 — Signal quality on the separate wire (Session 36, queued-topic #109).** The zone
mode gives agents a separate sensory channel (own-ID material for zone ID, B for suppression) —
the stigmergic loop IS broken (b_max 50.2 ≈ none's 47.9) but composition is WORSE than no
restriction (0/4 vs 2/4). The separate wire exists but carries a noisy signal (dilated own-ID
material is diffuse and endogenous). *A separate wire with a noisy signal doesn't recover the
function. Breaking the feedback loop is necessary but not sufficient — the replacement signal
must also be precise enough to concentrate agents effectively.*

### Level 4: Exogeneity (Session 37)

**Member 8 — Exogeneity (Session 37, queued-topic #113).** The focal mode's advantage is
exogeneity (loop-breaking), not precision (noise-free). A noisy exogenous signal (jitter=10,
12.5% of grid) preserves 4/4 full co-occurrence. The decisive comparison: jitter=40 (exogenous,
b_max=49.0) produces 3/4 coexist; zone mode (endogenous, b_max=50.2) produces 0/4 — at nearly
identical B magnitude, the exogenous signal outperforms the endogenous signal on every axis.
*The signal must not only be on a separate wire — it must be on a wire the system cannot reach.
Exogeneity is the load-bearing property, not precision.*

### Level 5: Noise Structure (Session 38)

**Member 9 — Noise structure on the exogenous wire (Session 38, queued-topic #114).** Exogeneity
is necessary but not sufficient — the noise structure (temporal vs spatial correlation) must
match the noise magnitude. At jitter=10 (12.5%): per-step jitter (temporally averaged) produces
4/4; per-agent jitter (spatially correlated) produces 1/4 — temporal averaging wins. At
jitter=20 (25%): per-step produces 1/4; per-agent produces 3/4 + 4/4 stable — spatial
correlation wins. The crossover is non-monotonic: at moderate noise, temporal averaging
(error cancellation) is better; at high noise, spatial correlation (consistency) is better.
*The noise structure on the exogenous wire must match the noise magnitude.*

### Level 6: Endogeneity (Session 39)

**Member 10 — Endogenous anticipatory signals are self-defeating (Session 39, queued-topic #103).**
An endogenous D-term (B_deriv from co-presence rate of change) is destructive without focal bias:
stable drops from 3/4 to 0/4 at g_deriv=0.1. The signal reads the system's own co-presence
(endogenous), creating a stigmergic feedback loop: cp rises → B_deriv rises → suppression
increases → structures stop growing → cp falls → B_deriv decays → suppression drops → structures
grow again → cp rises. This oscillation amplifies rather than damps. *An endogenous anticipatory
signal is self-defeating — the feedback loop amplifies the oscillation it tries to damp.*

### Level 7: Spatial Specificity of the Exogenous Signal (Session 40)

**Member 11 — Spatial specificity (Session 40, queued-topic #117).** An exogenous D-term
(external sinusoid) is less destructive than endogenous (stable 3/4→1/4 vs 3/4→0/4) but still
harmful. The 1-seed control leaks (2/4 at g_deriv=0.05) because the spatially uniform exogenous
signal creates B_deriv even for a single seed. *The exogenous signal must also be spatially
specific — non-zero only where two structures interact. Exogeneity alone is not enough; the
signal must be both unreachable by dynamics AND shaped by the spatial arrangement.*

This is the **Heisenberg trade-off**: the signal cannot be simultaneously exogenous (unreachable
by the system's dynamics) and spatially specific (shaped by the spatial structure) — because
spatial specificity IS system state. The focal mode's fixed home center is the unique signal
that is both exogenous (per-ID, set at initialization) and spatially specific (per-ID, at the
correct location). It is an **external spatial reference** — the composition problem's missing
ingredient.

### Level 8: Structure-to-Grid Ratio (Session 41)

**Member 12 — Structure-to-grid ratio (Session 41, queued-topic #119).** The previous eleven
members all concerned signal properties (channel separation, field separation, exogeneity,
noise structure). The twelfth is about a geometric property: the structure's physical extent
relative to the grid's half-width. At 160×600 (same density as 80×150), the 1-seed structural
guarantee leaks (2/4 at jit=10, 4/4 at jit=20) because the bigger single structure (~2700 cells
vs ~1700) overwhelms the midline even with focal bias. *The structural guarantee depends on
structure-to-grid ratio, not just signal properties. The structure must be small enough for the
boundary to separate two copies.*

## The Taxonomy

| Level | Member | Session | Property | Core claim |
|-------|--------|---------|----------|------------|
| 1 | Two-wire | S23 | Channel | Feedback and spatial signals on separate wires |
| 2 | Self-cancelling inhibitor | S26 | Channel | Distant and local signals on separate wires |
| 3 | Memory-specificity | S27-28 | Channel | Persistence and specificity on separate wires |
| 4 | Dual mode | S33 | Field | Formation and persistence on separate B fields |
| 5 | Agent distribution | S34 | Field | Boundary and agent movement on separate axes |
| 6 | Movement-wire decoupling | S35 | Signal | Deposit suppression and movement on separate signals |
| 7 | Signal quality | S36 | Signal | A separate wire with a noisy signal doesn't recover the function |
| 8 | Exogeneity | S37 | Dynamics | The signal must be on a wire the system cannot reach |
| 9 | Noise structure | S38 | Dynamics | Temporal vs spatial correlation must match noise magnitude |
| 10 | Endogeneity | S39 | Dynamics | An endogenous anticipatory signal is self-defeating |
| 11 | Spatial specificity | S40 | Dynamics | The exogenous signal must also be spatially specific |
| 12 | Structure-to-grid ratio | S41 | Geometry | The structural guarantee depends on geometric, not signal, properties |

## The Progression

The twelve members form a deepening progression:

1. **Structural separation** (Members 1-3): the two properties are on the same physical
   channel; separate them into different channels.
2. **Field separation** (Members 4-5): the two properties are in the same field; give them
   separate fields with independent dynamics.
3. **Signal quality** (Members 6-7): the replacement signal on the separate wire must be
   precise enough to carry the function.
4. **Dynamical unreachability** (Members 8-9): the signal must not be reachable by the
   system's own dynamics — exogeneity is the load-bearing property.
5. **Anticipatory feedback** (Members 10-11): an anticipatory signal derived from the system's
   state is self-defeating; even an exogenous anticipatory signal must be spatially specific.
6. **Geometric limits** (Member 12): the structure must be small enough for the boundary to
   separate it — a finite-size effect beyond signal properties.

Each level is a **stronger form** of the same principle: the signal must not be reachable by
the dynamics it controls, must be specific to where it acts, and the structure must be small
enough for the boundary to separate it.

## The Heisenberg Trade-off

The deepest form (Members 10-11) is a **Heisenberg trade-off**: the signal cannot be
simultaneously exogenous (unreachable by the system's dynamics) and spatially specific (shaped
by the spatial structure). Exogeneity requires independence from system state; spatial
specificity requires dependence on the spatial arrangement — which IS system state.

The **focal mode's fixed home center** is the unique signal that resolves this trade-off: it
is exogenous (set at initialization, per-ID) and spatially specific (at the correct location,
per-ID). It is an **external spatial reference** — the composition problem's missing
ingredient. No endogenous signal can be both; no spatially uniform exogenous signal can be
both. The focal mode is the gold standard because it provides an external reference the system
cannot reach.

## Cross-Domain Connections

### Stigmergic channels and ACO
In Ant Colony Optimization, the pheromone trail IS both the feedback signal and the spatial
signal — but ACO's response function (τ^α · η^β) is unbounded, so it never saturates. The
two-wire principle's self-defeating channel is the saturating form (`φ/(1+φ)`) — ACO avoids it
by using an unbounded response. MAX-MIN Ant System (Stützle & Hoos, 2000) explicitly bounds
τ ∈ [τ_min, τ_max] — the same cap the hybrid mode uses (Member 4).

### Developmental morphogen gradients
Morphogen gradients carry positional information (spatial signal) AND feedback
(concentration-dependent gene expression) on the same wire — and morphogen saturation is a
known developmental pathology. The two-wire principle predicts: morphogen saturation is
self-defeating because it puts the spatial signal and the feedback signal on the same wire.
The self-cancelling inhibitor (Member 2) is the spatial analog of lateral inhibition in neural
development — the inhibitory interneuron receives excitation from the very cells it inhibits,
and the circuit architecture separates self-excitation from lateral inhibition.

### Control theory
The strength-vs-growth trade-off (Session 30-32) maps to the gain margin problem: the
boundary's inh_gain is the feedback gain — too low → structures merge, too high → growth
killed. The two-wire principle says the fix is not to tune the gain but to separate the wires.
The PID decomposition (Sessions 39-40) is a temporal version: the P (proportional), I
(integral), and D (derivative) terms must travel on separate fields with separate dynamics.

### Statistical physics
The structure-to-grid ratio (Member 12) is a finite-size effect: the composition problem has a
thermodynamic limit (the structure must be small relative to the container for the boundary to
separate two copies). The Heisenberg trade-off is the composition problem's fundamental limit:
the missing ingredient is a signal that is both exogenous and spatially specific, which requires
an external spatial reference — just as a phase transition requires an external thermodynamic
variable.

## Criticisms

- **All twelve members come from one simulation family** (sim09–sim14, Grassé stigmergy on a
  2D grid). The principle may be an artifact of this particular architecture. Cross-validation
  in a different system (e.g., reaction-diffusion, agent-based chemostat) would strengthen it.
- **The taxonomy is retrospective.** Each member was discovered by finding a new failure mode,
  not by predicting it from the principle. The principle's predictive power is untested — can it
  predict the next failure mode before the simulation reveals it?
- **The Heisenberg trade-off is claimed, not proven.** "The signal cannot be simultaneously
  exogenous and spatially specific" is a strong claim. The focal mode resolves it — but the
  claim that no other signal can is based on exhaustion of alternatives within one simulation
  family, not a proof.
- **The twelfth member (geometry) may not belong.** Members 1-11 are about signal properties;
  Member 12 is about a geometric property. The connection ("the structure must be small enough
  for the boundary to separate it") is real but is it the same principle, or a different
  limitation?

## Empirical Evidence

Each member was demonstrated by a simulation that showed the failure mode, then the fix:
- Member 1: sim06/sim09 cue vs action (Session 22-23) — saturating cue fragments, action crosses
- Member 2: sim11 passive vs self-cancelling inhibitor (Session 26)
- Member 3: sim12 memory vs no-memory (Session 27)
- Member 4: sim14 dual vs single B field (Session 33) — stable 0/4 → 3/4
- Member 5: sim14 movement_bias 0.0 → 0.3 (Session 34) — full co-occurrence 1/4 → 4/4
- Member 6: sim14 boundary vs focal mode (Session 35) — b_max 104 vs 33
- Member 7: sim14 zone mode (Session 36) — loop broken but signal noisy
- Member 8: sim14 jitter sweep (Session 37) — exogenous outperforms endogenous
- Member 9: sim14 per-step vs per-agent jitter (Session 38) — non-monotonic crossover
- Member 10: sim14 PID D-term (Session 39) — endogenous anticipation self-defeating
- Member 11: sim14 exogenous D-term (Session 40) — spatially uniform signal leaks 1-seed
- Member 12: sim14 density sweep (Session 41) — 1-seed leaks at 160×600 (same density)

Determinism verified at every level. 1-seed controls at every level. Full data in
`simulations/sim14_heterogeneous_agents/output/`.
