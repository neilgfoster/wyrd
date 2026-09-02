# Phase 0 Research: Turn order and round structure

No `NEEDS CLARIFICATION` markers — `docs/design/03-rules.md` §2 and ADR 0018 fully specify the
rule; nothing here required a design decision this feature makes for the first time.

## Decision: combat scene state lives under a `combat` key in chronicle state

**Rationale**: `state.py`'s `chronicle_state.yaml` already holds chronicle-scoped, not
per-entity, state (`schema_version`, `last_roll`). A combat scene — who's fighting, whose turn
it started with, what round it's on — is exactly that kind of fact: one per chronicle at a time,
not a property of any single character file. Reusing the existing atomic save/load avoids a
second persistence mechanism.

**Alternatives considered**: storing scene state on one of the participating characters
(rejected — arbitrary and wrong for a scene with more than one participant per side); an
in-memory-only scene, mirroring `resolution.py`'s proposal store (rejected — a proposal is
deliberately ephemeral, discarded if never committed; a combat scene's round number needs to
survive across many separate `propose`/`commit` calls over the course of the fight, which an
in-memory dict tied to process lifetime cannot do for real play run across sessions).

## Decision: `determine_first_actor` is a pure function, independent of persisted state

**Rationale**: `docs/design/03-rules.md`'s own rule is a pure decision over stated inputs
(who started it, who's armed, who's the player side) — no roll, no randomness, matching
`docs/design/27-tooling.md`'s "deterministic over inference." Keeping it a pure function (like
`rules.py`'s own primitives) makes it trivially testable without needing a chronicle file at all,
and `start_combat` (the stateful wrapper) is a thin caller of it.

## Worked scenarios (SC-001–SC-003)

All four first-actor combinations, computed directly (a pure function, no dice — nothing to
disclose a seed for):

```
started_by="party"                                  -> "party" (explicit starter wins outright)
started_by=None, armed={"party": True, "opp": False}  -> "party" (sole armed side)
started_by=None, armed={"party": True, "opp": True}   -> player_side (both armed)
started_by=None, armed={"party": False, "opp": False} -> player_side (neither armed)
```

Surprise/ambush (SC-002/SC-003): a scene started with `surprised={"opp"}` reports
`can_act("opp")` as `False` while `round == 1`, `True` once `advance_round()` has run.
A scene started with `ambush={"party"}` reports `attack_modifier("party")` as `20` while
`round == 1`, `0` once `advance_round()` has run.
