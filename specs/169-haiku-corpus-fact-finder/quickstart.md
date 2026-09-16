# Quickstart: validating the Haiku corpus fact-finder subagent

This feature's actual files live in `wyrd-setting-template`, not this repository. Validation is
manual re-reading plus, where feasible, a manual dry run — this repo and the setting template have
no CI.

## Prerequisites

- A checkout of `wyrd-setting-template` with the new `.claude/agents/corpus-fact-finder.md` and
  the rewritten `create-setting/SKILL.md` in place.
- A `wyrd-setting-*` repository with `corpus/*.txt` already extracted (e.g. darkfuture or titan,
  per this session's own prior population work), to dry-run against real text.

## Step 1 — read the subagent definition on its own

Open `wyrd-setting-template/.claude/agents/corpus-fact-finder.md` with no other context loaded.
Confirm:

- Frontmatter declares `model: haiku` and a `tools` list containing only `Read, Grep, Glob`.
- The body states its one job (retrieval only) and gives no instruction that could be read as
  "write setting content" or "decide what to keep."

Expected outcome: SC-002 — a Haiku-tier model reading only this file has everything needed to
perform one lookup and nothing that invites it to write setting content.

## Step 2 — read create-setting's full Phase 3/4 flow

Open `wyrd-setting-template/.claude/skills/create-setting/SKILL.md` and read Phase 3 and Phase 4
top to bottom. For every sentence, classify it as either "delegated mechanical lookup" (names the
subagent) or "judgement, stays on the invoking skill" (prose-writing, register, hedging).

Expected outcome: SC-001 — every sentence is classifiable without consulting any file outside
`create-setting`'s own directory; no sentence does both a lookup and a judgement call in one step.

## Step 3 — manual dry run (if feasible)

Using a real setting's `corpus/` text:

1. Pick one claim already known to be verbatim present somewhere in `corpus/*.txt` (e.g. a
   faction name or a quoted line from a prior setting-population session).
2. Invoke the `corpus-fact-finder` subagent with that claim and the setting's `corpus/` directory.
3. Confirm it returns the exact quote and its source file/location, matching Acceptance Scenario
   1.
4. Pick one claim known **not** to appear anywhere in that corpus.
5. Invoke the subagent again with that claim.
6. Confirm it reports a clear not-found result rather than inventing or approximating a match,
   matching Acceptance Scenario 2.

Expected outcome: SC-003.

## Step 4 — confirm nothing else changed

Diff the rewritten `SKILL.md` against its previous version. Confirm:

- The governing rule (never invent an unsupported claim) is unchanged.
- Phase 1's web-research and original-invention permission language is unchanged (FR-009).
- No other phase (0, 1, 2) was touched beyond what this feature calls for.
