# Implementation Plan: Omen carryover across a proposed batch

**Branch**: `196-omen-carryover` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add an "Omen carryover" section to `docs/design/31-action-resolution.md`: a `pending_omen` field
on the actor's persistent state (new — added to `22-state.md`'s player-character frontmatter,
since nothing prior needed it) carries an Ill/Fair Omen across committed proposals; within one
batch, a step consuming another step's Omen records that as a `depends_on` edge, reusing
cascading resolution's/partial reroll's existing mechanism rather than inventing a new one. A
worked example (real seeded rolls, a two-roll batch, then a reroll of the Omen-producing step)
shows the modifier applying correctly and unwinding correctly — the consuming step's second
result genuinely differs, not just relabelled.

## Technical Context

**Language/Version**: N/A — design specification; no code implemented here.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`.

**Constraints**: Reuses #194/#195's `depends_on` mechanism (FR-005, FR-006) — no new reroll
logic. Reading `pending_omen` must not consume it until commit (FR-004), consistent with #193's
staging model.

**Scale/Scope**: One new section in `docs/design/31-action-resolution.md`; one new field in
`docs/design/22-state.md`'s player-character frontmatter.

## Constitution Check

- **No ADR** — consumes the already-specified `depends_on` mechanism; the Omen rule itself is
  unchanged, only how the engine tracks it, which follows directly from #193's staging model.
  PASS.
- **Design documents rewritten in place** — the new section extends the same growing document;
  `22-state.md`'s schema gap is fixed in place, not left stale. PASS.
- **Deterministic over inference** — the worked example uses real seeded rolls, including honest
  outcomes (a reroll producing no Omen at all, changing the downstream result). PASS.
- **Setting-agnostic** — no setting or system name introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/069-omen-carryover/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/31-action-resolution.md   # new "Omen carryover" section
docs/design/22-state.md               # new pending_omen field
```

## Complexity Tracking

*(empty — no constitution violations)*
