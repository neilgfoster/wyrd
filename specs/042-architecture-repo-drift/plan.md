# Implementation Plan: Fix 02-architecture.md's repo table, naming and stale layout trees

**Branch**: `042-architecture-repo-drift` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Correct `docs/design/02-architecture.md`'s repo table (add `wyrd-setting-template` and
`wyrd-research`, fix `wyrd-<setting>` → `wyrd-setting-<name>`) and its two "Inside each
repository" trees, verified against fresh clones of the real `wyrd-setting-template` and
`wyrd-chronicle-template` repos rather than assumed. One real finding (a stale entity-type
vocabulary in `wyrd-setting-template`, predating `25-entities.md`'s current ten-type model) is
explicitly out of scope — it's drift in a different repository this one doesn't own.

## Technical Context

**Language/Version**: N/A — Markdown design document only

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`; the trees
themselves were verified by direct `find` comparison against fresh clones of
`wyrd-setting-template` and `wyrd-chronicle-template`.

**Constraints**: Must not alter `25-entities.md`'s entity model to match a stale template repo
(FR-007). No ADR — factual correction, no alternative rejected.

**Scale/Scope**: One repo table, two file trees, one `doc/`→`docs/` fix, one `engine/`
does-not-exist-yet note.

## Constitution Check

- **No setting or system names** — repo names (`wyrd-setting-template` etc.) are the engine's own
  fleet naming, not a setting/system name. PASS.
- **Deterministic over inference** — verified against real cloned repos, not asserted from
  memory. PASS.
- **No ADR needed** — factual correction against observed reality, no alternative rejected. PASS.

No violations.

## Project Structure

```text
specs/042-architecture-repo-drift/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md

docs/design/02-architecture.md   # repo table + two file trees corrected
```

## Complexity Tracking

*(empty — no constitution violations)*
