# Tasks: Setting Overrides Mechanism

All tasks below were completed and verified during implementation (`ruff check`, `ruff format
--check`, `python3 -m pytest -q`, `python3 -m unittest discover -s tests/engine`, and the
quickstart commands, all green).

- [X] **T001** Extend `engine/wyrd/state.py`'s restricted YAML reader with flat flow-style
  `[...]`/`{...}` scalar-collection parsing, so an `overrides:` block written in the design docs'
  own documented shape parses correctly.
- [X] **T002** Mirror T001's parsing extension in `tools/check_bestiary.py`'s reader (the
  tools-side layer, independent of engine/ by design).
- [X] **T003** Create `engine/wyrd/overrides.py`: the closed `OVERRIDABLE` set,
  `describe_overridable()`, `validate_block()`, `resolve()` (three-layer, narrowing-only),
  `ResolvedConfig` and `filter_tools()`.
- [X] **T004** Add the `track` tool to `engine/wyrd/catalog.py`, tagged `mechanisms: ["taint",
  "trauma"]`, giving the disable/rename mechanism a real catalog entry to act on.
- [X] **T005** Add `verbs.track()`, enforcing "disabled is a structured error, not a silent
  no-op" and applying a rename only to the presented `label`, never to the `mechanism` field.
- [X] **T006** Wire `client.py`: `describe --overridable`; `describe --setting/--chronicle`
  (loads and resolves, filters the catalog); `track` subcommand with the same `--setting`/
  `--chronicle` flags; `OverrideError` caught and reported as a structured `{"error": ...}` for
  both verbs.
- [X] **T007** Add `render.py` text-output cases for `describe --overridable` and `track`.
- [X] **T008** Wire `tools/check_setting.py`'s `overrides:` validation to
  `wyrd.overrides.validate_block`, closing the gap #315 deliberately left open.
- [X] **T009** Tests: `tests/engine/test_overrides.py` (new), `tests/engine/test_verbs.py`
  (+`TrackVerbTest`), `tests/engine/test_client.py` (+`OverridableTest`),
  `tests/engine/test_state.py` (+`FlowStyleCollectionTest`), `tools/test_check_setting.py` (new
  -- first test coverage for `check_setting.py` at all).
- [X] **T010** Run the quickstart's six manual steps against the built CLI and confirm each
  matches its documented output exactly.
- [X] **T011** `ruff check .`, `ruff format --check .`, `python3 -m pytest -q`, `python3 -m
  unittest discover -s tests/engine`, `python3 tools/check_docs.py`, `python3 tools/backlog.py
  check` -- all green.
