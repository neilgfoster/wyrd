# Phase 1 Data Model: The Rally: recovery, advance award and commit

## Character Strain/Stamina (existing fields, `wyrd.character`)

Already defined by `engine/wyrd/character.py`'s `PLAYER_CHARACTER_FIELDS` (`stamina`, `strain`)
and `docs/design/22-state.md`. This feature adds no new frontmatter fields to the character
entity itself -- it computes new values for the existing `stamina`/`strain` fields (and reads the
existing `stamina_max`, held by the caller the way `advancement.py` already reads it, e.g.
`creation.py`'s `{"current": ..., "max": ...}` shape or a plain `stamina_max` int passed by the
caller). This feature's functions take the current values as plain arguments and return the
recovered values; writing them back onto the character record is the caller's job, the same
division `advancement.py`'s own functions already use.

## Rally recovery result (NEW, not an entity)

Produced by applying a Rally's fixed recovery step.

| Field | Type | Notes |
|---|---|---|
| `strain` | int | input Strain minus 1, floored at 0 |
| `stamina` | int | input Stamina plus 1, capped at `stamina_max` |

## Rally award outcome (NEW, not an entity -- wraps `advancement.award_advance`'s own result)

Produced only when a trigger is claimed; absent (or `None`) when no award is claimed
(FR-002/FR-003).

| Field | Type | Notes |
|---|---|---|
| `awarded` | bool | exactly `advancement.award_advance`'s own `awarded` field, unchanged |
| `trigger` | str | present when `awarded` is `True` |
| `refusal` | str | one of `award_advance`'s existing refusal reasons, present when `awarded` is `False` |
| `error` | str | `award_advance`'s own message, present when `awarded` is `False` |
| `record` | dict | the updated (or unchanged, on refusal) advancement record -- exactly `award_advance`'s own `record` |

This feature introduces no new refusal reason and no new field beyond what `award_advance` already
returns -- FR-006 requires the refusal to be surfaced, not reshaped.

## Rally result (NEW, the function's overall return value)

| Field | Type | Notes |
|---|---|---|
| `strain` | int | from the recovery result above |
| `stamina` | int | from the recovery result above |
| `award` | dict \| None | the Rally award outcome above, or `None` if no trigger was claimed |

Composing this from the recovery result and (optional) award outcome, rather than a flat dict, is
what keeps "a Rally with no award is a valid outcome" (User Story 2) structurally obvious to a
caller -- `award` is `None`, not a set of empty/zeroed award fields that could be mistaken for a
refused award.

## Persist/commit step (NEW, no stored state of its own)

Not a data structure -- a function that takes the Rally result above and a caller-supplied
zero-argument callable (or `None`), and calls that callable exactly once, after the recovery and
award above are both computed (FR-004/FR-005). This module implements no state of its own here;
it only guarantees the ordering and exactly-once property, the same division
`wyrd.session.run_close` already uses for its own three sub-steps.
