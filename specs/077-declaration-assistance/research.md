# Phase 0 research: Declaration and assistance bonuses

No `[NEEDS CLARIFICATION]` markers remained. This records decisions inherited from existing
design documents, an existing check script, and #221/#222's precedent.

## Declaration category representation

- **Decision**: A closed dict `DECLARATION_BONUSES = {"specific": 10, "specific_leveraging": 20,
  "brief": 0, "against_nature": -20, "removes_risk": None}`, where `None` is the sentinel for
  "no roll, automatic success" rather than a numeric bonus.
- **Rationale**: `docs/design/03-rules.md`'s Declaration table gives exactly these five rows.
  `None` (rather than e.g. `float("inf")`) is the clearest sentinel in Python for "not a number
  at all" — a caller who forgets to special-case it gets a `TypeError` on arithmetic rather than
  a silently wrong large bonus.
- **Alternatives considered**: A separate boolean `removes_risk` flag alongside a numeric bonus
  was rejected — it would let a caller supply both a bonus and `removes_risk=True`
  simultaneously, an invalid combination the type itself should rule out rather than requiring
  a runtime check to catch.

## Assistance formula and cap

- **Decision**: `assistance_bonus(helper_skill, can_attempt=True) -> int` computes
  `min(helper_skill // 10, 10)` if `can_attempt`, else `0`.
- **Rationale**: `docs/design/03-rules.md`'s Assistance subsection states the formula exactly
  ("a tenth of the helper's own skill, rounded down, to a ceiling of +10"), and
  `specs/011-assistance-and-group-tests/check_assistance.py` already computed and validated this
  exact divisor (10) and cap (10) against realistic skill values — this feature implements the
  already-checked numbers rather than re-deriving them.
- **Alternatives considered**: None — the formula and its constants were already settled by
  spec 011's own check script; this feature is the first to turn that checked formula into
  engine code.

## Extending `opposed_test` vs. a new function

- **Decision**: Add three optional keyword parameters (`declaration: str | None = None`,
  `helper_skill: int | None = None`, `helper_can_attempt: bool = True`) to the existing
  `rules.opposed_test`, defaulting to no modifier — rather than a new
  `modified_opposed_test` function.
- **Rationale**: The issue and spec frame this as "modify the base opposed test... rather than
  being separate mechanics" (#223's own Context). A second function would fork the resolution
  logic #222 already tested; a caller who forgot to switch to it would silently miss the
  modifiers. Optional keyword arguments defaulting to "off" preserve #222's exact existing
  three-argument call shape (verified directly by SC-003), which is what "not a new resolution
  path" actually requires in code, not just in framing.
- **Alternatives considered**: A separate `resolve_modifiers(skill, declaration, helper_skill,
  helper_can_attempt) -> int` that the caller adds to `skill` themselves, leaving `opposed_test`
  untouched, was considered. Rejected for the `removes_risk` case specifically — that case
  isn't a skill modifier at all, it's "skip the roll entirely," which only `opposed_test` itself
  can act on (a bonus-only helper function has no roll to skip). Keeping `removes_risk` external
  to `opposed_test` while every other case flows through it would split one mechanic's handling
  across two different call sites for no benefit.

## `removes_risk` no-roll behavior

- **Decision**: When `declaration == "removes_risk"`, `opposed_test` returns immediately with
  `no_roll: True`, `success: True`, `roll: None`, `effective_pct: None`, `degrees: None`,
  `wyrd: "none"` — without calling `roll_d100` at all.
- **Rationale**: `docs/design/03-rules.md`: "a plan good enough to remove the risk should simply
  succeed" — this is a real absence of a roll, not a 100%-chance roll that happens to always
  pass (which would still consume a Wyrd die reading and a random call, contradicting "no roll").
- **Alternatives considered**: Resolving it as `effective_pct = 100` (guaranteed success but
  still rolling, still reading a Wyrd die) was rejected — it would still be a roll, and
  `docs/design/03-rules.md` is explicit that this case has none; the Wyrd die's "what else
  happened" framing doesn't apply to an action that never left the plan stage.
