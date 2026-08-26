# Oracle prompts

The tables the GM rolls to **generate content the fiction hasn't specified yet**, instead of
inventing it: what an NPC actually wants, why a situation isn't as presented, what a thread turns
on, what complicates a scene. Where [`03a-5-oracle-answers.md`](03a-5-oracle-answers.md) settles a
yes/no question, this document generates the content an LLM GM would otherwise reach for
unconstrained — and, left unconstrained, reach for the same handful of dramatic shapes, then
escalate them across sessions.

It is a variant of the `oracles` family [`03a-tables.md`](03a-tables.md) commits to, sharing that
family's one index row with `03a-5-oracle-answers.md`. Everything below is declared within
`03a-tables.md`'s conventions.

---

## Why this is a separate document from the answer table

[ADR 0005](adr/0005-deterministic-over-inference.md) is the same principle behind both documents,
but the failure mode differs. An answer oracle keeps a settled fact from being re-invented
differently later. A prompt oracle keeps *invented* content itself from collapsing onto the same
few shapes — the GM's motive for an NPC, or its reason a scene isn't as presented, tends to
default to whichever the model reached for most recently, and default reaches trend toward
escalation. Verification differs to match: an answer table is checked by computing its
probabilities; a prompt table is checked by reading every row against two opposite registers and
confirming neither breaks it — there is no probability to compute here, because the risk this
closes isn't about the odds of a roll, it's about the shape of what a roll produces.

## The four prompt families

Four, and no more — the minimum that constrains invention where it actually runs loose in the
existing design, not a general table of atmosphere. Each is scoped to a place the design already
holds a structure that generated content has to land in:

| Family | Fills the gap in | Constrains |
|---|---|---|
| **NPC objective** | `objective.wants` on a companion, or the equivalent unstated motive on any NPC ([`04-session.md`](04-session.md)) | what a character actually wants, distinct from what they say |
| **Situation truth** | a scene the GM is about to narrate | why what's presented isn't the whole story |
| **Thread turn** | a thread's next beat ([`05-campaign.md`](05-campaign.md), [`15-arcs-and-beats.md`](15-arcs-and-beats.md)) | what changes about an open loop, and why now |
| **Complication** | an ordinary scene | what makes the next moment harder than it looked |

Considered and rejected: a broader table of atmosphere — NPC mannerisms, weather, location
dressing. None of that is a place invention actually runs loose the way a motive or a thread turn
does; it adds content without constraining anything, which is a different problem from the one
this family exists to close.

**What a prompt table is not for.** It does not override an NPC's already-established objective,
a companion's stated Tension, or a thread's already-recorded state ([`04-session.md`](04-session.md),
[`05-campaign.md`](05-campaign.md)). It fills a gap that hasn't been decided yet; once rolled, the
result is established the same way an oracle answer is, and stays fixed if the same gap comes up
again.

## When the GM must roll one

**The GM is obliged to roll a prompt table whenever both hold:**

1. **One of the four scoped gaps is about to be filled** — an NPC's real motive, why a situation
   isn't as presented, a thread's next turn, or a scene's complication needs inventing right now.
2. **Nothing has already established it.** An NPC's `objective.wants` already written, a
   companion's active Tension, or a thread's recorded state all take precedence — the roll fills
   the gap, it never overwrites a decided fact.

As with answer oracles, this is an obligation, not a suggestion. A prompt table nobody is obliged
to consult changes nothing: it becomes a tool reached for only once an invented motive already
feels thin, which is exactly the case that needs it least.

**What stays an ordinary GM decision.** Naming a merchant, choosing the weather, deciding an
NPC's manner of speech — none of that is scoped by any of the four families, and none of it needs
rolling.

## The roll

Every prompt table shares one roll declaration, following [`03a-5-oracle-answers.md`](03a-5-oracle-answers.md)'s
choice of die for the same reason: the ruleset already commits to `d100` as its one resolution
mechanic ([`03-rules.md`](03-rules.md) §1), and ten rows per table fit comfortably in contiguous
`1d100` ranges without needing finer resolution than that.

| | |
|---|---|
| **die** | `1d100` |
| **modifier** | none |
| **lowest possible total** | `1` |
| **uniqueness** | repeatable |
| **extra row fields** | `checked` |

**Repeatable, not unique.** Generating "wants the old order restored" for two different NPCs in
two different scenes is ordinary — nothing tracks which rows a given character or thread already
holds, unlike a transformation.

## The tables

Four keys, one per family, each ten rows of equal width (`1-10`, `11-20`, … `91-100`) — nothing in
this family's own needs favours skewing the odds toward any one row, unlike a critical's
modifier-driven table depth.

`checked` records that a row was read once as if the setting were grim and once as if it were
comic, and passed both — [ADR 0004](adr/0004-tone-belongs-to-the-setting.md)'s "tone is a setting
property" applied to the one place a table is most likely to leak a register in unnoticed, because
each row reads as harmless flavour rather than as a claim. Every row below carries `checked: yes`;
a row that failed either reading does not appear here at all, so there is no failing row to show —
its absence from the table is the record. Two worked examples per table illustrate the check
rather than restating it forty times:

### `oracle-prompt-npc-objective`

| Range | Effect | Description |
|---|---|---|
| 1–10 | `protect_someone` | Wants someone or something specific protected, and will do whatever it takes. |
| 11–20 | `escape_a_debt` | Wants out from under a debt or obligation, without anyone noticing until it's done. |
| 21–30 | `prove_worth` | Wants to prove their worth to someone whose opinion matters more than they'll admit. |
| 31–40 | `recover_something_taken` | Wants something taken from them recovered, by whatever means are still open. |
| 41–50 | `preserve_the_status_quo` | Wants things to stay exactly as they are — believes they're the last one holding it together. |
| 51–60 | `gain_advantage_over_a_rival` | Wants an advantage over a named rival, and sees this as the opening. |
| 61–70 | `keep_a_secret_buried` | Wants a specific secret to stay buried, whatever the immediate cost. |
| 71–80 | `be_free_of_an_arrangement` | Wants free of an arrangement they no longer chose, but can't simply walk away from. |
| 81–90 | `settle_an_old_grievance` | Wants an old grievance settled that the record has forgotten but they haven't. |
| 91–100 | `survive_at_any_cost` | Wants, above everything else, to survive whatever's coming — at nearly any expense to others. |

*Genre-neutrality check, worked:* `protect_someone` reads grim as a parent shielding a child from
a raiding column, and comic as a merchant guarding a prize goat from the next village's cook —
both read as sincere, neither needs the register named to work. `survive_at_any_cost` reads grim
as a defector selling out comrades to a warlord, and comic as a guest at a doomed dinner party
elbowing past the host to reach the only door — both land as the same shape of self-interest at
different volumes.

### `oracle-prompt-situation-truth`

| Range | Effect | Description |
|---|---|---|
| 1–10 | `deliberate_front` | What's presented is a deliberate front; the truth is hidden nearby, not far. |
| 11–20 | `no_longer_true` | What's presented used to be true and no longer is — nobody has updated it. |
| 21–30 | `true_but_changing` | What's presented is true, but only for now — it's actively changing. |
| 31–40 | `true_for_most_not_all` | What's presented is true for most people here, but not for the one who matters. |
| 41–50 | `missing_one_fact` | What's presented is missing one crucial fact that changes its meaning entirely. |
| 51–60 | `true_and_that_is_the_danger` | What's presented is true, and the danger is precisely that it looks safe. |
| 61–70 | `staged_for_someone_else` | What's presented was staged for someone specific, not for whoever's here now. |
| 71–80 | `true_on_the_surface_only` | What's presented is true on the surface, false in the details underneath. |
| 81–90 | `an_honest_mistake` | What's presented is a mistake, not a lie — whoever set it up believed it. |
| 91–100 | `true_for_the_wrong_reason` | What's presented is true, but the reason it's true is not what anyone assumes. |

*Genre-neutrality check, worked:* `deliberate_front` reads grim as a checkpoint staffed by
impostors while the real guards lie dead behind the gatehouse, and comic as a "closed for repairs"
sign covering a smuggling operation running at full tilt — both give the GM a hidden truth to place
without dictating how dark it is. `an_honest_mistake` reads grim as a village shrine tending a
grave everyone believes holds a saint but actually holds a fraud who died believing his own
story, and comic as a tavern proudly serving "the founder's original recipe" that the founder
never actually made — both work because the mistake, not a villain, is doing the work.

### `oracle-prompt-thread-turn`

| Range | Effect | Description |
|---|---|---|
| 1–10 | `someone_switches_sides` | Someone involved switches sides, for reasons that make sense to them. |
| 11–20 | `new_information_reframes_it` | New information surfaces that changes what the thread is actually about. |
| 21–30 | `a_deadline_moves_closer` | A deadline moves closer, forced by someone else's unrelated action. |
| 31–40 | `an_ally_becomes_a_liability` | An ally becomes a liability, through no fault of their own. |
| 41–50 | `the_opposition_escalates` | The opposition escalates, using a method not seen from them before. |
| 51–60 | `an_assumed_resource_is_gone` | A resource everyone assumed was available turns out not to be. |
| 61–70 | `the_goal_was_a_means_to_another` | The thread's apparent goal turns out to be a means to a different one. |
| 71–80 | `an_outsider_intervenes` | Someone outside the thread notices it and moves to intervene. |
| 81–90 | `two_threads_collide` | Two threads intersect, and progress on one now costs progress on the other. |
| 91–100 | `the_thread_stalls` | The thread stalls, and staying still becomes its own kind of danger. |

*Genre-neutrality check, worked:* `someone_switches_sides` reads grim as a lieutenant defecting
mid-siege once the cause turns visibly hopeless, and comic as the guild's star apprentice quitting
mid-contest to join the rival stall that pays better — both are a thread's ally becoming its
complication, at whatever stakes the setting carries. `the_thread_stalls` reads grim as a hunt for
a missing sibling going cold for want of any lead, and comic as a running feud with a rival
merchant fizzling into stalemate neither side will end first — both turn inaction itself into the
next beat.

### `oracle-prompt-complication`

| Range | Effect | Description |
|---|---|---|
| 1–10 | `an_uninvited_party_arrives` | An unexpected party arrives, with their own agenda. |
| 11–20 | `a_resource_fails` | A resource runs out or fails at the worst possible moment. |
| 21–30 | `the_wrong_person_overhears` | Something said is overheard by someone who shouldn't have heard it. |
| 31–40 | `the_environment_turns` | The environment itself turns hostile or unstable. |
| 41–50 | `an_old_debt_comes_due` | An old promise or debt comes due, right now. |
| 51–60 | `a_misunderstanding_compounds` | A misunderstanding compounds, and correcting it costs time nobody has. |
| 61–70 | `help_arrives_at_a_cost` | Help arrives, but at a cost nobody agreed to. |
| 71–80 | `the_plan_works_and_backfires` | The plan works, but produces a consequence nobody anticipated. |
| 81–90 | `an_earlier_choice_catches_up` | A choice made earlier in the chronicle catches up here. |
| 91–100 | `someone_is_not_who_they_seem` | Someone present is not who they appear to be. |

*Genre-neutrality check, worked:* `a_resource_fails` reads grim as the last torch guttering out
three turns into a collapsing mine, and comic as the getaway cart losing a wheel outside the one
building in town with witnesses — both are "the plan just lost a leg," independent of how much
blood is on the floor. `someone_is_not_who_they_seem` reads grim as the trusted informant who has
been the enemy's agent since before the chronicle started, and comic as the "blind" beggar who
turns out to run the district's information trade — both are a reveal the GM can play at any
register.

Every table's ranges are contiguous, start at 1, and — with no modifier applied — cover the
`1d100` space exactly, so the last row is open at the top the same way every no-modifier oracle
table is: nothing can roll past 100 in the first place. This, and that every row above carries a
passing `checked`, is computed and asserted, not eyeballed, in
[`tools/check_oracle_prompts.py`](../tools/check_oracle_prompts.py).

## Interaction with existing content structures

A generated result never invents a new place to live. It fills a field or a state transition the
design already defines:

- **NPC objective** rows fill a companion's `objective.wants`
  ([`04-session.md`](04-session.md)), or the equivalent unstated motive the GM is about to give
  any other NPC. `objective.next_step` is not generated by this table — what a character does
  about their want is the GM's ordinary judgment, informed by the want, not itself rolled.
- **Situation truth** rows inform what the GM narrates about a scene; they don't write to any
  entity's state on their own, the same way an oracle answer doesn't until something is done
  with it.
- **Thread turn** rows describe a change to a thread's `summary`, `hooks`, or `heat`
  ([`05-campaign.md`](05-campaign.md)) — the GM applies the row's shape to the specific thread in
  play and updates its recorded state accordingly.
- **Complication** rows describe an event dropped into the current scene; like situation-truth
  rows, they don't write to state directly.

## Recording

A prompt roll is recorded to the beat log with the same provenance shape every table roll already
carries ([`03a-tables.md`](03a-tables.md), [`06-state.md`](06-state.md)), plus this family's own
fields:

```json
{"beat": 517, "verb": "roll", "engine": "0.3.1", "setting": "0.2.0",
 "table": "oracle-prompt-npc-objective", "subject": "the harbourmaster",
 "roll": 34, "effect": "prove_worth",
 "outcome": "wants to prove her worth to someone whose opinion matters more than she'll admit"}
```

- **`table`** — one of the four keys above.
- **`subject`** — what the roll is generating content *for*: an NPC's name, a thread's id, a
  scene's label. As with an oracle answer's `question` ([`03a-5-oracle-answers.md`](03a-5-oracle-answers.md)),
  recognising that a later roll concerns "the same subject" is the GM's judgment call, not
  automated matching.
- **`roll`** and **`effect`** — the natural total and the row it landed on.
- **`outcome`** — the row's description, as narrated.

The generated content then lands in the structure named above — a companion's `objective`, a
thread's fields — rather than in a second, parallel store; the beat-log entry is the roll's
provenance, not a duplicate of where the content now lives. Unlike an oracle answer, there is no
Wyrd-die reading here: a prompt roll generates content, it doesn't resolve a yes/no question, so
`03-rules.md` §1's Wyrd die has nothing to attach to.

## What a setting may extend or replace

Per [`03a-tables.md`](03a-tables.md), a setting may replace any of these tables' rows wholesale —
their ranges, effects and descriptions — under `overrides.tables: {oracle-prompt-npc-objective:
...}`, exactly as any other table family. But a setting wanting its own prompts wants this more
often than it wants its own criticals, and full replacement means re-authoring and maintaining the
whole ten-row baseline just to add one setting-specific motive.

`extend:` ([`13-authoring-a-setting.md`](13-authoring-a-setting.md)) closes that gap: alongside its
existing careers/talents/gear/creatures entries, `extend:` now also accepts a table key, whose
rows are appended above the engine's own highest range — contiguous with it, never overlapping —
leaving every engine row live:

```yaml
overrides:
  extend: {oracle-prompt-npc-objective: setting/rules/tables/oracle-prompt-npc-objective-extra.yaml}
```

A setting's extension file carries the same row schema as the engine's own rows (`range`,
`effect`, `description`, `checked`), and the combined table's now-last row stays open at the top,
per `03a-tables.md`'s convention. As with replacement, no extension row may carry a setting's
name, a system's name, or a tonal register baked into its effect — only its description may carry
the setting's voice.

No table row, example, or label above names a specific setting, a source system, or a tonal
register — verified by grep, per `CLAUDE.md`.
