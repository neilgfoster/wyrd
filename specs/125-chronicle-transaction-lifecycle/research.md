# Research: Chronicle transaction lifecycle

No `NEEDS CLARIFICATION` markers were left in `plan.md`'s Technical Context — this feature
composes entirely from decisions already made elsewhere in the repo. This file records those
decisions and why each was picked over an alternative, for the record.

## Decision: a new `wyrd.chronicle` module owns `pending` semantics

**Rationale**: `pending` sits at the seam between three existing modules — `wyrd.state` (owns the
raw `chronicle.yaml` read/write), `wyrd.session` (owns the beat loop and already has stub
`set_pending`/`resume_from_pending`/`clear_pending` helpers), and `wyrd.rally` (owns the recovery
point that must trigger the discard). None of the three is the natural sole owner: putting it in
`state.py` would mix raw I/O with policy; putting it in `session.py` alone can't reach the Rally
trigger; putting it in `rally.py` alone can't express the load-time resume. A small dedicated
module keeps each of the three existing modules' own responsibility intact.

**Alternatives considered**: extend `wyrd.session`'s existing (pre-#328) `set_pending`/
`resume_from_pending`/`clear_pending` in place, since they already exist. Rejected: their shape
(`{beat_id, action, set_at}`) predates `chronicle.yaml`'s actual schema (`{beat, awaiting,
rolled}`, specs/122-chronicle-yaml-schema) and was never wired to a real `pending` field — it is a
scaffold `session.py`'s own docstring says nothing yet writes to. Reconciling means either
migrating those three functions onto the real shape in place, or superseding them from the new
module; Phase 1 (data-model.md) makes that call explicit rather than leaving both shapes live.

## Decision: single-open-proposal-per-actor enforced by the caller's own slot, not `resolution.py`

**Rationale**: `resolution.py`'s `_open_proposals` registry (module-level, in-memory) already
treats every proposal id as independently open or invalidated — it has no concept of "actor," so
teaching it a per-actor uniqueness rule would mean threading actor identity through a mechanism
that currently only deals in proposal ids, for a constraint that is really about `chronicle.yaml`
persistence, not the resolution engine's transaction bookkeeping. `pending.rolled` is already the
one persisted slot naming "this actor's currently open proposal, if any" — enforcing at-most-one
there (reject/replace on a second write attempt) is the existing mechanism the issue's own
constraint ("must not invent a second mechanism... for the same idea") points at.

**Alternatives considered**: add an actor-keyed dict inside `resolution.py` mirroring
`_open_proposals`. Rejected: this would be exactly the second mechanism CLAUDE.md/issue #328 warn
against — `pending.rolled` already is that mechanism; a second one duplicating it invites drift.

## Decision: Rally-discard is an optional step in `apply_rally`, not a separate call site

**Rationale**: `rally.py`'s `apply_rally` already threads an optional `commit` callable through in
a fixed order (recovery, award, persist). Discarding a still-open `pending.rolled` proposal is
naturally a fourth step in that same sequence — it must happen every Rally, unconditionally
checked (though a no-op when `pending.rolled` is already `None`), which matches `apply_rally`'s
existing "always applied, never discretionary" recovery step more than it matches the award step's
conditionality.

**Alternatives considered**: have `wyrd.session.run_close` perform the discard instead, since
`run_close` already sequences close-time steps. Rejected: the design doc ties discard to the
*Rally*, not to session close — a chronicle can reach many Rallies within one session, and the
discard must fire at the very next one, not deferred to whenever the session eventually closes.

## Decision: the moot-discard path is a thin, separately-invocable function, not folded into commit/discard

**Rationale**: `resolution.discard(proposal_id)` already does exactly what "abandon this proposal,
write nothing" needs. The moot-discard path this feature adds is a caller-level convenience that
(a) looks up the actor's current `pending.rolled` id, (b) calls `resolution.discard` on it if
present, (c) clears `pending.rolled` — composing the existing primitive rather than duplicating
its logic.

**Alternatives considered**: none seriously — this follows directly from reusing `discard`
unchanged, which the issue's scope explicitly calls for.
