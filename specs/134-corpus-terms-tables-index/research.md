# Research: Curated term and structural table indexes (terms.json, tables.json)

No `[NEEDS CLARIFICATION]` markers remain in spec.md. Three decisions worth recording:

- **Decision**: a "heading-like line" is a line under 60 characters with no terminal sentence
  punctuation, or a markdown `#`-prefixed line; "near" means within the 2 lines immediately
  before the term's own line.
  **Rationale**: extracted PDF text carries no reliable layout metadata (font size, boldness) —
  the only signal available is line shape. A short line ending without `.`/`!`/`?` is the
  standard proxy for "this reads like a heading, not a sentence", matching #354's own established
  convention of a cheap, documented, stdlib-only heuristic over a real parser.
  **Alternatives considered**: requiring a fixed heading marker (`#`) only — rejected, since real
  extracted text from a PDF/OCR source rarely carries markdown syntax; the design document's own
  examples are prose-extracted, not born-markdown.

- **Decision**: a table row is `^\s*(\d{1,3}(-\d{1,3})?)\s+\S` — a leading number or
  number-range key, then whitespace, then non-whitespace content, evaluated per line; a run of
  2+ consecutive matching lines is a table.
  **Rationale**: matches the design document's own worked examples (`01-05`, `2`, `11-15`)
  exactly, and the "run, not a single line" requirement (FR-005) is the direct reading of "runs
  of lines" in the design's own phrasing.
  **Alternatives considered**: a single matching line counting as a table on its own — rejected;
  explicitly contradicted by FR-005/Acceptance Scenario 4, since a lone row-shaped line is
  routine noise (a numbered list item, a page number) rather than evidence of a dice table.

- **Decision**: dice type is inferred purely from the numeric range covered by the run's keys
  (max endpoint 6/10/66/100), not from any dice-notation text nearby.
  **Rationale**: the design document's own record shape lists `dice type (d6/d10/d66/d100)` as a
  field the detector records, and its "structural, detectable by pattern" framing points at the
  numbers themselves as the signal, not prose dice notation which may not appear near every
  table (many published tables are captioned "roll 2d6" once, far from the table itself, or not
  at all).
  **Alternatives considered**: scanning nearby text for literal `d6`/`d10`/`d66`/`d100` strings
  and preferring that over the numeric inference — rejected as an unnecessary second signal for
  this feature's scope; the numeric-range inference alone satisfies every stated acceptance
  scenario, and combining signals is a natural additive extension if real corpus runs show gaps.
