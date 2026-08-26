# Feature Specification: Out-of-character mode at play time

**Feature Branch**: `031-ooc-mode`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Out-of-character mode at play time" (issue #32)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask an out-of-character question mid-scene (Priority: P1)

The player is mid-scene and wants to ask the GM a question as themselves — not as their
character — without that exchange becoming part of the fiction: "what's my actual Stamina?",
"remind me what we decided about the innkeeper", "did I actually see the second door, or is
that a guess?".

**Why this priority**: This is the load-bearing case from the issue. Without it, any
out-of-character question has to be smuggled into in-character speech, where it risks being
answered as if the character said it aloud — corrupting the fiction with a question that was
never asked in the world.

**Independent Test**: Trigger OOC mode, ask for exact Stamina, get a number back, resume play,
and confirm nothing about the question or its answer appears in the session's in-character
narrative or in the chronicle's recorded fiction.

**Acceptance Scenarios**:

1. **Given** an in-character scene in progress, **When** the player sends an OOC-triggered
   message asking for their exact Stamina, **Then** the response states the raw number and
   nothing about the exchange is treated as something the character said or did.
2. **Given** an OOC exchange has just happened, **When** the player's next message resumes
   play with no OOC trigger, **Then** the GM continues the scene exactly where it left off, with
   no reference to the OOC exchange having occurred in-world.

---

### User Story 2 - Ask whether the character would know something (Priority: P2)

The player wants to check, as themselves, whether their character would actually know a piece
of information before deciding whether to have the character act on it — "would I know that
this crest belongs to the Duke's house?" — and get an honest answer about the character's
knowledge, distinct from what the player (having read the scene) now knows.

**Why this priority**: This is the case the issue calls out as needing a specific answer
shape: the question is simultaneously about the world and about the character's competence,
and conflating the two is exactly the failure mode diegetic play is supposed to prevent.

**Independent Test**: In OOC mode, ask "would my character know X" for something the
character plausibly would not know; confirm the answer says so plainly and states what the
character would believe or assume instead, without granting the player's own knowledge to
the character.

**Acceptance Scenarios**:

1. **Given** a fact the player knows from the narration but the character has no in-fiction
   basis to know, **When** the player asks in OOC mode whether their character would know it,
   **Then** the answer says the character would not know it, and states what the character
   would believe instead where that is answerable.
2. **Given** a fact the character has plausible in-fiction grounds to know (established
   background, something witnessed, common knowledge for their competence), **When** the
   player asks the same kind of question, **Then** the answer confirms the character would
   know it and gives the answer at the character's scaled competence, consistent with
   [`docs/design/23-diegesis.md`](../../docs/design/23-diegesis.md).

---

### User Story 3 - See which mode is active at a glance (Priority: P3)

The player needs to be able to tell, without asking, whether their next message will be
read as in-character or out-of-character — particularly because a misjudged mode makes the
opposite mistake to User Story 1: an in-character message misread as OOC loses its place in
the fiction, and vice versa.

**Why this priority**: Necessary for the mode split to be usable at all without constant
uncertainty, but it is a usability safeguard on top of Stories 1-2 rather than the core
capability.

**Independent Test**: Trigger OOC mode, confirm the response is unmistakably marked as
out-of-character; resume in-character play, confirm the following response carries no such
marker.

**Acceptance Scenarios**:

1. **Given** the player sends a message with the OOC trigger, **When** the GM responds,
   **Then** the response is visibly and unambiguously marked as out-of-character.
2. **Given** the player is in an ordinary in-character exchange, **When** the GM responds,
   **Then** nothing in the response could be mistaken for an OOC marker.

### Edge Cases

- What happens when the player sends a message with the OOC trigger but no actual question —
  just the trigger character alone, or the trigger followed by whitespace? The GM should
  prompt for what they want to know, still marked OOC, rather than guessing or silently
  falling through to in-character play.
- What happens when a player asks an in-character-sounding question ("what do I know about
  this place?") without the trigger? Per [`docs/design/23-diegesis.md`](../../docs/design/23-diegesis.md),
  that is a legitimate in-character move already and is answered in character, at the
  character's competence — OOC mode is not required for it and this feature must not change
  that existing behaviour.
- What happens if the player tries to use OOC mode to retroactively change established
  fiction ("actually, my character didn't say that")? Rewind/undo of established fiction is
  explicitly out of scope for this feature (see issue #32); OOC mode can be used to *discuss*
  the fiction but this feature does not add a mechanism to alter what has already been
  established.
- What happens when the player asks an OOC question the GM cannot answer honestly without
  revealing information the character has no way to access (e.g. another character's hidden
  motive, a future plot point)? The answer must not fabricate an in-fiction justification;
  it should say plainly that the answer isn't available yet, consistent with the "never
  shown" visibility class in [`docs/design/23-diegesis.md`](../../docs/design/23-diegesis.md).
- What happens across a very long play session where many OOC exchanges accumulate — does
  the accumulation affect model context or session length in a way that degrades either
  mode? Out of scope to solve mechanically here; flagged as a known limit of the approach in
  Assumptions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a single-character prefix trigger on the player's input
  that switches the GM's handling of that message to out-of-character (OOC) mode. The `?`
  character is the chosen trigger (see Assumptions for the rejected alternative and why).
- **FR-002**: While handling an OOC-triggered message, the GM MUST suspend the diegetic
  contract of [`docs/design/23-diegesis.md`](../../docs/design/23-diegesis.md) for that response: raw
  mechanical state (exact Stamina, exact skill percentages, Taint score, and any other
  numeric state the player asks for) MUST be given as numbers on request, not translated into
  diegetic prose.
- **FR-003**: An OOC exchange (the player's triggered message and the GM's response to it)
  MUST NOT be treated as anything the character said, thought, or did, and MUST NOT be
  incorporated into the chronicle as established fiction.
- **FR-004**: The GM MUST be able to answer, in OOC mode, whether the player's character
  would know a specific piece of information, distinguishing the character's in-fiction
  knowledge from the player's own knowledge of the narration so far. Where the answer is "no,
  the character would not know this," the response SHOULD state what the character would
  believe or assume instead, where that is answerable from established fiction.
- **FR-005**: Every GM response to an OOC-triggered message MUST carry an unmistakable
  textual marker identifying it as out-of-character, distinguishing it from the GM's ordinary
  in-character responses.
- **FR-006**: The engine MUST return to in-character handling by default on the player's next
  message once that message does not itself carry the OOC trigger — OOC mode applies to the
  triggered message and the single response to it, not to the rest of the session, unless the
  player triggers it again.
- **FR-007**: OOC exchanges MUST NOT appear in the session's in-character narrative output.
- **FR-008**: OOC exchanges MUST be logged separately from the chronicle's in-fiction record
  (not silently discarded), so the player and GM can refer back to a prior OOC exchange (e.g.
  "what did you tell me about X earlier?") without it being mistaken for fiction. Where they
  are stored is an implementation choice out of this spec's scope, provided the separation
  from the chronicle's fictional record holds.
- **FR-009**: The trigger MUST be a single character prepended to the player's message, adding
  no more than one character of typing overhead to a terse play style.

### Key Entities

- **OOC exchange**: One triggered player message and the GM's response to it. Has content,
  is timestamped/ordered relative to the session, and is explicitly excluded from the
  chronicle's in-fiction record.
- **Mode**: The handling state (in-character / out-of-character) applied to a single message
  exchange. Not persistent session state beyond that one exchange (per FR-006).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A player can retrieve their character's exact Stamina value mid-scene and
  resume play with the in-character narrative completely unaffected by the exchange.
- **SC-002**: 100% of OOC-triggered responses carry the textual OOC marker, and 0% of
  ordinary in-character responses do.
- **SC-003**: The OOC trigger adds exactly one character to the player's message, so terse
  play (short in-character commands) remains just as fast to type as before this feature.
- **SC-004**: No OOC exchange, across a full played session, is found to have altered the
  chronicle's recorded fiction when the chronicle is reviewed after the session.

## Assumptions

- **Trigger choice**: `?` is used as the OOC trigger, prepended to the player's message
  (e.g. `?what's my stamina`). Rejected alternative: a slash command (e.g. `/ooc what's my
  stamina`) — more explicit and visually distinct, but heavier to type on a phone every time,
  which the issue identifies as the dominant play context; a single prefix character keeps
  terse play viable per the issue's own constraint. `?` was chosen over `$` because it reads
  naturally as "I'm asking a question" and is unlikely to collide with in-character dialogue
  that a player would plausibly type (unlike `$`, which has no such natural reading and is
  awkward to reach on a phone keyboard).
- **Mode scope**: OOC mode applies per-message, not as a session-wide toggle the player must
  remember to switch back out of. This avoids the failure mode of a player forgetting they
  left OOC mode on and having an intended in-character action misread as a query.
- **Visible mode indication**: This spec assumes Claude Code does not expose a hook to change
  UI chrome (e.g. input box colour) from within a conversation — GM responses are plain text
  and the engine has no channel to signal client-side styling. The fallback is the textual
  marker required by FR-005. (Confirming this Claude Code has-no-such-hook conclusion, and
  recording it, is part of the planning phase that follows this spec — see the issue's
  acceptance criterion on visible mode.)
- **Logging destination**: OOC exchanges are assumed to be recordable somewhere reachable by
  the session (e.g. alongside session notes) without engine support for a *new* storage
  mechanism being mandatory in this feature; the planning phase decides the concrete
  location using [`docs/design/16-session.md`](../../docs/design/16-session.md)'s existing session-state
  conventions.
- **Not a rewind mechanism**: Per the issue, rewinding or undoing established fiction is
  explicitly out of scope; OOC mode is a read/ask channel, not a fiction-editing one.
