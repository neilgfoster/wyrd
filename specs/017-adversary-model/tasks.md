# Tasks: The adversary model

**Feature**: 017-adversary-model | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## The block, on paper first

- [x] T001 Enumerate every field the ruleset already reads off an opponent, with the rule that reads each one, from `03-rules.md` §2 and §7, `03a-1-criticals.md`, `03a-2-aftermath.md` and ADR 0019. A field no rule reads does not enter the block (FR-001).
- [x] T002 Draw the line against the character model: which of Taint, Trauma, Strain, Resolve, Fate, Luck, career, career history, Loyalty, bond and advancement an adversary does *not* carry, and what reads each of them for a character — so the omission is a decision rather than an oversight (FR-002).
- [x] T003 Confirm the three fields ADR 0019's crowd lookup reads are in the block under the names the rule cites, and fix whichever side is wrong rather than adding a synonym (FR-003).

## The computation

- [x] T004 `check_adversary.py` — the memoised exchange table first, before any figure is derived from it, so a corrected figure is not a full re-run of fight resolution.
- [x] T005 Compute the achievable ratio range — `party_effective / H(written_for)` across every party size and `written_for` a chronicle plausibly produces. This is the curve's input domain and it is computed before the curve is fitted (FR-013c).
- [x] T006 Fit the skill-adjustment coefficient by requiring the extremes of that computed range to land on ladder rungs. The logarithmic form is the candidate, not the conclusion — if realistic pairings land on values the engine cannot express, reject it and fit a stepped table instead (FR-013a, FR-013c).
- [x] T007 Assert the identity case exactly: party of `p` against `written_for: p` yields adjustment `+0`, for every `p` in range, as an exact equality (FR-013b).
- [x] T008 Assert monotonicity — the adjustment never rises as the party shrinks — and decide the rounding granularity, 5s or 10s, by which one preserves both that and the identity case (FR-013a).
- [x] T009 Compute the bound at both ends and state what happens past it: an adjusted skill that would exceed the top of the ladder, and one that would fall below zero. Both are reachable (FR-013c, SC-005a).
- [x] T010 Assert that across party size 1–6, `written_for` 1–6 and danger 1–6, no adjusted skill leaves the ladder the engine can express (SC-005a).
- [x] T011 Resolve a complete exchange against a written opponent: opposed test, degrees, telling blow, damage, armour subtraction, the minimum of 1, the drop below zero, the critical table selected by damage type, and Aftermath (FR-014, US2).
- [x] T012 Run the crowd lookup against a written mob body and a written nemesis, landing on opposite sides with the deciding field named — including the boundary case where the character's skill is exactly 20 ahead (US3, FR-003).
- [x] T013 Assert agreement with the figures earlier issues published: the one-blow band 67%–100%, 11% in the lightest armour, 33% at Stamina 2, the 1.25×–1.82× clear discount, and the drop rates 14.8% and 48.6%. Non-zero exit on any disagreement (FR-015, SC-006).

## The validator

- [x] T014 `tools/check_bestiary.py` — stdlib only, following `tools/check_docs.py`'s conventions; reports every failure rather than the first, and exits non-zero on any (FR-010).
- [x] T015 Required-field and unrecognised-field rejection, each naming the entry and the field. An unrecognised field is how a setting quietly adds a mechanism, so it fails rather than being ignored (FR-010, US1).
- [x] T016 Range rejection: armour rank outside the published set, damage type outside the closed four, percentage outside the scale in `03b-the-character.md` §2 (FR-011).
- [x] T017 Trait rejection: an effect outside the closed vocabulary (FR-012).
- [x] T018 A fixture bestiary exercising each rejection, plus one entry that passes. A validator with no failing case is a validator nobody has seen fail (SC-003).

## The worked example

- [x] T019 `worked-exchange.md` — one written opponent and one written character through a complete fight from the rules as written, every figure produced by `check_adversary.py` (FR-014, SC-002).
- [x] T020 The same encounter prepared at three party sizes, so the count scaling and the skill adjustment appear together rather than being described separately (US4, SC-005).
- [x] T021 Fold back what the worked exchange found, as rules rather than notes. It may add a field to the block, and that is what it is for.

## The rules

- [x] T022 `design/03d-the-adversary.md` — new: the block, field by field, with the rule that reads each (FR-001, FR-004, FR-005, FR-007).
- [x] T023 The baseline: what it is, that it is required, and that it is not a floor under a listed skill (FR-006).
- [x] T024 The closed trait vocabulary, in full, with each effect named against the mechanism it acts on (FR-012).
- [x] T025 What happens when an opponent that is neither character nor companion drops below 0 — the critical, and whether Aftermath is rolled — agreeing with §2's existing statement about a crowd (FR-008).
- [x] T026 `design/03b-the-character.md` §4 — rewritten in place; it currently says the adversary model is not yet decided (FR-016).
- [x] T027 `design/03-rules.md` §7 — the skill-value half made evaluable: the adjustment, the identity case, the bound, and the published table at the party sizes a table has (FR-013, FR-013a–c).
- [x] T028 `design/13-authoring-a-setting.md` — `bestiary.yaml` gains its schema and an example, in the shape the other setting files already use (FR-009).
- [x] T029 `design/14-entities.md` — the `creature` row says what a creature carries, and the nemesis note says a `character` used as opposition carries an adversary block (FR-009, FR-016).
- [x] T030 `design/README.md` — link the new document from the hub, in the same commit that creates it (SC-007).

## The record

- [x] T031 `design/adr/0025` — the thin adversary block, against the full character model (FR-002).
- [x] T032 `design/adr/0026` — the skill adjustment: additive, identity-exact, ladder-bounded, against multiplying the percentage by `danger_effective` (FR-013a).
- [x] T033 Link both ADRs from the ADR index so `tools/check_docs.py` passes.

## The guards

- [x] T034 Run `python3 specs/017-adversary-model/check_adversary.py`, `python3 tools/check_bestiary.py` over the fixtures, `python3 tools/check_docs.py`, `python3 tools/backlog.py check`.
- [x] T035 Grep `design/` and `README.md` for setting and system vocabulary, and for any term this feature names but does not define (FR-017, SC-001).
