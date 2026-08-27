# Wyrd — the adversary

What an opponent is made of. The ruleset ([`03-rules.md`](03-rules.md)) rolls against these values;
this document says what they are, and which rule reads each one.

Every name here is an **engine** name. What a setting calls any of it is the setting's business
([`24-authoring-a-setting.md`](24-authoring-a-setting.md)), and renames are presentation-only.

---

## 1. An adversary is thinner than a character

A character ([`10-the-character.md`](10-the-character.md)) carries Taint, Trauma, Strain, Resolve,
Dread, Fate, Luck, a career and a career history, a Loyalty, and an advancement economy. Those exist
to model a person the chronicle follows for years.

**An adversary carries none of it.** It carries what a published rule reads off it, and nothing
else. The reason is not economy of typing: every track above accrues, and a thing that accrues needs
somewhere to accrue *to*. An opponent met once and killed in a corridor has no such place, and
giving it one means running an advancement economy for a wolf.

Recorded in [ADR 0025](../adr/0025-an-adversary-is-a-thin-block.md).

**A named antagonist is not a second model.** A nemesis, a rival, a hostile companion — anyone the
chronicle follows — is a `character` entity ([`25-entities.md`](25-entities.md)) that *also* carries
the block below. One description of an opponent, reached two ways. Where a rule asks what an
opponent rolls, it reads the block, whether that block sits in a bestiary or on a person.

## 2. The block

| Field | What it is | Read by |
|---|---|---|
| **`id`** | stable, kebab-case, unique in the repo | [`25-entities.md`](25-entities.md) |
| **`name`** | what the player ever sees | the prose |
| **`baseline`** | the percentage it tests **any skill it does not list** at | §3 below |
| **`stamina_max`** | what it survives; a critical when damage takes it below 0 | [`03-rules.md`](03-rules.md) §2, [`05-criticals.md`](05-criticals.md) |
| **`armour`** | one of **none**, **light**, **modest**, **heavy** — subtracts dice | [`03-rules.md`](03-rules.md) §2 |
| **`skills`** | names the setting owns, percentages the engine understands | [`03-rules.md`](03-rules.md) §1 |
| `damage` | the dice its blows roll | [`03-rules.md`](03-rules.md) §2 |
| `damage_type` | one of the closed four; selects the critical table | [ADR 0022](../adr/0022-four-damage-types-named-for-the-wound.md) |
| `ranged` | whether it can attack at range at all | [`03-rules.md`](03-rules.md) §2 |
| `traits` | named properties, from the closed vocabulary in §5 | §5 below |
| `notes` | prose. Nothing mechanical reads it | — |

The first six are **required**. An opponent missing one is an opponent the GM has to improvise, and
improvising an opponent's numbers is the judgement call this document exists to remove.

**A field no rule reads does not belong here.** That is the test any addition has to pass, and it is
also what makes an unrecognised field an error rather than a curiosity: a setting may extend,
retune, rename or disable, and may never add a mechanism
([`24-authoring-a-setting.md`](24-authoring-a-setting.md)). An unrecognised field is how one gets
added anyway.

**`damage` and `damage_type` travel together.** An opponent that deals damage must say what kind, or
the critical rule has no table to send you to. An opponent with **no attack at all** is legal and
carries neither — something dangerous by being present, or an obstacle.

**`ranged` defaults to false**, and the default is published rather than assumed. The engagement
rule branches on it every time an opponent is not in close engagement, so the question always has an
answer.

## 3. The baseline

**An opponent tests any skill its block does not list at its `baseline`.**

A block cannot list every skill a setting declares, and an opponent is asked to resist a shove, spot
a liar or run down a fleeing party constantly. The baseline is the answer, and it is a required
field for that reason.

**It is not the untrained 10%.** That rule ([`03-rules.md`](03-rules.md) §1) is about people who
never learned a thing and have nothing to fall back on. A thing that hunts is not untrained at
noticing; it is simply not written down as noticing. Falling back to 10 would also unmake the crowd
rule from underneath — the clearing test is *ahead by 20 or more*, so against a 10 fallback a merely
competent character clears almost anything, and a bounded exception becomes the way fights resolve.

**The baseline is not a floor under a listed skill.** A skill written below the baseline stays where
it was written. The baseline answers a question about an *absent* skill; it says nothing about the
ones that are there.

## 4. A turn, and dropping

**An adversary's turn is the same turn everyone gets** — one action, from the closed list in
[`03-rules.md`](03-rules.md) §2. Attack, close, break off, ready or use, act on the fiction. The
block carries no action list of its own, because there is no action it could carry that the list
does not already hold.

**A critical is rolled for an adversary exactly as for anyone else**: damage takes it below 0
Stamina, `1d6 + points below zero` on the table for the damage type
([`05-criticals.md`](05-criticals.md)).

**The Aftermath table is not.** Aftermath is rolled once per **character or companion** who dropped
([`03-rules.md`](03-rules.md) §2), and an adversary is neither. This is the rule §2 already states
for a crowd, holding for a single opponent as well and for the same reason: Aftermath prices a
lasting consequence for someone the chronicle carries forward. What became of an opponent is the
fiction's to say.

**A named antagonist is a character**, and therefore does roll — not because it is important, but
because it is a `character` entity, which is the same test the rule already applies.

## 5. Traits

A trait is a **display name** and an **effect**, and the effect comes from a closed vocabulary:

| Effect | What it may do |
|---|---|
| `difficulty` | shift the difficulty of a named class of test, in ladder rungs |
| `damage` | add or remove damage dice on this opponent's blows |
| `damage_type` | fix the damage type of this opponent's blows |
| `stamina_max` | raise or lower maximum Stamina |
| `armour_rank` | raise or lower the armour rank by whole ranks |
| `wyrd` | widen the Ill Omen or Fair Omen band on tests against this opponent |

**Every effect names a mechanism that already exists.** That is the whole of the constraint, and it
is the line between *retune* and *add*. A setting that wants a thing which regenerates, or which is
immune to a damage type, or which acts twice a round, is asking for a mechanism — and that is an
engine change, raised as engine work, not a line in a bestiary.

The vocabulary is small on purpose. It grows by an engine change, which is the correct cost: a
mechanism added deliberately, once, is a different thing from a mechanism that arrived in a stat
block and was never noticed.

## 6. Scaling

**The block is absolute.** A bestiary entry means one thing whatever content refers to it. Scaling
happens when content is prepared, never by rewriting an entry — otherwise the same creature reads
differently in two arcs and neither reads as wrong.

What scales is the **encounter**, through the one equation in
[`03-rules.md`](03-rules.md) §7, and through nothing else. Both quantities §7 names move: how many
opponents appear, and the percentage they are run at.

## 7. What a setting declares

`setting/bestiary.yaml` holds one `creatures:` list. Each entry is one block:

```yaml
creatures:
  - id: the-hunter
    name: A named antagonist
    baseline: 35
    stamina_max: 7
    armour: modest
    skills:
      blade: 55
      tracking: 60
    damage: 1d6
    damage_type: slashing
    ranged: false
    traits:
      - name: Unhurried
        effect:
          difficulty: -10
```

Validated by `tools/check_bestiary.py`, which rejects a missing required field, an unrecognised
field, an out-of-range value, a damage type outside the closed four, a trait effect outside the
vocabulary, and a duplicated id — reporting every failure rather than the first.

A worked opponent taken through a full exchange, the crowd lookup resolved against the schema, and
one encounter scaled across the parties a chronicle has, are in
[`specs/017-adversary-model/worked-exchange.md`](../../specs/017-adversary-model/worked-exchange.md).
