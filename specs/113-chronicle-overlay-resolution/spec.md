# Feature Specification: Chronicle overlay resolution

**Feature Branch**: `113-chronicle-overlay-resolution`

**Created**: 2026-09-09

**Status**: Draft

**Input**: GitHub issue #306 — Chronicle overlay resolution

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Setting entity with no overlay resolves unchanged (Priority: P1)

A chronicle is running against a setting. The engine loads an entity that this chronicle has
never touched — no overlay file exists for it. The effective entity the engine hands to the rest
of the system is exactly the setting entity's frontmatter and body.

**Why this priority**: This is the baseline the whole overlay mechanism must not break — most
entities in a chronicle are untouched, so this path runs constantly and must be a pure pass-
through.

**Independent Test**: Load a setting entity with no matching overlay file present in
`chronicle/overlay/` and confirm the resolved entity is byte-for-byte identical to the setting
entity's parsed frontmatter and body.

**Acceptance Scenarios**:

1. **Given** a setting entity `hallam` with no overlay, **When** the engine resolves `hallam`'s
   effective entity, **Then** every field matches the setting entity exactly and no overlay
   fields are present.

---

### User Story 2 - Overlay changes one field (Priority: P1)

The player's actions have shifted an NPC's attitude. The chronicle's overlay for that entity
carries only the field(s) that changed — for example `disposition: hunting`. The engine resolves
the effective entity with that field overridden and every other field intact from the setting.

**Why this priority**: This is the core delta mechanism the whole design exists for — it is what
lets one setting host many chronicles with different histories without ever touching the setting
files.

**Independent Test**: Create an overlay for an existing setting entity that changes exactly one
field, resolve the effective entity, and confirm that field carries the overlay's value while
every other field carries the setting entity's original value.

**Acceptance Scenarios**:

1. **Given** a setting entity `the-caretaker` with `disposition: unaware`, and an overlay
   `overlay_of: the-caretaker` with `disposition: hunting`, **When** the engine resolves
   `the-caretaker`'s effective entity, **Then** `disposition` is `hunting` and every other field
   (`name`, `role`, `allegiances`, etc.) matches the setting entity.
2. **Given** an overlay with multiple changed fields, **When** resolved, **Then** all overlaid
   fields take precedence and all remaining fields fall through to the setting entity.

---

### User Story 3 - Overlay promotes a bystander to a nemesis (Priority: P2)

A bystander the player wronged escalates into a recurring antagonist. The chronicle's overlay
introduces fields the setting entity never had at all — `role: nemesis` and a `threat` block —
without the setting file itself gaining those fields.

**Why this priority**: Promotion is the acceptance case the design explicitly calls out as the
payoff of the overlay split — it is a distinct behaviour (introducing new fields entirely, not
just overriding existing ones) that a naive shallow-merge could still get right, so it is worth
testing on its own, but it depends on the merge mechanism from User Story 2 already existing.

**Independent Test**: Create an overlay for a `role: bystander` setting entity that adds
`role: nemesis` and a `threat` block, resolve the effective entity, and confirm the resolved
entity carries both new fields while the underlying setting file is unmodified on disk.

**Acceptance Scenarios**:

1. **Given** a setting entity with `role: bystander` and no `threat` field, and an overlay
   `overlay_of: <id>` with `role: nemesis` and a `threat` block, **When** the engine resolves the
   effective entity, **Then** the resolved entity has `role: nemesis` and the given `threat`
   block, and the setting entity file on disk is unchanged.

---

### Edge Cases

- What happens when an overlay's `overlay_of` names a setting entity id that does not exist?
  Resolution reports the dangling reference rather than silently fabricating an entity from the
  overlay alone (referential-integrity enforcement itself is out of scope, per design/28, but a
  resolution-time failure must be surfaced, not swallowed).
- What happens when an overlay file's own `id` differs from its `overlay_of` target? The
  effective entity's `id` is the setting entity's `id` — the overlay's `overlay_of` is the join
  key, not a display field of the effective entity.
- What happens when an overlay sets a field to an empty/falsy value (e.g. `tags: []`) rather than
  omitting it? An explicitly-present field in the overlay — even if empty — overrides the setting
  value; only a field genuinely absent from the overlay frontmatter falls through.
- What happens when a chronicle has overlay files but no matching setting directory is loaded at
  all? Out of scope here — this feature resolves a given setting+overlay pair; wiring the
  directory scan into whatever loads a full chronicle is a separate concern.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST support loading entities from two distinct directories: a setting
  directory (read-only) and a chronicle overlay directory (the chronicle's deltas).
- **FR-002**: The engine MUST recognize an overlay file by its `overlay_of` field, naming the
  setting entity id it modifies.
- **FR-003**: The engine MUST resolve an effective entity for any setting entity id by merging
  its overlay (if one exists) over the setting entity: any field present in the overlay overrides
  the setting entity's value for that field; any field absent from the overlay falls through
  unchanged.
- **FR-004**: The engine MUST return the setting entity unchanged, with no overlay applied, when
  no overlay file exists for that entity id.
- **FR-005**: The engine MUST support an overlay introducing fields the setting entity did not
  have at all (promotion), producing an effective entity that validates against the destination
  type's schema post-merge (e.g. a promoted nemesis passes `character` validation with its new
  `role`/`threat` fields).
- **FR-006**: The engine MUST NOT modify the setting entity's file on disk as a result of
  resolving an overlay.
- **FR-007**: The engine MUST resolve the effective entity's body (the markdown prose below
  frontmatter) the same way as frontmatter: overlay body replaces setting body if the overlay
  file has a non-empty body, otherwise the setting body is used unchanged.
- **FR-008**: The engine MUST report an error naming the specific overlay file and its dangling
  `overlay_of` target when an overlay references a setting entity id that is not present in the
  loaded setting set.
- **FR-009**: The merge MUST validate the resolved effective entity against `entity.validate()`
  (from #305) and report a validation error if the merge produces a frontmatter that fails
  common-schema or type-specific validation.

### Key Entities *(include if feature involves data)*

- **Setting entity**: An entity file loaded from `chronicle/setting/` — read-only within a
  chronicle's lifetime.
- **Overlay**: A partial entity file loaded from `chronicle/overlay/`, carrying `id`,
  `overlay_of`, and any subset of fields that differ from the setting entity it targets.
- **Effective entity**: The result of merging a setting entity with its overlay (if any) — what
  the rest of the engine actually operates on. Never itself persisted as a file; computed at
  load time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a setting entity and no overlay, the resolved effective entity is identical
  to the setting entity in 100% of cases.
- **SC-002**: Given a setting entity and an overlay changing N of its fields, the resolved
  effective entity differs from the setting entity in exactly those N fields, for any N from 1 up
  to the full field count.
- **SC-003**: An overlay can promote any entity type to carry fields absent from its setting
  version, and the resulting effective entity passes the same validation any other entity of the
  destination shape would.
- **SC-004**: No test or usage in this feature ever results in a write to a file under
  `chronicle/setting/`.

## Assumptions

- Directory layout matches design/25 exactly: `chronicle/setting/` and `chronicle/overlay/`,
  both containing entity files in the same markdown+frontmatter format `state.py`/`entity.py`
  already read.
- Overlay files are loaded via the same `state.load_entity`/`parse_entity` primitives as setting
  files — an overlay is a partial entity file, not a different serialization format.
- One overlay file exists per overlaid entity (not multiple stacked overlay layers) — this
  matches design/25's description of a single chronicle-vs-setting split, not a layered history.
- Resolution happens at load time, in memory; there is no persisted "effective entity" file.
- Referential-integrity checking as a chronicle-wide health check (`wyrd doctor`) is out of
  scope, per the issue; this feature only needs the point failure named in FR-008 for a single
  resolution call.
