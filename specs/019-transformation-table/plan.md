# Implementation Plan: The transformation table

**Branch**: `019-transformation-table` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

## Summary

Define `docs/design/10-transformations.md` as the transformation table family required by
`03a-tables.md`'s conventions: a `1d6` table with a severity per row, concrete Taint threshold
values, a computed proof the re-roll loop terminates, the resolved body-versus-mind statement, the
hidden threshold's mechanics, and Dread. Update `03-rules.md` §4 and `03a-tables.md`'s index in
place, and record the threshold-spacing/severity-reuse decision as ADR 0029.

## The load-bearing decisions

**Thresholds at every 3 Taint, starting at 3.** Extends the two values `03-rules.md` §1's Wyrd-die
bands already anchor (3 and 6) at the same interval indefinitely, rather than leaving Taint's upper
range without thresholds or inventing an unmotivated second interval. See
[ADR 0029](../../docs/adr/0029-transformation-thresholds-at-every-three-taint.md) for the
rejected alternatives.

**Six-row `1d6` table, severities 1/1/2/2/3/4.** Large enough that a single-event threshold
crossing (max gain 3, per `03-rules.md` §4's Exposure cap) clears in 1–3 re-rolls in the worst case
scanned; small enough that no row disposes of a whole threshold band in one roll, which would make
severity meaningless as a per-row distinction.

**Termination has two independent guarantees, both computed.** The severity/threshold arithmetic
(scanned, not asserted, in `tools/check_transformation.py`) and, independently, the table's own
finiteness plus its unique-per-character rule (`03a-tables.md`) bound any re-roll burst at 6 rolls
regardless of severities. The second guarantee is what makes the design robust to a future
re-tuning of the severity numbers.

**Dread reuses severity rather than introducing a new per-row number.** One measured quantity, read
twice — into Taint's reduction and into the running Dread total — rather than a second number that
could drift out of step with the first on a re-tune.

**The body/mind collision is resolved in this document, once.** `03-rules.md` §4's "Transformation
(body) or Affliction (mind)" is corrected to state plainly that a Taint threshold always forces a
Transformation, and Afflictions arise only from Trauma reaching 6+ (§5) — a separate, unrelated
track. #19 (affliction table) has not landed, so this document is the one that owns the statement,
per the issue's own instruction.

## Structure

- `docs/design/10-transformations.md` — new. Thresholds, body/mind, the roll, the table, termination,
  hidden threshold, Dread.
- `docs/design/03-rules.md` §4 — rewritten in place to state the resolved thresholds and body/mind split,
  and to point at the new document for detail.
- `docs/design/07-tables.md` — index row updated from "not yet written" to the real file, roll, and
  link.
- `README.md` — hub row added for reachability.
- `docs/adr/0029-*.md` — records the threshold-spacing and Dread-reuse decisions and their
  rejected alternatives.
- `docs/README.md` — ADR index updated.
- `tools/check_transformation.py` — computes worst-case and expected re-roll counts; asserts the
  hard bound.

## No engine code

This feature is design-only, matching the shape of the table-family issues that came before it
(#15, #17): there is no `engine/` implementation of tables yet for this repo to extend. The
deliverable is the design document, its proof script, and the ADR.

## Verification

- `python3 tools/check_transformation.py` — passes, prints the computed table above.
- `python3 tools/check_docs.py` — reachability, links, ADR index, link policy.
- `python3 tools/backlog.py check` — unaffected by this change; run to confirm no drift introduced.
- `grep` across `design/` for setting/system vocabulary — no unexpected match in changed files.

## Complexity tracking

None. No constitution violations; no new dependencies; no code beyond a single stdlib script.
