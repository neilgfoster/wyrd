# Implementation Plan: Full design consistency check

**Branch**: `040-design-consistency-check` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Close #92 (Stage 13's last open item) by: (1) a manual cross-reading pass over the document pairs
most likely to carry the "two coherent descriptions" fault, recorded in `research.md`; (2) a new
`tools/check_probability_coverage.py` that re-runs every existing backing script for a derived
probability claim in `docs/design/` and fails if any regresses; (3) a new
`tools/check_no_setting_vocabulary.py` that greps `docs/design/*.md` and `README.md` against
`settings.yaml`'s live catalogue. One real drift was found and fixed by (3) during development: a
worked example in `docs/design/26-corpus-index.md` named the "Maelstrom" setting.

## Technical Context

**Language/Version**: Python 3.11+, standard library only

**Primary Dependencies**: none (both new scripts reuse the repo's existing no-third-party-YAML
convention)

**Storage**: N/A

**Testing**: the two new scripts are themselves the tests; `python3 tools/check_docs.py` and
`python3 tools/backlog.py check` re-run to confirm no regression.

**Target Platform**: local git working tree / CI-equivalent on-demand run

**Constraints**: no new mechanism, no ADR (per spec.md's Assumptions — this feature verifies, it
does not decide); `check_no_setting_vocabulary.py`'s denylist is derived from `settings.yaml`, not
hand-duplicated, so it can't drift from the actual catalogue the way a hardcoded list would.

**Scale/Scope**: two new ~100-line scripts under `tools/`; one one-line prose fix; a cross-reading
finding log in `research.md`.

## Constitution Check

- **Nothing unpublishable** — pure verification tooling plus a prose fix. PASS.
- **No setting or system names in `docs/design/`/`README.md`** — this feature is precisely what
  enforces that rule going forward; its own diff introduces none (the fix removes one). PASS.
- **Deterministic over inference** — both new scripts are exactly this principle applied to Stage
  13's last two scoped items. PASS.
- **A real rejected alternative earns an ADR; description alone does not** — no alternative is
  being rejected here (verification tooling, not a decision), so no ADR. PASS (per spec.md
  Assumptions).
- **Documents describe the present** — the corpus-index fix replaces a specific example with a
  generic one in place, no changelog note. PASS.

No violations. No Complexity Tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/040-design-consistency-check/
├── plan.md, spec.md, tasks.md, research.md
└── checklists/requirements.md
```

### Repository changes

```text
tools/check_probability_coverage.py     # new: re-runs 15 existing backing scripts
tools/check_no_setting_vocabulary.py    # new: greps design/ + README.md against settings.yaml
docs/design/26-corpus-index.md          # fix: "Maelstrom village haunting" -> "folk-horror village haunting"
```

## Cross-reading pass approach

Not every pair of `docs/design/` documents needs a symmetric read — most cross-references are one
document deferring to another's authority (`03-rules.md` deferring critical-table specifics to
`05-criticals.md`), which is the correct shape and not the fault this stage checks for. The fault
is two documents *each independently stating the same fact*, where they could silently disagree.
`research.md` identifies and reads the highest-risk such pairs: `03-rules.md`/`12-the-adversary.md`
on combat mechanics restated on the adversary side (the crowd threshold, the critical formula, the
Aftermath scope), and `07-transformations.md`/ADR 0029 on the threshold spacing. Both pairs were
read line-by-line against each other; no divergence was found in either (recorded in `research.md`
regardless of outcome, per spec.md SC-006 — a clean pass is itself the finding, not evidence the
pass didn't happen).

## Complexity Tracking

*(empty — no constitution violations)*
