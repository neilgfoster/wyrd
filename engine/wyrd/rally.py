"""The Rally: recovery, advance award and commit.

docs/design/16-session.md: "The Rally -- the save point" -- between beats comes a Rally, a short
pause with mechanical weight. On a Rally: Strain recovers 1, Stamina recovers 1
(docs/design/03-rules.md section 2, ADR 0020's rate), the GM assesses the beat just closed and may
award an advance, and state is written and the chronicle is committed. This module implements the
Rally itself: `apply_recovery` (the fixed Strain/Stamina amounts, always applied, never a roll or
GM discretion), and `apply_rally` (recovery plus an optional advance-award hook plus the
persist/commit step, in that order).

The advance award reuses `engine/wyrd/advancement.py`'s existing `award_advance` unchanged -- this
module performs no award logic of its own, per CLAUDE.md's reuse-over-invention rule and #310's
own out-of-scope note. The persist/commit step mirrors `wyrd.session.run_close`'s
injected-callable shape: this module guarantees the step runs exactly once, at the right point,
but does not implement what "write state" or "commit the chronicle" concretely do -- that depends
on the chronicle state layer under #300, which does not exist yet.

Every Rally also discards any proposal left open in `pending.rolled` past the end of a session
(#328, docs/design/22-state.md § Invariants -> Transaction lifecycle): `apply_rally` calls
`wyrd.chronicle.discard_at_rally` unconditionally and, when it reports an id to discard, calls
`wyrd.resolution.discard` on it before the recovery/award/commit sequence -- this is always
checked, never discretionary, though a `None`/already-clear `pending.rolled` makes it a no-op.

This module is invoked once #309's session loop (`wyrd.session`) reaches a beat boundary; it does
not itself decide when a beat has closed.

Python 3.11+, standard library only.
"""

from __future__ import annotations

from collections.abc import Callable

from wyrd import advancement, chronicle, resolution


def apply_recovery(strain: int, stamina: int, stamina_max: int) -> dict:
    """Apply a Rally's fixed recovery: Strain -1 (floored at 0), Stamina +1 (capped at
    `stamina_max`). No roll, no discretion over the amount -- docs/design/03-rules.md sections 2
    and 5, ADR 0020's rate (Strain's own rate, reused rather than a second number).

    Returns {"strain": ..., "stamina": ...}.
    """
    return {
        "strain": max(strain - 1, 0),
        "stamina": min(stamina + 1, stamina_max),
    }


def apply_rally(
    strain: int,
    stamina: int,
    stamina_max: int,
    advancement_record: dict,
    *,
    trigger: str | None = None,
    pending: dict | None = None,
    commit: Callable[[], None] | None = None,
) -> dict:
    """Apply a full Rally: fixed recovery, discard of any proposal left open in `pending.rolled`,
    an optional advance award, then the persist/commit step, in that order.

    `trigger`, when given, is passed straight to `advancement.award_advance(trigger,
    advancement_record)` -- this function performs no award logic of its own, and a refused claim
    (unknown trigger, already awarded, session ceiling) is surfaced unchanged rather than hidden.
    The fixed recovery above applies identically whether or not a trigger is given, and whether or
    not a given trigger is accepted -- a Rally with no award, or a refused one, is still a valid
    Rally (docs/design/16-session.md).

    `pending`, when given, is the chronicle's current `pending` value (docs/design/22-state.md).
    `wyrd.chronicle.discard_at_rally` is always called against it -- unconditionally checked,
    though a no-op when `pending` is `None` or `pending["rolled"]` is already `None` -- and, when
    it reports an id to discard, `wyrd.resolution.discard` is called on that id before recovery is
    computed. This is how an uncommitted proposal that survived past the end of a session is
    cleared "at the next Rally," never carried forward (#328).

    `commit`, when given, is called exactly once, after recovery, the pending-discard and the
    award (if any) are all computed -- never conditional on an award having been claimed or
    accepted. Omitting it is a valid Rally with nothing persisted yet, mirroring
    `wyrd.session.run_close`'s own injected-callable shape for the same reason: the chronicle
    state layer this step would write to (#300) does not exist yet.

    Returns {"strain": ..., "stamina": ..., "award": <award_advance's own result dict, or None if
    no trigger was given>, "pending": <pending with rolled cleared, or the input unchanged if it
    was already None/clear>}.
    """
    recovered = apply_recovery(strain, stamina, stamina_max)

    discard_result = chronicle.discard_at_rally(pending)
    if discard_result["to_discard"] is not None:
        resolution.discard(discard_result["to_discard"])
    new_pending = discard_result["pending"]

    award = None
    if trigger is not None:
        award = advancement.award_advance(trigger, advancement_record)

    if commit is not None:
        commit()

    return {
        "strain": recovered["strain"],
        "stamina": recovered["stamina"],
        "award": award,
        "pending": new_pending,
    }
