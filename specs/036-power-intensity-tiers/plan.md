# Implementation Plan: Optional intensity tiers for a system of power

**Branch**: `036-power-intensity-tiers` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/036-power-intensity-tiers/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add an optional `intensity_tiers` field to the systems-of-power schema
(`docs/design/09-systems-of-power.md`) so a setting can declare that framing an invocation more
ambitiously costs more and risks more Taint on an Ill Omen, without disturbing the existing
flat-cost behaviour for a setting that doesn't declare any tiers. `tools/check_power_systems.py`
gains matching validation for the new field, reusing its existing rejection shape (missing field,
bad value, one problem line per fault) rather than inventing a new validation style.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (`docs/design/27-tooling.md` §2 — no
third-party dependency; `check_power_systems.py` already carries its own restricted YAML reader
rather than importing one)

**Primary Dependencies**: None beyond the standard library

**Storage**: N/A — the artefact is a markdown design document plus a Python validation script; a
setting's own `power.yaml` is the data this validates, not something this repository stores

**Testing**: The embedded `self_test()` pattern `check_power_systems.py` already uses (fixture
YAML strings, `assert`, run via `python3 tools/check_power_systems.py` with no path argument) —
this feature extends that self-test, it does not introduce `pytest` or a separate test runner
for this file, matching every other `tools/check_*.py` script in the repository

**Target Platform**: Linux/CI, run via `python3 tools/check_power_systems.py <path>` — same as
today

**Project Type**: Single project — a design-document change plus one validation script change

**Performance Goals**: N/A — validation runs against a handful of setting files, well under any
meaningful threshold

**Constraints**: Must not change `strain_cost`/`resolve_cost`/`ill_omen_taint`'s existing
required/default semantics (FR-008); must not regress validation of a `power.yaml` with no
`intensity_tiers` field (FR-003, FR-006)

**Scale/Scope**: One design document section, one optional schema field, one validation function
extension, one worked example, self-test fixtures for the four malformation classes in User
Story 3

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are drawn from `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repository** — N/A; no source text, no setting content.
- **No setting or system names in `docs/design/` or `README.md`** — `intensity_tiers`, `label`,
  `difficulty`, `cost_multiplier`, `ill_omen_taint_bonus` are descriptive English, not borrowed
  from any source system. `label` is deliberately free text so a setting supplies its own words
  (e.g. minor/moderate/major) via its `rename:`/data layer, not the engine.
- **Tone is a setting property** — the worked example reuses the engine's existing register
  (ember-craft), no tone baked into the mechanic's description.
- **Deterministic over inference** ([ADR 0005](../../docs/adr/0005-deterministic-over-inference.md)) —
  cost and Taint-bonus arithmetic (`base * cost_multiplier`, `base + ill_omen_taint_bonus`) is
  exact integer/number arithmetic, stated in the doc and asserted in the self-test, not left to
  GM inference.
- **Rule changes apply forward only** — N/A; no existing character or setting declares
  `intensity_tiers` yet (spec Assumptions), so there is nothing retroactive to apply.
- **Design documents rewritten in place** — `14-systems-of-power.md` is edited in place, no
  changelog language added.
- **Capability change → Spec Kit cycle, `specs/<feature>/` committed** — this plan satisfies
  that; this is a schema/behaviour change, not documentation-only, so the docs-only exemption
  does not apply (this is exactly the earlier PR #127 mistake being corrected).
- **One configurable power mechanism** ([ADR 0036](../../docs/adr/0036-one-configurable-power-mechanism.md)) —
  `intensity_tiers` does not add a second power mechanism; it is additional shape *within* the
  single existing mechanism (still one schema, one resolution path, no power-specific dice or
  second table — reaffirmed explicitly in FR-007).

No violations. Gate passes.

## Project Structure

### Documentation (this feature)

```text
specs/036-power-intensity-tiers/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

No `contracts/` — this feature has no external API/CLI surface beyond
`tools/check_power_systems.py`'s existing argv/exit-code contract, which is unchanged (same
invocation, same JSON/text output shapes, one more field it can flag).

### Source Code (repository root)

```text
docs/design/
└── 14-systems-of-power.md      # schema table + intensity_tiers section + worked example

tools/
└── check_power_systems.py      # REQUIRED_FIELDS/OPTIONAL_FIELDS unchanged; new tier-validation
                                 # function; extended self-test fixtures; resolution_trace()
                                 # extended to accept an optional tier
```

**Structure Decision**: Single project, matching every other `tools/check_*.py` +
`docs/design/*.md` pair in this repository (e.g. `check_gear.py` / `13-gear-and-encumbrance.md`,
`check_bestiary.py` / `06-the-adversary.md`). No new directories.

## Complexity Tracking

*No violations — table omitted.*
