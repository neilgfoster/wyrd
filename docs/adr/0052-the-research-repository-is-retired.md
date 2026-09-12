# ADR 0052: The shared research repository is retired; all source material lives in setting repos

**Status:** Accepted
**Date:** 2026-09-12
**Supersedes:** [ADR 0051](superseded/0051-setting-specific-corpus-lives-in-the-setting-repo.md)

## Context

ADR 0051, accepted earlier the same day, corrected `02-architecture.md` and `26-corpus-index.md`
to match what every populated setting repo had already done — carry its own `library/` directly —
but kept one carve-out: a periodical whose issues carry material for several different worlds
would still need a shared home, since duplicating a whole issue into every setting that might draw
from it was judged "absurd."

That carve-out assumed the unit of duplication was the whole issue. It is not. The actual
workflow is to triage a periodical at the **article** level and copy only the relevant excerpt
into whichever setting(s) it belongs to — not the whole magazine, and not by reference to a
shared corpus. Under that workflow nothing is ever shared by more than one setting reading the
same stored text; each setting holds its own copy of only the material it actually uses. The
"duplicating a whole issue is absurd" argument does not apply to duplicating a few relevant pages,
and the alternative ADR 0051 rejected — "duplicate everything into every setting repo... and
retire `wyrd-research` entirely" — turns out to be the correct one once the unit of curation is
corrected from *issue* to *article*.

With no material left that is genuinely shared between settings, `wyrd-research` has no remaining
job: extraction and OCR are pipeline steps, not a reason for the *output* to live in a repo other
than the setting that will use it, and #97/#98/#101's pipeline work already builds that pipeline as
something any setting repo runs against its own `library/`.

## Decision

**All source material — raw library, extracted text, and indexes over it — lives in the setting
repo(s) it is relevant to. The `wyrd-research` repository is retired.** Periodical triage happens
per article: an article relevant to one setting is copied into that setting's own `library/`
(or `corpus/`, once extracted); an article relevant to several is copied into each. Extraction and
OCR remain pipeline steps (#101) run per setting repo, with no shared intermediate repo required.

## Why

- **Nothing is actually shared once triage is at article granularity.** The whole justification
  for a shared repo — the same stored text serving more than one setting — does not hold when
  each setting only ever holds the specific excerpt it curated for itself.
- **One fewer repository, one fewer place a setting's provenance chain can point to and go
  stale.** A setting's `sources:` field resolving into its own `corpus/` rather than out to
  another private repo is simpler to keep correct.
- **It matches the direction #101 was already headed.** #101 builds the extraction/indexing
  pipeline as something any setting repo runs for itself; retiring `wyrd-research` removes the
  one remaining case (the shared periodical corpus) that pipeline would otherwise still need to
  special-case.

## Alternatives rejected

- **Keep `wyrd-research` for the still-untriaged backlog** — a durable home for material not yet
  claimed by any setting. Considered and set aside: triage happens per source as it is mined, not
  as a separate durable-storage step, so there is no stage at which unclaimed material needs to
  persist anywhere beyond the working pull/extract tooling already in front of a setting's own
  `library/`.
- **Keep `wyrd-research` as pure scratch/staging** (downloads and OCR happen there transiently,
  nothing committed durably). Rejected for the same reason as above: with per-article triage,
  there is no intermediate durable state that isn't already either "not yet decided" (stays local,
  uncommitted, wherever the pull happens) or "decided" (belongs in a setting repo now).

## Consequences

- `02-architecture.md`'s repository table and "Where the corpus lives" section drop
  `wyrd-research` entirely: source material, extracted text and indexes all live in the setting
  repo(s) they belong to.
- `26-corpus-index.md`, `19-campaign.md`, `29-evolution.md`, `01-principles.md`, and `CLAUDE.md`
  drop their `wyrd-research` references.
- #3, #98, and #101 (re-scoped once already under ADR 0051) are re-scoped again: #98's remaining
  job (indexing a shared corpus) no longer exists and the feature is closed as obsolete; #101
  proceeds unchanged except that its second proof run (against `wyrd-research`'s corpus) is
  dropped — one real setting repo is enough to prove genericity.
- Anything still of value sitting in the (retired) `wyrd-research` repository — the corpus text
  from #97's fix, reference notes — is either migrated into the setting repo it belongs to as that
  setting is worked on, or left to lapse; this ADR does not itself perform that migration.
