# Feature Specification: Session-context resolves the player character from pc.yaml

**Feature Branch**: `160-session-context-reads-pc-yaml`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "session-context/party/find/get never discover pc.yaml -- player_character is always null in real play" (GitHub issue #415)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - session-context returns the real player character (Priority: P1)

A chronicle-writing skill (e.g. `/wyrd-bootstrap`) has already produced a real chronicle: a
`chronicle.yaml`, a `pc.yaml` at the chronicle root (the character entity `create-character`
returned), and `setting/`/`overlay/`/`entities/` directories that do not themselves contain the
player character. A caller (e.g. `/wyrd-play`) runs `session-context` to load the Always-loaded
tier at the start of a session.

**Why this priority**: this is the exact failure the issue reports -- `session-context` is the
one call `/wyrd-play`'s Always-loaded tier depends on, and it silently returns
`player_character: null` today against every chronicle these skills actually produce, blocking
play outright rather than merely degrading it.

**Independent Test**: build a chronicle directory with `pc.yaml` at its root and nothing mirrored
into `entities/`; call `session-context`; confirm `player_character` is the character's frontmatter,
not `null`.

**Acceptance Scenarios**:

1. **Given** a chronicle directory with `pc.yaml` at its root (`type: character`,
   `role: player`) and no player-character file anywhere under `entities/`, **When**
   `session-context` is called against that directory, **Then** its `player_character` field is
   that character's frontmatter.
2. **Given** the same layout, **When** `chronicle.yaml`/`entities/`/`overlay/`/`setting/` are
   otherwise unmodified from what a real bootstrap produces, **Then** no additional file need be
   written anywhere (in particular, nothing needs to be duplicated into `entities/`) for
   `session-context` to succeed.

---

### User Story 2 - get/find/party stay consistent with session-context's view (Priority: P2)

The same chronicle also needs its player character to be a resolvable entity for the other
verbs that share its entity set: `get <player-character-id>` should resolve it, and
`find --type character`/`party` should be able to see it alongside every other character the
chronicle already carries, rather than the player character being visible only through
`session-context`'s own special-cased field.

**Why this priority**: the issue's title names `party`/`find`/`get` alongside `session-context`
specifically because they all read the same effective entity set today; fixing only
`session-context`'s own tier query while leaving the underlying entity set blind to `pc.yaml`
would leave those verbs inconsistent with it (e.g. `get <pc-id>` still failing right after
`session-context` just returned that same id).

**Independent Test**: against the same chronicle directory as User Story 1, call `get` with the
player character's id and confirm it resolves; call `find --type character` and confirm the
player character's id is among the results.

**Acceptance Scenarios**:

1. **Given** the chronicle from User Story 1, **When** `get <player-character-id>` is called,
   **Then** it resolves to the same frontmatter `session-context` reported.
2. **Given** the same chronicle, **When** `find --type character` is called, **Then** the
   player character's id is included in the results.

---

### Edge Cases

- No `pc.yaml` exists at all (a chronicle before its first bootstrap, or one that genuinely has
  no player character yet): `session-context`'s `player_character` stays `null`, exactly as
  today -- this is not an error case, since `always_tier`'s own contract already treats "no
  player-role entity found" as a valid, `null` result.
- A player character already exists as an `entities/*.md` file (a hand-built fixture, or a
  future chronicle-writing skill that goes back to writing it there) *and* a `pc.yaml` is also
  present: this is a data inconsistency no caller asked this feature to arbitrate silently, so
  it is treated the same way `always_tier` already treats two `role: player` entities today --
  raising, rather than silently preferring one over the other.
- `pc.yaml` exists but fails schema validation (missing `id`, wrong `type`/`role`, malformed
  frontmatter): surfaced as the same kind of error an invalid `entities/*.md` file already
  produces today, not swallowed into a silent `null`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The chronicle's effective entity set MUST include the character described by
  `pc.yaml` at the chronicle root, when that file exists, without requiring it to also exist
  under `entities/`.
- **FR-002**: `session-context`'s `player_character` field MUST be populated from that entity
  when `pc.yaml` exists and describes a `role: player` character, against an otherwise-unmodified
  real chronicle layout (`chronicle.yaml`, `setting/`, `overlay/`, `entities/` as a chronicle
  bootstrap produces them, plus `pc.yaml` at the root).
- **FR-003**: `get`, `find`, and `party` MUST see the same entity `session-context` reports as
  `player_character` -- i.e. the fix MUST live where these verbs' shared entity set is
  assembled, not as a `session-context`-only special case.
- **FR-004**: No chronicle-writing skill (`/wyrd-bootstrap` or any future one) MUST be required
  to duplicate the player character into `entities/` for any of the above to hold -- `pc.yaml`
  remains the single source of truth for the player character.
- **FR-005**: If more than one entity in the resulting set carries `role: player` (whether from
  `pc.yaml` colliding with an `entities/*.md` file, or otherwise), the system MUST raise rather
  than silently pick one -- consistent with `always_tier`'s existing multiple-player-character
  behavior.
- **FR-006**: If `pc.yaml` does not exist, `session-context`'s `player_character` field MUST
  remain `null` -- this is not treated as an error.
- **FR-007**: If `pc.yaml` exists but fails entity schema validation, the system MUST surface
  that failure the same way an invalid `entities/*.md` file's validation failure is already
  surfaced -- not swallowed into a `null` result.

### Key Entities

- **Player character (`pc.yaml`)**: the chronicle's single `type: character`, `role: player`
  entity, stored as a standalone frontmatter+body file at the chronicle root rather than under
  `entities/` -- the same entity-file schema (docs/design/25-entities.md), just a different
  location, per `wyrd-chronicle-template`'s documented layout and the already-implemented
  `/wyrd-bootstrap` skill (specs/156-wyrd-bootstrap-skill).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Against a real, unmodified chronicle layout (`pc.yaml` at the chronicle root,
  nothing mirrored into `entities/`), `session-context`'s `player_character` field is non-null
  and matches `pc.yaml`'s frontmatter, every time -- verified by an automated regression test
  built from exactly that layout.
- **SC-002**: `get`, `find`, and `party` each resolve/see the same player character
  `session-context` reports, against the same layout.
- **SC-003**: A chronicle with no `pc.yaml` at all still returns `player_character: null` from
  `session-context`, unchanged from before this feature.

## Assumptions

- `pc.yaml`'s on-disk format is the same entity frontmatter+body schema every other entity file
  uses (docs/design/25-entities.md) -- confirmed by specs/156-wyrd-bootstrap-skill's own contract,
  which has `/wyrd-bootstrap` write it "per docs/design/25-entities.md's plain frontmatter+prose
  schema", not a bespoke bare-YAML format.
- A chronicle carries at most one `pc.yaml` (one player character per chronicle) -- consistent
  with `wyrd-chronicle-template`'s documented layout and every existing single-player-character
  assumption `always_tier` already makes.
- `docs/design/02-architecture.md` and `docs/design/22-state.md` describe the player character
  as living under `entities/` as an ordinary entity; the actually-implemented and deployed
  chronicle layout (`wyrd-chronicle-template`'s own README, and the already-merged
  `/wyrd-bootstrap` skill) instead writes it to a distinct `pc.yaml` at the chronicle root. This
  feature follows the deployed, real layout (matching this issue's own Definition of Done), and
  separately flags the design-document/implementation mismatch rather than silently resolving it
  by rewriting either the design docs or the chronicle template in this change -- both are a
  larger reconciliation than this bug fix's scope.
- This feature does not change `wyrd-chronicle-template` or any chronicle-writing skill; it
  changes only how this repository's engine resolves an existing, already-deployed `pc.yaml`
  file.
