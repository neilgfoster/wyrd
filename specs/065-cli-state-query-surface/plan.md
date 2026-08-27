# Implementation Plan: Design the CLI's state-loading and querying surface, and the three memory tiers

**Branch**: `187-cli-state-query-surface` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Expand `02-architecture.md`'s "Memory tiers" and "Code versus prose" (CLI sketch) sections to
specify concrete commands backing each tier: `wyrd session-context` for Always-loaded,
`wyrd get`/`wyrd find` (plus named conveniences `wyrd party`/`wyrd threads`/`wyrd threats`) for
On-demand, and `wyrd log` for Archival. All return structured output, matching `wyrd roll`'s
existing precedent. Full-text search over Archival is explicitly deferred, with a stated reason.
`22-state.md`'s player-character frontmatter example is corrected for two already-landed rules
changes it predates (Luck merged into Fortune; Resolve's cap is now computed, not stored).

## Technical Context

**Language/Version**: N/A — this is a design specification (`docs/design/` content); no code is
implemented here.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`.

**Constraints**: Setting-agnostic; stdlib-only Python per `27-tooling.md` if any future
implementation detail is specified beyond command shape (none needed here). A real rejected
alternative earns an ADR.

**Scale/Scope**: `02-architecture.md`'s Memory tiers and CLI sketch sections; `22-state.md`'s
player-character frontmatter example (a small, directly-touched correction).

## Constitution Check

- **A real rejected alternative, someone would re-propose it** — see Complexity Tracking; no ADR
  needed, this specifies a mechanism already implied by existing "query, not manifest" language
  rather than choosing between two workable designs. PASS.
- **Design documents rewritten in place** — `02-architecture.md`'s existing sections are
  expanded in place, not appended with a changelog note. PASS.
- **Setting-agnostic** — no setting or system name introduced. PASS.
- **Deterministic over inference** — all commands specified return structured, queryable output;
  none rely on inference at the CLI layer (that stays a GM-contract/prose concern). PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/065-cli-state-query-surface/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/02-architecture.md   # Memory tiers section, CLI sketch expanded
docs/design/22-state.md          # player-character frontmatter example corrected
```

## Complexity Tracking

*(empty — no constitution violations; no ADR needed, since this specifies a mechanism the
existing "query, not manifest" language already implied, not a choice between two rejected
alternatives)*
