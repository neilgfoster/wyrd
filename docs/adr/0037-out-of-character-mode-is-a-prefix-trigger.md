# ADR 0037 — Out-of-character mode is a one-character prefix, not a slash command

**Date:** 2026-08-26
**Status:** Accepted

## Context

At play time, everything the player types is handled as in-character speech and action —
there is no way to step outside the fiction and ask a question *as the player*. #32 asks for
an explicit mode, because the alternative (phrasing an out-of-character question inside the
fiction) corrupts the fiction the moment it's answered: an in-character answer to an
out-of-character question becomes established fact. `23-diegesis.md`'s diegetic contract —
state is described from the character's perspective, numbers withheld by default — makes this
sharper, not softer: it is exactly right during play and exactly wrong when the player is
deliberately asking for the number.

Two shapes of trigger were available:

1. **A single-character prefix on the input** (e.g. `?what's my stamina`), consuming one extra
   character per OOC message.
2. **A slash command** (e.g. `/ooc what's my stamina`), more explicit and visually distinct,
   but several characters heavier to type.

This is the load-bearing fork: the two choices trade the same thing — how unmistakably the
mode switch reads — against how much friction it adds to a message the player wants to send
quickly, and either could plausibly be re-proposed by someone who has forgotten why the other
lost. `01-principles.md`'s brief is explicit that sessions are "short... often on a phone, at
unpredictable intervals" — friction that is negligible at a keyboard is not negligible on a
phone screen typed one-handed on a train.

## Decision

**The OOC trigger is a single prefix character, `?`, prepended to the player's message.**

`?what's my stamina` switches the handling of that one message to out-of-character: the
diegetic contract is suspended for the response (raw numbers on request), the exchange is
excluded from the chronicle's fictional record, and the response carries an unmistakable
textual marker. The mode applies to that message and the GM's one response to it — the very
next message that does not itself carry the trigger returns to in-character handling
automatically, with no toggle for the player to remember to switch back.

`?` was chosen over the other single-character candidate the issue named, `$`, because it reads
naturally as "I'm asking a question" — a player typing `?` is doing something they would
recognise as normal punctuation usage, where `$` has no such natural reading and sits awkwardly
on a phone's default keyboard layer. It is also unlikely to collide with plausible in-character
dialogue: a player is far more likely to start a genuine in-character line with `$` (an amount
of money, in a setting where that's a live concern) than to start one with a bare `?`, which
reads as a query in almost every natural-language register.

See [`17-out-of-character-mode.md`](../design/17-out-of-character-mode.md) for the full mechanism
this decision grounds.

## Alternatives rejected

**A slash command (`/ooc ...`).** More explicit and visually distinct — a command word leaves
no doubt about intent — but heavier to type on every OOC message, in the dominant play context
this engine targets. The issue itself names the prefix as the leading candidate for exactly
this reason. A slash command also implies a wider space of subcommands the engine does not need
here; `?` is legible on its own, with no vocabulary to learn.

**A session-wide mode toggle** (switch into OOC mode, stay there until switched back).
Rejected: this trades one failure mode for its mirror image. Instead of an OOC question risking
misreading as in-character, a player who forgets they toggled OOC mode on risks having a
genuine in-character action misread as a query — silently losing play rather than corrupting
it, which is no better. Scoping the trigger to a single message removes the need to track
mode state across turns at all.

**No dedicated trigger — infer OOC intent from phrasing.** Rejected outright: this is exactly
the current failure mode #32 exists to fix. Inference has no reliable signal to key off, and a
misread produces the same fiction-corruption risk the feature is meant to eliminate. An explicit
trigger is deterministic; a phrasing heuristic is not.
