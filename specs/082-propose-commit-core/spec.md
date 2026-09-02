# Feature Specification: Propose/commit/discard core

**Feature Branch**: `082-propose-commit-core`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "Propose/commit/discard core — implement propose, commit, and discard exactly as specified in docs/design/31-action-resolution.md 'Propose, then commit' (ADR 0050): propose resolves one roll against state and returns roll data plus implied mutations without writing; commit applies exactly the staged mutations atomically and invalidates the id; discard writes nothing and invalidates the id. Single-step resolution only (closes #235, part of #211)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A caller resolves one test without pre-computing anything (Priority: P1)

A caller (the GM layer, or a test) wants to resolve one test — e.g. "Senna resists this
Exposure" — by naming the actor, the mechanic, and the skill, without first looking up her skill
value, computing `effective%`, or knowing what a failure costs. The engine looks all of that up
from state itself.

**Why this priority**: This is the entire point of `propose` — removing the freehand lookup and
computation from the caller, per `docs/design/27-tooling.md`'s "deterministic over inference"
rule and `docs/design/31-action-resolution.md`.

**Independent Test**: Given an actor entity with a stated skill value in state, calling
`propose(actor, mechanic, skill, ...)` returns a complete roll result (`roll`, `effective_pct`,
`degrees`, `wyrd_die`, `outcome`) and any implied mutations, without the caller supplying the
roll, the effective percentage, or the mutation amount.

**Acceptance Scenarios**:

1. **Given** an actor with a stated skill percentage in state, **When** `propose` is called
   naming the actor, mechanic, skill, and (optionally) difficulty/target/declaration_bonus,
   **Then** the engine computes `effective_pct` itself and returns the roll, degrees, and Wyrd
   die read — the caller supplies none of these.
2. **Given** a mechanic whose failure implies a state mutation (e.g. an Exposure test gaining
   Taint on failure), **When** the roll fails, **Then** the response's `mutations` list includes
   that mutation, computed by the engine from the mechanic's own rule.
3. **Given** an outcome with no implied consequence (e.g. many ordinary tests), **When**
   `propose` is called, **Then** it returns an empty `mutations` list — not an error.

---

### User Story 2 - Nothing is written until explicitly committed (Priority: P1)

A caller wants to see a proposed result before it becomes real — the base property every future
extension (cascading resolution, partial reroll, Omen carryover) depends on, even though this
feature does not itself implement any of those.

**Why this priority**: If `propose` already wrote to state, there would be nothing left for a
later `discard` to undo, or for a later reroll (out of scope here) to reconsider.

**Independent Test**: After a `propose` call, the actor's state is provably unchanged (read it
back and compare); only an explicit `commit` call against the same proposal id changes it.

**Acceptance Scenarios**:

1. **Given** a successful `propose` call, **When** the actor's state is read immediately
   afterward, **Then** it is byte-for-byte identical to before the call.
2. **Given** an open proposal id, **When** `commit` is called with it, **Then** exactly the
   staged mutations are applied atomically, and state reflects them afterward.
3. **Given** an open proposal id, **When** `discard` is called with it instead, **Then** state
   remains exactly as it was before `propose` was called.

---

### User Story 3 - Reusing or misusing a proposal id fails loudly (Priority: P2)

A caller must never be able to mistake "there was nothing to do" for "your commit actually went
through" — a proposal id that has already been resolved, or was never issued, must raise an
error rather than silently doing nothing.

**Why this priority**: A silent no-op here would corrupt every caller's ability to reason about
whether a mutation actually landed — a correctness property, not a convenience.

**Independent Test**: Calling `commit` or `discard` twice against the same id, or against a
fabricated id, raises an error both times after the first successful call.

**Acceptance Scenarios**:

1. **Given** a proposal id that was already committed, **When** `commit` or `discard` is called
   with it again, **Then** an error is raised — not a silent no-op.
2. **Given** a proposal id that was already discarded, **When** `commit` or `discard` is called
   with it again, **Then** an error is raised.
3. **Given** a proposal id that was never issued by `propose`, **When** `commit` or `discard` is
   called with it, **Then** an error is raised.

### Edge Cases

- What happens when `propose` is called for a mechanic that isn't in the closed mechanic
  vocabulary (`docs/design/31-action-resolution.md`'s `mechanic` parameter)? → An error naming
  the unknown mechanic, not a silent default.
- What happens when `propose` names a `target` entity that doesn't exist in state? → An error,
  not a resolved roll against absent data.
- What happens when two proposals are open for the same actor at once, and only one is
  committed? → Each proposal is independent and self-contained; committing one does not affect
  the other's staged data, though the caller is responsible for keeping their own bookkeeping
  consistent (multi-actor/multi-proposal orchestration is out of scope for this feature).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a `propose(actor, mechanic, skill, target=None,
  difficulty=Average, declaration_bonus=0)` call that looks up the actor's (and, if given, the
  target's) own skill values and track state directly — the caller never supplies a skill
  percentage, roll, or mutation amount.
- **FR-002**: `propose` MUST resolve the roll deterministically using the engine's existing dice
  primitives (`engine/wyrd/rules.py`), compute `effective_pct`, `degrees`, and the Wyrd die read,
  and return them as part of the result.
- **FR-003**: `propose` MUST compute any state mutation the mechanic's own rule implies for the
  resolved outcome, and stage it in the result's `mutations` list — an empty list when the
  outcome implies no mutation, never an error.
- **FR-004**: `propose` MUST NOT write to state — calling it any number of times, and reading
  state after each call, must show state unchanged.
- **FR-005**: `propose` MUST return a `proposal_id` uniquely identifying this staged result,
  usable by `commit` or `discard`.
- **FR-006**: The engine MUST provide `commit(proposal_id)`, which applies exactly the staged
  mutations from that proposal to state, atomically (all mutations land, or — on any failure —
  none do), and invalidates the id so it can never resolve again.
- **FR-007**: The engine MUST provide `discard(proposal_id)`, which writes nothing to state and
  invalidates the id so it can never resolve again.
- **FR-008**: Calling `commit` or `discard` with a `proposal_id` that does not resolve to a
  currently-open proposal (already committed, already discarded, or never issued) MUST raise an
  error, distinguishable from a successful no-op.
- **FR-009**: This feature covers single-step resolution only — one roll, one set of staged
  mutations, per proposal. Cascading resolution (a mutation crossing a threshold, or a roll's
  outcome calling for a further roll), partial reroll, and Omen carryover are explicitly out of
  scope, tracked as separate sibling features (#236, #237, #238) under #211.

### Key Entities

- **Proposal**: an unpersisted, in-memory record produced by `propose` — a `proposal_id`, the
  resolved `roll` data (actor, mechanic, roll, effective_pct, degrees, wyrd_die, outcome), the
  staged `mutations` list, and whether it is still open (neither committed nor discarded). Not
  written to any durable store until `commit`.
- **Mutation**: a staged, not-yet-applied change to one field of one entity's state — an entity
  id, a field name, an operation (e.g. `+`, `-`, `set`), and a value — produced by a mechanic's
  own rule from a resolved roll's outcome.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `propose` for a real seeded scenario (the Senna Vask Exposure example in
  `docs/design/31-action-resolution.md`, seed `20260852`) produces the exact roll, `effective_pct`,
  outcome, and mutation shown in that document.
- **SC-002**: State read immediately after `propose`, for any scenario, is identical to state
  read immediately before it — verified by a test, not asserted.
- **SC-003**: State read after `commit` reflects exactly the staged mutations and nothing else;
  state read after `discard` is identical to state before `propose`.
- **SC-004**: Every one of `commit`/`discard` called twice, or against a fabricated id, raises an
  error on the second/invalid call — verified by a test for each of the three cases in FR-008.
- **SC-005**: `ruff check . && ruff format --check . && python3 -m pytest -q` is clean.

## Assumptions

- This feature implements exactly the mechanism `docs/design/31-action-resolution.md` already
  specifies (produced by the earlier design feature, issue #193/spec 066) — no new design
  decision is made here, so no new ADR is expected from this feature.
- Proposals are process-local, in-memory state (a dict keyed by `proposal_id`), consistent with
  the engine having no backend/daemon (`CLAUDE.md`, `docs/design/27-tooling.md`) — nothing about
  cross-process proposal persistence is assumed or required.
- The closed mechanic vocabulary (`ordinary-test`, `exposure`, `terror-test`,
  `system-of-power:<id>`, …) is read from whatever the engine's existing rules/state modules
  already establish; this feature does not invent new mechanics, only the propose/commit/discard
  plumbing around invoking them.
- `engine/wyrd/state.py`/`character.py` already expose the actor/target lookups this feature
  needs; if a lookup this feature requires does not yet exist there, adding it is in scope as
  plumbing, not a new design decision.
