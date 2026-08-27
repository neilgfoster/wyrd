# Phase 1: The old→new path mapping

This is the single source of truth the migration script and every reference-rewrite step reads
from — never re-derived, never eyeballed twice.

## Design documents (`design/*.md` → `docs/design/*.md`)

| Old | New |
|---|---|
| `design/01-principles.md` | `docs/design/01-principles.md` |
| `design/02-architecture.md` | `docs/design/02-architecture.md` |
| `design/03-rules.md` | `docs/design/03-rules.md` |
| `design/03b-the-character.md` | `docs/design/10-the-character.md` |
| `design/03c-character-creation.md` | `docs/design/11-character-creation.md` |
| `design/03d-the-adversary.md` | `docs/design/12-the-adversary.md` |
| `design/03a-tables.md` | `docs/design/04-tables.md` |
| `design/03a-1-criticals.md` | `docs/design/05-criticals.md` |
| `design/03a-2-aftermath.md` | `docs/design/06-aftermath.md` |
| `design/03a-3-transformations.md` | `docs/design/07-transformations.md` |
| `design/03a-4-afflictions.md` | `docs/design/08-afflictions.md` |
| `design/03a-5-oracle-answers.md` | `docs/design/14-oracle-answers.md` |
| `design/03a-6-oracle-prompts.md` | `docs/design/15-oracle-prompts.md` |
| `design/03a-7-systems-of-power.md` | `docs/design/09-systems-of-power.md` |
| `design/03e-playtest-transcript.md` | `docs/design/30-playtest-transcript.md` |
| `design/04-session.md` | `docs/design/16-session.md` |
| `design/04a-out-of-character-mode.md` | `docs/design/17-out-of-character-mode.md` |
| `design/05-campaign.md` | `docs/design/19-campaign.md` |
| `design/06-state.md` | `docs/design/22-state.md` |
| `design/07-tooling.md` | `docs/design/27-tooling.md` |
| `design/08-maintenance.md` | `docs/design/28-maintenance.md` |
| `design/09-evolution.md` | `docs/design/29-evolution.md` |
| `design/10-diegesis.md` | `docs/design/13-diegesis.md` |
| `design/11-corpus-index.md` | `docs/design/26-corpus-index.md` |
| `design/12-parallel-chronicles.md` | `docs/design/21-parallel-chronicles.md` |
| `design/13-authoring-a-setting.md` | `docs/design/24-authoring-a-setting.md` |
| `design/14-entities.md` | `docs/design/25-entities.md` |
| `design/15-arcs-and-beats.md` | `docs/design/18-arcs-and-beats.md` |
| `design/16-chronicle-bootstrap.md` | `docs/design/23-chronicle-bootstrap.md` |
| `design/17-journeys.md` | `docs/design/20-journeys.md` |

## Decision records (`design/adr/*.md` → `docs/adr/*.md`)

Every file under `design/adr/`, including `design/adr/superseded/`, moves to the identical
filename under `docs/adr/` — **numbers are historical identifiers and are never renumbered.**
`0001-resolution.md` through `0037-out-of-character-mode-is-a-prefix-trigger.md`, plus everything
under `adr/superseded/`.

## Hub

| Old | New |
|---|---|
| `design/README.md` | `docs/README.md` |

## What is explicitly NOT remapped

- Prose *inside* `specs/*/*.md` — left as historical record (spec's Clarifications/FR-008); only
  each file's literal `design/...` path tokens are repaired, per the same clarification that
  later resolved this the same way as the ADR-link decision (a path repair, not a content edit).
- Closed GitHub issues — left as historical record (spec's Edge Cases).

## Cross-reference direction changes

Before the move, `design/*.md` → `design/adr/NNNN-....md` was parent→child (`adr/...`), and
`design/adr/*.md` → `design/*.md` was child→parent (`../03-rules.md`). After the move, both
directions are sibling→sibling: `docs/design/*.md` → `docs/adr/NNNN-....md` becomes `../adr/...`,
and `docs/adr/*.md` → `docs/design/*.md` becomes `../design/NN-....md`. Both halves of every
cross-reference change, not just the moved file's own outgoing links.
