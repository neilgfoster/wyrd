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

This index is **checked**, not maintained by hand alone: `python3 tools/check_docs.py` fails
when a record exists on disk that this table does not list. It had already drifted three
records behind before the check existed.
