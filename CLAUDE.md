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
sim06's null result is one of the most valuable things in the repo.

**Current state (as of Session 10, 2026-07-27):** 10 hypotheses (H1–H10), 16 concept files,
sims 01–07 built (sim07 implemented Session 10 — null result), sim08 designed but **not yet
implemented** (top priority). Everything hangs on **H7, the Trace→Actor Crossing Hypothesis** —
sim06 produced a null (positive feedback alone insufficient), sim07 produced a null (scalar
structure-sourced transport insufficient — wrong sign for consolidation), and the crossing is now
specified to require *directed* transport and/or an *externally-driven* one (H4). sim08 tests the
external-oscillation path.

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
    hypotheses.md      — ALL hypotheses in one file (H1–H10) + a summary status table
  concepts/            — one living document per topic cluster, refined across sessions
  daily-reports/       — YYYY-MM-DD.md session logs (one per nightly run)
  researchers/         — per-researcher notes (currently EMPTY — unused so far)
  simulations/         — Python building-block sims, one folder each
```

**Concepts** (`concepts/*.md`) are living documents, not session logs. Refine an existing file
rather than adding a new one unless the topic is genuinely new. Each has (or should have) a
"Criticisms" section and an "Empirical Evidence" section — this is a methodological requirement,
not decoration.

**Simulations** (`simulations/simNN_shortname/`):

| sim | topic | result |
|---|---|---|
| sim01_pheromone_trails | stigmergic coordination | trails form |
| sim02_dynamic_landscape | static vs. agent-modified fitness landscape | both converge; dynamic converges harder |
| sim03_chemical_organizations | Chemical Organization Theory, fixed network | converges by gen 1, stalls |
| sim04_evolving_networks | evolving reaction network, finite space | exhausts space, stalls |
| sim05_lambda_chemistry | AlChemy, unbounded space | L1 forms, L2 composition 0/6 (→H10) |
| sim06_termite_mound | H7 trace→actor crossing | **null**: +66% structure, detector never fires |
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

Stage narrowly: `cd ~/brain && git add artificial-life/ && git commit -m "…"`.

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
5. **Hypothesize** — add or refine in `hypotheses/hypotheses.md`. Refinements are **appended as
   dated "Refinement (Session N)" paragraphs**, never overwriting the original claim, and the
   summary table at the bottom is updated.
6. **Simulate** — small, focused sims that solve one sub-problem; building blocks for the eventual
   system, not the system itself.
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
- `alife-link-terms.py` — rewrites the first occurrence of each known term (H1–H10, concept names,
  glossary terms) in a daily report into a public-site hyperlink. Run on tonight's report before
  committing: `python3 ~/.local/bin/alife-link-terms.py <report.md>` (or `--all`). When a new
  concept or hypothesis is added, add it to this script's `TERMS` map. Note: it has re-linked
  already-linked text in the past, producing doubled URLs — check the diff.
- `alife-convert-concepts.py` — converts concept markdown (frontmatter and all) into the static
  site's page format.
- `alife-deploy-site.sh` — builds the static site (Zola, sources from this directory plus
  `~/alife-site/`) and publishes it.
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
  sim06's README and Part 8 session-log entry are the model for this.
- **Attribute Vance's contributions.** Ideas he originates get their own labeled sections
  ("Vance's contribution: the termite mound principle") in `synthesis.md` and
  `concepts/stigmergy-vance-notes.md`.
- **Next action:** implement sim07 Part-by-Part per `simulations/sim07_transport_coupling/DESIGN.md`
  — the transport field `T`, the `M_c` inert→active threshold, the `M_c` sweep, and the self-repair
  test that guards against building in the crossing we claim to detect.
