# Contract: the `/wyrd-play` Claude Code skill

This feature's only "interface" is a Claude Code skill invoked by name -- there is no new CLI
verb, HTTP endpoint, or library API. This contract states what the skill guarantees to a caller
(the player, at the terminal) and what it relies on from the engine CLI it calls, so the
relationship stays checkable even though neither side is a typed API.

## Invocation

- **Name**: `/wyrd-play`
- **Location**: `wyrd-chronicle-template/.claude/skills/wyrd-play/SKILL.md`
- **Precondition**: invoked from within a chronicle repository whose `chronicle.yaml` already
  exists (bootstrap already completed). If it does not exist, the skill reports that plainly and
  performs no engine calls (FR-002).
- **Postcondition (success)**: the chronicle passes `validate` with no errors, and either (a) no
  `pending` marker is set (beat closed cleanly at a Rally), or (b) a `pending` marker names the
  exact unresolved action if the player had to stop mid-beat (FR-011, FR-012).

## Verbs this skill calls (existing engine CLI; none of them are new)

Every verb below is called exactly as `docs/design/02-architecture.md` and
`engine/wyrd/catalog.py` already define it (see `research.md` for the full mapping). This skill
adds no new verb, no new flag, and no new return field to any of them.

| Verb | Purpose in this skill | This skill MUST NOT |
|---|---|---|
| `session-context` | Load the Always-loaded tier at the start of every invocation | Construct this tier's contents any other way (reading entity files directly, guessing presence) |
| `propose` | Stage a skill test's or combat action's roll and any implied mutation | Treat a proposal's mutation as applied before `commit` succeeds |
| `commit` | Apply a proposal's staged mutations | Call this before the player's declared action and its `propose` result are both known |
| `discard` | Invalidate a proposal without writing | Discard a proposal whose outcome was already narrated as having happened |
| `opposed-test` | Resolve a single acting-side roll against an NPC | Consult the opponent's own dice -- this verb already never does |
| `declaration-bonus` | Look up a fixed point value for a declaration category | Derive a bonus from the length or style of the player's text |
| `track` | Apply a delta to a trackable mechanism outside a `propose` cascade | Compute the new value itself before calling this |
| `advance-time` | Advance the calendar and resolve threat activation across elapsed time within the beat | Compute calendar arithmetic or threat activation odds itself |
| `threat-check` | An on-demand single-threat activation roll | Decide activation without this roll when the fiction calls for checking it |
| `rally` | Fixed Strain/Stamina recovery, discard of a leftover open proposal, optional advance award, at a clean beat close | Commit anything itself -- persistence is this skill's own `save` step |
| `save` | Persist chronicle state (a clean close, or a `pending` marker) before narrating the outcome | Narrate the outcome before this call succeeds |
| `validate` | Confirm the chronicle is left in a valid state at the end of the invocation | Report success without having actually run this |

## Guarantees to the player (from the spec's Functional Requirements)

- No option menu is ever presented (FR-006).
- No engine-internal identifier or raw number appears in in-character narration (FR-005).
- Every mechanical outcome narrated traces verbatim to one of the verb calls above (FR-007).
- The skill's own prose contains no setting- or system-specific name (FR-013).
- Character creation, downtime, and end-of-session compaction are never performed by this
  skill -- it may mention that `/wyrd-bootstrap`, `/wyrd-downtime`, or `/wyrd-end-session` is
  available, but does not reimplement any of their steps (FR-014).

## Known limitation carried forward, not fixed here

Issue #411 (career.py's `effective_cap`/`career_complete` skills-shape mismatch) may land
concurrently in a sibling batch member. `/wyrd-play` does not call `create-character` or any
advancement path that exercises it, so this contract is unaffected; if it is somehow hit during
verification, it is reported as already-tracked (#411), not re-diagnosed here.
