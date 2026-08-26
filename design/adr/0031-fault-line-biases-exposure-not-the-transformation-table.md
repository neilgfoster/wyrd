# ADR 0031 — The Fault Line biases Exposure's Taint gain, not the transformation table

**Date:** 2026-08-26
**Status:** Accepted

## Context

`03-rules.md` §4 named a Fault Line — "each character has a Fault Line derived at creation from
their Drives and Misfortune. It names *how* they fall — the direction, not only the quantity" —
and nothing read it. Two characters at the same Taint with different Fault Lines played
identically, which made the Fault Line prose rather than mechanism (#58).

Three places in the existing Taint machinery could plausibly carry the fix:

1. **Which transformation is rolled** — the Fault Line selects among effects on
   [`03a-3-transformations.md`](../03a-3-transformations.md)'s table instead of leaving the roll
   uniform.
2. **How the hidden threshold reads** — the secretly-rolled 1d6+2 that decides how many
   Transformations a character endures before being lost is skewed by direction.
3. **How Taint accrues** — Exposure, one of Taint's three gain routes, is biased by direction.

All three are real, and a future pass revisiting this area — including a future run of the design
programme itself — could plausibly propose either of the two not chosen here, having forgotten why.

## Decision

**The Fault Line biases Exposure's Taint gain.** When the GM judges an Exposure source runs with
the grain of a character's Fault Line — the same fiction-grounded judgment call §1 already uses to
invoke a Drive for −20 — a failed resistance gains Taint **one tier worse** (minor `1` → `2`,
moderate `2` → `3`, major stays at `3`), capped at one step per event, and independent of an
Invocation drawn against the same roll.

This is deliberately the smallest true fork: Exposure was already a plain
resisted-test-then-flat-Taint-number rule, and Drive invocation had already established the exact
judgment-call shape this reuses. It touches no die roll (the resolution roll to resist Exposure is
unmodified — only the Taint number consumed on a failure changes, so it does not compound
invisibly with the way Taint already bends the Wyrd die), and it touches no existing table.

## Alternatives considered and rejected

**Direction-keyed transformation rows.** Restructure
[`03a-3-transformations.md`](../03a-3-transformations.md) so each severity tier offers a small set
of direction-keyed effects, and the Fault Line picks among them instead of the 1d6 roll alone.
Rejected on two grounds. First, that table was only just settled (#18, merged) after resolving a
genuine body/mind collision in §4 — reopening its shape this soon to fork it by direction risks
exactly the fault `CLAUDE.md` names first among recurring ones: "two documents describing one thing
differently," here compressed into a single document now describing the same severity tier several
ways depending on a field most of the rest of the design never reads. Second, it requires
authoring a direction taxonomy with no existing anchor — Drives and Misfortune are prose, not a
closed vocabulary, and the engine is setting-agnostic, so any taxonomy invented here risks reading
as genre rather than mechanism, the fault CLAUDE.md calls "mechanic names carrying genre."

**A skew on the hidden threshold.** The secretly-rolled 1d6+2 (range 3–8, written once at a
character's first Transformation — [`03a-3-transformations.md`](../03a-3-transformations.md)) could
be biased up or down by direction, so some Fault Lines endure more Transformations before a
character is lost than others. Rejected because that number is, by design, never shown to the
player "in any form, including as unease" ([`10-diegesis.md`](../10-diegesis.md)) — a mechanical
difference the player can never observe or reason about is a weaker answer to #58's own acceptance
criterion ("two characters at equal Taint with different Fault Lines differ mechanically") than one
that shows up in play the next time Exposure is resisted.

## Consequences

- `03-rules.md` §4's Exposure subsection carries the tier-worse rule, its cap, and its
  independence from Invocation.
- `03a-3-transformations.md` is unchanged — verified by
  [`tools/check_fault_line.py`](../../tools/check_fault_line.py), which diffs it against `main` as
  part of this feature's own check.
- A setting authoring its own Fault Line taxonomy (`13-authoring-a-setting.md`'s existing "Fault
  Line derived from a culture rather than a Drive" retune) still lands on the same mechanism: the
  GM's judgment call is unchanged by how a setting derives the label.
