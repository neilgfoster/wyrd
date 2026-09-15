# Phase 0 Research: The /wyrd-play skill

No `NEEDS CLARIFICATION` markers remained in the Technical Context after drafting -- this
section records the decisions made while resolving choices that had more than one reasonable
shape, plus the conventions read from prior art rather than invented fresh.

## Decision: one beat per invocation, not an internal multi-beat loop

**Rationale**: docs/design/16-session.md's session loop step 5 ("REPEAT until the player
stops") describes a *session*, which in a Claude Code skill context maps naturally onto a
sequence of separate `/wyrd-play` invocations rather than one invocation looping internally
over several beats. The four existing sibling skills (`wyrd-character`, `wyrd-downtime`,
`wyrd-end-session`, `wyrd-bootstrap`) are each single-purpose, single-invocation skills with no
internal repeat loop of their own; matching that shape keeps `/wyrd-play` consistent with its
siblings and keeps each invocation's scope (and its persisted state) easy to reason about.

**Alternatives considered**: An internal loop that keeps running beats until the player says
"stop" was considered, since it maps more literally onto 16-session.md's wording. Rejected
because a Claude Code skill invocation is itself the natural unit of "the player asked for
something and got an answer" -- looping silently across multiple beats inside one invocation
would make the Rally's "clean stopping point... always accept `stop` there" harder to honour
predictably, and would risk running further than the player wanted before the skill next
checks in.

## Decision: locate the engine CLI the same way the sibling skills do

**Rationale**: All four existing skills use the identical snippet:

```bash
WYRD_PKG_DIR=$(find engine -maxdepth 4 -type d -name wyrd | head -1)
PYTHONPATH="$(dirname "$WYRD_PKG_DIR")" python3 -m wyrd.client <verb> [--flags]
```

Reusing it verbatim keeps `/wyrd-play` locatable and callable the same way as its siblings, and
avoids inventing a second convention for the same problem (CLAUDE.md's recurring-fault class 3:
two documents/skills describing one thing differently).

**Alternatives considered**: A fixed relative path (`engine/wyrd`) was rejected, matching the
sibling skills' own stated reason -- bootstrap's clone may nest the package one level deeper
than expected, so a dynamic `find` is the only version that has actually been shown to work.

## Decision: verbs called, and what they resolve

Read from `docs/design/02-architecture.md`'s CLI list and `engine/wyrd/catalog.py`/`client.py`
(the same source the four sibling skills' own citations draw from):

| Step | Verb(s) | Notes |
|---|---|---|
| Load Always-loaded tier | `session-context` | One call; returns player character, with-party companions, `heat >= 3` threads, `recap.md` text, and the engine contract text. |
| Resume a mid-beat stop | (read `chronicle.yaml`'s `pending` field, already returned as part of chronicle state) | No separate verb; `pending` is a field on chronicle state (docs/design/16-session.md, `wyrd.chronicle`'s schema), read/written via `save`. |
| A skill test with no NPC opposition | `propose` (`mechanic=ordinary-test`) → `commit` or `discard` | `propose` stages; nothing is written until `commit`. |
| Combat / an opposed roll against an NPC | `opposed-test`, or `propose` (`mechanic=combat-attack`) → `commit`/`discard` | `opposed-test` is used when only a single acting-side roll is needed and there's no combat-attack cascade to stage; `combat-attack` is used for the full attack/damage/armour/critical chain. |
| A declared specific/leveraging/brief/against-nature/removes-risk detail | `declaration-bonus --category <c>` | Looked up, never invented from length (docs/design/01-principles.md). |
| A track mutation outside `propose`'s own cascade | `track --value V --mechanism M --delta D` | Used for a state change a beat calls for directly (e.g. adjusting Standing narratively), not already staged by a `propose` cascade. |
| Elapsed time within a beat (a journey, a wait) | `advance-time <days>` | Also resolves threat expected-value activation across the span. |
| An on-demand threat activation roll | `threat-check <id>` | Used when the fiction calls for checking one threat's activation on demand, distinct from `advance-time`'s automatic sweep. |
| Ending a beat cleanly | `rally --strain 1 --stamina 1 --stamina-max <M> --advancement-record-json <...>` | Fixed recovery; discards any leftover open proposal in `pending.rolled`; optional advance award. Never commits -- persistence is this skill's own `save` step, same convention `wyrd-end-session` documents. |
| Persisting state (clean close, or a `pending` marker) | `save --state-json <...> --chronicle-dir .` | Validates before writing; matches `wyrd-end-session`'s own Step 2 convention exactly. |
| Confirming the chronicle is left valid | `validate --chronicle-dir .` | Read-only; used as this skill's own end-of-invocation check, matching SC-003/FR-012. |

**Alternatives considered**: Reimplementing any of the above arithmetic in the skill's own
prose was considered and rejected outright -- it is exactly the fault
docs/design/02-architecture.md's code/prose split and this issue's own acceptance criteria
forbid ("Every mechanical step... goes through an existing engine verb, never reimplemented in
the skill's own prose logic").

## Decision: no automated test harness; verify via a quickstart walkthrough

**Rationale**: A Claude Code skill's own prose instructions are not unit-testable code; the
engine's `tests/` suite already covers the CLI verbs this skill calls, so the correctness
surface specific to *this* feature is "does the skill call the right verb, in the right order,
narrate only from its result, and leave valid state" -- verified by actually running the skill
against a real bootstrapped chronicle, per the issue's own DoD ("run against a real bootstrapped
chronicle (darkfuture or titan)") and CLAUDE.md's own precedent for skill-shaped features
(#403's own verification demonstrated exactly this).

**Alternatives considered**: A synthetic fixture chronicle was considered for faster iteration,
but the issue's own guidance (and #403's own lesson, referenced by name) is that a synthetic
fixture would miss what a real setting's data exposes -- so the quickstart walkthrough runs
against a real setting (darkfuture or titan) rather than only a fixture.
