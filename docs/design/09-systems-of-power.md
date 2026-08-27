# Systems of power

The schema a setting fills in to give its practitioners supernatural or extraordinary reach —
what [`24-authoring-a-setting.md`](24-authoring-a-setting.md) means when it says a setting may
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
| `intensity_tiers` | no | see below — scales cost and Ill Omen Taint by declared ambition |

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

## Intensity tiers

**`intensity_tiers` is optional, and a system of power with none declared behaves exactly as
above** — a flat cost, a difficulty the GM sets from the fiction, an unmodified `ill_omen_taint`.
Nothing about this section requires an existing declared system of power to change.

A setting that wants "I warm myself against the chill" and "I burn the entire city down" to carry
different stakes, even when both are the same system of power, declares `intensity_tiers`: a list
of named points, each with

| Field | What it means |
|---|---|
| `label` | the setting's own word for this level of ambition — free text, e.g. minor/moderate/major |
| `difficulty` | one of the six rungs [`03-rules.md`](03-rules.md) §1 already defines — a shorthand for the difficulty the GM would otherwise set fresh each time; the GM may still override it from the fiction |
| `cost_multiplier` | multiplies the system's base `strain_cost`/`resolve_cost` for an invocation declared at this tier |
| `ill_omen_taint_bonus` | adds to the system's base `ill_omen_taint` before it feeds the Taint-accrual path below |

**This closes a gap difficulty alone does not.** Difficulty only discounts *how often* an
ambitious working succeeds — it does nothing about the asymmetry of the downside, since the
declared cost is paid identically whether the working was trivial or vast. A tier's
`ill_omen_taint_bonus` is what actually ties ambition to consequence: an Ill Omen on a working
declared at the `major` tier now risks meaningfully more Taint — and a more likely transformation
roll — than an Ill Omen on the same system invoked at `minor`. Which tier an invocation is
declared at is decided the same way any other declaration specificity is — the player states it
as part of the same declaration step, subject to the GM's usual authority over plausibility; this
is not a new procedural step.

**No new resolution path.** `cost_multiplier` and `ill_omen_taint_bonus` compose with the
existing rules exactly as stated above and below — win-or-lose cost, the same Taint-accrual path
— they do not introduce a second dice mechanic, a second table, or a tier-specific consequence
chain. A tier is a modifier on the one mechanism this document already defines, consistent with
[ADR 0036](../adr/0036-one-configurable-power-mechanism.md)'s decision that a system of power is
one configurable mechanism, not a family of mechanism shapes.

## The Ill Omen consequence

**An Ill Omen on an invocation applies the declared `ill_omen_taint` through the engine's existing
Taint-accrual path** ([`03-rules.md`](03-rules.md) §4), exactly as the Bargain, Exposure, or an
Invocation already feed it. If that Taint gain crosses a threshold, a transformation-table roll
follows immediately, using the same loop [`07-transformations.md`](07-transformations.md)
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

A setting that wants ember-craft's stakes to scale with what was attempted adds tiers to the same
declaration:

```yaml
systems_of_power:
  - id: ember-craft
    name: Ember-craft
    skill: ember-craft
    strain_cost: 2
    resolve_cost: 1
    requires_training: true
    ill_omen_taint: 1
    intensity_tiers:
      - label: minor
        difficulty: average
        cost_multiplier: 1
        ill_omen_taint_bonus: 0
      - label: moderate
        difficulty: hard
        cost_multiplier: 2
        ill_omen_taint_bonus: 1
      - label: major
        difficulty: very hard
        cost_multiplier: 4
        ill_omen_taint_bonus: 3
```

Warming your hands is `minor` — resolution is identical to the untiered example above.
Burning down a city is `major`: the GM sets Very Hard rather than picking a difficulty fresh, the
roll is against `d100` exactly as before, and on resolution the character pays `2 * 4 = 8` Strain
and `1 * 4 = 4` Resolve rather than the base 2 and 1. If the natural roll's units digit is 0 (Ill
Omen), the character gains `1 + 3 = 4` Taint through the same accrual path — not the 1 Taint a
`minor` Ill Omen would cost — reflecting that an ambitious working going wrong is a worse thing to
have happen, mechanically as well as fictionally.

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
