# Implementation Plan: Oracle prompts engine support

**Branch**: `109-oracle-prompts-engine-support` | **Spec**: [spec.md](spec.md) | **Issue**: #290

## Summary

Add the four oracle-prompt tables as pure data to `engine/wyrd/rules.py` (the module that already
holds pure, no-I/O lookup logic — `roll_d100`, `declaration_bonus`), a lookup function
`oracle_prompt(family, roll)` that rejects an unrecognized family with `ValueError`, and a new
`oracle-prompt` verb (`verbs.py`/`catalog.py`/`client.py`) that rolls `1d100` via
`rules.roll_d100` and returns the natural roll, effect key and description — read-only, no state
write, matching `skill-scale`'s shape rather than `roll`'s (FR-006). Also fix
`tools/check_oracle_prompts.py`'s stale `DOC` path (FR-007).

## Technical Context

- **Language**: Python 3.11+, standard library only.
- **Existing modules**: `engine/wyrd/rules.py` (pure lookups: `roll_d100`, `declaration_bonus`),
  `engine/wyrd/verbs.py` (`skill_scale` — a read-only verb with no state write, the shape this
  feature's verb follows), `engine/wyrd/catalog.py` (`TOOLS` dict), `engine/wyrd/client.py`
  (argparse subparser + dispatch per verb).
- **Sibling family**: oracle answers (#20/PR #84) is design-only — no `engine/*.yaml` or engine
  code exists for it either, so there is no existing oracle code to reuse or stay consistent
  with beyond the design documents' own shared conventions (both `1d100`, no modifier).
- **Testing**: `tests/` mirrors existing verb/rules test conventions (e.g. a
  `test_rules.py`/`test_verbs.py` pattern, or the nearest equivalent already in the tree).

## Design decisions

- **Tables live in `rules.py`, not a new module.** `rules.py` is already this engine's home for
  pure, stateless table-style logic (`declaration_bonus`'s closed-category lookup). A dedicated
  `oracle.py` would be the only single-purpose module in `engine/wyrd/` holding nothing but four
  small tables — not worth a new module for ~50 lines of data plus one function.
- **One lookup function, `oracle_prompt(family: str, roll: int) -> tuple[str, str]`,** returning
  `(effect, description)`. Family validation raises `ValueError` naming the four valid keys
  (FR-003), matching `resolution.py`'s `_critical_band` convention ("an unrecognized damage type
  is a load error, not a table quietly skipped") even though this lookup lives in `rules.py`
  rather than `resolution.py` — same failure posture, different module because this mechanic has
  no state to mutate.
- **Table data as a `dict[str, list[tuple[range, str, str]]]`**, one entry per family key, ten
  `(range(low, high+1), effect, description)` rows each — mirrors `resolution.py`'s existing
  `CRITICAL_SLASHING_TABLE`-style shape (`list[tuple[int, int, str, dict | None]]`) closely enough
  to stay recognizable, adapted for `range` object and a two-value payload since these rows carry
  no mechanical delta (docs/design/15-oracle-prompts.md: "not an immediate mechanical delta").
- **The verb (`oracle_prompt` in `verbs.py`) rolls internally** via `rules.roll_d100(seed=seed)`,
  then calls `rules.oracle_prompt(family, roll)`, returning
  `{"verb": "oracle-prompt", "family": ..., "roll": ..., "effect": ..., "description": ...}`.
  No `state_written` field and no call into `state.py` — this verb is read-only end to end
  (FR-006), the same shape `skill_scale()` already uses (no state parameter at all).
- **`ValueError` from an unrecognized family or an out-of-range roll propagates unchanged**,
  exactly as `roll_d100` already does for a bad `sides` value — `client.py`'s existing
  `try/except` boundary (seen wrapping `roll` at `client.py:240`) turns it into the structured
  `{"error": ...}` shape; this feature adds no new error-handling convention.
- **`tools/check_oracle_prompts.py`'s `DOC` constant** changes from
  `"13-oracle-prompts.md"` to `"15-oracle-prompts.md"` — a one-line fix, verified by actually
  running the script (CLAUDE.md: bulk find-and-replace and unverified fixes both explicitly
  called out as past failure modes in this repo).

## Project Structure

```
engine/wyrd/rules.py     # ORACLE_PROMPT_TABLES data, oracle_prompt() lookup
engine/wyrd/verbs.py     # oracle_prompt() verb wrapper (rolls + looks up, no state write)
engine/wyrd/catalog.py   # "oracle-prompt" TOOLS entry
engine/wyrd/client.py    # subparser + dispatch for "oracle-prompt"
tests/                   # table-coverage tests + verb tests
tools/check_oracle_prompts.py  # DOC path fix only
```

## Constitution Check

No `.specify/memory/constitution.md` exists in this repo — governance here is CLAUDE.md and the
design documents' own ADRs, both already followed above (deterministic-over-inference: dice via
`rules.roll_d100`, never `random` directly; no setting vocabulary in engine code; table data
matches the shipped design document, verified by the existing check script rather than
eyeballed).
