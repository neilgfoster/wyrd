# Implementation Plan: Foundation review and the reset

**Branch**: `005-foundation-reset` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Write ADR 0012 recording the reset and the consolidation rule, update `design/README.md`'s lifecycle
table to describe it, and extend `tools/check_docs.py` so a stale ADR reference cannot go unnoticed.

The foundation review found no fault in `design/01-principles.md`, so that document is not touched.
The finding is recorded in [research.md](./research.md) instead.

## The consolidation rule

The shape, decided here and recorded in the ADR:

```
design/adr/
  0001-….md                Accepted           ← live set, renumbered once, in Stage 13
  0005-….md                Accepted
  superseded/
    0009-….md              Superseded by 0014 ← keeps its original number, permanently
```

Four parts:

1. **Marking.** A superseded record's `**Status:**` line becomes `Superseded by ADR NNNN`, and the
   superseding record carries `**Supersedes:** ADR NNNN`. Nothing else in a superseded record is
   ever edited — its reasoning is the thing being preserved.
2. **Location.** Superseded records move to `design/adr/superseded/`.
3. **Numbering.** The archive keeps original numbers **permanently**. The live set is renumbered into
   a clean sequence. So a reference to a superseded decision always resolves; only references to
   records that stayed live and changed number need rewriting.
4. **Timing.** Numbers are frozen until Stage 13, when the renumber happens **once**, as a single
   scripted operation with every in-repo reference rewritten and verified.

Timing is the part that is easy to get wrong. Renumbering as each record is reworked would break
every external reference once per stage; doing it once breaks them once. During the programme, a
revisited decision simply takes the next free number.

## The guard

`check_docs.py` gains a fifth check. Today it verifies markdown **links**; a prose reference —
`ADR 0005`, of which there are 11 — resolves to nothing and nothing notices.

```
ADR 0005  →  design/adr/0005-*.md   or   design/adr/superseded/0005-*.md
```

Matching on the number rather than the slug is deliberate: a record's slug may be improved during
consolidation, and a reference that names only the number should survive that. The check is about
whether the decision is findable, not whether the prose quoted its title exactly.

**Why this is the right mitigation.** Renumbering was chosen knowing it breaks references. What makes
that acceptable rather than reckless is that the breakage becomes *visible*. Without this check the
programme's own cleanup would reintroduce the fault class the programme exists to remove.

What it cannot fix: 12 commit messages. Recorded in the ADR as an accepted, permanent cost.

## Constitution check

| Gate | How this satisfies it |
|---|---|
| Deterministic over inference (§1) | "Does this reference resolve?" has a correct answer → script. |
| Stdlib only (§2) | `pathlib`, `re`. |
| Documents describe the present | The lifecycle table is rewritten, not annotated. |
| Rejected reasoning is retained | No record is ever deleted; the archive is permanent. |

## Steps

1. `research.md` — the foundation review finding and the deferred tone knob.
2. ADR 0012 — the reset and the consolidation rule.
3. `design/README.md` — lifecycle table, and the archive convention.
4. `check_docs.py` — the ADR reference check, resolving against live set and archive.
5. Tests — construct a stale reference, a valid one, and one resolving into `superseded/`.
6. Run; confirm the repo is clean.

## Risks

**The check could fire on prose that says "ADR 0005" while meaning something else.** There is no such
prose, and the failure mode is a loud false positive — the right direction for a guard.

**`superseded/` will be empty until a record is actually superseded.** The checker must not require
the directory to exist, or it fails on a repo where nothing has been superseded yet.
