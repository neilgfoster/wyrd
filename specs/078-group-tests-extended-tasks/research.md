# Phase 0 research: Group tests and extended tasks

No `[NEEDS CLARIFICATION]` markers remained.

## Member skill representation

- **Decision**: `member_skills: list[int | None]`, where `None` means "no relevant skill at
  all" and is treated as exactly 10 (the untrained flat rate) during selection.
- **Rationale**: `docs/design/03-rules.md`: "A member with no relevant skill at all is tested at
  the untrained 10%." `None` is the clearest way to distinguish "genuinely has 0% at something"
  (a real, if very low, skill value) from "has no relevant skill to test at all" — the two are
  different facts about a character, and collapsing them to the same integer would lose that
  distinction for a caller who has it.
- **Alternatives considered**: Requiring the caller to pre-substitute 10 for any untrained
  member was rejected — it pushes documented engine behavior (the untrained rate) out to every
  caller to remember and get right, when it's a fixed rule this feature can hold once.

## Group test as thin composition over `opposed_test`

- **Decision**: `group_test(member_skills, mode, opponent, seed=None, **opposed_test_kwargs) ->
  dict` selects the skill via `select_group_skill`, then calls `opposed_test(selected_skill,
  opponent, seed=seed, **opposed_test_kwargs)` and merges in `member_skills`, `mode`,
  `selected_skill` fields.
- **Rationale**: "A group acts, a group rolls once" — reusing `opposed_test` unchanged is what
  guarantees exactly one roll (SC-002) by construction, and passing `**opposed_test_kwargs`
  through means declaration/assistance (#223) already compose with a group test for free,
  without this feature reimplementing or re-testing them.
- **Alternatives considered**: Duplicating `opposed_test`'s roll/degrees/Wyrd-die logic inline
  in a new `group_test` function was rejected — exactly the kind of drift-prone duplication
  `docs/design/27-tooling.md`'s "the dice roller is non-negotiable" warns against.

## Extended-task interval as thin composition over `opposed_test`

- **Decision**: `resolve_extended_interval(skill, opponent, progress, target, seed=None,
  **opposed_test_kwargs) -> dict` calls `opposed_test` once, computes `gained = max(1,
  result["degrees"])` if `result["success"]` (treating a `no_roll` result's automatic success as
  `gained = 1`, per spec.md's Assumption), else `gained = 0`, and returns `progress + gained`
  plus `done = (new_progress >= target)`.
- **Rationale**: "One test per interval... a success adds its degrees, minimum 1... a failed
  interval is spent and gains nothing... the Wyrd die is read every interval, from that
  interval's natural roll, as in any test" — every one of these is already exactly what
  `opposed_test` produces; this function's only new logic is the progress arithmetic itself.
- **Alternatives considered**: A separate stateful "extended task" object/class tracking its own
  progress internally was rejected — spec.md's Assumptions are explicit that persisting progress
  across real intervals is out of scope; a plain progress-in/progress-out function needs no
  object at all and keeps the state-I/O boundary exactly where #222/#223 already drew it.

## The `removes_risk`/extended-interval combination

- **Decision**: Treat `opposed_test`'s `no_roll: True, success: True, degrees: None` result as
  `gained = 1` for an extended-task interval — the minimum, per the closest existing rule ("a
  success adds its degrees, minimum 1").
- **Rationale**: `docs/design/03-rules.md` never states what a no-roll declaration is "worth" in
  degrees, because degrees is a d100-derived concept that doesn't exist for an action with no
  roll. The minimum-1 floor is the one number the doc does commit to for any success, so it's
  the least invented answer available, and is recorded as an explicit Assumption rather than
  silently guessed.
- **Alternatives considered**: Rejecting a `removes_risk` declaration outright on an extended
  interval (raising an error) was considered, but rejected — nothing in the doc suggests
  declaration doesn't apply to extended-task intervals ("one test per interval," and every other
  test-shaping rule composes freely), so refusing the combination would be inventing a
  restriction the source material doesn't state either.

## Scope-to-target table

- **Decision**: Not implemented as a lookup in this feature — the caller passes whatever integer
  `target` it has already chosen.
- **Rationale**: spec.md's Assumptions: the table (2/4/6 for night/season/great-labour) is
  presentational guidance for a GM choosing a target, not a closed enumerable input the way
  declaration categories are (#223) — a GM can and does choose targets outside that table (the
  doc's own "the scale has to come from the expected gain, not from a tidy-looking number" from
  `check_assistance.py`'s docstring implies the numbers are a starting point, not an exhaustive
  set). Encoding it as a mandatory lookup would falsely imply only three target values are legal.
- **Alternatives considered**: A convenience `extended_task_target(scope: str) -> int` lookup
  mirroring `declaration_bonus`'s pattern was considered. Rejected for the reason above — unlike
  declaration's five categories (a genuinely closed set the doc treats as exhaustive), the
  target table is illustrative, and adding the lookup risks the same "closed-set" reading a
  reviewer would reasonably apply to `declaration_bonus`.
