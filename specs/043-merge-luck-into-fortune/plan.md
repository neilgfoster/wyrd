# Implementation Plan: Merge Luck into Fortune

**Branch**: `043-merge-luck-into-fortune` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Remove Luck as a mechanic distinct from Fortune across seven `docs/design/` documents, fold its
two use cases (dodge a misfortune, break a tie) into Fortune's existing spend list, resolve the
Fate-rename-table naming collision, and supersede ADR 0039 with a new ADR (0041) following ADR
0012's consolidation rule (move to `docs/adr/superseded/`, status-only edit, both indexes
updated, live sequence left with a gap rather than renumbered).

## Technical Context

**Language/Version**: N/A — Markdown design documents and ADRs only

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 tools/check_probability_coverage.py`, `python3 tools/check_no_setting_vocabulary.py`,
`python3 -m pytest -q`.

**Constraints**: No accepted ADR (0014, 0039, 0040) is edited beyond 0039's status line, per ADR
0012's consolidation rule and CLAUDE.md's "accepted ADRs are never edited." No renumbering of the
live ADR sequence, per ADR 0012's own scoping (authorised only during Stage 13, now closed).
`specs/008-character-creation/check_creation.py` is left untouched (historical record).

**Scale/Scope**: One new ADR (~90 lines), one ADR moved+status-edited, two ADR indexes updated,
seven `docs/design/` documents edited, one document's numbered steps fully renumbered.

## Constitution Check

- **Nothing unpublishable** — pure design-document editing. PASS.
- **No setting or system names** — none introduced. PASS.
- **Decisions are recorded** — a real alternative (sharpen the split) is rejected, and the choice
  is one someone could plausibly re-propose; ADR 0041 records it. PASS.
- **Design documents rewritten in place** — every `docs/design/` edit removes Luck's content
  directly rather than appending a changelog note. PASS.
- **Accepted ADRs never edited** — 0014, 0040 untouched; 0039's only change is its `Status:`
  line, per ADR 0012's explicit exception for exactly this case. PASS.
- **Deterministic over inference** — every check script above is run, not assumed. PASS.

No violations. No Complexity Tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/043-merge-luck-into-fortune/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/adr/0041-luck-merges-into-fortune.md                              # new
docs/adr/superseded/0039-luck-resets-at-the-top-level-arc-boundary.md  # moved, status-edited
docs/adr/superseded/README.md                                          # index entry added
docs/README.md                                                         # 0039 removed, 0041 added
docs/design/03-rules.md            # Luck subsection removed, Fortune spend list extended,
                                    # Fate rename table fixed
docs/design/10-the-character.md    # Fate+Luck row -> Fate+Fortune
docs/design/11-character-creation.md  # Luck step/value removed, full renumbering
docs/design/12-the-adversary.md    # Luck -> Fortune in the character-carries list
docs/design/13-diegesis.md         # Luck removed from the Countable class
docs/design/19-campaign.md         # Luck removed from the not-inherited list
docs/design/30-playtest-transcript.md  # Luck step/field removed, renumbered
```

## Complexity Tracking

*(empty — no constitution violations)*
