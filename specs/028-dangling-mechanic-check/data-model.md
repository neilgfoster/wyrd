# Phase 1 Data Model: The dangling-mechanic check

This feature has no persistent storage or schema — it is a stateless scan over
`design/**.md` performed fresh on every run. The entities below are the in-memory shapes
the check's logic passes between its scan, match, and report steps.

## MechanicDefinition

Represents one place a mechanic is established as meaning something.

| Field | Type | Notes |
|---|---|---|
| `name` | `str` | The mechanic's canonical name, as it appears at the definition site |
| `source` | `Path` | The `design/**.md` file containing the definition |
| `kind` | `Literal["heading", "table_row", "glossary"]` | Which structural form matched (spec Key Entities: heading, table row, or glossary entry) |
| `line` | `int` | 1-indexed line number, for locating the definition if ever needed |

**Validation rule**: a mechanic may have more than one `MechanicDefinition` (e.g. named in a
heading in one document and restated as a table row in an index) — this is not itself an
error; the check only cares whether *at least one* definition exists for every referenced
name.

## MechanicReference

Represents one place a mechanic's name is used as though the reader already knows what it
means.

| Field | Type | Notes |
|---|---|---|
| `name` | `str` | The mechanic name as referenced |
| `source` | `Path` | The `design/**.md` file containing the reference |
| `line` | `int` | 1-indexed line number |
| `context` | `str` | The surrounding line's text, for the failure report (FR-003) |

**Validation rule**: a reference occurring on the same line/section as its own definition is
not counted as a dangling reference against itself — a heading naming a mechanic is a
definition, not simultaneously a reference to itself.

## Problem (dangling reference)

The check's actual output unit, matching `check_docs.py`'s `Problem(str)` pattern — a
human-readable string subclass so JSON serialization is trivial (`Problem` values are emitted
as plain strings in `--format json`'s problem list).

Constructed from a `MechanicReference` that has no matching `MechanicDefinition.name`
anywhere in the design tree. Message shape: `"<file>:<line>: '<name>' is referenced but not
defined anywhere in design/"`.

## Relationships

```
design/**.md  --scan-->  [MechanicDefinition]  ┐
                                                 ├─>  vocabulary: set[str] (defined names)
design/**.md  --scan-->  [MechanicReference]   ┘

for each MechanicReference where reference.name not in vocabulary:
    yield Problem(...)
```

No entity is written back to disk; the check is read-only over `design/` (spec FR-001/FR-002,
mirroring `check_docs.py`'s "Reads the filesystem, nothing else").
