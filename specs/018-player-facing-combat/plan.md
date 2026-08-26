# Implementation Plan: Player-facing combat rolls

**Branch**: `018-player-facing-combat` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Convert combat's opposed test into a single player-facing roll on each side of an exchange: the
attacker rolls once against an effective percentage derived from both skills, and a player under
attack rolls a defence the same way, so the opponent's dice never come out. The mapping itself
(`effective% = clip(50 + (S − O), 5, 95)`) is already computed and calibrated
([`specs/012-combat-sequencing/check_mapping.py`](../012-combat-sequencing/check_mapping.py)); this
feature computes what is not yet settled — the telling-blow threshold at the new roll's
distribution, the damage-multiplier consequence of a player-rolled defence, and starting Stamina
against the resulting fight length — and rewrites `03-rules.md` and ADR 0016 to describe the result.

## The load-bearing decisions

**One roll per side of an exchange, always the player's.** An attack is the attacker's single
`d100` against `effective%`; a defence, when a player character or companion is the target, is the
defender's single `d100` against `effective%` computed from the defensive skill and the attacker's
skill (or `baseline`). The opponent contributes only its skill values — it never rolls, in either
direction. This is what "the Wyrd die now always belongs to the player" (#69) requires: there is no
longer a roll on the far side of the table for a Wyrd die to belong to.

**Degrees keep their existing formula, fed a new number.** `tens(effective%) − tens(roll)`
(unchanged from `03-rules.md` §1) rather than a new margin measure — a second measure of the same
quantity is exactly the drift ADR 0001 already rejected once. What changes is that `effective%`
replaces a raw skill as the value degrees are read against, and that changes the *distribution* of
degrees enough that the telling-blow threshold (currently "3 or more") needs to be recomputed, not
carried over.

**The consequence #44 named is computed, not asserted.** A defence that the player rolls (rather
than the opponent needing to beat a static number) removes the double-failure case that used to
suppress damage — today, a hit lands only when the attacker succeeds *and* the defender's degrees
lose; under the new structure a hit lands whenever the single defence roll fails. The issue states
this raises incoming damage 1.4×–3.1×; `check_conversion.py` reproduces that figure under the new
mechanic and either confirms it or corrects it, then decides Stamina against whichever number is
right.

**ADR 0016 is superseded, not edited.** Its five provisions (acting side rolls first and must
succeed; degrees only on success; ties to the resister; margin from degrees; one Wyrd die) describe
a *two-sided* opposed test. Combat no longer has one. Whether anything outside combat still does is
FR-007's question, and the answer decides whether the new record narrows ADR 0016's scope or
retires two-sided opposed tests from the engine entirely. Either way a new ADR is written; the old
one is never touched.

## What the check script has to settle

`check_conversion.py`, stdlib only, exact arithmetic (`Fraction`) throughout, following
`check_mapping.py`'s and `check_adversary.py`'s conventions. It **asserts agreement with prior
figures** it depends on (the mapping table above, from `check_mapping.py`) rather than
re-deriving them from scratch.

1. **The degrees distribution under the new roll**, across the same representative skill-gap span
   `check_mapping.py` already used, and the resulting telling-blow rate at threshold 3 — most likely
   too low again, the same way ADR 0016 found it, since `effective%` compresses the input range to
   5–95 and pushes more mass toward the middle tens digits.
2. **The corrected telling-blow threshold**, chosen the same way ADR 0016 left as future work: a
   rate that stays a minority of hits at ordinary skill gaps and does not require a near-maximal gap
   to ever trigger.
3. **The damage-multiplier consequence**, comparing expected damage per exchange-round under the
   double-gate opposed test (today) against the single-roll structure (this feature), across the
   same realistic pairings `check_mapping.py` and `check_adversary.py` use. This either confirms
   the issue's stated 1.4×–3.1× or replaces it with the correct figure — the issue's number is a
   finding to verify, not a given.
4. **Starting Stamina, recomputed against the new expected fight length** — rounds to clear an
   opponent and rounds to be dropped, at the values `03-rules.md` §2's own table already states
   (dropped at Stamina 6/7; 4.6–4.9 rounds for an even fight; 2.2–3.3 at a 20-point advantage) —
   reproduced under the new damage rate and either reaffirmed or given a new figure.
5. **The Wyrd-die read at the clip boundary.** At `effective%` of 5 or 95, confirm the units-digit
   read is still uniform within the success and failure sets respectively (needed since the clip can
   make the *raw* skill gap arbitrarily larger than the percentage it maps to, but the roll and its
   units digit are unaffected by the clip — only which percentage they're compared against).
6. **A complete exchange, resolved from the rules as rewritten**: one attack roll, one defence roll,
   degrees, telling blow (at the new threshold), damage, armour, the drop below zero, Aftermath —
   against a written character and a written opponent from
   [specs/017-adversary-model](../017-adversary-model/spec.md)'s schema.
7. **Agreement with every figure earlier issues already published** that this feature touches or
   depends on: the mapping table in `check_mapping.py`, and the one-blow crowd band and drop rates
   from `check_adversary.py`/`check_mobs.py` if Stamina changes propagate there. Non-zero exit on
   any disagreement.

## Where the rules land

| Document | Change |
|---|---|
| `docs/design/03-rules.md` §1 | the two-sided opposed-test description is narrowed or removed per FR-007's answer; degrees' formula is unchanged in wording but its worked commentary updated for the new input |
| `docs/design/03-rules.md` §2 | the exchange rewritten: one attack roll, one defence roll, the opponent never rolls; telling-blow threshold updated to the computed figure; starting-Stamina table updated if changed |
| `docs/adr/0016-*.md` | left untouched (accepted ADRs are never edited) |
| `docs/adr/0027` (new) | supersedes ADR 0016 for combat's single-roll structure; states what, if anything, still uses a two-sided opposed test |
| `docs/adr/0028` (new) | the telling-blow threshold and the damage-multiplier finding, computed rather than asserted |
| `docs/README.md` | updated only if a new document is added (none currently planned — this is a rewrite of existing documents plus two ADRs) |

## The order of work

`check_conversion.py` comes first, because the telling-blow threshold and the Stamina question
cannot be written into `03-rules.md` until they are computed, and the script is allowed to reject
the issue's stated 1.4×–3.1× figure if the real number differs. The two ADRs are written from what
the script settles. `03-rules.md` is rewritten last, in place, from the surviving numbers. Finally
the guards — `check_conversion.py` itself, `python3 tools/check_docs.py`,
`python3 tools/backlog.py check`, and a grep for setting vocabulary — are run rather than assumed.

## Constitution Check

Evaluated against `CLAUDE.md` and the accepted ADRs, per `.specify/memory/constitution.md`.

| Gate | How this feature satisfies it |
|---|---|
| Nothing unpublishable | No source text, no quotation, no catalogue — a mapping formula and a worked example, both original to this repo. |
| No setting or system names | The rewritten sections use existing descriptive-English vocabulary (skill, degrees, telling blow, Stamina); verified by grep. |
| Engine labels are descriptive English | No new label is introduced; the feature changes *who rolls*, not what anything is called. |
| Tone is a setting property | Untouched — the exchange's mechanics change, not its register. |
| Computed, not inferred | Every figure — the telling-blow rate, the damage multiplier, starting Stamina — comes from `check_conversion.py`, which asserts agreement with `check_mapping.py`'s prior table and fails on disagreement. |
| Forward only | The conversion applies to combat going forward; nothing already played is recomputed (`09-evolution.md`). |
| Design docs describe the present | `03-rules.md` is rewritten in place, present tense, no changelog; rejected alternatives live in the two ADRs. |
| Accepted ADRs never edited | ADR 0016 is left untouched; a new ADR supersedes it. |
| Spec Kit cycle, `specs/` committed | This directory is committed with the change. |

### One gate worth naming explicitly

**The issue's own stated figure (1.4×–3.1× damage) is a claim to verify, not a given to design
around.** `CLAUDE.md`'s "check the maths" applies to numbers proposed in an issue exactly as much as
to numbers proposed from intuition — `check_conversion.py` reproduces it independently before
anything downstream (Stamina, armour) is set against it.
