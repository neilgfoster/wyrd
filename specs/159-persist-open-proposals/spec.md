# Feature Specification: Proposals survive across separate CLI invocations

**Feature Branch**: `159-persist-open-proposals`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: GitHub issue #414 — propose's staged proposal_id lives only in an
in-process dict; commit/discard in a separate CLI invocation can never find it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A GM skill stages a roll, narrates, then commits it in a later invocation (Priority: P1)

A GM-facing skill calls `python3 -m wyrd.client propose ...` to stage a roll, uses the returned
roll data and mutations to narrate the scene, and only afterwards — as a genuinely separate
process invocation, potentially after other CLI calls unrelated to this proposal — decides to
commit or discard it.

**Why this priority**: This is the whole point of the propose/commit/discard mechanism
(docs/design/31-action-resolution.md, ADR 0050). As shipped, this scenario is completely broken:
every real GM skill invokes the CLI as one-shot subprocesses, so a proposal staged by one
invocation is invisible to any later one. Nothing that stages now and decides later currently
works at all.

**Independent Test**: Run `python3 -m wyrd.client propose <args>` as one subprocess, capture the
`proposal_id` it prints, then run `python3 -m wyrd.client commit <proposal_id>` as a wholly
separate subprocess invocation and confirm it applies the staged mutations to the chronicle's
entity files on disk.

**Acceptance Scenarios**:

1. **Given** a proposal staged by one CLI process, **When** a separate, later CLI process commits
   that proposal's id, **Then** the staged mutations are applied to state exactly as they would
   be had `commit` been called in the same process.
2. **Given** a proposal staged by one CLI process, **When** a separate, later CLI process
   discards that proposal's id, **Then** nothing is written to state and the id no longer
   resolves to anything.

---

### User Story 2 - A stale, unresolved proposal from a prior session does not corrupt the next one (Priority: P2)

A session ends (deliberately or because the CLI process simply exits) while a proposal is open
and neither committed nor discarded. The next session begins.

**Why this priority**: Without an explicit staleness rule, a persisted proposal could otherwise
accumulate forever, or a later mismatched `commit` could apply a mutation computed against
state that has since moved on. docs/design/22-state.md's "Transaction lifecycle" section already
states the intended policy — this story is what makes that policy real for the same class of
proposal this issue is about, not a new invention.

**Independent Test**: Stage a proposal, end the process without committing or discarding, run
`wyrd rally` for the same actor, then confirm the earlier proposal id no longer resolves (an
attempt to commit or discard it returns the same "no open proposal" error as an unknown id).

**Acceptance Scenarios**:

1. **Given** an open, uncommitted proposal recorded in `chronicle.yaml`'s `pending.rolled`,
   **When** a Rally is applied for the proposal's actor, **Then** the proposal is discarded (its
   persisted record removed, nothing written to state) and its id no longer resolves.
2. **Given** an actor with an already-open, unresolved proposal, **When** a new proposal is
   staged for the same actor before the first is committed or discarded, **Then** the prior one
   is discarded first (an engine session never carries more than one genuinely open proposal per
   actor at a time, per docs/design/22-state.md).

---

### User Story 3 - An unknown or already-resolved id is still rejected, unchanged (Priority: P3)

A caller invokes `commit` or `discard` with a proposal id that was never issued, or that already
resolved (committed or discarded) earlier.

**Why this priority**: Existing, tested behaviour that persistence must not regress — the
acceptance criteria on #414 call this out explicitly.

**Independent Test**: Call `commit`/`discard` with a made-up id, or with an id already consumed
by a prior `commit`/`discard` in this or an earlier process, and confirm the same
"no open proposal: `<id>`" error as before.

**Acceptance Scenarios**:

1. **Given** a proposal id that was never issued, **When** `commit` or `discard` is called with
   it, **Then** the call fails with the existing "no open proposal" error.
2. **Given** a proposal id already committed or discarded (in this process or an earlier one),
   **When** `commit` or `discard` is called with it again, **Then** the call fails the same way.

### Edge Cases

- Two entirely separate proposals are staged (for different actors, or as independent branches
  of the same batch) and only one is ever committed — the other must remain independently
  resolvable, exactly as `reroll`'s existing "an independent branch survives a reroll elsewhere
  in the batch" property already guarantees in-process.
- The chronicle directory a `commit`/`discard` runs against must be the same one the original
  `propose` ran against — a proposal_id is meaningless outside the chronicle that produced it.
- A proposal that is `reroll`ed one or more times, across possibly-separate CLI invocations, must
  still be resolvable by a final, separate `commit`/`discard` call, with the persisted content
  reflecting the most recent reroll rather than the original stage.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST persist a staged proposal's full contents (its steps, mutations,
  and `depends_on` graph) somewhere that survives process exit, keyed by `proposal_id`, so that a
  separate later process invocation can look it up.
- **FR-002**: The persisted proposal MUST be scoped to the chronicle directory it was proposed
  against, consistent with how `character.load`/`save`/`chronicle.load_chronicle` are already
  chronicle-scoped (docs/design/22-state.md).
- **FR-003**: Writing a proposal's persisted record MUST use the same atomic-write convention the
  rest of chronicle state already uses (`state.write_text_atomic`), rather than a new mechanism.
- **FR-004**: `commit(proposal_id)` and `discard(proposal_id)`, when run as a separate process
  from the `propose`/`propose_batch`/`reroll` call that produced or last revised the proposal,
  MUST behave identically to running all calls in one process: `commit` applies exactly the
  staged mutations atomically; `discard` writes nothing.
- **FR-005**: `reroll(proposal_id, ...)`, when run as a separate process from the call that
  staged the proposal, MUST be able to revise it in place and have the revision itself persist
  for a still-later `commit`/`discard` call.
- **FR-006**: `commit`/`discard` on an id that was never issued, or that already resolved
  (committed or discarded, in this process or an earlier one), MUST continue to raise the
  existing "no open proposal" error, unchanged.
- **FR-007**: An open, uncommitted proposal recorded when a session ends mid-beat MUST be
  recorded in `chronicle.yaml`'s existing `pending.rolled` field, reusing
  `engine/wyrd/chronicle.py`'s existing `record_rolled` — not a second staleness mechanism.
- **FR-008**: Applying a Rally MUST discard any proposal still open for the Rallying actor,
  clearing the persisted record and the `pending.rolled` reference, per docs/design/22-state.md's
  "Transaction lifecycle" and `chronicle.py`'s existing `discard_at_rally`.
- **FR-009**: An engine session MUST never carry more than one genuinely open proposal per actor
  at a time — staging a new proposal for an actor with an already-open one discards the earlier
  one first (docs/design/22-state.md), whether or not the two calls are in the same process.
- **FR-010**: The persistence mechanism MUST NOT change `propose`/`propose_batch`/`commit`/
  `discard`/`reroll`'s existing return shapes or in-process behaviour when both calls do happen to
  run in the same process (no regression for existing callers/tests).

### Key Entities

- **Persisted proposal record**: the on-disk form of what `_open_proposals[proposal_id]`
  currently holds only in memory — `steps` (each with its roll data, mutations, and
  `depends_on` edges), the flattened `mutations` list, and an open/closed flag. Lives under the
  chronicle directory, one record per open proposal, keyed by `proposal_id`.
- **`chronicle.yaml`'s `pending.rolled`**: unchanged in shape (still just the `proposal_id`
  string) — continues to name *which* proposal is open for session-interruption purposes; the
  full contents live in the new persisted-proposal record this feature adds.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A proposal staged by one `python3 -m wyrd.client propose` subprocess invocation can
  be committed by a separate, later subprocess invocation, with the resulting state on disk
  identical to committing in the same process.
- **SC-002**: The same holds for `discard`: a separate, later subprocess invocation discards a
  proposal staged by an earlier one, with no state written.
- **SC-003**: Every existing propose/commit/discard/reroll test (in-process) continues to pass
  unmodified, demonstrating no behavioural regression from adding persistence.
- **SC-004**: An unknown or already-resolved proposal id, tested via a separate subprocess
  invocation, produces the same error message as the existing in-process behaviour.

## Assumptions

- The chronicle directory's location is available to a `commit`/`discard`/`reroll` CLI
  invocation the same way it already is to `propose` (an existing CLI convention, e.g. a
  `--chronicle` argument or cwd-relative default) — this feature does not change how the CLI
  locates the chronicle, only what it persists inside it.
- "Separate CLI invocation" means a distinct OS process (`subprocess.run`), not a distinct
  in-process call — this is what the regression test in scope must exercise directly rather than
  assume equivalent.
- Persisted proposal records are an implementation detail of chronicle state, not a new kind of
  entity file under `entities/`/`overlay/` — they do not participate in the entity id/link
  invariants docs/design/22-state.md defines for entities.
- Concurrent, simultaneous `propose` calls for the same actor from two truly concurrent processes
  are out of scope (Wyrd is a solo, single-player-at-a-time engine); "one open proposal per
  actor" is a correctness rule for sequential CLI invocations, not a concurrency-safety guarantee.
- FR-009 ("one open proposal per actor") is enforced today only by there being no call site that
  starts a second proposal without resolving the first — `chronicle.record_rolled` (the function
  that would name which proposal is open) is not yet wired into `propose` by anything, a
  pre-existing gap from #328's own scoping, not introduced or closed by this feature. This
  feature makes `commit`/`discard`/`reroll` work correctly across processes for whatever
  proposals already exist; it does not add new enforcement of "only one at a time," which remains
  a follow-up.
