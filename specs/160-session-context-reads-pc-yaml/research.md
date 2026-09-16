# Phase 0 research: session-context resolves the player character from pc.yaml

No `NEEDS CLARIFICATION` markers remained after `spec.md`'s Assumptions section — the research
below was already done during specification (grep + design-doc reading, not inference) and is
recorded here so `plan.md`'s Phase 0 gate has something concrete to point at.

## Decision: read `pc.yaml` directly into `verbs.load_effective_entities`'s dict

**Rationale**: `verbs.load_effective_entities` (engine/wyrd/verbs.py) is the one function
`session-context`, `get`, `find`, and `party` all call to build their shared entity dict. It
delegates to `resolution._load_chronicle_entities`, which globs `setting/*.md`, `overlay/*.md`,
`entities/*.md` — never `pc.yaml`. `entity.load(path)` (engine/wyrd/entity.py:268) already loads
and validates exactly one entity file by path and returns its frontmatter; `pc.yaml` uses that
same frontmatter+body schema (confirmed below), so the smallest correct fix is: after
`resolution._load_chronicle_entities` returns, if `<chronicle_dir>/pc.yaml` exists, load it with
`entity.load` and add it to the dict keyed by its own `id`. This keeps the "only one place reads
the chronicle's file layout" property intact for `entity.py`/`resolution.py`, and gives
`get`/`find`/`party` the same visibility `session-context` gets, satisfying User Story 2 without
duplicating logic four times.

**Alternatives considered**:
- *Change `resolution._load_chronicle_entities` itself to also glob `pc.yaml`.* Rejected:
  `resolution.py` backs proposal validation (commit-time checks) and is explicitly off-limits
  this pass (issue #414 may be landing concurrently against that file in a sibling batch member).
  Even absent that constraint, `resolution._load_chronicle_entities` is keyed off
  `_find_chronicle_root`'s directory-shape detection (must have `entities/`, `overlay/`,
  `setting/` all as subdirectories) — entangling a chronicle-root-only file like `pc.yaml` into
  that generic, proposal-facing helper would widen its contract for one caller's benefit.
- *`session-context`-only special case in `loadtier.always_tier`.* Rejected: `always_tier` takes
  an already-built `entities` dict — it has no path/IO of its own, and giving it one would break
  its otherwise-pure, testable-with-a-dict-literal shape. It would also leave `get`/`find`/`party`
  still blind to `pc.yaml` (User Story 2 unmet).
- *Have `/wyrd-bootstrap` mirror the player character into `entities/`.* Rejected by the issue
  itself (creates two copies of the same character that can drift) and out of scope regardless —
  that skill lives in `wyrd-chronicle-template`, a different repository this PR does not touch.

## Decision: `pc.yaml`'s file format is the same entity frontmatter+body schema

**Rationale**: `specs/156-wyrd-bootstrap-skill/contracts/wyrd-bootstrap-skill.md` states
`pc.yaml` is authored "per docs/design/25-entities.md's plain frontmatter+prose schema, the same
way a human setting author writes one" — i.e. `---\n<yaml>\n---\n<body>`, loadable by
`state.load_entity`/`entity.load` unchanged. This was confirmed by reading that already-merged
spec rather than assumed from the `.yaml` extension (which could otherwise suggest a bare-YAML,
no-frontmatter-delimiter file).

**Alternatives considered**: Assuming `pc.yaml` is bare YAML (no `---` delimiters, frontmatter
only, no body) was considered but rejected without a second reader/writer path already existing
for that shape anywhere in the engine — `entity.load` is the only loader this fix needs, and using
it keeps the schema/validation path identical to every other entity file.

## Decision: duplicate `role: player` entities raise, matching `always_tier`'s existing rule

**Rationale**: `loadtier.always_tier` already raises `ValueError` if more than one entity carries
`role: player`. Once `pc.yaml` is merged into the same entities dict `always_tier` consumes, a
stray `entities/*.md` player-role file colliding with `pc.yaml` is caught by that same existing
check for free — no new duplicate-detection code is needed in `load_effective_entities` itself.

**Alternatives considered**: Have `load_effective_entities` itself detect and reject an id
collision between `pc.yaml` and an existing entity before merging. Rejected as redundant:
`dict.update`-style merging already lets whichever id `pc.yaml` declares simply take that slot in
the dict (an id collision, not a silent multiple-player-character situation, is already handled
by `resolution._check_duplicate_id`-style reasoning belonging to write-time proposals, not this
read path) — and the `role: player` collision case specifically is what `always_tier` already
guards, which is the one case this feature's spec calls out (FR-005).
