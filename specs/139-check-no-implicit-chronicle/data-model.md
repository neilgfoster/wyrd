# Data Model: Check: no implicit current-chronicle global state

## `tools/check_no_implicit_chronicle.py`

- `_is_mutable_empty(node: ast.AST) -> bool`
  `True` for an empty `ast.Dict`/`ast.List`/`ast.Set`, or a no-argument `dict()`/`list()`/
  `set()` call.

- `find_problems(root: pathlib.Path) -> list[str]`
  For every `engine/wyrd/*.py` file: `ast.parse` it, walk `tree.body` (top level only), find
  every `Assign`/`AnnAssign` whose value is `_is_mutable_empty`, and for each `Name` target
  check the contiguous `#`-prefixed comment lines immediately above the assignment for
  `"process-local"` (case-insensitive). Returns one formatted `"<path>:<line>: ..."` string per
  unjustified candidate (FR-003).

- `main(argv) -> int`
  Matches `check_dangling_mechanics.py`'s CLI shape: `--root` (default `.`), prints a one-line
  summary on success (exit `0`) or each problem plus a count (exit `1`) on failure (FR-004).

## Example

```python
# unjustified -- flagged
_cache: dict = {}

# justified -- not flagged (comment contains "process-local")
#: Process-local scratch store, never persisted.
_scratch: dict = {}
```
