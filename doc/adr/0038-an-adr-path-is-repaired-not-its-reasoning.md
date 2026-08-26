# ADR 0038 — An ADR's path references are repaired; its reasoning is never edited

**Date:** 2026-08-26
**Status:** Accepted

## Context

`doc/README.md`'s own rule for a decision record is unambiguous about the record's *reasoning*:
"its reasoning is never edited; a later record supersedes it." CLAUDE.md states the same rule
for the repository as a whole: "An accepted ADR is never edited."

#38 (moving every design document from `design/` to `doc/design/`, and every decision record
from `design/adr/` to `doc/adr/`, with every design document also renumbered) makes this
concrete rather than abstract for the first time: every ADR that names another document by its
relative path — thirty-seven of them do, at least once — now has a link that would resolve to
nothing, purely because the file it points at moved. Neither `CLAUDE.md` nor `doc/README.md`
had ever been asked whether repairing that link counts as "editing" the record. Read literally,
"never edited" forbids touching the file at all, which would leave every one of those links
permanently dead the first time anything in `doc/design/` or `doc/adr/` is ever renamed or
moved again — and #38 will not be the last such move.

This is exactly the shape of decision `doc/README.md` says earns a record: a real alternative
(leave every such link dead forever) was rejected, and the question — may a path inside an
accepted ADR ever be touched — will plausibly be asked again the next time a document moves.

## Decision

**An ADR's reasoning is immutable. A relative path inside it is repaired like any other link in
the repository when the file it points at moves.**

Concretely: if `doc/design/09-aftermath.md` is later renamed or moved, every ADR linking to it
gets that one link's target updated to match, in the same pass that performs the move — the
same mechanical, mapping-driven, verified repair `tools/check_docs.py` already exists to
validate. Nothing else in the ADR changes: not its Context, Decision, Alternatives rejected, or
Consequences sections, not a word of its argument, and not its `Status:` line (which continues
to change only on supersession, per the existing rule).

The test for whether an edit is a permitted path repair rather than a forbidden content edit:
**does the sentence's meaning change if you read it before and after the edit, ignoring the
literal characters of the file path?** A path repair fails to change any meaning — the document
still says exactly what it said, about exactly the same thing, at its exactly-current location.
Any edit that changes what is being asserted, argued, or concluded is not a path repair and
remains forbidden by the existing rule.

This decision applies retroactively to every prior instance where a path was already the
literal target of a link (it does not reopen the substance of any prior decision), and
prospectively to every ADR written from here on.

## Alternatives rejected

**"Never edited" means never, full stop — a dead link inside an ADR stays dead forever.**
Rejected: this makes `tools/check_docs.py`'s link check permanently unable to reach "all checks
passed" the moment any document it references is ever renamed, for the life of the repository.
It also means the record itself becomes actively misleading over time — a reader following a
citation from an ADR would land nowhere, with no way to tell whether the citation was wrong when
written or the target simply moved since. Treating "the reasoning is preserved" and "the
citation resolves" as the same guarantee conflates two different promises the repository makes.

**Special-case `tools/check_docs.py` to exempt ADR files from the dead-link check.** Rejected:
this doesn't resolve the tension, it hides it — the links would still be dead, just silently
unchecked, which is precisely the "reads as authoritative and is not" fault CLAUDE.md's own
fault-class list names first. It also means a *genuinely* broken ADR link (a typo, not a move)
would go uncaught, which is a real regression in what the check protects.

**Require a new ADR every time a path needs repairing, explaining why this one link may move.**
Rejected as needless ceremony: the whole point of recording this decision once is that it never
needs re-litigating per broken link. A path repair is exactly the kind of mechanical,
non-judgment operation `design/07-tooling.md`'s "deterministic over inference" principle already
prefers scripted and verified over asserted case by case.

## Consequences

- `tools/check_docs.py`'s existing link-resolution check applies to `doc/adr/*.md` exactly as it
  does to any other document; a dead link there is always a bug to fix, never a policy the check
  must work around.
- Every future document move or rename (#38 will not be the last) repairs every ADR's affected
  links as part of the same pass, using the same mapping-driven, grep-verified method #38 used —
  never a manual, ADR-by-ADR judgment call about whether this particular link "counts."
- Nothing about this decision permits editing an ADR's title, its numbering, its `Status:`
  transition rule, or any sentence that asserts, argues, or concludes something. Those remain
  governed entirely by the existing "never edited" rule.
