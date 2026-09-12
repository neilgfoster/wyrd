# Wyrd — indexing the corpus

The library is 3,841 PDFs; the extracted text corpus will be tens of millions of words.
Most of it is consulted **rarely and unpredictably** — one a periodical adventure about a
corrupt official, once, three years in.

Reading it is not the problem. **Knowing where to look is.**

---

## One index will not do

The right index depends on the shape of the question, and Wyrd asks at least five different
shapes:

| Question | Shape | Index |
|---|---|---|
| "A scenario about a village with something under it" | thematic — no literal term to match | `scenarios` |
| "What are the Fear rules?" | mechanical — known vocabulary | `terms` |
| "Who was the ledger-keeper?" | proper noun — literal but unguessable | `nouns` |
| "A d100 transformation table" | structural — a *kind* of content | `tables` |
| "What is in issue 98 of that magazine?" | bibliographic | `documents` |

A single full-text search serves the middle three badly and the first not at all, because
the thing you are looking for is never named in the text you are looking for.

---

## The five indexes

### 1. `documents.json` — bibliographic

One record per extracted file: id, source path, system, edition, document type
(rules / setting / adventure / magazine / fanzine), page count, whether it came from a text
layer or OCR, and an OCR-confidence estimate.

Deterministic. Built at ingest, per setting repo, catalogueing that setting's own `library/`
([ADR 0052](../adr/0052-the-research-repository-is-retired.md)). A setting repo's own tooling
extracts its `library/` into plain text (extraction and OCR are that repo's own concern, never
the engine's — CLAUDE.md), then calls the engine's `build_setting_corpus_indexes` once across the
whole document set to produce `documents`, `nouns`, `terms` and `tables` together — the
per-document builders behind it never differ from setting to setting, which is what makes this a
pipeline "any `wyrd-setting-*` repo can run against its own `library/`," not bespoke code per
setting.

**OCR confidence matters** and is cheap to compute — dictionary-word ratio per document. A
1980s scan at 60% is usable for locating a passage and untrustworthy for quoting a table.
Anything Wyrd quotes from a low-confidence document should be flagged for eyeball
confirmation against the PDF.

### 2. `nouns.json` — the concordance

Every proper noun in the corpus mapped to where it appears: `name -> [{doc, count, offsets}]`.

Deterministic: capitalised tokens not sentence-initial, frequency-filtered, stop-listed
against common words and OCR noise.

This is the index that makes a long chronicle work. Three years in, "the ledger-keeper" appears in
the player's notes, in an entity, and in an adventure nobody has read since 2026. Proper
nouns are perfectly greppable **once you know they exist** — the concordance is what tells
you they exist, and where the *canonical* mention is rather than the fortieth passing one.

It also catches the reverse case, which is more valuable: the GM invents a name, the
concordance says it already belongs to somebody, and a collision is avoided.

### 3. `terms.json` — mechanical vocabulary

A **curated** vocabulary of mechanical terms — Fear, Terror, taint, transformation, critical,
career exit, trauma, Fate, transformation — mapped to postings, ranked by whether the
hit looks like a *definition* (near a heading, near a table) or a passing mention.

Curated rather than derived, because the vocabulary is small, stable, and known in advance.
Deterministic to apply.

### 4. `tables.json` — structural

Dice tables are the most reusable content in the entire library and the most annoying to
find. They are also **detectable by pattern**: runs of lines beginning with numbers or
ranges (`01-05`, `2`, `11-15`), preceded by a caption, often near a dice notation.

Record: document, offset, dice type (`d6`/`d10`/`d66`/`d100`), row count, and the nearest
preceding heading as a caption guess.

Deterministic. This turns "I need a d100 transformation table" from a search into a lookup, and it
harvests the tables Wyrd's own `engine/tables/` should be seeded from.

### 5. `scenarios.json` — thematic, selectable, and a campaign graph

The largest index and the only one needing a model, justified because **there is no literal
term for "a village with something under it."**

It does three jobs: describe the scenario, let it be *filtered* for fitness, and let
scenarios *chain* into a meta-campaign.

Scope is **this setting's whole library, not one shelf of it** — an investigation written for
another system, a folk-horror village haunting and a magazine six-pager are equally valid
inputs, judged on theme, once triaged into this setting's own `library/`
([ADR 0052](../adr/0052-the-research-repository-is-retired.md)). `adaptation` records what
conversion costs.

```yaml
id: the-drowning-well
source: {system: "a periodical", ref: "WD 98", pages: "34-39"}
adaptation: reskin                    # none | reskin | rewrite
settings: [<setting-id>]

# --- selection inputs: deterministic, evaluated against the player character ---
scale: village                        # village|town|city|wilderness|underground|waterway|road|ship|fortress
region: any
danger: 3                             # as written, for written_for (see 03-rules)
written_for: 4                        # SCALING INPUT, never a gate
length: 2                             # sessions
season: any                           # or winter | harvest | festival
needs_access: [temple]                # an in is required — obtaining it may itself be play
needs_capability: [literacy]          # a companion may supply it
helped_by: [medicine]                 # easier with; harder and better without

# --- thematic: model-generated once, cached ---
tone: [investigation, folk-horror]
themes: [taint-of-water, a-debt-unpaid, complicity]
shape: "a slow poisoning the village already half-knows about"

# --- graph ---
requires_threads: [rural, water, sickness]
emits_threads:
  - {tag: financier-escaped, if: "they are not caught"}
  - {tag: village-owes-you, if: "the well is cleansed"}
consequences: ["the village is materially worse off either way"]
chain: null                           # or {campaign: enemy-within, part: 3}
```

#### Almost nothing gates. Most things modulate.

The library is far too valuable to filter aggressively, and the obvious filters are traps.

**Party size is a scaling input, never a gate.** Nearly every published adventure is written
for four to six adventurers; gating on party size would exclude the entire corpus we went to
the trouble of building. Instead `written_for` feeds the danger calculation:

> `danger_effective = danger × (party_effective / written_for)`

where both party sizes are read as **effective** sizes rather than head counts — the k-th body is
worth `1/k`, so a party of three counts 1.833 and a party of four counts 2.083
([`03-rules.md`](03-rules.md) §7 holds the rule and the arithmetic). A danger-3 arc written for
four, run by one character and two companions, plays at **danger 2.64**: six cultists become five,
three watchmen stay three, and the stat lines and odds come down with them, via the same mechanism
that already scales content. Mob clearing does the rest of the work in combat.

`danger` in the record is therefore *intrinsic difficulty as written for its stated party
size*, not what this table will face. The engine computes the latter.

Field names match the beat schema in [`18-arcs-and-beats.md`](18-arcs-and-beats.md) exactly;
the index is a projection of the entities, not a parallel vocabulary.

**Access and capability are inputs too, not walls.** A low-status character can be hired by someone
with court access, or smuggled in — and *getting the in is often the better scenario*.
A companion can read what the player character cannot. So:

| Field | Effect |
|---|---|
| `needs_access` | an in is required; obtaining it may itself become play |
| `needs_capability` | must be supplied by the player character, a companion, or hired help |
| `helped_by` | flags only — easier with it, and more desperate and interesting without |

`helped_by` is the one that repays attention. An arc easier with literacy is a *better* arc
for a character who can read and a *harder, more frightening* one for a character who cannot.
That is a reason to choose it, not to skip it.

The genuine exclusions are few: wrong setting, or an `adaptation: rewrite` cost that is not
worth paying today. Everything else is a dial. That is the tooling rule
([`27-tooling.md`](27-tooling.md)) applied to selection — the arithmetic is code, the fit is
judgment, and the judgment should almost always be *yes, scaled*.

#### Two kinds of chaining

**Careers form a closed, named graph** — Boatman leads to Smuggler and nothing else, because
one author designed the whole web. Scenarios cannot work that way: they come from 112
systems and **no author wrote them to chain with each other.**

So scenarios use an **open, tag-matched graph**:

- `emits_threads` — what is left open afterwards, *conditional on outcome*
- `requires_threads` — what must already be live for this to be reachable

Selection is then: find scenarios whose `requires_threads` match currently hot threads
([`19-campaign.md`](19-campaign.md)), that pass the deterministic filters, and scale them to
current `T`. The meta-campaign tree is **emergent** rather than authored — which is the only
way it can span a library this heterogeneous, and it avoids the railroad that a fixed tree
would impose.

Where a real chain exists — a published multi-part campaign — it is
recorded in `chain`. Published campaigns keep their sequence; everything else earns its place
by matching threads.

**Haiku-tier** per [`27-tooling.md`](27-tooling.md): structured extraction against text that
already exists. Roughly 400 adventures library-wide, one pass each, cached forever.
Regenerated only when the schema changes.

---

## Indexes are scoped to a setting

Source material is extracted **once** and stored once
([`02-architecture.md`](02-architecture.md)); the indexes over it are **per setting**, because
the same work adapted for two worlds produces two different adaptations.

Index records reference documents **by id**, so a setting indexes shared source material
without holding a copy. Every record names its setting, so a query made in one chronicle
never returns another's material — which is also part of how chronicles stay isolated
([`21-parallel-chronicles.md`](21-parallel-chronicles.md)).

Tagging beats duplicating; scoping beats sharing.

---

## Retrieval

```
wyrd find noun "<a name>"
wyrd find rule "fear test"
wyrd find table --dice d100 --about transformation
wyrd find scenario --hook conspiracy --tone investigation --length short
wyrd find doc --work "<periodical>" --issue 98
```

**Plain `grep` is the fallback and is usually fast enough** — a few tens of MB of text is
nothing. The indexes exist not for speed but to answer questions grep cannot: what exists,
what kind of thing it is, and which of forty mentions is the one that matters.

Every result returns `doc + offset`, so the next step is always a bounded read of the
surrounding passage rather than loading a whole book into context. That bounded read is the
point — it keeps corpus access compatible with the memory tiers in
[`02-architecture.md`](02-architecture.md).

---

## Build and maintenance

| Index | Cost | When |
|---|---|---|
| `documents` | trivial | at ingest |
| `nouns` | one pass, deterministic | at ingest |
| `terms` | one pass, deterministic | at ingest |
| `tables` | one pass, deterministic | at ingest |
| `scenarios` | one Haiku call per adventure | lazily, on first need, then cached |

Four of five are free and built once. The expensive one is **lazy** — an adventure gets its
thematic record the first time anything asks for it, not up front. Most of the library will
never need one.

The lazy-cache rule is concrete, not just descriptive: a document's cached `scenarios.json`
record is **fresh** only when both its content hash and the record schema's version still match
what produced it; either one changing marks it **stale** and due for regeneration, and a document
with no cache entry at all is **missing**. The engine decides freshness; it never performs the
model call itself — that stays injected by the caller, so building this decision is fully
testable without ever reaching a real model.

Rebuilding is a `wyrd optimise` function
([`28-maintenance.md`](28-maintenance.md)), and `wyrd doctor` reports index staleness
against the corpus.

## Scheduled execution

Pass 0's catalogue, gap-survey and idempotence pass, and the four deterministic indexes above
(`documents`, `nouns`, `terms`, `tables`), share one property the `scenarios` index does not: no
step in them calls a model, so nothing about running them stops them running unattended, on a
schedule, with nobody watching. They are recommended to run that way.

**The workflow runs inside the setting repository, never anywhere else.** A setting repository is
already its own GitHub repository, private where its sources require it. GitHub Actions'
`schedule` (cron) trigger, defined in that repository's own `.github/workflows/`, keeps every
read of `library/` and every write to `index/` inside that one repository's own runner and
permission boundary — no source material or derived index ever crosses into a shared or public
repository to make this work. A schedule looks like:

```yaml
# illustrative only -- belongs in a wyrd-setting-<name> repo's own
# .github/workflows/, never in this repo
on:
  schedule:
    - cron: "0 6 * * 1"   # weekly; a setting repo tunes this to how often library/ changes
jobs:
  build-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 tools/setting_pass0.py .
      - run: python3 -c "from wyrd.corpus_pipeline import build_setting_corpus_indexes; ..."
```

**The `scenarios` index is excluded from the scheduled run.** Its one Haiku call per adventure is
the pipeline's only non-deterministic step, and it already has the right cadence for that:
lazy, on first need, cached forever, regenerated only on a schema change. Putting it behind a
blind schedule would add a new failure mode — a bad or drifted generation, unnoticed until
something reads it — that the lazy path does not have; nothing about issue #102's own request
requires trading that away.

**A scheduled run's failure must be observable, never silent.** Nobody is watching a scheduled
run in real time, so its failure — a step errors, or the workflow itself never fires — has to
surface through the runner's own failure reporting (GitHub Actions' own run-failure status and
notification) rather than disappearing. A scheduled workflow that fails quietly is worse than no
schedule at all, because it replaces a known gap with an unknown one.

## Public augmentation and provenance

A setting's library is private, but a gap Pass 0's own gap survey names (#100) does not have to
stay a gap forever — a public source may fill it, under one explicit rule:

> **A public source is in-bounds only when it carries its own independently checkable
> provenance, not contingent on the private library already existing.** A public-domain text, an
> author's or publisher's own freely and openly published material (errata, an SRD, an open-
> licensed glossary), or broadly attested common knowledge (folklore, an independently checkable
> real-world reference fact) all qualify. **"Found on the open internet" does not, by itself** —
> an arbitrary page with no traceable origin or licence is out of bounds, the same way an
> unverified claim is everywhere else in this engine's own deterministic-over-inference rule
> ([`27-tooling.md`](27-tooling.md)).

Every derived fact produced this way — whether from the library or from a qualifying public
source — carries a **provenance record**: `origin` (`library` or `public`) and, when `origin` is
`public`, a `reference` naming the specific source a reader could go check. A library-sourced
fact needs no separate reference — its provenance is the `documents.json` record it was already
extracted from. `engine/wyrd/corpus_provenance.py`'s `build_provenance_record` is this record's
pure, no-I/O implementation: a setting repository's own tooling calls it with a source it has
already identified and cited, exactly as it already calls `corpus_pipeline.build_setting_corpus_
indexes` with text it has already extracted. Neither this module nor anything else in this
repository performs the fetch itself — CLAUDE.md's "no tooling that fetches source material"
applies here exactly as it does to every other corpus module; an actual web fetch, if a setting
repository wants one, is that repository's own tooling to write.

## World-building content, and what is not indexed

Prose world-building material — regional gazetteers, organisation write-ups, histories, what an
ordinary person knows about daily life — is tagged with one of a closed set of categories
(`geography`, `factions`, `history`, `daily-life`) at ingest. A tagged document still gets a
`documents.json` record and contributes to the concordance exactly like any other document — that
is how such material is actually reached in play, not "tell me about Ostland" but "what is this
place the player just mentioned?" — but it is **never** run through `terms.json`/`tables.json`
detection: mechanical-vocabulary and table-shape detection have nothing to find in prose, and
running them anyway would only risk false-positive matches. This is the one boundary the pipeline enforces on the setting's behalf, rather than leaving it to
per-document judgment: world-building content is produced and kept distinct from mechanical
content in `terms.json`/`tables.json`, while still being catalogued and concordance-findable from
the moment it is ingested, the same as everything else in the corpus. Its value past that point is
still in the reading, not in a mechanical index that was never the right tool for prose.
