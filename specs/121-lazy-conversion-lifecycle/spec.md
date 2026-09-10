# Feature Specification: Lazy Conversion Lifecycle

**Feature Branch**: `121-lazy-conversion-lifecycle`

**Created**: 2026-09-10

**Status**: Draft

**Input**: User description: "Lazy conversion: stub/drafted/complete lifecycle and provenance (closes #322)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reject an under-specified stub (Priority: P1)

A setting author writes an arc or beat entity with `status: stub` but forgets to give it enough
information to ever be selected during play (no summary, no tags, or no recorded source). The
engine must catch this at validation time, before the entity ever reaches selection, rather than
failing confusingly later when something tries to present a stub with nothing in it.

**Why this priority**: Without this, "stub" stops meaning "selectable but not yet decomposed" and
degrades into "empty placeholder that will crash something downstream." This is the load-bearing
guarantee the whole lazy-conversion approach depends on.

**Independent Test**: Call the validation function directly against a stub entity with each
required field removed in turn (summary, tags, `sources[].path`) and confirm each is rejected with
a specific reason; confirm a stub carrying all three passes.

**Acceptance Scenarios**:

1. **Given** an entity with `status: stub` and no summary text, **When** it is validated,
   **Then** validation fails naming the missing summary.
2. **Given** an entity with `status: stub`, a summary, but no `tags`, **When** it is validated,
   **Then** validation fails naming the missing tags.
3. **Given** an entity with `status: stub`, a summary, and tags, but no `sources` entry carrying a
   `path`, **When** it is validated, **Then** validation fails naming the missing source path.
4. **Given** an entity with `status: stub` carrying a summary, tags, and a `sources` entry with a
   `path`, **When** it is validated, **Then** validation passes.

---

### User Story 2 - Reject a malformed or illegal source record (Priority: P1)

A setting repository (or a human) has performed a conversion and hands the engine a `sources`
entry to validate. The entry must carry the fields provenance depends on — which book it came
from, under what licence, and (once it has actually been used to write text, not merely to
identify a stub's origin) which pages. A `sources` entry with an unrecognised field, or missing a
field its own status level requires, is rejected rather than silently accepted with a gap in its
provenance.

**Why this priority**: Provenance is the whole point of recording `sources` at all — "so a
low-quality extraction can be found and redone." An unchecked `sources` schema means that
guarantee only holds by convention, not by construction.

**Independent Test**: Call the source-schema validation function against entries with each
required field missing, an unexpected extra field, and a fully valid entry, independent of the
entity's overall status.

**Acceptance Scenarios**:

1. **Given** a `sources` entry missing `work`, `licence`, or `path`, **When** it is validated,
   **Then** validation fails naming the missing field.
2. **Given** a `sources` entry on a `status: drafted` or `status: complete` entity that has no
   `pages`, **When** it is validated, **Then** validation fails naming the missing `pages`.
3. **Given** a `sources` entry with a field outside `{work, pages, licence, path}`, **When** it is
   validated, **Then** validation fails naming the unexpected field.
4. **Given** a `sources` entry with `work`, `licence`, and `path` (and `pages` where required),
   **When** it is validated, **Then** validation passes.

---

### User Story 3 - Reject an illegal status transition (Priority: P1)

Something in the pipeline — a setting repository's conversion tooling, or a human editing a file
by hand — proposes moving an entity from one lifecycle status to another. The engine must accept
only the two forward moves the design allows (`stub` → `drafted`, `drafted` → `complete`) and
reject everything else: staying in place is not a transition to check here, skipping straight from
`stub` to `complete`, or moving backward in either step.

**Why this priority**: This is the other half of the lifecycle's integrity — without it, nothing
stops a broken conversion run from silently corrupting an entity's declared maturity, which is
exactly the kind of drift this repository's tooling exists to catch mechanically rather than by
review.

**Independent Test**: Call the transition-check function with every pair of statuses (nine total,
including identical pairs) and confirm exactly the two legal forward pairs are accepted.

**Acceptance Scenarios**:

1. **Given** a proposed transition from `stub` to `drafted`, **When** it is checked, **Then** it
   is accepted.
2. **Given** a proposed transition from `drafted` to `complete`, **When** it is checked, **Then**
   it is accepted.
3. **Given** a proposed transition from `stub` to `complete`, **When** it is checked, **Then** it
   is rejected as skipping a state.
4. **Given** a proposed transition from `complete` to `stub`, or `drafted` to `stub`, or
   `complete` to `drafted`, **When** it is checked, **Then** it is rejected as moving backward.

---

### User Story 4 - Report the stub/drafted/complete mix (Priority: P2)

Someone running `wyrd doctor`-style reporting over a setting wants to know, at a glance, how much
of the setting is still stubs versus how much has actually been played through to completion — the
health-of-the-corpus number the design document's status table describes.

**Why this priority**: Useful and explicitly asked for by the design document, but the setting
functions correctly without it — this is a reporting convenience, not a correctness guarantee.

**Independent Test**: Call the ratio helper over a hand-built set of entities with a known mix of
statuses and confirm the counts and proportions it returns match by hand-calculation.

**Acceptance Scenarios**:

1. **Given** a set of entities with a mix of `stub`, `drafted`, and `complete` statuses, **When**
   the ratio helper is called, **Then** it returns the count of each status and each status's
   proportion of the total.
2. **Given** an empty set of entities, **When** the ratio helper is called, **Then** it returns
   zero counts and does not raise (no division-by-zero on an empty setting).

### Edge Cases

- An entity whose `status` is `drafted` or `complete` is not held to the stub-sufficiency rule
  (summary/tags/source path) — that rule exists to protect stub *selectability* specifically, not
  as a blanket completeness check that would duplicate `entity.validate()`'s existing common-field
  checks.
- A `sources` list may hold more than one entry (an entity assembled from several source
  passages); every entry is checked independently against the same schema.
- Checking a transition never mutates the entity itself — it is a pure predicate over a `(from,
  to)` pair, leaving the caller to decide what to do with the answer (this repo's engine modules
  take setting-supplied data as arguments and never own persistence).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a function that checks whether a `status: stub` entity
  carries a non-empty summary, non-empty `tags`, and at least one `sources` entry with a
  non-empty `path`, returning which requirement (if any) is unmet.
- **FR-002**: The engine MUST NOT apply the stub-sufficiency check of FR-001 to entities whose
  `status` is `drafted` or `complete`.
- **FR-003**: The engine MUST provide a function that checks a single `sources` entry against a
  closed field schema of `{work, pages, licence, path}`, rejecting any entry missing `work`,
  `licence`, or `path`, or carrying a field outside that set.
- **FR-004**: The engine MUST require a `sources` entry's `pages` field to be present when the
  owning entity's `status` is `drafted` or `complete`, and MUST NOT require it when `status` is
  `stub`.
- **FR-005**: The engine MUST provide a function that checks whether a proposed `(from_status,
  to_status)` pair is a legal transition, accepting only `stub` → `drafted` and `drafted` →
  `complete`, and rejecting every other pair (including a status paired with itself, skipping a
  state, and any backward move) with a reason distinguishing "skips a state" from "moves
  backward."
- **FR-006**: The engine MUST provide a pure function that, given a set of loaded entities, returns
  the count of entities at each of the three statuses and each status's proportion of the total,
  without reading from or writing to any file itself.
- **FR-007**: The stub-ratio function of FR-006 MUST return well-defined zero counts and
  proportions (not raise, not divide by zero) when given an empty entity set.
- **FR-008**: None of the functions in FR-001, FR-003, FR-005, or FR-006 MUST fetch, read, or
  otherwise access source text itself — each operates only on the frontmatter fields (and status
  values) already loaded into memory by the caller.

### Key Entities

- **Stub-sufficiency check**: a pure function taking one entity's frontmatter and body text,
  returning whether it carries enough (a non-empty summary body, tags, a sourced path) to be
  legitimately selectable while still a stub.
- **Source record**: one entry of an entity's `sources` list — `{work, pages, licence, path}` —
  recording provenance for a converted (or converting) piece of content; `pages` is required once
  the entity has moved past `stub`.
- **Status transition check**: a pure function taking a `(from, to)` pair of the three lifecycle
  statuses, returning whether that move is legal and, if not, why.
- **Stub ratio report**: a pure function taking a set of loaded entities, returning per-status
  counts and proportions for `doctor`-style reporting to consume.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every one of the acceptance scenarios above passes as an automated test.
- **SC-002**: A setting repository's conversion tooling can determine, from this engine's output
  alone and without inspecting engine internals, exactly which field is missing when a stub or a
  source record fails validation.
- **SC-003**: An attempt to skip a lifecycle state or move backward through it is rejected 100% of
  the time, with no code path that allows it to pass silently.
- **SC-004**: The stub-ratio report over a setting's full entity set completes as a single
  in-memory pass with no file or network access, so it can run inside `doctor`-style reporting on
  every invocation without added I/O cost.

## Assumptions

- This feature extends `engine/wyrd/entity.py`'s existing `STATUSES` tuple and `validate()`
  function rather than introducing a parallel module; the new checks are additional functions,
  not replacements.
- "Enough to be selected and nothing more" is interpreted per the design document as exactly:
  summary, tags, and a sourced path — no additional stub-sufficiency fields are invented here.
- Performing the actual conversion (pulling source text, running any decomposition), and matching
  an entity's entry/exit conditions, are both out of scope, per the parent issue and per
  CLAUDE.md's prohibition on source-fetching tooling in this repository.
- Wiring a `wyrd doctor` CLI command is out of scope if one does not yet exist; FR-006's function
  returns the computed structure only, for a future command to consume.
- A "transition" is checked as a `(from, to)` pair supplied by the caller; this feature does not
  itself track an entity's status history or detect a transition by diffing two file states.
