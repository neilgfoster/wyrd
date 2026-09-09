# Feature Specification: Entity file format engine support

**Feature Branch**: `112-entity-file-format`

**Created**: 2026-09-09

**Status**: Draft

**Input**: GitHub issue #305 — Entity file format engine support

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read and write an entity of any of the ten types (Priority: P1)

A GM (or another engine module) creates, reads, or updates an entity file — a markdown file with
YAML frontmatter — of any of the ten types `docs/design/25-entities.md` defines: `character`,
`place`, `organisation`, `arc`, `beat`, `creature`, `item`, `tracker`, `thread`, `lore`.

**Why this priority**: Without a working read/write path for the entity format itself, nothing
else in this feature (or any later feature building on it) has anything to operate on.

**Independent Test**: For each of the ten types, construct a minimal valid entity, write it,
read it back, and confirm the round trip reproduces the same data.

**Acceptance Scenarios**:

1. **Given** a valid entity of any of the ten types, **When** it is written then read back,
   **Then** every field present in the original is present and unchanged in the result.
2. **Given** an entity file missing a required common-schema field (`id`, `type`, `name`,
   `setting`, `status`), **When** it is read, **Then** the engine rejects it and names the
   missing field.
3. **Given** an entity file with a `type` outside the closed set of ten, **When** it is read,
   **Then** the engine rejects it.

---

### User Story 2 - Containment resolves without disagreement (Priority: P1)

An entity declares its container via `parent`; the container's children are found by reverse
lookup across the loaded set of entities, so the tree can never disagree with itself the way a
bidirectional `children` list could.

**Why this priority**: Containment (place → district → building, arc → arc → beat, and so on) is
the structural backbone every recursive container type relies on; without it the "two relations"
model in the design has only one working relation.

**Independent Test**: Load a set of entities forming a small tree via `parent`; ask for a given
entity's children and confirm the reverse-lookup result matches the tree by hand. Introduce a
`parent` cycle and confirm it is rejected.

**Acceptance Scenarios**:

1. **Given** three entities A (no parent), B (`parent: A`), C (`parent: B`), **When** A's
   children are requested, **Then** B is returned (not C, which is B's child, not A's).
2. **Given** an entity whose `parent` chain loops back to itself, **When** the set is loaded,
   **Then** the engine rejects the cycle rather than resolving it or looping forever.
3. **Given** an entity with no `parent` field, **When** loaded, **Then** it is accepted as a root
   (containment is optional, not every entity is contained).

---

### User Story 3 - Connections are read as a free, conditional, directional graph (Priority: P2)

A `place` (or any entity carrying connections) declares `connections` as a list of directional,
conditional edges, which may form loops (unlike containment). A `hidden: true` connection is
present in the loaded data but distinguishable from a discovered one.

**Why this priority**: Connection is the second of the two structural relations and is what makes
a world navigable rather than merely catalogued, but it is layered on top of User Stories 1-2's
read/write path rather than gating them.

**Independent Test**: Load a place with three connections, one of them `hidden: true`; confirm
all three are present in the loaded data and the hidden one is flagged distinctly from the other
two.

**Acceptance Scenarios**:

1. **Given** a place with connections `A → B` and `B → A` (a loop), **When** loaded, **Then**
   both edges are present — unlike containment, a connection cycle is not rejected.
2. **Given** a connection carrying `requires: "the gate is open"`, **When** loaded, **Then** the
   condition text is preserved verbatim and not evaluated by this feature (evaluation is a later
   concern for whichever module consults it).
3. **Given** a connection marked `hidden: true`, **When** the entity is loaded, **Then** the
   loaded data marks it as hidden, distinguishable from a connection with no such marking.

### Edge Cases

- An entity's `sources` includes an entry marked `licence: copyright`: this feature does not
  itself enforce distribution rules (that is a repository-level, human/process concern per
  `CLAUDE.md`), but the field round-trips unchanged so a later tool can act on it.
- A `[[wikilink]]`-style reference inside a field (e.g. `parent: [[the-river-city]]`) resolves to
  the bare entity id `the-river-city`; a reference to an id that is not present in the loaded set
  is reported, not silently dropped.
- An `arc`'s `scale` field (e.g. `campaign`, `adventure`) is accepted as a free label with no
  structural meaning — recursion depth is not bounded by `scale`.
- A `tracker` with `value` at or beyond a `fires` threshold: this feature loads the data
  faithfully; evaluating whether a threshold has fired is out of scope here.
- An entity file whose frontmatter parses but whose body (the prose) is empty: valid — the body
  is optional content, not a required field.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST read and write an entity file as a markdown file with YAML
  frontmatter plus a free-text body, for each of the ten closed entity types (`character`,
  `place`, `organisation`, `arc`, `beat`, `creature`, `item`, `tracker`, `thread`, `lore`).
- **FR-002**: The engine MUST validate the common schema on every entity regardless of type:
  `id` (unique, kebab-case), `type` (one of the ten), `name`, `aliases`, `setting`, `status`
  (`stub`|`drafted`|`complete`), `tags`, `sources` (each with `work`, `pages`, `licence`),
  `parent`, `links`.
- **FR-003**: The engine MUST reject an entity file missing a required common-schema field, or
  carrying a `type` outside the closed set of ten, naming the specific problem.
- **FR-004**: The engine MUST validate each type's own additional fields where the design
  specifies them (e.g. `place.scale`/`connections`/`danger`, `organisation.scale`/`objective`/
  `members`/`reach`, `arc.scale`/`entry`/`exit`/`place`/`cast`, `tracker.kind`/`value`/`max`/
  `advances_on`/`fires`, `character.role`/`archetype`/`disposition`/`allegiances`/`objective`/
  `stats`).
- **FR-005**: The engine MUST resolve an entity's children by reverse lookup over the loaded set's
  `parent` fields — `parent` is the only containment field; there is no separate `children` list
  to fall out of sync.
- **FR-006**: The engine MUST reject a `parent` chain that cycles back to itself (containment is
  strict and acyclic), and MUST accept an entity with no `parent` as a root.
- **FR-007**: The engine MUST load a `connections` list as a free, directional, conditional graph
  that MAY loop — unlike containment, a connection cycle is valid and preserved as-is.
- **FR-008**: The engine MUST preserve a connection's `hidden: true` marking distinctly in the
  loaded data, without evaluating discovery (that is a later, session-time concern).
- **FR-009**: The engine MUST resolve a `[[wikilink]]`-style reference within an entity field to
  the bare entity id it names, and MUST report (not silently ignore) a reference to an id absent
  from the loaded set.
- **FR-010**: The engine's YAML handling MUST use a restricted internal reader/writer (the pattern
  already used by `engine/wyrd/state.py` and `tools/check_bestiary.py`) rather than a third-party
  YAML dependency.

### Key Entities

- **Entity**: a markdown file with YAML frontmatter, one of ten closed types, carrying the common
  schema (`id`, `type`, `name`, `aliases`, `setting`, `status`, `tags`, `sources`, `parent`,
  `links`) plus type-specific fields.
- **Containment relation**: `parent`, a tree, strict and acyclic; children are derived by reverse
  lookup, never stored directly.
- **Connection**: a directional, conditional edge between two entities (typically places), free to
  loop, optionally `hidden`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An entity of each of the ten types can be written and read back through the new
  module with no data loss, verified by a round-trip test per type.
- **SC-002**: Every common-schema validation rule (required fields, closed `type` set, closed
  `status` set) rejects a deliberately malformed fixture in a dedicated test, with the specific
  problem named in the rejection.
- **SC-003**: A `parent` cycle is rejected 100% of the time it is constructed in a test fixture,
  and never causes an infinite loop or a stack overflow.
- **SC-004**: `python3 -m ruff check .` and `python3 -m ruff format --check .` report the new code
  clean, and tests pass under `PYTHONPATH=engine`.

## Assumptions

- This feature covers the entity file format's structure and the two structural relations only —
  it does not implement `wyrd doctor` referential-integrity checking (`docs/design/28-
  maintenance.md`), chronicle overlay resolution (a dependent feature, issue #306), or arc/beat
  entry/exit condition *evaluation* (`docs/design/18-arcs-and-beats.md`, a separate epic, #299).
- Condition text (`requires`, `entry`, `exit`) is preserved verbatim as data; this feature does
  not interpret or evaluate it.
- Entity storage location (setting repo vs. chronicle repo, and the setting/overlay split) is
  addressed by the dependent overlay feature (#306) and by chronicle-state work (#300); this
  feature works against a given set of entity files wherever they are found.
- `sources.licence` distribution enforcement remains a human/process concern per `CLAUDE.md`; this
  feature only round-trips the field faithfully.
