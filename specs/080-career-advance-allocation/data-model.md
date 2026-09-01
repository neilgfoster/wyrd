# Phase 1 data model: Career graph and advance allocation

## Career

| Field | Type | Description |
|---|---|---|
| `skills` | dict[str, int] | skill name → cap |
| `entry_point` | bool | whether this career is a legal starting point |

## Ancestry (optional)

| Field | Type | Description |
|---|---|---|
| `skills` | dict[str, int] | skill name → cap; widens eligibility only, never the 8-advance budget |

## Advance action

| Field | Type | Description |
|---|---|---|
| `action` | `"open"` \| `"raise"` | |
| `skill` | str | must be in career∪ancestry's skills |

## Allocation result

| Field | Type | Description |
|---|---|---|
| `valid` | bool | |
| `skills` | dict[str, int] | resulting percentages, present only when `valid` |
| `error` | string | present only when not `valid`; names the specific rule and the skill/total |

Validation order (research.md):
1. Total action count == 8 (FR-004)
2. Distinct `open` actions >= 2 (FR-005)
3. Per action, in sequence: skill in career∪ancestry union (FR-007); `open` not already open
   (FR-008); `raise` only on an already-open skill (FR-009); `raise` never exceeds
   `effective_cap` (FR-006)

`effective_cap(skill) = max(career cap if present, ancestry cap if present)`, `-1` if in
neither (which FR-007's eligibility check already rejects before a cap check would run).
