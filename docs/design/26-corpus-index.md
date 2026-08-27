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

Deterministic. Built at ingest. This is [`library.md`](https://github.com/neilgfoster/wyrd-research/blob/main/reference/library.md)
made machine-queryable and extended with what extraction learned.

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

Scope is **the whole library, not one shelf of it** — an investigation written for another world, a
folk-horror village haunting and a magazine six-pager are equally valid inputs, judged on theme
([`library-triage.md`](https://github.com/neilgfoster/wyrd-research/blob/main/reference/library-triage.md)). `adaptation` records
what conversion costs.

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

Rebuilding is a `wyrd optimise` function
([`28-maintenance.md`](28-maintenance.md)), and `wyrd doctor` reports index staleness
against the corpus.

## What is not indexed

Prose setting material — regional gazetteers, organisation write-ups, histories. It is read on
demand and its value is in the reading. The concordance already makes it findable by name,
which is how it is actually reached in play: not "tell me about Ostland" but "what is this
place the player just mentioned?"
