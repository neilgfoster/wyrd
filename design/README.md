# Design documents and decision records

Two kinds of document, with different lifecycles.

| | `design/*.md` | `design/adr/*.md` |
|---|---|---|
| Answers | **what Wyrd is** | **why, and what was rejected** |
| Tense | present | dated |
| When it changes | rewritten in place; always current | its reasoning is never edited; a later record supersedes it |
| Read for | building or playing | re-litigating a decision |

A design document is **replaceable**. When something changes, the old text goes and the
document describes the new state — git holds the history, but the document itself is only
ever the present.

A decision record is **historical**. It is written once, dated, and its reasoning is left
alone. If the decision is reversed, a new record supersedes it and both remain, because the
reasoning that was rejected is as useful as the reasoning that won.

**One line of a record does change: its `Status:`.** A superseded record's status names the
record that replaced it, and moves to [`adr/superseded/`](adr/superseded/README.md), where it keeps the
number it was written under — permanently, so a historical reference still resolves to the
reasoning it meant. Nothing else in an accepted record is ever edited, and no record is ever
deleted. The full rule, and the reset that made it necessary, are in
[ADR 0012](adr/0012-the-design-reset-and-how-records-are-consolidated.md).

## What earns a decision record

Not every choice. An ADR for each is noise, and noise is how a record stops being read.

A decision earns one when **both** hold:

1. **A real alternative was rejected** — not merely "we picked a name", but a workable option
   that would have produced a different engine.
2. **Someone would plausibly propose it again** — including the author, in a year, having
   forgotten why not.

By that test most of `design/` needs no record: it describes rather than chooses. The
records that exist mark the places where the obvious answer was wrong.

## Index

| | |
|---|---|
| [0001](adr/0001-resolution.md) | Percentile resolution, with the units digit as the Wyrd die |
| [0002](adr/0002-source-material.md) | Read source material natively; do not adopt the system it came from |
| [0003](adr/0003-recursive-containment.md) | Containment is recursive; the beat is the only leaf |
| [0004](adr/0004-tone-belongs-to-the-setting.md) | Tone is declared by the setting, not built into the engine |
| [0005](adr/0005-deterministic-over-inference.md) | Anything with a correct answer is computed, not inferred |
| [0006](adr/0006-state-is-entities.md) | State is entities; there is no second storage model |
| [0007](adr/0007-game-time.md) | Game time is independent of real time |
| [0008](adr/0008-tables-declare-their-own-roll.md) | The engine fixes the row schema; each table family declares its own roll |
| [0009](adr/0009-fate-closes-the-death-rows.md) | Fate closes the death rows rather than suppressing the roll |
| [0010](adr/0010-backlog-order-lives-on-the-board.md) | The backlog order lives on the board, not in a file |
| [0011](adr/0011-markdown-links-in-prose-wikilinks-in-data.md) | Markdown links in prose, wikilinks in data |
| [0012](adr/0012-the-design-reset-and-how-records-are-consolidated.md) | The design reset, and how decision records are consolidated |
| [0013](adr/0013-the-engine-names-no-skill.md) | The engine names no skill, and has no characteristics |
| [0014](adr/0014-character-creation-is-chosen-not-rolled.md) | A character is chosen, not rolled |
| [0015](adr/0015-loyalty-has-three-relations-not-two.md) | Loyalty has three relations, not two |
| [0016](adr/0016-opposed-tests-need-a-successful-actor.md) | An opposed test needs a successful actor, and a failure has no degrees |
| [0017](adr/0017-assistance-group-tests-and-extended-tasks.md) | Assistance scales with the helper's skill; a group rolls once; long work accumulates |
| [0018](adr/0018-combat-sequencing.md) | Turn order is read off the fiction; space is one bit; surprise costs a whole round |
| [0019](adr/0019-a-crowd-is-defined-by-one-blow-and-a-skill-gap.md) | A crowd is defined by one blow and a skill gap, and it answers once |
| [0020](adr/0020-stamina-recovers-on-the-clocks-the-engine-has.md) | Stamina recovers on the clocks the engine already has — the Rally and downtime |
| [0021](adr/0021-mending-steps-and-the-recurring-wound-does-not.md) | Mending steps one grade a season, and the recurring wound never closes |
| [0022](adr/0022-four-damage-types-named-for-the-wound.md) | Four damage types, named for the shape of the wound |
| [0023](adr/0023-a-critical-never-kills-during-the-fight.md) | A critical never kills during the fight |
| [0024](adr/0024-a-party-is-worth-less-than-its-head-count.md) | A party is worth less than its head count, on both sides of the ratio |
| [0025](adr/0025-an-adversary-is-a-thin-block.md) | An adversary is a thin block, and a named antagonist wears one |
| [0026](adr/0026-danger-scales-a-skill-in-points-not-in-multiples.md) | Danger scales a skill in points, not in multiples |
| [0027](adr/0027-combat-rolls-belong-to-the-player.md) | Combat rolls belong to the player; the opponent's dice are gone |
| [0028](adr/0028-the-telling-blow-threshold-and-the-damage-finding.md) | The telling blow moves to 6 degrees; the issue's damage-multiplier figure is corrected |
| [0029](adr/0029-transformation-thresholds-at-every-three-taint.md) | Taint thresholds sit at every 3 points, and Dread equals severity |
| [0030](adr/0030-afflictions-are-repeatable-and-test-no-named-skill.md) | Afflictions are repeatable, and the Trauma test names no skill |
| [0031](adr/0031-fault-line-biases-exposure-not-the-transformation-table.md) | The Fault Line biases Exposure's Taint gain, not the transformation table |
| [0032](adr/0032-career-cap-and-the-stamina-ceiling.md) | Career caps sit at 70%, and maximum Stamina stops climbing at 10 |
| [0033](adr/0033-standing-and-the-material-economy.md) | Standing is kept and defined; wealth reconciles with it, not beside it |
| [0034](adr/0034-bond-is-the-positive-party-track.md) | Bond is the positive party track; no standalone Cohesion track is added |
| [0035](adr/0035-opposed-tests-generalise-to-the-player-facing-roll.md) | Opposed tests generalise to the player-facing roll; ADR 0016 is retired |

This index is **checked**, not maintained by hand alone: `python3 tools/check_docs.py` fails
when a record exists on disk that this table does not list. It had already drifted three
records behind before the check existed.
