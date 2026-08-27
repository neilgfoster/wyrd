# Implementation Plan: Luck restoration rule

**Branch**: `034-luck-restoration-rule` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/034-luck-restoration-rule/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Luck's spend rule ("costs 1 Luck for the rest of the arc, pass or fail," `docs/design/03-rules.md`
§1) implies a reset boundary that is never stated. This feature decides that Luck resets to
maximum at the start of each top-level arc — the level `docs/design/19-campaign.md` already
singles out as having "a job the deeper ones do not" — and records the decision as an ADR, then
states the rule in `03-rules.md` itself. There is no code to write: `CLAUDE.md` exempts
documentation-only changes from anything beyond the Spec Kit cycle itself.

## Technical Context

**Language/Version**: N/A — documentation-only change to Markdown design documents

**Primary Dependencies**: N/A

**Storage**: N/A

**Testing**: `python3 tools/check_docs.py` (link/reachability check already run against all of
`docs/design/`); no new script is introduced by this feature

**Target Platform**: N/A

**Project Type**: design documentation (no source project)

**Performance Goals**: N/A

**Constraints**: Must not introduce setting/system vocabulary (`CLAUDE.md`); accepted ADRs are
never edited, only superseded

**Scale/Scope**: One design-document section (`03-rules.md` §1) plus one new ADR

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, the gates are drawn from `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repo**: PASS — no source text or copyrighted content is
  involved; this is an original engine rule.
- **No setting/system names in `docs/design/`**: PASS — "arc," "Luck," and "top-level arc" are
  already-established engine vocabulary from `03-rules.md` and `18-campaign.md`; nothing new is
  coined that reads as a borrowed term.
- **Tone is a setting property**: PASS — the rule states a mechanical reset, no register.
- **Deterministic over inference**: PASS — the rule is boolean (resets or doesn't) and the
  boundary is a level of structure `18-campaign.md` already defines, not a judgment call.
- **Rule changes apply forward only**: N/A — this is not a change to an existing, exercised rule;
  it is stating a rule that was implied but never written, so there is no history to preserve.
- **Decisions are recorded as ADRs; accepted ADRs never edited**: this feature adds one new ADR
  rather than editing any existing one. PASS.
- **Capability changes go through the Spec Kit cycle; documentation-only changes are exempt**:
  this is documentation-only, but the gap is significant enough (a standing rule contradiction)
  that running the full cycle anyway is proportionate — no violation either way.

No violations requiring the Complexity Tracking table.

## Project Structure

### Documentation (this feature)

```text
specs/034-luck-restoration-rule/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md         # Phase 1 output
└── tasks.md              # Phase 2 output (kord-feature-tasks — NOT created by plan)
```

`data-model.md` and `contracts/` are omitted: this feature has no entities, state machine, or
external interface beyond the existing Luck resource and arc structure that `spec.md`'s Key
Entities section already describes in full; a separate data model would duplicate it.

### Source Code (repository root)

Not applicable — no source project is touched. The change surface is:

```text
docs/design/03-rules.md       # §1 Luck — states the restoration rule
docs/adr/0039-luck-resets-at-the-top-level-arc-boundary.md   # new ADR recording the decision
```

**Structure Decision**: Edit `03-rules.md` in place (design documents are rewritten in place per
`CLAUDE.md`) and add one new, numbered, dated ADR under `docs/adr/`. No other document changes —
`18-campaign.md`'s arc structure is referenced, not altered, since the decision fits inside it
without contradiction (spec.md FR-003/Assumptions).

## Complexity Tracking

*No Constitution Check violations — table not needed.*
