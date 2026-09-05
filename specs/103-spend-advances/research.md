# Phase 0 Research: Spend advances — raise, open, change career

## Decision: the career-graph rules go in `career.py`, the spend transaction in `advancement.py`

**Chosen**: split by input, not by feature.

**Rationale**: #277 requires one copy of the career-graph rules and names `career.py` as their
home. `career.py` already answers "what does this career grant, and to what cap" (`effective_cap`)
without knowing anything about a character's balance; "is this career an entry career", "is this
career complete for these skills" and "may this history reach that career" are the same kind of
question over the same kind of input. The spend itself is a currency transaction — it needs
`advances_unspent`, which is `advancement.py`'s subject, and `advancement.py`'s own docstring
already states that "#277 spends what this module mints, and `career.py` holds the caps a spend is
validated against". This plan is that sentence carried out.

**Alternatives rejected**: a third module (`spend.py`) — it would import both and own nothing,
and the two halves have distinct, already-established homes; putting the graph rules in
`advancement.py` — it would make `career.py` the module that knows least about careers.

## Correction: the graph rules do not exist yet

#277's body says the rules are "already in `engine/wyrd/career.py`". `career.py` at
`d008775` holds `effective_cap`, `validate_allocation` and two constants — no `entry`, no
`prerequisites`, no completion predicate. The career graph is fully specified in
`docs/design/24-authoring-a-setting.md` (and settled by `specs/035-career-graph/`, issue #118) but
was never implemented, because nothing before this feature needed to ask a question of it. Read as
an instruction rather than a statement of fact, the issue's line still binds: the rules land in
`career.py` and nowhere else.

## Decision: eligibility keys off a *completed* career, from `career_history`

**Chosen**: a non-entry career is reachable when at least one id in its `prerequisites` appears in
the character's `career_history` with `completed: true`.

**Rationale**: `docs/design/24-authoring-a-setting.md` is explicit — "a character may choose a
non-entry career once any one of its declared prerequisites is **complete** for them", and
`docs/design/03-rules.md` §6 makes completion "every skill it grants at that 70% cap". Merely
holding a career grants nothing; a character who joined the guard and left after one skill has
completed nothing. The current career counts too when it happens to be complete at the moment of
the change, because the change records it as complete on departure — so the two paths agree.

**Alternatives rejected**: computing completion of past careers from the live skills dict — it
cannot work, since a later career may have raised a skill above a former career's cap, or the
character may have completed a career whose skills a wound has since reduced; history must be
recorded when it happens, not re-derived. This is the same "history is never recomputed" rule
`docs/design/29-evolution.md` states.

## Decision: `career_history` entries are `{career, completed}`

**Chosen**: `career_history: [{"career": "<id>", "completed": true}]`, appended on departure.

**Rationale**: `docs/design/22-state.md` documents `career_history: []` without an entry shape, so
this feature fixes one. It needs exactly two things: which career, and whether it was finished —
the first for eligibility, the second because eligibility keys off completion and re-entering an
abandoned career "starts a fresh instance". Per-instance tracking falls out for free: each
departure appends its own entry, so a career completed twice appears twice, which is what #278
will read to grant its Stamina and Mark each time.

**Alternatives rejected**: a bare list of ids (loses the distinction eligibility depends on); a
set of completed ids only (loses the abandoned instances, and #278 needs the instance record).

## Decision: a refusal key alongside the prose, as `award_advance` returns

**Chosen**: `{"spent": False, "refusal": <key>, "error": "<prose>", ...}` with the character view
returned unchanged.

**Rationale**: FR-010/SC-004 require a caller to tell an unaffordable spend from an illegal one,
and #276 already established the `refusal`-key pattern for exactly this reason. Returning the
unchanged view on refusal — rather than nothing — lets a caller thread the result through without
branching on success first, and makes FR-012's "nothing changed" directly assertable.

## Decision: refusal order — affordability first

**Chosen**: no-advance is checked before the action's own legality.

**Rationale**: this is the opposite of `award_advance`'s "most specific first", and deliberately.
There, the specific fault (a typo) and the general limit (the ceiling) describe the same claimed
award, so the specific one is more useful. Here, a character with no advance cannot make *any*
spend, and telling them why their chosen skill was ineligible invites them to pick another and be
refused again for the real reason. An unknown *action* is still checked first, because it is a
caller bug rather than a play-time answer.

## The cap bounds a raise, never a held percentage

`docs/design/03-rules.md` §6: "No advance may raise a skill past its career's cap." It says
nothing about a skill already held above a new career's cap, and the engine must not invent a
claw-back — a character who completed a career granting a skill at 70% and then changed to one
capping it at 70% keeps it, and one whose new career does not grant it at all keeps it too. So
`change career` touches no skill percentage, and `raise` is refused at the cap rather than
clamping to it. This matters because clamping would silently spend the advance for nothing.

## Cost is 1 for all three spends

`docs/design/03-rules.md` §6's spending table prices every row at 1, including changing career.
There is no discount and no scaling with career depth; the constant is stated once and shared.
