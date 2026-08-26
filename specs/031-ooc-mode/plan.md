# Implementation Plan: Out-of-character mode at play time

**Branch**: `031-ooc-mode` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/031-ooc-mode/spec.md`

## Summary

Give the engine a single-character trigger (`?`) that switches the handling of one player
message to out-of-character (OOC): the diegetic contract of
[`doc/design/23-diegesis.md`](../../doc/design/23-diegesis.md) is suspended for that response (raw
numbers on request), the exchange never enters the chronicle as fiction, and the response
carries an unmistakable textual marker. This is [ADR 0037](../../doc/adr/0037-out-of-character-mode-is-a-prefix-trigger.md)'s
load-bearing fork (a one-character prefix over a slash command), made concrete as a new design
document.

## The load-bearing decision

**A one-character prefix, not a slash command.** The issue weighs both: a slash command
(`/ooc what's my stamina`) is more explicit and visually distinct, but heavier to type on a
phone every session — and phone play is the dominant context per `01-principles.md`'s brief
("short sessions, often on a phone"). `?` was chosen because it reads naturally as "I'm asking
a question", costs exactly one character, and does not collide with plausible in-character
dialogue the way a bare `$` would. See ADR 0037 for the full reasoning and the rejected
alternative.

**Per-message, not a session-wide toggle.** OOC handling applies to the triggered message and
the GM's one response to it; the very next untriggered message returns to in-character handling
automatically. A session-wide toggle risks a player forgetting they left OOC mode on and having
an in-character action misread as a query — the opposite failure to the one this feature exists
to prevent.

**Nothing new is added to state or persistence.** An OOC exchange is not a new entity family
with its own schema; it is a handling mode applied to an ordinary message exchange, kept out of
the chronicle's fictional record and logged separately per FR-008. No new table, no new
validator-checked schema — this is a GM-contract/session-flow change, not a data feature.

## Where the rules land

| Document | Change |
|---|---|
| `doc/design/17-out-of-character-mode.md` (new) | the trigger, what suspends, what's logged, the marker, the "would my character know this" answer shape |
| `doc/adr/0037-out-of-character-mode-is-a-prefix-trigger.md` (new) | records the load-bearing fork |
| `doc/README.md` | links the new document so `tools/check_docs.py` finds it reachable |
| `doc/design/01-principles.md` | one-line cross-reference at the point that currently implies everything typed is in-character speech and action |
| `doc/design/23-diegesis.md` | one-line cross-reference at "Mechanical detail is always available on request", pointing to the new document as where the *request mechanism* is specified |
| `doc/design/16-session.md` | one-line cross-reference near "The player never hears the words beat, rally or arc" / session-flow section, noting OOC mode as the escape hatch that does not itself become part of a beat |

## Technical Context

**Language/Version**: N/A — this feature is prose only; no code, no validator (see below)

**Primary Dependencies**: none

**Storage**: N/A — this feature edits Markdown design documents; no runtime storage. It
specifies that OOC exchanges are logged separately from the chronicle, but the concrete
storage location is deferred to whichever implementation (not yet built — "nothing is
implemented" per `README.md`) later realises session logging.

**Testing**: `python3 tools/check_docs.py` (reachability from `README.md`), `python3
tools/check_dangling_mechanics.py` (no orphaned mechanic name), repo-wide `python3 -m pytest -q`

**Target Platform**: N/A — a design document, not a deployed service

**Project Type**: documentation only (no schema, no validator — see "What the check script has
to settle" below for why)

**Performance Goals**: N/A

**Constraints**: setting-agnostic — no setting or system name in `design/` or `README.md`;
terse play must stay viable (trigger adds exactly one character, per FR-009)

**Scale/Scope**: one new design document, one new ADR, three one-line cross-references in
existing documents

## What the check script has to settle

**No new `tools/check_*.py` validator.** Every prior rules feature with its own validator
(`check_power_systems.py`, `check_bestiary.py`, `check_transformation.py`, …) validates a
setting-authored **data schema** — YAML a setting fills in, checked for required fields, closed
vocabularies, cross-file references. This feature adds no such schema: there is no per-setting
data to author for OOC mode, no worked-example fixture to validate, nothing with a "correct
answer" in the sense ADR 0005 means. The load-bearing claims (one-character trigger, per-message
scope, marker requirement) are prose-only GM-contract rules, the same kind `01-principles.md`
and `10-diegesis.md` already state without a validator behind them. The existing repo-wide
checks (`check_docs.py`, `check_dangling_mechanics.py`) are the applicable guards; no new script
is added for this feature.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `CLAUDE.md` and the accepted ADRs (per `.specify/memory/constitution.md`'s
pointer), not a separate constitution file:

- **Nothing unpublishable enters this repository.** No setting content, no source-system
  material — this feature is a generic interaction mode. Pass.
- **No setting or system names in `design/` or `README.md`.** The new document and ADR use
  "out-of-character mode", "trigger", "marker" — descriptive English throughout. Pass.
- **Capability change → Spec Kit cycle, `specs/` committed.** This plan is that cycle. Pass.
- **Tone is a setting property, never baked into a mechanic** ([ADR 0004](../../doc/adr/0004-tone-belongs-to-the-setting.md)).
  The new document specifies mechanism (trigger, suspension, marker), not voice; the OOC
  marker's exact wording is left to the same rename/presentation layer every other engine
  label uses. Pass.
- **Deterministic over inference** ([ADR 0005](../../doc/adr/0005-deterministic-over-inference.md)).
  There is no numeric claim in this feature to compute — it is a mode switch, not a probability
  or a threshold — so this gate does not apply; no claim is asserted that a script could check
  instead. Pass (vacuously).
- **Design documents rewritten in place; accepted ADRs never edited.** `01-principles.md`,
  `10-diegesis.md` and `04-session.md` each receive a one-line cross-reference only; ADR 0037 is
  new and untouched thereafter. Pass.

No violations; Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/031-ooc-mode/
├── plan.md               # This file
└── (no research.md/data-model.md/contracts/quickstart.md — see below)
```

No `research.md`: no NEEDS CLARIFICATION remains in Technical Context above, and the spec's own
Assumptions section already resolved every open design question with a documented default. No
`data-model.md`/`contracts/`: this feature introduces no data entity and no schema a setting
would author — the "OOC exchange" and "Mode" entities named in the spec are handling-state
concepts fully specified by the new design document's prose, not fields on a record. No
`quickstart.md`: there is no runnable command to validate (no validator script per above); the
new design document's own worked example (asking for exact Stamina and resuming play) serves the
same illustrative purpose a quickstart would.

### Source Code (repository root)

```text
design/
├── 04a-out-of-character-mode.md   # new
├── 01-principles.md               # one-line cross-reference added
├── 10-diegesis.md                 # one-line cross-reference added
├── 04-session.md                  # one-line cross-reference added
├── README.md                      # links the new document
└── adr/
    └── 0037-out-of-character-mode-is-a-prefix-trigger.md   # new
```

**Structure Decision**: matches every prior Wyrd design-only feature — a new design document,
one new ADR, and `README.md`/cross-reference updates. No `tools/check_*.py` validator this time
(see "What the check script has to settle" above for why), and no `src/`/`tests/` structure
applies — this is not application code, and nothing in this repository is implemented yet.
