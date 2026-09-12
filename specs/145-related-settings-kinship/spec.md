# Feature Specification: Related settings — shared worlds and kindred tone

**Feature Branch**: `145-related-settings-kinship`

**Created**: 2026-09-12

**Status**: Draft

**Input**: User description: "Related settings: shared worlds and kindred tone — a setting can
declare its relationships to other settings, distinguishing same-world kinship (different games
in one world, content largely portable) from kindred-tone kinship (different worlds, similar
register, content needs reskinning), so that content converted for one setting can be reused in
a related one instead of re-derived from source, with the borrowed entity recording where it
came from."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Declare that two settings share a world (Priority: P1)

A setting author maintaining several settings that cover one world from different angles (for
example, several campaigns in one long-running far-future setting, or two settings covering one
pre-modern world from different rule systems) wants the catalogue to record that they are the
same world, so a later reuse decision can trust the catalogue instead of guessing from repo
names.

**Why this priority**: This is the relation the catalogue already gestures at (an existing
grouping field) but does not yet make anything of. Without it, nothing distinguishes "these are
the same world" from "these merely sound alike."

**Independent Test**: Can be fully tested by declaring two settings as the same world and
confirming the catalogue validator accepts the declaration, treats it as symmetric, and rejects
a setting claiming to share a world with itself or with a setting that does not exist.

**Acceptance Scenarios**:

1. **Given** two settings in the catalogue, **When** an author declares them as the same world,
   **Then** the catalogue records that relation in one place and the validator confirms it is
   internally consistent (each side of the relation names the other).
2. **Given** a same-world declaration naming a setting id that is not in the catalogue, **When**
   the catalogue is validated, **Then** validation fails with a specific error naming the unknown
   id.

---

### User Story 2 - Declare that two settings are kindred in tone (Priority: P2)

A setting author wants to record that two settings — different worlds, unrelated systems — sit
close enough in tone and register (grit, scale of heroism, attitude to mortality) that content
converted for one is a good starting point for the other, even though it needs reskinning rather
than direct import.

**Why this priority**: This is the relation the issue calls out as easy to conflate with
same-world kinship, and conflating them would make an author import content that reads as
directly portable when it actually needs reworking.

**Independent Test**: Can be fully tested by declaring two unrelated-world settings as
kindred-tone and confirming the catalogue records this as a distinct relation from same-world,
never merged into one list.

**Acceptance Scenarios**:

1. **Given** two settings with no world in common, **When** an author declares them
   kindred-tone, **Then** the catalogue records a kindred-tone relation that is visibly distinct
   from a same-world relation.
2. **Given** a setting declared both same-world and kindred-tone with a second setting, **When**
   the catalogue is validated, **Then** validation fails, because the two relations are not the
   same claim and a setting cannot be in both states with the same other setting.

---

### User Story 3 - Borrow content from a related setting with provenance recorded (Priority: P1)

A setting author building a new setting wants to bring in a character, creature, location,
adventure or threat already converted for a related setting, adapting it as needed (verbatim for
a same-world relation, reskinned for a kindred-tone one), and have the result record where it
actually came from — the same discipline already required of content converted from a published
source.

**Why this priority**: This is the payoff the whole feature exists for. Declaring kinship with no
reuse mechanism attached would leave the goal unmet.

**Independent Test**: Can be fully tested by borrowing one entity from a declared-kin setting
into another and confirming the resulting entity carries a provenance record naming the
originating setting and entity, and that the borrowing setting only proceeds when a kinship
relation is actually declared between the two.

**Acceptance Scenarios**:

1. **Given** two settings declared as the same world, **When** an entity is borrowed from one
   into the other, **Then** the borrowed entity is usable without reskinning and records which
   setting and entity it was borrowed from.
2. **Given** two settings declared kindred-tone, **When** an entity is borrowed from one into the
   other, **Then** the mechanical shape (stats, danger, structure) carries over but the entity
   also carries reskinned vocabulary and flavour appropriate to the destination setting, and still
   records its origin.
3. **Given** two settings with no declared relation, **When** an author attempts to borrow an
   entity between them, **Then** the borrowing is not treated as reuse — the author is doing a
   fresh conversion, with the same provenance discipline that already applies to a source
   converted from a published system.
4. **Given** a borrowed entity whose origin setting is private, **When** the borrowing setting is
   public, **Then** the borrowed entity's data does not enter the public repository — only the
   mechanism that borrowing uses is public, never private content moved into a public place.

### Edge Cases

- What happens when a setting declares kinship with itself? Rejected — a setting cannot be its
  own kin.
- What happens when a same-world group already recorded in the catalogue (the existing grouping
  field) implies content is portable, but an author instead wants to record only a looser
  kindred-tone tie between two of that group's members and something outside it? Both relations
  can coexist across a setting's different kin — the constraint (User Story 2, Scenario 2) is only
  that the *same pair* cannot hold both relations at once.
- What happens when a setting is deleted or renamed? Any relation naming it becomes invalid and
  the catalogue validator must fail until the relation is updated or removed — a relation is not
  permitted to point at nothing.
- What happens when a borrowed entity is itself already a borrowed or converted entity (borrowed
  twice, or converted then borrowed)? Provenance names the immediate setting and entity it was
  borrowed from, which in turn carries its own provenance — a chain, not a single flattened
  origin, so the trail is never lost.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The catalogue MUST provide a way to declare that two settings are the same world,
  distinct from any existing grouping mechanism, and this declaration MUST be the single place
  same-world kinship is recorded (not duplicated in each setting's own file).
- **FR-002**: The catalogue MUST provide a way to declare that two settings are kindred in tone,
  visibly distinct from a same-world declaration, and MUST NOT allow the same pair of settings to
  hold both relations simultaneously.
- **FR-003**: Every kinship declaration MUST be authored explicitly, not derived automatically
  from the tone contract — the tone contract's dimensions are categorical judgements, not a
  numeric distance, so no automatic threshold can be justified without being arbitrary; the
  rationale for asserting rather than deriving MUST be recorded alongside the feature.
- **FR-004**: A kinship declaration MUST be validated for consistency: both settings named in a
  relation must exist in the catalogue, a setting must not declare kinship with itself, and a
  relation must be recorded in a way that is checkable as symmetric (declaring A related to B
  must not silently omit that B is related to A).
- **FR-005**: The specification MUST state, for each kinship type, what may be borrowed
  unchanged and what must be reskinned: a same-world relation permits an entity to be borrowed
  and used as-is; a kindred-tone relation permits an entity's mechanical shape (stats, danger,
  structure) to be borrowed but requires its vocabulary and flavour to be reskinned for the
  destination setting.
- **FR-006**: A borrowed entity MUST record its provenance — which setting and which entity it
  was borrowed from — using the same discipline already required of an entity converted from a
  published source (a source and a version an entity is stamped with).
- **FR-007**: Borrowing between two settings with no declared kinship relation MUST NOT be
  treated as a distinct "reuse" path; it is an ordinary fresh conversion and follows the existing
  conversion provenance rules instead.
- **FR-008**: The mechanism for declaring kinship and recording provenance MUST be publishable in
  this repository; the content it names (the actual borrowed entities, and the settings
  themselves where private) MUST NOT enter this repository — borrowing happens entirely within
  and between setting repositories.
- **FR-009**: No setting or system name introduced by this feature's documentation or schema may
  appear in `docs/design/` or `README.md`; kinship types are named in descriptive, setting-neutral
  language.

### Key Entities

- **Same-world relation**: A symmetric declaration that two settings cover one world from
  different angles. Implies content is largely portable without reskinning.
- **Kindred-tone relation**: A symmetric declaration that two settings, covering unrelated
  worlds, share close enough tone and register that converted content is a productive starting
  point. Implies the mechanical shape of borrowed content carries over but vocabulary and flavour
  must be reworked for the destination setting.
- **Borrowed entity**: Any setting entity (character, creature, location, adventure, threat) that
  originated in one setting and was brought into a related one. Carries a provenance record
  naming its origin setting, origin entity, and the kinship relation under which it was borrowed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An author can look at the catalogue and determine, for any two settings, whether
  they are unrelated, same-world, or kindred-tone, without inspecting either setting's own files.
- **SC-002**: An author borrowing an entity between two related settings can do so without
  re-deriving it from the original source material, and the result unambiguously names where it
  came from.
- **SC-003**: A catalogue-consistency check (extending the existing catalogue validator) catches
  every malformed kinship declaration described in the Edge Cases and Functional Requirements
  above — an unknown setting id, self-kinship, an asymmetric relation, and a pair declared as
  both same-world and kindred-tone — before the catalogue is otherwise treated as valid.
- **SC-004**: No content specific to a private setting appears in this repository as a result of
  this feature; only the schema and validation mechanism do.

## Assumptions

- The existing `group:` field in `settings.yaml` is the natural home for same-world kinship — it
  already exists for exactly this purpose but currently has no defined semantics beyond a shared
  label; this feature gives it (or a field replacing it, named consistently) an actual meaning and
  a validator.
- Kindred-tone kinship is new and has no existing field; it is added to the same catalogue,
  alongside same-world, so kinship of either kind is declared in exactly one place —
  `settings.yaml` — rather than split between the catalogue and each setting's own `setting.yaml`.
- This feature specifies the declaration and provenance mechanism and the catalogue-level
  validation of it; it does not implement the tooling that performs an actual borrow (copying and
  reskinning an entity from one setting repository into another), which remains future work
  building on this specification, consistent with the issue's stated scope ("out of scope: the
  actual conversion of any specific content").
- Kinship declarations, like the rest of `settings.yaml`, are themselves publishable — they name
  which settings relate to which, not any of the settings' private content.
