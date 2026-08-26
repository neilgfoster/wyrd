# Research: Journeys as a subsystem

No `NEEDS CLARIFICATION` markers remained after the clarify pass — both load-bearing unknowns
(hazard trigger formula, leg mode ownership) were resolved there and are recorded in
`spec.md`'s Clarifications section. This document records the remaining design research: how
the existing mechanisms this feature reuses actually work, verified against source rather than
recalled.

## Decision: journeys are `scale: journey` arcs

**Rationale**: `design/15-arcs-and-beats.md` already generalises containment recursively —
"arcs contain arcs... at every level" — and arcs already carry a `scale` field (the existing
example uses `scale: adventure`). A journey needing no new containment shape, only two extra
fields (pace, hazard rating) and a recognised scale value, is the smallest change that satisfies
FR-001.

**Alternatives considered**: A dedicated `type: journey` entity distinct from `arc`/`beat` was
rejected — it would need its own selection/conversion logic duplicating what
`15-arcs-and-beats.md` already provides for arcs, and would not compose with lazy conversion
(User Story 3) without extra work.

## Decision: hazard trigger reuses the Threat activation formula

**Rationale** (clarified 2026-08-26): `design/05-campaign.md` defines Threat activation as
`d100 ≤ imminence × 10`, rolled per game-week. A journey leg is the travel-subsystem's
equivalent unit of time, so the same formula shape (`d100 ≤ hazard_rating × 10`, rolled per
leg) gives the engine one "does this recur" mechanic instead of two to keep consistent. Worked
example: `hazard_rating: 4` → 40% chance per leg, directly comparable to a Threat at imminence 4
(also 40%, but per week) — same shape, different unit, which is exactly the point: a GM who
already understands Threat activation understands hazard activation with no new rule to learn.

**Alternatives considered**: Scaling by the danger-rating curve (ADR 0024) was considered and
rejected — that curve answers "how tough is this fight for this party," a different question
from "how often does travel interrupt itself," and reusing it would imply a relationship
between combat difficulty and hazard frequency the design never claims. A per-entry fixed
percentage (no shared formula) was rejected as the CLAUDE.md-flagged pattern of reinventing an
existing mechanic instead of reusing one.

## Decision: leg resolution reuses the existing `mode:` field

**Rationale** (clarified 2026-08-26): `15-arcs-and-beats.md`'s beat frontmatter already has
`mode: played | summarised`. A journey leg is either an arc or a beat (per the decision above),
so it already has this field available — declaring it at authoring time (or at lazy-conversion
time, per User Story 3) needs no new mechanism, only the convention that a journey's legs use
it consistently.

**Alternatives considered**: A GM-judgment runtime rule was rejected because it produces the
recurring accreted-inconsistency fault CLAUDE.md's fault list names (fault class 3 — two
descriptions of "how does play advance" that could silently drift). "Played only when a hazard
triggers" was rejected because it makes the mode a side effect of the dice rather than an
authored choice, which breaks User Story 3's "converts the same way any other arc does."

## Decision: no new setting-facing schema or validator

**Rationale**: Unlike `gear.yaml`/`bestiary.yaml` (fixed catalogues, hence a schema and a
`tools/check_*.py` validator per ADR 0033's precedent), journey/leg fields live inside arc/beat
frontmatter, which `15-arcs-and-beats.md` already documents in prose rather than as a validated
schema. Adding a schema validator here would be new scope the issue doesn't ask for (the issue
asks for the subsystem to be specified and playable, not for tooling), and there is no existing
per-arc validator this would extend consistently.

**Alternatives considered**: A `journeys.yaml` catalogue file (mirroring `gear.yaml`) was
considered and rejected — journeys are played content (arcs/beats), not a lookup table of
static items; forcing them into a flat catalogue would fight the arc/beat recursion this
feature is built to reuse.

## Decision: travel roles are undefined mechanically

**Rationale**: The issue's scope line says "Specify roles, hazards, pace and supply, **or
whichever subset survives the anti-logistics rule**" — an explicit invitation to drop a piece
if it doesn't earn its place. Giving roles mechanical teeth (bonuses, requirements) would be
new engine behaviour with no existing precedent to reuse, unlike hazards (reuses Threat) and
mode (reuses the beat field). Carrying the role as a data slot only keeps the engine
setting-agnostic (`CLAUDE.md`) — a setting's `rename:`/configuration layer decides what
"navigator" does, the same way the engine carries skill names without defining what any skill
means beyond its percentile.

**Alternatives considered**: Defining a fixed role list with fixed effects (e.g. "forager rolls
Survival for supply") was rejected as inventing a new resolution shape parallel to the ordinary
skill test, and as baking setting-specific assumptions (what skills exist, what "supply" costs)
into the engine, which `03b-the-character.md` explicitly reserves for the setting.
