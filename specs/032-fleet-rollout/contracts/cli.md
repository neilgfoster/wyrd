# CLI Contract: `tools/fleet_rollout.py`

Argparse dispatch, same shape as `tools/backlog.py`. Two verbs.

## `status`

```bash
python3 tools/fleet_rollout.py status
python3 tools/fleet_rollout.py status --format json
python3 tools/fleet_rollout.py status --repo wyrd-setting-hemmelfurt   # single repo
```

Read-only (FR-010: no repository writes). Exit code 0 always for a completed read — a repo in
`behind`/`unreachable` state is a normal, successfully-reported result, not a script failure.
Non-zero exit is reserved for a tool-level failure (e.g. `gh` not authenticated).

**Output** (`--format json`): a list of Fleet repo records (see `data-model.md`). Default
text format is a table: repo, visibility, state, and (for `behind`) a comma-joined list of
missing entry ids.

## `rollout`

```bash
python3 tools/fleet_rollout.py rollout --dry-run                 # show what would be opened, open nothing
python3 tools/fleet_rollout.py rollout                            # open PRs for every behind repo
python3 tools/fleet_rollout.py rollout --repo wyrd-setting-hemmelfurt   # single repo
```

For each repo `status` reports as `behind`:

1. Skip if an open PR from a prior `rollout` run already targets the same latest entry id for
   that repo (FR-007 — no duplicate PRs).
2. Otherwise create a branch, apply the bundled entries in order (additive: copy paths from the
   entry's `sha`; structural: apply the entry's `migrate` step), commit, and open a PR via
   `gh pr create` against the target repo — never `git push` to its default branch.
3. Report the PR URL (or "skipped: already open" / "skipped: previously closed without
   merging") per repo.

`--dry-run` performs steps 1 and the content computation for step 2, but opens no branch, makes
no commit, and creates no PR — it prints what *would* happen, one line per repo.

Exit code non-zero only on a tool-level failure (auth, network, malformed manifest entry); a
repo with nothing to roll out, or a repo that was skipped as already-open/previously-rejected,
is a normal result reported in the output, not a failure.
