# Implementation Plan: Move the design documents under doc/ and settle numbering

**Branch**: `033-doc-move-and-numbering` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

## Summary

`git mv design/*.md` (renumbered flat, per data-model.md's mapping) into `docs/design/`;
`git mv docs/adr/` into `docs/adr/` (numbers unchanged); `git mv docs/README.md` to
`docs/README.md`. Rewrite every relative link inside the moved tree (parsed and substituted via a
mapping table, never blind find-and-replace) plus `README.md`, `CLAUDE.md`, and every
`design/`-referencing line in `tools/*.py`. Update every currently-open GitHub issue citing a
`design/` path. Retarget `tools/check_docs.py`'s `HUB`/`ADR_INDEX` constants at the new root.
Record the ADR-link-repair policy as a new ADR.

## Technical Context

**Language/Version**: Python 3.11+, standard library only

**Primary Dependencies**: `gh` CLI for the open-issue rewrite step

**Storage**: the repository's own files; no other state

**Testing**: `tools/test_check_docs.py` (existing, retargeted), plus a grep-based
corruption-detection pass (FR-009) run once at the end of implementation, not committed as an
ongoing test — it is a one-time verification of this migration, not a recurring check

**Target Platform**: local git working tree

**Project Type**: documentation/repository-structure change; the one script this feature keeps
(`tools/check_docs.py`, retargeted) already exists

**Constraints**: no unverified bulk find-and-replace (FR-009); every move via `git mv` (FR-010);
`specs/*/*.md` path tokens repaired, prose untouched (FR-008)

**Scale/Scope**: 30 design documents + 37 ADRs + 1 hub file moved; ~20 live-reference lines
across `README.md`/`CLAUDE.md`/`tools/` rewritten; 24 open issues updated

## Constitution Check

- **Nothing unpublishable** — pure reorganization of already-public design prose. **Pass.**
- **No setting or system names in `design/`/`README.md`** — this feature renames files and
  rewrites paths; it does not touch prose content. **Pass.**
- **Deterministic over inference** (`docs/design/27-tooling.md` — soon `docs/design/27-tooling.md`) —
  the old→new mapping is a fixed table (data-model.md), substitution is scripted and verified by
  grep, not asserted by eye. **Pass.**
- **Accepted ADRs never edited** — this feature's own Clarifications settle that a *path inside*
  an ADR is repairable without touching its reasoning; recorded as a new ADR per FR-012, not
  asserted informally. **Pass, by the recorded decision.**
- **Documentation-only, Spec Kit gate exempt for the move itself** (per the issue's own
  Constraints) — this plan still goes through the cycle because the link-check retargeting and
  the ADR-link policy are worth the same rigor, not because the gate requires it.
- **Git history followable** (FR-010) — `git mv` throughout. **Pass.**

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/033-doc-move-and-numbering/
├── plan.md, spec.md, research.md, data-model.md, quickstart.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
doc/
├── README.md                    # was docs/README.md
├── design/
│   ├── 01-principles.md         # ... through 30-journeys.md, per data-model.md's mapping
│   └── ...
└── adr/
    ├── 0001-resolution.md       # ... through 0037-..., numbers unchanged
    ├── ...
    └── superseded/

README.md                        # rewritten: design/... -> docs/design/... or docs/adr/...
CLAUDE.md                        # same
tools/check_docs.py              # HUB/ADR_INDEX retargeted at doc/
tools/*.py                       # every other design/ reference rewritten
docs/adr/0038-...-adr-link-repair.md   # new ADR recording the link-repair policy (FR-012)
```

**Structure Decision**: `design/` is retired entirely; `docs/design/` and `docs/adr/` are its
replacement, siblings under a new `doc/` root. No new script is written — `tools/check_docs.py`
is retargeted, per research.md's decision not to duplicate an existing checked mechanism.

## Complexity Tracking

*No violations — table omitted.*
