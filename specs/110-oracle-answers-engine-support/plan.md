# Implementation Plan: Oracle answers engine support

**Branch**: `110-oracle-answers-engine-support` | **Spec**: [spec.md](spec.md) | **Issue**: #291

## Summary

Add the five oracle-answer bands as pure data to `engine/wyrd/rules.py` (the module that already
holds `oracle_prompt`'s sibling table and pure lookups `roll_d100`, `_wyrd_die`,
`declaration_bonus`), a lookup function `oracle_answer(band, roll)` that rejects an unrecognized
band with `ValueError`, and a new `oracle-answer` verb (`verbs.py`/`catalog.py`/`client.py`) that
rolls `1d100` via `rules.roll_d100`, looks up the outcome, and reads the Wyrd die from the same
roll via the existing `_wyrd_die` helper — read-only, no state write, matching `oracle_prompt`'s
shape exactly (FR-006).

## Technical Context

- **Language**: Python 3.11+, standard library only.
- **Existing modules**: `engine/wyrd/rules.py` (`roll_d100`, `_wyrd_die`, `ORACLE_PROMPT_TABLES` /
  `oracle_prompt`), `engine/wyrd/verbs.py` (`oracle_prompt` — the read-only verb this feature's
  verb mirrors), `engine/wyrd/catalog.py` (`TOOLS` dict), `engine/wyrd/client.py` (argparse
  subparser + dispatch per verb).
- **Sibling family**: oracle prompts (#290/PR #293) landed immediately before this feature and
  is the closest precedent — same module, same read-only verb shape, same catalog/client wiring
  pattern.
- **Testing**: `tests/engine/test_rules.py` and `tests/engine/test_verbs.py` already carry the
  `oracle_prompt` tests this feature's tests sit alongside.

## Design decisions

- **Table lives in `rules.py`, next to `ORACLE_PROMPT_TABLES`.** Same rationale as that sibling
  feature's plan: this is a small table-lookup mechanic, not a module's worth of its own.
- **One lookup function, `oracle_answer(band: str, roll: int) -> tuple[str, str]`,** returning
  `(outcome, wyrd)` — the outcome key (`exceptional_yes`, `yes`, `no`, `exceptional_no`) and the
  Wyrd die reading for that same roll, read via the module's own `_wyrd_die` helper (the private
  function `opposed_test` already calls from within this module — never exposed across the
  `rules.py`/`verbs.py` boundary, matching every other private helper in this module). Band
  validation raises `ValueError` naming the five valid bands (FR-003); an out-of-range roll raises
  `ValueError` too, matching `oracle_prompt`'s existing convention exactly.
- **Table data as `ORACLE_ANSWER_THRESHOLDS: dict[str, int]`** (the five bands' `T` values:
  `90, 70, 50, 30, 10`) plus a pure `_oracle_answer_rows(threshold)` helper that derives the four
  `(range, outcome)` rows from `T` — rather than hand-writing 20 rows across five bands, since the
  four-row shape is a deterministic function of `T` alone
  (`docs/design/14-oracle-answers.md`: rows 1-5 / 6-T / T+1-95 / 96-100 for every band) and
  `tools/check_oracle_answers.py` already treats it that way. This keeps the single source of
  truth as the five threshold values, matching `CLAUDE.md`'s "check the maths" — deriving the rows
  algorithmically means there is no second place the 1-5/96-100 shape could drift from the design
  doc.
- **The verb (`oracle_answer` in `verbs.py`) rolls internally** via `rules.roll_d100(seed=seed)`,
  then calls `rules.oracle_answer(band, roll)` for `(outcome, wyrd)`, returning
  `{"verb": "oracle-answer", "band": ..., "roll": ..., "outcome": ..., "wyrd": ..., "seed": ...}`.
  No `state_written` field and no call into `state.py` — read-only end to end (FR-006), matching
  `oracle_prompt()`'s shape exactly. This is a deliberate deviation from the feature-description
  draft's initial framing (staging this as a `resolution.py`-style state-mutating roll): the
  design doc's own Recording section states the beat-log entry is written by the caller from this
  same tuple, not by this lookup itself — identical to how `journey.roll_hazard` resolves a table
  without writing to any log, and how `oracle_prompt` (this family's closest sibling) already
  chose read-only over `resolution.py`'s propose/commit machinery for the same reason: nothing
  here mutates persisted entity state.
- **`ValueError` from an unrecognized band or an out-of-range roll propagates unchanged**,
  handled by `client.py`'s existing per-verb `try/except` boundary into the structured
  `{"error": ...}` shape — no new error-handling convention.
- **Catalog entry `oracle-answer`** mirrors `oracle-prompt`'s shape: `band` (enum of the five
  band names) required, `seed` optional integer, `readOnlyHint: true`.

## Project Structure

```
engine/wyrd/rules.py     # ORACLE_ANSWER_THRESHOLDS data, oracle_answer() lookup
engine/wyrd/verbs.py     # oracle_answer() verb wrapper (rolls + looks up + Wyrd die, no state write)
engine/wyrd/catalog.py   # "oracle-answer" TOOLS entry
engine/wyrd/client.py    # subparser + dispatch for "oracle-answer"
tests/engine/test_rules.py   # table-coverage tests (every band, every boundary)
tests/engine/test_verbs.py   # verb tests
```

## Constitution Check

No `.specify/memory/constitution.md` exists in this repo — governance here is CLAUDE.md and the
design documents' own ADRs, both already followed above (deterministic-over-inference: dice via
`rules.roll_d100`, never `random` directly; the Wyrd die reused via the existing `_wyrd_die`
helper rather than a second units-digit implementation; no setting vocabulary in engine code;
table data matches the shipped design document, verified by the existing check script rather than
eyeballed).
