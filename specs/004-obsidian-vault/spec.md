# Feature Specification: Obsidian vault and the README as hub

**Feature Branch**: `004-obsidian-vault`

**Created**: 2026-08-25

**Status**: Draft

**Input**: GitHub issue #39 — make the repo an Obsidian vault with the root `README.md` as the hub
everything links from. Out of scope: making the setting and chronicle repos vaults, and the document
move and renumbering (#38, which depends on this).

## Context

The repo is read in two places that want different things. On github.com it is a public set of
design documents; in Obsidian it should be a navigable graph. The two are compatible, but only if
the link policy is chosen deliberately.

**Wikilinks are already a Wyrd convention — for data, not prose.** `design/14-entities.md` describes
the world mesh as "human-editable, diff-legible, and — because they link with `[[wikilinks]]` — a
working graph"; `design/07-tooling.md` says state is YAML with `[[wikilink]]` frontmatter parsed by a
small internal reader; `design/08-maintenance.md` runs a referential-integrity check over `[[link]]`.
So the *entity model* is already an Obsidian graph by design.

**But GitHub does not render `[[wikilinks]]`.** This repo is intended public. A wikilink degrades to
literal text for every reader arriving from github.com, while Obsidian resolves ordinary markdown
links perfectly well. The asymmetry decides the policy, and it is the opposite of the obvious answer.

**The intent is already half-recorded.** `.gitignore` already carries `.obsidian/workspace*`, which
settles a question that would otherwise need asking: vault configuration is committed, per-machine
workspace state is not.

## The hub is already stale, four times over

"Everything links from the README" earns its place as a *checked invariant* rather than a tidy-up,
because every index in the repo has already rotted silently:

| Index or claim | Verified state |
|---|---|
| `README.md` "Read in this order" | **missing `03a-2-aftermath.md`** |
| `design/README.md` ADR index | **stops at 0008**; 0009 and 0010 exist on disk |
| `README.md` repositories table | says `wyrd-<setting>`; actual repos are `wyrd-setting-<name>` |
| `README.md` Status section | **links to `playtest/`, which does not exist** — the repo's only dead link |
| `README.md` Status section | asserts **"Design complete; no implementation yet"** — the design programme (#1) exists because it is not |

Four of the five were found by script in this feature's first ten minutes. None was found by reading.

## Clarifications

- **Link policy** — markdown links in prose, `[[wikilinks]]` in entity data. Not a conversion of the
  documents to wikilinks: that would break every reader on github.com to please a tool that already
  handles markdown links.
- **What must be reachable** — every document under `design/`, including every ADR. `specs/` is
  per-change history rather than current design; it is reachable as a directory, not file by file.
- **Sequencing** — this lands before #38, because Obsidian updates links automatically on move and
  rename, which turns #38's 225-link rewrite from a bulk substitution into a tool operation.

## Requirements

### FR-1 — The repo opens as a vault

Committed, machine-independent configuration under `.obsidian/`. Per-machine workspace state stays
ignored. The configuration must express the link policy — Obsidian must *create* markdown links, not
wikilinks, so the policy holds by default rather than by discipline.

### FR-2 — The link policy is recorded

An ADR states markdown-in-prose / wikilinks-in-data and why, because "it is an Obsidian vault, so use
wikilinks" is the obvious answer, is wrong here, and will be proposed again.

### FR-3 — Everything is reachable from the README

Every markdown document under `design/` is reachable from `README.md`, directly or through one index
that `README.md` links to. `specs/` is exempt at file level and reachable as a directory.

### FR-4 — The four stale indexes are corrected

Including the dead `playtest/` link and the false "Design complete" claim. A status line that is
wrong is worse than no status line.

### FR-5 — A check makes recurrence loud

A stdlib script that fails on:

- a markdown document under `design/` not reachable from `README.md`
- a relative link resolving to nothing, anywhere in the repo
- an ADR on disk missing from `design/README.md`'s index
- a `[[wikilink]]` appearing in a prose document rather than in entity-data illustration

The last one guards the policy itself, which otherwise erodes the first time someone edits in
Obsidian with the default settings.

### FR-6 — GitHub rendering does not regress

Both audiences are real. Nothing may render worse on github.com than it does today.

## Constraints

- Python 3.11+, stdlib only (`design/07-tooling.md` §2). `unittest`, not pytest (§6).
- Committed vault config must be machine-independent — no absolute paths, no personal preferences.
- Nothing unpublishable: a vault config is not a place for library paths.
- No file under `.kord/`, `.specify/` or `.github/ISSUE_TEMPLATE/` is touched.
- Documentation changes describe the present; no "previously we…" notes.

## Acceptance criteria

- [ ] `.obsidian/` config is committed, machine-independent, and sets markdown links as the default.
- [ ] `.gitignore` keeps per-machine workspace state out.
- [ ] An ADR records the link policy and its rejected alternative.
- [ ] Every `design/**.md` is reachable from `README.md`.
- [ ] `design/README.md` indexes 0009 and 0010.
- [ ] `README.md` lists `03a-2-aftermath.md`, names repos `wyrd-setting-<name>`, has no dead link,
      and no longer claims the design is complete.
- [ ] `python3 tools/check_docs.py` exits non-zero on each failure class in FR-5 and zero on the
      repo as left.
- [ ] The check's tests exercise the check itself, not a restatement of its logic.
