# Implementation Plan: Dread as a reaction/social test penalty

**Branch**: `101-dread-reaction-penalty` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/101-dread-reaction-penalty/spec.md`

## Summary

Reaction/social tests already resolve through the engine's `ordinary-test` mechanic
(`resolution._resolve_ordinary_test`). This feature adds one new caller-supplied field to a
`propose` request — a boolean flagging whether the witness has *not* made peace with the target's
transformation — and, when set alongside a `target` whose state carries nonzero `dread`, subtracts
that Dread from the effective chance the same way `declaration_bonus` and the difficulty ladder
already stack. No new mechanic, no new persistent state; `dread` is read, never written, by this
feature.

## Technical Context

**Language/Version**: Python 3.11+ (stdlib-only)

**Primary Dependencies**: None new — extends `engine/wyrd/resolution.py`, `verbs.py`, `client.py`,
`catalog.py`

**Storage**: Character/companion frontmatter files on disk (existing `dread` field), read-only for
this feature

**Testing**: `pytest`, run under `PYTHONPATH=engine`

**Target Platform**: CLI / library, cross-platform (no OS-specific behaviour)

**Project Type**: Single project — `engine/wyrd` library plus its `wyrd` CLI

**Performance Goals**: N/A — one extra arithmetic term on an existing synchronous call path

**Constraints**: stdlib-only; effective chance stays clipped to [0, 100] exactly as today; no
change to any mechanic other than `ordinary-test`

**Scale/Scope**: One request field, one resolution-path change, CLI/catalog/verbs plumbing to
match

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic over inference** (ADR 0005): the Dread penalty is a straight subtraction of an
  already-stored number; nothing here is inferred. The "has the witness made peace" judgment stays
  the GM's own call, supplied as a request field — the engine never computes it. Pass.
- **No setting/system vocabulary**: field name (`dread_witnessed` or similar) and docs stay
  descriptive English matching the existing design document's own term, "Dread". Pass.
- **Design documents describe the present**: `docs/design/07-transformations.md`'s "Dread"
  section already states this rule; no design document changes are needed, only the engine
  catching up to what it already says. Pass.
- **Capability change goes through Spec Kit**: this plan. Pass.
- **Rule changes apply forward only**: no historical state is touched; this only changes how a
  *future* test resolves. Pass.

No violations — Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/101-dread-reaction-penalty/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

No `contracts/` directory: the one external interface this touches (the `propose` CLI/verb
request shape) is small enough to fully describe inline in `data-model.md` rather than duplicating
it as a separate contract file.

### Source Code (repository root)

```text
engine/
├── wyrd/
│   ├── resolution.py     # _resolve_ordinary_test, _normalize_request, propose/propose_batch
│   ├── verbs.py          # propose() passthrough
│   ├── client.py         # CLI arg for the new propose field
│   └── catalog.py        # TOOLS schema entry for propose
└── tests/
    └── test_resolution.py (or equivalent) # new Dread-penalty cases
```

**Structure Decision**: Single project (`engine/wyrd`), extending the existing `propose` request
plumbing already shared by every mechanic — no new module.
