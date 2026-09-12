# ADR 0051: Setting-specific source material lives in the owning setting repo, not the shared research repo

**Status:** Superseded by [ADR 0052](../0052-the-research-repository-is-retired.md)
**Date:** 2026-09-12

## Context

`02-architecture.md`'s "Where the corpus lives" section states that extracted source text lives
**once**, in the private `wyrd-research` repo, and never in setting repos — justified because
"sources do not divide cleanly by setting: a single magazine issue may carry material for several
different worlds, and duplicating it per setting would be absurd." `26-corpus-index.md` goes
further: `documents.json` records link straight to `wyrd-research` GitHub URLs, and the scenario
index's stated scope is "the whole library, not one shelf of it."

In practice, every populated setting repo (`wyrd-setting-wfrp-1e/2e/3e/4e`, `-tor`, `-titan`,
`-maelstrom`, `-darkfuture`, and others) already carries its own `library/` of source PDFs via Git
LFS, committed directly into that setting's repo — not staged through `wyrd-research` first.
`wyrd-setting-template`'s `library/` is a `.gitkeep` stub, confirming this was always a designed-in
per-setting slot, not an accident that crept in. #101 ("Generalise corpus extraction and indexing
for any setting repo") already assumes exactly this shape — "a setting repo supplies documents
under `library/`... every setting repo needs the same capability, generalised so any setting can
run it against its own `library/`" — and was raised without anyone noticing it contradicted
`02-architecture.md`.

The two design documents were never reconciled, and neither was updated to match what the fleet
actually did. This is the "two documents describing one thing differently" fault class this repo
keeps re-finding: both read as internally coherent, so neither looked wrong until read against the
actual state of the setting repos.

The rationale for centralizing was real for one specific case — a periodical (a magazine's issue
run) genuinely does not divide by setting, since one issue may carry material relevant to several
worlds at once, sharing an owner would be arbitrary. It was never a good reason to centralize a
single-system rulebook or adventure line that belongs to exactly one setting from the moment it is
acquired.

## Decision

**Source material that belongs to exactly one setting lives in that setting's own repo**
(`library/` for the raw source, `corpus/` for its extracted text, `index/` for indexes over it),
extracted and indexed by that setting's own copy of the (to-be-generalised, #101) pipeline.

**`wyrd-research` is retained only for material that genuinely does not divide by setting** — a
periodical whose issues carry content for multiple worlds (e.g. a long-running magazine), where
apportioning any one issue to a single setting would be arbitrary. Its extracted text stays
addressable by id from any setting's own indexes, exactly as `26-corpus-index.md` already
describes for the shared case.

## Why

- **Matches what every real setting repo already does.** This is not a change in direction, it is
  documenting the direction the fleet already took, so the design documents stop being wrong about
  current practice.
- **The rationale for centralizing never applied to single-setting material.** A rulebook and an
  adventure line for one system were never going to be split across settings; they only ever look
  "shared" if you don't ask which setting owns them.
- **It keeps the useful part of the original reasoning.** Genuinely cross-setting material (the
  periodical case) still has nowhere sensible to live except centrally — this ADR narrows the
  claim rather than reversing it outright.
- **It unblocks #101's ordering.** #98 (build the corpus's deterministic and arcs indexes) was
  scoped to run once, by hand, against `wyrd-research`'s corpus. Under the corrected model that
  work is per-setting-repo tooling (#101's job) applied first to `wyrd-research`'s narrowed,
  genuinely-shared corpus and to each setting's own `library/` — not one-off code against a corpus
  that was about to lose most of its content to the setting repos anyway.

## Alternatives rejected

- **Keep everything centralized in `wyrd-research`, including single-setting material**, and treat
  each setting repo's populated `library/` as a mistake to unwind. Rejected: it is already the
  practice across eight-plus setting repos, unwinding it would mean re-migrating PDFs already
  committed via LFS, and the original "does not divide by setting" argument was never true for
  single-setting rulebooks in the first place.
- **Duplicate everything into every setting repo, including genuinely cross-setting periodicals**,
  and retire `wyrd-research` entirely. Rejected: the periodical case is real — a single White Dwarf
  issue can carry material relevant to several different settings' corpora, and duplicating the
  same extracted text into every setting that might eventually draw from it is exactly the
  "absurd" `02-architecture.md` already correctly identified. `wyrd-research` (or an equivalent
  shared home) still earns its place for that slice.

## Consequences

- `02-architecture.md`'s "Where the corpus lives" section is rewritten to state the split: setting-
  specific material lives in the owning setting repo; only genuinely cross-setting material stays
  in `wyrd-research`.
- `26-corpus-index.md` is corrected: `documents.json` is per-repo (setting or `wyrd-research`), not
  a single global index pointing at `wyrd-research` URLs; the scenario index's scope is "this
  repo's library," with cross-setting scenarios drawn from `wyrd-research` addressed by id the same
  way any other referenced document is.
- #3, #98, #101 are re-scoped to match (see the issue-body updates accompanying this ADR): #98 no
  longer targets `wyrd-research` as a one-off; #101's generalized pipeline is built first and run
  against both `wyrd-research`'s narrowed corpus and `wyrd-setting-wfrp-1e`'s own `library/`.
- #97's fix (closed) still stands as-is: it corrected the extraction pipeline's own bugs
  (slug collision, wrong puller path), which apply regardless of which repo runs it.
