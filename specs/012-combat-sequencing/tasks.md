# Tasks: Combat sequencing, ranged combat, flight and surprise

**Feature**: 012-combat-sequencing | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## The computation

- [x] T001 `check_mapping.py` — settle the player-facing mapping's slope and clip (FR-11a). *(done during specify)*
- [x] T002 `check_sequencing.py` — model a whole fight to completion at realistic pairings (25–55%), under the current opposed rule, and report fight length in rounds (FR-14).
- [x] T003 Compute the value of acting first: the win rate of the side that takes the first round against an otherwise identical opponent (FR-2).
- [x] T004 Compute the value of a **free** round — the surprise gate (FR-8). Model the whole fight, not one exchange; a free round removes a round of the other side's attrition as well as adding one.
- [x] T005 Compute the ambush bonus across candidate rungs of the existing ladder, and pick one. No new rung is invented (FR-10). **Chose +20** — a rung of the ladder, and the ceiling of the declaration bonus, which fixes its meaning.
- [x] T006 Compute the cost of fleeing — expected parting-blow damage at realistic opponent counts — so FR-7's "never free" is a quantity (FR-7).
- [x] T007 Assert only what this feature decides. Anything the script reveals about the player-facing conversion is reported for the sibling issue, not asserted (FR-11b).

## The playtest

- [x] T008 `worked-exchange.md` — play one complete exchange by hand against the drafted rules: a ranged opening, a closing to engagement, an attempt to flee. Record every roll (FR-13).
- [x] T009 Check the played outcome against what `check_sequencing.py` predicts, and record any disagreement as a finding rather than smoothing it over.

## The rules

- [x] T010 `03-rules.md` §2 — define the round and the turn: one action, and what an action may be (FR-1, FR-4).
- [x] T011 `03-rules.md` §2 — turn order: whoever started it acts first, including the mutual-encounter fallback, and zero rolls (FR-2, FR-3).
- [x] T012 `03-rules.md` §2 — engagement as one binary state; closing costs the closing combatant their action (FR-5a, FR-6).
- [x] T013 `03-rules.md` §2 — ranged attacks: the engaged-shooter rung, cover and visibility, all on the existing ladder (FR-5).
- [x] T014 `03-rules.md` §2 — flight: the parting blow, then the group test in the everyone-must-get-through shape (FR-7).
- [x] T015 `03-rules.md` §2 — surprise costs the first round; ambush eases the first round's attacks (FR-8).
- [x] T016 Rewrite §2 in place. No changelog, no "previously we…" note; the section describes the present engine (FR-15).

## The record

- [x] T017 ADR 0018 — the sequencing decision, and the rejected alternatives: an initiative roll, named range bands, free disengagement, and surprise as a modifier rather than a lost round.
- [x] T018 Name the mutual-encounter fallback in the ADR as the metagame compromise it is, rather than leaving it to be discovered.
- [x] T019 Add the ADR 0018 row to the index in `design/README.md`.
- [x] T020 Raise the sibling issue under #44 for the player-facing conversion, carrying `check_mapping.py`'s slope and 5–95% clip (FR-11b).

## The gates

- [x] T021 Grep `design/` for positioning vocabulary — grid, metre, movement rate, facing, range in numbers — and confirm this feature added none (FR-9, SC-006).
- [x] T022 Confirm every added rule modifies the **skill**, never the roll, and that no shape introduces a second omen or a rerolled one (FR-10).
- [x] T023 Confirm nothing added depends on the opponent rolling except the flight test, which is stated as a difficulty (FR-11).
- [x] T024 Confirm the turn order is concrete enough for the mob rule (#13) to be written against (FR-12).
- [x] T025 `check_docs.py` and `backlog.py check` green.
- [ ] T026 Commit referencing #11, open the PR.

## Dependencies

T002–T007 gate T015 (the surprise rule ships only if the free round computes as survivable) and
T013 (the ambush rung is chosen, not picked). T008 depends on a draft of T010–T015 existing to play
against, and T009 feeds back into them — the playtest is allowed to change the rules, which is the
point of doing it before they are settled. T017 depends on everything above it. T021–T024 are
verification and run last.

## What the playtest changed

T008/T009 were not a formality. Playing five rounds found three rules that were missing and were
needed immediately, and all three are now in §2:

1. **A surprised combatant still defends.** "Does not act" could reasonably have meant "cannot
   defend", which would roughly double what surprise is worth and would contradict
   `check_sequencing.py`, which models the surprised side as defending normally.
2. **Shooting into someone else's close engagement** needed a difficulty and a consequence. It is
   one rung harder, and an Ill Omen hits the ally instead.
3. **Flight needed a stated difficulty ladder** rather than a GM's guess: Challenging for one
   pursuer, one rung harder for each further one.

## What the computation changed

The first draft of `check_sequencing.py` used a mean damage of 4 against Stamina 6 — two hits to
drop, where issue #44 established 4.5. Every fight came out roughly three times too short and the
value of surprise was overstated by half. That is the same fault #44 caught, reintroduced, and it
was caught here only by cross-checking the round counts against #44's own table. The damage figure
is now calibrated and asserted rather than chosen.
