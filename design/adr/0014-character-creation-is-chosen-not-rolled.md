# ADR 0014 — A character is chosen, not rolled

**Date:** 2026-08-25
**Status:** Accepted

## Context

[`16-chronicle-bootstrap.md`](../16-chronicle-bootstrap.md) has always promised guided character
creation from a setting's careers and names, and nothing said how many skills at what values, what
starting Stamina was, what starting Luck was, or what `mortality` set Fate to. An agent running
bootstrap had to invent those numbers, and two runs would not agree.

Two things narrowed the answer before it was designed.

**There is nothing to roll.** [ADR 0013](0013-the-engine-names-no-skill.md) settled that the engine
has no characteristics — so the traditional opening move of creation, generating a spread of
attributes, has no object. Skills come from a career, which is a choice.

**The advancement economy already has doors.** [`03-rules.md`](../03-rules.md) §6 says an advance
opens a career-granted skill at **25%** or raises one by **+5%** toward the career's cap. Creation
either uses those doors or invents a second set that would then have to be kept in step with them.

## Decision

**A character is chosen, not generated. Nothing at creation is rolled.**

- Pick an entry career; take **every skill it grants, at 25%** — the same door an advance uses.
- Spend **6 free advances** inside that career, under the ordinary spending rule. **This is the
  background**: a new character is already part-way through their first career, and how far and in
  which direction is who they were.
- **Stamina 6**, **Luck 40**, flat for everyone.
- **Fate** by the setting's `mortality`: `low` 2, `standard` 3, `high` 4. **Fortune** equals it.
- Every track the setting has not disabled starts at zero.
- Name, a Drive, a Bond, a place of origin — from the setting's tables.

The procedure is the engine's; the options are the setting's. There is one procedure, and a setting
may **retune** the values, which [`13-authoring-a-setting.md`](../13-authoring-a-setting.md) already
names as a permitted override.

Starting Stamina was **computed**, not picked — see
[`check_creation.py`](../../specs/008-character-creation/check_creation.py) and
[`03c-character-creation.md`](../03c-character-creation.md) §2.

## Consequences

**Background is expressed in the currency the game already uses.** No background skill list, no
origin table with mechanical weight, no second economy to keep in step with the first. A character's
past is visible in exactly the place their future will be — the spread of their career skills — and
it needs no setting data that careers do not already declare.

**Two characters of the same starting career differ, and differ meaningfully.** Six advances all on
one skill reads as *practised* in one thing and green in everything else; spread over six it reads as
a generalist who has seen a lot. Both are legal, neither is better, and the difference is a
statement about who the character was rather than a build.

**There is an allocation, and it buys no advantage.** This is the one place creation asks the player
to distribute anything, and the distribution is zero-sum inside a single career — depth costs
breadth. There is no optimum to find, only a shape to choose, which is why it does not reopen the
optimisation problem that talent trees and feats were rejected for
([ADR 0002](0002-source-material.md)).

**Nothing is frozen.** Because every advance is spent inside the starting career, every skill a
character has can still be raised by ordinary play. An earlier design gave background skills from
outside the career, and those would have sat at 25% permanently — advances may only raise
career-granted skills ([`03-rules.md`](../03-rules.md) §6) — producing competences the character
could never develop.

**Six is a ceiling, not a preference.** Seven advances would let a character open at 60%, which
[`10-diegesis.md`](../10-diegesis.md) calls *expert*. Beginning expert is what a chronicle is for.

**Bootstrap becomes deterministic.** Two runs against the same setting and the same answers produce
the same character. That is what makes it scriptable rather than a conversation the model has to get
right ([`07-tooling.md`](../07-tooling.md) §1).

**A career's skill list is now load-bearing.** Taking *every* granted skill means a career declaring
twenty skills produces a character with twenty skills at 25%, and one declaring four produces a
specialist. The engine does not police this — it cannot, having no skill vocabulary — so it is a
setting-authoring judgement with real mechanical weight.

**The values are engine defaults, not engine law.** A setting that wants fragile characters retunes
Stamina. What the engine fixes is that the number exists and is the same for everyone in that setting.

## Alternatives rejected

**Roll for Stamina, or for skill values.** The familiar shape, and here it buys variance in the one
place variance hurts most. With a single player character, a bad roll at creation is a chronicle
running for years from behind, with no party to compensate. Wyrd's randomness is deliberately placed
at the moment of action — the Wyrd die, the Aftermath table — where it produces story. At creation it
would only produce a worse starting position.

**A pool of points to distribute across skills, unconstrained.** Turns creation into an optimisation
exercise before the fiction has started, and needs a costing table the engine cannot write, since it
has no idea whether a setting's skills are broad or narrow
([ADR 0013](0013-the-engine-names-no-skill.md)). Constraining the pool to a single career's skills,
in the currency advances already use, is what makes it a background instead: the costing table is the
advance, and the career supplies the boundary.

**A separate background: an origin granting its own skills.** The obvious way to represent a life
before the career, and it fails on a rule already in place. Advances may only open or raise skills
*the career grants*, so a background skill from outside the career would sit at 25% for the whole
chronicle — a competence the character can never develop, and a second kind of skill the advancement
economy has no door for. It also needs a whole new class of setting data. Starting the character
part-way through their first career says the same thing about who they were, using machinery that
already exists.

**Rolling the background.** Attractive for a solo game, where a prompt beats an empty box, and
rejected on the same principle as rolled statistics: the line is *roll for identity, never for
capability*, and a spread of skill percentages is capability. A setting wanting the prompt can supply
a background table that suggests where to spend — as fiction feeding a choice, not as a generator.

**Take a *subset* of the career's skills — pick four of nine.** Preserves variety within a career and
reintroduces the optimisation problem in miniature, plus a number (four) that nothing determines.
Career completion — every granted skill at its cap — also becomes murkier if two characters of one
career are chasing different lists.

**Let the setting supply the whole procedure.** Maximum flexibility and it breaks the hard rule that
a setting may extend, retune, rename or disable but never add a mechanism
([`13-authoring-a-setting.md`](../13-authoring-a-setting.md)). Two settings would soon have
incompatible creation, and the bootstrap script would have to become a general interpreter.

**Fate falling as mortality rises.** The grimmer reading: a deadlier world gives fewer escapes. It
compounds rather than balances — a high-mortality setting would kill characters faster *and* give
them less to spend against it, which is a difficulty spiral rather than a tone. Fate is the
anti-frustration valve; the setting that needs the valve most gets the most of it.
