# Research: The character

**Feature**: 006-the-character | **Date**: 2026-08-25

## 1. The skill-list fork was already decided, and nobody re-read the table

Issue #5 asks the engine to "decide whether the skill list is engine-level or setting-level". It is
decided. [`24-authoring-a-setting.md`](../../docs/design/24-authoring-a-setting.md), in the engine/setting
contract:

| Engine provides | Setting supplies |
|---|---|
| `d100` resolution, degrees of success, the Wyrd die | **skill names** |

So there is no engine skill list, by a decision already written down. What #5 identified correctly is
that **the contract a setting must satisfy** was never specified — which is a different and smaller
job than the fork it was framed as.

## 2. Two rows of one document disagree about it

The same file, thirty lines later, in the permitted-overrides table:

| Override | Example |
|---|---|
| **Extend** | add setting-specific skills, careers, talents, gear, creatures |

*Extend* presupposes a base list to add to. [`27-tooling.md`](../../docs/design/27-tooling.md) agrees with
this reading — "a data file appended **to a list** — skills, careers, gear, creatures".

Both readings are internally coherent, which is exactly why neither looks wrong. This is fault class
3 in `CLAUDE.md` — two documents describing one thing differently, findable only by reading them
against each other.

**Resolution:** *extend* is the right verb for careers, gear and creatures, which do have engine-side
structure. It is the wrong verb for skills, which a setting **declares** outright.

## 3. The Aftermath document also gives two answers

| Line | Says |
|---|---|
| `03a-2-aftermath.md:177` | a penalty "to **the skill the wound bears on**" |
| `03a-2-aftermath.md:199` | "−10 to the character's **combat skill**" |

Line 199 names a skill the engine cannot know, because skill names are the setting's. Line 177 is
right and line 199 is the bug. Confirmed by the operator: the engine has **no** skill vocabulary, and
a wound binds to whichever skill was rolled.

## 4. `characteristics:` is vestigial

`13-authoring-a-setting.md:193` maps a source system onto engine characteristics:

```yaml
characteristics:
  map: {combat: weapon-skill, ranged: ballistic-skill, physical: strength}
```

`combat`, `ranged` and `physical` appear **nowhere else in the entire design.** Nothing reads them,
nothing writes them, no rule refers to them. They are the residue of a character model that was never
built.

With the decision in §3, they have no purpose: an engine that never names a skill needs no handles to
name skills by. The block goes.

**This closes #33's dangling reference** — the conversion contract's target is not undefined, it is
unnecessary.

## 5. The character model is more defined than #33 claimed — just scattered

#33 says the engine "never says what a character is". That overstates it. The pieces exist:

| Property | Where | State |
|---|---|---|
| skills as percentages | `03-rules.md` §1 | defined |
| what a percentage *means* | `10-diegesis.md` — a five-band table from "you would be guessing" to "part of who you are" | **defined, and good** |
| opening value | `03-rules.md` §6 — a new skill opens at **25%** | defined |
| increment | `03-rules.md` §6 — **+5%** per advance | defined |
| upper bound | `03-rules.md` §6 — the **career's cap** | named, value undefined (#12, Stage 9) |
| Stamina | `03-rules.md` §2, `06-state.md` | defined |
| the record | `06-state.md` | defined |
| characteristics | — | **do not exist, and should not** |
| all of it in one place | — | **missing** |

So the honest gap is not "nothing is defined". It is that a reader must assemble the character from
four documents, and that assembly has never been written down — which is how `characteristics:`
survived pointing at nothing, and how the diegetic band table came to be the only place the skill
scale is stated.

## 6. What is deliberately not settled here

- **The career cap value.** Named by `03-rules.md` §6 and owned by #12 in Stage 9. Stating a number
  now would be inventing one.
- **Starting skills at creation.** Owned by #9 in Stage 3, which is downstream of this.

Both are referenced by name against documents that define them, so neither adds a dangling reference.
