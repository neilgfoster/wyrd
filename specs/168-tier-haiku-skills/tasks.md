# Tasks: Tier the mechanical chronicle skills at Haiku

**Input**: Design documents from `/specs/168-tier-haiku-skills/`

## Phase 1: Implementation (all in wyrd-chronicle-template)

- [X] T001 Add `model: haiku` frontmatter and a one-line justification to
      `wyrd-chronicle-template/.claude/skills/wyrd-character/SKILL.md` (FR-001, FR-004).
- [X] T002 **Deviation from FR-002, reasoned and documented**: `wyrd-downtime`'s own text states
      its five uncoded Undertakings are played "exactly as any other GM judgment call" -- real
      judgment, not mechanical language work with a right answer. Per the issue's own escape
      hatch ("exclude that skill from this feature rather than forcing an ill-fitting tier"),
      `wyrd-downtime` is excluded from Haiku tier; a note was added to its `SKILL.md` explaining
      why, and stating it stays on the invoking session's model (capped at the Sonnet ceiling
      #429/#430 set for `/wyrd-play`/`/wyrd-bootstrap`) instead.
- [X] T003 Add `model: haiku` frontmatter and a one-line justification to
      `wyrd-chronicle-template/.claude/skills/wyrd-end-session/SKILL.md` (FR-003, FR-004).

## Phase 2: Verification

- [X] T004 Diff each of the three files against its pre-change version and confirm zero
      non-frontmatter/non-justification lines changed (FR-007, SC-003).
- [X] T005 Re-read all three files' frontmatter and confirm `model: haiku` is present in each,
      with no model above Sonnet declared anywhere (FR-006, SC-001).
