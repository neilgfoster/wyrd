# Phase 0 Research: Action economy and engagement

No `NEEDS CLARIFICATION` markers — `docs/design/03-rules.md` §2 fully specifies engagement,
breaking off, and both named ranged-difficulty rows.

## Decision: engagement pairs are stored as `{"a": ..., "b": ...}` dicts, not two-element lists

**Rationale**: `state.py`'s restricted YAML writer (`_dump_block`) only round-trips a list whose
items are dicts or scalars — a list item that is itself a list falls through to
`_dump_scalar`'s catch-all `str(value)`, which does not round-trip back through the reader.
Discovered concretely: `combat.close`'s first implementation attempt stored each engagement pair
as `[actor, opponent]`; after one `state.save`/`state.load` round-trip, `engaged_with` returned
an empty list for an actor that was, moments before, genuinely engaged. Switching each pair to a
two-key dict fixed it immediately — dicts are the shape `_dump_block` already handles correctly
(the same list-of-mappings convention `tools/check_bestiary.py`'s reader already relies on, per
`state.py`'s own docstring).

**Alternatives considered**: encoding a pair as a single string (e.g. `"a|b"`) and parsing it
back apart (rejected — an extra ad-hoc encoding for no benefit over the dict shape the writer
already supports natively).

## Decision: `resolve_ranged_attack` looks up the target's own engagement partner itself

**Rationale**: `docs/design/03-rules.md`'s "shooting into someone else's fight" row is a fact
about the *target's* own engagement, not something the shooter's player would separately know to
supply — the engine already has this fact in the persisted `combat` scene (`engaged_with`), so
asking the caller to also name "the ally" would be redundant and could drift from what the scene
actually records. `resolve_ranged_attack` derives it from state instead.

**Alternatives considered**: a caller-supplied `ally` parameter (rejected — spec.md's own Edge
Cases note this feature only handles the two named table rows; deriving the ally from engagement
state, rather than trusting a caller-supplied guess, is what keeps the redirect's target
correct even if the caller's own bookkeeping of "who's engaged with whom" has drifted).

## Worked example: engaged-shooter Difficult modifier (SC-003)

A shooter (`archery: 50`) engaged with an ally (irrelevant to this shot, just needed to make the
shooter's own `is_engaged` true), target `archery: 10`, weapon `1d8`, armour `1d3`, seed `2`:

```
unengaged (baseline):  eff. 90 (clip(50 + (50 - 10), 5, 95))
engaged (Difficult):   eff. 70 (90 - 20)
```

## Worked example: the ally-redirect, both branches (SC-004)

Same shooter/target, target engaged with a separate ally (`archery: 10`), weapon `1d8`, armour
`1d3`:

```
seed 5: original roll against target, eff. 80 (90 - 10, Challenging) -- roll 80, units 0, Ill
    Omen. Redirected: a fresh propose (seed 6) targets the ally instead. The final result's own
    target is the ally, not the originally-named target.
seed 1: original roll against target, eff. 80 -- roll 18, units 8, no Omen. No redirect --
    the final result's own target is still the originally-named target.
```
