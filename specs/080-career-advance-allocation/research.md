# Phase 0 research: Career graph and advance allocation

No `[NEEDS CLARIFICATION]` markers remained.

## Allocation as a sequence of actions, not a target-shape dict

- **Decision**: An allocation is `list[{"action": "open"|"raise", "skill": str}]`, replayed in
  order, rather than a caller-supplied `{skill: target_pct}` mapping the engine reverse-engineers
  into a cost.
- **Rationale**: `docs/design/11-character-creation.md`'s table names two distinct *actions*
  ("open a skill... at 25%" / "+5% to a skill already open"), each costing 1 — the ordering
  itself carries a real rule (FR-008/FR-009: you cannot raise before opening, cannot open twice).
  A target-shape dict would have to re-derive that ordering constraint by inference (was this
  skill "opened then raised" or "raised from an assumed prior open"?) instead of the caller
  simply stating what they did.
- **Alternatives considered**: `{skill: target_pct}` was rejected — it hides exactly the
  information (open-before-raise, one open per skill) the rules depend on, and would need a
  guessed reconstruction of the action sequence to validate FR-008/FR-009 at all.

## Cap resolution when a skill appears in both career and ancestry

- **Decision**: `effective_cap(skill) = max(career.skills.get(skill, -1),
  ancestry.skills.get(skill, -1) if ancestry else -1)` — the higher of the two, per spec.md's
  Assumption.
- **Rationale**: The ancestry's role is to widen *eligibility*, never to narrow what a career
  already permits; taking the lower cap would let an ancestry accidentally restrict a career
  skill's growth, which `docs/design/11-character-creation.md`/ADR 0040 never describes as
  ancestry's effect.
- **Alternatives considered**: Rejecting a career/ancestry pair with a cap conflict outright was
  considered, but rejected — no setting loader exists yet to make "a setting declared a
  conflicting cap" a real, checkable event; inventing a rejection for a case this feature can't
  yet observe from real data would be speculative.

## Reusing #229's skill-scale constants

- **Decision**: `open` sets a skill to `rules.SKILL_OPEN_VALUE` (25); `raise` adds
  `rules.SKILL_ADVANCE_STEP` (5). Both imported from `rules.py`, not redefined in `career.py`.
- **Rationale**: `docs/design/27-tooling.md`'s "adding a verb means adding a catalog entry and a
  function; nothing else changes" implies the converse too — a constant that already exists is
  reused, not duplicated, so there is exactly one place `25`/`5` could ever drift from the
  documented scale.
- **Alternatives considered**: Re-declaring `25`/`5` locally in `career.py` was rejected as
  needless duplication of #229's already-established constants.

## Total-count and minimum-opened checks: computed once, not per-action

- **Decision**: `validate_allocation` first checks `len(actions) == 8` and counts distinct
  `open` actions `>= 2` as whole-allocation properties, before replaying actions one at a time
  for per-action rules (cap, eligibility, open-before-raise).
- **Rationale**: These two rules are properties of the *whole* sequence, not any single action —
  checking them first gives a clearer, single-cause rejection message (SC-002's "distinct,
  correctly-attributed reason") rather than a confusing per-action error for what's actually a
  whole-allocation shape problem (e.g. only 6 actions given, none individually invalid).
- **Alternatives considered**: Checking everything in one single pass was considered, but
  rejected — interleaving whole-sequence checks with per-action state (current skill values,
  which skills are open) makes the failure-reason attribution murkier for no performance benefit
  at this scale (at most 8 actions).
