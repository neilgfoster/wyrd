# Implementation Plan: Reorder the design documents into a logical reading sequence

**Branch**: `039-doc-reading-order` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Renumber all 30 `docs/design/*.md` files per the operator-confirmed mapping (spec.md's
Assumptions table) via `git mv`, using a two-phase move through temporary names to avoid
collisions where old and new numbers overlap. Rewrite every relative link inside the moved tree,
`README.md`'s reading-order table, `docs/design/NN-...` references in `tools/*.py`, path tokens
in `specs/*/*.md` (excluding this feature's own directory), and open GitHub issues citing an
affected path. Verify with `python3 tools/check_docs.py`. ADR numbers are untouched — same policy
as #38 (ADR 0038).

## Technical Context

**Language/Version**: Python 3.11+, standard library only (reuses #38's approach)

**Primary Dependencies**: `gh` CLI, for the open-issue rewrite step

**Storage**: the repository's own files

**Testing**: `python3 tools/check_docs.py` (existing check, no retargeting needed — hub/ADR-index
paths don't move); a grep-based verification pass at the end, not committed as an ongoing test.

**Target Platform**: local git working tree

**Constraints**: no unverified bulk find-and-replace; every rename via `git mv`; `specs/*/*.md`
gets path-token-only repair, prose untouched, this feature's own spec directory excluded; every
open issue citing an affected path updated.

**Scale/Scope**: 30 design documents renamed; cross-links inside them and from `docs/adr/*.md`
rewritten; `README.md`'s reading-order table rebuilt; `tools/*.py` references updated; open-issue
citations updated.

## Constitution Check

- **Nothing unpublishable** — pure reorganization of already-public design prose. PASS.
- **No setting or system names introduced** — renumbering only; no prose content changes beyond
  path tokens. PASS.
- **Deterministic over inference** — the mapping is a fixed table (spec.md Assumptions), rewrites
  are scripted against it and verified by `check_docs.py` + grep, not eyeballed. PASS.
- **Accepted ADRs never edited** — ADR numbers and content are untouched; only design-doc numbers
  move, and any ADR's *outgoing* link to a design doc is a path repair under ADR 0038's existing
  policy, not a reasoning edit. PASS.
- **Git history followable** — `git mv` throughout (FR-008, verified by SC-004). PASS.

No violations. No Complexity Tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/039-doc-reading-order/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/
├── 01-principles.md            # unchanged
├── 02-architecture.md          # unchanged
├── 03-rules.md                 # unchanged
├── 04-tables.md                # was 07-tables.md
├── 05-criticals.md             # was 08-criticals.md
├── 06-aftermath.md             # was 09-aftermath.md
├── 07-transformations.md       # was 10-transformations.md
├── 08-afflictions.md           # was 11-afflictions.md
├── 09-systems-of-power.md      # was 14-systems-of-power.md
├── 10-the-character.md         # was 04-the-character.md
├── 11-character-creation.md    # was 05-character-creation.md
├── 12-the-adversary.md         # was 06-the-adversary.md
├── 13-diegesis.md              # was 23-diegesis.md
├── 14-oracle-answers.md        # was 12-oracle-answers.md
├── 15-oracle-prompts.md        # was 13-oracle-prompts.md
├── 16-session.md               # unchanged
├── 17-out-of-character-mode.md # unchanged
├── 18-arcs-and-beats.md        # was 28-arcs-and-beats.md
├── 19-campaign.md              # was 18-campaign.md
├── 20-journeys.md              # was 30-journeys.md
├── 21-parallel-chronicles.md   # was 25-parallel-chronicles.md
├── 22-state.md                 # was 19-state.md
├── 23-chronicle-bootstrap.md   # was 29-chronicle-bootstrap.md
├── 24-authoring-a-setting.md   # was 26-authoring-a-setting.md
├── 25-entities.md              # was 27-entities.md
├── 26-corpus-index.md          # was 24-corpus-index.md
├── 27-tooling.md               # was 20-tooling.md
├── 28-maintenance.md           # was 21-maintenance.md
├── 29-evolution.md             # was 22-evolution.md
└── 30-playtest-transcript.md   # was 15-playtest-transcript.md

README.md                       # reading-order table rebuilt
tools/*.py                      # docs/design/NN-... references updated
specs/*/*.md                    # path tokens repaired (excluding this feature's own dir)
```

## Migration approach

Because old and new numbers overlap (e.g. old `04` → new `10`, but new `04` is old `07`), a
single-pass `git mv` would clobber files mid-migration. Two phases, both via `git mv`:

1. **Phase A**: `git mv docs/design/NN-name.md docs/design/_tmp_MM-name.md` for every file, where
   `MM` is its final number — moving into a `_tmp_`-prefixed namespace that cannot collide with
   any existing filename.
2. **Phase B**: `git mv docs/design/_tmp_MM-name.md docs/design/MM-name.md` for every file,
   dropping the `_tmp_` prefix — landing each at its final name.

Both phases are `git mv`, so history is preserved through both renames (`git log --follow` walks
right through the intermediate name).

After the move, a link-rewrite pass parses every `.md` file under `docs/` for a relative link or
bare path token matching `docs/design/NN-name.md` against the mapping table and substitutes the
new number — never a blind string find-and-replace across unrelated content.

## Complexity Tracking

*(empty — no constitution violations)*
