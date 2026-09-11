"""`chronicle.yaml`'s `pending` field: real semantics on top of #325's opaque round-trip.

docs/design/22-state.md § Interrupted sessions and § Invariants -> Transaction lifecycle:
`pending: {beat, awaiting, rolled}` names an interrupted beat's outstanding decision
(`beat`/`awaiting`) and an open, uncommitted proposal that survived past the end of a session
(`rolled`). This module owns the semantics of those three sub-fields -- resuming from them, and
discarding a surviving proposal -- as pure functions with no I/O; a caller (`wyrd.rally.apply_rally`
for the automatic Rally-boundary case, or a live session's own moot-discard call site) is
responsible for actually calling `wyrd.resolution.discard` on the id this module reports and for
persisting the returned `pending` value.

**Reuses `wyrd.resolution`'s `propose`/`commit`/`discard` unchanged** (docs/design/31-action-
resolution.md, ADR 0050) -- this module adds no second proposal mechanism, per CLAUDE.md's
explicit constraint on this issue (#328): `pending.rolled` is the one place an open proposal
lives, never a parallel registry.

**Supersedes `wyrd.session`'s pre-#328 `set_pending`/`resume_from_pending`/`clear_pending`**,
which used an ad hoc shape (`{beat_id, action, set_at}`) that predates `chronicle.yaml`'s actual
schema and was never wired to a real `pending` field (zero call sites outside their own tests) --
see specs/125-chronicle-transaction-lifecycle/data-model.md.

Python 3.11+, standard library only.
"""

from __future__ import annotations


def resume_state(pending: dict | None) -> dict | None:
    """The `{"beat", "awaiting"}` a new session should resume from, or `None`.

    `None` both when `pending` itself is `None` (nothing interrupted) and when `pending["beat"]`
    and `pending["awaiting"]` are both `None` (only a surviving proposal was recorded, the beat
    itself had already resolved) -- docs/design/22-state.md's two sub-fields are read together
    here since they name one resumable decision, independent of whatever `pending["rolled"]`
    separately holds (FR-008: the two clear independently).
    """
    if pending is None:
        return None
    beat = pending.get("beat")
    awaiting = pending.get("awaiting")
    if beat is None and awaiting is None:
        return None
    return {"beat": beat, "awaiting": awaiting}


def _discard(pending: dict | None) -> dict:
    """Shared body for `discard_at_rally` and `discard_moot`: clear `rolled`, report what (if
    anything) the caller must pass to `resolution.discard`.

    Returns `{"pending": <new pending, rolled cleared>, "to_discard": <the id that was in
    rolled> | None}`. A `None` or already-`rolled: None` input is a no-op, never an error --
    mirrors `resolution.discard`'s own convention for an id that does not resolve.
    """
    if pending is None:
        return {"pending": None, "to_discard": None}
    to_discard = pending.get("rolled")
    new_pending = dict(pending)
    new_pending["rolled"] = None
    return {"pending": new_pending, "to_discard": to_discard}


def discard_at_rally(pending: dict | None) -> dict:
    """Discard a proposal that survived past the end of a session, at the first Rally reached.

    docs/design/22-state.md: "Cleared at the next Rally... an abandoned proposal is implicitly
    discarded once the character next recovers, not the moment the session ends." Called by
    `wyrd.rally.apply_rally` every Rally, unconditionally checked -- a no-op when `pending` is
    `None` or `pending["rolled"]` is already `None` (the ordinary case; spec.md Edge Cases).
    """
    return _discard(pending)


def discard_moot(pending: dict | None) -> dict:
    """Explicitly discard a live proposal whose situation has gone moot before `commit` or
    `discard` was called for it -- the in-session complement to `discard_at_rally`
    (docs/design/22-state.md: "a proposal a player is actively deciding on... becomes moot before
    either commit or discard is called... is explicitly discarded rather than left open"). Same
    shape and behaviour as `discard_at_rally`; kept as a separate named entry point because the
    two are invoked from different call sites in the session/Rally loop, matching
    `wyrd.session`'s existing small-named-wrapper convention.
    """
    return _discard(pending)


def record_rolled(pending: dict | None, proposal_id: str) -> dict:
    """Record `proposal_id` as the actor's one open proposal.

    Raises `ValueError` if `pending["rolled"]` is already non-null -- docs/design/22-state.md:
    "an engine session never carries more than one genuinely open proposal per actor at a time."
    This is the single write path that sets `rolled`, so it is where that invariant is actually
    enforced (FR-007) -- a caller must discard (`discard_at_rally`/`discard_moot`) or commit the
    existing one before recording a new one.
    """
    base = pending if pending is not None else {"beat": None, "awaiting": None, "rolled": None}
    if base.get("rolled") is not None:
        raise ValueError(
            f"actor already has an open proposal ({base['rolled']!r}); "
            "discard or commit it before recording another"
        )
    new_pending = dict(base)
    new_pending["rolled"] = proposal_id
    return new_pending
