# Implementation Plan: Related settings — shared worlds and kindred tone

**Branch**: `145-related-settings-kinship` | **Date**: 2026-09-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/145-related-settings-kinship/spec.md`

## Summary

`settings.yaml` gains a `relations:` list — pairwise, typed (`same-world` | `kindred-tone`) —
alongside the existing flat `settings:` catalogue, replacing the currently-inert `group:` field
with the same-world half of this mechanism. `tools/check_settings_catalogue.py` gains validation
that every relation names two distinct, existing settings, that no pair is declared both ways at
once, and (since a relation is recorded once but implies both directions) that it is read as
symmetric rather than needing to be written twice. `docs/design/24-authoring-a-setting.md` gains a
section on what a same-world versus kindred-tone relation licenses when borrowing content, and the
existing conversion provenance convention (`converted: {rules, on}`) is extended with a parallel
`borrowed: {from_setting, from_entity, relation, on}` stamp for the entity being carried across
settings — recorded in that design document as a schema entities MUST carry, not implemented
against any specific entity type here (no bestiary/gear entity schema exists to attach it to yet
outside the settings this feature does not touch).

## Technical Context

**Language/Version**: Python 3.11 (matches every other `tools/*.py` script; `pyproject.toml`
pins ruff's target to 3.11)

**Primary Dependencies**: None — standard library only, per `docs/design/27-tooling.md` §2 (no
third-party YAML dependency; `settings.yaml` is read with the same restricted-subset parser
`check_settings_catalogue.py` already uses)

**Storage**: `settings.yaml` (flat file, checked into this repository) — no database

**Testing**: `tools/check_settings_catalogue.py`'s existing invocation pattern
(`python3 tools/check_settings_catalogue.py`); the parser and validation additions are exercised by
extending that script's own fixtures/assertions, following the pattern every `tools/check_*.py`
script in this repo already uses (no separate test framework is present in `tools/`)

**Target Platform**: This repository's own tooling (`tools/`), run locally by a setting author or
by `python3 tools/backlog.py check`-style drift checks — not a runtime service

**Project Type**: Single project — a CLI-checked data schema plus its design documentation, matching
every existing `tools/check_*.py` + `docs/design/*.md` pair in this repo

**Performance Goals**: N/A — a one-shot local check over a file with, at present, on the order of
tens of settings and relations; no scale target applies

**Constraints**: Must not require `gh` for the new relation-consistency checks (those checks are
pure local-file consistency, unlike the existing fleet-drift check, which does call `gh`) — keeping
the fast, offline part of the check fast and offline

**Scale/Scope**: Sixteen settings today, a handful of relations; the schema must not assume a
ceiling on either

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are evaluated against `CLAUDE.md` and the accepted
ADRs:

- **Nothing unpublishable enters this repository.** PASS — this feature adds only a schema and a
  checker; the settings it will eventually be used to relate are named by id (already public in
  `settings.yaml`), and no setting's private content is touched.
- **No setting or system names in `docs/design/` or `README.md`.** PASS — the new design section
  and the relation types (`same-world`, `kindred-tone`) are descriptive English, not borrowed from
  any source system. Existing setting ids already appear in `settings.yaml` (outside `docs/design/`),
  which this feature does not change.
- **Tone is a setting property ([ADR 0004](../../docs/adr/0004-tone-belongs-to-the-setting.md)).**
  PASS — FR-003 explicitly declines to derive kinship from the tone contract automatically, for the
  reason ADR 0004 already establishes: tone dimensions are categorical, not a distance metric, so
  deriving a threshold would itself be inventing a false precision the contract doesn't support.
- **Deterministic over inference ([ADR 0005](../../docs/adr/0005-deterministic-over-inference.md)).**
  PASS — every claim this feature makes checkable (relation symmetry, unknown-id references,
  same-pair double-declaration) is checked by `check_settings_catalogue.py`, not asserted in prose.
- **Capability changes go through the Spec Kit cycle; `specs/<feature>/` is committed.** PASS — this
  plan.

No violations; the Complexity Tracking table below is empty.

## Project Structure

### Documentation (this feature)

```text
specs/145-related-settings-kinship/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks — not created here)
```

### Source Code (repository root)

```text
settings.yaml                              # gains `relations:`; `group:` retired in favour of it
docs/design/24-authoring-a-setting.md      # gains: relation types, borrow semantics, borrowed: stamp
tools/check_settings_catalogue.py          # gains: relation parsing + consistency checks
```

No `contracts/` directory: this feature has no network or process boundary — its one interface is
the `settings.yaml` schema itself, specified in `data-model.md`, and the checker's exit code /
error text, which `quickstart.md` documents directly rather than duplicating a contracts file for
a single local file format.

**Structure Decision**: Single project, matching this repository's existing shape — a design
document under `docs/design/`, a data file at the repo root, and a stdlib-only checker under
`tools/`. No new top-level directory is warranted for one schema addition.

## Complexity Tracking

*No violations — table intentionally empty.*
