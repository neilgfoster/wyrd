# Implementation Plan: Player-facing opposed tests

**Branch**: `029-player-facing-opposed-tests` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

## Summary

Generalise #69/ADR 0027's player-facing roll from combat to every opposed test where one side is
an NPC/opponent: the player rolls once against `effective% = clip(50 + (skill −
opponent_skill_or_baseline), 5, 95)`, the opponent's dice are never consulted, and a failure simply
fails the action with no resisting-side roll. The calibration is not recomputed — it is reused
exactly as `check_mapping.py`/`check_conversion.py` already settled it. What this feature actually
has to decide: what happens to a contest between two player-controlled entities (no NPC/opponent
side to set `effective%` against), and what remains of ADR 0016 once its combat scope (already
narrowed by ADR 0027) and now its general scope are both retired.

## The load-bearing decisions

**§1's "Opposed tests" becomes a pointer to §2, not a second description.** Today §1 defines the
two-sided shape and §2 already carries a note that combat supersedes it. After this feature, the
two-sided shape is retired wherever one side is an NPC/opponent, so §1 is rewritten to state the
player-facing roll directly (mirroring §2's wording, not duplicating it verbatim — the two sections
should read as one rule stated once and referenced, the same relationship the rest of the ruleset
already keeps between a defined mechanic and its uses).

**The NPC/opponent vs player-controlled-entity line is the one that matters, not combat vs
non-combat.** #69/ADR 0027 drew the line at combat because that was its scope; #77's own framing
(and this plan) draws it at *who is on each side* — the opponent's capability is a static number
`03d-the-adversary.md` already defines, and any test opposed by that kind of side gets the
single-roll treatment regardless of whether it happens in a fight.

**Two player-controlled entities in tension keep ADR 0016's original carve-out, not a new
mechanic.** `03-rules.md` §1 already states: "Where neither is [acting] ... the GM either names an
actor or calls for two ordinary tests." A PC-vs-companion arm-wrestle has an actor (one side is
trying to change the situation) but no NPC/opponent skill to set `effective%` against — reusing the
existing carve-out (ordinary test for whichever side is acting) is simpler than inventing a second
resolution shape for a case the design already anticipated, and no design rationale currently
depends on treating "no NPC/opponent side" differently from "no actor." This is stated as an
explicit rule (FR-004), not left implicit.

**ADR 0016 is retired, not further narrowed.** Its five provisions describe the two-sided
roll-both shape end to end. ADR 0027 already carved combat out of it; this feature carves out
every remaining case where one side is an NPC/opponent — which, per the issue's own grep, was the
*only* live use of the two-sided shape outside combat. Nothing is left for ADR 0016 to govern, so
the new ADR supersedes it entirely rather than narrowing its scope a second time. (If review of
`design/` during implementation turns up a genuine surviving use of the two-sided shape, the new
ADR narrows instead of retiring — the check script decides this by grepping the design corpus, it
is not asserted up front.)

## What the check script has to settle

`check_opposed_generalisation.py`, stdlib only, exact arithmetic, following
`check_mapping.py`/`check_conversion.py`'s conventions. It **asserts agreement with the prior
figures it depends on** (the `effective%` mapping from `check_mapping.py`, the telling-blow
threshold and degrees distribution from `check_conversion.py`) rather than re-deriving them.

1. **Grep `design/` for every live citation of "opposed test" as a mechanism** (not ADR 0016's own
   historical definition), and classify each: already routes through the player-facing shape
   (combat), needs rewriting to it (this feature's targets), or is the two-player-controlled-entity
   carve-out (unaffected in shape, restated in §1's own wording). This list is what confirms ADR
   0016 has no remaining live scope, rather than assuming it from the issue's own grep.
2. **Reconfirm the untrained-10%/assistance/declaration composition** already established for
   combat's attack/defence rolls applies unchanged to the generalised roll — no new interaction to
   compute, only confirmed against the existing rule text and `check_conversion.py`'s worked
   examples.
3. **A worked non-combat opposed test**, end to end: a player character (or companion) attempting
   something an NPC/opponent resists, resolved as a single roll against `effective%`, degrees read
   `tens(effective%) − tens(roll)`, against representative skill gaps from the same span
   `check_mapping.py` used — confirms the rule as rewritten produces the same numbers combat
   already produces at the same skill gap, since it is the same formula.
4. **Agreement with every figure this feature's rewrite touches or depends on**: the mapping table
   in `check_mapping.py`. Non-zero exit on any disagreement.

## Where the rules land

| Document | Change |
|---|---|
| `doc/design/03-rules.md` §1 | "Opposed tests" rewritten to the player-facing shape (generalised from §2's wording); the two-player-controlled-entities carve-out restated explicitly as its own rule |
| `doc/design/03-rules.md` §2 | unchanged in substance; its "Combat does not use this shape" cross-reference to §1 is revisited since §1 no longer describes a different shape |
| `doc/adr/0016-*.md` | left untouched (accepted ADRs are never edited) |
| `doc/adr/0035` (new) | supersedes ADR 0016 in full (pending Step 1's grep confirming no live scope survives) |
| `doc/README.md` | updated only if a new document is added (none planned — this is a rewrite of an existing document plus one ADR) |

## The order of work

`check_opposed_generalisation.py` comes first, since Step 1 (grepping `design/` for every live
"opposed test" citation) is what confirms whether ADR 0016 is retired outright or only narrowed
further — the ADR cannot be written correctly before that is settled. The ADR is written from what
the script settles, `03-rules.md` §1 is rewritten last, in place, and finally the guards —
`check_opposed_generalisation.py` itself, `python3 tools/check_docs.py`, `python3
tools/backlog.py check` — all run clean before the feature is considered done.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only (`fractions.Fraction` for exact arithmetic)

**Primary Dependencies**: none — matches every prior `specs/0NN-*/check_*.py` script in this repo

**Storage**: N/A — this feature edits Markdown design documents and adds one check script

**Testing**: the feature's own `check_opposed_generalisation.py`, plus the repo-wide
`tools/check_docs.py` and `tools/backlog.py check` guards

**Target Platform**: N/A — design documents and a CLI check script, not a runtime system

**Project Type**: design-document rewrite with a verification script (matches every prior
Wyrd rules feature, e.g. `specs/018-player-facing-combat`)

**Performance Goals**: N/A

**Constraints**: no setting/system vocabulary in `design/`; an accepted ADR is never edited;
rule changes apply forward only

**Scale/Scope**: one section of `doc/design/03-rules.md` rewritten in place, one new ADR, one check
script

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, the gates come from `CLAUDE.md` and the accepted ADRs:

- **No setting/system vocabulary in `design/`.** This feature only touches existing engine
  vocabulary (opposed test, `effective%`, NPC/opponent) already established by #69/ADR 0027. Pass.
- **Tone stays a setting property.** No tone language introduced. Pass.
- **Deterministic over inference.** The one open computation (whether ADR 0016 has any remaining
  live scope) is settled by `check_opposed_generalisation.py`'s grep pass, not asserted. Pass.
- **Rule changes apply forward only.** This is a resolution-mechanism rewrite for future play; no
  history is recomputed. Pass.
- **Design documents rewritten in place; accepted ADRs never edited.** `03-rules.md` is rewritten
  in place; ADR 0016 is left untouched and a new ADR supersedes it. Pass.
- **Capability change → Spec Kit cycle, `specs/` committed.** This plan is that cycle. Pass.

No violations; Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/029-player-facing-opposed-tests/
├── plan.md                              # This file
├── check_opposed_generalisation.py      # Phase 0/verification script
└── (no data-model.md/contracts/quickstart.md — see below)
```

No `data-model.md`, `contracts/`, or `quickstart.md`: this feature has no data entities, no
external interface, and no runnable end-user flow beyond the design-document text and its check
script — the same shape every prior Wyrd rules-only feature (`012`, `013`, `018`, `019`, `020`,
`021`, `028`) has used. `research.md` is likewise skipped: there is no NEEDS CLARIFICATION left
in the Technical Context above, and the one open question (ADR 0016's remaining scope) is resolved
by the check script itself, not by research.

### Source Code (repository root)

```text
design/
└── 03-rules.md              # §1 rewritten in place

doc/adr/
└── 0035-*.md                # new: supersedes ADR 0016 in full

specs/029-player-facing-opposed-tests/
└── check_opposed_generalisation.py   # new verification script
```

**Structure Decision**: matches every prior Wyrd rules feature — a design-document edit, one new
ADR, and one `specs/<feature>/check_*.py` script. No `src/`, `tests/`, or web/mobile structure
applies; this is not application code.
