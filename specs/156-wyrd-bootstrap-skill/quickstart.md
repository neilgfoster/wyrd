# Quickstart: validating `/wyrd-bootstrap`

Manual walkthrough — `wyrd-chronicle-template` has no automated check substrate (`.kord/`) of its
own, so this is the verification this feature's implementation runs before opening its PR.

## Prerequisites

- A clone of `wyrd-chronicle-template` with the new `.claude/skills/wyrd-bootstrap/SKILL.md`
  in place.
- Access to a real, playable setting repo (e.g. `wyrd-setting-darkfuture`, per issue #403's own
  References).

## Steps

1. `./bootstrap` — answer the setting prompt with the chosen setting, and the intent interview
   questions honestly (give a real `about`, at least one `avoid`, a `lethality`, and an offstage
   answer). Confirm it exits 0 and leaves `chronicle.yaml.json` present, `chronicle.yaml` absent.
2. Invoke `/wyrd-bootstrap` in Claude Code from the chronicle root.
   - Confirm it walks career choice, the 8-advance spend, Loyalty, Drive, Misfortune, and the
     Fault Line sentence, and that the resulting `pc.yaml`'s skill percentages/Fate/Stamina match
     what a direct `create-character` CLI call with the same inputs returns (SC-003).
   - Confirm it presents (or states) an opening situation that reflects the `about` answer and
     does not touch anything the `avoid` answer named.
   - Confirm at least one `overlay/` (or `entities/`) file exists afterward carrying a `threat:`
     block whose `connection` names something concrete tied to the character (typically the
     chosen Misfortune).
   - Confirm `chronicle.yaml` now exists, `chronicle.yaml.json` no longer does, and
     `python3 -m wyrd.client validate` (via the same `WYRD_PKG_DIR` convention) reports `valid:
     true`.
   - Confirm exactly one new git commit was made, covering `pc.yaml`, `chronicle.yaml`, and the
     new overlay/entity file(s).
3. Invoke `/wyrd-bootstrap` again (User Story 2). Confirm it declines and changes nothing —
   `git status --porcelain` reports no changes, no second commit exists.

## Expected outcome

Steps 1–2 produce a complete, playable chronicle in one pass (SC-001); step 3 confirms the
one-time guard (SC-002). This is the same bar issue #403's own DoD names: "running this skill
against a freshly-bootstrapped chronicle (against darkfuture or titan) produces a complete
character, an opening situation, at least one seeded Threat with a personal connection, and a
first commit."
