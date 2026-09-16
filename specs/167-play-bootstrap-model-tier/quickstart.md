# Quickstart: verifying the /wyrd-play and /wyrd-bootstrap tiering

`wyrd-chronicle-template` has no CI or automated tests (confirmed in wyrd#430's own Definition of
Done), so this feature is verified by manual re-reading, not by a script. This guide is the
checklist to run against the two updated files after implementation, in the
`wyrd-chronicle-template` repository (not this one).

## Prerequisites

- The two files exist and have been edited:
  `wyrd-chronicle-template/.claude/skills/wyrd-play/SKILL.md`
  `wyrd-chronicle-template/.claude/skills/wyrd-bootstrap/SKILL.md`

## Verification steps

1. **Read `wyrd-play/SKILL.md` in full**, frontmatter through the end of its `## Never` section.
   - Confirm the frontmatter block declares `model: sonnet`.
   - Confirm the frontmatter block declares `effort: high` (research.md's decision).
   - Confirm `model:` is never `opus` anywhere in the file.
   - Confirm a justification note (frontmatter comment or immediately-following prose) explains
     the `effort:` choice, naming at least one mechanical step (e.g. Step 1's `session-context`
     load, Step 10's `validate` call) and at least one judgement-requiring step (e.g. Step 3's
     orientation narration, Step 8's beat-closing narration) from the skill's own numbered steps.
   - Confirm the justification references `docs/design/27-tooling.md` section 5's
     narration-stays-capable stance, not just an unexplained value.

2. **Read `wyrd-bootstrap/SKILL.md` in full**, frontmatter through the end of its `## Never`
   section.
   - Confirm the frontmatter block declares `model: sonnet`.
   - Confirm the frontmatter block declares `effort: high` (research.md's decision).
   - Confirm `model:` is never `opus` anywhere in the file.
   - Confirm a justification note names Step 3's opening-scenario/arc selection (and/or Step 4's
     Threat-connection judgement) as the judgement-requiring case, against the skill's more
     mechanical steps (Step 2's `create-character` call, Step 5's `save` call, Step 6's commit).
   - Confirm the justification references `docs/design/27-tooling.md` section 5.

3. **Grep both files for `opus`** -- expect zero matches:

   ```bash
   grep -in opus wyrd-chronicle-template/.claude/skills/wyrd-play/SKILL.md \
                  wyrd-chronicle-template/.claude/skills/wyrd-bootstrap/SKILL.md
   ```

4. **Confirm no operational change**: diff each file against its pre-feature version and confirm
   every change is confined to the frontmatter block plus the added justification note -- no
   numbered step, CLI-verb invocation, or `## Never` entry was altered.

## Expected outcome

Both files declare `model: sonnet` / `effort: high`, each with its own written justification
naming specific mechanical and judgement steps, and neither file's operational content changed.
This satisfies spec.md's FR-001 through FR-008 and SC-001 through SC-004.
