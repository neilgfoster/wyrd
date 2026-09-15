# Phase 1 Data Model: The /wyrd-play skill

This feature introduces no new persisted schema -- every entity below already exists in the
engine (docs/design/22-state.md, docs/design/25-entities.md) and in the four sibling skills'
own documented shapes. This document exists to state, for this skill specifically, which fields
it reads and which it may write.

## Chronicle state (`chronicle.yaml`)

Read at the start of every invocation (via `session-context`'s implicit load, and directly for
the `pending` field); written at the end of every invocation (via `save`).

| Field | Read | Written | Notes |
|---|---|---|---|
| `pending` | yes | yes | `null` when no mid-beat stop is outstanding; otherwise `{beat, awaiting, rolled}` (docs/design/16-session.md, specs/122-chronicle-yaml-schema). This skill resumes exactly `pending.awaiting` if set, and sets it itself if the player must stop before the current action resolves. |
| `calendar` | yes | yes, only if `advance-time` was called | Unchanged unless the beat itself involved elapsed time. |
| `sessions` | yes | no | Not incremented by this skill -- session counting is `/wyrd-end-session`'s own concern. |

## Player character (`pc.yaml`, via `session-context`'s `player_character`)

Read-only from this skill's perspective except through a committed proposal's own mutation or a
`track`/`rally` call's own returned value, which this skill then writes back via `character-save`
or the chronicle-level `save`, exactly as `wyrd-downtime`/`wyrd-character` already do for their
own scope. No field is computed by this skill itself.

## Companion (`session-context`'s `companions`, `status: with-party` only)

Read-only. A companion not present (`status` other than `with-party`) is outside this skill's
always-loaded set and is not consulted for the beat's mechanical resolution (FR-015) -- though
the GM's own prose may still reference an absent companion's ongoing agenda, since that is a
narrative judgment call, not a mechanical one.

## Thread (`session-context`'s `threads`, `heat >= 3`)

Read-only. Available to ground the orientation narration; never mutated directly by this skill
(a thread's own state changes, if any, happen through whatever mechanic the beat calls for --
e.g. a `track` change on the thread's own `heat`, if the setting models it that way -- and
would be a targeted, explicit action by the GM's own judgment, not something `/wyrd-play`
does automatically every invocation).

## Beat (conceptual; not a separate file)

Not a persisted record of its own -- a beat is the atomic unit of play this skill runs one of
per invocation (docs/design/16-session.md). Its outcome is entirely represented by whatever
`chronicle.yaml`/`pc.yaml`/entity mutations the beat's own resolution steps produced, plus (at
a clean close) the Rally's own recovery values.

## Proposal (`resolution.py`'s in-memory `proposal_id`)

Not persisted to disk at all -- exists only between a `propose` call and its matching
`commit`/`discard` within the same invocation. This skill never treats a proposal's staged
mutation as applied, or narrates it as having happened, before the matching `commit` succeeds
(FR-009).
