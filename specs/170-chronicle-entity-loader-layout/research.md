# Research: Chronicle Entity Loader Layout

## Decision: canonical on-disk layout

**Decision**: `setting/entities/<type>/<id>.yaml`, `overlay/<type>/<id>.yaml`, and
`entities/<type>/<id>.yaml` — one per-type-subdirectory rule applied uniformly to all three
chronicle directories.

**Rationale**: `setting/entities/<type>/` and `entities/<type>/` are directly observed, populated
this way in both `wyrd-chronicle-darkfuture-rookie-op` (a real chronicle pinned to main) and
`wyrd-setting-darkfuture`'s `.claude/skills/create-setting` skill output (per-type directories
with `.gitkeep` placeholders for every entity type, including types with no files yet — e.g.
`setting/entities/tracker/.gitkeep`, `setting/entities/creature/.gitkeep`). `overlay/` is
observed empty (only `overlay/README.md`) in every chronicle checked, so its shape is a decision
rather than an observation — resolved in spec.md's Clarifications session by mirroring the other
two directories, for one consistent rule.

**Alternatives considered**: a flat `overlay/<id>.yaml` (no type subdirectory, since
`overlay_of` already names the target and its type). Rejected per the clarification: consistency
across all three directories was judged worth more than the one-line path shortening a flat
`overlay/` would give.

## Decision: file format — no change needed

**Decision**: `state.load_entity`/`state.parse_entity` (engine/wyrd/state.py) are already
extension-agnostic — they split any file's text on `---` frontmatter delimiters regardless of
the path's suffix. The `.yaml` files observed in real chronicles use the identical
`---\n<frontmatter>\n---\n<body>` shape as the `.md` files the loader currently assumes
(confirmed by inspecting `setting/entities/faction/hammond-maninski-agency.yaml` and
`entities/faction/vance-acceptance.yaml` byte-for-byte). No parsing change is required — only the
glob pattern needs to look for `.yaml` instead of (or alongside) `.md`, one directory level
deeper.

**Rationale**: Confirms FR-002 (spec.md) is satisfiable with zero changes to `entity.py`/
`state.py`'s parsing logic — the fix is entirely in `resolution.py`'s directory-walking, which
lowers the risk and size of the change.

**Alternatives considered**: none — this was a factual question (does the format differ?), not a
design choice.

## Decision: a first-line frontmatter-delimiter filter is needed after all

**Original decision (superseded during implementation — kept here for the record)**: this
research initially concluded no special-case guard against `README.md`/`.gitkeep` was needed,
reasoning that once the loader globs `setting/entities/<type>/*.yaml` one level deeper,
`setting/README.md` would no longer match (it isn't in a type subdirectory and isn't `.yaml`).

**Why that was wrong**: it only considered the *new* nested glob. FR-004 also keeps the flat
`(root / "setting").glob("*.md")` active for back-compat, and that flat glob still matches
`setting/README.md` exactly as it always did — every real chronicle checked has exactly such a
README sitting alongside its entities. The implementation's own regression test
(`test_readme_at_directory_top_level_does_not_crash_or_count_as_an_entity`) caught this
immediately: it raised `state.StateError`, the precise crash #440 reported, because keeping
FR-004's back-compat glob active necessarily keeps the original crash active too.

**Corrected decision**: filter every candidate path (from both the flat and nested globs) through
`_looks_like_entity_file` — a cheap check that the file's first line is the `---` frontmatter
delimiter `state.parse_entity` already requires — before handing it to `entity.load`/
`entity.load_set`. A `.gitkeep` placeholder inside a type subdirectory still needs no such guard
(it never matches a `*.yaml` glob in the first place); only the flat-glob/README interaction
needed the filter.

**Rationale**: This distinguishes "not an entity at all" (fails the delimiter check, silently
excluded) from "a broken entity" (opens with `---` but is otherwise malformed — still raises
through the normal `entity.load` path, exactly as before). It doesn't swallow a genuine authoring
error, only files that were never entities to begin with.

**Alternatives considered**: adding an explicit try/except around each file load to skip
unparseable files silently. Rejected — this would also swallow a malformed *real* entity file
(wrong frontmatter, corrupted content), hiding an actual authoring error rather than surfacing
it. The first-line delimiter check is narrower: it only excludes files that never claimed to be
entities in the first place.

## Decision: back-compat with the flat top-level layout

**Decision**: The loader will continue to check flat top-level `setting/*.md`, `overlay/*.md`,
`entities/*.md` in addition to the new nested `.yaml` walk, per FR-004.

**Rationale**: This module's own existing unit tests build fixtures directly against loose files
(`_find_chronicle_root`'s own docstring notes this), and nothing in the codebase demonstrates
that the flat layout is fully retired. Accepting both avoids a silent regression for any
in-progress fixture or chronicle still using the old shape, at negligible cost (one more pair of
globs).

**Alternatives considered**: dropping flat-`.md` support outright. Rejected — no evidence anyone
currently depends on being unable to add nested entities, but plenty of evidence (this module's
own tests) that flat fixtures still exist; dropping it is a strictly riskier move for no
observed benefit.
