# Phase 0 Research: Award advances against the four session triggers

## Decision: a new module, not an extension of `career.py`

**Chosen**: `engine/wyrd/advancement.py`.

**Rationale**: `career.py`'s docstring scopes it to creation's 8-advance allocation — validating a
caller's allocation against a career's grants. The award rules share no input with it: no career,
no skill, no cap. The two meet only when #277 validates a spend, which needs the balance this
module maintains and the caps `career.py` already computes.

**Alternatives rejected**: folding the triggers into `career.py` (would have to be moved out again
at #277, and widens a module with a stated narrow scope); putting them in `rules.py` (that module
holds shared constants, not stateful validators).

## Decision: not part of the propose/commit staging pipeline

**Chosen**: plain functions, like `career.validate_allocation`.

**Rationale**: `resolution.py`'s staging exists so a roll can be rerolled by spending Fate or
Fortune before it commits. An award rolls no dice and has nothing to reroll — staging it would
add a proposal id, a commit step and a discard step to a decision that is already deterministic.

## Decision: the award record is one object carrying both fields

**Chosen**: `{"triggers": [...], "advances_unspent": N}`.

**Rationale**: FR-006 says a new session clears the triggers and must *not* change the balance.
Keeping both in one record makes that claim directly testable — `begin_session` takes a record and
returns a record, and the test asserts one field reset and the other untouched. Two separate
arguments would let a caller reset one and forget the other, which is exactly the fault the
requirement guards against.

## Decision: three distinguishable refusals

**Chosen**: a `refusal` key naming one of `unknown_trigger`, `already_awarded`, `session_ceiling`,
alongside the human-readable `error` string every other validator in this engine returns.

**Rationale**: FR-004/SC-003 require a caller to tell a mistake from a limit. `career.py` returns
`{"valid": False, "error": "..."}` and a caller matching on prose is brittle; adding a stable key
next to the existing prose keeps the shape familiar without making the distinction depend on
wording.

## The ceiling and the one-of-each rule are independent

Four triggers, ceiling of three. They only disagree on a session where all four genuinely fired,
and that is the single case where a caller could reasonably expect a fourth advance. The design
document states both figures ("1-3 per session", "One of each per session at most") without
reconciling them, so the ceiling must bind independently rather than being inferred from the
vocabulary's size — which is why spec.md gives it its own user story and refusal reason.
