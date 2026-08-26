# Research: Optional intensity tiers for a system of power

No NEEDS CLARIFICATION markers were left by the spec or the plan's Technical Context — the design
was settled during the operator's design review before this feature entered the Spec Kit cycle
(see spec.md's Input section for the full resolved decision). This document records the design
choices actually made and the alternatives that were considered and rejected, in place of an
open-unknowns research pass.

## Decision: reuse the difficulty ladder rather than a bespoke tier scale

**Decision**: A tier's `difficulty` names one of the six existing rungs in
`docs/design/03-rules.md` §1 (Easy, Average, Challenging, Difficult, Hard, Very Hard).

**Rationale**: The engine already has exactly one difficulty scale, and every test in the game —
power or otherwise — reads it. Inventing a second numeric scale for "how ambitious was this"
would duplicate a scale that already exists for "how hard is this," for no distinction a player
would actually feel differently at the table.

**Alternatives considered**:
- A separate numeric intensity scale (e.g. 1–5) mapped internally to a difficulty modifier —
  rejected: two numbers doing the job of one invites them to drift out of sync, and a setting
  author has to learn a second scale for no benefit over naming the rung directly.
- Leaving difficulty out of the tier entirely, letting the GM set it fresh each time — rejected:
  this was the status quo the issue raised as insufficient (difficulty alone doesn't address the
  asymmetric-downside problem — see spec's resolved-decision section), and a tier that already
  bundles a *typical* difficulty for that ambition level is a genuine convenience the GM can still
  override, not a constraint added on top of the status quo.

## Decision: `cost_multiplier` scales the base cost, not a second cost field

**Decision**: A tier declares a multiplier applied to the system's existing `strain_cost`/
`resolve_cost`, not a second flat cost of its own.

**Rationale**: Keeps a single source of truth for "what this system of power costs" — the base
fields — with tiers as a pure modifier on top. A setting author who wants to change what
ember-craft costs changes one number (`strain_cost`) and every tier scales with it automatically,
rather than three or four numbers needing to move in lockstep.

**Alternatives considered**:
- Each tier declaring its own absolute `strain_cost`/`resolve_cost` — rejected: this is
  effectively three separate systems of power wearing one `id`, and a setting author changing the
  base cost would have to remember to update every tier by hand; nothing enforces they stay
  proportionate.

## Decision: `ill_omen_taint_bonus` is additive, not a tier-specific replacement table

**Decision**: A tier's `ill_omen_taint_bonus` adds to the system's base `ill_omen_taint` before
feeding the existing Taint-accrual path; there is no tier-specific consequence table.

**Rationale**: `docs/design/14-systems-of-power.md` already states "No second table exists for
this" for the base mechanism, and ADR 0036 rejected a set of engine-defined power shapes in favour
of one configurable mechanism. A tier-specific consequence table would reopen exactly the
distinction ADR 0036 closed. An additive bonus to the number already feeding the one existing
path preserves that: the loophole this feature closes is that the bonus was previously always
zero in practice (no way to declare one), not that the path itself was wrong.

**Alternatives considered**:
- A tier-specific transformation-table variant — rejected outright as contradicting ADR 0036 and
  the base mechanism's own "no second table" language; not seriously pursued.

## Decision: no new procedural step for choosing a tier

**Decision**: Which tier an invocation is framed at is decided the same way any other
declaration specificity is — the player states it, subject to the GM's usual authority over
plausibility (`docs/design/03-rules.md` §1's declaration rule) — not a new mechanical step this
feature defines.

**Rationale**: Matches the engine's existing pattern of leaving *how* a test is framed to
ordinary declaration and GM judgment, and keeps this feature's surface area to "what a tier is
and what it changes at resolution," not "how a tier gets chosen." Introducing a chooser mechanic
here would be new engine surface unrelated to the actual gap the issue raised.

**Alternatives considered**:
- A structured pre-roll "declare tier" step distinct from ordinary declaration — rejected as
  unnecessary complexity; ordinary declaration already carries this weight for difficulty and
  specificity bonuses, and a tier is simply one more thing that can be said as part of it.
