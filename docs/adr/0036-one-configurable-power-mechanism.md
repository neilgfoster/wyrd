# ADR 0036 — Supernatural power is one configurable mechanism, not a set of engine-side shapes

**Date:** 2026-08-26
**Status:** Accepted

## Context

The engine has no concept of magic or the supernatural at all — grepping `docs/design/` and
`README.md` finds nothing. Every catalogued setting has practitioners of some kind, and
[`24-authoring-a-setting.md`](../design/24-authoring-a-setting.md)'s hard rule — *"A setting may extend,
retune or disable what the engine provides. It may never add a mechanism the engine does not
have"* — forbids leaving this for a setting to invent. #96 asks for an engine-level mechanism
general enough that a setting declares one or more systems of power as data, specific enough that
casting has real mechanical weight.

Two shapes were available:

1. **One configurable mechanism.** The engine defines a single schema — what a system of power
   declares — and a setting instantiates it with data, the same way `bestiary.yaml`, `gear.yaml`
   and the career graph already work.
2. **A small closed set of mechanism shapes** (for example: a spell-slot caster, a mana-pool
   caster, a Taint-fuelled invoker) that a setting picks from, each hardcoded in the engine as a
   distinct resolution path.

This is the load-bearing fork: the two shapes produce genuinely different engines, and either
could plausibly be proposed again by someone who has forgotten why the other lost.

## Decision

**Supernatural power is one configurable mechanism: a "system of power" schema a setting declares
as data, not a menu of engine-defined mechanism shapes.**

A system of power declares:

- `skill` — the setting's own skill it tests (no engine skill vocabulary in between, per
  [ADR 0013](0013-the-engine-names-no-skill.md))
- `strain_cost` — paid on every invocation, mandatory
- `resolve_cost` — optional, for a system whose exceptional workings draw on Resolve
- `requires_training` — whether an untrained attempt exists at all
- `ill_omen_taint` — the Taint gain applied through the engine's existing accrual path when an
  invocation's Wyrd die reads Ill Omen

Invoking one resolves as the engine's ordinary d100 test ([`03-rules.md`](../design/03-rules.md) §1) —
same difficulty bands, same declaration bonuses, same assistance rule, same Wyrd die. Nothing
about resolution is new; only the cost application and the training gate are.

### Why one mechanism

**Every other piece of setting texture the engine already carries is one schema instantiated with
data**, never a menu of engine-side shapes: `bestiary.yaml` defines one adversary block, not a
choice between "brute," "caster," and "swarm" block *types*; `gear.yaml` defines one weapon/armour
schema, not a set of weapon-category mechanisms. Systems of power following the same shape is
consistency with the engine's own established pattern, not a new design principle invented for
this feature.

**A closed set of shapes would itself be several mechanisms sharing one name.** A spell-slot
caster and a Taint-fuelled invoker do not share a resolution path — they would need separate
engine code, separate state fields, and separate rules for how each interacts with declaration,
assistance and the Wyrd die. That is exactly what
[`24-authoring-a-setting.md`](../design/24-authoring-a-setting.md)'s hard rule exists to prevent
accumulating: "New mechanisms go in the core, for everyone. This is the rule that keeps Wyrd a
single system rather than a family of incompatible forks."

**A closed set is never actually closed.** The next setting that wants a fourth shape — a
bargain-with-an-entity caster, a ritual-with-a-time-cost caster — has nowhere to put it but a fork
of the engine or a fifth hardcoded shape, repeating the same decision indefinitely. One
configurable mechanism absorbs the same variety as setting data: cost tracks, training gate, and
Taint sensitivity are all the axes a shape-based design would otherwise hardcode per shape, and
they compose freely as fields on one schema instead.

**Casting still has real mechanical weight without a second resolution path.** The issue's
concern — that "one configurable mechanism" might mean magic reads as a reskinned ordinary skill
check with no teeth — is answered by the cost and Ill Omen fields, not by a second dice mechanism.
A system with a high `strain_cost`, a `resolve_cost`, and `requires_training: true` is a
meaningfully different thing to invoke than one with none of those, while both are the same one
schema.

## Consequences

**[`09-systems-of-power.md`](../design/09-systems-of-power.md) is a new design document**,
specifying the schema, the resolution rule (a pointer to `03-rules.md` §1, not a restatement), the
cost application, and the Ill Omen consequence via the existing transformation-threshold path
([`07-transformations.md`](../design/07-transformations.md)) — no new consequence table.

**`tools/check_power_systems.py` is the schema's validator**, following `check_bestiary.py` and
`check_gear.py`'s established shape exactly: required/optional field split, unrecognised-field
rejection, and every failure reported rather than just the first. The unrecognised-field rejection
is what actually enforces this ADR's decision at the tooling level, the same way it already
enforces the bestiary and gear schemas' closure.

**No new track.** Casting spends Strain and, optionally, Resolve — both already exist
([`03-rules.md`](../design/03-rules.md), [`22-state.md`](../design/22-state.md)) — and an Ill Omen feeds Taint
through the accrual path that already exists. `19-state.md`'s reuse guidance and the issue's own
"prefer reuse over a new track" are both satisfied without argument.

**A setting's actual spell content is unaffected and stays out of scope.** What a system of power
is called, what its invocations look like in the fiction, and what specific effects a caster
produces are setting data in a `wyrd-setting-*` repository — the schema constrains structure, not
content, the same boundary `26-authoring-a-setting.md` already draws for `bestiary.yaml`.

## Alternatives rejected

**A small closed set of mechanism shapes.** Rejected for the reasons above: it multiplies engine
code per shape, is never actually closed against a setting's next request, and the variety it
would provide (cost tracks, training gates, Taint sensitivity) is already available as fields on
one schema without hardcoding a second resolution path.

**No mechanism at all — leave power entirely to a setting's `rules/` overlay.** Rejected outright:
`26-authoring-a-setting.md`'s hard rule already forbids a setting adding a mechanism the engine
does not have, and every catalogued setting needs one. Leaving it unspecified would mean every
setting either forks the engine or goes without, which is the exact failure mode the hard rule
exists to prevent.

**A dedicated new track for casting cost** (e.g. a "Mana" or "Vigour" track parallel to Strain).
Rejected: the issue explicitly asks the design to prefer reuse over a new track, and nothing about
casting needs a cost shape Strain (short-term, recovered at a Rally) and Resolve (the spendable
counterweight to Taint) cannot already express — a new track would duplicate one of the two
without adding a distinction that matters mechanically.
