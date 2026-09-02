# Phase 0 Research: Propose/commit/discard core

No `NEEDS CLARIFICATION` markers were present in the Technical Context — the design document
(`docs/design/31-action-resolution.md`) and the existing `engine/wyrd/` codebase already answer
every open question this feature would otherwise need to research.

## Decision: proposal storage is an in-memory dict, not a file

**Rationale**: `docs/design/31-action-resolution.md` states a proposal is "an unpersisted,
in-memory ... record" and the engine has no backend/daemon (`CLAUDE.md`, `docs/design/27-
tooling.md`) — a proposal only needs to survive within one process's lifetime, between a
`propose` call and its matching `commit`/`discard`.

**Alternatives considered**: writing a proposal to a temp file (rejected — adds durability the
design explicitly does not ask for, and complicates "nothing writes to state" verification);
returning the full proposal to the caller and requiring it be passed back whole on `commit`
(rejected — the design's own worked examples show `commit`/`discard` taking only a
`proposal_id`, not the full payload).

## Decision: mechanic registry is a small closed dict, seeded with `ordinary-test` and `exposure`

**Rationale**: `docs/design/31-action-resolution.md`'s `mechanic` parameter is "a closed
vocabulary matching the engine's own rules, never a setting addition." This feature's own two
worked examples only exercise `exposure`; `ordinary-test` (a test with no implied mutation on
any outcome) is included because User Story 1's Acceptance Scenario 3 ("an outcome with no
implied consequence ... returns an empty mutations list") needs at least one such mechanic to
demonstrate against, and it is the simplest possible entry in the registry.

**Alternatives considered**: a mechanic string dispatched via a giant `if/elif` chain in
`propose` itself (rejected — `docs/design/31-action-resolution.md` frames mechanics as
independently-owned rules; a dict of `mechanic_name -> resolver_fn` keeps each mechanic's
mutation logic in one place and makes "unknown mechanic" a single lookup-miss check, matching
this feature's Edge Cases section).

## Decision: `exposure`'s mutation rule reproduces exactly the design doc's two worked examples

**Rationale**: `docs/design/03-rules.md` §4 states Exposure tiers (minor 1 / moderate 2 / major
3) are "reduced by degrees of success," but neither of `docs/design/31-action-resolution.md`'s
own worked examples exercises a successful resistance — both are failures, gaining the full
(possibly Fault-Line-biased) tier value with no reduction. Implementing exactly what both worked
examples show (full tier value gained on failure, nothing on success) satisfies this feature's
own SC-001 without speculating about a degrees-of-success reduction formula that is genuinely a
separate, not-yet-implemented piece of `03-rules.md` §4 (Fault Line bias is likewise out of
scope here — this feature's `exposure` mutation takes an already-decided tier value from the
caller, the same way `declaration_bonus` is already-decided per FR-001, rather than computing
Fault Line alignment itself).

**Alternatives considered**: implementing the full degrees-of-success reduction and Fault Line
bias now (rejected — out of this feature's stated scope, no acceptance criterion requires it,
and guessing the exact reduction formula from one sentence would risk exactly the kind of
unverified arithmetic `CLAUDE.md` warns against; "Check the maths" applies to code as much as to
design prose).
