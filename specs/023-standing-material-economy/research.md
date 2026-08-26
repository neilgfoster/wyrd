# Research: Standing and the material economy

No NEEDS CLARIFICATION markers remain in the spec — the three real forks were resolved during
`/speckit-clarify` (2026-08-26) from existing engine convention rather than left open. This
document records why each precedent applies.

## Standing's shape: open count vs. percentile vs. capped band

**Decision**: open-ended count, not a percentile or a fixed 0–N band.

**Rationale**: `doc/design/03-rules.md`'s engine-label table already lists Taint, Trauma, Strain,
Resolve as accruing tracks with no stated ceiling; none of them are percentiles, and none are
tested against a roll the way a skill is. Standing moves by exactly 1 at Upkeep and is compared
only to itself (coin spent "equal to Standing"), so it needs no bounded scale to function.

**Alternatives considered**: a percentile score (rejected — nothing tests Standing against a
roll, so a 0–100 scale would be unused precision); a small capped band like career caps' 70%
(rejected — career caps bound a *skill*, which is rolled against; Standing is never rolled
against, so the same bound doesn't transfer).

## Wealth: ledger vs. abstraction vs. small stated count

**Decision**: a small numeric count the player can state a total for, no itemized transactions.

**Rationale**: Upkeep's "spend coin equal to Standing" is a numeric comparison, which rules out a
pure narrative abstraction (there would be nothing to compare). But `doc/design/23-diegesis.md`
already rejects a numeric item list for inventory, and a full transaction ledger would reintroduce
exactly the logistics that document rules out for gear generally.

**Alternatives considered**: fully narrative wealth with no number (rejected — breaks Upkeep's
existing comparison); a tracked ledger of every transaction (rejected — contradicts
`10-diegesis.md`'s "realistic, not logistic" framing, and nothing else in the ruleset asks for
that granularity).

## Encumbrance: numeric threshold vs. GM judgment

**Decision**: a GM judgment call against the fiction, no roll, no weight table.

**Rationale**: `doc/design/23-diegesis.md` §"Inventory — realistic, not logistic" already resolves
the adjacent question — what a character is carrying, and what's missing — the same way: asked of
the fiction, not computed. Encumbrance is the same question asked in the other direction ("can
this plausibly be carried") and inherits the same answer shape.

**Alternatives considered**: a Strength-derived numeric carrying capacity (rejected — the engine
names no characteristics, per ADR 0013, so there is no stat to derive a capacity from without
inventing one); a weight-and-slot table (rejected — explicitly what `10-diegesis.md` rules out).

## Gear schema shape: novel format vs. adversary-block precedent

**Decision**: mirror `doc/design/06-the-adversary.md`'s closed-field, closed-vocabulary schema and
`tools/check_bestiary.py`'s validator shape.

**Rationale**: gear reads into the same mechanical fields combat already depends on (damage,
damage type, armour rank) that the adversary block validates today; reusing the same closed sets
(`ARMOUR_RANKS`, `DAMAGE_TYPES`) keeps them from drifting apart, and reusing the validator's
reporting shape (name every offending entry and field, fail loudly on missing/unrecognised
fields) is a pattern the repo has already committed to for exactly this kind of setting data.

**Alternatives considered**: an open/extensible schema (rejected — `13-authoring-a-setting.md`
already states a setting may never add a mechanism, and an unrecognised field is exactly how one
would sneak in, per `check_bestiary.py`'s own stated rationale).
