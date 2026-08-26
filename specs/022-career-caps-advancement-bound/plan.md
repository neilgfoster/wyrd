# Implementation Plan: Career caps and the advancement bound

**Branch**: `022-career-caps-advancement-bound` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

## Summary

State the career cap (70%, the top of the *expert* band), the career-completion grant (+1
maximum Stamina and one Mark, per career-instance), and a computed ceiling on maximum Stamina, in
`doc/design/03-rules.md` §6 where "career's cap" and "completing a career" already live but are never
bounded. Justify the ceiling with a script, `tools/check_advancement.py`, that runs the numbers for
a character completing careers back-to-back across a long chronicle — the same treatment
`check_creation.py` already gave Stamina's starting value of 6. Record the cap value and the
Stamina ceiling as ADR 0032.

## The load-bearing decisions

**The cap is flat at 70%, one number per career, not per skill.** `03-rules.md` §6 already writes
"to that career's cap" as a single figure per career; a per-skill table would need setting data
this feature has no way to source (careers are setting data) and would contradict "career grants a
list of skills," which implies uniform treatment. 70% is the top of the *expert* band
(`10-diegesis.md`, 60–70%), leaving "it is part of who you are" (75%+) reachable only by something
beyond ordinary career advancement — consistent with "depth over breadth" already being the
claimed shape of the whole power curve.

**Maximum Stamina's ceiling is computed, not chosen.** `03c-character-creation.md` already used a
computed argument to fix the *starting* value at 6 ("much above 10 and the sentence stops being
true" for the +1-per-completion gain). This feature extends the same reasoning to the *ceiling*:
`check_advancement.py` runs a character through repeated completions and reports the Stamina value
at which the "16.7% gain" framing from creation would first read as false (i.e., a further +1 stops
being a meaningfully large fraction of current Stamina), and states that as the hard ceiling rather
than leaving Stamina open-ended. A completion past the ceiling still grants the Mark; it stops
granting further Stamina.

**Completion is tracked per career-instance, not per career-for-life.** A character may hold the
same career twice across a lifetime (the career graph is a directed graph, not a DAG the spec rules
out cycles from); each instance is its own span with its own completion check, so re-entering a
finished career and finishing it again is legal and grants again. This matches
`09-evolution.md`'s forward-only posture: nothing about a past instance is recomputed when a new
instance of the same career begins.

**Companions are explicitly out of scope.** §6 already carves them out ("no career graph, no
Marks"); this feature does not touch that carve-out, it only fills in the player-character side of
the same section.

## Structure

- `doc/design/03-rules.md` §6 — rewritten in place: the cap value, the completion trigger and grant,
  and the Stamina ceiling, replacing the current unbounded "career's cap" / "completing a career"
  language with the resolved numbers.
- `doc/adr/0032-*.md` — records the 70%-cap and computed-Stamina-ceiling decisions and their
  rejected alternatives (e.g., a per-skill cap table, an unbounded Stamina gain).
- `doc/README.md` — ADR index updated.
- `tools/check_advancement.py` — computes, for a character completing careers back-to-back over a
  chronicle of 10+ career-instances: the Stamina value at each completion, the ceiling that value
  converges to, and a scan confirming no skill exceeds 100% under the 70%-cap rule. Asserts the
  ceiling and cap numbers this plan and the ADR state, the same way `check_creation.py` and
  `check_transformation.py` assert theirs.

## No engine code

Design-only, matching the shape of the table-family and character-creation issues that preceded
it (#8, #10, #12's own dependency #5): there is no `engine/` implementation for this feature to
extend. The deliverable is the design document change, its proof script, and the ADR.

## Verification

- `python3 tools/check_advancement.py` — passes, prints the computed Stamina sequence and the
  ceiling it converges to.
- `python3 tools/check_docs.py` — reachability, links, ADR index, link policy.
- `python3 tools/backlog.py check` — unaffected by this change; run to confirm no drift introduced.
- `grep` across `design/` for setting/system vocabulary in changed files — no unexpected match.

## Complexity tracking

None. No constitution violations; no new dependencies; one stdlib script alongside the existing
`check_creation.py`/`check_transformation.py`/`check_affliction.py` family.
