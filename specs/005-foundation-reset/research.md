# Research: Foundation review and the reset

**Feature**: 005-foundation-reset | **Date**: 2026-08-25

## 1. The foundation review — finding: sound, no amendment

`docs/design/01-principles.md` (197 lines) was re-read in full against what the programme has surfaced:
no engine mechanism for magic, no defined character model, no representation for adversaries, and
five scarce resources never treated as one system.

| Section | Finding |
|---|---|
| The brief | Holds. One player, text only, short sessions, years of elapsed time, setting-agnostic. |
| Seven engine principles | Hold. Each is about an LLM GM's failure modes or a long chronicle's guarantees; none depends on a mechanic the programme is changing. |
| The tone contract | Holds. One deliberate non-change, below. |
| The GM contract | Holds. MUST / MUST NOT / MAY are stated so they can be checked, which is the property that matters. |
| The division of labour | Holds. Illustrative rather than exhaustive, so new mechanics do not invalidate it. |
| Six success criteria | Hold. All are play-level and none is affected by the programme. |

Recorded explicitly because **"reviewed and unchanged" and "not reviewed" are indistinguishable in a
diff.** A stage that legitimately changes nothing has to say so, or the next reader cannot tell it ran.

## 2. The deferred tone knob

The tone contract declares `prophecy`, `victory`, `power_curve`, `scope`, `scale_drift`, `mortality`
and `register`. It has no knob for how commonplace supernatural power is, and adding one is tempting
now that magic is in scope (#26).

**Deferred to Stage 10, deliberately.** `mortality` is the model to follow: it is meaningful only
because `03a-2-aftermath.md` defines exactly what it does — closes the death rows. A magic knob added
now would point at a mechanism that does not exist, which is the programme's founding fault in
miniature. The knob, if needed, is defined when the thing it modifies is.

## 3. The cost of renumbering, measured

Raised with the operator, who confirmed the renumber should go ahead. Recorded here so the cost is
on the record rather than discovered later.

| Reference kind | Count | Fixable? |
|---|---|---|
| Markdown links (`adr/0009-…`) | 31 | yes — script, and `check_docs.py` already verifies them |
| Prose references (`ADR 0005`) | 11 | yes by script, but **nothing verified them** before this feature |
| Files containing either | 30 | — |
| **Commit messages** | **12** | **no — permanent** |
| Open issue bodies | 5 | yes, by hand |

`ADR 0005` alone accounts for 11 of the prose references — it is the deterministic-over-inference
record, cited throughout.

The 12 commit messages are the irreducible cost and are recorded as accepted in ADR 0012. Everything
else is made checkable, which is what turns a silent breakage class into a loud one.

## 4. Why superseded records keep their original numbers

The obvious scheme renumbers everything into one sequence. It has a flaw: a reference to a *superseded*
decision — the reasoning that was rejected, which `CLAUDE.md` values as much as the winning reasoning —
would point at whatever record inherited that number. Worse than a dead reference, because it resolves
to the wrong thing and reads as correct.

Freezing the archive fixes it: `docs/adr/superseded/0009-….md` means what it always meant. Only
records that stayed live and moved number need their references rewritten, and those are checkable.

## 5. Why the renumber waits for Stage 13

A record revisited in Stage 2 and renumbered immediately breaks every reference to it. A record
revisited in Stage 5 does the same. Twelve stages of that is twelve rounds of reference churn, each
one an opportunity for the bulk-substitution corruption `CLAUDE.md` records three instances of.

Doing it once, at the end, when the content has settled, costs one round. During the programme a
revisited decision simply takes the next free number — which is what ADR numbering has always meant.
