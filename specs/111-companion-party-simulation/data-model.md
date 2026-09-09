# Phase 1 Data Model: Companion and party simulation engine support

## Companion

A `character` entity (`state.py`'s entity frontmatter/body shape), `role: companion`.

**Narrative layer** — free text, never read by a resolution rule:

| Field | Type | Notes |
|---|---|---|
| `objective.wants` | string | what this companion is actually here for |
| `objective.next_step` | string | what they will do about it next |
| `flaw` | string | the thing that gets them into trouble |
| `secret` | string | something the player does not know |
| `arc` | string | the choice this companion is heading toward |

**Mechanical layer** — closed at exactly five fields (`tools/check_companion_layers.py` enforces
this against the design document; this feature does not change that set):

| Field | Type | Notes |
|---|---|---|
| `career` | string (career id) | bounds skill % as for the player character |
| `bond` | integer, -3..+3 | toward the player character |
| `taint` | integer | same terms as the player character's own |
| `strain` | integer | same terms as the player character's own |
| `wounds` | list of wound entries | same Aftermath table/rows as the player character |

**Validation rules** (FR-001, FR-002):
- The mechanical layer MUST contain all five fields and no others.
- `bond` MUST be an integer in `[-3, 3]`.
- A validation failure names the specific missing/extra field.

## Party

Not a separate entity file — the current set of companion entities plus the player character,
assembled on read (per research.md's decision). Bounded at 5 companions (FR-011).

| Concept | Representation |
|---|---|
| Membership | the set of companion entity files currently marked `status: with-party` |
| Tension | a single integer, 0-6, held on chronicle state (`state.py`'s state dict), not per-companion |

## Loyalty relation table

A setting-supplied mapping, passed as a parameter (research.md), from an unordered pair of
Loyalty ids to a relation:

```text
{("loyalty-a", "loyalty-b"): "strained", ("loyalty-c", "loyalty-d"): "irreconcilable"}
```

Any pair absent from the table is "undeclared" (no effect) — the stated default (FR-007). Lookup
is symmetric: `(a, b)` and `(b, a)` resolve identically.

## State transitions

- **Tension increment**: `base_delta` (the event's stated Tension addition) →
  optionally doubled if a `strained` pairing is present in the party (FR-009) →
  optionally offset by the named companion's `bond` (FR-003/FR-004) →
  applied to the current Tension, clamped so that reaching or exceeding 6 resolves as a break and
  resets Tension to 0 (FR-005).
- **Tension decrement**: -1 at downtime, -1 when a beat is spent on a companion's problem, floored
  at 0 (FR-006).
- **Loyalty change**: on any character's Loyalty changing, re-check all pairings in the current
  party; an existing pairing that becomes `irreconcilable` triggers an immediate Tension break
  (FR-010), independent of the current Tension value.
- **Join attempt**: refused outright if it would introduce an `irreconcilable` pairing (FR-008);
  refused if the party is already at 5 companions (FR-011); otherwise admitted.
