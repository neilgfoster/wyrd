# Data Model: Chronicle friction harvest

No persistent storage — these are the in-memory shapes `tools/harvest_friction.py` passes between
its own functions, for the tests in `tools/test_harvest_friction.py` to construct and assert
against directly.

## `FrictionEntry`

One bullet parsed from a chronicle's `log/friction.md`.

| Field | Type | Notes |
|---|---|---|
| `mechanic` | `str` | Which rule/table/design section was involved. Required. |
| `what_happened` | `str` | The surprising reading, wrong-feeling result, or improvisation gap. Required. |
| `what_gm_did` | `str` | The ruling made in the moment. Required. |
| `source_repo` | `str` | The chronicle repo this entry came from (local path or `owner/repo`), for User Story 2's per-repo attribution. |
| `raw_index` | `int` | Position within its source file, for stable, reproducible ordering and for referencing a malformed entry in the "skipped" report (FR-008). |

An entry missing `mechanic`, `what_happened`, or `what_gm_did` is not constructed as a
`FrictionEntry` — it becomes a `MalformedEntry` instead (below), never a `FrictionEntry` with an
empty field standing in for the gap.

## `MalformedEntry`

| Field | Type | Notes |
|---|---|---|
| `source_repo` | `str` | Same as above. |
| `raw_index` | `int` | Same as above. |
| `missing_fields` | `list[str]` | Which of the three required fields were absent, for the operator-facing report (FR-008). |
| `raw_text` | `str` | The original bullet text, for the operator to fix by hand at the source. |

## `TriageVerdict`

The result of applying `docs/design/16-session.md`'s "What qualifies" rule to one
`FrictionEntry`.

| Field | Type | Notes |
|---|---|---|
| `entry` | `FrictionEntry` | The entry judged. |
| `verdict` | `Literal["qualifies", "does_not_qualify", "needs_review"]` | Per research.md's triage decision — `needs_review` is reported, never silently dropped. |
| `reason` | `str` | A short, checkable statement of which condition matched (or why none did), for the operator-facing report. |

Only `qualifies` verdicts proceed to `HarvestProposal` construction; `does_not_qualify` and
`needs_review` are both reported to the operator (Edge Cases / SC-002), distinguished from each
other so a real gap the predicate was unsure about is never confused with confirmed color.

## `HarvestProposal`

A candidate `wyrd` issue, built only from the mechanical fields of one `FrictionEntry` (FR-005 —
never any other text from the chronicle repo).

| Field | Type | Notes |
|---|---|---|
| `title` | `str` | Built from `mechanic` alone (e.g. `"Friction: <mechanic>"`), never from `what_happened`/`what_gm_did` free text, since a title is the most exposed surface for an accidental narrative leak. |
| `body` | `str` | States `what_happened` and `what_gm_did` verbatim, plus the source entry's `mechanic` and `source_repo` for traceability — nothing else appended. |
| `source_entries` | `list[FrictionEntry]` | More than one when the Edge Cases' "same finding repeated within one log" merge rule applies — one proposal, multiple contributing entries. |
| `dedup_verdict` | `DedupVerdict \| None` | Filled in after the dedup check runs (`None` until then). |

## `DedupVerdict`

The result of running `github-issue-dedup-check` against one `HarvestProposal`.

| Field | Type | Notes |
|---|---|---|
| `matched_issue` | `dict \| None` | The existing issue's `{number, url, title}` if `github-issue-dedup-check` found one, else `None`. |
| `is_new` | `bool` | `True` when `matched_issue` is `None` — this proposal should be shown as a new candidate; `False` means it should be shown as a likely duplicate instead (User Story 3, FR-004). |

## Relationships

```
log/friction.md (one per chronicle repo)
  └─ parsed into: FrictionEntry[] and MalformedEntry[]
       FrictionEntry
         └─ triaged into: TriageVerdict (qualifies / does_not_qualify / needs_review)
              qualifies
                └─ grouped (same-log repeats merged) into: HarvestProposal
                     └─ checked via github-issue-dedup-check into: DedupVerdict
                          is_new=True  → reported as: new proposal
                          is_new=False → reported as: likely duplicate of matched_issue
```
