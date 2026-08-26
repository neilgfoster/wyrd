# Phase 1: The old→new path mapping

This is the single source of truth the migration script and every reference-rewrite step reads
from — never re-derived, never eyeballed twice.

## Design documents (`design/*.md` → `doc/design/*.md`)

| Old | New |
|---|---|
| `design/01-principles.md` | `doc/design/01-principles.md` |
| `design/02-architecture.md` | `doc/design/02-architecture.md` |
| `design/03-rules.md` | `doc/design/03-rules.md` |
| `design/03b-the-character.md` | `doc/design/04-the-character.md` |
| `design/03c-character-creation.md` | `doc/design/05-character-creation.md` |
| `design/03d-the-adversary.md` | `doc/design/06-the-adversary.md` |
| `design/03a-tables.md` | `doc/design/07-tables.md` |
| `design/03a-1-criticals.md` | `doc/design/08-criticals.md` |
| `design/03a-2-aftermath.md` | `doc/design/09-aftermath.md` |
| `design/03a-3-transformations.md` | `doc/design/10-transformations.md` |
| `design/03a-4-afflictions.md` | `doc/design/11-afflictions.md` |
| `design/03a-5-oracle-answers.md` | `doc/design/12-oracle-answers.md` |
| `design/03a-6-oracle-prompts.md` | `doc/design/13-oracle-prompts.md` |
| `design/03a-7-systems-of-power.md` | `doc/design/14-systems-of-power.md` |
| `design/03e-playtest-transcript.md` | `doc/design/15-playtest-transcript.md` |
| `design/04-session.md` | `doc/design/16-session.md` |
| `design/04a-out-of-character-mode.md` | `doc/design/17-out-of-character-mode.md` |
| `design/05-campaign.md` | `doc/design/18-campaign.md` |
| `design/06-state.md` | `doc/design/19-state.md` |
| `design/07-tooling.md` | `doc/design/20-tooling.md` |
| `design/08-maintenance.md` | `doc/design/21-maintenance.md` |
| `design/09-evolution.md` | `doc/design/22-evolution.md` |
| `design/10-diegesis.md` | `doc/design/23-diegesis.md` |
| `design/11-corpus-index.md` | `doc/design/24-corpus-index.md` |
| `design/12-parallel-chronicles.md` | `doc/design/25-parallel-chronicles.md` |
| `design/13-authoring-a-setting.md` | `doc/design/26-authoring-a-setting.md` |
| `design/14-entities.md` | `doc/design/27-entities.md` |
| `design/15-arcs-and-beats.md` | `doc/design/28-arcs-and-beats.md` |
| `design/16-chronicle-bootstrap.md` | `doc/design/29-chronicle-bootstrap.md` |
| `design/17-journeys.md` | `doc/design/30-journeys.md` |

## Decision records (`design/adr/*.md` → `doc/adr/*.md`)

Every file under `design/adr/`, including `design/adr/superseded/`, moves to the identical
filename under `doc/adr/` — **numbers are historical identifiers and are never renumbered.**
`0001-resolution.md` through `0037-out-of-character-mode-is-a-prefix-trigger.md`, plus everything
under `adr/superseded/`.

## Hub

| Old | New |
|---|---|
| `design/README.md` | `doc/README.md` |

## What is explicitly NOT remapped

- Prose *inside* `specs/*/*.md` — left as historical record (spec's Clarifications/FR-008); only
  each file's literal `design/...` path tokens are repaired, per the same clarification that
  later resolved this the same way as the ADR-link decision (a path repair, not a content edit).
- Closed GitHub issues — left as historical record (spec's Edge Cases).

## Cross-reference direction changes

Before the move, `design/*.md` → `design/adr/NNNN-....md` was parent→child (`adr/...`), and
`design/adr/*.md` → `design/*.md` was child→parent (`../03-rules.md`). After the move, both
directions are sibling→sibling: `doc/design/*.md` → `doc/adr/NNNN-....md` becomes `../adr/...`,
and `doc/adr/*.md` → `doc/design/*.md` becomes `../design/NN-....md`. Both halves of every
cross-reference change, not just the moved file's own outgoing links.
