# Research: Bibliographic and concordance indexes (documents.json, nouns.json)

No `[NEEDS CLARIFICATION]` markers remain in spec.md. Three decisions worth recording:

- **Decision**: `ocr_confidence` is the fraction of whitespace-split tokens matching a
  "plausible word" regex: purely alphabetic, length 2-20, and not an implausible
  consonant/vowel run (fewer than 3 consecutive identical-class characters).
  **Rationale**: the design document's own phrasing ("dictionary-word ratio") calls for a real
  word list, which is not a stdlib resource and this repo adds no third-party dependency
  (CLAUDE.md's "Python 3.11+, standard library only" convention, followed by every other module
  in this codebase). A word-shape heuristic is the closest deterministic stdlib-only proxy: OCR
  garbage on a scanned page characteristically produces short symbol/digit-heavy fragments and
  implausible letter runs, which this heuristic penalises even without a real dictionary.
  **Alternatives considered**: shipping a bundled word list as a data file — rejected as scope
  creep for this feature (a real word list is a meaningfully sized asset with its own licensing
  question, and this repo's own constitution is wary of anything that starts to look like
  "a catalogue" entering the engine); a fixed/guessed confidence value — rejected outright, since
  FR-002 explicitly requires it be computed from the text, not fixed.

- **Decision**: sentence-boundary detection for the concordance is a single regex:
  `[.!?]\s+` followed by testing whether the *next* token starts with an uppercase letter — a
  token immediately after such a boundary (or at the very start of the text) is sentence-initial
  and excluded regardless of capitalisation; every other capitalised token is a candidate.
  **Rationale**: the design document's own framing treats these indexes as "deterministic" and
  "one pass" — a full sentence splitter (handling abbreviations, quotations, etc.) is
  disproportionate ceremony for a heuristic the design document itself calls approximate; the
  plain `.`/`!`/`?`-plus-whitespace rule is the direct reading of "not sentence-initial" without
  inventing NLP machinery this codebase has no other use for.
  **Alternatives considered**: a proper NLP sentence tokenizer (e.g. `nltk.sent_tokenize`) —
  rejected as a third-party dependency this repo's stdlib-only constraint forbids.

- **Decision**: the stop list is a small, fixed Python set of common English words (~40 entries:
  articles, conjunctions, common sentence-openers like "The", "And", "But", "When", "If").
  **Rationale**: docs/design/26-corpus-index.md explicitly calls for the concordance to be
  "stop-listed against common words and OCR noise" — a small fixed set is sufficient to satisfy
  FR-005's acceptance criterion (a stop-listed word is excluded regardless of position) without
  needing a comprehensive general-English stop-word corpus, which again would be a third-party
  dependency or a bundled data asset out of this feature's scope.
  **Alternatives considered**: none seriously — the acceptance criterion only requires that
  *some* stop list functions correctly, not that it be exhaustive; exhaustiveness is explicitly
  deferred in spec.md's Assumptions.
