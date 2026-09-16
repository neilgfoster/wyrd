# Feature Specification: Chronicle Entity Loader Layout

**Feature Branch**: `170-chronicle-entity-loader-layout`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Fix _load_chronicle_entities to walk type-subdirectories and read .yaml" (GitHub issue #440)

## Clarifications

### Session 2026-09-16

- Q: `overlay/` has no type subdirectories in any real chronicle checked (only
  `overlay/README.md` exists everywhere); `setting/entities/<type>/` and `entities/<type>/`
  both use per-type subdirectories consistently. Should the fix require
  `overlay/<type>/<id>.yaml` (mirroring the other two), or accept `overlay/<id>.yaml` flat (no
  type subdirectory, since an overlay's type is already implied by the setting entity it
  targets)? → A: `overlay/<type>/<id>.yaml` — mirrors `setting/entities/<type>/` and
  `entities/<type>/` exactly, one consistent rule for all three directories.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A proposal is validated against a real chronicle's entities (Priority: P1)

A player (or the GM tooling acting on their behalf) proposes a mutation against a chronicle
entity — e.g. changing a faction's disposition, or a character's condition. Before the mutation
commits, the system checks it against every entity the chronicle currently knows about (so a
proposal cannot invent a duplicate id, or reference an entity that doesn't exist). For that check
to mean anything, the system must actually be able to find and read the chronicle's real entity
files, wherever the chronicle's bootstrap process put them.

**Why this priority**: This is the exact failure reported in #440: on a real, bootstrapped
chronicle the check currently sees zero entities regardless of what's on disk, silently
defeating the validation it exists to perform. Without this working, every other capability that
depends on the chronicle's entity set (session-context assembly, proposal validation) is
unreliable.

**Independent Test**: Point the loader at a chronicle laid out the way a real bootstrap produces
it (entity files nested under a per-type directory, in the setting's storage format) and confirm
it returns the full, non-empty entity set — not `{}`.

**Acceptance Scenarios**:

1. **Given** a chronicle whose `setting/`, `overlay/`, and `entities/` directories each hold
   entity files nested one level down by entity type (e.g.
   `setting/entities/faction/hammond-maninski-agency.yaml`), **When** the chronicle's effective
   entity set is loaded, **Then** every one of those files is found and included in the result.
2. **Given** the same layout, **When** an overlay file changes a setting entity's fields,
   **Then** the effective entity set reflects the setting entity resolved against its overlay —
   exactly as it already does for the layout the loader currently assumes.

---

### User Story 2 - A non-entity file sitting in an entity directory doesn't crash the loader (Priority: P2)

A chronicle's `setting/` directory holds a `README.md` describing the setting, alongside the
real entity files. A freshly-bootstrapped `entities/<type>/` directory may hold a `.gitkeep`
placeholder before any entity has been invented there. Neither of these is an entity, and neither
should stop the loader from reading everything else.

**Why this priority**: This is the second half of the reported failure — once the glob is
widened to actually find real files, it must not start crashing on the incidental files that
share those directories. Lower priority than Story 1 because it's only reachable once Story 1's
fix is in place.

**Independent Test**: Add a `README.md` at a directory's top level and a `.gitkeep` inside a
type subdirectory, alongside real entity files, and confirm the load still succeeds and still
returns exactly the real entities — no crash, no phantom entries.

**Acceptance Scenarios**:

1. **Given** `setting/README.md` exists alongside `setting/entities/<type>/*.yaml` files,
   **When** the chronicle's effective entity set is loaded, **Then** the load succeeds and the
   README is not treated as an entity.
2. **Given** an empty `entities/<type>/` directory containing only a `.gitkeep` file, **When**
   the chronicle's effective entity set is loaded, **Then** the load succeeds and contributes no
   entity from that directory.

---

### User Story 3 - The documented chronicle layout matches what bootstrap actually produces (Priority: P3)

Anyone reading the design documentation to understand where a chronicle's entities live should
find a description that matches what a real chronicle, produced by the current bootstrap
tooling, actually looks like on disk.

**Why this priority**: Valuable for future correctness (this exact class of bug — code and
layout drifting apart silently — is what caused #440), but the engine behaves correctly for
Stories 1 and 2 independent of whether the prose is updated. Lowest priority because it's a
documentation consistency check, not a behavioural fix.

**Independent Test**: Read the design document's description of chronicle entity storage and
confirm it names the per-type subdirectory structure and file format the loader now expects.

**Acceptance Scenarios**:

1. **Given** the confirmed canonical layout (per-type subdirectories, one file format), **When**
   the design documentation describing chronicle state is reviewed, **Then** it names that
   structure explicitly rather than leaving file layout unspecified.

### Edge Cases

- What happens when a chronicle root exists but one of `setting/`, `overlay/`, or `entities/` has
  no type subdirectories at all yet (nothing has been created there)? The load must succeed and
  contribute zero entities from that directory, not error.
- What happens when a type subdirectory contains a file that has the right extension but invalid
  or missing frontmatter? This is an existing failure mode for genuinely malformed entity files
  and is unchanged by this feature — only files that are not entities at all (no frontmatter
  delimiter, wrong extension) gain a defined non-crashing behaviour.
- What happens when both an old-layout flat file and a new-layout nested file exist for the
  chronicle at once? Resolved by FR-004 below (back-compat decision).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST locate entity files nested one level below `setting/`, `overlay/`,
  and `entities/` under a per-entity-type subdirectory — `setting/entities/<type>/<id>.yaml`,
  `overlay/<type>/<id>.yaml`, and `entities/<type>/<id>.yaml` — the same per-type subdirectory
  rule applied uniformly to all three directories, matching the layout a chronicle bootstrap
  actually produces.
- **FR-002**: The system MUST read entity files in the storage format bootstrap actually writes
  them in (YAML), not only the format previously assumed (Markdown with frontmatter).
- **FR-003**: The system MUST NOT fail the load, and MUST NOT count as an entity, a file that
  does not carry a parseable entity — including but not limited to a plain README file at a
  directory's top level or a placeholder file (e.g. `.gitkeep`) inside an otherwise-empty type
  subdirectory.
- **FR-004**: The system MUST continue to accept the previously-supported flat, top-level
  Markdown layout wherever it is still found, for chronicles that predate the nested-YAML
  bootstrap, so that neither layout silently loses entities during the transition.
- **FR-005**: The effective entity set produced by the loader MUST be identical in shape and
  resolution rules (setting entity resolved against its overlay counterpart, invented entities
  layered on top) regardless of which supported on-disk layout produced it.
- **FR-006**: The chronicle-state design documentation MUST describe the entity file layout
  (per-type subdirectory, file format) that the loader actually expects, so the two do not drift
  apart again undetected.

### Key Entities

- **Chronicle root**: The directory containing a chronicle's `setting/`, `overlay/`, and
  `entities/` directories (and `chronicle.yaml`). Already defined by the engine; unchanged by
  this feature.
- **Entity file**: A single file describing one entity's frontmatter (and, for setting/invented
  entities, a body). This feature changes where such files are found and what format they may be
  read in — not what an entity's fields mean.
- **Entity type subdirectory**: The new structural element this feature must recognise — a
  directory named for an entity type (e.g. `faction`, `character`) holding that type's entity
  files, nested one level under `setting/`, `overlay/`, or `entities/`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Loading the effective entity set for a chronicle laid out the way current bootstrap
  tooling produces it returns every entity actually present — zero missing entities, for any
  chronicle exercised by this feature's tests.
- **SC-002**: Loading the effective entity set never fails due to the presence of a non-entity
  file (README, placeholder) in a directory that also holds real entity files.
- **SC-003**: A chronicle in the previously-supported flat layout continues to load exactly as it
  did before this feature — no regression for existing chronicles.
- **SC-004**: A cold reader of the chronicle-state design documentation can state, without
  reading the loader's source, what directory structure and file format a chronicle's entities
  are stored in.

## Assumptions

- The canonical nested layout is `setting/entities/<type>/<id>.yaml`,
  `overlay/<type>/<id>.yaml`, and `entities/<type>/<id>.yaml` — confirmed against the
  wyrd-chronicle-darkfuture-rookie-op chronicle and wyrd-setting-darkfuture's create-setting
  skill output for the `setting/` and `entities/` sides (both hold real per-type-subdirectory
  files today); the `overlay/<type>/<id>.yaml` shape is a deliberate design decision (see
  Clarifications) rather than an observed fact, since no chronicle checked has ever populated
  `overlay/` beyond its `README.md`.
- Entity type names are directory names taken as-is (no additional validation of what counts as a
  legal type is introduced by this feature).
- "Back-compat" (FR-004) means the old flat top-level `*.md` glob keeps working unchanged
  alongside the new nested `*.yaml` walk — not that old and new layouts are merged or migrated
  automatically. A single entity id should not plausibly appear in both layouts at once for one
  chronicle; this feature does not define precedence for that case beyond "both are loaded,"
  which mirrors how `entities.update(...)` already lets a later source win in the existing code.
