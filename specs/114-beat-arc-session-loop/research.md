# Phase 0 Research: Beat/arc structure and the session loop

No unresolved `NEEDS CLARIFICATION` markers were left in spec.md, so this phase confirms the
technical approach against existing code rather than resolving open unknowns.

## Decision: reuse `wyrd.entity`'s containment primitives, don't duplicate them

**Rationale**: `engine/wyrd/entity.py` already implements the containment tree (`parent`,
`children_of`, `check_containment` for cycles) and already places `arc` in `RECURSIVE_TYPES` while
leaving `beat` out of it. That is the *shape* of "arcs organise, beats are played" — this feature
adds the missing *enforcement* (rejecting a child assigned to a beat) and the play-time layer
(mode, loop, pending marker, shape) on top, rather than re-deriving containment from scratch.

**Alternatives considered**: A second, session-scoped containment structure independent of the
entity graph. Rejected — `docs/design/25-entities.md`/#296 already established the entity file
format as the one containment mechanism (spec.md FR-013 makes this explicit), and a second
mechanism would immediately create the "two documents describing one thing differently" fault
class `CLAUDE.md` calls out.

## Decision: `mode` is recorded on a resolution/narration record, not on the beat entity

**Rationale**: spec.md User Story 2 requires the same beat definition to be played in one context
and summarised in another with zero shared mutable state. Storing `mode` as a frontmatter field on
the beat entity itself would violate that (one entity, one `mode` value). Instead, `mode` is a
field on the record produced by `narrate_beat()`, addressed by (beat id, chronicle) rather than
living on the beat's own frontmatter.

**Alternatives considered**: A `mode` field on the beat entity, overwritten per narration.
Rejected outright by acceptance scenario 2 in User Story 2 (two chronicles narrating the same beat
definition independently).

## Decision: the six loop steps are represented as an explicit state machine, not free-form calls

**Rationale**: FR-005 requires orient to complete before recap begins, and FR-007 requires close to
run exactly once. A plain sequence of function calls the caller is trusted to order correctly
would not be "engine-checkable" per spec.md's own phrasing. A small ordered-step enum/state value
with a `next_step()`-style transition function that rejects an out-of-order call gives the
guarantee mechanically, matching the pattern `wyrd.combat` already uses for turn sequencing
(referenced in `docs/design/13-combat-sequencing.md`/ADR 0018).

**Alternatives considered**: Leaving ordering as a documentation-only convention. Rejected — this
is exactly the "stale but plausible specification" fault class; a convention nothing checks drifts
silently.

## Decision: session shape classification is a pure function over recorded session facts

**Rationale**: FR-011/FR-012 require a shape (single beat/interlude/downtime/extended) to be
computable without ever leaking into player-facing text. A pure function taking the session's beat
count, whether any beat used dice, and whether a downtime phase occurred, returning one of the
four shape labels, keeps the classification fully separate from any narration string — nothing
narration-producing ever imports or calls it.

**Alternatives considered**: Tagging each beat with its shape as it's played. Rejected — shape is
a property of the whole session read after (or provisionally during) the fact, not a per-beat
field; tagging individual beats invites exactly the kind of leak FR-012 forbids.
