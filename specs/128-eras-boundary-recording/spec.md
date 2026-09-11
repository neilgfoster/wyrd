# Feature Specification: Eras: named periods and boundary recording

**Feature Branch**: `128-eras-boundary-recording`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Eras: named periods and boundary recording" (issue #336)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The GM reads the current era's ambient register (Priority: P1)

Every beat, the GM needs the chronicle's current ambient register — the context that colours
narration until the world's condition changes again. `chronicle.yaml` already carries a scalar
`era` field (docs/design/22-state.md); this feature gives it something to point at and a way to
look up what it means.

**Why this priority**: without a lookup, naming an era is decorative — nothing in the engine can
actually answer "what's the register right now".

**Independent Test**: given a chronicle's declared `eras` list and its current `era` pointer,
confirm the ambient register returned matches the pointed-to era's own declared register.

**Acceptance Scenarios**:

1. **Given** an `eras` list containing an era with a declared ambient register, and `era` pointing
   at that era's id, **When** the current ambient register is looked up, **Then** it returns
   exactly that era's register.
2. **Given** `era` is `null` (no era has ever been crossed into), **When** the current ambient
   register is looked up, **Then** it returns `None` rather than erroring.

---

### User Story 2 - Crossing an era boundary is recorded, not inferred (Priority: P1)

An arc ends with a real change to the world, and the GM decides that's where an era boundary is
drawn (docs/design/19-campaign.md). The crossing itself becomes a recorded fact — what era ended,
what era began, and when — the same way `migrations` records an engine/setting version change:
append-only, never edited or reordered.

**Why this priority**: without an explicit record, "the chronicle's history is navigable years
later" (the design's own stated purpose for eras) has nothing to navigate — a bare pointer update
loses exactly what a reader coming back after years would want to see.

**Independent Test**: given a chronicle at one era, cross into a different declared era, and
confirm both the `era` pointer moves and a crossing record is appended naming the from/to eras
and when it happened.

**Acceptance Scenarios**:

1. **Given** an `eras` list declaring two eras and `era` pointing at the first, **When** a
   crossing to the second is recorded, **Then** the returned `era` pointer is the second era's id,
   and a crossing entry naming `{from: <first>, to: <second>, at: <given date>}` is present.
2. **Given** `era` is `null` (the chronicle's first era), **When** a crossing into a declared era
   is recorded, **Then** the crossing entry's `from` is `null` and `era` becomes that era's id.
3. **Given** a target era id that is not present in the chronicle's declared `eras` list, **When**
   a crossing to it is attempted, **Then** the attempt is rejected — an era must be named in
   advance (docs/design/19-campaign.md) before a chronicle can cross into it.
4. **Given** the target era id is the same as the current `era`, **When** a crossing is
   attempted, **Then** the attempt is rejected — crossing into the era already current is not a
   boundary.

### Edge Cases

- A chronicle with an empty `eras` list rejects every crossing attempt (nothing has been named
  in advance yet) but still answers the ambient-register lookup with `None` rather than erroring.
- The direction, theme, or number of eras is never validated beyond "declared in advance" — per
  the design document, that is setting business, not the engine's (spec.md's Assumptions carries
  this forward explicitly).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a way to look up the ambient register of the era named by a
  chronicle's current `era` pointer against its declared `eras` list.
- **FR-002**: The ambient-register lookup MUST return `None` (not an error) when `era` is `null`
  or when the declared `eras` list is empty.
- **FR-003**: The engine MUST provide a way to record a crossing from the chronicle's current
  `era` to a different, already-declared era, returning both the new `era` pointer and an
  explicit crossing record `{from, to, at}`.
- **FR-004**: A crossing to an era id not present in the chronicle's declared `eras` list MUST be
  rejected.
- **FR-005**: A crossing whose target equals the chronicle's current `era` MUST be rejected —
  every recorded crossing is a real boundary.
- **FR-006**: `chronicle.yaml`'s crossing-record log MUST be append-only — this feature adds
  crossing records to it, never edits or reorders an existing entry, mirroring the existing
  `migrations` log's own convention (`state.py`).

### Key Entities

- **`eras`** (new, on `chronicle.yaml`): a list declared in advance, each entry
  `{id, name, ambient}` — the chronicle-level "named in advance" list docs/design/19-campaign.md
  requires. Direction/theme is never engine-validated.
- **`era`** (existing, `chronicle.yaml`, currently a bare `null`-defaulting scalar per
  docs/design/22-state.md): this feature is what gives it real semantics — it names the current
  entry's `id` in `eras`, or `null` before any crossing has happened.
- **`era_crossings`** (new, on `chronicle.yaml`): an append-only list of `{from, to, at}` records,
  mirroring `migrations`'s existing append-only convention (`state.py`) — never edited, never
  reordered.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The ambient-register lookup returns the correct register for a chronicle at any
  declared era, and `None` for a chronicle with no era yet — verified by exact-input tests.
- **SC-002**: Every successful crossing produces exactly one new, correctly-shaped
  `{from, to, at}` record, and moves `era` to the target — verified by exact-input tests.
- **SC-003**: Both rejection cases (undeclared target, no-op target) are covered by explicit
  tests and never silently succeed.

## Assumptions

- This feature is a runtime-logic slice only: plain dicts/lists in, plain dicts out, no
  file I/O — matching `chronicle.py`'s (#328) existing convention of owning one sub-field's
  semantics as pure functions, with a caller responsible for persisting the result via
  `state.py`'s existing `save_chronicle`.
- `eras`/`era_crossings` are new optional fields added to `state.py`'s
  `default_chronicle_state`/`validate_chronicle` (defaulting to `[]`, filled in the same way
  `migrations`/`intent` already are) — this feature extends that schema exactly the way #328
  extended `pending`'s semantics on top of #325's schema, rather than introducing a second state
  file.
- "Top-level arcs end with a recorded world change, and an era boundary is drawn around such
  changes" (docs/design/19-campaign.md) is a GM judgment call about *when* to cross, not
  something this feature automates — this feature provides the recording primitive; deciding to
  call it is out of scope, the same separation `journey.py`/`threat.py` already keep between
  mechanical resolution and GM narration.
- Git-tagging an era boundary (docs/design/19-campaign.md: "it is git-tagged, giving a decade of
  play navigable checkpoints") is a repository-operations concern, not `chronicle.yaml` state —
  out of scope here.
