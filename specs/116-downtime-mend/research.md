# Phase 0 research: Downtime phase, including Mend

No NEEDS CLARIFICATION markers remain in the Technical Context — this feature is a pure-Python,
stdlib-only library module following patterns already established by three sibling modules in
this repo. Findings below are drawn from reading those modules and the design corpus directly,
not from external research.

## Decision: Downtime loop state mirrors `session.py`'s `new_loop_state`/`advance_loop` pair

**Rationale**: `wyrd.session` already solved "a fixed sequence of named steps, checkable state,
illegal-transition rejection" for the session loop itself (`LOOP_STEPS`, `_LOOP_TRANSITIONS`,
`new_loop_state`, `advance_loop`). Downtime's five steps (Destination, Upkeep, Advances,
Undertaking, Rest) are the same shape at a smaller scale — a strictly linear sequence, no self-loop
like `beat`'s. Reusing the same "new_state / advance(state, to_step)" convention keeps the two
loop-state APIs recognizably related rather than inventing a second vocabulary for the same idea.

**Alternatives considered**: A single "resolve_downtime(all inputs at once)" function that takes
Destination/Upkeep choice/advances/undertaking/... as one call. Rejected: the spec's acceptance
scenarios test each step's outcome independently (User Story 1), and a caller may need to persist
state between steps (e.g. the player chooses Destination and Upkeep in one exchange, the
undertaking in a later one) — exactly the reason `session.py`'s own loop is stepped rather than
monolithic.

## Decision: Upkeep, Rest, and the undertaking gate are separate pure functions, not one combined call

**Rationale**: Matches `rally.py`'s separation of `apply_recovery` (the fixed part) from
`apply_rally` (recovery + optional award + commit hook) — small composable pieces a caller wires
together, rather than one function with many optional parameters. `economy.py`'s
`adjust_standing`/`spend_coin` are the direct model for Upkeep's two trade paths.

**Alternatives considered**: One `apply_upkeep(destination, standing, coin, choice)` function
covering both trade paths and the at-home no-op. Adopted in modified form — a single
`apply_upkeep` is right (it is one design-level step, docs/design/16-session.md's own table
treats it as one row), but it delegates to `economy.adjust_standing`/`economy.spend_coin`-shaped
logic internally rather than re-implementing Standing/coin arithmetic. Concretely, `economy.py`'s
existing functions take a full catalogue argument (`spend_coin`) that Upkeep's flat "coin -=
Standing" trade does not need, so Upkeep implements its own minimal coin subtraction rather than
calling `economy.spend_coin` — but reuses `economy.adjust_standing`'s exact delta convention
(`{"standing": standing + delta}`) for the Standing-loss path, so the two modules agree on shape
even though this feature adds one line for the coin case rather than importing `economy.py` for a
single subtraction.

## Decision: Mend takes the wounds list and a wound id, returns a new list (never mutates in place)

**Rationale**: Every existing pure function in this codebase (`character.active_wound_effects`,
`economy.gain_allegiance`, `advancement.award_advance`) returns new structures rather than
mutating inputs — `award_advance`'s docstring says so explicitly ("`record` is never mutated").
Mend follows the same convention for consistency and testability.

**Alternatives considered**: Mutate the wound dict in place and return `None`, matching how
`character.validate_wound` raises rather than returns. Rejected — Mend has a real result to report
(new effect value, or a rejection reason), unlike a validator, so the return-new-structure
convention (matching `economy.py`'s `_gain`/`_lose`) is the better fit.

## Decision: Mend's ladder is a fixed, hardcoded lookup table, not a formula

**Rationale**: ADR 0021 fixes the ladder exactly: `skill: -10 → -5 → closed`,
`stamina_max: -1 → closed`, `dread: +1 → closed`. These are three independent rungs, not a
generatable sequence (skill has two steps, the others have one) — a literal table is the direct,
readable expression of an ADR-fixed rule, matching how `advancement.TRIGGERS` and
`character.WOUND_EFFECT_KEYS` are themselves literal closed-vocabulary tuples/dicts rather than
computed.

**Alternatives considered**: A formula (`value + step` clamped) generalizing the `skill` case to
the others. Rejected: `stamina_max` and `dread` only have one rung between active and closed
(there is no "half-mended" -1→? for a track whose only nonzero magnitude ADR 0021 permits is 1), so
a formula would need the same per-effect special-casing a lookup table already gives directly, with
no simplification gained.

## Decision: no new ADR

**Rationale**: This feature implements a design and a decision record (`16-session.md`, ADR 0021)
that already exist and already settled every question this feature raises — no alternative is
being rejected here that the design corpus didn't already reject. CLAUDE.md's bar for an ADR
("a real alternative was rejected... someone would plausibly propose it again") is not met by
faithfully implementing an existing decision.
