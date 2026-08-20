# WFRP 3rd edition — what Wyrd takes from it

Sourced from the 3e *Core Rules* (98pp), *Player's Guide* (306pp), *Games Master's Guide*
(178pp) and *Liber Mutatis* (50pp). Full 3e line is in the library — 109 PDFs.

Mechanics summarised for implementation. Not a substitute for the books.

## The paradox

3e is, as written, **the worst possible edition to play over text.** It is a boxed game:
custom symbol dice, action cards, talent cards, punchboard tokens, cardboard standups,
plastic bases, a stance meter built from interlocking puzzle pieces, recharge tokens,
progress trackers. Almost none of that survives a phone.

And yet it has **the best conceptual toolkit of any edition for what Wyrd is trying to
do** — because 3e is the only WFRP that seriously designed *structure*: how a session is
shaped, how a party frays, how a story advances, how corruption keeps speaking between
crises.

**Strip the components, keep the concepts.** Everything below is a concept, not a card.

## 1. Episode / Act / Rally Step — the session shape

This solves the twenty-minutes-on-a-train problem directly.

- **Story mode** — "zoomed out", narrated broadly, used when events advance the story but
  carry little conflict and order does not matter.
- **Encounter mode** — "zoomed in", used when actions are opposed, sequence matters, or the
  player wants to play it out in character.
- **Episode** — "a single cohesive activity... usually over a short amount of time,
  resolved within a single setting" (which may be as broad as "a castle" or "the trading
  road"). Chasing a band of cultists is an episode.
- **Act** — "a single goal or action within that episode." Searching the temple is one act;
  fighting the cultists in the cellar is a second; stopping them collapsing the building is
  a third. Three-act structure: tension, fulfilment, resolution — and "the third act may
  often become a springboard for the next encounter."

**The Rally Step** is the pause between acts, and it is both narrative and mechanical. On a
Rally Step everyone: moves their stance one step toward neutral, removes a recharge token,
**recovers 1 stress and 1 fatigue**, and may take one rally action (a manoeuvre, first aid,
or a Resilience check to shed fatigue). The GM evaluates the previous act and may award
fortune.

**For Wyrd this is the save point.** A mechanically defined pause with recovery attached,
occurring naturally between acts, is exactly what an interrupted session needs. "Stop at
the Rally Step" is a real answer to "I have to get off the train."

## 2. Party Tension — the companion mechanic

The party shares a **party sheet** holding shared resources and a **party tension meter**:

> "Party tension is a representation of the friction, anxiety, and apprehension a group of
> heroes struggle with in the face of new challenges, arguments within the party, or as
> consequences for certain roleplaying actions."

Triggers push a token along the meter; spaces on the track fire effects; **reaching the end
fires a severe effect and resets the meter to zero.**

**This is the single most useful mechanic in 3e for Wyrd**, because Wyrd's party is entirely
NPCs. Party tension turns companions from scenery into a system: it gives the GM a
principled, visible, self-resetting reason to generate inter-party drama — an argument, a
desertion, a betrayal — on a schedule driven by what actually happened, rather than
inventing friction arbitrarily. It is the mechanism that makes an NPC party feel alive
instead of decorative.

Note *Liber Mutatis* uses it exactly this way: a wizard's unsettling behaviour makes the
others "apprehensive and push the party tension meter up a notch."

## 3. Corruption — GM Invocation

3e's corruption track is conventional: points accumulate; a **threshold** set by race and
Toughness; exceeding it forces a **mutation** (humans) or an **insanity** (elves, dwarfs,
halflings — resistant races take it in the mind, not the body). Each mutation/insanity has
a **severity rating** equal to the corruption it consumes, so you drop back below threshold
— and if still over, you draw again, repeating until you are under.

Exposure tiers mirror 4e: minor / moderate / major, resisted with a Resilience check.

**The part worth stealing is GM Invocation:**

> "Before a player performs an action, the GM may take one of the character's corruption
> points and replace it with a purple challenge die added to the task's dice pool... The GM
> narrates how the corruption is manifesting... an overwhelming sense of temptation, painful
> cramps, or whispered daemonic voices only the character can hear."

Max one per check, and it **consumes** the point.

This is the missing half of the corruption design. 4e's **Dark Deal** lets the *player*
spend their soul to succeed. 3e's **GM Invocation** lets the *GM* spend it to make things
harder, with narration attached. Together they make corruption a live, two-directional
presence between mutation thresholds instead of a number that only matters when it crosses
a line.

For Wyrd, invocation is also self-limiting in exactly the right way: it costs the GM the
resource it spends, so it can't be leaned on indefinitely.

## 4. The Progress Tracker — scenario clocks

A track advanced whenever the players make progress, with **event spaces** that fire GM
actions when reached. The published example lists concrete triggers — the PCs find the
suspicious books, locate the herb garden, notice a cult member behaving oddly, hear the
ravings of a madman — and at the first event space the GM steers them to an undiscovered
overt clue; at the final space they find the hidden Chaos temple.

Crucially, the guidance is anti-railroad:

> "The Progress Tracker is a tool to ensure that the story progresses, not a brake
> restricting the rate of discovery. If the players arrive at a key discovery early, simply
> advance the Progress Tracker to the appropriate event space."

This is the **clock** mechanism Wyrd needs for scenarios, already documented in a Warhammer
book. It is how a situation stays a situation — pressure and inevitability without a script.

## 5. Narrative dice — outcome texture

3e rolls a pool of symbol dice rather than a number. Beyond success/failure it yields:

| Symbol | Meaning |
|---|---|
| Success / Righteous Success | success; righteous also rolls another die |
| Challenge | cancels a success |
| **Boon** | a benefit — *can occur on a failure* |
| **Bane** | a complication — *can occur on a success* |
| **Chaos Star** | serious negative side effect; falls back to a bane if nothing eligible |
| **Sigmar's Comet** | powerful positive effect, or count as success/boon |
| Delay | the action takes longer; costs initiative or recharge |
| Exertion | 1 stress (mental task) or 1 fatigue (physical) |

The valuable idea is that **outcome is two-dimensional**: did you succeed, *and* what else
happened. Succeed-at-a-cost and fail-with-a-consolation are first-class results, not GM
improvisation.

Warlock's `d20 + skill >= 20` is flat binary. Wyrd can recover most of this texture with no
extra dice by reading the **margin**: a bare pass (hit 20-21) carries a bane; a large margin
carries a boon; a natural 1 or a catastrophic miss reads as a Chaos Star. That gives an LLM
GM structured narration hooks on every single roll — which matters enormously, because
"what else happened" is precisely where an unconstrained model otherwise invents.

## 6. Stress & Fatigue — two damage tracks

3e separates **fatigue** (physical) from **stress** (mental), distinct from wounds. Failed
mental tasks cost stress; physical ones cost fatigue; both recover at the Rally Step.

Warlock's Stamina already does the physical job. **Stress is worth adding as the
short-term mental counterpart to the long-term Insanity track** — the thing that accrues in
a bad night and mostly clears by morning, while Insanity is what never quite does.

## 7. Stance — the risk dial

Characters sit somewhere on a **reckless ↔ conservative** meter, converting dice
accordingly, adjustable at the start of a turn, and drifting back toward neutral at each
Rally Step. Some actions require a stance; a Troll Slayer's signature strike is far more
devastating when reckless.

For Wyrd this reduces to a stated posture that shifts the risk/reward of rolls and decays
toward neutral when you pause — cheap to run in text, and it gives the player a dial to
express intent without adding a subsystem.

## Assessment

3e is where Wyrd should get its **structure**, not its resolution:

| Take | Leave |
|---|---|
| Episode / Act / Rally Step session shape | Action & talent cards |
| Party Tension | Custom symbol dice |
| Corruption GM Invocation | Punchboard, standups, bases |
| Progress Tracker clocks | Stance meter puzzle pieces |
| Bane/Boon/Chaos Star outcome texture (via margin) | Recharge token economy |
| Stress as a short-term mental track | Encounter-mode positioning |

Combined with Warlock's resolution, 2e's Fate points and Insanity, and 4e's Dark Deals,
the four editions cover between them nearly everything Wyrd's engine needs. What remains
genuinely original to Wyrd is the **meta-campaign** layer — 3e's "Developing a Campaign and
Linking Stories" chapter is the closest prior art and is still written for a group meeting
weekly, not one player over years.
