# Phase 0 Research: effort-level decision for /wyrd-play and /wyrd-bootstrap

This feature has no technology unknowns (it edits YAML frontmatter and prose in two existing
files) -- the one substantive open question Technical Context left for this phase is **which
`effort:` value each skill should declare**, decided against `docs/design/27-tooling.md` section
5 and each skill's own full text (both already read in full for this feature; see spec.md's
Assumptions and wyrd#430's own body).

Confirmed vocabulary: this codebase's own precedent (`kord`'s `plugin/skills/*/SKILL.md`, the
only prior art for this frontmatter field visible from this repo) uses exactly three `effort:`
values -- `low`, `medium`, `high` -- alongside `model:`. No other values are in use anywhere
searched.

## Decision: /wyrd-play declares `effort: high`

**Rationale**: Read in full, `/wyrd-play`'s ten steps split as:

- **Mechanical** (Step 0 guard, Step 1 `session-context` load, Step 6's verbatim reporting of a
  `track`/`advance-time`/`threat-check` return value, Step 10 `validate` call): a computable right
  answer, already delegated to an engine CLI verb per `docs/design/02-architecture.md`'s
  code/prose split. These steps cost nothing to run at a higher effort tier -- relaying a CLI
  call's JSON verbatim is cheap regardless of reasoning depth.
- **Judgement-requiring** (Step 3 orienting the player in prose from `recap`/`threads`/
  `companions`; Step 4's interpretation of what a `propose` result *means* in the fiction and
  whether to `commit` or `discard`; Step 5's declaration-bonus *category* judgement; Step 7's call
  on whether a roll is warranted at all; Step 8's beat-closing narration; Step 9's honest
  `pending` marker when a beat must stop mid-action): narration, character voice, and judgement
  about what a result means -- exactly the class `docs/design/27-tooling.md` section 5 names as
  "the GM itself" and states plainly "is the one place not to economise."

By step count and by the skill's own self-description ("This is the central, repeatedly-invoked
skill of actual play... narration plus whatever code-backed resolution the beat calls for"), the
judgement-requiring steps are the skill's actual job; the mechanical steps exist only to feed them
verified numbers. Because a single `effort:` setting must cover the whole skill, and setting it
high carries no cost against the mechanical steps (they have a fixed right answer regardless of
reasoning depth) while setting it any lower risks under-provisioning the narration and judgement
steps that are the skill's actual point, `high` is the only choice that respects section 5's
stance without gambling quality against a saving that would not materialize.

**Alternatives considered**:
- `effort: low` -- rejected outright. This is exactly the "Haiku-sufficient" framing 27-tooling.md
  section 5 already rejected by name ("Running narration, voice, motive and judgement on Haiku is
  not deferred or aspirational; it is rejected, on the same grounds"); defaulting a
  narration-dominant skill to the cheapest effort tier is the same mistake at the effort axis
  instead of the model axis.
- `effort: medium` -- rejected. A middle tier would be the right call if the skill's steps were
  roughly balanced between mechanical and judgement-heavy, but they are not: the mechanical steps
  are thin wrappers around CLI calls with no judgement content at all, while the judgement steps
  carry the skill's entire value (narration quality, honest pending markers, correct declaration
  categorisation). There is no genuinely balanced middle ground to reach for here.

## Decision: /wyrd-bootstrap declares `effort: high`

**Rationale**: Read in full, `/wyrd-bootstrap`'s six steps split as:

- **Mechanical**: Step 0's guard, most of Step 2 (reading setting tables, calling
  `create-character` and trusting its returned `frontmatter`/`error` verbatim, per this skill's
  own "never computes one itself" framing), Step 5's state assembly and `save` call, Step 6's
  commit.
- **Judgement-requiring**: Step 2's own choice-presentation still requires narrating the setting's
  career/loyalty/drive/misfortune options and helping the player write the Fault Line sentence in
  a way that actually combines their Drive and Misfortune coherently -- not itself a
  computed-answer task. Step 3 is the clearest case: matching a setting's indexed scenario
  candidates (or an `entities/` arc, absent an index) against the player's stated `intent.about`/
  `avoid` is explicitly "the same kind of grounded judgment call Step 3 has always made... now
  applied to a richer pool" (the skill's own words) -- it sets the entire opening situation a
  chronicle plays out from. Step 4's Threat selection requires judging which existing entity is
  "plausibly implicated" by the chosen Misfortune, or authoring a new one's personal connection
  from scratch. Step 6's closing report must trace each fact to the step that produced it, which
  is itself an act of accurate narration, not a template fill.

This mix has a smaller share of pure narration than `/wyrd-play` (this skill runs once per
chronicle, is more procedural overall, and several of its steps really are "walk the player
through a form" work), but the judgement steps it does carry are unusually consequential: Step 3
picks the opening situation the entire chronicle will run from, and Step 4 seeds the one Threat
docs/design/19-campaign.md requires to already have a personal connection. Getting either wrong is
not a cosmetic narration slip -- it is a wrong foundational choice a chronicle then lives with.
The same asymmetry that decided `/wyrd-play` applies again: a high effort setting costs nothing
against this skill's mechanical steps (create-character's arithmetic is the CLI's job regardless),
while a lower setting risks the two decisions in this skill that matter most.

**Alternatives considered**:
- `effort: low` -- rejected for the same reason as `/wyrd-play`: this skill's Step 3 and Step 4
  are genuine grounded judgement calls, not lookups, and section 5's stance applies to them
  exactly as it does to narration proper.
- `effort: medium` -- this was the closer call of the two skills, precisely because
  `/wyrd-bootstrap` genuinely has more mechanical bulk than `/wyrd-play` (character creation's
  procedural walk, file writes, the commit). It was rejected because the *consequence* of Step 3
  and Step 4 going wrong is not proportional to how much of the skill's text they occupy -- a
  wrongly-matched opening scenario or an unconnected Threat is a foundational error the rest of
  the chronicle inherits, which is the same "not the place to economise" stakes 27-tooling.md
  names for narration, even though here it shows up as two judgement-heavy steps inside an
  otherwise procedural skill rather than as the skill's entire job.

## Summary

| Skill | `model:` | `effort:` | Judgement steps that drove the choice |
|---|---|---|---|
| `/wyrd-play` | `sonnet` | `high` | Steps 3, 4 (interpretation), 5 (category), 7, 8, 9 -- narration and judgement are the skill's entire job |
| `/wyrd-bootstrap` | `sonnet` | `high` | Steps 2 (Fault Line), 3 (scenario/arc match), 4 (Threat connection), 6 (traced report) -- fewer in count, but each is foundational to the chronicle that follows |

Both land on the same `effort:` value, but for distinguishable reasons stated in writing per each
skill's own step mix -- not because the two skills were assumed identical, and not defaulted.
