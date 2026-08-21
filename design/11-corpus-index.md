# Wyrd — indexing the corpus

The library is 3,841 PDFs; the extracted text corpus will be tens of millions of words.
Most of it is consulted **rarely and unpredictably** — one White Dwarf adventure about a
corrupt miller, once, three years in.

Reading it is not the problem. **Knowing where to look is.**

---

## One index will not do

The right index depends on the shape of the question, and Wyrd asks at least five different
shapes:

| Question | Shape | Index |
|---|---|---|
| "A scenario about a village with something under it" | thematic — no literal term to match | `scenarios` |
| "What are the Fear rules?" | mechanical — known vocabulary | `terms` |
| "Who was Hallam Weissbruck?" | proper noun — literal but unguessable | `nouns` |
| "A d100 mutation table" | structural — a *kind* of content | `tables` |
| "What's in White Dwarf 98?" | bibliographic | `documents` |

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

This is the index that makes a long chronicle work. Three years in, "Weissbruck" appears in
the player's notes, in a codex entry, and in an adventure nobody has read since 2026. Proper
nouns are perfectly greppable **once you know they exist** — the concordance is what tells
you they exist, and where the *canonical* mention is rather than the fortieth passing one.

It also catches the reverse case, which is more valuable: Claude invents a name, the
concordance says it already belongs to somebody, and a collision is avoided.

### 3. `terms.json` — mechanical vocabulary

A **curated** vocabulary of mechanical terms — Fear, Terror, corruption, mutation, critical,
career exit, insanity, Fate, miscast, warpstone — mapped to postings, ranked by whether the
hit looks like a *definition* (near a heading, near a table) or a passing mention.

Curated rather than derived, because the vocabulary is small, stable, and known in advance.
Deterministic to apply.

### 4. `tables.json` — structural

Dice tables are the most reusable content in the entire library and the most annoying to
find. They are also **detectable by pattern**: runs of lines beginning with numbers or
ranges (`01-05`, `2`, `11-15`), preceded by a caption, often near a dice notation.

Record: document, offset, dice type (`d6`/`d10`/`d66`/`d100`), row count, and the nearest
preceding heading as a caption guess.

Deterministic. This turns "I need a d100 mutation table" from a search into a lookup, and it
harvests the tables Wyrd's own `engine/tables/` should be seeded from.

### 5. `scenarios.json` — thematic, selectable, and a campaign graph

The largest index and the only one needing a model, justified because **there is no literal
term for "a village with something under it."**

It does three jobs: describe the scenario, let it be *filtered* for fitness, and let
scenarios *chain* into a meta-campaign.

Scope is **the whole library, not the WFRP shelf** — a Deadlands investigation, a Maelstrom
village horror and a *White Dwarf* six-pager are equally valid inputs, judged on theme
([`library-triage.md`](https://github.com/neilgfoster/wyrd-research/blob/main/reference/library-triage.md)). `adaptation` records
what conversion costs.

```yaml
id: the-drowning-well
source: {system: "White Dwarf", ref: "WD 98", pages: "34-39"}
adaptation: reskin                    # none | reskin | rewrite
settings: [reikland, imperium]

# --- selection inputs: deterministic, evaluated against pc.yaml ---
scale: village                        # village|town|city|wilderness|underground|waterway|road|ship|fortress
region: any
threat: 3                             # T as written, for party_written_for (see 03-rules)
party_written_for: 4                  # SCALING INPUT, never a gate
length: 2                             # sessions
season: any                           # or winter | harvest | festival
needs_access: [temple]                # an in is required — obtaining it may itself be play
needs_capability: [literacy]          # a companion may supply it
helped_by: [medicine]                 # easier with; harder and better without

# --- thematic: model-generated once, cached ---
tone: [investigation, folk-horror]
themes: [corruption-of-water, a-debt-unpaid, complicity]
shape: "a slow poisoning the village already half-knows about"

# --- graph ---
requires_threads: [rural, water, sickness]
emits_threads:
  - {tag: patron-escaped, if: "the patron is not caught"}
  - {tag: village-owes-you, if: "the well is cleansed"}
consequences: ["the village is materially worse off either way"]
chain: null                           # or {campaign: enemy-within, part: 3}
```

#### Almost nothing gates. Most things modulate.

The library is far too valuable to filter aggressively, and the obvious filters are traps.

**Party size is a scaling input, never a gate.** Nearly every published adventure is written
for four to six adventurers; gating on party size would exclude the entire corpus we went to
the trouble of building. Instead `party_written_for` feeds the threat calculation:

> `T_effective = T × (party_effective / party_written_for)`

where `party_effective` counts the PC as 1 and each companion at a fraction, since companions
are GM-run and less capable. A T3 scenario written for four, run by a PC and two companions,
plays at roughly T2 — fewer enemies, lower stat lines, shorter odds — via the same mechanism
that already scales content ([`03-rules.md`](03-rules.md)). Scarlet Heroes' Fray die does the
rest of the work in combat.

`threat` in the record is therefore *intrinsic danger as written for its stated party size*,
not the danger this table will face. The engine computes the latter.

**Access and capability are inputs too, not walls.** A rat-catcher can be hired by someone
with court access, or smuggled in — and *getting the in is often the better scenario*.
A companion can read the grimoire the PC cannot. So:

| Field | Effect |
|---|---|
| `needs_access` | an in is required; obtaining it may itself become play |
| `needs_capability` | must be supplied by the PC, a companion, or hired help |
| `helped_by` | flags only — easier with it, and more desperate and interesting without |

`helped_by` is the one that repays attention. A scenario easier with literacy is a *better*
scenario for an Initiate and a *harder, more frightening* one for a rat-catcher. That is a
reason to choose it.

The genuine exclusions are few: wrong setting, or an `adaptation: rewrite` cost that is not
worth paying today. Everything else is a dial. That is the tooling rule
([`07-tooling.md`](07-tooling.md)) applied to selection — the arithmetic is code, the fit is
judgment, and the judgment should almost always be *yes, scaled*.

#### Two kinds of chaining

**Careers form a closed, named graph** — Boatman leads to Smuggler and nothing else, because
one author designed the whole web. Scenarios cannot work that way: they come from 112
systems and **no author wrote them to chain with each other.**

So scenarios use an **open, tag-matched graph**:

- `emits_threads` — what is left open afterwards, *conditional on outcome*
- `requires_threads` — what must already be live for this to be reachable

Selection is then: find scenarios whose `requires_threads` match currently hot threads
([`05-campaign.md`](05-campaign.md)), that pass the deterministic filters, and scale them to
current `T`. The meta-campaign tree is **emergent** rather than authored — which is the only
way it can span a library this heterogeneous, and it avoids the railroad that a fixed tree
would impose.

Where a real chain exists — *The Enemy Within*'s eight parts, *Paths of the Damned* — it is
recorded in `chain`. Published campaigns keep their sequence; everything else earns its place
by matching threads.

**Haiku-tier** per [`07-tooling.md`](07-tooling.md): structured extraction against text that
already exists. Roughly 400 adventures library-wide, one pass each, cached forever.
Regenerated only when the schema changes.

---

## Retrieval

```
wyrd find noun "Weissbruck"
wyrd find rule "fear test"
wyrd find table --dice d100 --about mutation
wyrd find scenario --hook cult --tone investigation --length short
wyrd find doc --system "White Dwarf" --issue 98
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
([`08-maintenance.md`](08-maintenance.md)), and `wyrd doctor` reports index staleness
against the corpus.

## What is not indexed

Prose setting material — regional gazetteers, cult descriptions, histories. It is read on
demand and its value is in the reading. The concordance already makes it findable by name,
which is how it is actually reached in play: not "tell me about Ostland" but "what is this
place the player just mentioned?"
