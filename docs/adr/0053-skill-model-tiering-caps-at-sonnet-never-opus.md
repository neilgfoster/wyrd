# ADR 0053 — Skill model tiering caps at Sonnet; Opus is never selected, even for narration

**Date:** 2026-09-16
**Status:** Accepted

## Context

Epic #429 extended `docs/design/27-tooling.md` section 5's model-tiering policy from
engine-internal work to the user-facing skill layer (`SKILL.md` `model:`/`effort:` frontmatter),
for the first time in a real Wyrd repository. Three sibling features decided each skill's tier:

- `/wyrd-play` and `/wyrd-bootstrap` (#430) — almost entirely narration, character voice, and
  judgement about what a result means. Both were tiered `model: sonnet`, `effort: high`.
- `/wyrd-character` and `/wyrd-end-session` (#431) — pure CLI-verb dispatch and verbatim
  reporting, with a checkable right answer. Both were tiered `model: haiku`. `/wyrd-downtime`
  was considered for the same tier and explicitly excluded, because its own text states five of
  its six Undertakings are played "exactly as any other GM judgment call" — real judgement, not
  the mechanical class Haiku is specified for.
- `create-setting` (#432, in `wyrd-setting-template`) — tiered `model: sonnet`, with its
  mechanical corpus-lookup steps delegated to a new `.claude/agents/corpus-fact-finder.md`
  Haiku subagent (`tools: Read, Grep, Glob` only), so the closed retrieval task and the
  judgement-heavy prose/register synthesis no longer share a tier.

Every one of those decisions capped its *capable*-tier skill at Sonnet, never Opus — but until
now nothing said so as a rule, or considered the alternative. Section 5 already names "Sonnet /
Opus" together as one tier ("The GM itself... that is the one place not to economise") without
choosing between them. #430's own reasoning for `/wyrd-play` — narration, voice, motive, and
judgement about what a result means are exactly the work Sonnet at `effort: high` is being asked
to do, and a high effort setting on a capable model "costs nothing against a mechanical step" —
never argues that a *larger* model is warranted for that work; it only argues against
under-provisioning effort on a smaller one.

The real alternative was live, not hypothetical: Wyrd's narration-heaviest skills
(`/wyrd-play`, `/wyrd-bootstrap`) are precisely the ones "that is the one place not to economise"
was written to protect, and Opus is a plausible reach for exactly that class of work — voice,
motive, arc adaptation. Someone revisiting this in a year, remembering only "narration is the
one place not to economise" and not the tiering discussion that produced #430-#432, could
plausibly propose Opus for `/wyrd-play` believing it a strict quality upgrade with no offsetting
cost. It has real, considered costs: latency inside a synchronous per-beat player interaction,
and it works against Wyrd's own tiering discipline of matching model to the kind of work rather
than defaulting to "biggest available." Nothing about "the GM itself" work is open-ended in a way
that a larger model resolves better; it is bounded by the GM contract itself (voice, motive,
judgement about a fixed rule set), and Sonnet at `effort: high` was judged sufficient for that
bound by every skill actually tiered against it.

## Decision

**No wyrd skill is ever tiered `model: opus`. Sonnet is the ceiling for every capable-tier skill,
regardless of how narration-heavy or judgement-heavy that skill's work is.**

This is not a statement that Opus is unable to do the work — it is that the class of work
reserved for the capable tier (narration, character voice and motive, judgement about what a
result means, within the GM contract's own bounds) does not need it, and every skill actually
tiered so far (`/wyrd-play`, `/wyrd-bootstrap`, `create-setting`) confirmed that by choosing
`effort: high` on Sonnet rather than reaching for a larger model. Effort is the dial for a
judgement-heavy skill's quality; model choice is not.

Section 5's tiering table records this by naming the top tier "Sonnet" alone rather than
"Sonnet / Opus," and its Haiku-subagent delegation mechanism now has a real, built example:
`corpus-fact-finder.md` in `wyrd-setting-template` (added by #432), which took the mechanical
corpus-retrieval portion of `create-setting`'s work off the capable tier entirely rather than
raising that tier's ceiling.

## Consequences

- Any future skill added anywhere in the `wyrd-*` repositories is capped at `model: sonnet`
  regardless of how much narration or judgement it carries; a case for more capability is a case
  for `effort: high` plus, where a mechanical sub-task can be isolated, a Haiku subagent — not a
  case for `model: opus`.
- Revisiting this decision requires a new ADR that supersedes this one, not a quiet frontmatter
  change on one skill; the rejected alternative (Opus for narration-heavy skills) is recorded
  here specifically so that re-proposing it starts from the reasoning that already rejected it.
