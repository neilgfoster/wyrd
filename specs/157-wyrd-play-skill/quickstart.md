# Quickstart: verifying `/wyrd-play`

This is a validation guide, not implementation code -- it proves the feature works end-to-end
against a real bootstrapped chronicle. Run this manually (there is no automated harness for a
Claude Code skill's own prose instructions; see `research.md`).

## Prerequisites

- A `wyrd-chronicle-*` repository that has already run `./bootstrap` and completed
  `/wyrd-bootstrap` at least once (so `chronicle.yaml` and `pc.yaml` both exist), ideally against
  a real setting (`wyrd-setting-darkfuture` or `wyrd-setting-titan`) rather than only a
  synthetic fixture, per the issue's own guidance that a synthetic fixture would miss what a
  real setting's data exposes.
- `wyrd-play/SKILL.md` present under that chronicle's `.claude/skills/`.
- The engine vendored under that chronicle's `engine/` (as bootstrap already leaves it).

## Steps

1. **Cold-start check (no chronicle yet)**: in a freshly-cloned, not-yet-bootstrapped chronicle
   directory, invoke `/wyrd-play`. Expect: a plain statement that no chronicle exists yet, and
   no `session-context` (or any other) engine call attempted (FR-002).

2. **Orientation**: in the bootstrapped chronicle, invoke `/wyrd-play`. Expect:
   - `session-context` is called exactly once, and its returned `player_character`,
     `companions`, `threads`, `recap`, and `contract` are the only source of what's narrated.
   - Prose orientation names where the character is and what changed, without a thread id, a
     beat id, a difficulty number, or a Tension/Bond value ever appearing in the narration text.
   - No option menu is presented.

3. **Resuming a `pending` marker**: manually set `chronicle.yaml`'s `pending` field to a
   plausible `{beat, awaiting, rolled: null}` value, then invoke `/wyrd-play`. Expect: the skill
   resumes exactly the named `awaiting` action rather than starting a new beat.

4. **A beat with a skill test**: from a clean orientation, declare an in-character action that
   plausibly calls for a roll (with real uncertainty). Expect:
   - `propose` (or `opposed-test`, if a companion is opposed by an NPC) is called with a skill
     and difficulty grounded in the fiction and the character's own sheet.
   - The narrated outcome (success/failure, degree, any staged mutation) matches the verb's
     own returned result exactly -- verify by comparing the CLI's raw JSON output to what was
     narrated.
   - `commit` is called only after the outcome is known and accepted into the fiction;
     `discard` is used instead if the declared action is retracted before commit.

5. **A beat with no mechanical uncertainty**: declare an in-character action with no real
   chance of failure and no opposition. Expect: the outcome is narrated in prose with no
   `propose`/`opposed-test` call invented for it.

6. **Closing the beat cleanly**: bring the beat to a natural stopping point. Expect:
   - `rally` is called (Strain +1, Stamina +1, any advance award reported verbatim).
   - `save` is called, and succeeds, **before** the closing narration is shown.
   - `chronicle.yaml`'s `pending` is `null` afterward.
   - `validate --chronicle-dir .` reports no errors.

7. **Stopping mid-beat**: start a second beat and simulate needing to stop before its action
   resolves. Expect:
   - A `pending` marker is written naming the current beat and the specific unresolved action.
   - `save` succeeds before any closing narration.
   - `validate --chronicle-dir .` still reports no errors.
   - No outcome is fabricated to force a clean stopping point instead.

8. **Setting-agnostic prose check**: read back everything `/wyrd-play` narrated across steps
   2-7 and confirm no setting- or system-specific name was baked into the skill's own prose
   (as opposed to names the setting's own data legitimately supplied, e.g. an NPC's name from
   `session-context`'s returned entities).

## Expected outcome

All eight steps behave as described, against a real bootstrapped chronicle, with every
mechanical number traced back to the exact CLI call that produced it. This satisfies SC-001
through SC-005 and the issue's own acceptance criteria.
