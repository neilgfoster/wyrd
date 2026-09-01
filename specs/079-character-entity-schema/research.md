# Phase 0 research: Character entity schema and validator

No `[NEEDS CLARIFICATION]` markers remained.

## Entity file format: frontmatter + body

- **Decision**: `parse_entity(text) -> tuple[dict, str]` splits on the first two `---` lines
  (opening and closing the frontmatter block); everything after the second `---` is the body,
  returned as raw text. `dump_entity(frontmatter, body) -> str` writes it back in the same shape.
- **Rationale**: `docs/design/25-entities.md`: "Every fact Wyrd knows about a world is an
  entity: a markdown file with YAML frontmatter. The frontmatter is the schema, the body is the
  prose." A character is an entity like any other; #221's bare-YAML `chronicle_state.yaml` was a
  placeholder shape for that feature's own minimal needs, not a precedent this feature should
  extend past its actual scope.
- **Alternatives considered**: Treating the character file as pure YAML with no body was
  rejected — it would silently diverge from every other entity type's file format the moment a
  chronicle actually writes prose about a character (a description, session notes), which
  `docs/design/25-entities.md` treats as normal.

## List-of-mapping support in the reader/writer

- **Decision**: Extend `state.py`'s `_parse_block`/`_dump_block` to handle a list item that is a
  mapping (first key inline after the dash, remaining keys indented two further) — porting the
  pattern already proven in `tools/check_bestiary.py`'s reader, adapted with a matching writer.
- **Rationale**: `wounds`, `career_history`, `transformations`, `afflictions`, `holdings`,
  `allegiances`, `marks`, and `drives` are all lists, and at least `wounds` is a list of
  mappings (`docs/design/22-state.md`'s own worked example). #221's reader/writer only ever
  needed to round-trip a list of scalars or absent lists, so this genuinely wasn't built yet —
  discovered by attempting the round trip during this feature's own implementation, not
  predicted in the spec.
- **Alternatives considered**: A third-party YAML library was rejected — ruled out by
  `docs/design/27-tooling.md` section 2, unchanged since #221. Reinventing the parsing from
  scratch (rather than porting `check_bestiary.py`'s already-correct approach) was rejected as
  needless re-derivation of a shape that repo already has a working, tested reader for.

## Wound validation as a dedicated function, not inline in load

- **Decision**: `validate_character(data: dict) -> None` (raising `StateError` on any
  violation) is a separate, directly-testable function, called by `character.load` after
  `state.load` parses the frontmatter — not validation logic folded into `state.py`'s generic
  loader.
- **Rationale**: `state.py`'s load/save is entity-agnostic (any mapping); wound rules are
  specific to the character shape. Keeping validation in `character.py` means `state.py` stays a
  generic primitive other future entity types (companions, threats) can reuse without inheriting
  character-specific rules that don't apply to them.
- **Alternatives considered**: Validating inline wherever a wound is read was rejected — it
  would scatter the same five rules across every call site instead of one checkable function.

## Active wound effects as a pure function over already-loaded data

- **Decision**: `active_wound_effects(wounds: list[dict]) -> list[dict]` filters to wounds where
  `closed` is `None`, returning their `effect` dicts (with the owning wound's `id` and
  `bears_on` attached for a caller to act on).
- **Rationale**: `docs/design/22-state.md`: "A closed wound's effect applies to nothing; readers
  skip it." This is a pure filter over data already in memory — no new state, no new roll.
- **Alternatives considered**: Mutating a loaded wound's `effect` to `None` when closed (rather
  than filtering at read time) was rejected — it would destroy the documented distinction
  between "a wound whose effect is presently inactive because it's closed" and "a wound that
  never had an effect," and would make FR-007 (a closed wound stays present with its original
  effect recorded) impossible to satisfy.

## Skill-scale constants

- **Decision**: `SKILL_OPEN_VALUE = 25`, `SKILL_ADVANCE_STEP = 5` as module-level constants in
  `rules.py`, alongside the existing `UNTRAINED_SKILL = 10` from #221.
- **Rationale**: `docs/design/10-the-character.md` section 2's table states these two numbers
  directly ("Opens at: 25%", "Rises by: +5% per advance"); no computation is involved, so a
  constant is the whole implementation — no function is needed beyond exposing the values.
- **Alternatives considered**: An `advance_skill(current, cap=None)` function was considered,
  but rejected for this feature — cap enforcement needs the career graph (#210, not yet built),
  and a capless "advance" function would just be `current + SKILL_ADVANCE_STEP`, which any
  caller can already compute directly from the exposed constant without a wrapper function
  adding anything.
