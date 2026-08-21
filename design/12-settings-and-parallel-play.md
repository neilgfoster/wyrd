# Wyrd — settings, and running two chronicles at once

Fantasy and 40k share an engine and a library. They must not share anything else — and
eventually both may be live at the same time.

---

## What is shared and what is not

| Layer | Shared | Per setting |
|---|---|---|
| **Resolution** | d100, Wyrd die, SL, difficulty bands | — |
| **Combat** | stamina, armour dice, criticals, Aftermath | flavour of the critical tables |
| **Tracks** | Corruption, Insanity, Fate, Hope, Stress | *vocabulary* — mutation vs warp-taint, derangement vs the Whisperings |
| **Session** | beats, Rally, Fellowship phases, party tension | — |
| **Campaign** | Threats, threads, elapsed time, succession | — |
| **Careers** | the *shape* — exits, advance triggers | the entire career graph |
| **Content** | — | gear, creatures, deities, calendar, names, factions |
| **Voice** | — | **everything** |

The mechanical engine is genuinely setting-agnostic. What changes is **data and register**,
which is why the layering in [`02-architecture.md`](02-architecture.md) holds.

**The 40k setting is not a reskin, though.** Corruption is the same mechanic with a different
theology; the long defeat is *more* pronounced, not less; and the voice is a different
language — the Old World's dry municipal grimness against the Imperium's liturgical
brutality. `settings/imperium/voice.md` is the hardest file in that directory, not the
easiest.

## The corpus is shared; the indexes are tagged

One library, one extraction, one set of indexes. Every scenario record already carries
`settings: [...]` and an `adaptation` cost
([`11-corpus-index.md`](11-corpus-index.md)), so the same index serves both and a
`wyrd find scenario` in an Imperium chronicle simply never sees Reikland-only material.

This is deliberate. A Deadlands investigation may suit either; a *White Dwarf* hive-gang
piece suits one. Tagging beats duplicating.

## Four repositories

See [`02-architecture.md`](02-architecture.md) for the full layout:

```
wyrd/                        # engine only
wyrd-wfrp/                # Reikland setting, scenarios, indexes
wyrd-40k/             # Imperium setting, scenarios, indexes
wyrd-chronicle-hemmelfurt/   # one per chronicle
```

Reasons, in order of weight:

1. **Concurrency.** Two live sessions committing to one repo on every beat will race. Two
   repos never do. This is the reason that actually matters once parallel play is real.
2. **A chronicle is data with a different lifecycle to code.** The engine gets refactored;
   a chronicle only ever accumulates. Mixing them makes both histories harder to read.
3. **Portability.** A chronicle can be archived, backed up or moved on its own.
4. **Blast radius.** `wyrd doctor --repair` touches one chronicle and cannot disturb another.

Each chronicle pins `engine_version` and migrates on its own schedule
([`09-evolution.md`](09-evolution.md)) — so the Reikland chronicle can sit on 0.4 while the
Imperium one runs 0.5, which is exactly what you want when a rules change is being tried out.

## Session isolation

**One chronicle per session. Always. No exceptions.**

This belongs in the GM contract, because the failure is subtle and serious: knowledge
bleeding between chronicles. If a name, an NPC, a Threat or a plot turn from the Reikland
chronicle surfaces in the Imperium one, the second chronicle stops being its own world —
and the player has no way to detect it happening.

So:

- a session loads exactly one `chronicle.yaml` and one setting, and states which at the top
  of the recap
- the corpus is queried **with the setting as a filter**, never unfiltered
- the concordance ([`11-corpus-index.md`](11-corpus-index.md)) is checked per-chronicle for
  name collisions, not globally — the same innkeeper's name may legitimately exist in both
- `wyrd` verbs take an explicit chronicle path; there is no "current chronicle" global, so
  the wrong one cannot be edited by accident

**MUST NOT (GM contract):** carry any fact, name, NPC, event or invention from one chronicle
into another, in either direction, for any reason.

## Practical parallel play

Two chronicles, two sessions, two terminals — or one on the lab box and one from the phone.
Because the repos are separate and every verb is explicit about its target, there is no
contention and no locking to design.

The realistic pattern is not simultaneous play but **alternating** — a Reikland session on
Tuesday, an Imperium one on Thursday. That makes the resumption machinery matter more, not
less: `recap.md`, elapsed-time computation and thread heat all have to carry the weight of
"which world is this and what was happening" after a fortnight away.

Both chronicles' Threats advance on their own calendars, independently, and neither knows the
other exists.

## Cross-setting scenarios

A scenario tagged for both settings is stored **once** and adapted at selection time, with
`adaptation` recording the cost and the chronicle's `source:` field recording what was
changed ([`05-campaign.md`](05-campaign.md)).

The interesting case is the same scenario run in both chronicles. That is allowed, and it
will not feel repetitive — different characters, different threads, different companions, and
a corrupt miller in Hemmelfurt is not a corrupt tithe-clerk on a forge world. But
`source:` makes it visible, so the reuse is a choice rather than an accident.
