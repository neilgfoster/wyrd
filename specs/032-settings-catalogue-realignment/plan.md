# Implementation Plan: Realign the settings catalogue with reality

**Branch**: `032-settings-catalogue-realignment` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/032-settings-catalogue-realignment/spec.md`

## Summary

Rewrite `settings.yaml` against the fourteen live `wyrd-setting-*` repositories (correct `repo:`
names, an expressive `status:` reflecting real library/index state, an optional `group:` for
shared worlds), correct `CLAUDE.md`'s repository table to the same naming convention, and add
`tools/check_settings_catalogue.py` — a read-only drift check in `tools/backlog.py`'s shape.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (`doc/design/20-tooling.md` §2)

**Primary Dependencies**: none — `gh` CLI via `subprocess`, same as `tools/backlog.py`

**Storage**: `settings.yaml` itself; no other state

**Testing**: `stdlib unittest`, fixture-driven (no network in tests), matching
`tools/test_backlog.py`'s pattern

**Target Platform**: CLI, run by the maintainer

**Project Type**: single script extending `tools/`, plus a data file and a doc correction

**Performance Goals**: N/A — fourteen repos, well under a second either way

**Constraints**: read-only; nothing unpublishable enters the catalogue

**Scale/Scope**: fourteen settings today; the check must keep working as the fleet grows

## Constitution Check

- **Nothing unpublishable** — the catalogue already lists setting names/repos (that is its
  purpose, distinct from `design/`'s ban); this feature adds no library/corpus content. **Pass.**
- **No setting or system names in `design/` or `README.md`** — `settings.yaml` and `CLAUDE.md`
  are neither; unaffected. **Pass.**
- **Deterministic over inference** — status is read from each repo's actual `library/`/`index/`
  contents via `gh`, not asserted from memory. **Pass.**
- **Python 3.11+, stdlib only** — `gh` CLI only. **Pass.**
- **Capability changes go through Spec Kit** — this plan is that cycle; the doc corrections
  (`CLAUDE.md`, `settings.yaml` itself) are documentation/data, not capability, but ride along
  since they are what the capability (the drift check) checks against.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/032-settings-catalogue-realignment/
├── plan.md, spec.md, research.md, data-model.md, quickstart.md, tasks.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
settings.yaml                          # rewritten: correct repo:, expressive status:, group:
CLAUDE.md                              # repository table corrected to wyrd-setting-<name>
tools/
├── check_settings_catalogue.py        # drift check, backlog.py's shape
├── test_check_settings_catalogue.py   # unittest, fixture-driven
└── fixtures/settings_catalogue.json   # captured gh repo-list + settings.yaml shape for tests
```

**Structure Decision**: Single project, extending `tools/` the same way `tools/backlog.py` and
`tools/fleet_rollout.py` already do (a script, a fixture-driven test file, a fixture). No new
directory beyond that; the catalogue and `CLAUDE.md` are edited in place, not restructured.

## Complexity Tracking

*No violations — table omitted.*
