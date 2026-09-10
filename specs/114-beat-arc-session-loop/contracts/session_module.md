# Contract: `wyrd.session`

This is a library, not a network service — its "contract" is the public function surface
`engine/wyrd/session.py` exposes, matching the shape `entity.py`/`party.py` already use (plain
functions over plain dicts, no classes, standard library only).

```python
LOOP_STEPS = ("load", "orient", "recap", "beat", "close")
SESSION_SHAPES = ("single_beat", "interlude", "downtime", "extended")

def assert_beat_has_no_children(entities: dict[str, dict]) -> dict:
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

def advance_loop(loop_state: dict, to_step: str) -> dict:
    """Transition `loop_state` to `to_step`, enforcing load -> orient -> recap -> beat ->
    (beat | close), with orient required (elapsed_applied) before recap, and close reachable at
    most once. Raises ValueError naming the illegal transition if the move isn't permitted.
    Returns the updated loop_state (does not mutate the input in place).
    """

def set_pending(beat_id: str, action: str) -> dict:
    """A pending marker: {"beat_id", "action", "set_at"}, for a beat interrupted mid-resolution."""

def resume_from_pending(pending: dict) -> str:
    """The action to resume from, given a pending marker -- just `pending["action"]`, exposed as
    a named entry point so callers don't reach into the marker's shape directly.
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
- No changes to `wyrd.entity`'s public surface — `assert_beat_has_no_children` is additive, built
  on `entity.children_of`, not a modification of `entity.py` itself.
