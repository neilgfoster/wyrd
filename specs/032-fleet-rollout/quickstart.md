# Quickstart: validating the fleet rollout tool

## Prerequisites

- Python 3.11+
- `gh` CLI, authenticated with read access to the `wyrd-*` fleet and write access to open PRs
- No extra packages — stdlib only

## Run the tests (no network, fixture-driven)

```bash
python3 -m unittest tools.test_fleet_rollout -v
```

Exercises `status` and `rollout`'s logic against `tools/fixtures/fleet.json` — a captured
snapshot of `gh repo list` output, sample `.wyrd-version` contents, and sample manifest entries.
No live `gh` call happens during the test run (mirrors `tools/test_backlog.py`'s
`_exists_cache` pattern of injecting captured state).

## Validate against the live fleet (read-only)

```bash
python3 tools/fleet_rollout.py status
```

**Expected**: one row per repo matching `wyrd-setting-*`, `wyrd-setting-template`,
`wyrd-chronicle-template` (SC-005 — all sixteen setting repos plus the two templates appear,
including private ones). A freshly created repo from the current template reports `current`
(User Story 1, Scenario 1).

## Validate a dry-run rollout (no writes)

```bash
python3 tools/fleet_rollout.py rollout --dry-run
```

**Expected**: for each `behind` repo, a line naming the bundled entries that would be applied;
zero branches, commits, or PRs are created. Confirm no writes occurred by checking the target
repos' PR lists are unchanged before/after.

## Validate an actual additive rollout, end-to-end (needs a disposable test repo)

1. Add a new `rollout/changes/NNN-test-entry.yaml` to `wyrd-setting-template` with
   `class: additive` and a trivial new file under `add:`.
2. Run `python3 tools/fleet_rollout.py rollout --repo <a disposable clone of the template>`.
3. **Expected**: exactly one PR opens against that repo, containing the new file, with no
   direct push to its default branch (User Story 2, Scenario 1; SC-002, SC-003).
4. Merge or close the PR, then re-run `status` for that repo — it now reports `current`.
5. Re-run `rollout` again without merging first — confirm no duplicate PR opens (User Story 2,
   Scenario 5).

## Validate accepted divergence

1. Set `diverged_at: <the test entry's id>` in a target repo's `.wyrd-version`.
2. Run `status` — that repo reports `diverged (accepted)`, not `behind` (User Story 3,
   Scenario 1).
3. Run `rollout` — no PR opens for that entry (User Story 3, Scenario 2).
4. Add a second, later manifest entry and re-run both — the new entry is still proposed
   normally (User Story 3, Scenario 3).
