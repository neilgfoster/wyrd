# Feature Specification: conversion.yaml schema validator

**Feature Branch**: `317-conversion-yaml-validator`

**Created**: 2026-09-10

**Status**: Draft

**Input**: User description: "conversion.yaml schema validator — tools/check_conversion.py
validates a setting/conversion.yaml against the schema in docs/design/24-authoring-a-setting.md
('Conversion rules — required for any derived setting'), mirroring tools/check_bestiary.py and
tools/check_gear.py. Part of #298."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validating a well-formed conversion.yaml (Priority: P1)

A setting author who has derived their setting from an existing system needs to confirm their
`conversion.yaml` matches the documented schema before relying on it for on-demand conversion,
so the same source converted twice produces the same numbers (docs/design/24-authoring-a-setting.md).

**Why this priority**: Without a validator, a malformed conversion table is discovered only when
on-demand conversion silently improvises — exactly the non-determinism `27-tooling.md` exists to
prevent. This is the whole point of the feature.

**Independent Test**: Run the checker against a `conversion.yaml` matching the worked example in
`docs/design/24-authoring-a-setting.md` and confirm it passes with no problems reported.

**Acceptance Scenarios**:

1. **Given** a `conversion.yaml` with `from`, `version`, and well-formed `skills`, `difficulty`,
   `damage`, `armour`, `danger`, `rename`, `arcs`, `drop`, `drop_note`, and `manual` sections,
   **When** the checker runs, **Then** it exits 0 and reports success.

### User Story 2 - Rejecting a malformed conversion.yaml (Priority: P1)

A setting author who omits a required section or uses a value outside the schema needs to find
out immediately, with an error naming the specific problem, not have on-demand conversion
improvise around the gap.

**Why this priority**: Matches `check_bestiary.py`/`check_gear.py`'s existing contract — a missing
field, an unrecognised field, or a closed-vocabulary violation is a checkable claim
(`27-tooling.md`) and must be caught by the script.

**Independent Test**: Feed the checker a `conversion.yaml` missing `from` or `version`, and
separately one with a `damage_type` outside the closed four, and confirm each fails with an error
naming the offending field.

**Acceptance Scenarios**:

1. **Given** a `conversion.yaml` missing the top-level `from` or `version` key, **When** the
   checker runs, **Then** it exits non-zero with an error naming the missing key.
2. **Given** a `conversion.yaml` whose `damage.wounds_to_stamina` (or any other place a damage
   type appears) names a `damage_type` outside `slashing`, `piercing`, `blunt`, `searing`
   (docs/adr/0022), **When** the checker runs, **Then** it exits non-zero naming the offending
   value and the closed set.
3. **Given** a `conversion.yaml` containing a field the schema does not define, **When** the
   checker runs, **Then** it exits non-zero naming the unrecognised field.
4. **Given** a `conversion.yaml` that is not valid YAML, **When** the checker runs, **Then** it
   exits non-zero with a parse error.

### Edge Cases

- `skills.method`, `armour.method` are a closed vocabulary (`direct`/`scale`/`table`) — an
  unrecognised method is rejected the same way a bad `damage_type` is.
- `drop`, `manual` are lists of free-text labels (setting-defined, not engine-closed) — checked
  only for being lists of strings, mirroring how `gear.yaml`'s `availability` is left free-text.
- `danger.formula` is a free-text string (a human-readable derivation), not parsed or evaluated.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The checker MUST read a `conversion.yaml` file using the engine's existing
  restricted-subset YAML reader (`check_bestiary.read_yaml`), not a new parser.
- **FR-002**: The checker MUST reject a `conversion.yaml` missing either required top-level key,
  `from` or `version`, naming the missing key.
- **FR-003**: The checker MUST reject a `conversion.yaml` containing a top-level field the schema
  does not define, naming the unrecognised field.
- **FR-004**: When present, `skills.method` and `armour.method` MUST be validated against the
  closed vocabulary `direct`, `scale`, `table`; a value outside it is rejected naming the value
  and the closed set.
- **FR-005**: Any `damage_type` value appearing anywhere in the file MUST be validated against the
  closed four-value vocabulary already used by `check_bestiary.py`/`check_gear.py` (`slashing`,
  `piercing`, `blunt`, `searing`, docs/adr/0022).
- **FR-006**: `version` MUST be validated as a positive integer (matching the documented "bump on
  any change" contract) — a non-integer or non-positive value is rejected.
- **FR-007**: `drop` and `manual`, when present, MUST be validated as lists of strings.
- **FR-008**: `rename`, when present, MUST be validated as a mapping of string to string.
- **FR-009**: The checker MUST report every problem found in one run, not stop at the first, and
  each message MUST name the offending field and file.
- **FR-010**: A standalone command-line script `tools/check_conversion.py` MUST be provided,
  mirroring `check_bestiary.py`/`check_gear.py`'s CLI shape (`<path>...`, `--format text|json`,
  exit 0 on success, non-zero with problems printed on failure).
- **FR-011**: Performing an actual conversion, and per-entity `converted: {rules, on}` provenance
  stamping, are explicitly out of scope (chronicle-state / on-demand-conversion concerns, not
  setting-authoring validation).

### Key Entities

- **Conversion table** (`conversion.yaml`): `from`, `version`, `skills`, `difficulty`, `damage`,
  `armour`, `danger`, `rename`, `arcs`, `drop`, `drop_note`, `manual` — the full schema documented
  in `docs/design/24-authoring-a-setting.md`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A `conversion.yaml` matching the documented worked example validates cleanly, with
  no false rejection.
- **SC-002**: A `conversion.yaml` missing `from` or `version` is rejected with an error naming the
  specific key.
- **SC-003**: A `damage_type` outside the closed four is rejected, naming the offending value.
- **SC-004**: The script's usage is documented in `docs/design/24-authoring-a-setting.md` the same
  way `check_bestiary.py`/`check_gear.py` already are referenced there.

## Assumptions

- The schema validated is exactly the one shown in `docs/design/24-authoring-a-setting.md`'s
  worked example — this feature does not invent new conversion.yaml fields.
- `difficulty.map`, `damage`, `arcs` sections are free-form mappings whose values are not
  cross-checked against the engine's own skill/arc-scale vocabulary — that would require reading
  a compiled setting rather than a standalone file, which is out of scope (same boundary
  `check_gear.py` draws around `availability`).
