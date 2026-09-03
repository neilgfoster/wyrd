# Data Model: Dread as a reaction/social test penalty

No new persistent entity or state field is introduced. This feature reads one existing field and
adds one new transient request field.

## Existing entity read

**Character/companion `dread`** (`engine/wyrd/character.py`, `creation.py`): an integer, already
present on every character/companion, already accrued correctly by
`resolution._stage_transformation_chain`. This feature reads it off `target_state["dread"]`;
it is never mutated here.

## Request field added

**`dread_witnessed`** (new field on a `propose`/`propose_batch` request, alongside `target`,
`difficulty`, `declaration_bonus`):

- **Type**: boolean
- **Default**: `False` (no penalty; matches today's behaviour for every existing caller)
- **Meaning**: `True` states the GM's already-decided fictional judgment that the test's `target`
  has been seen by someone who has not made their peace with the target's transformation
- **Applies only when**: `mechanic == "ordinary-test"`, a `target` is given, `dread_witnessed` is
  `True`, and the target's `dread` is nonzero
- **Effect**: `_resolve_ordinary_test` folds `-target_state["dread"]` into the same
  `declaration_bonus` term it already passes to `_resolve_test`, so Dread is stacked exactly the
  way every other points modifier already is — through `_resolve_test`'s own existing
  `max(5, min(95, skill + difficulty + declaration_bonus))` clamp. No separate floor is added: the
  spec's "clipped at 0" language (matching `docs/design/07-transformations.md`'s own prose) is
  satisfied by not introducing any *new* way for the percentage to go lower than the engine's
  existing floor already prevents — see Edge Cases below.
- **Threaded through**: `client.py` (`--dread-witnessed` CLI flag), `catalog.py` (`propose` tool
  schema), `verbs.propose`, `resolution.propose`/`propose_batch`, `_normalize_request`,
  `_stage_request`, `_resolve_ordinary_test`

## Edge Cases (data-level)

- `dread_witnessed=True` with no `target`: no-op — there is no Dread to read. Same result as
  `dread_witnessed=False`.
- `dread_witnessed=True`, target's `dread == 0`: no-op — nothing to subtract.
- `dread_witnessed=True` on a mechanic other than `ordinary-test` (e.g. `exposure`,
  `combat-attack`): the field is accepted but never read by those resolve functions — no effect,
  matching FR-006.
- `_resolve_test`'s existing clamp (`max(5, min(95, ...))`) already prevents the returned
  percentage from reading negative, regardless of how large a subtraction Dread contributes — so
  the spec's "clipped to no lower than 0%" acceptance criterion holds without adding any new clamp
  (a floor of 5 is stricter than 0, so the requirement is satisfied a fortiori). Reusing the
  existing clamp, rather than adding a second one, is what "applied the same way every other
  points modifier applies" means concretely.
