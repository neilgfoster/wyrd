# ADR 0033 — Standing is kept and defined; wealth reconciles with it, not beside it

**Date:** 2026-08-26
**Status:** Accepted

## Context

`16-session.md`'s Upkeep step charged "lose 1 Standing, or spend coin equal to Standing" with no
definition of Standing anywhere in the repo — the fourth instance of a mechanic referenced before
it was defined (`CLAUDE.md`'s recurring fault list), found by grep rather than by reading.
Separately, `26-authoring-a-setting.md` had promised `gear.yaml` — "weapons, armour, prices, what
is legal to carry where" — since the document existed, without ever stating what a gear entry
declares, even though `03-rules.md` §2 already depends on gear mechanically (weapon damage,
armour rank, the casual/martial distinction). Four decisions had to be made, all load-bearing for
a chronicle played across years:

1. Whether Standing is defined or removed.
2. What shape Standing takes, if kept — a percentile, a capped band, or an open count.
3. How wealth (coin) works, and how it relates to Standing.
4. How encumbrance is handled, consistent with `23-diegesis.md`'s existing rejection of a numeric
   item list ("realistic, not logistic").

## Decision

**Standing is kept and defined, not removed.** It already does real narrative work in Upkeep, and
it is the natural anchor for the casual/martial social consequence `03-rules.md` §2 gestures at
but never made concrete — removing it would need a replacement to carry both jobs, which is more
invention than the alternative of simply defining what's there.

**Standing is a small, open-ended count — not a percentile, not a capped band.** It joins
Taint/Trauma/Strain/Resolve in `03-rules.md`'s engine-label table as an accruing track with no
stated ceiling. Nothing tests Standing against a roll the way a skill is tested, and Upkeep only
ever moves it by exactly 1, so a bounded 0–100 scale would be unused precision, and a capped band
like career caps' 70% doesn't transfer — that cap bounds a *rolled* skill, and Standing is never
rolled against.

**Coin is a small stated total, not a transaction ledger.** Upkeep's "spend coin equal to
Standing" is a numeric comparison, which rules out treating wealth as a pure narrative
abstraction — there would be nothing to compare. But the design stops well short of asking the
player to itemize purchases: a character has some coin, they spend it against a `gear.yaml`
price or at Upkeep, and the total simply changes.

**Standing and coin are two sides of one material position, reconciled rather than independent.**
Standing is what a character is *owed* by their position; coin is what they *have on hand*.
Upkeep is the one place they convert — away from home, a character pays in whichever one they
still have. Standing also moves outside Upkeep, as a direct scene consequence (the martial-weapon
sighting below is one case), the same way Taint or Trauma can move outside their own named
triggers.

**Encumbrance is a GM question asked of the fiction, not a new numeric mechanic.**
`23-diegesis.md` already answers the adjacent question — what a character has, and what's
missing — the same way: asked of the fiction, not computed. Encumbrance ("can this plausibly be
carried") inherits that shape rather than getting a weight table or a carrying-capacity roll.

**The casual/martial distinction resolves through Standing.** Being seen carrying a martial
weapon somewhere it's restricted costs 1 Standing the moment it's visible — a real, immediate
cost rather than only a sentence of social framing — or, where the fiction plainly calls for it,
triggers an encounter instead, but never both for the same sighting.

**The gear schema mirrors the adversary block's shape.** `gear.yaml` entries are validated by
[`check_gear.py`](../../tools/check_gear.py), built on the same closed-field,
closed-vocabulary pattern and the same YAML reader as
[`check_bestiary.py`](../../tools/check_bestiary.py) — gear reads into the same combat fields
(damage, damage type, armour rank) the adversary block already validates, and the two closed
sets (`ARMOUR_RANKS`, `DAMAGE_TYPES`) are shared by import so they cannot drift apart.

## Rejected alternatives

**Removing Standing and rewriting Upkeep without it.** Rejected: it discards the mechanic doing
real work (the payment choice, the social-consequence anchor) rather than fixing the actual
fault, which was that it was undefined, not that it was wrong.

**A percentile Standing, tested like a skill.** Rejected: nothing in the existing rules compares
Standing to a roll, so a 0–100 scale would carry precision the mechanic never uses.

**A capped band, following career caps' precedent.** Rejected: that cap bounds a skill a
character *rolls against*; Standing is never rolled against, so the same reasoning doesn't
transfer, and an arbitrary cap picked "for symmetry" would be exactly the round-number-without-
computation fault `CLAUDE.md` flags.

**Wealth as a pure narrative abstraction, no number at all.** Rejected: Upkeep's "coin equal to
Standing" is already a numeric comparison in the existing text; an abstraction with nothing to
compare would break that line rather than define it.

**Wealth as a full itemized ledger.** Rejected: directly contradicts `23-diegesis.md`'s
"realistic, not logistic" framing for gear generally, and nothing else in the ruleset asks for
transaction-level granularity.

**A numeric encumbrance mechanism** (a weight-and-slot table, or a Strength-derived carrying
capacity). Rejected on two grounds: `23-diegesis.md` already explicitly rules out an encumbrance
table, and the engine names no characteristics (ADR 0013), so there is no stat to derive a
capacity from without inventing one.

**A bespoke penalty for the casual/martial distinction, separate from Standing.** Rejected: it
would add a second social-consequence mechanism next to one this same feature just defined,
where routing the consequence through Standing keeps the design to one mechanism doing the work.

## Consequences

- `03-rules.md` states Standing in the engine-label table and defines gear, coin, encumbrance,
  and the martial-weapon consequence in §2, next to the mechanics that already depended on them.
- `16-session.md`'s Upkeep line resolves entirely within `docs/design/` — no dangling reference.
- `26-authoring-a-setting.md` gives a setting author the `gear.yaml` schema and its validator, the
  same way it already does for `bestiary.yaml`.
- `23-diegesis.md`'s "realistic, not logistic" framing is extended, not contradicted, by stating
  encumbrance explicitly as the same kind of question.
- [`check_gear.py`](../../tools/check_gear.py) is the durable, checked record of the gear
  schema; a future field addition changes the schema and the validator together, not the design
  prose alone.
