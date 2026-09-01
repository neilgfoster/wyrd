# Feature Specification: Character entity schema and validator

**Feature Branch**: `229-character-entity-schema`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "Character entity schema and validator — extend engine/wyrd/state.py to load, validate, and save the full player-character entity shape from docs/design/22-state.md, plus the skill-scale primitives from docs/design/10-the-character.md. Part of #209/#90."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A player-character entity round-trips through save and load (Priority: P1)

The GM saves a character's full state — every field docs/design/22-state.md documents — and
loads it back later, recovering exactly what was saved: an entity file (markdown with YAML
frontmatter, per `docs/design/25-entities.md`), not a bare YAML value.

**Why this priority**: Without this, nothing else in the character model can be built — every
later feature (character creation, combat, advancement) reads and writes this same shape.

**Independent Test**: Save a character entity with every documented field populated, load it
back, and confirm every field matches exactly — no CLI or rule logic needed to verify the round
trip itself.

**Acceptance Scenarios**:

1. **Given** a character entity with values for every field in docs/design/22-state.md's "The
   player's character" section, **When** it is saved then loaded, **Then** every field's value
   is recovered unchanged.
2. **Given** a character entity file, **When** it is loaded, **Then** its markdown body (any
   prose below the frontmatter) is preserved unchanged, even though this feature does not
   interpret it.
3. **Given** a character entity is saved, **When** the file is inspected, **Then** it is valid
   markdown with a `---`-delimited YAML frontmatter block, per the entity format every other
   entity type already uses.

---

### User Story 2 - A wound's documented rules are enforced, not merely stored (Priority: P2)

When a character's `wounds` list is loaded, every documented constraint on a wound entry is
checked, and a file that violates one is rejected with a clear error rather than silently
accepted.

**Why this priority**: `docs/design/22-state.md` names these as **load errors**, explicitly —
"an `effect` of `skill: -N` with no `bears_on` is a load error," not a warning. Silently
accepting a malformed wound would let a real rule (a lasting penalty) go unenforced with no
visible sign anything was wrong.

**Independent Test**: Construct a wound entry violating each documented rule in turn and confirm
each is rejected on load, independent of the rest of the character's fields.

**Acceptance Scenarios**:

1. **Given** a wound with `effect: {damage: 5}` (not one of `stamina_max`, `skill`, `dread`),
   **When** the character is loaded, **Then** loading fails with a clear error naming the wound
   and the invalid effect.
2. **Given** a wound with `effect: {skill: -10}` and no `bears_on`, **When** the character is
   loaded, **Then** loading fails — the penalty would have nothing to apply to.
3. **Given** a wound with `effect: {skill: -10}` and a `bears_on` value, **When** the character
   is loaded, **Then** it loads successfully.
4. **Given** a wound with `recurring: true` and a non-null `closed`, **When** the character is
   loaded, **Then** loading fails — a recurring wound never closes.
5. **Given** a wound with `closed` set to a beat number (not `recurring`), **When** the
   character's active effects are computed, **Then** that wound's effect is excluded, while the
   wound entry itself remains present in `wounds`.
6. **Given** a wound with `effect: {stamina_max: -1}` or `effect: {dread: 1}` and no `bears_on`,
   **When** the character is loaded, **Then** it loads successfully — `bears_on` is required
   only for a `skill` effect.

### Edge Cases

- What happens when a character entity has no `wounds` field at all? Treated as an empty list —
  a character with no wounds yet is not malformed.
- What happens when a saved entity is loaded by a reader that doesn't know a field (e.g. an
  older or newer schema)? Out of scope for this feature — schema versioning and migration
  (`docs/design/22-state.md`'s `schema_version` field, `docs/design/29-evolution.md`) is a
  separate, already-scoped concern this feature does not implement; this feature validates the
  *current* schema version's shape only.
- What happens to a wikilink-formatted value (e.g. `career: [[some-career]]`, per
  `docs/adr/0011`)? Stored and returned as an opaque string, unresolved — this feature has no
  career graph or setting data to resolve it against (documented as an Assumption below).
- What happens when the entity's markdown body contains its own `---` lines (e.g. a horizontal
  rule in prose)? Only the *first* two `---` lines (opening and closing the frontmatter block)
  delimit the frontmatter; everything after the second `---` is body, including any further
  `---` lines within it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST parse an entity file into its YAML frontmatter (a mapping) and its
  markdown body (raw text after the closing `---`), and MUST be able to serialize the two back
  into the same file format.
- **FR-002**: The engine MUST load, validate, and save every field docs/design/22-state.md's "The
  player's character" section documents: `id`, `type`, `role`, `loyalty`, `career`,
  `career_history`, `skills`, `stamina`, `fate`, `fortune`, `resolve`, `taint`, `trauma`,
  `strain`, `pending_omen`, `hidden_threshold`, `fault_line`, `transformations`, `afflictions`,
  `dread`, `reputation`, `drives`, `misfortune`, `wounds`, `holdings`, `allegiances`, `marks`,
  `advances_unspent`.
- **FR-003**: A wound's `effect` MUST be one of the closed set `stamina_max`, `skill`, `dread` —
  any other key is a load error.
- **FR-004**: A wound with a `skill` effect MUST carry a `bears_on` value — its absence is a
  load error. `bears_on` is not required for `stamina_max` or `dread` effects.
- **FR-005**: A wound with `recurring: true` MUST NOT carry a non-null `closed` — this
  combination is a load error.
- **FR-006**: The engine MUST provide a way to compute a character's currently active wound
  effects, excluding any wound whose `closed` is non-null (and never excluding a `recurring`
  wound, which cannot close).
- **FR-007**: A closed wound MUST remain present in the loaded `wounds` list — closing a wound
  never deletes it.
- **FR-008**: The engine MUST provide skill-scale primitives: the value a skill opens at (25) and
  the amount it rises by per advance (+5), per docs/design/10-the-character.md section 2.
- **FR-009**: The engine MUST reuse the existing `UNTRAINED_SKILL` constant (#221) rather than
  redefining the untrained rate.
- **FR-010**: The CLI MUST expose entity load/save and the skill-scale primitives as
  `describe`-discoverable, catalog-driven verbs, per the established shape.
- **FR-011**: Nothing in this feature may name a specific setting, system, or source text.

### Key Entities

- **Character entity**: a markdown file with YAML frontmatter, per `docs/design/25-entities.md`
  and `docs/design/22-state.md`'s specific player-character shape. Persisted via #221's atomic
  save/load, extended to handle the frontmatter+body format rather than a bare YAML value.
- **Wound**: one entry in a character's `wounds` list — `id`, `from`, `effect`, `bears_on`
  (optional), `recurring`, `closed`, `description`. Validated per FR-003 through FR-007.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A character entity populated with every documented field round-trips through
  save/load with zero field discrepancies, verified field-by-field.
- **SC-002**: Each of the four wound load-error rules (invalid effect key, missing `bears_on` on
  a skill effect, `recurring` with non-null `closed`) is rejected, and each of the two positive
  cases (valid skill effect with `bears_on`, `stamina_max`/`dread` effect with no `bears_on`) is
  accepted — six total cases, zero false positives or negatives.
- **SC-003**: Active-effects computation excludes exactly the closed, non-recurring wounds from
  a mixed set of open, closed, and recurring wounds, verified against a constructed set covering
  all three.
- **SC-004**: `skill_open_value()` returns 25 and `skill_advance_step()` returns 5, with zero
  deviation.

## Assumptions

- Wikilink-formatted values (`career`, `loyalty`, and similar identifiers written as
  `[[some-id]]` per ADR 0011) are stored and returned as opaque strings — this feature does not
  resolve them against any setting or career-graph data, since neither exists in the engine yet.
- Schema versioning/migration (`schema_version`, `docs/design/29-evolution.md`) is out of scope;
  this feature validates the current schema version's shape only.
- Character creation (turning a setting's options into a populated character) is out of
  scope — a separate epic (#210). This feature only defines and validates the shape a created
  character must satisfy.
- Companions (`docs/design/22-state.md`'s "Companions" section — `role: companion`, `status`,
  `bond`) and adversaries are out of scope for this feature; the player-character shape (`role:
  player`) is what's implemented here, per #209's own scoping in its issue body.
- Career-cap enforcement on skill advancement is out of scope — no career graph exists in the
  engine yet.
- Following #221-#224's precedent: Python 3.11+, standard library only, stdlib `unittest`, no
  pytest, catalog-driven CLI dispatch, no third-party YAML dependency.
