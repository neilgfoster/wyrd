# Wyrd — journeys

The subsystem for a setting whose story is travel: a road, a river, a trek across open country
that needs to be **played**, not summarised in a sentence. `13-authoring-a-setting.md`'s worked
example found this gap directly — a setting built around travel has nothing to run, and a
setting may never invent its own subsystem to fill the hole. This document is the engine's
generalised answer, which any setting may configure or leave off entirely.

A setting that never authors a journey is unaffected: travel is narrated exactly as
[`05-campaign.md`](05-campaign.md) already describes, and nothing below is invoked.

---

## A journey is an arc

Containment already recurses at every level — "arcs contain arcs"
([`15-arcs-and-beats.md`](15-arcs-and-beats.md)) — so a journey needs no new content type, only
a recognised `scale` and two fields specific to travel.

```yaml
---
id: the-road-to-the-shrine
type: arc
scale: journey
name: "The road to the shrine"
from: [[the-drowned-town]]
to: [[the-shrine]]

pace: "one day's travel"     # what one leg covers — optional; omit for an unstructured journey
hazard_rating: 4              # optional; default 0 — no hazard rolls at all
hazards:                      # optional; default empty — a triggered roll with nothing to match is a no-op
  1-2: {name: "washed-out ford", skill: athletics, difficulty: challenging, effect: "a day lost"}
  3-5: {name: "bandits on the ridge", skill: perception, difficulty: average, effect: "a beat: ambush"}
  6:   {name: "a traveller with news", skill: null, difficulty: null, effect: "a thread surfaces"}

roles: [navigator, forager, lookout]   # optional; default empty — see Roles below

children:
  - [[first-days-road]]
  - [[the-washed-out-ford]]
  - [[approach-to-the-shrine]]
---

What the road is like, who else travels it, what waits along it. Never a script.
```

| Field | Required | Default when omitted |
|---|---|---|
| `id`, `type: arc`, `scale: journey` | yes | — |
| `name` | yes | — |
| `from`, `to` | yes | — |
| `pace` | no | The whole journey runs as a single leg — see Legs below |
| `hazard_rating` | no | `0` — no hazard rolls |
| `hazards` | no | empty table — a triggered roll matches nothing and is a no-op |
| `roles` | no | empty — no travel roles named |
| `children` | yes | — the journey's legs, in order |

`from`/`to` are entity references to `place`s ([`14-entities.md`](14-entities.md)). A journey
with no `pace` still has legs — it simply has one, covering the whole route — so "no pace" is
how a setting author gets a journey that is structurally present (selectable, convertible) but
mechanically as light as ordinary narrated travel.

---

## Legs

A **leg** is an ordinary arc or beat, a child of the journey, that additionally declares its
resolution mode — the same `mode: played | summarised` field every beat already carries
([`15-arcs-and-beats.md`](15-arcs-and-beats.md)).

- **`mode: played`** — the leg is an ordinary beat: entry, cast, a scene, resolved through the
  core roll ([`03-rules.md`](03-rules.md)) like any other test.
- **`mode: summarised`** — the leg advances through the existing elapsed-time machinery
  (`wyrd advance-time`, [`05-campaign.md`](05-campaign.md)) — expected-value events over the
  leg's span, not a played scene.

**Mode is author-declared, never chosen at runtime.** A journey's author (or whoever converts
its stub — [`15-arcs-and-beats.md`](15-arcs-and-beats.md)) decides, leg by leg, which stretches
of the road are worth playing and which are worth a sentence. The engine does not pick this on
the fly from pacing or from whether a hazard happened to trigger — a leg's mode is fixed the
same way any other beat's is.

---

## The hazard roll

Once per leg, if the journey has a `hazard_rating` above zero, roll:

```
d100 ≤ hazard_rating × 10
```

This is the exact shape of a Threat's activation roll — `d100 ≤ imminence × 10`
([`05-campaign.md`](05-campaign.md)) — reused rather than duplicated, so a GM who already knows
how Threat activation works needs no second formula to hold in their head. **Worked example**:
`hazard_rating: 4` gives a 40% chance per leg, exactly comparable to a Threat at imminence 4
(also 40%, but per game-week rather than per leg — the unit differs, the shape does not).

On a trigger, roll again to find which entry on the journey's `hazards` table applies (the
`1-2`/`3-5`/`6` ranges above are an ordinary d6-or-similar sub-table, the same convention a
Threat's `effects:` table uses). The matched entry resolves through the **core roll**
([`03-rules.md`](03-rules.md)) against its named skill and difficulty — a journey introduces no
resolution mechanic of its own. An entry with no skill (the "traveller with news" row above) is
not a test at all; it is narration, exactly as an entry on any other table may be.

A hazard rolled with an empty `hazards` table is a no-op: the trigger happened, nothing was
there to answer it, play continues.

---

## Roles

A journey may name an ordered list of **travel roles** — navigator, forager, lookout, or
whatever a setting's fiction calls for. The engine carries this as a data slot only: it does not
define what a role does, grant a bonus for filling one, or require one to be filled.

This matches the engine's existing shape for skills and careers — the engine supplies the slot,
the setting supplies the meaning ([`03b-the-character.md`](03b-the-character.md)). A setting
that wants "forager" to lower the Survival difficulty, or to matter only in the fiction, decides
that itself; the journey's `roles` list is where it hangs the name.

---

## Ending a journey early

A journey need not run to its declared end. Abandoned, rerouted, or interrupted, it closes the
same way: elapsed time and any consequences already incurred apply for the distance actually
travelled — the legs reached, not the legs listed — and whatever remains either lapses (the
road not taken) or is picked up later as its own fresh journey. No separate "cancel" mechanism
exists; this is the ordinary rule that a played sequence produces only the consequences of what
was actually played.

---

## Consequences use the existing material economy

A hazard's `effect`, or an ordinary leg's outcome, may cost Standing, coin, condition, or supply.
These land through the same abstraction the rest of the engine already uses (Standing and the
material economy) — a journey introduces no per-item inventory, no weight table, no logistics
ledger. This is the same "realistic, not logistic" preference
([`10-diegesis.md`](10-diegesis.md)) extended to travel rather than reinvented for it.

## Passing through a Threat's reach

A route that crosses an active Threat's reach is exposure like any other passage through it —
its `ambient` cost ([`05-campaign.md`](05-campaign.md)) applies to whichever leg passes through.
There is no separate journey-versus-Threat resolution; a journey does not change what a Threat
is or how it is encountered, only that the character is travelling when they encounter it.
