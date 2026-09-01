# Feature Specification: Character creation procedure

**Feature Branch**: `232-character-creation-procedure`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "Character creation procedure — implement the 8-step procedure from docs/design/11-character-creation.md that turns a chosen career, a validated advance allocation, a Loyalty, and caller-supplied fiction into a complete player-character entity. Depends on #231. Part of #210/#90."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Creation produces the fixed starting values every time (Priority: P1)

Given any valid inputs, creation sets Stamina, Fate, Fortune and the zeroed tracks to exactly
the documented values — never something computed from the choices made, and never something
that could vary between two runs with the same inputs.

**Why this priority**: `docs/design/11-character-creation.md`: "it must produce the same
character shape every time — two runs that disagree are a bug, not a flourish." This is the
guarantee the whole procedure exists to hold, and the values themselves (Stamina 6, Fate by
`mortality`) are each independently derived and checked elsewhere (section 2's own "Why Stamina
is 6" and "Why Fate rises with mortality").

**Independent Test**: Call creation with a minimal valid career/allocation/Loyalty and confirm
Stamina/Fate/Fortune/tracks match the documented table exactly, independent of what career or
allocation was chosen.

**Acceptance Scenarios**:

1. **Given** any valid career and allocation, **When** a character is created, **Then**
   `stamina` is `{current: 6, max: 6}`.
2. **Given** `mortality: "low"`, **When** a character is created, **Then** `fate` is `{current:
   2, max: 2}` and `fortune` is `{current: 2}`.
3. **Given** `mortality: "standard"`, **When** a character is created, **Then** Fate/Fortune are
   3.
4. **Given** `mortality: "high"`, **When** a character is created, **Then** Fate/Fortune are 4.
5. **Given** any valid inputs, **When** a character is created, **Then** `taint`, `trauma`,
   `strain`, `dread` are all 0, and `resolve` is `{current: 0}`.

---

### User Story 2 - Creation composes a validated allocation into the character's skills (Priority: P2)

Creation calls #231's `validate_allocation` with the chosen career (and ancestry, if any) and
the caller's allocation; on success the resulting skill percentages become the character's
`skills` map. An invalid allocation stops creation before any character is produced.

**Why this priority**: This is where creation's step 1-2 (choose career, spend advances)
actually lands in the produced entity — without it, creation would need to re-implement
allocation logic #231 already owns.

**Independent Test**: Call creation with a deliberately invalid allocation (e.g. wrong total)
and confirm no character entity is produced, with the specific rejection reason surfaced.

**Acceptance Scenarios**:

1. **Given** a valid career and a valid 8-advance allocation, **When** a character is created,
   **Then** the produced `skills` map exactly matches what #231's `validate_allocation` returns
   for that allocation.
2. **Given** an allocation #231 would reject (e.g. totalling 7), **When** creation is attempted,
   **Then** no character entity is saved, and the rejection reason is reported.

---

### User Story 3 - Creation carries the caller's fiction through unjudged (Priority: P3)

The character's name, Loyalty, Drive(s), Misfortune, and Fault Line sentence are all supplied by
the caller (the GM and player, at the table) and are recorded exactly as given — creation does
not evaluate, generate, or reject them on content.

**Why this priority**: `docs/design/11-character-creation.md`: "the GM and player agree the
sentence at the table" — these are judgment calls this procedure explicitly does not make.
Lowest priority because it's the smallest, most mechanical piece: passing values through
unchanged.

**Independent Test**: Supply a name, Loyalty, Drive list, Misfortune, and Fault Line sentence,
and confirm each appears in the produced entity unchanged.

**Acceptance Scenarios**:

1. **Given** a name, a Loyalty identifier, a list of Drives, a Misfortune, and a Fault Line
   sentence, **When** a character is created, **Then** each appears in the produced entity's
   frontmatter exactly as supplied.
2. **Given** no career_history, wounds, holdings, allegiances, or marks are supplied (a
   brand-new character), **When** created, **Then** each of these fields is an empty list in the
   produced entity.

### Edge Cases

- What happens to `advances_unspent`? Creation's 8 advances are fully spent on the allocation
  (per #231, an allocation always totals exactly 8), so a freshly created character has
  `advances_unspent: 0`.
- What happens to `hidden_threshold`, `pending_omen`, `transformations`, `afflictions`,
  `reputation`? All start at their documented empty/zero state (`docs/design/22-state.md`):
  `hidden_threshold: null`, `pending_omen: null`, `transformations: []`, `afflictions: []`,
  `reputation: {score: 0, label: null}` — nothing has happened yet.
- What happens to "a Bond" (step 7 of the procedure)? Out of scope — `docs/design/22-state.md`'s
  player-character shape has no `bond` field; `bond` belongs to a *companion* entity's relation
  toward the player, not a field this procedure sets on the character it produces (documented as
  an Assumption below).
- What happens if the career passed to creation doesn't match the career the allocation was
  validated against? This procedure calls `validate_allocation(actions, career, ancestry)`
  itself with the career/ancestry it's given — there is no separate "already-validated
  allocation" input to mismatch; the same career is used for both the validation call and the
  produced `career` field.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST set `stamina` to `{current: 6, max: 6}` on every created
  character, regardless of any input.
- **FR-002**: The engine MUST set `fate`/`fortune` from a `mortality` input: `low` → 2, `standard`
  → 3, `high` → 4; `fortune.current` MUST always equal `fate.current`.
- **FR-003**: The engine MUST set `taint`, `trauma`, `strain`, `dread` to 0 and `resolve` to
  `{current: 0}` on every created character.
- **FR-004**: The engine MUST call #231's allocation validator with the given career, ancestry
  (if any), and advance actions, and MUST NOT produce a character entity if that validation
  fails — the rejection reason MUST be reported instead.
- **FR-005**: On successful validation, the engine MUST set the character's `skills` to exactly
  the validator's returned percentages.
- **FR-006**: The engine MUST set `role: "player"`, the given `loyalty`, `career`, name, Drive(s)
  (`drives`), Misfortune (`misfortune`), and Fault Line (`fault_line`) exactly as supplied,
  without evaluating their content.
- **FR-007**: The engine MUST initialize `career_history`, `wounds`, `holdings`, `allegiances`,
  `marks`, `transformations`, `afflictions` to empty lists, `advances_unspent` to 0,
  `hidden_threshold`/`pending_omen` to `null`, and `reputation` to `{score: 0, label: null}`.
- **FR-008**: The engine MUST produce the character via #229's `character.save`, so the result is
  a valid entity file per that feature's own validation (e.g. an empty `wounds` list trivially
  satisfies #229's wound rules).
- **FR-009**: The CLI MUST expose creation as a `describe`-discoverable, catalog-driven verb.
- **FR-010**: Nothing in this feature may name a specific setting, system, or source text.

### Key Entities

- **Creation input**: `{name, career: dict, ancestry: dict | None, actions: list[dict], loyalty,
  mortality: "low"|"standard"|"high", drives: list, misfortune, fault_line}`.
- **Created character**: the full player-character entity from #229, produced with the fixed
  values above and #231's validated skill percentages.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For all three `mortality` values, Fate and Fortune match the documented table
  exactly, with Fortune always equal to Fate — 3 cases, zero deviation.
- **SC-002**: Stamina is `6/6` and every zeroed track is `0` across 10 differently-shaped valid
  inputs (varying career/allocation/name/etc.), with zero deviation.
- **SC-003**: An invalid allocation prevents character creation in 100% of tested rejection
  cases (reusing #231's own eight rejection cases) — no partial or invalid entity is ever
  written to disk.
- **SC-004**: A created character's `skills` map matches `validate_allocation`'s own returned
  percentages exactly, for the same four worked spreads #231 already validated.
- **SC-005**: A created character round-trips through #229's `character.save`/`character.load`
  with zero field discrepancies.

## Assumptions

- "A Bond" (creation step 7) is not a field this procedure sets on the produced character — no
  `bond` field exists in `docs/design/22-state.md`'s player-character shape; a Bond is a
  companion entity's own relation toward the player, out of scope for this feature to create or
  modify.
- "Where they are from" (a place, per step 7) is fiction the engine never reads
  (`docs/design/11-character-creation.md`'s own framing) — not a mechanical field this procedure
  sets.
- Which career, allocation, Loyalty, name, Drive, Misfortune, and Fault Line sentence to choose
  are all GM/player judgment calls this procedure accepts as already-made inputs — it composes
  and validates (via #231) but never generates or evaluates them for quality.
- Setting-requirements validation (`docs/design/11-character-creation.md` section 4) is out of
  scope — no setting loader exists in this engine yet.
- Following #221-#231's precedent: Python 3.11+, standard library only, stdlib `unittest`, no
  pytest, catalog-driven CLI dispatch.
