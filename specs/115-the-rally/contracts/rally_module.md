# Contract: `wyrd.rally`

This is a library, not a network service -- its "contract" is the public function surface
`engine/wyrd/rally.py` exposes, matching the shape `session.py`/`advancement.py` already use
(plain functions over plain dicts, no classes, standard library only).

```python
def apply_recovery(strain: int, stamina: int, stamina_max: int) -> dict:
    """Apply a Rally's fixed recovery.

    Returns {"strain": <strain - 1, floored at 0>, "stamina": <stamina + 1, capped at
    stamina_max>}. No roll, no discretion over the amount -- docs/design/03-rules.md section 2/5,
    ADR 0020's rate.
    """

def apply_rally(
    strain: int,
    stamina: int,
    stamina_max: int,
    advancement_record: dict,
    *,
    trigger: str | None = None,
    commit: Callable[[], None] | None = None,
) -> dict:
    """Apply a full Rally: fixed recovery, an optional advance award, then the persist/commit
    step, in that order.

    `trigger`, when given, is passed straight to `advancement.award_advance(trigger,
    advancement_record)` -- this function performs no award logic of its own. `commit`, when
    given, is called exactly once, after recovery and the award (if any) are both computed --
    never conditional on an award having been claimed or accepted (FR-003/FR-004).

    Returns {"strain": ..., "stamina": ..., "award": <award_advance's own result dict, or None if
    no trigger was given>}.
    """
```

## Non-goals (explicitly out of scope, see spec.md Assumptions)

- No Downtime-phase recovery/undertaking logic (Recover, Mend, Rest, Pursue, Cultivate, Learn,
  Ask) -- a separate feature under this epic (#311 and beyond).
- No reimplementation of `advancement.award_advance`'s trigger vocabulary, session ceiling, or
  refusal shapes -- `apply_rally` calls it unchanged.
- No concrete persist/commit content -- `apply_rally`'s `commit` parameter only sequences a
  caller-supplied callable; the chronicle state layer that callable would use (#300) does not
  exist yet, mirroring `wyrd.session.run_close`'s own scoping.
- No decision about *when* a Rally becomes available to a caller -- that is #309's session loop
  (`wyrd.session`), which this module is invoked by, not the reverse.
