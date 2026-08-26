# Implementation Plan: The character

**Branch**: `006-the-character` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Write `docs/design/04-the-character.md`, record the decision as an ADR, and correct the four places that
contradict it.

The shape of the answer, from [research.md](./research.md): **the engine describes a character
entirely in terms it owns — skills as percentages, Stamina, the tracks, careers, advances — and names
none of them.** A skill is a name the setting supplies and a number the engine understands. That is
the whole model, and it is why no characteristics are needed: there is nothing for them to do.

## The document's placement

`docs/design/04-the-character.md`, and in `README.md`'s reading order it sits **immediately after
`03-rules`**, before the table annexes. The character belongs directly after resolution and before
combat, which is where standard design order puts it and where this design's absence of it caused the
trouble.

The `03b` filename is provisional: #38 owns the numbering convention and will settle whether the
letter suffix survives. Naming it now to sort near the ruleset is the least-wrong option that does
not pre-empt that decision.

## What the document says

1. **A character is a name, a career, a set of skills, Stamina, the tracks, and a history.** Nothing
   else is numeric.
2. **Skills.** A percentage the engine understands under a name the setting owns. Opens at 25%, rises
   +5% per advance, bounded by the career cap (`03-rules.md` §6). What each band *means* is already
   tabulated in `10-diegesis.md` and is cited rather than restated — one statement of one fact.
3. **No characteristics.** Stated, with the reasoning pointed at the ADR.
4. **The skill declaration contract.** What a setting must provide, and what the engine assumes.
5. **How engine rules refer to a skill** — by relationship, never by name.

## The corrections

| File | Fault | Fix |
|---|---|---|
| `13-authoring-a-setting.md` | `characteristics:` maps to nothing | remove the block |
| `13-authoring-a-setting.md` | *Extend* claims settings extend skills | skills are declared, not extended |
| `07-tooling.md` | same *Extend* claim | same |
| `03a-2-aftermath.md:199` | names a "combat skill" | "the skill the wound bears on" |
| `06-state.md` | wound has no `bears_on` | add it |

Fixing one and not the others is how the fault comes back, so all five land together.

## Constitution check

| Gate | How this satisfies it |
|---|---|
| Setting-agnostic | The engine names no skill; that is the decision, not a side effect. |
| One statement of one fact | The skill bands stay in `10-diegesis.md` and are cited. |
| Nothing referenced undefined | The career cap and starting skills are cited against the documents that own them. |
| Documents describe the present | The corrections rewrite; they do not annotate. |

## Steps

1. `docs/design/04-the-character.md`.
2. ADR 0013 — no characteristics, no skill vocabulary.
3. The five corrections.
4. `README.md` reading order; `docs/README.md` index.
5. `check_docs.py`, `backlog.py check`, and a grep for `characteristic` as a mechanic.

## Risks

**`bears_on` may need a fallback.** Not every wound arrives from a skill roll — a fall, a fire, a
poisoning. The field must be optional, and a wound with no skill behind it carries no `skill: -N`
effect. Stated in the document rather than discovered in Stage 6.
