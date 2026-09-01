# Phase 0 research: Core opposed-test resolution

No `[NEEDS CLARIFICATION]` markers remained. This file records the decisions inherited from
existing design documents and from #221's precedent.

## Reuse of #221's dice primitive

- **Decision**: Call `rules.roll_d100(seed=seed)` from within the new `opposed_test` function,
  rather than any new dice-rolling code.
- **Rationale**: `docs/design/27-tooling.md`: "the dice roller in particular is non-negotiable."
  A second roll implementation would be a second place a d100 could silently diverge from the
  first — exactly the erosion principle 1 exists to prevent.
- **Alternatives considered**: Inlining `random.Random(seed).randint(1, 100)` again was
  rejected — it would duplicate #221's already-tested primitive for no benefit.

## `effective%` clipping

- **Decision**: `effective_pct = max(5, min(95, 50 + (skill - opponent)))`.
- **Rationale**: `docs/design/03-rules.md`'s "Opposed tests" subsection states the formula
  exactly: `clip(50 + (skill - opponent_skill_or_baseline), 5, 95)`.
- **Alternatives considered**: None — the formula is fully specified, not a design choice this
  feature makes.

## Degrees only on success

- **Decision**: The result dict omits (or sets `None`) a `degrees` key on failure, rather than
  computing and reporting a (possibly negative or meaningless) value.
- **Rationale**: `docs/design/03-rules.md`: "A failure simply fails the action. There is no
  resisting-side roll and no degrees comparison to have skipped." Reporting a degrees value on
  failure would imply a comparison the spec explicitly says does not happen.
- **Alternatives considered**: Always computing `tens(effective_pct) - tens(roll)` regardless of
  success was rejected — it produces a numerically well-defined but semantically meaningless
  value on failure (the doc's base rule frames degrees as "degrees of *success*").

## Wyrd die independence

- **Decision**: Read the Wyrd die from `roll % 10` unconditionally, before checking success, and
  never let the success/failure branch affect which units-digit table is consulted.
- **Rationale**: `docs/design/03-rules.md`: "The units digit is uniform within both the success
  and failure sets, so the axes are genuinely independent." Implementing it as a shared
  first step (read units digit → look up table) before the success branch, rather than inside
  either branch separately, is what makes the independence structurally obvious rather than
  merely tested-for.
- **Alternatives considered**: Computing the Wyrd die separately inside the success and failure
  branches (duplicated logic) was rejected — correct today, but an easy place for the two copies
  to drift apart under a future edit.

## Scope boundary: Taint and Omen carryover

- **Decision**: Implement only the base (Taint-free) Wyrd die table; do not implement Taint's
  widening of the Ill Omen band, and do not implement the Omen's ±10 carryover onto the next
  roll.
- **Rationale**: Both require chronicle state this feature's stateless primitive does not hold —
  Taint doesn't exist as tracked state yet (#215), and the carryover modifier is already
  specified as a separate concern (`specs/069-omen-carryover/`). Building either here would mean
  inventing an ad hoc state mechanism this feature isn't scoped to own.
- **Alternatives considered**: Accepting an optional `taint: int` parameter now, "for later," was
  rejected — YAGNI: no caller exists yet that has a Taint value to pass, and the parameter's
  correct behavior can't be tested until #215 exists to supply real values.

## No state I/O

- **Decision**: `verbs.opposed_test` calls no `state.save`/`state.load` at all — unlike #221's
  `verbs.roll`, which persists `last_roll`.
- **Rationale**: spec.md's Key Entities section states this explicitly: no later feature yet
  depends on reading a stored opposed-test result back, so persisting one now would be
  speculative state with no reader.
- **Alternatives considered**: Persisting a `last_opposed_test` field, mirroring `roll`'s
  pattern, was rejected for the same YAGNI reason — nothing reads it yet, and inventing its
  shape now risks guessing wrong about what a real caller (combat, #212) will actually need.
