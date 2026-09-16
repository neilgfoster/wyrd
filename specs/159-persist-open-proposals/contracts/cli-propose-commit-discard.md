# Contract: `wyrd propose`/`commit`/`discard`/`reroll` across separate CLI invocations

This feature changes no CLI argument, no JSON output shape, and no error text for any of these
four verbs — the contract below states what continues to hold, plus the one new cross-process
guarantee.

## Unchanged surface

- `python3 -m wyrd.client propose --actor <path> --mechanic <name> [...]` — same flags, same
  stdout shape (`{"verb": "propose", "proposal_id", "roll", "mutations", "steps"}`).
- `python3 -m wyrd.client commit <proposal_id>` — same positional arg, same stdout shape
  (`{"verb": "commit", "proposal_id", "mutations"}`), same `{"error": {"verb": "commit",
  "reason": "no open proposal: <id>"}}` shape for an unknown/resolved id.
- `python3 -m wyrd.client discard <proposal_id>` — same, `{"verb": "discard", "proposal_id"}`.
- `python3 -m wyrd.client reroll <proposal_id> --step <n> --resource <name>` — same.

## New guarantee

**Given** `propose` (or `propose_batch`) is run as one OS process and returns `proposal_id`,
**when** `commit`/`discard`/`reroll` is run with that same `proposal_id` as a wholly separate,
later OS process, with the same current working directory the `propose` call used,
**then** it succeeds (or fails) identically to running both calls in the same process.

**Precondition made explicit by this feature**: both calls must share the same working
directory — the same one that already has to hold `chronicle.yaml` for every other cwd-relative
CLI convention to work (data-model.md "Relationship to existing entities"; research.md
Decision 1). This is not a new constraint particular to proposals; it is the same one every
other chronicle-scoped verb already has.
