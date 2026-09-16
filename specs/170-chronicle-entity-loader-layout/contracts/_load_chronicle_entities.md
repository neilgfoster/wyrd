# Contract: `resolution._load_chronicle_entities`

This feature adds no new public function and no new CLI verb — it changes the observable
contract of one existing internal function that `commit`'s passive validation and
`verbs.load_effective_entities` (and therefore `session-context`/`get`/`find`/`party`) already
depend on transitively.

## Before

```python
def _load_chronicle_entities(any_touched_path: pathlib.Path) -> dict[str, dict]:
    """... setting_paths = sorted((root / "setting").glob("*.md")) ..."""
```

Globs `setting/*.md`, `overlay/*.md`, `entities/*.md` — flat, top-level, Markdown-suffixed only.
On any chronicle laid out with per-type subdirectories and `.yaml` files, matches nothing:
returns `{}` regardless of how many real entities exist. If a non-entity file (e.g.
`setting/README.md`) happens to sit at the flat top level, `entity.load()` raises
`state.StateError` on it (no frontmatter delimiter) instead of the glob simply not finding it.

## After

```python
def _load_chronicle_entities(any_touched_path: pathlib.Path) -> dict[str, dict]:
    """... every entity nested one level under a per-type subdirectory
    (setting/entities/<type>/*.yaml, overlay/<type>/*.yaml, entities/<type>/*.yaml),
    plus the previously-supported flat setting/*.md, overlay/*.md, entities/*.md, for
    chronicles still in that layout. ..."""
```

Same signature, same return shape (`dict[str, dict]`, keyed by entity id, same resolution rules
applied to whichever files are found). The only observable change: a chronicle laid out with
per-type `.yaml` subdirectories now contributes its real entities to the result, instead of
contributing none.

## Callers affected (none change their own signature)

| Caller | Effect of this change |
|---|---|
| `commit`'s passive validation (`_validate_proposal`, resolution.py) | Now checks a proposed mutation against the chronicle's actual entity set, instead of an empty one — duplicate-id and reference checks become meaningful. |
| `verbs.load_effective_entities` | Returns the chronicle's real entities, so every verb built on it (`session_context`, `get`, `find`, `party`, `threads`, `threats`) sees them. |

## Failure modes

| Condition | Behavior |
|---|---|
| Chronicle root has type subdirectories with real `.yaml` entity files | All are loaded and included in the result (this feature's fix). |
| Chronicle root still has only the flat `*.md` layout | Loaded exactly as before (FR-004, unchanged). |
| A type subdirectory contains only a `.gitkeep` placeholder | Contributes no entity; no error (doesn't match the `*.yaml` glob). |
| `setting/README.md` (or similar) sits at a directory's top level | Still matches the flat back-compat glob, but is filtered out by `_looks_like_entity_file` (no `---` frontmatter delimiter on its first line) before `entity.load` sees it — no error, correctly excluded. |
| A file that *does* match `*.yaml` inside a type subdirectory but is not a valid entity (malformed frontmatter, wrong schema) | Unchanged existing behavior: `entity.load()` raises `state.StateError` naming the file — a real authoring error, not suppressed by this feature. |
