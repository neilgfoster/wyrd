# Feature Specification: Adversary block loading and validation

**Feature Branch**: `094-adversary-block-loading`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Adversary block loading and validation (issue #259): give the
engine a way to load one adversary block (by id, from a setting's bestiary) into a validated
in-memory shape other engine code (resolution, combat) can read from -- the same role
character.load plays for a player character. Reuse tools/check_bestiary.py's field rules rather
than re-deriving them."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load one adversary block by id (Priority: P1)

Something in the engine (resolution, combat) needs to act on a specific opponent named in the
fiction. Given a setting's bestiary and that opponent's id, the engine produces the validated
block of values every published rule reads off it.

**Why this priority**: this is the entire feature -- every other adversary-model feature (#260
baseline, #261 traits, #262 turn/Aftermath, #263 scaling) depends on having a loaded, validated
block to read from.

**Independent Test**: given a bestiary file containing a well-formed entry and its id, loading
returns a mapping with that entry's values, unchanged from what the file declared.

**Acceptance Scenarios**:

1. **Given** a bestiary file with a valid entry for id `the-hunter`, **When** the engine loads
   `the-hunter` from that file, **Then** it returns a mapping carrying that entry's fields,
   ready for other engine code to read.
2. **Given** a bestiary file with no entry for the requested id, **When** the engine attempts to
   load it, **Then** it fails clearly, naming the id and the file, rather than returning an
   empty or partial result.

---

### User Story 2 - Reject a malformed block the same way check_bestiary.py already does (Priority: P2)

A setting author's bestiary entry is missing a required field, carries a field the block doesn't
define, or holds a value outside the range the ruleset can absorb. Loading that entry for play
must fail the same way `tools/check_bestiary.py` already fails it at authoring time -- not pass
silently into play with a hole the GM has to improvise around.

**Why this priority**: docs/design/12-the-adversary.md's whole premise is that an opponent
missing a value is a judgement call the block exists to remove; a play-time loader with looser
rules than the authoring-time validator would undermine that.

**Independent Test**: load a handful of deliberately malformed entries (missing a required
field, an unrecognised field, damage without damage_type, an out-of-range value) and confirm
each is rejected with a message naming the offending field.

**Acceptance Scenarios**:

1. **Given** an entry missing one of the six required fields (`id`, `name`, `baseline`,
   `stamina_max`, `armour`, `skills`), **When** it is loaded, **Then** loading fails, naming the
   missing field.
2. **Given** an entry carrying a field the block does not define, **When** it is loaded,
   **Then** loading fails, naming the unrecognised field -- it is never silently ignored.
3. **Given** an entry with `damage` but no `damage_type` (or vice versa), **When** it is loaded,
   **Then** loading fails, naming the missing companion field.
4. **Given** an entry with no `damage` and no `damage_type` at all, **When** it is loaded,
   **Then** loading succeeds -- an opponent with no attack at all is legal.

---

### User Story 3 - Optional fields default sensibly (Priority: P3)

A setting author writing a bestiary entry doesn't have to spell out every optional field by
hand. `ranged`, when omitted, is `false` -- published rather than merely assumed, so the
engagement rule always has an answer.

**Why this priority**: a smaller correctness detail than the required-field and rejection rules
above, but load-bearing for the engagement rule elsewhere in combat, which branches on `ranged`
every time.

**Independent Test**: load a valid entry that omits `ranged` and confirm the loaded block reports
`ranged: false`.

**Acceptance Scenarios**:

1. **Given** a valid entry that does not declare `ranged`, **When** it is loaded, **Then** the
   loaded block's `ranged` is `false`.
2. **Given** a valid entry that explicitly declares `ranged: true`, **When** it is loaded,
   **Then** the loaded block's `ranged` is `true`, unchanged.

### Edge Cases

- Two entries in the same bestiary sharing an id: `check_bestiary.py` already rejects this at
  authoring time (a duplicated id); loading by id from such a file is out of scope for this
  feature to re-detect -- authoring-time validation is assumed to have already run, per how
  `character.load` also assumes a well-formed file class (it raises on parse/shape failure, not
  on cross-entry data-integrity concerns like duplicates).
- A bestiary file that fails to parse at all (malformed YAML): fails the same way `state.py`'s
  existing YAML reader already fails a malformed chronicle state file -- a named, explicit error,
  never a silent empty result.
- A `traits` entry naming an effect outside the closed six-effect vocabulary: rejected at load,
  matching `check_bestiary.py`'s existing behavior (this feature loads and validates the block's
  *shape*; issue #261 is what later *applies* a trait's effect).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a way to load one adversary block, identified by its `id`,
  from a bestiary file.
- **FR-002**: Loading MUST validate the block against the same required-field set
  `tools/check_bestiary.py` already enforces (`id`, `name`, `baseline`, `stamina_max`, `armour`,
  `skills`), failing loudly and naming the missing field(s) if any are absent.
- **FR-003**: Loading MUST reject any field not defined by the adversary block (the same closed
  optional-field set `check_bestiary.py` already enforces: `damage`, `damage_type`, `ranged`,
  `traits`, `notes`, alongside the six required fields) -- an unrecognised field is an error, not
  a silently-ignored extra.
- **FR-004**: Loading MUST enforce that `damage` and `damage_type` travel together: a block
  declaring one without the other is rejected; a block declaring neither is legal (no attack at
  all).
- **FR-005**: Loading MUST default `ranged` to `false` when the entry omits it, and pass through
  an explicit `true`/`false` unchanged when present.
- **FR-006**: Loading MUST fail clearly (naming the requested id and the file) when no entry with
  that id exists in the bestiary.
- **FR-007**: Loading MUST fail clearly when the bestiary file itself cannot be parsed, rather
  than returning a partial or empty result.
- **FR-008**: The validation rules this feature enforces MUST be the same rules
  `tools/check_bestiary.py` already enforces for the fields in scope here (required fields,
  unrecognised fields, the damage/damage_type pairing) -- expressed as engine code rather than by
  importing `tools/check_bestiary.py` directly, since `engine/` (the shipped engine) and `tools/`
  (repository-maintenance scripts) must not depend on each other (existing precedent:
  `engine/wyrd/state.py`'s YAML reader is deliberately a separate implementation of the same
  restricted subset `tools/check_bestiary.py`'s reader already covers, for the same reason).

### Key Entities

- **Adversary block**: the validated in-memory shape this feature produces -- the fields
  docs/design/12-the-adversary.md section 2 defines (`id`, `name`, `baseline`, `stamina_max`,
  `armour`, `skills`, and the optional `damage`/`damage_type`/`ranged`/`traits`/`notes`). This
  feature creates and validates this shape; it does not define what later code does with it
  (baseline resolution, trait effects, combat participation -- each a separate, dependent
  feature).
- **Bestiary file**: a setting's `setting/bestiary.yaml`, holding one `creatures:` list of
  adversary-block entries. This feature reads it; it does not write to it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given any bestiary entry that already passes `tools/check_bestiary.py`'s
  validation, loading that entry by id at play time succeeds and returns every field the entry
  declared.
- **SC-002**: Given any bestiary entry that `tools/check_bestiary.py` already rejects for a
  reason in this feature's scope (missing required field, unrecognised field, damage/damage_type
  mismatch), loading that entry at play time fails with a message naming the same field
  `check_bestiary.py` would name.
- **SC-003**: A block loaded with `ranged` omitted always reports `ranged: false` -- never
  `None`/missing/undefined -- so downstream code never has to special-case its absence.

## Assumptions

- "The engine" providing this load path is a new module (or an addition to an existing one)
  under `engine/wyrd/`, following the same per-entity load/validate shape
  `engine/wyrd/character.py`'s `load`/`validate_character` already establishes, per issue #259's
  own framing ("the same role `character.load` plays for a player character").
- Reading the bestiary file's YAML reuses `engine/wyrd/state.py`'s existing `parse_yaml`
  (the module already covers this feature's YAML needs: nested mappings, lists of mappings,
  scalars) rather than a third separate YAML reader -- `state.py`'s own docstring already frames
  this as the engine-side counterpart to `tools/check_bestiary.py`'s reader.
- Out-of-range *value* checks (a percentage outside 0-100, an armour rank outside the closed set,
  a damage type outside the closed four, a trait naming an effect outside the closed six) are in
  scope for this feature's validation, since `check_bestiary.py` already enforces them at the
  same field-presence layer this feature mirrors -- not deferred to #260/#261, which are about
  *applying* baseline/trait values during resolution, not validating that they're well-formed.
- Trait *effects* are validated for shape here (a trait needs a name and a non-empty effect from
  the closed vocabulary) but not *applied* to anything -- applying them to resolution/combat is
  #261's scope, per the issue's own out-of-scope note.
