# Tasks: Oracle prompt tables

**Input**: Design documents from `/specs/026-oracle-prompt-tables/`
**Prerequisites**: plan.md, research.md, data-model.md, quickstart.md (all present)

Single-threaded, ordered — each task depends on the ones before it landing in the same document.

- [X] **T001** Write `tools/check_oracle_prompts.py`: for each of the four `oracle-prompt-*`
  tables in `design/03a-6-oracle-prompts.md`, assert row ranges are contiguous, start at 1, and
  the last row is open at the top; assert every row carries the `checked` field. Matches
  `tools/check_bestiary.py`'s structural-validation style (module + `if __name__ == "__main__"`),
  not `tools/check_oracle_answers.py`'s probability-computation style — this family has no
  probability claim to compute (`research.md`).
- [X] **T002** Write `design/03a-6-oracle-prompts.md`:
  - What a prompt oracle is and why it's a distinct family from `03a-5-oracle-answers.md`
    (generates content vs. settles a question), per the issue's Context.
  - The four prompt families with stated rationale for the set (NPC objective, situation truth,
    thread turn, complication), each mapped to the existing structure it fills
    (`design/04-session.md`, `design/05-campaign.md` / `design/15-arcs-and-beats.md`).
  - The roll declaration block per family (`key`, `die`, `modifier`, `uniqueness`, `extra row
    fields`), matching the format used in `design/03a-5-oracle-answers.md`.
  - The four tables themselves, every row genre-neutral and carrying `checked`, with the
    grim/comic reading check recorded per row (a table column or explicit per-row statement).
  - The obligation clause: when the GM must roll rather than invent, per `research.md`.
  - The recording section (beat-log entry shape from `data-model.md`).
  - The "what a setting may replace/extend" section, referencing the amended `extend:` mechanism
    from T004.
- [X] **T003** Amend `design/03a-tables.md`:
  - Oracles index row: link `03a-6-oracle-prompts.md` alongside the existing
    `03a-5-oracle-answers.md` link (per spec Clarifications — one row, two documents).
  - "What a setting may replace" section: add the additive-extension path (append rows above the
    engine's own range, contiguous, last row stays open at the top) as distinct from wholesale
    `tables:` replacement.
- [X] **T004** Amend `design/13-authoring-a-setting.md`: `extend:` gains tables as an extendable
  kind alongside careers/talents/gear/creatures, with an example entry
  (`extend: {oracle-prompt-npc-objective: setting/rules/tables/oracle-prompt-npc-objective-extra.yaml}`),
  consistent with the "may extend, retune or disable; never add a new mechanism" framing already
  there — this is a generalisation of an existing override kind, not a new mechanism.
- [X] **T005** Check `design/02-architecture.md:91` and `design/07-tooling.md:84` against the
  final filename and layout; amend only if either has gone stale.
- [X] **T006** Run verification: `python3 tools/check_oracle_prompts.py`; grep `design/` for
  setting/system vocabulary; `python3 tools/check_docs.py` for reachability.
- [X] **T007** `ruff check . && ruff format --check .` and `python3 -m pytest -q` (repo-wide gate
  before PR).
