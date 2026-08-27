# Implementation Plan: What a party counts for

**Branch**: `016-party-effective` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Define `party_effective` as an exact function of head count, define the matching reading of
`written_for` so both sides of the ratio are in the same units, state the one rounding rule every
quantity built from `danger_effective` applies, and rewrite `docs/design/03-rules.md` §7 in place so the
engine's only scaling equation can actually be evaluated. Compute the resulting danger at every
party a real chronicle has before writing a word of it, replace the uncomputed figure
`docs/design/26-corpus-index.md` currently quotes, and record the curve as an ADR.

## The load-bearing decisions

**A body is worth less than the body before it.** The k-th companion is worth `1/(k+1)` — the first
a half, the second a third, the third a quarter. The series has a closed form: a party of `p`
bodies has an effective size of `1 + 1/2 + 1/3 + … + 1/p`, the p-th harmonic number. Two properties
earn it. It is **order-independent**, so no roster ordering has to be invented and two readers
counting the same party in different orders get the same number. And it **bounds the retinue**:
effective size grows like the logarithm of head count, so gathering bodies is not a way to flatten
every arc. A flat weight was the alternative, and it is simpler; it was rejected because under it a
party of ten scales danger like a party of ten, and a party of GM-run companions is not that.

**Both sides of the ratio are read through the same function.** `party_effective` is the effective
size of the party present; the denominator is the effective size of a party of `written_for`
bodies. This is what keeps the identity case exact — four bodies run content written for four
exactly as written — and it is the difference between a ratio and a category error. `written_for`
still means what it always meant, a head count; the formula still has the shape it always had,
`danger` times a ratio of party sizes. What is new is only the conversion, and it is applied to
both counts or the equation compares a harmonic number with a head count.

**`danger_effective` is never rounded.** It stays exact, and each quantity built from it — a dice
count, an enemy count, a skill value — rounds at its own point of use, by one rule: **round half
up, and never below 1 where the written quantity was at least 1.** Rounding up front discards
precision the later multiplications need, and it is precisely the multiplications that make danger
visible at the table. The minimum of 1 is what stops a lone character walking through content for
free: a trap written `Nd4` always throws at least one die.

**The party is a query, not a roster.** Companions with `status: with-party` count; `away`, `dead`,
`lost` and `departed` do not. This is not a new predicate — `docs/design/22-state.md` already defines
the party as exactly that query, and inventing a second definition here would be the two-documents
fault class in its purest form. Presence in a particular room is never consulted, because scaling
happens when content is prepared, not when a door opens.

**The curve is not overridable.** With the same function on both sides, a setting override on one
side breaks the identity case and an override on both sides cancels. A setting's levers over
difficulty are the companions it grants and the `danger` its content carries. This is worth stating
in the document, because "every number is a default a setting may replace" is otherwise the
standing assumption in this engine and a reader will assume it here too.

**A missing `written_for` means the content runs as written.** The ratio is 1. A record that never
stated a party size is not a record claiming a party of none, and dividing by zero is not an
answer.

## What the check script has to settle

`check_party.py`, stdlib only, exact arithmetic (`Fraction`), no sampling. Cheap to run — this
feature's model is arithmetic, not a fight resolution — so no memoisation is needed, but every
figure any design document publishes must be asserted by it.

1. **The effective-size table** for 1 to 20 bodies, exact, and its growth: that each additional
   body adds strictly less than the one before, and that the total grows like a logarithm rather
   than a line.
2. **Scaled danger at the parties a real chronicle has** — one player character with zero through
   four companions — against records written for four and for six, at every written `danger` from 1
   to 6. Not at a midpoint.
3. **The identity case**, exactly: `p` bodies against `written_for: p` yields `danger_effective`
   equal to `danger`, for every `p` in range, as an exact equality and not a near one.
4. **The retinue bound**: what a party of ten and of twenty actually buys against `written_for: 4`,
   so the claim that a large retinue is not an exploit is a computed property rather than a hope.
5. **The rounding rule at its awkward points**: exact halves, and every case where a written
   quantity of at least 1 could round to 0 and must not.
6. **The degenerate inputs**: `written_for` absent, and `written_for: 0`, both yielding the ratio 1.
7. **Every figure the design documents publish** — including the figure replacing "roughly danger
   2" in `11-corpus-index.md` — asserted against the model, so an edit that drifts fails loudly
   instead of reading plausibly.

## The worked example

`worked-scaling.md`: a single arc record taken through the equation at three points in one
chronicle's life — the player character alone, then with two companions, then with a retinue — with
each derived quantity (dice count, enemy count, skill value) rounded at its own point of use and
shown. This is where the rounding-at-use decision is either vindicated or exposed, because it is
the only place all three points of use appear together.

## Where the rules land

| Document | Change |
|---|---|
| `docs/design/03-rules.md` §7 | rewritten in place: the effective-size function, both sides of the ratio, the rounding rule, the degenerate cases, and why the curve is not overridable |
| `docs/design/26-corpus-index.md` | the one-sentence description replaced so it agrees with §7; the quoted worked figure replaced with the computed one |
| `docs/adr/` | one ADR: the diminishing curve and the symmetric reading of `written_for`, against the flat weight and the raw denominator |
| `docs/adr/0012` | the open-term row for `party_effective` is a record of the reset, not an index — left alone |

## The order of work

The computation comes first and is allowed to reject the curve before it is written into anything.
The worked example comes second and is allowed to expose the rounding rule. The design documents
are written last, from what survived, and the ADR records what was rejected. Finally the guards —
`check_party.py`, `tools/check_docs.py`, `tools/backlog.py check`, and a grep for setting
vocabulary and for any surviving undefined term — are run rather than assumed.

## Constitution Check

Evaluated against `CLAUDE.md` and the accepted ADRs, per `.specify/memory/constitution.md`.

| Gate | How this feature satisfies it |
|---|---|
| Nothing unpublishable | The curve is arithmetic. No source text, no quotation, no catalogue. |
| No setting or system names | The change names head counts and a rounding rule. Verified by grep. |
| Tone is a setting property | §7 says what scales and by how much, and nothing about how danger feels. |
| Computed, not inferred | Every figure comes from `check_party.py`, which fails on disagreement — including with the figure `11-corpus-index.md` has been quoting uncomputed. |
| Forward only | Scaling is computed when content is prepared; nothing already played is recomputed (`09-evolution.md`). |
| Design docs describe the present | §7 is rewritten in place, present tense, no changelog. The rejected alternatives live in the ADR. |
| Spec Kit cycle, `specs/` committed | This directory is committed with the change. |
