# Phase 0 Research: Setting-Level Character Creation Data

No `NEEDS CLARIFICATION` markers were left in the Technical Context — this is a small,
self-contained addition to an existing, well-established pattern in this repo (`check_bestiary.py`,
`check_gear.py`, `check_setting.py`), so no external research was needed. This document records
the decisions made instead, in the same Decision/Rationale/Alternatives shape Phase 0 calls for.

## Decision: One validator script covering all six files, not one script per file

**Rationale**: the issue's own Definition of Done says "There is one creation procedure, not an
engine one and a setting one." A single `check_character_creation_data.py` mirrors that: one
command tells a setting author whether the *whole* character-creation surface is ready, rather
than six commands they have to remember to run and reconcile themselves. It also matches how the
files are consumed — `11-character-creation.md`'s procedure reads all of them together in one
pass, never one in isolation.

**Alternatives considered**: a `check_careers.py`, `check_loyalties.py`, etc. pattern mirroring
`check_bestiary.py`/`check_gear.py`'s one-file-one-script layout. Rejected: `careers.yaml` and
`gear.yaml` are large, independently-evolving tables consulted throughout play, not just at
creation, so a dedicated script for each earns its keep. Loyalties/Drives/Misfortunes/Names/
ancestries are small, creation-only inputs that are only ever meaningful together — splitting them
into five scripts would recreate the "two documents describing one thing differently" drift class
`CLAUDE.md` calls out, since nothing would then check they are all present and mutually
consistent (e.g. §4's "at least two skills opened" language and career/ancestry pool union
already assumes both exist together).

## Decision: Reuse `check_bestiary.py`'s YAML reader, not a new one

**Rationale**: `check_gear.py` and `check_setting.py` already import `read_yaml`/`YamlError` from
`check_bestiary.py` rather than each writing their own. `docs/design/27-tooling.md` section 2
requires no third-party YAML dependency; a third hand-written reader would be the "two documents
describing one thing differently" fault class applied to code instead of prose.

**Alternatives considered**: adding `PyYAML` as a dependency. Rejected outright — violates the
stdlib-only constraint the three existing validators already satisfy, for no gain since the
existing reader already handles every YAML shape this feature's files need (flat lists of
mappings, list-of-string leaf values).

## Decision: `careers.yaml` gets validated by this new script, not a separate one

**Rationale**: `careers.yaml`'s shape has been fully specified in
`docs/design/24-authoring-a-setting.md` since that document was written, but grep across `tools/`
turns up no `check_careers.py` — the rules FR-003 states (entry/prerequisite shape, acyclic graph,
at least one entry career) have never been checked by anything. Since this feature's whole point is
closing exactly this kind of documented-but-unvalidated gap, leaving `careers.yaml` out because it
already has *prose* would defeat the purpose.

**Alternatives considered**: raising a separate tactical issue for `check_careers.py` and leaving
it out of this feature. Rejected: `careers.yaml` is one of §4's required inputs, so a "the
character-creation contract is specified and in the template... validated, not merely documented"
claim (issue #37's own acceptance criteria) would be false with careers left unchecked.

## Decision: Ancestries are optional in the validator, exactly as in the design doc

**Rationale**: `11-character-creation.md` §3 is explicit — "a setting may optionally declare an
ancestry" — and a setting with none "declares nothing, and creation is exactly as described
above." The validator must not require a file the design document itself says a setting need not
have.

**Alternatives considered**: requiring `ancestries.yaml` to exist but allowing it to be empty.
Rejected — an empty-but-present file versus an absent file is a distinction the design document
does not draw, and inventing one would be new engine behaviour this feature does not need.

## Decision: Repository-boundary scope — no changes outside `wyrd`

**Rationale**: `CLAUDE.md`'s repository table places `wyrd-setting-template`'s skeleton and any
setting's actual population outside this repository entirely; this feature's own worktree has no
access to those repositories. `docs/design/24-authoring-a-setting.md` and `tools/` are exactly
where the engine's half of a setting contract belongs — the schemas a setting's data must satisfy,
and the tool that checks it, both live with the engine that defines what "correct" means, the same
way `check_bestiary.py` and `check_gear.py` already do for their tables.

**Alternatives considered**: attempting to also update `wyrd-setting-template` or a real setting
repository from this session. Not possible — those repositories are not present in this worktree
and are not this repository's to change; doing so would also violate the "nothing unpublishable
enters this repository" rule in reverse (engine tooling has no business appearing inside a setting
repo's own history via a side channel). Tracked instead as follow-up work for those repositories,
per the Assumptions section of `spec.md`.
