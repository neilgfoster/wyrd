# Feature Specification: Loyalty and party eligibility

**Feature Branch**: `009-loyalty-and-party-eligibility`

**Created**: 2026-08-25

**Status**: Draft

**Input**: GitHub issue #34, under Stage 3 (#42). Some settings offer mutually hostile kinds of
character, and those kinds would never travel together. The engine must know. Out of scope: any
setting's actual Loyalties, and capacity gates of other kinds (whether a character can work magic at
all belongs to #26).

## Context

The player runs one character and **the GM runs everyone else**, so "may this companion join?" is
answered dozens of times across a chronicle without anyone asking for it. Left to judgement it
drifts, and nothing about a party that should never have formed looks wrong.

It is engine work by the hard rule: a setting may extend, retune, rename or disable, and may never
add a mechanism. A constraint on party composition is a mechanism.

## Requirements

### FR-1 — A character carries a Loyalty

What they serve, or what they are. The engine fixes no values — a setting declares and names them,
the same way it declares skills.

### FR-2 — Three relations, not two

*(undeclared)*, **strained**, **irreconcilable**. A boolean forces the tense-but-possible pairing —
which is the case most settings actually contain — into being either forbidden or unremarkable, and
both readings discard what the setting was saying.

### FR-3 — Only non-default pairs are declared

A setting with one dividing line writes one line. A setting with none writes nothing.

### FR-4 — `strained` introduces no new machinery

Party Tension already measures this kind of friction and already says what happens when it
accumulates. A strained party is a party on a shorter fuse, not a special case.

### FR-5 — `irreconcilable` is refused, not warned

The engine declines to add the companion. A rule the GM is asked to remember gets forgotten
inconsistently, which ADR 0002 argues is worse than not having it.

### FR-6 — A changed Loyalty re-checks the party

Settings that allow conversion or corruption will use it. An existing pairing turned irreconcilable
breaks Tension immediately — machinery that already exists. The player's character is not exempt.

### FR-7 — No moral register enters the engine

The engine never says which Loyalty is the good one and has no vocabulary for them at all.

## Constraints

- Setting-agnostic; no Loyalty is named in `design/`.
- The name must not collide with `Allegiance`, `faction`, `Bond`, `Drive` or `Standing`.
- Settings declare Loyalties as **data**, never code.
- `check_docs.py` and `backlog.py check` stay green.

## Acceptance criteria

- [ ] A character carries a Loyalty in `06-state.md`.
- [ ] The three relations are specified, with `strained` feeding Party Tension.
- [ ] `irreconcilable` prevents a companion joining.
- [ ] A mid-chronicle Loyalty change has a stated outcome that reuses Tension breaking.
- [ ] The setting contract in `13-authoring-a-setting.md` lists what a setting must declare.
- [ ] Creation chooses a Loyalty.
- [ ] An ADR records why three relations rather than two, and why not a full matrix.
- [ ] No engine document names a Loyalty or implies one is preferable.
