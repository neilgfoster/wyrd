# Implementation Plan: Loyalty and party eligibility

**Branch**: `009-loyalty-and-party-eligibility` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Add `Loyalty` to the character, define the three-relation rule beside the party it governs, and
record the decision. **No new document and no new track** — the mechanism is small and belongs next
to what it constrains.

## Placement

| Change | Where | Why there |
|---|---|---|
| the character carries a Loyalty | `03b-the-character.md` | it is a thing a character has |
| the relations, and enforcement | `04-session.md` | it governs the party, which that document owns |
| choosing one | `03c-character-creation.md` | a creation step |
| the field | `06-state.md` | the record |
| what a setting declares | `13-authoring-a-setting.md` | the engine/setting contract |

Resisting a new `03e-loyalty.md` is deliberate. The mechanism is one table and three paragraphs;
giving it a document of its own would separate it from Party Tension, which is the machinery it
depends on entirely.

## The reuse that makes this cheap

`strained` doubles the rate of a track that already exists, and `irreconcilable` mid-chronicle
triggers a break that is already defined. Neither needs new state beyond one field per character.
The alternative — a Loyalty-friction track of its own — would be a second thing measuring what Party
Tension measures, which is the drift class this repo is corrected for most often.

## Constitution check

| Gate | How |
|---|---|
| A setting may not add a mechanism | this is engine-side; settings supply values only |
| Tone belongs to the setting (ADR 0004) | the engine never says which Loyalty is preferable |
| No setting vocabulary in `design/` | no Loyalty is named; the engine has no vocabulary for them |
| One statement of one fact | Tension is not restated, only referenced and modified |

## Steps

1. `research.md` — the vocabulary collision, and why three relations.
2. `03b`, `04-session`, `03c`, `06-state`, `13-authoring`.
3. ADR 0015.
4. Verify: no Loyalty named anywhere; checks green.

## Risks

**Doubling Tension is a guess.** The rate has never been played, and neither has Tension itself. It
is the simplest expression of "a shorter fuse" and a setting can retune it. Worth revisiting once
Stage 11 has looked at the party properly, and flagged there rather than pretended to be certain.
