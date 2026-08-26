# ADR 0011 — Markdown links in prose, wikilinks in data

**Date:** 2026-08-25
**Status:** Accepted

## Context

The repository is now an Obsidian vault. Obsidian's native link form is the `[[wikilink]]`, and Wyrd
already uses wikilinks — so the obvious move is to convert the documents and be done.

That move is wrong here, and it is wrong for a reason that is easy to miss because it depends on who
is reading.

**Wyrd already uses wikilinks, but for data.** [`27-entities.md`](../design/27-entities.md) describes the
world mesh as "human-editable, diff-legible, and — because they link with `[[wikilinks]]` — a working
graph". [`20-tooling.md`](../design/20-tooling.md) says state is YAML with `[[wikilink]]` frontmatter, read
by a small internal parser. [`21-maintenance.md`](../design/21-maintenance.md) runs a referential-integrity
check across every `[[link]]`. The entity model *is* an Obsidian graph, by design and before Obsidian
was involved.

**GitHub does not render wikilinks.** This repository is intended public
([`02-architecture.md`](../design/02-architecture.md)), and its design documents are read on github.com,
where `[[03-rules]]` degrades to literal text. Obsidian, meanwhile, resolves ordinary markdown links
without complaint.

So the two link forms are not equivalent in cost. One works for both audiences; the other works for
one.

## Decision

**Prose uses markdown links. Entity data uses `[[wikilinks]]`.**

- Every document a person reads as prose — `README.md`, `CLAUDE.md`, `doc/design/*.md`, ADRs, specs —
  links with a markdown link: square brackets for the text, round brackets for a relative path.
- Every entity record — the world mesh in a setting or chronicle repo — links with `[[wikilinks]]`,
  unchanged.
- The vault is configured to *create* markdown links: `.obsidian/app.json` sets
  `useMarkdownLinks: true` and `newLinkFormat: "relative"`. The policy is the default rather than
  something to remember.
- `tools/check_docs.py` fails on a `[[wikilink]]` in a prose document outside a code block, so the
  policy survives someone editing with different settings.

The dividing line is **audience, not file type**: prose is read on github.com by people who have not
cloned anything; entity data is read by the engine and by Obsidian, and never by a stranger.

## Consequences

**Both readers are served.** The graph view, backlinks and rename-refactoring all work, because
Obsidian resolves markdown links natively. Nothing regresses for a reader arriving from a search
engine.

**Renaming becomes safe, which unblocks the document restructure.** Obsidian updates markdown links
automatically on move and rename. That turns the 225-link rewrite in the document move (#38) from a
bulk find-and-replace — which `CLAUDE.md` records corrupting words in this repo three times — into a
tool operation. This ADR is why #38 waits on the vault rather than the other way round.

**The README becomes load-bearing.** Reachability from the hub is now checked, so a document nothing
links to fails the build. That is intended: an unreachable document is one nobody reads. Four indexes
had already gone stale silently before the check existed.

**One rule to remember instead of two.** "Prose links like GitHub, data links like Obsidian" is a
sentence, and the tooling enforces it either way.

## Alternatives rejected

**Convert everything to wikilinks.** The obvious reading of "make it an Obsidian vault", and the one
that breaks every reader who has not cloned the repo. It optimises for the tool over the audience,
and the tool did not need it.

**Convert entity data to markdown links.** Consistent in the other direction, and it would break the
world mesh: `27-entities.md` builds a graph out of wikilinks, `21-maintenance.md` checks referential
integrity across them, and a setting's entity files are hand-edited by people who want the short
form. Consistency is not worth paying for with the thing that already works.

**Support both forms in prose and let each author choose.** No policy is a policy: within a year half
the documents would render as literal brackets on github.com and nobody would know which half. A rule
nothing checks is a rule that has already drifted.
