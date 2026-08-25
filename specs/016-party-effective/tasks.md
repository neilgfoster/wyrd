# Tasks: What a party counts for

**Feature**: 016-party-effective | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## The computation

- [x] T001 `check_party.py` — the effective-size function over 1–20 bodies in exact arithmetic, and the assertions that make it a curve: each further body adds strictly less than the one before, and the total is bounded well below the head count (FR-001, FR-003).
- [x] T002 Assert the identity case exactly, for every party size in range: `p` bodies against `written_for: p` yields `danger_effective` equal to `danger` — an exact equality, not a near one (FR-011).
- [x] T003 Compute scaled danger at the parties a real chronicle has — one player character with zero, one, two, three and four companions — against records written for four and for six, at every written `danger` from 1 to 6. Not at a midpoint (SC-002).
- [x] T004 Compute the retinue bound: what ten and twenty bodies actually buy against `written_for: 4`, so "a large retinue is not an exploit" is a computed property (US3).
- [x] T005 Assert the rounding rule at every awkward point — exact halves, and every case where a written quantity of at least 1 could otherwise round to 0 (FR-004, FR-005).
- [x] T006 Assert the degenerate inputs: `written_for` absent and `written_for: 0` both yield the ratio 1 (FR-006).
- [x] T007 Assert which companions count, from `status` alone, across all five values (FR-003).
- [x] T008 Assert every figure the design documents publish, including the figure that replaces "roughly danger 2" in `11-corpus-index.md`, so drift fails loudly rather than reading as authoritative (FR-009).

## The worked example

- [x] T009 `worked-scaling.md` — one arc record through the equation at three points in a chronicle's life: the player character alone, with two companions, and with a retinue, each derived quantity rounded at its own point of use and shown.
- [x] T010 Fold back what the worked example found, as rules rather than notes. It may change the rounding rule.

## The rules

- [x] T011 `design/03-rules.md` §7 — rewritten in place: the effective-size function, both sides of the ratio read through it, the identity case, and the degenerate cases (FR-001, FR-002, FR-007, FR-011).
- [x] T012 §7 — the single rounding rule applied at each point of use, with its minimum of 1, and the worked figures (FR-004, FR-005).
- [x] T013 §7 — why the curve is not overridable, and what a setting's levers over difficulty are instead (US3).
- [x] T014 `design/11-corpus-index.md` — the one-sentence description rewritten to agree with §7, and the quoted worked figure replaced with the computed one (FR-008).

## The record

- [x] T015 `design/adr/` — the ADR: the diminishing curve against a flat weight, and the symmetric reading of `written_for` against a raw denominator (FR-010).
- [x] T016 Link the ADR from the ADR index so `tools/check_docs.py` passes.

## The guards

- [x] T017 Run `python3 specs/016-party-effective/check_party.py`, `python3 tools/check_docs.py`, `python3 tools/backlog.py check`, and grep `design/` for setting vocabulary and for any surviving undefined term in §7 (FR-007).
