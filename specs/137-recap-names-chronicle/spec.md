# Feature Specification: Recap names its chronicle and setting

**Feature Branch**: `137-recap-names-chronicle`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Recap names its chronicle and setting" (issue #363)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The recap says which world this is (Priority: P1)

A session opens, loads a chronicle, and reads its recap. The recap names the chronicle and its
setting explicitly, so a player switching between two live chronicles (design/21-parallel-
chronicles.md: "one on Tuesday and another on Thursday") can never mistake which world they're
reading about — the recap is the diegetic anchor point that says so.

**Why this priority**: docs/design/21-parallel-chronicles.md states this as a GM-contract MUST —
"a session loads exactly one chronicle and one setting, and says which in the recap" — and it is
currently unmet: `generate_recap` accepts a `chronicle` parameter and explicitly discards it.

**Independent Test**: given two chronicle dicts with different `name`/`setting.repo` values but
otherwise identical entity data, confirm their generated recaps are textually distinguishable by
chronicle/setting name.

**Acceptance Scenarios**:

1. **Given** a chronicle dict with `name: "the-drowned-chronicle"` and
   `setting: {repo: "my-setting"}`, **When** a recap is generated, **Then** the recap's text
   includes both `"the-drowned-chronicle"` and `"my-setting"`.
2. **Given** two chronicles differing only in `name`, **When** each generates a recap from
   otherwise-identical entity data, **Then** the two recaps differ in exactly the text naming
   the chronicle.
3. **Given** an empty or minimal chronicle dict (missing `name`/`setting`), **When** a recap is
   generated, **Then** it still produces a well-formed recap with a placeholder in place of the
   missing name(s), rather than raising.

### Edge Cases

- A chronicle dict with `name` but no `setting` (or vice versa) reports the one it has and a
  placeholder for the one it doesn't — never an error, matching `generate_recap`'s existing
  fallback-to-placeholder convention for `where`/`changes`/`body_mind`.
- The existing recap sections (Where and when, Hottest threads, What changed, Body and mind,
  Who's present) and their existing tests are unaffected — this feature adds a new section, it
  does not restructure the existing ones.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `generate_recap` MUST include the chronicle's `name` (from the `chronicle` dict
  it already accepts) in its output when present.
- **FR-002**: `generate_recap` MUST include the chronicle's setting (`chronicle["setting"]["repo"]`)
  in its output when present.
- **FR-003**: A missing `name` or `setting` MUST fall back to the existing placeholder
  convention (`_RECAP_PLACEHOLDER`), never raise.
- **FR-004**: The existing recap sections and their word-count/placeholder behaviour MUST be
  unaffected — this is an additive section, not a restructuring.

### Key Entities

- **`chronicle`** (already accepted by `generate_recap`, previously discarded): read here only
  for `name` and `setting.repo`, both already part of `state.default_chronicle_state`'s shape
  (#325) — no schema change.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A generated recap always names its chronicle and setting when the chronicle dict
  carries them — verified by exact-input tests, not eyeballed.
- **SC-002**: Two recaps built from chronicles differing only in `name`/`setting` are
  distinguishable by that difference alone.
- **SC-003**: Every pre-existing `test_loadtier.py::GenerateRecapTest` case continues to pass
  unchanged (regression safety for the existing sections).

## Assumptions

- This feature only reads `chronicle["name"]`/`chronicle["setting"]["repo"]` — it does not read
  or depend on any other chronicle field (`calendar`, `era`, etc.); `generate_recap`'s own
  docstring already reserves `chronicle` for "calendar/session context a future caller may add",
  and this feature is the first concrete use of that reservation.
- No schema change to `chronicle.yaml` — `name`/`setting.repo` already exist in
  `state.default_chronicle_state`'s shape (#325); this feature only starts reading fields that
  already exist.
