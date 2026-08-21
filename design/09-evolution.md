# Wyrd — engine evolution

A chronicle may run for a decade. The engine will not stand still for a decade: rules get
tuned, tables grow, subsystems get replaced, bugs get fixed. A chronicle begun under
engine 0.1 must still be playable under engine 2.0 — and must still be *the same chronicle*.

This is the same problem as [`08-maintenance.md`](08-maintenance.md), one level up, and it
takes the same shape: **the past is a fact; only the future is negotiable.**

---

## The governing rule

> **Rule changes apply forward. They never recompute the past.**

If taint gain is retuned in year three, the taint accrued in years one and two
stands. If the Aftermath table gains entries, past injuries do not change. If a probability
is corrected because it was wrong, the rolls it produced still happened.

This is not merely pragmatic. A chronicle's value is that it is a true record of what
occurred. An engine that quietly reinterprets old events destroys the thing it exists to
preserve — and the player would be right to stop trusting it.

The one exception is a **provably corrupt state** (an invariant violated by a bug, a
negative stamina maximum). Those are repaired, and the repair is recorded as a repair, not
disguised as history.

---

## Change classes

Every engine change is classified. The class determines what happens to live chronicles.

| Class | Meaning | Live chronicles |
|---|---|---|
| **Additive** | New content that cannot alter existing outcomes — a new career, extra table entries, another arc, a new setting | Adopt automatically |
| **Tuning** | Numbers change: thresholds, probabilities, costs, decay rates | Forward-only, on confirmation |
| **Structural** | The save schema changes — new field, renamed key, moved file | Requires a migration; state rewritten, facts preserved |
| **Behavioural** | A subsystem works differently — a track is replaced, resolution changes | Requires a migration **and** an explicit decision about in-flight state |
| **Corrective** | A bug produced results the rules never intended | Forward-only by default; retroactive repair only with explicit consent |

Additive is the class to aim for. Most Wyrd growth — more scenarios, more careers, more
table entries, an entire new setting — is additive by construction, which is a direct
benefit of the layering in [`02-architecture.md`](02-architecture.md).

---

## Version pinning

`chronicle.yaml` carries the versions and the migration history, in the shape defined in
[`06-state.md`](06-state.md) — engine and setting each with a `version` and a
`created_under`, plus an append-only `migrations` list. Entities carry their own
`schema_version`, and derived entities the `converted:` rules that produced them.

On load, the engine compares its own version with the chronicle's:

- **equal** → play
- **chronicle older, only additive changes between** → play, silently adopt
- **chronicle older, migration required** → refuse to play; report what is needed
- **chronicle newer than the engine** → refuse to play; never downgrade a chronicle

Refusing to play is correct. Playing a session under half-migrated rules produces exactly
the kind of quiet inconsistency that is unrecoverable a year later.

---

## Migrations

```bash
wyrd migrate --check          # what would change, and of what class
wyrd migrate --dry-run        # full diff of the resulting state, writes nothing
wyrd migrate --apply
```

Rules:

- migrations are **explicit, versioned, ordered and one-way**; each lives in
  `engine/migrations/0001_....py` as a pure `state -> state` function
- each declares its **class**, and Tuning/Behavioural/Corrective migrations **require
  confirmation** — they are Revision-tier in maintenance terms
- a migration runs only on a clean git tree and lands as **its own commit**, tagged
- every migration appends to `chronicle.migrations`, so the chronicle carries its own
  provenance forever
- migrations are **tested against golden chronicles** (see below) — a migration that
  changes a past outcome fails its test by definition

### In-flight state

Behavioural changes must say what happens to state that exists mid-flight: a Threat at
Imminence 4 when the Imminence scale is rescaled; a partially-accrued track that no longer
exists. Every Behavioural migration answers this explicitly, and the honest default is
**preserve the value and reinterpret it forward**, never delete it.

### Era boundaries are the natural seam

Where a change is large enough to feel different at the table, apply it at an **era
boundary** ([`05-campaign.md`](05-campaign.md)). Eras already exist, already carry a tonal
shift, and are already git-tagged. "The world works differently now" is absorbed far more
gracefully between eras than mid-arc — and it costs nothing to wait.

---

## Provenance

Every recorded outcome carries the engine version that produced it:

```json
{"beat": 412, "verb": "roll", "engine": "0.3.1", "dice": [5,5,2], ...}
```

Cheap to write, and it makes the whole history auditable: you can always tell which ruleset
produced a given result, and therefore whether an apparent inconsistency is drift or an
intended change. Without it, a decade of log is unfalsifiable.

---

## House rules

The engine should not need forking to be tuned. A chronicle may carry overrides:

```yaml
# chronicles/<name>/houserules.yaml
resolution:
  wyrd_die:
    neutral_band: [2, 3, 4, 5]     # widen if side effects prove too busy
taint:
  dark_deal_enabled: true
session:
  advances_per_session: [1, 2]
```

Layered over engine defaults at load, reported by `wyrd doctor`, and recorded in the
chronicle so the history remains interpretable. House rules are **Tuning-class by
definition** and therefore forward-only — changing one mid-chronicle does not rewrite what
came before.

This matters because the open questions in
[`dice-design.md`](https://github.com/neilgfoster/wyrd-research/blob/main/reference/dice-design.md) — is 44% side-effect frequency
too busy? should triples be distinguished? — are settled by *playing*, not by argument, and
that settling should not require an engine release.

---

## Golden chronicles

The regression suite that makes all of the above safe.

A golden chronicle is a saved state plus a scripted sequence of verbs plus the expected
resulting state, committed under `tests/golden/`. They are the only thing that reliably
catches rule drift across refactors.

- at least one per engine minor version, **frozen at that version**
- replayed on every change: additive changes must not alter any golden outcome
- a change that *does* alter one is, by definition, not additive — the suite classifies the
  change whether or not the author did
- migrations are tested by migrating an old golden chronicle forward and asserting that its
  **history is unchanged** and only its representation moved

This is the mechanism that turns "the past is a fact" from an intention into something the
build enforces.

---

## Design records

The design documents themselves evolve, and the *reasons* matter more than the current
state — most of what is in `design/` is a decision with a rejected alternative behind it.

`design/adr/NNNN-title.md`, one per significant decision: context, the decision, the
alternatives rejected and why, and consequences. Superseded ADRs are marked superseded, not
deleted.

The first few are already implicit in the existing docs and should be extracted:

- the dice mechanic, and why margin and a summed side-die were rejected
- deferred death via an Aftermath table rather than in-combat resolution
- Resolve/Shadow as a balance rather than one-way ratchet
- succession through the thread rather than the bloodline
- deterministic-over-inference

---

## What this means for the build

Three things move earlier than they otherwise would:

1. **Version pinning and `migrations[]` in the schema from the first commit** — engine,
   setting, state format and conversion rules, per [`06-state.md`](06-state.md).
   Retrofitting provenance is impossible, because the history you would describe has already
   happened.
2. Provenance stamping on log entries **from the first beat**, for the same reason.
3. The first golden chronicle created as soon as `roll`, `damage` and `track` exist — before
   there is any pressure to change them.

None of it is expensive up front. All of it is impossible to add later.
