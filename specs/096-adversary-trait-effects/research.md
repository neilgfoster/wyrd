# Research: Adversary trait effects

No `NEEDS CLARIFICATION` markers remained in the Technical Context.

## Decision: fold stamina_max/armour_rank/damage/damage_type into one `effective_block` function

**Rationale**: these four effects all retune a field already present on the loaded block, and
every caller that would need the retuned value (combat's Stamina/armour reads, the damage
request built for `resolution.py`'s combat-attack mechanic) wants the whole adjusted block at
once, not four separate calls. A single function returning a new dict (never mutating the input,
matching #259's `load`'s own "never mutate the source" convention from #263's sibling spec) is
the natural shape.

**Alternatives considered**: four separate functions (`effective_stamina_max`,
`effective_armour`, `effective_damage`, `effective_damage_type`). Rejected as unnecessary
fragmentation -- all four read the same `traits` list and are almost always wanted together by
the same caller building a combat request.

## Decision: `shift_difficulty` stays a standalone utility, not wired into every difficulty call site

**Rationale**: docs/design/12-the-adversary.md section 5 describes a `difficulty` trait as
shifting "the difficulty of a named class of test" -- which test is fiction-decided (spec.md
Assumptions), not something a block's data alone determines. `combat.py`'s existing
difficulty-selecting call sites (e.g. ranged-attack difficulty) don't currently accept "the
opponent's active traits" as an input, and retrofitting each one is a materially larger, separate
concern than a single ladder-stepping utility. This feature provides the utility; wiring specific
call sites to consult it is left to whichever future feature actually needs a specific
difficulty-trait interaction (the issue's own acceptance criteria describe the utility's
behavior, not a rewrite of `combat.py`'s call sites).

**Alternatives considered**: threading an `adversary_traits` parameter through every existing
difficulty-selecting function in `combat.py`. Rejected as scope creep beyond this issue's stated
acceptance criteria, and each such site would need its own judgment call about which trait
applies to it -- exactly the fiction-decided question this feature deliberately does not
automate.

## Decision: the ladder order is read from `resolution.DIFFICULTY_BONUSES`'s own key order

**Rationale**: `resolution.py`'s `DIFFICULTY_BONUSES` dict is already declared in ladder order
(`easy, average, challenging, difficult, hard, very_hard`) and Python dicts preserve insertion
order -- `combat.py`'s own `PURSUIT_DIFFICULTIES` list is a hand-written *subset* of exactly this
same order for its own narrower ladder. Reading `tuple(resolution.DIFFICULTY_BONUSES)` reuses the
one existing source of the ladder's order rather than declaring a second, parallel list that
could drift from it.

**Alternatives considered**: a new hand-written `DIFFICULTY_LADDER` constant in `adversary.py`
duplicating the six names. Rejected -- exactly the kind of second copy of one fact this repo's
process has flagged before (CLAUDE.md "Two documents describing one thing differently").

## Decision: `omen_width` is additive on `rules._wyrd_die`/`opposed_test`, default 0

**Rationale**: the Wyrd die is read in exactly one place (`rules._wyrd_die`, called from
`rules.opposed_test`). Widening the band for a `wyrd` trait is naturally expressed as one more
optional parameter, defaulting to today's exact behavior (units digit 0 -> ill_omen, 9 ->
fair_omen, nothing else) so every existing caller (`opposed_test`'s own test suite, and anything
built on it) is unaffected (SC-003). A caller that has computed an adversary's trait-derived
width (a new `adversary.wyrd_band_width(block)` helper, sibling to `effective_block`) passes it
through.

**Alternatives considered**: a second, adversary-specific dice-reading function duplicating
`_wyrd_die`'s logic. Rejected -- the Wyrd die's reading rule is one fact (docs/design/03-rules.md:
"the units digit is uniform within both the success and failure sets"); a second implementation
of it is exactly the class of drift risk `state.py`'s own docstring warns about for its YAML
reader, generalized to any duplicated mechanism.

## Decision: `wyrd_band_width` lives alongside `effective_block` in `adversary.py`

**Rationale**: like the other trait-derived values, this is a pure sum over the block's `traits`
list; keeping it in `adversary.py` (which already owns everything about reading an adversary
block) rather than in `rules.py` (which stays the player-facing resolution primitives module,
per #260's precedent of not folding adversary-specific reads into it) keeps the same boundary
#260 established.
