# Phase 0 Research: The dangling-mechanic check

No NEEDS CLARIFICATION markers remain in the Technical Context — this feature's shape is fully
determined by existing repo precedent. Decisions below record why, matching that precedent
rather than inventing a new pattern.

## Decision: reuse `check_docs.py`'s script shape exactly

**Decision**: `tools/check_dangling_mechanics.py` exposes `find_problems(root: Path) ->
list[Problem]` as its core entry point, a `Problem(str)` subclass for results, and an
`argparse` CLI supporting `--format json` alongside the default human-readable summary.

**Rationale**: `tools/check_docs.py` already solved "scan `design/**.md`, report structured
problems, support both a human and a machine-readable mode" for a sibling fault class (broken
links/reachability). Reusing its shape means a contributor who already knows one check knows
the other, and it satisfies FR-004/FR-008/FR-009 directly.

**Alternatives considered**: A bespoke CLI shape (e.g. positional args, custom output format)
was rejected — it would add a second convention to learn for no benefit, and CLAUDE.md's fault
class 3 ("two documents/tools describing one thing differently") applies to tooling
conventions too.

## Decision: definitions and references are detected structurally, not semantically

**Decision**: A "definition" is recognized by Markdown structure — an ATX heading whose text
names the mechanic, a table row whose leading cell names it, or a bolded term at the start of a
paragraph followed by an explanation (the glossary-entry shape). A "reference" is any other
occurrence of that exact name in prose or table cells, excluding fenced code blocks and inline
code spans.

**Rationale**: `check_docs.py`'s own `ADR_PROSE_REF`, `WIKILINK`, `FENCE`, `INLINE_CODE`
patterns already establish the repo's convention for "detect a structural marker with a
regex/parse pass over Markdown, skip fenced/inline code" — reused directly rather than
building an NLP-based semantic matcher, which industry-standard practice for this kind of
lint (e.g. broken-link checkers, doc linters) also avoids: false positives from semantic
guessing are worse than a stricter structural rule with documented escape hatches.

**Alternatives considered**: Semantic/NLP matching (e.g. embedding similarity to catch a
renamed term) was rejected as out of scope per the spec's Assumptions — that is the
cross-document-contradiction fault (class 3), a `Consider` extension in issue #59, not this
feature's Definition of Done.

## Decision: the vocabulary is derived from the design tree itself, not hand-maintained

**Decision**: The check's first pass builds its own list of known mechanic names by scanning
for definitions (headings/table-rows/glossary-entries) across `design/`; the second pass checks
every detected reference against that derived list. No separate maintained list of "mechanic
names" lives anywhere.

**Rationale**: A hand-maintained vocabulary list would itself go stale — exactly the fault
class this feature exists to prevent (CLAUDE.md: "stale but plausible specifications"). Deriving
it from the documents each run keeps the check self-updating as the design grows, matching
`check_docs.py`'s own derive-don't-duplicate approach to reachability.

**Alternatives considered**: A static YAML/JSON registry of mechanic names, updated by hand
alongside `design/` changes, was rejected — it duplicates information already present in the
documents and would drift the moment someone forgot to update it.

## Decision: tests use per-test temporary trees, no on-disk fixture files

**Decision**: `tools/test_check_dangling_mechanics.py` follows `tools/test_check_docs.py`'s
`TreeCase` pattern exactly — a fresh `tempfile.TemporaryDirectory()` per test, files written
inline in the test body via a small `write(rel, text)` helper, and assertions against
`find_problems()`'s real return value.

**Rationale**: `test_check_docs.py`'s own module docstring states the reasoning directly: "a
guard whose tests reimplement it cannot fail when it is wrong — a fault already fixed twice in
this repo." Building six fixtures for the historical instances (FR-005) as literal file
contents, one per test, both documents each historical fault in a readable, reviewable way and
satisfies FR-006 (exercising the real detection logic, not a parallel model of it).

**Alternatives considered**: A `tools/fixtures/` directory of static Markdown files (the
pattern `tools/fixtures/board.json` uses for `backlog.py`) was considered, but rejected for
this check specifically — a fixture *tree* (multiple files, cross-references between them) is
more naturally expressed inline per test than as a directory-of-directories under
`tools/fixtures/`, and `test_check_docs.py` already established the temp-tree convention for
exactly this shape of check (multi-document, cross-referencing).
