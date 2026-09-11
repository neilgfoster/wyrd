# Implementation Plan: Chronicle load-tier resolution and recap.md

**Branch**: `123-chronicle-load-tiers` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/123-chronicle-load-tiers/spec.md`

## Summary

Add the always-tier query and `recap.md` regeneration that `engine/wyrd/session.py`'s
`run_close` deliberately left as an injected step ("out of scope here" per that module's own
docstring, pending "the chronicle/campaign state layer"). A new module queries the entity set
already loadable via `entity.load_set`/`resolve_entity` for the player character (`role: player`),
with-party companions (`role: companion`, `status: with-party`), and hot threads (`type: thread`,
`heat >= 3`), alongside `chronicle.yaml` and `recap.md` themselves — no manifest, purely a query
re-run each time. A companion function generates `recap.md`'s text from that same entity set plus
`chronicle.yaml`, and is passed into `session.run_close` as one of its steps.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: none — standard library only, reusing `wyrd.entity` and `wyrd.state`

**Storage**: reads the existing per-chronicle entity files and `chronicle.yaml`; writes only
`recap.md` (plain text/markdown, atomic write matching `state.py`'s existing convention)

**Testing**: stdlib `unittest` (`tests/engine/test_loadtier.py`), per docs/design/27-tooling.md
§6 (no pytest)

**Target Platform**: wherever the engine runs (CLI/library, no server component)

**Project Type**: library module within `engine/wyrd/`

**Performance Goals**: N/A — one chronicle's entity set is at most a few hundred files; the
always-tier query and recap generation run at most once per session boundary

**Constraints**: tier membership computed fresh from current entity state only, never cached in
a manifest (FR-002); `recap.md` write is atomic (old-or-new content only); standard library only;
ruff-clean (E/F/I/UP, line length 100)

**Scale/Scope**: one chronicle's entity set per call; `recap.md` itself stays near 200 words
regardless of chronicle size, since it names only the three hottest threads

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates come from `CLAUDE.md` and the accepted ADRs:

- **No setting/system names, descriptive English labels**: all vocabulary here (`player
  character`, `with-party`, `thread`, `heat`, `recap`) is already the engine's own terminology
  from docs/design/22-state.md and docs/design/25-entities.md; nothing new is introduced. PASS.
- **Tone is a setting property**: `recap.md`'s generated prose is short factual statements (where,
  when, what changed, who's present) with no register baked in — the same neutral tone the
  design doc's own example implies. PASS.
- **Deterministic over inference** (ADR 0005): tier membership is an exact query over `role`,
  `status` and `heat` fields — no inferred judgment calls. `recap.md`'s content list (FR-007) is
  fixed; only prose phrasing is generated text, and that generation is deterministic given the
  same entity state (no randomness, no LLM call inside the engine layer). PASS.
- **Rule changes apply forward only**: not applicable — this feature reads current state only,
  recomputing recap.md fresh at each close rather than reinterpreting history. PASS.
- **Nothing unpublishable enters this repository**: no source-derived content. PASS.
- **Capability change goes through the Spec Kit cycle**: this plan is that cycle. PASS.

No violations; Complexity Tracking section is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/123-chronicle-load-tiers/
├── plan.md              # This file
├── research.md           # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output
└── tasks.md              # Phase 2 output (speckit-tasks -- not created here)
```

### Source Code (repository root)

```text
engine/wyrd/
├── loadtier.py           # new: always_tier(), on_demand lookup/search, generate_recap()
├── entity.py             # unchanged reader/resolver this module builds on
├── session.py            # wires generate_recap() into run_close() as an injected step
└── state.py              # unchanged; recap.md write reuses its atomic-write helper

tests/engine/
└── test_loadtier.py      # new
```
