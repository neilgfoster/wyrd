# Feature Specification: The dangling-mechanic check

**Feature Branch**: `028-dangling-mechanic-check`

**Created**: 2026-08-26

**Status**: Draft

**Input**: GitHub issue #59, "The dangling-mechanic check" — Stage 13 of the design programme (#1).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A script catches a mechanic named before it is defined (Priority: P1)

A contributor edits a design document and references a mechanic by name — in prose, in a
table, in a cross-reference — that no document actually defines. Today nothing catches this
until a reader notices, and prose review has already missed six such cases. Running the check
must fail with a specific list of the undefined mechanics and where they were referenced.

**Why this priority**: This is the entire purpose of the feature — the check exists to close
this fault class. Without it, the check delivers nothing.

**Independent Test**: Plant a reference to a mechanic that no document defines anywhere in
`design/`, run the check, and confirm it fails and names the planted reference.

**Acceptance Scenarios**:

1. **Given** a design document that references a mechanic by name, **When** no document
   contains a definition for that mechanic, **Then** the check exits non-zero and reports the
   mechanic name and the referencing document.
2. **Given** the design as it stands once the design programme (#1) has completed all its
   stages, **When** the check is run, **Then** it exits zero — every mechanic referenced
   anywhere in `design/` is defined somewhere in `design/`.

---

### User Story 2 - The check is proven against the six known historical faults (Priority: P1)

The programme's own history lists six mechanics that were referenced before they were
defined: engine characteristics in the conversion contract, Standing in Upkeep,
`party_effective` in the danger formula, the damage-type critical tables, the skill list, and
the wound schema. A check that cannot re-detect these, reconstructed as fixtures, is not
trustworthy — it might pass today only because nothing in the current design happens to
trigger it.

**Why this priority**: Ties for top priority with User Story 1 — the issue's own acceptance
criteria require the check to fail on each of the six historical instances, and that is the
proof the check's detection logic is real rather than accidental.

**Independent Test**: For each of the six historical instances, construct a minimal fixture
reproducing the dangling reference as it originally existed, run the check against it, and
confirm each one fails independently.

**Acceptance Scenarios**:

1. **Given** a fixture reproducing each of the six historical dangling-reference instances in
   turn, **When** the check runs against that fixture, **Then** it fails and names that
   instance's mechanic.
2. **Given** the check's own test suite, **When** it is inspected, **Then** each test exercises
   the check's actual detection logic against a fixture (not a hand-maintained reimplementation
   of what the check is supposed to compute).

---

### User Story 3 - A contributor runs the check on demand and understands the result (Priority: P2)

A contributor working on a design document wants to confirm before opening a PR that they
have not left a mechanic referenced-but-undefined. They run the check locally and get a
result they can act on without needing to already know the check's internals.

**Why this priority**: Secondary to detection itself — the check is only useful if a
contributor can and does run it, and if a failure tells them exactly what to fix.

**Independent Test**: Run the check against the current, clean state of `design/` and confirm
it passes with a clear summary; then plant one dangling reference and confirm the failure
output names it specifically enough to locate and fix without further investigation.

**Acceptance Scenarios**:

1. **Given** a clean design tree, **When** the check runs, **Then** it reports success and how
   many mechanics it verified.
2. **Given** a design tree with one planted dangling reference, **When** the check runs,
   **Then** the failure output names the undefined mechanic and the file/location referencing
   it, without requiring the contributor to read the check's source to interpret the result.

### Edge Cases

- A mechanic name appears only inside a fenced code block or inline code span (e.g. an
  example schema) — is that a reference that must resolve, or exempt as illustrative text?
- A mechanic is defined in one document and referenced by a different, non-obvious spelling
  or capitalization elsewhere — does the check require exact-name matching, or is near-miss
  drift (a defined term renamed in one place and not another) also its concern?
- A mechanic name appears in `specs/` (a record of a past change) rather than `design/` (the
  present description) — specs/ is exempt from `check_docs.py`'s reachability requirement for
  the same reason; this check needs an explicit ruling on whether specs/ references are in or
  out of scope, since a spec describing already-superseded design would otherwise generate
  permanent false failures.
- A single word incidentally matches a mechanic's name without being a reference to the
  mechanic at all (e.g. ordinary English use of a word that also happens to be a defined
  term) — the check must not flag plain prose as a dangling reference.
- A document defines a mechanic by table row or glossary entry rather than a heading — the
  check's definition of "definition" must cover more than headings alone, or it will produce
  false failures on the repo's own existing patterns.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The check MUST scan every document under `design/` for both mechanic
  **definitions** (a heading, a table row, or a glossary entry that establishes what a named
  mechanic is) and mechanic **references** (a use of that name elsewhere that assumes the
  reader already knows what it means).
- **FR-002**: The check MUST fail (non-zero exit) when it finds a reference to a mechanic name
  for which no definition exists anywhere under `design/`.
- **FR-003**: The check's failure output MUST name the specific undefined mechanic and the
  file (and, where practical, the line or section) where the dangling reference was found, so
  a contributor can act on it without reading the check's source.
- **FR-004**: The check MUST be implemented as stdlib-only Python in `tools/`, following the
  existing pattern of `tools/backlog.py` and `tools/check_docs.py` (docs/design/27-tooling.md
  section 2: no third-party dependencies, no daemon, auditable top to bottom).
- **FR-005**: The check's own test suite MUST include a fixture-based reproduction of each of
  the six historical dangling-mechanic instances named in issue #59 (engine characteristics in
  the conversion contract, Standing in Upkeep, `party_effective` in the danger formula, the
  damage-type critical tables, the skill list, and the wound schema), and each MUST fail
  independently when run against its fixture.
- **FR-006**: The check's tests MUST exercise the check's actual scanning/matching logic
  against fixture documents, not a parallel reimplementation of that logic that could drift
  from what the check itself does.
- **FR-007**: The check MUST pass (zero exit) when run against the design tree as it stands
  once every stage of the design programme (#1) that precedes this one has landed.
- **FR-008**: The check MUST be runnable on demand via a direct command
  (`python3 tools/check_dangling_mechanics.py`), matching the invocation pattern of
  `tools/backlog.py check` and `tools/check_docs.py`.
- **FR-009**: The check MUST support a machine-readable output mode (`--format json`),
  matching the existing convention in `tools/backlog.py` and `tools/check_docs.py`, so it can
  be composed into other tooling later without a redesign.
- **FR-010**: The check MUST NOT flag a mechanic name that appears only inside a fenced code
  block, inline code span, or as an ordinary English word coincidentally matching a defined
  term, as a dangling reference — see the Assumptions section for how "reference" is scoped to
  avoid this.
- **FR-011**: The check MUST treat `specs/` as exempt from the reference-must-resolve
  requirement, consistent with `check_docs.py`'s existing treatment of `specs/` as a record of
  past change rather than current design (see Assumptions).

### Key Entities

- **Mechanic definition**: A place in `design/` that establishes what a named mechanic is —
  operationalized as a Markdown heading naming the mechanic, a table row whose first column
  names it, or a glossary-style entry (a bolded or defined term followed by its explanation).
- **Mechanic reference**: A use of a mechanic's name in prose or a table outside its own
  definition, that assumes the reader already knows what the term means.
- **Dangling reference**: A mechanic reference for which the check finds no matching
  definition anywhere under `design/`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The check fails on every one of the six historical dangling-mechanic instances,
  reconstructed as fixtures, with zero false negatives among them.
- **SC-002**: The check passes when run against the design tree at the end of the design
  programme, with zero false positives against the repo's own existing, intentional
  definitions (headings, table rows, glossary entries).
- **SC-003**: A contributor can identify and locate a planted dangling reference from the
  check's failure output alone, without reading the check's source code.
- **SC-004**: Every test in the check's suite exercises the check itself; none reimplements
  the check's detection logic independently.

## Assumptions

- **Definition forms**: a definition is a Markdown heading naming the mechanic, a table row
  whose leading column names it, or a glossary-style bolded-term-plus-explanation entry. This
  matches the existing shapes already used across `design/` (e.g. the skill list is a table,
  the wound schema is headed sections) rather than requiring the design docs to be restructured
  to fit the checker.
- **Reference scope**: only prose and table content outside fenced code blocks / inline code
  spans counts as a reference that must resolve. Code/schema examples are illustrative, not
  claims that a mechanic is defined elsewhere, and are exempt — mirroring `check_docs.py`'s own
  `INLINE_CODE`/`FENCE` handling for its wikilink-policy check.
- **`specs/` is out of scope for reference resolution**, same as `check_docs.py`'s existing
  reachability exemption: a spec is the record of one past change, not the present description,
  and may legitimately reference a mechanic under a since-superseded name.
- **Vocabulary is a closed, explicit list**, not free-text NLP matching: the check operates
  over a known set of mechanic names (harvested from the definitions it finds, per FR-001) —
  it does not attempt fuzzy matching to catch a renamed-in-one-place-only mechanic; that drift
  is out of scope for this feature and belongs to the cross-document-contradiction fault
  (class 3), which the issue names as a `Consider` (optional extension), not a requirement.
- **Runs on demand, not in CI, for this iteration**: `check_docs.py` is currently the only
  precedent and this issue does not mandate CI wiring. Whether to add it to CI is decided and
  recorded (per the issue's own scope item) at implementation time, following the same
  reasoning `check_docs.py` used, rather than specified here as a functional requirement.
- **This feature only checks `design/`**, not `README.md` prose in isolation, since
  `README.md` does not itself define mechanics — it is checked by `check_docs.py` for
  reachability already.
