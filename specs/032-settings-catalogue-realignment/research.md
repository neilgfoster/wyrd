# Phase 0 Research

## Decision: status determined by live inspection, not by trusting the old value

**Decision**: Every entry's `status:` is set from what `gh api` actually shows in that repo's
`library/` and `index/` trees at the time this feature is written, not carried over from the
stale value.

**Rationale**: The whole point of this feature is that the old catalogue is untrustworthy.
Checked directly: all fourteen `wyrd-setting-*` repos have real subdirectories under `library/`
(beyond the template's `.gitkeep` placeholder); all fourteen have only `.gitkeep` under `index/`.
So every corrected entry reads `status: library-loaded`.

**Alternatives considered**: inferring status from `settings.yaml`'s own history (rejected —
that's exactly the stale source this feature replaces).

## Decision: four-value status vocabulary

**Decision**: `stub | library-loaded | indexed | playable`, an ordered progression.

**Rationale**: Matches the issue's own framing exactly ("distinguish an empty repo from a loaded
one... a boolean is no longer expressive enough") and the three real pipeline stages visible in
the fleet today (empty template skeleton → library present → indexed, per #98's still-open work)
plus the terminal "confirmed usable at the table" state the maintainer sets by hand once a
chronicle has actually run against it — not something a script can observe remotely.

**Alternatives considered**: a numeric percentage (rejected — implies false precision over
something that is really a small number of discrete stages); a free-text field (rejected —
defeats the drift check's ability to validate it against a closed set).

## Decision: shared-world grouping as a plain data field, no new mechanic

**Decision**: An optional `group:` string per entry (e.g. `wh40k`, `maelstrom`); nothing reads or
acts on it yet.

**Rationale**: The issue explicitly says "do not build both" (the catalogue field and the
related-settings feature/#36's actual behavior). Recording the grouping as inert data satisfies
"the catalogue should express" the relationship without building the mechanism #36 owns.

**Alternatives considered**: a nested structure grouping settings under their shared world
(rejected — a bigger schema change than this feature's scope, and #36 may want a different shape
once it actually builds something that consumes it).

## Decision: drift check follows `tools/backlog.py`'s exact shape

**Decision**: `tools/check_settings_catalogue.py`, stdlib-only, `gh repo list` for the live
fleet, PyYAML-free reader for `settings.yaml` (reuses the same restricted-subset approach
`tools/fleet_rollout.py` introduced, since `settings.yaml`'s shape is a simple list of flat
mappings), reports repos missing from the catalogue and catalogue entries naming a repo that
doesn't exist, on demand rather than in CI (`docs/design/27-tooling.md` §1: this repo has no CI yet).

**Alternatives considered**: extending `tools/backlog.py` itself with a new subcommand
(rejected — `backlog.py`'s docstring and purpose are specifically the board/issue graph; a
settings-catalogue check is a different concern with a different data source, and bolting it on
would blur what each script is for, the opposite of the "MCP-shaped, one tool per concern"
structure `docs/design/27-tooling.md` §3 asks for even in the zero-backend tooling case).
