# Wyrd — state schema

What is written to disk. The contract between the deterministic CLI and Claude.

Principle: **if the player could catch Claude cheating at it, it lives here.**

---

## `chronicle.yaml`

```yaml
name: the-drowning-well
setting: reikland
engine_version: 0.1.0
created: 2026-08-20
calendar:
  year: 2512
  month: Nachexen
  day: 14
era: "The Quiet Years"
threat_rating: 2          # scenario scaling T (see 03-rules)
sessions: 7
last_played: 2026-08-19
```

## `pc.yaml`

```yaml
name: Anselm Vogt
career: rat-catcher
career_history: [rat-catcher]
skills:
  brawling: 3
  stealth: 4
  perception: 3
  animal-care: 2
career_skill: 2           # = lowest skill in current career
stamina: {current: 9, max: 9}
luck: {current: 5, max: 5}
fate: {current: 2, max: 2}         # permanent; spent to avoid death
fortune: {current: 2}              # renewable daily, = fate max
hope: {current: 4, max: 5}
corruption: 1
corruption_weakness: "will do anything to keep his sister fed"
doom_clock: null                   # SECRET. 1d10+toughness, set at first mutation.
insanity: 0
stress: 0
derangements: []
mutations: []
fear_points: 0
reputation: {score: 1, label: "the man who found the child"}
passions:
  - {type: fear, object: "deep water"}
  - {type: loyalty, object: "his sister Grete"}
cruel_misfortune: "You have seen things — as a child he saw what came out of the well"
wounds: []                         # lasting marks from the Aftermath table
holdings: []
advances_unspent: 1
conditions: []                     # beset, weary, etc — derived, cached
```

`doom_clock` is written once, on first mutation, and **never shown to the player**. Any
render of `pc.yaml` for the player must strip it.

## `party.yaml`

```yaml
companions:
  - name: Grete Vollen
    career: rat-catcher
    agenda: "get her brother out of the debt he owes the Meisters"
    flaw: "cannot leave a wrong alone"
    bond: 3                        # -3..+3, to the PC
    corruption: 1
    stress: 0
    secret: "she already knows what happened to the brother"
    arc: "will have to choose between the debt and the party"
    status: with-party             # with-party | away | dead | damned | departed
    skills: {brawling: 2, stealth: 3}
    stamina: {current: 7, max: 7}
tension: 2                         # 0-6 party tension (see 04-session)
```

Companions are **cheaper to model than the PC** — no fate, no fortune, no doom clock. Only
the player carries the full state.

## `threats.yaml`

```yaml
threats:
  - id: the-rot-beneath-grenzstadt
    imminence: 3
    clues_found: [the-millers-cough, the-well-that-tastes-of-iron]
    activations: 4
    last_activated: {year: 2512, month: Nachexen, day: 2}
    connection: "Anselm's sister lives in Grenzstadt"
    known_to_player: partial       # none | rumoured | partial | understood
```

## `threads.yaml`

```yaml
threads:
  - id: the-escaped-patron
    opened: {year: 2512, month: Jahrdrung}
    summary: "the man who paid the cultists walked away; you saw his ring"
    hooks: [nobility, altdorf, jewellery, the-rot-beneath-grenzstadt]
    heat: 2                        # 0-5; rises when touched, decays when ignored
    status: open                   # open | resolved | cold | never-answered
```

## `codex/`

One file per entity, loaded on demand. Claude greps by name.

```
codex/npc/hallam-weissbruck.md
codex/location/grenzstadt.md
codex/faction/the-meisters.md
```

Each carries a one-line summary at the top for cheap matching, then detail, then a
`last_seen:` and `knows:` block recording what the *player* has learned — distinct from what
is true.

NPC entries also carry an **entanglement** block, which is what makes thread-based
succession possible (see [`05-campaign.md`](05-campaign.md)):

```yaml
entanglement:
  threads: [the-escaped-patron, the-rot-beneath-grenzstadt]
  owed: "the PC left her brother in the cellar"
  disposition: hostile        # ally | wary | hostile | hunting | unaware
  viable_successor: true
```

`viable_successor` is set by Claude when an NPC becomes sufficiently entangled to carry a
chronicle on their own. On the PC's death these are the candidates offered.

## `recap.md`

Regenerated at every session close. Always loaded. Target ~200 words:

- where you are and when
- what is unresolved (top 3 threads by heat)
- what changed while you were away
- the state of your body and soul in one sentence
- who is with you and how they are

## Invariants the CLI enforces

- `career_skill` == lowest skill in the current career
- `stamina.max` only rises when `career_skill` rises
- `fortune.current` <= `fate.max`
- character is **Beset** iff `hope.current <= corruption` and `corruption > 0`
- `insanity >= 6` triggers a Willpower test on every further gain
- mutations count > `doom_clock` → status becomes `damned`
- `tension` in 0..6; reaching 6 fires an event and resets to 0
- every write is atomic; every write is followed by a schema validation
- **no write may be skipped because narration already happened** — persist precedes narrate

## Session-interrupt marker

If a session stops mid-beat:

```yaml
pending:
  beat: "searching the physician's cellar"
  awaiting: "player choice: force the door, or fetch Grete first"
  rolled: null
```

Cleared at the next Rally. Its presence means the next session resumes exactly, rather than
recapping vaguely.
