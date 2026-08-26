# Feature Specification: Foundation review and the reset

**Feature Branch**: `005-foundation-reset`

**Created**: 2026-08-25

**Status**: Draft

**Input**: GitHub issue #40 — Stage 1 of the design programme (#1). Confirm the foundation still
holds, record the reset, and define the rule by which decision records may be consolidated. Out of
scope: performing the consolidation, which happens as records are reworked through Stages 2–12 and
is completed in Stage 13.

## Context

The design programme revises documents and decision records that the repository's own rules protect.
`docs/README.md` states that an ADR is "never edited; superseded by a later record", and `CLAUDE.md`
says an accepted ADR is never edited. The programme is authorised to change that, but an authorised
exception that is not written down is indistinguishable from drift six months later.

So Stage 1 has two jobs, and only one of them is a change: **confirm the foundation**, and **write
the rule** every later stage will revise records under.

## Findings — the foundation review

`docs/design/01-principles.md` was re-read in full against everything the programme has surfaced:
magic having no engine mechanism, characters having no defined model, adversaries having no
representation, and the economies never being treated as one system.

**It needs no substantive amendment.** The brief, the seven engine principles, the tone contract, the
GM contract, the division of labour and the six success criteria all still describe what Wyrd is and
none is contradicted by what the programme found. This is recorded as a finding rather than left
implicit, because "reviewed and unchanged" and "not reviewed" look identical in a diff.

One deliberate **non-change** is worth stating, because it is the programme's own fault in miniature:

> The tone contract has no knob for how commonplace supernatural power is, and it is tempting to add
> one now that magic is in scope (#26). **Deferred to Stage 10.** A tone knob whose effect points at
> a mechanism that does not yet exist is exactly the fault this programme was convened to correct —
> a reference to something undefined, in text that reads as authoritative. The knob, if it is needed,
> is defined when the thing it modifies is.

## Requirements

### FR-1 — The reset is recorded

An ADR states what the reset is, what it authorises, why it was needed, and what it does not
authorise. Without it, a later reader finds ADRs that were edited under a rule saying they never are.

### FR-2 — The consolidation rule is precise enough to follow

It must answer, unambiguously:

- how a superseded record is marked;
- where a superseded record lives, and under which number;
- **when** renumbering happens;
- what is never permitted.

"Supersede and renumber" is a direction, not a procedure. Three people would implement it three ways.

### FR-3 — Renumbering happens once

Numbers are **frozen for the duration of the programme** and the renumber is a single operation in
Stage 13. Renumbering incrementally as records are reworked breaks every external reference once per
stage instead of once in total.

### FR-4 — Superseded records keep their original numbers

A superseded record moves to `docs/adr/superseded/` and **keeps the number it was written under**,
permanently. The live set is renumbered into a clean sequence; the archive is not. This means a
historical reference to a superseded decision still resolves to the reasoning it meant.

### FR-5 — The silent breakage class is made loud

Renumbering was chosen with its cost understood: 76 references across 30 files, of which 11 are prose
(`ADR 0005`) rather than links, plus 12 commit messages that can never be corrected.

`tools/check_docs.py` currently verifies **links**. A prose reference to a renumbered record would
break silently — the exact fault class the programme exists to eliminate, reintroduced by the
programme's own cleanup. The checker must therefore verify that every `ADR NNNN` reference in prose
resolves to a record that exists, in either the live set or the archive.

### FR-6 — The lifecycle table describes the new rule

`docs/README.md` currently says ADRs are never edited. It must describe what is actually true, in
the present tense, with no "previously we…" note.

## Constraints

- Python 3.11+, stdlib only; `unittest`.
- No record is deleted, at any point, for any reason.
- `docs/design/01-principles.md` is amended only where the review found a genuine fault. It found none.
- Nothing under `.kord/`, `.specify/` or `.github/ISSUE_TEMPLATE/`.

## Acceptance criteria

- [ ] An ADR records the reset, the consolidation rule, and what the reset does not authorise.
- [ ] The rule states marking, location, numbering and timing unambiguously.
- [ ] `docs/README.md`'s lifecycle table describes the present rule.
- [ ] `check_docs.py` fails on a prose `ADR NNNN` reference that resolves to nothing.
- [ ] The checker resolves references against both the live set and `superseded/`.
- [ ] The foundation review is recorded as a finding, including the deferred tone knob.
- [ ] All existing checks still pass; no design document is left with a dead reference.
