# Feature Specification: What a party counts for

**Feature Branch**: `016-party-effective`

**Created**: 2026-08-25

**Status**: Draft

**Input**: Issue [#8](https://github.com/neilgfoster/wyrd/issues/8) — define `party_effective`
precisely enough to implement as a pure function, verify the resulting danger at the party sizes a
real chronicle has, and update [`doc/design/03-rules.md`](../../doc/design/03-rules.md) §7 in place.

## Why this exists

[`doc/design/03-rules.md`](../../doc/design/03-rules.md) §7 publishes the engine's only scaling equation:

> `danger_effective = danger × (party_effective / written_for)`

`written_for` is defined — it is a field on a corpus record
([`doc/design/24-corpus-index.md`](../../doc/design/24-corpus-index.md)), the party size the content was
written for. `danger` is defined — intrinsic difficulty as written. `party_effective` is not
defined anywhere. The nearest thing to a definition is one sentence in `11-corpus-index.md`:

> where `party_effective` counts the player character as 1 and each companion at a fraction, since
> companions are GM-run and less capable

Which fraction is never said. So the equation cannot be evaluated, and every claim in the repo that
rests on it — that a chronicle stays interesting for years without escalating the fiction, that the
whole four-to-six-adventurer corpus is usable by a one-player table — rests on a term nobody can
compute. `11-corpus-index.md` goes further and quotes a *result*: a danger-3 arc written for four,
run by one character and two companions, "plays at roughly danger 2". That figure was never
computed from anything, because there was nothing to compute it from.

This feature therefore carries a decision, not a transcription: **what a companion is worth**, and
**what the engine does with the fractional danger that falls out**.

## Clarifications

### Session 2026-08-25

- **Q: What is one companion worth inside `party_effective`?** → **Diminishing: the k-th companion
  is worth `1/(k+1)`** — the first a half, the second a third, the third a quarter, and so on. A
  retinue is therefore not a power curve; the tenth companion is worth about a tenth of the first.
  The series has a closed form: `1 + 1/2 + 1/3 + … + 1/p` for `p` bodies, the p-th harmonic number,
  so the definition is order-independent and needs no roster ordering. Rejected: a flat half each,
  which is simpler and is the only scheme under which the figure `11-corpus-index.md` already
  quotes comes out exactly — but which makes a large retinue scale danger linearly, and a party of
  bodies is not a party of players. Rejected also: a flat two-thirds, same objection, higher.
- **Q: Both sides of the ratio must be in the same units — does the curve apply to `written_for`
  too?** → **Yes: both counts are read through the same function.** `written_for` still means
  exactly what it meant, the head count the content was written for; what is defined here is how a
  head count of either kind becomes an effective size. Like is compared with like, and a table of
  four bodies runs content written for four exactly as written. Rejected: leaving the denominator a
  raw head count, which is the formula as literally printed today — but which permanently caps
  content at roughly a quarter to a half of its written danger and makes the identity case
  unreachable (`party_effective` would need about thirty-one bodies to reach 4).
- **Q: `danger_effective` is almost never an integer, and `danger` is a dice-count and enemy-count
  multiplier. How does it become a count?** → **It does not. `danger_effective` stays exact, and
  each quantity built from it rounds at its own point of use** — one rounding rule applied at each
  point, not three different ones: round half up, with a minimum of 1 wherever the written quantity
  was at least 1. Rounding once, up front, throws away precision that the later multiplications
  need. Rejected: rounding `danger_effective` itself to an integer, either half-up or down.
- **Q: Which companions count?** → **Those with `status: with-party`, and no others.** The party is
  already a query on exactly that predicate ([`doc/design/19-state.md`](../../doc/design/19-state.md)); a
  companion who is `away`, `dead`, `lost` or `departed` contributes nothing. Presence in a
  particular room is not consulted — scaling is a preparation-time computation, not a per-scene one.
- **Q: What if `written_for` is missing or zero?** → **The content runs as written** — the ratio is
  1. A record that never stated a party size is not a record that claims a party of none.
- **Q: May a setting override the weighting?** → **No.** With the same curve on both sides of the
  ratio, an override on one side alone would break the symmetry that makes the identity case exact,
  and an override on both sides would cancel out. A setting's lever over difficulty is the
  companions it grants and the `danger` its content carries, not the curve.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The engine scales a piece of content to the table that is actually present (Priority: P1)

The GM is preparing a beat. Its record says `danger: 3, written_for: 4`. At the table there is one
player character and two companions. The engine must produce the danger the content will actually
run at, with no judgement call, before any dice are built from it.

**Why this priority**: It is the only scaling equation the engine has, and it currently cannot be
evaluated at all. Nothing else in this feature matters if this does not resolve.

**Independent Test**: Given a party composition and a record's `danger`/`written_for`, the effective
danger is determinable from `doc/design/03-rules.md` §7 alone, and two readers computing it
independently get the same integer.

**Acceptance Scenarios**:

1. **Given** a party of one player character and two companions and a record at `danger: 3,
   written_for: 4`, **When** the engine scales it, **Then** it yields one exact value, and
   `11-corpus-index.md` quotes a figure computed from that value rather than one that merely
   sounded right.
2. **Given** the same party and a record at `written_for: 6`, **When** the engine scales it,
   **Then** the result is lower than for `written_for: 4`.
3. **Given** a party of as many bodies as `written_for`, **When** the engine scales it, **Then**
   `danger_effective` equals `danger` exactly — the identity case is exact, not approximately
   exact.
4. **Given** any `danger_effective`, **When** a dice count, an enemy count or a skill value is
   built from it, **Then** that quantity is rounded half up and is never 0 where the written
   quantity was at least 1 — a trap written `Nd4` always throws at least one die.

---

### User Story 2 - The party changes mid-chronicle (Priority: P2)

A companion is left behind, is killed, or joins. The GM needs to know whether the party the engine
counts is the roster, the people on this journey, or the bodies in this room, and at what moment the
count is taken.

**Why this priority**: Companions leave and return constantly — `status` already has five values
([`doc/design/19-state.md`](../../doc/design/19-state.md)) precisely because this happens. A definition that
does not say which statuses count is undefined in practice even if it names a fraction.

**Independent Test**: Given a set of `character` entities with `role: companion` and their statuses,
the count is derivable from the entity data alone, with no query to the GM.

**Acceptance Scenarios**:

1. **Given** companions at each of the five `status` values, **When** `party_effective` is computed,
   **Then** exactly which statuses contribute is stated, and the rest contribute nothing.
2. **Given** a companion joins between two beats of the same arc, **When** the next beat is scaled,
   **Then** the rule for when a scaled danger is recomputed versus held is stated, and does not
   require recomputing anything already played
   ([`doc/design/22-evolution.md`](../../doc/design/22-evolution.md)).

---

### User Story 3 - A chronicle accumulates a large retinue (Priority: P3)

A chronicle runs long and the player has gathered five, eight, a dozen companions. The GM needs to
know whether the retinue has quietly become a difficulty exploit.

**Why this priority**: A long chronicle is the case the whole scaling equation exists to serve, and
an unbounded party term would make gathering bodies the cheapest way to flatten every arc.

**Independent Test**: Computed directly — the scaled danger for parties from one body to twenty,
against a record written for four.

**Acceptance Scenarios**:

1. **Given** a party that doubles in size, **When** the engine scales content, **Then** the
   effective danger rises by markedly less than double, and each further companion adds less than
   the one before.
2. **Given** a setting that wants companions to matter more or less, **When** it is authored,
   **Then** the design document states that the curve is not overridable and what the setting's
   levers are instead.

---

### Edge Cases

- **A party of the player character alone.** The lower bound of the whole equation, and the most
  common opening state of a chronicle. `party_effective` is 1; the scaled danger must still be a
  playable integer and must not be 0.
- **A record with `written_for: 1`,** or a party larger than `written_for`. Scaling upward is the
  same equation and must not be special-cased into incoherence.
- **A record with `written_for` absent or 0.** Division by zero, or by nothing. The engine must
  have a stated answer rather than crashing or silently guessing.
- **A very large retinue.** Whether the tenth companion is worth what the first was, and whether
  gathering bodies is a way to flatten every arc.
- **Fractional results.** `danger × (party_effective / written_for)` is almost never an integer,
  and `danger` is used as a dice-count and enemy-count multiplier (§7: a trap written `Nd4` does
  `6d4` at danger 6). Every quantity built from it needs a stated rounding.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST define `party_effective` as a pure function of party composition —
  every input is data already held on `character` entities, and no term requires a GM judgement
  call at evaluation time.
- **FR-002**: The player character MUST count as exactly 1.
- **FR-003**: Each qualifying companion MUST contribute a stated weight determined only by how
  many companions there are, and the document MUST say which companion `status` values qualify.
- **FR-004**: `danger_effective` MUST remain exact rather than being rounded to an integer, and the
  engine MUST state the single rounding rule every quantity built from it applies at its own point
  of use, including behaviour at exact halves.
- **FR-005**: No quantity built from `danger_effective` MUST come out as 0 where the written
  quantity was at least 1.
- **FR-011**: Both sides of the ratio MUST be converted from a head count to an effective size by
  the same function, so that a party of as many bodies as `written_for` runs content exactly as
  written.
- **FR-006**: The engine MUST state its behaviour when `written_for` is missing or zero.
- **FR-007**: `doc/design/03-rules.md` §7 MUST contain no undefined term after this change, and MUST be
  rewritten in place rather than appended to.
- **FR-008**: The sentence in `doc/design/24-corpus-index.md` that describes `party_effective`, and the
  worked figure it quotes, MUST agree with `doc/design/03-rules.md` §7 — one description of one thing.
- **FR-009**: A committed script MUST compute the scaled danger for the party compositions a real
  chronicle has, and MUST assert agreement with every figure any design document quotes, so a later
  edit that drifts from the numbers fails rather than reads plausibly.
- **FR-010**: The decision MUST be recorded as an ADR if a workable alternative was rejected.

### Key Entities

- **Party**: not an entity — a query over `character` entities with `role: companion` and a
  qualifying `status`, plus the player character
  ([`doc/design/19-state.md`](../../doc/design/19-state.md)). This feature does not introduce a
  `party.yaml`.
- **Companion**: a `character` entity whose mechanical layer is deliberately thin — presence, bond,
  a competence or two, and no numeric capability score. Any definition of `party_effective` that
  needs a companion's power level would have to invent that data.
- **Beat/arc record**: carries `danger` and `written_for`
  ([`doc/design/24-corpus-index.md`](../../doc/design/24-corpus-index.md),
  [`doc/design/28-arcs-and-beats.md`](../../doc/design/28-arcs-and-beats.md)). Neither field is changed by
  this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Two readers given the same party composition and the same record compute the same
  integer `danger_effective`, from `doc/design/03-rules.md` §7 alone, without consulting each other.
- **SC-002**: Scaled danger is shown for every party a real chronicle has — one player character
  with zero, one, two, three and four companions — against records written for four and for six, as
  computed output rather than as prose, and again out to a retinue large enough to show the curve
  flattening.
- **SC-003**: Every numeric claim about scaling that appears in any design document is asserted by
  the committed script; changing the rule without changing the documents fails the script.
- **SC-004**: No term in `doc/design/03-rules.md` §7 is undefined, and no reader has to consult
  `11-corpus-index.md` to evaluate the equation.
- **SC-005**: The shape of the danger formula — `danger` times a ratio of party sizes — and the
  meaning of `written_for` as a head count are both unchanged by this feature. What is new is only
  how a head count of either kind becomes an effective size.

## Assumptions

- The formula's shape (`danger × (party_effective / written_for)`) and `written_for`'s meaning are
  fixed by the issue's scope. Only `party_effective`, and the arithmetic needed to turn its result
  into a usable number, are open.
- Companions carry no numeric capability, and this feature does not add one — the thin companion
  layer is a stated design position
  ([`doc/design/19-state.md`](../../doc/design/19-state.md), [`doc/design/16-session.md`](../../doc/design/16-session.md)).
- Scaling is a preparation-time computation, not a per-roll one. Rules changes apply forward only
  ([`doc/design/22-evolution.md`](../../doc/design/22-evolution.md)), so nothing already played is
  recomputed.
- Hired help and other non-companion bodies are outside this feature; `needs_capability` already
  covers what they are for.
