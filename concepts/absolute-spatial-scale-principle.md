---
status: active
formed: "Session 85"
connected_to: "extensive-intensive-signals, two-wire-principle, gompertz-logistic-transition, H5, H7, H10"
topic: "the absolute-spatial-scale principle — any mechanism acting through an absolute spatial scale converts density-dependence into n-dependence; local scales are scale-invariant, global scales are not"
key_findings: "The fill is density-dependent without any absolute-spatial-scale mechanism (66.25% ≈ 66.49% ≈ 64.26%, spread 2.23% at 23.4/kc across 80×80/160×160/320×320) and n-dependent with the focal bias (48.33% → 31.58% → 24.95%, spread 23.38%). The focal bias (1-cell steps toward a fixed home center — a GLOBAL absolute spatial scale) was the sole source of n-dependence. The curvature channel's local operations (1-cell Laplacian, 1-cell Moore dilation, 0.2-cell diffusion — LOCAL absolute scales) are scale-invariant at matched density. LOCAL absolute scales (acting on local shape) are scale-invariant; GLOBAL absolute scales (distance-dependent, acting on position) are not. This maps onto gauge theory: local interactions are renormalizable; global references are not. The 50th mechanism (fill depends on absolute n) and the 53rd mechanism (boundary converts density-dependence into n-dependence) are both consequences of the absolute-spatial-scale principle — the 53rd was falsified (Session 84) because at low gain the boundary is negligible; the 50th holds because the focal bias is a global absolute spatial scale. Session 95: the 30th ceiling shifts with grid size — on 80×80 stability persists at 64–76% fill (23–35pp above Moore), confirming the 30th is about absolute structure size vs the boundary's spatial scale (dilation radius 8 cells), not fill fraction. The 2.93pp gap on 160×160 is coincidental. Session 96: the 30th ceiling is the structure-to-boundary RATIO — varying the dilation radius on 160×160 shifts the ceiling (r=4 → ~40%, r=8 → ~43.6%, 80×80 r=8 → ~64–76%); the degradation mode shifts over-splitting → under-splitting = spatial KJMA crossover. Session 97: the 30th ceiling SATURATES at ~43% for r ≥ 8 on 160×160 — r=10 (6.25%) and r=12 (7.5%) give the same ceiling as r=8 (5%); the over-splitting → under-splitting crossover requires r/grid ≥ 10% (not 5–10%); the 80×80 r=8 under-splitting is confounded by the 50th mechanism (grid-size effect); the 30th ceiling is NOT the matched-granularity point (L/r = 7–18 at the ceiling, far from 1) — it is dynamical (suppression vs growth rate), not geometric (L=r)."
---

# The Absolute-Spatial-Scale Principle

## The Concept

In a stigmergic system on a grid, mechanisms can act through **absolute spatial
scales** — fixed distances measured in cells, not in fractions of the grid.
A 1-cell step, an 8-cell dilation radius, a fixed home center at grid/4 — these
are absolute scales. Their effectiveness depends on the grid's linear size: a
1-cell step covers 1/80 of an 80×80 grid but 1/320 of a 320×320 grid.

The principle: **any mechanism acting through an absolute spatial scale converts
density-dependence into n-dependence.** At matched density (same n/grid²), the
mechanism is less effective on a larger grid because the same absolute distance
covers a smaller fraction of the grid. The fill — which would be density-dependent
without the mechanism — becomes n-dependent (decreasing with grid size at matched
density).

The refinement: **LOCAL absolute scales are scale-invariant; GLOBAL absolute
scales are not.** A 1-cell Laplacian stencil acts on local shape — it measures
curvature at a point, which is the same regardless of grid size. A 1-cell Moore
dilation acts on local connectivity, also grid-size-independent. These LOCAL
scales produce the same result at the same density on any grid. But a GLOBAL
absolute scale — a fixed home center at grid/4, with agents stepping 1 cell
toward it — acts on *position*, not shape. The same 1-cell step covers less of
the distance to home on a larger grid, making the mechanism less effective.

## Empirical Evidence

### Session 85: the fill is density-dependent without the focal bias

At 23.4/kc density with NO focal bias (movement_bias=0) and NO boundary (g=0):

| Grid | n | Fill% |
|------|---|-------|
| 80×80 | 150 | 66.25% |
| 160×160 | 600 | 66.49% |
| 320×320 | 2400 | 64.26% |

Spread = 2.23% — approximately the same across grid sizes. The curvature
channel's local operations (1-cell Laplacian, 1-cell Moore dilation, 0.2-cell
diffusion) produce the same fill at the same density regardless of grid size.

### Session 85: the fill is n-dependent with the focal bias

At 23.4/kc density with focal bias (movement_bias=0.3) and NO boundary (g=0):

| Grid | n | Fill% |
|------|---|-------|
| 80×80 | 150 | 48.33% |
| 160×160 | 600 | 31.58% |
| 320×320 | 2400 | 24.95% |

Spread = 23.38% — an order of magnitude larger. The focal bias (1-cell steps
toward a fixed home center) is less effective on larger grids: the same 1-cell
step covers a smaller fraction of the distance to home.

### The 2.23% vs 23.38% comparison

The 10× difference (2.23% without focal bias vs 23.38% with) shows the focal
bias accounts for >90% of the n-dependence. The residual 2.23% may be 2-seed
noise (320×320 had only 2 seeds) or a small residual from the 1-cell step size
(a LOCAL absolute scale that is *approximately* but not *exactly* scale-invariant
at finite grid sizes).

## The LOCAL vs GLOBAL Distinction

### LOCAL absolute scales (scale-invariant)

A local absolute scale acts on the **shape** of the field at a point:

- **1-cell Laplacian** (curvature computation): measures the second derivative
  of the material field at a point. The curvature at a point depends on the
  local shape, not the grid size. At matched density, the local shape is the
  same on any grid.

- **1-cell Moore dilation** (co-presence computation): marks cells within a
  fixed radius. At matched density, the local density of marked cells is the
  same on any grid — the dilation covers the same local neighborhood.

- **0.2-cell diffusion** (field smoothing): diffuses the material field over
  a fixed fraction of a cell. At matched density, the diffusion produces the
  same local smoothing on any grid.

These are the curvature channel's operations. They are **renormalizable** in
the gauge theory sense: they can be coarse-grained without changing the
physics, because they act on local quantities that are density-dependent.

### GLOBAL absolute scales (not scale-invariant)

A global absolute scale acts on the **position** of an agent relative to a
fixed reference:

- **1-cell step toward a fixed home center** (focal bias): the agent moves
  1 cell toward home_center = grid/4. On an 80×80 grid, home is at x=20, and
  a 1-cell step covers 1/20 of the distance. On a 320×320 grid, home is at
  x=80, and a 1-cell step covers 1/80 of the distance. The mechanism is 4×
  less effective at the same density.

- **Fixed home center** (the reference itself): the home center is at grid/4,
  which is a different absolute position on each grid. The distance from an
  agent to its home center depends on the grid size.

These are **not renormalizable**: they reference a global frame (the fixed
home center) that cannot be coarse-grained without changing the mechanism.
The step size is absolute, but the distance it must cover is grid-dependent.

## The Gauge Theory Analogy

In gauge theory, interactions are classified by their behavior under
coordinate transformations:

- **Local interactions** (gauge couplings) are renormalizable: they depend on
  fields at the same point, so they are independent of the system size. They
  can be coarse-grained — the physics at one scale is determined by the
  physics at the next scale up, without reference to the system boundary.

- **Global references** (external fields, fixed boundary conditions) are not
  renormalizable: they depend on the system's global structure. A fixed
  external field breaks translation invariance and introduces a scale
  (the distance from the boundary).

The absolute-spatial-scale principle is the stigmergic analog:

| Gauge theory | Stigmergic system |
|---|---|
| Local interaction (gauge coupling) | Local stencil (1-cell Laplacian, Moore dilation) |
| Global reference (external field) | Global reference (fixed home center, focal bias) |
| Renormalizable (scale-invariant) | Scale-invariant at matched density |
| Not renormalizable (scale-dependent) | n-dependent (not density-dependent) |
| Coarse-graining preserves physics | Coarse-graining (larger grid at same density) preserves fill |
| Coarse-graining breaks global reference | Coarse-graining weakens focal bias |

The design principle: **prefer local mechanisms over global references for
scale-invariant stigmergic systems.** A local curvature channel (1-cell
stencils) produces the same dynamics at any grid size at matched density. A
global focal bias (fixed home center) does not — it is the stigmergic analog
of an external field that breaks scale invariance.

## Connection to the 50th and 53rd Mechanisms

### The 50th mechanism (Session 80): fill depends on absolute n

The fill decreases with grid size at matched density (48.26% > 31.23% > 24.72%
at 23.4/kc). Session 84 attributed this to the focal bias (an absolute spatial
scale). Session 85 confirmed: without the focal bias, the fill is density-
dependent (66.25% ≈ 66.49% ≈ 64.26%). The 50th mechanism's empirical finding
holds but its mechanism is the focal bias, not the boundary.

### The 53rd mechanism (Session 81): boundary converts density-dependence into n-dependence

Session 81 found the fill is n-dependent with the boundary (g=0.01) and
density-dependent without. Session 84 falsified this: the fill is n-dependent
even without the boundary (the focal bias was the cause). Session 85 confirmed
from the other direction: without the focal bias, the fill is density-dependent
even without the boundary. The 53rd mechanism is falsified at low gain (g=0.01)
where the boundary is negligible.

**Open question (Session 86):** does the 53rd mechanism hold at high gain
(g=0.3)? At g=0.01 the boundary adds <0.5% to the fill. At g=0.3 the boundary's
suppression is strong enough to matter — it may convert density-dependence into
n-dependence independently of the focal bias. If so, the 53rd mechanism is
partially rescued at high gain, and the 50th mechanism has two components
(focal bias at low gain, boundary at high gain).

**Session 86 result: the 53rd mechanism IS partially rescued at high gain.** The
high-gain boundary n-dependence sweep (g=0.3, bias=0, no focal bias) found the fill
decreases monotonically: 54.92% (80×80) → 54.14% (160×160) → 51.61% (320×320),
spread 3.31%. This is n-dependent (unlike the g=0, bias=0 spread of 2.23%). The
boundary at g=0.3 DOES convert density-dependence into n-dependence — but weakly.
The spread (3.31%) is 14% of the focal bias's spread (23.38%). The 50th mechanism's
n-dependence is primarily from the focal bias (86%) with a small boundary
contribution (14%) at high gain.

The mechanism: the co-presence at steady state is extensive (Session 83 found
cp_mean scales with n, not density). More termites on a larger grid produce more
material, higher co-presence, stronger B, and more suppression. The boundary's
reduction increases with n: -11.33% (80×80), -12.35% (160×160), -12.65% (320×320).
The 53rd mechanism's original framing (boundary converts via intensive co-presence)
was correct in principle but wrong in magnitude — the co-presence is extensive at
steady state, not intensive, and the effect is small because the boundary's response
curve saturates (g·B_norm/(1+B_norm)).

The absolute-spatial-scale principle holds with a nuance: the GLOBAL absolute scale
(focal bias) is the primary source of n-dependence; the boundary's extensive co-presence
signal contributes a secondary n-dependence at high gain. The LOCAL/GLOBAL distinction
is not binary — the boundary is a hybrid mechanism (local co-presence computation +
global n-dependent magnitude).

## Connection to the Extensive/Intensive Signal Distinction

The absolute-spatial-scale principle and the extensive/intensive distinction
(Session 82) are complementary:

- **Extensive/intensive (Session 82):** the fill (extensive) is density-dependent;
  the co-presence signal (intensive) is arrangement-dependent. The boundary acts
  on the intensive signal, converting density-dependence into n-dependence.

- **Absolute-spatial-scale (Session 85):** the LOCAL operations (1-cell stencils)
  are scale-invariant; the GLOBAL operations (focal bias) are not. The n-dependence
  comes from the global reference, not the local operations.

The 53rd mechanism's original framing (boundary converts extensive fill's
density-dependence into n-dependence via the intensive co-presence signal) is
*falsified at low gain* because the boundary's contribution is negligible. But
the *principle* — that a mechanism acting on an intensive property through a
global reference converts density-dependence into n-dependence — may hold at
high gain. The boundary's co-presence signal is intensive (arrangement-dependent);
the boundary's suppression is gain-dependent; at high gain the suppression
may be strong enough to matter.

The absolute-spatial-scale principle adds the LOCAL/GLOBAL distinction: the
intensive co-presence signal is computed by LOCAL operations (1-cell Moore
dilation) that are scale-invariant. The n-dependence is not from the intensive
signal itself (which is scale-invariant when computed locally) but from the
GLOBAL focal bias that concentrates the material the co-presence signal is
computed from.

## Design Implications

1. **For scale-invariant stigmergic systems:** use local mechanisms (1-cell
   stencils, local curvature, local dilation). These produce the same dynamics
   at any grid size at matched density.

2. **For n-dependent systems:** use global references (fixed home centers,
   distance-dependent biases). These are the stigmergic analog of external
   fields — they break scale invariance.

3. **The boundary is a hybrid:** it acts on a LOCAL signal (co-presence from
   1-cell Moore dilation) but its suppression is applied through the deposit
   probability (a local action). At low gain the boundary's contribution is
   negligible (the LOCAL signal is scale-invariant, and the suppression is
   weak). At high gain the boundary's suppression may be strong enough to
   convert density-dependence into n-dependence — but this is the 53rd
   mechanism's domain, not the 50th's.

4. **The focal bias is the stigmergic analog of an external field.** It is
   necessary for composition (the 1-seed structural guarantee requires it),
   but it breaks scale invariance (the fill becomes n-dependent). The design
   trade-off: the focal bias enables composition but prevents density-
   independent scaling.

## Cross-Domain Connections

- **Gauge theory → stigmergy:** local interactions (gauge couplings) are
  renormalizable; global references (external fields) are not. The stigmergic
  analog: local stencils are scale-invariant; global references (focal bias)
  are not.
- **Statistical physics → stigmergy:** finite-size effects in statistical
  mechanics scale with the correlation length relative to the system size.
  The stigmergic analog: the focal bias's effectiveness scales with the step
  size relative to the grid size (1/80 vs 1/320).

## Session 90: The Relative-Scale Test — Intensive vs Extensive n-Dependence

### The prediction

The absolute-spatial-scale principle predicts: if ALL spatial scales are made
relative (step ∝ size, radius ∝ size), the system becomes scale-invariant —
the fill at matched density should be the same across grid sizes.

### The test

2 conditions × 2 grid sizes × 4 seeds at 23.4/kc:
- **absolute:** 80×80 (step=1, radius=8), 160×160 (step=1, radius=8)
- **relative:** 80×80 (step=1, radius=8), 160×160 (step=2, radius=16)

80×80 is identical for both (control arm). Only the 160×160 differs.

### The result — PARTIALLY CONFIRMED

| Measure | Type | Absolute spread | Relative spread |
|---------|------|----------------|-----------------|
| b_scale | intensive (local max) | 0.124 vs 0.004 (31×) | 0.124 vs 0.124 (0×) |
| fill_pct | extensive (total) | 30.78 vs 22.58 (8.20%) | 30.78 vs 21.33 (9.45%) |
| cf (coexist_frac) | intensive (fraction) | 0.988 vs 0.700 (0.288) | 0.988 vs 1.000 (0.012) |
| stable | intensive (fraction) | 4/4 vs 3/4 | 4/4 vs 4/4 |

**b_scale** (#232 answered): density-dependent with relative dilation. The
dilation radius is the sole cause of b_scale's n-dependence. With a relative
radius (16 on 160×160), b_scale = 0.124 — identical to 80×80's 0.124.

**Composition quality (cf, stable):** density-dependent with relative scales.
The cf spread dropped from 0.288 (absolute) to 0.012 (relative) — a 24×
reduction. The relative 160×160 achieved cf=1.000, stable=4/4 — matching or
exceeding the 80×80's cf=0.988, stable=4/4.

**Fill (extensive):** n-dependent with BOTH absolute and relative scales.
The relative spread (9.45%) is slightly LARGER than the absolute spread (8.20%).
Making the focal step relative (2 cells) made the focal bias STRONGER, reducing
the fill further (21.33% vs 22.58%) — overcorrecting rather than fixing.

### The refinement: intensive vs extensive n-dependence

The absolute-spatial-scale principle applies to **intensive measures** (b_scale,
composition quality) but NOT to **extensive measures** (fill). This connects
directly to the extensive/intensive signal distinction (Session 82):

- **Intensive measures** (local maximum, fraction) are density-dependent with
  relative scales. The absolute spatial scale is the sole cause of their
  n-dependence; making it relative restores density-dependence.

- **Extensive measures** (total material) remain n-dependent with relative
  scales. The focal bias's concentration effect is inherently extensive — it
  changes the TOTAL amount of material in each region, not just its
  distribution. Making the step relative changes the concentration strength,
  not the fundamental extensivity.

The fill's n-dependence has TWO components:
1. The absolute spatial scale (step=1) — making it relative changes the
   concentration strength but doesn't eliminate n-dependence.
2. The focal bias's extensive effect (concentrating material) — inherently
   n-dependent because the focal bias acts on position (global), not shape
   (local). More termites on a larger grid have more distance to cover, and
   the focal bias's concentration effect scales with the distance.

The design principle: **to make a stigmergic system density-dependent, make
all spatial scales relative AND use intensive quality measures (composition
fractions), not extensive quantity measures (fill).** The fill is inherently
n-dependent when a global mechanism (focal bias) is present; the composition
quality is density-dependent when the global mechanism's spatial scale is
relative.
- **Renormalization group → stigmergy:** coarse-graining (increasing the
  grid size at matched density) preserves local physics but changes the
  global reference's effectiveness. The focal bias is a relevant operator
  under this RG transformation; the local stencils are marginal (scale-invariant).

## Session 91: Third Grid Size Confirmation (320×320)

The relative-scale 320×320 sweep confirmed the extensive/intensive measure-type
distinction at a third grid size. 80×80 control (4 seeds) + 320×320 absolute (2
seeds, radius=8, step=1) + 320×320 relative (2 seeds, radius=32, step=4) at 23.4/kc:

| Measure | Type | 80×80 | 320×320 absolute | 320×320 relative |
|---------|------|-------|------------------|-------------------|
| b_scale | intensive | 0.123749 | 0.000000 | 0.123749 (EXACT) |
| cf | intensive | 0.988 | 0.000 | 1.000 (MATCH) |
| fill | extensive | 30.78% | 16.58% | 13.77% (n-dep, both) |

The b_scale exact match (0.123749 = 0.123749) is the purest confirmation: b_scale
is a pure initialization quantity (95th percentile of initial co-presence), computed
before any simulation dynamics. With absolute dilation (radius=8), the 320×320 seed
regions (160 cells apart) are not bridged → b_scale=0. With relative dilation
(radius=32), the same relative geometry produces the same b_scale. The fill remains
n-dependent with both (step=4 overcorrects — the focal bias is stronger, not weaker,
with a larger step). See `relative_scale_320_sweep.py` and H5 Session-91 refinement.

## Session 95: The 30th Ceiling Shifts With Grid Size

The 30th mechanism's persistence ceiling (~43.6% fill on 160×160) was tested for
universality by running a high-density plateau sweep on 80×80 (n=300–600 at
g=0.005–0.01, 4 seeds). If the 30th ceiling is the Moore threshold (universal
~40.7%), it should be the same fill fraction on all grids.

**It is NOT universal — it shifts with grid size.** On 80×80, stability persists
at 64–76% fill — 23–35pp above the Moore threshold and above the 160×160's 30th
ceiling. The stability degrades gradually (4/4 at 64% → 1/4 at 76%) with no sharp
collapse, and shows UNDER-splitting (late_lc/rc < 1, structures too compact) not
over-splitting (late_lc/rc > 3, the 160×160's 30th mode).

**The absolute-spatial-scale principle explains the shift.** The boundary's
dilation radius (8 cells) is an absolute spatial scale. On 80×80, 8 cells = 10%
of the grid width; on 160×160, 8 cells = 5%. The boundary is relatively wider on
80×80, so it can maintain stable composition at higher fill fractions. The focal
bias (1-cell step) is also relatively stronger on 80×80 (1.25% vs 0.625%). The
30th ceiling is about the ratio of the structure's absolute size to the
boundary's absolute spatial scale — on 80×80, this ratio is more favorable at
any given fill fraction.

**The boundary's fill-capping power is negligible on 80×80** — the fill with and
without the boundary are nearly identical (64.3% vs 65.0% at n=300). The curvature
channel alone caps the fill at ~76%. The boundary adds stability but not
fill-capping on 80×80, while on 160×160 it IS the primary fill-capping mechanism.

**The 2.93pp gap on 160×160 is coincidental.** The 30th is a boundary-specific
mechanism (over-splitting at large absolute structure size), not a connectivity
threshold. Its proximity to the Moore threshold on 160×160 is because the
boundary's 8-cell dilation radius happens to produce over-splitting near the
Moore fill on that grid size. On 80×80, the 30th is 30+pp above the Moore
threshold.

See `grid80_high_density_plateau.py` and H5 Session-95 refinement.

## Session 97: The 30th Ceiling Saturates — Crossover Requires r/grid ≥ 10%

### The crossover sweep

r=10 (6.25% of grid) and r=12 (7.5% of grid) were tested on 160×160 at n=3000 and n=5000 (2 seeds, separable max-filter optimization verified identical to the original O(r²) dilation).

| Radius | r/grid | n | Fill% | Stable | lc | rc | Mode |
|--------|--------|---|-------|--------|----|----|------|
| 4 | 2.5% | 2000 | 41.3% | 0/4 | 3.81 | 5.55 | over-splitting |
| 8 | 5.0% | 3000 | 43.6% | 0/4 | 5.50 | 6.80 | over-splitting |
| 10 | 6.25% | 3000 | 43.1% | 0/2 | 4.60 | 5.88 | over-splitting |
| 12 | 7.5% | 3000 | 43.3% | 0/2 | 5.85 | 6.53 | over-splitting |
| 10 | 6.25% | 5000 | 48.0% | 0/2 | 5.00 | 5.35 | over-splitting |
| 12 | 7.5% | 5000 | 48.3% | 0/2 | 6.25 | 5.60 | over-splitting |
| 8 (80×80) | 10.0% | 600 | 76.3% | 2/4 | 0.42 | 0.57 | under-splitting |

**All four new configs are over-splitting.** The 30th ceiling saturates at ~43% for r ≥ 8 on 160×160 — r=10 and r=12 give the same ceiling as r=8. The fill at n=5000 (~48%) matches the existing r=8 n=5000 data — the fill cap is NOT affected by the wider boundary at r/grid < 10%.

### The 30th ceiling is NOT the matched-granularity point

At the ceiling, L/r = 18.2 (r=4), 9.3 (r=8), 7.4 (r=10), 6.2 (r=12) — all >> 1. The matched-granularity point (L=r) would be at fill ≈ 0.1–2%, far below the ceiling (~43%). The ceiling is DYNAMICAL (boundary suppression can't keep up with structure growth), not GEOMETRIC (L=r). The L/r ratio decreases with wider radius because the fill stays approximately constant while r increases.

### The 80×80 r=8 under-splitting is confounded

The 80×80 r=8 (10% of grid) shows under-splitting, but it's on a different grid (80 vs 160) with fewer termites at the same density (150 vs 600). The 50th mechanism (fill depends on absolute n) means the structures are smaller in absolute terms, and the focal bias (1-cell step) covers a larger fraction of the grid. The under-splitting may be a grid-size effect, not purely a boundary-width effect. The r=10 and r=12 data on 160×160 show that the boundary width alone does not produce under-splitting at r/grid < 10%.

### Refinement of Session 96

Session 96 concluded the 30th ceiling is the structure-to-boundary ratio based on r=4 → r=8 → 80×80 r=8. Session 97 shows the r=4 → r=8 shift was the narrow-boundary effect (r/grid < 5% lowers the ceiling), but r ≥ 8 saturates — the ceiling does NOT continue to shift with wider radius on the same grid. The KJMA crossover analogy holds for the r=4 vs r=8 contrast but does NOT extend to intermediate radii.

## Cross-References

- [[concepts/extensive-intensive-signals]] — the complementary distinction:
  extensive fill (density-dependent) vs intensive co-presence (arrangement-dependent)
- [[concepts/two-wire-principle]] — the 15th member: LOCAL vs GLOBAL absolute
  scales on separate wires
- [[concepts/gompertz-logistic-transition]] — the fill-fraction thresholds are
  intensive, but the focal bias's n-dependence sets the density range
- [[hypotheses/H5]] — the persistence condition; the focal bias is necessary
  for composition but breaks scale invariance
- [[hypotheses/H7]] — the crossing is robust because it depends on the local
  curvature signal (scale-invariant), not the global focal bias
- [[hypotheses/H10]] — the composition problem; the 50th mechanism is the
  absolute-spatial-scale principle's macroscopic expression
