# Tasks: Player-facing opposed tests

**Feature**: 029-player-facing-opposed-tests | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## The computation

- [x] T001 `check_opposed_generalisation.py` — set up, stdlib only, exact arithmetic (`Fraction`).
  Reproduce and assert agreement with `specs/012-combat-sequencing/check_mapping.py`'s `effective%`
  mapping table before computing anything new (FR-009).
- [x] T002 Grep `design/` for every live citation of "opposed test" as a mechanism (excluding ADR
  0016's own historical definition), and classify each: already routes through the player-facing
  shape, needs rewriting to it, or is the two-player-controlled-entities carve-out — this is what
  settles whether ADR 0016 has any remaining live scope (FR-007, FR-008).
- [x] T003 Confirm assistance, declaration and the untrained-10% rule compose with the generalised
  roll exactly as they already compose with combat's attack/defence rolls — check against the
  existing rule text and `specs/018-player-facing-combat/check_conversion.py`'s worked examples, no
  new interaction to compute (FR-005).
- [x] T004 Resolve a worked non-combat opposed test end to end — a player character or companion
  opposed by an NPC/opponent, one roll against `effective%`, degrees read
  `tens(effective%) − tens(roll)` — across representative skill gaps from `check_mapping.py`'s span,
  confirming the rewritten rule reproduces the same numbers combat already produces at the same gap
  (FR-001, FR-002, FR-003, US1).
- [x] T005 Assert agreement with every figure this feature touches or depends on: the mapping table
  from `check_mapping.py`. Non-zero exit on any disagreement (FR-009, SC-003).

## The decision this settles

- [x] T006 From T002's classification, decide explicitly what happens to a contest between two
  player-controlled entities with no NPC/opponent side — reusing ADR 0016's existing "GM names an
  actor, or two ordinary tests" carve-out, per the plan's load-bearing decision, unless T002 turns
  up a reason it does not fit (FR-004, US2).
- [x] T007 Write `design/adr/0035-*.md`, superseding ADR 0016 — in full if T002 confirms no live
  scope survives outside combat and the two-player-controlled-entities carve-out, in part if T002
  turns up a genuine surviving use of the two-sided shape. Records T006's answer. ADR 0016 itself is
  left untouched (FR-008).

## The rules

- [x] T008 `design/03-rules.md` §1 — rewrite "Opposed tests" to the player-facing shape, generalised
  from §2's combat wording rather than duplicated from it: single player roll against `effective%`
  wherever one side is an NPC/opponent, opponent's dice never consulted, failure simply fails the
  action (FR-001, FR-002, FR-003, FR-006).
- [x] T009 `design/03-rules.md` §1 — state T006's answer for the two-player-controlled-entities case
  explicitly, replacing the implicit "where neither is acting" framing with the resolved rule
  (FR-004).
- [x] T010 `design/03-rules.md` §2 — revisit the "Combat does not use this shape" cross-reference to
  §1, since §1 no longer describes a different shape from what §2 already does (FR-006).
- [x] T011 Confirm no other document under `design/` is left describing or depending on the retired
  two-sided shape — resolve every citation T002 found that needed rewriting (FR-007).

## The guards

- [x] T012 Run `python3 specs/029-player-facing-opposed-tests/check_opposed_generalisation.py`,
  `python3 tools/check_docs.py`, and `python3 tools/backlog.py check`; all three exit zero (SC-003).

## Dependencies

- T001 → T002 → T006 → T007 (the ADR cannot be written before the classification and the decision
  it depends on are settled)
- T003, T004, T005 can run in parallel with T002 once T001 is done — they don't depend on its
  classification result
- T008, T009, T010 depend on T006/T007 (the rules text follows the decided ADR, not the reverse)
- T011 depends on T002's list and T008–T010's rewrites
- T012 last, after every other task

## Parallel execution example

Once T001 is done, T002, T003, T004 and T005 touch different concerns (grep classification vs.
composition check vs. worked example vs. figure-agreement assertion) and can be worked in any
order or concurrently within the same check script.

## Implementation strategy

**MVP scope**: T001–T005 (the computation) plus T006–T007 (the ADR) are the load-bearing decisions
— once those land, T008–T011 (the rules text) is a direct transcription of what they settled, and
T012 is verification. There is no meaningful partial-delivery slice smaller than the full set: a
half-rewritten `03-rules.md` §1 would leave the design corpus in the "two documents describing one
thing differently" fault class CLAUDE.md names explicitly.
