# Feature Specification: Curated term and structural table indexes (terms.json, tables.json)

**Feature Branch**: `134-corpus-terms-tables-index`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Curated term and structural table indexes (terms.json, tables.json)" (issue #355)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - "What are the Fear rules?" finds the definition, not a passing mention (Priority: P1)

A GM asks a mechanical-vocabulary question. The term index maps a small, fixed set of known
mechanical terms to every place they occur, ranking a hit that looks like the term's actual
definition (near a heading) above one that merely mentions it in passing.

**Why this priority**: this is the entire point of a curated index over grep — a mechanical term
appears dozens of times in a large corpus, and only one or two of those are the definition worth
reading.

**Independent Test**: given a passage containing both a heading-adjacent occurrence of a curated
term and a plain-prose occurrence, confirm the heading-adjacent one is ranked `definition` and
the other `mention`.

**Acceptance Scenarios**:

1. **Given** a curated term appearing on the line immediately after a heading-like line, **When**
   the term index is built, **Then** that occurrence is ranked `definition`.
2. **Given** the same term appearing elsewhere in ordinary prose with no nearby heading,
   **When** the term index is built, **Then** that occurrence is ranked `mention`.
3. **Given** a word that is not in the curated vocabulary, **When** the term index is built,
   **Then** it produces no entry for that word — the vocabulary is closed, not derived from the
   text.
4. **Given** a curated term appearing with different capitalisation ("fear", "Fear", "FEAR"),
   **When** the term index is built, **Then** all three are matched as the same term.

---

### User Story 2 - "I need a d100 transformation table" is a lookup, not a search (Priority: P1)

A run of range-prefixed lines — `01-05`, `06-10`, ... `96-100` — preceded by a caption is a dice
table. The structural index detects it by shape alone, without knowing what it's about, and
records its dice type, row count, and a caption guess drawn from the nearest preceding line.

**Why this priority**: this is the design document's own stated purpose — turning "I need a
d100 transformation table" from a search into a lookup — and dice tables are, per the design,
"the most reusable content in the entire library."

**Independent Test**: given a passage containing a run of range-keyed lines matching a known dice
shape, preceded by a caption line, confirm the detector reports the correct dice type, row count,
and caption.

**Acceptance Scenarios**:

1. **Given** a run of ten range-keyed lines spanning `01-10` through `91-100`, **When** the table
   detector runs, **Then** it reports `dice: "d100"` and `row_count: 10`.
2. **Given** a run of six single-value-keyed lines `1` through `6`, **When** the table detector
   runs, **Then** it reports `dice: "d6"`.
3. **Given** a run of range-keyed lines immediately preceded by a non-row line, **When** the
   table detector runs, **Then** that preceding line is reported as the `caption` guess.
4. **Given** a single row-shaped line with no second row following it, **When** the table
   detector runs, **Then** it is not reported as a table — a table is a *run*, never a single
   line.

### Edge Cases

- Text with no curated term present produces an empty term index, never an error.
- Text with no row-shaped lines at all produces an empty table list, never an error.
- A row-shaped line embedded in ordinary prose (a single stray line matching the pattern, not
  part of a real run) is not reported as a table, per Acceptance Scenario 4.
- A term occurrence with no preceding line at all (start of text) is ranked `mention`, not
  `definition` — there is nothing to be near.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a curated, fixed vocabulary of mechanical terms (at least
  Fear, Terror, taint, transformation, critical, career exit, trauma, Fate) and match a term's
  occurrences in a text case-insensitively.
- **FR-002**: The engine MUST rank each matched occurrence `definition` when it is near a
  heading-like line (within a small fixed line window immediately before it), and `mention`
  otherwise.
- **FR-003**: The engine MUST NOT produce an entry for a word outside the curated vocabulary,
  regardless of how it appears in the text.
- **FR-004**: The engine MUST detect a run of two or more consecutive range/number-keyed lines
  as a table, recording its document, offset, dice type, row count, and a caption guess drawn
  from the nearest preceding non-row line.
- **FR-005**: A single row-shaped line with no adjacent row MUST NOT be reported as a table.
- **FR-006**: Dice type MUST be inferred from the run's key values: a maximum endpoint of 6
  implies `d6`, 10 implies `d10`, 66 (with every key a two-digit number whose digits are each
  1-6) implies `d66`, and 100 implies `d100`; a run matching none of these is reported with
  `dice: null` rather than a guessed value.
- **FR-007**: Every term-index and table-index record MUST carry the `setting` it was built for.

### Key Entities

- **Term posting**: `{term, doc, setting, offset, rank: "definition" | "mention"}`
  (docs/design/26-corpus-index.md § "3. terms.json").
- **Table record**: `{doc, setting, offset, dice: "d6" | "d10" | "d66" | "d100" | null,
  row_count, caption}` (docs/design/26-corpus-index.md § "4. tables.json").

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A heading-adjacent occurrence is always ranked above a passing mention of the same
  term — verified by exact-input tests, not eyeballed.
- **SC-002**: Every one of the four dice types is correctly inferred from its own worked example
  in tests.
- **SC-003**: A single stray row-shaped line never produces a table record.
- **SC-004**: Every produced record (term posting or table) carries its `setting`.

## Assumptions

- This feature is a runtime-logic slice only: plain strings/dicts in, plain dicts out, no I/O —
  matching #354's `corpus_document.py` convention exactly (same epic, same division of labour).
- "Near a heading" is a documented, deterministic heuristic: a heading-like line is a short
  (under 60 characters) line with no terminal sentence punctuation (`.`/`!`/`?`), or a markdown
  `#`-prefixed line — the same kind of stdlib-only, pattern-based proxy #354's `ocr_confidence`
  already establishes as this codebase's convention for "deterministic and cheap" over a real
  layout-aware parser. "Within a small fixed line window" is 2 lines.
- A row-keyed line is `^\s*(\d{1,3}(-\d{1,3})?)\s+\S` — a leading number or number-range key
  followed by descriptive text on the same line — matching the design document's own worked
  examples (`01-05`, `2`, `11-15`) exactly.
- The curated vocabulary is fixed in this feature's own source, not configurable per setting or
  loaded from a file — matching `succession.py`'s (#340) closed-vocabulary precedent. Extending
  it later is a small, additive change, not a structural one.
- This feature does not implement the "near a table" half of definition-ranking mentioned in the
  design's prose alongside "near a heading" — heading-proximity alone is the deterministic signal
  this feature implements; extending ranking to also consider table proximity is a natural,
  additive follow-up once both indexes' record shapes are settled, not required for this
  feature's own acceptance criteria (which name only "near a heading" explicitly in their
  worked scenarios).
