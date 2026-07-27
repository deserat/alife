# Sim04: Evolving Reaction Networks — Novel Cores and Compartmentalization

## What it tests

Whether reaction networks that generate new reactions (evolving networks) can produce evolvable organizations where a fixed reaction network stalls. Based on Vasas et al. (2012) "Evolution before genes."

## Hypotheses tested

- **H7** (Trace→Actor Crossing): Do novel reactions produce new self-maintaining organizations (new actors)?
- **H1** (Composition): Does multi-scale structure (molecular + compartmental) emerge?
- **H9** (Evolving Network): Does an evolving reaction network produce open-ended dynamics where a fixed network stalls?
- **H8** (Computational Irreducibility): Can we predict which novel cores will appear?

## Design

- Binary polymer chemistry (alphabet {a, b}, max length 8)
- Food set: all polymers up to length 3 (14 species)
- Catalyzed ligation/cleavage reactions (random catalysis, P_catalyst=0.75, P_catalyze=0.005)
- **Fixed condition**: No uncatalyzed reactions
- **Evolving condition**: Rare uncatalyzed reactions produce novel species (rate=0.01)
- 20 compartments, each containing a reaction network
- Compartments grow and divide (stochastic segregation)
- Selection: compartments with more mass grow faster (implicit)

## Results

> **These numbers replace the pre-2026-07-27 figures, which were not reproducible.**
> `_is_catalyst` and `_catalyzes` derived the catalysis map — which molecule catalyses which
> reaction, i.e. the chemistry itself — from Python's builtin `hash()`, which is randomized
> per process (PEP 456): `hash(("abab","catalyst")) % 1000` returned 992, 410 and 696 on
> three successive runs. Four further set-iteration-order dependencies compounded it, the
> decisive one being that `concentrations` was keyed by iterating a set, so `divide()`
> consumed RNG draws in a process-dependent order. Every earlier figure here was a single
> unrepeatable sample. Catalysis is now derived from a stable string-seeded generator and
> reproducibility is verified byte-identical across two full runs. See `../REVIEW.md` §5.

| Metric | Fixed | Evolving |
|--------|-------|----------|
| Species discovered | 510 | 510 |
| Total mass | 4169 | 3418 |
| Non-food mass | 878 | 684 |
| Cores (sampled) | 3 | 3 |
| Compartments | 40 | 37 |
| Compartment diversity | 10 | 10 |

## Key Findings

1. **Both conditions saturate the species space.** 510 = all possible binary polymers up to length 8 (2+4+8+16+32+64+128+256=510). Both catalyzed and uncatalyzed reactions explore the full combinatorial space. The "novel reactions from shadow" mechanism is redundant when catalyzed reactions already explore the space. *(Unaffected by the determinism fix — 510 is a structural bound.)*

2. **The evolving network finds no more cores than the fixed one — 3 vs 3.** *(Retracted 2026-07-27: this previously read "the evolving network finds slightly more cores (5 vs 4) but with less total mass", and inferred that novel species from uncatalyzed reactions create new catalytic pathways while introducing resource-consuming side reactions. Both the comparison and the inference came from the unreproducible run and do not survive.)* The evolving condition does carry less mass (3418 vs 4169) and less non-food mass (684 vs 878), so the "side reactions consume resources" half may still hold — but with core counts equal there is no measured benefit to set against it.

3. **Compartment diversity is identical (10 in both conditions).** The between-compartment variation does not increase with evolving networks. Compartments share one catalysis cache, so all of them discover the same species. *(The parenthetical "same hash-based catalysis rules" is still true in substance — catalysis is a fixed pseudo-random function of (catalyst, reaction) — but it is now seeded deterministically rather than by the builtin `hash()`.)*

4. **Neither condition produces open-ended evolution.** Both reach a fixed species count (510) and stop. This confirms the "one bit" limitation from Vasas et al.: the combinatorial space of binary polymers up to length 8 is finite, and both conditions exhaust it.

5. **The simulation does not reproduce Vasas et al.'s key finding** (5/460 runs showing persistent complexity increase). Our P_catalyze (0.005) may be too high — all species become catalytic, producing one large core rather than distinct cores. Vasas used P''=0.0025 and noted that P needs to be low enough to produce multiple distinct cores, not one large one.

## Limitations

- **Finite species space**: Binary polymers up to length 8 = 510 species. Both conditions exhaust this space. Need longer polymers or larger alphabet for open-ended exploration.
- **Catalysis cache is shared**: All compartments use the same hash-based catalysis rules. Vasas et al. generate catalysis randomly per compartment. Our model is more like parallel exploration of the same chemistry, not independent experiments.
- **No explicit selection**: We rely on implicit selection (compartments with more mass grow faster). Vasas et al. implemented explicit Moran process with selective advantage.
- **P_catalyze too high**: 0.005 may produce one large core instead of multiple distinct cores. Vasas needed P low enough for distinct cores to form.

## What it teaches

1. COT formalism CAN be operationalized for ALife (sim03 + sim04)
2. Fixed and evolving networks both stall at the boundary of the combinatorial space
3. The distinction between "evolvable" and "open-ended" is real and large
4. Novel reactions alone don't produce open-endedness — the species space must also be unbounded
5. The "one bit" problem from Vasas et al. is confirmed: even with novel cores, the system exhausts its possibilities
6. For sim05: need (a) unbounded species space (lambda calculus chemistry, not fixed-length polymers), (b) per-compartment catalysis (not shared), (c) explicit selection mechanism
