# Feature Specification: Partial reroll

**Feature Branch**: `237-partial-reroll`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Partial reroll — rerolling one step discards exactly what causally depends on it, and nothing else, per docs/design/31-action-resolution.md 'Partial reroll'. reroll(proposal_id, step, resource) computes the downstream set from depends_on, discards and freshly resolves exactly that set under the resource's own modifier (Resolve +20, Fortune plain, Bargain plain for 1 Taint), leaves everything outside the downstream set untouched, and re-cascades under #236's rule. reroll never invalidates the proposal id. Depends on #235, #236. Closes #237, part of #211."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Spending a reroll resource against one step leaves an independent branch untouched (Priority: P1)

A caller proposes two unrelated tests together in one batch, then spends a reroll resource
against only one of them. The other test's result — already staged — is exactly what it was
before, unaffected by a reroll that has nothing to do with it.

**Why this priority**: This is `docs/design/31-action-resolution.md`'s own worked example for
this feature, and the property that makes "downstream set" meaningful rather than "reroll
everything in the proposal."

**Independent Test**: Given a proposal with two independent top-level steps (neither depends on
the other), calling `reroll` against one of them changes only that step (and whatever depends on
it); the other step's roll data and mutations are identical, by value, to what `propose_batch`
first returned for it.

**Acceptance Scenarios**:

1. **Given** a batch proposal with steps 0 and 1, neither depending on the other, **When**
   `reroll` is called against step 0, **Then** step 1's roll data and mutations in the revised
   proposal are unchanged from the original proposal.
2. **Given** the same setup, **When** the reroll is committed, **Then** state reflects step 1's
   original (untouched) result and step 0's freshly-rerolled result, exactly.

---

### User Story 2 - Rerolling discards exactly the downstream set, nothing else (Priority: P1)

A caller rerolls a step whose original resolution triggered a cascade (e.g. a Taint mutation
that crossed a threshold and staged a Transformation). The reroll discards the rerolled step
*and* every step that cascade produced, then re-resolves and re-cascades fresh — it does not
leave a stale cascade step from the old roll sitting alongside a new one.

**Why this priority**: This is the case the design document's own `depends_on` mechanism exists
to get right — a cascade step's continued presence after its trigger was undone would be a
correctness bug, not a cosmetic one.

**Independent Test**: Given a step whose original resolution staged one or more dependent
cascade steps, calling `reroll` against the original step removes every one of those dependent
steps from the proposal and, if the fresh roll's own outcome calls for a cascade, stages a fresh
one (which may differ in shape from the original).

**Acceptance Scenarios**:

1. **Given** step 0 originally staged a dependent step 1 (e.g. a Transformation triggered by a
   crossed Taint threshold), **When** `reroll` is called against step 0, **Then** the revised
   proposal's steps no longer include the original step 1's content — a fresh cascade (or none,
   if the new roll doesn't cross the threshold) has taken its place.
2. **Given** a step with no dependents, **When** it is rerolled, **Then** only that one step is
   discarded and refreshed.

---

### User Story 3 - Each reroll resource applies its own modifier and cost (Priority: P2)

A caller rerolls the same failed step three different ways (Resolve, Fortune, the Bargain) and
observes the correct modifier applied to the fresh roll and the correct cost staged alongside
it.

**Why this priority**: Getting a resource's own numbers wrong would silently misapply
`docs/design/03-rules.md`'s own stated values.

**Independent Test**: Rerolling under `resolve` computes the fresh roll's `effective_pct` +20
over what an unmodified reroll would have used, and stages a `resolve.current -1` mutation.
Rerolling under `fortune` uses the unmodified `effective_pct` and stages `fortune.current -1`.
Rerolling under `bargain` uses the unmodified `effective_pct` and stages `taint +1`.

**Acceptance Scenarios**:

1. **Given** a step rerolled under `resolve`, **When** the fresh roll is resolved, **Then** its
   `effective_pct` is 20 higher than the original step's own `effective_pct`, and a
   `resolve.current -1` mutation is staged on the same step.
2. **Given** a step rerolled under `fortune`, **When** the fresh roll is resolved, **Then** its
   `effective_pct` matches the original step's own, and a `fortune.current -1` mutation is
   staged.
3. **Given** a step rerolled under `bargain`, **When** the fresh roll is resolved, **Then** its
   `effective_pct` matches the original step's own, and a `taint +1` mutation is staged.
4. **Given** an unknown resource name, **When** `reroll` is called, **Then** it raises an error
   rather than silently applying no modifier.

---

### User Story 4 - `reroll` never ends the proposal (Priority: P2)

A caller rerolls a step, inspects the revised proposal, and can still commit or discard it (or
reroll a further step) — the proposal id stays open throughout.

**Why this priority**: `docs/design/31-action-resolution.md` states this explicitly; getting it
wrong would silently make a proposal one-reroll-only.

**Independent Test**: After one or more `reroll` calls against the same `proposal_id`, `commit`
still succeeds and applies the revised (not the original) mutations.

**Acceptance Scenarios**:

1. **Given** a proposal that has been rerolled once, **When** `commit` is called, **Then** it
   succeeds and applies the *revised* proposal's mutations.
2. **Given** the same proposal, **When** `reroll` is called a second time against a different
   step, **Then** it succeeds — the id was never invalidated by the first reroll.

### Edge Cases

- What happens when `reroll` is called against a step that was itself produced by a cascade
  (e.g. a `transformation`/`weapon-damage`/`armour`/`critical` step, never a direct caller
  request)? → An error — only a step that was originally a top-level request (one a reroll
  resource is actually spent against, per `docs/design/03-rules.md` §§3-4) is directly
  rerollable. See Assumptions.
- What happens when `reroll` names a `step` id that doesn't exist in the proposal? → An error.
- What happens when `reroll` is called against an already-committed or already-discarded
  proposal? → `ProposalError`, the same as `commit`/`discard` against a closed proposal (#235).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide `reroll(proposal_id, step, resource)`, computing the
  downstream set of `step` — itself and every step that transitively depends on it via
  `depends_on` — and discarding exactly that set from the proposal.
- **FR-002**: `reroll` MUST freshly resolve the rerolled step using its own original request
  (actor, mechanic, skill, target, difficulty, tier, dice), under the named resource's modifier,
  and re-run the same cascade rule (#236) against the fresh result — producing however many new
  dependent steps that fresh result actually calls for (which may differ from the original
  cascade's shape).
- **FR-003**: Every step outside the downstream set MUST be left byte-for-byte unchanged in the
  revised proposal (User Story 1).
- **FR-004**: `resolve` MUST add +20 to the rerolled step's `effective_pct` computation and stage
  a `resolve.current -1` mutation on the rerolled step.
- **FR-005**: `fortune` MUST leave `effective_pct` unmodified and stage a `fortune.current -1`
  mutation on the rerolled step.
- **FR-006**: `bargain` MUST leave `effective_pct` unmodified and stage a `taint +1` mutation on
  the rerolled step.
- **FR-007**: The resource's cost mutation MUST be staged as part of the same `reroll` call, on
  the rerolled step's own mutations — never a separate call the caller must remember to make.
- **FR-008**: `reroll` MUST NOT invalidate `proposal_id` — `commit`/`discard` remain the only
  calls that do.
- **FR-009**: `reroll` MUST raise an error for an unknown `resource`, an unknown `step` id, or a
  `step` that was not itself a top-level request.
- **FR-010**: The rerolled step MUST keep its own original `step_id`; any further cascade steps
  the fresh resolution produces MUST receive fresh ids that never collide with any kept step's
  id (including an unrelated step elsewhere in the same batch).

### Key Entities

- **Downstream set**: the transitive closure, over `depends_on` edges, of every step that would
  no longer make sense once the rerolled step's own result changed — computed fresh from the
  proposal's current `steps` each time `reroll` is called.
- **Reroll resource**: one of `resolve`/`fortune`/`bargain`, each with a fixed `effective_pct`
  modifier and a fixed cost mutation (`docs/design/03-rules.md` §§3-4).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `propose_batch` + `reroll` for a real seeded scenario constructed for this feature
  (research.md; disclosed, not asserted) reproduces the shape of `docs/design/31-action-
  resolution.md`'s own "an independent branch survives a reroll elsewhere in the batch" example:
  the untouched step's result is unchanged, the rerolled step's mutation plus the resource's own
  cost combine on the same step.
- **SC-002**: A reroll against a step that originally triggered a Transformation cascade removes
  the stale cascade step(s) and, if the fresh roll still crosses the threshold, stages a fresh
  cascade — never leaving both old and new cascade steps present at once.
- **SC-003**: Each of the three resources' modifier and cost is independently verified (User
  Story 3).
- **SC-004**: `commit` after one or more rerolls applies the revised proposal's mutations, not
  the original ones.
- **SC-005**: `ruff check . && ruff format --check . && python3 -m pytest -q` is clean.

## Assumptions

- Only a step that was itself a direct top-level request (what a `propose`/`propose_batch` call
  actually named) is directly rerollable — matching every use of "reroll" in
  `docs/design/03-rules.md` §§3-4, which is always the player's own test, never an internal
  cascade step like `weapon-damage`/`armour`/`critical`/`transformation`. Extending reroll to an
  internal step is a documented follow-up, not required by this feature's own acceptance
  criteria or worked example.
- `docs/design/31-action-resolution.md`'s own worked example's numbers come from real hand-rolled
  dice in a playtest transcript (not a disclosed engine seed) — like #236's own research.md, this
  feature computes and discloses its own seeded scenario reproducing the same *shape*, rather
  than claiming to match numbers that were never seed-disclosed in the first place.
- Omen carryover's own interaction with reroll (a rerolled step whose downstream set includes a
  step that consumed its Omen) is explicitly out of scope — a separate, later feature (#238)
  that has not yet introduced the Omen-consumption `depends_on` edge this module doesn't have.
