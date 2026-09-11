# Feature Specification: Holdings: accumulated stakes

**Feature Branch**: `129-holdings-personal-stakes`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Holdings: accumulated stakes" (issue #337)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Threat against a held entity is flagged personal, with no GM invention (Priority: P1)

A threat to a settlement is a problem; a threat to a settlement where the character owns the mill
is *personal* — and the engine should say so directly rather than requiring the GM to remember
which entities the character holds every time a Threat's active set is reviewed
(docs/design/19-campaign.md: "requires no invention on the GM's part to make it so").

**Why this priority**: this is the entire mechanical purpose the design document states for
holdings — "it converts accumulated investment into stakes" — and it is the one piece of that
statement with no existing runtime support: `economy.py` (#276-280) already records and
distinguishes holdings from allegiances as plain id lists; nothing yet connects a held id to an
active Threat.

**Independent Test**: given a list of active Threats (as `threat.active_threats` already
returns) and a character's `holdings` list, confirm each Threat whose entity id appears in
`holdings` is returned flagged as personal, and every other Threat is not.

**Acceptance Scenarios**:

1. **Given** an active Threat whose entity id is in the character's `holdings` list, **When**
   personal stakes are computed, **Then** that Threat is returned flagged `personal: True`.
2. **Given** an active Threat whose entity id is not in `holdings`, **When** personal stakes are
   computed, **Then** that Threat is returned flagged `personal: False` — present, not omitted,
   so a caller can distinguish "checked, not personal" from "not checked at all".
3. **Given** an empty `holdings` list, **When** personal stakes are computed over any Threats,
   **Then** every Threat is flagged `personal: False` — not an error.

### Edge Cases

- A Threat entity carries no `id` field at all — treated the same as "not held" (`personal:
  False`), never an error; matches every other lookup-by-id function in this codebase
  (`threat.py`'s own dict-based convention).
- The same entity id appears twice in `holdings` (a data-quality issue upstream, not this
  feature's concern) — the flag is still simply `True`, since membership, not count, is what
  matters.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a way to annotate a collection of Threats (entity dicts, as
  returned by `threat.active_threats`) with whether each one's entity id appears in a supplied
  `holdings` list.
- **FR-002**: Every Threat passed in MUST be present in the output, each carrying an explicit
  `personal: bool` flag — never silently dropped, and never omitted when not personal.
- **FR-003**: A Threat entity with no `id` field, or an empty `holdings` list, MUST be treated as
  `personal: False`, never raise.

### Key Entities

- **Holding**: already fully implemented (`economy.gain_holding`/`lose_holding`, #276-280, epic
  #216) as a plain `holdings: list[str]` field on a character, kept distinct from `allegiances`
  (docs/design/22-state.md, `character.py`) — this feature adds no new holding mechanism, only
  the read-side connection to Threats the design document calls for.
- **Threat**: as returned by `threat.active_threats` (#334) — an entity dict carrying a `threat`
  block. This feature reads only its `id` field.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every Threat in a mixed list (some held, some not, some with no id) is annotated
  correctly and none is dropped — verified by exact-input tests.
- **SC-002**: An empty `holdings` list never raises and produces `personal: False` for every
  Threat passed in.

## Assumptions

- "Holdings are recorded and distinguishable from allegiances" (this issue's first acceptance
  criterion) is already satisfied by existing, tested code — `economy.gain_holding`/
  `lose_holding` operate on a `holdings` list field kept entirely separate from `allegiances`
  (`character.py`, `creation.py`, `tests/engine/test_economy.py`'s existing
  `test_gaining_a_holding_*`/`test_losing_a_holding_*` coverage) — from #276-280, epic #216. This
  feature adds nothing to that half; it implements only the still-missing "a Threat affecting a
  held entity is flagged as personal" half (this issue's second acceptance criterion).
- This feature is a runtime-logic slice only: plain dicts/lists in, plain dicts out, no I/O —
  matching `threat.py` (#334)'s existing convention exactly. It does not decide *what happens*
  because a Threat is personal (raised stakes in play, GM narration) — only that the fact is
  computed and surfaced, the same separation `journey.py`/`threat.py` already keep between
  mechanical resolution and GM narration.
- "A dwelling, a boat, a workshop, a household, a debt owed to them" (docs/design/19-campaign.md)
  are all represented the same way — an id in `holdings` pointing at whatever entity carries the
  Threat (or would carry one) — no per-holding-type distinction is introduced.
