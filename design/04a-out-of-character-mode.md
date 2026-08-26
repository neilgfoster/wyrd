# Wyrd — out-of-character mode

At play time, everything the player types is handled as in-character speech and action by
default. This document specifies the one deliberate exception: a way for the player to step
outside the fiction, ask the GM something directly, and return to play with the fiction
untouched.

See [ADR 0037](adr/0037-out-of-character-mode-is-a-prefix-trigger.md) for why the trigger takes
this shape rather than a slash command or a session-wide toggle.

---

## The trigger

A message that begins with `?` is handled out-of-character (OOC) instead of in-character:

```
?what's my stamina
```

The `?` is stripped from what follows; the rest of the message is the player's question or
request, addressed to the GM as the player, not as the character.

**Scope is per-message, not a mode the player switches into and out of.** The trigger applies
to the message that carries it and to the GM's one response — nothing more. The player's very
next message, if it doesn't itself begin with `?`, is handled in-character exactly as if the
OOC exchange had not happened. There is no toggle to remember to switch back.

A bare `?`, or `?` followed only by whitespace, is not treated as a question with an inferred
subject. The GM asks what the player wants to know, still OOC-marked, rather than guessing —
falling silently through to in-character play would be the exact failure mode this feature
exists to prevent.

## What suspends

For the single response to an OOC-triggered message:

- **The diegetic contract is suspended.** [`10-diegesis.md`](10-diegesis.md) withholds raw
  numbers by default and renders state from the character's own perspective — right during
  play, wrong when the player is deliberately asking for the number. In OOC mode, exact
  mechanical state (Stamina, skill percentages, Taint, any other numeric state the player asks
  for) is given as a number directly. This is the same "on request" query
  `10-diegesis.md` already names; the `?` trigger is that request mechanism, made explicit.
- **Nothing said becomes established fiction.** The player's OOC message and the GM's response
  to it are never treated as something the character said, thought, or did, and are never
  incorporated into the chronicle. This is the load-bearing rule: an OOC exchange that leaked
  into the fiction would recreate exactly the corruption this feature exists to prevent, just
  with an extra step.
- **Nothing about the exchange appears in the session's in-character narrative.** The scene the
  player was in continues from where it left off on their next in-character message, with no
  reference — explicit or implied — to the OOC exchange having occurred in-world.

## What's logged

An OOC exchange is not discarded; it is logged somewhere separate from the chronicle's
fictional record, so the player and GM can refer back to a prior OOC exchange ("what did you
tell me about X earlier?") without mistaking it for something that happened in the fiction. The
exact storage location is an implementation decision for whatever system later realises session
logging — this document's requirement is the separation from the chronicle's fiction, not a
particular file or format.

## Answering "would my character know this?"

This is the question the issue calls out as needing a specific shape, because it is
simultaneously a question about the world and a question about the character's competence —
and conflating the two (letting the player's own knowledge of the narration leak into what the
character is treated as knowing) is exactly the failure diegetic play exists to prevent.

- **Where the character would not know it**, the answer says so plainly, and — where
  answerable from established fiction — states what the character would believe or assume
  instead. The player's own knowledge, gained from reading the narration, is never granted to
  the character on the strength of an OOC question.
- **Where the character would know it**, the answer confirms that and gives the information at
  the character's scaled competence, per [`10-diegesis.md`](10-diegesis.md)'s "the character as
  a knowledge source" section — the same competence-scaling that already governs an in-character
  "what do I know about this place?" question.
- **Where the honest answer would reveal engine-hidden state**, or another character's
  information the player's own character has no path to (the hidden threshold, another
  character's private motive — the "never shown" visibility class in
  [`10-diegesis.md`](10-diegesis.md)) — the response says plainly that the answer isn't
  available. It does not fabricate an in-fiction justification for withholding it; it simply
  says so.

## The mode is always visible

Every response to an OOC-triggered message opens with an unmistakable textual marker (for
example, a leading `[OOC]` line) distinguishing it from an ordinary in-character response. No
in-character response carries this marker under any circumstances.

**No client-side signal is assumed.** The issue asks whether Claude Code exposes a hook that
could change UI chrome — an input box's colour, say — to reflect the active mode. It does not:
a GM response is plain text delivered into the conversation, with no channel back into the
client's own styling. The textual marker above is the fallback the issue itself calls for when
no such hook exists, not a placeholder pending one.

Mechanism, not voice: the marker's exact wording is a rename candidate like any other engine
label, available to a setting's `rename:` block per `CLAUDE.md`'s engine-labels rule, but every
setting must render *some* unmistakable marker — this document specifies that it exists, not
its exact text.

## What this is not

- **Not a rewind or undo mechanism.** OOC mode lets the player discuss the fiction as
  themselves; it does not add a way to alter what has already been established. Rewind/undo is
  explicitly out of scope for this feature (#32) and remains its own, separate decision.
- **Not required for in-character knowledge questions.** "What do I know about this place?",
  asked without the `?` trigger, is already a legitimate in-character move per
  [`10-diegesis.md`](10-diegesis.md) and is answered in character, at the character's
  competence. OOC mode does not change that existing behaviour, and using it is not necessary
  to ask that kind of question.

## Worked example

```
> The lock gives under the pick, and the door swings in on a room
> that hasn't been aired in years.

?what's my stamina

[OOC] 14/20.

> You step through. Dust, and the smell of something long dead.
```

The player's Stamina question and its numeric answer never entered the scene; play resumes
exactly where it left off, with no in-fiction trace of the exchange.
