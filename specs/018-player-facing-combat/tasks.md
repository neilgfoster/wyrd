# Tasks: Player-facing combat rolls

**Feature**: 018-player-facing-combat | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## The computation

- [x] T001 `check_conversion.py` — set up, stdlib only, exact arithmetic (`Fraction`). Reproduce and
  assert agreement with `check_mapping.py`'s mapping table before computing anything new (FR-002).
- [x] T002 Compute the degrees distribution produced by `tens(effective%) − tens(roll)` across the
  representative skill-gap span, and the resulting telling-blow rate at the current threshold of 3
  (FR-005, FR-006).
- [x] T003 Determine the corrected telling-blow threshold: a rate that stays a minority of hits at
  ordinary skill gaps and does not require a near-maximal gap to ever trigger, mirroring how ADR
  0016 originally framed the same question for the opposed test (FR-005, FR-006).
- [x] T004 Compute expected damage per exchange-round under today's double-gate opposed test and
  under the new single-roll structure, across the same realistic pairings `check_mapping.py` uses,
  and derive the actual damage-multiplier factor — confirming or correcting the issue's stated
  1.4×–3.1× (FR-010).
- [x] T005 Recompute starting Stamina's expected fight length (rounds to clear an opponent, rounds
  to be dropped) under the corrected damage rate from T004, against the values already published in
  `03-rules.md` §2 (dropped at Stamina 6/7, 4.6–4.9 rounds even, 2.2–3.3 rounds at +20), and either
  reaffirm them or produce corrected figures (FR-009).
- [x] T006 Confirm the Wyrd-die read stays uniform within the success and failure sets at both clip
  boundaries (`effective%` of 5 and 95) — the clip changes which percentage a roll is compared
  against, never the roll or its units digit (FR-011).
- [x] T007 Resolve a complete exchange from the rewritten rules — one attack roll, one defence roll,
  degrees, telling blow at the corrected threshold, damage, armour, the drop below zero, Aftermath —
  against a written character and a written opponent from
  `specs/017-adversary-model`'s schema (FR-001, FR-003, US1, US2).
- [x] T008 Assert agreement with every figure this feature depends on or touches: the mapping table
  from `check_mapping.py`, and (if Stamina changes) the one-blow crowd band and drop rates from
  `check_adversary.py`/`check_mobs.py`. Non-zero exit on any disagreement (FR-014, SC-005).

## The decisions this settles

- [x] T009 Decide whether two-sided opposed tests survive outside combat, and state the answer
  plainly — reaffirmed, narrowed, or retired entirely (FR-007).
- [x] T010 Write `design/adr/0027-*.md`, superseding ADR 0016 for combat's single-roll structure and
  recording T009's answer for what remains outside combat. ADR 0016 itself is left untouched
  (FR-008).
- [x] T011 Write `design/adr/0028-*.md`, recording the corrected telling-blow threshold (T003) and
  the damage-multiplier finding (T004), each as a computed figure with the rejected threshold/figure
  named (FR-006, FR-010).

## The rules

- [x] T012 `design/03-rules.md` §1 — narrow or remove the two-sided opposed-test description per
  T009's answer; the degrees formula's wording is unchanged, but its worked commentary is updated
  for `effective%` as the input (FR-007, FR-013).
- [x] T013 `design/03-rules.md` §2 — rewrite the exchange: the attack roll, the defence roll, the
  opponent never rolling, the corrected telling-blow threshold, and (if changed) the corrected
  starting-Stamina table (FR-001, FR-003, FR-005, FR-006, FR-009, FR-013).
- [x] T014 Confirm assistance (§1) is stated to apply identically to the attack and the defence roll
  — no attack-specific wording survives the rewrite (FR-012).
- [x] T015 Confirm the Wyrd die is stated as always read from the acting player's own roll, attack
  or defence, never simulated for the opponent (FR-011).

## The guards

- [x] T016 Run `python3 specs/018-player-facing-combat/check_conversion.py`,
  `python3 tools/check_docs.py`, `python3 tools/backlog.py check`.
- [x] T017 Grep `design/` and `README.md` for setting and system vocabulary, and for any term this
  feature names but does not define (SC-003, SC-004).
- [x] T018 Link both new ADRs from the ADR index so `tools/check_docs.py` passes.
