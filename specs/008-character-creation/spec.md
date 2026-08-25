# Feature Specification: Character creation

**Feature Branch**: `008-character-creation`

**Created**: 2026-08-25

**Status**: Draft

**Input**: GitHub issue #9 (R1.3), under Stage 3 (#42). A creation procedure complete enough that a
character can be made from a setting's data without a judgement call the rules do not cover. Out of
scope: the skill list (settled by #5/#33), character categories (#34, the stage's other child), and
the bootstrap script's implementation.

## Context

`16-chronicle-bootstrap.md` promises guided character creation and nothing said how many skills at
what values, what starting Stamina was, what starting Luck was, or what `mortality` set Fate to. An
agent running bootstrap had to invent them, and two runs would not agree — the failure the engine's
determinism rule exists to prevent.

Two things narrowed the answer before it was designed:

- **There is nothing to roll.** ADR 0013 settled that the engine has no characteristics, so the
  traditional opening move — generating a spread of attributes — has no object.
- **The advancement economy already has doors.** `03-rules.md` §6 opens a career-granted skill at
  25% and raises one by +5%. Creation either uses those or invents a second set to keep in step.

## Requirements

### FR-1 — One procedure, ordered and complete

Every step stated, in order, with each one's content sourced either from the engine or from named
setting data. Running it twice on the same inputs gives the same character.

### FR-2 — A character has a background, expressed as career progress

A new character is part-way through their first career. A pool of free advances is spent inside that
career, and how it is spent is who they were. No separate background skill list: advances may only
raise career-granted skills, so a skill from outside the career would be frozen at 25% forever.

### FR-3 — Every starting value is defined

Skills, Stamina, Luck, Fate, Fortune and every track. No value may be left to judgement.

### FR-4 — Starting Stamina is computed, not chosen

Four already-merged facts constrain it: the +1 from a completed career being "the only durable
toughening", "a character ten years in is not harder to kill", `check_aftermath.py`'s verified
assumption that a drop of 1–3 below zero is ordinary, and the engine's armour dice. A script must
demonstrate the value satisfies all of them.

`CLAUDE.md`: probability claims here have been wrong twice, and both were caught only by computing
them.

### FR-5 — The setting's obligations are stated

What a setting must provide for creation to run at all, so a setting missing one fails to load
rather than being filled in by the GM.

### FR-6 — Creation hands off cleanly

No creation-only rule that later stops applying, and no separate "starting character" state.
Succession runs the same procedure.

### FR-7 — The decision is recorded

Chosen-not-rolled has real rejected alternatives — rolled statistics, a point pool, a subset of the
career's skills — and someone will propose each again.

## Constraints

- Setting-agnostic; no setting or system name, in prose, example or table row.
- Values are engine **defaults**; `13-authoring-a-setting.md` already permits retuning them.
- Python 3.11+, stdlib only for the check.
- Nothing referenced that is not defined; the career cap remains Stage 9's (#12).

## Acceptance criteria

- [ ] A design document states every step, in order, and every starting value.
- [ ] The free-advance pool is derived from the diegetic skill bands, not picked.
- [ ] `check_creation.py` derives Stamina from the four constraints and exits zero.
- [ ] The script fails when a constraint is violated, not merely when the author disagrees.
- [ ] An ADR records chosen-not-rolled and its rejected alternatives.
- [ ] The setting's obligations are enumerated.
- [ ] Succession is shown to use the same procedure.
- [ ] `check_docs.py` and `backlog.py check` stay green.
