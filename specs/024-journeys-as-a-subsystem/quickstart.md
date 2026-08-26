# Quickstart: validating the journeys subsystem

This is a design-document feature — "running" it means reading the finished
`docs/design/30-journeys.md` cold and confirming a journey resolves end to end using only what's
written, per the spec's Success Criteria.

## Prerequisites

- `docs/design/30-journeys.md` written, linked from `README.md`'s design table.
- Cross-references added to `docs/design/18-campaign.md` and `docs/design/28-arcs-and-beats.md`.
- `settings.yaml`'s `tor` note checked against the finished document and updated.

## Validation scenario: run a journey end to end (SC-001, User Story 1)

1. Sketch a minimal journey by hand, following only `17-journeys.md`'s documented fields: two
   places, a pace of "one day", a `hazard_rating` of 3, one hazard table entry, three legs
   (two `mode: summarised`, one `mode: played`).
2. Walk it leg by leg:
   - Summarised legs: confirm the elapsed-time step is exactly `wyrd advance-time`
     (`05-campaign.md`) — no separate mechanic invoked.
   - The played leg: confirm it resolves as an ordinary beat (entry/exit, cast, core roll).
   - At each leg, compute the hazard roll: `d100 ≤ 3 × 10` (30%). Confirm the document states
     this formula, not a different one, and that a trigger routes to the hazard table's named
     skill/difficulty through the core roll (`03-rules.md`) — no bespoke resolution appears.
3. Confirm every term used (pace, hazard rating, mode, roles) is defined either in
   `17-journeys.md` itself or in a document it links — nothing is referenced before it's
   defined (the fault the design programme exists to catch).

**Expected outcome**: the journey runs to arrival with no undefined mechanic and no step that
required inventing a rule not on the page.

## Validation scenario: unconfigured setting shows no change (SC-002, User Story 2)

1. Diff `docs/design/18-campaign.md`'s elapsed-time section before and after this feature lands.
2. Confirm the only change is an added cross-reference line — no rewritten prose, no new
   required field, no altered `wyrd advance-time` behaviour.

**Expected outcome**: a setting that never authors a `scale: journey` arc is unaffected.

## Validation scenario: gap note closed (SC-004)

1. Read `settings.yaml`'s `tor` entry.
2. Confirm the `note:` either no longer exists or accurately names whatever narrower gap (if
   any) remains once `17-journeys.md` is finished — not the pre-feature wording.

## Commands

```bash
python3 tools/check_docs.py     # reachability, dead links, ADR index, link policy
python3 tools/backlog.py check  # drift guard
```
