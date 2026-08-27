# Feature Specification: Define the register tone field in 01-principles.md

**Feature Branch**: `041-register-tone-field`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Define the register tone field in 01-principles.md (closes #135). register is declared as a tone: field and used generically in prose but the 'What each means to the engine' table skips it entirely."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A setting author or GM reads what `register` does (Priority: P1)

Someone reading `01-principles.md`'s tone contract wants to know what the `register` field means
to the engine, the same way they can already read what `prophecy` or `mortality` mean, without
having to separately discover `24-authoring-a-setting.md`'s worked-example row or infer it from
the YAML comment alone.

**Why this priority**: This is the exact gap #135 raised — every other tone field is documented in
the table; `register` is declared and used but never explained there.

**Independent Test**: Read the "What each means to the engine" table and find a `register` row
with the same depth of explanation as every other row.

**Acceptance Scenarios**:

1. **Given** `01-principles.md`'s tone-field table, **When** a reader looks for `register`,
   **Then** they find a row explaining it is a one-line pointer to the setting's `voice.md` — the
   compressed summary of the narrative voice, read alongside the full voice file — not a separate
   mechanism of its own.
2. **Given** `24-authoring-a-setting.md`'s own existing explanation of `register` (its worked
   example: "The register | `voice.md` — elegiac, where another line might be dry or brutal"),
   **When** compared against `01-principles.md`'s new row, **Then** both describe the same thing
   consistently — no two-coherent-descriptions divergence (the exact fault #92 checks for).

### Edge Cases

- Does `register` need mechanical enforcement the way `prophecy: forbidden` does (the GM contract
  explicitly forbids inventing a prophecy)? No — `register` is documentary/descriptive, read as
  context for narration, not a hard constraint the engine checks against. The new table row states
  this explicitly so it isn't mistaken for an enforced field like the others.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `01-principles.md`'s "What each means to the engine" table MUST include a `register`
  row, matching the documentation depth of every other tone field.
- **FR-002**: The row's explanation MUST be consistent with `24-authoring-a-setting.md`'s existing
  description of `register` (its `voice.md` worked-example row) — no divergent restatement.
- **FR-003**: This feature MUST NOT introduce a new mechanism — `register` remains exactly what it
  already is (a one-line YAML field, a pointer to `voice.md`), only now documented where every
  other tone field already is.

### Key Entities

*(none — this feature adds one table row, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader of `01-principles.md` alone (no need to cross-reference
  `24-authoring-a-setting.md`) can state what `register` means to the engine.
- **SC-002**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass
  with the new row in place.

## Assumptions

- `register`'s meaning is not being invented here — `24-authoring-a-setting.md` already
  establishes it (a one-line pointer to `voice.md`, the full narrative-voice file) and explicitly
  points setting authors back to `01-principles.md` for the tone contract's field-by-field
  meaning. This feature closes that loop rather than deciding new semantics.
- Documentation-only: no ADR needed (no alternative is being rejected, per CLAUDE.md's ADR test)
  and no code/schema changes, since `register` is prose-only YAML data already in use.
