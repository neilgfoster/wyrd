# Implementation Plan: Scenarios Index Build and Bootstrap Wiring

**Branch**: `166-scenarios-index-build` | **Spec**: `spec.md`

## Summary

Add `tools/setting_scenarios.py` to the engine repo: a thin CLI, following
`tools/setting_build.py`'s own convention, with two verbs (`plan`, `commit`) over the already-built
pure logic in `engine/wyrd/corpus_pipeline.py` (`build_scenario_index`,
`documents_needing_scenario_generation`, `scenario_cache_status`) and
`engine/wyrd/corpus_scenario.py` (`validate_scenario_record`). `commit` takes a caller-supplied
JSON file of already-produced scenario records (the injected-model-response pattern
`generation_pipeline.py` established) and never calls a model itself. Then wire
`wyrd-chronicle-template/.claude/skills/wyrd-bootstrap/SKILL.md` Step 3 to prefer
`scenario_selection.select_scenario` against a setting's `index/scenarios.json` when present and
non-empty, falling back to today's `entities/`-reading path otherwise. Finally, run `commit` for
real against `wyrd-setting-titan`'s `03 - adventures/` for a handful of gamebooks, each record
grounded in that adventure's own `corpus/` text, and commit the result in that setting repo.

## Technical Context

- Python 3.11+, standard library only (engine repo constraint).
- No new engine-repo dependency; reuses `corpus_pipeline`/`corpus_scenario` unchanged.
- `wyrd-chronicle-template` and `wyrd-setting-titan` changes are out of this repo's ruff/lint
  scope but follow their own existing conventions.

## Constitution Check

- No setting/system name enters `docs/design/` or `README.md`: the new tool and its docstrings
  stay setting-agnostic (a caller-supplied path filter, never a hardcoded directory name).
- Capability change -> Spec Kit cycle applies (this document).
- ruff clean, line length 100, `E`/`F`/`I`/`UP`, target 3.11.

## Project Structure

### New/changed files (this repo)

```
tools/setting_scenarios.py       # new: plan/commit CLI verbs
tools/test_setting_scenarios.py  # new: unit tests against fixtures
specs/166-scenarios-index-build/ # this spec/plan/tasks
```

### Changed files (other repos, tracked here for the record but reviewed under those repos' own
conventions)

```
wyrd-chronicle-template/.claude/skills/wyrd-bootstrap/SKILL.md   # Step 3 rewritten
wyrd-setting-titan/index/scenarios.json                          # built for real
wyrd-setting-titan/index/scenario_build_cache.json               # built for real
```

## Phase 0: Research

No open unknowns -- `corpus_pipeline.py`/`corpus_scenario.py`/`scenario_selection.py` already
specify every primitive this feature composes; `tools/setting_build.py` already specifies the CLI
convention to follow. No `research.md` needed.

## Phase 1: Design

- `plan` verb: reads a setting directory's `index/corpus_build_cache.json` (path -> content hash,
  written by `tools/setting_build.py`) and `index/scenario_build_cache.json` if present, filters
  to documents matching a caller-supplied `--path-prefix` (default: all), and reports each as
  `missing`/`stale`/`fresh` via `corpus_pipeline.scenario_cache_status`.
- `commit` verb: takes the same filtered document set plus `--records <file>` (a JSON object,
  document id -> already-produced scenario record). Builds a `generate(doc)` closure that looks up
  `doc["id"]` in that file, validates it with `corpus_scenario.validate_scenario_record`, and
  raises naming the id if it's absent or invalid. Calls `corpus_pipeline.build_scenario_index`
  with that closure; on success, writes `index/scenarios.json` (the full record list) and
  `index/scenario_build_cache.json` (the updated cache, JSON-serializable form of the `(setting,
  id)`-keyed dict). On the closure raising, writes neither file (all-or-nothing, FR-005).
- Bootstrap wiring: Step 3 first checks for `setting/../index/scenarios.json` (the setting's own
  built index, read-only from a chronicle) -- if present and non-empty, load it, call
  `scenario_selection.select_scenario` with the chronicle's live threads-so-far (empty at
  bootstrap, since no arc has run yet) and treat the player's stated `about`/`avoid` as the
  matching signal the skill's own judgment applies (this module's `select_scenario` matches on
  thread heat, which is empty at bootstrap -- so Step 3's own prose describes filtering candidates
  by `is_eligible_for_setting`/theme-match against intent, the same judgment-call framing Step 3
  already uses for choosing an entity, now applied to a richer candidate pool). If the file is
  absent or `[]`, Step 3's existing entities/-reading text is unchanged.

## Complexity Tracking

No violations to justify.
