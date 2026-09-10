# Contract: `wyrd.session`

This is a library, not a network service — its "contract" is the public function surface
`engine/wyrd/session.py` exposes, matching the shape `entity.py`/`party.py` already use (plain
functions over plain dicts, no classes, standard library only).

```python
LOOP_STEPS = ("load", "orient", "recap", "beat", "close")
SESSION_SHAPES = ("single_beat", "interlude", "downtime", "extended")

def check_beat_has_no_children(entities: dict[str, dict]) -> dict:
    """Check that no entity of type "beat" in `entities` has a child (via entity.children_of).

    Returns {"valid": True} or {"valid": False, "beat": <id>, "child": <id>} for the first
    violation found. A beat is never a container, regardless of how the arc above it is shaped.
    """

def narrate_beat(beat_id: str, mode: str) -> dict:
    """Produce a beat resolution record: {"beat_id", "mode", "resolved_at"}.

    `mode` must be "played" or "summarised"; raises ValueError otherwise. Never reads or writes
    any field on the beat entity's own frontmatter -- mode lives only on the returned record.
    """

def new_loop_state() -> dict:
    """A fresh session loop state: {"step": "load", "elapsed_applied": False,
    "beats_this_session": [], "closed": False}."""

def advance_loop(loop_state: dict, to_step: str, *, beat_id: str | None = None) -> dict:
    """Transition `loop_state` to `to_step`, enforcing load -> orient -> recap ->
    (beat -> (beat | close) | close), with orient required (elapsed_applied) before recap, and
    close reachable at most once. `recap -> close` is legal directly (FR-006: a session may have
    zero beats). `beat_id` is required when `to_step` is "beat" and is appended to
    `beats_this_session` -- this is the only way that list is populated. Raises ValueError naming
    the illegal transition if the move isn't permitted. Returns the updated loop_state (does not
    mutate the input in place).
    """

def run_close(steps: list[Callable[[], None]] | None = None) -> None:
    """Run close's sub-steps -- compaction, recap regeneration, commit -- in the order given.

    `steps` is a caller-supplied list of zero-argument callables; this module does not implement
    what any of them do (that depends on the chronicle state layer, #300, which does not exist
    yet) -- it only guarantees the order and that an empty/omitted list is a valid close.
    """

def set_pending(beat_id: str, action: str) -> dict:
    """A pending marker: {"beat_id", "action", "set_at"}, for a beat interrupted mid-resolution."""

def resume_from_pending(pending: dict) -> str:
    """The action to resume from, given a pending marker -- just `pending["action"]`, exposed as
    a named entry point so callers don't reach into the marker's shape directly.
    """

def clear_pending() -> None:
    """The value a caller stores in place of a pending marker once its beat resolves cleanly --
    this module holds no state itself, so "clearing" is the caller replacing that stored value
    with this function's result rather than this module deleting anything.
    """

def classify_shape(beats_this_session: list[str], used_dice: bool, ran_downtime: bool) -> str:
    """One of SESSION_SHAPES, computed from session facts. Never consulted by any function that
    produces player-facing narration text -- callers must not thread its result into a narration
    string.
    """
```

## Non-goals (explicitly out of scope, see spec.md Assumptions)

- No Rally logic (Strain/Stamina recovery, advance award, commit-on-Rally) — #310.
- No Downtime-phase internals (upkeep, undertakings, Mend, rest) — #311. `classify_shape` may
  *return* `"downtime"` as a label, but this module does not implement what happens inside one.
- No concrete compaction/recap-regeneration/commit logic — `run_close` only sequences whatever
  callables a caller supplies; the chronicle state layer those callables would use (#300) does
  not exist yet.
- No changes to `wyrd.entity`'s public surface — `check_beat_has_no_children` is additive, built
  on `entity.children_of`, not a modification of `entity.py` itself.
