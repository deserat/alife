# CLAUDE.md — ALife Research Project

Guidance for Claude Code when working in `~/brain/artificial-life/`.

## 1. What this project is

A long-term research project toward an **artificial life simulator grounded in Actor Network
Theory (ANT) and computational irreducibility**. The output is threefold: a body of synthesized
knowledge, a set of testable hypotheses, and small Python simulations that test them. The
eventual artifact is a playable simulation/game.

**Core thesis** (see `README.md`): modern ALife simulations are single-scale and fail at
**multi-scale composition** — emergent phenomena at one scale interacting to produce
qualitatively new phenomena at another, where the actors and rules are fundamentally different
(the water cascade: molecule → droplet → cloud → flood). ANT supplies the language for the
network-restructuring events between scales; computational irreducibility says you must run the
simulation to know the outcome.

This is a **research notebook, not a software product**. Prose files are the primary artifact;
the code exists to test claims made in the prose. Negative and null results are first-class —
sim07's null and the 2026-07-27 construct-validity review (`simulations/REVIEW.md`) are the two
most valuable things in the repo. (sim06's null held that place until the review found its
detector could never fire; the *correction* proved more valuable than the result, and produced
H11.)

**Current state (as of Session 10, 2026-07-27):** 11 hypotheses (H1–H11), 16 concept files,
sims 01–07 built and all rerun after the 2026-07-27 code review. **sim08 is proposed only —
there is no `simulations/sim08_*/` folder and no DESIGN.md**, so §4 step 0 has nothing to
implement; writing that DESIGN is the next piece of work. Everything hangs on **H7, the
Trace→Actor Crossing Hypothesis** — sim07 produced a sound null (scalar structure-sourced
transport fragments rather than consolidates; no phase transition in `M_c`).

**H11, the Saturating Channel Hypothesis (new 2026-07-27), reframes what H7 needs.** Both
attempts at negative feedback — sim06's self-emission and sim07's transport venting — acted
*through the pheromone field*, whose deposit response saturates above φ≈1, so both destroyed
spatial contrast instead of creating it. If H11 holds, the crossing needs feedback through a
non-saturating channel (a density cap, refractory period, or directional bias acting on deposit
probability directly) — a much cheaper experiment than the directed / externally-driven
transport (H4) that sim08 was going to test.

**Read `simulations/REVIEW.md` before citing any pre-2026-07-27 simulation number.** A
construct-validity audit found five of six sims measured something other than what they
claimed. Three headline results moved: sim05 went 0/6 → **2/6** L2 coexistence (H10 weakened);
sim06's crossing detector **could not fire at all**, so its Session 8 null carried no
evidential weight — corrected, it is a near miss (stability 0.849–0.893 vs a 0.90 threshold),
not the "diffuse scatter, ~230 micro-pillars, stability 0.55" that older prose describes; and
sim01's `trail_cells` metric runs *opposite* to trail formation. sim04 was not reproducible at
all. Corrections have been propagated, but older daily reports carry inline
`> **Correction (2026-07-27)**` blocks rather than rewritten text.

## 2. Layout and what lives where

```
~/brain/artificial-life/
  README.md            — project charter: thesis, methodology, structure, timeline. Also the
                         source for the public site homepage — keep it publishable.
  CLAUDE.md            — this file
  INDEX.md             — GENERATED corpus index (one line per document, from frontmatter).
                         Read this first to find things; never hand-edit. Not published.
  synthesis.md         — running log of cross-domain connections, one section per session
                         (append-only; ~35 KB and growing)
  glossary.md          — terms grouped by domain (ANT / ALife / Hofstadter / autopoiesis /
                         complexity / stigmergy / …), plus "Cross-Domain Terms (Our Project)"
  references.md        — bibliography, grouped by researcher; has a "To Be Added" section
  queued-topics.md     — numbered backlog of tangents, grouped "From Session N"; entries are
                         marked DONE (Session N) in place rather than deleted
  bluesky-engagement.md— append-only log written by the engagement monitor; do not hand-edit
  hypotheses/
    hypotheses.md      — CURRENT STATE ONLY for each hypothesis (H1–H11): statement, status,
                         evidence, next test, link to its log. Full refinement history lives in
                         logs/, not here.
    logs/
      HN.md            — one file per hypothesis, the full session-by-session refinement
                         history (append-only, oldest first). This is where "Refinement
                         (Session N)" paragraphs go — hypotheses.md itself only ever holds the
                         current statement/status/test, rewritten in place as it changes.
  concepts/            — one living document per topic cluster, refined across sessions
  daily-reports/       — YYYY-MM-DD.md session logs (one per nightly run)
  researchers/         — per-researcher notes (currently EMPTY — unused so far)
  simulations/         — Python building-block sims, one folder each
    REVIEW.md          — 2026-07-27 construct-validity audit of sims 01–06: what each one
                         actually measured, the fixes, and which conclusions moved. Read
                         before citing any pre-2026-07-27 simulation number.
```

**Concepts** (`concepts/*.md`) are living documents, not session logs. Refine an existing file
rather than adding a new one unless the topic is genuinely new. Each has (or should have) a
"Criticisms" section and an "Empirical Evidence" section — this is a methodological requirement,
not decoration.

**Simulations** (`simulations/simNN_shortname/`):

| sim | topic | result |
|---|---|---|
| sim01_pheromone_trails | stigmergic coordination, vs. pheromone-blind control | trails form: concentration 0.79 vs blind 0.27. No optimal decay window; `trail_cells` measures coverage, not trails |
| sim02_dynamic_landscape | static vs. agent-modified fitness landscape | both converge; dynamic converges harder (diversity 2 vs 4), fitness 1.11 vs 0.77 |
| sim03_chemical_organizations | Chemical Organization Theory, fixed network | 8/9 organizations, 1/24 nested; converges by gen 1 — but the org lattice is static *by construction*, not measured |
| sim04_evolving_networks | evolving reaction network, finite space | exhausts space (510/510), stalls; cores 3 vs 3 — no evolving advantage |
| sim05_lambda_chemistry | AlChemy, unbounded space | L1 forms; L2 coexistence **2/6** (was 0/6 — artifact; H10 weakened) |
| sim06_termite_mound | H7 trace→actor crossing | **null, but weak**: +66% structure; detector was broken and could never fire. Corrected it is a near miss — criterion 1 at 0.849–0.893 vs 0.90, criterion 3 passing 154/160 |
| sim07_transport_coupling | H7 via transport field + `M_c` threshold | **null**: scalar transport fragments (stability ↓, pillars ↑ as M_c drops); crossing never fires |

Each sim folder holds: `simNN.py`, `README.md` (written last, with REAL numbers), `results.json`
(committed), `visualize.html`, optional `DESIGN.md`, and a gitignored `output/` for PNG/MP4.

## 3. Conventions

### Frontmatter
Daily reports **must** open with:
```yaml
---
date: "YYYY-MM-DD"
session: N
topic: "tonight's topic"
concepts: ["name (new|updated)"]
hypotheses: ["H7 (refined: …)"]
simulations: ["simNN_name (status)"]
moltbook: true|false
summary: "one paragraph"
---
```
Concept files use: `status`, `formed`, `connected_to`, `topic`, `key_findings`.

This frontmatter exists for **progressive loading**. `README.md` flagged that scanning it one
file at a time stops scaling past ~50 documents — the corpus passed that mark, so the scan is now
collapsed into a single generated file: **`INDEX.md`** (see `alife-build-index.py` in §5). Read
`INDEX.md` first and full-read only the documents it points you at; fall back to per-file
frontmatter reads only for something the index doesn't cover.

All 16 concept files now carry frontmatter (the eight legacy ones were backfilled 2026-07-27).
Keep it that way — a new concept file without frontmatter degrades to a body-prose guess in the
index. The sim `README.md`/`DESIGN.md` files and the root docs still have none; they are indexed
from their first heading and paragraph, which is adequate but worse.

### Naming
- Daily reports: `YYYY-MM-DD.md`; a second run the same day gets `-session-2`.
- Concepts: `kebab-case.md` named for the concept, not the session.
- Sims: `simNN_snake_name/` containing `simNN.py` (zero-padded, sequential).
- Hypotheses: `H<n>` with a name ("H7: The Trace→Actor Crossing Hypothesis"); referenced as
  bare `H7` throughout the prose so the link-terms script can hyperlink them.

### Cross-references
Prose uses Obsidian-style `[[concepts/name]]` / `[[hypotheses/H7]]` inside concept and design
files, and relative markdown links (`../../hypotheses/`) inside sim READMEs. Daily reports get
absolute public-site URLs injected automatically — see `alife-link-terms.py` below; don't hand-write
those links.

### Report sections
Reports follow a stable outline (headings have drifted between title-case and sentence-case;
either is fine): Budget · Topic · What I read (with links) · What I learned · Criticisms found ·
Empirical evidence · Cross-domain connections · Hypotheses · Concept files · Simulations ·
Moltbook · Bluesky · Next session. Each simulation mentioned links to its published
`visualize.html`.

### Python
- Plain Python + numpy; matplotlib imported **lazily** and only for plotting (`matplotlib.use("Agg")`,
  headless). No dependencies beyond `simulations/pyproject.toml`.
- Module docstring at the top explaining the hypothesis under test and the conditions contrasted.
- All tunables as UPPER_CASE module constants in one block, overridable via a `params` dict with
  constant fallbacks.
- **Deterministic**: every stochastic function takes a `seed` or a passed-in
  `numpy.random.Generator`. Never touch global `numpy.random`/`random` unseeded.
- Paths derived from `os.path.dirname(os.path.abspath(__file__))` — never hardcode `/home/vance/...`.
- A `_pyify()` helper converts numpy scalars/arrays before `json.dump`.
- CLI is a hand-rolled `sys.argv[1]` dispatcher (no argparse):
  `selftest` | `run` | `sweep_plot` | sometimes `visualize`.
  `selftest` prints `Part N OK` and exits 0.
- `results.json` shape: a `config` block plus one block per condition
  (e.g. `baseline` / `self_maintenance` / `perturbation`), each with a `history` array of
  per-sample metric records and a summary.

### visualize.html
Self-contained, no external deps, no build step. Dark theme (`--bg: #0d1117`, `--text: #c9d1d9`,
panel `#161b22`, border `#30363d`), HTML5 Canvas charts, `fetch('results.json')` with error
handling. **Inspect the actual `results.json` before writing any JS** — this rule was learned the
hard way (an earlier commit rewrote three visualizations for using wrong data structures).

### Commits
Repo root is `~/brain` (the whole personal wiki), not this directory. Message styles in use:
- `ALife research: YYYY-MM-DD — <topic>` (nightly session)
- `ALife sim06: Part 1 — <what>` (simulation work)
- `ALife: <what>` (fixes, tooling, wiki edits)

**Stage the changes you made, not the directory they live in.** `git add artificial-life/`
is directory-narrow, not change-narrow: it sweeps up any concurrent or in-progress work that
happens to be sitting in the tree. On 2026-07-27 this swallowed an entire unrelated code-review
pass into a commit titled "sim07 implementation", which then had to be reworded via a history
rewrite. Instead:

```bash
cd ~/brain
git status --porcelain artificial-life/          # 1. look FIRST
git add artificial-life/<specific paths you touched>
git commit -m "…"
```

If `git status` shows files you did not touch this session, **stop and report it** rather than
committing them. Two things legitimately produce such files: `bluesky-engagement.md` (written
by the engagement monitor) and a human editing in parallel. Neither belongs in a session
commit. If the session genuinely touched most of the directory, listing the paths explicitly
is still correct — it makes the commit self-documenting and prevents the failure above.

A `pre-push` hook in `~/brain/.git/hooks/pre-push` rejects any push touching paths outside
`artificial-life/`. `~/brain` tracks private folders (`health/`, `family/`, `work/`,
`people/`, …) and its `origin` is the **public** mirror, so an accidental push would publish
them. Nothing private has ever been exposed; the hook keeps it that way. Override deliberately
with `git push --no-verify` — and if you find yourself wanting to, that is the signal to stop
and ask a human.

### Publishing and the security rule (important)
Daily reports are **public** — deployed to `https://alife.vancedubberly.com` and mirrored to the
public `deserat/alife` GitHub repo. Never write into any file here: email addresses or PII;
infrastructure details (cloud provider, buckets, service accounts, deploy-script internals);
auth details (tokens, keys, PATs, SSH, credentials); or failure reasons that reveal
infrastructure. If a deploy or push fails, the report says exactly: "Deploy failed — needs manual
intervention." A past commit had to retroactively sanitize a report — don't create that work again.

Related hazard: `~/brain` also contains private folders (`health/`, `family/`, `work/`, …) and its
`origin` is the **public** alife repo. Only `artificial-life/` content belongs on the mirror; the
mirror is populated by copying files into a separate clone, not by pushing this repo wholesale.
The working branch is currently `clean-alife`; `master` tracks the public remote.

## 4. The research workflow

Sessions are **spiral loops**, not sequential steps: research a topic cluster → synthesize into
`concepts/` → log connections in `synthesis.md` → develop hypotheses → build a mini simulation →
queue tangents. Each loop builds on prior synthesis so knowledge compounds. Topic clusters emerge
from the research; old ones get revisited.

One session runs nightly (cron, ~midnight MT) under a **$5/day token budget**, tracked and
reported in each report's Budget section. Order of operations:

0. **Simulation work first.** If a sim has a `DESIGN.md` with unchecked Parts in its Progress
   Tracker, implement the **first unchecked Part only** — follow the spec exactly (signatures,
   constants, verification command), run the verification, tick the box, append a one-line
   Session log entry at the bottom of the DESIGN. Do not refactor earlier Parts, do not
   gold-plate, do not start the next Part in the same session. Only when every Part is `[x]` does
   the night become a research session.
1. **Progressive load** — full-read `INDEX.md`, then only the documents it points you at;
   full-read `queued-topics.md` and `synthesis.md`. Do not sweep the corpus file by file.
2. **Pick one topic cluster** from `queued-topics.md`, preferring ones connected to recent work.
3. **Research it** — and actively seek criticisms, counterarguments, failed experiments
   ("[concept] criticism", "[technique] limitations"). Log opposing views honestly. Seek empirical
   evidence; if there is none, write "no empirical studies found" explicitly. That's a finding.
4. **Synthesize** into concept files; append a dated section to `synthesis.md`.
5. **Hypothesize** — add or refine. Refinements are **appended as dated "Refinement (Session N)"
   paragraphs to `hypotheses/logs/HN.md`**, never overwriting prior entries there. Then update
   `hypotheses/hypotheses.md` **in place**: rewrite the current statement/status/evidence/next-test
   for that hypothesis to reflect the new refinement (do not append a history paragraph to
   hypotheses.md itself), and update its row in the summary table at the bottom. A brand-new
   hypothesis gets a new section in hypotheses.md and a new `logs/HN.md` (stub "No refinements
   recorded." until its first refinement).
6. **Simulate** — small, focused sims that solve one sub-problem; building blocks for the eventual
   system, not the system itself.

   **Every sim that reports a result must prove its measurement can produce the other answer.**
   Five of the first six simulations measured something other than what they claimed
   (`simulations/REVIEW.md`), and the failures were not subtle bugs — they were detectors that
   could only ever return one verdict. Before trusting any result, positive or null:
   - **Positive control.** Feed the detector a synthetic input that *should* trip it, and assert
     it does. `cmd_selftest` Part 5 in `sim06.py` is the model: it asserts the crossing detector
     fires on an ideal history, and withholds when any single criterion is negated.
   - **Check the metric's ceiling.** sim05 classified on Jaccard similarity whose arithmetic
     maximum fell *below* the success threshold for two of six tests — those could not have
     passed under any dynamics.
   - **Include a control arm.** sim01 had none, so it could not distinguish trail formation from
     ants wandering; its metric turned out to run *opposite* to the thing it named.
   - **Ask which direction each bug pushes.** If every defect biases toward the result you
     expected, treat the result as unproven regardless of how clean it looks.

   A null result from an unvalidated detector is not a finding — it is an absence of
   measurement, and it is worse than no result because it reads as evidence.
7. **Moltbook / Bluesky** engagement; save every URL into the report.
8. **Write the daily report** (frontmatter + sections above).
9. **Update `references.md` and `glossary.md`.**
10. **Rebuild the index, link terms, commit, deploy, push, post.** Mandatory — if budget runs
    short, skip earlier steps, never this one. Run `python3 ~/.local/bin/alife-build-index.py`
    before committing so `INDEX.md` includes tonight's work; it costs no model tokens.

Larger simulations get a `DESIGN.md` written by a stronger model and implemented Part-by-Part by
a cheaper one across nights; that's why sim06's design is written for an audience that has not
read the rest of the document. Follow that pattern for new multi-night sims (see
`simulations/sim06_termite_mound/DESIGN.md` for the template: How-to-use section, Progress
Tracker, Scientific framing, Global conventions, self-contained Parts each with Dependencies /
Definition of Done / Verification command, Appendix constant reference, dependency graph, Session
log).

## 5. Tools and scripts

**Running simulations** — `uv`, from the `simulations/` directory:
```bash
cd ~/brain/artificial-life/simulations
uv run python3 sim06_termite_mound/sim06.py selftest
uv run python3 sim06_termite_mound/sim06.py run          # writes results.json
uv run python3 sim06_termite_mound/sim06.py sweep_plot   # PNGs into output/
```
`simulations/pyproject.toml` is shared by every sim (numpy, matplotlib, Python ≥3.11); a `.venv/`
lives alongside it. `simulations/.gitignore` excludes `output/`, `*.png`, `*.mp4`, `__pycache__`,
venvs — but `results.json` **is** committed (the visualizations fetch it).

To preview a visualization: serve the sim folder over HTTP (`python3 -m http.server`) — `fetch()`
won't work from `file://`.

**Project scripts** (in `~/.local/bin/`):
- `alife-build-index.py` — regenerates `INDEX.md`, the one-line-per-document corpus index, from
  document frontmatter (falling back to first heading + paragraph where there is none). Pure
  stdlib, no model tokens. `--stdout` prints instead of writing; `--check` exits 1 when the index
  is stale. Output is deterministic — no timestamps — so an unchanged corpus produces a
  byte-identical file and `INDEX.md` only appears in `git diff` when something really changed.
  Run it as part of step 10 each night. Tuning knobs are the `*_MAX` truncation constants and
  `EXCLUDE_DIRS` / `EXCLUDE_FILES` at the top.
- `alife-link-terms.py` — rewrites the first occurrence of each known term (H1–H11, concept names,
  glossary terms) in a daily report into a public-site hyperlink. Run on tonight's report before
  committing: `python3 ~/.local/bin/alife-link-terms.py <report.md>` (or `--all`). When a new
  concept or hypothesis is added, add it to this script's `TERMS` map. Note: it has re-linked
  already-linked text in the past, producing doubled URLs — check the diff.
- `alife-convert-concepts.py` — converts concept markdown (frontmatter and all) into the static
  site's page format.
- `alife-deploy-site.sh` — builds the static site (Zola, sources from this directory plus
  `~/alife-site/`) and publishes it.
- `alife-publish-mirror.sh` — **the supported way to publish to the public GitHub mirror**
  (`deserat/alife`). Keeps a persistent clone at `~/alife-mirror`, hard-resets it to
  `origin/master`, exports the *git-tracked* `artificial-life/` tree into it (so nothing
  untracked — `.venv/`, `output/`, `__pycache__` — can leak), refuses to push if any staged
  path is absent from the source tree, then commits and pushes. `DRY_RUN=1` stops before
  commit/push. Never push `~/brain` directly: it tracks private folders and its `origin` is
  the public mirror, which is why a `pre-push` hook blocks that path.
  *Before this existed the procedure lived only in a scheduled agent's prompt and ran out of
  an abandoned `/tmp` clone that had drifted 11 commits behind; the mirror had also
  accumulated an orphaned `simulations/sim01_pheromone_trails.py` from a superseded layout,
  because copy-based publishing only ever added and overwrote, never deleted.*
- `alife-backup.sh` — periodic backup of the whole wiki.
- `bsky-post "text"` — posts the nightly summary to Bluesky (first person, "Today I…", robot
  emoji, link to `https://alife.vancedubberly.com/reports/YYYY-MM-DD/`, 2–3 hashtags including
  `#AIAgent`, under 300 chars). Save the returned URL in the report.
- `bsky-check-engagement.py` — engagement monitor; appends to `bluesky-engagement.md` every 6h.

The nightly session itself is a scheduled agent job ("ALife Nightly Research", 06:00 UTC) whose
prompt encodes the workflow in §4 — if the workflow changes, that prompt is the thing to update,
not just this file.

## 6. Working notes

- **Read before writing.** Frontmatter first, full text only when relevant. The budget is real.
- **Don't reorganize.** Append to `synthesis.md`, refine concepts in place, mark queued topics
  DONE rather than deleting them. The history of how a claim evolved is part of the data.
- **Report null results honestly**, with root-cause analysis and what the next sim must add.
  `simulations/REVIEW.md` and the 2026-07-27 entry in sim06's DESIGN session log are the model
  for this. (Explicitly *not* sim06's Part 8 session-log entry, which was the previous
  exemplar — its numbers and its root-cause analysis were both wrong, and it was quoted
  forward into sim07's DESIGN before anyone noticed.)
- **Before trusting a null, check the detector can fire.** sim06's crossing criteria included
  one that was unsatisfiable by construction, so the null was guaranteed regardless of the
  model. Any detector should have a test asserting it fires on a synthetic ideal case and
  withholds on single-criterion negatives — see `cmd_selftest` Part 5 in sim06.py.
- **Attribute Vance's contributions.** Ideas he originates get their own labeled sections
  ("Vance's contribution: the termite mound principle") in `synthesis.md` and
  `concepts/stigmergy-vance-notes.md`.
- **Next action — two cheap analyses before any new simulation.** Both came out of the
  2026-07-27 review and both are higher value per token than building sim08:
  1. **What distinguishes sim05's 2 coexisting pairs from the other 4?** (queued-topics #52).
     Pure analysis of the existing `results.json` — no new code. Tests H10 directly, and the
     question did not exist at the old 0/6.
  2. **Repeat sim06's Part-8 parameter sweep against the working detector** (#54). The
     original sweep ran against a detector that could not fire, and the corrected result misses
     only criterion 1 by ≤0.05 — a crossing regime may already lie inside the swept space.

  Then, if a new sim is warranted: the cheapest informative one is **non-saturating
  inhibition** (#53) — a density cap or refractory period acting on deposit probability
  directly — not directed transport. Two attempts at feedback *through the cue field* have now
  fragmented the structure, and the saturating deposit response explains why. Directed
  transport and the external-oscillation path (H4) remain open but are more expensive tests of
  a less well-specified claim.
