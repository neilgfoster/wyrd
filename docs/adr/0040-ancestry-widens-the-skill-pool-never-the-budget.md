# ADR 0040 — Ancestry widens creation's skill pool, never its budget

**Date:** 2026-08-27
**Status:** Accepted

## Context

Issue #121 asked how the engine accounts for a "tough dwarf vs. graceful elf" — a mechanical
difference along a species/ancestry axis. Nothing in `docs/design/` answers this: Stamina and
Luck are flat values fixed at creation (`05-character-creation.md`), and no species/ancestry
concept exists anywhere the entity model or creation rules are described. That silence is
plausibly deliberate — `26-authoring-a-setting.md`'s "a setting may never add a mechanism" rule
would forbid a setting from bolting on a stat-bonus mechanic the engine doesn't already provide —
but the reasoning was never written down, so a reader cannot tell "no mechanical species
differentiation, on purpose" from "not designed yet."

Creation already has exactly one door for character differentiation: **8 advances, spent under
`03-rules.md` §6's rules, constrained to the starting career's own skill list**
(`05-character-creation.md` §3). That constraint is what makes the result a background rather than
a shopping trip, and it is the only place in creation two characters can end up different.

## Decision

**A setting may optionally declare an ancestry — a species, lineage, or cultural grouping — that
grants a list of skills, exactly as a career does. Where a character has one, creation's 8
advances may be spent on any skill in the union of the starting career's list and the ancestry's
list. Ancestry grants no additional advances, and no Stamina, Luck, or other stat modifier.**

A setting with no ancestry concept declares nothing, and creation is unchanged: the eligible pool
is the starting career's list alone, exactly as it reads today.

## Why

**It reuses the mechanism the engine already has, rather than inventing one.** `03-rules.md` §6's
doors — open a skill at 25%, or raise one already open by +5%, both against a granted list — are
the only doors creation or advancement uses. Ancestry-as-a-second-list-source is the same door,
fed from a second, optional source; it is not a new roll, a new resource, or a new track. That is
what keeps this a setting-declarable extension rather than the engine mechanism
`26-authoring-a-setting.md` forbids a setting from adding on its own.

**It answers the issue's own example without a stat bonus.** A dwarf and an elf who both take the
same entry career now legitimately differ — they are choosing from different eligible sets under
the same budget — without the engine ever computing "+1 Toughness" or any other flat modifier.
That keeps Stamina and Luck flat exactly as `05-character-creation.md` already commits to, and
avoids inventing a stat axis the rest of the engine has no other use for.

**The budget stays untouched on purpose.** Widening the pool without widening the 8 advances means
depth still costs breadth — `05-character-creation.md`'s "there is no optimum, only a shape" holds
exactly as it did before ancestry existed. A character with an ancestry has more *choices*, not
more *character*.

## Alternatives rejected

**No mechanical species/ancestry differentiation at all — career and fiction only.** The
consistent minimal answer, and a legitimate one: it keeps the entity model exactly as it is and
needs no new vocabulary anywhere. Rejected because it leaves the issue's own example — two
characters with identical careers who should read as different — with no mechanical texture at
all, and the operator judged that gap worth closing with a design that costs nothing new rather
than leaving it to fiction alone.

**A separate ancestry advance budget** (e.g. ancestry grants its own N advances, spent only on its
own list, on top of the career's 8). Also workable, and closer to how a source system with
race-and-class layering typically handles this. Rejected because it is strictly more mechanism
than the union-of-lists approach for the same outcome: it introduces a second, ancestry-scoped
resource pool alongside the existing one, doubling the bookkeeping `check_creation.py` and
`check_advancement.py` already price against a single figure (8), for a result — two characters in
the same career reading differently — the wider-pool version already delivers with zero new
numbers.

**A flat stat/Stamina/Luck modifier per ancestry** (the literal "tough dwarf" reading of the
issue's example). Rejected outright: `05-character-creation.md` states Stamina and Luck are flat
at creation, and a per-ancestry modifier is exactly the kind of setting-declared *mechanism* —
rather than setting-declared *data feeding an existing mechanism* — that `26-authoring-a-setting.md`
forbids a setting from adding.

## Consequences

- `docs/design/11-character-creation.md` §3 gains an explicit statement of what ancestry is and
  is not permitted to do, next to the 8-advances rule it extends.
- No entity schema, career schema, or validator in this repository changes: career and skill data
  is setting-declared and lives in `wyrd-setting-*` repositories, not here, so this ADR closes a
  documentation gap without touching code.
- A setting author now has a concrete, minimal pattern to reach for when a world wants
  species/ancestry to matter mechanically, without inventing their own mechanism and risking
  drift from `26-authoring-a-setting.md`'s rule.
