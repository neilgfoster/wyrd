# Feature Specification: Omen carryover

**Feature Branch**: `238-omen-carryover`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Omen carryover — an Ill or Fair Omen applies to the roller's own next roll, in the order play actually produces them, per docs/design/31-action-resolution.md 'Omen carryover'. An actor's committed state carries a persistent pending_omen field that survives across committed proposals until spent. Within one batch, each roll checks whether an earlier step belonging to the same actor produced an Omen; a step that consumes another step's Omen depends on it via the same depends_on edge cascading resolution introduced. Depends on #235, #236. Closes #238, part of #211 (the last of its four sibling features)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An Omen produced by one roll modifies the actor's own next roll (Priority: P1)

A caller proposes two of the same actor's unrelated tests together in one batch. The first
reads an Omen off its own Wyrd die (the natural roll's units digit); the second, resolved next
for that same actor, is modified by it — without either the caller or any intervening code
having to notice or wire this up explicitly.

**Why this priority**: This is the entire mechanism `docs/design/31-action-resolution.md` "Omen
carryover" specifies, and its own worked example.

**Independent Test**: Given a batch with two requests for the same actor, if the first's own
Wyrd die reads Fair Omen, the second's `effective_pct` is 10 higher than an unmodified
computation would give it; if Ill Omen, 10 lower.

**Acceptance Scenarios**:

1. **Given** the first of two same-actor requests reads Fair Omen off its own roll, **When** the
   second is resolved, **Then** its `effective_pct` includes `+10`, and it `depends_on` the step
   that produced the Omen.
2. **Given** the first reads Ill Omen instead, **When** the second is resolved, **Then** its
   `effective_pct` includes `-10`.
3. **Given** neither request's own roll reads an Omen, **When** the second is resolved, **Then**
   its `effective_pct` is unmodified and it does not `depends_on` the first for this reason.

---

### User Story 2 - A persisted Omen carries into a fresh proposal (Priority: P1)

An actor's own committed state already carries a pending Omen (from an earlier, already-
committed proposal). A new `propose`/`propose_batch` call for that actor applies it to their
first request in the new batch, exactly as if it had been produced earlier in the same batch.

**Why this priority**: `docs/design/31-action-resolution.md` states the field is "persistent, not
batch-local" — an Omen must be able to cross a commit boundary, not only survive within one
proposal.

**Independent Test**: Given an actor whose state has `pending_omen: +10` already set, a fresh
`propose` for that actor applies the `+10` to the first roll, without that roll `depends_on`-ing
anything (no step in this proposal produced it).

**Acceptance Scenarios**:

1. **Given** `pending_omen: +10` already on disk, **When** `propose` resolves a test for that
   actor, **Then** its `effective_pct` includes `+10` and its `depends_on` is empty.
2. **Given** the same setup, **When** the proposal is only `discard`ed, **Then** the actor's
   `pending_omen` on disk is still `+10`, exactly as before (reading never consumes).
3. **Given** the same setup, **When** the proposal is `commit`ted, **Then** the actor's
   `pending_omen` on disk reflects whatever the batch's own final token ended at (`None` if
   spent and nothing further produced one).

---

### User Story 3 - A second Omen in the same batch replaces, never stacks (Priority: P2)

An actor's first request in a batch produces an Omen; before it's ever applied to anything, a
later request for the same actor also happens to read a fresh Omen off its own roll. The
pending token becomes the fresh one — never both, never summed.

**Why this priority**: `docs/design/31-action-resolution.md` states this explicitly; getting it
wrong would double-count a modifier the rules never intend to compound.

**Independent Test**: Given three same-actor requests where the first and second both read an
Omen (of either kind) before a third consumes one, the third is modified by the *second's* Omen
only, and `depends_on` the second, not the first.

**Acceptance Scenarios**:

1. **Given** request 1 reads Fair Omen and request 2 (which consumed and then itself also read a
   fresh Omen) reads Ill Omen, **When** request 3 is resolved, **Then** its modifier is `-10`
   (request 2's), not `+10` (request 1's), and it `depends_on` request 2.

---

### User Story 4 - Rerolling an Omen-producing step correctly discards its consumer too (Priority: P1)

A caller rerolls a step that originally produced an Omen another (already-staged) step consumed.
The consuming step — even though it belongs to a *different* top-level request and has no
mutation-based dependency on the producer — is discarded and freshly re-resolved alongside it,
under whatever the fresh roll's own Omen output (if any) actually is.

**Why this priority**: This is the property the design document's own worked example exists to
demonstrate, and the reason the Omen-consumption edge reuses `depends_on` rather than inventing
a separate mechanism — reroll (#237) gets this right without any Omen-specific code in `reroll`
itself.

**Independent Test**: Given a batch where request 1 produced an Omen request 2 consumed,
rerolling request 1's own step: request 2's original result no longer appears in the revised
proposal; a fresh request 2 result does, computed with whatever Omen (if any) the fresh request 1
actually produced.

**Acceptance Scenarios**:

1. **Given** the setup above, **When** `reroll` is called against request 1's step, **Then** the
   revised proposal's steps no longer include request 2's original roll data.
2. **Given** the fresh request 1 produces no Omen this time, **When** request 2 is freshly
   re-resolved, **Then** its `effective_pct` is unmodified and it does not `depends_on` anything
   for Omen reasons.

### Edge Cases

- What happens when the actor's `pending_omen` is already spent by the time a batch's own first
  request would apply it (i.e., it's `None`)? → No modifier applied; the request resolves
  exactly as an unmodified one would.
- What happens when the request that would consume a pending Omen belongs to a *different actor*
  than the one who produced it? → Nothing — Omen carryover is strictly per-actor; another
  actor's own requests never see it.
- What happens when a whole proposal is discarded after an Omen was read but never applied? →
  Nothing is written; the actor's persisted `pending_omen` is exactly as it was before `propose`
  was ever called (spec.md's own "propose writes nothing" property, unchanged by this feature).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every actor entity's own `pending_omen` field (already part of the character schema:
  `None`/`+10`/`-10`) MUST be read, not consumed, at the start of resolving that actor's first
  request within a `propose`/`propose_batch` call, and applied as a modifier to that request's
  own `effective_pct` computation.
- **FR-002**: Within one call, each of an actor's own further requests MUST check whether an
  earlier request for that same actor produced a still-pending Omen; if so, apply and spend it
  as that request's own modifier, and record a `depends_on` edge to the step that produced it.
- **FR-003**: A request whose own roll reads a fresh Omen (whether or not it also just consumed
  one) MUST make that fresh Omen the new pending token for that actor, replacing — never
  stacking with — whatever was pending before.
- **FR-004**: A pending token consumed by a request MUST clear to `None` if that same request's
  own roll does not read a fresh Omen (FR-003's replacement did not occur).
- **FR-005**: At the end of resolving a `propose`/`propose_batch` call, for every actor whose
  final token differs from what was persisted going in, exactly one `pending_omen` `set` mutation
  MUST be staged, on the last step that changed it for that actor.
- **FR-006**: A `pending_omen` mutation MUST NOT be staged for an actor whose final token equals
  what was already persisted (no needless no-op mutation).
- **FR-007**: `reroll`ing a step MUST correctly discard and freshly re-resolve every step in its
  downstream set, including a step belonging to a *different* top-level request that is only in
  the downstream set via an Omen-consumption `depends_on` edge — reusing the existing downstream-
  set/re-cascade machinery (#237) without any Omen-specific logic inside `reroll` itself.
- **FR-008**: Reading `pending_omen` (at the start of a batch, or by `reroll` rebuilding its own
  scratch state) MUST NOT itself write anything — only a `commit` that includes a staged
  `pending_omen` mutation changes what's on disk; a `discard`ed proposal leaves it untouched.

### Key Entities

- **Omen token** (per actor, tracked only for the duration of one `propose`/`propose_batch`/
  `reroll` call): the currently-pending modifier (`+10`/`-10`/`None`) for that actor, and — if it
  came from a step within *this* call — which step produced it, for the `depends_on` edge.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A real seeded scenario constructed for this feature (research.md; disclosed, not
  asserted) reproduces the shape of `docs/design/31-action-resolution.md`'s own "an Omen carries
  across a batch, then unwinds correctly on reroll" worked example: the second request's
  `effective_pct` is modified by the first's Omen and `depends_on` it; rerolling the first
  correctly discards and freshly re-resolves the second, with no stale dependency once the fresh
  roll produces no Omen.
- **SC-002**: A persisted incoming `pending_omen` applies to a fresh proposal's first request
  with no `depends_on` edge (User Story 2), and survives a `discard` untouched.
- **SC-003**: A second in-batch Omen replaces rather than stacks with a still-pending one (User
  Story 3).
- **SC-004**: No `pending_omen` mutation is staged when an actor's final token equals what was
  already persisted (FR-006).
- **SC-005**: `ruff check . && ruff format --check . && python3 -m pytest -q` is clean.

## Assumptions

- `docs/design/31-action-resolution.md`'s own worked example's numbers come from real hand-rolled
  dice in a playtest transcript (not a disclosed engine seed) — like #236/#237's own research.md,
  this feature computes and discloses its own seeded scenario reproducing the same *shape*.
- Only the two mechanics `propose`/`propose_batch` already dispatch through (`ordinary-test`,
  `exposure`, `combat-attack`) participate in Omen tracking; the internal cascade-only mechanics
  (`transformation`/`weapon-damage`/`armour`/`critical`) are not top-level requests and are
  unaffected, consistent with #237's own scoping of what a `reroll`-affecting request means.
