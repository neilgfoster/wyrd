# Phase 1 Data Model: Fleet rollout

## `.wyrd-version` (committed in every target repo's root)

The version marker a fleet repo carries. One file, YAML, `[[wikilink]]`-free (it is data, not
prose — ADR 0011's markdown-vs-wikilink split doesn't apply to a file this small, but it stays
plain key/value to match `design/07-tooling.md` §2's "no third-party YAML dependency, small
internal reader" rule).

```yaml
template_source: wyrd-setting-template     # or wyrd-chronicle-template
template_sha: 8f3c1a9...                   # 40-hex commit SHA in the source repo
engine_sha: 4b2d701...                     # optional; commit SHA in this (wyrd) repo
diverged_at: null                          # or a manifest entry id this repo deliberately skipped
```

| Field | Type | Meaning |
|---|---|---|
| `template_source` | enum | which source repo this target was created from / tracks |
| `template_sha` | 40-hex string | last-synced commit SHA in `template_source` |
| `engine_sha` | 40-hex string or absent | last-synced commit SHA in the engine repo, if this repo declares an engine dependency |
| `diverged_at` | manifest entry id or `null` | the change this repo deliberately will not adopt; absent/`null` means no accepted divergence |

**Validation rules**: `template_source` MUST be one of the two known source repos.
`template_sha`/`engine_sha`, when present, MUST be 40 hex characters and MUST exist as a commit
in the named source repo (checked by `status`, reported as unresolvable state per the spec's
edge cases if not found — e.g. history was rewritten upstream).

## Manifest entry (`rollout/changes/<NNN>-<slug>.yaml`, committed in each source repo)

One file per rollout-eligible change in `wyrd-setting-template` or `wyrd-chronicle-template`.
Entries are ordered by `NNN` (zero-padded sequence), which also gives a stable ordering for
bundling multiple entries into one PR.

```yaml
id: 007-add-voice-guide
class: additive              # additive | structural
sha: 8f3c1a9...              # commit in the source repo this change corresponds to
summary: "Add setting/voice.md skeleton"
add:                         # present when class: additive
  - setting/voice.md
migrate: null                # present when class: structural; path to a migration script/instructions
```

| Field | Type | Meaning |
|---|---|---|
| `id` | string | stable identifier, referenced by `.wyrd-version`'s `diverged_at` |
| `class` | enum | `additive` or `structural`, per `design/09-evolution.md`'s two relevant classes |
| `sha` | 40-hex string | the commit in the source repo where this change landed |
| `summary` | string | one-line human description, used in the rollout PR body |
| `add` | list of paths, additive only | files/directories to bring into the target repo verbatim from `sha` |
| `migrate` | path or instructions, structural only | how to transform the target repo's existing state |

**Validation rules**: exactly one of `add`/`migrate` is present, matching `class`. No path
under `add` may fall under `library/`, `corpus/`, or `index/` (defense-in-depth per research.md's
private-repo decision) — an entry that does is a load error, not a warning, mirroring
`design/07-tooling.md` §4's "an override naming something outside the closed set is a load
error" pattern.

## Fleet repo record (computed, not stored — the `status` verb's output shape)

```json
{
  "repo": "wyrd-setting-hemmelfurt",
  "visibility": "PRIVATE",
  "template_source": "wyrd-setting-template",
  "recorded_sha": "8f3c1a9...",
  "state": "behind",
  "missing": [
    {"id": "008-rename-index-dir", "class": "structural", "summary": "..."},
    {"id": "009-add-voice-guide", "class": "additive", "summary": "..."}
  ],
  "diverged_at": null
}
```

`state` is one of: `current`, `behind`, `unversioned` (no `.wyrd-version` at all),
`diverged` (an accepted divergence covers all currently-outstanding entries), `unreachable`
(repo could not be read — renamed, archived, deleted, or the recorded SHA no longer exists
upstream).

## Rollout PR (produced by the `rollout` verb, not stored — describes what gets opened)

- One PR per repo whose `status` is `behind`.
- Branch name: `wyrd-fleet-rollout/<latest-entry-id>`.
- Body lists every bundled entry (`id`, `class`, `summary`) in order.
- Additive entries: files copied verbatim from the source repo at each entry's `sha`.
- Structural entries: the entry's `migrate` step applied to the target repo's current tree.
- Never pushed directly to the target repo's default branch (FR-004).
