# Feature Specification: Character, downtime and session-close skills

**Feature Branch**: `154-session-close-skills`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "Build the /wyrd-character, /wyrd-downtime and /wyrd-end-session skills (neilgfoster/wyrd#404)"

## Clarifications

### Session 2026-09-15

- Q: Where do the three skills live — the engine repo (`wyrd`) or the chronicle repo
  (`wyrd-chronicle-template`)? → A: `wyrd-chronicle-template`, per that repo's own README
  ("self-contained after bootstrap") and the issue's own scope note. This spec's artefacts
  still live in `wyrd` (per this feature's process requirement), but the skill files themselves
  are a separate deliverable raised in `wyrd-chronicle-template`, closing this issue from there.
- Q: `engine/wyrd/downtime.py` and `rally.py` have no CLI verb wrapping them today
  (`spend-advance`, `save`, `recap`, `adjust-standing` etc. exist; a `downtime`/`rally` verb does
  not — `adjust-standing`'s own catalog description explicitly excludes Upkeep). Does this
  feature add that verb wiring, or does the downtime skill find another way to reach the
  arithmetic? → A: this feature adds the minimal verb wiring in the engine repo (`wyrd`) as a
  companion PR — the alternative (the skill reimplementing Upkeep's trade or Mend's ladder in its
  own prose) violates the issue's own constraint that no skill reimplements engine arithmetic.
  This makes the feature span two PRs in two repos, both against the same tracking issue.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect or advance the player character (Priority: P1)

Between or during beats, the player wants to see their character sheet or spend an unspent
advance earned at a prior Rally.

**Why this priority**: This is the smallest of the three skills and has no dependency on the
other two — a real MVP slice.

**Independent Test**: From within a bootstrapped chronicle, invoking the character skill shows
the current sheet; choosing to spend an advance on a specific skill or career change applies
exactly the change the existing `spend-advance` engine verb reports, and refuses cleanly when
there is no unspent advance.

**Acceptance Scenarios**:

1. **Given** a chronicle with a saved player character, **When** the player asks to see their
   sheet, **Then** the skill reads and presents the character's current state without changing it.
2. **Given** a player character with at least one unspent advance, **When** the player chooses to
   spend it on a specific skill or a career change, **Then** the skill calls the engine's
   spend-advance verb with that choice and reports the resulting sheet.
3. **Given** a player character with no unspent advance, **When** the player asks to spend one,
   **Then** the skill reports the refusal the engine verb returns, unchanged, rather than
   inventing its own message.

---

### User Story 2 - Run a downtime phase (Priority: P2)

At the end of a scenario or arc, or when the player asks, the player wants to spend downtime:
pay Upkeep away from home, choose exactly one Undertaking, and let Stamina return to maximum.

**Why this priority**: Depends on the same character-state surface as User Story 1 but adds a
genuinely new player choice (the Undertaking) and a real gap — no CLI verb currently wraps
`engine/wyrd/downtime.py`'s pure functions, so this story is where that gap must be resolved
before the skill can call anything.

**Independent Test**: From within a chronicle, invoking the downtime skill walks Destination,
Upkeep, Advances, Undertaking and Rest in order, presenting the Upkeep trade and the Undertaking
choice as player decisions, and produces exactly the numeric outcome the underlying arithmetic
computes for whichever choices were made.

**Acceptance Scenarios**:

1. **Given** a character away from home entering downtime, **When** the player chooses to trade
   Standing rather than coin for Upkeep, **Then** the skill applies a Standing loss of exactly 1
   and leaves coin unchanged, matching `apply_upkeep`'s own result for that trade.
2. **Given** the same situation, **When** the player instead chooses to spend coin, **Then** the
   skill deducts coin equal to the character's current Standing and leaves Standing unchanged, or
   reports the refusal if coin is insufficient.
3. **Given** a downtime phase in progress, **When** the player is asked to choose an Undertaking,
   **Then** exactly one of the six declared Undertakings (Recover, Mend, Pursue, Cultivate,
   Learn, Ask) is offered and chosen, and the skill will not let a second Undertaking be chosen in
   the same period.
4. **Given** any downtime phase reaching Rest, **When** that step is reached, **Then** Stamina is
   restored to maximum unconditionally, regardless of which Undertaking was chosen.
5. **Given** an Undertaking of Mend chosen against a named lasting wound, **When** the skill
   resolves it, **Then** the wound's effect moves exactly one step down `MEND_LADDER`, or is
   refused unchanged if the wound is `recurring`.

---

### User Story 3 - Close a session (Priority: P3)

At the end of a session, the player wants the chronicle compacted, its recap regenerated, and the
result committed, so that resuming later starts from an accurate `recap.md`.

**Why this priority**: Depends on state already being consistent (the other two skills, or a
played beat, having left it so); it is the natural last step and lowest priority to build first
of the three, though all three are needed for a complete session lifecycle.

**Independent Test**: From within a chronicle with at least one played beat, invoking the
end-session skill produces a `recap.md` whose content matches the engine's own `recap` verb
output for the current chronicle state, and a commit exists afterward recording that state.

**Acceptance Scenarios**:

1. **Given** a chronicle session ready to close, **When** the player ends the session,
   **Then** the skill calls the engine's `save` verb before `recap`, so the regenerated recap
   reflects the fully persisted state, not a stale in-memory one.
2. **Given** a successful `recap` call, **When** the skill finishes, **Then** `recap.md` on disk
   matches the text the verb returned, and a git commit exists covering the changed chronicle
   files.
3. **Given** a session that stops mid-beat, **When** the player ends the session anyway,
   **Then** the skill persists a `pending:` marker naming the unresolved action (per
   docs/design/16-session.md) rather than silently discarding it, and still commits.

### Edge Cases

- What happens when the player asks to spend an advance but names a skill or career the engine
  verb rejects (e.g. already at cap, or not reachable from the current career)? The skill
  reports the verb's own refusal reason verbatim.
- How does the downtime skill handle a player who is at home (no Upkeep cost) — does it skip
  presenting a trade choice? Yes: `apply_upkeep` itself passes `destination == "home"` through
  with no trade required, so the skill must not force a choice that has no effect.
- What happens if `/wyrd-end-session` is invoked with nothing changed since the last commit? The
  skill still regenerates and writes `recap.md` (idempotent), and commits only if the working
  tree actually differs afterward — it does not force an empty commit.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The character skill MUST present the player character's current sheet by calling
  the engine's existing character-load/session-context verbs, without recomputing any value
  itself.
- **FR-002**: The character skill MUST let the player spend an unspent advance by calling the
  engine's `spend-advance` verb with the player's chosen spend (skill or career change), and MUST
  report that verb's result — success or refusal — unchanged.
- **FR-003**: The downtime skill MUST present Upkeep's trade choice (Standing vs coin) to the
  player as a decision, away from home only, and apply it by calling
  `engine/wyrd/downtime.py`'s `apply_upkeep` (via a thin CLI verb added for this purpose, since
  no such verb exists yet — see Assumptions).
- **FR-004**: The downtime skill MUST present the Undertaking choice as exactly one of the six
  values `downtime.UNDERTAKINGS` declares, and MUST NOT allow a second Undertaking to be chosen
  within the same downtime period, reusing `advance_downtime`'s own enforcement of that gate.
- **FR-005**: The downtime skill MUST apply Rest (Stamina to maximum) unconditionally, regardless
  of which Undertaking was chosen, matching docs/design/16-session.md's "Stamina is not on that
  list" rule.
- **FR-006**: The downtime skill's Mend undertaking MUST name exactly one lasting wound by its
  `id`, move its effect one step per `MEND_LADDER`, and refuse a `recurring` wound outright,
  reusing `downtime.py`'s existing Mend function without reimplementing the ladder.
- **FR-007**: The end-session skill MUST call the engine's `save` verb before calling `recap`, so
  the regenerated `recap.md` reflects fully persisted state.
- **FR-008**: The end-session skill MUST write the returned recap text to `recap.md` and commit
  the chronicle's changed files, matching docs/design/16-session.md's `CLOSE` step (compaction,
  recap regeneration, commit).
- **FR-009**: None of the three skills MAY reimplement arithmetic that an existing engine
  function already performs — each mechanical effect must be produced by calling that function
  (directly or via a thin CLI verb added in this feature), never recomputed in the skill's own
  prose logic.
- **FR-010**: Each skill's prose MUST distinguish, per docs/design/02-architecture.md's
  code/prose table, the player's own choice (which Undertaking, whether/how to spend an advance,
  which trade for Upkeep) from the code-computed numeric effect that choice triggers — the choice
  is presented and gathered by the skill, the effect is only ever reported from what the engine
  verb returned.
- **FR-011**: No skill's prose MAY name a setting or game system; all vocabulary MUST be the
  engine's own descriptive terms (Rally, Downtime, Undertaking, Upkeep, Standing, Stamina,
  Strain, advance), consistent with docs/adr/0013's distinct vocabulary from Claude Code's own
  "skill" concept.
- **FR-012**: All three skills MUST live in the chronicle repo (`wyrd-chronicle-template`), not
  the engine repo, since a chronicle is self-contained after bootstrap and these skills operate
  on chronicle-local state (`pc.yaml`, `party.yaml`, `chronicle.yaml`, `recap.md`) that does not
  exist in the engine repo itself.

## Key Entities

- **Player character sheet** (`pc.yaml`): the state the character skill reads and, via
  spend-advance, mutates one field of at a time.
- **Downtime period state**: the linear Destination → Upkeep → Advances → Undertaking → Rest
  progression from `engine/wyrd/downtime.py`, held only for the duration of one downtime
  invocation.
- **Recap** (`recap.md`): regenerated text the end-session skill writes verbatim from the
  engine's `recap` verb.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A player can view their character sheet or spend an available advance in a single
  skill invocation, with no manual editing of `pc.yaml`.
- **SC-002**: A full downtime phase (Destination through Rest) completes in one skill invocation,
  presenting exactly two player decisions (Upkeep trade when away from home, and the Undertaking)
  and no more.
- **SC-003**: Ending a session always leaves `recap.md` matching what the engine's `recap` verb
  would independently report for the same chronicle state, and a commit exists covering it.
- **SC-004**: 100% of the mechanical numbers these three skills produce (Standing/coin change,
  wound-effect step, advance spend outcome, Stamina-to-max) trace to an existing engine
  function's return value — none is computed in the skill's own prose.

## Assumptions

- `engine/wyrd/downtime.py` and `engine/wyrd/rally.py` are not currently wired into
  `engine/wyrd/catalog.py`/`verbs.py` as CLI verbs. This feature adds the minimal CLI verbs needed
  (a `downtime` verb family and a `rally` verb) to expose their existing pure functions, rather
  than having the skill reimplement or directly import engine internals — consistent with
  docs/design/27-tooling.md's CLI-as-boundary rule. Adding these verbs is engine-repo work and
  will be a separate, small PR in `wyrd` itself if the two repos cannot share one PR; the
  chronicle-repo skills depend on it.
- These three skills belong in `wyrd-chronicle-template`, alongside the not-yet-built
  `/wyrd-play` and `/wyrd-bootstrap`, per that repo's own README ("the repo is self-contained
  after bootstrap"). No skill exists yet in that repo to model conventions from, so this feature
  also establishes the base `.claude/skills/<name>/SKILL.md` shape the later `/wyrd-play` and
  `/wyrd-bootstrap` skills will follow.
- `/wyrd-play` and `/wyrd-bootstrap` themselves are out of scope (separate sibling features, per
  the tracking issue).
- The `spend-advance`, `save`, `recap`, `character-load`/`character-save` and `session-context`
  CLI verbs already exist (landed in #402/PR #407) and are sufficient for the character and
  end-session skills without further engine changes.
- Entity-status validation bugs (e.g. #408, entity.py) are out of scope; if a companion/thread
  entity's status blocks a call these skills make, that dependency is noted rather than fixed
  here.
