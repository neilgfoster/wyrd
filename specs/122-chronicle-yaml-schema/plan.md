# Implementation Plan: Chronicle.yaml schema, load/save and versioning

**Branch**: `122-chronicle-yaml-schema` | **Date**: 2026-09-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/122-chronicle-yaml-schema/spec.md`

## Summary

Extend `engine/wyrd/state.py`'s existing minimal chronicle-state scaffold (`schema_version` +
`last_roll`) to the full `chronicle.yaml` shape docs/design/22-state.md specifies: engine/setting
version pins (current vs. `created_under`), calendar/era/sessions/danger_rating, an append-only
`migrations` log, the bootstrap `intent` block, and an opaquely round-tripped `pending` field.
Reuses the module's existing atomic-write and restricted-YAML-subset read/write rather than a
second implementation.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: none — standard library only (`os`, `pathlib`, `re`, `tempfile`,
already used by `engine/wyrd/state.py`)

**Storage**: a single YAML file per chronicle, `chronicle.yaml`, read/written via this module's
own restricted-subset reader/writer (no third-party YAML dependency, per the module's existing
docstring and docs/design/02-architecture.md)

**Testing**: stdlib `unittest` (`tests/engine/test_state.py`, extending the existing test module) — docs/design/27-tooling.md §6: no pytest

**Target Platform**: wherever the engine runs (CLI/library, no server component)

**Project Type**: library module within `engine/wyrd/`

**Performance Goals**: N/A — a chronicle.yaml is small (well under a few KB) and read/written at
most once per session boundary; no throughput target applies

**Constraints**: atomic write (old-or-new state only, never a partial file); standard library
only; ruff-clean (E/F/I/UP, line length 100)

**Scale/Scope**: one file per chronicle; a migrations log that grows by roughly one entry per
version bump across a chronicle's whole multi-year life — dozens of entries at most

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates come from `CLAUDE.md` and the accepted ADRs:

- **No setting/system names, descriptive English labels**: this feature touches no player-facing
  vocabulary at all — `chronicle.yaml`'s field names (`engine`, `setting`, `calendar`, `intent`,
  `migrations`) are already the engine's own descriptive terms from docs/design/22-state.md. PASS.
- **Tone is a setting property**: not applicable — no tone-bearing content here. PASS.
- **Deterministic over inference** (ADR 0005): every field this feature reads/writes is an exact
  value with no inferred default beyond what docs/design/22-state.md documents explicitly (e.g.
  `era: null`). PASS.
- **Rule changes apply forward only, history never recomputed**: directly implemented by the
  append-only `migrations` log (FR-003/FR-004) — this is the feature that carries that guarantee
  for chronicle state. PASS.
- **Nothing unpublishable enters this repository**: no source-derived content anywhere in this
  feature. PASS.
- **Capability change goes through the Spec Kit cycle**: this plan is that cycle. PASS.

No violations; Complexity Tracking section is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/122-chronicle-yaml-schema/
├── plan.md              # This file
├── research.md           # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
└── tasks.md              # Phase 2 output (speckit-tasks — not created here)
```

### Source Code (repository root)

```text
engine/
└── wyrd/
    └── state.py          # extended in place: chronicle-level schema, save/load, migrations

tests/
└── engine/
    └── test_state.py     # extended in place: round-trip, versioning, migrations tests
```

**Structure Decision**: Single project (this is a library module inside the existing `engine/`
tree). No new top-level directory — `engine/wyrd/state.py` is extended, not replaced, per the
issue's own scope and the module's docstring ("Later features extend the schema; this module's
read/write contract does not change to accommodate that").
