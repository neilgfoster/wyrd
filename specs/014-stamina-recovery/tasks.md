# Tasks: Stamina recovery and the fate of lasting wounds

**Feature**: 014-stamina-recovery | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## The computation

- [x] T001 `check_recovery.py` — model the damage scale from merged numbers and assert agreement with what #44/#13 computed: 1.56 through modest armour, 4.5 hits to drop (FR-9, FR-10).
- [x] T002 Compute Rallies to full from every reachable Stamina, at maximum 6 and 7, including the dropped case at 0 (FR-1, FR-9).
- [x] T003 Compute one ordinary fight's cost in Rallies, and assert a chronicle of ordinary fights converges rather than spirals under the clarified rate (FR-2).
- [x] T004 Compute the spiral threshold — the Stamina below which entering a fight means dropping in it — and the rest it demands (FR-3).
- [x] T005 Express downtime's automatic restore in Rallies, so both clocks compare on one axis (FR-2).
- [x] T006 Compute the Mend ladder against the Aftermath table's own accumulation rate (71% a lasting mark per drop), and assert the recurring wound never reaches closed (FR-4, FR-6).
- [x] T007 Assert every step of the Mend ladder lands on a value the closed effect set already permits (FR-8).
- [x] T008 Assert every figure the design documents publish, so a change to either fails rather than drifting (FR-11).

## The playtest

- [x] T009 `worked-recovery.md` — play a two-fight arc by hand: a fight that hurts, several beats of Rallies, a downtime with one undertaking spent, and a second fight entered short (FR-9).
- [x] T010 Fold back what the play found, as rules rather than notes.

## The rules

- [x] T011 `03-rules.md` §2 — the recovery rule: trigger, rate, the dropped combatant's restart, and the downtime restore (FR-1, FR-2, FR-3).
- [x] T012 `04-session.md` — the Rally gains its Stamina line; downtime gains the automatic restore, stated as costing no undertaking (FR-2).
- [x] T013 `04-session.md` — **Mend** gains its defined effect: one named wound, one grade per downtime (FR-5).
- [x] T014 `03a-2-aftermath.md` — replace "not this table's business" with the pointer, and answer the wound record's deferred healing question in place (FR-4).
- [x] T015 `03a-2-aftermath.md` — state the recurring wound's exemption where the "unless a later rule says otherwise" clause sits, with the Fate argument (FR-6).
- [x] T016 `06-state.md` — the wound record's closing field, additively; a closed record is kept, never deleted (FR-7).
- [x] T017 `03b-the-character.md` — the Stamina row points at the recovery rule.
- [x] T018 Rewrite each section in place. No changelog, no "previously we…" note (FR-13).

## The record

- [x] T019 ADR 0020 — Stamina recovery: the decision, and the rejected alternatives (full at every Rally, downtime only, Stamina as a Recover undertaking, a fraction of maximum on waking).
- [x] T020 ADR 0021 — mending: stepping rather than closing outright, the recurring wound's exemption, and the rejected alternative that wounds never mend at all.
- [x] T021 Add both ADR rows to the index in `design/README.md`.

## The gates

- [x] T022 Confirm nothing added introduces a third restoration clock, a new track, or a new die (FR-2).
- [x] T023 Confirm no rule here depends on the opponent rolling, or on a number the player-facing mapping removes (FR-12).
- [x] T024 Confirm no rule names a skill (ADR 0013) and no setting vocabulary or register entered `design/`.
- [x] T025 `python3 specs/014-stamina-recovery/check_recovery.py`, `python3 tools/check_docs.py` and `python3 tools/backlog.py check` green.
