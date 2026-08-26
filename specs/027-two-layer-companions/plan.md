# Implementation Plan: Two-layer companions and a positive party track

**Branch**: `027-two-layer-companions` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/027-two-layer-companions/spec.md`

## Summary

Amend `design/04-session.md`'s companion record so it is explicitly split into a **narrative
layer** (`objective`, `flaw`, `secret`, `arc` — who this person is) and a **mechanical layer**
(`career`, `bond`, `taint`, `strain`, `wounds` — what resolution actually consumes), stating the
mechanical layer as closed and small. Resolve the positive-party-track gap by reconciling it with
**Bond**: Bond already tracks the same "how is this relationship going" question a new track
would, so the fix is to give Bond an explicit positive *mechanical* effect (not just narrative
colour) rather than invent a second track that would duplicate it — recorded as an ADR since a
real alternative (a standalone positive Tension-mirror track) is rejected. Confirm
`design/03-rules.md`'s companion-advancement and succession passage against the completed split
(advancement lands on the mechanical layer only; a successor starts a fresh mechanical layer,
narrative layer written fresh). Add a verification script checking the mechanical layer's field
count against the party-size bound and that no duplicate-track language survives.

## Technical Context

**Language/Version**: Markdown design documents; Python 3 for the verification script (matches
existing `tools/*.py` / `specs/*/check_*.py` convention in this repo).

**Primary Dependencies**: None — stdlib only, per existing `check_*.py` scripts in other
`specs/*/` directories.

**Storage**: N/A — this feature produces design prose, not application state or a data file.

**Testing**: `tools/check_companion_layers.py` — checks that the mechanical-layer field list
named in `design/04-session.md` is a fixed, enumerable set (asserts the exact list this plan
records in `data-model.md`, so a future edit that quietly grows it fails the check rather than
drifting unnoticed); that no field appears in both the narrative-layer and mechanical-layer lists;
and that `design/03-rules.md`'s companion/succession passage does not name a mechanical field
absent from that same list. Plus the repo-wide checks this change must keep green:
`tools/check_docs.py` (reachability) and a grep for setting/system vocabulary (`CLAUDE.md`).

**Target Platform**: N/A — this repo has no runtime target; it is design documents read by a
future rules engine (Stage 13).

**Project Type**: Documentation / design-record change to a single-repo TTRPG engine (`wyrd`).

**Performance Goals**: N/A.

**Constraints**: No setting or system name anywhere in `design/` (`CLAUDE.md`); every mechanic
named must be defined where introduced, not merely referenced; companions must not gain a
capability score (`design/03-rules.md`'s existing "the engine holds no capability score for a
companion" rule, danger-scaling section) — the mechanical layer's fields are all fields the design
already uses elsewhere (career cap, taint, strain, wounds, bond), not a new competence rating;
design documents rewritten in place, no changelog prose (`CLAUDE.md`).

**Scale/Scope**: Two existing documents amended (`design/04-session.md` for the two-layer split
and Bond's new positive effect; `design/03-rules.md` for the confirmed advancement/succession
passage), one new ADR (Bond as the positive track, rejecting a standalone mirror of Tension), one
verification script. No new design document — this is a refinement of an existing one, unlike the
oracle-table features which each opened a new file.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

This repo has no `.specify/memory/constitution.md`; its governing document is `CLAUDE.md`
(project root). Relevant gates, checked against this plan:

- **Setting-agnostic engine** — no setting/system name in `design/`. Gate: satisfied by
  construction; every field name used already exists in the engine's own vocabulary. Verified by
  grep (`quickstart.md`) before this feature is done.
- **No capability score for a companion** (`design/03-rules.md`) — Gate: the mechanical layer
  adds no new numeric rating; it names fields the design already defines elsewhere. Verified by
  `tools/check_companion_layers.py` cross-checking the field list against `design/03-rules.md`'s
  own statement of that rule.
- **A decision earns an ADR only if a real alternative was rejected and someone would plausibly
  propose it again** (`CLAUDE.md`) — the Bond-vs-new-track choice qualifies: a standalone positive
  track mirroring Tension is a workable alternative that produces a different engine (two tracks
  answering the same question), and it is exactly the kind of thing a future contributor would
  propose again having forgotten Bond already covers it. Gate: satisfied — see the ADR.
- **Design documents rewritten in place, no changelogs** — `design/04-session.md` and
  `design/03-rules.md` are edited to describe the present state only.
- **Capability change goes through the Spec Kit cycle, `specs/` committed** — this plan.

No violations requiring the Complexity Tracking table below.

## Project Structure

### Documentation (this feature)

```text
specs/027-two-layer-companions/
├── plan.md                    # This file
├── research.md                # Phase 0 output
├── data-model.md              # Phase 1 output
├── quickstart.md              # Phase 1 output
└── tasks.md                   # Phase 2 output (/speckit-tasks)
```

No `contracts/` — this feature has no external interface (API, CLI surface, wire format); it
amends existing design prose and entity fields already governed by `design/06-state.md` /
`design/14-entities.md`.

### Source Code (repository root)

```text
design/
├── 03-rules.md                   # amended: companion advancement/succession passage confirmed
│                                  #   against the completed two-layer model
├── 04-session.md                 # amended: companion record split into narrative/mechanical
│                                  #   layers; Bond given an explicit positive mechanical effect
└── adr/
    └── 00NN-bond-is-the-positive-party-track.md   # new: rejects a standalone positive track

tools/
└── check_companion_layers.py     # new: checks the mechanical-layer field set is fixed, disjoint
                                   #   from the narrative layer, and consistent across both docs
```

**Structure Decision**: No new top-level design document — companions and Party Tension already
have a home (`design/04-session.md`), and this feature refines that document rather than opening
a sixth one, unlike the table-family features which each introduced a new file under a shared
index row. The ADR number is assigned at write time from the next free slot in `design/adr/`.

## Complexity Tracking

No gate violations — table not filled.
