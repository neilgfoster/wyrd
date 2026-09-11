# Data Model: Chronicle transaction lifecycle

## `pending` (sub-field of `chronicle.yaml`, already round-tripped opaquely by #325)

```yaml
pending:
  beat: <beat-id> | null
  awaiting: <string describing the outstanding decision> | null
  rolled: <proposal-id string, as returned by resolution.propose/propose_batch> | null
```

- The whole `pending` value may be `null` (nothing interrupted) — the existing #325 default.
- `beat`/`awaiting` and `rolled` are cleared **independently** (FR-008): either sub-field may be
  non-null while the other is null (edge cases in spec.md).
- **Validation**: `beat` and `awaiting` are set and cleared together — `beat` non-null with
  `awaiting` null (or vice versa) is not a state this module ever produces, though it is not
  actively rejected on read (defensive, not authoritative: this feature doesn't own the writer of
  every `pending` mutation elsewhere in the engine).
- `rolled`, when non-null, MUST resolve as an open proposal id in `resolution._open_proposals` at
  the moment it is read for a discard — if it does not (already committed/discarded through some
  other path, or from a previous engine run whose in-memory registry is gone), the discard call is
  a no-op (mirrors `resolution.discard`'s own convention for an id that doesn't resolve).

## Functions this feature adds (`engine/wyrd/chronicle.py`, new module)

- **`resume_state(pending: dict | None) -> dict | None`** — returns `{"beat", "awaiting"}` to
  resume from, or `None` if `pending` is `None` or both sub-fields are null. Pure function, no I/O
  (FR-001, FR-002).
- **`discard_at_rally(pending: dict | None) -> dict`** — given the current `pending` value,
  returns the new `pending` value with `rolled` cleared, and (if `rolled` named an id) the id to
  pass to `resolution.discard`. Does not call `resolution.discard` itself — pure, so a caller
  (`rally.apply_rally`) performs the actual discard and the actual write (FR-003, FR-004).
- **`discard_moot(pending: dict | None) -> dict`** — same shape as `discard_at_rally`, for the
  explicit in-session moot-discard call site (FR-005, FR-006); behaviourally identical to
  `discard_at_rally` (both just clear `rolled` and report what to discard) — kept as two named
  entry points because they are triggered by different callers at different points in the loop,
  matching `wyrd.session`'s existing naming convention (`set_pending`/`resume_from_pending`/
  `clear_pending` are similarly small named wrappers rather than one generic function).
- **`record_rolled(pending: dict | None, proposal_id: str) -> dict`** — returns the new `pending`
  value with `rolled` set to `proposal_id`. Raises `ValueError` if `pending.rolled` is already
  non-null (FR-007: at most one open proposal per actor — this is the single write path that sets
  `rolled`, so this is where the constraint is actually enforced).

## Reconciling `wyrd.session`'s pre-existing helpers

`wyrd.session.set_pending`/`resume_from_pending`/`clear_pending` (shape `{beat_id, action,
set_at}`) predate `chronicle.yaml`'s real schema and are not called from anywhere that persists to
`chronicle.yaml` today (grep confirms zero call sites outside their own definitions and tests).
This feature supersedes them: `chronicle.resume_state`/the `pending.beat`/`pending.awaiting`
sub-fields take over their role using the real schema; `session.py`'s three functions and their
tests are removed as part of implementation, rather than left as a second, never-wired mechanism
alongside the one this feature actually connects to `chronicle.yaml` (CLAUDE.md's "don't invent a
second mechanism" rule, applied here even though the issue's own wording was about `pending.rolled`
specifically — the same reasoning covers `pending.beat`/`awaiting` too).
