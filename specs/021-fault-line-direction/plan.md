# Implementation Plan: Fault Line accrual bias

**Branch**: `021-fault-line-direction` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

## Summary

Give the Fault Line a mechanical read: `design/03-rules.md` §4's Exposure route gains one
conditional step — when the GM judges an Exposure source runs with the grain of a character's
Fault Line (the same fiction-grounded judgment call already used to invoke a Drive), a failed
resistance gains Taint one tier worse (minor 1 → 2, moderate 2 → 3, major stays 3). The
resolution roll itself is untouched; the transformation table (`design/03a-3-transformations.md`)
is untouched. A check script computes, at real Taint trajectories, how much sooner aligned
Exposure crosses the next threshold than unaligned Exposure at the same starting Taint. Record the
decision — and the two rejected alternatives — as an ADR.

## The load-bearing decision

**The bias attaches to Exposure's Taint gain, not to the transformation table or the hidden
threshold.** Both alternatives were real: reworking `03a-3-transformations.md` so each severity
tier offers a direction-keyed set of effects, or skewing the secretly-rolled hidden threshold
(1d6+2) by direction. The first would fork or restructure a table the design programme just
finished settling in #18 (merged) — CLAUDE.md's own maintenance cost of "two documents describing
one thing differently" applies directly to keeping a duplicate, direction-keyed variant of an
already-settled table in sync. The second changes a number the player never sees, which sits
awkwardly against the issue's own acceptance criterion that two equal-Taint characters must
*differ mechanically* — an invisible skew is a weaker mechanical difference than a visible one.
Exposure's Taint gain is already a plain resisted-test-then-flat-number rule (§4), the same shape
Drive invocation (§1) already extends with a fiction-grounded GM judgment call, so extending that
established pattern to the Fault Line is the smallest true fork, not a new mechanism. This is
recorded as an ADR because both rejected paths are ones a future reader — including a future
version of this same design programme — would plausibly propose again.

## Structure

- `design/03-rules.md` §4 — the Exposure subsection gains the tier-worse rule, its cap (one step
  per event), and a statement that it is independent of an Invocation drawn against the same roll.
  §4's Fault Line subsection is rewritten to point at the mechanism instead of standing alone.
- `design/03a-3-transformations.md` — unchanged. Verified unchanged by the check script (a
  content-hash or direct diff check) so a future edit here doesn't silently reopen the table this
  feature deliberately left alone.
- `design/adr/00XX-*.md` — records the decision and the two rejected alternatives (transformation
  row selection; hidden threshold bias).
- `design/README.md` — ADR index updated.
- `tools/check_fault_line.py` — computes, across a spread of starting Taint values and Exposure
  tiers, the number of Exposure events until the next threshold crossing under aligned vs.
  unaligned Exposure, and confirms the tier-worse step never exceeds major (3) at the ceiling case.

## No engine code

Design-only, matching every table/mechanic-family issue in this stage so far (#15, #17, #18, #19):
there is no `engine/` implementation for this repo to extend yet. The deliverable is the design
document edit, its computation script, and the ADR.

## Verification

- `python3 tools/check_fault_line.py` — passes, prints the computed threshold-crossing comparison
  and confirms the ceiling case (major stays at 3).
- `python3 tools/check_docs.py` — reachability, links, ADR index, link policy.
- `python3 tools/backlog.py check` — unaffected by this change; run to confirm no drift introduced.
- `grep` across `design/` for setting/system vocabulary — no unexpected match in changed files.
- Manual diff of `design/03a-3-transformations.md` against `main` — confirms it is untouched, per
  FR-006/SC-003.

## Complexity tracking

None. No constitution violations; no new dependencies; no code beyond a single stdlib script.
