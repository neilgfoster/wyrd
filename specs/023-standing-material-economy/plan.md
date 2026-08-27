# Implementation Plan: Standing and the material economy

**Branch**: `023-standing-material-economy` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

## Summary

Define Standing where Upkeep already spends it (`docs/design/16-session.md`), give it a place among
the other open-ended tracks in `docs/design/03-rules.md`, and specify the gear schema
`docs/design/24-authoring-a-setting.md` has promised since it first named `gear.yaml`. Wealth (coin)
is reconciled with Standing rather than modelled as a second parallel resource. Encumbrance stays
a GM judgment call, matching `docs/design/13-diegesis.md`'s existing "realistic, not logistic" rule —
no new numeric mechanism. The casual/martial distinction gets a concrete consequence path through
Standing rather than a second, unrelated mechanic. Record the decisions as an ADR, and validate
the gear schema with a script in the shape of `tools/check_bestiary.py`.

## The load-bearing decisions

**Standing is kept and defined, not removed.** The spec's own Assumptions section already
resolved this: Standing already does narrative work in Upkeep, and it is the natural anchor for
the casual/martial consequence (User Story 4) — removing it would need a replacement mechanic to
carry both jobs, which is more invention than definition. Standing is a small, open-ended count
(clarified 2026-08-26), the same shape as Taint/Trauma/Strain/Resolve, not a percentile or a
capped 0–N band — Upkeep only ever moves it by 1, and nothing in the existing rules compares it
against a skill roll.

**Wealth (coin) is a small numeric count, not a ledger.** Upkeep's "spend coin equal to Standing"
already requires comparing two numbers, so coin cannot be a pure narrative abstraction the way
inventory is — but the design stops short of asking the player to itemize purchases
(clarified 2026-08-26). Standing and coin are reconciled as two sides of the same material
position rather than fully independent or fully interchangeable: Standing is what a character
*is owed* by their position, coin is what they *have on hand*, and Upkeep is the one place they
convert into each other.

**Encumbrance is a GM question against the fiction, not a new mechanic.** `10-diegesis.md`
already answers "what is missing" the same way; this feature extends that shape to "can this
plausibly be carried" rather than inventing a weight table or a roll (clarified 2026-08-26). No
numeric encumbrance value is added anywhere in the design.

**The casual/martial distinction resolves through Standing, not a second social system.** A
martial weapon seen somewhere it's restricted is framed as a Standing consequence (and, where the
GM judges the fiction calls for it, an encounter trigger) rather than a bespoke new penalty —
this keeps the feature from adding a mechanism parallel to one it just defined.

**The gear schema mirrors the adversary block's shape.** `03d-the-adversary.md` already has a
closed-field, closed-vocabulary schema with a validator (`tools/check_bestiary.py`); gear reads
into the same combat fields (damage, damage type, armour rank) plus the fields specific to an
item (casual/martial, price, availability/legality), so the schema and its validator follow that
precedent rather than inventing a new validation shape.

## Structure

- `docs/design/16-session.md` — Upkeep's "lose 1 Standing, or spend coin equal to Standing" line
  rewritten against the defined terms; no more forward reference to an undefined mechanic.
- `docs/design/03-rules.md` — Standing added to the engine-label table (§ top) alongside Taint,
  Trauma, Strain, Resolve, Fate; §2 gains the wealth/coin definition, the encumbrance rule, and
  the casual/martial consequence, next to the existing weapon/armour/damage material it already
  depends on.
- `docs/design/24-authoring-a-setting.md` — the `gear.yaml` line expanded into the field list a setting
  author needs: weapon fields (damage, damage type, casual/martial, price,
  availability/legality) and armour fields (rank, price, availability/legality).
- `docs/adr/0033-standing-and-the-material-economy.md` — records: Standing kept and defined
  (not removed); Standing as an open count, not a percentile; coin as a stated total, not a
  ledger; encumbrance as GM judgment, not a roll; the casual/martial consequence routed through
  Standing. Each with its rejected alternative.
- `docs/README.md` — ADR index updated.
- `tools/check_gear.py` — validates a setting's `gear.yaml` against the schema: required/optional
  fields, closed armour-rank and damage-type vocabularies (reusing the same closed sets
  `check_bestiary.py` already encodes), casual/martial as a closed two-value field, price as a
  non-negative number. Fails loudly and names every offending entry and field, following
  `check_bestiary.py`'s reporting shape.
- `specs/023-standing-material-economy/` — this plan, `research.md`, `data-model.md`,
  `quickstart.md`, `tasks.md` (Phase 2).

## No engine code

Design-only, matching #12/#19/#18/#8's own precedent: the deliverable is the design document
changes, the ADR, and the gear validator script — there is no `engine/` runtime for this feature
to extend.

## Verification

- `python3 tools/check_gear.py specs/023-standing-material-economy/example-gear.yaml` — a small
  worked example (a few weapons, a few armour pieces) validates cleanly, and a deliberately broken
  copy of it is rejected with a specific, per-field error for each planted fault (missing field,
  bad armour rank, bad damage type, unrecognised field) — mirroring how `check_bestiary.py` is
  itself exercised.
- `python3 tools/check_docs.py` — reachability, dead links, ADR index, link policy.
- `python3 tools/backlog.py check` — confirms no drift introduced.
- `grep` across changed files in `design/` for setting/system vocabulary — no unexpected match.
- Read Upkeep (`docs/design/16-session.md`) cold against only `design/` — every term it uses resolves
  (SC-003 from the spec).

## Complexity tracking

None. No constitution violations; no new runtime dependencies; one stdlib script alongside the
existing `check_bestiary.py`/`check_affliction.py`/`check_transformation.py`/`check_advancement.py`
family.
