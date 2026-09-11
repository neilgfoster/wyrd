# Feature Specification: Check: no implicit current-chronicle global state

**Feature Branch**: `139-check-no-implicit-chronicle`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Check: no implicit current-chronicle global state" (issue #365)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A future module-level global is caught before it ships (Priority: P1)

`docs/design/21-parallel-chronicles.md` states as a GM-contract MUST: "there is no 'current
chronicle' global, so the wrong one cannot be edited by accident." Every module in
`engine/wyrd/` already follows this by convention — a deterministic check turns the convention
into an enforced invariant, catching a future module that introduces an unjustified
chronicle-scoped global before it ships, the same way `check_dangling_mechanics.py` catches an
undefined mechanic reference.

**Why this priority**: this is the entire content of the feature — without the check, the
invariant is only as durable as everyone remembering to keep following it.

**Independent Test**: run the check against the real repo and confirm it passes clean; run it
against a scratch tree containing a deliberately unjustified module-level mutable global and
confirm it fails, naming the offending module and identifier.

**Acceptance Scenarios**:

1. **Given** the current `engine/wyrd/` tree, **When** the check runs, **Then** it exits `0`,
   reporting what it scanned.
2. **Given** a scratch module containing `_cache: dict = {}` at module level with no
   justifying comment, **When** the check runs against it, **Then** it exits non-zero, naming
   the module and `_cache`.
3. **Given** a scratch module containing a module-level mutable global whose immediately
   preceding comment block contains the word `"process-local"` (the existing precedent's own
   justification language, `resolution._open_proposals`), **When** the check runs, **Then** it
   is treated as justified and does not fail the check.

### Edge Cases

- A module-level assignment to an immutable value (a string, an int, a tuple, a frozenset
  literal with contents, a plain function/class definition) is never flagged — only an *empty*,
  *mutable* container (`{}`, `[]`, `set()`, or the equivalent `dict()`/`list()`/`set()` calls)
  is a candidate, since only an empty mutable container can accumulate state across calls in a
  way a constant value cannot.
- A module-level constant *populated* at definition time (e.g. `_STOP_WORDS = frozenset({...})`,
  already present in `corpus_document.py`) is never flagged — it is read-only reference data,
  not accumulating state, and its content is fixed at import time, matching this check's own
  "mutable and initially empty" scope, not "any module-level name."
- A justifying comment must be a comment (`#`-prefixed line) immediately above the assignment,
  not a docstring elsewhere in the module — matching where `resolution._open_proposals`'s own
  justification actually lives.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The check MUST scan every `.py` file directly under `engine/wyrd/` for
  module-level assignments whose value is an empty, mutable container (`{}`, `[]`, `set()`, or
  an equivalent no-argument `dict()`/`list()`/`set()` call).
- **FR-002**: For each candidate found, the check MUST look for a justifying comment
  (containing the case-insensitive substring `"process-local"`) in the comment lines
  immediately preceding the assignment.
- **FR-003**: A candidate without a justifying comment MUST be reported as a problem, naming
  the file, line, and identifier.
- **FR-004**: The check MUST exit `0` when no unjustified candidate is found, and non-zero
  otherwise, matching `check_dangling_mechanics.py`'s own exit-code convention.
- **FR-005**: The check MUST be runnable on demand (`python3 tools/check_no_implicit_chronicle.py`)
  — this repo has no CI to run it automatically.

### Key Entities

- **Candidate**: a module-level `Assign`/`AnnAssign` node whose value is an empty mutable
  container, found via `ast` parsing (not text/regex matching) for accuracy against a real
  Python grammar.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The check passes clean against this repo's real `engine/wyrd/` tree today
  (verified as part of this feature's own test suite, not just asserted).
- **SC-002**: The check's own test suite exercises both a passing case (justified global) and a
  failing case (unjustified global) in a scratch tree, mirroring
  `test_check_dangling_mechanics.py`'s "no fixtures on disk, build a scratch tree per test"
  convention.

## Assumptions

- This feature is a repo-maintenance tool, not an engine capability — matching
  `tools/check_docs.py`/`tools/check_dangling_mechanics.py`'s own precedent of living in
  `tools/` with its own `specs/` record (e.g. `specs/028-dangling-mechanic-check`), run on
  demand, never wired into a CI this repo doesn't have.
- The check scans `engine/wyrd/*.py` only (top-level files in that directory) — not `tools/`,
  not `specs/`, not any test file — since the invariant this check enforces
  (`docs/design/21-parallel-chronicles.md`'s "no current-chronicle global") is specifically
  about the shipped engine's own modules, the ones a chronicle-loading caller actually imports.
- `"process-local"` (case-insensitive substring match) is the one recognised justification
  marker, chosen because it is the exact phrase `resolution._open_proposals`'s own comment
  already uses — this feature does not invent a new marker vocabulary, it operationalises the
  one already in the codebase.
