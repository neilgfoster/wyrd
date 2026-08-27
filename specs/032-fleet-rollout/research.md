# Phase 0 Research: Fleet rollout

All Technical Context items had a clear answer from the clarify session and existing repo
precedent (`tools/backlog.py`); no `NEEDS CLARIFICATION` markers remained after `/speckit-plan`'s
setup. This file records the decisions that shaped the plan, since the "why" is what
`CLAUDE.md` asks commits and specs to carry.

## Decision: fleet discovery by name-prefix listing

**Decision**: `gh repo list neilgfoster --json name,visibility,isArchived --limit 200`, filtered
to names matching `^wyrd-setting-.*$` or equal to `wyrd-setting-template` /
`wyrd-chronicle-template`.

**Rationale**: Confirmed in clarify. No new file to maintain (a registry would itself be state
that can drift — the exact fault class this feature exists to fix, per `CLAUDE.md`'s recurring
faults). `tools/backlog.py` already establishes the precedent of reading GitHub live rather than
maintaining a local list.

**Alternatives considered**: an explicit registry file (rejected: new state, new drift surface);
a GitHub topic tag (rejected: requires retroactively tagging sixteen existing repos before the
feature can see any of them, for no benefit over a name pattern that already holds for every
existing repo).

## Decision: version marker is a committed SHA-pointer file

**Decision**: Each fleet repo carries `.wyrd-version` at its root, recording the commit SHA of
the source repo (`wyrd-setting-template`, `wyrd-chronicle-template`) it last synced to, plus
(optionally) the engine SHA it targets.

**Rationale**: Confirmed in clarify. A SHA is unambiguous and requires no separate
version-bumping discipline in the source repos — "what changed since SHA X" is answerable by
walking that repo's own commit log, which is exactly what git is for.

**Alternatives considered**: manually bumped semantic versions (rejected: needs a bump-and-tag
discipline maintained by hand, and doesn't by itself say what changed — the manifest below would
still be needed).

## Decision: outstanding changes are read from an explicit manifest, not diffed

**Decision**: `wyrd-setting-template` and `wyrd-chronicle-template` each carry a
`rollout/changes/<NNN>-<slug>.yaml` manifest, one file per rollout-eligible change, each
declaring `class: additive | structural`, the commit `sha` it was introduced at, a human
`summary`, and either an `add:` list of paths (additive) or a `migrate:` script/instructions
reference (structural) — the same shape `design/09-evolution.md` already uses for engine
migrations (`engine/migrations/0001_....py`, each declaring its class).

**Rationale**: `design/07-tooling.md` §1's decision procedure: "does it have a single correct
answer given the state? → script" only holds if the classification and the change content are
themselves data, not inferred from a raw diff. Auto-diffing two trees cannot reliably tell
"a file was renamed" (structural) from "an old file was deleted and an unrelated new one added"
(coincidentally additive) — this is the same reasoning `design/09-evolution.md` gives for why
migrations are hand-authored and hand-classified rather than derived. Reusing the exact
two-class subset (additive/structural) the issue names, instead of the full five-class
chronicle taxonomy, keeps this feature's classification meaningful for *repository files*
without overloading vocabulary that `design/09-evolution.md` defines for *chronicle state*
(these are different axes, per FR-005's own note, and the spec's Assumptions scope this feature
away from chronicle-state migration entirely).

**Alternatives considered**: computing outstanding changes via `git diff <recorded-sha>..HEAD`
directly against the target repo's tree (rejected: cannot classify structural vs. additive
automatically, and would either always guess "additive" — silently corrupting a structural
change into a blind file copy — or require the same manifest anyway to hold the classification,
making the diff redundant).

## Decision: one bundled PR per behind repo

**Decision**: Confirmed in clarify — `rollout` opens exactly one branch/PR per repo that is
behind, containing every manifest entry newer than that repo's recorded SHA, applied in order.

**Rationale**: Matches the acceptance criteria's framing ("a template change can be proposed to
every repo that needs it in one operation") and avoids sixteen-repo review fatigue from one
change producing sixteen separate PRs, or repeated staleness from a repo accumulating many
small unreviewed PRs between maintainer sessions.

**Alternatives considered**: one PR per individual change (rejected in clarify — multiplies
review surface for no benefit here, since structural and additive entries are already
distinguishable within a single PR body by their manifest class).

## Decision: private-repo safety by construction, not by special-casing

**Decision**: The tool never reads a target repo's `library/`, `corpus/`, or `index/`
directories under any verb, and the manifest/rollout mechanism operates purely on the
`.wyrd-version` marker and the paths a manifest entry names explicitly (files the *template*
owns, never files a setting authors). `gh` calls that read/write repos work identically for
public and private repos given read/write auth, so no branching is needed for repo visibility.

**Rationale**: Per FR-006, safety here is best guaranteed by the tool structurally never
touching setting-authored content, rather than by a runtime check that could be bypassed by a
manifest entry naming the wrong path. `gh repo list --json visibility` still reports visibility
for the status report's own information, but nothing about *how* the tool operates depends on
it.

**Alternatives considered**: an explicit path-based blocklist enforced at runtime (kept as a
defense-in-depth validation on manifest entries — a manifest entry naming a path under
`library/`, `corpus/`, or `index/` is rejected as invalid — but the primary guarantee is that
the manifest format has no reason to ever name those paths, since the template repo does not
contain setting-authored content in the first place).

## Decision: divergence is a marker in the target repo, not the source

**Decision**: A deliberately diverged repo carries an entry in its own `.wyrd-version` file,
e.g. `diverged_at: <sha>`, naming the manifest entry it will not adopt. `status` reports that
repo as `diverged (accepted)` for changes up to and including that entry, and evaluates any
later manifest entry normally.

**Rationale**: Directly satisfies FR-008/User Story 3. Keeping the marker in the target repo
(not a central list in this repo) means the decision travels with the repo it describes, and
`status`/`rollout` only ever need to read one file per repo to get the complete picture for that
repo — no second source of truth to keep in sync.

**Alternatives considered**: a central divergence registry in this repo (rejected: same
drift-prone shape as the rejected fleet-registry alternative above).
