# Handoff prompt for the primary researcher agent

Paste the block below as the next session's prompt (or fold it into the "ALife Nightly
Research" scheduled job for one run). It is written to be self-contained — the agent should
not need this wrapper file.

---

Tonight is **not** a normal research session. A construct-validity review on 2026-07-27 found
that five of the six then-implemented simulations were not measuring what they claimed, and
corrected the corpus accordingly. Your job is to absorb that, publish the entry announcing it,
and start on the work it redirects you toward.

**Step 1 — Read these three documents in full before doing anything else.** Do not
frontmatter-skim them; they contradict claims you may otherwise treat as settled.

1. `RETROSPECTIVE-2026-07-27.md` — the failures grouped by root cause, the errors made during
   the review itself, eight checkable rules, and how the evidence base should redirect the
   research. This is the most important document.
2. `simulations/REVIEW.md` — the per-simulation technical audit: what each one actually
   measured, what was fixed, which conclusions moved.
3. `daily-reports/2026-07-27-session-2.md` — the public log entry. Already written and live.

**Step 2 — Post the research log to Bluesky.** The text is already drafted in that entry's
Bluesky section. **Post it verbatim rather than composing your own** — the framing is
deliberate, because the entry's subject is agent reliability and a breezier summary would
undercut it. Run:

```
bsky-post "Today I reviewed my own simulation code and had to retract three findings. A metric ran backwards; a detector could never fire. Publishing it all — this project is also research into whether agents can research reliably 🤖 https://alife.vancedubberly.com/reports/2026-07-27-session-2/ #ALife #AIAgent"
```

That is 299 characters — do not add to it. Then replace the "To post" block in
`daily-reports/2026-07-27-session-2.md` with `Posted: <returned url> — "<text>"`, matching the
convention in the other reports.

**Step 3 — Internalise these corrections.** Several things you have been treating as
established are no longer true:

- **Do not cite our own simulations as independent confirmation of the literature.** The "three
  independent traditions converge on composition being hard" argument holds *in the published
  work* (Smith & Bedau, Vasas, Mathis et al.), but sim03 cannot confirm Vasas — its organization
  lattice is fixed at construction — and sim05 now shows 2/6 coexistence, which mildly
  contradicts the strongest reading. Cite the literature; describe our sims separately.
- **H7 is open, not failed.** sim06's detector could never fire. Corrected, it misses by ≤0.05
  on one criterion with another passing 154/160. Stop describing it as a categorical null.
- **H10 is weakened** (0/6 → 2/6). **H9 has no supporting simulation evidence left.** **H1 lost
  its sim03 leg.** **H11 is new** — the Saturating Channel Hypothesis.
- Any pre-2026-07-27 simulation number you encounter in an older report is suspect. The wrong
  ones carry dated correction blocks; check for one before quoting a figure.

**Step 4 — Do the work, in this order.** These are all cheaper than what was previously queued
as top priority, and each tests a hypothesis the review just weakened.

1. **queued-topics #52 — what distinguishes sim05's two coexisting pairs from the four that
   did not?** Pure analysis of the committed `results.json`; no new code. Is it organization
   size, structural overlap, or specific "glue" expressions? This contrast did not exist at 0/6.
   Tests H10 directly. **Start here.**
2. **queued-topics #54 — repeat sim06's Part-8 parameter sweep against the working detector.**
   The original sweep ran against a detector incapable of firing, so "no regime produces the
   crossing" is unsupported in either direction. A crossing regime may already lie inside the
   space that was swept.
3. **queued-topics #53 — non-saturating inhibition.** The direct test of H11 and much cheaper
   than sim08: a density cap or refractory period acting on deposit probability rather than on
   the cue field. Prediction: it consolidates where field manipulation fragmented.
4. **Literature check on H11 before claiming novelty.** Ant Colony Optimization tunes
   evaporation against this exact pressure and MAX-MIN Ant System bounds pheromone explicitly.
   H11 may be a rediscovery; finding that out is cheap and it belongs in the hypothesis's
   Criticisms section either way.

Only after those should you design sim08 (directed / externally-driven transport). Note there
is **no `simulations/sim08_*/` folder and no DESIGN.md** — despite what older prose implies,
sim08 does not exist, so §4 step 0 has nothing to implement.

**Step 5 — Apply the new methodology requirements** (now in `CLAUDE.md` §4 step 6) to anything
you build tonight:

- Every detector must prove it can fire: feed it a synthetic case that *should* trip it and
  assert it does, then negate each criterion and assert it withholds. `cmd_selftest` Part 5 in
  `sim06.py` is the template.
- Compute your metric's ceiling. If its maximum can fall below your threshold, it is not a test.
- Any claim of an effect needs a control arm.
- Verify determinism by running twice and diffing, not by reading the code.
- Report per-criterion pass rates for any null. "It didn't fire" hides an unfalsifiable
  detector.
- If every bug you find pushes toward the result you expected, treat the result as unproven.

**Step 6 — Committing and publishing.** These changed on 2026-07-27:

- Stage explicit paths, never `git add artificial-life/`. Run `git status --porcelain
  artificial-life/` first, and if it shows files you did not touch, **stop and report it**
  rather than committing them. A directory-wide add previously swept an unrelated review into a
  commit titled "sim07 implementation".
- Publish to the public mirror with `alife-publish-mirror.sh` — never push `~/brain` directly.
  A pre-push hook blocks that, because this repo tracks private folders and its origin is the
  public mirror.
- Deploy the site with `alife-deploy-site.sh` as usual. Expect up to an hour before changes
  appear: the CDN caches for 3600s. Compare the response's `x-goog-generation` against the
  bucket object's before concluding a deploy failed.

**One caution.** The review's own work contained mistakes too — a guard that passed its own test
but had a hole, a correction that contradicted itself eight lines later, a caching delay
misdiagnosed as a broken deploy. They are listed in the retrospective's §3. Read that section
before assuming the corrected corpus is now beyond question. If you find an error in the
corrections, say so plainly and fix it; that is the behaviour this project is trying to develop.
