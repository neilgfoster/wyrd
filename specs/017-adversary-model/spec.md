# Feature Specification: The adversary model

**Feature Branch**: `017-adversary-model`

**Created**: 2026-08-25

**Status**: Draft

**Input**: Issue [#54](https://github.com/neilgfoster/wyrd/issues/54) — decide how an opponent is
represented, give the setting file that holds them a schema and a validator, and update
[`design/`](../../design/) in place so combat has something defined on the other side of the roll.

## Why this exists

**Nothing in `design/` says how an opponent is represented.** Adversary, opponent and statblock
return no matches across every design document.

Two documents gesture at it and neither delivers:

- [`design/13-authoring-a-setting.md`](../../design/13-authoring-a-setting.md) lists
  `setting/bestiary.yaml` in the setting layout with the parenthetical "creature stat blocks (a
  lookup table)". No schema, no example, no field list.
- [`design/14-entities.md`](../../design/14-entities.md) lists `creature` as an entity type —
  "a stat block — a kind of thing, not an individual". It says what a creature *is not* and never
  says what it carries.

Meanwhile the ruleset has been reading fields off an opponent for four stages:

| Rule | Reads from the opponent |
|---|---|
| the exchange ([`03-rules.md`](../../design/03-rules.md) §2) | a skill to resist an attack with; a weapon's damage to roll |
| armour subtracts dice | an armour rank |
| the critical rule | current and maximum Stamina, and the damage type of its blows |
| the crowd rule ([ADR 0019](../../design/adr/0019-a-crowd-is-defined-by-one-blow-and-a-skill-gap.md)) | **maximum Stamina**, **armour**, and **its relevant skill** — all three, as an explicit lookup |
| ranged attacks | whether it can attack at range at all |
| Aftermath ([`03a-2-aftermath.md`](../../design/03a-2-aftermath.md)) | whether it is a character or companion, or neither |

The crowd rule is the sharp case. It is stated as *"a lookup, and nothing else"* over three fields,
and none of those three fields is defined anywhere as belonging to anything. A rule whose entire
claim to determinism is that it reads values rather than judging them is currently reading values
off a record with no schema.

So a setting author has no contract to fill, and the GM has to invent an opponent's numbers at the
table — which is exactly the *judgement call the rules do not cover* that this repo keeps being
corrected for.

This feature therefore carries a decision, not a transcription: **how much of the character model an
adversary gets**, and **what a setting is allowed to put in a stat block without forking the
engine**.

## Clarifications

### Session 2026-08-25

- **Q: What does an opponent test when a roll names a skill its block does not carry?** → **A
  per-adversary baseline.** Each block declares one percentage used for any skill it does not list.
  Rejected: the untrained 10% a character falls back to — that rule was written for people, who have
  a reason to be bad at what they never learned, and applying it to opposition makes every opponent a
  10% at everything off its short list. It also breaks the crowd rule from underneath: the
  skill-gap test is *ahead by 20 or more*, so against a 10% fallback a merely competent character
  clears almost anything for free. A baseline that can sit above 30 keeps that test doing the work
  [ADR 0019](../../design/adr/0019-a-crowd-is-defined-by-one-blow-and-a-skill-gap.md) gave it.
  Rejected also: requiring the block to enumerate every skill it could be tested on, which makes a
  stat block scale with the setting's skill count and turns an unlisted skill into an authoring bug
  rather than a rule.
- **Q: Does danger scale an opponent's own skill percentages, or only how many appear?** → **Both,
  as [`03-rules.md`](../../design/03-rules.md) §7 already publishes.** Enemy counts scale *and* skill
  values scale. §7's sentence stands and is not corrected. Rejected: counts only, which would have
  made the published sentence wrong and required correcting it in place — leaner, and it keeps a
  stat block meaning exactly one thing, but it also leaves the engine with one lever where the
  design has always claimed two, and a party of six walking into content written for one meets more
  of the same rather than anything harder. Rejected also: pointing content at a separate tougher
  entry, which pushes the work onto every setting author and multiplies entries.

  **This decision creates an obligation, and the spec carries it as one.** A percentage cannot be
  multiplied by `danger_effective` — 45 × 2.64 is not a skill. The engine modifies skills
  *additively* everywhere it modifies them at all (the difficulty ladder is +20 to −40), so the
  ratio must resolve to a **points adjustment**, it must be **exactly zero at the identity case**,
  and it must be **bounded so no opponent leaves the ladder**. The mapping is not chosen in this
  spec: it is computed, at the party sizes and danger ratings a real chronicle has, and the bound is
  derived before any round number is written down. See FR-013a–c.
- **Q: May an adversary block carry traits?** → **Yes, from a closed effect vocabulary.** A trait is
  a name plus an effect drawn from an engine-defined list that touches only mechanisms that already
  exist — difficulty, damage, Stamina, armour, the Wyrd die — and the validator enforces the list.
  Rejected: no traits, which is leaner and unpoliceable-proof but makes every monster a man with
  different numbers. Rejected: free-text traits the GM interprets, which is the one option under
  which a setting can add a mechanism —
  [`13-authoring-a-setting.md`](../../design/13-authoring-a-setting.md) forbids that outright — and
  which is inference where a rule could be deterministic
  ([ADR 0005](../../design/adr/0005-deterministic-over-inference.md)).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A setting author writes down an opponent, completely (Priority: P1)

An author is filling in a setting's `bestiary.yaml`. They need to know every field an opponent
carries, which are required, what each one means, and what the engine will do with it — without
reading the ruleset end to end and reverse-engineering the answer from which rules mention an
opponent.

**Why this priority**: This is the contract. Nothing else in this feature can be tested until there
is a schema to test against, and no setting can be built until an author knows what to type.

**Independent Test**: Write a complete opponent from the schema alone, run the validator over it,
and get a pass. Then remove each required field in turn and get a specific, named failure each time.

**Acceptance Scenarios**:

1. **Given** the schema, **When** an author writes an opponent with every required field, **Then**
   the validator accepts it and no rule in §2 of the ruleset has to be resolved by GM judgement to
   run it.
2. **Given** an opponent missing a required field, **When** the validator runs, **Then** it names
   the field and the entry, and exits non-zero.
3. **Given** an opponent carrying a field the engine does not define, **When** the validator runs,
   **Then** it fails rather than ignoring it — an unrecognised field is how a setting quietly adds a
   mechanism ([`design/13-authoring-a-setting.md`](../../design/13-authoring-a-setting.md) forbids
   exactly that).

---

### User Story 2 - The GM runs a full exchange against that opponent from the rules as written (Priority: P1)

The player attacks a written opponent. Every step — the opposed test, degrees, the telling blow,
damage, armour, the drop below zero, the critical table, Aftermath — resolves by reading the block
and applying a published rule. Nothing is invented at the table.

**Why this priority**: A schema that cannot be run is a table of field names. This is the story that
proves the block is *sufficient*, which is the actual acceptance criterion on the issue.

**Independent Test**: Take one written opponent and one written character and resolve a complete
exchange, deterministically, from a fixed seed — and separately compute the exchange's outcome
distribution in closed form so the worked example can be checked rather than asserted.

**Acceptance Scenarios**:

1. **Given** a written opponent and a written character, **When** the character attacks, **Then**
   the opposed test, the margin, the telling blow, the damage roll, the armour subtraction and the
   minimum of 1 all resolve from published rules and declared fields.
2. **Given** damage that takes the opponent below 0 Stamina, **When** the critical is rolled,
   **Then** the damage type comes off the block that struck and the table is selected without a
   judgement call.
3. **Given** the opponent drops, **When** the fight ends, **Then** whether Aftermath is rolled for
   it is answered by the block, not by the GM.

---

### User Story 3 - The same model serves a named antagonist and an anonymous crowd (Priority: P2)

A nemesis who recurs across a campaign and twenty nameless bodies in a yard are both opponents. The
engine must run both without a second representation, and the crowd rule's three-field lookup must
resolve against both — qualifying the crowd and, ordinarily, not qualifying the nemesis.

**Why this priority**: The crowd rule already depends on this and shipped before it existed. It is
the highest-value consistency check in the feature, but it is only testable once Story 1 defines the
fields it reads.

**Independent Test**: Run the crowd-membership lookup over a written nemesis and a written mob body
and confirm each lands on the side the fiction expects, with the deciding field named.

**Acceptance Scenarios**:

1. **Given** a mob body written to the schema, **When** the crowd lookup runs against a character,
   **Then** all three tests are answerable from declared fields and the body qualifies.
2. **Given** a named antagonist written to the schema, **When** the same lookup runs, **Then** it
   fails on a named field rather than on the GM's sense that a nemesis ought not to be swept aside.
3. **Given** a character whose relevant skill is within 20 points of the mob's, **When** the lookup
   runs, **Then** the body does not qualify, and the fight is rolled — confirming the gap test reads
   two declared percentages and not a category.

---

### User Story 4 - Danger scaling reaches an opponent through the mechanism that already exists (Priority: P2)

A piece of content written for a party of four is run by a party of three. The opposition it
contains must scale by the published equation
(`danger_effective = danger × (party_effective / written_for)`,
[`03-rules.md`](../../design/03-rules.md) §7) and by nothing else.

**Why this priority**: The issue's fifth scope item. It is also where a second, competing difficulty
mechanism would get in — and §7 currently claims something about opponents that no rule delivers.

**Independent Test**: Scale one written encounter across the party sizes a real chronicle has and
confirm every quantity that changed is traceable to §7's arithmetic, with the identity case landing
exactly.

**Acceptance Scenarios**:

1. **Given** an encounter record and a party, **When** the engine prepares it, **Then** the count of
   opponents is derived from `danger_effective` under §7's rounding rule, minimum 1.
2. **Given** the same encounter run by a party of exactly `written_for` bodies, **When** it is
   prepared, **Then** it runs exactly as written.
3. **Given** any party size, **When** the encounter is prepared, **Then** the opponents' skill
   percentages carry a points adjustment derived from §7's ratio and from nothing else, and the
   bestiary entry they were read from is unchanged.
4. **Given** a party of exactly `written_for` bodies, **When** the encounter is prepared, **Then**
   the skill adjustment is **exactly +0** — the identity case holds on both quantities §7 scales,
   not just on the count.

---

### Edge Cases

- **An opponent is asked to test a skill it does not carry.** Constant in play — an opponent
  resisting a shove, spotting a liar, chasing a fleeing party. The block cannot list every skill a
  setting declares, so the fallback is published: it tests at its declared **baseline**.
- **An opponent that is a person.** A nemesis is already a `character` entity with `role: nemesis`
  ([`14-entities.md`](../../design/14-entities.md)), not a `creature`. Both must be runnable as
  opposition without two schemas describing one thing differently — recurring fault class 3.
- **An opponent with no attack at all** — something that is dangerous by being present, or purely an
  obstacle. Damage must be optional without leaving the exchange undefined.
- **An opponent whose armour is better than heavy, or whose Stamina is far above a character's.**
  The scale has to state its own bounds, or a setting will write a number the ladder cannot absorb.
- **A crowd body and a named antagonist with identical numbers.** The crowd lookup is explicitly
  numeric, so it must not be silently overridden by a name or a role — or the rule stops being a
  lookup.
- **An opponent dropping below 0 Stamina.** The critical rule and the Aftermath rule treat
  characters and companions specially; an opponent is neither, and §2 already says the Aftermath
  table is *not* rolled for a crowd. What happens for a single opponent must be stated.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST define an **adversary block** — the complete set of fields the ruleset
  reads off an opponent — and MUST state, for each field, which published rule consumes it. A field
  no rule reads does not belong in the block.
- **FR-002**: The adversary block MUST be a deliberately thinner record than the player character's
  ([`03b-the-character.md`](../../design/03b-the-character.md)), and the design MUST state which
  parts of the character model an adversary does *not* carry and why. This is a rejected alternative
  with a working competitor and MUST be recorded as an ADR.
- **FR-003**: The block MUST carry, at minimum, the three fields the crowd rule already reads as a
  lookup: **maximum Stamina**, **armour rank**, and **skill percentages** — and the field names in
  the design MUST be the ones the crowd rule cites, so the rule and the record cannot drift apart.
- **FR-004**: The block MUST specify what the opponent rolls (skill percentages under setting-owned
  names), what it survives (Stamina, armour), and what it does on a turn — the last expressed
  entirely within the closed action list in [`03-rules.md`](../../design/03-rules.md) §2, never as a
  new action.
- **FR-005**: The block MUST declare the **damage** an attack deals and its **damage type**, drawn
  from the closed set of four ([ADR 0022](../../design/adr/0022-four-damage-types-named-for-the-wound.md)),
  so the critical table is selected without a judgement call. An opponent with no attack MUST be
  expressible, and the exchange MUST remain defined when one is present.
- **FR-006**: The block MUST carry a **baseline** percentage, and the engine MUST publish that an
  opponent tests any skill its block does not list at that baseline. The baseline is a required
  field: an opponent with no baseline is an opponent the GM has to improvise, which is the fault
  this feature exists to remove.
- **FR-007**: The block MUST state whether the opponent can attack at range, because
  [`03-rules.md`](../../design/03-rules.md) §2's ranged table and engagement rule both branch on it.
- **FR-008**: The engine MUST state what happens when an opponent that is neither a character nor a
  companion drops below 0 Stamina — whether a critical is rolled, and whether Aftermath is — and it
  MUST agree with §2's existing statement that Aftermath is not rolled for a crowd.
- **FR-009**: `setting/bestiary.yaml` MUST have a published schema, and the schema MUST be the same
  one a `character` entity uses to be run as opposition — one description of an opponent, reached
  two ways, not two descriptions.
- **FR-010**: A **validator** MUST exist that checks a `bestiary.yaml` against the schema, reports
  the entry and field for every failure, and exits non-zero on any. It MUST reject unrecognised
  fields rather than ignoring them.
- **FR-011**: The validator MUST reject any value outside the bounds the ruleset can absorb —
  armour ranks outside the published set, a damage type outside the closed four, a skill percentage
  outside the scale in [`03b-the-character.md`](../../design/03b-the-character.md) §2.
- **FR-012**: The block MAY carry **traits**. A trait is a display name plus an effect drawn from a
  **closed engine vocabulary**, and the engine MUST publish that vocabulary in full. Every effect in
  it MUST act on a mechanism that already exists — difficulty, damage, Stamina, armour, the Wyrd die
  — and none may introduce one. The validator MUST reject any effect outside the vocabulary. A
  setting may extend, retune, rename or disable, and may **never add a mechanism**
  ([`13-authoring-a-setting.md`](../../design/13-authoring-a-setting.md)); an unbounded trait is
  precisely how that rule gets circumvented.
- **FR-013**: Opposition MUST scale to the party present through §7's equation and through no other
  mechanism. Per the clarification, §7 stands as published: **both the count of opponents and their
  skill values scale**. The design MUST state exactly which quantities scale and how, and the block
  itself MUST remain absolute — scaling happens when content is prepared, never by rewriting a
  bestiary entry.
- **FR-013a**: The skill scaling MUST be expressed as a **points adjustment added to the
  percentage**, not a multiplication of it. Every other modifier in the engine is additive on the
  skill (the difficulty ladder is +20 to −40), and a percentage multiplied by a ratio is not a
  percentage.
- **FR-013b**: The adjustment MUST be **exactly zero when `party_effective` equals the effective
  size of `written_for`** — the identity case that makes §7 a ratio rather than a discount
  ([ADR 0024](../../design/adr/0024-a-party-is-worth-less-than-its-head-count.md)). Content written
  for four, run by four bodies, meets opponents at their written percentages.
- **FR-013c**: The adjustment MUST be **bounded so that no opponent leaves the difficulty ladder**,
  and the bound MUST be **computed before it is written down** — derived from the party sizes,
  `written_for` values and danger ratings a real chronicle actually produces, not chosen as a round
  number and justified afterwards. The design MUST publish the resulting adjustment at the party
  sizes a table has, the same way §7 publishes its own ratio table, and MUST state what happens at
  the extreme where the computed adjustment would push a skill past the ladder's top or below zero.
- **FR-014**: A **worked exchange** MUST be published — one written opponent, one written character,
  a complete fight resolved from the rules as written — and every figure in it MUST be computed by a
  script rather than asserted, per [ADR 0005](../../design/adr/0005-deterministic-over-inference.md).
- **FR-015**: That script MUST assert agreement with the figures earlier issues already computed
  and published, so a change here cannot silently contradict them: the crowd rule's one-blow band
  (**67% to 100%** at Stamina 1 unarmoured, **11%** in the lightest armour, **33%** at Stamina 2),
  the free clear's **1.25× to 1.82×** discount, and the drop rates at **14.8%** and **48.6%** in §2.
- **FR-016**: Every affected design document MUST be rewritten in place to describe the present —
  including [`03b-the-character.md`](../../design/03b-the-character.md) §4, which currently states
  that how an adversary is represented "is not yet decided", and
  [`14-entities.md`](../../design/14-entities.md)'s `creature` row.
- **FR-017**: Every engine label introduced MUST be descriptive English, and no setting or system
  name may appear in any document this feature touches under `design/` or in `README.md`.

### Key Entities

- **Adversary block**: the fields the ruleset reads off an opponent — what it rolls, what it
  survives, what it does on a turn, and what its blows are. Absolute values, not values relative to
  a party or a danger rating.
- **`bestiary.yaml` entry**: a `creature` — a kind of thing, not an individual. One adversary block
  plus the identity fields a lookup table needs. Many instances of one entry appear in one fight.
- **`character` entity used as opposition**: an individual — a nemesis, a rival, a hostile
  companion. Carries the person layer already defined in [`04-session.md`](../../design/04-session.md)
  *and* an adversary block, so the same rules read the same fields.
- **Encounter opposition**: what a piece of content declares it contains — which entries, how many,
  at what `danger` and `written_for`. §7 scales the count and the skill percentages the opponents
  are run at; the bestiary entry itself is never rewritten.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every field the ruleset reads off an opponent is defined in exactly one place; a grep
  for each of the crowd rule's three lookup fields finds the rule and the schema agreeing on the
  name.
- **SC-002**: A complete opponent can be written from the schema alone, and a full exchange against
  it resolves with **zero** GM judgement calls outside the published difficulty ladder.
- **SC-003**: The validator passes a correct `bestiary.yaml`, and fails a missing required field, an
  unrecognised field, an out-of-range value and an out-of-set damage type — each with the entry and
  field named, and a non-zero exit.
- **SC-004**: The crowd lookup resolves against both a written mob body and a written named
  antagonist, landing on opposite sides, with the deciding field named in each case.
- **SC-005**: An encounter prepared for a party of exactly `written_for` bodies runs exactly as
  written — count unchanged **and** skill adjustment +0 — and every quantity that changes at any
  other party size is reproducible from §7's arithmetic alone.
- **SC-005a**: Across every combination of party size 1–6, `written_for` 1–6 and danger 1–6, no
  opponent's adjusted skill leaves the ladder the engine can express, and the check script asserts
  it rather than the design claiming it.
- **SC-006**: Every numeric claim in the worked exchange is produced by the check script, and the
  script asserts the previously published figures listed in FR-015 — non-zero exit on any
  disagreement.
- **SC-007**: `python3 tools/check_docs.py` and `python3 tools/backlog.py check` both pass, and no
  document under `design/` still says the adversary model is undecided.

## Assumptions

- **The thin model wins.** Issue #54 states a thin model is the likelier right answer for a solo
  engine, and this spec proceeds on that basis. The alternative — adversaries carrying the full
  character model, including the tracks, a career and advancement — is still recorded as the
  rejected option in the ADR, per FR-002.
- **The person layer already exists and is not re-specified here.** A named antagonist's objective,
  bond, secret and arc are defined in [`04-session.md`](../../design/04-session.md). This feature
  adds the adversary block to such a character; it does not redesign what a character entity is.
- **Skills stay setting-owned and engine-agnostic.** An adversary's skills are names the setting
  supplies and percentages the engine understands, exactly as for a character
  ([ADR 0013](../../design/adr/0013-the-engine-names-no-skill.md)). No engine rule introduced here
  may name a skill.
- **Armour ranks are the published four** — none, light `1d3`, modest `1d6`, heavy `2d6`, with a
  shield raising one rank ([`03-rules.md`](../../design/03-rules.md) §2). This feature does not add
  a rank.
- **No new entity type.** `creature` already exists ([`14-entities.md`](../../design/14-entities.md))
  and a new type is explicitly an engine change; this feature fills the existing type in rather than
  adding one.
- **The baseline is one number, not a second skill list.** It is what the opponent tests any
  unlisted skill at — it does not become a floor under its listed skills, and a listed skill below
  the baseline stays where it was written.
- **Tooling stays stdlib-only** ([`design/07-tooling.md`](../../design/07-tooling.md)), so the
  validator and the check script use the standard library and the repo's existing conventions.
