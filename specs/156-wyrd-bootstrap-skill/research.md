# Phase 0 research: Wyrd bootstrap skill

No NEEDS CLARIFICATION markers remained in Technical Context, so this phase records the decisions
actually made while reading the existing code and design docs, rather than resolving open
unknowns.

## Decision: where the skill file lives

**Decision**: `wyrd-chronicle-template/.claude/skills/wyrd-bootstrap/SKILL.md`.

**Rationale**: the three precedent skills this feature must follow the conventions of
(`/wyrd-character`, `/wyrd-downtime`, `/wyrd-end-session`, all from issue #404/PR #1) already live
at exactly this path shape in that repository, and the chronicle repo — not the engine repo — is
what needs to invoke the skill, since it is self-contained after bootstrap (per that repo's own
README).

**Alternatives considered**: copying the skill into the chronicle at bootstrap time from a
central source, so updates to the skill logic could reach existing chronicles. Rejected: nothing
else in this family of skills does this, `./bootstrap` does not template `.claude/` at all today,
and it would introduce a versioning/update question (which version of the skill logic a given
chronicle carries) that the three precedent skills sidestep entirely by living directly in the
template repo. Out of scope for this feature; noted as a possible future retune of `./bootstrap`
if the setting/engine update mechanism (docs/design/23-chronicle-bootstrap.md's "Updating"
section) is ever extended to cover skill files too.

## Decision: how the skill consumes `chronicle.yaml.json`

**Decision**: the skill reads `chronicle.yaml.json` (the deterministic script's intermediate
record — `name`, `engine`, `setting`, `intent`, `pending_seed: true`) as its own input, builds the
full chronicle state via the engine's `default_chronicle_state()` shape merged with that recorded
`intent`, seeds the calendar/era/threat presence, writes it through the `save` CLI verb, and then
deletes `chronicle.yaml.json` once `save` succeeds (folding its content into the real
`chronicle.yaml`).

**Rationale**: `bootstrap`'s own docstring is explicit that "the *interpretation* of the answers
... is done by Claude" — this skill is that interpretation step. `chronicle.yaml.json` carries a
`pending_seed: true` marker for exactly this reason: it is a signal, not a permanent file. FR-002
uses the presence/absence of `chronicle.yaml` vs. `chronicle.yaml.json` as the completed/not-yet-
completed test, giving the skill a cheap, deterministic re-run guard (User Story 2) without
needing any new marker field.

**Alternatives considered**: leaving `chronicle.yaml.json` in place permanently as a record of the
raw interview answers. Rejected: `chronicle.yaml`'s own `intent:` field already carries those
answers (docs/design/23-chronicle-bootstrap.md: "Answers are written to `chronicle.yaml` as
`intent:`"), so keeping both would be two copies of the same data, exactly the drift class
CLAUDE.md's fault list calls out.

## Decision: `bootstrap`'s stale "run /wyrd-play next" message

**Decision**: this feature's `wyrd-chronicle-template` PR also corrects `bootstrap`'s own final
printed message (and its docstring's parenthetical) from "run `/wyrd-play`" to "run
`/wyrd-bootstrap`", since issue #403 and docs/design/23-chronicle-bootstrap.md are explicit that
the interpretation half is a distinct, prior step to `/wyrd-play`, and the current text would
actively mislead a player following it literally.

**Rationale**: docs/design/23-chronicle-bootstrap.md's own layout table lists bootstrap producing
`chronicle.yaml`, the player character, and the first commit *before* mentioning `/wyrd-play`
("After bootstrap the repo is self-sufficient. `/wyrd-play` needs nothing else.") — so the
existing prompt is a stale artefact from before this skill existed, not a deliberate design
choice this feature would be overriding.

**Alternatives considered**: leaving the message as-is, treating it as out of scope. Rejected: a
one-line textual correction to the very script this feature completes the other half of is well
within the feature's stated scope ("wyrd-chronicle-template/bootstrap and its README" is listed
among the issue's own References), and shipping the new skill while leaving its own entry point's
signpost wrong would be an obvious, easily-avoided rough edge for the first real playtest.

## Decision: how the seeded Threat and opening situation are authored

**Decision**: written directly as entity/overlay markdown files (frontmatter + prose), per
docs/design/25-entities.md's plain schema — there is no CLI verb for "create an entity" (`grep`
across `engine/wyrd/client.py`'s verb list confirms none exists), so this is authored the same way
a human setting author would write one, not a mechanic requiring a verb.

**Rationale**: docs/design/02-architecture.md's code/prose split assigns arithmetic and refusal
logic to code, and judgment — what a scene is about, which existing entity a Threat overlay
promotes — to the GM/skill. Selecting an opening situation and picking a Threat's personal
connection are exactly that kind of judgment call, with no "correct answer" a script could check
(unlike a skill percentage or Fate value), so ADR 0005 (deterministic over inference) does not
apply to them.

**Alternatives considered**: adding a new CLI verb (e.g. `seed-threat`) to formalize this.
Rejected as out of scope for this feature — issue #403's Scope/steps section names only
`create-character` and the #402 chronicle-level verbs as what this skill calls; inventing a new
engine verb here would be new engine capability the issue never asked for, and speculative before
a second real chronicle bootstrap shows whether the write pattern needs to be shared.
