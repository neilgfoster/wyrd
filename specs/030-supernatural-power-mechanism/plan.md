# Implementation Plan: Systems of power

**Branch**: `030-supernatural-power-mechanism` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

## Summary

Give the engine a single, configurable **system of power** declaration — the schema a setting
fills in to define supernatural or extraordinary effort — instead of a closed set of engine-side
mechanism shapes. Invoking one resolves as the engine's ordinary d100 test against a setting-owned
skill (no new dice mechanism); the declared Strain cost (and optional Resolve cost) is paid on
resolution regardless of outcome; an Ill Omen applies the declared Taint gain through the existing
transformation-threshold path. This is [ADR 0036](../../docs/adr/0036-one-configurable-power-mechanism.md)'s
load-bearing fork, made concrete as a new design document and a validator that mirrors
`check_bestiary.py`/`check_gear.py`.

## The load-bearing decision

**One schema, not a menu of shapes.** `docs/design/26-authoring-a-setting.md`'s hard rule — a setting
may extend, retune, rename or disable, never add a mechanism — already governs every other piece
of setting texture (`bestiary.yaml`, `gear.yaml`, the career graph) as one engine-defined schema
instantiated with data. A closed set of engine-side "mechanism shapes" (Vancian slots, a mana
pool, a corruption-fuelled invocation, …) would itself be several mechanisms sharing one name, and
would still leave a setting wanting a fourth shape with nowhere to put it but a fork. One schema,
general enough to carry a strain cost, an optional Resolve cost and a training gate, covers every
worked example this plan checks against without a setting ever touching engine code. See ADR 0036
for the full reasoning and the rejected alternative.

**Nothing new is added to state or resolution.** Casting is an ordinary test (`03-rules.md` §1) —
same difficulty bands, same declaration bonuses, same assistance rule, same Wyrd die. The only new
runtime behaviour is: pay the declared Strain/Resolve cost on resolution, and on an Ill Omen apply
the declared Taint gain through the transformation-table machinery `03a-3-transformations.md`
already defines. No new track, no new table family — matching the spec's Clarifications section.

## What the check script has to settle

`tools/check_power_systems.py`, stdlib only, following `check_bestiary.py`/`check_gear.py`'s
conventions exactly (same restricted YAML reader, same required/optional field split, same
unrecognised-field rejection, same failure-reporting shape — every failure reported, not just the
first).

1. **Schema validation**: `id` (kebab-case, unique), `name`, `skill`, `strain_cost` (positive
   int), `requires_training` (bool) required; `resolve_cost` (positive int) and `ill_omen_taint`
   (positive int, default 1) optional; `description` optional flavour. Rejects a missing required
   field, an unrecognised field, an out-of-range cost, and a `skill` absent from the setting's own
   `careers.yaml`-declared skill list (cross-file check, same shape `check_gear.py` already does
   nothing like but `check_bestiary.py`'s single-file closed-vocabulary checks establish the
   pattern for).
2. **Two worked examples**, embedded as test fixtures: a mythic-fantasy system of power and a
   structurally different far-future/psionic one, both validating clean against the identical
   schema — the spec's SC-003.
3. **Confirms the resolution steps make no new claim on `03-rules.md` §1** — the script asserts
   the d100/difficulty/declaration/assistance/Wyrd-die composition is unchanged, it does not
   recompute it (nothing about a power test perturbs those figures; `check_mapping.py`'s numbers
   are untouched, so this feature does not import them).

## Where the rules land

| Document | Change |
|---|---|
| `docs/design/14-systems-of-power.md` (new) | the schema: declaration, cost, training gate, Ill Omen consequence, worked example |
| `docs/adr/0036-one-configurable-power-mechanism.md` (new) | records the load-bearing fork |
| `docs/README.md` | links the new document so `tools/check_docs.py` finds it reachable |
| `docs/design/03-rules.md` | unchanged in substance — casting reuses §1 verbatim; a one-line cross-reference added at the end of §1 pointing to the new document, matching how other consequence chains are cross-referenced |
| `tools/check_power_systems.py` (new) | the validator |

## The order of work

The ADR is written first — it is what the design document and validator both have to agree with,
not something the design document's prose derives after the fact. Then `docs/design/14-systems-of-power.md`,
then `tools/check_power_systems.py` (which embeds the two worked examples the design document also
shows), then the `README.md`/`03-rules.md` cross-references, then the guards: the new validator
itself, `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, `python3
tools/backlog.py check`, and the repo-wide `ruff check . && ruff format --check . && python3 -m
pytest -q`.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only

**Primary Dependencies**: none — matches every prior `tools/check_*.py` script in this repo

**Storage**: N/A — this feature edits Markdown design documents and adds one validator script with
embedded YAML fixtures; no runtime storage

**Testing**: `tools/check_power_systems.py` itself (asserts on its own embedded fixtures), plus the
repo-wide `python3 -m pytest -q`, `python3 tools/check_docs.py`, `python3
tools/check_dangling_mechanics.py`

**Target Platform**: N/A — a design document and a CLI validator, not a deployed service

**Project Type**: documentation + CLI tooling (matches every other Wyrd rules feature)

**Performance Goals**: N/A

**Constraints**: setting-agnostic — no setting or system name in `design/` or `README.md`; every
engine label descriptive English (`CLAUDE.md`)

**Scale/Scope**: one new design document, one new ADR, one new validator with two embedded worked
examples

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `CLAUDE.md` and the accepted ADRs (per `.specify/memory/constitution.md`'s
pointer), not a separate constitution file:

- **Nothing unpublishable enters this repository.** No setting content, no spell lists, no
  source-system material — this feature is schema only. Pass.
- **No setting or system names in `design/` or `README.md`.** The new document and ADR use
  "system of power," "invocation," "backlash" — descriptive English throughout; both worked
  examples in the validator's fixtures are generic (`ember-craft`, `signal-attunement`), not named
  after any real setting or system. Pass.
- **Capability change → Spec Kit cycle, `specs/` committed.** This plan is that cycle. Pass.
- **A setting may extend, retune, rename or disable; never add a mechanism.** The entire point of
  this feature — see "The load-bearing decision" above. Pass.
- **Deterministic over inference** ([ADR 0005](../../docs/adr/0005-deterministic-over-inference.md)).
  Every claim in the design document (schema fields, cost application, Ill Omen path) is checked
  by `check_power_systems.py`, not merely asserted. Pass.
- **Design documents rewritten in place; accepted ADRs never edited.** `03-rules.md` receives a
  one-line cross-reference only, `README.md` gains a link, ADR 0036 is new and untouched
  thereafter. Pass.

No violations; Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/030-supernatural-power-mechanism/
├── plan.md               # This file
└── (no research.md/data-model.md/contracts/quickstart.md — see below)
```

No `research.md`: no NEEDS CLARIFICATION remains in Technical Context above, and the spec's own
Clarifications section already resolved every open design question with a documented default. No
`data-model.md`/`contracts/`/`quickstart.md`: this feature's one entity (system of power) is fully
specified by the new design document's schema table and the validator's field lists — the same
shape every prior Wyrd rules-with-a-schema feature (`023-standing-material-economy`,
`019-transformation-table`) has used, where the design document and check script together are the
data model and the contract.

### Source Code (repository root)

```text
design/
├── 03a-7-systems-of-power.md   # new
├── 03-rules.md                 # one-line cross-reference added at the end of §1
├── README.md                   # links the new document
└── adr/
    └── 0036-one-configurable-power-mechanism.md   # new

tools/
└── check_power_systems.py      # new validator, with two embedded worked-example fixtures
```

**Structure Decision**: matches every prior Wyrd rules feature with a data schema — a new design
document, one new ADR, a `tools/check_*.py` validator, and a `README.md` link. No `src/`, `tests/`,
or web/mobile structure applies; this is not application code.
