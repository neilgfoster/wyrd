# Phase 0 Research: Companion and party simulation engine support

No `NEEDS CLARIFICATION` markers remain in the Technical Context — this feature adds no new
dependency, language, or platform choice. The two genuinely open questions were where party-level
state lives and how Loyalty-relation data reaches the engine, both resolved below by precedent
already established elsewhere in `engine/`.

## Decision: companion records are `character` entities; Tension lives on chronicle state

**Rationale**: `docs/design/16-session.md` states plainly: "Each companion is a `character` entity
carrying two layers." `engine/wyrd/state.py` already has a generic `save_entity`/`load_entity` pair
for entity files and a `default_state()` dict for chronicle-scoped state. A companion is one entity
file (`role: companion`, narrative + mechanical layers). Party Tension is a single value shared by
the whole party, not a per-companion field the design ever lists among the closed five — so it
belongs on the chronicle's shared state dict, the same place Fate/Fortune/Dread and other
campaign-scoped counters already live, not duplicated onto every companion file.

**Alternatives considered**:
- *A single "party" entity file bundling all companions.* Rejected: it would fight `state.py`'s
  existing one-entity-per-file convention (already used for the player character and would be used
  for adversaries), and would make `tools/check_companion_layers.py`'s per-companion five-field
  check harder to point at cleanly.
- *Tension stored per-companion, then aggregated on read.* Rejected: `16-session.md` describes
  "a single Tension track," not a per-companion one; storing it five times invites the two-numbers-
  drift fault class `CLAUDE.md` names explicitly.

## Decision: Loyalty-relation data is a setting-supplied parameter, not engine-owned data

**Rationale**: The engine "fixes nothing about what Loyalties exist — a setting declares them"
(`16-session.md`). `engine/wyrd/career.py` already establishes the pattern for exactly this shape
of problem: `find_career`, `change_career_legality`, etc. all take the setting's career list as a
plain parameter (a `list[dict]`) rather than the engine loading or owning setting data itself —
settings are separate, private repos (`CLAUDE.md`: "wyrd-setting-<name>... private where its
sources are"). Loyalty relations follow the same shape: a `strained`/`irreconcilable` relation
table is passed in by the caller (ultimately sourced from the setting) as a parameter to the
relation-lookup function, keyed by an unordered pair of Loyalty ids, with "undeclared" as the
default for any pair absent from the table.

**Alternatives considered**:
- *A fixed engine-side schema/file for Loyalty relations.* Rejected: would make the engine own
  setting content, which `CLAUDE.md`'s setting-agnosticism rule and the existing career-graph
  precedent both forbid.

## Decision: `party.py` is a new module, not an addition to `character.py`

**Rationale**: `character.py`'s own docstring scopes it to "the player-character entity." A
companion is a `character` entity but the concerns this feature adds — Tension arithmetic, Bond
offset, Loyalty gating, party-roster assembly — are party-level, not player-character-level, and
have no player-character analogue. This mirrors how `adversary.py` sits alongside `character.py`
as its own module rather than a branch inside it.

**Alternatives considered**:
- *Extend `character.py` with companion-specific functions.* Rejected: would mix player-character
  and party-simulation concerns in one file, the opposite of the existing one-module-per-domain
  layout `journey.py`/`combat.py`/`economy.py` already establish.

## Resolved unknowns

None remain. All Technical Context fields in `plan.md` are settled by precedent already present in
`engine/wyrd/`.
