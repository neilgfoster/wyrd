# Feature Specification: Backlog priority order

**Feature Branch**: `003-backlog-priority`

**Created**: 2026-08-25

**Status**: Draft

**Input**: GitHub issue #24 — "Track backlog priority order across root-level kord epics and
features". kord records a dependency order inside an epic and no priority order anywhere. Give Wyrd
one authoritative record of which root-level item comes first, and a deterministic way to ask what
to implement next. Out of scope: re-prioritising the existing backlog beyond seeding an initial
order, and any change to kord itself.

## Context

Choosing the next piece of work is currently a fresh judgement call every session, made by reading
issue titles off the board. That is undocumented re-derivation, and it drifts between sessions —
the fault class `CLAUDE.md` exists to prevent.

kord gives the board a **dependency** order, but only within an epic: `kord-epic-decompose` writes
a `Depends on: #N` line into a child's body, and `kord-loop-epic` walks the child tree. Nothing
records **priority**, and nothing at all orders the roots against each other.

### What the board actually looks like

Issue #24 asserted that #17–#21 were standalone root-level features. **They are not.** Every open
issue except the four epics resolves to a parent:

```
#1  Build the Wyrd engine            (root, epic, 10 children)
    #5  R1.6 skill list
    #6  R1.1 Define the engine's tables   (epic, 7 children)
        #17 damage-type criticals  #18 transformation  #19 affliction
        #20 oracle answers         #21 oracle prompts
    #7 #8 #9 #10 #11 #12 #13 #14
#2  Close the known engine gaps      (root, epic, 0 children)
#3  Corpus extraction and indexing   (root, epic, 0 children)
#4  Onboard settings                 (root, epic, 0 children)
#24 this feature                     (root, feature)
```

Two consequences follow, and they are the whole shape of this feature:

1. **The root set is tiny — five items.** Ranking roots alone answers "which epic matters most",
   not "what do I implement next". A useful answer has to *descend* the tree to a leaf that is
   actually ready to start. Ranking is therefore necessary but not sufficient.
2. **Descent is already possible without new data.** Parentage comes from GitHub's native
   sub-issue graph, and readiness comes from the `Depends on: #N` lines kord already writes. #9,
   #10, #12, #13, #14 and #17 all carry one. Nothing new needs to be recorded per child.

### A gap this feature must not paper over

`#24` is **not on the project board.** `kord-epic-create` adds its issue as a project item;
`kord-feature-create` does not. Any ranking that lives on a board field is therefore blind to
root-level features until someone adds them by hand. This is a real hole in the mechanism and the
tooling must report it rather than silently ranking a subset.

## Clarifications

Resolved with the operator before specification:

- **Where the order lives** — a numeric `Rank` field on the `wyrd` Project (v2 #5). Not a file:
  `CLAUDE.md` forbids a backlog file because two lists of the same work drift. Not a P0/P1/P2
  single-select: buckets leave ties, and a tie is exactly the judgement call this removes.
- **What is ranked** — root-level issues only (no parent issue). Children already carry a
  dependency order; ranking them too would be a second ordering of the same work.
- **The read path** — a script in this repo, following `doc/design/20-tooling.md`. Not raised upstream
  to kord as a prerequisite, so Wyrd is not blocked on another repo.

## Requirements

### FR-1 — One ranked order, on the board

Root-level open issues carry a position in a single total order, recorded as a numeric `Rank`
field on the `wyrd` Project (v2 #5). The board remains the only place the order exists.

Ranks are **sparse** — seeded in tens — so an item can be inserted between two others without
renumbering the rest.

### FR-2 — Deterministic "what is next"

A single documented command answers what to implement next, by computation and not by reading.
Given the board and the issue graph it:

1. takes open root-level issues in ascending `Rank`;
2. descends each into its sub-issue tree;
3. reports the first **ready leaf** — an issue with no open children, whose every `Depends on: #N`
   references a closed issue.

An item whose dependencies are all open is **blocked** and is named as such, with the issues
blocking it, rather than being silently skipped.

### FR-3 — Priority yields to dependency

Where the two orders disagree, **dependency wins**. A higher-ranked item that is blocked cannot be
started, so the tool descends to the next ready leaf and reports the higher-ranked item as blocked.
Priority orders *choice*; dependency constrains *possibility*. Priority never authorises starting
work whose prerequisites are open.

### FR-4 — Drift is reported, not assumed

The tool fails loudly on the ways this mechanism can rot:

- an open root-level issue with **no** `Rank`
- two root-level issues sharing a `Rank`
- an open `kord-epic`/`kord-feature` issue that is **not a project item at all** — the
  `kord-feature-create` hole above
- a `Depends on: #N` naming an issue that does not exist

This mirrors `check_aftermath.py`: where a claim can be checked by a script, check it.

### FR-5 — The order stays refined

Raising a new epic or feature includes giving it a rank if it is root-level. The rule is written in
`CLAUDE.md`, where a cold session reads the workflow, and the drift check in FR-4 makes a forgotten
rank visible rather than silent.

## Constraints

- **One source of truth.** No second list of the same work anywhere in the repo.
- **No hand-edited substrate files.** `.github/ISSUE_TEMPLATE/`, `.specify/` and `.kord/` are owned
  by `kord-install`.
- **Cross-repo.** The board spans `wyrd`, `wyrd-<setting>` and `wyrd-research`; nothing may assume
  a single repository.
- **Python 3.11+, stdlib only** (`doc/design/20-tooling.md` §2). GitHub access shells out to `gh`.
- **Read-only.** The reporting tool never mutates an issue, a field or the board.
- **Publishable.** Nothing derived from a copyrighted source.

## Acceptance criteria

- [ ] A `Rank` number field exists on project 5, and every open root-level issue has a value.
- [ ] `python3 tools/backlog.py next` names one issue to work on, or reports that none is ready.
- [ ] `python3 tools/backlog.py check` exits non-zero on each drift class in FR-4.
- [ ] Descent reaches a leaf: with #1 ranked first, the answer is a feature under #1, not #1.
- [ ] A blocked higher-ranked item is reported as blocked, naming what blocks it — #13 is blocked
      by #11, and #9/#12 by #5, so the fixture is real rather than contrived.
- [ ] `CLAUDE.md` names the mechanism and states the refinement rule.
- [ ] An ADR records the rejection of a backlog file in favour of a board field.
- [ ] No file under `.specify/`, `.kord/` or `.github/ISSUE_TEMPLATE/` is modified.
