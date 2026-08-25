# ADR 0013 — The engine names no skill, and has no characteristics

**Date:** 2026-08-25
**Status:** Accepted

## Context

Wyrd resolves everything by rolling `d100` under a `skill%`
([ADR 0001](0001-resolution.md)). Two questions about what sits under that percentage had never
been answered, and were raised as separate issues because they look separate.

**Are skills the engine's or the setting's?** Already answered, in a table nobody re-read.
[`13-authoring-a-setting.md`](../13-authoring-a-setting.md)'s engine/setting contract states that the
engine provides `d100` resolution, degrees of success and the Wyrd die, and the setting supplies
**skill names**. What was genuinely missing is the contract a setting must satisfy — a smaller job
than the fork it was raised as.

**Does a layer exist beneath skills?** `13-authoring-a-setting.md` maps a source system onto engine
characteristics:

```yaml
characteristics:
  map: {combat: weapon-skill, ranged: ballistic-skill, physical: strength}
```

`combat`, `ranged` and `physical` appear **nowhere else in the design.** Nothing reads them, nothing
writes them, no rule refers to them. They are the residue of a character model that was never built —
and a conversion contract whose target does not exist is a specification that reads as authoritative
and is not.

The two questions turn out to be one, because a layer beneath skills would only earn its place if
some engine rule needed to *name* a skill. Three passages looked like they did:

| Passage | What it wanted |
|---|---|
| [`03a-2-aftermath.md`](../03a-2-aftermath.md), the wound effect | "the skill the wound bears on" |
| [`03a-2-aftermath.md`](../03a-2-aftermath.md), the worked example | "the character's **combat skill**" |
| [`03-rules.md`](../03-rules.md) §7, danger scaling | "skill values scale from the same number" |

The second is the only one that names anything, and it names something the engine cannot know. The
same document, twenty lines earlier, states the general rule correctly.

## Decision

**The engine has no characteristics, no skill categories, and no skill list. It never refers to a
skill by name.**

A skill is **a name the setting owns and a number the engine understands.** The engine guarantees the
number — opens at 25%, rises +5% per advance, bounded by the career's cap
([`03-rules.md`](../03-rules.md) §6), rolled `d100` under. The setting supplies the name and decides
which skills exist at all.

Where an engine rule must act on a particular skill, it identifies it **by relationship**, and the
value is carried in state:

- *the skill being tested* — whichever the current roll named
- *the skill the wound bears on* — recorded on the wound when it was taken
- *a skill the career grants* — read from the setting's career graph

A lasting wound therefore records which skill it burdens, taken from the roll that caused it. The
binding is optional: a fall, a fire or a wound taken while unconscious has no skill behind it and
carries no `skill: -N` effect.

The `characteristics:` block leaves the conversion contract. A setting converting a source system
maps its skills to its own skill names; there is no engine vocabulary in between for them to pass
through.

## Consequences

**A setting-agnostic engine becomes literally true rather than aspirational.** No engine document can
name a skill, because there is nothing to name. A setting of swordsmen and a setting of void-pilots
need no mapping table between them, and the "no setting vocabulary in `design/`" rule stops depending
on vigilance for the one category most likely to leak.

**#33's dangling reference is closed by deletion rather than by definition.** The conversion
contract's target was not undefined; it was unnecessary. That is the cheaper of the two ways to
resolve a reference to nothing, and it is available more often than it is taken.

**Wounds gain a field, and the state schema gains a rule.** `bears_on` is optional, and its absence
is meaningful rather than missing data.

**The engine must state an untrained base, because there is nothing to derive one from.** Most
percentile systems let an untrained character fall back on a characteristic. Removing characteristics
removes that floor, so [`03-rules.md`](../03-rules.md) §1 names a flat **10%** instead — anyone may
try to shoot; almost nobody hits. A setting may mark a skill as requiring training, and then there is
no untrained attempt at all. This was missed when the decision was first written, and the omission
said the opposite: that difficulty and declaration already covered it. They cannot. Difficulty
modifies the *skill*, so with no skill there is nothing for it to modify.

**The engine cannot balance skills against each other.** It has no idea whether a setting's skill set
is eleven broad skills or ninety narrow ones, so it cannot warn that one is too broad. That is
correct: it is the setting author's judgement, and an engine that policed it would be making genre
decisions.

**Two contradictions are removed, in both directions.** `13-authoring-a-setting.md` and
[`07-tooling.md`](../07-tooling.md) both describe settings as *extending* skills, which presupposes a
base list. Settings **declare** skills; they extend careers, gear and creatures, which do have
engine-side structure. Fixing one and leaving the other is how the fault recurs.

## Alternatives rejected

**A small closed set of engine roles** — `combat`, `ranged`, `physical` — that every setting maps its
skills onto. This is what the conversion contract already assumed, and it is the option that makes
"the character's combat skill" legal. Rejected on two counts: it is a second vocabulary every setting
must maintain alongside its own, and the closed set has to be right for a pre-modern setting and a
far-future one simultaneously. Every attempt to enumerate it is a genre statement. The engine gets
the same expressive power by reading the skill off the roll, at no vocabulary cost.

**An engine base skill list that settings extend.** Reconciles the *Extend* rows by making them
literally true, and contradicts the engine/setting contract outright. Any list is a genre statement:
a set with *Ride* and no *Pilot* is a pre-modern engine wearing a general-purpose label.

**Characteristics as a layer beneath skills**, in the traditional shape — a skill derives from an
attribute. Familiar, and it buys nothing here. It exists in other systems to give an untrained
character a fallback number and to make skills cheaper to generate; Wyrd has no unskilled default by
design, and generates skills through careers. Adding the layer would mean inventing a second scale,
a derivation rule, and a conversion story for both — to answer a question the design does not ask.

**Leaving `characteristics:` in place as a documentation stub.** Harmless-looking and the reason the
gap survived this long. A block that maps onto nothing is worse than an absence, because it reads as
a specification.
