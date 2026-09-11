# Research: Check: no implicit current-chronicle global state

No `[NEEDS CLARIFICATION]` markers remain in spec.md. Two decisions worth recording:

- **Decision**: candidate detection uses `ast.parse` over the module's `tree.body` (only
  top-level statements), not a text/regex scan.
  **Rationale**: a regex risks false positives inside a function body, a docstring, or a string
  literal that merely *looks* like `_name: dict = {}` -- `ast` gives exact, unambiguous
  top-level-vs-nested discrimination for free, the same reliability
  `check_dangling_mechanics.py`'s own module docstring argues for structural detection over
  pattern-guessing in its "detected structurally, not semantically" reasoning.
  **Alternatives considered**: a line-based regex scan (simpler to write) -- rejected; it cannot
  distinguish a module-level assignment from an indented one inside a function without
  re-implementing indentation-aware parsing, which `ast` already does correctly.

- **Decision**: `"process-local"` (case-insensitive) is the one recognised justification
  marker, matched against the comment lines immediately preceding the assignment (contiguous
  `#`-prefixed lines directly above it, no blank line in between).
  **Rationale**: this is the exact phrase already present in `resolution._open_proposals`'s own
  comment ("Process-local proposal store... Never written to disk") -- the one accepted
  exception in the current codebase. Operationalising the existing precedent's own language
  avoids inventing a new vocabulary this repo would then need to retrofit onto that comment.
  **Alternatives considered**: a broader keyword set (e.g. also accepting "not chronicle-scoped",
  "in-memory only") -- rejected for this feature's first cut; a single, exact, already-proven
  marker is simpler to verify and extend later if a second justified exception with different
  wording is ever added.
