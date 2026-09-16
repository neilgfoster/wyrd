# Feature Specification: Commit-Back Path for Accepted Generated Content

**Feature Branch**: `164-commit-back-path-for-generated-content`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Commit-back path for accepted generated content" (issue #422)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accepting a generated result commits it as ordinary content (Priority: P1)

A GM (or the engine acting on the GM's behalf) has a `GenerationResult` (#420) that has passed
the anti-inflation checks (#421). Accepting it writes a new `arc`/`beat` entity to disk, at
`status: drafted`, and consumes/emits whatever threads and threat state the candidate declared —
using the exact same mutation functions authored content already goes through.

**Why this priority**: without this, generation produces content nothing can ever play — #420
and #421 are pure validation with no persistence path at all.

**Independent Test**: build a `GenerationResult` whose checks all report `pass`, call the accept
function, and confirm an entity file exists on disk at `status: drafted` with the expected
`sources.generated` provenance, and that the supplied thread/threat state was mutated via
`thread.py`/`threat.py`'s own functions (not reimplemented).

**Acceptance Scenarios**:

1. **Given** a `GenerationResult` whose `checks` all report `pass`, **When** it is accepted,
   **Then** a new entity file is written with `status: drafted` and a `sources` entry of
   `{generated: true, mode: <the request's mode>, consumed: [<the request's thread/threat ids>]}`.
2. **Given** an accepted result whose candidate declares new threads to emit, **When** it is
   accepted, **Then** `thread.new_thread` is called to create them (or `thread.touch` for an
   existing thread the candidate re-raises), never a bespoke equivalent.
3. **Given** an accepted result whose candidate declares a new threat to introduce, **When** it is
   accepted, **Then** `threat.promote` attaches it to the named entity, exactly as an authored
   threat is introduced.

---

### User Story 2 - Declining or rejecting a result writes nothing (Priority: P1)

A `GenerationResult` that the caller declines, or whose `checks` list carries any `reject`
outcome, must leave no trace: no entity file, no thread mutation, no threat mutation.

**Why this priority**: generation must be side-effect-free until acceptance (FR-015 of the
parent spec) — an engine that ever writes a rejected candidate would let inflated content leak
in through an unaccepted branch.

**Independent Test**: build a `GenerationResult` carrying a `reject` outcome (or call the decline
path directly on a passing one), attempt to commit it, and assert the call reports rejection
without touching the filesystem or any thread/threat state passed in.

**Acceptance Scenarios**:

1. **Given** a `GenerationResult` whose `checks` list contains at least one `reject` entry,
   **When** a caller attempts to accept it, **Then** the call reports rejection and no entity
   file is created.
2. **Given** a `GenerationResult` that would otherwise pass, **When** the caller declines it
   instead of accepting, **Then** no entity file is created and no thread/threat state changes.

---

### User Story 3 - A committed generated entity plays exactly like an authored one (Priority: P2)

Once accepted and written, a generated `arc`/`beat` entity has no marker anywhere except its
`sources` provenance distinguishing it from a converted (authored) entity — it moves through the
ordinary `stub → drafted → complete` lifecycle the same way, and once played to `complete` it is
never regenerated, retconned, or silently rewritten.

**Why this priority**: this is what makes "generated" a provenance fact rather than a second class
of content the rest of the engine has to special-case.

**Independent Test**: run `entity.validate` against a committed generated entity's frontmatter and
confirm it passes the same common-schema validation as an authored entity, with no field present
that an authored entity would not also carry (other than the `sources.generated` shape itself).

**Acceptance Scenarios**:

1. **Given** a committed generated `beat` entity, **When** its frontmatter is validated with
   `entity.validate`, **Then** it passes exactly as an authored entity's frontmatter would.
2. **Given** a generated entity already at `status: complete`, **When** a later generation pass
   covering the same ground is accepted, **Then** nothing about the existing entity's file is
   ever mutated by this feature's commit path — a later pass can only produce a new entity, never
   alter one already played.

### Edge Cases

- Accepting a `GenerationResult` whose `checks` list is empty (never run) is treated the same as
  one carrying a `reject` — acceptance requires evidence the checks ran and passed, not merely the
  absence of a recorded rejection.
- A candidate declaring no thread/threat changes at all (a self-contained beat) is accepted
  normally, writing only the entity file — the thread/threat mutation calls are a function of what
  the candidate actually declares, never mandatory busywork.
- Two results are never merged: accepting a second result while an earlier one covering the same
  thread state is still `drafted` produces a second, independent entity — this feature does not
  detect or prevent overlapping generation, since selection between them is a game-mastering
  decision made before acceptance, not this feature's concern.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a function that, given an accepted `GenerationResult`
  (#420) and the target `arc`/`beat` shape it describes, writes it to disk as an ordinary entity
  file at `status: drafted`, using the existing entity schema and I/O
  (`entity.py`/`state.py`) — matching parent spec FR-012.
- **FR-002**: The written entity's `sources` field MUST include an entry of the shape
  `{generated: true, mode: live-play|setting-authoring, consumed: [<thread/threat ids the request
  supplied>]}`, additive to (never replacing or narrowing) the existing `{work, pages, licence,
  path}` shape `entity.validate_source` already accepts — matching parent spec FR-012.
- **FR-003**: Accepting a result MUST consume and emit thread state through `thread.py`'s own
  `new_thread`/`touch` functions, and threat state (a new threat, or a clue/imminence change to
  an existing one) through `threat.py`'s own `promote`/`check_activation`/`resolve_effects`
  functions — never a parallel implementation of the same behaviour — matching parent spec FR-013.
- **FR-004**: No new persistence file, table, or frontmatter field may be introduced solely to
  hold "generated" thread or threat state separately from the fields authored content already
  uses — matching parent spec FR-013.
- **FR-005**: The system MUST provide a matching decline/reject path: given a `GenerationResult`
  that the caller declines, or whose `checks` list contains any `reject` outcome, the function
  MUST write no entity file and MUST NOT call any thread/threat mutation function — matching
  parent spec FR-015.
- **FR-006**: A `GenerationResult` whose `checks` list is empty MUST be treated as not yet
  evaluated, and MUST be rejected by the accept path on the same footing as an explicit `reject`
  outcome (Edge Cases).
- **FR-007**: This feature MUST NOT add any regeneration, retcon, or rewrite path for an entity
  once committed — an entity produced by this feature's accept path is, from that point on,
  subject to `18-arcs-and-beats.md`'s ordinary lifecycle and `29-evolution.md`'s "the past is a
  fact" rule identically to an authored entity — matching parent spec FR-014.

### Key Entities *(include if feature involves data)*

- **Committed arc/beat**: an ordinary `arc`/`beat` entity (`25-entities.md`), written at
  `status: drafted`, distinguished from an authored entity only by its `sources.generated`
  provenance shape. No new entity type.
- **Accept/reject outcome**: a transient function-return value describing whether a
  `GenerationResult` was written or declined, and why — never itself persisted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of accepted `GenerationResult`s are written using the existing entity file
  format and pass `entity.validate` identically to an authored entity.
- **SC-002**: 100% of declined or rejected `GenerationResult`s result in zero filesystem writes
  and zero thread/threat state mutation, verified by an automated test that asserts this directly
  rather than by inspecting a return value alone.
- **SC-003**: The accept path introduces exactly one new field shape (`sources.generated`) to the
  existing entity schema, and zero new files, tables, or parallel state structures for
  thread/threat data — verifiable by diffing the touched schema against `18-arcs-and-beats.md`/
  `19-campaign.md`'s existing shapes.
- **SC-004**: Every thread or threat mutation an accepted result causes is traceable to a call of
  an existing `thread.py`/`threat.py` function, verified by a test asserting the accept path
  invokes that identical function rather than equivalent inline logic.

## Assumptions

- This feature covers commit-back only (parent spec FR-012–FR-015); assembling the actual
  candidate content (FR-016–FR-020) is the dependent sibling feature (the generation pipeline)
  and is out of scope here.
- The accept function receives the target entity's id, type, and parent placement as ordinary
  caller-supplied arguments (matching every other `engine/wyrd/*` module's pure-function
  contract) — this feature does not decide *where* a generated beat is filed, only how it is
  written once that decision is made.
- "The same functions authored play already uses" means `thread.py`'s `new_thread`/`touch` and
  `threat.py`'s `promote`/`check_activation`/`resolve_effects` directly — there is no existing
  higher-level "apply an exit block" orchestrator elsewhere in the engine for this feature to
  reuse instead; this feature is not expected to add one, only to call the primitives directly
  the same way any future orchestrator would.
- `known_entities`/setting-membership concerns are #421's job (already run before a result reaches
  this feature) and are not re-validated here.
