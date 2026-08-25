# Wyrd — the character

What a character is made of, and on what scale. The ruleset
([`03-rules.md`](03-rules.md)) rolls against these values; this document says what they are.

Every name here is an **engine** name. What a setting calls any of it is the setting's business
([`13-authoring-a-setting.md`](13-authoring-a-setting.md)), and renames are presentation-only.

---

## 1. What a character carries

| | What it is | Where it is specified |
|---|---|---|
| **Skills** | percentages, under names the setting supplies | §2 below |
| **Stamina** | current and maximum; cuts, bruises and losing control of the fight | [`03-rules.md`](03-rules.md) §2 |
| **The tracks** | Taint, Trauma, Strain, Resolve, Dread — those the setting has not disabled | [`03-rules.md`](03-rules.md) §4–5 |
| **Fate** and **Luck** | the death valve, and the tested counterweight | [`03-rules.md`](03-rules.md) §1, §3 |
| **A career**, and a career history | where competence comes from, and a biography | [`03-rules.md`](03-rules.md) §6 |
| **What has happened to them** | wounds, Marks, Reputation, Allegiances, Holdings, Bonds | [`06-state.md`](06-state.md), [`03-rules.md`](03-rules.md) §6 |

**Nothing else is numeric.** There are no characteristics, no attributes, no derived statistics. A
skill percentage is the only number a character rolls against, and difficulty modifies *it* rather
than the roll ([`03-rules.md`](03-rules.md) §1).

Why there is no layer beneath skills is recorded in
[ADR 0013](adr/0013-the-engine-names-no-skill.md).

## 2. Skills

**A skill is a name the setting owns and a number the engine understands.**

The engine guarantees the number: what it means, how it opens, how it grows, what bounds it. The
setting supplies the name and decides which skills exist at all
([`13-authoring-a-setting.md`](13-authoring-a-setting.md), the engine/setting contract).

### The scale

| | | Where it comes from |
|---|---|---|
| **Opens at** | 25% | an advance opens a skill the career grants ([`03-rules.md`](03-rules.md) §6) |
| **Rises by** | +5% per advance | the entire advancement economy ([`03-rules.md`](03-rules.md) §6) |
| **Bounded by** | the career's cap | completing a career means every granted skill at its cap ([`03-rules.md`](03-rules.md) §6) |
| **Rolled as** | `d100`, succeed at or under | [`03-rules.md`](03-rules.md) §1 |

What a given percentage *means* — from "you would be guessing" to "it is part of who you are" — is
tabulated once, in [`10-diegesis.md`](10-diegesis.md), because that is where the engine's own
vocabulary for describing a character to their player lives. It is not repeated here.

A character has a skill or does not — and **not having it does not mean not trying.** An untrained
test is taken at a flat **10%**, before difficulty and declaration
([`03-rules.md`](03-rules.md) §1). Anyone may try to shoot; almost nobody hits.

That base has to be stated rather than derived, because there are no characteristics to derive it
from ([ADR 0013](adr/0013-the-engine-names-no-skill.md)). Most percentile systems fall back to an
attribute; this one has nowhere to fall back to, so the engine names the number.

### What a setting declares

A skill entry is a name and the fiction around it. The engine assumes only this:

- **A stable identifier**, so state written years ago still resolves.
- **A display name**, which is what the player ever sees.
- **Which careers grant it**, because that is what makes it openable and what caps it
  ([`03-rules.md`](03-rules.md) §6).
- **Whether it may be attempted untrained.** Most skills may: a person who has never shot can still
  point a weapon and pull. Some cannot, and a setting says which — reading a language you do not
  speak, or performing surgery, is not a 10% chance, it is nothing. A skill is attemptable untrained
  unless the setting says otherwise, because that is the commoner case and the safer default.

The engine does not assume a category, a parent statistic, a governing attribute, or a fixed count.
A setting with eleven skills and a setting with ninety are both legal, and neither is more correct.

## 3. The engine names no skill

**No engine rule may refer to a skill by name or by category.** It has no vocabulary to do so with,
by design — see [ADR 0013](adr/0013-the-engine-names-no-skill.md).

Where an engine rule must act on a particular skill, it identifies it **by its relationship to what
happened**, and the value is carried in state rather than assumed:

| The rule says | It means |
|---|---|
| *the skill being tested* | whichever skill the current roll named |
| *the skill the wound bears on* | recorded on the wound when it was taken ([`06-state.md`](06-state.md)) |
| *a skill the career grants* | read from the setting's career graph |

This is what allows one engine to run a setting of swordsmen and a setting of void-pilots without a
mapping table between them.

### Wounds bind to a skill

A lasting wound with a `skill: -N` effect ([`03a-2-aftermath.md`](03a-2-aftermath.md)) records
**which** skill it bears on, taken from the roll that caused it. The wound to a sword arm burdens the
skill the sword arm was used for, under whatever name this setting gives it.

**The binding is optional.** Not every wound arrives through a skill roll — a fall, a fire, a
poisoning, a wound taken while unconscious. A wound with no skill behind it simply carries no
`skill: -N` effect; it may still cost Stamina or carry any other effect the table gives it.

## 4. Companions and adversaries

A companion is a person first and a small set of numbers second
([`04-session.md`](04-session.md)), and advances rarely and simply — one competence gained or
limitation lost at a downtime ([`03-rules.md`](03-rules.md) §6).

How an adversary is represented, and whether it uses this model or a deliberately thinner one, is not
yet decided. It is the subject of Stage 7 of the design programme and nothing here presumes the
answer.
