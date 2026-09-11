# Feature Specification: Bibliographic and concordance indexes (documents.json, nouns.json)

**Feature Branch**: `133-corpus-document-nouns-index`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Bibliographic and concordance indexes (documents.json, nouns.json)" (issue #354)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every extracted source gets a bibliographic record (Priority: P1)

A setting has extracted a source document's text; the engine builds one queryable record
describing what it is — id, path, system, edition, type, page count, whether it came from a text
layer or OCR, and an OCR-confidence estimate — so a GM can later ask "what is in issue 98 of
that magazine?" without opening the file.

**Why this priority**: every other index in this epic (#355, #356, #357) references a document
by id — nothing else can exist until a document has one.

**Independent Test**: given a source's metadata and its extracted text, confirm the returned
record carries every documented field, and that its OCR-confidence estimate reflects the text's
actual quality (a clean passage scores higher than a garbled one).

**Acceptance Scenarios**:

1. **Given** a source's id, path, system, edition, document type, page count, and extraction
   method (`text_layer` or `ocr`), **When** a document record is built, **Then** the returned
   record carries all six fields unchanged, plus a computed `ocr_confidence`.
2. **Given** two texts of equal length, one composed of well-formed words and one of scrambled
   character runs, **When** OCR confidence is computed for each, **Then** the well-formed text
   scores strictly higher.
3. **Given** a document record, **When** it is built, **Then** it carries the `setting` it was
   built for (docs/design/26-corpus-index.md: "every record names its setting").

---

### User Story 2 - A proper noun's every appearance is findable (Priority: P1)

Three years into a chronicle, "the ledger-keeper" appears in the player's notes, an entity, and
an adventure nobody has read since. The concordance maps every proper noun in the corpus to
where it appears, so a GM (or the engine, checking for a name collision before inventing one)
can find it without re-reading anything.

**Why this priority**: this is the mechanism the design document calls out as "what makes a long
chronicle work" — without it, a name's canonical source is unrecoverable once forgotten.

**Independent Test**: given a passage of text, confirm every capitalised word that is not the
first word of its sentence is recorded as a candidate noun, with its document id, an occurrence
count, and character offsets — and that a sentence-initial capitalised word (an ordinary word
starting a sentence) is not.

**Acceptance Scenarios**:

1. **Given** a passage containing a proper noun that appears mid-sentence, **When** the
   concordance is built, **Then** that noun is recorded with the document id, its occurrence
   count, and the character offset of every appearance.
2. **Given** a passage whose only capitalised words are sentence-initial ("The village was
   quiet. The well was old."), **When** the concordance is built, **Then** neither "The" nor any
   other sentence-initial word is recorded — sentence-initial capitalisation alone is not
   evidence of a proper noun.
3. **Given** the same proper noun appearing in two different documents, **When** the concordance
   is built across both, **Then** its entry lists both documents, each with its own count and
   offsets.
4. **Given** a common word that happens to be stop-listed (e.g. "The", "And"), **When** it
   appears mid-sentence in capitalised form, **Then** it is still excluded — the stop list is
   checked regardless of sentence position.

### Edge Cases

- An empty text input produces an empty document/concordance result, never an error.
- A word appearing only once anywhere in the corpus is still recorded — "frequency-filtered"
  (docs/design/26-corpus-index.md) is read as filtering *noise* (single-character fragments, OCR
  garbage), not filtering out genuinely rare-but-real names, since a name that appears exactly
  once is exactly the kind of thing the concordance exists to catch (spec.md's Assumptions).
- A capitalised word immediately following an abbreviation's period (e.g. "Mr. Smith") is not
  treated as sentence-initial merely because it follows a `.` — the sentence-boundary heuristic
  only fires on `.`/`!`/`?` followed by whitespace and a capital letter *and* is itself preceded
  by whitespace or start-of-text, a plain best-effort heuristic documented as such, not a full
  natural-language sentence splitter.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a way to build a document record carrying `id`, `path`,
  `system`, `edition`, `document_type`, `page_count`, `extraction_method`
  (`text_layer` | `ocr`), a computed `ocr_confidence`, and `setting`.
- **FR-002**: `ocr_confidence` MUST be computed from the document's own extracted text as a
  deterministic ratio of well-formed word-shaped tokens to total tokens — never a guessed or
  fixed value.
- **FR-003**: The engine MUST provide a way to build a concordance mapping a proper-noun
  candidate to every document it appears in, each with an occurrence count and character
  offsets.
- **FR-004**: A candidate MUST be a capitalised token that is **not** the first token of its
  sentence — sentence-initial capitalisation alone MUST NOT be recorded.
- **FR-005**: A candidate matching a stop list of common words MUST be excluded regardless of
  sentence position.
- **FR-006**: Every concordance entry and document record MUST carry the `setting` it was built
  for.

### Key Entities

- **Document record**: `{id, path, system, edition, document_type, page_count,
  extraction_method, ocr_confidence, setting}` (docs/design/26-corpus-index.md § "1.
  documents.json").
- **Concordance entry**: `name -> [{doc, count, offsets: list[int]}]` (docs/design/26-corpus-
  index.md § "2. nouns.json").

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A well-formed passage's `ocr_confidence` is always strictly higher than a garbled
  passage of the same length — verified by exact-input tests.
- **SC-002**: Every sentence-initial capitalised word in a tested passage is excluded from the
  concordance, and every non-sentence-initial capitalised word (not stop-listed) is included —
  verified by exact-input tests, not eyeballed.
- **SC-003**: A concordance built across two documents correctly attributes each occurrence to
  its own document, never merging counts across documents into one entry.

## Assumptions

- This feature is a runtime-logic slice only: plain strings/dicts in, plain dicts out, no file
  I/O — this tooling never fetches, stores, or reads source material itself (CLAUDE.md's explicit
  constraint on this repo); a setting repo supplies already-extracted text and metadata as plain
  Python values.
- `ocr_confidence` is computed by a simple, stdlib-only heuristic (the ratio of tokens matching a
  plausible-word shape: alphabetic, reasonable length, not all-consonant/all-vowel runs) — not a
  true dictionary lookup, since no dictionary word list is a stdlib resource and this repo adds
  no third-party dependency. This is a lower-fidelity proxy than the design document's own
  "dictionary-word ratio" phrasing implies literally; documented here rather than silently
  overclaiming accuracy.
- "Frequency-filtered" is read as filtering token-level noise (very short fragments, digit-heavy
  runs) rather than filtering out singly-occurring real names — a name that appears once is
  still recorded (Edge Cases).
- The stop list is a small, fixed set of common English words (articles, conjunctions, common
  sentence-openers) — not a comprehensive list, and not configurable per setting in this
  feature; extending it is left for a later pass if real corpus runs show gaps.
- Sentence-boundary detection is a plain, documented heuristic (`.`/`!`/`?` + whitespace + a
  capital letter), not a full natural-language sentence splitter — matching the design
  document's own framing of these indexes as "deterministic" and "cheap", not linguistically
  exhaustive.
