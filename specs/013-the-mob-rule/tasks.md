# Tasks: The crowd rule

**Feature**: 013-the-mob-rule | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## The computation

- [x] T001 `check_mobs.py` — model damage through armour across the weapon band and find where one ordinary hit stops removing a body (FR-2, FR-8).
- [x] T002 Assert the threshold sits on a real line: the qualifying body passes the one-blow bar on the **worst** weapon in the band, and the body one Stamina up fails it. **Rejected the first draft** (Stamina 3, light armour) at 16.7% on a mid-band weapon.
- [x] T003 Assert the armour clause does work: the same body in the lightest armour must fail the bar.
- [x] T004 Compute the rolled-out clear rate at real skills under both resolution models, and report the discount the free clear represents (FR-4).
- [x] T005 Bound the discount under the mapping (≤2×) and report the opposed-test figure without gating on it (FR-4, FR-7).
- [x] T006 Compute what the crowd does back: rounds to put a starting character below zero, at real body counts, armoured and not (FR-5).
- [x] T007 Compute where weight of numbers saturates, and assert the largest real crowd can reach that ceiling against the largest real party (FR-5, FR-8).
- [x] T008 Compute rounds to clear at real party and crowd sizes, and assert a lone unarmoured character **loses** to six bodies (FR-8).
- [x] T009 Anchor the skill gap to merged numbers — the untrained 10% and the 25% a skill opens at — and assert it is neither free on the day a skill opens nor five advances away (FR-3).
- [x] T010 Assert agreement with the damage scale #44 established: 1.56 through modest armour, 4.5 hits to drop (FR-9). **Caught a real disagreement** — an earlier draft used the band mean and computed 2.15 and 3.26.
- [x] T011 Assert every figure `docs/design/03-rules.md` publishes against the model, so a change to either fails rather than drifting (FR-10).

## The playtest

- [x] T012 `worked-crowd.md` — play one complete crowd fight by hand against the drafted rule: three characters, nine bodies, and one opponent who does not qualify (FR-11).
- [x] T013 Fold back what the play found, as rules rather than notes: the clear requires close engagement; companions clear too; a crowd's parting blow is one attack, not one per body.

## The rules

- [x] T014 `03-rules.md` §2 — the clear: who, when, how many, at what cost (FR-4).
- [x] T015 `03-rules.md` §2 — the qualifying test, as a table read off the opponent's own sheet (FR-2).
- [x] T016 `03-rules.md` §2 — the skill gap replacing *weaker* (FR-3).
- [x] T017 `03-rules.md` §2 — the crowd's attack, weight of numbers, and its ceiling (FR-5).
- [x] T018 `03-rules.md` §2 — state that the Aftermath table is not rolled for a crowd, before someone rolls it twenty times.
- [x] T019 Rewrite the section in place, under a title carrying no register. No changelog, no "previously we…" note (FR-12).

## The record

- [x] T020 ADR 0019 — the decision, and the rejected alternatives: keeping *petty*, defining a crowd member by skill alone, scaling the clear with degrees, letting the crowd roll per body, and no ceiling on weight of numbers.
- [x] T021 Answer the *petty* naming question explicitly in the ADR, with the reason it fails `CLAUDE.md`'s naming rule (FR-1).
- [x] T022 Record in the ADR what this constrains for the adversary model (#54): an adversary must be able to state a maximum Stamina and an armour rating, and need state nothing else.
- [x] T023 Add the ADR 0019 row to the index in `docs/README.md`.

## The gates

- [x] T024 Confirm every added rule modifies the **skill**, never the roll, and introduces no second omen, no new die and no new track (FR-6).
- [x] T025 Confirm no rule here works only because the opponent rolls (FR-7).
- [x] T026 `python3 tools/check_docs.py` and `python3 tools/backlog.py check` green.
