# Phase 0 Research: The Aftermath table and wound records

No open unknowns — the spec's Assumptions section already resolved every implementation-detail
question a research pass would otherwise raise. Recorded here for completeness.

## Decision: reuse `_stage_critical`'s staging shape for `_stage_aftermath`

**Rationale**: `resolution.py` already establishes the pattern a table-roll staging function
follows — roll dice, look up the total against a row table, build zero-or-one wound mutations,
append a `steps` entry recording `mechanic`, `roll` (with `roll`/`modifier`/`total`/`table`/`key`),
and `mutations`. Aftermath is structurally the same shape (one roll, one table, zero-or-one wound
mutation) with a different die (`d100` vs `1d6`), a different modifier source (`points_below_zero`
directly, already ×5 per the design doc, vs raw `points_below_zero`), and more rows.

**Alternatives considered**: A wholly separate module for post-fight resolution. Rejected — one
table and one function does not warrant a new module, and splitting the row-table pattern across
two files would make the next reader compare two places instead of one for what is the same kind
of thing (`04-tables.md`'s own family convention).

## Decision: wound `id` generation

**Rationale**: `_stage_critical` already generates `f"critical-{step_id}"` for its wound records
— a simple, stable-within-the-proposal scheme. `_stage_aftermath` follows the same convention:
`f"aftermath-{step_id}"`. This satisfies `validate_wound`'s only requirement on `id` (present,
namespaced by table) without inventing a new generation scheme the codebase doesn't already use
elsewhere.

## Decision: `bears_on` source for the `recurring-wound` row

**Rationale**: `_stage_critical` already takes `bears_on_skill` as an explicit parameter from its
caller (the combat-resolution code that knows which skill the blow bears on) rather than deriving
it internally. `_stage_aftermath` takes the same parameter for the same reason — this is combat
context the resolution stage owns, not something the table-lookup function should infer.

## Decision: `beat` value

**Rationale**: Docs/design/06-aftermath.md's own example JSON (`{"beat": 412, ...}`) shows `beat`
as a caller-supplied field on the recorded roll, not a Aftermath-table concept. `_stage_aftermath`
accepts `depends_on_step`/`step_id` exactly as `_stage_critical` does; the wound record's `from`
field records `{"table": "aftermath", "beat": step_id}`, consistent with how the codebase already
has no separate "beat" counter distinct from proposal step ids (grep confirms no `beat` field
exists elsewhere in `resolution.py`'s staged steps — `step_id` is the closest existing concept and
is what this feature uses).
