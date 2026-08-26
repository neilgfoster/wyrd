# Systems of power

The schema a setting fills in to give its practitioners supernatural or extraordinary reach —
what [`26-authoring-a-setting.md`](26-authoring-a-setting.md) means when it says a setting may
never add a mechanism the engine does not have. Magic, psionics, a saint's grace, an engineered
apex organism's neural overclock — every one of them is *one system of power*, declared as data
against the schema below. See [ADR 0036](../adr/0036-one-configurable-power-mechanism.md) for why
this is one configurable mechanism rather than a set of engine-defined shapes.

---

## What a system of power declares

| Field | Required | What it means |
|---|---|---|
| `id` | yes | stable, kebab-case, unique within the setting |
| `name` | yes | the label a player sees; renamed freely, presentation-only |
| `skill` | yes | the setting's own skill an invocation tests — no engine skill vocabulary in between ([ADR 0013](../adr/0013-the-engine-names-no-skill.md)) |
| `strain_cost` | yes | Strain paid on every invocation, win or lose |
| `requires_training` | yes | `true` removes the untrained attempt entirely; `false` leaves the standard untrained-10% rule in force |
| `resolve_cost` | no | Resolve paid on every invocation, in addition to Strain |
| `ill_omen_taint` | no, default `1` | Taint gained when an invocation's Wyrd die reads Ill Omen |
| `description` | no | flavour only; no mechanical effect |

A setting declares as many systems of power as it needs. Nothing about the schema constrains how
many a character may know, how a system is learned, or what an invocation looks like in the
fiction — those are the career graph and `voice.md`'s job, unchanged by this document.

`skill` must name a skill the setting has actually declared; a system of power cannot test a
skill that does not exist. Two systems of power may share a skill (a mundane and a supernatural
use of the same trained ability) — the schema does not require skill uniqueness across systems.

## Resolution

**Invoking a system of power is an ordinary test.** [`03-rules.md`](03-rules.md) §1 governs it in
full: `d100` against the character's `skill%`, difficulty modifying the skill never the roll,
degrees read from the tens digits, the Wyrd die read from the natural roll's units digit,
declaration and assistance composing exactly as they do for any other test. **Nothing about
invoking a system of power changes the resolution mechanic.** There is no separate power-test
roll, no additional dice, no power-specific difficulty ladder.

**`requires_training: true` removes the untrained attempt outright** — the same rule
[`03-rules.md`](03-rules.md) §1 already gives a skill requiring training (a language the
character does not speak is not a 10% chance; nor is a system of power marked this way).

**Cost is paid once the roll resolves, regardless of outcome.** The declared `strain_cost` always
applies; the declared `resolve_cost`, if present, applies identically. Failing an invocation still
costs what attempting it costs — the same shape any strenuous, risky effort already has in this
engine.

**Cost does not scale with the narrative magnitude of what was attempted — that is intentional,
not an oversight.** "I warm myself against the chill" and "I burn the entire city down" cost the
same declared Strain if both are framed as the same system of power, because the schema already
has a lever for how hard an invocation is: **difficulty**, set by the GM from the fiction, which
modifies the skill the roll is tested against ([`03-rules.md`](03-rules.md) §1). A second lever
that scaled cost by intensity would duplicate difficulty's job without a clean boundary of its
own — nothing distinguishes "this working is difficult" from "this working is costly" cleanly
enough to justify two mechanically distinct dials for the same fictional judgment. A GM who wants
burning down a city to cost more than warming a hand does that by making it a harder test, or by
having the fiction demand a second invocation, not by a cost multiplier. This keeps every system
of power a single flat number, exactly as the schema already requires.

## The Ill Omen consequence

**An Ill Omen on an invocation applies the declared `ill_omen_taint` through the engine's existing
Taint-accrual path** ([`03-rules.md`](03-rules.md) §4), exactly as the Bargain, Exposure, or an
Invocation already feed it. If that Taint gain crosses a threshold, a transformation-table roll
follows immediately, using the same loop [`10-transformations.md`](10-transformations.md)
already defines. **No second table exists for this.** A power-specific consequence table would
duplicate a consequence chain the engine already has, for no distinction that changes what
happens at the table.

**A Fair Omen carries no power-specific rule** — it is read exactly as [`03-rules.md`](03-rules.md)
§1 already reads it for any other test; a system of power adds nothing here.

**When a setting has disabled Taint** (`overrides.disable: [taint]`), an Ill Omen on an invocation
applies no Taint-track consequence at all — the same behaviour disabling Taint already produces
everywhere else it is fed. The base d100 resolution and the declared Strain/Resolve costs are
unaffected; disabling Taint removes only the Taint-fed half of this mechanism, not invocation
itself.

## A worked example

```yaml
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    resolve_cost: 1
    requires_training: true
    ill_omen_taint: 1
    description: >
      Drawing heat and light from the practitioner's own reserve rather than the world's.
```

A trained practitioner attempts an Ember-craft working: the GM sets a difficulty from the
fiction, the player rolls `d100` against their Ember-craft skill exactly as any other test. On
resolution — success or failure — the character's Strain drops by 2 and Resolve by 1. If the
natural roll's units digit was 0 (Ill Omen), the character also gains 1 Taint through the existing
accrual path, with a transformation roll to follow only if that crosses a threshold.

A second, structurally different example — confirming the schema does not assume a mythic
register:

```yaml
systems_of_power:
  - id: signal-attunement
    name: Signal attunement
    skill: signal-attunement
    strain_cost: 3
    requires_training: true
    ill_omen_taint: 2
    description: >
      Reading and briefly steering the ambient dataflow a practitioner's augmentation was
      never rated for.
```

No `resolve_cost` here — this system draws on Strain alone — and a higher `ill_omen_taint`,
reflecting that pushing an augmentation past its rating is a worse thing to get wrong. Both
examples validate against the identical schema; nothing about either needed a field the other does
not use, which is the test a far-future setting has to pass for this mechanism to hold without a
second one being invented for it.

Run `python3 tools/check_power_systems.py <path-to-power.yaml>` to validate a setting's own
declarations — same shape as `tools/check_bestiary.py` and `tools/check_gear.py`: it rejects a
missing required field, a field the schema does not define, a non-positive cost, and a malformed
`id`.
