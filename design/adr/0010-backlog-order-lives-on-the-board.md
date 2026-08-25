# ADR 0010 — The backlog order lives on the board, not in a file

**Date:** 2026-08-25
**Status:** Accepted

## Context

kord tracks work as GitHub issues. It records a **dependency** order inside an epic — a
`Depends on: #N` line written into a child's body by `kord-epic-decompose` — and no **priority**
order anywhere. Nothing orders the roots against each other.

So "what should I implement next?" was answered by reading issue titles off the board and forming
a fresh judgement. That is undocumented re-derivation: the answer is not recorded, so it is not
stable between sessions, and nothing about a wrong one looks wrong.

The obvious fix is a file listing the work in order. This repository already forbids it, in
[`CLAUDE.md`](../../CLAUDE.md):

> There is no backlog file. Open work lives on the board, because two lists of the same work
> drift — which is the fault class most of this design has been corrected for.

That rule settles where the order may *not* live. It does not supply somewhere it *can*.

## Decision

**The order is one numeric `Rank` field on the `wyrd` GitHub Project (v2), on root-level items
only. The repository holds a reader for it and never a copy of it.**

Three parts, and the third is the one that does the work:

1. **Rank, on the roots.** Issues with no parent carry a position in a total order, seeded in tens
   so an item can be inserted between two others by setting one number. Children are not ranked:
   they already carry a dependency order, and ranking them too would be a second ordering of the
   same work — the fault this ADR exists to avoid, reintroduced one level down.

2. **`tools/backlog.py` reads, and never writes.** It combines the board's `Rank`, GitHub's native
   sub-issue graph, and the `Depends on:` lines kord already writes, then walks them to a **ready
   leaf** — an issue with no open children whose every declared dependency is closed. `check`
   reports the ways the mechanism can rot; `next` reports the answer and what it passed over.

3. **Dependency outranks priority.** Where the two disagree, dependency wins. A rank orders what
   you *choose between*; it never authorises starting work whose prerequisites are open. A blocked
   top-ranked item is named as blocked rather than silently skipped, so the answer explains itself.

## Consequences

**The board stays the single source of truth.** The order is one number per root, stored where the
work already lives. Nothing in the repository duplicates it, so there is no second list to drift.

**The answer is computed, not remembered.** This is [ADR 0005](0005-deterministic-over-inference.md)
applied to the work rather than to play: the question has a single correct answer given the board,
so a script gives it. Writing the walk immediately found a dependency nobody had noticed — #21 on
#20 — which is the argument for scripting it in one line.

**Ranking the roots was necessary and not sufficient.** With five roots, one of them holding a
16-issue subtree, a rank alone says which epic matters, not what to do today. The descent to a leaf
is where the value is; the rank is only its entry point. A design that had stopped at the rank
would have looked complete and answered the wrong question.

**The order is not in the git history.** A file would have been. This is the accepted cost: the
*reasoning* for the seeded order is recorded in
[`specs/003-backlog-priority/plan.md`](../../specs/003-backlog-priority/plan.md), and the order
itself is current state, which is what a board is for.

**A gap in kord is now visible rather than silent.** `kord-epic-create` adds its issue to the
project; `kord-feature-create` does not. A root-level feature therefore never reaches the board on
its own and cannot be ranked — #24, the issue that commissioned this work, was itself missing.
`check` reports any labelled issue absent from the board. The proper fix belongs in kord and is not
made here.

## Alternatives rejected

**A markdown file listing the backlog in order.** Trivially scriptable, visible in the history, and
the thing `CLAUDE.md` names as the repository's most-corrected fault class. Two lists of the same
work drift, and the drift is invisible: each list reads as internally coherent, so neither looks
wrong. Recorded here rather than merely refused, because it is the option someone will propose
again, having forgotten the rule — including me, in a year.

**A `Priority` single-select of P0/P1/P2/P3.** Reads well on a board and is easier to set by hand.
It produces *buckets*, not an order, so every tie inside a bucket reinstates exactly the judgement
call the mechanism exists to remove. A tiebreak rule would have to be invented, at which point it
is a total order with extra steps.

**The board's own manual item order.** No schema change at all — drag to reorder. GitHub does not
expose that position as a stable, sortable value through the API, so the deterministic read path
would rest on scraping an ordering nobody promises to keep. That fails
[ADR 0005](0005-deterministic-over-inference.md) at the only point where it matters.

**Ranking every open issue, not just the roots.** Removes the need to descend the tree: sort
everything, take the top. It also means every child carries both a rank and a dependency line, two
orderings of the same work, disagreeing sooner or later — and re-ranking on every decomposition.
The descent is cheap and derives from data that already exists.
