# Research: Backlog priority order

**Feature**: 003-backlog-priority | **Date**: 2026-08-25

Findings established against the live board and issue graph before the plan was written.

## 1. The root set is five items, not nine

Issue #24 asserted that #17–#21 were standalone root-level features. Querying the sub-issue graph
disproves it:

```
$ gh api graphql -f query='{ repository(owner:"neilgfoster",name:"wyrd"){
    issues(states:OPEN,first:100){ nodes{ number parent{number} subIssues{totalCount} } } } }'
```

| Issue | Parent | Open children |
|---|---|---|
| #1 | — | 10 |
| #2, #3, #4 | — | 0 |
| #5, #7–#14 | #1 | 0 (except #6) |
| #6 | #1 | 7 |
| #17–#21 | #6 | 0 |
| #24 | — | 0 |

**Consequence.** Ranking roots answers "which epic matters most", not "what do I implement next".
With five roots and one of them holding a 16-issue subtree, the useful answer is a leaf. The
feature is a *walk*, of which the rank is only the first step.

## 2. The dependency data already exists and is parseable

`kord-epic-decompose` writes `Depends on: #N` into a dependent child's body. Grepping the open
issues:

| Issue | Line | Form |
|---|---|---|
| #9 | 1 | `Depends on: #5` |
| #10 | 1 | `Depends on: #6` |
| #12 | 1 | `Depends on: #5` |
| #13 | 1 | `Depends on: #11` |
| #14 | 40 | `Depends on: #5, #6, #7, #8, #9, #10, #11, #12, #13` |
| #17 | 76 | `- Depends on: #15` |

Three forms in six issues: bare first line, a list of several, and a bullet. All are `#N` after a
`Depends on:` prefix, so one parser covers them.

**The trap.** #6, #11 and #17 also contain *prose* using the word "depends":

> `R1.2 (Stamina recovery ...) depends on the Aftermath table landing here.`
> `R1.8 (the mob rule) depends on this landing: petty and weaker only mean something once...`

Matching on the word "depends" anywhere would read #11 as depending on #13 — inverting the real
relationship, since #13 depends on #11. The parser therefore anchors on a line *beginning*
`Depends on:` (after stripping list markers and bold), and this inversion is a test case.

## 3. #17's dependency is already satisfied

#17 declares `Depends on: #15`, and #15 (Table conventions) is closed and merged — as is #16 (the
Aftermath table), which is why #10's dependency on #6 is still open but its sibling work has moved.
A closed target counts as satisfied, so #17 is a genuinely ready leaf today. This gives the
acceptance criteria a real fixture rather than a contrived one.

## 4. The board has no priority field and is missing an item

```
$ gh project field-list 5 --owner neilgfoster
Title, Assignees, Status, Labels, Linked pull requests, Milestone,
Repository, Reviewers, Parent issue, Sub-issues progress, Created, Updated, Closed
```

All defaults. No priority, no rank. The token in use carries the `project` scope, so adding a field
is possible without re-auth.

`gh project item-list 5` returns items #1–#21 — **#24 is absent.** Reading kord's skill
descriptions explains why: `kord-epic-create` "creates a GitHub issue ... and adds it as an item of
a named GitHub Project (v2)"; `kord-feature-create` describes no project step. So a root-level
*feature* never reaches the board on its own.

This is a hole in the mechanism, not a detail: a rank stored on a board item cannot rank an issue
that is not a board item. Two responses, and the plan takes both — add #24 by hand now, and have
`check` report any labelled open issue missing from the board so the next occurrence is loud.

## 5. Alternatives considered for the storage location

**Project v2 numeric field — chosen.** Total order, sortable, queryable via `gh project item-list
--format json`, cross-repo, and the board is already the single source of truth.

**Single-select P0/P1/P2/P3.** Reads well on a board but produces buckets, not an order. Ties
inside a bucket reinstate exactly the judgement call being removed. Rejected.

**The board's native manual item order.** No schema change, but position is not exposed as a stable
sortable value by the API, so the deterministic read path would rest on scraping an ordering that
GitHub does not promise. Fails `design/07-tooling.md` §1. Rejected.

**A file in the repo.** Trivially scriptable and visible in git history, and forbidden: `CLAUDE.md`
says there is no backlog file, "because two lists of the same work drift — which is the fault class
most of this design has been corrected for". Rejected on the repository's own stated rule; recorded
in ADR 0010 because it is the option someone will propose again.

## 6. Placement of the script

`design/07-tooling.md` §3 lays out `engine/wyrd/` for the game engine's CLI. This tool is not engine
behaviour — it reads GitHub, it has no bearing on play, and it must never ship to a chronicle. It
goes in `tools/`, which is already the established name for repo-side tooling in the wyrd family
(`wyrd-research` uses `tools/pull.py`). Keeping it out of `engine/` also keeps the engine free of a
`gh` dependency it must never acquire.
