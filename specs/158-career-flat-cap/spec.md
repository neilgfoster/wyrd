# Feature Specification: Career skill cap is one flat value, not a per-skill dict

**Feature Branch**: `158-career-flat-cap`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "career.py treats a career's skills list as a per-skill cap dict, contradicting the flat 70% rule" (GitHub issue #411)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create a character against a real setting's careers.yaml (Priority: P1)

A person running `create-character` against any currently-authored setting (its careers.yaml
listing each career's `skills` as a plain list of names) can allocate their starting 8 advances
and finish creation without the engine raising an unhandled error.

**Why this priority**: This is the defect reported in #411 — character creation is broken
end-to-end against every real setting today. Nothing else in this spec matters if this doesn't
work.

**Independent Test**: Load a real career entry from wyrd-setting-darkfuture's or
wyrd-setting-titan's actual `careers.yaml`, and validate an 8-advance allocation against it via
`career.validate_allocation`. Succeeds (or fails for a legitimate rule reason) without a
`TypeError`.

**Acceptance Scenarios**:

1. **Given** a career whose `skills` field is a list of skill names (the real, documented shape),
   **When** a caller asks what cap binds one of those skills, **Then** the engine returns the
   single flat cap value (70%) rather than raising a `TypeError`.
2. **Given** the same career and an ancestry that also grants one of its skills,
   **When** a caller asks what cap binds that skill, **Then** the engine returns the same flat cap
   value regardless of which of the two grants it (there is only one cap value in the whole
   system, so there is nothing left to compare).

---

### User Story 2 - Spend an advance to raise or open a skill mid-chronicle (Priority: P2)

A person running `spend-advance`'s `raise`/`open`/`change_career` path against a real career (the
same list-of-names shape) can spend an advance without the shared `career.py` helpers raising a
`TypeError`.

**Why this priority**: `advancement.py` shares the same broken helpers, so the defect blocks
ongoing play, not just character creation.

**Independent Test**: Call `advancement.py`'s advance-spending entry points with a real career
entry and confirm they succeed or fail for legitimate rule reasons only.

**Acceptance Scenarios**:

1. **Given** a character who has opened every skill a career grants at the flat cap,
   **When** the engine checks whether that career is complete, **Then** it reports complete and
   pays the completion's Stamina and Mark exactly once.
2. **Given** a character who is short of the flat cap on at least one granted skill,
   **When** the engine checks whether that career is complete, **Then** it reports not complete.

### Edge Cases

- A career whose `skills` list is empty grants nothing and can never be complete (existing
  `career_complete` behavior for the empty case is preserved).
- A skill granted by neither the career nor the ancestry still has no effective cap (`None`),
  exactly as before.
- A skill granted by both the career and an ancestry has exactly one flat cap value now, so there
  is no "higher of the two" case left to resolve — asking for the cap simply confirms the skill is
  granted and returns that one value.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST treat a career's (and an ancestry's) `skills` field as a plain list
  of skill names, never as a dict mapping skill name to a numeric cap.
- **FR-002**: `effective_cap` MUST return one flat cap value (the documented 70%) for any skill
  named in the career's or ancestry's `skills` list, and `None` for a skill named in neither.
- **FR-003**: The flat cap value MUST be a single named constant defined in `rules.py`, not a
  magic number repeated at each call site.
- **FR-004**: `career_complete` MUST report a career complete only when every skill it grants (per
  its list) is at or above the flat cap, exactly preserving its existing empty-grant-list handling
  (never complete) and its existing above-cap handling (still counts as complete).
- **FR-005**: `effective_cap`'s docstring MUST no longer describe returning "the higher" of two
  differing per-skill caps, since there is only one cap value in the system once this fix lands.
- **FR-006**: Every existing automated test that exercises these helpers with a synthetic
  `{skill: cap}`-dict fixture MUST be updated to use the real, documented list-of-names shape, so
  a future regression of this exact class is not masked again.
- **FR-007**: At least one automated test MUST exercise these helpers against a career entry
  loaded from a real setting repository's actual `careers.yaml` (not a hand-rolled fixture).

### Key Entities

- **Career**: A dict with (at minimum) an `id`, an `entry`/`prerequisites` shape, and a `skills`
  field that is a list of skill names it grants.
- **Ancestry**: A dict with a `skills` field of the same list-of-names shape, optionally widening
  which skills a character may spend advances on during creation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `create-character` completes an 8-advance allocation against every entry career in
  both wyrd-setting-darkfuture's and wyrd-setting-titan's real `careers.yaml` without raising a
  `TypeError`.
- **SC-002**: 100% of this module's existing tests pass after being updated to the real fixture
  shape, plus the new real-setting-data regression test.
- **SC-003**: The flat cap value appears exactly once as a literal number in the codebase (the
  `rules.py` constant definition) rather than being repeated at each call site.

## Assumptions

- The flat cap value is 70%, per docs/design/03-rules.md section 6 ("Every career caps its skills
  at 70%"), and this spec does not revisit that figure — it only fixes how `career.py` applies it.
- `docs/design/24-authoring-a-setting.md`'s `careers.yaml` schema (list of skill names) is the
  correct, current schema; `career.py` is what must change to match it, not the other way round.
- No other module besides `career.py` and `advancement.py` depends on the old per-skill-cap dict
  shape (confirmed by reading both files in full during specification).
