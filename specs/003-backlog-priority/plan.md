# Implementation Plan: Backlog priority order

**Branch**: `003-backlog-priority` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-backlog-priority/spec.md`

## Summary

Add a numeric `Rank` field to the `wyrd` Project (v2 #5), seed it for the five open root-level
issues, and write `tools/backlog.py` — a stdlib-only script that shells out to `gh` and answers
"what do I implement next?" by computation.

The load-bearing insight from [research.md](./research.md): **ranking the roots is not the
feature.** With only five roots, a rank alone tells you which epic matters, not what to do. The
answer comes from combining three sources that already exist — the board's `Rank`, GitHub's native
sub-issue graph, and the `Depends on: #N` lines `kord-epic-decompose` already writes — and walking
them to a leaf that is genuinely ready to start.

Nothing new is recorded per child issue. The only new state anywhere is one number per root.

## Technical Context

**Language**: Python 3.11+, standard library only (`docs/design/20-tooling.md` §2). No pytest —
`unittest` (§6).

**GitHub access**: `subprocess` to `gh`. The token needs the `project` scope, which is already
present. Two calls, both read-only:

- `gh project item-list 5 --owner neilgfoster --format json` — items and their `Rank`
- one GraphQL query for open issues with `parent`, `subIssues.totalCount`, `labels`, `body`

**Placement**: `tools/backlog.py`, not `engine/`. The engine is the game engine — setting-agnostic
and shipped; this is repository workflow and has no business inside it. `tools/` is already the
established name for this in the wyrd family.

## Constitution check

| Gate | How this satisfies it |
|---|---|
| Deterministic over inference (§1) | Single correct answer given board + issue graph → script. The whole point is removing a judgement call. |
| Stdlib only, zero backend (§2) | `subprocess`, `json`, `argparse`. No packages, no daemon. |
| Structured output by default (§3) | `--format json` emits a stable object; text is for humans. |
| No backlog file (`CLAUDE.md`) | The order lives on the board. The repo holds the *reader*, never the *order*. |
| Substrates not hand-edited | Nothing under `.kord/`, `.specify/`, `.github/ISSUE_TEMPLATE/` is touched. |

## Design

### The data model

```
root issues (parent == null, open, kord-epic|kord-feature)
  └─ Rank: int          <- the only new state, on the project item
      └─ sub-issue tree  <- GitHub native, already exists
          └─ Depends on: #N   <- kord already writes this
```

### The selection algorithm

```
for root in roots sorted by (Rank, number):
    walk root's subtree depth-first, children ordered by (Rank if any, number)
    for each node with no OPEN children:          # a leaf
        if every `Depends on: #N` is CLOSED:      # ready
            return it
        else record it as blocked-by those issues
return None, plus the blocked list
```

Dependency is checked **against the issue's own state, not against rank** — this is FR-3. A root
ranked first whose whole subtree is blocked yields to the next root, and the blocked items are
reported rather than dropped, so the operator can see *why* the obvious answer was not the answer.

A closed `Depends on:` target counts as satisfied. A dependency naming a nonexistent issue is drift
(FR-4), not a satisfied dependency — the difference matters, because a typo'd number would
otherwise read as "ready".

### Parsing `Depends on:`

kord writes the line either as the body's first line (`Depends on: #5`) or as a bullet
(`- Depends on: #5 (R1.6, skill list)`), and #14 carries a list (`Depends on: #5, #6, #7, ...`).
The parser takes every `#N` on any line whose text starts with `Depends on:` after stripping
list markers and bold, and ignores prose that merely mentions the word "depends" — #6, #11 and #17
all contain such prose, so this is tested rather than assumed.

### Why sparse ranks

Seeded in tens (10, 20, 30, …). Inserting between two items is a single `gh` call setting one
number, rather than renumbering the tail. The order is a total order; the gaps carry no meaning.

## Seeded order

| Rank | Issue | Why here |
|---|---|---|
| 10 | #1 Build the Wyrd engine | The engine is the product. Everything else is downstream of a working ruleset, and this is the only root with a decomposed tree ready to work. |
| 20 | #24 Backlog priority order | This feature. Cheap, and it is what makes the rest of the order legible. Ranked above the remaining epics because it is nearly done, not because it outranks the engine. |
| 30 | #2 Close the known engine gaps | Gap-closing presupposes the engine it is closing gaps in. Undecomposed. |
| 40 | #3 Corpus extraction and indexing | Lives mostly in `wyrd-research`; not gating the engine. Undecomposed. |
| 50 | #4 Onboard settings | A setting overlays a finished engine (`docs/design/26-authoring-a-setting.md`), so this is last by construction. Undecomposed. |

The order is the operator's to change; it is recorded here as the seed, not as a claim that will
stay true. The board is authoritative — this table is the reasoning, which is what a design
document is for.

## Steps

1. Create the `Rank` number field on project 5.
2. Add #24 to the board (it is absent — `kord-feature-create` does not add items) and set the five
   ranks.
3. Write `tools/backlog.py` with `next` and `check` subcommands.
4. Write `tools/test_backlog.py` — `unittest`, against captured fixtures, no network.
5. Write ADR 0010; update `CLAUDE.md` with the mechanism and the refinement rule.

## Risks

**The board can be edited outside the tool.** That is intended — the board is the source of truth
and the tool only reads it. `check` is what catches the resulting gaps.

**`kord-feature-create` does not add items to the board.** Until that is fixed upstream, a new
root-level feature is invisible to the ranking. `check` reports it as drift, which converts a
silent hole into a loud one. Fixing kord is out of scope here and should be raised in the kord repo.
