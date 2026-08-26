# CLI contract: `tools/check_dangling_mechanics.py`

Matches `tools/check_docs.py`'s existing CLI contract exactly, so both checks compose the
same way in a shell pipeline or in CI later.

## Invocation

```text
python3 tools/check_dangling_mechanics.py [--format {text,json}]
```

- No positional arguments. The scan root is always the repository's `design/` directory,
  resolved relative to the script's own location (matching `check_docs.py`'s `REPO =
  pathlib.Path(__file__).resolve().parent.parent` convention).
- `--format text` (default): human-readable summary.
- `--format json`: machine-readable payload for composition into other tooling later
  (FR-009).

## Exit codes

| Code | Meaning |
|---|---|
| `0` | No dangling references found. |
| `1` | One or more dangling references found. |

## `--format text` output

On success:

```text
tools/check_dangling_mechanics.py: N mechanic definitions, M references, 0 dangling
```

On failure, one line per problem, then a summary line, e.g.:

```text
design/05-adversaries.md:42: 'party_effective' is referenced but not defined anywhere in design/
design/10-danger.md:7: 'party_effective' is referenced but not defined anywhere in design/
tools/check_dangling_mechanics.py: 2 dangling references found
```

## `--format json` output

```json
{
  "definitions": 41,
  "references": 118,
  "problems": [
    "design/05-adversaries.md:42: 'party_effective' is referenced but not defined anywhere in design/"
  ]
}
```

`problems` is empty on success; the process still exits `0`/`1` per the table above
regardless of `--format`, matching `check_docs.py`'s existing convention (script exit code is
the actionable signal for CI/scripting; `--format json` is for a human or tool consuming the
detail).

## Contract source

This mirrors `check_docs.py`'s existing `--format json` support and its exit-code convention
(`0` on a clean tree, non-zero on any problem) — see `tools/check_docs.py`'s `argparse` setup
and its own module docstring ("Usage: python3 tools/check_docs.py [--format json]").
