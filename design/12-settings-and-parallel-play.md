# Wyrd — setting separation, and chronicles side by side

Settings share an engine and may share source material. They must share nothing else — and
more than one chronicle may be live at a time.

---

## What is shared and what is not

| Layer | Shared | Per setting |
|---|---|---|
| **Resolution** | `d100`, the Wyrd die, degrees of success, difficulty bands | — |
| **Combat** | stamina, armour dice, criticals, Aftermath | flavour of the critical tables |
| **Tracks** | Taint, Trauma, Strain, Resolve, Fate | their *names*, and whether they exist at all |
| **Session** | beats, Rally, downtime, party tension | what downtime looks like here |
| **Campaign** | threats, threads, elapsed time, succession | who the threats are |
| **Careers** | the graph — entries, exits, advance triggers | the graph's contents |
| **Content** | — | gear, creatures, calendar, names, organisations |
| **Tone** | — | **the whole contract** ([`01-principles.md`](01-principles.md)) |
| **Voice** | — | **everything** |

The engine is genuinely setting-agnostic: what changes is data and register.

**A second setting in the same genre is not a reskin of the first.** Two worlds may share a
mechanic and mean entirely different things by it — one calls it damnation and one calls it
fatigue of the soul — and the register that carries that difference is the hardest file to
write, not the easiest.

## The corpus is shared; the indexes are per setting

Source material is extracted once, but **indexed per setting**, because the same adventure
adapted for two worlds produces two different adaptations
([`11-corpus-index.md`](11-corpus-index.md)). Every index record is scoped to its setting,
so a query in one chronicle never returns another's material.

Tagging beats duplicating; scoping beats sharing.

## One repository per chronicle

```
wyrd/                        # engine
wyrd-<setting-a>/            # setting
wyrd-<setting-b>/            # another setting
wyrd-chronicle-<name>/       # one per chronicle
```

Reasons, in order of weight:

1. **Concurrency.** Two live sessions committing on every beat will race. Two repositories
   never do. This is the reason that matters once parallel play is real.
2. **Lifecycle.** A chronicle only accumulates; an engine gets refactored. Mixed histories
   are unreadable.
3. **Portability.** A chronicle can be archived or moved on its own.
4. **Blast radius.** `wyrd doctor --repair` touches one chronicle and cannot disturb another.

Each chronicle pins its own engine and setting versions
([`09-evolution.md`](09-evolution.md)), so one can trial a rules change while another stays
put — which is the cheapest way to test a change that only shows up in play.

## Session isolation

**One chronicle per session. Always.**

This is a GM contract **MUST NOT** because the failure is subtle and serious: knowledge
bleeding between chronicles. If a name, a character, a threat or a plot turn crosses over,
the second chronicle stops being its own world — **and the player has no way to detect it
happening.**

So:

- a session loads exactly one chronicle and one setting, and says which in the recap
- the corpus is queried **with the setting as a filter**, never unfiltered
- name collisions are checked *per chronicle*, not globally — the same innkeeper's name may
  legitimately exist in both
- every verb takes an explicit chronicle path; there is no "current chronicle" global, so the
  wrong one cannot be edited by accident

## In practice

Two chronicles, two terminals — or one on a desktop and one from a phone. Because the
repositories are separate and every verb names its target, there is no contention and no
locking to design.

The realistic pattern is not simultaneous play but **alternating** — one on Tuesday, another
on Thursday. That makes resumption matter more, not less: `recap.md`, elapsed-time
computation and thread heat all have to carry *which world is this and what was happening*
after a fortnight away.

Both chronicles' threats advance on their own calendars, independently, and neither knows the
other exists.

## The same arc in two chronicles

Allowed, and it will not feel repetitive: different characters, different threads, different
companions, and the same situation means something different in a different world.

`source:` on the converted entity makes the reuse visible, so it stays a choice rather than an
accident.
