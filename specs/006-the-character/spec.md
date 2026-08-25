# Feature Specification: The character

**Feature Branch**: `006-the-character`

**Created**: 2026-08-25

**Status**: Draft

**Input**: GitHub issues #5 (the skill list) and #33 (characteristics), the two children of Stage 2
(#41). They are one decision seen from two sides and are settled together. Out of scope: the career
cap value (#12, Stage 9) and starting skills at creation (#9, Stage 3).

## Context

Stage 2 of the design programme. Nine of the thirteen stages wait on it, because creation,
progression, adversaries, conversion and danger scaling all need to know what a character is made of.

The research found the gap is narrower and stranger than the issues describe. See
[research.md](./research.md); in short:

- **#5's fork is already decided.** `13-authoring-a-setting.md` states that the setting supplies
  skill names. What was missing is the *contract* a setting must satisfy.
- **Two rows of that same document disagree**, one saying settings supply skill names and one saying
  settings *extend* skills — which presupposes an engine list.
- **`03a-2-aftermath.md` gives two answers too**, saying both "the skill the wound bears on" and "the
  character's combat skill".
- **`characteristics: {combat, ranged, physical}` appears nowhere else in the design.** Nothing reads
  it. It is the residue of a character model that was never built.
- **The character model is mostly defined but scattered** across four documents, and never assembled.

## Clarifications

Settled with the operator: **the engine has no skill vocabulary.** A wound binds to whichever skill
was rolled, recorded by the setting's own name. There are no engine characteristics, no engine skill
roles, and no engine base skill list.

## Requirements

### FR-1 — One document says what a character is

A design document collects the character model: what a character carries, on what scale, and what a
percentage means. Assembling it from four documents is how `characteristics:` survived pointing at
nothing.

### FR-2 — The engine names no skill, ever

Engine rules refer to a skill only by its relationship to the fiction — "the skill the wound bears
on", "the skill being tested" — never by name or category. A setting's skill names are the setting's.

### FR-3 — A wound records the skill it bears on

`03a-2-aftermath.md` promises a `skill: -N` effect against "the skill the wound bears on" and the
state schema has nowhere to put which skill that is. The wound record gains the field.

### FR-4 — The engine has no characteristics

Recorded as a decision, not merely omitted. The `characteristics:` block leaves `conversion.yaml`,
and the ADR says why an engine that never names a skill needs no handles to name skills by.

### FR-5 — The contradictions are resolved, both directions

- `13-authoring-a-setting.md`'s *Extend* row stops claiming settings extend skills.
- `07-tooling.md`'s *Extend* row likewise.
- `03a-2-aftermath.md:199` stops naming a "combat skill".

Fixing one and leaving the other is how the fault recurs.

### FR-6 — The skill declaration has a contract

What a setting declares for a skill, and what the engine may assume about it. Without this, "the
setting supplies skill names" is not implementable.

## Constraints

- Setting-agnostic. No skill name may appear in `design/` as an engine-level example.
- Nothing may be given a value that a later stage owns — the career cap and starting skills are
  referenced by name, not invented.
- Design documents describe the present; no "previously we…" notes.
- `python3 tools/check_docs.py` and `python3 tools/backlog.py check` stay green.

## Acceptance criteria

- [ ] One design document describes the character; it is reachable from `README.md`.
- [ ] An ADR records that the engine has neither characteristics nor a skill vocabulary.
- [ ] `characteristics:` is gone from the conversion contract.
- [ ] Both *Extend* rows and `03a-2-aftermath.md:199` are corrected.
- [ ] The wound record carries the skill the wound bears on.
- [ ] A setting's skill declaration has a stated contract.
- [ ] No engine document names a skill.
- [ ] Grepping `design/` for `characteristic` returns only prose usage, not a mechanic.
