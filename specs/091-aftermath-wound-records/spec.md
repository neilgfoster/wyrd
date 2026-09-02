# Feature Specification: The Aftermath table and wound records

**Feature Branch**: `091-aftermath-wound-records`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "The Aftermath table and wound records — implement the post-fight
`aftermath` roll (d100 + 5 x points below zero) against the row table in
docs/design/06-aftermath.md, producing wound records (including the recurring: true shape) via
the existing wound machinery in character.py. Out of scope: mortal-critical -> death-row re-read,
Fate spend re-reading death, mortality:low closing death rows, companion status transitions,
recurring wound's combat-start firing effect."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rolling Aftermath for a combatant who dropped (Priority: P1)

Once a fight ends, every combatant who dropped during it rolls once on the `aftermath` table,
modified by how far below zero they fell, and the result lands on one of the table's 8 rows.

**Why this priority**: This is the entire feature — nothing in the engine currently resolves the
roll that deferred death depends on.

**Independent Test**: Stage an aftermath roll at a range of points-below-zero modifiers and
confirm each total resolves against the correct row (by key), at every published boundary
(6/30/31, 52/53, 66/67, 78/79, 88/89, 98/99, 110/111).

**Acceptance Scenarios**:

1. **Given** a combatant who dropped by 1 point below zero, **When** aftermath is staged, **Then**
   the roll is `d100 + 5`, with a floor total of 6.
2. **Given** a total of 30, **When** the row is resolved, **Then** it reads `out-of-action`; a
   total of 31 reads `lasting-wound`.
3. **Given** a total of 111 or higher, **When** the row is resolved, **Then** it reads `death`.
4. **Given** a total above the table's last published row's upper bound, **When** the row is
   resolved, **Then** it still resolves (the last row is open-ended) rather than erroring.

---

### User Story 2 - Wound records created from a row's effect (Priority: P1)

A row that names a wound record produces one, in the exact shape `character.py`'s existing
validation (`validate_wound`) accepts, so the wound is immediately usable by every mechanic that
already reads `wounds`.

**Why this priority**: The roll alone answers nothing the chronicle can act on; the wound record
is the persisted consequence.

**Independent Test**: Resolve each row that creates a wound record and confirm the record passes
`character.py.validate_wound` unmodified, carries `from: {table: aftermath, beat: <N>}`, and
(where the row specifies one) the correct `effect`.

**Acceptance Scenarios**:

1. **Given** a `lasting-wound` result, **When** the wound record is built, **Then** it carries no
   `effect` (the row specifies "one wound record" with no named mechanical effect) and validates.
2. **Given** a `disfigured` result, **When** the wound record is built, **Then** its `effect` is
   `{dread: 1}` and it validates.
3. **Given** a `recurring-wound` result, **When** the wound record is built, **Then** it carries
   `recurring: true`, `effect: {skill: -10}`, a `bears_on` value, and no `closed` field, and it
   validates against `validate_wound`'s recurring/closed rule.
4. **Given** an `out-of-action` result, **When** resolved, **Then** no wound record is produced
   (the row's effect is "nothing lasting").

---

### User Story 3 - Every row's non-wound effect is recorded (Priority: P2)

Rows `new-enemy`, `taken`, and `death` carry consequences beyond a wound record (a nemesis entity,
a captured status, death itself); this feature records what row was reached and what it names,
without resolving those consequences into other subsystems yet (out of scope, per the driving
issue).

**Why this priority**: These rows must resolve to *something* recorded rather than silently
dropping information the later features (#3/#4 in the decomposition) depend on, but wiring them
into entity creation/companion status is explicitly deferred.

**Independent Test**: Resolve `new-enemy`, `taken`, and `death` and confirm each produces a wound
record (where the row calls for one) plus a distinguishable marker of the row's non-wound
consequence in the result, without creating any `character`/`thread` entity or mutating any
`status` field.

**Acceptance Scenarios**:

1. **Given** a `new-enemy` result, **When** resolved, **Then** a wound record is produced and the
   result names the row `new-enemy` (entity creation is out of scope here).
2. **Given** a `taken` result, **When** resolved, **Then** no wound record is produced (the row
   creates no wound) and the result names the row `taken` (thread-entity creation is out of
   scope).
3. **Given** a `death` result, **When** resolved, **Then** no wound record is produced and the
   result names the row `death` (re-reading onto the worst non-death row is out of scope — that
   is the mortal-critical/Fate-spend/`mortality: low` machinery of later features).

---

### Edge Cases

- What happens at a roll of exactly 6 (the table's documented floor)? It must resolve to
  `out-of-action`, not error.
- What happens for a points-below-zero value that pushes the modifier past what any published
  boundary anticipates (e.g. dropped by 30)? The open-ended `death` row absorbs it.
- What happens if a caller passes `points_below_zero <= 0`? This is a caller-contract violation
  (aftermath is only ever staged for a combatant who dropped, i.e. went below 0 Stamina) —
  reject it rather than silently rolling with a non-positive modifier.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide an aftermath roll: `d100 + 5 × points_below_zero`, where
  `points_below_zero` is supplied by the caller (the same value criticals already compute).
- **FR-002**: The engine MUST resolve a total against the 8-row `aftermath` table exactly as
  published in docs/design/06-aftermath.md (`out-of-action`, `lasting-wound`, `left-for-dead`,
  `new-enemy`, `taken`, `disfigured`, `recurring-wound`, `death`), with the last row open above
  111.
- **FR-003**: Rows that specify "one wound record" MUST produce a wound record dict compatible
  with `character.py`'s `validate_wound`/`WOUND_EFFECT_KEYS`, carrying `from: {table: "aftermath",
  beat: <beat>}` and a stable, unique `id`.
- **FR-004**: The `disfigured` row's wound record MUST carry `effect: {dread: 1}`.
- **FR-005**: The `recurring-wound` row's wound record MUST carry `recurring: true`, `effect:
  {skill: -10}`, and a `bears_on` field, and MUST NOT carry `closed`.
- **FR-006**: Rows that specify no wound record (`out-of-action`, `taken`, `death`) MUST NOT
  produce one.
- **FR-007**: `left-for-dead` MUST produce a wound record (the row specifies "one wound record")
  in addition to naming the row; the "wakes elsewhere, without what they carried" consequence
  (location/inventory) is narrative and out of scope for state mutation here.
- **FR-008**: The engine MUST record which row was reached (its key) and the roll/modifier/total,
  in a shape following the existing critical-roll recording convention (docs/06-aftermath.md's
  own `{"verb": "roll", "table": "aftermath", ...}` example).
- **FR-009**: The engine MUST NOT create any `character`/`thread` entity, mutate any companion
  `status`, or re-read a `death` result onto another row — all explicitly out of scope for this
  feature per the driving issue.
- **FR-010**: A check script MUST assert, by computation (not eyeballing), that across drops of
  1–12 points below zero the unweighted rates match docs/design/06-aftermath.md's own published
  figures: a lasting mark 71%, death 23%.

### Key Entities

- **Aftermath roll result**: the outcome of one aftermath roll — roll, modifier, total, resolved
  row key, and (where the row specifies one) the wound record produced.
- **Wound record**: an entry in a character's `wounds` list (docs/design/22-state.md), reused
  unchanged from the existing `character.py` machinery — this feature only produces instances of
  the existing shape, it does not extend the shape.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every one of the aftermath table's 8 rows resolves correctly at both of its
  boundary totals (and, for the last row, well above its lower boundary), verified by an
  automated check.
- **SC-002**: Every wound record produced by this feature passes `character.py.validate_wound`
  unmodified.
- **SC-003**: A check script computes and asserts the 71%/23% figures docs/design/06-aftermath.md
  states, failing if a future edit changes the rows without updating that document.

## Assumptions

- `points_below_zero` is supplied by the caller exactly as criticals already compute it
  (docs/design/05-criticals.md); this feature does not derive it from raw Stamina values itself.
- The `bears_on` value for a `recurring-wound` result is drawn from the combat context (the skill
  the blow that caused the drop bears on), consistent with how `character.py` already requires
  `bears_on` whenever an `effect` includes `skill`; the exact source field is an implementation
  detail resolved during planning, not a new schema concept.
- "Beat" follows the existing convention already used by criticals' own roll recording
  (docs/design/06-aftermath.md's own example JSON) — an integer the caller supplies, not
  something this feature invents.
- Wound `id` generation (kebab-case, unique per character) follows whatever pattern the codebase
  already uses elsewhere for generated identifiers, if one exists; otherwise a simple
  table-key-plus-beat scheme is a reasonable default, since the design doc does not mandate a
  specific generation algorithm.
