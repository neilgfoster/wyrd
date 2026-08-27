# Afflictions

The table a character rolls on **when a Trauma test fails at 6+ Trauma**. It is what
[`03-rules.md`](03-rules.md) means by *take an Affliction*, and it is the only place the lasting
shape of Trauma is defined.

It is a family of the kind [`04-tables.md`](04-tables.md) defines, and everything below is
declared within those conventions.

---

## Body, never mind — restated

[`07-transformations.md`](07-transformations.md) already resolves the collision
[`03-rules.md`](03-rules.md) §4 used to read: **a Taint threshold always forces a Transformation,
never an Affliction.** This document restates it once for a reader who starts here: Afflictions
are Trauma's business alone. Taint and Trauma are independent scores with independent triggers,
and where the two ever appear to disagree, `10-transformations.md`'s statement governs.

## The test

**"Test on every further point"** ([`03-rules.md`](03-rules.md) §5) is an ordinary test under the
[`03-rules.md`](03-rules.md) §1 resolution rule — `d100` against a skill — not a new mechanic.
**The skill is chosen by the GM to fit what is actually straining the character**, the same shape
as Exposure's "resist with a test" (§4): the engine names no skill
([ADR 0013](../adr/0013-the-engine-names-no-skill.md)), so a universal "Willpower" would be exactly
the kind of borrowed vocabulary this engine avoids. A soldier holding a battle line under fire, a
scholar staring at something that should not exist, and a parent watching their child suffer are
straining against different things, and the test should read that way at the table.

**Only pass or fail matters.** Degrees are not read for this test — there is no magnitude to a
mental break, only whether it happens — matching how the transformation table's roll reads no
Wyrd die either.

**6 is the floor, not itself a further point.** A character who reaches exactly 6 Trauma does not
test; the test fires on the next point past it (7, 8, 9, …), and on every one thereafter for as
long as Trauma stays at 6 or above. If a single event adds more than one point at once (the GM's
"genuinely terrible event" discretion in §5), each point crossed past the floor is its own further
point and is tested in turn, in the order the points were gained.

## The roll

| | |
|---|---|
| **key** | `affliction` |
| **die** | `1d12` |
| **modifier** | none |
| **lowest possible total** | `1` |
| **uniqueness** | repeatable |
| **extra row fields** | none |

**The family is repeatable, not unique per character.** `07-tables.md`'s default is unique per
family, with an explicit carve-out for a family where the same result twice is ordinary — and §5
already says exactly that: "the track sawtooths, so a character can break many times across
years." A repeat draw is not a defect to guard against here; it is the same fracture recurring,
which is the more honest reading of a track that resets by design rather than terminating.
Repeatability also means this family carries no exhaustion clause: unlike the transformation
table's hidden threshold, nothing caps how many times a character can break this way, and nothing
in §5 asks for one.

**No severity field.** §5 already fixes the track's cost at a flat 6 Trauma per Affliction —
unlike a Transformation, a break here does not come in degrees of magnitude that would need a
number to charge against Taint. A row has nothing left to price.

## The table

Every row is phrased as **behaviour the character exhibits**, never as a named condition or
diagnosis — the engine's sharpest presentation constraint for this family
([`03-rules.md`](03-rules.md) §5). Every row's effect is stated so the engine can apply it without
reading the prose: a declared test the character cannot make without cost, or a standing penalty
to a category of test, using the same points-modifier and difficulty-ladder vocabulary
[`03-rules.md`](03-rules.md) §1 already defines elsewhere. No row grants a net mechanical
advantage, applies a punitive stat loss beyond its stated effect, or carries a tone (grim, heroic,
comic): what a row means in a given chronicle is for the GM to render in that setting's register,
never baked into the row itself. No row presumes a particular moral reading of the behaviour it
describes — none of them are written as a failure of character.

| Range | Effect | Description |
|---|---|---|
| 1 | Once per session, the GM may require a test before the character acts on the impulse the row names, or the action does not happen this beat. | Something insists on being done, right now, whether or not it is wise. |
| 2 | The character cannot be the first to act in a scene involving the thing this Affliction fixes on, without a test — someone else must move first. | They wait. Everyone else notices the waiting. |
| 3 | A declared category of test (the GM names it once, fitting the fiction) is at **Challenging** instead of its ordinary difficulty whenever this Affliction's trigger is present in the scene. | The trigger walks into the room and the hands stop being steady. |
| 4 | The character avoids a named circumstance where they reasonably could act; doing so anyway requires a test, and failure ends the attempt before it starts. | There is a door they do not open. It would be so easy to open it. |
| 5 | Once triggered in a scene, the character's declared bonuses ([`03-rules.md`](03-rules.md) §1) are unavailable for the rest of that scene — nothing said lands as specific anymore. | The words are there. They will not come out right. |
| 6 | The character must spend a Resolve point or take 1 Strain to continue an ordinary task once interrupted by the trigger; refusing ends the task for the scene. | Once it starts, stopping costs something. |
| 7 | A companion or ally attempting to help the character on a relevant test must themselves test first, or the help is refused in the fiction. | Help looks, from the inside, like something else. |
| 8 | The character takes the isolating action by default when a scene offers a choice between it and staying with the party; staying instead requires a test. | The room empties before anyone asks them to leave. |
| 9 | A specific object, place, or person becomes something the character must reach, protect, or check on before anything else in a scene; delaying it requires a test. | Everything else can wait. This cannot. |
| 10 | The character reads a named category of ordinary event as the trigger's return; a test is required to act on what is actually in front of them instead. | It has already happened before. It is happening again. It has not happened yet. |
| 11 | Strangers and casual acquaintances react to the character at one step worse on the reaction ladder ([`03-rules.md`](03-rules.md) §1) by default, until the character spends a scene establishing otherwise. | People decide something about them before a word is said. |
| 12 | The character's Fault Line ([`03-rules.md`](03-rules.md) §4) is one step easier for the GM to invoke against them — an existing Drive-based penalty applies at half the usual bar for triggering it. | Whatever already ran through them runs closer to the surface now. |

## The sawtooth cadence

The cadence is computed, not asserted, in
[`tools/check_affliction.py`](../../tools/check_affliction.py). Once a character's Trauma first
reaches 6, the long-run rate at which further Trauma-adding events produce an Affliction has an
exact closed form: **1 in every 6 events, independent of the test's skill.** The floor (6) and the
drop (6) are the same number, and that cancellation is what removes the skill dependence — the
mechanism does not depend on what the GM chooses to test against, only on the floor and the drop
agreeing. It holds for any skill below **5/6 (≈83%)**; a character passing more reliably than that
has no long-run Affliction rate at all, because Trauma then drifts upward without the sawtooth
ever pulling it back down (the script confirms the runaway numerically past that point, rather
than only asserting the algebra).

At representative event rates — 0.25 to 2 Trauma-adding events (criticals taken, failed Terror
tests) per session — the computed cadence runs from roughly **1 Affliction every 24 sessions**
(a quiet chronicle) to **1 every 3 sessions** (a hard-fought one), or **1.9 to 15 per
chronicle-year** at a rough weekly cadence (45 sessions/year). Both ends are stated as findings:
the quiet end is well short of "one every ten years," and the busy end is short of "one every two
sessions" but close enough to it that a chronicle running hot on criticals and failed Terror tests
should expect this track to matter, not sit dormant.

## What a setting may replace

Per [`04-tables.md`](04-tables.md): a setting may replace this table's rows — their ranges,
effects and descriptions — under `overrides.tables: {affliction: ...}`. It may not change the die,
the modifier, the uniqueness (repeatable), or the row schema. No row may carry a setting's name, a
system's name, or a tonal register; a setting renames what the descriptions say, never what the
effects do.
