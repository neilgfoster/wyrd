# ADR 0012 — The design reset, and how decision records are consolidated

**Date:** 2026-08-25
**Status:** Accepted

## Context

Wyrd's design was built well and built **by topic**. Documents were written as subjects came up
rather than in the order the subjects depend on each other, and the recurring consequence is one
fault repeated: *a mechanic is referenced before it is defined*, in prose that reads as
authoritative.

Six instances, none found by reading:

| Referenced | Where | Defined |
|---|---|---|
| engine characteristics | [`13-authoring-a-setting.md`](../13-authoring-a-setting.md), the conversion contract | no |
| **Standing** | [`04-session.md`](../04-session.md), charged by Upkeep | no |
| `party_effective` | [`03-rules.md`](../03-rules.md) §7, the danger formula | no |
| damage-type critical tables | [`03-rules.md`](../03-rules.md) §2 | no |
| the skill list | [`03-rules.md`](../03-rules.md) §1 | no |
| the wound schema | [`06-state.md`](../06-state.md) | since the Aftermath family |

The structural cause is that **no document says what a character is**. The design goes from
resolution straight to combat, so five of the six follow from one absence.

Correcting this means revisiting the design in dependency order. That work — the design programme —
necessarily edits documents and decision records that this repository's own rules protect. Design
documents are rewritten in place already, so they present no difficulty. **Decision records are the
problem:** [`README.md`](../README.md) says a record is "never edited", and that rule exists for a
good reason — the rejected reasoning is as useful as the winning reasoning, and a record that can be
quietly rewritten is a record that cannot be trusted.

An authorised exception that is not written down is indistinguishable from drift. Hence this record.

## Decision

**The design programme is a reset. It may restructure the decision records, and it may never
destroy the reasoning in them.**

Three things are authorised, and the third is bounded tightly:

1. **A decision may be revisited.** Where a stage finds a decision wrong or superseded by what has
   been learned, it writes a **new** record. The old one is marked and kept.
2. **The set may be renumbered**, once, into a clean sequence.
3. **A record's `Status:` line may be edited.** That is the only edit an accepted record ever
   receives. Its context, decision, consequences and rejected alternatives are never touched.

**No record is deleted. At any point. For any reason.**

### The consolidation rule

**Marking.** A superseded record's status becomes `Superseded by ADR NNNN`. The record that replaces
it carries `**Supersedes:** ADR NNNN`. The link runs both ways so neither can be found without the
other.

**Location.** A superseded record moves to `design/adr/superseded/`.

**Numbering.** The archive keeps original numbers **permanently**. The live set is renumbered into a
clean sequence. So a reference to a superseded decision always resolves to the reasoning it meant;
only a record that stayed live and changed number needs its references rewritten.

This asymmetry is the point. Renumbering the archive too would leave a historical reference pointing
at whatever record inherited its number — worse than a dead link, because it resolves to the wrong
decision and reads as correct.

**Timing.** Numbers are **frozen for the duration of the programme.** The renumber is a single
operation in Stage 13, after the content has settled. During the programme a revisited decision takes
the next free number, which is what ADR numbering has always meant.

Timing is the part that is easy to get wrong. Renumbering as each record is reworked would break every
external reference once per stage — twelve rounds of reference churn, each an opportunity for the
bulk-substitution corruption [`CLAUDE.md`](../../CLAUDE.md) records three instances of in this repo.
Once, at the end, costs one round.

### What this does not authorise

- Editing an accepted record's reasoning. Only the status line moves.
- Deleting a record, or omitting one from the archive.
- Renumbering outside Stage 13.
- Treating "the programme authorised it" as a general licence. This record covers the programme and
  ends with it; afterwards the normal rule resumes, unchanged.

## Consequences

**The rule that mattered is preserved; the rule that got in the way is not.** "Never edited" was
protecting the rejected reasoning. That protection is now explicit and absolute, while the numbering
— which was never the thing worth protecting — is free to change.

**Renumbering has a cost, and it was accepted with the cost measured.** 76 references across 30
files, of which 11 are prose rather than links, plus **12 commit messages that can never be
corrected**. The commit messages are the irreducible loss and are recorded here rather than
discovered later.

**The silent half of that cost is now loud.** [`tools/check_docs.py`](../../tools/check_docs.py)
verified links but not prose, so `ADR 0005` breaking would have gone unnoticed — the programme's own
cleanup reintroducing the fault class the programme exists to remove. It now checks that every
`ADR NNNN` reference resolves, against the live set and the archive. Without that check this decision
would have been reckless rather than merely expensive.

**A reader can tell consolidation from drift.** Anyone finding an edited record can find this record
and see it was deliberate, bounded and dated.

## Alternatives rejected

**Leave the records untouched and reconcile them later.** Lowest risk and it defers the problem into
a worse position: records pointing at documents that have moved, been merged or been renumbered by
Stage 13, with no rule for what to do about it. The reset is the moment the rule is cheapest to set.

**Revise and delete freely.** The cleanest end state, and it throws away the thing the never-edit
rule was protecting. `CLAUDE.md` is explicit that the rejected reasoning is as useful as the winning
reasoning, and a decision looks obvious in hindsight precisely because the record of why the
alternative failed is doing quiet work.

**Never renumber; numbers are permanent identifiers.** The position argued when this was raised, on
the evidence above — 11 prose references nothing verified, 12 commit messages beyond repair, and the
observation that ADR numbers are conventionally identifiers rather than an ordering, since the number
already carries the chronology. The operator considered it and chose the clean sequence. Recorded
because it is the strongest case against what was decided, and a reader in a year deserves to see
that it was weighed rather than missed.

**Renumber, keeping an old→new redirect table.** Would make stale references recoverable instead of
wrong. Rejected as a second list of the same fact — the drift class this repository has been
corrected for more than any other. The archive keeping its own numbers achieves the same end without
a table to maintain.
