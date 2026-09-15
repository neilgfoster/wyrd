# Research: Chronicle CLI Verbs

## Existing pure-function coverage (per verb)

A pass over `engine/wyrd/{session,chronicle,state,era,thread,threat,entity,loadtier,
advance_time,party}.py` found more coverage than the issue text alone suggested — several
verbs are near-direct wrappers over functions the "authoring-a-setting"/"chronicle state" epics
(#297/#300) already landed.

| Verb | Existing function | Gap this feature fills |
|---|---|---|
| `session-context` | `loadtier.always_tier(entities)` — exact Always-loaded composition | Compose with `chronicle.yaml`, `recap.md` text, and the engine contract text (all plain file reads); no new pure logic |
| `get <id>` | `entity.resolve_entity(id, setting_entities, overlays, ...)` — effective-form resolution, already raises `state.StateError` on an unknown id | None — thin wrapper loading the three entity sources and calling it |
| `find --type T [--status S] [--tag G]` | none | New: a general multi-filter query over the loaded entity set (type/status/tag, each optional, all ANDed) |
| `party` | `party.roster(companions)` — pass-through once companions are selected | New: the `role: companion` + `status: with-party` filter itself (a small predicate, not a duplicate of `find`'s public flags — see spec.md Clarifications) |
| `threads` | none directly (`loadtier._hottest_open_threads` caps at 3 and is private) | New: the *full* `status: open` set sorted by `heat` descending — broader than `session-context`'s slice, so a new function rather than a hidden cap change |
| `threats` | `threat.active_threats(entities)` — entities with `imminence > 0` | None — thin wrapper |
| `log --last N \| --since <beat>` | none | New: `log/` has no reader today; `loadtier.py` explicitly defers this ("reachable by ordinary file access... deliberately never surfaced"). This feature adds the minimal read function the CLI verb needs (see "Log format" decision below) |
| `save` / `load` / `validate` | `state.save_chronicle` / `state.load_chronicle` / `state.validate_chronicle` | None — thin wrappers |
| `recap` | `loadtier.generate_recap` + `loadtier.recap_close_step` | None — thin wrapper supplying `where`/`changes`/`body_mind` as caller-optional CLI flags |
| `advance-time <days>` | `advance_time.advance_time(calendar, threats, elapsed_days, seed=...)` | None — thin wrapper |
| `threat-check` | `threat.check_activation(imminence, wyrd_roll)` | None — thin wrapper drawing one roll via the existing dice tool and a single threat's imminence |

## Decision: log format

**Decision**: log entries are JSON Lines, one record per resolved beat, each shaped
`{"beat_id": str, "mode": "played"|"summarised", "resolved_at": float}` — exactly
`session.narrate_beat`'s existing return shape, appended to a single live file
(`log/<chronicle-name>.jsonl`) as beats resolve. `log --last N` returns the last N lines
parsed and returned in file order (which is already beat order, since entries are appended in
resolution order); `log --since <beat>` returns every entry from the first occurrence of
`beat_id == <beat>` onward.

**Rationale**: `session.narrate_beat` already defines the one narration record this codebase
produces; reusing its exact shape avoids inventing a second, competing log-entry format. JSON
Lines matches `docs/design/28-maintenance.md`'s own stated archive format
(`log/archive/<era>.jsonl`) for old entries, so the live file and its eventual archived form
share one convention rather than two.

**Alternatives considered**:
- A structured chronicle-state field (e.g. `chronicle.yaml`'s own list) — rejected: `chronicle.
  yaml`'s schema (`state.py`'s `_CHRONICLE_REQUIRED_FIELDS`) is fixed and versioned; growing it
  unboundedly with every beat contradicts `docs/design/22-state.md`'s "Archival, rarely read"
  characterisation of `log/` as a separate location precisely so it never grows the always-loaded
  file.
- Deferring `log` entirely as out of scope — rejected: the issue and
  `docs/design/02-architecture.md` both name it as one of the eleven verbs to wire, and
  `session.narrate_beat` already gives it a well-defined record shape to read, so there is no
  open design question blocking it.

## Decision: `find`'s filter semantics

**Decision**: `find --type T [--status S] [--tag G]` runs over the loaded entity set (setting +
overlay, effective form, plus chronicle-native entities), keeping only entities where every
given filter matches: `frontmatter["type"] == T`, and (if given) `frontmatter["status"] == S`
and `G in frontmatter.get("tags", [])`. Omitted filters are not applied. `party`/`threads`/
`threats` are separate named functions using the same effective entity set but their own fixed
predicates (`role`+`status` for `party`, `status`+`heat` order for `threads`, threat-block
presence for `threats`) — not literal `find` calls, since their predicates need fields (`role`,
`heat` ordering) `find`'s own public flags do not expose (spec.md Clarifications, 2026-09-15).

**Rationale**: matches `docs/design/02-architecture.md`'s literal `find --type T [--status S]
[--tag G]` signature exactly, and keeps `find`'s own flag surface unchanged rather than growing
it to accommodate every named verb's distinct predicate.

**Alternatives considered**: extending `find` with a generic `--field value` filter that `party`/
`threads`/`threats` could all delegate to — rejected as an unrequested generalisation beyond
what the issue or the architecture document ask for; the three named verbs are explicitly
described as "thin named wrappers over `find`... for the query patterns already named as
queries," not literal re-invocations of `find`'s own CLI surface.

## Decision: effective entity set assembly

**Decision**: every verb that reads entities (`session-context`, `get`, `find`, `party`,
`threads`, `threats`) assembles its working set the same way: load `setting/**/*.md` via
`entity.load_set`, load `overlay/**/*.md` the same way, resolve each id through
`entity.resolve_entity`, and merge in `entities/**/*.md` (chronicle-native, no overlay
resolution needed) unchanged. This one assembly routine is added once (in `verbs.py`, alongside
the other thin wrappers) and reused by every verb above, rather than each verb re-deriving it.

**Rationale**: `docs/design/22-state.md`'s own definition of "effective entity" is exactly this
composition; every verb in this feature needs the same set, so building it once avoids six
near-identical, easily-diverging copies.

## Testing approach

Match the repo's existing convention exactly (`docs/design/27-tooling.md` §6, and every file
under `tests/engine/`): stdlib `unittest`, no pytest, one `test_<verb-area>.py` (or additions to
an existing one where a verb's area already has a test file — e.g. `test_threat.py` for
`threat-check`, `test_advance_time.py` for `advance-time`, `test_loadtier.py` for
`session-context`/`get`/`recap`) asserting real computed values, run via
`PYTHONPATH=engine python3 -m unittest discover -s tests/engine`.
