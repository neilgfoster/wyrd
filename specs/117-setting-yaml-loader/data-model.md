# Phase 1 Data Model: setting.yaml loader and validator

No persistent state is introduced — this feature validates a file that already exists on disk and
returns/reports on it; nothing is written. The "entities" below are the shape `check_setting.py`
parses and validates, matching `docs/design/24-authoring-a-setting.md`'s `setting.yaml` example.

## Setting identity (top level)

| Field | Required | Type | Validation |
|---|---|---|---|
| `name` | yes | string | non-empty |
| `title` | yes | string | non-empty |
| `line` | yes | string | non-empty, free text (Research Unknown 3) |
| `requires_engine` | yes | string | matches the closed comparator syntax (Research Unknown 2) |
| `version` | yes | string | `MAJOR.MINOR.PATCH` (matches `docs/design/24-authoring-a-setting.md`'s own `version: 0.3.0` example) |
| `description` | yes | string | non-empty |
| `tone` | yes | mapping | see Tone contract below |

No optional top-level fields are validated by this feature — `overrides:` (if present) is
explicitly ignored (FR-008), consistent with `check_bestiary.py`'s pattern of an `ALL_FIELDS` set,
except here an unrecognised top-level field is *not* rejected the way an unrecognised bestiary
field is, because `overrides:` is a legitimate field this feature deliberately does not validate.
(See Edge case note below.)

**Edge case resolved**: `check_bestiary.py` rejects *any* field outside its `ALL_FIELDS` — but
`setting.yaml` genuinely has a field (`overrides:`) that a sibling feature (#316) owns validating.
This feature's `ALL_FIELDS` therefore includes `overrides` as a recognised-but-unvalidated key
(present or absent, opaque to this validator), so a future setting.yaml using it isn't wrongly
rejected here while #316 is still pending. Any other unrecognised top-level key IS rejected, same
as `check_bestiary.py`.

## Tone contract (`tone:` block)

| Field | Required | Closed vocabulary |
|---|---|---|
| `prophecy` | yes | `forbidden` \| `rare` \| `central` |
| `victory` | yes | `mitigation` \| `mixed` \| `triumph` |
| `power_curve` | yes | `flat` \| `moderate` \| `heroic` |
| `scope` | yes | `personal` \| `regional` \| `world` |
| `scale_drift` | yes | `suppressed` \| `allowed` |
| `mortality` | yes | `low` \| `standard` \| `high` |
| `register` | yes | free text, non-empty |

Source: `docs/design/24-authoring-a-setting.md`'s `setting.yaml` example, cross-checked against
`docs/design/01-principles.md`'s tone contract section (Research phase found no discrepancy
between the two — both already agree, so no "two documents describing one thing differently"
fault applies here).

## Validation result

A single `ValidationResult`-shaped object (matching `check_bestiary.py`'s pattern): a list of
problem strings, each naming the offending field and, for a closed-vocabulary violation, the
allowed values. Empty list = valid. This is not a persisted entity — it exists only for the
duration of one CLI invocation.
