---

description: "Task list for 002-aftermath-table"
---

# Tasks: The Aftermath table

**Input**: Design documents from `/specs/002-aftermath-table/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/aftermath-table.md,
quickstart.md, check_aftermath.py

**Tests**: No test suite — this repository has no engine yet. Verification is
[`check_aftermath.py`](./check_aftermath.py) for everything with a computable answer, plus the
grep-and-read pass in [quickstart.md](./quickstart.md) for everything without one. Per `CLAUDE.md`
these are run, not asserted. The script already exists and passes: it was written during planning
because it was the only way to test the `mortality` design, and it rejected the first draft.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)

## Path Conventions

Design documentation at `design/`, decision records at `docs/adr/`. No source tree is touched:
`engine/` does not exist and is not created here.

---

## Phase 1: Setup

**Purpose**: Fix the document's shape before any rows go into it, so the stories below fill
independent sections rather than negotiating structure.

- [x] T001 Create `docs/design/06-aftermath.md` with its title, a one-paragraph statement of what the
      family is and when it is rolled, and its section headings only. Sections: the roll; when it is
      rolled; the table; the lasting wound; the recurring wound; closing the death rows; companions;
      what a setting may replace. Present tense, no changelog (`docs/README.md`).

**Checkpoint**: the document exists and its shape is fixed.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the family's declaration and the trigger have to be settled before rows can be written
against them — every row's range depends on the roll, and the whole table depends on when it fires.

- [x] T002 [US1] Write the **family declaration** section of `docs/design/06-aftermath.md` from
      [contracts/aftermath-table.md](./contracts/aftermath-table.md): key `aftermath`; roll
      `d100 + (5 × points below zero)`; lowest possible total 6, showing the arithmetic; last row
      open at the top and why (the modifier is unbounded); **repeatable**, with an explicit note that
      the exhaustion clause of `docs/design/04-tables.md` does not apply because the family is not
      unique; **no extra row fields**, stating that no rule reads a severity for this family
      (FR-002, FR-003, FR-006, FR-007).

- [x] T003 [US1] Write the **when it is rolled** section: after the fight, never during it; once per
      combatant who dropped however many times they dropped; resolution order between multiple
      downed combatants changes nothing. State the boundary with the critical table — criticals
      resolve during the fight, per damage type; Aftermath resolves after it — so the sibling issue
      writing criticals has a fixed edge to write against (FR-001, US1 scenario 1).

**Checkpoint**: the roll, its modifier and its trigger are fixed. Rows can now be written.

---

## Phase 3: User Story 1 — Resolving a combatant who dropped (Priority: P1) 🎯 MVP

**Goal**: a dropped combatant resolves to exactly one applied outcome, with no judgement call the
document does not cover.

**Independent test**: take a character who dropped to −3 Stamina, roll, and follow the document alone
to one row, one applied effect, one recorded outcome.

- [x] T004 [US1] Write the **table** into `docs/design/06-aftermath.md`: all eight rows, each carrying
      range, effect and description, exactly as fixed in
      [contracts/aftermath-table.md](./contracts/aftermath-table.md). Effects stated so they can be
      applied without reading the prose; descriptions carrying no tonal register (FR-004, FR-005,
      FR-008, FR-009, FR-025).

- [x] T005 [US1] Add the **reading procedure and the recorded outcome**: roll, apply the modifier,
      find the row, apply the effect, say the description, record with the table key — per
      `docs/design/04-tables.md`. Include the log shape from [data-model.md](./data-model.md) §6,
      including `fate_spent` (US1 scenarios 2–4).

- [x] T006 [US1] Add the **weighting** paragraph, quoting the computed figures from
      [research.md](./research.md) D8 — a lasting mark 70.8% against death 22.9% across drops of
      1–12, and that a drop of 1 or 2 cannot reach the death row at all. State that death overtakes
      marks past a drop of 12 rather than claiming death is always rare. Cite
      `check_aftermath.py` as the authority, not the prose (FR-010, FR-026).

- [x] T007 [US1] Run `python3 specs/002-aftermath-table/check_aftermath.py` against the rows **as
      written in the document** — reconcile `ROWS` in the script with the document's table and fix
      whichever is wrong. This is quickstart step 2, and it is the step that catches the table
      drifting from its own checker.

**Checkpoint**: US1 is independently complete — a dropped combatant can be fully resolved.

---

## Phase 4: User Story 2 — The lasting wound record (Priority: P1)

**Goal**: a lasting wound is a thing state holds and a later rule can read.

**Independent test**: apply a lasting-wound result, write the record, confirm a recovery rule could
key on it.

- [x] T008 [US2] Write the **lasting wound** section of `docs/design/06-aftermath.md` from
      [data-model.md](./data-model.md) §2: what a wound record is, its fields, and the closed set of
      effects (`stamina_max`, `skill`, `dread`). State that an effect naming an unknown mechanic is a
      load error rather than a row quietly ignored (FR-011, FR-012).

- [x] T009 [US2] State explicitly that the record carries **no healing field, no duration and no
      severity**, and why: whether a wound heals is R1.2's decision, and a field shaped for one
      answer would prejudge it. Adding one later is additive under `docs/design/29-evolution.md`
      (FR-013, SC-008).

- [x] T010 [US2] Amend `docs/design/22-state.md`: give the existing `wounds: []` field its record shape,
      in place, present tense, no changelog. Cross-link to `docs/design/06-aftermath.md`. Add the
      diegetic-rendering note pointing at `docs/design/13-diegesis.md` — a wound is "the knee never set
      right", never `skill: -10` (FR-011, FR-023, US2 scenario 2).

**Checkpoint**: R1.2 has something to give a fate to.

---

## Phase 5: User Story 4 — Fate, and closing the death rows (Priority: P1)

**Goal**: the two mechanics that both claim the moment of death resolve to one reading.

**Independent test**: roll a death result with Fate remaining, spend it, follow both documents to one
unambiguous outcome.

> Sequenced before US3 despite the lower story number: US3's recurring wound is the row a closed
> death result lands on, so this section fixes what that row has to bear.

- [x] T011 [US4] Write the **closing the death rows** section of `docs/design/06-aftermath.md`: one
      mechanism, two things that invoke it — a spent Fate point, and `mortality: low`. Deterministic
      re-read on the worst non-death row; no second roll, no GM judgement. State that Fate may be
      spent **only** against a `death` result and never to improve another row (FR-016, FR-020).

- [x] T012 [US4] State the **`mortality`** clause explicitly: `low` closes the death rows for
      everyone; `standard` and `high` read the table as written. Note that `mortality` does not
      modify the roll, and why — [research.md](./research.md) D2, where making it a `±10` adjustment
      broke the range contract at `low` and let a drop of 1 kill at `high`. This honours the claim
      `docs/design/01-principles.md` already makes about `mortality` (FR-020).

- [x] T013 [US4] Write `docs/adr/0009-fate-closes-the-death-rows.md`: the decision that Fate closes
      the death rows rather than suppressing the roll, the rejected alternatives (suppress entirely;
      declare before rolling), and why — a suppressed roll makes "survives and is not better off"
      prose with no mechanism under it. Note that `mortality: low` reuses the same mechanism.
      Numbered and dated; an accepted ADR is never edited afterwards (FR-027).

- [x] T014 [US4] Confirm against `docs/design/03-rules.md` §3 that nothing here contradicts Fate's
      existing boundaries: Fate buys against dice and never against agendas; a companion is saved
      only when the player is present and able to act; declining to spend is recorded. Fix the new
      document if it drifts, not `03-rules.md` (US4 scenarios 1–3).

**Checkpoint**: the death moment has exactly one reading.

---

## Phase 6: User Story 3 — The recurring wound (Priority: P2)

**Goal**: an ongoing effect that fires deterministically at every future fight.

**Independent test**: give a character a recurring wound, start three fights, confirm the same effect
fires each time with no per-fight judgement.

- [x] T015 [US3] Write the **recurring wound** section: a wound record with `recurring: true`; fires
      when a fight begins, before the first roll; applies `−10` to the character's combat skill for
      that fight; imposes nothing between fights; persists for the rest of the chronicle unless a
      later rule says otherwise; stacks, because the family is repeatable (FR-014, US3 scenarios 1–2).

- [x] T016 [US3] State **why `−10` and not a new number**: `docs/design/03-rules.md` §1 already publishes
      `−10` as the Challenging step, and already establishes that difficulty modifies the skill and
      never the roll — so the recurring wound leaves the Wyrd die clean. Record that a Strain-based
      version was rejected because the ruleset never says what Strain does ([research.md](./research.md)
      D7) (FR-015).

**Checkpoint**: all five promised outcome shapes now have a mechanical definition.

---

## Phase 7: User Story 5 — Companions (Priority: P2)

**Goal**: a dropped companion resolves from this document alone.

**Independent test**: resolve a dropped companion without reading the player rules and guessing what
transfers.

- [x] T017 [US5] Write the **companions** section: same table, same modifier, same rows. The only
      difference is the valve — companions have no Fate of their own, so a death row stands unless
      the player is present, able to act, and spends theirs. State explicitly that there is no
      companion-specific row, modifier or table, and why adding one would double-count a fragility
      the ruleset already has (FR-017).

- [x] T018 [US5] State the **state changes** for a companion outcome, using only values
      `docs/design/22-state.md` already declares: `status: dead` on an unsaved death, `status: away` while
      captured. Do not invent a status value (US5 scenario 3).

**Checkpoint**: US5 complete.

---

## Phase 8: Entities and the remaining outcome shapes

**Purpose**: two rows create things in the world; both must reuse the shapes `docs/design/25-entities.md`
already fixes rather than recording free text.

- [x] T019 [P] Write the **new enemy** clause: the `new-enemy` row creates a `character` entity with
      `role: nemesis`, `disposition: hostile`, and a populated `objective` block — required, because
      an enemy without an objective is a note rather than a character that acts while the player is
      elsewhere. Link `docs/design/25-entities.md` (FR-018).

- [x] T020 [P] Write the **capture** clause: the `taken` row opens a `thread` entity, the type
      `docs/design/25-entities.md` already has for an open loop the chronicle carries. Say what ends it is
      the chronicle's business, not the table's.

- [x] T021 [P] Write the **disfigurement** clause: the `disfigured` row's wound has effect
      `dread: +1`, feeding the existing Dread track. State that no second social-consequence mechanic
      is introduced, because Dread already is one (FR-019).

- [x] T022 State that **Trauma is unchanged** by this table: `docs/design/03-rules.md` §5 already awards
      1 Trauma per critical taken, and awarding more here would double-count the same blow
      ([data-model.md](./data-model.md) §5). This is the kind of interaction that silently
      double-counts if nobody writes it down.

---

## Phase 9: Wiring the document into the design set

**Purpose**: two documents currently describe a table that does not exist. Both must stop.

- [x] T023 Amend `docs/design/03-rules.md` §2: link `03a-2-aftermath.md`, and stop describing the table as
      a promise. The five outcome shapes now live in the table, so the sentence names the mechanism
      and points at it rather than enumerating what the table will contain. Present tense, in place,
      no "previously" note (FR-021, FR-023).

- [x] T024 Complete the **Aftermath row** of the index in `docs/design/04-tables.md`: roll
      `d100 + 5 × points below zero`, uniqueness `repeatable`, and replace "not yet written" with a
      link to `03a-2-aftermath.md`. Check every cell against
      [contracts/aftermath-table.md](./contracts/aftermath-table.md) rather than against memory
      (FR-022, SC-007).

- [x] T025 Grep for **anywhere else** that describes Aftermath as undefined or future —
      `docs/design/01-principles.md`, `docs/design/16-session.md`, `docs/design/27-tooling.md`,
      `docs/design/24-authoring-a-setting.md`, `docs/design/23-chronicle-bootstrap.md`,
      `docs/design/29-evolution.md`. Update in place where the description is now wrong; leave alone where
      it is merely a reference (FR-023).

- [x] T026 Write the **what a setting may replace** section: rows via `overrides.tables:`, keyed
      `aftermath`. A setting may not change the die, the modifier, the uniqueness, the row schema, or
      how the death rows close — the last because Fate depends on that mechanism. `mortality` is the
      lethality knob a setting already has.

---

## Phase 10: Polish & verification

**Purpose**: run the checks rather than assert them.

- [x] T027 Run `python3 specs/002-aftermath-table/check_aftermath.py`. Must exit `0`.

- [x] T028 Run quickstart steps 2, 3 and 5 — document rows against the script's `ROWS`, every outcome
      key present, index row complete. Fix whatever disagrees.

- [x] T029 Run quickstart step 4 — grep every added and changed file for setting and system names.
      Then **read** the rows for the thing grep cannot catch: a label that needs a particular book to
      understand, or a description carrying a register the setting should own (FR-024, FR-025,
      SC-006).

- [x] T030 Run quickstart step 7 — read `docs/design/03-rules.md` §2 and §3 against
      `docs/design/06-aftermath.md` and confirm each of the four interactions resolves to exactly one
      reading. This is `CLAUDE.md` fault class 3 and no script finds it (SC-005).

- [x] T031 Walk the four manual cases in [quickstart.md](./quickstart.md) using the finished document
      alone — including the two that share a roll and differ only by a spent Fate point (SC-001).

- [x] T032 Re-check the Constitution Check in [plan.md](./plan.md) against the finished diff, and
      confirm `specs/002-aftermath-table/` is committed (FR-028).

---

## Dependencies

- **Phase 1** blocks everything: the document must exist.
- **Phase 2** blocks Phases 3–8: every row's range depends on the declared roll.
- **Phase 3 (US1)** is the MVP. It is independently complete and shippable on its own.
- **Phase 5 (US4)** is sequenced before **Phase 6 (US3)** because a closed death result lands on the
  recurring-wound row; US3 then writes what that row does.
- **Phase 4 (US2)** blocks **Phase 6 (US3)**: a recurring wound is a wound record with a flag, so the
  record has to exist first.
- **Phase 8** depends on Phase 3 (the rows exist) and is internally parallel — T019, T020 and T021
  touch different sections.
- **Phase 9** depends on the document being substantially written; T024's index row must match the
  finished declaration.
- **Phase 10** is last, and is the only phase that may not be skipped.

## Parallel opportunities

- T019, T020, T021 — different clauses, no shared state.
- T013 (the ADR) is a separate file and may be written any time after T011 fixes the decision.
- T010 (`docs/design/22-state.md`) touches a different file from the rest of Phase 4.

## Implementation strategy

**MVP** is Phases 1–3: the table exists, is declared, and resolves a dropped combatant. Everything
after that closes a promise `docs/design/03-rules.md` has already made, and R1.2 needs Phase 4.

The one non-negotiable is Phase 10. `CLAUDE.md` records that this repository's probability claims
have been wrong twice and that both were caught only by computing them — and `check_aftermath.py`
has already rejected one design in this feature that read perfectly well.
