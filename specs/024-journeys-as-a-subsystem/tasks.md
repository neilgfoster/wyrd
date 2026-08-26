# Tasks: Journeys as a subsystem

**Input**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md),
[research.md](./research.md)

## Phase 1 — Design document: the journey shape (US1)

- [ ] T001 Write `design/17-journeys.md`: define a journey as a `scale: journey` arc
  (`id`/`type`/`scale`/`name`/`from`/`to`/`pace`/`hazard_rating`/`hazards`/`roles`/`children`,
  per `data-model.md`), and a leg as an ordinary arc/beat child that declares `mode`. State
  each field's default when omitted. [FR-001, FR-003, FR-006]
- [ ] T002 In `17-journeys.md`, state the per-leg hazard roll exactly: `d100 ≤ hazard_rating ×
  10`, mirroring `05-campaign.md`'s Threat activation formula, with a worked numeric example
  (rating 4 → 40% per leg). A trigger consults the journey's `hazards` table and resolves
  through the core roll (`03-rules.md`) against the entry's named skill/difficulty. [FR-004,
  FR-004a]
- [ ] T003 In `17-journeys.md`, state that a leg's resolution mode (`played`/`summarised`) is
  author-declared via the existing `mode:` field, never chosen at runtime; a played leg
  resolves as an ordinary beat, a summarised leg resolves via `wyrd advance-time`. [FR-002,
  FR-004b, FR-008]
- [ ] T004 In `17-journeys.md`, state that a journey may end before its declared distance is
  covered (abandoned, rerouted, interrupted): elapsed time and consequences apply for the
  distance actually travelled, and the remainder either lapses or is resumed later as a fresh
  journey. [FR-007]
- [ ] T005 In `17-journeys.md`, state that supply/harm/Standing consequences from a hazard or a
  leg use the existing material-economy abstraction (ADR 0033) — no per-item inventory or
  logistics ledger — and that `roles` are a named data slot with no engine-defined mechanical
  effect; what a role does is left to the setting. [FR-005]
- [ ] T006 In `17-journeys.md`, state the passage-through-a-Threat's-reach case: travelling
  through a Threat's reach applies its `ambient` cost as ordinary exposure, with no separate
  journey-vs-threat resolution rule. [Edge case — Threat interaction]

## Phase 2 — Cross-references from the documents journeys extend (US1, US2)

- [ ] T007 In `design/05-campaign.md`'s elapsed-time section, add one cross-reference line to
  `17-journeys.md` for the played-journey case, changing no other prose in that section. [FR-002,
  FR-006, SC-002]
- [ ] T008 In `design/15-arcs-and-beats.md`, add one cross-reference noting `scale: journey` as
  a recognised arc scale, pointing to `17-journeys.md` for its fields. [FR-001, SC-001]
- [ ] T009 In `design/13-authoring-a-setting.md`'s worked example, update the "Journeys as a
  played mechanic — an engine gap" row to point at `17-journeys.md` now that the gap is closed;
  leave the permitted/not-permitted "engine gap" framing itself untouched (it is still true in
  general — checked, not assumed). [FR-009, SC-004]

## Phase 3 — Hub and catalogue

- [ ] T010 Add `17-journeys` to `README.md`'s design table, following the existing row
  convention. [reachability — CLAUDE.md's document-graph rule]
- [ ] T011 Check `settings.yaml`'s `tor` entry's `note:` against the finished
  `17-journeys.md`; remove it if the gap is fully closed, or restate it to name accurately
  whatever narrower gap (if any) remains. [FR-010, SC-004]

## Phase 4 — Verification

- [ ] T012 Read `17-journeys.md` cold, with only `05-campaign.md`, `15-arcs-and-beats.md`, and
  `03-rules.md` open; confirm every term it uses (pace, hazard rating, mode, roles) resolves
  without an undefined forward reference. [SC-001]
- [ ] T013 Compute the hazard-roll worked example (T002) against the Threat activation table's
  own worked numbers in `05-campaign.md` and confirm they agree in shape (percent-per-unit =
  rating × 10). [CLAUDE.md — "check the maths"]
- [ ] T014 Diff `design/05-campaign.md`'s elapsed-time section before/after T007 and confirm the
  only change is the added cross-reference line — no rewritten prose. [SC-002]
- [ ] T015 `grep` the touched files for setting/system vocabulary; confirm none. [CLAUDE.md]
- [ ] T016 Run `python3 tools/check_docs.py` — must pass.
- [ ] T017 Run `python3 tools/backlog.py check` — must pass.

## Dependencies

Phase 1 (T001-T006) must complete before Phase 2's cross-references (T007-T009) have anywhere
correct to point, and before Phase 3's `settings.yaml` check (T011), which reads the finished
document. Phase 4 (verification) runs last, after every design-document edit lands. Within
Phase 1, T001 (the field shapes) precedes T002-T006, which each document one behaviour built on
those fields.

## Parallel opportunities

T007, T008, T009 (the three cross-reference edits, once Phase 1 is done) touch different files
and can run in any order. T012-T017 (verification) can run in any order once all edits land.
