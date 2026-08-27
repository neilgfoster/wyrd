# Wyrd — running more than one chronicle

More than one chronicle may be live at a time — in the same setting or different ones. This
is the only part of Wyrd where two things run at once, so it is the only part that needs
rules about isolation.

What separates a setting from the engine is in
[`24-authoring-a-setting.md`](24-authoring-a-setting.md); how the repositories divide is in
[`02-architecture.md`](02-architecture.md). This document is about the running of them.

---

## Isolation is the whole problem

**One chronicle per session. Always.**

This is a GM contract **MUST NOT** ([`01-principles.md`](01-principles.md)) because the
failure is subtle and serious: knowledge bleeding between chronicles. If a name, a character,
a threat or a plot turn crosses over, the second chronicle stops being its own world — **and
the player has no way to detect it happening.** Every other failure in Wyrd is visible to
someone. This one is not.

So:

- a session loads exactly one chronicle and one setting, and **says which in the recap**
- the corpus is queried **with the setting as a filter**, never unfiltered
  ([`26-corpus-index.md`](26-corpus-index.md))
- name collisions are checked **per chronicle, never globally** — the same innkeeper's name
  may legitimately exist in both, and merging them would be the bleed, not the fix
- every verb takes an **explicit chronicle path**. There is no "current chronicle" global, so
  the wrong one cannot be edited by accident

## Concurrency needs no locking

Because each chronicle is its own repository and every verb names its target, two live
sessions cannot contend. There is nothing to lock and no shared mutable state.

Each chronicle also pins its own engine and setting versions
([`29-evolution.md`](29-evolution.md)), so one may trial a rules change while another stays
put — the cheapest way to test a change that only shows up in play.

## Alternating, not simultaneous

The realistic pattern is not two sessions at once but **one on Tuesday and another on
Thursday**. That makes resumption matter *more*, not less: `recap.md` and thread heat have to
carry *which world is this, and what was happening* after a fortnight away
([`22-state.md`](22-state.md)).

Each chronicle's threats advance on its own calendar — and only when its own game time
advances ([`19-campaign.md`](19-campaign.md)). Neither knows the other exists.

## The same arc in two chronicles

Allowed, and it will not feel repetitive: different characters, different threads, different
companions, and the same situation means something else in a different world — or in the same
world at a different time.

`source:` on the converted entity makes the reuse visible, so it stays a choice rather than an
accident.
