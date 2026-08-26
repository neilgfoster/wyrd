# Implementation Plan: Journeys as a subsystem

**Branch**: `024-journeys-as-a-subsystem` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

## Summary

Define a journey as a `scale: journey` arc whose children are legs, closing the engine gap
`design/13-authoring-a-setting.md` names outright and `settings.yaml` records against `tor`. A
leg is an ordinary arc/beat that additionally declares `mode: played | summarised` (already a
beat field — [`15-arcs-and-beats.md`](../../design/15-arcs-and-beats.md)); summarised legs use
the existing `wyrd advance-time` machinery, played legs run as ordinary beats. Hazards trigger
per leg by mirroring the Threat activation roll (`rating × 10` on `d100`,
[`05-campaign.md`](../../design/05-campaign.md)) and resolve through the core roll like any
other test. The subsystem is inert unless a setting authors a journey — no enable/disable flag
is needed. New design document `design/17-journeys.md`, linked from the hub and from the two
documents it extends; the `settings.yaml` gap note is restated to close.

## The load-bearing decisions

**A journey is an arc, not a new content type.** `15-arcs-and-beats.md` already generalises
"arc contains arcs, at every level, matched by entry/exit conditions" — a journey is that shape
with two additions (pace, hazard rating) rather than parallel machinery. This keeps journeys
selectable, convertible and stub-able exactly like every other arc, satisfying User Story 3
without extra work.

**A leg's played/summarised split reuses the existing `mode:` field, not a new one.**
Clarified 2026-08-26: the field already exists on every beat; a journey leg just declares it
the same way an ordinary beat does. No runtime pacing rule, no separate journey-only enum.

**Hazard chance mirrors the Threat activation formula exactly.** Clarified 2026-08-26: a
journey carries one `hazard_rating`, rolled once per leg against `rating × 10` on `d100` — the
same shape `05-campaign.md` already defines for Threats, so the engine gains no second
"chance per time unit" formula to keep consistent with the first. A triggered hazard resolves
through an ordinary skill test (`03-rules.md`) against a difficulty and a skill named on the
hazard entry — never a bespoke resolution.

**Travel roles are a slot, not a mechanic.** The engine carries an ordered list of role names
per journey (data only); what a role does is left to the setting, per the "engine labels are
defaults, settings rename/configure" rule (`CLAUDE.md`). This keeps the engine from baking in
assumptions (e.g. "forager gives a supply bonus") that belong to a setting's own configuration.

**Supply consequences reuse the material economy, not a new ledger.** ADR 0033 already settled
"encumbrance is GM judgment, coin is a stated total" — a journey references that same
abstraction (a hazard entry may cost Standing, coin, or condition) rather than introducing
per-item travel logistics, matching the "anti-logistics" precedent CLAUDE.md's fault list
warns against re-litigating.

**No enable/disable flag.** A setting that never authors a `scale: journey` arc sees no
behavioural change — narrated travel via `05-campaign.md`'s existing elapsed-time section is
untouched. This satisfies the spec's "configurable and disablable" acceptance criterion without
adding a field to `setting.yaml`'s override vocabulary.

## Structure

- `design/17-journeys.md` *(new)* — defines the journey/leg shape (frontmatter fields: `pace`,
  `hazard_rating`, `hazards` table, `roles`), the per-leg hazard roll, and how a leg resolves
  (played vs. summarised, reusing `mode:`). Linked from `README.md`'s design table and from the
  two documents it extends.
- `design/05-campaign.md` — a short cross-reference from the elapsed-time section to
  `17-journeys.md` for the played-journey case; no rewrite of the existing narrated-travel text
  (Success Criterion SC-002 requires it stay unchanged).
- `design/15-arcs-and-beats.md` — a short cross-reference noting `scale: journey` as a
  recognised arc scale alongside `adventure`/whatever scales already exist, pointing to
  `17-journeys.md` for the fields specific to it.
- `design/13-authoring-a-setting.md` — the worked example's "Journeys as a played mechanic — an
  engine gap" row is updated to point at `17-journeys.md` now that the gap is closed; the
  "engine gap" framing in the permitted/not-permitted section stays (it's still true in
  general, journeys are just no longer the example of an unfilled one) unless review finds it
  reads stale — checked, not assumed.
- `design/README.md` — ADR index unaffected (no ADR from this feature — see below); design
  table gains the `17-journeys` row.
- `settings.yaml` — the `tor` entry's `note:` is either removed (gap closed, nothing left to
  record) or restated to whatever narrower gap remains once `17-journeys.md` lands (checked
  against the finished document, not assumed at plan time).
- `specs/024-journeys-as-a-subsystem/` — this plan, `research.md`, `data-model.md`,
  `quickstart.md`, `tasks.md` (Phase 2).

## No engine code, and no ADR

Design-only, matching #55/#19/#18/#8's own precedent — the deliverable is the new design
document plus small cross-reference edits to two existing ones. **No ADR**: every load-bearing
decision above reuses an already-decided engine mechanism (the arc/beat tree, the `mode:`
field, the Threat activation formula, the material-economy abstraction) rather than rejecting a
real alternative that would have produced a different engine — the CLAUDE.md bar for an ADR
("a real alternative was rejected... someone would plausibly propose it again") is not met by
"reuse the existing shape." This is checked against CLAUDE.md's own two-part test before
`tasks.md` is generated, not assumed.

## Verification

- Read `17-journeys.md` cold, following only its own links and `05-campaign.md`/
  `15-arcs-and-beats.md`/`03-rules.md` — every term it uses resolves (mirrors SC-001).
- `python3 tools/check_docs.py` — reachability, dead links, ADR index (none added), link policy.
- `python3 tools/backlog.py check` — confirms no drift introduced.
- `grep` across changed files for setting/system vocabulary — no unexpected match.
- Confirm `design/05-campaign.md`'s existing elapsed-time prose is byte-identical apart from
  the added cross-reference line (SC-002, "zero behavioural difference when unconfigured").
- Compute the hazard-roll worked example in `17-journeys.md` at a stated rating (e.g. rating 4
  → 40% per leg) and check it against the Threat activation table's own worked numbers in
  `05-campaign.md`, per CLAUDE.md's "check the maths" rule.
- `settings.yaml`'s `tor` note read against the finished document — restated accurately or
  removed, not left stale (FR-010/SC-004).

## Complexity tracking

None. No constitution violations; no new runtime dependencies; no new script (this feature adds
no schema file requiring a validator — journey/leg fields live in existing arc/beat
frontmatter, which is prose-documented, not schema-validated, the same as the rest of
`15-arcs-and-beats.md`).
