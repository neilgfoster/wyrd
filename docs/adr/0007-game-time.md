# ADR 0007 — Game time is independent of real time

**Status:** accepted 2026-08-21

## Context

Wyrd is built for sessions weeks apart. The world is supposed to move while the player is
not looking. It is tempting — and was, briefly, the design — to advance the world by the
**real** time elapsed between sessions.

## Decision

**Game time advances only when the fiction advances it.** Real-world gaps are irrelevant to
the world clock ([`../18-campaign.md`](../design/19-campaign.md)).

What moves it: a summarised beat covering a span, narrated travel, an explicit wait,
downtime, or an implied gap between arcs. **Nothing else — and closing a session advances
nothing.**

Threats still act unobserved, but across spans of *game* time the character did not witness.
That is what `world_acts_offstage` controls.

## Alternatives rejected

**Advancing the world by real elapsed time.** It sounds evocative — come back after a
fortnight and find the world changed — and it is wrong in a way that breaks the format
outright.

If a beat ends with a character in a cellar with a blade drawn, and the player returns three
weeks later, **no game time has passed**. They are still in the cellar. A wall-clock world
would age the world three weeks between two consecutive heartbeats, and every mid-scene
stop — which the whole session design encourages — would corrupt the fiction.

The inverse also holds and is easy to miss: two beats played back to back in one sitting may
sit a season apart, if downtime separates them. Neither direction survives a clock tied to
the wall.

## Consequences

- The expected-value abstraction survives intact — it just operates over spans of game time,
  and `advance-time` is called when the fiction says time passed, not at session start.
- Returning after a long absence is a **recap** problem, not a world-clock one. The
  `pending:` marker restores the exact moment if the session stopped mid-beat.
- The session loop's second step became orientation rather than simulation.

> The player's absence is a fact about the player, not about the world.
