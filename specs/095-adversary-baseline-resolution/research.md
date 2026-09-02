# Research: Adversary baseline skill resolution

No `NEEDS CLARIFICATION` markers remained in the Technical Context.

## Decision: a pure function in `adversary.py`, not `rules.py`

**Rationale**: `rules.py` holds the player-facing resolution machinery (`opposed_test`,
`select_group_skill`, `UNTRAINED_SKILL`) this feature's own Definition of Done requires staying
independent from. Placing `resolve_skill` in `adversary.py` alongside the block shape it reads
keeps the two fallback rates in genuinely separate modules, not merely separate functions in the
same file where a future edit could accidentally couple them.

**Alternatives considered**: adding an adversary branch to `rules.select_group_skill` (e.g. an
`is_adversary` flag). Rejected -- FR-005 is explicit that the two paths must not read each other,
and folding an adversary case into the player-side selector is exactly the kind of shared code
path that would make future changes to one silently affect the other.

## Decision: dict lookup with `baseline` as the fallback, no new exception path

**Rationale**: `resolve_skill(block, skill)` is `block["skills"].get(skill, block["baseline"])`
in spirit -- a block already validated by #259's `validate_adversary` always has both `skills`
(non-empty) and `baseline` (an int 0-100) present, so no additional error handling is needed here
for a well-formed block. A caller passing an unvalidated dict is a caller misuse this feature
doesn't need to guard against, the same way `character.active_wound_effects` doesn't re-validate
its input either.

**Alternatives considered**: raising if `block` is missing `baseline`/`skills` entirely.
Rejected as unnecessary defensive coding -- `#259`'s `load()` is the only intended source of a
`block` this function receives, and it already guarantees both fields.
