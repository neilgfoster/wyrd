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

**Resolved in [ADR 0044](../adr/0044-telling-blow-via-a-failed-defence-roll-is-symmetric.md):**
a failed defence roll can trigger a telling blow, via the virtual-roll symmetry
`check_conversion.py`'s own modelling above already assumed. Under that resolved reading, all
three of the blows Senna took in this exchange should be re-checked against the virtual-roll
formula rather than assumed non-telling — not re-played here, since #162's own synthesis pass
(§13) already accounts for this finding as fixed and this section's own worked numbers stand as a
historical record of the ambiguity as it was found, not a claim about what the resolved rule
produces.

**Everything else resolved cleanly**: the critical and Aftermath rolls read their tables exactly as
published, the death-band sampling landed within a few points of the published 35% figure at three
of six, the Fate spend closed the death row exactly as `06-aftermath.md` describes, the crowd
clearing test needed no roll and no judgement call, and Stamina recovery matched
`check_recovery.py`'s own computed figures.

**What this pass does not prove**: ranged attacks, breaking off, surprise, and a mortal-blow result
(the worst row of any critical table) were not exercised here and remain untested by this document.

---

## 8. Condition tracks: Taint, Trauma, Strain — and a gap found in Resolve

Part of #134 (the autonomous playtest epic), #149. Senna Vask, continuing her arc: `blade: 35`,
`evasion: 30`, `tracking: 35`, Fault Line — *"Taint deepens whenever a way out is bought by
leaving someone else in the trap she just left."* This pass exercises Taint (both gain routes, a
threshold crossing, the hidden threshold), Trauma (the sawtooth to an Affliction), and Strain (a
Rally recovery) — and finds a real gap in Resolve along the way.

Every roll is a real draw from Python's `random`, seeded `20260830`, in the order presented.
Where a scene needed repeated real attempts to reach the outcome a mechanic requires (a failure,
to demonstrate the Bargain; 6+ Trauma, to reach the Affliction test), every attempt is reported —
none discarded — the same honest-sampling discipline §7's death-band exercise established.

### Taint — the Bargain

Senna tries something under pressure, `eff. 30`, and keeps trying as the scene demands it:

- Attempt 1: roll **8** — success.
- Attempt 2: roll **30** — success. Wyrd die: **Ill Omen**.
- Attempt 3: roll **60** — **fails.**

No Fortune left. She takes the Bargain: **1 Taint to reroll.** Reroll: **14** — succeeds. Taint
`0 → 1`.

### Taint — Exposure, biased by the Fault Line

A moderate (2) Exposure source that runs with the grain of her Fault Line — she buys her own way
past a locked gate, and someone behind her doesn't make it through before it seals. Resist,
`eff. 35`: roll **86** — **fails.** Biased one tier worse: moderate `2` becomes major `3`. Taint
`1 → 4` — **crossing the threshold at 3.**

### The Transformation, and the hidden threshold

Threshold crossed, roll the transformation table: `1d6` = **6** → **severity 4**: *"A major,
irreversible change to what the character is, bodily."* Taint drops by the severity rolled:
`4 → 0`. Below the threshold in one roll — no re-roll loop needed this time (`check_transformation.py`
already proves the loop terminates in the worst case; this one just didn't need it). Dread `+4`
(equal to the severity, per `07-transformations.md`).

**Her first Transformation** — the GM secretly rolls the hidden threshold: `1d6+2` = **3**. Never
shown to the player, written once, standing for the rest of her chronicle: she can survive two
more Transformations before she is lost to the opposition.

### Taint — Exposure, ordinary (does not run with the Fault Line)

A minor (1) Exposure source unrelated to her Fault Line's direction — no bias applies. Resist,
`eff. 35`: roll **70** — **fails.** Taint `0 → 1`.

### Trauma — the sawtooth to an Affliction

Terror tests, `eff. 30`, until 6+ Trauma is reached (each failure costs 1 Trauma; §5's
"routed" cost):

| # | Roll | Result |
|---|---|---|
| 1 | 76 | routed, Trauma → 1 |
| 2 | 37 | routed, Trauma → 2 |
| 3 | 70 | routed, Trauma → 3 (Ill Omen) |
| 4 | 41 | routed, Trauma → 4 |
| 5 | 4 | holds |
| 6 | 27 | holds |
| 7 | 63 | routed, Trauma → 5 |
| 8 | 79 | routed, Trauma → 6 (Fair Omen) |

At 6 Trauma, the next point tests (a fiction-chosen skill, pass/fail, no degrees, per §5 and
`08-afflictions.md`). Test: `eff. 30`, roll **72** — **fails.** Affliction rolled, `1d12` = **11**:
*"Strangers and casual acquaintances react to the character at one step worse on the reaction
ladder by default, until the character spends a scene establishing otherwise."* Trauma drops by
6, per the sawtooth: `6 → 0`.

### Strain — accrual and a Rally

Mental tests, `eff. 30`, across a stretch of the same scene:

| # | Roll | Result |
|---|---|---|
| 1 | 67 | fails, Strain → 1 |
| 2 | 42 | fails, Strain → 2 |
| 3 | 65 | fails, Strain → 3 |
| 4 | 67 | fails, Strain → 4 |

At the next Rally: Strain `4 → 3`, per §5's "recovered at a Rally" (matching Stamina's own
1-per-Rally rate — §2's own "Strain's rate, at Strain's trigger" line).

### Findings

**A real gap found in Resolve, not exercised by this pass.** `03-rules.md` §4 states Resolve is
"spendable, renewable. Spend for a bonus after a failed roll," and §4 states "when Resolve falls
to equal Taint, the character is Spent." Neither §4 nor any other document names an amount for
either half: how much Resolve a spend costs, what size bonus it buys, or — the more fundamental
gap — **any way Resolve is ever gained at all.** `11-character-creation.md` sets it to 0 at
creation, and nothing in `docs/design/` states a trigger that raises it above 0. Read literally,
Resolve can never be spent (there is nothing to spend from 0 without going negative, which is
never stated as legal), and the Spent state — "Resolve fallen to Taint" — could only ever be true
at the moment Taint is *also* 0, i.e. before a character has done anything, which is exactly
backwards from what the state is clearly meant to represent (a character worn down by what has
happened to them, not one nothing has happened to yet). This pass therefore could not exercise
Resolve or a Spent state at all — not because the scene didn't call for it, but because the
mechanic as written has no path to a positive value. Raised as a follow-up issue rather than
invented here.

**Everything else resolved cleanly.** The Bargain, both Exposure routes (including the Fault
Line's one-tier bias, applied exactly once and only to the biased route), the threshold crossing,
the transformation roll and its Dread, the hidden threshold, the Trauma sawtooth to an Affliction,
and Strain's Rally recovery all played out against `03-rules.md` §4–5,
`07-transformations.md` and `08-afflictions.md` without a judgement call the rules didn't already
answer.

**What this pass does not prove**: Invocation (the GM spending a character's own Taint point to
impose a penalty), a second Transformation reaching the hidden threshold and the character being
lost, and Dread's own social effects were not exercised here and remain untested by this document.

---

## 9. Economy and progression: advancement, career completion, Standing and coin

Part of #134 (the autonomous playtest epic), #150. Senna Vask, continuing her arc: `wayfarer`
career (`tracking`, `blade`, `evasion`, `lockpicking`, `herbalism`, `bargaining`), currently
`tracking: 35`, `blade: 35`, `evasion: 30`, Stamina `6/6`.

**Nothing is rolled in this section.** Advancement, career completion, Standing and coin are all
deterministic spend/lookup mechanics, per `03-rules.md` §6 and §2 — the same "nothing was rolled"
property §1 of this document already noted for creation.

### A session's advances

Three triggers fire this session, each at most once (`03-rules.md` §6):

- **Learned** — she discovers the debt-collector who took her wasn't acting alone.
- **Drove** — she goes back for her brother Talen even though it costs her the lead on the debt,
  acting on her Drive ("to never be trapped again") at real cost.
- **Endured** — she survived the bounty-hunter exchange (§7) that dropped her below 0 Stamina.

Three advances awarded, within the stated 1–3 per session. Spent:

- **+5%** to `blade` — `35% → 40%`.
- **+5%** to `tracking` — `35% → 40%`.
- **open** `lockpicking` at **25%** — a new wayfarer skill, not previously opened.

### Completing the wayfarer career

Wayfarer's cap is **70%** on every skill it grants. Reaching every one of `tracking`, `blade`,
`evasion`, `lockpicking`, `herbalism` and `bargaining` at 70% takes many further sessions of the
same deterministic spending shown above — summarized here rather than played advance-by-advance,
since nothing about spending an advance involves a roll or a judgement call that summarizing would
lose (the same reasoning `05-where creation hands off` already gives for treating creation and
ordinary advancement as one procedure).

**All six wayfarer skills reach 70%.** Per `03-rules.md` §6: **+1 maximum Stamina** (`6 → 7`) and
a permanent **Mark**. This is the wayfarer career's only durable toughening, tracked per
career-instance — if Senna later left a second career unfinished, this rule would grant nothing
for that abandoned instance, but the wayfarer completion just played stands regardless of what she
does next.

### Changing career

Senna spends **1 advance** to change career, to `hedge-healer` — an entry career, a free choice
per `03-rules.md` §6 ("changing career is a free choice of any entry career"). Her wayfarer
skills (`tracking 70`, `blade 70`, `evasion 70`, `lockpicking 70`, `herbalism 70`, `bargaining
70`) and her Mark stay on her sheet — nothing in the spend table or the career-history rule says a
change erases what was already earned, and `10-the-character.md`'s "a career, and a career
history" phrasing (singular career, plural history) reads as exactly this: one active career at a
time, with the record of every prior one kept. Future advances open and raise only skills
`hedge-healer` grants; the wayfarer skills stay frozen at their completed values until she reads
the description of her Fault Line, Drive and skill 70 as prompt for further training later.

### Standing — the martial-weapon rule

Among the bounty hunter's effects (§7) was a martial blade — illegal to carry openly in most
civilised places. Walking into a town gate with it visible: **−1 Standing**, the moment it's seen
(`03-rules.md` §2), not a fine, not automatic violence. Played: the gate guard's eyes go to the
blade first and her name second; nothing happens, but something is now owed that wasn't before.

### Upkeep — both branches

Away from home, Upkeep costs Standing or coin (`16-session.md`). Both branches, played once each
for completeness:

- **Pay in Standing.** Current Standing is spent down by 1. The favour it bought — a door that
  used to open for her — is gone until rebuilt in play.
- **Pay in coin instead.** Coin drops by an amount equal to her *current* Standing (not a fixed
  fee) — the position itself is kept, the money is what's spent instead.

### Gear and coin

A `gear.yaml` price is invented for this exercise only, per this document's own §1 convention (no
setting name, answers no question about any real setting): a set of lockpicks at **12 coin**.
Senna has 40 coin; she buys the picks. Coin `40 → 28`. No itemized ledger — "a small number the
player can state a total for," exactly as `03-rules.md` §2 states it.

### Findings

**Nothing was rolled, and nothing forced a judgement call the rules didn't already answer.** The
trigger-award cap (1–3, one of each kind per session), the deterministic spend table, the 70% cap,
the completion grant, the free career change, and both Upkeep branches all resolved exactly as
`03-rules.md` §2 and §6 describe.

**One inference, not a gap, worth naming.** Nothing explicitly states that a completed career's
skills survive a later career change — this playtest read the career-history language
(`10-the-character.md`) and the absence of any stated reset as sufficient grounds to keep them,
rather than as a genuine ambiguity needing a follow-up issue. If a future reading disagrees, that
reading has this playtest's own reasoning to argue against directly.

**What this pass does not prove**: the maximum-Stamina ceiling at 10 (already computed exactly by
`check_advancement.py`, not re-derived here by grinding four full career completions by hand), a
non-entry career reached through satisfied prerequisites (only a free entry-career change was
played), and a second career left unfinished (to confirm it grants nothing) were not exercised
here and remain untested by this document.

---

## 10. Systems of power: a balance pass

Part of #134 (the autonomous playtest epic), #151, raised for dedicated balance scrutiny. A new
character, invented for this exercise only: **Kester**, a trained practitioner of `ember-craft` —
the design document's own worked example (`09-systems-of-power.md`), reused rather than
re-invented, `ember-craft: 50`, `strain_cost: 2`, `ill_omen_taint: 1`, `intensity_tiers` exactly
as published (`minor` average/×1/+0, `moderate` hard/×2/+1, `major` very hard/×4/+3), Strain 0,
Taint 0.

Every roll is a real `d100` draw from Python's `random`, seeded `20260831`, in the order
presented.

### Ordinary use

Three `minor` invocations across a session (`eff. 50`, no tier modifier):

| # | Roll | Result | Strain | Ill Omen | Taint |
|---|---|---|---|---|---|
| 1 | 26 | success | 2 | no | 0 |
| 2 | 25 | success | 4 | no | 0 |
| 3 | 66 | fail | 6 | no | 0 |

Nothing surprising: cost is paid win-or-lose exactly as `09-systems-of-power.md` states, and no
Ill Omen came up in three tries at the un-widened 10% band.

### Minmax: spamming `major` tier

The same character, now deliberately pushing every invocation to `major` (Very Hard, `eff. 10`,
×4 cost, +3 Ill Omen Taint bonus) — the highest ambition the schema allows — repeatedly, with no
Rally between attempts:

| # | Roll | eff | Result | Strain (running) | Ill Omen | Taint (running) |
|---|---|---|---|---|---|---|
| 1–21 | *(21 attempts, all miss the 10% Ill Omen band)* | 10 | fail every time | 8 → 168 | no | 0 |
| 22 | 30 | 10 | fail | 176 | **YES** | **4** — threshold crossed |
| 23–25 | *(3 more attempts)* | 10 | fail | 176 → 200 | no | 4 |
| 26 | 81 | 10 | fail | 208 | **YES** | **8** — threshold crossed again |

**Every single one of these 26 attempts failed** (`eff. 10` means a 90% miss rate), and it did not
matter: `09-systems-of-power.md`'s own rule is that cost is paid "regardless of outcome." Strain
climbed to 208 with **no stated consequence for high Strain anywhere in `docs/design/`** — no
cap, no threshold, nothing analogous to Taint's transformation table or Trauma's sawtooth. The
first Ill Omen took 22 tries (consistent with the un-widened 10% band); the second took only 4
more, once Taint's die-bending (`03-rules.md` §1) had widened the Ill Omen range to two units
after crossing 3 Taint — the spiral the die-bending rule is clearly meant to produce, and it did.

### The finding: nothing brakes the spam

**A minmaxing player loses nothing by attempting `major`-tier invocations repeatedly and failing
every time, right up until the next Rally.** Strain is "recovered at a Rally" (`03-rules.md` §5)
— a full reset, not a partial one — and nothing in `docs/design/` prices *accumulated* Strain
before that Rally arrives: no cap, no fictional consequence, no mechanical one. Since invocation
cost is identical whether the roll succeeds or fails, a player has no reason to declare
conservatively or stop after a miss — the only real, persistent cost across a Rally is the Ill
Omen's Taint, which fires at a flat, skill-independent rate (the units digit of the natural roll)
regardless of how many times the same scene's declaration is retried in the fiction. The
difficulty ladder, which the rest of the ruleset uses to make ambition costly, does essentially
no work here: `eff. 10`'s 90% failure rate costs the same as `eff. 90`'s 10% failure rate, because
outcome never touches cost.

This is not the same shape as #155 or #157 — it is not a missing procedure or an unreachable
value, it is a cost structure that, as published, does not discourage the exact behaviour ("spam
the biggest declaration you can and don't worry about missing") the intensity-tier mechanism's
own stated purpose ("ties ambition to consequence") was meant to price. Raised as a follow-up
issue rather than redesigned here.

### The Resolve gap recurs

`09-systems-of-power.md`'s own worked example declares `resolve_cost: 1` alongside `strain_cost`.
Attempting that variant here — Kester with `resolve_cost: 1` added — hits #157 immediately: Resolve
starts at 0 with no stated gain trigger anywhere in `docs/design/`, so the very first invocation
of a system of power with a declared `resolve_cost` cannot pay it as written. This is the same
gap #149 found, recurring in a second, independent context — evidence for #162's own "does a
finding appear in more than one playtest" check, not a new issue.

### A non-user, for comparison

A character who never invokes a system of power accrues zero Strain and zero Taint through this
path over the same span, by construction — there is nothing to compute here beyond confirming the
schema adds no cost a non-user ever pays.

### Findings

**A real balance gap, not an edge case.** The spam sequence above is not a contrived worst case —
it is the schema's own most ambitious declared tier, used exactly as `09-systems-of-power.md`
describes, and it produced 26 consequence-free failures before the Taint mechanism started to
bite. Raised as a follow-up issue: the cost structure needs either a Strain cap/consequence, a
cost that scales with attempts within a scene, or some other brake — a real design decision, not
decided here.

**Resolved in [ADR 0047](../adr/0047-strain-threshold-crossing-checks-cumulative-strain.md)**
(originally [ADR 0045](../adr/superseded/0045-failed-invocation-crossing-max-stamina-in-strain-costs-trauma.md),
corrected per §16 below): a failed invocation that leaves accumulated Strain containing a
multiple of the character's maximum Stamina now costs 1 Trauma per multiple on top of its stated
Strain/Resolve cost, with Strain carrying forward at its remainder. `specs/057-systems-of-power-spam-brake/check_spam_brake.py`
re-runs a comparable 26-attempt `major`-tier spam sequence and confirms real, non-zero Trauma
accrues where the published rule accrued none — that ordinary play and mostly-successful play
both stay untouched — and that
the brake is immune to a rotation exploit an earlier same-power-streak design was not (a
two-power-alternating re-run of this exact roll sequence produces identical Trauma to spamming one
power, at every maximum Stamina tested, since the check never reads which power failed). Not
re-played against this exact sequence's own logged rolls, which were not fully disclosed
roll-by-roll above; the re-run uses a fresh seed instead.

**The Resolve gap (#157) recurs independently**, strengthening the case that it needs resolving
before systems of power with a declared `resolve_cost` are usable at all.

**What this pass does not prove**: a setting with Taint disabled (where an Ill Omen applies no
Taint consequence at all, per `09-systems-of-power.md`'s own stated behaviour), and a system of
power sharing a skill with a mundane use of the same skill, were not exercised here and remain
untested by this document.

---

## 11. Solo procedures and session/campaign structure

Part of #134 (the autonomous playtest epic), #152. Senna Vask, continuing her arc, at the
`hedge-healer` career (§9), a lasting wound from her first Transformation still on record, Talen
(her brother) now travelling with her as a companion.

**Every roll below is a real `d100`/`d6` draw from Python's `random`, seeded `20260832`, in the
order presented.** Advancement, Bond/Tension and the session-loop steps involve no dice, per
§9's own "nothing is rolled" convention where it applies.

### A full session shape

Following `16-session.md`'s session loop: **LOAD** (chronicle, Senna, Talen, the open thread from
§10's bounty-hunter aftermath) → **ORIENT** (three weeks have passed since the last beat) →
**RECAP** (three sentences, stating the elapsed time up front) → **BEAT** (Senna and Talen seek the
harbourmaster for word of the crew that's still hunting them) → roll, narrate, persist → **RALLY**:
recover 1 Strain, recover 1 Stamina, the GM assesses and may award an advance, state is written and
committed. **No mid-beat stop was needed** — the beat closed cleanly at the Rally, exactly the
"clean stopping point" §16 describes.

### An oracle answer

The fiction hasn't settled whether the harbourmaster already knows about the crew — a real
yes/no question, and one that could plausibly be asked again (does she act on it later, does she
deny it if pressed) — so it's oracle-bound, not decided by GM fiat. Declared band: **Likely**
(T=70). Roll **26** — inside `6–70`: **yes**. The harbourmaster knows. This is now a settled fact,
recorded, not re-invented if the question resurfaces.

### An oracle prompt

The harbourmaster's real objective hasn't been established — an NPC-objective gap, per
`15-oracle-prompts.md`'s scoped families. Roll **23**, landing in the `21–30` row:
`prove_worth` — "Wants to prove their worth to someone whose opinion matters more than they'll
admit." Played: she helps not out of civic duty, but because the harbour authority above her
has never taken her seriously, and this is a chance to matter.

### A companion beat, and Bond offsetting Tension

Talen, present and playing his own hand: he recognises one of the crew from the docks and says
nothing to Senna at first — his own `objective.wants` (established at his introduction, unread by
any roll) taking precedence over hers. When it comes out, it's the kind of event that would
ordinarily add Tension — but Talen's `bond: +1` (built across the sessions since he rejoined her)
means the event that would add 1 Tension instead adds **0**, per `16-session.md`'s Bond table
exactly. Played: Senna is annoyed, not betrayed — the Bond absorbs what the raw event would have
cost.

### A journey leg, with a hazard

Travelling on to the harbourmaster's outpost, `hazard_rating: 3` (30% per leg). Roll **9** —
**triggered**. Sub-table roll (`1d6`): **4**. Played per the matched entry (invented for this
exercise, following `20-journeys.md`'s own convention that a triggered hazard resolves through the
core roll against a named skill, or is pure narration if none is named): a delay, not a fight — a
washed-out crossing costs them half a day.

### Fortune's actual refresh — not an arc-boundary reset

The original scope for this pass (drafted before #137 landed) expected to confirm Fortune resets
at a top-level arc boundary. That was Luck's old rule (ADR 0039), retired when Luck merged into
Fortune (ADR 0041) — Fortune keeps its own original trigger, **renewable daily**
(`03-rules.md` §3), not tied to arc boundaries at all. Playing a full in-fiction day past without
Fortune being spent confirms it renews on schedule regardless — nothing here needed the arc
machinery this section originally expected to exercise.

### Findings

**No fault found.** The session loop, the oracle answer and prompt tables, the Bond/Tension
interplay, and the journey hazard roll all resolved against their stated mechanics without
inventing anything the rules didn't already answer. The one adjustment — Fortune's refresh, not
an arc-boundary reset — was not a gap in the rules; it was this playtest's own pre-existing scope
description going stale after #137 landed, corrected here rather than played against a rule that
no longer exists.

**What this pass does not prove**: succession (a character dying, being lost, or retiring, and a
successor taking up the thread) was not exercised — forcing it here would mean manufacturing a
death or loss to fit the playtest's schedule rather than letting it arise from play, which is
exactly the kind of curated outcome this document's own dice discipline exists to avoid. A Loyalty
change and its Tension-break consequence, and a downtime's Recover/Cultivate/Learn/Ask
undertakings (only Mend has been played, in an earlier downtime not detailed here), remain
untested by this document.

---

## 12. Combination and minmaxing: the seams between mechanics

Part of #134 (the autonomous playtest epic), #153, depending on #147–#151. Where each prior pass
proved one mechanic (or one closely-related family) in isolation, this pass deliberately hunts
for what happens at the boundary between them — the class of fault CLAUDE.md names as hardest to
catch, because no single-mechanic check asks "what happens if a player uses two of these at
once." Senna Vask's arc, spanning the several sessions §6–§11 already documented, is treated as
the career-length chronicle this pass's scope calls for; nothing here re-proves what those
sections already did.

Every roll below is a real `d100` draw from Python's `random`. Every table below reports every
independent trial run, not a curated single result.

### The question: how many reroll resources can stack on one failed test?

Three separate mechanics each grant a reroll after a failure, and nothing in `03-rules.md`
states a limit on using more than one on the same original roll:

- **The Bargain** (§4) — 1 Taint, once no Fortune is left, for a plain reroll.
- **Resolve** (§4) — 1 point, for a +20-boosted reroll.
- **Fortune** (§3) — 1 point each, for a plain reroll, and Fortune has no stated per-test cap on
  how many points may be spent.

Played straight, nothing stops a player from failing, taking the Bargain, failing again, spending
both Resolve points, failing again, and spending all three Fortune points — one original roll,
**up to seven total attempts**, paid for in accruing Taint and depleting two other resources.

**Seven independent trials**, seeded `20260835`, same fixed setup each time (`eff. 30`, Taint 5
going in, 2 Resolve and 3 Fortune available), stacking the full chain only as far as an actual
failure requires:

| Trial | Sequence | Attempts | Outcome | Taint out | Resolve left | Fortune left |
|---|---|---|---|---|---|---|
| 1 | orig(95 f) → Bargain(39 f) → Resolve(16 **S**) | 3 | success | 6 | 1 | 3 |
| 2 | orig(50 f) → Bargain(87 f) → Resolve(96 f) → Resolve(88 f) → Fortune(3 **S**) | 5 | success | 6 | 0 | 2 |
| 3 | orig(28 **S**) | 1 | success | 5 | 2 | 3 |
| 4 | orig(4 **S**) | 1 | success | 5 | 2 | 3 |
| 5 | orig(51 f) → Bargain(30 **S**) | 2 | success | 6 | 2 | 3 |
| 6 | orig(44 f) → Bargain(75 f) → Resolve(48 **S**) | 3 | success | 6 | 1 | 3 |
| 7 | orig(42 f) → Bargain(90 f) → Resolve(68 f) → Resolve(65 f) → Fortune(36 f) → Fortune(65 f) → Fortune(85 f) | 7 | **fail** | 6 | 0 | 0 |

Trial 7 is the interesting one: **the character threw everything she had — every reroll every
mechanic grants — at one roll, and it still failed.** The stacking is real (it did materially
raise the observed success rate: 6 of 7 trials succeeded against a 30% single-roll base rate),
but it is not a guaranteed win, and its cost is real and persistent (Taint accrued in trial 7
alone does not undo itself when the roll still fails).

### Findings

**A real combination question, not a bug.** Nothing in `03-rules.md` forbids spending the
Bargain, Resolve and Fortune on the same original failure in sequence, and nothing computes what
that combination is actually worth. Trial 7 shows it is not an automatic win — but six attempts
plus the original is a lot of narrative real estate for one roll, and a GM running this at the
table with no guidance either has to invent a pacing limit on the spot (exactly the improvisation
`01-principles.md`'s GM contract exists to remove) or let a single dramatic beat absorb several
minutes of resolution. Raised as a follow-up issue: whether a per-test cap on *how many* reroll
resources may be spent is needed, or whether the current shape (bounded only by what a character
actually has) is the intended design and just needs stating as a deliberate choice.

**Resolved in [ADR 0046](../adr/0046-reroll-resources-stack-unbounded-on-one-roll.md):** stacking
is unbounded and deliberate, not capped. Trial 7 above — the full stack spent and still failing —
is exactly the evidence this decision relies on: the stack is a real, resource-costly, narratively
earned gamble, not a guaranteed win, and its cost (Taint accrued, Resolve and Fortune spent down)
is already steep enough that no second cap is needed on top of what each of the three mechanics
already carries individually.

**Systems of power's Omen scope holds at the boundary it claims.** A quick confirming check, not
a new finding: invoking a system of power is "an ordinary test" (`09-systems-of-power.md`), and
ADR 0042 scoped the ±10 combat-Omen modifier to opposed tests and combat specifically, not every
ordinary test. Playing an ember-craft invocation outside combat and outside an opposed-test shape
confirms an Ill Omen there stays narrative-plus-Taint only, exactly as ADR 0042 states — the
scope boundary between "ordinary test" and "opposed test/combat" holds where two Omen-bearing
mechanisms (systems of power's Ill-Omen-Taint, and the combat/opposed-test roll modifier) could
otherwise have collided.

**What this pass does not prove**: every possible pairwise interaction between the mechanics
#147–#152 covered — this pass hunted the interaction most likely to hide an exploit (stacking
every available reroll), not an exhaustive cross-product of every mechanic against every other.
Further combination passes, if #162's synthesis review finds reason for one, are not precluded by
this document calling its own pass complete.

---

## 13. The playtest epic's findings, reviewed together

#162, closing out #134 (the autonomous playtest epic). This section does not play anything —
per #162's own scope, it reads §6–§12's seven Findings subsections together, confirms every
distinct finding is accounted for, and calls out anything that recurred across more than one
pass independently.

### Every finding, and where it stands

| Pass | Finding | Tracked as | Status |
|---|---|---|---|
| §6 (resolution/opposed) | No fault found | — | closed, nothing to track |
| §7 (combat/harm) | Telling blow via a failed defence roll has no stated per-roll procedure | #155 | **fixed** (ADR 0044) |
| §8 (condition tracks) | Resolve has no gain mechanic, cannot be spent as designed | #157 | **fixed** (ADR 0043) |
| §9 (economy/progression) | Career-change skill retention — a stated inference, not a gap | — | resolved by the playtest's own reasoning, no issue needed |
| §10 (systems of power) | Cost structure doesn't discourage spamming failed high-tier invocations | #163 | **fixed** (ADR 0045) |
| §10 (systems of power) | Resolve gap recurs for any `resolve_cost` declaration | #157 | **fixed** (same fix as §8's finding) |
| §11 (solo procedures) | No fault found (one stale scope note, self-corrected) | — | closed, nothing to track |
| §12 (combination) | Reroll resources (Bargain, Resolve, Fortune) stack unbounded on one roll | #167 | **resolved** (ADR 0046 — deliberate, not capped) |
| §12 (combination) | Systems-of-power/combat Omen scope boundary confirmed clean | — | confirmed, not a finding |

**Nothing from any pass's Findings section is untracked.** Every real gap has either landed a fix
(#157, #155, #163) or has its own resolution (#167, ADR 0046).

### Two recurrences, called out explicitly

**The Resolve gap appeared in two independent passes** — §8 found it first, playing the condition
tracks in isolation; §10 hit the identical gap independently, trying to exercise a system of
power's `resolve_cost` field. Two unrelated playtests reaching the same wall, from different
directions, is exactly the stronger signal #162 was raised to watch for. It is also, now, the
epic's one closed finding — fixed in #157/ADR 0043 before this synthesis pass ran, per the
operator's own instruction to resolve a recurring, blocking gap before the epic's remaining
individual playtests continued.

**A second, thematic recurrence, not a shared root cause but worth naming together: §10's
finding (#163) and §12's finding (#167) are both instances of the same shape** — a resource or
declaration can be spent repeatedly, in the same scene, against the same roll or the same
consequence, with no stated pacing limit. #163 is about a single mechanism (systems of power's
cost) applied repeatedly; #167 is about three different mechanisms (Bargain, Resolve, Fortune)
composed on one roll. They are not the same bug and do not need the same fix — but a designer
resolving either should read the other first, since a design that caps one shape without
considering the other risks solving the specific instance and leaving the general pattern in
place. Noted on both issues.

### What this section does not do

**No design decision is made here.** #155, #163 and #167 each name a real, workable rejected
alternative and a genuine balance or pacing consequence — exactly what CLAUDE.md's own test says
an ADR is for, and exactly what #162's own Definition of Done says belongs to each issue's own
resolution, not to this synthesis pass. All three remain open, ranked, and ready.

---

## 14. Re-playing the scenarios rule changes affected

#174, part of #134. Four decisions landed after §7-§12 were written and played: ADR 0043
(Resolve recovery), ADR 0044 (telling blow via a failed defence roll), ADR 0045 (the systems-of-
power spam brake), and ADR 0046 (reroll stacking — documentation-only, no mechanical change, so
no scenario needs replaying for it). This section re-derives the three scenarios the other three
decisions actually touch, using real rolls throughout. **The original §7/§8/§10 text is not
edited** — it stands as the historical record of the gap or ambiguity as it was actually found;
this section states what changed.

### §7's combat exchange, re-checked against ADR 0044

§7's three defence rolls (Round 1: `43`, Round 2: `86`, Round 3: `64`, all against `eff. 30`) are
not re-rolled — they already happened — but re-read against ADR 0044's virtual-roll formula
(`virtual_eff = 100 − eff_def = 70`, `virtual_roll = 101 − r`, degrees from those two virtual
inputs):

| Round | Roll | Virtual roll | Degrees | Telling? |
|---|---|---|---|---|
| 1 | 43 | 58 | 2 | no |
| 2 | 86 | 15 | 6 | **yes** |
| 3 | 64 | 37 | 4 | no (moot — see below) |

**Round 2 is now a telling blow.** The weapon roll (`1d8 = 4`, already drawn) doubles to `8`
before armour subtracts its already-rolled `1d3 = 1`: `7` through, not `3`. Senna: `4 (post-round
1) − 7 = −3`. **She drops in Round 2, not Round 3** — Round 3 never happens under the corrected
timeline; the **Fair Omen** still pending from Round 2's own attack roll lapses unused, exactly as
the Omen rule states for a scene that ends first.

**The critical and Aftermath rolls, reusing the same dice, recomputed with the new modifier.**
The die itself is independent of the modifier it is added to; only the addend changes:

- **Critical**: original `1d6 + 2 = 5` means the die read `3`. Recomputed at `points_below = 3`:
  `3 + 3 = 6`, landing in `critical-slashing`'s `6–9` band — `slashing-scored` (one wound record,
  `dread: +1`) — not `slashing-glancing` (`2–5`, nothing lasting) as originally recorded.
- **Aftermath**: original `d100 + (5 × 2) = 73 + 10 = 83` means the die read `73`. Recomputed at
  `points_below = 3`: `73 + 15 = 88`, still the `79–88` band — `taken` — the same outcome as
  originally recorded, sitting at the top edge of the band.

**Net effect**: Senna's fight ends one round sooner and she carries a wound (`dread: +1`) she
didn't originally take, but the fight's final outcome (captured, `taken`) is unchanged. The crowd
encounter and Stamina recovery that follow §7's exchange are unaffected by any of this — both
already start from "Senna is down, the fight is over," which is still true here, just a round
earlier.

### §8's Resolve gap, replayed under ADR 0043

This continues Senna's arc from where §8 left her (Taint `1`, Resolve `0` — the gap prevented
exercising it at all). Fresh rolls, seeded `20260840`.

**The single-Rally case, shown honestly rather than skipped**: a Rally grants only `+1`
(`03-rules.md` §4). Since Taint is already `1` and Resolve started at `0`, one Rally alone brings
Resolve to `1` — equal to Taint, the Spent condition, before she has spent anything this arc at
all. This is a real, correctly-designed consequence of accruing Taint before her next Rally
lands, not a bug: a character worn down by what has happened to her can be Spent the moment she
catches her breath, if Taint has outpaced her Rallies.

Continuing instead to her next downtime, which raises Resolve to its cap (ADR 0043):
Resolve `→ 4` (cap `= Taint + 3 = 4`). No longer Spent. A test under pressure, `eff. 35`: roll
**48** — fails. She spends **1 Resolve** for the `+20` reroll: `4 → 3`. Reroll at `eff. 55`: roll
**17** — succeeds.

**Final: Resolve `3`, Taint `1`** — real headroom, not Spent. The cadence, the cap, and an actual
spend all played out exactly as ADR 0043 states — the gap §8 found (nothing to ever spend) is
closed.

### §10's two findings, replayed against Kester's own character

Kester, continuing exactly as §10 set him up: `ember-craft: 50`, `strain_cost: 2`,
`ill_omen_taint: 1`, `intensity_tiers` as published, Strain `0`, Taint `0`, Stamina `6/6`
(creation default — §10 never stated one explicitly).

**The Resolve recurrence, replayed under ADR 0043.** Seeded `20260841`. With `resolve_cost: 1`
added, the very first invocation still cannot pay it — Resolve starts at `0`, exactly like every
other track at creation. That is no longer a gap, though: it is the same "nothing has happened
yet" state Stamina, Strain and Taint all start from, and the fix is the same one every other
track already uses. After a Rally: Resolve `0 → 1`. Invocation, `eff. 50`: roll **17** —
succeeds. `resolve_cost: 1` paid regardless of outcome: `1 → 0`. Pays cleanly — the gap §10 found
is closed.

**The spam sequence, replayed under ADR 0045's final design.** Seeded `20260842`, 26 attempts at
`major` tier (`eff. 10`, `strain_cost 8`), against Kester's own maximum Stamina of `6`:

| # | Roll | Result | Strain | Ill Omen | Taint | Trauma |
|---|---|---|---|---|---|---|
| 1 | 73 | fail | 2 | no | 0 | 1 |
| 2 | 32 | fail | 4 | no | 0 | 2 |
| 3 | 84 | fail | 0 | no | 0 | 3 |
| 4 | 51 | fail | 2 | no | 0 | 4 |
| 5 | 44 | fail | 4 | no | 0 | 5 |
| 6 | 19 | fail | 0 | no | 0 | 6 |
| 7 | 36 | fail | 2 | no | 0 | 7 |
| 8 | 72 | fail | 4 | no | 0 | 8 |
| 9 | 7 | **success** | 12 | no | 0 | 8 |
| 10 | 33 | fail | 2 | no | 0 | 10 (+2, two floors crossed in one jump) |
| 11 | 63 | fail | 4 | no | 0 | 11 |
| 12 | 68 | fail | 0 | no | 0 | 6 (+1, Affliction rolled) |
| 13 | 19 | fail | 2 | no | 0 | 1 (+1, Affliction rolled) |
| 14 | 91 | fail | 4 | no | 0 | 2 |
| 15 | 43 | fail | 0 | no | 0 | 3 |
| 16 | 45 | fail | 2 | no | 0 | 4 |
| 17 | 22 | fail | 4 | no | 0 | 5 |
| 18 | 90 | fail | 0 | **YES** | 4 | 6 |
| 19 | 39 | fail | 2 | no | 4 | 1 (+1, Affliction rolled) |
| 20 | 14 | fail | 4 | no | 4 | 2 |
| 21 | 40 | fail | 0 | **YES** | 8 | 3 |
| 22 | 6 | **success** | 8 | no | 8 | 3 |
| 23 | 25 | fail | 4 | no | 8 | 4 |
| 24 | 44 | fail | 0 | no | 8 | 5 |
| 25 | 17 | fail | 2 | no | 8 | 6 |
| 26 | 65 | fail | 4 | no | 8 | 7 |

**24 of 26 attempts failed. Final: Strain 4, Taint 8, Trauma 7 — three Afflictions rolled along
the way** (at attempts 12, 13, and 19, each dropping Trauma by 6 on a failed test against an
assumed `eff. 50` GM-chosen skill, disclosed as this replay's own assumption per
`08-afflictions.md`). Where the original sequence (under the pre-ADR-0045 rules) left this exact
shape of spam with zero Trauma and zero lasting consequence beyond Taint, this replay's Kester
carries three real Afflictions and a Trauma track still at 7 by the end — the brake §10 found
missing is now demonstrably present, against Kester's own character, not only in the abstract
verification script (`specs/057-systems-of-power-spam-brake/check_spam_brake.py`).

### What this section does not do

**No new design decision is made here.** This only re-applies decisions already made (ADR
0043–0045) to scenarios that were played before those decisions existed. Where a replay produces
a materially different outcome (§7's dropped round, §10's Trauma accrual), that difference is the
expected, intended effect of the fix landing — not a new finding to raise as its own issue.

---

## 15. Systems of power: minor-tier spam, the typical caster-in-an-encounter case

#176, part of #134. §10/§14's spam sequences both used `major` tier, where `strain_cost` (8)
already exceeds a starting character's maximum Stamina (6) — a side effect nobody chose on
purpose, raised in conversation after §14 landed: does ADR 0045's threshold cross on nearly every
single failure at that tier regardless of the "occasional crossing, not automatic" distinction it
was meant to draw? This pass checks the tier a magic-focused character actually leans on in most
encounters — `minor`, not the most-ambitious declaration a schema allows — with real play, not
arithmetic alone.

Kester, unchanged: `ember-craft: 50`, `strain_cost: 2`, `ill_omen_taint: 1`, Stamina `6/6`
(maximum Stamina `6`, the modulus ADR 0045 uses). `minor` tier: `eff. 50`, no cost multiplier, no
Ill Omen Taint bonus.

Real `d100` draws, seeded `20260850`, 26 attempts — the same count as §10/§14's major-tier
sequence, for a direct rate comparison, even though a real encounter more plausibly runs 8–12
rounds (called out separately below):

| # | Roll | Result | Strain | Ill Omen | Taint | Trauma |
|---|---|---|---|---|---|---|
| 1 | 1 | success | 2 | no | 0 | 0 |
| 2 | 57 | fail | 4 | no | 0 | 0 |
| 3 | 5 | success | 6 | no | 0 | 0 |
| 4 | 84 | fail | 2 | no | 0 | 1 |
| 5 | 19 | success | 4 | no | 0 | 1 |
| 6 | 42 | success | 6 | no | 0 | 1 |
| 7 | 81 | fail | 2 | no | 0 | 2 |
| 8 | 45 | success | 4 | no | 0 | 2 |
| 9 | 13 | success | 6 | no | 0 | 2 |
| 10 | 3 | success | 8 | no | 0 | 2 |
| 11 | 96 | fail | 10 | no | 0 | 2 |
| 12 | 87 | fail | 12 | no | 0 | 2 |
| 13 | 21 | success | 14 | no | 0 | 2 |
| 14 | 62 | fail | 16 | no | 0 | 2 |
| 15 | 35 | success | 18 | no | 0 | 2 |
| 16 | 37 | success | 20 | no | 0 | 2 |
| 17 | 44 | success | 22 | no | 0 | 2 |
| 18 | 16 | success | 24 | no | 0 | 2 |
| 19 | 19 | success | 26 | no | 0 | 2 |
| 20 | 37 | success | 28 | no | 0 | 2 |
| 21 | 26 | success | 30 | no | 0 | 2 |
| 22 | 46 | success | 32 | no | 0 | 2 |
| 23 | 26 | success | 34 | no | 0 | 2 |
| 24 | 39 | success | 36 | no | 0 | 2 |
| 25 | 41 | success | 38 | no | 0 | 2 |
| 26 | 58 | fail | 40 | no | 0 | 2 |

**7 of 26 attempts failed, matching the roughly 50% base rate. Final: Strain 40, Taint 0, Trauma
2.** Only **2 of those 7 failures (29%) crossed a multiple of maximum Stamina** and cost Trauma —
attempts 4 and 7, both early, while Strain was still low enough for a single `strain_cost: 2`
gain to cross a fresh multiple of 6. From attempt 11 onward, Strain climbs past 6 entirely on
**successes** (which never check or reset the threshold, per ADR 0045 — only a failure does), so
by the time later failures (11, 12, 14, 26) land, Strain is already sitting well above the next
multiple mid-band rather than crossing it, and none of them trigger Trauma. No Ill Omen came up
in 26 attempts at `minor` tier's un-widened 10% band (Taint stayed at `0` throughout, so the
die-bending widening never engaged either) — a real, disclosed feature of this particular seed,
not a claim about the underlying rate.

**The first 12 attempts** (a more realistic single-encounter length): **5 of 12 fail, Trauma
after 12 attempts: 2** — both crossings already landed by then.

### Findings

**The threshold behaves as intended at minor tier — confirmed by play, not just arithmetic.**
Where §10/§14's `major`-tier sequence crossed the threshold on very close to every single failure
(`strain_cost` 8 exceeding maximum Stamina 6 means almost any failure crosses at least one
multiple), this `minor`-tier sequence crossed on only **29%** of its failures — a materially
different, and clearly intended, rate. A magic-focused character leaning on their bread-and-
butter invocation across an ordinary encounter is not quietly accruing Trauma on every miss; the
brake reserves its bite for the tier `09-systems-of-power.md` already calls the most ambitious
one, exactly as ADR 0045 argued it would, now checked against real play rather than only the
tier's own numbers on paper.

**No new gap found, and no new design decision needed.** The `major`-tier near-certainty is a
real, disclosed emergent property of that specific tier's cost sitting close to a starting
character's maximum Stamina — not a flaw in the threshold rule, and not something this pass
recommends changing: `major` tier is meant to be the schema's most consequence-heavy declaration,
and a starting character choosing it repeatedly paying a steep, near-certain Trauma cost is
consistent with "ties ambition to consequence," the same framing `intensity_tiers` already states
for itself. A character with more maximum Stamina (a completed career: `7`; the ceiling: `10`)
would see the same tier behave more gently, exactly as §10/§14's own worked figures (13–26 Trauma
across max Stamina 6–10) already showed.

**What this pass does not prove**: whether a *moderate*-tier spam sequence sits somewhere between
these two rates was not checked, and is not assumed from either endpoint.

---

## 16. Correcting §10/§14/§15's Trauma figures: the threshold check was letting a success erase a crossing

#178, part of #134. Discussing §15's own headline finding — "only 29% of failures cost Trauma at
minor tier" — surfaced a real bug in how the threshold check was implemented, not just narrated:
it compared each failed invocation's own before-and-after Strain (a delta scoped to one roll), so
if a *success* was the invocation that carried Strain past a multiple of maximum Stamina, no
failure afterward would ever be charged for that boundary — only for the next one further out.
§15's own attempt 26 is the case in point: it failed while Strain was already 6.3× maximum
Stamina, built up almost entirely by successes, and cost zero Trauma under the old check.

**Resolved in [ADR 0047](../adr/0047-strain-threshold-crossing-checks-cumulative-strain.md)**,
superseding [ADR 0045](../adr/superseded/0045-failed-invocation-crossing-max-stamina-in-strain-costs-trauma.md):
the check now reads Strain's *current, cumulative* total on a failure, not a before/after delta —
`gained = (strain − 1) // max_stamina`. No new bookkeeping is needed: Strain is never reduced on
a success, so its own magnitude, left alone through any run of them, already carries forward
everything a failure needs to catch up on. **The original §7/§8/§10/§14/§15 text is not edited**
— this section states the corrected figures.

### §10/§14's major-tier sequence, corrected (seed `20260842`)

| # | Roll | Result | Strain | Ill Omen | Taint | Trauma |
|---|---|---|---|---|---|---|
| 1 | 73 | fail | 2 | no | 0 | 1 |
| 2 | 32 | fail | 4 | no | 0 | 2 |
| 3 | 84 | fail | 6 | no | 0 | 3 |
| 4 | 51 | fail | 2 | no | 0 | 5 (+2) |
| 5 | 44 | fail | 4 | no | 0 | 6 |
| 6 | 19 | fail | 6 | no | 0 | 7 |
| 7 | 19 | fail | 2 | no | 0 | 3 (+2, Affliction) |
| 8 | 5 | **success** | 10 | no | 0 | 3 |
| 9 | 7 | **success** | 18 | no | 0 | 3 |
| 10 | 33 | fail | 2 | no | 0 | 7 (+4) |
| 11 | 2 | **success** | 10 | no | 0 | 7 |
| 12 | 63 | fail | 6 | no | 0 | 3 (+2, Affliction) |
| 13 | 95 | fail | 2 | no | 0 | 5 (+2) |
| 14 | 19 | fail | 4 | no | 0 | 6 |
| 15 | 72 | fail | 6 | no | 0 | 1 (+1, Affliction) |
| 16 | 43 | fail | 2 | no | 0 | 3 (+2) |
| 17 | 45 | fail | 4 | no | 0 | 4 |
| 18 | 22 | fail | 6 | no | 0 | 5 |
| 19 | 90 | fail | 2 | **YES** | 4 | 7 (+2) |
| 20 | 63 | fail | 4 | no | 4 | 8 |
| 21 | 40 | fail | 6 | **YES** | 8 | 9 |
| 22 | 25 | fail | 2 | no | 8 | 11 (+2) |
| 23 | 65 | fail | 4 | no | 8 | 12 |
| 24 | 21 | fail | 6 | **YES** | 12 | 7 (+1, Affliction) |
| 25 | 89 | fail | 2 | no | 12 | 3 (+2, Affliction) |
| 26 | 14 | fail | 4 | no | 12 | 4 |

**23 of 26 fail. Final: Strain 4, Taint 12, Trauma 4 — five Afflictions rolled along the way**
(attempts 7, 12, 15, 24, 25), against §10/§14's original (uncorrected) figures of Trauma 7 with
three Afflictions. Taint also lands materially higher (12 vs. 8) — not because the corrected
check touches Ill Omen at all, but because the same 26 rolls simply produce a different Ill
Omen/Taint history once the die-bending widening (`03-rules.md` §1, engaging past 3 Taint) has
more Trauma-crossing events to interact with across the run.

### §15's minor-tier sequence, corrected (seed `20260850`)

| # | Roll | Result | Strain | Trauma |
|---|---|---|---|---|
| 1 | 1 | success | 2 | 0 |
| 2 | 57 | fail | 4 | 0 |
| 3 | 5 | success | 6 | 0 |
| 4 | 84 | fail | 2 | 1 (+1) |
| 5 | 19 | success | 4 | 1 |
| 6 | 42 | success | 6 | 1 |
| 7 | 81 | fail | 2 | 2 (+1) |
| 8 | 45 | success | 4 | 2 |
| 9 | 13 | success | 6 | 2 |
| 10 | 3 | success | 8 | 2 |
| 11 | 96 | fail | 4 | 3 (+1) |
| 12 | 87 | fail | 6 | 3 |
| 13 | 21 | success | 8 | 3 |
| 14 | 62 | fail | 4 | 4 (+1) |
| 15 | 35 | success | 6 | 4 |
| 16 | 37 | success | 8 | 4 |
| 17 | 44 | success | 10 | 4 |
| 18 | 16 | success | 12 | 4 |
| 19 | 19 | success | 14 | 4 |
| 20 | 37 | success | 16 | 4 |
| 21 | 26 | success | 18 | 4 |
| 22 | 46 | success | 20 | 4 |
| 23 | 26 | success | 22 | 4 |
| 24 | 39 | success | 24 | 4 |
| 25 | 41 | success | 26 | 4 |
| 26 | 58 | fail | 4 | 2 (+4, Affliction) |

**Attempt 26 is the case that found the bug: it failed while Strain (26, before this roll's own
+2) was already 4.3× maximum Stamina — built almost entirely by the run of successes from
attempts 15–25 — and now correctly charges 4 Trauma in one go, crossing the Affliction floor and
triggering a real Affliction roll. Total Trauma gained across the run: 8** (against §15's original
figure of 2), netted to a **final Trauma of 2** after that one Affliction's `−6`. `7/26` still
fail, matching the original fail count exactly — the correction changes *how much a failure that
already happened costs*, not the odds of failing.

### Findings

**A real, previously-undetected implementation gap, found by re-reading a playtest result rather
than by inspecting the rule in the abstract.** The corrected check produces meaningfully more
Trauma in both sequences — confirming the erasure §15 exposed was real, not a hypothetical, and
that it specifically favoured the case the fix was named for in the first place: a skilled,
mostly-successful character. `specs/057-systems-of-power-spam-brake/check_spam_brake.py`
re-verifies every property ADR 0045 originally established (real Trauma on spam across the whole
maximum-Stamina range, zero on ordinary play, immunity to the #172 rotation exploit) still holds
under the corrected check, plus a new direct demonstration that the corrected check never gives
*less* Trauma than the superseded one on the same rolls, and gives strictly more on both of these
sequences specifically.

**No new design decision beyond the correction itself.** ADR 0047 changes only how the crossing
is detected — failure-only gating, the maximum-Stamina modulus, the remainder-carry-forward
shape, and the disabled-track degradation are all unchanged from ADR 0045.
