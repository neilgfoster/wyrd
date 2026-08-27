# Tasks: Standing and the material economy

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md)

## Phase 1 — Gear schema and validator (must precede the design doc's claims)

- [X] T001 Write `tools/check_gear.py`, mirroring `tools/check_bestiary.py`'s shape: parse a
  setting's `gear.yaml`, validate each entry against `data-model.md`'s weapon/armour schema
  (required/optional fields per `kind`, reject unrecognised fields), reusing the existing
  `ARMOUR_RANKS`/`DAMAGE_TYPES` closed sets. [FR-003, FR-004]
- [X] T002 In the same script, validate `class` (weapon) as exactly `casual`/`martial` and
  `price` as a non-negative number on every entry; report every failing entry and field, not just
  the first. [FR-003]
- [X] T003 Write `specs/023-standing-material-economy/example-gear.yaml`: a small worked example
  (2-3 weapons spanning casual/martial and at least two damage types, 2-3 armour pieces spanning
  ranks) that validates cleanly. [SC-002]
- [X] T004 Write `specs/023-standing-material-economy/example-gear-broken.yaml`: a copy with one
  planted fault of each kind (missing required field, invalid armour rank, invalid damage type,
  unrecognised field, negative price) and confirm `check_gear.py` reports each by name. [SC-002]

## Phase 2 — Design document: Standing (US1)

- [X] T005 Add **Standing** to the engine-label table at the top of `docs/design/03-rules.md`,
  alongside Taint/Trauma/Strain/Resolve/Fate: what it measures (social position), that it is an
  open-ended count like the other tracks (not a percentile, not a capped band). [FR-001, FR-008]
- [X] T006 In `docs/design/03-rules.md` (near the other tracks, §4-5's neighbourhood), state what
  raises and lowers Standing in play, and cross-reference `docs/design/13-diegesis.md` for how it is
  rendered to the player (diegetic status, never a raw number). [FR-001, FR-002]
- [X] T007 Rewrite `docs/design/16-session.md:112`'s Upkeep line in place: "lose 1 Standing, or spend
  coin equal to Standing" now resolves against the definitions from T005/T006 and the coin
  definition from T009 — no dangling forward reference. State what losing Standing costs the
  character concretely (not only that the number changes). [FR-001, FR-002, SC-001, SC-003]

## Phase 3 — Design document: wealth and gear (US2)

- [X] T008 Expand `docs/design/24-authoring-a-setting.md:19`'s `gear.yaml` line into the field list
  from `data-model.md` (weapon and armour schemas), and note `tools/check_gear.py` as its
  validator, mirroring how the adversary block's line points at `check_bestiary.py`. [FR-003,
  FR-004, SC-002]
- [X] T009 In `docs/design/03-rules.md` §2, add the wealth (coin) definition: a small stated count, no
  transaction ledger, and its explicit reconciliation with Standing (Standing is owed by
  position, coin is on hand; Upkeep is where they convert). [FR-005]

## Phase 4 — Design document: encumbrance and casual/martial (US3, US4)

- [X] T010 In `docs/design/13-diegesis.md`'s "Inventory — realistic, not logistic" section, extend the
  existing "what is missing" framing to state the encumbrance question explicitly ("can this
  plausibly be carried") as the same kind of GM judgment call, with no numeric mechanism added.
  [FR-006, SC-004]
- [X] T011 In `docs/design/03-rules.md` §2, next to the existing casual/martial sentence, state the
  concrete Standing consequence (and, where the GM judges it, an encounter trigger) for a martial
  weapon seen somewhere restricted — replacing the current social-framing-only sentence. [FR-007]

## Phase 5 — Decision record

- [X] T012 Write `docs/adr/0033-standing-and-the-material-economy.md`: Standing kept and
  defined (rejecting removal); Standing as an open count (rejecting a percentile or capped band);
  coin as a stated total (rejecting both pure abstraction and a full ledger); encumbrance as GM
  judgment (rejecting a weight table or a roll); the casual/martial consequence routed through
  Standing (rejecting a new parallel mechanism). Each with its rejected alternative.
- [X] T013 Add ADR 0033 to `docs/README.md`'s index.

## Phase 6 — Verification

- [X] T014 `grep -rn "Standing" design/` and confirm every hit resolves within a document that
  also defines the term — no remaining dangling reference. [SC-001]
- [X] T015 Read `docs/design/16-session.md`'s Upkeep step cold, with no other document open; confirm
  every term it uses resolves within `design/`. [SC-003]
- [X] T016 `grep` the touched files for setting/system vocabulary and tonal register; confirm
  none. [FR-008]
- [X] T017 Run `python3 tools/check_gear.py specs/023-standing-material-economy/example-gear.yaml`
  — must pass. [SC-002]
- [X] T018 Run `python3 tools/check_docs.py` — must pass.
- [X] T019 Run `python3 tools/backlog.py check` — must pass.

## Dependencies

Phase 1 (schema/validator) before Phase 3's gear-schema claim in the design doc (T008 cites
`check_gear.py`, so the script must exist first). Phase 2 (Standing) is otherwise independent of
Phase 3/4 and could run in parallel, but Phase 3's coin definition (T009) depends on Standing
already being defined (T005/T006), since it's specified in relation to it. Phase 4 depends on
Phase 2/3 completing (the casual/martial consequence in T011 references Standing). Phase 5 (ADR)
follows once all load-bearing decisions in Phases 2-4 are fixed text. Phase 6 last.
