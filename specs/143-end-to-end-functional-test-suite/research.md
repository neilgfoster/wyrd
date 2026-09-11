# Research: End-to-end functional test suite

Phase 0 output. Each decision was checked against the actual module source and its existing
unit-test file under `tests/engine/`, not guessed.

## Decision: driver module and fixture shape

- **Decision**: One `unittest.TestCase` in `tests/engine/test_integration.py`, using the same
  `sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))` +
  `from wyrd import ...` pattern every existing file in `tests/engine/` already uses, backed by a
  single `tempfile.TemporaryDirectory()` per test.
- **Rationale**: matches repo convention exactly (CLAUDE.md, docs/design/27-tooling.md); no new
  test-support module needed.
- **Alternatives considered**: pytest fixtures — rejected, repo's own convention is stdlib
  `unittest` throughout `tests/engine/`, confirmed by every existing file there.

## Decision: which concrete functions each of the 11 areas calls

Resolved by reading `engine/wyrd/*.py` and each area's own `tests/engine/test_*.py` directly.
Full call shapes, argument examples, and exact seeds are recorded in this feature's
`quickstart.md` and `data-model.md`, and were cross-checked against:

- `creation.create_character` (creation, area 1)
- `resolution.propose`/`commit` for `ordinary-test`, `combat-attack`, `exposure`,
  `system-of-power` mechanics (areas 2, 3, 6, 8)
- `downtime.apply_mend`/`apply_rest` plus the 5-step downtime loop (area 4)
- `adversary.load`/`adjusted_skill` against an inline bestiary fixture (area 5)
- `economy.spend_coin`/`adjust_standing`/`gain_allegiance` (area 7)
- `journey.legs_for`/`roll_hazard`/`close_journey` plus `scenario_selection`'s in-memory dict
  functions (area 9)
- `session.new_loop_state`/`advance_loop`, `rally.apply_rally`, `advancement` records (area 10)
- `state.default_chronicle_state`/`save_chronicle`/`load_chronicle` plus
  `chronicle.record_rolled`/`discard_at_rally` (area 11)

## Decision: determinism

- **Decision**: reuse exact seeds already proven correct in `tests/engine/test_resolution.py`
  (e.g. `20260852` for the Exposure worked example that gains +2 taint on a bargaining-40
  actor, `2` for the combat chain that lands a telling, mortal-false slashing blow) rather than
  picking fresh seeds and trusting an eyeballed outcome.
- **Rationale**: CLAUDE.md's "check the maths" note — probability/seed claims in this repo have
  been wrong twice before, caught only by computing them; reusing a seed another test file
  already computed and asserts against removes that risk entirely for this feature.
- **Alternatives considered**: a fresh seed chosen to "look like" a landed blow — rejected, no
  way to verify without literally running the RNG, which the existing test already did.

## Decision: no real corpus dependency

- **Decision**: solo-procedure modules (`corpus_scenario.py`, `scenario_selection.py`,
  `arc_selection.py`, `journey.py`) are exercised via caller-supplied in-memory dicts; no real
  corpus text file is created or read.
- **Rationale**: confirmed by reading each module's own functions — none of the four opens a file
  itself; they all take an already-loaded `record`/`threads`/`candidates` dict. Only
  `corpus_document.py`/`corpus_terms.py`/`corpus_find.py` (not in this feature's required
  sequence) parse real text, and per wyrd's own repo split (CLAUDE.md's repo table) real corpus
  text belongs in `wyrd-research`, never in this repo's tests.
- **Alternatives considered**: stubbing a fake corpus file on disk — rejected as unnecessary once
  the module boundary was actually checked, and it would have invented a fixture shape not
  reflective of how these modules are really called elsewhere in the repo.

## Decision: validation-layer scope, and which economy verb to exercise

- **Decision**: entity files for this suite are loose files under the temp directory (no
  `entities/`/`overlay/`/`setting/` chronicle tree), matching how `test_resolution.py` and
  `test_combat.py` already construct their own fixtures. The economy area exercises
  `economy.gain_holding` rather than `economy.gain_allegiance`.
- **Rationale**: `resolution.commit`'s own `_validate_proposal` passive-validation pass is *not*
  gated behind a discoverable chronicle root the way this feature first assumed while planning --
  running the suite for real caught this (CLAUDE.md "check the maths" applies just as much to a
  behavioural assumption as to a probability): `_load_chronicle_entities` returns `{}` with no
  root, but `_validate_proposal` still runs its four passive checks against whatever the
  mutation's own entity resolves to, including `entity.unresolved_references`'s check of
  `_REFERENCE_FIELDS` (`parent`, `links`, `allegiances`, `cast`, `members`, `based_at`). Once
  `allegiances` names an id with no matching entity anywhere in the (empty, loose-file) merged
  set, every later `resolution.commit` against that same character raises `ProposalError` --
  confirmed by actually hitting it once `gain_allegiance` was wired in. `holdings` is not one of
  `_REFERENCE_FIELDS`, so `economy.gain_holding` exercises the same set-membership verb family
  with no chronicle-root dependency, staying inside this feature's scope (FR-007: no new engine
  capability, so no full `entities/`/`overlay/`/`setting/` tree is built just to satisfy one
  reference field's check).
- **Alternatives considered**: building the full chronicle root so `allegiances` could be used
  after all — rejected: it would require every entity file this suite touches (including the
  combat attacker and the adversary-derived creature) to also satisfy `entity.validate`'s full
  common-field schema (`id`/`type`/`name`/`setting`/`status`), which `creation.create_character`'s
  own player-character shape does not carry either — confirming this is a genuinely separate
  concern from character-level propose/commit, not a gap in this suite's fixtures.
