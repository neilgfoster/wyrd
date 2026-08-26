# Implementation Plan: Career graph — skill counts and succession

**Branch**: `035-career-graph` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/035-career-graph/spec.md`

## Summary

Define, in the design documents, what a career declares (identifier, skill list, entry-point
flag, and — for a non-entry career — a single prerequisite career) and what "completing" a
career means (every skill it grants opened and raised to the career's cap). Correct the dead
cross-reference in `05-character-creation.md` to point at the real home for this structure —
`26-authoring-a-setting.md`, where `careers.yaml`'s shape already lives — rather than
`27-entities.md`, since a career is a lookup-table row, not one of the ten entity types.
Documentation-only; no code changes.

## Technical Context

**Language/Version**: N/A — Markdown design documents (Obsidian vault, per `27-entities.md`)

**Primary Dependencies**: N/A

**Storage**: N/A — no `careers.yaml` schema validator is in scope (FR-009); this defines the
shape a future validator would check, not the validator itself

**Testing**: `python3 tools/check_docs.py` (reachability/dead-link check); manual proof that a
worked example (an entry career and a dependent non-entry career) resolves eligibility and
completion with no remaining ambiguity

**Target Platform**: N/A — documentation

**Project Type**: Documentation (design decision, per `CLAUDE.md`'s Spec Kit gate: capability
changes go through the cycle, documentation-only changes are exempt from *requiring* it, but
this one already entered the cycle via issue #118 and stays in it)

**Performance Goals**: N/A

**Constraints**: No setting or system names in `docs/design/` (`CLAUDE.md`); no new entity type
introduced (`27-entities.md` closes its list at ten, "a new type is an engine change, never a
setting one")

**Scale/Scope**: Two design documents touched (`27-entities.md` is confirmed to stay untouched
per the home decision below; the graph structure lands in `26-authoring-a-setting.md` instead),
plus the cross-reference fix in `05-character-creation.md`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **No setting/system names** — the design uses only descriptive English (`career`, `entry
  career`, `prerequisite`, `completion`), all already in use in the corpus. Pass.
- **No new entity type** — careers stay a lookup-table row (`careers.yaml`), consistent with
  `26-authoring-a-setting.md`'s existing classification alongside gear, names, and the
  bestiary. Confirmed in Phase 0 research (below) rather than assumed. Pass.
- **Design documents rewritten in place** — `26-authoring-a-setting.md` and
  `05-character-creation.md` are edited to describe the present structure; no changelog or
  "previously" language added. Pass.
- **Deterministic over inference** — completion and eligibility are both defined as checkable
  facts (every career-granted skill at cap; prerequisite career complete), not GM judgment
  calls. Pass.
- **Nothing unpublishable** — no source-system text or names introduced. Pass.

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/035-career-graph/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

No `contracts/` directory: this feature has no external interface (API, CLI, or otherwise) — it
defines a data shape inside a setting-authored YAML lookup table, documented in prose, not a
contract another system programmatically consumes yet (FR-009 keeps a validator out of scope).

### Source Code (repository root)

Documentation-only change. No `src/`, `tests/`, or other code tree is affected.

```text
docs/design/
├── 05-character-creation.md   # cross-reference corrected (FR-007)
└── 26-authoring-a-setting.md  # careers.yaml shape defined per the decided structure (FR-001–FR-006, FR-008)
```

**Structure Decision**: Single documentation change set under `docs/design/`. `27-entities.md`
is deliberately left untouched (see Phase 0 research) — careers are not promoted to an entity
type.

## Complexity Tracking

Not applicable — no Constitution Check violations.
