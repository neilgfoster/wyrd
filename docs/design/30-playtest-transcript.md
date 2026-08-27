# A hand-run playtest

R3 of epic #1 ([`docs/adr/0012-the-design-reset-and-how-records-are-consolidated.md`](../adr/0012-the-design-reset-and-how-records-are-consolidated.md)
records what the reset was; this document is the proof the resulting R1 specification can be run
without a rulebook the GM is inventing on the fly). One character, created entirely by hand
against [`11-character-creation.md`](11-character-creation.md), and one exchange of combat, run
entirely by hand against [`03-rules.md`](03-rules.md) §2, [`05-criticals.md`](05-criticals.md)
and [`06-aftermath.md`](06-aftermath.md). Every roll is a real `python3` `random` draw,
seeded (`20260826`) so the run is reproducible, not a chosen-to-be-interesting sequence.

The setting data used here — the career, its skills, the Loyalties, the Drives and Misfortunes, and
the single adversary — is invented for this exercise only. It carries no setting name and answers no
question about any real setting; it exists to give the procedure something to read.

---

## 1. Character creation

Following [`11-character-creation.md`](11-character-creation.md) §1, step by step.

### Setting data assumed for this run

```yaml
careers:
  - id: wayfarer
    entry: true
    cap: 70
    skills: [tracking, blade, evasion, lockpicking, herbalism, bargaining]

loyalties: [the-road, kin]
drives: ["to never be trapped again"]
misfortunes: ["marked by a debt that cannot be repaid"]
```

### Step 1 — choose a career

**Wayfarer**, an entry career. Grants `tracking`, `blade`, `evasion`, `lockpicking`, `herbalism`,
`bargaining`, each capped at 70%.

### Step 2 — spend 8 advances inside that career

At least two skills must open (§3 of `05-character-creation.md`). Chosen spread: open three,
raise unevenly — the "working spread" shape the doc tables as `35% / 35% / 30%`:

| Advance | Spends on | Result |
|---|---|---|
| 1 | open `tracking` | 25% |
| 2 | open `blade` | 25% |
| 3 | open `evasion` | 25% |
| 4 | +5% `tracking` | 30% |
| 5 | +5% `tracking` | 35% |
| 6 | +5% `blade` | 30% |
| 7 | +5% `blade` | 35% |
| 8 | +5% `evasion` | 30% |

Eight advances spent, three skills opened. `tracking 35%`, `blade 35%`, `evasion 30%`.
`lockpicking`, `herbalism` and `bargaining` were never opened — the character is untrained (10%) at
each, per [`03-rules.md`](03-rules.md) §1.

### Step 3 — choose a Loyalty

**The Road** — a life spent moving is what this character is loyal to, over kin or a settled
place.

### Step 4 — Stamina

Set to **6**, current and maximum.

### Step 5 — Fate

`mortality: standard` → Fate **3**, current and maximum. Fortune **3**, renewed daily.

### Step 6 — the tracks

`Taint 0`, `Trauma 0`, `Strain 0`, `Resolve 0`, `Dread 0`. Nothing has happened yet.

### Step 7 — name, place, Drive, Misfortune, Bond

- **Name:** Senna Vask.
- **Place:** born in a fen-town at the edge of the map, the kind of place a road runs through and
  out of again.
- **Drive:** to never be trapped again.
- **Misfortune:** marked by a debt that cannot be repaid.
- **Bond:** her brother, Talen — still owed to the same creditor she got clear of.

### Step 8 — write the Fault Line

One sentence, combining the Drive and the Misfortune above, per the fixed gap below: **Senna's
Taint deepens whenever a way out is bought by leaving someone else in the trap she just left.** The
direction is entrapment and debt — an Exposure source that plays on abandoning someone to save
herself gains Taint one tier worse ([`03-rules.md`](03-rules.md) §4).

### The finished sheet

```yaml
id: senna-vask
role: player
career: wayfarer
skills: {tracking: 35, blade: 35, evasion: 30}
stamina: {current: 6, max: 6}
fate: {current: 3, max: 3}
fortune: {current: 3, max: 3}
taint: 0
trauma: 0
strain: 0
resolve: 0
dread: 0
loyalty: the-road
drive: "to never be trapped again"
misfortune: "marked by a debt that cannot be repaid"
fault_line: "Taint deepens whenever a way out is bought by leaving someone else in the trap she just left"
bond: {who: talen-vask, note: "brother, owed to the same creditor"}
wounds: []
```

**Nothing was rolled in this section, per [ADR 0014](../adr/0014-character-creation-is-chosen-not-rolled.md).**
Every value above is either fixed by the procedure or a choice from setting data.

---

## 2. One gap found, and fixed before continuing

Step 9 did not exist before this run. [`03-rules.md`](03-rules.md) §4 states as established fact
that "each character has a Fault Line derived at creation from their Drives and Misfortune," and
[`ADR 0031`](../adr/0031-fault-line-biases-exposure-not-the-transformation-table.md) already built a
mechanism that reads it — but [`11-character-creation.md`](11-character-creation.md)'s eight-step
procedure never produced one, and never asked for a Misfortune at all. Step 8 said "Name, a Drive, a
Bond, and where they are from" and stopped there. Run literally, creation could not produce a
character §4 already assumes exists — a judgement call the rules did not cover.

**Fixed in [`11-character-creation.md`](11-character-creation.md)**, in place, before the
transcript above continued past step 8:

- Step 8 now includes choosing a **Misfortune** alongside the Drive.
- A new **step 9** writes the Fault Line as one sentence combining the Drive and Misfortune chosen
  — a GM-and-player judgement call, explicitly not a roll or a table lookup, mirroring the judgement
  call §1 already uses to invoke a Drive.
- §4 ("what a setting must provide") now lists **Misfortunes** alongside Drives, since
  [`19-campaign.md`](19-campaign.md)'s "Seeded" Threat origin already assumed a Misfortune existed
  to seed from, and nothing declared where a setting's Misfortunes come from.

No new ADR: the mechanism the Fault Line feeds was already decided in ADR 0031, which anticipated
exactly this retune path ("a setting authoring its own Fault Line taxonomy... still lands on the same
mechanism"). This fix is the missing plumbing into creation, not a new fork of the decision ADR 0031
already made.

---

## 3. Combat: one exchange

Senna, alone, against a single adversary built to [`12-the-adversary.md`](12-the-adversary.md)'s
schema.

```yaml
creatures:
  - id: the-collector
    name: A debt-collector
    baseline: 30
    stamina_max: 6
    armour: light
    skills: {blade: 45}
    damage: 1d6
    damage_type: slashing
    ranged: false
```

**The fiction:** Senna corners the man she was told holds Talen's debt, in an alley, blade already
drawn. She started the exchange — [`03-rules.md`](03-rules.md) §2's ordinary sequencing rule, no
roll, no attribute. She acts first, and — since both combatants are already engaged and armed —
every round from here alternates her attack, then his (resolved as her defence roll, since the
opponent never rolls — [ADR 0027](../adr/0027-combat-rolls-belong-to-the-player.md)).

`effective%` for **either** roll is `clip(50 + (35 − 45), 5, 95) = 40` — the two skills never change
across the fight, so the number is fixed for both attack and defence throughout.

Every roll below is a real `d100`/`d6`/`d3` draw from Python's `random`, seeded `20260826`, drawn in
this exact order (attack roll, then its damage/armour dice only if the attack hit; defence roll,
then its damage/armour dice only if the defence failed) — the same order the fight actually needed
them in, so no die drawn here was thrown away.

### Round 1

- **Senna attacks** (eff. 40). Roll **61** — fails. No degrees (degrees only exist on a success).
  The Wyrd die is still read on a failure ([`03-rules.md`](03-rules.md) §1: success and failure
  carry the units digit independently) — units digit 1, nothing. No damage.
- **The collector attacks; Senna defends** (eff. 40). Roll **69** — fails to defend, meaning **the
  blow lands**. Units digit 9 → **Fair Omen**, but the Wyrd die belongs to the roll that was made,
  and this roll failed, so the omen reads on the failure: something also breaks Senna's way even as
  the blow lands (played as: she reads where the next blow is coming from). Damage `1d6` = **5**;
  light armour subtracts `1d3` = **1**; **4** gets through. Senna: **6 → 2** Stamina.

### Round 2

- **Senna attacks** (eff. 40). Roll **10** — succeeds. `tens(40) − tens(10) = 4 − 1 = 3` degrees.
  Units digit 0 → **Ill Omen** (something also goes wrong for Senna, played as: her blade catches
  a fold of his coat and nearly sticks). Not a telling blow (needs 6+ degrees). Damage `1d6` = **6**;
  his light armour subtracts `1d3` = **2**; **4** gets through. Collector: **6 → 2** Stamina.
- **The collector attacks; Senna defends** (eff. 40). Roll **20** — succeeds (defence holds, blow
  does not land). Degrees `4 − 2 = 2`. Units digit 0 → **Ill Omen**: something goes wrong even on a
  successful defence — played as Senna losing her footing on wet cobbles, costing her nothing
  mechanical this round but setting the alley's ground for what follows.

### Round 3

- **Senna attacks** (eff. 40). Roll **66** — fails. No damage.
- **The collector attacks; Senna defends** (eff. 40). Roll **27** — succeeds. Degrees `4 − 2 = 2`.
  No Wyrd die (units digit 7).

### Round 4

- **Senna attacks** (eff. 40). Roll **17** — succeeds. Degrees `4 − 1 = 3`. No Wyrd die. Damage
  `1d6` = **1**; armour subtracts `1d3` = **2**; minimum 1 always gets through
  ([`03-rules.md`](03-rules.md) §2) → **1** applied. Collector: **2 → 1** Stamina.
- **The collector attacks; Senna defends** (eff. 40). Roll **10** — succeeds. Degrees `4 − 1 = 3`.
  Units digit 0 → **Ill Omen** on a successful defence again — Senna's grip is slick with the first
  wound's blood; no mechanical effect this round, carried as texture for the GM's prose.

### Round 5

- **Senna attacks** (eff. 40). Roll **23** — succeeds. Degrees `4 − 2 = 2`. Damage `1d6` = **1**;
  armour subtracts `1d3` = **3**; minimum 1 gets through → **1** applied. Collector: **1 → 0**
  Stamina.
- **The collector attacks; Senna defends** (eff. 40). Roll **6** — succeeds. Degrees `4 − 0 = 4`. No
  Wyrd die.

### Round 6

- **Senna attacks** (eff. 40). Roll **28** — succeeds. Degrees `4 − 2 = 2`. Damage `1d6` = **1**;
  armour subtracts `1d3` = **1**; minimum 1 gets through → **1** applied. Collector: **0 → −1**
  Stamina — **below zero**. The fight's over move.

### The critical

Damage took the collector below 0 Stamina, so ([`03-rules.md`](03-rules.md) §2,
[`05-criticals.md`](05-criticals.md)) roll `1d6 + points below zero` on the table for the
weapon's damage type — `critical-slashing`, since a blade's wound is slashing.

`1d6` = **2**, `+ 1` (one point below zero) = **3** total. Range **2–5** on `critical-slashing`:
`slashing-glancing` — **nothing lasting**. "It opens skin and no more." The collector is out of
action, marked but not maimed.

**No Trauma is charged for this critical.** [`03-rules.md`](03-rules.md) §5 prices a critical taken
at 1 Trauma, but the collector is an adversary block, and an adversary carries none of the tracks
[`10-the-character.md`](10-the-character.md) §4 and [`12-the-adversary.md`](12-the-adversary.md)
§1 list — Trauma among them. There is no track here to charge. This was not a judgement call: §1 of
`06-the-adversary.md` already states the block carries none of a character's tracks, and Trauma is
one by name.

**The Aftermath table is not rolled.** [`12-the-adversary.md`](12-the-adversary.md) §4 is explicit:
Aftermath is rolled once per character or companion who dropped, and an adversary is neither — the
same rule the crowd section of [`03-rules.md`](03-rules.md) §2 already states. What became of the
collector — bound, questioned, sent running — is the fiction's, not a roll's.

### The fight, resolved

Senna never dropped below 0 (she ended at **2** Stamina, and recovers on the ordinary Rally/downtime
clock — [`03-rules.md`](03-rules.md) §2). The collector dropped once, took a glancing critical, and
is out of action. Six rounds, twelve rolls, no roll made outside what the rules called for, and no
step in the sequence needed the GM to invent a number.

---

## 4. Gaps found, and how each was resolved

| # | Gap | Where surfaced | Resolution |
|---|---|---|---|
| 1 | [`11-character-creation.md`](11-character-creation.md) had no step to produce the Fault Line that [`03-rules.md`](03-rules.md) §4 and [ADR 0031](../adr/0031-fault-line-biases-exposure-not-the-transformation-table.md) already assumed every character has, and never asked for a Misfortune at all. | Character creation, step 8 | Fixed in place in [`11-character-creation.md`](11-character-creation.md) — see §2 above. No new ADR: ADR 0031 already decided the mechanism this fills in. |

Nothing else forced a judgement call. Combat ran six full rounds — sequencing, an attack roll, a
defence roll, armour, a telling-blow check that came up short of its threshold three separate times,
a Wyrd die on both a hit and a clean defence, a drop below zero, a critical, and the explicit
non-roll of Aftermath for an adversary — without the GM inventing a single number the rules did not
already supply. That is the acceptance criterion this document exists to demonstrate.

---

## 5. What this does and does not prove

**It proves** the R1 specification, as it stood once the one gap above was closed, is sufficient to
run one character through creation and one exchange through to its resolution without inventing a
rule at the table.

**It does not prove** every rule in `docs/design/` is complete — only the ones this run actually
exercised: creation steps 1–8, ordinary (non-surprise, non-ranged, non-crowd) sequencing, the
player-facing attack/defence roll, armour, the telling blow (never triggered, so its threshold was
read but not crossed), a single critical, and the adversary's non-participation in Trauma and
Aftermath. Surprise, ranged attacks, crowds, breaking off, Fate spent against a death result,
Transformations, Afflictions and the advancement economy were not exercised here, and remain
untested by this document. §6 below runs a deeper, dedicated pass over ordinary resolution and
opposed tests specifically — the shape of roll this section's combat exchange only exercised in
combat's own two-sided form.

---

## 6. Resolution and opposed tests: a deeper pass

Part of #134 (the autonomous playtest epic), #147. Where §3 exercised resolution *inside* combat's
fixed two-sided shape, this section exercises the ordinary test — the shape every non-combat roll
in the game actually uses — across the difficulty ladder, declaration, assistance, untrained
attempts, and the player-facing opposed-test shape §1 describes for a non-combat contest.

Every roll below is a real `d100` draw from Python's `random`, seeded `20260827`, drawn in the
exact order presented, one call per attempt — and **no roll is drawn for an attempt already
impossible before the die is thrown** (Very Hard on an untrained or barely-trained skill, Hard
untrained), matching §3's own discipline that no die drawn here is thrown away, and none is
skipped either. **Degrees are read only on a success**, per §1's own convention (already
established in §3's combat exchange: "No degrees (degrees only exist on a success)") — a failure's
Wyrd die is still read from the same natural roll, independently.

Senna Vask (§1) again: `tracking: 35`, `blade: 35`, `evasion: 30`.

### The difficulty ladder — tracking, brief declaration

| Difficulty | Effective% | Roll | Result | Wyrd die |
|---|---|---|---|---|
| Very Hard (−40) | −5 | *(impossible — not rolled)* | — | — |
| Hard (−30) | 5 | 68 | fail | — |
| Difficult (−20) | 15 | 100 | fail | **Ill Omen** |
| Challenging (−10) | 25 | 20 | **success**, 0 degrees | **Ill Omen** |
| Average (+0) | 35 | 73 | fail | — |
| Easy (+20) | 55 | 80 | fail | **Ill Omen** |

Challenging succeeding at 0 degrees, played: Senna finds the trail again, but only just — the sign
is nearly gone. The natural 100 at Difficult confirms §1's rule needs no special case for it: "at
or under" already fails a 100 against any skill under 100, and the units digit (0) reads as an Ill
Omen exactly like any other 0, with no exception the doc would need to state.

### Declaration bonus stacking — tracking, Average difficulty

| Declaration | Effective% | Roll | Result | Wyrd die |
|---|---|---|---|---|
| Brief | 35 | 31 | **success**, 0 degrees | — |
| Specific and in character (+10) | 45 | 53 | fail | — |
| Specific *and* leveraging (+20) | 55 | 1 | **success**, 5 degrees | — |

The roll of **1** at 55% lands 5 degrees — the highest-magnitude success this pass drew — on the
best-declared attempt, which is the shape the rule is meant to reward: specificity buys a wider
margin, not a guaranteed one (the brief attempt at 35% also succeeded, just narrowly).

### Untrained attempts — the #139 table, played

| Attempting | Base | Difficulty | Declaration | Effective% | Roll | Result |
|---|---|---|---|---|---|---|
| average, brief | 10 | +0 | — | 10 | 65 | fail |
| easy, brief | 10 | +20 | — | 30 | 86 | fail |
| easy, specific and leveraging | 10 | +20 | +20 | 50 | 49 | **success**, 1 degree |
| hard | 10 | −30 | — | −20 | *(impossible — not rolled)* | — |

Matches the reworked table in #139/03-rules.md exactly: the 50% row is the same two +20 bonuses
stacking on the 10% base, and it played out as a genuine near-coin-flip success (roll 49 against
50), not a certainty.

### Assistance — blade, one helper (evasion 30% → +3)

Effective% `35 + 3 = 38`. Roll **6** — **success**, `tens(38) − tens(6) = 3 − 0 = 3` degrees. The
helper's own skill (30%, a tenth rounded down is 3, per §1's assistance table) matched the
published figure exactly.

### Player-facing opposed test — evasion vs. a baseline-40 opponent

`effective% = clip(50 + (30 − 40), 5, 95) = 40`. Roll **52** — fail: the opposed action simply
fails, no resisting-side roll, per §1's opposed-test shape. Played: Senna tries to slip past a
suspicious gatekeeper on evasion; the gatekeeper's attention holds, and she's stopped at the gate.

### The two-player-controlled-entities edge case

Not rolled — by design. §1 states this shape (a contest between the player character and a
companion, or two companions, with no NPC/opponent side) is resolved as one ordinary test on
whichever side the GM names as acting, or as two separate ordinary tests — not a special roll of
its own. Played through in the fiction (Senna and a hypothetical companion disagreeing on which
road to take at a fork) confirms the rule as written needs nothing further: the GM naming Senna as
the acting side and calling one Average tracking test (already exercised above) resolves it with no
new mechanism required.

### Findings

**No fault found.** Every attempt resolved against §1's stated formulas without a judgement call:
the natural 100 needed no special case, the assistance bonus matched its published table exactly,
the untrained table's stacked bonuses played out as the reworked #139 table describes, and the
two-player-controlled-entities edge case resolved with the ordinary-test shape §1 already names,
with nothing further to invent.

**What this pass does not prove**: extended tasks (§1's interval-based work), the Bargain (Taint
route via a failed roll), and Fortune spent to reroll, defend again, act sooner, dodge a
misfortune, or break a tie — none were exercised here and remain untested by this document.

---

## 7. Combat and harm: a deeper pass

Part of #134 (the autonomous playtest epic), #148. Where §3 ran one exchange to a survived
resolution, this pass deliberately picks a tougher single opponent so a drop is a real possibility,
then plays whatever the dice actually produce — including, this time, a drop, a critical, an
Aftermath roll, and (via a separate, explicitly-labelled sampling exercise) a Fate spend against a
death result. A crowd encounter and Stamina recovery close the pass.

Senna Vask again: `blade: 35`, `evasion: 30`, Stamina `6/6`, light armour.

```yaml
creatures:
  - id: the-bounty-hunter
    name: A professional the debt-collector called in
    baseline: 30
    stamina_max: 6
    armour: modest
    skills: {blade: 50}
    damage: 1d8
    damage_type: slashing
    ranged: false
```

Every roll below is a real `d100`/`d6`/`d8`/`d3` draw from Python's `random`, seeded `20260828`,
drawn in the exact order the fight needed them (attack roll, its damage/armour dice only on a hit;
defence roll, its damage/armour dice only on a landed blow) — the same discipline §3 and §6 both
already established.

`effective%` for Senna's attack: `clip(50 + (35 − 50), 5, 95) = 35`. For her defence:
`clip(50 + (30 − 50), 5, 95) = 30`. Both fixed for the fight, same as §3.

### The exchange

- **Round 1.** Senna attacks (eff. 35). Roll **47** — fails, Wyrd die reads nothing (units 7). The
  bounty hunter attacks; Senna defends (eff. 30). Roll **43** — **fails: the blow lands.** Wyrd die
  nothing (units 3). Damage `1d8` = **4**; light armour subtracts `1d3` = **2**; **2** gets
  through. Senna: **6 → 4**.
- **Round 2.** Senna attacks (eff. 35). Roll **59** — fails. Units digit 9 → **Fair Omen** on a
  failure (something breaks her way even as the strike goes wide — played as: she reads an opening
  for next round). Senna defends (eff. 30). Roll **86** — **blow lands**, nothing on the Wyrd die.
  Damage `1d8` = **4**; armour `1d3` = **1**; **3** through. Senna: **4 → 1**.
- **Round 3.** Senna attacks (eff. 35). Roll **99** — fails. **Fair Omen** again. Senna defends
  (eff. 30). Roll **64** — **blow lands**, nothing on the Wyrd die. Damage `1d8` = **5**; armour
  `1d3` = **2**; **3** through. Senna: **1 → −2**. She drops.

Senna never landed a hit — all three of her own attack rolls failed — and took all three of the
bounty hunter's blows through a failed defence roll each time. See **Findings** below for what
this exposed about telling blow on the defence side.

### The critical and Aftermath

Dropped by **2**. Critical: `1d6 + 2` = **5**, read on `critical-slashing`'s **2–5** row —
`slashing-glancing`, nothing lasting. It opens skin and no more; the drop itself is what actually
costs her.

Aftermath: `d100 + (5 × 2)` — roll **73** + **10** = **83**, landing in the **79–88** band:
`taken` — captured, a `thread` entity opens. Played: the bounty hunter doesn't finish her; he
delivers her to whoever is owed the debt.

### A separate sampling pass: reaching the death band, to play the Fate spend

The single Aftermath roll above landed on `taken`, not death — which is itself a real result, not
a disappointing one, but it leaves the Fate-spend mechanic (#148's own required scope) unplayed.
Rather than reroll the actual fight's outcome, a fresh, separately-seeded (`20260829`) sample of
six Aftermath rolls at `points_below = 9` (the 35%-death row from `06-aftermath.md`'s own published
table) was drawn to reach — honestly, not by discarding misses — an actual death result to play
through:

| Roll | `d100` | Total (`+45`) | Band |
|---|---|---|---|
| 1 | 78 | 123 | **death** |
| 2 | 53 | 98 | disfigured |
| 3 | 44 | 89 | disfigured |
| 4 | 85 | 130 | **death** |
| 5 | 84 | 129 | **death** |
| 6 | 9 | 54 | left-for-dead |

Three of six landed in the death band — consistent with the published 35% figure at this drop
depth. Taking roll 1 (**123**, death) to play the Fate spend: Senna's player has Fate remaining and
chooses to spend it. Per `03-rules.md` §3 and `06-aftermath.md`, the result is **re-read on the
worst row that is not death** — `99–110`, `recurring-wound`: one wound record, `recurring: true`,
effect `skill: -10`. She survives, and is not better off — the wound "wakes before every fight
after this one," exactly as the row describes, and exactly the cost `06-aftermath.md` prices for
spending Fate rather than the free pass it would otherwise read as.

### A crowd encounter

Three more of the debt-collector's hired hands close in — skill 15%, Stamina 1, no armour.
Set against Senna's blade 35%, the gap is **20**, meeting the clearing test's threshold exactly (all
three: Stamina 1 ✓, no armour ✓, gap ≥20 ✓ — all three qualify). At the start of each of Senna's
turns while she remains engaged with them, she clears one without a roll and without spending her
action; three of her turns clear all three. No dice were drawn for this — the rule is a lookup, not
a roll, and playing it through confirmed it needs none.

### Stamina recovery

Following the fight (all of it — the exchange, the drop, the crowd), Senna is at 0 (per
`03-rules.md` §2: "a combatant who dropped below 0 wakes at 0 when the fight ends"). At her next
Rally: **0 → 1**. At the following downtime: **1 → 6** (maximum), matching
[`check_recovery.py`](../../specs/014-stamina-recovery/check_recovery.py)'s own computed figures
for a starting-Stamina character with no further complication.

### Findings

**One real ambiguity found, not silently resolved.** `03-rules.md` §2 states degrees are "read
from the roll exactly as in §1" and telling blow triggers on "win by 6 or more degrees" — but §1's
own convention, already established in §3's combat exchange ("No degrees — degrees only exist on a
success"), means a **failed defence roll has no degrees to compare against 6 at all**, even though
that failure is exactly what makes the blow land. This pass hit the case directly: all three blows
Senna took arrived via a failed defence roll, and under the only textually-supported reading (no
degrees on a failure, full stop), none of them could have been a telling blow, however badly the
roll missed. `specs/018-player-facing-combat/check_conversion.py`'s own probability modelling
(`telling_rate(100 - effective_pct(...), threshold)`) suggests the *intended* mechanic does let a
telling blow land via a failed defence — treating the miss as symmetric to a virtual attack success
at the complementary skill — but nothing in `03-rules.md`'s prose tells a GM how to compute that by
hand for one specific roll. **This playtest used the conservative, textually-supported reading (no
degrees, no telling blow, on a defence failure) rather than deciding the ambiguity itself** — a
real design question, not a documentation typo, and one with a genuine balance consequence (whether
an opponent can ever land a telling blow against a purely-defending player character). Raised
separately as a follow-up issue rather than resolved inline here.

**Everything else resolved cleanly**: the critical and Aftermath rolls read their tables exactly as
published, the death-band sampling landed within a few points of the published 35% figure at three
of six, the Fate spend closed the death row exactly as `06-aftermath.md` describes, the crowd
clearing test needed no roll and no judgement call, and Stamina recovery matched
`check_recovery.py`'s own computed figures.

**What this pass does not prove**: ranged attacks, breaking off, surprise, and a mortal-blow result
(the worst row of any critical table) were not exercised here and remain untested by this document.
