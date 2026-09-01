# Phase 0 research: Character creation procedure

No `[NEEDS CLARIFICATION]` markers remained.

## Mortality-to-Fate lookup

- **Decision**: `MORTALITY_FATE = {"low": 2, "standard": 3, "high": 4}`, a plain dict in
  `creation.py`.
- **Rationale**: `docs/design/11-character-creation.md` section 2 states the table directly; no
  computation is involved beyond the lookup itself.
- **Alternatives considered**: None — the table is fully specified, not a design choice.

## Validate-then-save ordering, not save-then-validate-and-rollback

- **Decision**: `create_character` calls `career.validate_allocation` first; only on success does
  it build the frontmatter and call `character.save`. A failed validation returns
  `{"valid": False, "error": ...}` and touches no file at all.
- **Rationale**: `docs/design/22-state.md`'s atomic write (`os.replace`) already guarantees no
  *partial* file is ever left, but it says nothing about whether a file gets written *at all* —
  writing an invalid character and then deciding to reject it would still leave a real file on
  disk if the caller didn't also remember to delete it. Validating first means the "no entity
  produced" half of FR-004 holds by construction, not by a caller's follow-up cleanup step.
- **Alternatives considered**: Writing first and returning an error only if the character
  itself later failed #229's own `validate_character` was rejected — #231's allocation rules are
  checked before a character shape exists at all, so there is no reason to defer that check past
  the point where it's cheap and side-effect-free.

## Fixed-value table lives in `creation.py`, not `character.py` or `career.py`

- **Decision**: Stamina 6, the mortality table, and the zeroed-track list are constants/logic in
  the new `creation.py`, not added to `character.py` (which validates a character's *structural*
  rules, e.g. wounds) or `career.py` (which validates an *allocation*, not starting values).
- **Rationale**: Neither existing module has anything to do with "what a brand-new character's
  numbers are" — that's specifically creation's own concern (`docs/design/11-character-
  creation.md` section 2), distinct from both the entity's general shape and the career
  allocation rule.
- **Alternatives considered**: Adding a `default_player_character()` helper to `character.py`
  was considered (it already has one implicitly absent), but rejected — Stamina 6 and the
  mortality table are creation-specific numbers with their own cited rationale
  (`docs/design/11-character-creation.md`'s "Why Stamina is 6"/"Why Fate rises with mortality"),
  not generic defaults `character.py` should own.
