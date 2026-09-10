# Implementation Plan: Setting Overrides Mechanism

**Branch**: `118-setting-overrides-mechanism` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/118-setting-overrides-mechanism/spec.md`

## Summary

Implement the engine-side override mechanism docs/design/27-tooling.md section 4 and
docs/design/24-authoring-a-setting.md's "Rules overrides" describe but nothing in `engine/wyrd/`
yet does: a closed, `describe --overridable`-published set of what a setting may disable, rename,
retune (`tables:`) or extend; validation that rejects an override naming anything outside that
set as a load error; and three-layer resolution (engine defaults → setting overrides → chronicle
houserules, last wins, narrowing-only). `#315` (setting.yaml loader) already parses and passes
through the `overrides:` block unvalidated -- this feature is exactly the validation and
resolution that block was deliberately left without.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (docs/design/27-tooling.md section 2).

**Primary Dependencies**: None -- no third-party YAML, no plugin/hook mechanism.

**Storage**: N/A (a resolved configuration is computed in-process; persisting it into a
chronicle's bootstrap state is out of this feature's scope -- the mechanism, not chronicle
wiring).

**Testing**: `unittest` (stdlib), matching every existing `engine/` and `tools/` test module.

**Target Platform**: The `wyrd` CLI (`engine/wyrd/client.py`), invoked by a GM or the model
driving it.

**Project Type**: Library/CLI (single project; this repo has no frontend/backend split).

**Performance Goals**: N/A -- resolution runs once per CLI invocation over small, in-memory data.

**Constraints**: Declarative only (no setting-supplied code); an override outside the closed set
is a load error, never a silent no-op or warning; a rename must never reach stored state.

**Scale/Scope**: The closed overridable set starts with the mechanisms already wired for
setting-facing override in the current engine -- Taint and Trauma (disable/rename) and the four
oracle-prompt table families plus `skills` (tables/extend), per `docs/design/15-oracle-prompts.md`'s
own worked example. Growing the set to cover further mechanisms (critical tables, careers, gear,
creatures) is a follow-on, tracked by adding entries to `overrides.OVERRIDABLE` as those
mechanisms' own setting-facing paths land -- not a gap in this feature's own scope, since the
issue's Definition of Done is the mechanism, not universal coverage on day one.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, checked against `CLAUDE.md` and the accepted ADRs:

- **No setting or system names.** `overrides.py`, its tests, and this plan name no setting or
  system -- checked by grep before commit.
- **Deterministic over inference** (ADR 0005). Resolution and validation are pure functions over
  the three layers' data; nothing here is inferred by a model at runtime.
- **Declarative only.** No hook or plugin path is introduced; a setting supplies only data the
  closed set recognises.
- **Capability change → Spec Kit cycle.** This plan, spec, data-model, quickstart and tasks are
  all committed under `specs/118-setting-overrides-mechanism/`.
- **No duplicate YAML reader.** The engine's own restricted reader (`state.parse_yaml`) is
  extended (flow-style `[...]`/`{...}` of scalars) rather than a second one being written;
  `tools/check_bestiary.py`'s reader gets the same, narrow extension for the same reason, since
  engine/ and tools/ are already independent layers by design (`state.py`'s own docstring) and
  neither may import the other.

No violations requiring the Complexity Tracking table.

## Project Structure

### Documentation (this feature)

```text
specs/118-setting-overrides-mechanism/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
└── tasks.md              # Phase 2 output
```

### Source Code (repository root)

```text
engine/wyrd/
├── overrides.py          # NEW -- closed set, validation, three-layer resolution, catalog filter
├── catalog.py             # + "track" tool entry, tagged with `mechanisms`
├── verbs.py                # + track() verb
├── client.py                # + `describe --overridable`/`--setting`/`--chronicle`, `track` subcommand
├── render.py                 # + text rendering for `describe --overridable` and `track`
└── state.py                   # + flow-style `[...]`/`{...}` scalar-collection parsing

tools/
├── check_setting.py       # `overrides:` block now validated via wyrd.overrides.validate_block
└── check_bestiary.py       # same flow-style parsing extension, mirrored for the tools-side reader

tests/engine/
├── test_overrides.py       # NEW
├── test_verbs.py             # + TrackVerbTest
├── test_client.py             # + OverridableTest
└── test_state.py               # + FlowStyleCollectionTest

tools/
└── test_check_setting.py    # NEW -- first test coverage for check_setting.py at all
```

**Structure Decision**: Single project, matching the rest of `engine/wyrd/`. No new top-level
directory; the mechanism is one new module (`overrides.py`) plus small, additive touches to the
existing catalog/verb/CLI/render/state modules the same way every prior engine feature has landed.
