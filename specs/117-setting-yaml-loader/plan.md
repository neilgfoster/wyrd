# Implementation Plan: setting.yaml loader and validator

**Branch**: `315-setting-yaml-loader` | **Date**: 2026-09-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/117-setting-yaml-loader/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a `setting.yaml` reader/validator, following the existing `tools/check_bestiary.py` /
`tools/check_gear.py` pattern exactly: a small internal restricted-YAML reader, a schema of
required/optional fields and closed vocabularies, a `validate(...)` function reporting every
problem (not just the first), and a `tools/check_setting.py` CLI entry point. `check_gear.py`
already imports `read_yaml`/`YamlError` from `check_bestiary.py` rather than duplicating a parser —
`check_setting.py` reuses that same shared reader the same way, keeping one restricted-YAML
implementation in `tools/` rather than three.

## Technical Context

**Language/Version**: Python 3.11+ (repo-wide constraint, CLAUDE.md / docs/design/27-tooling.md)

**Primary Dependencies**: None — standard library only, reusing `tools/check_bestiary.py`'s
`read_yaml`/`YamlError` restricted-subset YAML reader (the same way `check_gear.py` already does)
rather than adding a new parser or a third-party YAML dependency.

**Storage**: N/A — reads a single YAML file passed as a path argument; no state written.

**Testing**: `pytest`, run via `PYTHONPATH=engine python3 -m pytest -q` per repo convention (see
`wyrd-architecture-reconciliation-in-progress` memory) — though this feature's own tests live
under `tools/` alongside the sibling `check_bestiary.py`/`check_gear.py`, which have no dedicated
test files today and are instead exercised by hand against known-good/known-bad fixtures per their
own docstring `Usage:` sections. This feature follows that precedent: manual fixture runs
documented in `quickstart.md`, matching how `check_bestiary.py`/`check_gear.py` are verified today.

**Target Platform**: Linux CLI (matches the rest of `tools/`)

**Project Type**: CLI / library — a stdlib-only validation script, matching `check_bestiary.py`

**Performance Goals**: N/A — a single small file read and validated once per invocation; no
performance target beyond "instant" at this scale.

**Constraints**: stdlib-only, zero-dependency (CLAUDE.md, docs/design/27-tooling.md section 2);
ruff-clean, line length 100 (`pyproject.toml`); every validation failure reported, not just the
first (matching `check_bestiary.py`'s own stated design).

**Scale/Scope**: One file (`tools/check_setting.py`), reusing an existing shared reader. No new
directories, no engine runtime changes — `setting.yaml` runtime loading at chronicle bootstrap
(actually reading a setting into a running chronicle) is explicitly out of scope here; this
feature is the setting-authoring-time validator, matching the existing `check_bestiary.py` /
`check_gear.py` precedent. That runtime bootstrap path belongs to the separate "Chronicle
bootstrap" epic (#304) when it is decomposed.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Nothing unpublishable enters this repository**: satisfied — no source text, no setting
  content, only a validator against a documented schema. PASS.
- **No setting or system names in design/ or README.md**: satisfied — this is `tools/` code, not
  `docs/design/`; the schema it validates is already generic (`line: fantasy` in the design doc is
  the engine's own worked example, not a borrowed system name). PASS.
- **Tone is a setting property, never baked into a mechanic** (ADR 0004): satisfied — the
  validator only checks that a `tone:` block exists and uses the engine's own closed vocabulary
  for each axis; it does not interpret or bake in any particular tone. PASS.
- **Deterministic over inference** (ADR 0005): satisfied — this entire feature is a deterministic
  script; nothing here is inferred. PASS.
- **Rule changes apply forward only**: N/A — no state mutation, no rule change.
- **Design documents describe the present; ADRs are immutable**: N/A — no design doc or ADR is
  being edited by this feature. If `docs/design/24-authoring-a-setting.md` needs a cross-reference
  to `tools/check_setting.py` added (the way it already references `check_bestiary.py`), that is
  an in-place edit to the existing present-tense description, not a new document.
- **Capability changes go through the Spec Kit cycle, `specs/<feature>/` committed**: satisfied —
  this plan.

No violations. Complexity Tracking table is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/117-setting-yaml-loader/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

No `contracts/` directory — this is a stdlib CLI validator with no external API surface (matching
`check_bestiary.py`/`check_gear.py`, neither of which has one either).

### Source Code (repository root)

```text
tools/
├── check_bestiary.py    # existing; source of the shared read_yaml/YamlError reader
├── check_gear.py         # existing; already imports read_yaml/YamlError from check_bestiary
└── check_setting.py      # NEW: this feature — imports read_yaml/YamlError from check_bestiary,
                           # defines the setting.yaml schema, validate(), and the CLI entry point
```

**Structure Decision**: Single new file in `tools/`, following the `check_gear.py` precedent of
importing the shared reader from `check_bestiary.py` rather than adding a new module under
`engine/wyrd/`. No change to `engine/wyrd/` — runtime setting-loading at chronicle bootstrap is a
separate, later feature (out of scope here, see Scale/Scope above).

## Complexity Tracking

*No violations — table not needed.*
