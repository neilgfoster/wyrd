# Phase 1 Data Model: Beat/arc structure and the session loop

## Arc (existing entity type, `wyrd.entity`)

Already defined by `docs/design/25-entities.md` / `wyrd.entity`; this feature adds no new fields.
An arc is in `RECURSIVE_TYPES`: its children (found via `children_of`) may be further arcs or
beats. Has entry/exit conditions per the design doc (represented as existing entity fields, not
introduced here).

## Beat (existing entity type, `wyrd.entity`)

Already defined; this feature adds no new frontmatter fields to the beat entity itself. A beat is
not in `RECURSIVE_TYPES`. This feature adds the enforcement step: `check_beat_has_no_children()`
rejects any entity set where a beat has a child, using `entity.children_of` against the loaded
set.

## Beat resolution record (NEW, session-scoped, not an entity)

Produced by narrating a beat once. Not itself an entity file — it lives in per-chronicle session
state (alongside the pending marker, below).

| Field | Type | Notes |
|---|---|---|
| `beat_id` | str | the narrated beat's entity id |
| `mode` | `"played"` \| `"summarised"` | set once, at narration time; never inferred from the beat's own definition |
| `resolved_at` | timestamp/step marker | for ordering within a session |

Independence requirement (User Story 2, SC-002): two resolution records for the same `beat_id`
across different chronicles/sessions share no mutable state — each is a fresh record.

## Session loop state (NEW)

A small state machine tracking where the current session sits in the six-step loop.

| Field | Type | Notes |
|---|---|---|
| `step` | one of `load`, `orient`, `recap`, `beat`, `close` | `repeat` is not a distinct step value — it is "return to `beat`" |
| `elapsed_applied` | bool | set `True` once orient has run; recap is only reachable once this is `True` |
| `beats_this_session` | list[str] | beat ids resolved so far, in order |
| `closed` | bool | set `True` once close has completed; guards against running close twice |

Transition rule (FR-005/FR-006/FR-007): `step` may only advance
`load → orient → recap → (beat → (beat | close) | close)`; attempting `recap` before
`elapsed_applied` is `True` is rejected. `recap → close` is legal directly, because FR-006
permits a session with zero beats. Moving to `beat` requires a beat id, which is appended to
`beats_this_session` — this is the only way that list is populated, so nothing can add to it
without going through the checked transition. `close` is a terminal step — no further transition
is valid after it, matching FR-007's exactly-once requirement. Close's own three sub-steps
(compaction, recap regeneration, commit) are sequenced by `run_close`, which takes them as
caller-supplied callables rather than implementing them — see `contracts/session_module.md`'s
Non-goals.

## Pending marker (NEW, per-chronicle state)

| Field | Type | Notes |
|---|---|---|
| `beat_id` | str | which beat was interrupted |
| `action` | str | free-text/structured description of the specific unresolved action |
| `set_at` | timestamp/step marker | when the interruption happened |

Written only when a session stops with `step == "beat"` and the current beat has not resolved
(FR-008): the caller builds the marker via `set_pending` and stores it in the chronicle's own
per-session state (this module holds no state of its own). Cleared when that beat resolves
cleanly on resumption (FR-010): the caller replaces the stored marker with `clear_pending()`'s
result. At most one pending marker exists per chronicle at a time — a beat cannot itself contain
a nested unresolved beat per the containment rule above.

## Session shape (NEW, computed, not stored on any entity)

One of `single_beat`, `interlude`, `downtime`, `extended` — returned by a pure function of the
session's own recorded facts (beat count, whether any beat used dice, whether a downtime phase
ran). Never written into a resolution record consumed by narration, and never appears in a
narration string (FR-012).
