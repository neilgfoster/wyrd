# Feature Specification: The base propose/commit mechanism — staged rolls and mutations

**Feature Branch**: `193-propose-commit-mechanism`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Design the base propose/commit mechanism: staged rolls and mutations (closes #193, part of #192, part of #133). Prose passes intent (actor, action/skill, target, declaration); the engine looks up everything else from state, resolves the roll deterministically, stages both the roll data and the derived state mutation it implies, and returns a proposed result with a handle prose can later commit or discard. Nothing writes to state until committed. Cascading resolution, partial reroll, and Omen carryover are explicitly out of scope for this feature."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prose requests a test without pre-computing anything (Priority: P1)

A GM wants to resolve one test — "Senna resists this Exposure" — without first looking up her
skill, computing `effective%`, or knowing what a failure costs. The engine does all of that from
state.

**Why this priority**: This is the whole point of the propose call — removing the freehand
lookup/computation work from prose that the engine principles already say it shouldn't be
trusted with.

**Independent Test**: Given an actor entity with a stated skill and a named mechanic (e.g.
`exposure`, tier `moderate`), calling propose with only the actor, the mechanic, the skill name,
and any declaration bonus already decided returns a complete roll result and its implied
mutation, without the caller having supplied `effective%`, the roll, or the mutation amount.

**Acceptance Scenarios**:

1. **Given** an actor with a stated skill percentage, **When** propose is called naming the
   actor, the mechanic, the skill, and a difficulty band, **Then** the engine computes
   `effective%` itself and returns the roll, degrees, and Wyrd die read — the caller supplies
   none of these.
2. **Given** a mechanic whose failure implies a state mutation (e.g. Exposure gaining Taint),
   **When** the roll fails, **Then** the response includes the staged mutation, computed by the
   engine from the mechanic's own rule, not supplied by the caller.

### User Story 2 - Nothing is written until explicitly committed (Priority: P1)

A player may spend a reroll resource after seeing a proposed result (out of scope for *this*
feature to resolve, but the base mechanism must not preclude it) — so the initial roll must not
already be persisted when it's returned.

**Why this priority**: This is the property every later feature in #192 (cascading, reroll,
Omen carryover) depends on — if propose already wrote to state, there would be nothing left to
discard or partially reroll.

**Independent Test**: After a propose call, the actor's state on disk is unchanged; only after
an explicit commit call against the same proposal id does state change.

**Acceptance Scenarios**:

1. **Given** a proposed result with a staged Taint mutation, **When** the actor's state is read
   before commit, **Then** Taint is unchanged from before the propose call.
2. **Given** the same proposal, **When** commit is called with its id, **Then** Taint reflects
   exactly the staged mutation, and the proposal id no longer resolves to anything further to
   commit or discard.
3. **Given** a proposed result, **When** discard is called with its id instead of commit,
   **Then** state is unchanged and the id no longer resolves.

### Edge Cases

- What does propose return for a mechanic with no failure-driven mutation (an ordinary test with
  no stated consequence)? An empty mutation list — a roll result with nothing staged is a valid,
  common outcome, not an error.
- What happens if commit or discard is called with an id that doesn't exist (already committed,
  already discarded, or never issued)? It MUST error clearly, distinct from a no-op success —
  silently succeeding on an invalid id risks a caller believing something committed that didn't.
- Does this feature resolve a multi-step chain (attack → damage → armour → critical)? No —
  explicitly out of scope; a later #192 feature (cascading resolution) extends this to a chain.
  This feature's own worked example is deliberately a single-roll mechanic.
- Does this feature resolve declaration bonus from raw prose text? No — the GM's own judgment
  (is this specific and leveraging something established) is exactly the freehand narrative
  reasoning the engine cannot replace; propose takes the bonus as an already-decided numeric
  input (0, +10, +20, or −20), not text to parse.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Propose MUST take an actor, a named mechanic, a skill (for mechanics that test
  one), a difficulty band, and an already-decided declaration-bonus value — and MUST NOT require
  the caller to supply `effective%`, the roll, or any derived mutation.
- **FR-002**: Propose MUST look up the actor's skill and any opponent/baseline from state itself,
  compute `effective%` per `03-rules.md` §1's existing formula, and resolve the roll
  deterministically.
- **FR-003**: Propose's response MUST include the roll data (roll, degrees, Wyrd die read,
  outcome) and any mutation the mechanic's own rule implies on that outcome, computed by the
  engine — never supplied by the caller.
- **FR-004**: Propose MUST NOT write anything to persistent state — only commit does.
- **FR-005**: Commit MUST take a proposal id and apply exactly its staged mutations to state,
  atomically, then invalidate the id.
- **FR-006**: Discard MUST take a proposal id, write nothing, and invalidate the id.
- **FR-007**: Commit or discard called with an id that does not resolve to an open proposal MUST
  error clearly, distinct from a successful no-op.
- **FR-008**: Cascading resolution (a mutation that itself crosses a threshold and spawns a
  further roll), partial reroll, and Omen carryover across multiple rolls are explicitly out of
  scope for this feature.

### Key Entities

- **Proposal** — an unpersisted, in-memory (or otherwise non-authoritative-state) record: an id,
  its roll data, its staged mutations, and whether it is still open (neither committed nor
  discarded).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new design document specifies the propose/commit/discard request and response
  shapes concretely.
- **SC-002**: A worked example (one ordinary Exposure test, real seeded roll, propose then
  commit) shows state unchanged before commit and correctly mutated after, with the exact
  numbers shown.
- **SC-003**: The error case (commit/discard on an invalid id) is stated explicitly, not left
  implicit.
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.

## Assumptions

- This is a design specification, not an implementation — the mechanism is specified (request
  shape, response shape, behaviour), not built; `#90` (Implement the engine) is where code
  lands, matching every other document in `docs/design/`.
- The worked example uses a real seeded roll (Python's `random`, seed disclosed) to compute the
  actual numbers shown, per this repo's deterministic-over-inference discipline — not asserted
  arithmetic.
- No ADR: this specifies a new mechanism (the propose/commit split itself), which is a genuine
  design decision, but its own Alternatives-rejected reasoning belongs in #192's own umbrella
  record if one is warranted once all five children land — raised here as an open question for
  plan.md to resolve, not assumed either way.
