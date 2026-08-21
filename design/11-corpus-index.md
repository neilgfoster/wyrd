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

Deterministic. Built at ingest. This is [`../reference/library.md`](../reference/library.md)
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

### 5. `scenarios.json` — thematic

The only index needing a model, and the only one where that is justified: **there is no
literal term for "a village with something under it."**

Per adventure, generated **once** and cached: hooks, themes, tone, approximate length in
sessions, cast size, whether it needs a map, the shape of the situation, and what threads it
would emit. This is the record [`05-campaign.md`](05-campaign.md)'s scenario selection
matches against.

**Haiku-tier** per [`07-tooling.md`](07-tooling.md) — bulk structured extraction against
existing text, with a right answer. Roughly 400 adventures across the library, one pass
each, cached forever. Regenerated only when the schema changes.

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
