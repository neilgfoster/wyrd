# Implementation Plan: conversion.yaml schema validator

**Branch**: `317-conversion-yaml-validator` | **Spec**: [spec.md](spec.md) | **Issue**: #317

## Summary

Add `tools/check_conversion.py`, a standalone validator for `setting/conversion.yaml`, mirroring
`tools/check_gear.py`'s shape exactly: import `read_yaml`/`YamlError` from `check_bestiary`, walk
the documented schema field by field, collect every problem rather than stopping at the first, and
expose the same `<path>... [--format text|json]` CLI. Document it in
`docs/design/24-authoring-a-setting.md` next to the `check_bestiary.py`/`check_gear.py` mentions.

## Technical Context

**Language**: Python 3.11, stdlib only (docs/design/27-tooling.md).
**Testing**: `python3 -m pytest -q` — add `tests/test_check_conversion.py` mirroring the existing
`tests/test_check_gear.py` pattern (fixture files under `tests/fixtures/`, or inline YAML strings
written to `tmp_path`).
**Reuse**: `check_bestiary.read_yaml`/`YamlError` (already the shared reader `check_gear.py`
imports); no new parsing code.

## Constitution Check

- Setting-agnostic: PASS — the checker validates structure, not any setting's content; no setting
  or system names appear in the code or docs.
- No unpublishable content: PASS — no source text quoted; the worked example already lives in
  `docs/design/24-authoring-a-setting.md`.
- Deterministic over inference: PASS — this is exactly a check script per `27-tooling.md`.

## Project Structure

```
tools/check_conversion.py          # new
tests/test_check_conversion.py     # new
docs/design/24-authoring-a-setting.md  # amended: reference the new script
```

No `engine/` changes — this is a standalone tools/ script, same as `check_bestiary.py`/
`check_gear.py`, not engine runtime code.

## Complexity Tracking

None — this follows an established pattern with no new dependencies or architecture.
